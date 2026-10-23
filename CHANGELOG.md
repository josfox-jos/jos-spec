# Changelog

All notable changes to the JOS specification are documented here. Versions are semantic. A released version is the git tag `vMAJOR.MINOR.PATCH`.

## [2.0.0] - 2026-10-22

Additive superset of 1.0.0. No required member is added at the root (`jos` and `meta` remain the only ones). No member of 1.0.0 is removed.

### Changed
- One media type: `application/vnd.jos+json`. One registration text (`IANA.md`).
- `Encoding considerations`: `binary` (RFC 8259 Section 11).
- Media type parameter `version`: no implicit default; `jos.version` is authoritative; a mismatch is an error.
- `integrity.hash` is computed over the RFC 8785 canonical form with `integrity.hash` and `integrity.signature` set to the empty string; verification precedes execution.
- Members `ui`, `metrics`, `billing` move to profiles (`ui/1`, `observability/1`, `commerce/1`) and are still read.
- Language tags in examples are BCP 47 with a hyphen (`en-US`).

### Added
- Optional header member `jos.profiles` and the profile mechanism; `x-*` extension keys.
- Kinds `template`, `crystal`, `directory`, `engine` (see SPEC Section 4.1).
- Criteria objects (`exit`, `stdout_matches`, `json_schema`, `sha256`, `judge`, `all`, `any`, `not`), `guardrails.limit`, `guardrails.require`.
- Composition: `use`, `with`, `as`, `needs` (acyclic graph), gate objects.
- Engine classes, `model_policy.task_class`, `model_id`, `seed`.
- Receipts, exit codes, ledger, crystals, `reproducibility.tolerance` and `n_runs`, `requires[].digest`.
- Normalization on read of 1.1.0 short-form and 0.0.7 legacy input.
- Registration package: `IANA.md`, `SECURITY.md`, `GOVERNANCE.md`, `CONFORMANCE.md`, `CONTRIBUTING.md`, `README.md`, `LICENSE`, `CHANGELOG.md`.
- Security requirements: active-content declaration, prompt-injection mitigations, TOCTOU procedure for `integrity.hash`, untrusted `billing`, SSRF, limits, TLS, duplicate-key rejection, UTF-8 without BOM.

### Compatibility
- Every valid 1.0.0 document is valid under 2.0.0 (`tools/check-superset.py`). The one qualification is numeric: a number literal that Section 2.1 of the specification makes invalid (an integer value with magnitude above 2^53 and below 10^21, or a decimal that is not the shortest round-trip form of its binary64 value) is invalid whatever version the document declares; 1.0.0 gave such literals no reproducible canonical form, so no hash of such a document was ever stable.

## Release candidates of 2.0.0

Each candidate is a tag `jos-spec-v2.0.0-rc.<n>` on the review branch; these sections are its release notes.

### [2.0.0-rc.8] - 2026-10-21

The reference kernel attached to this candidate is `jos-core` 2.0.0-rc.9; the command-line host is `@josfox/jos` 5.0.0-rc.5.

**Normative text:** the requirements of 2.0.0-rc.7 are unchanged. Changes, all from independent reviews of the candidate:

- Compatibility wording states the number-rule exception in every place that speaks of compatibility with 1.0.0 (external review RC7-03): `CONFORMANCE.md` Section 1, the compatibility paragraph of `IANA.md`, `RELEASE_PROCESS` and `README.md`.
- `schema/core.schema.json` agrees with `schema/jos.schema.json` and the text: an `id` carries no `@<version>` suffix, and the pre-release of `meta.version` has no hyphen (the published `jos.schema.json` already enforced both).
- `IANA.md` Security considerations cite the stable URL of `SECURITY.md` at the tag `v2.0.0`.
- `IANA.md`: language tags in documents SHOULD be BCP 47 tags with a hyphen; the schema does not enforce the syntax (decision of the change controller, 2026-10-21; the text said they are).
- The table of Section 2 states that `jos.version` is `MAJOR.MINOR.PATCH`, as the schema enforces.
- Profile `exec-contract/1`: identifier patterns accept any lowercase prefix of 2 to 8 letters instead of one vendor prefix (every identifier valid before stays valid); its `$comment` no longer refers to a product.
- `CONFORMANCE.md`: the example of `guardrails.inherit` is a string, as the schema defines it.

**Conformance:** 7179 checks on both kernels (`CONFORMANCE.md` Section 9), document TCK 279/279 on both, 0 parity differences.

