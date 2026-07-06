# COMPOSEAUTH (G3) — the compositional-authorization rail

**GLOVES gates each ACTION; COMPOSEAUTH gates the SEQUENCE.** A running blast-radius budget
over GLOVES' allowed actions, so that a stream of individually-safe, individually-authorized
steps **cannot silently compose into a catastrophe** — 100 small reversible deletes = one
irreversible wipe; 50 authorized $20 charges = $1000 nobody approved. Item #6 / gap G3 of the
KIT-EXPANSION plan; the completion of GLOVES (the effector layer).

## What it does

Each GLOVES-allowed action adds its blast-radius to running per-class counters (financial,
data_mutation, broadcast, destruction, external_calls). Before each NEW action the FROZEN
gate compares the running sums to **committed policy thresholds** and returns:

- **OK** — under all thresholds (no false halt on a benign stream).
- **ESCALATE** — a STEP_UP threshold crossed → the NEXT action is raised to STEP-UP.
- **HALT** — a HALT threshold (or the composite blast-score) crossed → stop + escalate to a
  human, even though every step alone was authorized.

Effect in a resource class G3 does NOT enumerate is reported **UNCOVERED** — never silently
counted as "within budget."

## Run it

```sh
cd /Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/composeauth
python3 selftest_all.py                 # the non-waivable gate-of-the-gate tests; exits 0 on green
python3 demo_composition/run_demo.py    # the killer demo vs committed predictions
python3 composeauth_router.py selftest  # the router's own selftest
```

Pure Python 3 stdlib — **no third-party packages, no pip install** required.

## Files

- `composeauth_gate.py` — the FROZEN budget gate: `BudgetStore` (persistent, monotonic,
  crash-resume) + `ComposeAuthGate.decide()`. Contains the 5 non-waivable self-tests.
- `composeauth_policy.py` — all committed thresholds AND score weights, labeled **POLICY**.
- `mock_gloves_ledger.py` — MOCK GLOVES feed (GLOVES' exact ledger shape + the
  `other_effects` catch-all) and the POLICY effect-extractor.
- `composeauth_router.py` — routes an action BUDGET / UNCOVERED / ABSTAIN (with `_selftest`).
- `selftest_all.py` — runs every self-test; non-zero exit on any failure.
- `demo_composition/` — `PREDICTION.md` (frozen before running), `run_demo.py`, `results.json`.
- `SPEC.md`, `GROUNDING.md`, `AUDIT.md`.

## κ honesty

- **κ=1** — the accumulation (Σ per class) + the threshold comparison. A committed sum
  crossing a committed threshold is a machine fact.
- **κ=1 within / κ<1 across** — the effect-extractor is exact for a KNOWN tool inside its
  policy table; across the tool population it is κ<1, so an unknown tool / novel blast class
  routes to UNCOVERED.
- **κ=0** — "is this composition malicious?" is intent. G3 ESCALATEs / HALTs; it **never
  accuses**.

## The honest ceiling

- **It budgets ONLY what it counts.** An attacker who spreads effect across resource classes
  G3 doesn't enumerate is not caught — that effect is *reported UNCOVERED*, never hidden as
  "within budget," but it is not budgeted. Completeness = your enumeration.
- **The thresholds AND the weights are human-owned POLICY, not derived truth.** G3 cannot
  tell you the "right" threshold; it is exact only about "did the committed sum cross the
  committed threshold." Every verdict carries that banner.
- **It is NOT an intent judge.** It escalates/halts on the arithmetic; it does not decide
  whether the sequence was malicious.
- **It needs GLOVES.** Without GLOVES' per-action classification there is nothing to budget.
  This build runs against a **MOCK GLOVES ledger** in GLOVES' exact shape (to stay unblocked
  on GLOVES infra); the swap to the real feed is a single seam.
- **Persistence is infra-limited.** The budget survives a crash-resume (atomic-rename JSON
  store), but in a pure-software box the store is not guaranteed outside the agent's write
  scope — true tamper-resistance needs fs-perms / a separate process / the harness. Stated.
  G3 *cannot prevent* tampering, but it does NOT *trust* a store it can detect as corrupt or
  budget-decreasing: a corrupt file or a negative persisted counter **poisons** the store →
  every verdict HALTs (it never silently resets to $0 and never crashes `__init__` open).
- **Monotonicity is ENFORCED, not just claimed (audit fix).** Counters are non-decreasing
  within a session because negative / NaN / Inf / un-parseable blast amounts are **refused**
  at the extractor and `BudgetStore.add()` rejects any negative delta — all fail closed to
  HALT. (An earlier version *claimed* "no decrement API" while `add()` silently applied a
  negative delta; that false-accept is fixed and regression-tested.)
- **Not a promotion.** G3 is a capability EXPANSION that **completes GLOVES** (the effector
  layer can now bound a sequence, not just a single action). It is NOT a ≥10% A/B promotion.
