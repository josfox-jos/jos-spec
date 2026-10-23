# `.jos` Object Specification — version 2.0.0

**Status:** 2.0.0 (published as the tag `v2.0.0`) · **Date:** 2026-10-21 · **Author:** JOSFOX LLC (change controller) · **Supersedes:** 1.0.0 (additively) · **Reads:** 1.1.0 short form, 0.0.7 legacy with string flow steps
**Media type:** `application/vnd.jos+json; version=2.0.0` (definitive, 2026-10-14; registration template in `IANA.md`) · **Schema:** `schema/jos.schema.json` (core), `schema/profiles/exec-contract-1.schema.json` (the one profile schema published with 2.0.0)
**Promise audit:** `PROMISES.md` — every row there cites the section here that delivers it.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as described in RFC 2119.

---

## 1. Scope and principles

### 1.1 What a `.jos` document is

A `.jos` document is the **minimum unit of intention**: a JSON object that declares *what is intended*, *when it is done*, and *what must be avoided*, together with the metadata needed to identify, verify, compose and execute it. It is declarative. It does not describe how to compute; it declares a goal and the bounds within which any conforming engine may pursue it.

### 1.2 Validity does not depend on executability

A document is valid if it conforms to §2–§4. It remains valid when no engine available to a given runtime can execute it. Runtimes MUST distinguish *invalid* (rejected by the schema or by §2.4) from *unexecutable* (valid, no engine) in their results (§7.4).

### 1.3 Agnosticism

The core (§3–§9) contains no vendor, platform, product or trademark vocabulary; profile names are descriptive, never brands. Vendor names appear only as values of open enumerations (`model_policy.vendor`) and inside profiles (§10). Two independent reference engines in different languages MUST produce identical results on the conformance vectors (§11).

### 1.4 One shape at every scale

The same schema describes an atom, a flow of atoms, a long-running service, a template, a sealed execution record (crystal) and a directory. Composition is by nesting and by reference; it never introduces a new document shape (§5, §9).

---

## 2. Document model

### 2.1 Encoding

A `.jos` document is a JSON text (RFC 8259) whose top-level value is an object, encoded in UTF-8 without a byte order mark. A document that begins with a BOM, that is not valid UTF-8, or whose top-level value is not an object is invalid (code 2). Member names are case-sensitive. An object with duplicate member names is invalid: parsers MUST reject it rather than keep the first or the last value. Numbers MUST be finite; `NaN`, `Infinity` and literals that overflow the parser's number type are invalid. Because every member takes part in `integrity.hash` and the content identifier (Section 8.1; RFC 8785 Section 3.1), a number literal MUST survive the canonical form unchanged: a literal whose value is an integer with magnitude greater than 2^53 and less than 10^21 is invalid (code 2) however it is written (`9007199254740993`, `1e20`, `9.007199254740994e15`; RFC 8785 writes such a value as an integer literal, which no binary64 number represents exactly in general), and any other literal whose value differs from the value of the shortest decimal that reads back to the same binary64 number (for example `1.00000000000000001`, `1e-400`, `9007199254740993.0`) is invalid (code 2). `0.1`, `1.0`, `9007199254740992`, `1e+21` and `5e-324` are valid. The rule is closed under the canonical form: the canonical form of a valid document is a valid document. Nesting deeper than 64 levels and documents larger than the runtime's declared limit (RECOMMENDED 1 MiB) are invalid; the limits are declared, never implicit.

File extensions: `.jos` (primary) and `.jos.json` (for tooling that keys on a `.json` suffix; it does not define a different representation). The media type parameter `version`, when present, MUST equal `jos.version`. There is no implicit default: `jos.version` is authoritative, and a conflict between the parameter and the member is an error.

**Fragment identifiers.** RFC 6839 defines no fragment identifier syntax for the `+json` suffix; this specification adopts JSON Pointer (RFC 6901) for `application/vnd.jos+json`: `#/meta/name` refers to the `name` member of `meta` in the identified document.

A YAML authoring profile MAY be used by tools; tools MUST convert it to JSON before validation, hashing or signing.

### 2.2 Header

```json
{ "jos": { "version": "2.0.0", "kind": "atom", "profiles": ["observability/1"] } }
```

| Field | Req | Type | Meaning |
|---|---|---|---|
| `jos.version` | MUST | MAJOR.MINOR.PATCH | Specification version the document conforms to |
| `jos.kind` | MUST | enum §4 | Document kind; determines execution semantics |
| `jos.profiles` | MAY | string[] | Profiles the document uses (§10), each `name/MAJOR` |
| `jos.schema` | MAY | URI | Schema used for validation; informative |

**Later and other versions.** A reader that implements 2.0.0 MUST NOT reject a document only because its `jos.version` is a later minor or patch version of major version 2 (for example `2.1.0`). It validates the document against the schema it implements, so a member, a value or a kind that it does not know makes the document invalid (Sections 2.3 and 4.1, code 2); forward compatibility therefore covers only documents that use nothing added after 2.0.0. A `jos.version` `1.0.x` is read as specified in Section 2.4, and the 1.1.0 short form and the 0.0.7 legacy form are detected by their shape (Section 2.4). Any other `jos.version` is invalid (code 2). A reader never executes an obligation it does not implement: obligations are `requires[]` entries (Section 6.6).

### 2.3 Root members

| Member | Req | Section | Purpose |
|---|---|---|---|
| `jos` | MUST | §2.2 | Header |
| `meta` | MUST | §2.6 | Name and descriptive metadata |
| `id` | SHOULD | §2.7 | Stable identifier for reuse |
| `intention` | SHOULD | §3.2 | Objective and success criteria |
| `guardrails` | MAY | §3.5 | Avoid list, requirements, limits |
| `execution` | MAY | §6 | Engine, inputs, outputs, bindings |
| `orchestration` | MAY | §5 | Steps, flows, gates (kinds `flow`, `service`, `directory`) |
| `model_policy` | MAY | §6.2 | Task class, tier, vendor, pinning |
| `persona` | MAY | §6.3 | Behavioral contract for `llm` engines |
| `tool_policy` | MAY | §6.4 | Tool allow/deny, approval |
| `security` | MAY | §6.5 | Tier, permissions, data class |
| `capabilities`, `requires` | MAY | §6.6 | Provided and required capabilities |
| `lifecycle` | MAY | §6.7 | Service probes and hooks |
| `reproducibility` | MAY | §8.4 | Determinism class and parameters |
| `integrity` | MAY | §8.1 | Hash, signature, key identifier, seal time |
| `crystal` | MAY | §8.3 | Sealed result of one execution (kind `crystal`) |
| `x-*` | MAY | §2.5 | Extension data |