### [2.0.0-rc.7] - 2026-10-21

The reference kernel attached to this candidate is `jos-core` 2.0.0-rc.8; the command-line host is `@josfox/jos` 5.0.0-rc.4.

**Normative text:** twelve sentences, each already enforced by both reference kernels and covered by vectors (the sentence-by-sentence justification is in the review record of this candidate). Eight are clarifications of text that two implementers could read differently: the detection order of Section 2.4 (and a root `intent`/`use` beside a 2./1.0. header is an unknown root member); the 0.0.7 row keeps definitions as written, so a `type` outside `shell`/`jos`/`http` is invalid (2); `meta.version` as the schema enforces it; `id` carries no version (`@` is invalid; `use` keeps `@<semver range>`); a definition is exactly one of four closed forms (Section 5.1); gate keys `after-<step>` (Section 5.5); the semantics of the 1.0.0 alias `execution.flow` (Section 6.8); and the Section 8.1 seal when `integrity.signature` is absent, with the 1.0.x hash accepted for 1.0.x documents without a signature. The sentence on the 0.0.7 normalization both kernels apply (Section 2.4: members the schema does not define inside `security`, `guardrails`, `intention`, `meta`, `tool_policy`, `model_policy` and `orchestration` move to `x-legacy-<member>`, never dropped; `max_retries`/`timeout_ms` merge into a declared `limit`; a non-empty `files` list becomes definitions and is not kept, an empty or non-array one is kept as `x-legacy-files`; `orchestration_contract` is kept unless it is a string `version` alone; collisions are code 2) and three clarifications of edge cases (lexical resolution of `integrity_ref`, the file system's case rule, `<name>#<n>` beside `after-<name>`). Three are tightenings and are named as such: a number literal whose value is an integer with magnitude greater than 2^53 and less than 10^21 is invalid however it is written, so the canonical form of a valid document is valid (Section 2.1; `SECURITY.md` item 6 already required exact values for hashed members, and every member is hashed), and the 0.0.7 detached manifest `security.integrity_ref` MUST be verified before the first step (Section 2.4; codes 3 and 5 in Section 7.1; Section 12 item 2), which `@josfox/jos` 4.0.6–4.1.0 implemented and 2.0 had silently dropped, and a kernel asked to validate or to run a folder `D` or `D/.jos` whose manifest is not of kind `directory` refuses it with code 2 before any step, except a 1.0.0 manifest of kind `flow` with `meta.labels.dotjos`, so that `validate` and `run` agree (Section 9.1). The 0.0.7 normalization also tightens edge inputs of 0.0.7 documents, each named here. A guard member that the schema defines with another shape (in `guardrails`, `security`, `tool_policy`, `model_policy`, and `intention.success_criteria`) is code 2 and never moved, because the document ran without the limit, `avoid`, tier or policy it states. A value that a mapping produces must satisfy Section 2.1 and the schema, so `max_retries: "3"`, a negative or non-number `timeout_ms` and `timeout_ms: 1e22` are code 2. A `files` entry that is neither a string nor an object, and a `meta` that is not an object, are code 2 instead of being dropped. A missing `meta.name` is `id_jos` as written, no longer cut to 128 characters. No change to the media type or the schema; for 1.0.0 documents the only effect is the number rule (a literal that no binary64 value carries through the canonical form was never hashable, and is now invalid).

**Conformance:** 7177 checks on both kernels (`CONFORMANCE.md` Section 9), document TCK 279/279 on both, 0 parity differences; new vector groups `numbers`, `init-0.0.7`, `legacy-ref`; vectors for every rc.7 sentence (`detect-*`, `invalid-id-at-suffix`, `invalid-meta-version-*`, `legacy-0.0.7-limit-*`, `legacy-0.0.7-*-collision`, `invalid-number-1e20`, `dir-run-manifest-*`). After readiness pass 5: vectors for the 0.0.7 normalization (`legacy-0.0.7-contract-*`, `-files-*`, `-guard-*`, `-tool-policy-kept`, `-meta-not-object`, `-name-*`, `-root-x-member`, `-max-retries-shape`, `-timeout-ms-*`, every valid one with its `art_` pinned), for folders (`dir-validate-run-dot-jos`, `dir-run-manifest-not-directory-dot-jos`, `dir-run-manifest-1.0.0-labels-dotjos`) and for Section 5.1 (`invalid-definition-short-form-member`, `invalid-definition-type-outside-enum`).

### [2.0.0-rc.6] - 2026-10-20

The reference kernel attached to this candidate is `jos-core` 2.0.0-rc.7; the command-line host is `@josfox/jos` 5.0.0-rc.3.

**Normative text:** unchanged since 2.0.0-rc.5, except one editorial sentence in Section 13. The references no longer call PAL and Envelope specifications "of this repository" (they are not part of it) and no longer list JOSID and Capability as merely informative: they point to `companions/README.md`, which states which companion is normative for each conformance class of Section 11. No requirement is added.

**Conformance kit**
- `tck/run-documents.py`: an alternative outcome that rests on a property the kit cannot observe carries `"claim"`; today the run of a `sandbox` step (`"claim": "sandbox"`). A run that matches it is reported as UNVERIFIED (exit code 2), never as a pass, because a receipt that says `isolation: "sandbox"` is not evidence of confinement (Section 6.5). A vector whose validation fails is a failure even if its run matches such an alternative.
- `tck/compare-implementations.py`: runs two implementations on the same documents and compares their complete results (exit codes, every member printed by `validate` and `run`, receipts, error texts); it normalizes only what the specification allows to differ (minted identifiers, `ts`, durations, receipt hashes after verifying them).
- 59 new document vectors (192 in total): `requires` of every kind, satisfied and not; `sandbox` through every path (document, flow, step, definition, every level of the `.jos/` chain, 1.0.0 documents); sealed folders changed in every way (file edited, added, deleted, renamed, step swapped, excluded entries changed); `dir-sealed-external-program`.
- The README of the kit says what the document level cannot observe: side effects of a refused step.

**Package**
- `SECURITY.md` Section 5: the directory hash identifies the folder's documents, not the programs they run, and does not make a run reproducible; pin a program with `requires[].digest` (Section 6.6).
- `IANA.md` cites RFC 6838 Section 4.4 (for the vendor tree a public specification is encouraged, not required) where it cited Section 4.10.
- `CONFORMANCE.md` Section 9: 5301 checks of the reference kernels; they run on macOS and Linux; their only difference is the echo of an integer outside the interoperable range of RFC 8259 Section 6 (vector `jcs-numbers`, same `art_`).
- `.well-known/security.txt`: its pending marker is written so that the check of a final tag finds it.

### [2.0.0-rc.5] - 2026-10-20

The reference kernel attached to this candidate is `jos-core` 2.0.0-rc.6; the command-line host is `@josfox/jos` 5.0.0-rc.2.

**Normative text (decisions D-1, D-3, D-4 and D-8, approved by the change controller after an independent review)**
- Section 9.1 and 9.3, the directory:
  - the location and meaning of `D/.jos/manifest.jos`, the chain (9.2), the directory identity (9.3) and the paths that 9.2 to 9.4 name are normative; any other layout under `.jos/` is a runtime convention;
  - `D/.jos` and the manifest cannot be symbolic links;
  - 9.3 states the algorithm: root `D/.jos/`, entries read without following links, the manifest in canonical form with `integrity.hash` and `integrity.signature` empty, the exclusions;
  - for a manifest of kind `directory`, `integrity.hash` is the directory hash, and `run` verifies it before anything starts. This resolves a contradiction of rc.4, where `validate` and `run` read `integrity.hash` with two different meanings, so no sealed folder could run;
  - Section 8.1 points to 9.3;
  - 9.2 says that `requires[]` is not merged along the chain and that a runtime declares its boundary.
- Section 2.2: a reader of 2.0.0 accepts a later minor version of major 2 and validates it with the schema it implements, so anything added later is invalid for it. `1.0.x` is read as in 2.4; any other version is invalid.
- Section 6.6 (new subsection): obligations are `requires[]` entries, decided before the first step from the runtime's own configuration. An unsatisfied entry makes the document unexecutable (code 5), naming the entry by JSON Pointer.
- Section 6.5 (new subsection):
  - when the effective tier of a step is `sandbox` (declared by the step, an enclosing document or any level of its chain), the runtime confines the processes of the step as stated, or refuses the run before its first step (code 5);
  - every step receipt records `isolation` (Section 7.2);
  - `require_auth`, `require_admin` and `require_approval` are declarations for the host's authorization layer, not guarantees of the core kernel;
  - a `privileged` document whose signature the runtime cannot verify is not run (code 5).
- Section 6.8: `cwd` resolves inside the document's directory (code 3); confinement of the processes is only that of 6.5.
- Section 7.1: code 3 names `cwd` outside the directory; code 5 names unsatisfied `requires[]`, isolation not available and a signature that cannot be verified.
- Section 10.1: a profile imposes no obligation; an unknown profile is ignored.
- Appendix C: `requires[]` and `security.tier: sandbox` gain runtime meaning; a 1.0.0 document that declares them stays valid and can be unexecutable.
- `SECURITY.md`, `CONFORMANCE.md`, `VERSIONING.md` and `IANA.md` (security, interoperability and versions) say the same.
- Schema: `requires[].kind` keeps the three kinds of 1.0.0 and `digest` is an `art_` with 64 hex digits. This is the same as the core schema of the kernels: rc.4 published four more kinds and a shorter digest that no kernel accepted.

**Editorial**
- `IANA.md` lists two applications, the reference kernel and the command-line host. Each keeps its pending marker until its version 2.0.0 or 5.0.0 is published.
- `GOVERNANCE.md` keeps the commitment to propose a neutral foundation, without a working name.
- `CONFORMANCE.md` cited the specification by a path one level above the root of this repository; it now cites `SPECIFICATION.md`.
- `companions/README.md` says which companion is normative for which claim of Section 11.
- The schema had a duplicated `description` in `guardrails.inherit`; the duplicate is removed and the effective text is unchanged.

**Tooling and tests**
- 21 new document vectors (133 in total). They cover:
  - later and other versions;
  - `requires[]`, including a flow whose first step must not run;
  - effective `sandbox`, including the chain and a later step;
  - `privileged` without a signature;
  - descriptive authorization declarations;
  - sealed folders: sealed, tampered, and sealed with the document hash.
- The runner of the reference kernels checks symbolic links, the root of the directory hash and the exclusion of the signature.
- `tools/traceability.py --strict` fails when a requirement of Sections 2.1, 2.2, 5.3, 6.5, 6.6, 9.1 to 9.3 or 12 has no vector; it runs in CI.
- A development check of the source repository (not part of this tree) finds relative paths that leave the repository.

### [2.0.0-rc.4] - 2026-10-20

No change to the schemas (`schema/` is byte-identical to rc.3) and no new requirement. The reference kernel attached to this candidate is `jos-core` 2.0.0-rc.5.

**Normative text**
- Section 9.1: the reference to the `.jos/` directory specification is no longer stated as normative; it is a pending decision (publish that specification as a normative companion, or make the reference informative). No requirement of Section 9 changes.

**Editorial (the text says what is true; no requirement changes)**
- `SPECIFICATION.md` header: release candidate, not published; date; JOSFOX LLC as change controller. No path of the development repository remains: the companion specifications cited by the text are in `companions/` (identifiers, Capability, ledger, context engine), the document-level vectors in `tck/documents/`, and specifications of later phases are named as drafts.
- Section 9.1: an informative note separates running a folder (the reference kernels run `D/.jos/manifest.jos` with `D` as working directory; delivered) from a crystallized directory (Section 9.4, later phase). `PROMISES.md` P33 says the same.
- Appendix B: it no longer says that every MUST has a vector; each candidate publishes the traceability of every requirement, including those without a vector (`tools/traceability.py`).
- `IANA.md`: applications corrected after measuring them on 2026-10-20. The reference kernel is not on the npm registry, the published `@josfox/jos` (4.1.0) reads only the earlier 0.0.7 draft, and the published editor extension validates an earlier YAML shape; the three entries carry pending markers until the versions that read this media type are public. "Applications 1 to 5" is now "1 to 3". This corrects the rc.3 note above, which listed the three as publicly available applications of this media type.
- `PROMISES.md`: every promise has a class (normative format guarantee, implemented and tested, partial, future phase, needs external services) and `tools/promises-proof.py` refuses a class that the evidence does not support.
- `versions/1.0.0/README.md` and `README.md`: the 1.0.0 examples are read unchanged and their runs exit with code 5 (rc.3 said the flow exits with 0; it references atoms that are not in the folder). The 1.0.0 documents are called the submission, not "registered", while the ticket is open.
- `RELEASE_PROCESS.md`, `GOVERNANCE.md`, `README.md`: review tags `jos-spec-vX.Y.Z-rc.N` in the review repository versus the public tag `vX.Y.Z`, created by a person; the assets of each prerelease.
- `CONFORMANCE.md` Section 9: measured on 2026-10-20 (3159 checks), with what the reference kernels do not do (no network sandbox for `shell` steps; how a later minor version is read).
- Three schema vectors that were copies of internal manifests are replaced by neutral English documents with the same structure; the vector of an object that is not a document is named `invalid-not-a-jos-document`.

**Tooling and tests**
- Reference implementations pinned by hash: `tck/reference-implementations.lock.json` (JavaScript kernel, Python kernel, command-line host); every prerelease attaches them, and the job `reference-implementations` downloads them, checks the sha256, installs them offline and runs the document level of the TCK with `--expect-version` (`tools/verify-reference-implementations.py`).
- `tck/run-documents.py`: `--expect-version`; vectors that run a folder (`run_document`, `"validate": null`); errors judged by their JSON Pointer, with `--strict-messages` for the reference kernels.
- New document vectors: `dir-run-folder`, `dir-run-folder-cwd`, `dir-run-no-manifest`, `invalid-not-utf8`, `legacy-0.0.7-object-step` (112 in total).
- CI: the aggregated check of invalid vectors is removed (it passed when a single one failed); a self-test injects a valid document as an invalid vector and requires the TCK to fail; the repository gate is mandatory; the traceability report is in the summary of every run.
- `tools/traceability.py`: every requirement of the text, the schema members it names, the vectors that cite its section and their results.
- Reference kernel `jos-core` 2.0.0-rc.5: a signal to the kernel (SIGTERM, SIGINT, SIGHUP) now kills the running step, in both engines.

### [2.0.0-rc.3] - 2026-10-19
- The normative text is `SPECIFICATION.md` (the version is in the tag, not in the file name).
- Both versions in the repository: `versions/1.0.0/` (text, examples, and the registration fields as submitted next to the ones of this package) and `schema/1.0.0/`.
- Document-level Test Compatibility Kit: `tck/run-documents.py` and `tck/documents/` run the 107 conformance documents of the reference kernels against any implementation; each vector names the promises it proves. `tck/PROOF.md` and the README table are generated from it: 23 of 48 promises delivered in 2.0, 6 partly, the rest specified for later phases.
- A folder is a `.jos` when it is run: `run D` uses `D/.jos/manifest.jos` (Section 9.1, promises P9 and P15), in both reference kernels and in `@josfox/jos`.
- `IANA.md` lists only applications that are publicly available: `@josfox/jos-core`, `@josfox/jos` and the editor extension `JOSFOX.josfox-jos`.
- Only `application/vnd.jos+json` is named anywhere in this repository.
- Profile `exec-contract/1`: member `jos_native` (was a product name), value `gateway`, member `generator_version`, descriptions in English.

### [2.0.0-rc.2] - 2026-10-19
- The prose and the schemas agree at every depth: signature members, 0.0.7 object-form steps (exit code 2 until 2.1), `limit.context_tokens`, `integrity.timestamp`, the members of `crystal`.
- Every invalid vector fails for a single cause; the vector index is in English.
- `CONFORMANCE.md` Section 9: conformance measured on the two reference kernels.
- The conformance workflow passes on release candidates and fails on a final tag that still carries pending markers.

### [2.0.0-rc.1] - 2026-10-19
- First candidate of the registration package. Superseded by rc.2: a validation found four mismatches between the prose and the schema that its checks did not measure.

## [1.0.0] - 2026-06

- Introduced the JOS 1.0.0 document model.
- Added `jos.version` and `jos.kind`.
- Added atom, flow, service and persona kinds.
- Added intention, guardrails, dependencies, execution budgets, orchestration, model policy, UI metadata, metrics, billing metadata, security metadata, lifecycle metadata, integrity metadata and reproducibility metadata.

## 1.0.0 registration material (branch `hardening/iana-v1-spec`, not a release)

- Media type aligned to `application/vnd.jos+json`.
- Media-type version consistency rules.
- `.jos` as primary extension, `.jos.json` as alternative.
- Normative RFC 8785 canonicalization for `integrity.hash`.
- Declarations never grant authorization; A2A and MCP integration boundaries; JSON Pointer fragment identifiers.
- `SPECIFICATION.md`, `IANA.md`, `SECURITY.md`, `CONFORMANCE.md`, `GOVERNANCE.md`, `CONTRIBUTING.md`.

## Historical drafts

Earlier drafts used pre-1.0 structures such as `id_jos` and `orchestration_contract`. Those drafts are not JOS 1.0.0 and SHOULD NOT be used as the definition of the current format. Version 2.0.0 reads them through normalization (SPEC Section 2.4) and does not define them.
