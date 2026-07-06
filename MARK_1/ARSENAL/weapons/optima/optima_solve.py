#!/usr/bin/env python3
"""OPTIMA solve loop — model -> CP-SAT solve -> emit a CLAIM for the INDEPENDENT gate.

This module does the SOLVING (a deterministic machine step, $0, no LLM in the loop). It
NEVER renders a verdict: it produces a plain `claim` dict (status, solution, objective,
optimality_certificate, iis) that `optima_gate.certify` then judges INDEPENDENTLY. The
solver's "OPTIMAL" is a self-report; the gate is the result.

Each builder returns BOTH a CP-SAT model AND the gate-readable plain model (same numbers,
re-expressed in the solver-independent schema of optima_gate). The two are kept in lockstep
by construction; the gate re-checks the plain model from scratch, so a builder bug that
disagrees between the two surfaces as a gate REJECT, not a silent pass.

INTEGER-EXACT: all data and variables are integers -> CP-SAT solves over integers, no
floating-point tolerance (kickoff section 4 caveat). We DISCLOSE that and never use float MILP here.

Independent optimality certificates (for the gate, strongest first):
  * EXHAUSTIVE / INDEPENDENT  -- a different exact method (brute force / DP / Hungarian)
    recomputes the optimum; the gate corroborates. Used wherever tractable. FULL independence.
  * SOLVER_BOUND_GAP0          -- CP-SAT's own best_bound == objective. Honest fallback for
    larger instances; the gate re-checks feasibility+objective but the BOUND is the solver's.
"""
import sys
import itertools
from ortools.sat.python import cp_model


# ============================================================ ASSIGNMENT (min-cost)
def build_assignment(cost):
    """cost[i][j] = cost of agent i doing task j (n x n). Minimize total, one-to-one.

    Returns (cp_model, vars, plain_model). LP relaxation is INTEGRAL (assignment polytope is
    TUM) -> an LP dual / the Hungarian optimum is a fully-independent optimality proof.
    """
    n = len(cost)
    m = cp_model.CpModel()
    x = {(i, j): m.NewBoolVar(f"x_{i}_{j}") for i in range(n) for j in range(n)}
    for i in range(n):
        m.Add(sum(x[i, j] for j in range(n)) == 1)
    for j in range(n):
        m.Add(sum(x[i, j] for i in range(n)) == 1)
    m.Minimize(sum(cost[i][j] * x[i, j] for i in range(n) for j in range(n)))

    plain = {"vars": {f"x_{i}_{j}": [0, 1] for i in range(n) for j in range(n)},
             "constraints": [], "objective": {"sense": "min", "constant": 0,
                 "coeffs": {f"x_{i}_{j}": cost[i][j] for i in range(n) for j in range(n)}}}
    for i in range(n):
        plain["constraints"].append({"coeffs": {f"x_{i}_{j}": 1 for j in range(n)},
                                     "op": "==", "rhs": 1, "label": f"row_{i}"})
    for j in range(n):
        plain["constraints"].append({"coeffs": {f"x_{i}_{j}": 1 for i in range(n)},
                                     "op": "==", "rhs": 1, "label": f"col_{j}"})
    return m, x, plain


def hungarian_min(cost):
    """Independent exact assignment optimum via brute force over permutations (small n).
    Returns (optimum, witness_perm). A DIFFERENT algorithm than CP-SAT -> independence."""
    n = len(cost)
    best, arg = None, None
    for perm in itertools.permutations(range(n)):
        c = sum(cost[i][perm[i]] for i in range(n))
        if best is None or c < best:
            best, arg = c, perm
    return best, arg


# ============================================================ KNAPSACK (0/1, max value)
def build_knapsack(weights, values, capacity):
    n = len(weights)
    m = cp_model.CpModel()
    take = [m.NewBoolVar(f"t_{i}") for i in range(n)]
    m.Add(sum(weights[i] * take[i] for i in range(n)) <= capacity)
    m.Maximize(sum(values[i] * take[i] for i in range(n)))
    plain = {"vars": {f"t_{i}": [0, 1] for i in range(n)},
             "constraints": [{"coeffs": {f"t_{i}": weights[i] for i in range(n)},
                              "op": "<=", "rhs": capacity, "label": "capacity"}],
             "objective": {"sense": "max", "constant": 0,
                           "coeffs": {f"t_{i}": values[i] for i in range(n)}}}
    return m, take, plain


