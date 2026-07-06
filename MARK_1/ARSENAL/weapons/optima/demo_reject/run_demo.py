#!/usr/bin/env python3
"""GATE-REJECTS demo: feed the gate deliberately broken 'OPTIMAL'/'INFEASIBLE' claims on a
genuinely solved instance. The gate must REJECT lies and ACCEPT the truth. (The gate that
can't fail is not a gate.)"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import optima_solve as S
import optima_gate as G

# a genuinely solvable 3x3 assignment
cost = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]
cp_m, x, plain = S.build_assignment(cost)
opt, perm = S.hungarian_min(cost)
good_sol = {f"x_{i}_{j}": (1 if perm[i] == j else 0) for i in range(3) for j in range(3)}
good_cert = {"type": "independent", "value": opt, "witness": good_sol}

cases = []

# A1 control: a valid solution + correct cert -> OPTIMAL_CERTIFIED
v = G.certify(plain, {"status": "OPTIMAL", "solution": good_sol, "objective": opt,
                      "optimality_certificate": good_cert})
cases.append({"id": "A1_valid_control", "expect": "OPTIMAL_CERTIFIED", "got": v["verdict"]})

# A2: 'OPTIMAL' but solution violates a constraint (agents 0 and 1 both take task 1)
bad_sol = dict(good_sol)
for k in bad_sol:
    bad_sol[k] = 0
bad_sol["x_0_1"] = 1; bad_sol["x_1_1"] = 1; bad_sol["x_2_2"] = 1   # col_1 has TWO -> infeasible
v = G.certify(plain, {"status": "OPTIMAL", "solution": bad_sol, "objective": 999,
                      "optimality_certificate": good_cert})
cases.append({"id": "A2_infeasible_optimal", "expect": "REJECTED_INFEASIBLE_SOLUTION",
              "got": v["verdict"], "violation_caught": v["feasibility"]["violations"][:2]})

# A3: 'OPTIMAL' but wrong objective value (feasible solution, lied cost)
v = G.certify(plain, {"status": "OPTIMAL", "solution": good_sol, "objective": opt - 99,
                      "optimality_certificate": good_cert})
cases.append({"id": "A3_wrong_objective", "expect": "REJECTED_WRONG_OBJECTIVE", "got": v["verdict"]})

# A4: 'OPTIMAL' with a nonzero gap (best_bound != objective) -> relabel a bound
v = G.certify(plain, {"status": "OPTIMAL", "solution": good_sol, "objective": opt,
                      "optimality_certificate": {"type": "solver_bound_gap0",
                                                 "best_bound": opt - 2}})
cases.append({"id": "A4_nonzero_gap", "expect": "FEASIBLE_WITH_GAP", "got": v["verdict"],
              "got_startswith_ok": v["verdict"].startswith("FEASIBLE_WITH_GAP")})

# A5/A6: infeasibility — bogus IIS rejected, valid IIS proven
inf_model = {"vars": {"z": [0, 10]},
             "constraints": [{"coeffs": {"z": 1}, "op": ">=", "rhs": 7, "label": "lo"},
                             {"coeffs": {"z": 1}, "op": "<=", "rhs": 4, "label": "hi"}]}
v_bogus = G.certify(inf_model, {"status": "INFEASIBLE", "iis": ["lo"]})        # satisfiable alone
cases.append({"id": "A5_bogus_iis", "expect": "REJECTED_no_infeasibility_proof",
              "got": v_bogus["verdict"]})
v_real = G.certify(inf_model, {"status": "INFEASIBLE", "iis": ["lo", "hi"]})   # contradictory
cases.append({"id": "A6_valid_iis", "expect": "INFEASIBLE_PROVEN", "got": v_real["verdict"]})

for c in cases:
    c["PASS"] = (c["got"] == c["expect"]) or c.get("got_startswith_ok", False)

out = {"demo": "GATE-REJECTS — the gate can fail the solver",
       "all_pass": all(c["PASS"] for c in cases), "cases": cases}
print(json.dumps(out, indent=2))
json.dump(out, open(os.path.join(os.path.dirname(__file__), "RESULT.json"), "w"), indent=2)
