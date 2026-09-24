# JOS Object Specification

**JOS** is a portable, declarative JSON format for describing AI execution contracts: intent, success criteria, guardrails, capabilities, dependencies, execution budgets, orchestration, and runtime policy.

- **Current specification:** JOS 1.0.0
- **Media type:** `application/vnd.jos+json` (IANA registration pending)
- **Primary file extension:** `.jos`
- **Alternative extension:** `.jos.json`
- **Encoding:** UTF-8 JSON text, without BOM
- **JSON Schema:** Draft 2020-12

JOS documents are data. They are **not executable code**. A conforming runtime decides whether and how to act on declarations in a JOS document and MUST apply its own authorization, sandboxing, policy, and resource controls.

## Documents

- [Specification](SPECIFICATION.md) — normative JOS 1.0.0 definition
- [JSON Schema](schema/jos.schema.json) — machine-readable validation schema
- [IANA registration](IANA.md) — media type registration material
- [Conformance](CONFORMANCE.md) — document and runtime conformance requirements
- [Security](SECURITY.md) — threat model and implementation requirements
- [Changelog](CHANGELOG.md) — specification history
- [Governance](GOVERNANCE.md) and [Contributing](CONTRIBUTING.md)

## Minimal document

```json
{
  "jos": {
    "version": "1.0.0",
    "kind": "atom"
  },
  "meta": {
    "name": "Document Summarizer"
  },
  "intention": {
    "objective": "Summarize the supplied document"
  }
}
```

## Relationship to A2A and MCP

JOS does not replace Agent2Agent (A2A) or the Model Context Protocol (MCP).

- **A2A** provides agent-to-agent communication and transport semantics. A JOS document can be carried as structured data with media type `application/vnd.jos+json`.
- **MCP** exposes tools, resources, prompts, and related capabilities. A JOS document can declare dependencies on MCP capabilities and policy constraints for their use.
- **JOS** describes the execution contract carried between systems or interpreted by a runtime.

In short: **A2A communicates, MCP connects capabilities, JOS declares the contract.**

## Design principles

1. **Portable** — not tied to one model vendor, runtime, or transport.
2. **Declarative** — describes intended work and constraints rather than granting execution authority.
3. **Fail-closed** — declarations never override runtime authorization or sandbox policy.
4. **Machine-verifiable** — JSON Schema plus explicit conformance rules.
5. **Versioned** — the `jos.version` member is authoritative for document semantics.
6. **Interoperable** — based on JSON, URI, semantic versioning, BCP 14 requirement language, and registered media-type conventions.

## Change control

JOS 1.0.0 is maintained by JOSFOX LLC. Substantive changes are proposed and reviewed through the repository process described in [GOVERNANCE.md](GOVERNANCE.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
