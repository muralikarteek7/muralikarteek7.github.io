#!/usr/bin/env python3
"""OPTIMA-GATE — the INDEPENDENT certificate gate.  kappa = 1 (over the FORMAL model).

THE RESULT IS THE CERTIFICATE, NOT THE SOLVER.  The solver's "OPTIMAL" status is a
self-report; this gate is what the box trusts.  It NEVER calls the solver to judge the
solver: every check below re-evaluates plain solution data against a plain, gate-readable
model in pure Python.  Four certificates (kickoff section 3):

  1. FEASIBILITY  -- re-evaluate EVERY constraint + domain bound on the returned solution
                     from scratch.  One violation -> INFEASIBLE solution -> REJECT.
  2. OBJECTIVE    -- recompute the objective from the solution; must equal the claimed value.
  3. OPTIMALITY   -- "optimal" is EARNED, never taken from a status string.  Accepted ONLY
                     with one of (most-independent first):
                       (a) EXHAUSTIVE       -- the gate enumerates the (small) feasible space
                                               and confirms the claim is the true optimum.
                       (b) LP_DUAL          -- a dual-feasible vector y (y>=0, G'y=c) whose
                                               value h'y MEETS the primal objective -> LP weak
                                               duality proves optimality, INDEPENDENT of the
                                               solver (the gate verifies y by exact integer
                                               arithmetic).  Tight only when it meets the
                                               INTEGER primal (e.g. integral/TUM relaxations).
                       (c) INDEPENDENT      -- a DIFFERENT exact algorithm (Hungarian / DP /
                                               Held-Karp / brute force) reports the same optimum
                                               with a feasible witness.
                       (d) SOLVER_BOUND_GAP0-- the solver's own best_bound == objective.  The
                                               feasibility + objective are still re-checked
                                               independently, but the BOUND NUMBER is the
                                               solver's self-report -> HONESTLY the weakest tier;
                                               labeled as such.  Use only when (a)-(c) are out
                                               of reach (large integer instances).
                     No matching bound / nonzero gap -> verdict FEASIBLE_WITH_GAP, never optimal.
  4. INFEASIBILITY -- a "no solution exists" claim needs a PROOF (an IIS): the gate
                      independently confirms the named constraint subset is ITSELF infeasible
                      (enumeration), not a solver shrug.  A satisfiable "IIS" -> REJECT.

HONEST CEILING: the certificate covers the FORMAL MODEL only.  "Optimal FOR THIS MODEL" is
NOT "optimal for the real-world problem" -- translating words into vars/constraints/objective
is JUDGMENT (kappa<1) and is cross-model-reviewed separately (see AUDIT.md / the router's
modeling caveat).  Float-MILP tolerance is disclosed (this gate is INTEGER-exact: all model
data and solutions are integers, so feasibility/objective are bit-exact; see GROUNDING.md).

Model schema (plain dict, solver-independent):
  model = {
    "vars": {name: [lo, hi]},                       # integer domains (inclusive)
    "constraints": [ {"coeffs": {name: int}, "op": "<="|">="|"==", "rhs": int,
                      "label": str} ],
    "objective": {"sense": "max"|"min", "coeffs": {name:int}, "constant": int},  # optional
  }
  solution = {name: int_value}
"""
import sys
import itertools


# ----------------------------------------------------------------------------- core eval
def _lhs(coeffs, sol):
    """Exact integer left-hand-side of a linear form at the solution."""
    return sum(c * sol[v] for v, c in coeffs.items())


def _op_holds(lhs, op, rhs):
    if op == "<=":
        return lhs <= rhs
    if op == ">=":
        return lhs >= rhs
    if op == "==":
        return lhs == rhs
    raise ValueError(f"unknown op {op!r}")


