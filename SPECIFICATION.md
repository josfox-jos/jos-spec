# JOS Object Specification 1.0.0

Status: Registration Candidate  
Media type: `application/vnd.jos+json`

## 1. Introduction

The JOS Object Specification defines a portable JSON document format for declarative AI execution contracts. A JOS document can describe an intended outcome, success criteria, guardrails, capabilities, dependencies, execution constraints, orchestration metadata, and runtime policy hints.

JOS defines a **document format**, not an execution engine, programming language, authorization mechanism, or transport protocol.

## 2. Conformance language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174) when, and only when, they appear in all capitals.

## 3. Representation

A JOS document:

- MUST be a JSON text conforming to RFC 8259.
- MUST be encoded as UTF-8.
- MUST NOT include a byte order mark when generated.
- MUST have a JSON object as its top-level value.
- MUST contain a top-level `jos` object.
- MUST contain a top-level `meta` object.
- MUST reject duplicate object member names during conformance validation.
- MUST treat member names as case-sensitive.

The registered media type is `application/vnd.jos+json`.

The primary file extension is `.jos`. The alternative extension `.jos.json` MAY be used where generic JSON tooling relies on filename extensions.

### 3.1 Media type version parameter

The optional `version` media type parameter identifies the JOS specification version carried by the representation.

If the parameter is present, its value MUST equal the top-level `jos.version` value. If the parameter is absent, `jos.version` is authoritative. No implicit media-type version default is defined.

Examples:

```
Content-Type: application/vnd.jos+json
Content-Type: application/vnd.jos+json; version=1.0.0
```

A receiver MUST treat a mismatch between the media type parameter and `jos.version` as an error.

## 4. Document header

The `jos` object identifies specification version and artifact kind.

```json
{
  "jos": {
    "version": "1.0.0",
    "kind": "atom",
    "schema": "https://example.org/jos/schema/1.0.0/jos.schema.json"
  }
}
```

### 4.1 `jos.version`

`jos.version` is REQUIRED and MUST be a semantic version in `MAJOR.MINOR.PATCH` form.

A runtime MUST NOT silently interpret a document using semantics from an incompatible major version.

### 4.2 `jos.kind`

`jos.kind` is REQUIRED. JOS 1.0.0 defines:

| Kind | Purpose |
|---|---|
| `atom` | A single logical unit of work |
| `flow` | A composition of multiple units of work |
| `service` | A long-running or endpoint-oriented service contract |
| `persona` | A declarative AI persona or behavioral contract |

### 4.3 `jos.schema`

`jos.schema` is OPTIONAL. When present it MUST be an absolute URI identifying a schema applicable to the document.

A schema URI is descriptive metadata and MUST NOT be treated as a trust anchor.

## 5. Metadata

The top-level `meta` object is REQUIRED and MUST contain `name`.

Optional metadata includes artifact version, author, license, description, domain, tags, and string labels.

Metadata MUST NOT grant privileges or alter authorization.

## 6. Artifact identifier

The top-level `id` member is OPTIONAL. When used, it SHOULD be stable for the logical artifact and SHOULD follow the reverse-DNS-style pattern defined by the JSON Schema.

Document identity and document content version are distinct concepts. Runtimes MUST NOT infer trust from an `id` value alone.

## 7. Intention and success criteria

The optional `intention` object describes the intended outcome.

- `objective` describes the goal.
- `success_criteria` describes one or more conditions used to evaluate completion.

Natural-language content in these fields is untrusted input. A runtime that supplies these fields to a language model SHOULD preserve provenance and apply prompt-injection defenses appropriate to its threat model.

## 8. Guardrails

The optional `guardrails` object describes execution constraints such as prohibited behaviors, required conditions, or per-call cost limits.

Guardrails are declarative requirements. A runtime MUST NOT assume a document is safe merely because it declares guardrails. Runtime-enforced policy takes precedence over document-declared policy.

## 9. Capabilities and dependencies

The optional `capabilities` array describes capabilities the artifact provides.

The optional `requires` array describes dependencies expected from the environment, including JOS artifacts, services, or MCP servers.

A dependency declaration MUST NOT cause automatic installation, network access, credential release, or code execution without independent runtime authorization.

## 10. Tool policy

The optional `tool_policy` object can describe allowed tools, denied tools, and whether human approval is requested.

A conforming runtime MUST treat this object as a **restriction or request**, never as an authority escalation. A JOS document cannot grant itself access to a tool that the runtime would otherwise deny.

When `allowed` and `denied` conflict, the more restrictive runtime policy MUST win.

## 11. Execution contract

The optional `execution` object can declare:

- a requested capability,
- input mappings,
- protocol bindings,
- flow invocations,
- resource budgets.

Budgets are upper-bound requests. A runtime MAY impose stricter limits and MUST NOT exceed its own configured limits because a JOS document declares a larger budget.

Input values are data and MUST be validated according to the receiving capability.

## 12. Orchestration

The optional `orchestration` object can declare named steps and flows.

JOS 1.0.0 schema recognizes step types including `shell`, `jos`, and `http`.

A `shell` declaration is **not executable by itself**. A runtime that supports shell-backed steps MUST validate the command against its own policy, execute it only in an appropriately isolated environment, and MUST NOT interpret the presence of a shell declaration as user authorization.

