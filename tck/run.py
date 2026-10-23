#!/usr/bin/env python3
"""TCK, schema level: valid vectors must validate, invalid vectors must fail. Offline. Exit 0 only when both hold.
Usage: python3 -I tck/run.py [--tests <dir>]   (needs the jsonschema package; --tests defaults to tests/ of this repository)"""
import glob, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, 'tools', 'validate-jos.py'); SCHEMA = os.path.join(ROOT, 'schema', 'jos.schema.json')
T = sys.argv[sys.argv.index('--tests') + 1] if '--tests' in sys.argv else os.path.join(ROOT, 'tests')
valid = sorted(glob.glob(os.path.join(T, 'valid-*.json'))); invalid = sorted(glob.glob(os.path.join(T, 'invalid-*.json')))
if not valid or not invalid: print('TCK schema level: FAIL (no vectors in', T + ')'); sys.exit(1)
ok = True
r = subprocess.run([sys.executable, '-I', V, '--schema', SCHEMA, *valid]); print(f'valid vectors: {len(valid)} ->', 'PASS' if r.returncode == 0 else 'FAIL'); ok &= r.returncode == 0
bad = 0
for f in invalid:
    r = subprocess.run([sys.executable, '-I', V, '--schema', SCHEMA, f], capture_output=True)
    if r.returncode == 0: print('  invalid vector validated:', os.path.basename(f)); bad += 1
print(f'invalid vectors: {len(invalid)} ->', 'PASS' if bad == 0 else f'FAIL ({bad} validated)'); ok &= bad == 0
print('TCK schema level:', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
