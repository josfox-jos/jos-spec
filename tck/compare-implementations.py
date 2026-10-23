#!/usr/bin/env python3
"""TCK, implementation parity: two implementations run the same documents and their complete results are compared with
each other, not with an expectation. Offline, standard library only.

Usage:
  python3 -I tck/compare-implementations.py --a "<command of implementation A>" --b "<command of implementation B>"
                                            [--documents <dir>] [--only name1,name2] [--json] [--pointer-only]
                                            [--version-args "version"]
  python3 -I tck/compare-implementations.py --a "node /path/to/kernel/js/bin/jos-core" --b "python3 -I /path/to/kernel/py/bin/jos-core"

Each command is invoked as tck/run-documents.py invokes the implementation under test (`version`,
`validate <file> --json`, `run <file> --json --runs <dir> [extra arguments]`), on the same documents, prepared the same
way: a copy of --documents (default tck/documents/) in a temporary directory, an empty HOME, the same environment. For
every `<name>.expected.json` the document it names (`document`, `run_document` or `<name>.jos`) goes through
`validate` (unless the vector sets "validate": null) and through `run` with its `run_args`. Both implementations get
the same directory path, one after the other, and run the documents in the same order, so a path in a result is the
same path for both. The expectation in the vector is not consulted: run-documents.py judges each implementation
against it; this tool judges the two against each other.

What is compared, for each command: the exit code and the whole JSON object printed on standard output (every member,
at every depth: a member present in one result and absent in the other is a difference, as are a different type,
`true` against `1`, a different array length or order, a different error text). Numbers are compared by the exact
value of their JSON text: `1` and `1.0` are the same number, `9007199254740993` and `9007199254740992` are not, even
though they are the same IEEE 754 double (the report says so). Output that is not JSON is compared as text.
Not compared: standard error, and the files an implementation writes under --runs (the ledger layout is the
implementation's; run-documents.py does not judge it either). The path of the temporary directory is written
`<work>` in the report; it is the same path for both implementations.

Normalized, and nothing else (what the specification allows two conforming implementations to print differently):
  1. Minted identifiers: a JOSID whose payload is a ULID (`run_`, `cap_`, `usr_`, `org_`, `rt_`, `host_`, `job_`,
     `day_`, `int_`, `apr_`, `clone_`, with or without a `system.` prefix), wherever it appears in a string, becomes
     `<kind_N>`, N being its order of first appearance in that document's results (members visited in RFC 8785 key
     order, validate before run). The same identifier keeps the same label, so "the receipt names the run that
     produced it" is still compared. Content identifiers (`art_`) are not normalized.
     Allowed by: SPECIFICATION.md Section 11 (Kernel — Core: "identical receipts (except `duration_ms`, minted ids,
     `ts`)") and Section 8.2;
     `companions/josid/0.1.0/SPEC.md` Section 4.1 (a ULID is clock time plus CSPRNG output).
  2. Timestamps: the value of every `ts` member becomes `<ts>`. The `issued` member of a Capability becomes `<ts>`
     and its `expires` becomes `<issued+Ns>`, so the lifetime of the Capability is still compared.
     Allowed by: SPECIFICATION.md Section 11 and Section 7.2 (`ts`);
     `companions/capability/0.1.0/SPEC.md` Section 2 (`issued`, `expires`: RFC 3339 times of a Capability minted for the run).
  3. Measured durations: the value of every `duration_ms` member becomes `<ms>`.
     Allowed by: SPECIFICATION.md Section 11 and Section 7.2.
  4. Receipt hashes, as a consequence of 1 to 3: SPECIFICATION.md Section 7.2 hashes the receipt with its `run_id`,
     `capability`, `duration_ms` and `ts`, so `hash` and the `prev` that repeats it cannot match. Each receipt's
     `hash` is first recomputed (SHA-256 over the RFC 8785 form of the receipt with `hash` set to "") and has to verify
     in its own implementation, or that is a difference; then each receipt hash becomes `<receipt_N>` everywhere it
     appears, so the chain (`prev` of a receipt is the hash of the one before it, a flow lists its steps' hashes) is
     still compared. The all-zero `prev` of the first receipt is not normalized.
  5. The `version` command: only the version words (MAJOR.MINOR.PATCH with an optional pre-release) are compared;
     the rest of the line (the implementation's name, `(js)`, `(py)`) may differ. The specification does not define
     that line; the TCK reads only the version from it (run-documents.py --expect-version).
--pointer-only also reduces every entry of an `errors` array to its JSON Pointer (the text before ": "), as
run-documents.py does by default, because error messages are not part of the format (tck/README.md). It is off by
default: the reference implementations are held to the same error texts.

Output: a table with one row per document (exit codes of validate and run in A and B, number of differences) and the
differences, path by path. --json prints the evidence: both commands, both versions, the normalizations applied, and
for every document both normalized results and every difference. Exit code 0 only if there is no difference.
"""
import decimal, hashlib, json, os, re, shlex, shutil, subprocess, sys, tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
val = lambda k, d=None: a[a.index(k) + 1] if k in a else d
CLI = {'A': val('--a'), 'B': val('--b')}
if not CLI['A'] or not CLI['B']:
    print(__doc__); sys.exit(64)
