#!/usr/bin/env python3
"""EXACT-SOLVE demo: assignment + knapsack + small TSP, each certified optimal by an
INDEPENDENT exact method (the gate, not the solver status, is the result)."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import optima_solve as S
import optima_gate as G

out = {"demo": "EXACT-SOLVE certified optimality", "cases": []}

# ---- assignment ----
cost = [[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]]
cp_m, x, plain = S.build_assignment(cost)
opt, perm = S.hungarian_min(cost)
witness = {f"x_{i}_{j}": (1 if perm[i] == j else 0) for i in range(4) for j in range(4)}
claim = S.solve_to_claim(cp_m, plain,
                         {f"x_{i}_{j}": x[(i, j)] for i in range(4) for j in range(4)},
                         optimality_cert={"type": "independent", "value": opt, "witness": witness})
v = G.certify(plain, claim)
out["cases"].append({"problem": "assignment_4x4", "solver_status": claim["status"],
                     "objective": claim["objective"], "independent_optimum": opt,
                     "gate_verdict": v["verdict"],
                     "independence": v["optimality"]["independence"]})

# ---- knapsack ----
w, val, cap = [2, 3, 4, 5, 9], [3, 4, 5, 6, 10], 10
cp_m, take, plain = S.build_knapsack(w, val, cap)
dp_opt, dp_take = S.knapsack_dp(w, val, cap)
witness = {f"t_{i}": dp_take[i] for i in range(len(w))}
claim = S.solve_to_claim(cp_m, plain, {f"t_{i}": take[i] for i in range(len(w))},
                         optimality_cert={"type": "independent", "value": dp_opt, "witness": witness})
v = G.certify(plain, claim)
out["cases"].append({"problem": "knapsack_0_1", "solver_status": claim["status"],
                     "objective": claim["objective"], "independent_optimum": dp_opt,
                     "gate_verdict": v["verdict"],
                     "independence": v["optimality"]["independence"]})

# ---- small TSP ----
pts = [(0, 0), (0, 3), (4, 3), (4, 0), (2, 5)]
d = [[int(round(10 * math.dist(a, b))) for b in pts] for a in pts]
cp_m, (xx, uu), plain = S.build_tsp(d)
vi = {f"x_{i}_{j}": xx[(i, j)] for i in range(5) for j in range(5) if i != j}
for i in range(5):
    vi[f"u_{i}"] = uu[i]
bf_opt, tour = S.tsp_bruteforce(d)
# build the witness in the plain namespace from the brute-force tour
wit = {f"x_{i}_{j}": 0 for i in range(5) for j in range(5) if i != j}
for k in range(5):
    a, b = tour[k], tour[(k + 1) % 5]
    wit[f"x_{a}_{b}"] = 1
for idx, city in enumerate(tour):
    wit[f"u_{city}"] = idx
claim = S.solve_to_claim(cp_m, plain, vi,
                         optimality_cert={"type": "independent", "value": bf_opt, "witness": wit})
v = G.certify(plain, claim)
out["cases"].append({"problem": "tsp_5cities_MTZ", "solver_status": claim["status"],
                     "objective": claim["objective"], "independent_optimum": bf_opt,
                     "brute_force_tour": list(tour), "gate_verdict": v["verdict"],
                     "independence": v["optimality"]["independence"]})

out["all_certified"] = all(c["gate_verdict"] == "OPTIMAL_CERTIFIED" for c in out["cases"])
out["all_independent_agree"] = all(c["objective"] == c["independent_optimum"] for c in out["cases"])
out["model_caveat"] = v["model_caveat"]  # non-waivable: certificate covers the FORMAL MODEL only
print(json.dumps(out, indent=2))
json.dump(out, open(os.path.join(os.path.dirname(__file__), "RESULT.json"), "w"), indent=2)
