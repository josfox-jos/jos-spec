# Companion specifications

Documents that `SPECIFICATION.md` cites for runtime behaviour. Each one has its own version and status, written in its first lines; none of them changes the media type registered for `application/vnd.jos+json`. Where a companion has vectors, they are in its `tests/`.

Which ones are normative depends on what an implementation claims (`SPECIFICATION.md` Section 11):

| Companion | Defines | Document, parser, validator | Kernel — Core | Kernel — Composition | Kernel — Replay | Engine |
|---|---|---|---|---|---|---|
| `josid/0.1.0` | identifiers (`art_`, `run_`, `cap_`, `usr_`, …) | normative for `art_` only (Section 8.1, 8.2) | normative | normative | normative | normative for the ids it reports |
| `capability/0.1.0` | the authorization a run is bound to | not needed | normative | normative | normative | normative (never open a channel the Capability did not grant) |
| `ledger/0.1.0` | the hash-chained ledger of receipts | not needed | informative (receipts are Section 7.2) | informative | normative (Section 7.3) | not needed |
| `context-engine/0.1.0` | the engine that builds model context | not needed | not needed | not needed | not needed | normative for an engine that claims it (a later phase) |

A parser or validator of `.jos` documents needs only `SPECIFICATION.md` and `schema/`. The layout of a `.jos/` folder beyond what Section 9 names is not a companion of this version.
