#!/usr/bin/env python3
"""Prueba de superset: el schema .jos 2.0 es un superset aditivo estricto del 1.0.0. Sin red.

Uso: python3 -I specs/jos-format/2.0/tools/check-superset.py

Comprueba:
  (a) valid-1.0.0-* y los ejemplos de 1.0.0-hardening-iana-v1/examples/*.jos validan contra 1.0.0 Y contra 2.0
      (corpus extra: los .jos reales de 2.0/.jos/ que ya validan 1.0.0 deben seguir validando en 2.0)
  (b) valid-2.0.0-* validan contra 2.0
  (c) invalid-* fallan en 2.0
  (d) `required` de 2.0 en cada objeto que ya existe en 1.0.0 es subconjunto del de 1.0.0.
      Los objetos que solo existen en 2.0 (bloques nuevos, ramas nuevas de oneOf) solo son alcanzables
      desde propiedades opcionales nuevas: se listan como INFO y no rompen el superset.
Sale con codigo 0 si todo pasa, 1 si algo falla.
"""
import sys, json, glob, os
from jsonschema import Draft202012Validator

HERE = os.path.dirname(os.path.abspath(__file__))
FMT = os.path.normpath(os.path.join(HERE, '..'))                # repository root (public layout)
S1 = os.path.join(FMT, 'schema', '1.0.0', 'jos.schema.json')
S2 = os.path.join(FMT, 'schema', 'jos.schema.json')
TESTS = os.path.join(FMT, 'tests')
EXAMPLES = os.path.join(FMT, 'versions', '1.0.0', 'examples')
DOTJOS = os.path.join(FMT, 'examples')


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


s1, s2 = load(S1), load(S2)
for s in (s1, s2):
    Draft202012Validator.check_schema(s)
v1, v2 = Draft202012Validator(s1), Draft202012Validator(s2)

rows, bad = [], 0


def rel(p):
    return os.path.relpath(p, FMT)


def record(group, path, expect, got, ok, note=''):
    global bad
    if not ok:
        bad += 1
    rows.append((group, rel(path), expect, got, 'PASS' if ok else 'FAIL', note))


def first_err(v, doc):
    errs = sorted(v.iter_errors(doc), key=lambda e: list(map(str, e.path)))
    if not errs:
        return ''
    e = errs[0]
    return '/' + '/'.join(map(str, e.path)) + ': ' + e.message[:70]


def ok_in(v, doc):
    return v.is_valid(doc)


# (a) 1.0.0 documents: must validate in 1.0.0 and in 2.0
a_files = sorted(glob.glob(os.path.join(TESTS, 'valid-1.0.0-*.json'))) + sorted(glob.glob(os.path.join(EXAMPLES, '*.jos')))
for p in a_files:
    d = load(p)
    r1, r2 = ok_in(v1, d), ok_in(v2, d)
    record('a', p, '1.0.0=ok 2.0=ok', f"1.0.0={'ok' if r1 else 'ERR'} 2.0={'ok' if r2 else 'ERR'}", r1 and r2,
           '' if r1 and r2 else first_err(v2 if r1 else v1, d))

# (a') corpus real: .jos de 2.0/.jos/ -> si valida en 1.0.0, debe validar en 2.0
for p in sorted(glob.glob(os.path.join(DOTJOS, '**', '*.jos'), recursive=True)):
    if os.sep + 'contexto' + os.sep in p:      # contexto/ es solo lectura y contiene formatos 0.0.7
        continue
    # replays/ son salidas de corridas (copias de atomos, fuera de git): contarlas hacia variar el resultado segun las
    # corridas presentes en el arbol (G1-ANALISIS: 38 SKIP/INFO en un arbol, 46 en otro, y el texto que citan los
    # arbitros de in/preflight.json cambiaba con el)
    if os.sep + 'replays' + os.sep in p:
        continue
    d = load(p)
    r1, r2 = ok_in(v1, d), ok_in(v2, d)
    if not r1:
        rows.append(('a+', rel(p), 'si 1.0.0=ok => 2.0=ok', '1.0.0=ERR (omitido)', 'SKIP', first_err(v1, d)))
        continue
    record('a+', p, 'si 1.0.0=ok => 2.0=ok', f"1.0.0=ok 2.0={'ok' if r2 else 'ERR'}", r2, '' if r2 else first_err(v2, d))

# (b) 2.0 documents
for p in sorted(glob.glob(os.path.join(TESTS, 'valid-2.0.0-*.json'))):
    d = load(p)
    r2 = ok_in(v2, d)
    record('b', p, '2.0=ok', f"2.0={'ok' if r2 else 'ERR'}", r2, '' if r2 else first_err(v2, d))

# (c) invalid documents
c_files = sorted(glob.glob(os.path.join(TESTS, 'invalid-*.json')))
for p in c_files:
    d = load(p)
    r2 = ok_in(v2, d)
    record('c', p, '2.0=ERR', f"2.0={'ok' if r2 else 'ERR'}", not r2, '' if r2 else first_err(v2, d))
if not c_files:
    record('c', TESTS, 'hay invalid-*', 'ninguno', False)


