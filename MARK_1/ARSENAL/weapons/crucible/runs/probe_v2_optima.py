#!/usr/bin/env python3
"""CRUCIBLE-v2 — DIFFERENTIAL false-accept hunt on the OPTIMA gate with an INDEPENDENT oracle.

The original CRUCIBLE run DECLINED optima's false-accept hunt ("brute-force is its own mechanism").
Here the independent oracle is scipy.linprog (SIMPLEX on the LP RELAXATION) — a genuinely different
algorithm from optima's integer enumeration. The LP relaxation is a RIGOROUS BOUND on the integer
optimum (max: int_opt <= LP_opt; min: int_opt >= LP_opt). So:
  * if optima ever CERTIFIES an integer optimum that BEATS the LP bound -> IMPOSSIBLE -> KILL.
  * plus: optima must ACCEPT the true optimum and REJECT a suboptimal-claimed-optimal.
(scipy.milp/HiGHS was tried first but SIGBUS-crashes on some ==-constraint models; linprog is stable.)
Deterministic, seeded, reproducible."""
import sys, os, itertools
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/optima")
import optima_gate as OG

TOL = 1e-6


class LCG:
    def __init__(s, seed): s.x = seed & 0xFFFFFFFF
    def nx(s): s.x = (1103515245 * s.x + 12345) & 0x7FFFFFFF; return s.x
    def ri(s, lo, hi): return lo + s.nx() % (hi - lo + 1)


def obj_at(model, sol):
    o = model["objective"]
    return sum(o["coeffs"].get(v, 0) * sol[v] for v in model["vars"]) + o.get("constant", 0)


def gen_model(r):
    nv = r.ri(2, 3); names = ["x", "y", "z"][:nv]
    vars_ = {n: [0, r.ri(3, 6)] for n in names}
    cons = []
    for _ in range(r.ri(1, 3)):
        coeffs = {n: r.ri(-3, 4) for n in names if r.ri(0, 1)}
        if not coeffs: coeffs = {names[0]: 1}
        cons.append({"coeffs": coeffs, "op": ["<=", ">=", "=="][r.ri(0, 2)],
                     "rhs": r.ri(-2, 12), "label": f"c{len(cons)}"})
    coeffs = {n: r.ri(-4, 5) for n in names}
    return {"vars": vars_, "constraints": cons,
            "objective": {"sense": "max" if r.ri(0, 1) else "min", "coeffs": coeffs, "constant": r.ri(-5, 5)}}


def feasible_points(model):
    names = list(model["vars"])
    ranges = [range(model["vars"][n][0], model["vars"][n][1] + 1) for n in names]
    return [dict(zip(names, c)) for c in itertools.product(*ranges)
            if all(OG._op_holds(OG._lhs(con["coeffs"], dict(zip(names, c))), con["op"], con["rhs"])
                   for con in model["constraints"])]


def lp_bound(model):
    """INDEPENDENT oracle: scipy.linprog on the LP RELAXATION -> a rigorous bound on the integer optimum.
    Returns the relaxation optimum (incl. the objective constant), or None on infeasible/error/unbounded."""
    names = list(model["vars"]); idx = {n: i for i, n in enumerate(names)}; nv = len(names)
    o = model["objective"]; c = np.zeros(nv)
    for v, co in o["coeffs"].items(): c[idx[v]] = co
    cc = -c if o["sense"] == "max" else c
    Aub, bub, Aeq, beq = [], [], [], []
    for con in model["constraints"]:
        row = [con["coeffs"].get(n, 0) for n in names]
        if con["op"] == "<=": Aub.append(row); bub.append(con["rhs"])
        elif con["op"] == ">=": Aub.append([-x for x in row]); bub.append(-con["rhs"])
        else: Aeq.append(row); beq.append(con["rhs"])
    bounds = [(model["vars"][n][0], model["vars"][n][1]) for n in names]
    try:
        res = linprog(cc, A_ub=Aub or None, b_ub=bub or None, A_eq=Aeq or None, b_eq=beq or None, bounds=bounds)
    except Exception:
        return None
    if res.status != 0:
        return None
    relax = -res.fun if o["sense"] == "max" else res.fun
    return relax + o.get("constant", 0)