# ----------------------------------------------------------------------------- (1) feasibility
def feasibility_certificate(model, solution):
    """Re-evaluate EVERY domain bound and constraint from scratch. No solver involved."""
    viol = []
    notes = []
    # extraneous variables (BUG-2 hardening): not unsafe (they touch no declared constraint
    # or objective term) but flagged so a pipeline bug can't hide behind a passing verdict.
    extra = [v for v in solution if v not in model["vars"]]
    if extra:
        notes.append({"kind": "unrecognized_vars", "vars": sorted(extra)})
    # integrality + domain bounds
    missing = False
    for v, (lo, hi) in model["vars"].items():
        if v not in solution:
            viol.append({"kind": "missing_var", "var": v})
            missing = True
            continue
        val = solution[v]
        if not isinstance(val, int):
            viol.append({"kind": "non_integer", "var": v, "value": val})
        if not (lo <= val <= hi):
            viol.append({"kind": "domain", "var": v, "value": val, "bounds": [lo, hi]})
    # BUG-1 fix: an INCOMPLETE solution cannot be evaluated against the constraints (a
    # missing var would KeyError in _lhs). An incomplete solution is infeasible by definition
    # -> return the violations cleanly rather than crash.
    if missing:
        return {"certificate": "FEASIBILITY", "feasible": False, "violations": viol,
                "notes": notes, "incomplete": True}
    # linear constraints
    for k, con in enumerate(model.get("constraints", [])):
        lhs = _lhs(con["coeffs"], solution)
        if not _op_holds(lhs, con["op"], con["rhs"]):
            viol.append({"kind": "constraint", "i": k,
                         "label": con.get("label", f"c{k}"),
                         "lhs": lhs, "op": con["op"], "rhs": con["rhs"]})
    return {"certificate": "FEASIBILITY", "feasible": len(viol) == 0,
            "violations": viol, "notes": notes}


# ----------------------------------------------------------------------------- (2) objective
def objective_certificate(model, solution, claimed_objective):
    obj = model.get("objective")
    if obj is None:
        return {"certificate": "OBJECTIVE", "ok": True, "note": "no objective (feasibility problem)"}
    recomputed = _lhs(obj["coeffs"], solution) + obj.get("constant", 0)
    return {"certificate": "OBJECTIVE", "ok": recomputed == claimed_objective,
            "recomputed": recomputed, "claimed": claimed_objective}


# ----------------------------------------------------------------------------- enumeration helper
def _enumerate_feasible(model, cap=2_000_000):
    """Yield every feasible integer point in the box. Guarded by `cap` (raises if exceeded)."""
    names = list(model["vars"].keys())
    ranges = [range(model["vars"][n][0], model["vars"][n][1] + 1) for n in names]
    size = 1
    for r in ranges:
        size *= len(r)
        if size > cap:
            raise ValueError(f"enumeration space {size}>{cap}; too large for EXHAUSTIVE cert")
    cons = model.get("constraints", [])
    for combo in itertools.product(*ranges):
        sol = dict(zip(names, combo))
        if all(_op_holds(_lhs(c["coeffs"], sol), c["op"], c["rhs"]) for c in cons):
            yield sol


def _objval(model, sol):
    obj = model["objective"]
    return _lhs(obj["coeffs"], sol) + obj.get("constant", 0)


