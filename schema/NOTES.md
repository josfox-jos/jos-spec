# NOTES — schema 2.0 (regenerated 2026-10-14 from SPEC-2.0 Draft 1)

Generated programmatically: a deep copy of the registered 1.0.0 schema plus only the additions SPEC-2.0 defines, so the superset holds by construction. `$id` points at the immutable tag `v2.0.0`.

Added (all optional): `jos.profiles`; kinds `template, crystal, directory, engine` (the previous draft's `adapter, guardian, pipeline` removed: not in the spec); criteria objects (§3.3, same definition as `core.schema.json`); `guardrails.limit` (+ `context_tokens`, `tokens`, `cost_usd`), `guardrails.inherit`; `execution.engine/run/shell/cwd/env/outputs/on_error`; definitions as 1.0.0 step | `use` reference | inline shell atom | inline document, with `needs/with/as`; flows `parallel`, `on_error`, `outputs`, gates string or `{kind, expr, on_fail}`; `model_policy.task_class/model_id/seed/max_cost_usd/per_step`, `vendor` open; `requires[].digest` and more kinds; `integrity.signature`; `crystal`; `reproducibility.tolerance/n_runs`; `x-*` at every object; BCP 47 examples.

Moved out of the core into `schema/profiles/exec-contract-1.schema.json` (19 blocks of the execution-contract draft, applied when `jos.profiles` contains `exec-contract/1`). The core contains no product name.

Kept as core members for 1.0.0 compatibility: `ui`, `metrics`, `billing` (profile members, §2.3).

Gates: `tools/check-superset.py` (superset), jsonschema over the 43 normalized conformance documents (all valid in 2.0 and in core), `core.schema.json` ⊆ 2.0 on the same documents.
