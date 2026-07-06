#!/usr/bin/env python3
"""SYMBOLICA router — given a task, decide WHICH mode fires (or route to armor).

Mirrors socius/psymetrix/proofsmith routers: classify the task by whether a cheap
EXACT cross-method agreement check exists (kappa), draw the matching mode, and route
the kappa=0 residue (modeling / interpretation / "what does it MEAN") to ARMOR. It
decides routing; it does not run the math. Single-engine answers are never shipped.

The decisive question is the kappa-gate: *is there a closed form / identity / special
value whose correctness >=2 INDEPENDENT methods can agree on?* If yes -> a weapon mode.
If the object has no closed form (only numeric-with-error-bars) -> report numeric +
error bars, do NOT fake exactness. If it is interpretation -> armor.
"""
import sys, json

# precondition key -> (mode, kappa, track, rationale)
RULES = [
    ("is_definite_integral_or_ode_with_closed_form", "CLOSED-FORM", 0.9, "weapon",
     "A definite integral/ODE with a plausible closed form: symbolic antiderivative "
     "vs mpmath-quad vs scipy-quad must agree (>=2 independent families)."),
    ("is_equality_or_identity_to_check", "IDENTITY-PROVE", 0.9, "weapon",
     "An equality/identity: symbolic simplify->0 AND K-point high-precision numeric "
     "agreement (both required); series expansion as the diversified 3rd method."),
    ("is_infinite_sum_with_closed_form", "SERIES", 0.9, "weapon",
     "An infinite sum: CONVERGENCE is checked first (symbolic + numeric partial sums); "
     "only then is the claimed closed form checked against independent summation."),
    ("is_known_special_value", "SPECIAL-VALUE", 0.9, "weapon",
     "A known special value (zeta(2)=pi^2/6, Gaussian integral): REPRODUCE vs a fetched "
     "reference and cross-check numerically. Labeled reproduction, not an original result."),
    ("has_no_closed_form_numeric_only", "NUMERIC-FALLBACK", 0.0, "armor",
     "No closed form exists -> report a high-precision numeric value WITH explicit error "
     "bars. Never dress a numeric estimate as exact (the W7 fallback)."),
    ("is_modeling_or_interpretation", "ARMOR", 0.0, "armor",
     "What an integral/result MEANS physically, or which model to use, is kappa=0 -> "
     "ground in a fetched source or ABSTAIN. The agreement gate certifies arithmetic, "
     "never interpretation."),
]

CEILING = ("SYMBOLICA ships only what >=2 INDEPENDENT methods agree on (symbolic + "
           "high-precision numeric, a 3rd diversified method on load-bearing cases). "
           "It certifies 'verified to D digits' (empirical-strong) or 'symbolically "
           "simplified to 0' (still NOT kernel-grade — PROOFSMITH is). A single-engine "
           "answer is a CLAIM, not a result. No closed form -> numeric WITH error bars.")


def route(task):
    fired, seen = [], set()
    for key, mode, kappa, track, why in RULES:
        if task.get(key):
            if mode in seen:
                continue
            seen.add(mode)
            fired.append({"mode": mode, "kappa": kappa, "track": track,
                          "trigger": key, "rationale": why})
    plan = {
        "fired_modes": fired,
        "weapon_track": [f for f in fired if f["track"] == "weapon"],
        "armor_track": [f for f in fired if f["track"] == "armor"],
        "ceiling": CEILING,
    }
    if not fired:
        plan["note"] = ("No precondition matched — under-specified. Abstain and ask for "
                        "the exact integral/identity/sum/value to check.")
    elif not plan["weapon_track"]:
        plan["note"] = ("kappa=0: no exact closed form to cross-check -> ARMOR "
                        "(numeric-with-error-bars or ground+abstain). SYMBOLICA does NOT "
                        "manufacture an exact answer where none exists.")
    else:
        plan["note"] = ("Weapon mode(s) fire: every shipped value carries its cross-method "
                        "agreement (which methods, how many digits, how many points). "
                        "Load-bearing results add a methodologically-different 3rd check.")
    return plan


def _selftest():
    # a definite integral with a closed form -> CLOSED-FORM weapon
    assert route({"is_definite_integral_or_ode_with_closed_form": True})["weapon_track"][0]["mode"] == "CLOSED-FORM"
    # an identity -> IDENTITY-PROVE
    assert route({"is_equality_or_identity_to_check": True})["weapon_track"][0]["mode"] == "IDENTITY-PROVE"
    # an infinite sum -> SERIES (convergence-gated)
    assert route({"is_infinite_sum_with_closed_form": True})["weapon_track"][0]["mode"] == "SERIES"
    # a known special value -> SPECIAL-VALUE (reproduction)
    assert route({"is_known_special_value": True})["weapon_track"][0]["mode"] == "SPECIAL-VALUE"
    # NO closed form -> armor (numeric + error bars), NOT a weapon
    nf = route({"has_no_closed_form_numeric_only": True})
    assert nf["weapon_track"] == [] and nf["armor_track"][0]["mode"] == "NUMERIC-FALLBACK", nf
    # interpretation -> armor only
    interp = route({"is_modeling_or_interpretation": True})
    assert interp["weapon_track"] == [] and interp["armor_track"][0]["mode"] == "ARMOR", interp
    # empty task -> abstain
    assert route({})["fired_modes"] == []
    # ceiling always present, naming the single-engine doctrine
    assert "CLAIM, not a result" in route({})["ceiling"]
    print("symbolica_router selftest: PASS (integral->CLOSED-FORM; identity->IDENTITY-PROVE; "
          "sum->SERIES; special-value->reproduction; no-closed-form->armor numeric+error-bars; "
          "interpretation->armor; empty->abstain)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: symbolica_router.py selftest | <task.json>")