Members defined by 1.0.0 that are not listed above (`ui`, `metrics`, `billing`) are **profile members** (§10.2); a core kernel MUST accept and ignore them.

Root `additionalProperties` is false except for `x-*` keys. Unknown non-`x-` keys make the document invalid.

### 2.4 Normalization and compatibility

A conforming kernel MUST implement `normalize(document) → canonical 2.0 document` and MUST apply it before validation and before hashing a short-form document:

| Input | Detection | Mapping |
|---|---|---|
| **2.0 canonical** | `jos.version` starts with `2.` | identity |
| **1.0.0** | `jos.version` starts with `1.0` | identity; `execution.budget` → `guardrails.limit` alias (§3.5) |
| **1.1.0 short form** | `jos` is a string, or root has `intent`/`use` and no `intention` | `intent`(string) → `intention.objective`; `intent`(array) → `orchestration` flow `main` with inline steps (§5.2); `done` → `intention.success_criteria`; `avoid` → `guardrails.avoid`; `limit` → `guardrails.limit`; `retries`/`on_error`/`with`/`as`/`parallel` → execution/step fields; `sig` → `integrity`; `kind` inferred (§4.2); missing `meta.name` → `id` or the first 64 characters of `intent` |
| **0.0.7 legacy** | root has `orchestration_contract` | `orchestration_contract.version` recorded as `x-legacy-version`; `orchestration.flows[*].steps` kept when every step is a string (a step in object form is rejected with code 2; its normalization is scheduled for 2.1); definitions kept as written, so a definition whose `type` is not `shell`, `jos` or `http` (the 0.0.7 `type: prompt`) makes the document invalid (code 2, Section 5.1); `files[]` → `orchestration.definitions` of type `jos`; `security`, `guardrails`, `intention`, `meta`, `tool_policy`, `model_policy` kept with the member rule below; `x_run_params`, `adaptive_ai`, `id_jos`, `artifacts` and every other root member that is not an `x-` member → `x-legacy-*` (see **0.0.7 normalization**) |

**Detection order.** The rows are tried in this order, and the first that matches applies: (1) the root has `orchestration_contract`: 0.0.7 legacy; (2) `jos` is a string: 1.1.0 short form; (3) the root has `intent` or `use` and no `intention`, and `jos` is not an object whose `version` starts with `2.` or `1.0.`: 1.1.0 short form; (4) `jos.version` starts with `2.`: 2.0 canonical; (5) `jos.version` starts with `1.0.`: 1.0.0. A header that declares a `2.` or `1.0.` version therefore names the canonical form, and a root `intent` or `use` beside it is an unknown root member (Section 2.3, code 2).

**0.0.7 normalization.** The 0.0.7 row maps as follows, and the content identifier of a 0.0.7 input is the identifier of the normalized document (Section 8.2). A member whose name begins with `x-` is kept as written at every level (Section 2.5). *Kept objects:* `security`, `guardrails`, `intention`, `meta`, `tool_policy` and `model_policy` are kept, and a member the schema does not define at that level moves to `x-legacy-<member>` in the same object, never dropped and never interpreted. A member the schema defines at that level but whose value does not have the schema's shape moves the same way in `meta` and `intention`; in `guardrails` (`limit` and each of its members included), `security`, `tool_policy` and `model_policy`, and for `intention.success_criteria`, it makes the document invalid (code 2, the schema's errors at its JSON Pointer, as in a 2.0 document) and is never moved, because the document would otherwise run without the limit, pattern, tier, policy or definition of done it states. A kept member that is not an object stays as written, and the schema refuses it (code 2). In `orchestration`, `definitions` and `flows` are kept as written and every other member moves to `x-legacy-<member>`. *Root:* a root member the row does not list, other than an `x-` member, moves to `x-legacy-<member>` at the root. Writing an `x-legacy-<member>` that the object already has (a move, or at the root `x-legacy-version`, `x-legacy-orchestration_contract` or `x-legacy-files`), in any member order, makes the document invalid (code 2). *Contract:* `x-legacy-version` is `orchestration_contract.version` when that is a string, else `"0.0.7"`; `orchestration_contract` is kept as `x-legacy-orchestration_contract` unless it is an object whose only member is a string `version`. *Limits:* the 0.0.7 `guardrails.max_retries` → `guardrails.limit.retries` and the 0.0.7 `guardrails.timeout_ms` (a number of milliseconds) → `guardrails.limit.seconds` (divided by 1000), merged member by member into a `guardrails.limit` the document declares: a declared member that the legacy member would set to a different value makes the document invalid (code 2), and the other declared members are kept. A value produced by a mapping MUST itself satisfy Section 2.1 and the schema, otherwise the document is invalid (code 2 at the legacy member) and nothing is set aside: `max_retries: "3"`, a `timeout_ms` that is negative or not a number, and `timeout_ms: 1e22` (its `limit.seconds`, 1e19, is an integer that the canonical form writes as `10000000000000000000`, which Section 2.1 refuses) are code 2. *Files:* a non-empty array `files` maps each entry to `orchestration.definitions.file_<i+1>`: a string as `{ "type": "jos", "artifact": <files[i]> }`, an object as `{ "type": "jos", "artifact": <the first of `path`, `artifact`, `name` the entry has, whatever its type>, "x-legacy-file": <files[i]> }` (without `artifact` when it has none of the three), and any other entry is invalid (code 2); a definition named `file_<i+1>` already present is a collision (code 2); the list itself is not kept. A `files` that is empty or not an array maps nothing and is kept as `x-legacy-files`. An `orchestration` or `orchestration.definitions` that is not an object stays as written, and the schema refuses it (code 2). *Name and kind:* a missing `meta` is `{}`; a missing `meta.name` (after the member rule) is `id_jos` as written when that is a non-empty string, else `"legacy"`, so an `id_jos` longer than 128 characters gives a name the schema refuses (code 2); `jos.kind` is `flow` when `orchestration.flows` names a flow, else `atom`.

Mixing canonical and short-form spellings of the same field (e.g. both `intention.objective` and `intent`) is invalid. The receipt (§7.2) MUST record `input_version`.

