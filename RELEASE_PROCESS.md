# Release process

A release of the JOS specification is an immutable git tag `vMAJOR.MINOR.PATCH` (`GOVERNANCE.md`, Versions and tags). This document says how a tag is cut, in two stages, and what blocks it.

## Tags

| Tag | Where | Created by | Meaning |
|---|---|---|---|
| `jos-spec-vMAJOR.MINOR.PATCH-rc.N` | the review repository (private, pre-production), branch `jos-spec-v2`, annotated | the maintainer, after the checks of Stage 1 | a release candidate under review; never cited as published; never moved or deleted |
| `vMAJOR.MINOR.PATCH` | the public repository `https://github.com/josfox-jos/jos-spec` | a person, by hand (no automation pushes to the public repository) | the published version; the registration cites it |

The branch `jos-spec-v2` of the review repository has no history in common with the development repository: each candidate is one commit whose tree is the exported repository and whose parent is the previous candidate. The absence of a common ancestor with the development repository is intended; nothing of its history, and no commit trailer, travels with a delivery.

## Stage 1: release candidate `jos-spec-vMAJOR.MINOR.PATCH-rc.N`

1. The change class of everything merged since the last tag is recorded in `CHANGELOG.md` under the new version, with normative, editorial and tooling changes listed separately.
2. From a clean checkout, without network access:

```
python3 -I tools/check-superset.py      # exit 0: every 1.0.0 vector and example is valid 2.0.0 (the number rule of SPECIFICATION Section 2.1 is the one exception)
python3 -I tck/run.py                   # exit 0: every valid vector validates, and each invalid vector fails on its own
```

3. The repository gate reports no P0 in red and a score of 100 (`tools/guard-repo-jos.mjs --dir . --perfil spec`), including the golden rule: every root property of `schema/jos.schema.json` is defined in the specification and vice versa.
4. The reference implementations are built deterministically and pinned: `tck/reference-implementations.lock.json` names each one (package, version, asset file, size, sha256).
5. The maintainer tags `jos-spec-vMAJOR.MINOR.PATCH-rc.N` and publishes it in the review repository as a prerelease whose assets are the reference implementations named in the lock, the lock itself, the evidence of the candidate (`EVIDENCE.md`) and, when it exists, the list of revisions for the next candidate (`RC-REVISIONS.md`). The release is created as a draft, the assets are uploaded, and then it is published; the `release published` event runs the job `reference-implementations`, which downloads the assets, checks each sha256 against the lock of the tag, installs them offline and runs the document-level TCK on them with `--expect-version` (`tools/verify-reference-implementations.py`).
6. A release candidate MAY still carry `<pending: …>` markers; the conformance workflow reports them as a warning and fails only on a final tag. The candidate is open for review; no document cites it as published.

## Stage 2: final `vMAJOR.MINOR.PATCH`

1. The review pipeline (red teams, blue team, independent arbiters scoring the versioned rubric against offline truth) reports a confidence of at least 0.99 as the lower bound of the 95 % confidence interval, with no weight-5 check failed. Its verdict is sealed in `replays/<run>/veredicto.json`.
2. A person verifies every URL of the release, including the `$id` of each schema, and records the result (`tools/url-check.py --human`). Every `$id` and every link in the released documents refers to the tag, not to a branch.
3. The `<pending>` markers are gone from every file of the package.
4. A person pushes the tree of the accepted candidate to the public repository and tags `vMAJOR.MINOR.PATCH` there. The tag is never moved or deleted.
5. After the tag: the registration template (`IANA.md`) is sent or updated under RFC 6838 Section 5.5, and the `Published specification` field names the tag.

## What blocks a release

- A P0 of the repository gate in red (license, security, governance, CI, schema, prose, vectors).
- `tools/check-superset.py` with exit code other than 0, or an invalid vector that validates.
- A normative change without its schema change, its vectors and its `CHANGELOG.md` entry (golden rule).
- A `<pending>` marker in a file of the package.
- A URL or `$id` that does not resolve, or that points to a branch.

## Pending

- Signed tags (`git tag -s`) once the signing key of the change controller is published.
- Release automation (`release-please`, as A2A and `openai-agents-python` use) once the public repository exists; the two-stage flow above mirrors `cut-release.yml` of MCP (`rc` and `final`).