DOCS = os.path.abspath(val('--documents', os.path.join(HERE, 'documents')))
ONLY = set(val('--only').split(',')) if val('--only') else None
POINTER_ONLY = '--pointer-only' in a
VERSION_ARGS = shlex.split(val('--version-args', 'version'))
NORMALIZATIONS = [
    'minted JOSID with a ULID payload -> <kind_N> by order of first appearance (SPECIFICATION.md §11, §8.2; JOSID §4.1)',
    'ts -> <ts>; Capability issued -> <ts>, expires -> <issued+Ns> (SPECIFICATION.md §11, §7.2; Capability §2)',
    'duration_ms -> <ms> (SPECIFICATION.md §11, §7.2)',
    'receipt hash verified, then -> <receipt_N> wherever it appears (SPECIFICATION.md §7.2, consequence of the above)',
    'version line: only the version words are compared (tck/run-documents.py --expect-version)',
] + (['errors[] entries reduced to their JSON Pointer (--pointer-only; tck/README.md)'] if POINTER_ONLY else [])

MINTED = re.compile(r'(?<![A-Za-z0-9._-])((?:[a-z0-9-]{1,32}\.)?(usr|org|rt|host|run|job|day|int|cap|apr|clone)_)[0-9A-HJKMNP-TV-Z]{26}(?![A-Za-z0-9_-])')
SEMVER = re.compile(r'(?<![\w.-])v?(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)(?![\w.-])')
NUM = (int, float, decimal.Decimal)
NUMBER_OUT = lambda o: (int(o) if o == o.to_integral_value() else float(o)) if isinstance(o, decimal.Decimal) else str(o)


# --- RFC 8785 (JCS), for the receipt hash of SPECIFICATION.md Section 7.2 -------------------------------------------
def jcs_number(x):
    if isinstance(x, decimal.Decimal):
        x = int(x) if x == x.to_integral_value() and abs(x) < 2 ** 53 else float(x)
    if isinstance(x, int):
        if abs(x) < 2 ** 53:
            return str(x)
        x = float(x)                                       # an I-JSON number is an IEEE 754 double (RFC 8785 §3.2.2.3)
    if x != x or x in (float('inf'), float('-inf')):
        raise ValueError('not a JSON number')
    if x == 0:
        return '0'
    sign = '-' if x < 0 else ''
    t = decimal.Decimal(repr(abs(x))).as_tuple()          # shortest round-trip digits, as ECMAScript chooses them
    digits = ''.join(map(str, t.digits)).rstrip('0') or '0'
    exp = t.exponent + (len(t.digits) - len(digits))
    k, n = len(digits), len(digits) + exp                  # value = 0.digits x 10^n
    if k <= n <= 21:
        s = digits + '0' * (n - k)
    elif 0 < n <= 21:
        s = digits[:n] + '.' + digits[n:]
    elif -6 < n <= 0:
        s = '0.' + '0' * (-n) + digits
    else:
        e = n - 1
        s = digits[0] + ('.' + digits[1:] if k > 1 else '') + 'e' + ('+' if e >= 0 else '-') + str(abs(e))
    return sign + s