**0.0.7 detached manifests.** A 0.0.7 legacy document whose input member `security.integrity_ref` is present and is neither `null` nor the empty string is sealed by a detached manifest. Before the first step of a run starts, including a dry run, a kernel MUST verify it as follows, and MUST NOT start any step when a check fails (the document is valid and blocked: code 3, `reason` beginning `integrity_ref:`). (a) The value MUST be a string that is a relative path with `/` separators and contains no NUL, no `\` and no `:`; it is resolved against the directory of the document — the directory of the path the kernel was given, lexically normalized (`a/../m.json` is `m.json`), without resolving a symbolic link that the document itself may be — and MUST stay inside it, also after resolving the symbolic links of its directory components; a kernel MUST NOT dereference a URI to find it. Whether `M.JSON` names `m.json` is the file system's case rule; no conformance vector depends on it. (b) The manifest MUST be a regular file that is not a symbolic link, of at most 65536 octets, that parses as a JSON object under the rules of Section 2.1; its member `artifact_sha256` MUST be 64 lowercase hexadecimal digits, and its other members are ignored. (c) `artifact_sha256` MUST equal the lowercase hex SHA-256 of the octets from which the kernel parsed the document, or of those octets with every CRLF replaced by LF, or of that LF form with every LF replaced by CRLF. The kernel MUST hash the same octets it parses. A kernel that does not have those octets MUST NOT run the document (code 5). A `type: jos` definition that names a 0.0.7 file is verified in the same way, against that file's directory, before the first step of the run. Validation does not read the manifest. The check reads the input member, never `security.x-legacy-integrity_ref` of the normalized document; normalization, the content identifier and Section 2.5 are unchanged.

### 2.5 Extension data

Keys beginning with `x-` are extension data at any object level. A kernel MUST preserve them, MUST include them in the canonical hash, and MUST NOT interpret them. Vendor-specific behavior belongs in a profile (§10), not in `x-*`.

### 2.6 `meta`

As 1.0.0: `name` (MUST, ≤128 chars), `version` (version of the content: `MAJOR.MINOR.PATCH` with an optional pre-release of ASCII letters, digits and dots after one hyphen, pattern `^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$`; a hyphen inside the pre-release and build metadata make the document invalid, code 2), `author`, `license` (SPDX), `description` (≤500), `domain`, `tags` (≤20, unique, ≤32 each), `labels` (string map).

### 2.7 `id`

Reverse-DNS or short name, pattern `^[a-z][a-z0-9.\-_]*$`. An `id` carries no version: the version of a document is `meta.version` (§2.6), and an `id` that contains `@` is invalid (code 2). Used for `use` resolution (§5.3), where a reference MAY add `@<semver range>` after the `id`. Distinct from the content identifier `art_<hash>` (§8.2), which is derived, never declared.

---

## 3. The atom

### 3.1 Minimal valid atom

```json
{
  "jos": { "version": "2.0.0", "kind": "atom" },
  "meta": { "name": "hello" },
  "intention": { "objective": "Print a greeting", "success_criteria": [ { "exit": 0 } ] },
  "execution": { "engine": "shell", "run": ["echo", "hello"] }
}
```

Short form of the same atom (normalized by §2.4): `{ "jos": "2.0.0", "intent": "Print a greeting", "done": [{ "exit": 0 }], "run": ["echo", "hello"] }`.

### 3.2 `intention`

| Field | Req | Type | Meaning |
|---|---|---|---|
| `objective` | SHOULD | string ≤1000 | What is intended. Never overridden by `use` |
| `success_criteria` | SHOULD | criterion[] | When it is done (§3.4). A string alone is accepted as a one-element list |

An atom without `success_criteria` is a **wish**: it runs, and `ok` is the engine's own success signal (exit 0 for `shell`). Authoring tools SHOULD flag a wish as a draft.

### 3.3 Kinds of criteria

A criterion is one of:

| Form | Evaluated by | Verdict |
|---|---|---|
| `"free text"` | nobody | `descriptive`: recorded, never affects `ok` |
| `{ "exit": n }` | kernel | `pass`/`fail` |
| `{ "stdout_contains": s }`, `{ "stdout_matches": regex }`, `{ "stderr_empty": true }` | kernel | `pass`/`fail` |
| `{ "file_exists": path }`, `{ "file_sha256": { "path", "hash" } }` | kernel, paths confined to the run's `cwd` | `pass`/`fail` |
| `{ "json_schema": <schema or ref> }` | kernel, over the engine's structured output | `pass`/`fail` |
| `{ "sha256": hash }` | kernel, over the engine's output bytes | `pass`/`fail` |
| `{ "judge": { "rubric": text or ref, "task_class": "judge", "threshold": 0..1 } }` | a `judge` engine (§6.1) | `score` with `pass` = score ≥ threshold |
| `{ "all": [criteria] }`, `{ "any": [criteria] }`, `{ "not": criterion }` | kernel | combinator |

### 3.4 Definition of done

`ok` is true iff every non-descriptive criterion passes (`all` is the implicit combinator). When `success_criteria` is absent or contains only descriptive items, `ok` is the engine's success signal. Each criterion's verdict MUST appear in the receipt (§7.2).

**Correction loop.** When `ok` is false and `guardrails.limit.retries` > 0, the kernel MUST re-run the atom, supplying the previous output and the failed verdicts to the engine as input (`inputs.previous`), up to `retries` times. Each attempt produces its own receipt.

### 3.5 `guardrails`

| Field | Type | Enforcement |
|---|---|---|
| `avoid` | string[] (substring or `/regex/`) | **Before** launch: if any pattern matches the engine input (the joined `run` argv, the rendered prompt), the step MUST NOT start; code 3. **After**: engines MAY post-check output and trigger the correction loop |
| `require` | string[] | Post-check: each pattern MUST appear in the output, else `ok` is false |
| `limit.seconds` | number | Supervisor kills the engine; code 124 |
| `limit.output_bytes` | integer | Supervisor truncates and kills; code 137; `truncated: true` |
| `limit.tokens`, `limit.cost_usd` | number | Supervisor stops the engine when the counters exceed; counters are kept outside the engine |
| `limit.retries` | integer | §3.4 |
| `limit.context_tokens` | integer | Cap on the context an engine hands to a model in one call (`companions/context-engine/0.1.0/SPEC.md`); an engine MUST NOT send more and MUST stop with code 3 rather than truncate silently; engines that call no model ignore it |
| `max_cost_per_call` | number | 1.0.0 alias of `limit.cost_usd` per engine call |

**Cascade.** In a flow or directory the effective limit of a step is the element-wise **minimum** of its own limit, its parent's remaining budget and the Capability's budget (`companions/capability/0.1.0/SPEC.md`). A step that would exceed the effective limit MUST NOT start.

1.0.0 `execution.budget{max_cost_usd,max_tokens,max_duration,max_retries}` is read as an alias of `guardrails.limit`; writers SHOULD use `guardrails.limit`.

---

## 4. Kinds

### 4.1 Registry

| Kind | Meaning | Required members beyond core |
|---|---|---|
| `atom` | One unit of execution | `execution` SHOULD be present |
| `flow` | Composition of steps (§5) | `orchestration.flows` MUST have at least one flow |
| `service` | A flow the runtime keeps alive | `lifecycle` SHOULD be present |
| `persona` | Behavioral contract for `llm` engines | `persona` MUST be present |
| `template` | Document with slots, instantiated by `use`+`with` (§5.7) | `execution.inputs` MUST declare the slots' schema |
| `crystal` | Sealed record of one execution (§8.3) | `crystal` member MUST be present (profile `crystal/1` is part of core) |
| `directory` | A `.jos/` folder's manifest (§9) | `orchestration` describes the folder's flows; `x-dotjos` MAY carry folder metadata |
| `engine` | Declaration of an engine's contract (§6.1) | `capabilities` MUST list the engine classes provided |

### 4.2 Inference for short form

When `jos.kind` is absent (short form only): `use` → `atom`; `intent` string → `atom`; `intent` array → `flow`; `persona` present → `persona`; `lifecycle` present → `service`.

---

## 5. Composition

### 5.1 Steps and flows

```json
"orchestration": {
  "definitions": {
    "extract":   { "use": "ai.acme.extract@1.2.0", "with": { "doc": "{{ input }}" }, "as": "entities" },
    "lang":      { "jos": { "version": "2.0.0", "kind": "atom" }, "meta": { "name": "lang" }, "intention": { "objective": "Detect language" }, "execution": { "engine": "llm" } },
    "translate": { "use": "ai.acme.translate", "with": { "text": "{{ entities }}", "from": "{{ lang }}" }, "needs": ["extract", "lang"] },
    "verify":    { "engine": "shell", "run": ["./verify.sh"], "needs": ["translate"] }
  },
  "flows": {
    "main": { "steps": ["extract", "lang", "translate", "verify"],
              "gates": { "verify": { "kind": "auto", "expr": "exit == 0", "on_fail": "halt" } } }
  }
}
```

A **definition** is exactly one of: a reference (`use`, with the overrides of §5.3), an inline document in full form (it carries `jos` and `meta`), an inline shell atom (`run`, with `engine: shell` when the engine is written), or a 1.0.0 step (`type: shell|jos|http` with `command|artifact|url`). The members of a definition are closed, as `schema/jos.schema.json` states: the short-form members (`intent`, `done`, `avoid`, `limit`, `sig`), a `type` other than `shell`, `jos` and `http`, and a definition that has none of `use`, `jos` with `meta`, `run` or `type` make the document invalid (code 2). Inline short-form steps of a short-form document are normalized before validation (§2.4, §5.2) and are not definitions in this sense. Every definition is normalized to a `.jos` document (§2.4); a `shell` step becomes an atom with `engine: shell`.

A **flow** lists step names. Order in `steps` is the default sequential order. Steps MAY declare `needs: [step...]`; the resulting graph MUST be acyclic (§5.4).

### 5.2 Data flow

The kernel threads one **context** through a flow: `input` (the run's initial input), `last` (previous step's output), every `as` name, and run metadata (remaining budget, ids). A step's input is `with` rendered with `{{ }}` interpolation over the context, or `last` when `with` is absent. `as` writes the step's output under that name. The flow's output is the output of its last completed step unless `outputs` names another.

Inline short-form steps (`"Clean the text."`) are atoms with `engine` chosen by the runtime (§6.1).

### 5.3 Reference: `use`

`use: "<id>[@<semver range>]"` resolves, in order: inline definitions with that `id` in the current document → the `.jos/` chain (§9.2) → the local library → configured registries. Resolution MUST NOT fall back silently; an unresolved `use` is an error (code 5).

Before running a resolved document the kernel MUST verify `integrity.hash` when present, and MUST verify the signature when the effective policy requires it (`security.tier: privileged`, or a registry policy).

**Overrides.** A reference MAY carry `with`, `as`, `needs`, and MAY tighten `guardrails` (`avoid` ∪, `limit` min) and replace `success_criteria`. It MUST NOT change `intention.objective` or `execution.engine` class.

### 5.4 Dependencies: a DAG

`needs` edges define a directed graph over a flow's steps. The kernel MUST reject a flow with a cycle (code 2). Steps whose dependencies are satisfied MAY run concurrently; `parallel: false` on the flow forces the `steps` order. A step that fails stops its dependents; unrelated branches continue unless `on_error: halt` on the flow.

### 5.5 Gates

A gate is attached to a step name (or to `<name>#<n>` for the n‑th occurrence):

