# IANA Media Type Registration Material

This document tracks the registration material for the JOS media type.

## Proposed registration

**Type name:** application

**Subtype name:** vnd.jos+json

**Required parameters:** None

**Optional parameters:** `version`

The `version` parameter identifies the JOS specification version represented by the document. Its value uses `MAJOR.MINOR.PATCH` syntax.

When present, the parameter MUST equal the document's top-level `jos.version` value. When absent, `jos.version` is authoritative. No implicit default is defined.

**Encoding considerations:** binary

JOS documents are UTF-8 encoded JSON text without BOM. JOS documents are not line-oriented and a serialized document may exceed 998 octets on a single line. The binary designation follows the registration of `application/json` in RFC 8259 and avoids transport assumptions that can alter the serialized representation.

**Security considerations:** See [SECURITY.md](SECURITY.md) and the Security Considerations section of [SPECIFICATION.md](SPECIFICATION.md). JOS also inherits the JSON security considerations in RFC 8259, Section 12.

**Interoperability considerations:** JOS documents are JSON objects conforming to RFC 8259 and use the `+json` structured syntax suffix. Generic JSON processors can parse JOS representations; JOS-aware implementations are required for JOS semantics.

**Published specification:** this repository, [SPECIFICATION.md](SPECIFICATION.md), with [schema/jos.schema.json](schema/jos.schema.json) as the machine-readable validation schema.

**Applications that use this media type:** AI execution runtimes, agent orchestration systems, workflow engines, task-contract systems, agent-to-agent integrations, marketplaces or registries of execution contracts, and applications that exchange declarative AI workflow definitions.

**Fragment identifier considerations:** JSON Pointer (RFC 6901) is the fragment identifier syntax for JOS. Example:

```
https://example.com/contracts/demo.jos#/meta/name
```

**Restrictions on usage:** None.

**Provisional registration:** No.

**Additional information:**

- Deprecated alias names: None
- Magic number(s): None
- File extension(s): `.jos`, `.jos.json`
- Primary file extension: `.jos`
- Macintosh file type code: None
- Object identifiers: None

**Person to contact for further information:** Josué Emmanuel Gómez Carrillo, JOSFOX LLC, jos@josfox.cloud

**Intended usage:** COMMON

**Author/Change controller:** Josué Gómez — JOSFOX LLC

## Registration notes

The media type is intentionally `application/vnd.jos+json`, not `application/vnd.josfox+json`.

The `.jos.json` extension is an alternative for environments where generic JSON tooling relies on a `.json` suffix. It does not define a different representation.
