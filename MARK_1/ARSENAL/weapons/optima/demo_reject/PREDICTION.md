# PREDICTION — GATE-REJECTS demo (committed BEFORE running)
*Written 2026-06-20, before `run_demo.py` executed. Frozen forecast; compare to RESULT.json.*

**The gate that can't fail is not a gate.** We take a genuinely solved instance and feed the gate
**deliberately broken "OPTIMAL" claims** to prove it catches them. A solver status string of
"OPTIMAL" must NOT survive the gate when the underlying solution is wrong.

| # | adversarial input | committed prediction (gate verdict) | why |
|---|---|---|---|
| A1 | a valid assignment solution + correct cert | **OPTIMAL_CERTIFIED** (control: good input passes) | the gate must accept the truth, not just reject |
| A2 | claim "OPTIMAL" but the solution **violates a constraint** (two agents on one task) | **REJECTED_INFEASIBLE_SOLUTION** | feasibility re-check catches it regardless of the status string |
| A3 | claim "OPTIMAL" with a **wrong objective value** (lie about the cost) | **REJECTED_WRONG_OBJECTIVE** | objective recompute catches the lie |
| A4 | claim "OPTIMAL" with a **non-zero gap** (best_bound ≠ objective) | **FEASIBLE_WITH_GAP** (relabeled a bound, NOT optimal) | optimality is earned by gap=0, never a status string |
| A5 | claim "INFEASIBLE" with a **bogus IIS** (a satisfiable subset) | **REJECTED_no_infeasibility_proof** | infeasibility is a claim that needs a real proof |
| A6 | claim "INFEASIBLE" with a **valid IIS** (genuinely contradictory subset) | **INFEASIBLE_PROVEN** | the gate accepts a real infeasibility certificate |

**Falsifiers:** ANY broken input (A2/A3/A4/A5) receiving an OPTIMAL_CERTIFIED / INFEASIBLE_PROVEN
verdict; the good controls (A1/A6) being rejected. Either would mean the gate is not trustworthy.

**Honesty commitment:** this demo exists to show the gate **can fail the solver**. The solver's
"OPTIMAL" is a self-report; only the independent certificate decides — and it must reject lies.
