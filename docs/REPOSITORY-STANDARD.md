# JOS Public Repository Standard

Status: Design baseline for JOS public repositories.

This standard is inspired by mature public specification and implementation repositories including A2A, MCP, OpenAPI, Open Workflow Specification, and major SDK repositories.

## Repository classes

Every public JOS repository MUST declare exactly one primary class in its README:

- **SPEC** — normative specification and schemas
- **REFERENCE** — reference implementation, examples, profiles, or corpus
- **SDK** — reusable runtime/library implementation
- **INTEGRATION** — bridge/profile for another protocol such as A2A or MCP
- **TOOL** — CLI, editor extension, build tool, validator, or generator
- **SAMPLE** — demonstration only; not production or normative

## Universal gate — all public JOS repositories

A repository MUST have:

- `README.md`
- `LICENSE`
- `SECURITY.md`
- `CONTRIBUTING.md` or an explicit statement that external contributions are not accepted
- `CHANGELOG.md` or release notes linked from README
- maintainership ownership (`MAINTAINERS.md`, `CODEOWNERS`, or equivalent)
- CI under `.github/workflows/`
- a declared repository class
- current status: experimental, draft, release candidate, stable, deprecated, or archived
- explicit relationship to the canonical JOS specification
- explicit supported JOS specification version/range
- no broken canonical links
- no contradictory current version claims
- no credentials, private endpoints, or secrets in public examples

A repository SHOULD have:
- `CODE_OF_CONDUCT.md`
- issue/PR templates;
- dependency update automation;
- linting/format rules;
- reproducible local test commands;
- signed or provenance-backed releases where the ecosystem supports them.

## SPEC class

A SPEC repository MUST additionally contain:

- normative specification document;
- BCP 14 requirement language policy;
- versioned schema directory;
- immutable released schemas;
- schema source-of-truth declaration;
- valid examples;
- invalid examples;
- conformance or compatibility test kit;
- security considerations;
- media type/IANA material when applicable;
- governance and change-control process;
- proposal/ADR mechanism for substantial changes;
- migration documentation;
- version history;
- machine-readable release manifest;
- automated schema validation;
- automated example validation;
- automated link validation;
- drift checks between normative text and schema;
- release tags matching specification releases.

The SPEC repository SHOULD expose a stable canonical schema URI independent of a mutable `main` branch.

## REFERENCE class

A REFERENCE repository MUST contain:

- a link to the normative spec;
- a compatibility matrix;
- runnable examples;
- at least one minimal and one realistic enterprise example;
- explicit non-normative status;
- automated validation of every checked-in `.jos` artifact;
- migration examples for supported JOS versions.

## SDK class

An SDK repository MUST contain:

- install instructions;
- quickstart;
- API/reference docs;
- tests;
- exact supported JOS spec range;
- conformance suite execution;
- release automation;
- package registry metadata pointing back to the canonical source repository;
- source tag corresponding to every published package;
- security policy;
- dependency lockfile where appropriate.

An SDK SHOULD publish an SBOM and provenance attestation for releases.

## INTEGRATION class

An INTEGRATION repository MUST contain:

- exact upstream protocol name/version;
- exact JOS spec version/range;
- mapping document;
- runnable end-to-end example;
- compatibility matrix;
- upstream attribution/license compliance;
- integration conformance tests;
- clear statement of which protocol owns transport, auth, lifecycle, and execution-contract semantics.

For A2A specifically, JOS SHOULD be described as a structured execution-contract payload/profile carried using A2A mechanisms, not as a replacement for A2A.

## TOOL class

A TOOL repository MUST contain:

- install/update/uninstall instructions;
- versioned releases;
- supported JOS spec range;
- fixture-based tests using canonical valid and invalid documents;
- offline-safe baseline behavior where practical;
- no hidden dependency on mutable schemas from `main`.

For editor tools, diagnostics MUST reflect current JOS syntax. JOS 1.x is JSON; editor documentation and validators MUST NOT describe the current format as YAML unless explicitly supporting a separate conversion/view mode.

## SAMPLE class

A SAMPLE repository MUST:
- identify itself as non-normative;
- pin versions of the spec/runtime it demonstrates;
- include one-command setup or explicit prerequisites;
- avoid production/security claims not demonstrated by the sample.

## Release quality levels

- **G0 / discoverable** — README, license, status, canonical links.
- **G1 / reviewable** — security, contribution model, versioning, examples, CI.
- **G2 / interoperable** — schemas, conformance, compatibility matrix, deterministic releases.
- **G3 / ecosystem-grade** — automated provenance, SBOM, release attestations, downstream compatibility tests, stable docs/schema URLs.

No JOS repository SHOULD be labeled stable until it passes G2 for its class.