def knapsack_dp(weights, values, capacity):
    """Independent exact 0/1-knapsack optimum via DP (different method than CP-SAT)."""
    n = len(weights)
    dp = [0] * (capacity + 1)
    keep = [[False] * (capacity + 1) for _ in range(n)]
    for i in range(n):
        w, v = weights[i], values[i]
        for c in range(capacity, w - 1, -1):
            if dp[c - w] + v > dp[c]:
                dp[c] = dp[c - w] + v
                keep[i][c] = True
    # reconstruct
    c = capacity
    take = [0] * n
    # recompute forward to get a consistent witness (simple re-DP with parent tracking)
    # do an O(n*cap) parent-based reconstruction:
    D = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            D[i][c] = D[i - 1][c]
            if c >= w and D[i - 1][c - w] + v > D[i][c]:
                D[i][c] = D[i - 1][c - w] + v
    c = capacity
    for i in range(n, 0, -1):
        if D[i][c] != D[i - 1][c]:
            take[i - 1] = 1
            c -= weights[i - 1]
    return D[n][capacity], take


# ============================================================ TSP (min tour, exact)
def build_tsp(dist):
    """Symmetric/asymmetric TSP via MTZ subtour elimination. dist[i][j] integer. n cities.
    Returns (cp_model, (x, u), plain_model). Plain model includes the MTZ constraints so the
    gate re-checks the SAME formal model (note: the gate certifies optimality FOR THIS MTZ
    model; we corroborate small instances with an independent Held-Karp/brute optimum)."""
    n = len(dist)
    m = cp_model.CpModel()
    x = {(i, j): m.NewBoolVar(f"x_{i}_{j}") for i in range(n) for j in range(n) if i != j}
    for i in range(n):
        m.Add(sum(x[i, j] for j in range(n) if j != i) == 1)   # out-degree 1
        m.Add(sum(x[j, i] for j in range(n) if j != i) == 1)   # in-degree 1
    u = [m.NewIntVar(0, n - 1, f"u_{i}") for i in range(n)]     # MTZ order vars
    m.Add(u[0] == 0)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                # u_i - u_j + n*x_ij <= n-1
                m.Add(u[i] - u[j] + n * x[i, j] <= n - 1)
    m.Minimize(sum(dist[i][j] * x[i, j] for i in range(n) for j in range(n) if i != j))

    plain = {"vars": {}, "constraints": [], "objective": {"sense": "min", "constant": 0, "coeffs": {}}}
    for (i, j) in x:
        plain["vars"][f"x_{i}_{j}"] = [0, 1]
        plain["objective"]["coeffs"][f"x_{i}_{j}"] = dist[i][j]
    for i in range(n):
        plain["vars"][f"u_{i}"] = [0, n - 1]
    for i in range(n):
        plain["constraints"].append({"coeffs": {f"x_{i}_{j}": 1 for j in range(n) if j != i},
                                     "op": "==", "rhs": 1, "label": f"out_{i}"})
        plain["constraints"].append({"coeffs": {f"x_{j}_{i}": 1 for j in range(n) if j != i},
                                     "op": "==", "rhs": 1, "label": f"in_{i}"})
    plain["constraints"].append({"coeffs": {"u_0": 1}, "op": "==", "rhs": 0, "label": "mtz_anchor"})
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                plain["constraints"].append(
                    {"coeffs": {f"u_{i}": 1, f"u_{j}": -1, f"x_{i}_{j}": n},
                     "op": "<=", "rhs": n - 1, "label": f"mtz_{i}_{j}"})
    return m, (x, u), plain


