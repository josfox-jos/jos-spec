#!/usr/bin/env node
// tools/guard-repo-jos.mjs — EL QUALITY GATE DE UN REPO DE `.jos`: ¿está a la altura de A2A y MCP?
//
//   node tools/guard-repo-jos.mjs --repo josfox-jos/jos-spec            un repo de GitHub (gh api, sólo lectura)
//   node tools/guard-repo-jos.mjs --dir /ruta/al/repo                   un checkout local
//   node tools/guard-repo-jos.mjs --repo … --perfil spec|sdk|cli|extension  qué clase de repo es (default: spec)
//   node tools/guard-repo-jos.mjs --repo … --ref hardening/iana-v1-spec     una rama que no es la default
//   node tools/guard-repo-jos.mjs … --json                              datos por stdout
//   node tools/guard-repo-jos.mjs … --minimo 80                         sale 1 si la nota es menor (default 100 para spec)
//   node tools/guard-repo-jos.mjs … --salida ./quality                  escribe QUALITY.md y quality-report.json
//   Perfiles (clases del JOS Standards Guardian): spec · profile · reference · implementation · sdk · tooling · catalog · extension.
//   Decisión: BLOCK si falta un P0 (aunque la nota sea 99) · PASS_CON_AVISOS si falta un P1 · RELEASE_READY.
//
// ── POR QUÉ ────────────────────────────────────────────────────────────────────────────────────
// El dueño lo dijo el 24 sep 2026: el repo del estándar es «la IANA de .jos» y tiene que estar a la
// altura de google A2A o de MCP. «A la altura» no es un adjetivo: es una lista de archivos y
// mecanismos que esos repos tienen y que se pueden comprobar con un comando. Esta herramienta es esa
// lista, como DATO (`GATE`), con un check por requisito, y una nota de 0 a 100. Falla cerrado: lo que
// no se pudo leer cuenta como ausente, y se dice.
//
// Las fuentes de cada requisito están en docs/JOS-REPO-SPEC.md (medido sobre a2aproject/A2A y
// modelcontextprotocol/modelcontextprotocol el 24 sep 2026).
//
// Cero dependencias. ESM. Node >= 22.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
// 2026-10-14: antes importaba un módulo auxiliar que no existe en este repositorio; misma semántica inline.
const esteEsElPrograma = (u) => { try { return process.argv[1] && pathToFileURL(fs.realpathSync(process.argv[1])).href === u; } catch { return false; } };

// Las clases de repo del JOS Standards Guardian (memo del 24 sep): primero se clasifica, luego se aplica el gate.
const PERFILES = Object.freeze(['spec', 'profile', 'reference', 'implementation', 'sdk', 'tooling', 'catalog', 'extension']);
const ALIAS_PERFIL = Object.freeze({ cli: 'tooling', tool: 'tooling', ref: 'reference', impl: 'implementation' });
const CODIGO = ['sdk', 'tooling', 'implementation', 'extension'];
// Niveles: P0 bloquea el release aunque la nota sea 99; P1 es calidad de estándar; P2 es clase mundial.
export const NIVELES = Object.freeze({ P0: 'bloquea', P1: 'estándar', P2: 'clase mundial' });

