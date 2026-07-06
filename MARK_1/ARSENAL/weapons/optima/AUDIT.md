# OPTIMA — INDEPENDENT AUDIT REPORT

**Auditor:** Sonnet (independent, adversarial — generator was Opus; not trusted)
**Date:** 2026-06-20
**Files audited:** optima_gate.py, optima_solve.py, optima_router.py, SPEC.md, GROUNDING.md,
demo_certified/run_demo.py + RESULT.json, demo_reproduce/run_demo.py + RESULT.json,
demo_boundprove/run_demo.py + RESULT.json, demo_reject/run_demo.py + RESULT.json

---

## VERDICT: SOUND_WITH_CAVEATS

The gate's correctness logic is solid. All delivered optimums are verified independently correct.
The gate cannot be tricked into returning OPTIMAL_CERTIFIED for a wrong or infeasible solution
via any certificate type. Two defects found: one crash bug (not exploitable for false positives)
and one output-completeness gap (modeling caveat absent from demo_certified RESULT.json). No
false OPTIMAL_CERTIFIED was achievable through any attack attempted.

---

## SECTION A — INDEPENDENT RE-CHECK OF SHIPPED SOLUTIONS

Every check was implemented from scratch (no import of optima_gate or optima_solve).

### A.1 demo_certified claimed values (13, 13, 156)

**Assignment 4×4** (`cost=[[9,2,7,8],[6,4,3,7],[5,8,1,8],[7,6,9,4]]`):
- Brute-force over all 24 permutations: minimum cost = **13** at permutation (1,0,2,3)
  (agent 0→task 1, agent 1→task 0, agent 2→task 2, agent 3→task 3)
- RESULT.json claims 13. **MATCH. PASS.**

**Knapsack 0/1** (`w=[2,3,4,5,9], val=[3,4,5,6,10], cap=10`):
- Brute-force over all 32 subsets: maximum value = **13** at items {0,1,3}
  (weights 2+3+5=10 ≤ 10, values 3+4+6=13). Unique optimal solution.
- RESULT.json claims 13. **MATCH. PASS.**

**TSP 5 cities** (`pts=[(0,0),(0,3),(4,3),(4,0),(2,5)]`, `dist=int(round(10·euclid))`):
- Distance matrix computed independently. Brute-force over all 24 tours (fixing city 0):
  optimal = **156** at tour (0,1,4,2,3). Claimed tour [0,1,4,2,3] verified: cost = 30+28+28+40+30 = 156.
- RESULT.json claims 156. **MATCH. PASS.**

### A.2 demo_reproduce — burma14 optimum 3323

**GEO distance formula:** Re-implemented independently from TSPLIB95 specification.
geo_dist(city0, city1) = 153 (matches reference). Full matrix matches demo_reproduce's matrix exactly.

**Independent Held-Karp DP:** Implemented from scratch (O(2^14 × 14^2) = ~3.7M states, feasible).
Result: **3323**. PASS.

**Published optimum:** 3323 (Heidelberg TSPLIB95 STSP table, cited in GROUNDING.md). **Three routes agree.**

**Minor observation (not a defect):** A 1-indexed tour string for burma14 cited in this audit as
[1,13,2,14,8,12,4,6,5,7,3,10,11,9] produces cost 5274 with our distance matrix — indicating the
wrong tour was referenced. This does not affect the audit: Held-Karp independently confirmed 3323
and CP-SAT's gate-verified solution achieves 3323. The published optimum value is correct.

---

## SECTION B — GATE ATTACK ATTEMPTS

All attacks written independently. None achieved a false OPTIMAL_CERTIFIED for a wrong/infeasible claim.

### B.1: Infeasible solution with OPTIMAL status — ALL CORRECTLY REJECTED

- `x+y=10 > 7` (violates ≤ constraint): **REJECTED_INFEASIBLE_SOLUTION** ✓
- `x=11` (domain violation): **REJECTED_INFEASIBLE_SOLUTION** ✓
- `x+y=10 ≠ 7` (== constraint violated): **REJECTED_INFEASIBLE_SOLUTION** ✓
- `x=3 < 5` (≥ constraint violated): **REJECTED_INFEASIBLE_SOLUTION** ✓
- `y=0.0` (float non-integer): **REJECTED_INFEASIBLE_SOLUTION** ✓ (non_integer violation in list)
- `x=6.9` (float, fails non-integer check): **REJECTED_INFEASIBLE_SOLUTION** ✓

