# Examples

Documents taken verbatim from the document-level conformance suite (`tck/documents/`, where each one sits next to
its `*.expected.json`). Each one validates against `schema/jos.schema.json` and `schema/core.schema.json`; the
flow, template and directory examples run on the reference kernel `jos-core` (both engines; its version is in
`tck/reference-implementations.lock.json`) with the
results recorded in those expected files.

| File | Kind | Shows |
|---|---|---|
| `atom-hello.jos` | atom | the minimal executable document: objective, criteria `exit` and `stdout_contains`, `avoid`, limits, `engine: shell` |
| `flow-three-steps.jos` | flow | three atoms in sequence; the result carries one receipt per step and one for the flow |
| `flow-dag-needs.jos` | flow | `needs` edges: a failing step skips its dependents and unrelated branches continue |
| `template-with-slots.jos` | flow + template | `execution.inputs` as a JSON Schema of slots, `use` + `with`, deterministic `art_` |
| `crystal.jos` | crystal | a sealed execution record (SPEC-2.0 section 8.3) |
| `directory-manifest.jos` | directory | a `.jos/manifest.jos`: guardrails, permissions and tool policy that children may only restrict (section 9) |
| `legacy-1.0.0.jos` | 1.0.0 document | a registered 1.0.0 document, read unchanged |

Validate them: `python3 -I tools/validate-jos.py --schema schema/jos.schema.json examples/*.jos`
