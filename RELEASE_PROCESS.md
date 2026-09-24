# Release process

A JOS release is a tagged, immutable version of the normative specification, its JSON Schema, and its conformance material. Versions follow semantic versioning as defined in [GOVERNANCE.md](GOVERNANCE.md) (change classes decide MAJOR, MINOR, PATCH).

## What blocks a release (P0)

A release is not cut while any of these fails on the release branch:

1. `LICENSE`, `README.md`, `SPECIFICATION.md`, `schema/jos.schema.json`, `SECURITY.md`, `CONFORMANCE.md`, `GOVERNANCE.md`, `CHANGELOG.md`, `MAINTAINERS.md` present.
2. The golden rule: every root property of the JSON Schema is defined in `SPECIFICATION.md`, and every field the specification defines exists in the schema. A change that touches only one of them fails.
3. Every document under `examples/` validates; every vector under `conformance/vectors/invalid/` is rejected, for the reason recorded in `conformance/expected/`.
4. The media type `application/vnd.jos+json` and the `.jos` extension are the same in README, SPECIFICATION, IANA and CONFORMANCE.
5. No broken link in normative documents.
6. `CHANGELOG.md` has an entry for the version, referencing the pull requests or JEPs that produced it.
7. CI (`.github/workflows/`) is green on the release commit.

## Steps

1. Open a release pull request against `main` titled `release: JOS X.Y.Z`. It updates `CHANGELOG.md`, the version in `README.md` and `SPECIFICATION.md`, and freezes the version under `versions/X.Y.Z/` (specification, schema, examples) once that layout exists.
2. A maintainer other than the author reviews it (CODEOWNERS enforces this).
3. After merge, the release manager tags `vX.Y.Z` on `main` and publishes a GitHub release whose notes are the changelog entry.
4. The tag is immutable. A correction is a new PATCH version, never a moved tag.
5. Implementations record the version they conform to (`"jos": { "spec": ">=X.Y.0 <X+1.0.0" }` in their package metadata) and appear in `docs/ECOSYSTEM.md`.

## Draft versions

Work on the next MAJOR lives under `versions/draft/` and in accepted JEPs (`proposals/`). Drafts are not releases: nothing under `draft/` is stable, and IANA material only ever points at a released version.