| Field | Values | Meaning |
|---|---|---|
| `kind` | `auto`, `human` | `human` gates require an approval event in the ledger before the next step |
| `expr` | string | Boolean expression over the step's receipt: `exit`, `ok`, `score`, `tokens`, `cost_usd`, `duration_ms`, `grade` and `all/any` |
| `on_fail` | `halt` (default), `continue`, `retry`, `goto:<step>` | `goto` MUST target a step not yet executed in this pass and MUST NOT create a cycle in the executed path |

A 1.0.0 string gate (`"exit_code == 0"`) is read as `{ kind: "auto", expr, on_fail: "halt" }`.

**Gate keys.** A key of `gates` names a step of its flow, `<name>#<n>`, or `after-<step>` (the 1.0.0 spelling): `after-<step>` is the gate of `<step>` when the flow has no step named `after-<step>`. Gating one step under both keys is invalid (code 2), in validation and in a run alike; `<name>#<n>` is a third key, distinct from both, and the rule concerns the pair `<name>` / `after-<name>` only. A key that names no step of its flow is valid and is never evaluated.

### 5.6 Decomposition into nano‑intentions

Writing an intention and letting the system split it is a first-class operation, performed by an engine of class `decompose` (§6.1), never by the kernel. Its contract:

- Input: an atom whose `intention.objective` is natural language and whose `execution.engine` is `decompose`.
- Output: a **flow document** whose steps are atoms, each with its own `success_criteria`, `guardrails.limit` and `model_policy.task_class`; edges in `needs`; the parent's `success_criteria` preserved as the flow's criteria.
- Invariants: every produced step MUST be independently executable and metered (receipt per step); the sum of step limits MUST NOT exceed the parent's effective limit; the output MUST validate as a `flow`.

The produced flow is a normal document: it can be sealed, stored, reused and crystallized.

### 5.7 Templates

A `template` declares `execution.inputs` as a JSON Schema of its slots and uses `{{ slot }}` anywhere in string values. Instantiation is `use` + `with`; the kernel renders slots, validates `with` against the slots schema, and produces a concrete document whose `art_` hash is deterministic for the same `with`. Unfilled required slots are an error (code 2).

---

## 6. Execution

Legacy member: `execution.capability` (1.0.0, a free string naming the capability to invoke) is accepted for backward compatibility and ignored by 2.0.0 kernels; `execution.engine` (§6.1) replaces it. A 2.0.0 document SHOULD NOT declare it.

