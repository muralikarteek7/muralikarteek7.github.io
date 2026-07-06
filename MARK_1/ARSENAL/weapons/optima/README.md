# OPTIMA — exact optimization / OR weapon

**What it is.** The OR/Operations facility of the CS & Engineering department. Given a discrete
optimization problem (scheduling, routing, packing, assignment, allocation) with a clean model, OPTIMA
*produces* a **certified-optimal (or proven-bound) solution** and ships nothing an **independent
certificate** hasn't re-verified. It promotes the registry's `W2_exact_combinatorial_solver` to a full
weapon. **The solver's "OPTIMAL" is a self-report; the independent certificate is the result.**

**The genuinely new thing** (over the already-owned v3 "execute-don't-guess" armor) is the **independent
optimality certificate**: feasibility re-checked from scratch + objective recomputed + a proof of gap=0
(exhaustive / LP weak-duality / a different exact algorithm). A weapon ADDED = capability **EXPANSION**,
**NOT a ≥10% promotion.**

## Files
- `optima_gate.py` — **the gate (built first; the result).** Four independent certificates: feasibility,
  objective, optimality (gap=0 / LP-dual / independent-method / honest solver-bound tier), infeasibility
  (IIS). Never calls the solver to judge the solver. `python3 optima_gate.py selftest`.
- `optima_solve.py` — CP-SAT model builders (assignment / knapsack / TSP-MTZ) + **independent exact
  reference solvers** (Hungarian-brute / DP / Held-Karp / brute) used as the strongest certificates +
  a rigorous independent TSP lower bound.
- `optima_router.py` — deterministic mode routing (EXACT-SOLVE / BOUND-PROVE / REPRODUCE-RECORD); κ=0
  fuzzy "optimize our strategy" → armor; every weapon route carries the modeling-κ<1 caveat.
- `selftest_all.py` — **the frozen gate.** Exits 0 only if the gate accepts truth AND rejects every
  broken claim, and the router routes + abstains correctly. **Run this before trusting any output.**
- `demo_certified/`, `demo_reproduce/`, `demo_boundprove/`, `demo_reject/` — committed `PREDICTION.md`
  (written before running) + `run_demo.py` + `RESULT.json`.
- `SPEC.md`, `GROUNDING.md`, `AUDIT.md` — the one-page spec, the grounded facts, the cross-model red-team.

## Run it
```
python3 selftest_all.py                 # gate must be green first
python3 demo_certified/run_demo.py      # assignment+knapsack+TSP, certified optimal (3 independent methods)
python3 demo_reproduce/run_demo.py      # reproduce TSPLIB burma14 = 3323 (CP-SAT == Held-Karp == literature)
python3 demo_boundprove/run_demo.py     # hard TSP under a budget -> FEASIBLE + independent gap, never optimal
python3 demo_reject/run_demo.py         # the gate rejecting broken 'OPTIMAL' claims and a bogus IIS
```

## Honest ceiling
OPTIMA certifies **optimal FOR THE FORMAL MODEL**, not optimal for the real-world problem — translating
words into vars/constraints/objective is **judgment (κ<1)** and is cross-model-reviewed, not certified.
It is **integer-exact** (no float-MILP tolerance here). A timeout is reported as a **bound with a gap**,
never optimal (the W2 failure-mode rail). It **reproduces** published optima labeled as reproductions and
**never claims a record** without an audited certificate strictly beating prior art. It raises
**certified-optimality throughput**, not the model's capability ceiling.
