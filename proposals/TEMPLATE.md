---
jep: JEP-NNNN
title: <short title>
status: Draft
authors: [<name> (<github handle>)]
created: YYYY-MM-DD
target: <JOS version, e.g. 2.0.0>
depends_on: []
---

# JEP-NNNN: <title>

## Abstract

One paragraph.

## Motivation

What cannot be expressed, validated, or exchanged today. Cite real documents or implementations.

## Specification

Normative text, in the same voice as `SPECIFICATION.md` (MUST, SHOULD, MAY).

## Schema changes

The exact JSON Schema fragment added, changed, or removed, and where it goes.

## Security considerations

Threats introduced or mitigated. Reference `SECURITY.md` sections.

## Backward compatibility

What happens to existing documents and to conforming runtimes. Change class per `GOVERNANCE.md`.

## Migration

How a 1.x document becomes a document that uses this change, if anything changes.

## Examples

At least one `.jos` document that validates with the proposed schema, and one vector that must be rejected.

## Conformance tests

Vectors to add under `conformance/vectors/` and their expected outcome under `conformance/expected/`.

## Reference implementation

Where it is implemented (repository, version) and how to run it.
