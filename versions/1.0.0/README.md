# JOS 1.0.0

Version 1.0.0 is the version cited by the registration request of 2026-09-20 (IANA ticket 1460136). It remains in force; version 2.0.0 is an additive superset of it.

| Item | Where |
|---|---|
| Specification text | [SPECIFICATION.md](SPECIFICATION.md) (editorial copy; the publication of record is tag `v1.0.0` of this repository) |
| JSON Schema | [../../schema/1.0.0/jos.schema.json](../../schema/1.0.0/jos.schema.json), byte for byte the schema of tag `v1.0.0` |
| Examples | [examples/](examples/): `minimal.jos`, `flow.jos`, `persona.jos` |

## What 1.0.0 defines

A `.jos` document is one JSON object (RFC 8259) with a required `jos` header (`version`, `kind`) and `meta` (`name`), and optional members: `intention` (objective and success criteria), `guardrails` (avoid list, cost and retry limits), `capabilities` and `requires`, `tool_policy`, `execution` (engine, inputs, bindings to MCP and A2A, budget), `orchestration` (definitions and flows of steps with gates), `model_policy`, `persona`, `security`, `lifecycle`, `integrity` (a SHA-256 hash and a signer identifier), `reproducibility`, and the descriptive blocks `ui`, `metrics` and `billing`. Kinds: `atom`, `flow`, `service`, `persona` and the others of its kind registry. Version 1.0.0 describes documents; it does not define how a runtime executes them, which exit codes it returns or how results are recorded.

## What the registration request of 2026-09-20 said, and what this package says

| Template field | Request of 2026-09-20 | This package (`IANA.md`) | Why |
|---|---|---|---|
| Type and subtype | `application/vnd.jos+json` | `application/vnd.jos+json` | unchanged |
| Encoding considerations | `8bit` | `binary` | the registration of `application/json` (RFC 8259 Section 11) uses `binary` |
| Optional parameter `version` | default `1.0.0` when absent | no default; the document's `jos.version` is authoritative when the parameter is absent | a default would contradict a 2.0.0 document served without the parameter |
| Published specification | tag `v1.0.0` | tag `v2.0.0`, with tag `v1.0.0` still in force | 2.0.0 adds normalization, execution, receipts and conformance vectors |

## Try 1.0.0, and its compatibility with 2.0.0

From the root of this repository, without network access (Python 3 and the `jsonschema` package):

```
python3 -I tools/validate-jos.py --schema schema/1.0.0/jos.schema.json versions/1.0.0/examples/*.jos   # valid under 1.0.0
python3 -I tools/validate-jos.py --schema schema/jos.schema.json      versions/1.0.0/examples/*.jos   # the same documents are valid under 2.0.0
python3 -I tools/check-superset.py                                                                  # every 1.0.0 property and enum value is kept in 2.0.0
```

With a 2.0 implementation (for example the reference kernel attached to the release, `npx -y --package ./assets/josfox-jos-core-<version>.tgz jos-core validate versions/1.0.0/examples/flow.jos --json`, then `run`):

| 1.0.0 document | Valid under 1.0.0 | Valid under 2.0.0 | 2.0 kernel |
|---|---|---|---|
| `flow.jos` (two steps that reference the atoms `ai.example.atom.summarize` and `ai.example.atom.review` by id) | yes | yes | read unchanged; `run` exits with code 5, "not found", at the first step, because the referenced atoms are not in this folder |
| `minimal.jos` (nothing to execute) | yes | yes | read unchanged; `run` exits with code 5, "unexecutable" (valid, with no `execution`) |
| `persona.jos` (kind `persona`) | yes | yes | read unchanged; `run` exits with code 5, kind `persona` is not executable by the kernel |

What is not backward compatible, by design: a 1.1.0 short-form document is normalized to the 2.0 form before validation (its free root keys move under `x-`); a 0.0.7 document runs when its flow steps are strings, and is rejected with exit code 2 when they are objects (their normalization is scheduled for 2.1). The document-level vectors `legacy-1.0.0`, `short-1.1.0`, `legacy-0.0.7` and `legacy-0.0.7-prompt-step` in [../../tck/documents/](../../tck/documents/) fix each of these outcomes.
