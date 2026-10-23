# The `.jos` promise — every claim ever made, and where it lands in 2.0

**Version:** 0.1.0 · **Status:** Draft · **Date:** 2026-10-14 · **Author:** JOSFOX LLC
**Purpose:** `.jos` 2.0 MUST keep or improve every promise made by earlier specifications. This document is the audit trail: one row per promise, its source, where 2.0 delivers it (format core, format profile, kernel, engine, service), in which phase, and what happens to a document written against the old version.

Legend — **Where:** C = format core (`SPECIFICATION.md` §3–§7) · P = format profile (§10) · K = kernel (`companions/`) · E = engine (pluggable executor) · S = service (store, grader, router). **Compat:** ✔ read unchanged · ⇄ read via normalization (§2.4) · ✘ dropped (reason given).

**Class** (one per promise; `tools/promises-proof.py` refuses a class that the evidence does not support):
- **Normative format guarantee**: a property of the document that a validator checks from the document alone; F0/F1 only, with passing vectors.
- **Implemented and tested**: behaviour of a runtime, demonstrated by both reference kernels; F0/F1 only, with passing vectors or a runner check.
- **Partial**: one part is delivered in F0/F1 and the rest is in a later phase; the Phase column names each part.
- **Future phase**: specified in this text, not executed by the reference kernels of this release.
- **Needs external services**: a later phase that also needs an engine or a service outside the kernel (a model provider, a registry, a router).

## 1. Identity of the format

| # | Promise (source) | 2.0 | Where | Phase | Compat | Class |
|---|---|---|---|---|---|---|
| P1 | "The minimum unit of intention: what, when done, what to avoid" (1.1.0 §1, §3) | Core atom = `intention.objective` + `intention.success_criteria` + `guardrails.avoid`. Short form `intent/done/avoid` accepted and normalized | C §3 | F0 | ⇄ 1.1.0 | Normative format guarantee |
| P2 | "Declarative, never imperative: names *what*, not *how*" (1.1.0 §1.1) | The document declares intention and constraints; the runtime supplies engine, prompts, policy. A document with no runnable engine is still valid | C §1.2 | F0 | ✔ | Normative format guarantee |
| P3 | "Portable, self-describing, LLM-friendly JSON" (0.0.7 §1, 1.0.0 overview) | JSON (RFC 8259) UTF-8, `jos` header, JSON Schema published; YAML authoring profile converts to JSON before hashing | C §2 | F0 | ✔ | Normative format guarantee |
| P4 | "Agnostic: runtime-neutral, vendor-neutral, platform-agnostic" (0.0.7 §5.5, the generator, benefit 7) | Core has no vendor vocabulary; vendors appear only in `model_policy.vendor` enum (open) and in profiles. Two reference engines in two languages prove it | C §1.3, K | F0 | ✔ | Implemented and tested |
| P5 | "Open world: unknown keys are extension data; the core never grows" (1.1.0 §1.3, §10) | Core keys are closed (`additionalProperties:false` at root, as 1.0.0 defined); extension goes through `profiles` and the `x` namespace (`x-*` keys allowed anywhere) | C §2.5 | F0 | ⇄ (1.1.0 free keys move under `x-` or a profile) | Normative format guarantee |
| P6 | "Sealed artifact, cryptographically verifiable" (1.0.0 overview, 0.0.7 §3.4, 1.1.0 §12) | `integrity.hash` over canonical JSON (JCS, RFC 8785) + `integrity.signed_by` + detached or inline signature; content id `art_<sha256>` | C §8, K | F0 hash · F2 signature | ✔ (1.0.0 `integrity`) ⇄ (1.1.0 `sig`) | Partial |
| P7 | "A2A is the transport; `.jos` is the contract carried over A2A" (1.0.0, 0.0.7 §6) | `execution.bindings.a2a` kept; the agent-to-agent **envelope** is a kernel spec | C §6.4, K | F1 | ✔ | Implemented and tested |
| P8 | "MIME type registered; `version` parameter" (IANA ticket) | `application/vnd.jos+json; version=2.0.0` (definitive, `DECISION-NOMBRE.md`, 2026-10-14) | C §2.1 | F4 | ✔ | Future phase |

## 2. Composition and scale