HTTP references MUST be validated before dereferencing. Implementations SHOULD mitigate SSRF, redirect abuse, DNS rebinding, local-network access, and credential forwarding.

## 13. Model policy and persona

The optional `model_policy` object describes model preferences or constraints. Model identifiers are runtime-facing hints and do not guarantee model availability.

The optional `persona` object describes language, tone, behavioral rules, greeting, and related persona attributes.

A runtime MAY reject, ignore, or further restrict model or persona fields when they conflict with platform policy, user policy, or security requirements.

## 14. UI, metrics, billing, security, and lifecycle metadata

JOS 1.0.0 includes optional objects for UI hints, metrics, billing metadata, scoped security requirements, and lifecycle hooks.

These objects are declarations for cooperating runtimes. In particular:

- `security` describes requested conditions; it does not confer authorization.
- `billing` values are untrusted and MUST be validated against authoritative billing systems before charging, crediting, or transferring value.
- lifecycle hooks MUST be authorized like any other executable action.
- UI fields MUST be treated as presentation hints and MUST NOT be trusted as security indicators.

## 15. Integrity

A JOS document MAY contain an `integrity.hash` value of the form:

```
sha256:<64 lowercase hexadecimal characters>
```

For JOS 1.0.0, the hash input is defined as follows:

1. Parse the document as strict JSON and reject duplicate member names.
2. Remove the `integrity.hash` member from the in-memory object. If the `integrity` object becomes empty, retain the empty object.
3. Canonicalize the resulting JSON value using the JSON Canonicalization Scheme (JCS), RFC 8785.
4. Encode the canonicalized representation as UTF-8.
5. Compute SHA-256 over those octets.
6. Compare the lowercase hexadecimal digest with the value after the `sha256:` prefix.

An integrity hash detects content changes; it does **not** establish publisher identity.

The `integrity.signed_by` member is an identifier hint only in JOS 1.0.0. A runtime MUST NOT treat `signed_by` alone as a cryptographic signature or proof of identity. Signature formats, if used, MUST be defined by a separate profile or later specification revision.

## 16. A2A integration

JOS and A2A are complementary.

A2A provides agent communication, task lifecycle, discovery, and protocol bindings. JOS defines a structured execution-contract document.

When a JOS document is carried inside an A2A Part, the sender SHOULD identify it using:

```
mediaType: application/vnd.jos+json
```

A JOS document may be placed in structured `data` when the A2A binding preserves the JSON value, or transferred as a file/URL representation where appropriate.

JOS does not redefine A2A task semantics, authentication, Agent Cards, or transport behavior.

## 17. MCP integration

JOS and MCP are complementary.

MCP exposes tools, resources, prompts, and other capabilities. JOS may declare that a runtime requires MCP-accessible capabilities or may constrain the permitted use of tools.

JOS does not redefine MCP protocol messages, authorization, capability negotiation, or transport behavior.

## 18. Fragment identifiers

For `application/vnd.jos+json`, JSON Pointer as defined by RFC 6901 is the fragment identifier syntax.

For example, given a JOS resource located at:

```
https://example.com/contracts/demo.jos
```

the URI:

```
https://example.com/contracts/demo.jos#/meta/name
```

identifies the value at JSON Pointer `/meta/name`.

## 19. Security considerations

JOS shares the security considerations of JSON described in RFC 8259 and introduces additional risks because documents may describe executable intentions.

Implementations MUST apply the requirements in [SECURITY.md](SECURITY.md). In particular they MUST NOT:

- evaluate a JOS document itself as executable code,
- treat declared permissions as granted permissions,
- trust external references without validation,
- trust billing or identity fields without authoritative verification,
- execute referenced commands solely because they appear in a JOS document.

Implementations SHOULD impose limits on document size, nesting depth, collection sizes, referenced-resource count, execution duration, tokens, retries, and monetary cost.

## 20. Interoperability

A syntactically valid JOS document is valid JSON and can be processed by generic JSON tooling because of the `+json` structured syntax suffix.

Full semantic interpretation requires a JOS-aware implementation.

Conformance requirements are defined in [CONFORMANCE.md](CONFORMANCE.md).

## 21. Versioning and compatibility

JOS uses semantic versioning.

- MAJOR: incompatible semantic or structural changes.
- MINOR: backward-compatible additions.
- PATCH: backward-compatible corrections and clarifications.

A conforming runtime SHOULD explicitly declare which JOS versions and kinds it supports.

Unknown fields are rejected by the JOS 1.0.0 JSON Schema unless a future specification defines an extension mechanism. Extension handling is therefore version-sensitive and MUST NOT be silently guessed.

## 22. References

Normative:

- RFC 2119 — Key words for use in RFCs
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- RFC 8259 — The JavaScript Object Notation (JSON) Data Interchange Format
- RFC 6901 — JavaScript Object Notation (JSON) Pointer
- RFC 8785 — JSON Canonicalization Scheme (JCS)

Informative:

- RFC 6838 — Media Type Specifications and Registration Procedures
- RFC 6839 — Additional Media Type Structured Syntax Suffixes
- Agent2Agent (A2A) Protocol
- Model Context Protocol (MCP)
