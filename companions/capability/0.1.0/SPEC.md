# Capability and Policy — Specification

**Version:** 0.1.0 · **Status:** Draft · **Date:** 2026-10-14 · **Layer:** kernel · **Conformance:** `tests/vectors.json`
**Depends on:** JOSID 0.1.0, `.jos` 2.0 §3.5 (limits), §6.4–6.5 (tool_policy, security), §9.2 (inheritance) · **Used by:** supervisor, ledger, store.

RFC 2119 key words apply.

## 1. Purpose and invariant

Nothing runs without a Capability (kernel invariant **K1**). A Capability is a signed statement that a **subject** may execute an **object** in a **context** within a **budget** and a **permission set**. The only function in a conforming kernel that starts an engine or a process takes a Capability as its first argument and verifies it; no other call path exists. A conforming implementation MUST ship a test that proves there is exactly one such call site.

## 2. Structure

```json
{
  "cap": "cap_01JA…",
  "trust": "signed",
  "subject":  { "id": "usr_01JA…", "org": "org_01JA…", "roles": ["editor"] },
  "object":   { "artifact": "art_3f9c…", "kind": "flow", "visibility": "internal", "origin": { "host_class": "localhost", "org": "org_01JA…" } },
  "context":  { "runtime": "rt_01JA…", "runtime_class": "user", "host": "host_01JA…", "host_class": "cloud", "env": "prod", "ctx_class": "prod" },
  "permissions": ["engine:shell", "engine:llm", "fs:read:./", "fs:write:./out", "net:none"],
  "budget":   { "cost_usd": 2.0, "tokens": 500000, "seconds": 600, "output_bytes": 1048576, "retries": 3 },
  "cache":    "allow",
  "issued":   "2026-10-14T12:00:00Z", "expires": "2026-10-14T13:00:00Z",
  "issuer":   { "id": "rt_01JA…", "key": "ed25519:…" },
  "signature": "…"
}
```

| Field | Req | Meaning |
|---|---|---|
| `cap` | MUST | JOSID kind `cap` |
| `trust` | MUST | `signed` (verified signature), `local-trusted` (F0: constructed in-process by the gate, unsigned; MUST NOT cross a process or host boundary) |
| `subject` | MUST | Who. Claims: `id`, `org`, `roles[]` |
| `object` | MUST | What. `artifact` is the `art_` of the normalized document; claims `kind`, `visibility` (`public`, `community`, `internal`, `enterprise`), `origin` |
| `context` | MUST | Where. `runtime_class` ∈ {`sadmin`, `admin`, `user`, `public`}; `host_class` ∈ {`localhost`, `edge`, `cloud`, `vendor`}; `ctx_class` is the cache namespace |
| `permissions` | MUST | Grant list (§4). Deny by default: anything not listed is denied |
| `budget` | MUST | Hard ceilings; the supervisor enforces (K2) |
| `cache` | MAY | `allow` / `deny` / `replay-only` for crystals (`.jos` 2.0 §8.3) |
| `issued`, `expires` | MUST | RFC 3339; an expired Capability is invalid |
| `issuer`, `signature` | MUST when `trust: signed` | ed25519 over the canonical Capability with `signature` empty |

A Capability is bound to **one** `object.artifact`. A flow's Capability covers its steps only through **derivation** (§6).

## 3. Admission

`admit(document, subject, context, policy) → Capability | Denial` is a **pure function** of its inputs. It MUST: normalize the document and compute `art_`; evaluate the policy (§5) over claims; compute the effective permissions as the **intersection** of document declarations (`security.permissions`, `tool_policy`), the directory chain (`.jos` 2.0 §9.2), the subject's grants and the runtime's grants; compute the effective budget as the element-wise **minimum** of document `guardrails.limit`, chain limits, subject budget and runtime budget; return a Denial with a reason code when any required permission is absent or the budget is non-positive.

Denials are ledger entries. Admission never spawns anything.

## 4. Permission vocabulary

