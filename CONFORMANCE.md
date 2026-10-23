# Conformance

This document defines conformance requirements for `.jos` 2.0.0 documents, parsers and runtimes. It is part of the registration package for `application/vnd.jos+json`. The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in capitals. Section references of the form "SPEC" are to `SPECIFICATION.md`.

## 1. Document conformance

A JOS document conforms when it:

1. is valid UTF-8 JSON text (RFC 8259) without a byte order mark;
2. has an object as its top-level value;
3. has no two members with the same name in any object;
4. contains the `jos` object (with `version` and `kind`) and the `meta` object (with `name`);
5. validates against the JOS 2.0.0 JSON Schema (`schema/jos.schema.json`) after normalization (SPEC Section 2.4);
6. satisfies the requirements of SPEC Sections 2 to 4 and the required members of its kind (SPEC Section 4.1);
7. is in the canonical form: a 1.1.0 short-form spelling (for example `intention.intent` next to `intention.objective`) is normalized before validation (SPEC Section 2.4) and is not a member of the canonical form.

Schema validation is necessary and is not sufficient: some requirements (acyclic `needs`, unique names, integrity) are checked by code.

Every document that is valid under JOS 1.0.0 is a valid document under 2.0.0, with one exception: a number literal that Section 2.1 of the specification makes invalid (an integer value of magnitude above 2^53 and below 10^21, such as `1e20`, or a decimal that is not the shortest round-trip form of its binary64 value) is invalid whatever version the document declares. 1.0.0 gave such a literal no reproducible canonical form, so no hash of such a document was ever stable.

## 2. Parser conformance

A conforming parser:

- MUST parse according to RFC 8259;
- MUST reject invalid UTF-8;
- MUST reject a leading byte order mark;
- MUST reject duplicate object member names;
- MUST preserve member names unchanged;
- MUST NOT execute, resolve, fetch or interpret any member while parsing;
- MUST apply the size, depth and count limits of `SECURITY.md` Section 8 and fail closed when one is exceeded.

## 3. Runtime conformance

A conforming runtime:

- MUST validate a document before interpreting it, and MUST distinguish an invalid document from a valid document that it cannot execute (SPEC Section 1.2);
- MUST declare the JOS versions and kinds it supports, MUST read a later minor version of a major version it implements as SPEC Section 2.2 states, and MUST reject or decline any other version or kind rather than reinterpret it;
- MUST NOT start a document that has an unsatisfied `requires[]` entry (SPEC Section 6.6), or a step whose effective tier is `sandbox` that it cannot confine (SPEC Section 6.5); both are exit code 5;
- MUST apply independent authorization and sandbox policy, and MUST NOT treat a declared permission as a granted permission (`SECURITY.md` Section 3);
- MUST enforce resource budgets at or below runtime policy;
- MUST let stricter runtime policy prevail over document policy;
- MUST treat external references as untrusted (`SECURITY.md` Section 7);
- MUST produce a receipt for each executed step (SPEC Section 7.2) and use the exit codes of SPEC Section 7.1;
- SHOULD keep trusted instructions and untrusted document content separate when it calls a language model (`SECURITY.md` Section 4).

A runtime MAY support a subset of kinds. If it does not support the `jos.kind` of a document, it MUST reject or decline execution (exit code 5 for a valid document with no engine).

## 4. Normalization conformance

A kernel MUST implement the normalization of SPEC Section 2.4 for the 2.0 canonical form, the 1.0.0 form, the 1.1.0 short form and the 0.0.7 legacy form with string flow steps (a 0.0.7 document with object-form steps is rejected with exit code 2), and MUST apply it before validation and before hashing a short-form document. The receipt MUST record `input_version`.

## 5. Media type conformance

When `application/vnd.jos+json; version=...` is used:

- the value of `version` MUST have the form `MAJOR.MINOR.PATCH`;
- the value of `version` MUST equal `jos.version`;
- a receiver MUST treat a mismatch as an error and MUST NOT process the representation;
- when `version` is absent, `jos.version` is authoritative; there is no default.

A receiver MUST NOT select a handler from the file extension alone (`.jos` is also used by unrelated software).

## 6. Integrity conformance

A runtime that claims support for `integrity.hash` MUST implement the procedure of `SECURITY.md` Section 5: RFC 8785 canonicalization with `integrity.hash` and `integrity.signature` set to the empty string, SHA-256 over the canonical bytes, comparison, and execution of the object that was hashed. It MUST NOT treat `integrity.signed_by` as proof of identity.

