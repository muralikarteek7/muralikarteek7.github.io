#!/usr/bin/env python3
"""BOUND-PROVE demo: a harder TSP (n=26) under a short budget -> FEASIBLE + an honest gap,
reported as a BOUND, never optimal. The gap rests on a RIGOROUS solver-INDEPENDENT lower bound."""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import optima_solve as S
import optima_gate as G

N, SEED, TIME_LIMIT = 26, 11, 2.0
rnd = random.Random(SEED)
pts = [(rnd.randint(0, 1000), rnd.randint(0, 1000)) for _ in range(N)]
D = [[0 if i == j else int(round(math.dist(pts[i], pts[j]))) for j in range(N)] for i in range(N)]

cp_m, (xx, uu), plain = S.build_tsp(D)
vi = {f"x_{i}_{j}": xx[(i, j)] for i in range(N) for j in range(N) if i != j}
for i in range(N):
    vi[f"u_{i}"] = uu[i]

# solve with a deliberately short budget, single worker for determinism
from ortools.sat.python import cp_model
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = TIME_LIMIT
solver.parameters.num_search_workers = 1
solver.parameters.random_seed = SEED
status = solver.Solve(cp_m)
status_name = solver.StatusName(status)

result = {"demo": "BOUND-PROVE — TSP n=26 under a 2s budget", "n": N, "seed": SEED,
          "time_limit_s": TIME_LIMIT, "solver_status": status_name}

if status_name in ("OPTIMAL", "FEASIBLE"):
    sol = {name: int(round(solver.Value(var))) for name, var in vi.items()}
    incumbent = int(round(solver.ObjectiveValue()))
    solver_bound = solver.BestObjectiveBound()
    indep_lb = S.tsp_independent_lower_bound(D)   # RIGOROUS, no solver

    # gate WITHOUT an optimality certificate -> it must report FEASIBLE_WITH_GAP, never optimal
    claim = {"status": "OPTIMAL" if status_name == "OPTIMAL" else "FEASIBLE",
             "solution": sol, "objective": incumbent}
    v = G.certify(plain, claim)

    indep_gap = round((incumbent - indep_lb) / incumbent * 100, 2)
    solver_gap = round((incumbent - solver_bound) / incumbent * 100, 2)
    result.update({
        "feasible_incumbent_length": incumbent,
        "gate_feasibility_recheck": v["feasibility"]["feasible"],
        "gate_verdict": v["verdict"],
        "INDEPENDENT_lower_bound": indep_lb,
        "INDEPENDENT_gap_pct": indep_gap,
        "solver_self_reported_bound": round(solver_bound, 1),
        "solver_self_reported_gap_pct": solver_gap,
        "claimed_optimal": False,
        "honest_statement": (f"FEASIBLE tour of length {incumbent}; proven to lie within "
                             f"[{indep_lb}, {incumbent}] by an INDEPENDENT lower bound "
                             f"({indep_gap}% gap). NOT optimal — a bound. The solver's own "
                             f"tighter bound {round(solver_bound,1)} is a self-report, "
                             f"labeled as such, not the certificate."),
    })
else:
    result["note"] = (f"status {status_name} (no incumbent) — shorten budget / enlarge n to "
                      "produce a FEASIBLE-with-gap case")

print(json.dumps(result, indent=2))
json.dump(result, open(os.path.join(os.path.dirname(__file__), "RESULT.json"), "w"), indent=2)
