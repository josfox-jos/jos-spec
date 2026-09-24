# Governance

JOS is maintained as an open specification.

## Scope

This repository defines the JOS document format, its normative specification, schemas, security requirements, conformance rules, examples, and registration material.

Runtime implementations, SDKs, hosted services, and vendor-specific integrations SHOULD live in separate repositories.

## Change control

The current change controller for JOS 1.0.0 is:

Josué Gómez — JOSFOX LLC

Substantive changes SHOULD be proposed through GitHub issues and pull requests.

## Change classes

### Editorial

Examples:

- typo fixes;
- wording clarifications that do not alter requirements;
- broken-link fixes.

Editorial changes MAY be merged without a specification version change.

### Patch

Examples:

- non-breaking clarification of normative text;
- correction of an ambiguity where intended behavior is already clear;
- test-vector additions that do not change accepted documents.

Patch changes increment PATCH.

### Minor

Examples:

- new optional fields;
- new optional artifact kinds;
- backward-compatible schema additions;
- new optional protocol profiles.

Minor changes increment MINOR.

### Major

Examples:

- changing required fields;
- removing fields;
- changing field meaning incompatibly;
- changing validation so previously conforming documents become invalid without an explicit migration path.

Major changes increment MAJOR.

## Design principles for proposed changes

Changes SHOULD:

- preserve portability;
- avoid binding the core format to one model vendor, runtime, cloud, or transport;
- keep authorization external to document content;
- define machine-verifiable semantics where practical;
- include security analysis;
- include schema updates and test vectors;
- explain compatibility impact.

## Extensions

JOS 1.0.0 intentionally has no generic extension namespace.

New cross-implementation semantics SHOULD be standardized through a specification revision or a separately documented profile rather than silently inventing unknown fields.

## Compatibility

A proposal that changes behavior SHOULD explicitly state:

- affected versions;
- whether existing documents remain valid;
- migration requirements;
- runtime compatibility impact;
- schema impact;
- security impact.
