# JOS Quality Gates

## Phase 1 — repository design gate

The repository-quality guard evaluates every public JOS repository against the JOS Public Repository Standard.

### Blocking failures

The following are release-blocking:

1. canonical spec URL is missing or contradictory;
2. supported JOS spec version is missing;
3. required license or security policy is missing;
4. current README version disagrees with schema/package/release metadata;
5. examples do not parse;
6. checked-in `.jos` examples fail the declared canonical schema;
7. public docs point to a private or missing canonical dependency;
8. integration repo does not identify upstream protocol/version;
9. a package or extension has no public canonical source link when presented as open source;
10. release artifact version does not match its source tag;
11. normative spec and schema disagree on required fields or enums;
12. public docs contain secrets or credentials.

### Warning failures

Warnings include:
- missing CODE_OF_CONDUCT;
- missing ADR/proposal process;
- no link checker;
- no dependency update automation;
- missing SBOM/provenance;
- stale examples;
- unpinned external dependencies;
- mutable `main` schema URLs used by released artifacts.

## Phase 2 — distribution gate

### npm packages

For every published package:

- `package.json.version` MUST equal the release tag/package version;
- `repository` metadata MUST resolve to the canonical public source;
- `license` MUST match the repository license;
- package tarball MUST contain no secrets or internal-only files;
- package MUST declare supported JOS spec range separately from package version;
- changelog entry MUST exist;
- CI test suite MUST pass before publish;
- conformance fixtures MUST pass;
- publish SHOULD use npm trusted publishing/provenance when available;
- release SHOULD attach an SBOM or equivalent dependency inventory.

Package version and JOS specification version are separate namespaces and MUST NOT be forced to match.

### VS Code extension

The extension release gate MUST verify:

- Marketplace version equals source tag and extension manifest version;
- Marketplace repository/homepage links resolve;
- `.jos` and `.jos.json` are associated with JSON/JOS language support;
- bundled schemas are canonical and versioned;
- validation works offline;
- current JOS 1.x examples validate;
- legacy pre-1.0 documents are either migrated or explicitly recognized as legacy;
- syntax highlighting covers current top-level keys;
- diagnostics include duplicate-key/version/schema mismatch cases where feasible;
- extension docs do not describe JOS 1.x as YAML;
- CLI integration targets a currently published and tested CLI;
- extension compatibility matrix names supported JOS versions.

## Ecosystem consistency gate

A nightly or release-time ecosystem audit SHOULD compare:

- normative spec version;
- schema version and hash;
- reference corpus version;
- SDK supported version ranges;
- npm package versions;
- VS Code extension version;
- public documentation links;
- GitHub release/tag state.

The audit output SHOULD be a single machine-readable report plus a human summary.

## Gate result

- PASS — no blocking failures.
- PASS_WITH_WARNINGS — no blockers, warnings remain.
- FAIL — one or more blocking failures.

No automated gate should assign marketing claims. It verifies evidence for claims made elsewhere.