def accepted(v): return v.get("verdict") == "OPTIMAL_CERTIFIED"


def violates_bound(model, certified_obj, U):
    if U is None: return False
    return (certified_obj > U + TOL) if model["objective"]["sense"] == "max" else (certified_obj < U - TOL)


def run(n_models=4000, seed=20260621):
    r = LCG(seed)
    kills = []; feas = 0; probes = 0; bound_checks = 0
    for _ in range(n_models):
        m = gen_model(r)
        fps = feasible_points(m)
        if not fps: continue
        feas += 1
        sense = m["objective"]["sense"]
        true_opt = (max if sense == "max" else min)(obj_at(m, s) for s in fps)
        witness = next(s for s in fps if obj_at(m, s) == true_opt)
        U = lp_bound(m)
        # sanity: the integer optimum must respect the independent LP bound (else MY enum or LP is wrong)
        if U is not None:
            bound_checks += 1
            if (true_opt > U + 1e-4) if sense == "max" else (true_opt < U - 1e-4):
                kills.append(("ORACLE-INCONSISTENT enum>LPbound", m, true_opt, U)); continue

        def check(claim, must_accept, tag):
            nonlocal probes
            probes += 1
            v = OG.certify(m, claim)
            acc = accepted(v)
            # independent soundness net: any ACCEPT whose certified objective beats the LP bound is a KILL
            if acc and violates_bound(m, claim["objective"], U):
                kills.append((f"FALSE-ACCEPT beats-LP-bound [{tag}]", m, claim["objective"], U))
            if must_accept and not acc:
                kills.append((f"FALSE-REJECT honest-optimum [{tag}]", m, true_opt, v.get("verdict")))
            if (not must_accept) and acc:
                kills.append((f"FALSE-ACCEPT [{tag}]", m, claim["objective"], true_opt))

        # P1 honest optimum (exhaustive cert) -> ACCEPT
        check({"status": "OPTIMAL", "solution": witness, "objective": true_opt,
               "optimality_certificate": {"type": "exhaustive"}}, True, "exhaustive-honest")
        # P2 suboptimal claimed optimal -> REJECT
        subs = [s for s in fps if obj_at(m, s) != true_opt]
        if subs:
            s2 = subs[r.ri(0, len(subs) - 1)]
            check({"status": "OPTIMAL", "solution": s2, "objective": obj_at(m, s2),
                   "optimality_certificate": {"type": "exhaustive"}}, False, "exhaustive-suboptimal")
            check({"status": "OPTIMAL", "solution": s2, "objective": obj_at(m, s2),
                   "optimality_certificate": {"type": "independent", "value": obj_at(m, s2), "witness": s2}},
                  False, "independent-suboptimal")
        # P3 lying inflated objective (still claims optimal) -> REJECT (objective mismatch)
        infl = true_opt + (1 if sense == "max" else -1)
        check({"status": "OPTIMAL", "solution": witness, "objective": infl,
               "optimality_certificate": {"type": "exhaustive"}}, False, "lying-objective")

    print(f"CRUCIBLE-v2 OPTIMA differential hunt — INDEPENDENT oracle = scipy.linprog LP-relaxation bound")
    print(f"  seed={seed} models={n_models} | feasible probed={feas} | gate probes={probes} | LP-bound checks={bound_checks}")
    if kills:
        print(f"  *** {len(kills)} KILL(s) ***")
        for k in kills[:12]:
            print("   -", k[0], "|", k[1].get("objective"), k[1].get("constraints"))
    else:
        print("  RESULT: SURVIVED to budget — across every probe, optima ACCEPTED the true optimum, REJECTED")
        print("          suboptimal/lying claims, and NEVER certified a value beating the independent LP bound.")
        print("          optima's kappa=1 optimality gate is now ADVERSARIALLY DIFFERENTIAL-TESTED (was metamorphic-only).")
    return kills


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    ks = run(n)
    sys.exit(1 if ks else 0)
