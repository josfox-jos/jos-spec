# IANA Media Type Registration: application/vnd.jos+json

**Status:** draft submission package for `.jos` 2.0.0. **Template:** RFC 6838 Section 5.6. **Ticket:** IANA #1460136.

This is the only registration text for this media type. The specification, the JSON Schema, `SECURITY.md`, `README.md`, the examples and any correspondence with IANA use the same subtype, `vnd.jos+json`. The name decision is recorded in `DECISION-NOMBRE.md` of the specification workspace (`.jos/docs/`).

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in capitals.

## Registration template

**Type name:** application

**Subtype name:** vnd.jos+json

**Required parameters:** N/A

**Optional parameters:** `version`

The `version` parameter identifies the version of the JOS specification that the document conforms to.

- Syntax: `version = 1*DIGIT "." 1*DIGIT "." 1*DIGIT` (`MAJOR.MINOR.PATCH`). Pre-release and build suffixes are not permitted. The value is the same string that the schema pattern `^\d+\.\d+\.\d+$` accepts for `jos.version`.
- Absent parameter: there is no implicit default. The top-level `jos.version` member of the document is authoritative.
- Present parameter: the value MUST equal the document's top-level `jos.version`.
- Conflict rule: if the parameter is present and differs from `jos.version`, the receiver MUST treat the representation as an error and MUST NOT process it. The receiver MUST NOT choose one of the two values.
- A parameter name is case-insensitive and MUST NOT appear more than once (RFC 6838 Section 4.3).

Examples:

```
Content-Type: application/vnd.jos+json
Content-Type: application/vnd.jos+json; version=2.0.0
```

**Encoding considerations:** binary

A JOS document is a JSON text (RFC 8259) encoded in UTF-8 without a byte order mark. A JOS document is not line-oriented, and a serialized document can exceed 998 octets on one line. The value `binary` is the value that RFC 8259 Section 11 gives for `application/json`. The value `8bit` is not used: it describes CRLF-delimited 8bit text (RFC 6838 Section 4.8), and a JOS document is neither required nor expected to be CRLF-delimited. RFC 6839 Section 3.1 describes JSON in UTF-8 as 8bit-compatible; `binary` is the more general value and is the one RFC 8259 Section 11 registers. The `integrity.hash` value is computed over the RFC 8785 canonical representation of the JSON data (Section 8.1 of the specification), not over the original serialized octets. Transport transformations must not alter the JSON data or its interpretation. When independent raw-octet integrity protection is used, byte-for-byte preservation is required by that protection mechanism.

**Security considerations:** See `SECURITY.md` in this package, https://github.com/josfox-jos/jos-spec/blob/v2.0.0/SECURITY.md, and the Security considerations of the specification. JOS inherits the JSON security considerations of RFC 8259 Section 12. In summary, as required by RFC 6838 Section 4.6:

- A JOS document is declarative. It contains members that name commands, programs, HTTP endpoints, other documents, tools and services (`orchestration.definitions` entries with `type` `shell`, `execution.run`, `execution.flow[].invoke`, `execution.engine`). A conforming parser MUST NOT evaluate or execute any of them. A runtime that acts on them is active content: it MUST apply its own authorization and budget before acting, MUST confine the processes it starts or refuse to run when a document asks for isolation (`security.tier: sandbox`), and MUST NOT run a document whose `requires[]` it cannot satisfy.
- A document cannot grant itself privileges. Declared permissions are requests, not grants.
- Natural-language members can carry prompt injection. `integrity.hash` detects change and does not authenticate a publisher. `billing` values are untrusted input. URIs in a document are untrusted and can be used for server-side request forgery.
- JOS does not employ compression. JOS requires external confidentiality and integrity protection (TLS) when documents cross an untrusted network.

**Interoperability considerations:** A JOS document is a JSON object (RFC 8259) and uses the `+json` structured syntax suffix registered by RFC 6839 Section 3.1. A generic JSON processor can parse it. A JOS-aware implementation is required for JOS semantics. A `.jos` document can be carried as structured data in an agent-to-agent message, with this media type as the content type of the part.

- The top-level value MUST be an object. Member names are case-sensitive.
- Duplicate member names MUST be rejected by conformance processing (RFC 8259 Section 4 says names SHOULD be unique and leaves the behavior of parsers that accept duplicates unspecified; JOS removes that ambiguity).
- Version 2.0.0 is an additive superset of 1.0.0. Every valid 1.0.0 document is a valid 2.0.0 document (`tools/check-superset.py`, exit code 0). The one qualification is numeric: a number literal that Section 2.1 of the specification makes invalid (an integer value with magnitude above 2^53 and below 10^21, or a decimal that is not the shortest round-trip form of its binary64 value) is invalid whatever version the document declares; 1.0.0 gave such literals no reproducible canonical form, so no hash of such a document was ever stable. A 2.0.0 reader reads 1.1.0 short-form input and 0.0.7 legacy input whose flow steps are strings through the normalization defined in the specification; 0.0.7 documents with object-form steps are rejected with the specification's exit code 2 (their normalization is scheduled for 2.1).
- A 2.0.0 receiver reads a document of a later 2.y version by validating it against the 2.0.0 schema (a member it does not know makes the document invalid) and does not execute what it cannot satisfy (`requires[]`). A document of another major version is invalid.
- Language tags in documents SHOULD be BCP 47 tags with a hyphen (`en-US`, not `en_US`); the schema does not enforce the syntax.
- Valid and invalid test vectors are published in `tests/` and run without network access.

**Published specification:**