| # | Promise (source) | 2.0 | Where | Phase | Compat | Class |
|---|---|---|---|---|---|---|
| P9 | "Fractal: same schema at every scale, atom → organization" (0.0.7 §4, the generator, fractal, 1.1.0 §4.4) | One shape. A step of a flow is a `.jos` (inline or by reference); a flow is a `.jos`; a directory `.jos/` is a `.jos` (kind `directory`) | C §5, §9 | F0 atom · F1 flow/dir | ✔ | Normative format guarantee |
| P10 | "Lego: `use` a brick by id, override its studs locally" (1.1.0 §7) | `use: "id@version"` + `with` + local overrides (tighten only; `objective` never overridden). Canonical slot: `orchestration.definitions[*].use` | C §5.3 | F1 | ⇄ | Implemented and tested |
| P11 | "Sequential piping: output of each child is input of the next" (1.1.0 §4.1) | Default data flow in a flow; named flow with `as`/`with` and `{{ }}` interpolation | C §5.2 | F1 | ⇄ | Implemented and tested |
| P12 | "Parallel fan-out" (1.1.0 §4.3, the generator, `parallel_invoke`) | `needs: []` dependency edges make a **DAG**; steps without edges run concurrently; the kernel MUST reject cycles | C §5.4 | F1 | ⇄ | Implemented and tested |
| P13 | "Composition via reference, type-preserving, integrity-checked before inclusion" (0.0.7 §4.2) | `use` resolves a sealed artifact; the kernel verifies `integrity.hash` (and signature when policy requires) before running it | C §5.3, K | F1 | ✔ | Implemented and tested |
| P14 | "Kind inferred, never required" (1.1.0 §11) vs "kind registry" (1.0.0) | `jos.kind` stays **required** (as in 1.0.0). A normalizer MAY infer it for short-form documents. Registry: `atom, flow, service, persona, template, crystal, directory, engine` | C §4 | F0 | ✔ 1.0.0 · ⇄ 1.1.0 | Normative format guarantee |
| P15 | "A company is just a very complex `.jos`" (1.1.0 §17.7) | Kind `directory`: a `.jos/` folder whose `manifest.jos` is the artifact; children inherit and may only restrict | C §9 | F1 | ✔ | Implemented and tested |

## 3. Intention, decomposition, measurement

| # | Promise (source) | 2.0 | Where | Phase | Compat | Class |
|---|---|---|---|---|---|---|
| P16 | "Write in intentions; the engine decomposes vague intent into nano-intentions, each independently executable and metered" (nano-intentions v1, crystallization v1 CLARIFY→DECOMPOSE→SELECT→BUILD) | Decomposition **produces** a flow whose steps are atoms. The format defines the output (a flow of atoms with `success_criteria` and `limit` each). The decomposer is an engine (`engine: decompose`), never the kernel | C §5.6, E | F2 engine · F1 format | ✔ (new) | Partial |
| P17 | "Definition of done: deterministic checks and judged checks; self-correction loop" (1.1.0 §5, the generator, anti-hallucination) | `success_criteria[]` items: string (descriptive or judged), or structured: `exit`, `stdout_matches`, `json_schema`, `sha256`, `file_exists`, `judge{rubric, task_class}`, `all/any`. Correction loop with `retries` feeding failure back | C §3.4, K | F0 structured · F2 judged | ⇄ (string stays; 0.0.7 descriptive) | Partial |
| P18 | "Measure whether an intention or nano-intention was met" (Jos, 2026-10-14; the generator, benefit 4) | Every step emits a **receipt** with per-criterion verdicts; a flow's `ok` is derived from its steps' receipts and its own criteria | C §7.2, K | F0 atom · F1 flow | ✔ (new) | Implemented and tested |
| P19 | "Guardrails are structural enforcement, not suggestions" (the generator, guardrails, 1.1.0 §6) | `avoid` enforced **before** launch (deny-list on command/prompt) and after (post-check → correction loop); `limit` enforced by the supervisor; breach stops the sequence | C §3.5, K | F0 | ✔ | Implemented and tested |
| P20 | "Budgets cascade: child inherits remaining budget, can only tighten" (1.1.0 §6.2) | `guardrails.limit{cost_usd,tokens,seconds,output_bytes,retries}` cascades through flows and directories; the kernel computes the effective limit as the minimum | C §3.5, K | F1 | ⇄ (1.0.0 `execution.budget` kept as alias) | Implemented and tested |
| P21 | "Policy layering: brick ∩ user ∩ environment, only tightens" (1.1.0 §6.3, DD-004 gates) | Capability spec: effective policy = intersection of document, directory chain, user claims and runtime claims | K capability | F2 | ✔ | Future phase |
| P22 | "Thermodynamics: T=0 and pinned model for transactional work; seed enables memoization" (the generator, thermodynamics) | `model_policy.temperature`, `seed`, `model_id` pinned (never `latest`) in the receipt; `reproducibility.class` derives from them | C §6.2 | F0 fields · F2 enforcement | ✔ | Partial |

