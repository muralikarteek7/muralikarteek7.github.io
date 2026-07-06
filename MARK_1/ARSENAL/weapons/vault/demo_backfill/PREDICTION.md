# VAULT backfill demo — COMMITTED PREDICTIONS (written BEFORE running)
*Box discipline: predictions frozen here before `run_demo.py` is executed. The machine
judge (the frozen gate + store read-contract) decides pass/fail. A prediction that
fails is reported as failed.*

We backfill a handful of REAL results from this season into a fresh VAULT, then exercise
the read contract. Every verdict is decided by `vault_gate` / `vault_store`, not by any
narrative.

## The ingested entries (the inputs)
| # | candidate | declared tier | record? | stakes |
|---|---|---|---|---|
| A | burma14 optimal tour length = 3323 | VERIFIED_FACT | machine: CP-SAT == Held-Karp == TSPLIB (OPTIMA) | low |
| B | ζ(2) = π²/6 ≈ 1.6449340668 | VERIFIED_FACT | machine: SYMBOLICA 30-digit cross-method agreement | low |
| C | sqlite3 library version = 3.51.0 (this machine, 2026-06-20) | FETCHED_FACT | machine probe + date, but content can drift | high |
| D | "selective-context decomposition might cut cost ~5×" | LEAD | none (a session hunch) | low |
| E | "approach Z is probably optimal" written WITH `requested_tier=VERIFIED_FACT` but NO record | VERIFIED_FACT (attempted) | none — the record-less FACT attack | low |
| F | "promote me" written WITH an EMPTY record `{verified:true}` | VERIFIED_FACT (attempted) | present-but-empty — the in-place LEAD-promotion attack | low |

## Committed predictions (what the machine MUST do)
1. **A, B admit as VERIFIED_FACT**, read back in a `facts` query WITH their verification
   method, and trace to provenance. They are **non-decaying** (a proof has no calendar TTL).
2. **C admits as FETCHED_FACT** with a TTL set; read TODAY (within 30d) it is **FRESH**;
   read 100 days later it is **REVERIFY** (high-stakes stale -> re-verify, never silently
   served) and appears on the **reverify_queue**.
3. **D admits as a LEAD**; it is **NEVER returned by `query_facts`** (even when its domain
   text overlaps a query); it IS returned by `query_leads`, labeled a hypothesis-to-test.
4. **E (record-less FACT request) is DEMOTED to a LEAD** — not admitted as a fact. It does
   NOT appear in `query_facts`; it appears in `query_leads` with a demotion reason.
5. **F (present-but-EMPTY record) is DEMOTED to a LEAD** — the in-place LEAD-promotion
   attack FAILS. `verification_record` is stored as `None`; it does NOT appear in
   `query_facts`.
6. The final `facts` query returns **exactly {A, B, C}** (3 facts) and **zero leads**;
   the `leads` query returns **exactly {D, E, F}** (3 leads) and **zero facts**.
7. Provenance survives a **disk round-trip**: re-open the persisted JSON and A/B/C still
   trace to their verification method + source.

## What would falsify the VAULT
- Any of D, E, F appearing in `query_facts` (a lead masquerading as a fact — the cardinal sin).
- A, B, or C missing from `query_facts`, or losing their verification method/provenance.
- C served WITHOUT a stale flag after its TTL on a high-stakes read.
- The empty-record write (F) admitted as a FACT (LEAD-promotion succeeds).
- Counts other than 3 facts / 3 leads at the end.

## Honesty notes baked into the prediction
- κ=1 (exact, the entry gate): "does this write carry a valid record?" and the tier
  assignment are deterministic code checks.
- κ<1 (judgment, NOT decided by the VAULT): whether C's *content* is still true after its
  TTL — the VAULT FLAGS it for re-verify; it does not reconcile temporal change.
- This is INFRA (stops rework), NOT a capability/weapon and NOT a ratchet move.