def jcs(v):
    if v is None or isinstance(v, bool):
        return json.dumps(v)
    if isinstance(v, (int, float, decimal.Decimal)):
        return jcs_number(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return '[' + ','.join(jcs(x) for x in v) + ']'
    keys = sorted(v, key=lambda k: k.encode('utf-16-be'))
    return '{' + ','.join(json.dumps(k, ensure_ascii=False) + ':' + jcs(v[k]) for k in keys) + '}'


def receipt_hash(r):
    return 'sha256:' + hashlib.sha256(jcs(dict(r, hash='')).encode('utf-8')).hexdigest()


# --- running ---------------------------------------------------------------------------------------------------
work = os.path.realpath(tempfile.mkdtemp(prefix='jos-parity-'))
docs, home, runs = (os.path.join(work, n) for n in ('documents', 'home', 'runs'))
env = dict(os.environ, HOME=home, JOS_VECTOR_ALLOWED='allowed', JOS_VECTOR_SECRET='leak')


def call(cmd, args):
    try:
        r = subprocess.run(cmd + args, cwd=docs, env=env, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return {'exit': 'timeout (120 s)', 'stdout': None}
    except OSError as e:
        return {'exit': 'error: %s' % e, 'stdout': None}
    try:
        out = json.loads(r.stdout, parse_float=decimal.Decimal)   # the exact number written, not its double
    except ValueError:
        out = {'(stdout, not JSON)': r.stdout}
    return {'exit': r.returncode, 'stdout': out}


names = sorted(f[:-len('.expected.json')] for f in os.listdir(DOCS) if f.endswith('.expected.json'))
names = [n for n in names if not ONLY or n in ONLY]
raw, version = {}, {}
for side in ('A', 'B'):
    cmd = shlex.split(CLI[side])
    for d in (docs, home, runs):
        shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(DOCS, docs); os.makedirs(home)
    v = call(cmd, VERSION_ARGS)
    line = v['stdout'].get('(stdout, not JSON)', '') if isinstance(v['stdout'], dict) else json.dumps(v['stdout'])
    version[side] = {'exit': v['exit'], 'line': line.strip().splitlines()[0] if line.strip() else '', 'versions': SEMVER.findall(line)}
    for name in names:
        exp = json.load(open(os.path.join(docs, name + '.expected.json'), encoding='utf-8'))
        doc = os.path.join(docs, exp.get('run_document') or exp.get('document', name + '.jos'))
        res = {}
        if exp.get('validate', {}) is not None:
            res['validate'] = call(cmd, ['validate', doc, '--json'])
        res['run'] = call(cmd, ['run', doc, '--json', '--runs', runs] + exp.get('run_args', []))
        raw.setdefault(name, {})[side] = res
shutil.rmtree(work, ignore_errors=True)


# --- normalization ---------------------------------------------------------------------------------------------
def walk(v, path=''):
    """Yield (path, value) for every node, members in RFC 8785 key order."""
    yield path, v
    if isinstance(v, dict):
        for k in sorted(v, key=lambda k: k.encode('utf-16-be')):
            yield from walk(v[k], path + '/' + k)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from walk(x, path + '/' + str(i))


def normalize(res):
    """Normalize one implementation's results for one document. Returns (normalized, self-check problems)."""
    problems, labels, counters, rhash = [], {}, {}, {}
    for cmd in ('validate', 'run'):           # 1. ids, 4. receipt hashes: labels by order of first appearance
        for path, v in walk(res.get(cmd, {}).get('stdout'), '/' + cmd):
            if isinstance(v, str):
                for m in MINTED.finditer(v):
                    if m.group(0) not in labels:
                        counters[m.group(2)] = counters.get(m.group(2), 0) + 1
                        labels[m.group(0)] = '<%s_%d>' % (m.group(2), counters[m.group(2)])
            if isinstance(v, dict) and 'receipt' in v and isinstance(v.get('hash'), str):
                if receipt_hash(v) != v['hash']:
                    problems.append({'path': path + '/hash', 'kind': 'receipt hash does not verify', 'value': v['hash'], 'computed': receipt_hash(v)})
                rhash.setdefault(v['hash'], '<receipt_%d>' % (len(rhash) + 1))

    def fix(v, key=None, parent=None):
        if isinstance(v, dict):
            out = {k: fix(x, k, v) for k, x in v.items()}
            if POINTER_ONLY and isinstance(out.get('errors'), list):
                out['errors'] = [e.split(': ', 1)[0] if isinstance(e, str) else e for e in out['errors']]
            return out
        if isinstance(v, list):
            return [fix(x, key, parent) for x in v]
        if key == 'ts' and isinstance(v, str):
            return '<ts>'
        if key == 'duration_ms' and isinstance(v, NUM) and not isinstance(v, bool):
            return '<ms>'
        if key in ('issued', 'expires') and isinstance(v, str) and isinstance(parent, dict) and 'cap' in parent:
            if key == 'issued':
                return '<ts>'
            try:
                p = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))
                return '<issued+%gs>' % (p(v) - p(parent['issued'])).total_seconds()
            except (ValueError, KeyError, TypeError):
                return '<expires: %s>' % v
        if isinstance(v, str):
            if v in rhash:
                return rhash[v]
            v = MINTED.sub(lambda m: labels[m.group(0)], v)
            return v.replace(work, '<work>')
        return v
    return {cmd: {'exit': r['exit'], 'stdout': fix(r['stdout'])} for cmd, r in res.items()}, problems


# --- comparison ------------------------------------------------------------------------------------------------
def same_scalar(x, y):
    if isinstance(x, bool) or isinstance(y, bool) or x is None or y is None:
        return type(x) is type(y) and x == y
    if isinstance(x, NUM) and isinstance(y, NUM):
        return decimal.Decimal(x) == decimal.Decimal(y)   # the value of the JSON text: 1 = 1.0, 2^53+1 != 2^53
    return type(x) is type(y) and x == y


