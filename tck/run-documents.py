#!/usr/bin/env python3
"""TCK, document level: every conformance document runs through the implementation under test and its result is
compared with the expected one. Offline. Each vector names the promises of PROMISES.md it proves, so the report says,
promise by promise, what the implementation demonstrates.

Usage:
  python3 -I tck/run-documents.py --cli "npx -y --package ./assets/josfox-jos-core-<version>.tgz jos-core"   # the kernel attached to a release
  python3 -I tck/run-documents.py --cli "python3 -I /path/to/kernel/py/bin/jos-core"
  python3 -I tck/run-documents.py --cli "<cmd>" [--documents <dir>] [--only name1,name2] [--json]
                                  [--expect-version <v>] [--version-args "version"]

A vector MAY list `"alternatives"`: other outcomes that the specification also allows (for example, a runtime that
confines a `sandbox` step runs it, while one that cannot confine it refuses it with code 5). Each alternative is an
object with `code` and `result`; the vector passes when the run matches the main expectation or one alternative.
An alternative that carries a `"claim"` (today only `"sandbox"`) rests on a property this TCK cannot observe from
outside: a run that matches it is reported as UNVERIFIED, never as a pass, because a receipt that says
`isolation: "sandbox"` is not evidence of confinement (SPEC Section 6.5). A sandbox claim is proven only by a suite
that probes confinement from outside the process (planned for 2.1).

Error messages are not part of the format: an expected `errors` entry "<JSON Pointer>: <message>" is judged by its
JSON Pointer only (the part before ": "), so an implementation does not have to reproduce the wording of the reference
kernels. --strict-messages compares the whole text; the reference kernels are judged with it.

--expect-version makes the run prove which build it tested: `<cmd> version` (or --version-args) must print <v> as a
whole word, or the TCK stops with exit code 1 before any vector runs. The version printed is in the report.

The command under test MUST accept `validate <file> --json` and `run <file> --json --runs <dir> [extra arguments]`,
print one JSON object and exit with the code the specification assigns (CONFORMANCE.md). Documents run from a copy in
a temporary directory with an empty HOME, so no `.jos/` directory of the machine takes part. A vector passes when the
validate exit code and fields (skipped when the vector sets "validate": null, as the vectors that run a folder do), the run exit code, the expected result fields (a subset comparison: every expected key
is present with an equal value) and, when pinned, the content identifier `art_` all match. Keys that measure an
implementation rather than the format (timings, ledger layout, planning cost) are reported as not judged.
Exit code 0 only if every judged vector passes; 1 if any fails; 2 if none fails and some are UNVERIFIED.
"""
import json, os, re, shlex, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
val = lambda k, d=None: a[a.index(k) + 1] if k in a else d
CLI = val('--cli')
if not CLI:
    print(__doc__); sys.exit(64)
DOCS = os.path.abspath(val('--documents', os.path.join(HERE, 'documents')))
ONLY = set(val('--only').split(',')) if val('--only') else None
NOT_JUDGED = ('ledger_kinds', 'graph', 'max_duration_ms')

work = tempfile.mkdtemp(prefix='jos-tck-')
docs = os.path.join(work, 'documents'); shutil.copytree(DOCS, docs)
home = os.path.join(work, 'home'); os.makedirs(home)
runs = os.path.join(work, 'runs')
env = dict(os.environ, HOME=home, JOS_VECTOR_ALLOWED='allowed', JOS_VECTOR_SECRET='leak')
cmd = shlex.split(CLI)
EXPECT = val('--expect-version')
VERSION = None
if EXPECT or '--json' in a:
    try:
        vr = subprocess.run(cmd + shlex.split(val('--version-args', 'version')), capture_output=True, text=True, timeout=120)
        VERSION = (vr.stdout or vr.stderr).strip().splitlines()[0] if (vr.stdout or vr.stderr).strip() else ''
    except (OSError, subprocess.TimeoutExpired) as e:
        VERSION = 'error: %s' % e
    if EXPECT and not re.search(r'(?<![\w.-])' + re.escape(EXPECT) + r'(?![\w.-])', VERSION or ''):
        print(f'TCK document level: FAIL (the command under test reports {VERSION!r}, expected version {EXPECT})')
        sys.exit(1)


def call(args):
    r = subprocess.run(cmd + args, cwd=docs, env=env, capture_output=True, text=True, timeout=120)
    try:
        return r.returncode, json.loads(r.stdout)
    except ValueError:
        return r.returncode, None


STRICT = '--strict-messages' in a
pointer = lambda e: e.split(': ', 1)[0] if isinstance(e, str) else e