- Repository: `https://github.com/josfox-jos/jos-spec`
- Version 2.0.0 (normative for this registration): tag `v2.0.0`
- Version 1.0.0: tag `v1.0.0`
- JSON Schema: `schema/jos.schema.json` at tag `v2.0.0`. The schema `$id` is a URL that contains the tag, not `main`.
- The registration cites tags only. It does not cite `main`, because the content of a branch can change after registration (for the vendor tree RFC 6838 Section 4.4 encourages a public specification without requiring one; this registration references one, and a mutable reference would not identify one version).

**Applications that use this media type:** The list is not exhaustive. An entry is listed only when the version that reads this media type is publicly available.

1. `@josfox/jos-core`, the reference kernel (JavaScript, with a Python kernel `jos-core` that computes the same `art_` and gives the same results on every conformance vector): it normalizes, validates, hashes and executes `.jos` documents and passes the conformance vectors of this specification (`CONFORMANCE.md` Section 9). Published on npm: https://www.npmjs.com/package/@josfox/jos-core
2. `@josfox/jos`, a command-line runtime: from version 5.0.0 it reads `.jos` files (versions 2.0.0, 1.1.0 short form, 1.0.0 and 0.0.7 with string steps) and runs them through the reference kernel. Published on npm: https://www.npmjs.com/package/@josfox/jos

**Fragment identifier considerations:** The fragment identifier syntax for `application/vnd.jos+json` is JSON Pointer (RFC 6901). The URI fragment representation is the one defined in RFC 6901 Section 6 (UTF-8, percent-encoded). RFC 6839 Section 3.1 does not define a fragment identifier syntax for `+json`; RFC 6901 Section 6 states that a media type has to specify JSON Pointer explicitly, and this registration does so. RFC 6839 Section 3.1 states that, for cases not defined in `+json`, a fragment identifier is processed as specified for the specific `xxx/yyy+json` type. The JSON Pointer syntax is that specification for this type.

Example:

```
https://example.com/contracts/demo.jos#/meta/name
https://example.com/contracts/demo.jos#/intention/success_criteria/0
https://example.com/contracts/demo.jos#/orchestration/definitions/a~1b
```

The first fragment identifies the value of `meta.name`. The second identifies the first element of `intention.success_criteria`. In the third, `~1` encodes `/` inside the member name `a/b` (RFC 6901 Section 3). A fragment that does not resolve is an error of the application that evaluates it.

**Additional information:**

- Deprecated alias names for this type: N/A
- Magic number(s): N/A
- File extension(s): `.jos` (primary), `.jos.json` (alternative)
- Macintosh file type code(s): N/A
- Extension note: other software uses the extension `.jos` for unrelated formats (for example, JOSM, the Java OpenStreetMap editor, uses `.jos` for session files). The extension is not part of the media type identity. Receivers MUST select the processing from the media type, or from `jos.version` and `jos.kind` after parsing, and MUST NOT select it from the file extension alone. The alternative `.jos.json` is for environments in which generic JSON tooling selects a handler by a `.json` suffix. It does not define a different representation.

**Person & email address to contact for further information:** Josué Emmanuel Gómez Carrillo, JOSFOX LLC, jos@josfox.cloud

**Intended usage:** COMMON

The format is intended for exchange between independent implementations, and applications 1 and 2 above are separate programs or classes of programs that read or write it. No restriction on use is requested (RFC 6838 Section 4.9).

**Restrictions on usage:** N/A

**Author:** Josué Emmanuel Gómez Carrillo, JOSFOX LLC

**Change controller:** JOSFOX LLC

**Provisional registration? (standards tree only):** N/A (vendor tree)

## Registration notes

### Name and tree

The subtype is `vnd.jos+json`. It is in the vendor tree (RFC 6838 Section 3.2). The leading facet `vnd.` is present. The name conforms to the ABNF of RFC 6838 Section 4.2. The `+json` suffix is registered (RFC 6839 Section 3.1) and the representation is JSON, as RFC 6838 Section 4.2.8 requires. The subtype does not appear in the IANA registry of application media types (snapshot `iana-media-types-application.csv`, 1813 lines, no entry `vnd.jos+json`).

The registration request is for `application/vnd.jos+json` only.

### Versions

Version 1.0.0 remains in force. Version 2.0.0 is additive: it adds optional members and kinds, adds no required member at the root (`jos` and `meta` remain the only required root members), and removes nothing. A 1.0.0 document is a valid 2.0.0 document, with one exception: a number literal that Section 2.1 of the specification makes invalid (an integer value of magnitude above 2^53 and below 10^21, such as `1e20`, or a decimal that is not the shortest round-trip form of its binary64 value) is invalid whatever version the document declares. A single media type covers both versions. The `version` parameter, or `jos.version`, identifies the version of a document. Where the text of tag `v1.0.0` and the text of tag `v2.0.0` differ on the spelling of the subtype, tag `v2.0.0` governs. 2.0.0 gives runtime meaning to `requires[]` and to `security.tier: sandbox`; a 1.0.0 document that declares them stays valid and can be unexecutable in a runtime that cannot satisfy them.

### Specification license and patents

- The specification text is published under CC BY 4.0; the JSON Schema, conformance vectors and reference kernels under the Apache License 2.0. The change controller grants a royalty-free non-assertion covenant covering the implementation of this format (reading, writing, validating, hashing and executing conforming documents). Techniques used by particular engines or services that process documents are outside the scope of this registration.
- Copyright of this template: the text of this registration template MAY be copied by IANA into the media types registry (RFC 6838 Section 4.10).

### References

Normative: RFC 2119; RFC 8174; RFC 8259 (Sections 4, 8.1, 11, 12); RFC 6901 (Sections 3, 6); RFC 8785; RFC 6838 (Sections 3.2, 4.2, 4.2.8, 4.3, 4.6, 4.8, 4.10, 4.11, 4.12, 5.6); RFC 6839 (Section 3.1).

Informative: RFC 7493 (I-JSON, input assumed by RFC 8785).
