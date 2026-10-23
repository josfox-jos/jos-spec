#!/usr/bin/env python3
"""Valida artefactos .jos contra un JSON Schema. Sin red. Uso: validate-jos.py --schema <schema.json> <archivos...>"""
import sys, json, argparse
from jsonschema import Draft202012Validator
ap = argparse.ArgumentParser(); ap.add_argument('--schema', required=True); ap.add_argument('files', nargs='+')
a = ap.parse_args()
schema = json.load(open(a.schema, encoding='utf-8')); V = Draft202012Validator(schema); bad = 0
for f in a.files:
    try:
        doc = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        print(f"FAIL {f}: JSON invalido: {e}"); bad += 1; continue
    errs = sorted(V.iter_errors(doc), key=lambda e: list(e.path))
    if errs:
        bad += 1; print(f"FAIL {f}")
        for e in errs[:8]: print(f"   /{'/'.join(map(str,e.path))}: {e.message[:140]}")
    else: print(f"OK   {f}")
sys.exit(1 if bad else 0)
