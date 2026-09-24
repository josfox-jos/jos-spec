# Changelog

All notable changes to the JOS Object Specification are documented here.

## [Unreleased]

### Changed
- Media type aligned to `application/vnd.jos+json`.
- Added explicit media-type version consistency rules.
- Defined `.jos` as the primary extension and `.jos.json` as an alternative.
- Added normative RFC 8785 canonicalization for `integrity.hash`.
- Clarified that JOS declarations never grant authorization.
- Clarified A2A and MCP integration boundaries.
- Defined JSON Pointer fragment identifier semantics.

### Added
- Normative `SPECIFICATION.md`.
- `IANA.md`.
- `SECURITY.md`.
- `CONFORMANCE.md`.
- `GOVERNANCE.md`.
- `CONTRIBUTING.md`.

## [1.0.0] - 2026-06

- Introduced JOS 1.0.0 document model.
- Added `jos.version` and `jos.kind`.
- Added atom, flow, service, and persona kinds.
- Added intention, guardrails, dependencies, execution budgets, orchestration, model policy, UI metadata, metrics, billing metadata, security metadata, lifecycle metadata, integrity metadata, and reproducibility metadata.

## Historical drafts

Earlier internal and public drafts used pre-1.0 structures such as `id_jos` and `orchestration_contract`. Those drafts are not JOS 1.0.0 and SHOULD NOT be used as the authoritative definition of the current format.
