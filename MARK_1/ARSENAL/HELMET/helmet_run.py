#!/usr/bin/env python3
"""helmet_run — the END-TO-END auto-dispatch pipeline (closes HELMET gap #2).

Before this, the helmet was "a routing brain (provost.py) + separate weapons, not one closed loop."
helmet_run closes the loop: a descriptor -> provost.route() -> a routing VERDICT -> for the WEAPON path,
AUTO-DISPATCH to the matched weapon's REAL gate and run it -> one unified delivery.

  verdict WEAPON           -> dispatch to the matched weapon adapter (runs the real kappa=1 gate)
  verdict GROUND_AND_ANSWER-> instruct: fetch an authoritative source and answer (kappa=0 fact)
  verdict ARMOR_ABSTAIN    -> instruct: grounded analysis + honest abstention (kappa=0 normative/open/proxy)

Weapon adapters call the ACTUAL gate (no re-implementation). Adapters are wired for a representative set;
an unwired weapon returns the routing + "adapter not yet wired" (honest, not a silent pass)."""
import sys, os
_H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _H)
import provost

_W = os.path.dirname(_H) + "/weapons"
for d in ("optima", "enclose", "psymetrix"):
    sys.path.insert(0, f"{_W}/{d}")
sys.path.insert(0, os.path.dirname(_H) + "/cap_set")


def _derive_verdict(plan):
    if plan["kappa_effective"] > 0:
        return "WEAPON"
    if plan["must_end_in_abstention_if_unverifiable"]:
        return "ARMOR_ABSTAIN"
    return "GROUND_AND_ANSWER"


# ---- weapon adapters: each runs the REAL gate on its weapon-specific input ------------------- #
def _adapt_optima(win):
    import optima_gate
    return optima_gate.certify(win["model"], win["claim"])


def _adapt_enclose(win):
    import enclose_gate
    return enclose_gate.gate(win["problem"], win["claim"])


def _adapt_psymetrix(win):
    import forensics_verify as fv          # GRIM exact-arithmetic slice
    return fv.grim(win["mean"], win["n"], win.get("items", 1))


def _adapt_capset(win):
    import capset_verify as cv             # Frontier Construction Engine — cap-set validity (no-3-AP)
    valid, reason = cv.is_capset([tuple(p) for p in win["points"]])
    return {"weapon": "FRONTIER/capset", "valid_capset": valid, "reason": reason, "size": len(win["points"])}


WEAPON_ADAPTERS = {
    "CS_ENG_OR": ("OPTIMA", _adapt_optima),
    "NAT_SCI": ("ENCLOSE/SYMBOLICA", _adapt_enclose),     # numeric containment -> ENCLOSE
    "QUANT_PSYCH": ("PSYMETRIX", _adapt_psymetrix),       # GRIM exact-arithmetic forensics
    "MATH_TCS": ("FRONTIER", _adapt_capset),              # extremal-object construction (cap-set)
}


def helmet_run(descriptor, weapon_input=None):
    """descriptor: the provost intake descriptor. weapon_input: weapon-specific gate input (for the
    WEAPON path). Returns a unified result: the routing plan, the verdict, and (WEAPON) the gate output."""
    plan = provost.route(descriptor)
    verdict = _derive_verdict(plan)
    out = {"verdict": verdict, "scale": plan["scale"], "kappa_effective": plan["kappa_effective"],
           "convened": [d["department"] for d in plan["convened_departments"]],
           "integrity_flags": plan["integrity_flags"]}

    if verdict == "WEAPON":
        depts = [d["department"] for d in plan["convened_departments"]]
        wired = next((dk for dk in depts if dk in WEAPON_ADAPTERS), None)
        if wired is None:
            out["dispatch"] = {"status": "NO_ADAPTER",
                               "note": f"weapon path for {depts} — no adapter wired yet (routing delivered, "
                                       "gate not auto-run). Wire an adapter to close the loop for this dept."}
        elif weapon_input is None:
            wname = WEAPON_ADAPTERS[wired][0]
            out["dispatch"] = {"status": "AWAIT_INPUT", "weapon": wname,
                               "note": f"routed to {wname}; supply weapon_input to auto-run its gate."}
        else:
            wname, fn = WEAPON_ADAPTERS[wired]
            try:
                gate_out = fn(weapon_input)
                out["dispatch"] = {"status": "RAN", "weapon": wname, "gate_result": gate_out}
            except Exception as e:
                out["dispatch"] = {"status": "GATE_ERROR", "weapon": wname,
                                   "error": f"{type(e).__name__}: {e}"}
    elif verdict == "GROUND_AND_ANSWER":
        out["dispatch"] = {"status": "GROUND_AND_ANSWER",
                           "note": "kappa=0 settled fact -> fetch an authoritative source and ANSWER (do NOT abstain)."}
    else:  # ARMOR_ABSTAIN
        out["dispatch"] = {"status": "ARMOR_ABSTAIN",
                           "note": "kappa=0 normative/open/proxy -> grounded analysis + honest abstention on the verdict."}
    return out