### 6.1 Engines

`execution.engine` names a **class**, never a vendor or model:

| Class | Executes | Determinism |
|---|---|---|
| `shell` | `execution.run` as `argv[]` (no shell unless `execution.shell: true`) | deterministic |
| `function` | a runtime-registered function by name | deterministic |
| `jos` | another document (a flow step) | inherits |
| `llm` | a model call built from `persona` and `inputs` | bounded or stochastic |
| `judge` | grading of an output against a rubric | bounded |
| `decompose` | §5.6 | bounded |
| `human` | waits for a human event in the ledger | n/a |

When `engine` is absent the runtime chooses by policy and records the choice. An engine is declared by a `kind: engine` document listing `capabilities[].name` = classes provided; runtimes load engines as guests of the kernel (`companions/`).

### 6.2 `model_policy`

1.0.0 fields kept (`preferred`, `tier`, `vendor`, `fallbacks`, `temperature`, `max_output_tokens`) plus:

| Field | Meaning |
|---|---|
| `task_class` | `extract`, `transform`, `generate`, `reason`, `judge`, `plan`, `code`, `chat`, `embed` — the routing key |
| `per_step` | Flows only: a map `step id → model_policy` whose members override the document's `model_policy` for that step; the receipt of the step records the merged policy (vector `valid-2.0.0-model-policy-per-step.json`) |
| `model_id` | Exact model identifier when pinned; `latest` and aliases are invalid values |
| `seed` | Integer; MUST be recorded in the receipt when the engine supports it |
| `max_cost_usd` | Per-call ceiling; alias of `guardrails.max_cost_per_call` |

Routing contract: the document declares `task_class` and constraints; the runtime selects `model_id` (from a routing table, a policy or a fixed configuration); the receipt records the actual `model_id`, `vendor`, `temperature`, `seed`. A runtime MUST NOT select a model outside `vendor`/`tier`/`fallbacks` when they are present.

### 6.3 `persona` and prompt structure

1.0.0 fields kept. For `llm` engines the rendered prompt is split into a **prefix** (`persona.system_prompt`, `rules`, static parts of `inputs`) and a **suffix** (interpolated values, `previous` on retries). The receipt records `prompt_prefix_hash` and `cache_hit` when the engine reports it. Engines SHOULD order content so that the prefix is byte-stable across calls.

### 6.4 `tool_policy`

As 1.0.0. `tool_policy` is an input to the Capability (`companions/capability/0.1.0/SPEC.md`); the kernel enforces, the document declares.

### 6.5 `security`

`security.permissions` and `tool_policy` are inputs to the Capability (`companions/capability/0.1.0/SPEC.md`); the kernel enforces and the document declares. The **effective tier** of a step is `sandbox` when the step, any document or flow that contains it, or any level of its `.jos/` chain (Section 9.2) declares `security.tier: sandbox`; a child cannot remove it.

When the effective tier of a step is `sandbox`, the runtime MUST confine every process that the step starts, and all their descendants, so that: (a) they cannot open or use a network socket, including the loopback interface and name resolution, except to destinations that a `net:egress:<host-pattern>` permission of the Capability grants; (b) they cannot create, modify or remove files outside the step's working directory (Section 6.8) and a private temporary directory; (c) they cannot read files outside the working directory, except the read-only files that the runtime needs to start the declared program; (d) they receive only the environment of `execution.env`. Traffic of an engine adapter through routes admitted by the Capability (Section 12, item 4) is not a process of the step. A runtime that cannot confine every such step MUST refuse the run before its first step starts: the document is valid and unexecutable (code 5, `unexecutable` `sandbox not available`).

Every step receipt records `isolation`: `"sandbox"` when the step ran confined as stated above, `"none"` otherwise. A runtime MUST NOT record `"sandbox"` for a step it did not confine. The permissions of a Capability in a result state what was granted, not what was enforced on the processes of a step.

`security.require_auth`, `security.require_admin` and `tool_policy.require_approval` are declarations for the authorization layer of the host that admits the caller (`SECURITY.md` Section 3, item 4). The core kernel records them in the document it runs and does not enforce them; a conforming kernel does not claim them as guarantees. A host that admits callers other than the local user MUST enforce them or refuse the run. The signature that `security.tier: privileged` requires is not one of these declarations: Section 5.3 applies, and a runtime that cannot verify it MUST NOT run the document (code 5).

### 6.6 `capabilities` and `requires`

`capabilities[]` states what a document provides; `requires[]` states what it needs from the runtime, and `requires[].digest` (`art_…`) pins a dependency's content. Before the first step of a run starts, a runtime MUST decide, from its own configuration or an authoritative source (Section 12, item 3) and never from the document, whether it satisfies each `requires[]` entry of the document and of every definition known before the run (inline definitions and resolved `use` references). A definition produced during the run (Sections 5.6 and 5.7) is checked before its step starts. An entry is satisfied only when the runtime satisfies its `kind`, `name` and `version`, and, when `digest` is present, resolves an artifact whose content identifier equals it; an entry of a kind for which the runtime defines no satisfaction is unsatisfied. A runtime MUST NOT start any step of a document that has an unsatisfied entry: the document is valid and unexecutable (code 5), and `unexecutable` names the entry by JSON Pointer (for example `/requires/0`). A later minor version expresses every obligation it adds as a `requires[]` entry of an existing kind, so that a runtime of an earlier version refuses to execute the document instead of ignoring the obligation.

### 6.7 `lifecycle`

As 1.0.0.

### 6.8 `execution` fields

| Field | Type | Meaning |
|---|---|---|
| `engine` | class | §6.1 |
| `run` | string[] or string | For `shell`: argv (array) or a command line (string, requires `shell: true`) |
| `shell` | boolean | Default false |
| `cwd` | path | Relative to the document's location; it MUST resolve inside the document's directory (code 3). What the step's processes can reach is confined only under Section 6.5 |
| `env` | string[] | Allow-list of environment variable names passed to the engine (default `["PATH"]`) |
| `inputs` | object | Named inputs; for templates, a JSON Schema |
| `outputs` | object | Names the output(s) of the step (`{ "result": "stdout" }`) |
| `on_error` | `fail`, `continue`, `retry`, `{ "use": id }` | Default `fail` |
| `bindings.mcp`, `bindings.a2a` | object | As 1.0.0 |
| `flow` | `[{ invoke }]` | 1.0.0 alias of `orchestration.flows.main` (see below) |
| `budget` | object | 1.0.0 alias of `guardrails.limit` |

