# Conformance

This document defines conformance requirements for JOS 1.0.0.

## 1. Document conformance

A JOS document is conforming when it:

1. is valid UTF-8 JSON text;
2. has a top-level JSON object;
3. contains the required `jos` and `meta` objects;
4. validates against the JOS 1.0.0 JSON Schema;
5. satisfies the additional semantic requirements in `SPECIFICATION.md`;
6. does not rely on undefined extension behavior.

Schema validation is necessary but not sufficient for full semantic conformance.

## 2. Parser conformance

A conforming parser:

- MUST parse according to RFC 8259;
- MUST reject duplicate object member names for JOS conformance processing;
- MUST reject invalid UTF-8;
- MUST expose the parsed top-level object without silently rewriting member names;
- MUST NOT execute content while parsing.

## 3. Runtime conformance

A conforming runtime:

- MUST validate JOS documents before interpretation;
- MUST declare the JOS versions it supports;
- MUST fail closed on unsupported major versions;
- MUST apply independent authorization and sandbox policy;
- MUST NOT treat document-declared permissions as granted permissions;
- MUST enforce resource budgets at or below runtime policy;
- MUST honor stricter runtime policy over document policy;
- MUST treat external references as untrusted;
- SHOULD preserve provenance for natural-language fields supplied to models;
- SHOULD expose validation and execution failures in a machine-readable way.

## 4. Kind conformance

A runtime MAY support a subset of JOS kinds.

If a runtime does not support a document's `jos.kind`, it MUST reject or decline execution rather than reinterpret the document as another kind.

## 5. Media type conformance

When `application/vnd.jos+json; version=...` is used, the parameter value MUST equal `jos.version`.

Receivers MUST treat mismatches as errors.

## 6. Integrity conformance

A runtime claiming support for `integrity.hash` MUST implement the hashing procedure defined in `SPECIFICATION.md`, including RFC 8785 canonicalization.

Implementations MUST NOT treat `signed_by` as proof of identity in JOS 1.0.0.

## 7. Test vectors

The `examples/` and `tests/` directories are intended to contain:

- valid minimal documents;
- valid documents for each kind;
- invalid syntax cases;
- invalid structural cases;
- invalid semantic cases;
- integrity hash vectors;
- media-type version mismatch vectors.

A future conformance suite SHOULD make these vectors executable in CI.
