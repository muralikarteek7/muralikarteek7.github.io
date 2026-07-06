# VAULT — SPEC (verifier-gated, TTL-aware verified-result memory)
*KIT piece SHOES-b (`Next/KIT_EXPANSION_PROPOSAL.md` §4). Built 2026-06-20, BOX-style.
Status: INFRA, not a weapon — no ratchet movement. Gate green (`selftest_all.py` exit 0).*

## 0. The one-line job
Store only MACHINE-VERIFIED (or fetched-source) results as **facts** — each with its
verification method, provenance, and a TTL — demote everything unverified to a clearly
labeled **LEAD** that is NEVER returned as truth, and FLAG / re-verify stale high-stakes
entries on read rather than silently serving them. It stops the box re-walking proven
ground without ever letting an unverified belief masquerade as a fact.

## 1. The three entry tiers (the read/write contract)
| tier | enters as | TTL | reuse rule |
|---|---|---|---|
| **VERIFIED_FACT** | a VALID machine-proof / cross-method-agreement record attached | none (does not decay) | reuse freely; a machine proof has no calendar |
| **FETCHED_FACT** | a fetched source + URL + date record | 30 days | shorter TTL; stale high-stakes read -> re-verify |
| **LEAD** | NO valid verification record | n/a (never a fact) | surfaced as a hypothesis to TEST, never as truth |

## 2. The minimum verification-record SCHEMA (the audit-fix, κ=1 core)
A FACT-tier write is admitted ONLY with a STRUCTURALLY VALID record. Required fields,
each a **NON-EMPTY STRING** after strip (`method`/`artifact`/`result` are textual
provenance, not numbers or flags):

```
verification_record = {
  "method":   <how it was verified — e.g. "CP-SAT == Held-Karp == TSPLIB">,
  "artifact": <where the proof lives — a file path / URL + date / stdout>,
  "result":   <the verified value/claim the record certifies>,
}
```

**Rejection rules (`validate_verification_record`, the gate-of-the-gate):**
- `None` / non-dict record -> REJECT.
- Any required field MISSING -> REJECT.
- Any required field present-but-EMPTY (`""`, whitespace-only) -> REJECT.
- Any required field that is NOT a `str` -> REJECT. This includes falsy-but-non-empty
  values (`False`, int `0`) AND truthy-non-string values (`True`, `42`, `3.14`, `[]`,
  `{}`, `None`). A non-text value certifies nothing. (`bool` is checked first because
  `bool ⊂ int` in Python.) **[audit fix — Defect 2: the type-confusion LEAD-promotion
  attack.]**
- `{"verified": true}` -> REJECT (no method/artifact/result).

**Why this is the κ=1 core:** "has a record" must mean a VALID one. Without the
present-but-empty AND the type rejection, a LEAD is promoted in place by attaching
`{verified:true}`, an all-empty record, or a contentless `{"method": False, ...}` —
the **in-place / type-confusion LEAD-promotion attack**. The record check is a
deterministic, non-gameable code function: PASS/FAIL is not a matter of opinion.

## 3. The verifier-gated WRITE (`vault_gate.gate_write`)
- The **record decides the tier, not the request.** A write asking for VERIFIED_FACT /
  FETCHED_FACT is admitted at that tier ONLY if its record validates; otherwise it is
  **DEMOTED to LEAD** with a recorded `demotion_reason`. No tier is ever self-claimed
  into existence.
- A LEAD NEVER carries a stored verification record (`verification_record: None`).
- Structural minimums: `result` and `domain` (keying scope) required, non-empty.
- `stakes` is a **committed ENUM** `("low","high")` declared by the writer — NOT inferred
  by a model. A non-enum value raises.

## 4. TTL + staleness (κ<1 routing — flag, don't reconcile)
- TTL is **committed per tier** (`TTL_DAYS`): VERIFIED_FACT=None (non-decaying),
  FETCHED_FACT=30d. FETCHED facts anchor their TTL on `fetched_at`.