// Cada requisito: id · nivel (obligatorio | recomendado) · perfiles a los que aplica · peso · cómo se
// comprueba (`archivos`: alguno existe; `contenido`: regex sobre un archivo; `fn`: función sobre el
// árbol) · por qué (con el referente que lo tiene).
export const GATE = Object.freeze([
  { id: 'licencia', tier: 'P0', perfiles: PERFILES, peso: 10, archivos: ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'LICENCE'], por: 'Sin licencia nadie puede usar el estándar. A2A: Apache-2.0; MCP: MIT.' },
  { id: 'readme', tier: 'P0', perfiles: PERFILES, peso: 6, archivos: ['README.md'], contenido: { archivo: 'README.md', regex: /(qué es|what is|overview|introducci|getting started|quick ?start|instal)/i }, por: 'README con qué es, para quién y cómo empezar (A2A, MCP, antigravity-sdk).' },
  { id: 'schema', tier: 'P0', perfiles: ['spec'], peso: 12, fn: (t) => t.some((p) => /(^|\/)(schema|schemas|specification)\/.*\.(json|ts|proto)$/i.test(p)), por: 'La spec vive como esquema formal en el repo, no sólo como prosa. A2A: specification/json/a2a.json + .proto; MCP: schema/<versión>/schema.ts + schema.json generado.' },
  { id: 'spec_prosa', tier: 'P0', perfiles: ['spec'], peso: 8, fn: (t) => t.some((p) => /^SPECIFICATION\.mdx?$/i.test(p)) || t.some((p) => /(^|\/)(docs?|specification)\/.*\.(md|mdx)$/i.test(p)) || t.some((p) => /^jos\.v\d+\.\d+\.\d+\.md$/.test(p)) || t.some((p) => /^SPEC-\d+\.\d+(\.\d+)?\.md$/.test(p)), por: 'La prosa normativa versionada junto al esquema (A2A docs/specification.md; MCP docs/specification/<versión>/).' },
  { id: 'versionado', tier: 'P0', perfiles: PERFILES, peso: 8, fn: (t, a) => t.some((p) => /versioning/i.test(p)) || t.some((p) => /release-please|cut-release|publish-release/i.test(p)) || (t.some((p) => /^changelog/i.test(p)) && (a.tags || []).length > 0), contenido: { archivo: 'README.md', regex: /(semver|semantic versioning|versionado|versioning policy)/i }, por: 'Cómo se versiona la spec y qué rompe compatibilidad (MCP: docs/specification/versioning.mdx; A2A: releases semver).' },
  { id: 'changelog', tier: 'P0', perfiles: PERFILES, peso: 6, fn: (t) => t.some((p) => /(^|\/)changelog(\.md|\.mdx)?$/i.test(p)), por: 'Qué cambió entre versiones, legible sin abrir el git log (MCP changelog por versión; A2A releases).' },
  { id: 'contributing', tier: 'P0', perfiles: PERFILES, peso: 6, archivos: ['CONTRIBUTING.md', '.github/CONTRIBUTING.md', 'docs/CONTRIBUTING.md'], por: 'Cómo se propone un cambio (A2A y MCP lo tienen; MCP además SEPs).' },
  { id: 'conducta', tier: 'P0', perfiles: PERFILES, peso: 4, archivos: ['CODE_OF_CONDUCT.md', '.github/CODE_OF_CONDUCT.md'], por: 'Código de conducta (A2A, MCP).' },
  { id: 'seguridad', tier: 'P0', perfiles: PERFILES, peso: 6, archivos: ['SECURITY.md', '.github/SECURITY.md'], por: 'A quién reportar una vulnerabilidad y cómo (A2A, MCP).' },
  { id: 'gobernanza', tier: 'P0', perfiles: ['spec'], peso: 6, archivos: ['GOVERNANCE.md', 'docs/GOVERNANCE.md', 'docs/community/governance.md', 'docs/community/governance.mdx'], por: 'Quién decide y cómo (MCP docs/community/governance; A2A con un GOVERNANCE de fundación neutral).' },
  { id: 'maintainers', tier: 'P0', perfiles: ['spec'], peso: 4, archivos: ['MAINTAINERS.md', '.github/MAINTAINERS.md', 'docs/MAINTAINERS.md'], por: 'Quiénes mantienen y cómo se entra o se sale (A2A y MCP lo tienen los dos).' },
  { id: 'security_txt', tier: 'P1', perfiles: ['spec'], peso: 2, fn: (t) => t.some((p) => /(^|\/)\.well-known\/security\.txt$/.test(p)), por: 'RFC 9116: a quién reportar, legible por máquinas (MCP docs/.well-known/security.txt).' },
  { id: 'codeowners', tier: 'P1', perfiles: PERFILES, peso: 3, archivos: ['CODEOWNERS', '.github/CODEOWNERS', 'docs/CODEOWNERS'], por: 'Dueños por ruta (A2A, MCP).' },
  { id: 'ci', tier: 'P0', perfiles: PERFILES, peso: 8, fn: (t) => t.some((p) => /^\.github\/workflows\/.*\.ya?ml$/.test(p)), por: 'CI en cada PR: valida el esquema, los ejemplos y la prosa (A2A y MCP tienen workflows).' },
  { id: 'ejemplos', tier: 'P0', perfiles: ['spec', 'profile', 'reference', ...CODIGO], peso: 8, fn: (t) => t.some((p) => /(^|\/)(examples?|samples?|ejemplos)\//i.test(p)), contenido: { archivo: 'README.md', regex: /(github\.com\/[^\s)]*(samples?|examples?)|\bsamples?\b|\bexamples?\b)/i }, por: 'Ejemplos ejecutables o validables (A2A samples en repo hermano; MCP examples; antigravity-sdk examples/).' },
  { id: 'validador_o_tests', tier: 'P0', perfiles: PERFILES, peso: 8, fn: (t) => t.some((p) => /(^|\/)(tests?|__tests__|conformance|validator|validate)/i.test(p)) || t.some((p) => /\.test\.(m?js|ts|py)$/.test(p)) || t.some((p) => /^\.github\/workflows\/.*(lint|test|valid|check|conform|schema|spell).*\.ya?ml$/i.test(p)), por: 'Un estándar sin validador es una convención (jsfx-site/pass/jos.mjs). A2A: tests de conformidad en SDKs; MCP: validación del schema en CI.' },
  { id: 'releases', tier: 'P0', perfiles: PERFILES, peso: 5, fn: (t, ctx) => (ctx.tags || []).length > 0, por: 'Tags/releases con la versión de la spec (A2A v0.3.x; MCP por fecha 2025-06-18).' },
  { id: 'llms_txt', tier: 'P1', perfiles: ['spec'], peso: 3, archivos: ['llms.txt', 'llms-full.txt', 'docs/llms.txt'], por: 'Los agentes leen la spec: A2A publica llms.txt.' },
  { id: 'implementaciones', tier: 'P0', perfiles: ['spec'], peso: 6, fn: (t) => t.some((p) => /(^|\/)(sdks?|implementations?|registry|ecosystem)(\/|\.mdx?$)/i.test(p)), contenido: { archivo: 'README.md', regex: /(implementaci|implementation|\bsdks?\b|pip install|npm install|go get|registry|cat[aá]logo|ecosystem|ecosistema)/i }, por: 'La spec lista dónde están las implementaciones y SDKs (A2A README → a2a-python, a2a-js…; MCP → SDKs y registry).' },
  { id: 'proceso_propuestas', tier: 'P1', perfiles: ['spec'], peso: 3, fn: (t) => t.some((p) => /(^|\/)(seps?|proposals?|rfcs?|propuestas)\//i.test(p)) || t.some((p) => /\.github\/ISSUE_TEMPLATE\//.test(p)), por: 'Propuestas con plantilla (MCP SEPs; A2A issue templates).' },
  // ── Los P0 propios de un repo de ESTÁNDAR (memo del 24 sep, §8 y §10) ──────────────────────────
  { id: 'normativa_sincronizada', tier: 'P0', perfiles: ['spec'], peso: 10, solo_jos: true, fn: (t, a) => reglaDeOro(t, a).ok, detalle: (t, a) => reglaDeOro(t, a).dice, por: 'REGLA DE ORO: cada propiedad raíz del JSON Schema se define en la prosa normativa, y viceversa. Un cambio que sólo toca una de las dos FALLA.' },
  { id: 'mime_consistente', tier: 'P0', perfiles: ['spec'], peso: 4, solo_jos: true, fn: (t, a) => mimeConsistente(t, a).ok, detalle: (t, a) => mimeConsistente(t, a).dice, por: 'El media type (application/vnd.jos+json) es el mismo en README, SPECIFICATION, IANA y CONFORMANCE; un nombre de trabajo anterior no aparece salvo como historia.' },
  { id: 'vectores_invalidos', tier: 'P0', perfiles: ['spec'], peso: 4, solo_jos: true, fn: (t) => t.some((p) => /(^|\/)(examples\/invalid|conformance\/(vectors|invalid)|test-vectors|tck)\//i.test(p) || /(^|\/)tests?\/invalid[^/]*\.(json|jos)$/i.test(p)), por: 'Ejemplos que DEBEN fallar: sin ellos el validador sólo demuestra que acepta, no que rechaza (OpenAPI, OCI image-spec, MCP).' },
  { id: 'release_process', tier: 'P1', perfiles: ['spec'], peso: 3, archivos: ['RELEASE_PROCESS.md', 'docs/RELEASE_PROCESS.md', 'docs/release-process.md', 'RELEASING.md'], por: 'Cómo se corta una versión, quién la firma y qué la bloquea (AsyncAPI, OpenAPI).' },
  { id: 'pr_template', tier: 'P1', perfiles: PERFILES, peso: 2, archivos: ['.github/PULL_REQUEST_TEMPLATE.md', '.github/pull_request_template.md', 'PULL_REQUEST_TEMPLATE.md'], por: 'Plantilla de PR con la lista de sincronización (prosa, esquema, vectores).' },
  { id: 'versiones_inmutables', tier: 'P2', perfiles: ['spec'], peso: 3, fn: (t) => t.some((p) => /^(versions|schema)\/\d+\.\d+\.\d+\//.test(p)) || t.some((p) => /^schema\/\d{4}-\d{2}-\d{2}\//.test(p)), por: 'Cada versión publicada queda inmutable en su carpeta (MCP schema/<fecha>/, OpenAPI versions/).' },
  { id: 'tck', tier: 'P2', perfiles: ['spec', 'profile'], peso: 3, fn: (t) => t.some((p) => /(^|\/)tck\//i.test(p)), por: 'Test Compatibility Kit para implementaciones (A2A SDKs, open-workflow ctk/).' },
  { id: 'package_publicable', tier: 'P0', perfiles: CODIGO, peso: 10, archivos: ['package.json', 'pyproject.toml', 'setup.py', 'Cargo.toml', 'go.mod'], por: 'Un SDK/CLI se instala desde un registro (npm/PyPI) y su repo lo declara.' },
  { id: 'manifiesto_extension', tier: 'P0', perfiles: ['extension'], peso: 10, contenido: { archivo: 'package.json', regex: /"contributes"\s*:/ }, por: 'Una extensión de VS Code declara contributes (languages, grammars, jsonValidation).' },
]);

const MIME = 'application/vnd.jos+json';
// the working name used before the registration, matched by pattern so the tool itself never carries it
const MIME_VIEJO_RE = /application\/vnd\.jos(?:fox)\+json/;
function esquemaDe(t, a) {
  const ruta = t.find((p) => /(^|\/)schema\/(.*\/)?jos\.schema\.json$/.test(p)) || t.find((p) => /(^|\/)(schema|schemas|specification)\/.*\.json$/i.test(p));
  if (!ruta) return null;
  try { return { ruta, json: JSON.parse(a.leer(ruta) || 'null') }; } catch { return { ruta, json: null }; }
}
function prosaDe(t, a) {
  const ruta = t.find((p) => /^SPECIFICATION\.md$/i.test(p)) || t.find((p) => /^SPEC-\d+\.\d+(\.\d+)?\.md$/.test(p)) || t.find((p) => /^jos\.v\d+\.\d+\.\d+\.md$/.test(p)) || t.find((p) => /(^|\/)(docs|specification)\/.*spec.*\.mdx?$/i.test(p));
  return ruta ? { ruta, texto: a.leer(ruta) || '' } : null;
}
/** Regla de oro: propiedades raíz del esquema ⊆ prosa, y las que la prosa nombra con backticks a nivel raíz ⊆ esquema. */
export function reglaDeOro(t, a) {
  const e = esquemaDe(t, a), p = prosaDe(t, a);
  if (!e || !e.json) return { ok: false, dice: 'sin esquema JSON legible' };
  if (!p) return { ok: false, dice: 'sin prosa normativa (SPECIFICATION.md o jos.vX.Y.Z.md)' };
  const props = Object.keys(e.json.properties || {});
  const menciona = (k) => new RegExp('`' + k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '`|\\b' + k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b').test(p.texto);
  const sinProsa = props.filter((k) => !menciona(k));
  const requeridos = (e.json.required || []).filter((k) => !menciona(k));
  const dice = [];
  if (sinProsa.length) dice.push(`en el esquema y NO en ${p.ruta}: ${sinProsa.join(', ')}`);
  if (requeridos.length) dice.push(`required sin definir en la prosa: ${requeridos.join(', ')}`);
  return { ok: dice.length === 0, dice: dice.join(' · ') || `${props.length} propiedades raíz definidas en ${p.ruta}` };
}
export function mimeConsistente(t, a) {
  const archivos = ['README.md', 'SPECIFICATION.md', 'IANA.md', 'CONFORMANCE.md'].concat(t.filter((f) => /^SPEC-\d+\.\d+(\.\d+)?\.md$/.test(f))).filter((f) => t.includes(f));
  if (!archivos.length) return { ok: false, dice: 'sin README/SPECIFICATION/IANA/CONFORMANCE' };
  const sin = archivos.filter((f) => !(a.leer(f) || '').includes(MIME));
  const viejo = archivos.filter((f) => { const x = a.leer(f) || ''; return MIME_VIEJO_RE.test(x) && !/deprecated|historic|anterior|viejo/i.test(x); });
  const dice = [];
  if (sin.length) dice.push(`sin ${MIME}: ${sin.join(', ')}`);
  if (viejo.length) dice.push(`nombre de trabajo anterior sin marcar como histórico en: ${viejo.join(', ')}`);
  return { ok: dice.length === 0, dice: dice.join(' · ') || `${MIME} en ${archivos.join(', ')}` };
}

function git(args, cwd) { return spawnSync('git', args, { cwd, encoding: 'utf8' }); }

/** Árbol y metadatos de un checkout local. */
export function arbolLocal(dir) {
  const raiz = path.resolve(dir);
  const ls = git(['ls-files'], raiz);
  const tree = ls.status === 0 ? ls.stdout.split('\n').filter(Boolean) : caminar(raiz);
  const tagsR = git(['tag', '--list'], raiz);
  const tags = tagsR.status === 0 ? tagsR.stdout.split('\n').filter(Boolean) : [];
  return { origen: `dir:${raiz}`, tree, tags, leer: (rel) => { try { return fs.readFileSync(path.join(raiz, rel), 'utf8'); } catch { return null; } } };
}
function caminar(raiz, rel = '') {
  const out = [];
  for (const e of fs.readdirSync(path.join(raiz, rel), { withFileTypes: true })) {
    if (e.name === '.git' || e.name === 'node_modules') continue;
    const r = rel ? `${rel}/${e.name}` : e.name;
    if (e.isDirectory()) out.push(...caminar(raiz, r)); else out.push(r);
  }
  return out;
}

/** Árbol y metadatos de un repo de GitHub, con gh (sólo lectura). */
export function arbolGitHub(repo, ref = null) {
  // 2026-10-14: maxBuffer explícito; el default de 1 MiB vaciaba en silencio el árbol de repos grandes (temporalio/temporal, 4732 entradas) y el gate daba 21.
  const gh = (args) => { const r = spawnSync('gh', ['api', ...args], { encoding: 'utf8', timeout: 60_000, maxBuffer: 64 * 1024 * 1024 }); return r.status === 0 ? r.stdout : null; };
  const meta = JSON.parse(gh([`repos/${repo}`]) || 'null');
  if (!meta) throw Object.assign(new Error(`no se pudo leer ${repo} con gh api (¿existe? ¿hay sesión?)`), { code: 'sin_repo' });
  const branch = ref || meta.default_branch;
  const t = JSON.parse(gh([`repos/${repo}/git/trees/${branch}?recursive=1`]) || '{"tree":[]}');
  const tree = (t.tree || []).filter((x) => x.type === 'blob').map((x) => x.path);
  const tags = (JSON.parse(gh([`repos/${repo}/tags?per_page=100`]) || '[]')).map((x) => x.name);
  const cache = new Map();
  const leer = (rel) => {
    if (cache.has(rel)) return cache.get(rel);
    const j = JSON.parse(gh([`repos/${repo}/contents/${rel}?ref=${branch}`]) || 'null');
    const txt = j && j.content ? Buffer.from(j.content, 'base64').toString('utf8') : null;
    cache.set(rel, txt); return txt;
  };
  return { origen: `github:${repo}@${branch}`, tree, tags, leer, meta: { private: meta.private, license: meta.license?.spdx_id || null, pushed_at: meta.pushed_at, stars: meta.stargazers_count, description: meta.description } };
}

/** Evalúa un árbol contra el GATE para un perfil. Puro. */
export function evaluarRepo(arbol, { perfil = 'spec' } = {}) {
  perfil = ALIAS_PERFIL[perfil] || perfil;
  if (!PERFILES.includes(perfil)) throw Object.assign(new Error(`perfil «${perfil}» desconocido; los que hay: ${PERFILES.join(', ')}`), { code: 'perfil_desconocido' });
  const set = new Set(arbol.tree);
  const existe = (rel) => set.has(rel);
  const resultados = [];
  // ¿Es un repo de .jos? Si no lo es (A2A, MCP, OpenAPI…) los checks propios de .jos no aplican ni cuentan.
  const esJos = arbol.tree.some((p) => /jos\.schema\.json$/.test(p)) || (arbol.leer('README.md') || '').includes(MIME);
  for (const g of GATE) {
    if (!g.perfiles.includes(perfil)) continue;
    if (g.solo_jos && !esJos) continue;
    let ok = false; let evidencia = '';
    if (g.archivos) { const hit = g.archivos.find(existe); if (hit) { ok = true; evidencia = hit; } }
    if (!ok && g.contenido) { const txt = arbol.leer(g.contenido.archivo); if (txt && g.contenido.regex.test(txt)) { ok = true; evidencia = `${g.contenido.archivo} ~ ${g.contenido.regex}`; } }
    if (!ok && g.fn) { try { ok = !!g.fn(arbol.tree, arbol); if (ok) evidencia = 'árbol'; } catch { ok = false; } }
    let detalle = null; if (g.detalle) { try { detalle = g.detalle(arbol.tree, arbol); } catch (e) { detalle = e.message; } }
    resultados.push({ id: g.id, tier: g.tier, peso: g.peso, ok, evidencia: ok ? (detalle || evidencia) : (detalle || 'ausente'), por: g.por });
  }
  const total = resultados.reduce((n, r) => n + r.peso, 0);
  const suma = resultados.filter((r) => r.ok).reduce((n, r) => n + r.peso, 0);
  const nota = Math.round((suma / total) * 100);
  const p0 = resultados.filter((r) => r.tier === 'P0' && !r.ok).map((r) => r.id);
  const p1 = resultados.filter((r) => r.tier === 'P1' && !r.ok).map((r) => r.id);
  const p2 = resultados.filter((r) => r.tier === 'P2' && !r.ok).map((r) => r.id);
  // La decisión NO es la nota: un P0 rojo bloquea aunque la nota sea 99.
  const decision = p0.length ? 'BLOCK' : p1.length ? 'PASS_CON_AVISOS' : 'RELEASE_READY';
  return { origen: arbol.origen, perfil, es_jos: esJos, nota, decision, p0_faltan: p0, p1_faltan: p1, p2_faltan: p2, obligatorios_faltan: p0, a_la_altura: p0.length === 0, resultados, meta: arbol.meta || null };
}

export function narrar(v) {
  const L = [`${v.decision === 'BLOCK' ? '✖' : v.decision === 'PASS_CON_AVISOS' ? '◑' : '✓'} ${v.origen} · perfil ${v.perfil} · ${v.decision} · nota ${v.nota}/100${v.p0_faltan.length ? ` · P0 en rojo: ${v.p0_faltan.join(', ')}` : ''}${v.p1_faltan.length ? ` · P1: ${v.p1_faltan.join(', ')}` : ''}`];
  if (v.meta) L.push(`  ${v.meta.private ? 'PRIVADO' : 'público'} · licencia ${v.meta.license || 'NINGUNA'} · último push ${String(v.meta.pushed_at || '').slice(0, 10)} · ${v.meta.stars ?? '?'} estrellas`);
  for (const r of v.resultados) L.push(`  ${r.ok ? '✓' : (r.tier === 'P0' ? '✖' : '◑')} ${r.tier} ${r.id.padEnd(24)} ${String(r.peso).padStart(2)}  ${r.ok ? r.evidencia : `${r.por}${r.evidencia && r.evidencia !== 'ausente' ? ` → ${r.evidencia}` : ''}`}`);
  return L.join('\n');
}

export function qualityMd(v) {
  const L = [`# QUALITY — ${v.origen}`, '', `> Generado por \`tools/guard-repo-jos.mjs\` (JOS Standards Guardian). Perfil **${v.perfil}** · decisión **${v.decision}** · nota ${v.nota}/100 (KPI; la decisión la dan los P0).`, ''];
  L.push('| nivel | requisito | ok | evidencia o qué falta |', '|---|---|---|---|');
  for (const r of v.resultados) L.push(`| ${r.tier} | \`${r.id}\` | ${r.ok ? '✓' : '✗'} | ${(r.ok ? r.evidencia : `${r.por}${r.evidencia && r.evidencia !== 'ausente' ? ` → ${r.evidencia}` : ''}`).replace(/\|/g, '\\|')} |`);
  L.push('', `P0 en rojo: ${v.p0_faltan.join(', ') || 'ninguno'} · P1: ${v.p1_faltan.join(', ') || 'ninguno'} · P2: ${v.p2_faltan.join(', ') || 'ninguno'}`, '');
  return L.join('\n');
}

if (esteEsElPrograma(import.meta.url)) {
  const argv = process.argv.slice(2);
  const val = (k, d = null) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
  const perfil = val('--perfil', 'spec');
  const minimo = Number(val('--minimo', perfil === 'spec' ? 100 : 80));
  const repo = val('--repo'); const dir = val('--dir'); const ref = val('--ref');
  if (!repo && !dir) { console.error('uso: node tools/guard-repo-jos.mjs (--repo owner/name | --dir ruta) [--perfil spec|sdk|cli|extension] [--minimo N] [--json]'); process.exit(2); }
  let v;
  try { v = evaluarRepo(repo ? arbolGitHub(repo, ref) : arbolLocal(dir), { perfil }); }
  catch (e) { console.error(`✖ ${e.message}`); process.exit(2); }
  const salida = val('--salida');
  if (salida) { fs.mkdirSync(salida, { recursive: true }); fs.writeFileSync(path.join(salida, 'quality-report.json'), JSON.stringify(v, null, 2) + '\n'); fs.writeFileSync(path.join(salida, 'QUALITY.md'), qualityMd(v)); console.error(`✓ escritos ${salida}/QUALITY.md y quality-report.json`); }
  if (argv.includes('--json')) process.stdout.write(JSON.stringify(v, null, 2) + '\n'); else console.error(narrar(v));
  process.exit(v.decision !== 'BLOCK' && v.nota >= minimo ? 0 : 1);
}