def _selftest():
    # (1) WEAPON path, auto-dispatched to the REAL optima gate, end to end.
    desc = {"problem": "certify the optimum of this assignment LP", "domains": ["CS_ENG_OR"],
            "task_type": "construct", "kappa": 1.0, "triviality": "substantial", "stakes": "high"}
    model = {"vars": {"x": [0, 10], "y": [0, 10]},
             "constraints": [{"coeffs": {"x": 1, "y": 1}, "op": "<=", "rhs": 7, "label": "cap"}],
             "objective": {"sense": "max", "coeffs": {"x": 3, "y": 2}, "constant": 0}}
    claim = {"status": "OPTIMAL", "solution": {"x": 7, "y": 0}, "objective": 21,
             "optimality_certificate": {"type": "exhaustive"}}
    r1 = helmet_run(desc, {"model": model, "claim": claim})
    assert r1["verdict"] == "WEAPON" and r1["dispatch"]["status"] == "RAN", r1
    assert r1["dispatch"]["gate_result"]["verdict"] == "OPTIMAL_CERTIFIED", r1
    # and the loop REJECTS a bad claim through the real gate
    bad = helmet_run(desc, {"model": model, "claim": {"status": "OPTIMAL", "solution": {"x": 5, "y": 5},
                            "objective": 25, "optimality_certificate": {"type": "exhaustive"}}})
    assert bad["dispatch"]["gate_result"]["verdict"] == "REJECTED_INFEASIBLE_SOLUTION", bad

    # (2) WEAPON path, ENCLOSE gate, end to end (a verified integral enclosure).
    import mpmath
    pdesc = {"problem": "rigorously enclose an integral", "domains": ["NAT_SCI"], "task_type": "analyze",
             "kappa": 1.0, "triviality": "substantial", "stakes": "medium"}
    pin = {"problem": {"kind": "integral", "f": lambda x: 4 / (1 + x * x), "a": 0, "b": 1, "N": 2000},
           "claim": {"lo": "3.14", "hi": "3.15"}}
    r2 = helmet_run(pdesc, pin)
    assert r2["dispatch"]["status"] == "RAN" and r2["dispatch"]["gate_result"]["verdict"] == "ACCEPT", r2

    # (3) GROUND_AND_ANSWER path (a settled fact -> answer, not abstain).
    g = helmet_run({"problem": "capital of Australia?", "domains": ["HUMANITIES_LAW_POLICY"],
                    "task_type": "explain", "kappa": 0.0, "groundable": True, "triviality": "oneliner",
                    "stakes": "low"})
    assert g["verdict"] == "GROUND_AND_ANSWER" and g["scale"] == "DESK", g

    # (4) ARMOR_ABSTAIN path (a normative verdict -> abstain).
    a = helmet_run({"problem": "is it ethical to deploy autonomous weapons?",
                    "domains": ["HUMANITIES_LAW_POLICY"], "task_type": "decide", "kappa": 0.0,
                    "groundable": False, "triviality": "substantial", "stakes": "high"})
    assert a["verdict"] == "ARMOR_ABSTAIN", a

    # (5) WEAPON path with NO adapter wired -> honest NO_ADAPTER (routing delivered, not faked).
    na = helmet_run({"problem": "reproduce an empirical social-science finding", "domains": ["SOCIAL_SCI"],
                     "task_type": "measure", "kappa": 0.6, "has_data": True, "triviality": "substantial",
                     "stakes": "high"})
    assert na["verdict"] == "WEAPON" and na["dispatch"]["status"] == "NO_ADAPTER", na

    # (6) WEAPON->PSYMETRIX real GRIM gate: a GRIM-impossible mean is flagged inconsistent end to end.
    gr = helmet_run({"problem": "is this reported mean achievable?", "domains": ["QUANT_PSYCH"],
                     "task_type": "measure", "kappa": 1.0, "triviality": "bounded", "stakes": "medium"},
                    {"mean": "5.19", "n": 28})
    assert gr["dispatch"]["status"] == "RAN" and gr["dispatch"]["gate_result"]["consistent"] is False, gr

    # (7) WEAPON->FRONTIER real cap-set gate: a valid cap is confirmed; an AP-containing set is rejected.
    cap = helmet_run({"problem": "verify this cap set", "domains": ["MATH_TCS"], "task_type": "construct",
                      "kappa": 1.0, "triviality": "substantial", "stakes": "high"},
                     {"points": [(0, 0), (1, 0), (0, 1)]})
    assert cap["dispatch"]["gate_result"]["valid_capset"] is True, cap
    capbad = helmet_run({"problem": "verify this cap set", "domains": ["MATH_TCS"], "task_type": "construct",
                         "kappa": 1.0, "triviality": "substantial", "stakes": "high"},
                        {"points": [(0, 0), (1, 1), (2, 2)]})  # an AP mod 3 -> NOT a cap set
    assert capbad["dispatch"]["gate_result"]["valid_capset"] is False, capbad

    print("helmet_run selftest: PASS — end-to-end loop closed: descriptor -> provost route -> AUTO-DISPATCH")
    print("  (1) WEAPON->OPTIMA: ACCEPTs the optimum, REJECTs the infeasible claim")
    print("  (2) WEAPON->ENCLOSE: ACCEPTs a verified integral enclosure")
    print("  (3) GROUND_AND_ANSWER (DESK)  (4) ARMOR_ABSTAIN  (5) unwired dept -> honest NO_ADAPTER")
    print("  (6) WEAPON->PSYMETRIX: flags a GRIM-impossible mean   (7) WEAPON->FRONTIER: cap-set accept/reject")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: helmet_run.py selftest")
