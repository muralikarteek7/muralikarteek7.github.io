#!/usr/bin/env python3
"""REPRODUCE-RECORD demo: reproduce the published TSPLIB burma14 optimum (3323).
Labeled REPRODUCTION. Three independent routes must agree: CP-SAT, Held-Karp, the literature."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import optima_solve as S
import optima_gate as G

# burma14 coordinates (lat, long) — TSPLIB GEO, fetched (see GROUNDING.md). The reproduction
# of 3323 via three independent routes is itself the check that these are correct.
COORDS = [(16.47, 96.10), (16.47, 94.44), (20.09, 92.54), (22.39, 93.37), (25.23, 97.24),
          (22.00, 96.05), (20.47, 97.02), (17.20, 96.29), (16.30, 97.38), (14.05, 98.12),
          (16.53, 97.38), (21.52, 95.59), (19.41, 97.13), (20.09, 94.55)]
PUBLISHED_OPT = 3323  # TSPLIB / Heidelberg STSP optimal-solutions table (fetched 2026-06-20)


def geo_rad(x):
    deg = int(x); minute = x - deg
    return math.pi * (deg + 5.0 * minute / 3.0) / 180.0


def geo_dist(a, b):
    RRR = 6378.388
    la, lo = geo_rad(a[0]), geo_rad(a[1])
    lb, lo2 = geo_rad(b[0]), geo_rad(b[1])
    q1 = math.cos(lo - lo2); q2 = math.cos(la - lb); q3 = math.cos(la + lb)
    return int(RRR * math.acos(0.5 * ((1 + q1) * q2 - (1 - q1) * q3)) + 1.0)


n = len(COORDS)
D = [[0 if i == j else geo_dist(COORDS[i], COORDS[j]) for j in range(n)] for i in range(n)]

cp_m, (xx, uu), plain = S.build_tsp(D)
vi = {f"x_{i}_{j}": xx[(i, j)] for i in range(n) for j in range(n) if i != j}
for i in range(n):
    vi[f"u_{i}"] = uu[i]

# route 1: CP-SAT to optimality
claim = S.solve_to_claim(cp_m, plain, vi)
cpsat_len = claim.get("objective")
# route 2: independent Held-Karp DP
hk = S.held_karp(D)
# strengthen the optimality certificate to the INDEPENDENT exact value (Held-Karp witness:
# we don't reconstruct HK's tour, but the gate's 'independent' type needs a feasible witness;
# the CP-SAT tour IS feasible and achieves the value, and HK independently confirms the value
# is optimal -> use exhaustive-equivalent: HK == published == CP-SAT). We certify via the
# matching independent optimum value with the solver's (gate-rechecked feasible) tour as witness.
cert = {"type": "independent", "value": hk, "witness": claim["solution"]}
claim["optimality_certificate"] = cert
v = G.certify(plain, claim)

out = {"demo": "REPRODUCE-RECORD — TSPLIB burma14",
       "label": "REPRODUCTION of a published optimum (NOT a discovery, NOT a record)",
       "cpsat_optimal_length": cpsat_len,
       "held_karp_independent_optimum": hk,
       "published_optimum_TSPLIB": PUBLISHED_OPT,
       "three_routes_agree": (cpsat_len == hk == PUBLISHED_OPT),
       "gate_verdict": v["verdict"],
       "optimality_independence": v["optimality"]["independence"],
       "model_caveat": v["model_caveat"]}
print(json.dumps(out, indent=2))
json.dump(out, open(os.path.join(os.path.dirname(__file__), "RESULT.json"), "w"), indent=2)
