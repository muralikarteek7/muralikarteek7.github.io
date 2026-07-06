# OPTIMA — exact optimization / OR (v5 weapon, CS_ENG/OR department)
*One-page spec. Home: `Expanding_Frontiers/weapons/optima/`. Registered in `Next/BOX_V5.md`. Promotes
registry **W2 (exact combinatorial solver)** to a full department weapon.*

## What it is (and is NOT)
OPTIMA is the v5 weapon for **discrete/combinatorial optimization** — scheduling, routing, packing,
assignment, allocation. An optimization solution has a **sharp cheap verifier**: re-evaluate every
constraint on the returned assignment (feasibility), recompute the objective, and back "optimal" with
a **matching dual/bound** (primal = dual ⇒ proven optimal). OPTIMA *produces* a certified solution and
**ships nothing the independent checker hasn't re-verified.** Its value is the **CERTIFICATE + the
modeling**, not "the model did mental math."

**IS NOT — the four rails (kickoff section 1):**
- **NOT "trust the solver's OPTIMAL status."** That is a self-report; the box never trusts a
  self-report. The gate **independently re-checks** feasibility (every constraint, from scratch, no
  solver), the objective, and optimality (gap=0 / matching dual / a different exact method).
- **NOT "optimal for the real problem" — only "optimal FOR THIS FORMAL MODEL."** Translating a
  word-problem into vars/constraints/objective is **JUDGMENT (κ<1)**; the model can be wrong even when
  the solve is exact. The modeling step gets an **independent cross-model review**.
- **NOT "best-found = optimal."** A timeout/open gap ⇒ a **feasible solution + the honest gap**, never
  "optimal." An infeasibility claim needs a **certificate (IIS)**, not a solver shrug.
- **NOT a capability boost.** OPTIMA's edge over a one-shot LLM is the already-owned **execute-don't-
  guess armor (v3)** + the **independent optimality certificate** (the genuinely new thing). A weapon
  ADDED = capability EXPANSION, **NOT a ≥10% promotion.**

## The three modes (each maps to the κ-router; each gated by the independent 4-part certificate)
| mode | router analogue | produces | the FROZEN exact verifier (κ=1) | file |
|---|---|---|---|---|
| **EXACT-SOLVE** | FETCH-KNOWN / armor++ | a certified-optimal solution | feasibility re-check (all constraints, no solver) + objective recompute + **proof of gap=0** (exhaustive / LP-dual / a different exact method) | `optima_gate.py` |
| **BOUND-PROVE** | SEARCH-OPEN | best feasible solution + a proven dual bound on hard instances | primal feasibility re-check + an **independently-valid lower/dual bound**; report the **gap**, never "optimal" | `optima_gate.py` + `tsp_independent_lower_bound` |
| **REPRODUCE-RECORD** | construction engine | a known-best on a benchmark (TSPLIB/MIPLIB) | re-check vs the published optimum **and** a different exact method; labeled **REPRODUCTION**. A record needs an audited certificate strictly beating prior art — **honest negative expected** | `demo_reproduce/` |

## The certificate, not the solver, is the result (kickoff section 3) — `optima_gate.py`
Four independent certificates, each re-evaluating plain solution data against a plain, gate-readable
model in pure Python (the gate NEVER calls the solver to judge the solver):
1. **FEASIBILITY** — re-evaluate every domain bound and constraint on the returned solution. One
   violation ⇒ `REJECTED_INFEASIBLE_SOLUTION`.
