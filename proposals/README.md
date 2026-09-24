# JEP: JOS Enhancement Proposals

A JEP is how the JOS specification changes beyond editorial fixes. It is the only path for a new field, a new kind, a new profile, or a breaking change. MCP has SEPs, Python has PEPs; JOS has JEPs.

## Lifecycle

```
Draft → Proposed → Accepted → Implemented → Final
                 ↘ Rejected / Withdrawn
```

- **Draft**: written from [TEMPLATE.md](TEMPLATE.md), opened as a pull request adding `proposals/JEP-NNNN-slug.md`.
- **Proposed**: complete (all template sections filled, at least one example, schema change and conformance vectors drafted).
- **Accepted**: maintainers agree under [GOVERNANCE.md](../GOVERNANCE.md); a target version is assigned.
- **Implemented**: the change is in the specification, the schema, and the conformance vectors, and at least one implementation demonstrates it.
- **Final**: the version that contains it is released.

## Numbering

`JEP-NNNN`, four digits, assigned by the maintainer who accepts the draft pull request. Numbers are never reused.

## Rules

1. One JEP, one change. A JEP that needs another JEP says so in its dependencies.
2. A JEP without a schema change and conformance vectors cannot pass Proposed (the golden rule applies to proposals too).
3. Security considerations and backward compatibility are not optional sections.
4. Candidate material lives in the reference repository (`josfox-ai/jos-format-spec`, profiles and real-world examples) before it becomes a JEP: experiment → profile → multiple implementations → JEP → draft specification → next version.

## Index

| JEP | title | status | target |
|---|---|---|---|
| (none yet) | | | |
