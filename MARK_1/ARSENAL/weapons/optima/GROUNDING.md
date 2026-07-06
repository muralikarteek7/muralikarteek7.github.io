# OPTIMA — GROUNDING (fetched sources + machine probes for every load-bearing fact)

*Box rule: a load-bearing fact gets a fetched source or a machine check, not memory. For OPTIMA the
**machine probe is usually the stronger evidence** (the C++ CP-SAT bindings ship empty docstrings, so a
live probe beats any doc page). Each fact below carries a fetched URL AND/OR a reproducible machine
check. Grounded 2026-06-20.*

---

## 0. INFRA CHECK (done BEFORE designing around any engine — kickoff section 4)
**Result:** **OR-Tools 9.15.6755 is installed**; `from ortools.sat.python import cp_model` imports;
CP-SAT solves and exposes the bound + IIS APIs. Machine-probed this session (see facts 1–3).
- `python3 -c "import ortools; print(ortools.__version__)"` → `9.15.6755`
- Fallbacks (NOT needed, recorded for completeness): PuLP/python-mip/Pyomo+CBC for MILP; pure-Python
  brute/DP/Held-Karp for tiny instances (we use these anyway as the INDEPENDENT optimality certificates).

## 1. CP-SAT status values + proven OPTIMAL (the EXACT-SOLVE basis)
**Fact:** CP-SAT returns `OPTIMAL` ("an optimal feasible solution was found"), `FEASIBLE` ("a feasible
solution was found, but we don't know if it's optimal"), `INFEASIBLE` ("proven infeasible"),
`MODEL_INVALID`, `UNKNOWN`.
- Fetched: Google OR-Tools, "Solving a CP Problem" / CP-SAT solver:
  https://developers.google.com/optimization/cp/cp_solver  (status table verbatim)
- **Machine probe (stronger):** `max 3x+2y s.t. x+y≤7` → status `OPTIMAL`, `ObjectiveValue()=21`,
  `BestObjectiveBound()=21` ⇒ **gap=0 confirmed**. CP-SAT's `OPTIMAL` means the dual bound met the
  primal. We still re-check feasibility+objective independently and require gap=0 — the status alone is
  never trusted.

## 2. BestObjectiveBound() — the dual/best bound (the optimality-certificate input)
**Fact:** `CpSolver.BestObjectiveBound()` returns the solver's best proven bound on the objective (the
dual side). On `OPTIMAL` it equals `ObjectiveValue()` (gap 0); on `FEASIBLE` it is a valid bound with a
residual gap.
- Fetched: OR-Tools `cp_model` Python API reference (lists `BestObjectiveBound` on `CpSolver`):
  https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html
- **Machine probe (stronger):** confirmed `BestObjectiveBound()=21=ObjectiveValue()` on the OPTIMAL toy;
  and on the BOUND-PROVE TSP n=26 under a 2 s budget, `FEASIBLE` with `BestObjectiveBound() < incumbent`
  (a real residual gap). **Honesty rail:** this bound is the SOLVER'S self-report — our certificate-grade
  gap uses an **independent** bound (fact 5), and the solver bound is labeled "self-reported."

## 3. INFEASIBLE + an IIS (the infeasibility certificate)
**Fact:** CP-SAT proves infeasibility (`INFEASIBLE`) and, with assumption literals + `model.AddAssumptions`,
`CpSolver.SufficientAssumptionsForInfeasibility()` returns a **subset of assumptions that is already
sufficient for infeasibility** — an infeasibility core / IIS analogue.
- Fetched: OR-Tools `cp_model` API reference (method listed on `CpSolver`):
  https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html
- **Machine probe (stronger):** model `x≥5 (if A1)`, `x≤3 (if A2)`, assume `[A1,A2]` → status
  `INFEASIBLE`, `SufficientAssumptionsForInfeasibility()` returned `[A1,A2]` (the contradictory pair).
  Our gate does NOT take this on trust: it independently enumerates the box and confirms the named
  subset has no feasible point (a satisfiable "IIS" is rejected).

## 4. LP weak duality (the LP_DUAL optimality-certificate basis)
**Fact:** For `max c'x s.t. Gx ≤ h`, any **dual-feasible** `y ≥ 0` with `G'y = c` gives `c'x ≤ h'y` for
all feasible `x` (weak duality). So a dual-feasible `y` whose value `h'y` **meets** a feasible primal
objective is an **INDEPENDENT proof of optimality** — it does not trust the solver at all. When the bound
meets the INTEGER primal (e.g. integral/totally-unimodular relaxations such as the assignment polytope),
it certifies integer-optimality.
- Reference (standard LP duality): Bertsimas & Tsitsiklis, *Introduction to Linear Optimization*, ch. 4
  (weak duality: any dual-feasible solution bounds the primal optimum). Vanderbei, *Linear Programming*,
  ch. 5. (Textbook theorem; not solver-specific.)
