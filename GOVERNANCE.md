# Governance

The JOS specification is maintained as a public specification. The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in capitals.

## Scope

This repository defines the JOS document format: the normative specification, the JSON Schemas, the security requirements, the conformance requirements and test vectors, and the registration material for `application/vnd.jos+json`.

Runtime implementations, SDKs, hosted services and vendor-specific integrations SHOULD be maintained in separate repositories. They implement the format and do not define it.

## Change controller

The change controller of the JOS specification and of the media type `application/vnd.jos+json` is JOSFOX LLC. Contact: jos@josfox.cloud.

A change to the registered media type (name, parameters, encoding, security considerations, fragment identifier syntax) is requested from IANA by the change controller under RFC 6838 Section 5.5.

Governance model (decided 2026-10-15): JOSFOX LLC is the change controller and the sole maintainer of the registration while the format has fewer than two independent conforming implementations beyond the reference kernels. Changes to the normative text follow the public process of this file (issue, proposal, vectors, two reviews, tag). When two independent implementations claim conformance against `CONFORMANCE.md`, the change controller commits to propose the transfer of change control to a neutral foundation with the same process and the covenant of `LICENSE-SPEC.md` carried over; until then the covenant binds JOSFOX LLC.

## Versions and tags

- Specification versions use semantic versioning: `MAJOR.MINOR.PATCH`.
- Each released version is an immutable git tag `vMAJOR.MINOR.PATCH` in `https://github.com/josfox-jos/jos-spec`. A tag MUST NOT be moved or deleted after publication.
- A release candidate is a tag `jos-spec-vMAJOR.MINOR.PATCH-rc.N` in the review repository; it is never cited as published, and it is never moved or deleted either (`RELEASE_PROCESS.md`, Tags).
- Registration material, the `$id` of each JSON Schema, and every link in a released document MUST refer to a tag, not to a branch.
- The version of the specification and the version of an implementation package are independent and MUST NOT be forced to match.

Current versions: 1.0.0 (tag `v1.0.0`, in force) and 2.0.0 (tag `v2.0.0`). Version 2.0.0 is an additive superset of 1.0.0.

## Change classes

| Class | Examples | Version change |
|---|---|---|
| Editorial | typo fixes; wording that does not alter a requirement; link fixes | none |
| Patch | non-breaking clarification of normative text; test vectors that do not change which documents are accepted | PATCH |
| Minor | new optional members; new optional kinds; backward-compatible schema additions; new optional profiles | MINOR |
| Major | new required members; removed members; incompatible change of meaning; validation that rejects previously valid documents without a migration path | MAJOR |

A MINOR or PATCH change MUST keep every document that is valid under the previous MINOR version of the same MAJOR version valid. `tools/check-superset.py` MUST exit with code 0 on the proposed schema before the change is merged.

## Process

1. A change is proposed as an issue or pull request that contains the items listed in `CONTRIBUTING.md`.
2. The change controller or a maintainer designated by it reviews the change. A change to normative text, to a schema, or to `SECURITY.md` requires a recorded review of its security impact.
3. A change that alters a normative requirement is merged only with: updated schema, updated vectors (valid and invalid), updated `CHANGELOG.md`, and an updated compatibility statement.
4. A release is a tag. Before tagging, the checks in `CONFORMANCE.md` Section 7 pass without network access, and the URLs of the release are verified by a person (`tools/url-check.py --human`).

## Core and extensions

The core format has no generic extension namespace other than keys that start with `x-` and optional, versioned profiles (`name/MAJOR`, SPEC-2.0 Section 10). A profile MUST NOT add a required core member and MUST NOT change core semantics. A new cross-implementation semantic is standardized by a specification revision or by a documented profile, not by implementations that add unknown members.

## Principles for changes

A change SHOULD:

- preserve portability, and not bind the core format to one model vendor, runtime, cloud or transport;
- keep authorization outside the document (`SECURITY.md` Section 3);
- define behavior that a program can verify;
- include security analysis, schema updates and vectors;
- state affected versions, whether existing documents remain valid, migration, and runtime impact.

The normative text does not contain trademarks or product names, other than the name of the change controller.

## Licenses and patents

- The specification text is licensed under CC BY 4.0 and the JSON Schema, test vectors, examples, tools and reference kernels under the Apache License 2.0 (`LICENSE`, `LICENSE-SPEC.md`), with a royalty-free patent non-assertion covenant on the format (decided 2026-10-15).
- Patents: no known patent claims on the format. The change controller's non-assertion covenant is in `LICENSE-SPEC.md` (decided 2026-10-15).
- A contribution is licensed under the license of the repository (see `CONTRIBUTING.md`).
