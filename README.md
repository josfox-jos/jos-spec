# .jos — JOS Object Specification v1.0.0

> Portable, declarative, sealed AI execution contracts.

## What is .jos?

`.jos` is a JSON-based contract format for AI agent orchestration. A `.jos` document encodes intention, guardrails, execution budget, orchestration steps, and cryptographic integrity in a single JSON object.

**MIME Type:** `application/vnd.josfox+json` (IANA registration pending)

## Specification

- [**jos.v1.0.0.md**](jos.v1.0.0.md) — Full format specification
- [**schema/jos.schema.json**](schema/jos.schema.json) — JSON Schema (2020-12)

## Quick Example

```json
{
  "jos": { "version": "1.0.0", "kind": "atom" },
  "id": "ai.foxtana.atom.summarize",
  "meta": { "name": "Document Summarizer" },
  "intention": { "objective": "Summarize input documents" },
  "execution": { "budget": { "max_cost_usd": 0.50 } }
}
```

## Kind Registry

| Kind | Purpose |
|------|---------|
| `atom` | Single unit of execution |
| `flow` | Composed sequence of atoms |
| `service` | Long-running service with endpoints |
| `persona` | Declarative AI agent personality |

## License

Apache 2.0 — © 2026 JOSFOX LLC. All rights reserved.