**DEFECT B.1-CRASH (BUG-1): Missing variable causes unhandled KeyError.**

When any variable declared in `model["vars"]` is absent from the solution dict,
`feasibility_certificate()` correctly adds a `missing_var` violation to the list but then
**continues into the constraint loop**, where `_lhs()` calls `sol[v]` on the missing key and
raises `KeyError`. The exception propagates through `certify()` uncaught.

Reproducing code:
```python
import optima_gate as G
m = {"vars": {"x": [0,10], "y": [0,10]},
     "constraints": [{"coeffs": {"x":1,"y":1}, "op": "<=", "rhs": 7, "label": "cap"}],
     "objective": {"sense": "max", "coeffs": {"x":3,"y":2}, "constant": 0}}
G.certify(m, {"status": "OPTIMAL", "solution": {"x": 7}, "objective": 21,
              "optimality_certificate": {"type": "exhaustive"}})
# -> KeyError: 'y'
```

**Severity: MEDIUM.** Not exploitable for a false OPTIMAL_CERTIFIED (the crash happens before
optimality can be certified), but the system crashes rather than returning
`REJECTED_INFEASIBLE_SOLUTION`. Any caller that doesn't catch exceptions will crash. The
self-test suite does not test missing-variable inputs.

**Fix (one line):** In `feasibility_certificate()`, skip the constraint loop (or use a default of
0 for missing vars) when `viol` already contains a `missing_var` entry, OR catch `KeyError` in
`_lhs()` and treat it as a constraint violation.

### B.2: Wrong objective — ALL CORRECTLY REJECTED

- Claimed 999, true 21: **REJECTED_WRONG_OBJECTIVE** ✓
- Claimed 22, independent says 22, true 21: **REJECTED_WRONG_OBJECTIVE** ✓ (obj recheck fires first)
- solver_bound_gap0 with wrong obj=999 and bound=999: **REJECTED_WRONG_OBJECTIVE** ✓

### B.3: Certificate forgery attempts — ALL FAIL TO CERTIFY