**`execution.flow`.** Each entry `{ "invoke": <name> }` is one step of the flow `main`, in the order written: `<name>` is a definition of the document, or else a `use` reference (§5.3) whose step is named after it, or `invoke_<n>` (1-based position) when the reference is not a valid step name. The alias is read when the document runs, as `execution.budget` is: normalization, the canonical hash and the content identifier see the document as written. A document that writes both `execution.flow` and `orchestration.flows.main`, or an `invoke` that is neither a definition nor a valid reference, is invalid (code 2). A document of kind `flow` whose only flow is `execution.flow` is valid.

---

## 7. Results, receipts, ledger

### 7.1 Exit codes

| Code | Meaning |
|---|---|
| 0 | done (`ok` true) |
| 1 | not done (`ok` false after retries) |
| 2 | invalid document, cycle, unresolved slot |
| 3 | blocked: `avoid` matched, Capability denied, `execution.cwd` outside the document's directory, `integrity.hash` mismatch, or a 0.0.7 `security.integrity_ref` that does not verify (Section 2.4) (`reason` names which) |
| 4 | budget exceeded before start |
| 5 | valid but unexecutable: unresolved `use`, missing engine, unsatisfied `requires[]` entry (Section 6.6), isolation not available (Section 6.5), a signature that `security.tier: privileged` requires and the runtime cannot verify (Section 5.3), or the octets of a 0.0.7 document sealed by `security.integrity_ref` are not available (Section 2.4) (`unexecutable` names which) |
| 124 | timeout |
| 137 | output limit or kill |

### 7.2 Receipt

Every executed step and every run MUST produce a receipt:

```json
{
  "receipt": "1",
  "run_id": "run_01JA…", "step": "translate", "attempt": 1,
  "artifact": "art_3f9c…", "input_version": "2.0.0",
  "capability": "cap_01JA…", "engine": "llm", "model_id": "…", "vendor": "…", "temperature": 0, "seed": 42,
  "ok": true, "code": 0, "criteria": [ { "check": "json_schema", "pass": true }, { "check": "judge", "score": 0.93, "pass": true } ],
  "tokens_in": 812, "tokens_out": 240, "cost_usd": 0.0031, "duration_ms": 1830, "cache_hit": false,
  "input_hash": "sha256:…", "output_hash": "sha256:…", "output_ref": "…",
  "truncated": false, "timeout": false,
  "prev": "sha256:<hash of previous receipt>", "hash": "sha256:<hash of this receipt with hash set to the empty string>",
  "ts": "2026-10-14T12:00:00Z"
}
```

Hashing rule (same as Ledger 0.1.0 §2 and §8.1): `hash` = SHA‑256 over the canonical receipt with `hash` set to `""`; `prev` of the first receipt of a run is `sha256:` + 64 zeros. `tokens_*`, `cost_usd`, `model_id`, `seed`, `cache_hit` are REQUIRED when the engine reports them and MUST be absent otherwise (never zero-filled). `isolation` (`"sandbox"` or `"none"`, Section 6.5) is REQUIRED in every step receipt. A flow's receipt lists its steps' receipt hashes and derives `ok` per §3.4 over its own criteria plus `all` of its steps unless gates say otherwise.

### 7.3 Ledger

Receipts of a run form an append-only, hash-chained sequence (`prev`). The runtime signs the chain head (`companions/ledger/0.1.0/SPEC.md`). Approval events (human gates), capability grants and policy denials are ledger entries with the same chaining.

### 7.4 Result object

`run()` returns `{ ok, code, run_id, artifact, receipts[], output, unexecutable?: reason }`.

---

## 8. Integrity, identity, crystals

### 8.1 Canonical form and hash

Canonical JSON is JCS (RFC 8785). For a document of kind `directory`, see Section 9.3. `integrity.hash` = `sha256:` + hex of SHA‑256 over the canonical document with `integrity.hash` and `integrity.signature` set to empty strings; when `integrity.signature` is absent, it is inserted as the empty string for this computation. A document whose `jos.version` is `1.0.x` and that has no `integrity.signature` member MAY instead carry the hash that 1.0.0 specifies (computed with `integrity.hash` set to the empty string and no `signature` member inserted); a verifier MUST accept either value for such a document, and its content identifier is the one of this section. A 2.x document, and a 1.0.x document that carries `integrity.signature`, is verified only by the rule of this section. `integrity.signed_by` is a key identifier; `integrity.signature` is a detached signature over the hash (ed25519 recommended). 1.1.0 `sig{hash,author,signature,timestamp}` maps to these fields.

`integrity.timestamp` (RFC 3339 date-time) records when the document was sealed. It is covered by the hash, it is informative, and a verifier MUST NOT use it to decide trust or ordering.

### 8.2 Identifiers

The **content identifier** of a document is `art_` + the hex digest of §8.1 (`companions/josid/0.1.0/SPEC.md`). Minted identifiers (`run_`, `cap_`, `usr_`, `rt_`, `host_`, `org_`, `apr_`) follow the JOSID specification. Relations between identifiers are stated in receipts and ledger entries, never by concatenation.

### 8.3 Crystals

A **crystal** is a document of kind `crystal` that seals one execution so it can be served instead of repeated:

```json
{
  "jos": { "version": "2.0.0", "kind": "crystal" }, "meta": { "name": "translate#1" },
  "crystal": {
    "key": "sha256:<crystal_key>", "artifact": "art_…", "inputs_hash": "sha256:…", "ctx_class": "prod",
    "engine": "llm", "model_id": "…", "temperature": 0, "seed": 42,
    "output_hash": "sha256:…", "output_ref": "crystals/translate#1.out", "receipt": "sha256:<receipt hash>",
    "created": "2026-10-14T12:00:00Z", "expires": null
  },
  "integrity": { "hash": "sha256:…", "signed_by": "…" }
}
```

| Member | Type | Meaning |
|---|---|---|
| `key` | `sha256:<64 hex>`, required | `crystal_key` below; the lookup key |
| `artifact` | `art_…`, required | content identifier (§8.2) of the document whose execution is sealed |
| `inputs_hash` | `sha256:<hex>` | hash of the canonical inputs of that execution |
| `ctx_class` | string | context class of the execution (`local`, `prod`, …); part of the key |
| `engine` | string | engine that produced the output (§6.1) |
| `model_id`, `temperature`, `seed` | string, number, integer | model parameters of the execution, when the engine calls a model (§6.2); part of the key |
| `output_hash` | `sha256:<hex>`, required | hash of the output bytes; a server MUST verify it before serving the crystal |
| `output_ref` | string | where the output bytes are stored: a path relative to the crystal or a `blob_` identifier |
| `receipt` | `sha256:<hex>` | hash of the receipt (§7) of the run that produced the output |
| `created` | RFC 3339 date-time | when the crystal was sealed |
| `expires` | RFC 3339 date-time or `null` | after this instant the crystal MUST NOT be served; `null` means no expiry |

