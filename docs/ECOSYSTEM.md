# JOS Ecosystem Repository Model

This document defines the public repository roles for the JOS ecosystem.

## One source of normative truth

The canonical normative specification is:

- `josfox-jos/jos-spec`

This repository owns:
- normative JOS language and semantics;
- media type registration material;
- versioned JSON Schemas;
- conformance requirements and test vectors;
- security considerations;
- governance and change control;
- migration notes between specification versions.

No implementation repository may redefine JOS semantics.

## Reference and implementation corpus

`josfox-ai/jos-format-spec` remains public, but its role is implementation-facing rather than normative.

It SHOULD contain:
- JOSFOX AI reference implementations;
- enterprise examples;
- downloadable `.jos` artifacts;
- migration examples;
- profile demonstrations;
- implementation notes;
- compatibility matrices;
- real-world use cases.

Its README MUST identify `josfox-jos/jos-spec` as the normative source of truth.

Historical pre-1.0 specification material SHOULD be retained under a clearly marked `legacy/` tree rather than presented as the current standard.

## Protocol integrations

Integration repositories such as A2A or MCP bridges MUST clearly state:
- the upstream protocol and exact supported version;
- the JOS specification version or range supported;
- that JOS does not replace the upstream protocol;
- the mapping between JOS constructs and upstream constructs;
- conformance tests and runnable examples;
- provenance and attribution when upstream code is reused.

A public repository that is substantially an upstream copy MUST either contain a clearly documented JOS-specific delta or be marked as a fork/mirror. Ambiguous copies are not acceptable as canonical JOS implementations.

## Runtime and package repositories

Runtime, SDK, CLI, and package repositories implement JOS but do not define it.

Every released package MUST publish:
- its own implementation version;
- a separate JOS specification compatibility range;
- a source repository URL;
- an immutable source tag corresponding to the published package;
- release notes;
- test/conformance status.

Implementation versions do NOT need to equal the JOS specification version.

Example:

```
@josfox/jos 4.1.0
supports JOS spec >=1.0.0 <2.0.0
```

## Editor integrations

Editor plugins MUST consume the canonical JOS schema and MUST identify the exact JOS versions they support.

They SHOULD work offline using a bundled canonical schema and MAY refresh newer schemas from the canonical repository.

## jos-foundation organization

Until a formal governance transfer occurs, the `jos-foundation` organization is not a normative authority for JOS.

It may be reserved for future independent governance, but introducing a third source of truth before such a transfer would create ambiguity.

## Authority rule

When documents disagree, precedence is:

1. released version of `josfox-jos/jos-spec`;
2. versioned canonical JSON Schema for that release;
3. normative conformance/security documents in the same release;
4. implementation documentation;
5. examples, tutorials, search-engine summaries, and third-party descriptions.

Search results are evidence of public discoverability, not specification authority.