# (d) required subset
def resolve(node, root):
    seen = 0
    while isinstance(node, dict) and '$ref' in node and seen < 20:
        ref = node['$ref']
        if not ref.startswith('#/'):
            raise SystemExit(f'$ref no local no soportado (sin red): {ref}')
        cur = root
        for part in ref[2:].split('/'):
            cur = cur[part.replace('~1', '/').replace('~0', '~')]
        node, seen = cur, seen + 1
    return node


def collect(node, root, path, out, stack=()):
    """out: {path: set(required)} para cada nodo-esquema alcanzable por properties/items/additionalProperties/oneOf/anyOf/allOf."""
    node = resolve(node, root)
    if not isinstance(node, dict):
        return
    key = id(node)
    if key in stack:
        return
    stack = stack + (key,)
    out.setdefault(path, set()).update(node.get('required', []))
    for k, sub in node.get('properties', {}).items():
        collect(sub, root, f'{path}.{k}', out, stack)
    if isinstance(node.get('additionalProperties'), dict):
        collect(node['additionalProperties'], root, f'{path}.*', out, stack)
    if isinstance(node.get('items'), dict):
        collect(node['items'], root, f'{path}[]', out, stack)
    for comb in ('oneOf', 'anyOf', 'allOf'):
        for i, sub in enumerate(node.get(comb, [])):
            collect(sub, root, f'{path}<{comb}{i}>', out, stack)


r1m, r2m = {}, {}
collect(s1, s1, '$', r1m)
collect(s2, s2, '$', r2m)
violations, new_req = [], []
for path, req2 in sorted(r2m.items()):
    if path in r1m:
        extra = req2 - r1m[path]
        if extra:
            violations.append((path, sorted(extra)))
    elif req2:
        new_req.append((path, sorted(req2)))
shared = sum(1 for p in r2m if p in r1m)
record('d', S2, f'required(2.0) <= required(1.0) en {len(r1m)} nodos de 1.0.0',
       f'{shared} nodos comparados, {len(violations)} violaciones', not violations,
       '; '.join(f'{p}+{x}' for p, x in violations))
root_ok = r2m['$'] == {'jos', 'meta'} and r1m['$'] == {'jos', 'meta'}
record('d', S2, 'required raiz == [jos, meta]', f"raiz 2.0 = {sorted(r2m['$'])}", root_ok)
missing_1 = [p for p in r1m if p not in r2m]
record('d', S2, 'todo nodo de 1.0.0 sigue existiendo', f'{len(missing_1)} ausentes', not missing_1, ', '.join(missing_1[:5]))
tops = sorted({p.split('.')[1].split('[')[0].split('<')[0] if p.count('.') >= 1 else p for p, _ in new_req})
rows.append(('d-info', f'{len(new_req)} objetos nuevos con required', 'solo via campos opcionales nuevos',
             'bloques: ' + ', '.join(tops), 'INFO', ''))

# (e) propiedades: toda propiedad de 1.0.0 existe en 2.0 y todo enum de 1.0.0 esta contenido en el de 2.0
def props_enums(node, root, path, props, enums, stack=()):
    node = resolve(node, root)
    if not isinstance(node, dict) or id(node) in stack:
        return
    stack = stack + (id(node),)
    if 'enum' in node:
        enums[path] = list(node['enum'])
    if 'const' in node:
        enums[path] = [node['const']]
    for k, sub in node.get('properties', {}).items():
        props.add(f'{path}.{k}')
        props_enums(sub, root, f'{path}.{k}', props, enums, stack)
    if isinstance(node.get('additionalProperties'), dict):
        props_enums(node['additionalProperties'], root, f'{path}.*', props, enums, stack)
    if isinstance(node.get('items'), dict):
        props_enums(node['items'], root, f'{path}[]', props, enums, stack)


p1, e1, p2, e2 = set(), {}, set(), {}
props_enums(s1, s1, '$', p1, e1)
props_enums(s2, s2, '$', p2, e2)
lost_p = sorted(p1 - p2)
# un valor de enum se conserva si sigue siendo valido en 2.0: mismo enum lo contiene, o el nodo dejo de tener enum (enumeracion abierta, SPEC-2.0 §1.3)
lost_e = sorted(f'{k}:{v}' for k, vs in e1.items() for v in vs if k in e2 and v not in e2[k])
record('e', S2, 'propiedades y enums de 1.0.0 conservados', f'{len(lost_p)} propiedades y {len(lost_e)} valores de enum perdidos',
       not lost_p and not lost_e, ', '.join(lost_p + lost_e)[:100])

# tabla
cols = ('grp', 'archivo', 'esperado', 'obtenido', 'estado', 'nota')
w = [max(len(str(r[i])) for r in rows + [cols]) for i in range(5)]
w = [min(x, y) for x, y in zip(w, (6, 70, 38, 44, 6))]
def fmt(r):
    return '  '.join(str(r[i]).ljust(w[i]) for i in range(5)) + ('  ' + r[5] if r[5] else '')
print(fmt(cols))
print('-' * (sum(w) + 10))
for r in rows:
    print(fmt(r))
n_pass = sum(1 for r in rows if r[4] == 'PASS')
n_skip = sum(1 for r in rows if r[4] in ('SKIP', 'INFO'))
print('-' * (sum(w) + 10))
print(f'{n_pass} PASS, {bad} FAIL, {n_skip} SKIP/INFO  ->  {"SUPERSET OK" if bad == 0 else "SUPERSET ROTO"}')
sys.exit(1 if bad else 0)