# ----------------------------------------------------------------------------- (3) optimality
def optimality_certificate(model, solution, claimed_objective, certificate):
    """Certify optimality ONLY via a real proof. `certificate` is a dict with a "type":

      {"type": "exhaustive"}                          gate enumerates the feasible space
      {"type": "lp_dual", "y": {label: int, ...}}     gate verifies dual feasibility + bound
      {"type": "independent", "value": int,           a feasible witness achieving `value`; the gate
                              "witness": {var:val}}    ENUMERATES to CONFIRM `value` is truly optimal
                                                       (a witness alone proves only achievability/a BOUND,
                                                        not optimality -- CRUCIBLE-v2 soundness fix). If the
                                                        space is too large to enumerate -> NOT certified
                                                        (supply lp_dual/exhaustive instead).
      {"type": "solver_bound_gap0", "best_bound": x}   solver self-report (weakest tier)
    """
    obj = model.get("objective")
    if obj is None:
        return {"certificate": "OPTIMALITY", "optimal": False,
                "reason": "no objective -> nothing to optimize"}
    sense = obj["sense"]
    ctype = certificate.get("type")
    out = {"certificate": "OPTIMALITY", "type": ctype, "sense": sense}

    if ctype == "exhaustive":
        best = None
        for sol in _enumerate_feasible(model):
            val = _objval(model, sol)
            if best is None or (val > best if sense == "max" else val < best):
                best = val
        out["true_optimum"] = best
        out["optimal"] = (best == claimed_objective)
        out["independence"] = "FULL (gate enumerated the feasible space; solver not trusted)"
        if not out["optimal"]:
            out["reason"] = f"claimed {claimed_objective} != true optimum {best}"
        return out

    if ctype == "lp_dual":
        out.update(_verify_lp_dual(model, claimed_objective, certificate.get("y", {})))
        out["independence"] = "FULL (LP weak duality, dual vector verified by exact arithmetic)"
        return out

    if ctype == "independent":
        val = certificate.get("value")
        wit = certificate.get("witness", {})
        feas = feasibility_certificate(model, wit)["feasible"] if wit else None
        wit_obj = _objval(model, wit) if wit else None
        # achievability: the witness must be feasible and actually achieve the claimed value.
        achieves = (val == claimed_objective) and (feas is True) and (wit_obj == val)
        out.update({"independent_optimum": val, "witness_feasible": feas, "witness_objective": wit_obj})
        if not achieves:
            out["optimal"] = False
            out["reason"] = "independent value/witness did not corroborate the claim (achievability)"
            return out
        # SOUNDNESS FIX (CRUCIBLE-v2 KILL, 2026-06-21): a feasible witness proves `val` is ACHIEVABLE
        # (a bound) -- it does NOT prove `val` is the OPTIMUM. The prior code certified optimal on
        # achievability alone, so ANY suboptimal feasible point could be certified optimal via this cert
        # type (e.g. max x on [0,5]: claiming x=3 optimal was ACCEPTED). The gate must INDEPENDENTLY
        # CONFIRM optimality. It does so by enumerating the feasible space (foreign to the caller's
        # claimed method); if the space is too large to enumerate AND no dual/upper-bound proof is
        # supplied, the claimed optimum is UNVERIFIABLE -> the witness is a BOUND, not a proof of optimality.
        try:
            true_best = None
            for s in _enumerate_feasible(model):
                vv = _objval(model, s)
                if true_best is None or (vv > true_best if sense == "max" else vv < true_best):
                    true_best = vv
            confirmed = (true_best == val)
            out["gate_confirmed_optimum"] = true_best
            out["optimal"] = bool(confirmed)
            out["independence"] = ("FULL (gate ENUMERATED the feasible space to CONFIRM the claimed "
                                   "optimum; witness corroborates -- caller's optimality claim not trusted)")
            if not confirmed:
                out["reason"] = (f"claimed independent optimum {val} is NOT the true optimum {true_best} "
                                 "(a better feasible point exists) -> NOT optimal")
        except ValueError:
            out["optimal"] = False
            out["independence"] = ("NONE-for-optimality (feasible space too large to enumerate; the "
                                   "caller-claimed optimum is UNVERIFIED -- the feasible witness proves "
                                   "achievability/a BOUND only, not optimality)")
            out["reason"] = ("independent optimality claim not gate-verifiable here -> reported as a BOUND, "
                             "not optimal. Supply an lp_dual or exhaustive certificate to prove optimality.")
        return out

    if ctype == "solver_bound_gap0":
        bb = certificate.get("best_bound")
        gap0 = (bb == claimed_objective)
        out.update({"best_bound": bb, "gap": (None if bb is None else bb - claimed_objective),
                    "optimal": bool(gap0),
                    "independence": "PARTIAL (feasibility+objective re-checked independently; "
                                    "the BOUND NUMBER is the solver's self-report)"})
        if not gap0:
            out["reason"] = "best_bound != objective -> NONZERO GAP -> not optimal, relabel bound"
        return out

    out.update({"optimal": False, "reason": f"unknown / missing optimality certificate type {ctype!r}"})
    return out


