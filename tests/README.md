# Test vectors (schema level)

Every file here is checked by `tools/validate-jos.py` against `schema/jos.schema.json`, without network access. `valid-*` files MUST validate; `invalid-*` files MUST fail, and each fails for the single reason given below. `tools/check-superset.py` also validates the `valid-1.0.0-*` files against the 1.0.0 schema. Document-level vectors (byte order mark, duplicate member names, canonical numbers and strings, an object that is not a .jos document) are in `kernel/` with their expected exit codes; they are run by the reference kernels, not by a JSON Schema validator. `CONFORMANCE.md` Section 7 indexes both sets.

| Vector | Expected | What it exercises |
|---|---|---|
| `invalid-alias-conflict.json` | invalid | `intention.intent` is not a 2.0 member; the 1.1.0 aliases exist only in the short form and are normalized before validation (SPEC Section 2.4) |
| `invalid-bad-kind.json` | invalid | `jos.kind` outside the closed list of Section 4.1 (`robot`) |
| `invalid-brand-block-in-core.json` | invalid | a product-named root block is not a core member; product data belongs to a profile or an `x-*` key (Sections 2.5, 10) |
| `invalid-definition-no-form.json` | invalid | a definition that is neither a step, a reference, a shell atom nor a document (Section 5.1) |
| `invalid-gate-bad-shape.json` | invalid | a gate object with `kind` outside `auto`/`human` and members a gate does not have (Section 5.5); the only error is the gate |
| `invalid-gate-missing-expr.json` | invalid | an `auto` gate without `expr` (Section 5.5) |
| `invalid-id-at-suffix.json` | invalid | an `id` carries no version: `rt.tool@0.3.1` fails the `id` pattern (Section 2.7); the version of a document is `meta.version` |
| `invalid-integrity-sig-member.json` | invalid | `integrity.sig` is not a member; the signature member is `integrity.signature` (Section 8.1) |
| `invalid-kind-pipeline.json` | invalid | `pipeline`, a kind of an earlier draft, is not a 2.0 kind (Section 4.1) |
| `invalid-meta-version-build-metadata.json` | invalid | build metadata (`1.0.0+build.5`) is not part of the `meta.version` pattern (Section 2.6) |
| `invalid-meta-version-hyphen-in-prerelease.json` | invalid | a hyphen inside the pre-release (`1.0.0-rc-1`) is not part of the `meta.version` pattern (Section 2.6) |
| `invalid-missing-jos.json` | invalid | the required root member `jos` is missing (Section 2.3) |
| `invalid-model-id-latest.json` | invalid | a floating model alias (`latest`) is not a pinned model identifier (Section 6.2) |
| `invalid-required-added.json` | invalid | a member new in 2.0 (`crystal`) without its own required members `key`, `artifact`, `output_hash` (Section 8.3); new required members appear only inside new optional members |
| `invalid-unknown-root-field.json` | invalid | an unknown non-`x-` root member (`intent`, the 1.1.0 flat form) makes the document invalid (Section 2.3) |
| `valid-1.0.0-full.json` | valid under 1.0.0 and 2.0.0 | the richest 1.0.0 example of the submission: intention, `execution.budget`, a flow with two definitions |
| `valid-1.0.0-minimal.json` | valid under 1.0.0 and 2.0.0 | the minimal 1.0.0 example of the submission |
| `valid-1.0.0-persona.json` | valid under 1.0.0 and 2.0.0 | a 1.0.0 document of kind `persona` |
| `valid-1.0.0-pipeline-original.json` | valid under 1.0.0 and 2.0.0 | a large 1.0.0 flow (18 definitions, string gates, `model_policy`, `tool_policy`, `reproducibility`) |
| `valid-2.0.0-aliases-1.1.0.json` | valid under 2.0.0 | the canonical 2.0 form of a document first written in the 1.1.0 short form (objective, criteria, avoid) |
| `valid-2.0.0-atom-exit-criterion.json` | valid under 2.0.0 | the Section 3.1 atom with the structured criterion `{ "exit": 0 }` |
| `valid-2.0.0-crystal.json` | valid under 2.0.0 | a document of kind `crystal` with every member of Section 8.3 |
| `valid-2.0.0-directory-kind.json` | valid under 2.0.0 | a document of kind `directory` with `guardrails.inherit: ["intersect"]` (Section 9.2) |
| `valid-2.0.0-directory.json` | valid under 2.0.0 | a directory manifest: string gates, `integrity` with `signed_by` and `timestamp`, `model_policy`, `tool_policy`, `reproducibility` (its hash is not re-sealed; the vector tests the shape) |
| `valid-2.0.0-engine.json` | valid under 2.0.0 | a document of kind `engine` declaring capabilities |
| `valid-2.0.0-flow-dag.json` | valid under 2.0.0 | a flow whose definitions are a reference, an inline shell step and a 1.0.0 step, with `needs` and object gates including `human` |
| `valid-2.0.0-model-policy-per-step.json` | valid under 2.0.0 | `model_policy` with `task_class`, a pinned `model_id`, `seed` and `per_step` overrides (Section 6.2) |
| `valid-2.0.0-pipeline-per-step.json` | valid under 2.0.0 | a large 2.0 flow (18 definitions) with mixed string and object gates, `model_policy.per_step` and `guardrails.inherit` |
| `valid-2.0.0-profile-exec-contract.json` | valid under 2.0.0 | `jos.profiles` naming `exec-contract/1`; profile members are validated by `schema/profiles/` (Section 10) |
| `valid-2.0.0-template.json` | valid under 2.0.0 | a document of kind `template` with slots (Section 5.7) |
| `valid-meta-version-prerelease-dots.json` | valid under 2.0.0 | a pre-release of letters, digits and dots after one hyphen (`1.0.0-rc.1.2`) and an `id` without `@` (Sections 2.6, 2.7) |
| `valid-use-semver-range.json` | valid under 2.0.0 | a `use` reference MAY add `@<semver range>` after the `id`: `^0.3.1`, `~1.2.0` and an exact `0.3.1` (Sections 2.7, 5.3) |