For `kind: directory`, the hash scope is that of SPEC Section 9.3.

## 7. Test vectors

Vectors are in `tests/` (document and schema level) and run without network access. They are indexed in `tests/README.md`.

| Vector | Expected result | Requirement exercised |
|---|---|---|
| `invalid-alias-conflict.json` | invalid | `intention.intent` is not a 2.0 member; the 1.1.0 aliases exist only in the short form and are normalized before validation (SPEC Section 2.4) |
| `invalid-bad-kind.json` | invalid | `jos.kind` outside the closed list of Section 4.1 (`robot`) |
| `invalid-brand-block-in-core.json` | invalid | a product-named root block is not a core member; product data belongs to a profile or an `x-*` key (Sections 2.5, 10) |
| `invalid-definition-no-form.json` | invalid | a definition that is neither a step, a reference, a shell atom nor a document (Section 5.1) |
| `invalid-gate-bad-shape.json` | invalid | a gate object with `kind` outside `auto`/`human` and members a gate does not have (Section 5.5); the only error is the gate |
| `invalid-gate-missing-expr.json` | invalid | an `auto` gate without `expr` (Section 5.5) |
| `invalid-integrity-sig-member.json` | invalid | `integrity.sig` is not a member; the signature member is `integrity.signature` (Section 8.1) |
| `invalid-kind-pipeline.json` | invalid | `pipeline`, a kind of an earlier draft, is not a 2.0 kind (Section 4.1) |
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
| `valid-2.0.0-directory-kind.json` | valid under 2.0.0 | a document of kind `directory` with `guardrails.inherit: "intersect"` (Section 9.2) |
| `valid-2.0.0-directory.json` | valid under 2.0.0 | a directory manifest: string gates, `integrity` with `signed_by` and `timestamp`, `model_policy`, `tool_policy`, `reproducibility` (its hash is not re-sealed; the vector tests the shape) |
| `valid-2.0.0-engine.json` | valid under 2.0.0 | a document of kind `engine` declaring capabilities |
| `valid-2.0.0-flow-dag.json` | valid under 2.0.0 | a flow whose definitions are a reference, an inline shell step and a 1.0.0 step, with `needs` and object gates including `human` |
| `valid-2.0.0-model-policy-per-step.json` | valid under 2.0.0 | `model_policy` with `task_class`, a pinned `model_id`, `seed` and `per_step` overrides (Section 6.2) |
| `valid-2.0.0-pipeline-per-step.json` | valid under 2.0.0 | a large 2.0 flow (18 definitions) with mixed string and object gates, `model_policy.per_step` and `guardrails.inherit` |
| `valid-2.0.0-profile-exec-contract.json` | valid under 2.0.0 | `jos.profiles` naming `exec-contract/1`; profile members are validated by `schema/profiles/` (Section 10) |
| `valid-2.0.0-template.json` | valid under 2.0.0 | a document of kind `template` with slots (Section 5.7) |
| `kernel/invalid-bom.jos` + `.expected.json` | document-level (exit code and masked output) | leading BOM rejected (SPEC-2.0 §2.1, exit 2) |
| `kernel/invalid-duplicate-keys.jos` + `.expected.json` | document-level (exit code and masked output) | duplicate member names rejected (IANA.md Interoperability, exit 2) |
| `kernel/jcs-numbers.jos` + `.expected.json` | document-level (exit code and masked output) | RFC 8785 canonical numbers in art_ |
| `kernel/jcs-unicode.jos` + `.expected.json` | document-level (exit code and masked output) | RFC 8785 canonical strings in art_ |
| `kernel/invalid-not-a-jos-document.jos` + `.expected.json` | document-level (exit code and masked output) | a JSON object without `jos` and `meta` (an envelope with the members `protected`, `payload` and `signature`) is not a .jos document (SPEC-2.0 §1) |

One vector is still missing: a `version` media type parameter that disagrees with `jos.version` (the parameter lives in the transport, not in the document, so the vector is a processor-level test to be written with the first HTTP host). Duplicate member names, leading BOM, RFC 8785 canonicalization and an object that is not a .jos document are covered by the document-level vectors under `tests/kernel/`.