def held_karp(dist):
    """Independent EXACT TSP optimum via the Held-Karp DP, O(2^n * n^2). A DIFFERENT exact
    method than CP-SAT's MTZ branch-and-bound -> corroborates small reproductions (n<=~15)."""
    n = len(dist)
    C = {(1 << k, k): (dist[0][k], 0) for k in range(1, n)}
    for sz in range(2, n):
        for subset in itertools.combinations(range(1, n), sz):
            bits = 0
            for b in subset:
                bits |= 1 << b
            for last in subset:
                prev = bits & ~(1 << last)
                best = min((C[(prev, k)][0] + dist[k][last], k)
                           for k in subset if k != last)
                C[(bits, last)] = best
    full = (1 << n) - 2  # all cities 1..n-1
    opt, _ = min((C[(full, k)][0] + dist[k][0], k) for k in range(1, n))
    return opt


def tsp_independent_lower_bound(dist):
    """A RIGOROUS, solver-INDEPENDENT lower bound on the optimal SYMMETRIC-TSP tour. (Valid for
    symmetric dist; for asymmetric instances use in/out-edge minima separately — not done here.)
    LB on the optimal symmetric-TSP tour:
        LB = (1/2) * sum_i (two cheapest edges incident to city i).
    Proof: every city has degree exactly 2 in a tour, so 2*tour = sum_i(its two tour edges)
    >= sum_i(its two cheapest edges). Integer-exact via floor. Used in BOUND-PROVE so the
    reported gap rests on an INDEPENDENT bound, not the solver's self-reported best_bound."""
    n = len(dist)
    total = 0
    for i in range(n):
        edges = sorted(dist[i][j] for j in range(n) if j != i)
        total += edges[0] + edges[1]
    return total // 2  # floor keeps it a valid (<=) lower bound for integer tours


def tsp_bruteforce(dist):
    """Independent exact TSP optimum by enumerating tours (fixing city 0). Small n only.
    Returns (optimum, best_tour as a list of cities)."""
    n = len(dist)
    best, arg = None, None
    for perm in itertools.permutations(range(1, n)):
        tour = (0,) + perm
        c = sum(dist[tour[k]][tour[(k + 1) % n]] for k in range(n))
        if best is None or c < best:
            best, arg = c, tour
    return best, arg


# ============================================================ generic CP-SAT solve -> claim
def solve_to_claim(cp_m, plain_model, var_index, time_limit=None, optimality_cert=None):
    """Solve a CP-SAT model and return a plain CLAIM dict for optima_gate.certify.

    var_index: dict mapping the gate var-name (str) -> the CP-SAT variable, so we can read
               the solution back into the gate's plain namespace.
    optimality_cert: if provided (e.g. an INDEPENDENT exact optimum), attach it; otherwise we
               attach the honest SOLVER_BOUND_GAP0 self-report for the gate to judge.
    """
    solver = cp_model.CpSolver()
    if time_limit is not None:
        solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(cp_m)
    status_name = solver.StatusName(status)
    claim = {"status": status_name, "solver_objective_self_report": None}

    if status_name in ("OPTIMAL", "FEASIBLE"):
        sol = {name: int(round(solver.Value(var))) for name, var in var_index.items()}
        obj = int(round(solver.ObjectiveValue()))
        claim["solution"] = sol
        claim["objective"] = obj
        claim["solver_objective_self_report"] = obj
        claim["solver_best_bound"] = solver.BestObjectiveBound()
        if optimality_cert is not None:
            claim["optimality_certificate"] = optimality_cert
        else:
            # honest fallback tier: hand the gate the solver's own bound to judge gap=0.
            bb = solver.BestObjectiveBound()
            bb_int = int(round(bb)) if bb == int(round(bb)) else bb
            claim["optimality_certificate"] = {"type": "solver_bound_gap0", "best_bound": bb_int}
        # normalize status: the GATE decides optimal, but we relay what the solver said.
        claim["status"] = "OPTIMAL" if status_name == "OPTIMAL" else "FEASIBLE"
    elif status_name == "INFEASIBLE":
        claim["status"] = "INFEASIBLE"
    return claim


if __name__ == "__main__":
    print("optima_solve: builders for assignment / knapsack / TSP + independent exact "
          "reference solvers. Import and use; see demo_*/run_demo.py.")