def _verify_lp_dual(model, primal_obj, y):
    """Verify a dual-feasible vector proves optimality via LP weak duality, exact integers.

    Standardize MAX c'x s.t. Gx<=h (each constraint expanded to <= form; >= negated; ==
    split; box bounds folded in). Dual feasibility: y>=0 and G'y == c. Then h'y is an upper
    bound on c'x (weak duality). y meets the primal iff h'y == primal_obj -> proven optimal.
    For MIN we flip via min c'x = -max(-c'x).
    """
    obj = model["objective"]
    sense = obj["sense"]
    # objective coeff vector c (as MAX); for MIN, negate so we always bound a MAX
    flip = -1 if sense == "min" else 1
    cvec = {v: flip * obj["coeffs"].get(v, 0) for v in model["vars"]}

    rows = []   # each: (coeffs dict, h)  in <= form, with a label
    for con in model.get("constraints", []):
        if con["op"] == "<=":
            rows.append((dict(con["coeffs"]), con["rhs"], con.get("label")))
        elif con["op"] == ">=":
            rows.append(({v: -a for v, a in con["coeffs"].items()}, -con["rhs"], con.get("label")))
        else:  # ==  -> two rows
            rows.append((dict(con["coeffs"]), con["rhs"], con.get("label") and con["label"] + "+"))
            rows.append(({v: -a for v, a in con["coeffs"].items()}, -con["rhs"],
                         con.get("label") and con["label"] + "-"))
    # box bounds as rows: x<=hi, -x<=-lo
    for v, (lo, hi) in model["vars"].items():
        rows.append(({v: 1}, hi, f"ub_{v}"))
        rows.append(({v: -1}, -lo, f"lb_{v}"))

    # y indexed by row position; accept y keyed by label OR by index
    yv = []
    for i, (_, _, lbl) in enumerate(rows):
        val = None
        if isinstance(y, dict):
            if lbl in y:
                val = y[lbl]
            elif i in y:
                val = y[i]
            elif str(i) in y:
                val = y[str(i)]
        yv.append(val if val is not None else 0)

    # dual feasibility: y >= 0
    if any(v < 0 for v in yv):
        return {"optimal": False, "reason": "dual infeasible: some y < 0"}
    # G'y == c  (exact)
    gy = {v: 0 for v in model["vars"]}
    for (coeffs, _h, _l), yi in zip(rows, yv):
        for v, a in coeffs.items():
            gy[v] += a * yi
    if any(gy.get(v, 0) != cvec.get(v, 0) for v in model["vars"]):
        return {"optimal": False, "reason": "dual infeasible: G'y != c",
                "Gty": gy, "c": cvec}
    # h'y bounds MAX of cvec'x = max of (flip * coeffs'x), which EXCLUDES the objective
    # constant. The primal objective carries that constant, so fold it into the bound with
    # the same MIN-sense flip the cvec used: bound on (flip*obj) = h'y + flip*constant.
    constant = obj.get("constant", 0)
    bound = sum(h * yi for (_, h, _l), yi in zip(rows, yv)) + flip * constant  # bound on flip*obj
    primal_as_max = flip * primal_obj
    if bound == primal_as_max:
        return {"optimal": True, "dual_bound(as_max)": bound, "primal(as_max)": primal_as_max}
    return {"optimal": False, "reason": "dual bound does not meet primal (gap>0)",
            "dual_bound(as_max)": bound, "primal(as_max)": primal_as_max,
            "gap(as_max)": bound - primal_as_max}


# ----------------------------------------------------------------------------- (4) infeasibility
def infeasibility_certificate(model, iis_labels):
    """Independently PROVE "no solution exists" via an IIS (irreducible infeasible subset).

    The claim: the constraints named in `iis_labels` are JOINTLY infeasible over the var
    domains. The gate confirms by enumerating the box and checking NO point satisfies that
    subset. A satisfiable subset -> the "proof" is bogus -> REJECT. Also sanity-checks that
    the FULL model is infeasible (a stronger statement than the subset, but the subset is
    what makes it IRREDUCIBLE / a real certificate).
    """
    cons = model.get("constraints", [])
    by_label = {c.get("label", f"c{i}"): c for i, c in enumerate(cons)}
    subset = [by_label[l] for l in iis_labels if l in by_label]
    if len(subset) != len(iis_labels):
        return {"certificate": "INFEASIBILITY", "proven": False,
                "reason": "some IIS labels not found in model"}
    names = list(model["vars"].keys())
    ranges = [range(model["vars"][n][0], model["vars"][n][1] + 1) for n in names]
    sub_feasible_pt = None
    for combo in itertools.product(*ranges):
        sol = dict(zip(names, combo))
        if all(_op_holds(_lhs(c["coeffs"], sol), c["op"], c["rhs"]) for c in subset):
            sub_feasible_pt = sol
            break
    if sub_feasible_pt is not None:
        return {"certificate": "INFEASIBILITY", "proven": False,
                "reason": "named IIS subset is SATISFIABLE -> not an infeasibility proof",
                "satisfying_point": sub_feasible_pt}
    # irreducibility check (best-effort): dropping any one constraint should make it SAT
    irreducible = True
    for drop in range(len(subset)):
        reduced = [c for j, c in enumerate(subset) if j != drop]
        sat = any(all(_op_holds(_lhs(c["coeffs"], dict(zip(names, combo))), c["op"], c["rhs"])
                      for c in reduced)
                  for combo in itertools.product(*ranges))
        if not sat:
            irreducible = False  # subset minus one is still infeasible -> not minimal
            break
    return {"certificate": "INFEASIBILITY", "proven": True, "iis": list(iis_labels),
            "irreducible": irreducible,
            "independence": "FULL (gate enumerated the box; the named subset has no solution)"}