def subset(exp, act, path=''):
    if not STRICT and path.endswith('/errors') and isinstance(exp, list) and isinstance(act, list):
        exp, act = [pointer(e) for e in exp], [pointer(x) for x in act]
    if isinstance(exp, dict):
        if not isinstance(act, dict):
            return [path or '/']
        out = []
        for k, v in exp.items():
            out += [path + '/' + k + ' (missing)'] if k not in act else subset(v, act[k], path + '/' + k)
        return out
    if isinstance(exp, list):
        if not isinstance(act, list) or len(exp) != len(act):
            return [(path or '/') + ' (length)']
        return [x for e, v in zip(exp, act) for x in subset(e, v, path)]
    same = exp == act and isinstance(exp, bool) == isinstance(act, bool) and (exp is None) == (act is None)
    return [] if same else [f'{path or "/"} ({exp!r} != {act!r})']


results, by_promise = [], {}
names = sorted(f[:-len('.expected.json')] for f in os.listdir(docs) if f.endswith('.expected.json'))
for name in names:
    if ONLY and name not in ONLY:
        continue
    exp = json.load(open(os.path.join(docs, name + '.expected.json'), encoding='utf-8'))
    # "run_document" names a folder that runs as a document (SPEC §9.1); "validate": null skips validate for it
    doc = os.path.join(docs, exp.get('run_document') or exp.get('document', name + '.jos'))
    bad = []
    if exp['validate'] is not None:
        vcode, v = call(['validate', doc, '--json'])
        want_v = 0 if exp['validate'].get('valid', True) else 2
        if vcode != want_v or v is None:
            bad.append(f'validate exit {vcode} (want {want_v})')
        else:
            bad += ['validate ' + x for x in subset(exp['validate'], v)]
    rcode, r = call(['run', doc, '--json', '--runs', runs] + exp.get('run_args', []))

    def judge(want_code, want_result, want_artifact):
        if r is None or rcode != want_code or r.get('code') != want_code:
            return [f'run exit {rcode} (want {want_code})']
        out = ['result ' + x for x in subset(want_result, r)]
        if want_artifact is not None and r.get('artifact') != want_artifact[0]:
            out.append(f'artifact {r.get("artifact")} != {want_artifact[0]}')
        return out
    main = judge(exp['code'], exp['result'], (exp['artifact'],) if 'artifact' in exp else None)
    claim = None
    if main:
        for alt in exp.get('alternatives', []):
            if not judge(alt['code'], alt.get('result', {}), (alt['artifact'],) if 'artifact' in alt else None):
                main, claim = [], alt.get('claim')  # an outcome the specification also allows
                break
    bad += main
    ok = not bad and claim is None
    results.append({'vector': name, 'ok': ok, 'unverified': claim if not bad else None, 'promises': exp.get('promises', []), 'problems': bad[:4],
                    'not_judged': [k for k in NOT_JUDGED if k in exp]})
    for p in exp.get('promises', []):
        by_promise.setdefault(p, {'pass': [], 'fail': [], 'unverified': []})['pass' if ok else 'unverified' if not bad else 'fail'].append(name)

shutil.rmtree(work, ignore_errors=True)
fails = [x for x in results if not x['ok'] and not x['unverified']]
unverified = [x for x in results if x['unverified']]
if '--json' in a:
    print(json.dumps({'cli': CLI, 'version': VERSION, 'expected_version': EXPECT, 'strict_messages': STRICT, 'vectors': len(results), 'pass': len(results) - len(fails) - len(unverified), 'unverified': len(unverified), 'results': results, 'promises': by_promise}, indent=1))
else:
    for x in fails:
        print(f"FAIL {x['vector']}: {'; '.join(x['problems'])}")
    for x in unverified:
        print(f"UNVERIFIED {x['vector']}: the run matches the {x['unverified']} alternative, which this TCK cannot observe")
    key = lambda p: int(re.sub(r'\D', '', p) or 0)
    for p in sorted(by_promise, key=key):
        s = by_promise[p]
        total = len(s['pass']) + len(s['fail']) + len(s['unverified'])
        print(f"{p:>4}  {'FAIL' if s['fail'] else 'UNVERIFIED' if s['unverified'] else 'PASS'}  {len(s['pass'])} of {total} vectors")
    if VERSION is not None:
        print(f"implementation under test: {VERSION}")
    print(f"TCK document level: {len(results) - len(fails) - len(unverified)} of {len(results)} vectors pass"
          + (f", {len(unverified)} UNVERIFIED" if unverified else '')
          + f"; promises proven: {sum(1 for s in by_promise.values() if not s['fail'] and not s['unverified'])} of {len(by_promise)}")
sys.exit(1 if fails else 2 if unverified else 0)
