# JOSID — Identifier Specification

**Version:** 0.1.0 · **Status:** Draft · **Date:** 2026-10-14 · **Layer:** kernel · **Conformance:** `tests/vectors.json`
**Depends on:** `.jos` 2.0 §8 (canonical hash) · **Used by:** Capability, Ledger, Envelope, Store.

RFC 2119 key words apply.

## 1. Purpose

A JOSID names anything that can be **owned, cited, audited or grouped**: users, runtimes, hosts, organizations, runs, jobs, days, approvals, instantiated intentions, documents, crystals. It MUST be generatable **offline, on any device, without coordination**, and MUST be unique with negligible collision probability. Relations between identified things are stated in ledger entries, never encoded by concatenating identifiers.

## 2. Grammar (ABNF, RFC 5234)

```
josid      = [ system "." ] kind "_" payload
system     = 1*32( ALPHA / DIGIT / "-" )          ; lowercase; routing/readability only (§5.1)
kind       = 2*8 LOWER                             ; see §3
payload    = ulid / digest / named
ulid       = 26 CROCK                              ; §4.1
digest     = 12*64 HEXLOWER                        ; §4.2, even length
LOWER      = %x61-7A
HEXLOWER   = DIGIT / %x61-66
CROCK      = DIGIT / %x41-48 / %x4A-4B / %x4D-4E / %x50-54 / %x56-5A   ; Crockford base32, uppercase, no I L O U
```

Total length MUST NOT exceed 128 octets. A JOSID contains only `[A-Za-z0-9._-]`; it is safe unquoted in shells, URLs and file names.

## 3. Kinds

| Family | Kind | Identifies | Payload |
|---|---|---|---|
| minted | `usr` | a user or agent principal | ULID |
| minted | `org` | an organization / tenant | ULID |
| minted | `rt` | a runtime (sadmin, admin, user, public are *classes* carried as claims, not kinds) | ULID |
| minted | `host` | a host (localhost, a cloud region, a vendor endpoint) | ULID |
| minted | `run` | one execution of a document | ULID |
| minted | `job` | a scheduled or grouped set of runs | ULID |
| minted | `day` | an accounting day of a runtime | ULID |
| minted | `int` | an instantiated intention (a template filled with inputs) | ULID |
| minted | `cap` | a Capability (permission + budget grant) | ULID |
| minted | `apr` | an approval event (human gate, budget approval) | ULID |
| minted | `clone` | a shadow clone (agent instance) | ULID |
| content | `art` | a `.jos` document by content | SHA‑256 of the canonical document (`.jos` 2.0 §8.1) |
| content | `crystal` | a sealed execution record by its key | SHA‑256 crystal key (`.jos` 2.0 §8.3) |
| content | `blob` | arbitrary bytes (outputs, attachments) | SHA‑256 of the bytes |
| derived | `ent` | a catalog member or a document by its stable name (§4.3) | UUID v5 of `class:name` |

The family is determined by the **kind**, never by the payload shape. New kinds MAY be registered in a later version; implementations MUST reject unknown kinds in `parse` (strict mode) and MAY accept them in lenient mode, reporting `kind_unknown`.

## 4. Payloads

### 4.1 ULID (minted)

128 bits: 48‑bit Unix time in milliseconds (big‑endian) followed by 80 bits from a cryptographically secure random source. Encoded as 26 Crockford base32 characters (RFC‑free reference: ulid spec 1.0). Implementations MUST NOT keep a shared monotonic counter (stateless, K6); two ULIDs minted in the same millisecond are unrelated. Time is informative: ordering by ULID is a convenience, not a guarantee.

### 4.2 Digest (content)

Lowercase hex of SHA‑256. The full 64‑character form is canonical. A **short form** of 12–62 characters MAY be used for display and lookup; a short form MUST resolve to exactly one full identifier in the resolver's scope or the lookup fails (`ambiguous`). Equality between identifiers is defined on the full form only.

### 4.3 Name-derived identifiers

A third payload form, `named`, is a UUID v5 (RFC 9562) computed as `uuid5(NS_JOSFOX, "<class>:<name>")` with `NS_JOSFOX = uuid5(NS_DNS, "josfox.ai")`, written as 32 lowercase hex characters: `ent_3a144c795a4051bd8bdd8534d731fc76`. It identifies *the same thing across versions*: it never changes while `art_` (content) changes on every edit and `meta.version` is moved by the author. Kinds using it: `ent` (any catalog member), and, when a document declares `id`, the kernel MAY expose `ent_` = uuid5 of `"<kind>:<id>"` as its stable identity. The family is `derived`; it is never minted and never reassigned.

## 5. Rules

### 5.1 Prefix is routing, not authority

`system.` is an optional label for readability and routing (`acme.usr_…`). Trust NEVER derives from the string: it derives from the ledger entry that recorded who minted it, signed by that runtime's key (Ledger spec §4). Two identifiers that differ only by `system.` are **different** identifiers.

### 5.2 Relations live in the ledger

"Run R was launched by user U on runtime T at host H under capability C" is a ledger entry `{ run: R, by: U, at: T, host: H, cap: C }`. Implementations MUST NOT encode relations by concatenating identifiers.

### 5.3 No reuse, no reassignment

A JOSID, once minted or derived, refers to one thing forever. Revocation is a ledger entry; the identifier is never reissued.

### 5.4 Policies name classes and claims, not strings

Policies (Capability spec §5) are written over the kind and over claims carried in a Capability (`org`, `runtime_class`, `visibility`, `origin.host_class`). A policy MUST NOT compare identifier strings except for equality of a specific identifier.

### 5.5 Content identifiers are derived, never declared

`art_`, `crystal_` and `blob_` are computed by the kernel. A document MAY carry `integrity.hash`; the kernel MUST recompute and MUST reject a mismatch (code 3).

## 6. Operations

| Operation | Contract |
|---|---|
| `mint(kind) → josid` | kind MUST be minted-family; uses CSPRNG; never fails offline |
| `derive(kind, bytes) → josid` | kind MUST be content-family; deterministic |
| `parse(text) → { system?, kind, family, payload, time? }` | strict by default; errors: `empty`, `too_long`, `bad_chars`, `bad_kind`, `kind_unknown`, `bad_ulid`, `bad_digest`, `odd_digest` |
| `equals(a, b)` | after full-form normalization; `system.` is significant |
| `short(josid, n)` | content-family only |

## 7. Security considerations

A JOSID carries no secret and proves nothing. Minted ULIDs reveal creation time to millisecond precision; implementations that must hide timing MAY mint with a coarse timestamp (e.g. day resolution) at the cost of ordering. Content identifiers reveal nothing about content beyond equality. Implementations MUST use a CSPRNG for minting.

## 8. Conformance

`tests/vectors.json` contains: valid identifiers of every kind with and without `system.`; invalid cases for each error of §6; a minted sample set of 10,000 ULIDs that MUST contain no duplicates; `derive` vectors with known SHA‑256 inputs; short-form resolution cases (unique, ambiguous, not found).
