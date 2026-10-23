#!/usr/bin/env python3
"""Traceability of the normative requirements: every MUST, MUST NOT, SHALL and REQUIRED sentence of SPECIFICATION.md,
the schema members it names, the vectors that cite its section, and the result of the reference kernels on those
vectors. Offline. Generated; never edited by hand.

Usage (from the repository root):
  python3 -I tools/traceability.py [--results tck-js.json --results tck-py.json] [--out TRACEABILITY.md] [--json]
                                   [--strict 2.1,2.2,5.3,6.5,6.6,9.1,9.2,9.3,12]

--strict takes a list of sections: the tool exits 1 when a requirement of one of them (or of a subsection) has no vector
that cites its section. The conformance workflow runs it over the sections whose guarantees are security or identity,
so a rule of those sections cannot lose its last vector without the check failing.

--results takes the JSON report of `tck/run-documents.py --json` for one implementation (repeatable). Without it, the
kernel column says "not run". A requirement is matched to a vector when the vector's `spec` field (document-level
vectors, `tck/documents/*.expected.json`) or its row in `tests/README.md` (schema-level vectors) cites the section of
the requirement or a subsection of it. The match is by section, not by sentence: a vector that cites a section is
counted for every requirement of that section, so the report is an upper bound of coverage, and the list of
requirements without any vector is exact.
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = sys.argv[1:]
vals = lambda k: [a[i + 1] for i, x in enumerate(a) if x == k and i + 1 < len(a)]
OUT = (vals('--out') or [os.path.join(ROOT, 'quality', 'TRACEABILITY.md')])[0]
spec = open(os.path.join(ROOT, 'SPECIFICATION.md'), encoding='utf-8').read()
schema = json.load(open(os.path.join(ROOT, 'schema', 'jos.schema.json'), encoding='utf-8'))
KW = re.compile(r'\b(MUST NOT|MUST|SHALL NOT|SHALL|REQUIRED)\b')

# 1. requirements, by section (### n.m or ## n)
reqs, sec, prefix, must_col = [], None, {}, None
SEP = lambda l: l.startswith('|') and all(re.fullmatch(r':?-+:?', c.strip()) for c in l.strip().strip('|').split('|'))
lines = spec.split('\n')
for li, line in enumerate(lines):
    m = re.match(r'#{2,4}\s+(?:Appendix\s+)?([0-9]+(?:\.[0-9]+)*|[A-C])\b(.*)$', line)
    if m:
        sec, must_col = m.group(1), None
        tick = re.findall(r'`([A-Za-z_]\w*)`', m.group(2))
        prefix[sec] = tick[0] if len(tick) == 1 else None   # "### 2.6 `meta`": members named in the section are under meta
        continue
    if sec is None:
        continue
    if line.startswith('|'):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if SEP(line):
            continue
        if li + 1 < len(lines) and SEP(lines[li + 1]):   # the header row of a table
            must_col = next((i for i, c in enumerate(cells) if KW.fullmatch(c)), None)   # a column whose title is MUST
            continue
        if must_col is not None and len(cells) > must_col:
            reqs.append({'section': sec, 'text': re.sub(r'\*', '', cells[0]) + ' MUST: ' + cells[must_col]})
            continue
        lvl = [c for c in cells if KW.fullmatch(c)]
        if lvl:   # a row whose requirement level is a cell ("| `jos.kind` | MUST | ... |")
            reqs.append({'section': sec, 'text': ' · '.join(cells)})
            continue
    else:
        must_col = None
    if not KW.search(line):
        continue
    text = re.sub(r'^\s*(?:[-*]|\d+\.)\s+', '', line.strip().strip('|'))
    for s in re.split(r'(?<=[.;])\s+(?=[A-Z`*])', text):
        if KW.search(s):
            reqs.append({'section': sec, 'text': s.strip()})
for i, r in enumerate(reqs, 1):
    r['id'] = 'R%03d' % i


# 2. schema members named by a requirement
def deref(node, seen):
    r = node.get('$ref') if isinstance(node, dict) else None
    if isinstance(r, str) and r.startswith('#/') and r not in seen:
        t = schema
        for part in r[2:].split('/'):
            t = t.get(part, {}) if isinstance(t, dict) else {}
        return t, seen | {r}
    return node, seen


def members(node, path='', seen=frozenset()):
    if isinstance(node, dict):
        for k, v in (node.get('properties') or {}).items():
            q = path + '.' + k if path else k
            yield q, v
            t, s2 = deref(v, seen)
            if t is not v:
                yield q, t
            yield from members(t, q, s2)
        for key in ('items', 'additionalProperties'):
            if isinstance(node.get(key), dict):
                t, s2 = deref(node[key], seen)
                yield from members(t, path + '[]' if key == 'items' else path + '.*', s2)
        for key in ('allOf', 'anyOf', 'oneOf'):
            for v in node.get(key) or []:
                t, s2 = deref(v, seen)
                yield from members(t, path, s2)


SCH = {}
for p, n in members(schema):
    SCH.setdefault(p, set()).update(k for k in ('type', 'enum', 'const', 'pattern', 'minimum', 'maximum', 'minLength', 'maxLength', 'minItems', 'maxItems', 'required', 'additionalProperties', '$ref', 'format') if k in n)
leaf = {}
for p, k in SCH.items():
    leaf.setdefault(p.split('.')[-1], set()).add(p)
for r in reqs:
    hits = set()
    for tok in re.findall(r'`([A-Za-z_][\w.\-\[\]*]*)`', r['text']):
        t = tok.replace('[*]', '[]').strip('.')
        if t in SCH:
            hits.add(t)
        elif prefix.get(r['section']) and prefix[r['section']] + '.' + t in SCH:
            hits.add(prefix[r['section']] + '.' + t)
        elif '.' not in t and t in leaf and len(leaf[t]) <= 3:
            hits |= leaf[t]
    r['schema'] = sorted(hits)

# 3. vectors that cite each section
cites = {}
for p in sorted(glob.glob(os.path.join(ROOT, 'tck', 'documents', '*.expected.json'))):
    name = os.path.basename(p)[:-len('.expected.json')]
    s = json.load(open(p, encoding='utf-8')).get('spec', [])
    for c in ([s] if isinstance(s, str) else s):
        m = re.match(r'^(?:SPEC-2\.0\s+)?§\s*([0-9]+(?:\.[0-9]+)*)$', c.strip())
        if m:
            cites.setdefault(m.group(1), set()).add(name)
readme = open(os.path.join(ROOT, 'tests', 'README.md'), encoding='utf-8').read()
for m in re.finditer(r'^\| `((?:valid|invalid)-[^`]+)` \|.*$', readme, re.M):
    for s in re.findall(r'Section\s+([0-9]+(?:\.[0-9]+)*)', m.group(0)):
        cites.setdefault(s, set()).add('tests/' + m.group(1))

# 4. results of implementations
res = {}
for f in vals('--results'):
    j = json.load(open(f, encoding='utf-8'))
    res[j.get('version') or j.get('cli')] = {x['vector']: x['ok'] for x in j['results']}

rows = []
for r in reqs:
    near = lambda sec: set().union(set(), *[v for s, v in cites.items() if s == sec or s.startswith(sec + '.')])
    vs = sorted(near(r['section']))
    via = sorted(set(re.findall(r'§\s*([0-9]+(?:\.[0-9]+)*)', r['text'])) - {r['section']})
    if not vs and via:   # a requirement that only points to other sections (the conformance table) takes their vectors
        vs = sorted(set().union(*[near(s) for s in via]))
        r['via'] = via
    r['vectors'] = vs
    doc = [v for v in vs if not v.startswith('tests/')]
    if res:
        r['kernels'] = {impl: (sum(1 for v in doc if m.get(v)), sum(1 for v in doc if v in m)) for impl, m in res.items()}
    r['status'] = ('vector via §' + ', §'.join(r['via']) if r.get('via') else 'vector') if vs else ('schema only' if r['schema'] else 'no vector')
    rows.append(r)

count = {k: sum(1 for r in rows if r['status'].startswith(k)) for k in ('vector', 'schema only', 'no vector')}
if '--json' in a:
    print(json.dumps({'requirements': rows, 'count': count}, indent=1, ensure_ascii=False)); sys.exit(0)
L = ['<!-- generated by tools/traceability.py; do not edit -->', '', '# Traceability of the normative requirements', '',
     f"{len(rows)} requirements (sentences with MUST, MUST NOT, SHALL or REQUIRED in `SPECIFICATION.md`). "
     f"With at least one vector that cites their section: {count['vector']}. With schema members only: {count['schema only']}. "
     f"With no vector and no schema member: {count['no vector']}. The match is by section (see the header of the tool), so the first number is an upper bound; the last list is exact.", '']
if res:
    L += ['Implementations whose results are included: ' + ', '.join(f'`{k}`' for k in res) + '.', '']
L += ['| Id | § | Requirement | Schema members | Vectors citing the section | ' + ' | '.join(f'`{k}`' for k in res) + (' | ' if res else '') + 'Status |',
      '|---|---|---|---|---|' + '---|' * len(res) + '---|']
for r in rows:
    t = r['text'].replace('|', '\\|')
    t = t if len(t) <= 220 else t[:217] + '…'
    vs = ', '.join(f'`{v}`' for v in r['vectors'][:4]) + (f' and {len(r["vectors"]) - 4} more' if len(r['vectors']) > 4 else '') or '—'
    k = ''.join(f" {p} of {n} pass |" if n else ' — |' for p, n in r.get('kernels', {}).values())
    L.append(f"| {r['id']} | {r['section']} | {t} | {', '.join('`' + s + '`' for s in r['schema'][:3]) or '—'} | {vs} |{k} {r['status']} |")
L += ['', '## Requirements without any vector', ''] + [f"- {r['id']} (§{r['section']}, {r['status']}): {r['text']}" for r in rows if not r['status'].startswith('vector')]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print(f"traceability: {len(rows)} requirements; vector {count['vector']}, schema only {count['schema only']}, no vector {count['no vector']} · {OUT}")
strict = vals('--strict')
if strict:
    secs = [x.strip() for x in strict[0].split(',') if x.strip()]
    missing = [r for r in rows if not r['status'].startswith('vector') and any(r['section'] == s or r['section'].startswith(s + '.') for s in secs)]
    for r in missing:
        print(f"  no vector in a strict section: {r['id']} (§{r['section']}): {r['text'][:140]}")
    print('traceability --strict ' + ','.join(secs) + ': ' + ('PASS' if not missing else f'FAIL ({len(missing)})'))
    sys.exit(1 if missing else 0)