`crystal_key = sha256( art_hash ‖ canonical(inputs) ‖ ctx_class ‖ model_id ‖ temperature ‖ seed )` where `‖` is concatenation with a `\n` separator and absent fields are the empty string.

A kernel MAY serve a crystal in place of executing a step when: the step's `reproducibility.class` is `deterministic`; or it is `bounded` and the effective policy allows (`cache: allow`); never when `stochastic` unless the Capability explicitly permits replay-from-crystal. A served crystal produces a receipt with `cache_hit: true` and `output_hash` equal to the crystal's.

### 8.4 `reproducibility`

| Field | Meaning |
|---|---|
| `class` | `deterministic` (same input → same output, e.g. `shell` with pinned inputs, `llm` at T=0 with pinned model and seed), `bounded` (variance within a tolerance), `stochastic` |
| `tolerance` | For `bounded`: numeric or `{ "metric", "value" }` |
| `n_runs` | Number of runs a conformance check uses to establish the class |

A kernel MUST derive `class` as `stochastic` when `temperature` > 0 and no seed is pinned, regardless of the declared value, and MUST record the derived class in the receipt.

---

## 9. Directories

### 9.1 A folder is a document

A directory `D` is a `.jos` when `D/.jos/manifest.jos` exists and is a document of kind `directory`. The manifest's `orchestration` describes the folder's flows; its `guardrails`, `security`, `tool_policy`, `model_policy` apply to everything below `D` that does not restrict them further. Folder layout. The location and meaning of `D/.jos/manifest.jos` (this section), the scope and inheritance rules (Section 9.2), the directory identity (Section 9.3) and the paths that Sections 9.2 to 9.4 name (`flows/`, `templates/`, `crystals/` and `store/` for `use` resolution; `logs/`, `replays/`, `dev/` and `ai/cache/` as excluded content) are normative. `D/.jos` MUST be a directory and `D/.jos/manifest.jos` MUST be a regular file; neither is a symbolic link (otherwise `D` is not a document, code 2). A kernel asked to validate or to run `D` or `D/.jos` (both name the directory `D`) whose manifest is not of kind `directory` refuses with code 2 at `/jos/kind` before any step, except a 1.0.0 manifest of kind `flow` whose `meta.labels.dotjos` is a string (the 1.0.0 `.jos/` convention), which is accepted as the manifest of `D` (`validate` reports it as a warning); `validate` and `run` give the same answer to the kind check for `D` and for `D/.jos` (`validate` may still report, as errors of its own, documents under `.jos/` that `run` does not read). Any other layout under `.jos/` is a convention of a runtime or of a companion specification and is not part of this specification; a runtime that does not read such a part MUST NOT treat its absence as a grant. A parser or validator of single documents does not need directory support. A kernel that claims the Composition level implements Sections 9.1 to 9.3, and a kernel that claims the Replay level also implements Section 9.4 (Section 11).

*Note (informative).* Running a folder and serving a crystallized directory are different things. When the reference kernels are asked to run `D` or `D/.jos`, they run `D/.jos/manifest.jos` as the document, with `D` as the working directory, and every step executes; a folder without `.jos/manifest.jos` is not a document and the run exits with code 2 (vectors `dir-run-folder`, `dir-run-folder-cwd`, `dir-run-no-manifest`). This follows from the first sentence of this section and adds no requirement. A crystallized directory (Section 9.4) is a later phase: its steps are served from crystals and no engine executes.

### 9.2 Scope and inheritance

The **scope** of a run is the nearest `.jos/` upward from the document's location. The **effective** document for a run is `merge(user, root, …, scope, document)` where: `guardrails.avoid` is the union; `guardrails.limit` is the element-wise minimum; `security.permissions` and `tool_policy.allowed` are the intersection; `tool_policy.denied` is the union; `model_policy` fields are the child's when present, else the parent's. A child MUST NOT widen. `use` resolution consults each `.jos/` in the chain (`flows/`, `templates/`, `crystals/`, a local `store/`) before the library and registries. `guardrails.inherit` MAY be declared with the single valid value `intersect` (the default); it exists only to state the rule explicitly, and no value can widen what the chain allows.

The chain is the user level (a runtime-configured directory, when one is configured) followed by every `D/.jos/manifest.jos` found from the filesystem root, or from a boundary the runtime declares, down to the scope. A runtime MUST declare the boundary it uses. `requires[]` and `capabilities[]` are not merged along the chain. The effective `security.tier` is defined in Section 6.5.

### 9.3 Directory identity

The identity of a directory `D` is computed over `D/.jos/`; content of `D` outside `.jos/` is not covered. Entries are read without following symbolic links. A regular file contributes the SHA-256 of its bytes; `manifest.jos` contributes the SHA-256 of its canonical form (Section 8.1) with `integrity.hash` and `integrity.signature` set to empty strings; a symbolic link whose target resolves inside `D/.jos/` contributes the SHA-256 of its target text. A symbolic link that dangles or resolves outside `D/.jos/`, and any entry that is neither a directory, a regular file nor such a link, makes the directory invalid (code 2). Entries under a path segment `logs`, `replays` or `dev`, or under `ai/cache`, at any depth, are excluded and are never opened. The directory hash is `sha256:` followed by the hex SHA-256 of the canonical JSON (RFC 8785) of `{ "files": { <path relative to D/.jos/, with "/" separators>: <hex digest> } }`, and the content identifier of `D` is `art_` followed by the same hex. For a document of kind `directory` at `D/.jos/manifest.jos`, `integrity.hash` is the directory hash and not the hash of Section 8.1. A kernel that runs `D` MUST compute the directory hash with the same entry rules before executing anything, MUST refuse a mismatch (code 3, `reason` `integrity.hash`), and records the content identifier of `D` as the `artifact` of the run.

### 9.4 Crystallized directories

A directory is **crystallized** when, for the flow(s) named in `manifest.jos → x-dotjos.crystallized_flows`, every step has a crystal in `.jos/crystals/` whose `crystal.key` matches the step's key under the directory's declared `ctx_class`, and those crystals are covered by §9.3. Running a crystallized directory executes no engine: every step is served (§8.3) and the run's receipts all carry `cache_hit: true`. A single mismatch makes the directory *partially crystallized*; the kernel MUST report which steps would execute.

---

## 10. Profiles

### 10.1 Mechanism

A profile is a named, versioned JSON Schema fragment that adds **optional** members under a reserved root key (or extends an existing member additively). A document lists the profiles it uses in `jos.profiles`. A kernel MUST validate the core; it MUST validate a listed profile when it knows it and MUST ignore unknown profiles' members. Profiles MUST NOT add required core members and MUST NOT change core semantics.