## 4. Agents, engines, routing

| # | Promise (source) | 2.0 | Where | Phase | Compat | Class |
|---|---|---|---|---|---|---|
| P23 | "Engines: an intention may be executed by a shell, an LLM, a function, or a human; the runtime chooses" (1.1.0 §8.5) | `execution.engine` is a **class** (`shell`, `llm`, `function`, `human`, `decompose`, `judge`, `jos`), never a vendor. Engines are pluggable and declare their contract (kind `engine`) | C §6.1 | F0 shell · F2 others | ✔ | Partial |
| P24 | "Best model at lowest cost; cheapest viable per nano" (nano-intentions economics, grader/orchestrator, Jos O3) | The document declares `task_class` and constraints in `model_policy`; the runtime routes via a routing table fed by graded receipts; the receipt records the actual `model_id` and cost. The router (orchestrator) and the grader are services, the contract is in the format | C §6.2, S | F2 | ✔ (new) | Needs external services |
| P25 | "Semantic grading of every call" (the generator, benefit 4; grader v1) | Receipts carry an optional `grade` block written by a judge engine; the kernel never grades | C §7.2, E | F2 | ✔ | Needs external services |
| P26 | "Shadow agents: spawn, monitor, kill, cost ledger per clone, A/B, canary" (shadow-agents v1, `serve --detach` 4.0.x) | Kernel primitive: envelope + one JOSID, ledger and budget per clone. Protocol (A/B, canary, dispatch) is a profile over the primitive | K envelope, P | F2 primitive · F3 profile (moved on 2026-10-19 from the composition phase: the clone primitive and the envelope have no code in 2.0.0-rc; `FASES.md` places clones in F3) | ✔ | Future phase |
| P27 | "Human in the loop: `require_approval`, human gate" (1.0.0 tool_policy, DD-004 gates) | Gate `kind: human` in flows; `tool_policy.require_approval` kept | C §5.5 | F1 | ✔ | Implemented and tested |

## 5. Reuse, templates, crystals, cache

| # | Promise (source) | 2.0 | Where | Phase | Compat | Class |
|---|---|---|---|---|---|---|
| P28 | "Reuse before create: libraries of bricks, registries, `use`" (1.1.0 §7, Jos O2) | Resolution order: inline → `.jos/` chain → local library → configured registries. A `use` that cannot resolve is an error, never a silent fallback | C §5.3, K | F1 | ✔ | Implemented and tested |
| P29 | "Templates: prompts and bricks with slots, versioned" (crystallization v1 slots, DD-004 templates) | Kind `template`: a `.jos` with `inputs` schema and `{{ }}` slots; instantiation = `use` + `with` → a concrete atom with a deterministic `art_` hash | C §5.7 | F1 | ✔ (new) | Implemented and tested |
| P30 | "Crystallization: structured, verifiable, cost-bounded briefs from vague intent" (crystallization v1) | Two meanings, both kept and separated: (a) **crystallize intent** = the `decompose` engine (P16); (b) **crystal** = a sealed record of an execution (`kind: crystal`: input hash, engine/model id, output, receipt chain, hash) that MAY be served instead of re-executing | C §8.3, E | F2 | ✔ (new) | Future phase |
| P31 | "Anti-token waste: same hash → cache hit, seconds to milliseconds" (the generator, benefit 1) | Normative cache key: `crystal_key = sha256(art_hash ‖ canonical(inputs) ‖ ctx_class ‖ model_id ‖ temperature ‖ seed)`. A kernel MAY serve a crystal when `reproducibility.class` is `deterministic`, or `bounded` and policy allows | C §8.3, K | F2 | ✔ | Future phase |
| P32 | "Prompt cache friendly: stable prefix, variable suffix" (DD-004 provider prompt cache, Jos O4) | `persona.system_prompt` and `execution.inputs` are split by the engine contract into `prefix` (stable, hashed) and `suffix`; receipts record `cache_hit` | C §6.3, E | F2 | ✔ (new) | Future phase |
| P33 | "A folder can be a crystallized `.jos`" (Jos, 2026-10-14) | A directory is **crystallized** when every step of its flows has a matching crystal under `.jos/crystals/` and the manifest's `integrity.hash` covers them; running it executes nothing and replays everything. Not to be confused with running a folder (§9.1, P15, delivered in 2.0: every step executes) | C §9.4 | F2 | ✔ (new) | Future phase |

