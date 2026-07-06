# SHOES_ROUTING A/B-lite — COMMITTED PREDICTIONS (written BEFORE running)

*Box discipline: predictions frozen here BEFORE `run_demo.py` exists and BEFORE it is executed. The
machine (the two rails) decides pass/fail. A prediction that fails is reported as failed. This is an
ILLUSTRATION on a tiny synthetic task set, not a benchmark — no borrowed headline numbers, no kappa=0
quality claim.*

## The task set (8 synthetic tasks, machine-classifiable)
A mix designed to exercise the ladder: machine-checkable computation, routine generation, hard-but-
executable, genuinely-un-executable-hard, and interpretation (kappa=0). Each task carries a hidden
`required_tier` (the tier it truly needs) used ONLY to score misroutes after the fact.

## Arm A vs Arm B
- **Arm A = always-Opus** (every task to the most-capable rung). The expensive baseline.
- **Arm B = ROUTE-PLANNER** (cheapest rung that clears the bar). The rail under test.
Cost = sum of relative-cost weights (execute=0, haiku=1, opus=40, fable=80; from BOX_V4: execute $0,
Haiku ~1/40 Opus, Fable ~2x Opus).

## Committed predictions

### P1 — ROUTE-PLANNER cuts cost vs always-Opus
- **Arm B total cost is < 50% of Arm A total cost** on this task set (the machine-checkable + routine
  tasks leave the expensive rung, only the genuinely-hard-unexecutable tasks stay on Opus).
- Predicted direction: large cost cut. Exact ratio decided by the machine.

### P2 — EXECUTE preserves the exact-verifier pass on the machine-checkable subset (STRUCTURAL INVARIANT, **by construction — NOT a quality claim**)
- **HONESTY CORRECTION (audit DEFECT 2):** this demo **generates NO model output and compares none.** Both
  Arm A and Arm B invoke the **IDENTICAL deterministic Python verifier lambda** for each machine-checkable
  task (e.g. `sum(range(1,101))==5050`). So this check asks only *"does the same function return True?"* —
  which **cannot fail regardless of which tier was routed.** It is therefore a **structural invariant that is
  TRUE BY CONSTRUCTION**, demonstrating only that routing a machine-checkable task to EXECUTE preserves the
  exact-verifier pass-path.
- It is **explicitly NOT** evidence of "no quality regression" on model-generated output. Establishing that
  would require **actually calling models on each arm and comparing their outputs** — out of scope for this
  deterministic in-folder demo, and **not claimed here.**
- The only **empirical** A/B claim in this demo is **P1 (cost)** — routing produces genuinely different cost
  weights. On the kappa=0 subset we make **NO quality claim** at all (honest limit — reported, not scored).

### P3 — FOOTING flags every injected under-grounded / unstable draft
- We inject 3 deliberately under-grounded or paraphrase-unstable drafts. **FOOTING flags all 3**
  (`uncertain=True`, action in {ROUTE_UP, GROUND_THEN_RECHECK, ABSTAIN}), and flags **0** of the 3
  matched well-grounded drafts (no false alarms on the clean ones).

### P4 — the misroute (g) backstop fires
- For the task whose `required_tier=opus` but which Arm-B-cheap-defaults would send to Haiku (a misroute),
  **ROUTE-PLANNER sets `misrouted_below_required_tier=True` AND FOOTING flags the degraded draft.** The
  silent-quality-regression adversary is caught by at least one of the two rails (target: both).

### P5 — the stuck-detector ends a dead search instead of looping
- A simulated weapon-track search with `STUCK_AFTER_N` consecutive zero verified-fact-delta iterations
  returns `stuck=True, action=STRATEGY_SWITCH_OR_IMPASSE`; a productive search returns `CONTINUE`.

## What would FALSIFY the rails
- P1: Arm B cost >= Arm A cost (router not saving) → fail.
- P2: any machine-checkable task where Arm B's EXECUTE path fails the same exact verifier Arm A passes → fail.
  (NB: this is the structural-invariant check, not a quality-regression test; no model output is generated, so
  P2 carries NO quality claim — see the HONESTY CORRECTION above.)
- P3: any injected bad draft NOT flagged, or any clean draft FALSELY flagged → fail.
- P4: the misroute slips BOTH rails (planner flag False AND FOOTING uncertain False) → fail (this is the
  primary adversary; a single-rail catch is acceptable-but-noted, a double-miss is a hard fail).
- P5: stuck search returns CONTINUE, or productive search returns STRATEGY_SWITCH → fail.
- ANY "verified"/"safe"/"correct" wording emitted by FOOTING anywhere → fail.