A profile adds optional members only and MUST NOT impose an obligation on the runtime. An obligation is a `requires[]` entry (Section 6.6), so that a runtime that does not know the profile refuses to execute the document instead of ignoring the profile.

### 10.2 Profiles defined alongside this specification

| Profile | Adds | Owner |
|---|---|---|
| `ui/1` | `ui` (1.0.0) | core editors |
| `observability/1` | `metrics` (1.0.0), receipt extensions `grade` | core editors |
| `commerce/1` | `billing` (1.0.0), store listing fields | core editors |
| `shadow/1` | clone protocol over the kernel envelope (A/B, canary, dispatch) | core editors |
| `exec-contract/1` | execution-contract blocks (gates, crystallization, persona, runtime, isolation, lineage). Vendor-neutral name; the product that originated it is a registered trademark and is not named in normative text | JOSFOX LLC |

---

## 11. Conformance

| Target | MUST |
|---|---|
| **Document** | Validate against `schema/jos.schema.json` after normalization; satisfy §2–§4 and the kind's required members |
| **Kernel — Core** | Implement §2.4 normalization for the three inputs, §3 atoms with `shell` engine, §3.4 done, §3.5 avoid/limit, §7 receipts and exit codes, §8.1–8.2 hash and ids; pass the `core` vectors in two independent implementations with identical receipts (except `duration_ms`, minted ids, `ts`) |
| **Kernel — Composition** | Core + §5 flows, DAG, gates, `use` resolution with integrity check, §9 directories and inheritance |
| **Kernel — Replay** | Composition + §7.3 ledger, §8.3 crystals and §9.4 crystallized directories, replay with divergence reporting |
| **Engine** | Declare its classes (`kind: engine`), report `tokens_*`/`cost_usd`/`model_id`/`seed`/`cache_hit` when applicable, honor `avoid` on its input and `limit` from the supervisor, never open a channel the Capability did not grant |
| **Registry** | Serve only sealed documents, verify signatures before `activate`, enforce Capability claims on publish and pull |

Conformance vectors live in `tests/` (document and schema) and `tck/documents/` (kernels), indexed in Appendix B.

---

## 12. Security considerations

A `.jos` document is JSON text and inherits the considerations of RFC 8259 §12. In addition:

1. **Declarative, never evaluated.** `execution.run`, `orchestration.definitions[*].command` and every other reference to a program or script are declarations. A parser or validator MUST NOT execute anything. Execution is the exclusive act of a conforming kernel after admission (a Capability with the required permissions and a positive budget) and inside the limits of §3.5. A document is never "executable" by being opened.
2. **Integrity and time of check.** `integrity.hash` is computed over the canonical form (JCS, RFC 8785). A kernel MUST canonicalize, hash and compare **before** executing and MUST execute exactly the bytes it hashed (re-parsed from the canonical form), so that no mutation between check and use is possible. A mismatch is a refusal (code 3), never a warning. The same holds for the detached manifest of a 0.0.7 document (Section 2.4): it detects change and does not authenticate a publisher.
3. **Untrusted inputs.** Natural-language members (`intention.objective`, `persona.system_prompt`, criteria text) reach language models; implementations MUST bound them (`guardrails.limit.context_tokens`, document size) and SHOULD apply prompt-injection mitigations declared by the engine. `billing`, `requires[]` and any member that names money, wallets or dependencies are untrusted input and MUST be validated against an authoritative source before use.
4. **URIs.** Documents MAY contain URIs. Implementations MUST NOT dereference them during validation. A kernel dereferences only PAL routes admitted by a Capability; raw URLs are adapter concerns and MUST be validated (allow-lists, no redirects beyond a declared count) to prevent SSRF.
5. **Supply chain.** `use` and `requires[]` resolve other documents. A kernel MUST verify `integrity.hash` of a resolved document when present and MUST verify a signature when the effective policy requires it; `requires[].digest` pins content.
6. **Keys and secrets.** Signing keys and secrets never appear in a document: `vault://` references resolve through a Capability and their values are never written to receipts, ledgers or outputs.
7. **Resource exhaustion.** Size, depth, time, output and token limits are mandatory in a conforming kernel (§3.5); limits cascade and only tighten.
8. **Transport.** Documents transmitted over a network SHOULD be served over TLS.

## 13. References

Normative: RFC 2119; RFC 8259 (JSON); RFC 6838 (media type registration procedures); RFC 6839 (structured syntax suffixes, `+json`); RFC 6901 (JSON Pointer); RFC 8785 (JCS canonicalization); RFC 3339 (timestamps); BCP 47 (language tags); JSON Schema 2020-12. Companion specifications: the documents under `companions/`, each with its own version and status (JOSID, Capability, Ledger and the context engine); `companions/README.md` states which of them are normative for each conformance class of Section 11. None of them changes the media type.

## Appendix A — Worked examples

A.1 `hello.jos` (§3.1). A.2 A flow with a DAG and a human gate (§5.1, §5.5). A.3 A template and its instantiation (§5.7). A.4 A crystal and a crystallized directory (§8.3, §9.4). A.5 A 0.0.7 document and its normalization (§2.4). A.6 A 1.1.0 short-form flow and its normalization. *(Files under `examples/`, each paired with its expected receipt.)*

## Appendix B — Vector index

Schema-level vectors are indexed in `tests/README.md` and document-level vectors are in `tck/documents/` with the promises and sections each one proves. Each release candidate publishes the traceability of every requirement of this text to the schema constraints and the vectors that enforce it (`tools/traceability.py`), including the requirements that still have no vector.

## Appendix C — Changes from 1.0.0

Additive: `jos.profiles`; `x-*`; criteria objects; `guardrails.limit` and `require` semantics; `needs`, gates as objects, `use`/`with`/`as` in definitions; `engine` classes; `model_policy.task_class/model_id/seed`; receipts and exit codes; kinds `template`, `crystal`, `directory`, `engine`; `crystal` member; `reproducibility.tolerance/n_runs`; `requires[].digest`. Moved to profiles: `ui`, `metrics`, `billing` (still read). Nothing removed; `required` at root unchanged (`jos`, `meta`).

Changes of meaning: `requires[]` and `security.tier: sandbox`, which 1.0.0 declared without runtime semantics, are enforced (Sections 6.5 and 6.6). A valid 1.0.0 document that declares them stays valid and can be unexecutable (code 5) in a runtime that cannot satisfy them. The number rule of Section 2.1 applies to every document whatever version it declares: a 1.0.0 document with a literal that no binary64 value carries through the canonical form is invalid in 2.0.0 (1.0.0 gave such a literal no reproducible canonical form, so its hash was never stable).
