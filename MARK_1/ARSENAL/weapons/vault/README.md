# VAULT — verifier-gated, TTL-aware verified-result memory
*KIT piece SHOES-b. INFRA, not a weapon. Built 2026-06-20, BOX-style. Gate green.*

The VAULT turns the box's underused memory directory into a SYSTEM: each session's
MACHINE-VERIFIED results become reusable assets, so the box stops re-walking ground it
already proved — **without ever letting an unverified belief masquerade as a fact.**

## Quick start
```bash
cd /Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/vault
python3 selftest_all.py            # the frozen gate — MUST exit 0 before anything counts
python3 demo_backfill/run_demo.py  # backfill real season results + check 19 predictions
python3 vault_router.py selftest   # router self-test
```

## The contract in one paragraph
A result enters as a **FACT** only if it ships with a STRUCTURALLY VALID verification
record (`method` / `artifact` / `result`, all non-empty). A machine-proof record ->
**VERIFIED_FACT** (non-decaying). A fetched-source record -> **FETCHED_FACT** (30-day
TTL). Anything else — a belief, a "the session concluded X", an empty `{verified:true}`
record — is **DEMOTED to a LEAD** and NEVER returned by a facts query. On read, a stale
high-stakes fact is flagged for **re-verify**, never served silently. (Full contract:
`SPEC.md`. Fetched facts behind the design: `GROUNDING.md`.)

## Files
- `vault_gate.py` — the frozen κ=1 entry gate: record validation (the in-place
  LEAD-promotion defense), tier assignment, TTL/staleness, provenance. `_selftest()` is
  the heart.
- `vault_store.py` — JSON persistence + the read contract (`query_facts` / `query_leads` /
  `reverify_queue`). Enforces "no lead in a facts query."
- `vault_router.py` — classifies a candidate into its eligible tier by the κ-gate.
- `selftest_all.py` — runs all three self-test suites; exits non-zero on any failure.
- `demo_backfill/` — `PREDICTION.md` (frozen before running) + `run_demo.py` + `results.json`.
- `SPEC.md`, `GROUNDING.md`, `AUDIT.md`.

## THE HONEST CEILING — what the VAULT does NOT do
- **It does NOT model temporal change.** A fetched fact true in March can be stale in
  June; the VAULT FLAGS it (TTL + stale-on-read) and routes to re-verify — it does NOT
  know the new truth and does not reconcile it. This is the mem0-2026 open problem
  (`GROUNDING.md` G1/G2): *"Staleness in high-relevance memories is a harder, open
  problem"* and *"Most systems treat change as replacement."* The VAULT mitigates, it
  does not solve.
- **It is not a weapon and not a ratchet move.** It produces no new verified object; it
  STORES ones other weapons/machine-checks produced. The value is not-redoing-verified-
  work. No 10% A/B claim is made or implied.
- **Retrieval is literal-key, not semantic.** `query_facts(query)` does substring matching
  on domain/result. If the query key is not literally in the stored text, recall can miss
  (the same retrieval-recall caveat flagged across the kit). It is a correctness store,
  not a semantic search engine.
- **A fact is only as good as the record it cites.** The gate guarantees a record is
  STRUCTURALLY valid (present, non-empty) and that the FACT traces to it; it does NOT
  re-run the verification. Garbage-but-well-formed in -> stored as a fact with that
  (traceable) provenance. The defense is provenance: every fact names its method/artifact
  so a reader can re-check.
- **It is external memory, not weight-level continual learning** — a deliberate choice
  (`GROUNDING.md` G3): weight updates risk catastrophic forgetting and are impractical for
  production.

## κ labels
- **κ=1 (exact):** record validity, tier assignment, FACT-vs-LEAD — deterministic code.
- **κ<1 (judgment):** whether a fetched fact's content is still true after its TTL — the
  VAULT flags, does not adjudicate. "High stakes" is a committed ENUM, not a model guess.