`<domain>:<action>[:<scope>]`, lowercase. Core domains: `engine` (`shell`, `llm`, `function`, `judge`, `decompose`, `human`, `jos`), `fs` (`read`, `write` with a path scope relative to the run's `cwd`), `net` (`none`, `egress:<host-pattern>`), `vault` (`read:<ref-pattern>`), `store` (`pull:<visibility>`, `publish:<visibility>`), `clone` (`spawn`, `kill`), `shell` (`enable` — required for `execution.shell: true`). Profiles MAY add domains with their own prefix.

## 5. Policy

A policy is an ordered list of rules evaluated first-match, with a final implicit `deny`:

```json
[
  { "effect": "deny",  "when": "subject.org != object.origin.org && object.visibility == 'enterprise'" },
  { "effect": "deny",  "when": "action == 'store:publish:enterprise' && object.origin.host_class == 'localhost'" },
  { "effect": "deny",  "when": "action == 'store:pull:*' && object.visibility == 'enterprise' && context.runtime_class == 'public'" },
  { "effect": "allow", "when": "subject.org == object.origin.org" }
]
```

`when` is a boolean expression over `subject.*`, `object.*`, `context.*`, `action`, `document.*` (normalized document fields) with operators `== != in && || !` and glob `*`. It MUST be side‑effect free and MUST evaluate in bounded time (no loops, no calls). Rules reference classes and claims (JOSID §5.4), never identifier strings except equality.

**Layering (brick ∩ user ∩ environment).** Policies come from three sources: the document and its directory chain, the subject's grants, the runtime. The effective result is the intersection: any source may deny; all must allow.

### 5.1 Roles and RBAC (absorbed here; no external library)

RBAC is not a separate component. A **role** is a claim in `subject.roles[]`; a **role definition** is a policy fragment that maps a role to permissions and budgets; both live in the directory chain under `.jos/auth/`:

```
.jos/auth/roles.jos      kind: atom, x-auth: { roles: { owner: { permissions: ["engine:*", "store:publish:internal"], budget: {...} }, editor: {...}, auditor: { permissions: ["ledger:read:*"] } } }
.jos/auth/policy.jos     kind: atom, x-auth: { rules: [ ...§5 rules... ] }
```

Resolution: roles and rules are collected along the chain from root to scope; a deeper level MAY add rules and MAY narrow a role, never widen it (the effective permission set of a role is the intersection across levels; budgets the minimum). Identity providers (OIDC, Firebase, API keys) are host adapters that produce `subject` claims; they never evaluate policy. Runtime classes (`sadmin`, `admin`, `user`, `public`) are `context.runtime_class` claims and are matched by rules exactly like roles. The whole evaluation is the pure function of §3: no I/O, no model, bounded time; a conforming implementation is expected in about a hundred lines with zero dependencies.

## 6. Derivation for flows and clones

A step of a flow runs under a **derived** Capability: same subject and context, `object.artifact` = the step's `art_`, permissions ⊆ parent, budget ≤ parent's *remaining* budget (the supervisor subtracts as receipts are sealed), `expires` ≤ parent's. A shadow clone receives a derived Capability with its own `clone_` id and its own ledger. Derivation is recorded in the ledger (`{ cap: child, from: parent }`). A derived Capability MUST NOT widen anything.

## 7. Enforcement points

| Point | Check |
|---|---|
| Before spawn | `trust` valid, not expired, signature (if `signed`), `object.artifact == art_(document)`, required engine permission present, `avoid` not matched, budget positive |
| During | Supervisor counters vs `budget`; exceed → kill, code 124/137/4 |
| On `use` | Derived Capability for the resolved artifact; integrity verified |
| On store publish/pull | `store:*` permission and policy over `visibility`/`origin` |
| On vault read | `vault:read` scope; the value is passed to the engine and never written to the ledger |

## 8. Security considerations

A `local-trusted` Capability is a programming convenience for single-process kernels and MUST be rejected if received from another process, file or network. Signed Capabilities are bearer tokens: they MUST be short-lived and bound to one artifact. The gate's signing key is the runtime's identity (JOSID `rt_`); key custody is a vault concern, outside the kernel.

## 9. Conformance

Vectors: admission allow/deny for each rule of §5 with the four example policies; intersection and minimum computations; derivation that attempts to widen (MUST fail); expired, unsigned-but-`signed`, mismatched-artifact Capabilities (MUST fail); the single-call-site test description.