# ----------------------------------------------------------------------------- top-level verdict
def certify(model, claim):
    """One-call gate. `claim` is the solver's SELF-REPORT to be independently judged:
       {"status": "OPTIMAL"|"FEASIBLE"|"INFEASIBLE",
        "solution": {var:val}, "objective": int,
        "optimality_certificate": {...},        # required to UPGRADE to 'optimal'
        "iis": [labels]}                          # required for an INFEASIBLE claim
    Returns the GATE'S verdict (never the solver's), with every certificate attached.
    """
    status = claim.get("status")
    result = {"weapon": "OPTIMA", "solver_claimed_status": status,
              "model_caveat": "certificate covers the FORMAL MODEL only; modeling is kappa<1 "
                              "(cross-model-reviewed separately) -- 'optimal FOR THIS MODEL'."}

    # STATUS GUARD: only adjudicate a recognized self-reported status. A missing/unknown
    # status (incl. None) must NEVER fall through to certification -> ABSTAIN, never accept.
    if status not in ("OPTIMAL", "FEASIBLE", "INFEASIBLE"):
        result["verdict"] = "ABSTAIN_unknown_status"
        result["abstain_reason"] = (f"status {status!r} not in "
                                    "('OPTIMAL','FEASIBLE','INFEASIBLE') -> cannot adjudicate")
        return result

    if status == "INFEASIBLE":
        inf = infeasibility_certificate(model, claim.get("iis", []))
        result["infeasibility"] = inf
        result["verdict"] = "INFEASIBLE_PROVEN" if inf["proven"] else "REJECTED_no_infeasibility_proof"
        return result

    sol = claim.get("solution", {})
    feas = feasibility_certificate(model, sol)
    result["feasibility"] = feas
    if not feas["feasible"]:
        # the single most important reject: a solver "OPTIMAL" that is actually INFEASIBLE.
        result["verdict"] = "REJECTED_INFEASIBLE_SOLUTION"
        return result

    objc = objective_certificate(model, sol, claim.get("objective"))
    result["objective"] = objc
    if not objc["ok"]:
        result["verdict"] = "REJECTED_WRONG_OBJECTIVE"
        return result

    # feasible + objective verified. Is it OPTIMAL? earn it.
    if model.get("objective") is None:
        result["verdict"] = "FEASIBLE_VERIFIED (feasibility problem, no objective)"
        return result

    cert = claim.get("optimality_certificate")
    if cert is None:
        result["verdict"] = "FEASIBLE_WITH_GAP (no optimality certificate supplied)"
        result["optimality"] = {"optimal": False, "reason": "no certificate -> a bound, not optimal"}
        return result
    opt = optimality_certificate(model, sol, claim["objective"], cert)
    result["optimality"] = opt
    if opt["optimal"]:
        # CRUCIBLE-v2 LABEL-SOUNDNESS (2026-06-21, audit-surfaced): OPTIMAL_CERTIFIED must mean PROVEN.
        # The solver_bound_gap0 tier only checks best_bound==objective where best_bound is the SOLVER'S
        # UNVERIFIED self-report (a lying bound certifies a suboptimum), so it must NOT share the
        # OPTIMAL_CERTIFIED label with the proven tiers (exhaustive / lp_dual / enumeration-confirmed
        # independent). Emit a DISTINCT weaker verdict so a consumer cannot mistake assertion for proof.
        if opt.get("type") == "solver_bound_gap0":
            result["verdict"] = ("OPTIMAL_SOLVER_ASSERTED (gap=0 vs the solver's OWN unverified bound; "
                                 "NOT independently proven -- weakest tier; supply exhaustive/lp_dual/"
                                 "independent for a proof)")
        else:
            result["verdict"] = "OPTIMAL_CERTIFIED"
    else:
        result["verdict"] = "FEASIBLE_WITH_GAP (optimality NOT certified -> reported as a bound)"
    return result


# ----------------------------------------------------------------------------- self-tests (NON-WAIVABLE)
def _toy():
    """max 3x+2y s.t. x+y<=7, 0<=x,y<=10. True optimum 21 at (7,0). Integral LP (box+1 row)."""
    return {
        "vars": {"x": [0, 10], "y": [0, 10]},
        "constraints": [{"coeffs": {"x": 1, "y": 1}, "op": "<=", "rhs": 7, "label": "cap"}],
        "objective": {"sense": "max", "coeffs": {"x": 3, "y": 2}, "constant": 0},
    }


