# Ledger and Replay — Specification

**Version:** 0.1.1 · **Status:** Draft · **Date:** 2026-10-20 (0.1.0: 2026-10-14) · **Layer:** kernel · **Conformance:** `tests/vectors.json`
**Depends on:** JOSID 0.1.0, Capability 0.1.0, `.jos` 2.0 §7 (receipts), §8.3 (crystals), §9.4 · **Antecedents:** witness 4.0.x (`~/.jos/runs/<ISO>/events.jsonl`), kernel 5.0.0 `witness.js`, 1.1.0 §8.3 receipts.

RFC 2119 key words apply.

**0.1.1 (2026-10-20), additive:** the entry kind `verify` (Section 2). Nothing else changes: a 0.1.0 reader that verifies the chain verifies a 0.1.1 ledger, and the metering view (Section 5) does not read `verify`. The folder keeps its 0.1.0 name so the paths that cite it stay valid.

## 1. Purpose

Every run leaves an **append-only, hash-chained, signed** record from which the run can be audited, metered and replayed (kernel invariants **K4**, **K5**). The kernel writes it; nothing else holds the file descriptor. Analytics, dashboards, grading and billing read it; they never write it.

## 2. Entries

A ledger is a sequence of JSON lines. Every entry has:

```json
{ "seq": 7, "run": "run_01JA…", "kind": "receipt", "ts": "2026-10-14T12:00:01.234Z",
  "body": { …kind-specific… },
  "prev": "sha256:<hash of entry 6>", "hash": "sha256:<hash of this entry with hash empty>" }
```

Entry kinds: `admit` (Capability granted, body = Capability without signature material), `deny` (reason, policy rule index), `start`, `receipt` (`.jos` 2.0 §7.2), `approval` (`apr_` id, who, what gate), `derive` (child/parent Capability), `secret_read` (ref only, never the value), `kill` (reason, counters at kill), `crystal` (crystal sealed, key), `message` (Envelope delivered, hash of payload), `verify` (0.1.1: a seal checked before the first step; body `{ artifact, method, … }`, today only `method: "0.0.7-integrity_ref"` with `manifest`, `sha256` and `eol`, written right after `admit`), `end` (final result object), `error`.

`hash` = SHA‑256 over the canonical entry (JCS) with `hash` = "". `prev` of `seq` 1 is `sha256:0000…0000`.

## 3. Writing rules

- One ledger per run, at `<scope>/.jos/replays/<run_id>/ledger.jsonl` when a `.jos/` scope exists, else in the runtime's run directory.
- The supervisor appends with `O_APPEND`; entries are flushed before the next engine call starts.
- Entries are never modified or deleted. Rotation is forbidden for an open run; retention of closed runs is a runtime policy outside the kernel. (The 4.0.x behaviour of deleting old runs from `serve` is non-conforming.)
- Counters in `receipt` entries come from the supervisor, not from the engine's self-report; when both exist, the receipt carries `reported` and `measured` and `measured` governs budget.
- Secrets never appear: a `vault://` reference is logged, its value is not; engine stdout/stderr MAY be redacted by pattern before logging when the Capability requires (`redact` claim).

## 4. Sealing and signature

At `end`, the kernel writes `seal.json`: `{ run, head: <hash of last entry>, count, artifact: art_, capability: cap_, runtime: rt_, signature }` where `signature` is ed25519 by the runtime key over the canonical seal with `signature` empty. Verification of a ledger = recompute every `hash`, check every `prev`, compare `head`, verify the signature.

## 5. Metering view

From a ledger the following MUST be derivable without any other source: per step and per run `tokens_in`, `tokens_out`, `cost_usd` (as reported by engines; pricing tables are a service concern), `duration_ms`, `attempts`, `cache_hits`, engines and model ids used, approvals, denials. A conforming implementation provides `meter(ledger) → summary` as a pure function.

## 6. Replay

`replay(run_id, mode)`:

| Mode | Behaviour |
|---|---|
| `verify` | Re-validate the chain and the seal; re-hash referenced outputs (`output_ref`) if present. No execution |
| `deterministic` | Re-execute every step whose receipt has `reproducibility.class == deterministic` with the same inputs, engine and pinned parameters; compare `output_hash`. Serve every other step from its crystal if present, else mark `unreplayable` |
| `full` | Re-execute every step; report divergence per step (`same`, `diverged`, `unreplayable`) |

A replay MUST write its own ledger (a new `run_`) that references the original (`body.replay_of`). Divergence is reported, never hidden; a replay that silently substitutes outputs is non-conforming.

## 7. Crystallized directories

Running a crystallized directory (`.jos` 2.0 §9.4) is a replay in `deterministic` mode where every step is served from `.jos/crystals/`; the resulting ledger has all receipts with `cache_hit: true` and no `start` of any engine. The kernel MUST verify the directory's `integrity.hash` before serving.

## 8. Security considerations

The ledger proves what the runtime recorded, under its key. It does not prove the engine's honesty beyond what the supervisor measured. Ledgers can contain sensitive outputs by reference; `output_ref` targets inherit the directory's `security.data_class`. Replay in `full` mode spends budget and MUST require a Capability.

## 9. Conformance

Vectors: a valid 12-entry ledger and seal; tampered entry (hash mismatch), broken `prev`, truncated tail, bad seal signature (all MUST fail `verify`); a run with one deterministic and one stochastic step and its `deterministic` replay result; a crystallized-directory run with zero engine starts; `meter()` expected summary.
