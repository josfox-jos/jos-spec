# Versioning

How the `.jos` specification and the media type `application/vnd.jos+json` are versioned, and what breaks compatibility.

## Versions of the specification

- The specification uses semantic versions: `MAJOR.MINOR.PATCH`. The `version` media type parameter carries the full version of the document's format (`application/vnd.jos+json; version=2.0.0`); inside the document, `jos.version` is authoritative and there is no implicit default (IANA.md, Optional parameters).
- Every published version is an immutable git tag (`v1.0.0`, `v2.0.0`) and an immutable folder in this repository: `schema/<version>/` holds the schemas exactly as published for that version; `registered/` holds what was registered with IANA. Files under those folders never change after the tag; corrections go to the next version.
- **PATCH**: editorial corrections and new test vectors; no change to what validates.
- **MINOR**: additive changes only: new optional members, new engine classes, new profiles. Every document valid under `X.Y` MUST be valid under `X.(Y+1)` (`tools/check-superset.py` is run against the previous version's vectors on every pull request). A minor version never adds an obligation that a reader of an earlier minor version could ignore: a new member, value or kind makes a document invalid for such a reader (closed core), and a new obligation is expressed as a `requires[]` entry of an existing kind (SPEC-2.0 Section 6.6).
- **MAJOR**: anything that makes a previously valid document invalid, changes the meaning of an existing member, or changes the canonical form (`art_`, RFC 8785). A major version is announced in `CHANGELOG.md` with a migration note and keeps the previous major in force at its tag for at least twelve months.

## Compatibility promises

- 2.0.0 is an additive superset of 1.0.0: every valid 1.0.0 document is a valid 2.0.0 document (CONFORMANCE.md, Section 1). The one qualification is numeric: a number literal that Section 2.1 of the specification makes invalid (an integer value with magnitude above 2^53 and below 10^21, or a decimal that is not the shortest round-trip form of its binary64 value) is invalid whatever version the document declares; 1.0.0 gave such literals no reproducible canonical form, so no hash of such a document was ever stable.
- Reading older input (1.1.0 short form, 0.0.7 legacy with string steps) is normalization, not a change of version: the normalized document is a 2.0.0 document and its `art_` is computed on the normalized form (SPECIFICATION.md §2.4).
- Profiles (`jos.profiles`) are versioned by major only (`exec-contract/1`); a profile never removes or changes a core member.

## What is not a compatibility change

Receipts, ledgers and `art_` values of a run belong to the kernel that produced them and are versioned by the kernel (`jos-core` CHANGELOG), not by this specification; the specification only fixes the canonical form they hash.

## Process

See `RELEASE_PROCESS.md` for the checklist that cuts a version (superset check, vectors, conformance of both reference kernels, repository gate, tag).
