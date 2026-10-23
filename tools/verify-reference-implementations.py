#!/usr/bin/env python3
"""Verify the reference implementations attached to a release and run the document-level TCK on them. Offline once the
assets are on disk.

Usage (from the repository root):
  python3 -I tools/verify-reference-implementations.py --assets <dir> [--lock tck/reference-implementations.lock.json] [--out <dir>]

Steps, each one blocking:
  1. every asset named in the lock is in <dir> and its sha256 and size match the lock;
  2. the npm tarballs install with `npm install --offline` into an empty project (no registry is contacted);
     the Python kernel is extracted;
  3. the document-level TCK (tck/run-documents.py) runs on the JavaScript and the Python kernel with
     --expect-version, so the report proves which build it tested, and with --strict-messages, so the reference
     kernels are held to the exact error texts of the vectors;
  4. smoke test of the command-line host: version, validate and run of an example, and run of a folder
     (a directory whose `.jos/manifest.jos` is the document).
Writes <out>/tck-<id>.json (one result per vector), <out>/host-smoke.json and <out>/SUMMARY.md (assets, hashes,
versions, results). Exit code 0 only if every step passes.
"""
import hashlib, json, os, shlex, subprocess, sys, tarfile, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = sys.argv[1:]
val = lambda k, d=None: a[a.index(k) + 1] if k in a else d
ASSETS = val('--assets')
if not ASSETS:
    print(__doc__); sys.exit(64)
ASSETS = os.path.abspath(ASSETS)
LOCK = os.path.abspath(val('--lock', os.path.join(ROOT, 'tck', 'reference-implementations.lock.json')))
OUT = os.path.abspath(val('--out', os.path.join(ROOT, 'quality', 'reference-implementations')))
os.makedirs(OUT, exist_ok=True)
lock = json.load(open(LOCK, encoding='utf-8'))
impls = {i['id']: i for i in lock['implementations']}
rows, ok_all = [], True


def step(name, ok, detail=''):
    global ok_all
    ok_all &= bool(ok)
    rows.append((name, 'PASS' if ok else 'FAIL', detail))
    print(('PASS ' if ok else 'FAIL ') + name + (': ' + detail if detail else ''))


# 1. hashes
for i in impls.values():
    p = os.path.join(ASSETS, i['asset'])
    if not os.path.exists(p):
        step('asset ' + i['asset'], False, 'missing'); continue
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    step('sha256 ' + i['asset'], h == i['sha256'] and os.path.getsize(p) == i['size'], h)
if not ok_all:
    sys.exit(1)

# 2. offline install and extraction
work = tempfile.mkdtemp(prefix='jos-ref-')
install = os.path.join(work, 'install'); os.makedirs(install)
open(os.path.join(install, 'package.json'), 'w').write('{"name":"jos-reference-check","version":"0.0.0","private":true}\n')
npm = [os.path.join(ASSETS, i['asset']) for i in impls.values() if i['kind'] == 'npm tarball']
r = subprocess.run(['npm', 'install', '--offline', '--no-audit', '--no-fund', '--ignore-scripts', *npm], cwd=install, capture_output=True, text=True)
step('npm install --offline (' + ', '.join(os.path.basename(x) for x in npm) + ')', r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else '')
extract = os.path.join(work, 'extract'); os.makedirs(extract)
for i in impls.values():
    if i['kind'] == 'source tarball':
        with tarfile.open(os.path.join(ASSETS, i['asset'])) as t:
            t.extractall(extract, filter='data')
        step('extract ' + i['asset'], os.path.isdir(os.path.join(extract, i['root'])))
fill = lambda s: s.replace('{install}', install).replace('{extract}', extract)

# 3. document-level TCK with the expected version
results = {}
for i in impls.values():
    if 'tck' not in i:
        continue
    cli = fill(i['tck']['cli'])
    r = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tck', 'run-documents.py'), '--cli', cli, '--expect-version', i['tck']['expect_version'], '--strict-messages', '--json'],
                       capture_output=True, text=True, timeout=1800)
    try:
        rep = json.loads(r.stdout)
    except ValueError:
        rep = {'error': (r.stdout + r.stderr).strip()[-600:]}
    json.dump(rep, open(os.path.join(OUT, 'tck-' + i['id'] + '.json'), 'w'), indent=1)
    results[i['id']] = rep
    good = r.returncode == 0 and rep.get('vectors') and rep.get('pass') == rep.get('vectors')
    step(f"TCK document level, {i['id']} ({rep.get('version')})", good, f"{rep.get('pass')} of {rep.get('vectors')} vectors" if 'vectors' in rep else rep.get('error', ''))

# 4. host smoke test
smoke = []
for i in impls.values():
    if 'smoke' not in i:
        continue
    host = shlex.split(fill(i['smoke']['cli']))
    docs = os.path.join(ROOT, 'tck', 'documents')
    def run(args, cwd):
        r = subprocess.run(host + args, cwd=cwd, capture_output=True, text=True, timeout=300, env=dict(os.environ, HOME=work))
        return r.returncode, r.stdout
    code, out = run(['--version'], work)
    smoke.append({'check': 'version', 'code': code, 'out': out.strip()[:200]})
    step('host version', code == 0 and i['smoke']['expect_version'] in out.split(), out.strip().splitlines()[0] if out.strip() else '')
    for label, args in (('validate example', ['validate', os.path.join(docs, 'hello.jos'), '--json']),
                        ('run example', ['run', os.path.join(docs, 'hello.jos'), '--json']),
                        ('run folder', ['run', os.path.join(docs, 'fixtures', 'dirs', 'runnable'), '--json']),
                        ('run sealed folder', ['run', os.path.join(docs, 'fixtures', 'dirs', 'sealed-ok'), '--json'])):
        code, out = run(args, work)
        try:
            j = json.loads(out)
        except ValueError:
            j = {}
        good = code == 0 and (j.get('valid') is True if label.startswith('validate') else j.get('ok') is True)
        if label == 'run sealed folder':  # the host verifies the directory hash and reports the directory (SPEC-2.0 §9.3)
            exp = json.load(open(os.path.join(docs, 'dir-sealed-runs.expected.json'), encoding='utf-8')).get('artifact')
            good = good and j.get('artifact') == exp
        smoke.append({'check': label, 'code': code, 'artifact': j.get('artifact'), 'ok': good})
        step('host ' + label, good, f"exit {code}, artifact {j.get('artifact')}")
json.dump(smoke, open(os.path.join(OUT, 'host-smoke.json'), 'w'), indent=1)

lines = ['# Reference implementations: verification', '',
         'Lock: `' + os.path.relpath(LOCK, ROOT) + '`. Assets from `' + ASSETS + '`.', '',
         '| Asset | Package | Version | sha256 |', '|---|---|---|---|']
lines += [f"| `{i['asset']}` | `{i['package']}` | {i['version']} | `{i['sha256']}` |" for i in impls.values()]
lines += ['', '| Step | Result | Detail |', '|---|---|---|'] + [f'| {n} | {s} | {d} |' for n, s, d in rows]
lines += ['', 'Result: ' + ('PASS' if ok_all else 'FAIL')]
open(os.path.join(OUT, 'SUMMARY.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('reference implementations:', 'PASS' if ok_all else 'FAIL', '·', os.path.join(OUT, 'SUMMARY.md'))
sys.exit(0 if ok_all else 1)
