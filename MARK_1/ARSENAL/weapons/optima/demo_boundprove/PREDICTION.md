# PREDICTION — BOUND-PROVE demo (committed BEFORE running)
*Written 2026-06-20, before `run_demo.py` executed. Frozen forecast; compare to RESULT.json.*

A **harder TSP (n=26, random Euclidean, seed=11)** given a **short time budget (2 s, single
worker)** so CP-SAT does **NOT** close the gap. This is the W2 failure-mode rail in action:
**timeout ⇒ a feasible solution + an honest gap, reported as a BOUND, never "optimal."** The gap
rests on a **RIGOROUS, solver-INDEPENDENT lower bound** (½·Σ two-cheapest-incident-edges), not on
the solver's self-reported best_bound.

| # | claim | committed prediction | why |
|---|---|---|---|
| P1 | CP-SAT status under the 2 s budget | **FEASIBLE** (not OPTIMAL) | probe: n=26 returns FEASIBLE with a residual gap; MTZ bounds are weak |
| P2 | gate verdict on the incumbent | **FEASIBLE_WITH_GAP** (NOT optimal) | feasibility re-checked & passes, but no optimality certificate ⇒ a bound |
| P3 | the returned tour is feasible | **YES** (gate feasibility passes) | CP-SAT respects degree + MTZ; gate re-checks independently |
| P4 | independent lower bound ≤ incumbent | **YES** (LB < incumbent, gap > 0) | the two-cheapest-edges bound is rigorous and below any tour |
| P5 | is "optimal" ever claimed? | **NO — explicitly reported as a bound + gap%** | the whole point of the W2 honesty rail |
| P6 | we also report CP-SAT's self-bound, labeled | **YES, labeled "solver self-reported (tighter)"** | transparency: the certificate-grade gap uses the INDEPENDENT bound |

**Falsifiers:** CP-SAT returning OPTIMAL within budget (then it is not a BOUND-PROVE case — rerun
with a shorter budget / larger n); the gate calling it optimal; the independent LB exceeding the
incumbent (would mean the LB is not valid — a bug to fix).

**Note on reproducibility:** time-limited solves are wall-clock dependent; the EXACT incumbent and
bound may vary run-to-run. The committed prediction is **structural** (FEASIBLE + a positive gap +
never-optimal), which is robust to that variation; RESULT.json records the actual numbers.

**Honesty commitment:** a timeout is **never** dressed as optimal. We ship the feasible tour as a
**bound with a quantified gap**, with the rigorous independent bound carrying the claim.