2. **OBJECTIVE** — recompute the objective; must equal the claimed value, else `REJECTED_WRONG_OBJECTIVE`.
3. **OPTIMALITY** — earned, never taken from a status string. Accepted only with (most-independent first):
   **(a) EXHAUSTIVE** (gate enumerates the small feasible space); **(b) LP_DUAL** (a dual-feasible
   vector `y` with `G'y=c`, `y≥0`, whose value `h'y` meets the primal — LP weak duality, verified by
   exact integer arithmetic, solver never consulted); **(c) INDEPENDENT** (a different exact algorithm —
   Hungarian/DP/Held-Karp/brute — reports the same optimum with a feasible witness); **(d)
   SOLVER_BOUND_GAP0** (the solver's own `best_bound == objective` — the honest *weakest* tier:
   feasibility+objective are re-checked independently but the bound number is the solver's self-report).
   No matching bound / nonzero gap ⇒ `FEASIBLE_WITH_GAP`, never optimal.
4. **INFEASIBILITY** — a "no solution exists" claim is proven by an **IIS**: the gate independently
   confirms the named constraint subset is itself infeasible (enumeration). A satisfiable "IIS" ⇒
   `REJECTED_no_infeasibility_proof`.

**Gate self-tests (non-waivable, `selftest_all.py`):** ACCEPT a known optimal w/ a valid gap=0 cert;
REJECT an "OPTIMAL" that is actually INFEASIBLE; REJECT an "optimal" with a non-zero gap; REJECT a
wrong objective; PROVE a real IIS; REJECT a bogus one. Gate green before any solve counts.

## Infra + exactness (kickoff section 4) — grounded, see `GROUNDING.md`
- **OR-Tools CP-SAT** (v9.15, installed + machine-probed): emits `OPTIMAL`/`FEASIBLE`/`INFEASIBLE`,
  exposes `BestObjectiveBound()` (dual bound) and `SufficientAssumptionsForInfeasibility()` (an IIS over
  assumption literals). Probe confirmed gap=0 on `OPTIMAL` and a real IIS on `INFEASIBLE`.
- **INTEGER-EXACT:** all model data and variables are integers ⇒ CP-SAT solves over integers with **no
  floating-point tolerance**. We do NOT use float-MILP here; if we ever did, the tolerance would be
  disclosed and feasibility re-checked with an explicit epsilon. We never dress a tolerance-bound float
  result as bit-exact.

## Router (`optima_router.py`)
Deterministic. EXACT-SOLVE / BOUND-PROVE / REPRODUCE-RECORD fire on their κ=1 preconditions; **every**
weapon route carries the **modeling κ<1 caveat**. **κ=0 → armor, not weapon:** a fuzzy "optimize our
strategy" with no formalizable exact objective, or a deliverable scored only by a gameable proxy.
CONFLICT RULE: positive trigger + negative item → **negative wins, weapon off.**

## Killer demos (committed prediction → run → compare)
- `demo_certified/` — assignment + knapsack + small TSP solved to certified optimality; each proven by
  a **different exact algorithm** (Hungarian/DP/brute); gate re-verifies feasibility + objective.
- `demo_reproduce/` — **reproduce** TSPLIB `burma14`'s published optimum **3323** via three independent
  routes (CP-SAT, Held-Karp, the literature); labeled REPRODUCTION.
- `demo_boundprove/` — a harder TSP (n=26) under a 2 s budget → FEASIBLE incumbent + a **rigorous
  independent lower bound** + the honest gap; **never** optimal (the W2 rail).
- `demo_reject/` — the gate REJECTING a broken "OPTIMAL-but-infeasible", a wrong objective, a hidden
  gap, and a bogus IIS; accepting the truth and a valid IIS.

## Honesty rails (non-waivable, OPTIMA-specific)
- **"Optimal" is earned by a certificate (gap=0 / matching dual / a different exact method), never by a
  solver status string alone.** No certificate ⇒ "feasible + gap," labeled.
- **Certified-optimal ≠ right answer to the real problem** — the model is judgment (κ<1); cross-model-
  review the formulation. The certificate covers the formal model only; say so.
- **Timeout / open gap ⇒ a bound, never optimal** (W2 + weak-weapon-cap). Carry the gap, always.
- **Infeasibility is a claim that needs a proof (IIS),** not a solver shrug.
- **Float tolerance is disclosed** — prefer integer/CP exactness (this weapon is integer-exact).
- **The gate that can't fail is not a gate** — no gate ships without its 4 reject self-tests.
- **κ=0 stays armor** — a fuzzy "optimize our strategy" → ground + abstain, never a manufactured cert.

## Ceiling (stated every run)
OPTIMA ships only independent-certificate-passed solutions; it certifies **optimal FOR THE FORMAL
MODEL**, not real-world truth; it reproduces published optima labeled as reproductions; it reports
timeouts as bounds-with-gap, never optimal; it never claims a record without an audited certificate.
It raises **certified-optimality throughput**, not the model's capability ceiling; κ=0 asks → armor.