def diff(x, y, path):
    if isinstance(x, dict) and isinstance(y, dict):
        out = []
        for k in sorted(set(x) | set(y), key=lambda k: k.encode('utf-16-be')):
            if k not in y:
                out.append({'path': path + '/' + k, 'kind': 'only in A', 'a': x[k]})
            elif k not in x:
                out.append({'path': path + '/' + k, 'kind': 'only in B', 'b': y[k]})
            else:
                out += diff(x[k], y[k], path + '/' + k)
        return out
    if isinstance(x, list) and isinstance(y, list):
        out = [d for i, (p, q) in enumerate(zip(x, y)) for d in diff(p, q, path + '/' + str(i))]
        out += [{'path': path + '/' + str(i), 'kind': 'only in A', 'a': x[i]} for i in range(len(y), len(x))]
        out += [{'path': path + '/' + str(i), 'kind': 'only in B', 'b': y[i]} for i in range(len(x), len(y))]
        return out
    if isinstance(x, (dict, list)) or isinstance(y, (dict, list)) or not same_scalar(x, y):
        d = {'path': path or '/', 'kind': 'value', 'a': x, 'b': y}
        if isinstance(x, NUM) and isinstance(y, NUM) and not isinstance(x, bool) and not isinstance(y, bool) and float(x) == float(y):
            d['note'] = 'same IEEE 754 double, different number'
        return [d]
    return []


rows, total = [], 0
vdiff = [] if version['A']['versions'] == version['B']['versions'] and version['A']['exit'] == version['B']['exit'] == 0 else \
    [{'path': '/version', 'kind': 'value', 'a': version['A'], 'b': version['B']}]
total += len(vdiff)
for name in names:
    na, pa = normalize(raw[name]['A'])
    nb, pb = normalize(raw[name]['B'])
    d = [dict(p, path='A' + p['path']) for p in pa] + [dict(p, path='B' + p['path']) for p in pb]
    for cmd in ('validate', 'run'):
        if cmd in na or cmd in nb:
            d += diff(na.get(cmd), nb.get(cmd), '/' + cmd)
    total += len(d)
    rows.append({'document': name, 'exits': {c: [na.get(c, {}).get('exit'), nb.get(c, {}).get('exit')] for c in ('validate', 'run') if c in na},
                 'differences': d, 'a': na, 'b': nb})

if '--json' in a:
    print(json.dumps({'a': CLI['A'], 'b': CLI['B'], 'version': version, 'documents_dir': DOCS, 'pointer_only': POINTER_ONLY,
                      'normalizations': NORMALIZATIONS, 'documents': len(rows), 'differences': total,
                      'documents_with_differences': sum(1 for r in rows if r['differences']), 'version_differences': vdiff,
                      'results': rows}, indent=1, ensure_ascii=False, default=NUMBER_OUT))
else:
    short = lambda v: (s if len(s) <= 90 else s[:87] + '...') if (s := json.dumps(v, ensure_ascii=False, default=NUMBER_OUT)) else s
    w = max([len('document')] + [len(r['document']) for r in rows])
    print('A: %s  [%s]\nB: %s  [%s]\n' % (CLI['A'], version['A']['line'], CLI['B'], version['B']['line']))
    print('%-*s  %-12s  %-11s  %s' % (w, 'document', 'validate A/B', 'run A/B', 'differences'))
    for r in rows:
        ex = lambda c: '/'.join(str(e) for e in r['exits'][c]) if c in r['exits'] else '-'
        print('%-*s  %-12s  %-11s  %s' % (w, r['document'], ex('validate'), ex('run'), len(r['differences']) or 'none'))
    for p in vdiff:
        print('\nDIFF version: A %r, B %r' % (version['A']['line'], version['B']['line']))
    def body(p):
        if p['kind'] == 'only in A':
            return 'only in A: ' + short(p['a'])
        if p['kind'] == 'only in B':
            return 'only in B: ' + short(p['b'])
        if p['kind'] == 'value':
            return 'A ' + short(p['a']) + '  B ' + short(p['b']) + ('  (' + p['note'] + ')' if 'note' in p else '')
        return p['kind'] + ': ' + short(p.get('value'))      # a receipt hash that does not verify
    for r in rows:
        for p in r['differences']:
            print('DIFF %s %s: %s' % (r['document'], p['path'], body(p)))
    print('\nimplementation parity: %d documents, %d with differences, %d difference(s)%s' % (
        len(rows), sum(1 for r in rows if r['differences']), total, '' if not vdiff else ' (including the version)'))
sys.exit(1 if total else 0)