Checks that a repository maintainer runs from the `2.0/` directory (`jsonschema` required):

```
python3 -I tools/check-superset.py
python3 -I tools/validate-jos.py --schema schema/jos.schema.json tests/valid-*.json
```

`tools/check-superset.py` exits with code 0 when every 1.0.0 vector and example validates under 2.0.0, every 2.0.0 vector validates, every invalid vector fails, and no `required` list of a node that exists in 1.0.0 gained an entry. `tools/url-check.py --human` is a person's record that each URL of the release resolved; it makes no network request.

## 8. Kernel and engine levels

Levels of kernel conformance (Core, Composition, Replay), and the conformance of an engine and of a registry, are defined in SPEC Section 11.

## 9. Conformance claims of the reference kernels

Measured on 2026-10-21 with `python3 -I kernel/tests/conformance/run.py` in the development repository, on both reference kernels `jos-core` 2.0.0 (JavaScript on Node.js 24.19, Python 3.12.7), offline. This runner is not part of this repository. What a third party can run is the document level of the TCK on the implementations attached to the release (`tools/verify-reference-implementations.py`, whose results the release job publishes).

| Group | Checks | Result |
|---|---|---|
| Document vectors (validate and run, both kernels, masked results compared in RFC 8785 canonical form; every receipt checked for `isolation: "none"`) | 3268 | pass |
| Canonical form (RFC 8785), identifiers, Capability (admission and derivation, both kernels; `expires` as an RFC 3339 date-time under three time zones) | 605 | pass |
| Platform access layer, directories, ledger | 282 | pass |
| Graph of identifiers (experimental in jos-core 2.0.0) | 148 | pass |
| Embedded store (JOSDB; tested from source, not part of the jos-core 2.0.0 packages, planned for 2.1) | 190 | pass |
| Independent review vectors, fuzzing, static (packaging, public names, version line), runtime (cancellation, symbolic links, directory hash, `--version`, limits) and timing checks | 429 | pass |
| Command line of both kernels, path by path (usage errors, help, text forms, `validate` of a folder, `ids`, `facts`, `run --uses`, version ranges of `use`) | 379 | pass |
| **Total** | **7179** | **7179 pass, 0 fail (CONFORMANT)** |

Every promise of `PROMISES.md` scheduled for the first two phases has a vector in this run (16 of 16 and 16 of 16). The level reached is Core plus Composition (SPEC Section 11). A third-party implementation claims conformance with `tck/run.py` (schema level) and `tck/run-documents.py` (document level, Section 7).

What the reference kernels do not do, measured on the same date, so that no reader takes it for a property of the format or of the kernels:

- They confine no process. Every step runs as a local, trusted process and every receipt records `isolation: "none"` (SPEC Section 6.5). A document whose effective tier is `sandbox` is therefore never run by them (exit code 5, vectors `tier-*`); a document with any other tier runs without confinement, and the permission `net:none` of its Capability states what was granted, not what was enforced on the processes of a step.
- They satisfy only `requires[]` entries of kind `artifact` that resolve (inline, through the `.jos/` chain or the library) in the requested version and, with `digest`, to that content identifier. Entries of kind `mcp-server` or `service` are never satisfied, so a document that declares one is not run (exit code 5, vectors `requires-*`).
- They do not verify signatures, so a `privileged` document is not run (exit code 5, vector `tier-privileged-unsigned`).
- They record `require_auth`, `require_admin` and `require_approval` and do not enforce them (SPEC Section 6.5): those are declarations for the host that admits the caller.
- The boundary they declare for the `.jos/` chain (SPEC Section 9.2) is the filesystem root: they read every `.jos/manifest.jos` from the document's directory up to `/`, plus the user level `<home>/.jos/` when a home directory is given (`--home`).
- They run on macOS and Linux (POSIX). A command line runs under `/bin/sh` and cancellation signals process groups, so Windows is not a platform of the 2.0.0 reference kernels; their CI runs on Windows for information only.
- They give identical results on every document vector (`tck/compare-implementations.py`: 0 differences). An integer literal that no IEEE 754 double represents exactly, and any integer value with magnitude above 2^53 and below 10^21, is invalid (SPECIFICATION Section 2.1, vector `jcs-numbers` and the `invalid-number-*` vectors), so neither kernel ever has to echo such a number; SECURITY.md recommends carrying large integers as strings.
