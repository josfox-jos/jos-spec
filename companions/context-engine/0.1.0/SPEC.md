# `context` engine — context assembly and embedding injection

**Version:** 0.1.0 · **Status:** Draft · **Date:** 2026-10-14 · **Layer:** L2 engine · **Conformance:** `tests/vectors.json`
**Depends on:** `.jos` 2.0 §3.5 (limits), §6.3 (prefix/suffix), §7.2 (receipt), PAL 0.1.0, the context tree (`genesis/`) 0.1.0, Capability 0.1.0 · **Antecedents:** the generator's guardrails layer 2 (anti-dissolution), the context tree's load order, the judge service's v1 embeddings (mock).

RFC 2119 key words apply.

## 1. Purpose and boundary

The kernel never knows what a vector is. Everything that reaches a model as context is produced by this engine, under three guarantees the kernel enforces: it is **declared** (every injected item is an `execution.inputs` entry or a context-tree path), **measured** (tokens counted by the supervisor and recorded in the receipt), and **bounded** (`guardrails.limit.context_tokens`; exceeding it is code 4 before the model is called, never a silent truncation).

## 2. Contract

Input: a step whose engine chain includes `context` (`execution.context: { … }`), the run context, the Capability. Output: an ordered list of **context items** `{ ref, blob, tokens, source, reason }` and the rendered prefix/suffix split for the downstream `llm` engine.

```json
"execution": {
  "context": {
    "order": ["defs", "constraints", "invariants", "specs", "ai"],
    "sources": ["jos://genesis/", "jos://db/app/notes?topic={{ topic }}"],
    "select": { "strategy": "walk", "max_items": 12, "max_tokens": 6000 },
    "embed": { "strategy": "similarity", "model_class": "embed", "threshold": 0.70, "top_k": 8 }
  }
}
```

| Field | Meaning |
|---|---|
| `order` | Anti-dissolution order. Items are emitted in this order regardless of selection: definitions, then constraints, invariants, specs, agent configuration. A conforming engine MUST NOT reorder |
| `sources` | PAL routes only. No URLs, no file paths outside the scope |
| `select.strategy` | `walk` (deterministic pattern walk over the context tree; $0), `similarity` (embeddings), `rank` (a cheap `llm` at temperature 0 ranks candidates), `all` |
| `embed` | Used by `similarity`: `model_class: embed` is routed like any model (router service); `threshold` and `top_k` bound the result |
| `max_tokens` | Hard cap for this step; MUST be ≤ `guardrails.limit.context_tokens` |

## 3. Rules

1. **Declared or nothing.** The engine MUST NOT read anything not reachable from `sources` through PAL with the step's Capability. Reads are ledger `pal` entries with `blob_`.
2. **Deterministic by default.** `walk` is the default and produces the same items for the same tree hash. `similarity` and `rank` are `bounded`: the receipt records the embedding model id and the scores; the crystal key includes the item `blob_`s, so the same tree and query hit the cache.
3. **Prefix stability.** Items from `defs`, `constraints`, `invariants` form the **prefix** (stable across calls, byte-identical ordering); `specs` and `ai` selected per query form the **suffix**. The receipt carries `prompt_prefix_hash`.
4. **Overflow is an error, not a trim.** If the selected items exceed `max_tokens`, the engine MUST drop whole items from the end of the suffix in reverse selection order until it fits, and record `dropped[]`; it MUST NOT cut an item mid-way. If the prefix alone exceeds the cap, code 4.
5. **Provenance in the receipt.** `context.items[]` with `ref`, `blob_`, `tokens`, `reason` (`walk`, `similarity:0.83`, `rank:3`). This is what makes "the project context was injected" verifiable (prompt-enhancer promise).
6. **No learning inside the run.** User feedback and relevance learning are a service that updates the context tree or the router between runs.

## 4. Embeddings

An embedding is a `blob_` keyed by `(model_id, blob_ of text)`; engines SHOULD store embeddings through `jos://blob/` so they are content-addressed and shared. Cosine similarity with threshold is the only normative operation; vector stores are adapters. The judge service's v1 `mockVectorize` is non-conforming (not a model).

## 5. Performance

Zero cost when a step has no `execution.context`. With `walk`: one tree hash lookup plus file reads already cached by `blob_`. Token counting uses the engine's tokenizer or, when absent, a declared estimator (`chars/4`) flagged `estimated: true` in the receipt.

## 6. Conformance

Vectors: order preserved under every strategy; overflow dropping whole items; prefix hash stable across two queries; a source outside the Capability denied (code 3); `walk` determinism on a fixed tree; `similarity` receipt with scores.