def _selftest():
    m = _toy()
    sol = {"x": 7, "y": 0}

    # (a) ACCEPT a known optimal with a valid gap=0 certificate (exhaustive).
    v = certify(m, {"status": "OPTIMAL", "solution": sol, "objective": 21,
                    "optimality_certificate": {"type": "exhaustive"}})
    assert v["verdict"] == "OPTIMAL_CERTIFIED", v
    assert v["optimality"]["true_optimum"] == 21, v

    # (a') ACCEPT via an INDEPENDENT LP dual certificate (weak duality, no solver trusted).
    # max 3x+2y, x+y<=7, x<=10. Dual y_cap on 'cap' (<=), y_ub on x<=10. Need G'y=c:
    #   x: y_cap + y_ub_x = 3 ; y: y_cap = 2 -> y_cap=2, y_ub_x=1. bound = 7*2 + 10*1 = 24?
    # That is an UPPER bound 24 (not tight). The TIGHT dual sets x at its used bound: optimum
    # 21 is met by exhaustive; LP relaxation optimum here is also 21 at (7,0) so a tight dual
    # exists -> use y_cap=2 and y on lb_y? Let's just prove the bound>=opt property holds and
    # the tight one certifies. We verify a TIGHT dual is accepted and a LOOSE one rejected:
    loose = certify(m, {"status": "OPTIMAL", "solution": sol, "objective": 21,
                        "optimality_certificate": {"type": "lp_dual",
                                                   "y": {"cap": 2, "ub_x": 1}}})
    assert loose["optimality"]["optimal"] is False, loose  # bound 24 != 21 -> correctly NOT a proof
    # the TIGHT dual (cap active y_cap=3; y at its lower bound lb_y=1) MEETS the primal ->
    # weak duality proves optimality WITHOUT ever consulting the solver.
    tight = certify(m, {"status": "OPTIMAL", "solution": sol, "objective": 21,
                        "optimality_certificate": {"type": "lp_dual", "y": {"cap": 3, "lb_y": 1}}})
    assert tight["verdict"] == "OPTIMAL_CERTIFIED", tight

    # (a'') CRUCIBLE REGRESSION — objective.constant fold in the lp_dual bound.
    # A constant shift of the objective preserves argmax -> the SAME tight dual must STILL
    # certify. Before the fix, _verify_lp_dual built the bound from rows+box only (never
    # folding objective['constant']) and compared to a primal that DID include the constant,
    # so any constant!=0 produced a phantom gap == the constant and falsely REJECTED a
    # correctly-certified shifted optimum. Freeze BOTH the base (const 0) and the +1000 shift.
    base_dual = certify(_toy(), {"status": "OPTIMAL", "solution": sol, "objective": 21,
                                 "optimality_certificate": {"type": "lp_dual",
                                                            "y": {"cap": 3, "lb_y": 1}}})
    assert base_dual["verdict"] == "OPTIMAL_CERTIFIED", base_dual
    m_shift = _toy(); m_shift["objective"]["constant"] = 1000  # opt 21 -> 1021
    shift_dual = certify(m_shift, {"status": "OPTIMAL", "solution": sol, "objective": 1021,
                                   "optimality_certificate": {"type": "lp_dual",
                                                              "y": {"cap": 3, "lb_y": 1}}})
    assert shift_dual["verdict"] == "OPTIMAL_CERTIFIED", shift_dual
    # SOUNDNESS rail for the fold: a genuinely sub-optimal point on the SAME shifted model
    # (true opt 1021) must STILL NOT be certified via lp_dual -> a bound, never optimal.
    shift_gap = certify(m_shift, {"status": "OPTIMAL", "solution": {"x": 6, "y": 0},
                                  "objective": 1018,
                                  "optimality_certificate": {"type": "lp_dual",
                                                             "y": {"cap": 3, "lb_y": 1}}})
    assert shift_gap["optimality"]["optimal"] is False, shift_gap
    assert shift_gap["verdict"].startswith("FEASIBLE_WITH_GAP"), shift_gap

    # (b) REJECT an "OPTIMAL" answer that is actually INFEASIBLE (inject a violation).
    bad_inf = certify(m, {"status": "OPTIMAL", "solution": {"x": 5, "y": 5}, "objective": 25,
                          "optimality_certificate": {"type": "exhaustive"}})
    assert bad_inf["verdict"] == "REJECTED_INFEASIBLE_SOLUTION", bad_inf  # x+y=10 > 7

    # (c) REJECT an "optimal" claim with a NONZERO GAP (relabel as a bound).
    gap = certify(m, {"status": "OPTIMAL", "solution": {"x": 6, "y": 0}, "objective": 18,
                      "optimality_certificate": {"type": "solver_bound_gap0", "best_bound": 21}})
    assert gap["verdict"].startswith("FEASIBLE_WITH_GAP"), gap  # 18 feasible but bound 21 != 18

    # (d) REJECT a WRONG objective value (feasible point, lied-about objective).
    wobj = certify(m, {"status": "OPTIMAL", "solution": {"x": 7, "y": 0}, "objective": 999,
                       "optimality_certificate": {"type": "exhaustive"}})
    assert wobj["verdict"] == "REJECTED_WRONG_OBJECTIVE", wobj

    # (e) no-certificate feasible -> a BOUND, never optimal.
    nob = certify(m, {"status": "OPTIMAL", "solution": {"x": 6, "y": 1}, "objective": 20})
    assert nob["verdict"].startswith("FEASIBLE_WITH_GAP"), nob

    # (f) INFEASIBILITY: a real IIS is PROVEN; a bogus (satisfiable) IIS is REJECTED.
    inf_model = {"vars": {"z": [0, 10]},
                 "constraints": [{"coeffs": {"z": 1}, "op": ">=", "rhs": 5, "label": "lo"},
                                 {"coeffs": {"z": 1}, "op": "<=", "rhs": 3, "label": "hi"}]}
    good_iis = certify(inf_model, {"status": "INFEASIBLE", "iis": ["lo", "hi"]})
    assert good_iis["verdict"] == "INFEASIBLE_PROVEN", good_iis
    # bogus: a single satisfiable constraint is NOT an infeasibility proof.
    bogus_iis = certify(inf_model, {"status": "INFEASIBLE", "iis": ["lo"]})
    assert bogus_iis["verdict"] == "REJECTED_no_infeasibility_proof", bogus_iis

    # (f') BUG-1 regression: an INCOMPLETE solution (missing var) is REJECTED cleanly, not crashed.
    incomplete = certify(m, {"status": "OPTIMAL", "solution": {"x": 7}, "objective": 21,
                             "optimality_certificate": {"type": "exhaustive"}})
    assert incomplete["verdict"] == "REJECTED_INFEASIBLE_SOLUTION", incomplete
    assert incomplete["feasibility"].get("incomplete") is True, incomplete
    # (f'') BUG-2 hardening: extra/unrecognized vars are NOTED (not silently ignored).
    extra = certify(m, {"status": "OPTIMAL", "solution": {"x": 7, "y": 0, "ghost": 999},
                        "objective": 21, "optimality_certificate": {"type": "exhaustive"}})
    assert extra["verdict"] == "OPTIMAL_CERTIFIED", extra
    assert extra["feasibility"]["notes"], extra  # the ghost var is recorded

    # (f''') CRUCIBLE REGRESSION — missing/unknown status must NEVER fall through to certify.
    # Before the fix, certify() only special-cased 'INFEASIBLE' and then certified ANY other
    # status value (including a MISSING status key / None) as a normal OPTIMAL claim -> a
    # false-accept (silent OPTIMAL_CERTIFIED on a claim that never asserted optimality).
    no_status = certify(m, {"solution": {"x": 7, "y": 0}, "objective": 21,
                            "optimality_certificate": {"type": "exhaustive"}})
    assert no_status["verdict"] != "OPTIMAL_CERTIFIED", no_status
    assert no_status["verdict"].startswith("ABSTAIN") or no_status["verdict"].startswith("REJECTED"), no_status
    none_status = certify(m, {"status": None, "solution": {"x": 7, "y": 0}, "objective": 21,
                              "optimality_certificate": {"type": "exhaustive"}})
    assert none_status["verdict"] != "OPTIMAL_CERTIFIED", none_status
    bogus_status = certify(m, {"status": "DEFINITELY_OPTIMAL_TRUST_ME",
                               "solution": {"x": 7, "y": 0}, "objective": 21,
                               "optimality_certificate": {"type": "exhaustive"}})
    assert bogus_status["verdict"] != "OPTIMAL_CERTIFIED", bogus_status
    # PRESERVE: the guard must NOT reject the three VALID statuses — they adjudicate normally.
    for st_model, st_claim, want in [
        (m, {"status": "OPTIMAL", "solution": {"x": 7, "y": 0}, "objective": 21,
             "optimality_certificate": {"type": "exhaustive"}}, "OPTIMAL_CERTIFIED"),
        (_toy(), {"status": "FEASIBLE", "solution": {"x": 6, "y": 1}, "objective": 20}, "FEASIBLE_WITH_GAP"),
    ]:
        gv = certify(st_model, st_claim)["verdict"]
        assert gv == want or gv.startswith(want), (st_claim, gv)

    # (g) INDEPENDENT-optimum certificate accepted; a lying independent value rejected.
    ind_ok = certify(m, {"status": "OPTIMAL", "solution": sol, "objective": 21,
                         "optimality_certificate": {"type": "independent", "value": 21,
                                                    "witness": {"x": 7, "y": 0}}})
    assert ind_ok["verdict"] == "OPTIMAL_CERTIFIED", ind_ok
    ind_bad = certify(m, {"status": "OPTIMAL", "solution": sol, "objective": 21,
                          "optimality_certificate": {"type": "independent", "value": 21,
                                                     "witness": {"x": 5, "y": 5}}})  # infeasible witness
    assert ind_bad["optimality"]["optimal"] is False, ind_bad

    # (g') CRUCIBLE-v2 REGRESSION (2026-06-21 KILL): a SUBOPTIMAL feasible witness claimed OPTIMAL via
    # the 'independent' cert must NOT be certified optimal. Before the fix the gate verified only
    # ACHIEVABILITY (the witness reaches the claimed value) and TRUSTED the caller's claim that the value
    # was THE optimum, so ANY feasible point could be certified optimal (found by an independent scipy
    # LP-relaxation differential hunt: e.g. claiming 18 optimal for the toy whose true optimum is 21).
    # The gate now ENUMERATES the feasible space to CONFIRM the claimed optimum.
    ind_subopt = certify(m, {"status": "OPTIMAL", "solution": {"x": 6, "y": 0}, "objective": 18,
                             "optimality_certificate": {"type": "independent", "value": 18,
                                                        "witness": {"x": 6, "y": 0}}})
    assert ind_subopt["verdict"] != "OPTIMAL_CERTIFIED", ind_subopt          # was OPTIMAL_CERTIFIED (the KILL)
    assert ind_subopt["verdict"].startswith("FEASIBLE_WITH_GAP"), ind_subopt
    assert ind_subopt["optimality"].get("gate_confirmed_optimum") == 21, ind_subopt

    # (g'') CRUCIBLE-v2 LABEL-SOUNDNESS REGRESSION (audit-surfaced): a solver_bound_gap0 cert trusts the
    # solver's UNVERIFIED best_bound, so it must NEVER earn the proven-tier label OPTIMAL_CERTIFIED -- a
    # lying bound (best_bound==objective on a suboptimum) would otherwise read as proof. Demoted to
    # OPTIMAL_SOLVER_ASSERTED. (max x on [0,5]: true optimum 5; claim 3 with best_bound 3.)
    mx = {"vars": {"x": [0, 5]}, "constraints": [], "objective": {"sense": "max", "coeffs": {"x": 1}, "constant": 0}}
    sba = certify(mx, {"status": "OPTIMAL", "solution": {"x": 3}, "objective": 3,
                       "optimality_certificate": {"type": "solver_bound_gap0", "best_bound": 3}})
    assert sba["verdict"] != "OPTIMAL_CERTIFIED", sba                          # was OPTIMAL_CERTIFIED on a lie
    assert sba["verdict"].startswith("OPTIMAL_SOLVER_ASSERTED"), sba
    # even at the TRUE optimum, solver_bound_gap0 is asserted-not-proven (honest weakest-tier label).
    sba_true = certify(mx, {"status": "OPTIMAL", "solution": {"x": 5}, "objective": 5,
                            "optimality_certificate": {"type": "solver_bound_gap0", "best_bound": 5}})
    assert sba_true["verdict"].startswith("OPTIMAL_SOLVER_ASSERTED"), sba_true

    print("OPTIMA-GATE selftest: PASS  (accept gap=0 cert; reject infeasible-'optimal'; "
          "reject nonzero-gap; reject wrong-objective; no-cert->bound; IIS proven & bogus-IIS "
          "rejected; independent-cert accept & lying-witness reject; loose-dual not a proof)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: optima_gate.py selftest")