- **Machine check (stronger):** `optima_gate._verify_lp_dual` verifies `y≥0` and `G'y=c` by **exact
  integer arithmetic** and checks `h'y == primal`. Self-test: a TIGHT dual (`y_cap=3, lb_y=1`) for
  `max 3x+2y, x+y≤7` → `OPTIMAL_CERTIFIED` (bound 21 = primal 21); a LOOSE dual (bound 24) → correctly
  NOT a proof. The solver is never consulted on this path.

## 5. An independent, RIGOROUS lower bound for TSP (the BOUND-PROVE certificate)
**Fact:** For symmetric TSP, `LB = ½ · Σ_i (two cheapest edges incident to city i)` is a valid lower
bound on any tour: every city has degree exactly 2 in a tour, so `2·tour = Σ_i (its two tour edges) ≥
Σ_i (its two cheapest edges)`. (The classic "two-cheapest-edges" / nearest-edge relaxation bound; a
weaker but fully independent cousin of the Held–Karp 1-tree bound.)
- Reference: Held & Karp, "The traveling-salesman problem and minimum spanning trees," *Operations
  Research* 18 (1970) — the 1-tree lower-bound family. https://doi.org/10.1287/opre.18.6.1138
- **Machine check (stronger):** `optima_solve.tsp_independent_lower_bound`; in `demo_boundprove` it
  yields LB=3572 ≤ incumbent 5509 (35% gap), computed with **no solver** — the gap rests on this bound,
  not on CP-SAT's self-reported bound.

## 6. The benchmark with a known optimum (the REPRODUCE-RECORD target)
**Fact:** TSPLIB `burma14` (14 cities, GEO distances) has **proven optimal tour length 3323**; all TSPLIB
instances are solved to optimality (Heidelberg STSP optimal-solutions table).
- Fetched (optimum): Heidelberg TSPLIB95 "Optimal solutions for symmetric TSPs":
  http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/STSP.html  (burma14 → 3323)
- Fetched (instance data, 14 lat/long coordinate pairs): TSPLIB mirror
  https://raw.githubusercontent.com/mastqe/tsplib/master/burma14.tsp  (EDGE_WEIGHT_TYPE GEO)
- Fetched (GEO distance formula): TSPLIB95 documentation (deg+min → radians, RRR=6378.388, the
  `int(RRR·acos(...)+1)` rounding): http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp95.pdf
- **Machine check (strongest):** `demo_reproduce/run_demo.py` computes the GEO matrix from the fetched
  coordinates, solves with CP-SAT → **3323**, and an **independent Held-Karp DP** → **3323**. Three
  routes agree (CP-SAT, Held-Karp, the literature) — which also retro-validates the fetched coordinates
  (wrong coordinates would not hit the published optimum).

## 7. MTZ subtour elimination (the TSP formal model)
**Fact:** The Miller–Tucker–Zemlin formulation eliminates subtours with order variables `u_i` and
constraints `u_i − u_j + n·x_ij ≤ n−1` (for i,j ≥ 1), giving a compact integer TSP model.
- Reference: Miller, Tucker & Zemlin, "Integer programming formulation of traveling salesman problems,"
  *J. ACM* 7 (1960) 326–329. https://doi.org/10.1145/321043.321046
- **Honest note:** the certificate covers THIS MTZ model. We corroborate small instances with an
  independent Held-Karp/brute optimum (a different formulation), so a bug in the MTZ encoding would
  surface as a disagreement, not a silent pass.

---

### What is grounded by FETCH vs by MACHINE (the honest split)
- **Fetched (literature labels):** CP-SAT status semantics; that `BestObjectiveBound`/IIS APIs exist;
  LP weak duality and the Held–Karp/MTZ formulations are standard theorems; burma14's optimum is 3323.
- **Machine-verified (this session, stronger than any citation):** that CP-SAT actually returns gap=0 on
  OPTIMAL and a real IIS on INFEASIBLE; that the LP-dual / independent-method / IIS certificates accept
  truth and reject lies (`selftest_all.py`); that burma14 reproduces 3323 via three independent routes.
  OPTIMA only ever ships the machine-checked object, labeled with the fetched optimality status.
