#!/usr/bin/env python3
"""PASO HUMANO. No hace red. Lee replays/<run>/urls.json y exige que cada URL tenga http_status, sha256 y verificado_por (persona) y fecha.
Excepciones: un dominio de documentacion (RFC 2606 / RFC 6761) nunca se resuelve; una URL del propio repositorio que apunta al tag que se
registra (raw.githubusercontent.com/josfox-jos/jos-spec/v2.0.0/...) y cuya `nota` dice que resuelve cuando el tag se publique queda
"pendiente de publicacion": no cuenta como sin verificar (exit 0), se lista, y hay que volver a correr el check despues de publicar.
Uso: url-check.py --human <urls.json>"""
import sys, json, re
f = sys.argv[-1]; u = json.load(open(f, encoding='utf-8'))
EX = re.compile(r'^https?://([a-z0-9-]+\.)*(example\.(com|net|org)|[a-z0-9-]+\.example)(/|:|$)', re.I)      # RFC 2606 / RFC 6761
OWN_TAG = re.compile(r'^https://raw\.githubusercontent\.com/josfox-jos/jos-spec/v2\.0\.0/')                  # the project's own repository, the tag being registered
WAITS = re.compile(r'tag .{0,40}\bis published\b', re.I)                                                    # the entry says it resolves when the tag is published
ex = [x['url'] for x in u if EX.match(x['url'])]
ok = lambda x: x.get('http_status') == 200 and x.get('sha256') and x.get('verificado_por') and x.get('fecha')
pend = [x['url'] for x in u if x['url'] not in ex and not ok(x) and OWN_TAG.match(x['url']) and WAITS.search(x.get('nota') or '') and x.get('verificado_por') and x.get('fecha')]
bad = [x['url'] for x in u if x['url'] not in ex and x['url'] not in pend and not ok(x)]
print(f"urls: {len(u)}  sin verificar: {len(bad)}  ejemplos (RFC 2606, no se resuelven): {len(ex)}  pending publication: {len(pend)}")
for b in bad: print('  ', b)
if pend:
    print(f"pending publication: {len(pend)} URL(s) resolve after the tag is published: re-run E4 after publication")
    for q in pend: print('  ', q)
sys.exit(1 if bad or not u else 0)
