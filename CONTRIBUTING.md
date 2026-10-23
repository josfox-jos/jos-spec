# Contributing

Contributions to the JOS specification are accepted through issues and pull requests in `https://github.com/josfox-jos/jos-spec`.

## Where a change belongs

Decide first whether the proposal belongs in:

- the core format (`SPECIFICATION.md`, `schema/`);
- a profile (SPEC-2.0 Section 10);
- a protocol integration profile;
- a runtime or SDK (a separate repository);
- a vendor-specific extension (`x-*` keys; not specified here).

The core specification MUST stay transport-neutral and vendor-neutral. Normative text MUST NOT contain trademarks or product names.

## A specification pull request SHOULD contain

1. the problem statement;
2. the proposed normative behavior, using the key words of RFC 2119 and RFC 8174 in capitals;
3. the compatibility impact: affected versions, whether documents that are valid today stay valid, and migration;
4. the security considerations (`SECURITY.md` sections affected);
5. the schema change, when applicable;
6. vectors: at least one valid and one invalid document under `tests/` for each new MUST, with the reason the invalid one fails;
7. a `CHANGELOG.md` entry.

Before a pull request is merged, from a clean checkout and without network access:

```
python3 -I tools/check-superset.py     # exit code 0
python3 -I tools/validate-jos.py --schema schema/jos.schema.json tests/valid-*.json
```

(`jsonschema` is required.) The invalid vectors in `tests/invalid-*.json` MUST fail.

## Issues

Issues are appropriate for ambiguities, interoperability problems, security concerns (see below), proposed members or kinds, media-type questions and conformance questions.

## Security reports

Do not publish an exploitable defect in a public issue. Send it to jos@josfox.cloud (see `SECURITY.md` Section 12).

## Language

Normative text is in English. Language tags in examples are BCP 47 (`en-US`).

## Licensing

By contributing, you agree that your contribution is distributed under the license of the repository: Apache License 2.0 for schema, vectors, examples and tools, CC BY 4.0 for the specification text (`LICENSE`, `LICENSE-SPEC.md`). A contributor SHOULD state in the pull request any patent claim that the contributor holds and that reads on the contribution.