**LP_DUAL forgery:**
- Negative y (`y_cap=-1`): correctly rejected (dual infeasible: some y < 0) ✓
- Wrong G'y (`y_cap=1, ub_x=1`): correctly rejected (G'y ≠ c) ✓
- Valid tight dual (`y_cap=3, lb_y=1`): correctly accepts as OPTIMAL_CERTIFIED ✓
- Wrong claimed obj=22 with lp_dual: caught at objective check first ✓
- All-zero dual (MIN assignment): correctly rejected (G'y ≠ c) ✓

**Note on label indexing:** The gate accepts y keyed by label string, integer index, or string-integer
index (e.g., `{"0": 3}` or `{0: 3}`). This is by design (the row ordering is deterministic), and
is not exploitable since dual feasibility is still verified. Confirmed that integer-indexed and
string-indexed keys work identically to label keys for valid duals.

**INDEPENDENT cert forgery:**
- value=25 ≠ claimed 21: correctly rejected (optimal=False) ✓
- value=21, infeasible witness (x+y=10 > 7): correctly rejected (witness_feasible=False) ✓
- value=21, valid witness but achieves 18 not 21: correctly rejected (witness_objective=18 ≠ 21) ✓
- Empty witness `{}`: returns FEASIBLE_WITH_GAP (not certified, because `wit={}` → `feas=None` → `ok=False`) ✓
- No witness key at all: returns FEASIBLE_WITH_GAP ✓
- `certificate=None`: returns FEASIBLE_WITH_GAP (no certificate supplied) ✓

**SOLVER_BOUND_GAP0:**
- Wrong obj=999 with bound=999: caught at objective check ✓
- Nonzero gap (bound=opt-2): correctly returns FEASIBLE_WITH_GAP ✓

### B.4: IIS attacks — ALL CORRECTLY HANDLED

- Single satisfiable constraint: **REJECTED_no_infeasibility_proof** ✓
- Empty IIS `[]`: **REJECTED_no_infeasibility_proof** ✓ (empty subset is satisfied vacuously)
- Non-existent label: **REJECTED_no_infeasibility_proof** ✓ (label count mismatch caught)
- Satisfiable pair (z≥2, z≤8) claimed infeasible: **REJECTED_no_infeasibility_proof** ✓

### B.5: Edge cases

**DEFECT B.5-EXTRA (BUG-2): Extra variables in solution silently ignored.**

A solution dict with variables not in `model["vars"]` (e.g., `{"x":7, "y":0, "evil_var":9999}`)
passes feasibility and proceeds to OPTIMAL_CERTIFIED. The gate only iterates over `model["vars"]`
for domain checks and does not flag extra variables.

Reproducing code:
```python
G.certify(m, {"status": "OPTIMAL",
              "solution": {"x": 7, "y": 0, "evil_var": 1000000},
              "objective": 21,
              "optimality_certificate": {"type": "exhaustive"}})
# -> OPTIMAL_CERTIFIED
```

**Severity: LOW.** Not exploitable for wrong optimality — the extra variable has no effect on any
constraint or objective calculation (those use only model-declared variables). The solution is
still genuinely optimal. However, silently ignoring extra variables could mask data-pipeline bugs
(e.g., sending the wrong solution) in production use.

---

## SECTION C — MODELING FIDELITY REVIEW

### C.1: Does build_assignment enforce true one-to-one assignment?

**YES.** Constraints: for each row i, `Σ_j x_{i,j} == 1` (each agent assigned exactly once);
for each col j, `Σ_i x_{i,j} == 1` (each task assigned exactly once). Both are `==` constraints.

Tested:
- agents 0 and 1 both → task 1: REJECTED (col_1 lhs=2 ≠ 1) ✓
- agent 0 → tasks 0 AND 1: REJECTED (row_0 lhs=2 ≠ 1, row_3 lhs=0 ≠ 1) ✓

**PASS. The assignment model correctly enforces one-to-one.**

### C.2: MTZ formulation — does it actually forbid subtours?

**Tested 2-subtour: (0→1→0) + (2→3→4→2) with valid degree constraints.**

The gate rejects this: MTZ constraint `mtz_4_2`: `u_4 - u_2 + 5*x_{4,2} = u_4 - u_2 + 5 ≤ 4`
forces `u_4 - u_2 ≤ -1`. Combined with `u_2 ≤ u_3 - 1` and `u_3 ≤ u_4 - 1` (from
`mtz_2_3` and `mtz_3_4`), we get `u_2 ≥ u_4 + 1 ≥ u_3 + 2 ≥ u_2 + 3` — contradiction.
MTZ CORRECTLY FORBIDS the 3-city sub-cycle among non-depot cities. ✓

**2-city subtour alone (0→1→0) without covering cities 2,3,4:** Rejected by degree constraints
(out_2, in_2 etc. require degree 1 at every city). ✓

The depot-relative MTZ ordering (i,j ≥ 1 only) is standard and correct: any subtour among
non-depot cities creates an ordering cycle that MTZ forbids, and a 2-cycle involving the depot
forces the remaining n-2 cities into a separate sub-cycle (caught by MTZ or degree constraints).

**PASS. The MTZ formulation correctly forbids all subtours in the gate-checked plain model.**

### C.3: Is `tsp_independent_lower_bound` always a valid lower bound?

**Formula:** `LB = floor(½ · Σ_i (two cheapest edges incident to city i))`

**Mathematical validity:** Every city has degree exactly 2 in any tour, so
`2 · tour_cost = Σ_i(both tour edges of i) ≥ Σ_i(two cheapest edges of i)`. Thus
`tour_cost ≥ raw_sum/2 ≥ floor(raw_sum/2) = LB`. Valid lower bound by proof. ✓

**Implementation:** Uses `dist[i][j]` for `j ≠ i`, correct for symmetric distances.

**Caveat (noted in code, not a defect):** Valid ONLY for symmetric TSP. All demo instances
use symmetric distances (Euclidean or GEO with symmetric matrix), so this is fine in context.
If the formula is ever applied to asymmetric dist, the bound becomes invalid (undisclosed).

**Tested:** 5-city instance gives LB=156 = brute_opt=156 (tight). 3-city test with odd raw_sum=10
gives LB=5 = opt=5. ✓

**PASS with caveat: document that the formula requires symmetric distances.**

### C.4: MTZ formula — off-by-one / sign check

Formula in code: `u_i - u_j + n * x_{i,j} ≤ n-1` for i,j ∈ {1..n-1}, i≠j.

Original Miller-Tucker-Zemlin (1960): `u_i - u_j + p * x_{i,j} ≤ p-1` where p = number of cities.
With p=n (as in the code), these are **identical**. ✓

u variables: domain [0, n-1]. City 0 anchored at u_0=0. MTZ for i,j ≥ 1. Correct per standard. ✓

**PASS. No off-by-one or sign errors in the MTZ encoding.**

### C.5: GEO distance formula (burma14)

Independently verified: `geo_dist(city0, city1) = 153` matches reference value.
Full 14×14 matrix matches between my implementation and demo_reproduce's implementation exactly.
Three routes (CP-SAT, Held-Karp, literature) all agree on 3323. ✓

**PASS.**

### C.6: Valid Hamiltonian tour passes feasibility

Tour 0→1→4→2→3→0 with u=(0,1,4,2,3): `feasible=True`, cost=156. Correct. ✓

---

## SECTION D — HONESTY RAIL CHECK

### D.1: "Optimal FOR THIS MODEL" consistently labeled?

**YES — in the gate output.** Every call to `certify()` attaches `model_caveat` to the returned
dict regardless of verdict. The caveat text is:
> "certificate covers the FORMAL MODEL only; modeling is kappa<1 (cross-model-reviewed separately) — 'optimal FOR THIS MODEL'."

**MINOR GAP:** `demo_certified/RESULT.json` does NOT include the `model_caveat` field. The
run_demo.py extracts only `gate_verdict` and `independence` from the verdict dict, discarding the
caveat. Compare `demo_reproduce/RESULT.json` which DOES include `model_caveat`.

This is not a correctness issue (the caveat is always in the raw gate output) but a presentation
gap: the demo's committed output file omits the caveat that the SPEC calls non-waivable. A reader
seeing only demo_certified/RESULT.json would not see the "optimal FOR THIS MODEL" qualifier.

### D.2: Reproduction honestly labeled as REPRODUCTION?

**YES.** demo_reproduce/RESULT.json: `"label": "REPRODUCTION of a published optimum (NOT a discovery, NOT a record)"`. Explicitly says NOT a record. ✓

### D.3: Solver self-reported bound honestly distinguished?

**YES.** demo_boundprove/RESULT.json reports both `INDEPENDENT_lower_bound: 3572` and
`solver_self_reported_bound: 3260.0` as separate fields. The `honest_statement` field explicitly
labels the solver bound "a self-report, labeled as such, not the certificate." ✓

### D.4: Timeout/open gap reported as bound, never optimal?

**YES.** demo_boundprove: `claimed_optimal: false`, `gate_verdict: "FEASIBLE_WITH_GAP (no optimality certificate supplied)"`.
No optimality certificate is supplied when no proof exists; the gate returns FEASIBLE_WITH_GAP. ✓

### D.5: Infeasibility requires IIS, not solver shrug?

**YES.** Gate independently enumerates the domain to verify IIS. Empty, single-constraint, and
satisfiable-pair IIS all correctly return REJECTED_no_infeasibility_proof. ✓

### D.6: The "independent" cert in demo_reproduce — slight circularity

The `independent` cert uses: `value = Held-Karp_DP(D)` (truly independent) and
`witness = CP-SAT's solution` (not HK's tour). The gate then checks: (1) value == claimed_obj
(3323 == 3323 ✓), (2) witness feasible (gate re-checks CP-SAT tour ✓), (3) witness achieves
value (gate recomputes cost from tour ✓).

**This is valid but subtly uses CP-SAT's tour as the optimality witness.** HK confirms 3323 is
the *optimal value*; the gate's re-check confirms CP-SAT's tour *achieves* 3323 and is feasible.
Together these establish CP-SAT is correct. The demo code itself notes this honestly: "Held-Karp
witness: we don't reconstruct HK's tour." This is an acknowledged honest caveat, not overclaiming.

### D.7: SPEC / GROUNDING.md — any overclaims?

- SPEC ceiling section is explicit and conservative ("certifies optimal FOR THE FORMAL MODEL, not real-world truth"). ✓
- GROUNDING.md is honest about what is fetched vs machine-probed. ✓
- SPEC/GROUNDING do not overclaim v5 as a ≥10% promotion (explicitly says it is not). ✓
- No instance where "OPTIMAL" is used without a qualifying cert. ✓

---

## DEFECT SUMMARY

| ID | Severity | Description | Exploitable for False OPTIMAL_CERTIFIED? |
|----|----------|-------------|------------------------------------------|
| BUG-1 | MEDIUM | Missing variable in solution dict causes unhandled KeyError crash in certify() | NO (crashes, does not accept) |
| BUG-2 | LOW | Extra variables in solution dict silently ignored | NO (only affects pipeline hygiene) |
| GAP-1 | LOW | demo_certified/RESULT.json omits model_caveat field | NO (gate output contains it; demo JSON elides it) |
| NOTE-1 | INFO | tsp_independent_lower_bound is only valid for symmetric TSP; not documented in function signature | N/A |

---

## WHAT PASSED (attacks that FAILED to break the gate)

- All <= / >= / == constraint violations correctly detected
- Domain bound violations correctly detected
- Non-integer values correctly rejected
- Wrong objective correctly detected before optimality check
- LP dual with negative y: rejected
- LP dual with G'y ≠ c: rejected
- LP dual with loose bound (h'y > primal): rejected
- Independent cert with mismatched value: rejected
- Independent cert with infeasible witness: rejected
- Independent cert with witness achieving wrong value: rejected
- Empty witness or no-witness independent cert: FEASIBLE_WITH_GAP, not certified
- solver_bound_gap0 with nonzero gap: FEASIBLE_WITH_GAP, not certified
- Empty IIS: rejected
- Satisfiable IIS: rejected
- Non-existent IIS labels: rejected
- Bogus single-constraint IIS: rejected
- MTZ 2+3 subtour: correctly infeasible per gate
- Assignment with duplicate row/column assignments: correctly rejected
- All RESULT.json values confirmed independently correct (13, 13, 156, 3323)

---

## SINGLE MOST IMPORTANT DEFECT

**BUG-1 (CRASH): Missing variable in solution dict causes unhandled KeyError in certify().**

This is not a security hole (it cannot produce false OPTIMAL_CERTIFIED), but it is the most
dangerous defect operationally: any real pipeline that occasionally produces incomplete solutions
(e.g., a solver that doesn't assign values to all variables on early termination) will crash the
gate rather than receive a clean REJECTED verdict. The fix is trivial: return early from
`feasibility_certificate()` when `missing_var` violations are detected (before the constraint loop),
or make `_lhs()` treat missing solution variables as 0 (and add a violation). The current code
detects missing variables correctly but then crashes before it can act on the detection.

---

## RESOLUTION — defects fixed by the generator + re-verified (2026-06-20, post-audit)

The Sonnet audit verdict was **SOUND_WITH_CAVEATS** with no exploitable false-certification. All four
findings were addressed and machine-re-verified:

- **BUG-1 (MEDIUM, missing-var KeyError)** — FIXED. `feasibility_certificate` now detects an incomplete
  solution and returns a clean `REJECTED_INFEASIBLE_SOLUTION` (with `"incomplete": True`) BEFORE the
  constraint loop, instead of crashing in `_lhs`. Permanent regression added to the gate self-test
  (case f': missing var -> REJECTED, not crash).
- **BUG-2 (LOW, extra vars silently accepted)** — HARDENED. Unrecognized variables are now recorded in
  `feasibility["notes"]` as `unrecognized_vars` (still a valid verdict — they touch no declared
  constraint/objective — but no longer silent). Regression added (case f'': ghost var is noted).
- **GAP-1 (LOW, demo_certified omitted model_caveat)** — FIXED. `demo_certified/RESULT.json` now records
  the non-waivable `model_caveat`.
- **Symmetric-TSP caveat** on `tsp_independent_lower_bound` — DOCUMENTED in the function docstring
  (valid for symmetric distances; the demos are all symmetric).

Post-fix: `python3 selftest_all.py` green (gate + router); all four demos re-run and still match their
committed predictions. No defect found by the audit was exploitable for a false OPTIMAL_CERTIFIED; the
fixes harden operational robustness and honesty-labeling. **This is the box working as designed: an
independent model (Sonnet) ≠ the generator (Opus) caught real defects that were then fixed and
re-verified.**
