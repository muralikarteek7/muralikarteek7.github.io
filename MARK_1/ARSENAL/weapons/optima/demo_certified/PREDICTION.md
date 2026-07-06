# PREDICTION — EXACT-SOLVE demo (committed BEFORE running)
*Written 2026-06-20, before `run_demo.py` executed. Frozen forecast; compare to RESULT.json.*

Three small discrete-optimization problems solved to **certified optimality**. The independent
gate (`optima_gate.py`) re-checks every returned solution from scratch (feasibility + objective)
and the optimality is proven by a **FULLY INDEPENDENT exact method** (a different algorithm than
CP-SAT): Hungarian/brute for assignment, DP for knapsack, brute-force for the small TSP.

| # | claim | committed prediction | why |
|---|---|---|---|
| P1 | 4×4 min-cost **assignment** solves; gate verdict | **OPTIMAL_CERTIFIED** | CP-SAT obj == independent brute-force/Hungarian optimum; gate re-checks one-to-one feasibility |
| P2 | assignment certified optimum value | **13** (probe value; locked) | independent permutation search returns 13 with a feasible witness |
| P3 | 0/1 **knapsack** (5 items, cap 10) solves; gate verdict | **OPTIMAL_CERTIFIED** | CP-SAT obj == independent DP optimum; gate re-checks the capacity constraint |
| P4 | knapsack certified optimum value | **13** (probe value; locked) | DP returns 13 with a feasible witness |
| P5 | small **TSP** (5 cities) solves; gate verdict | **OPTIMAL_CERTIFIED** | CP-SAT obj == independent brute-force tour optimum; MTZ feasibility re-checked by the gate |
| P6 | independent method agrees with the solver on all three | **YES (exact equality)** | the whole point — the certificate, not the solver status, is the result |
| P7 | every shipped certificate's `independence` field | **"FULL ... solver not trusted"** | assignment/knapsack/TSP all use a different exact algorithm as the proof |

**Falsifiers:** any gate verdict ≠ OPTIMAL_CERTIFIED on these tiny instances; the independent
method disagreeing with CP-SAT (would expose a modeling bug — and is exactly what the gate is for);
a certificate marked optimal without the independent value matching.

**Honesty commitment:** these are tiny instances where the box's edge is **execute-don't-guess
(v3 armor)** + the **independent optimality certificate** (the genuinely new thing). NOT a
capability promotion. "Optimal" here means **optimal FOR THIS FORMAL MODEL**, machine-certified.