## 6. Observability, replay, store

| # | Promise (source) | 2.0 | Where | Phase | Compat | Class |
|---|---|---|---|---|---|---|
| P34 | "Receipts chain into an auditable ledger" (1.1.0 §8.3, witness 4.0.x) | Receipt schema normative; ledger = append-only, hash-chained, signed by the runtime; one per run | C §7, K ledger | F0 receipt · F1 ledger | ✔ | Implemented and tested |
| P35 | "Auditable replay: same seed + model = identical reproduction" (the generator, thermodynamics) | `replay(run_id)`: deterministic steps re-execute and compare hashes; stochastic steps are served from crystals; divergence is reported, never hidden | K replay | F2 | ✔ | Future phase |
| P36 | "Metering: tokens, runs, cost, per nano-intention" (nano-intentions, the budget service, Jos O5) | Receipt fields `tokens_in/out`, `cost_usd`, `duration_ms` are mandatory when an engine reports them; the kernel counts, services price | C §7.2, K | F0 shape · F2 counts | ✔ | Partial |
| P37 | "Registry / app store of agents, versioned, signature required to activate" (registry.js cloudv3, jos-store) | Store spec: sealed artifacts only; `activate` requires `integrity.signed_by`; policies by Capability claims (org, visibility, origin) | S store, K | F3 | ✔ | Needs external services |
| P38 | "Offline-first: works with no network" (the generator, benefit 6, 4.2.0-alpha) | Core kernel opens no socket (K8). Network engines and registries are adapters | K | F0 | ✔ | Implemented and tested |
| P39 | "Context server / anti-context-dissolution: canonical vocabulary and invariants loaded before every run" (the generator, guardrails layer 2) | Directory chain: `.jos/PROJECT.md`, `genesis/`, policies are loaded by scope resolution before a run; the kernel exposes `effective(ctx)` | C §9.2 | F1 | ✔ | Implemented and tested |
| P40 | "Nano-personalization: two users, same prompt, different result" (nano-intentions, Jos) | Directory inheritance + user claims in the Capability + templates with `with` | C §9, K | F1 | ✔ | Implemented and tested |
| P41 | "Declarative views: structure in JSON, roles, archetypes, agent-generated, no HTML strings in code" (`.joshtml` 1.0.0, after a production outage from a template literal) | Profile `ui/1`: a view is a `.jos`; blocks with roles, tokens by reference, data only through PAL routes, `show_if` over claims, rendered by the host, crystallizable | P ui/1 (draft of a later phase, not in this release) | F3 | ⇄ (`.joshtml` fields mapped; layers/renderer/REST dropped) | Future phase |
| P42 | "Intention-native memory: local YAML + cloud store, multi-tenant, hash-chained credits" (JOSDB 1.0.0) | Upgraded: JOSDB is the `.jos`-aware embedded store (SQLite, zero deps), reference adapter for `jos://db`, `blob`, `store`, `ledger`, `genesis`; content-addressed artifacts and crystals, append-only ledger tables, FTS over intentions; tenancy by claim; credits as Ledger `tx` | A josdb (draft of a later phase, not in this release) | F2 (on 2026-10-20 Jos took the store and its API out of jos-core 2.0.0: they arrive with 2.1, tested meanwhile in the development tree with 26 + 34 vectors; mounting it as `jos://db` inside a run is F2, decision p1 of the JOSDB project) | ✔ improved | Future phase |
| P43 | "Anti-context-dissolution: canonical vocabulary, constraints and invariants loaded in a fixed order before every run" (the generator, layer 2; context service v1) | `context` engine with mandatory order and context-tree layout; provenance of every injected item in the receipt | E context, S genesis | F2 | ✔ (new) | Needs external services |
| P44 | "Semantic grading in two stages, cheap gate, routing signals with decay, ≥10 samples" (grader v1) | `judge` engine + router service; weights, gate, grades and ATH-007/008 kept; embeddings moved to `context` | E judge, S router | F2 | ✔ | Needs external services |
| P45 | "Prompt enhancement verifiable in the ledger" (prompt-enhancer v1) | `enhance` engine: versioned templates, prefix stability, injected items listed by `blob_` instead of a flag | E enhance | F2 | ✔ improved | Needs external services |
| P46 | "Antispam first, 0.1 ms, before anything else" (Sentinel) | Sentinel host middleware before admission; kernel unaware of IPs | H sentinel | F3 | ✔ | Future phase |
| P47 | "Write intentions in prose with five tags" (AS-JOS / Intention Engine v1) | `seed/1` authoring profile and compiler | P seed | F2 | ✔ | Future phase |
| P48 | "Learning and nano-personalization: two users, same prompt, different result; the system learns from selections and from failures; nothing is discarded" (the project-context MDM 2026-08, context service v1, nano-intentions, Jos 2026-10-14) | MDM Learn service (medallion cobre → plata on adoption → oro on quality gate; the project context as antecedent): proposals, evidence-backed votes, scoring with decay and anti-Sybil clipping, rollback by alias, A/B between versions, grader batch gate, constitution outside the learning layer, scope isolation, consent claims | S mdm (draft of a later phase, not in this release) | F2/F3 | ✔ (new) | Needs external services |