- `staleness(stored, now)` returns one of:
  - `FRESH` — within TTL, or non-decaying.
  - `FLAG_STALE` — expired, **low** stakes -> may be served WITH a stale flag.
  - `REVERIFY` — expired, **high** stakes -> must re-verify before reuse (never served silently).
- This is the κ<1 boundary: whether the *content* is still true in the world after the
  TTL is a judgment / a fresh fetch — the VAULT FLAGS it, it does NOT reconcile temporal
  change (the mem0-2026 open problem; see `GROUNDING.md`).

## 5. The READ contract (`vault_store`)
- `write(entry)` -> persists the gate's normalized entry and returns a **distinct COPY**
  (JSON round-trip). The returned dict and the stored dict share NO references, so a
  caller mutating the returned value CANNOT flip a stored LEAD to a FACT or tamper a
  stored fact's verification record. **[audit fix — Defect 1: the returned-reference
  in-memory mutation bypass.]** (The disk-backed Vault was already safe via reload; the
  in-memory Vault now matches it.)
- `query_facts(query)` -> **ONLY** FACT tiers, each annotated with `freshness`. A LEAD is
  filtered out here — the cardinal invariant, asserted in the self-tests (including the
  case where a lead's `domain` text matches the query).
- `query_leads(query)` -> **ONLY** LEAD tiers, labeled `UNVERIFIED — a hypothesis to TEST`.
- `reverify_queue()` -> high-stakes fact-tier entries whose freshness is `REVERIFY`.
- `trace_provenance(stored)` -> the verification trail of a FACT (method/artifact/result +
  provenance); returns `None` for a LEAD (a fact you can't trace is not a fact).

## 6. The router (`vault_router`)
Classifies a CANDIDATE result by the κ-gate — is there a non-circular record (a machine
run, a fetched source) backing it? — into eligible tier BEFORE the gate runs:
- `has_machine_verification_record` -> VERIFIED_FACT (κ=1, non-decaying).
- `has_fetched_source_record` -> FETCHED_FACT (κ=1 at write, DECAYS).
- `is_unverified_belief_or_conclusion` / `is_judgment_or_interpretation` -> LEAD (κ=0).
- empty / unmatched -> LEAD (default; no declared verification path is not a fact).
The router decides routing; the gate decides admission (defense in depth — a candidate
that *claims* a machine record is fact-eligible at routing, but the gate still validates
the record's contents).

## 7. Self-tests (non-waivable; `selftest_all.py` exits non-zero on any failure)
(a) accept-good: valid-record result -> VERIFIED_FACT, reads back with method + provenance.
(b) catch-broken: record-less FACT write -> DEMOTED to LEAD, never a fact.
(c) abstain-malformed / LEAD-promotion attack: present-but-empty record (`{verified:true}`,
    all-empty, whitespace, missing field, empty-list, None) -> ALL rejected to LEAD; a
    valid record still ACCEPTED (the gate is not always-reject).
(d) stale FETCHED fact past TTL -> FLAG_STALE (low) / REVERIFY (high), never silent.
(e) a LEAD is NEVER returned in a facts query (even on domain match); leads query only.
(f) provenance survives a disk round-trip; stakes ENUM + structural minimums enforced.

## 8. κ honesty
- **κ=1 (EXACT):** the record-validity check, tier assignment, and FACT-vs-LEAD decision —
  deterministic, non-gameable code.
- **κ<1 (JUDGMENT, NOT adjudicated here):** whether a fetched fact's content is still true
  after its TTL — flagged for re-verify, never reconciled. "High stakes" is a committed
  ENUM, not a model judgment.

## 9. What this is NOT (see README ceiling)
Not a weapon; not a place for unverified beliefs dressed as facts; not a model of temporal
change; not weight-level continual learning. It is external memory that stops rework.