## 7. Dropped or narrowed (with reason)

| Old promise | Decision |
|---|---|
| 0.0.7 "dual kernel: 13 required root keys, no exceptions" | ✘ Narrowed. 2.0 requires only `jos` and `meta` (as 1.0.0 did). 0.0.7 documents are read through the legacy normalization (§2.4) and `files[]` maps to `orchestration.definitions`. Requiring `x_run_params`, `adaptive_ai`, `id_jos`, `artifacts` never bought anything: the kernel never read them (audit 2026-10-13) |
| 1.1.0 "one required field: `intent`" | ✘ Narrowed to short form. A stored document MUST carry `jos` and `meta.name`; an inline step MAY be `{ "intent": "…" }`. Reason: the IANA registration and the `version` parameter need the header |
| 1.1.0 "a kernel MUST NOT reject unknown keys" | ⇄ Replaced by `x-*` keys and profiles. Reason: silent acceptance of typos is how `supports`, `jos_id` and a product-named key drifted between spec and schema in June 2026 |
| 1.0.0 `billing`, `ui`, `metrics` as core blocks | Moved to profiles (`commerce`, `ui`, `observability`). Kept readable (⇄). Reason: vendor-neutral core for IANA |
| The generator's `.seed.yaml` PLUMBING / traits `std://…` | ✘ Not carried. YAML stays an authoring profile; `traits` are `use` |
| The 1.0.0 monolith that held metering, auth, antispam, secrets and markup in one component | ✘ Dissolved into Ledger (metering), identity adapters (claims), Sentinel (host), PAL vault (secrets), the budget service (markup). Reason: one component holding keys, money and the audit log is the opposite of a hypervisor |
| AS-JOS dual kernel (MAGIC/JOSFOXAI) | ✘ Dropped; it is 0.0.7 restated. Its five tags survive in `seed/1` |
| JOSDB 1.0.0 as a Firestore collection inventory | ⇄ Replaced by the `.jos`-aware embedded store (P42); the collection list is product data of the directory service |
| `.joshtml` five-layer page model, the component-registry class field, the registry renderer value, REST `data.sources` | ✘ Dropped from the profile; they tie a view to one renderer and one product (P41) |

## 8. Backward compatibility statement

A conforming 2.0 kernel MUST read: (a) any valid 1.0.0 document unchanged; (b) any 1.1.0 short-form document through normalization; (c) any 0.0.7 document whose flow steps are strings through the legacy mapping, and MUST reject with code 2 a 0.0.7 document whose flow steps are objects (their normalization is scheduled for 2.1). It MUST write receipts in the 2.0 shape regardless of input version, and MUST report the detected input version in the receipt. The JSON Schema 2.0 is an additive superset of 1.0.0 (`check-superset.py`).
