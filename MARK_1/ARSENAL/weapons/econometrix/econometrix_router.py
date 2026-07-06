#!/usr/bin/env python3
"""ECONOMETRIX router — given an economics/finance task, choose which sub-weapons fire.

Cloned from socius_router.py (the mixed-kappa "be a chooser" shape). It reads the task, classifies its
claims by checkability (kappa), draws the kappa>0 sub-weapons whose preconditions hold, and routes the
kappa=0 residue (forecasts, "should" questions, market direction) to ARMOR (ground or abstain). It does
NOT do the analysis — it decides which checks apply and labels every routed piece with its kappa so
nothing kappa=0 is ever presented as machine-verified.

THE GUARDED-KAPPA RULE (C14, non-waivable): an in-sample / single-split backtest score is GAMEABLE ->
it does NOT raise kappa to 1. A market-edge claim routes to E-BACKTEST whose verdict is walk-forward OOS
+ Deflated Sharpe + costs, never the in-sample number. "Will it go up / should we" -> kappa=0 -> armor.

Intake is a structured task descriptor (booleans). In live use these come from an armor-side reading of
the task; here they are explicit so the routing logic is itself testable.
"""
import sys, json

# precondition -> (sub-weapon, kappa, track, rationale)
RULES = [
    ("market_edge_with_price_data",     "E-BACKTEST",   0.4, "weapon",
     "A trading/market-edge claim with price data is stress-tested OUT-OF-SAMPLE (walk-forward) + "
     "Deflated Sharpe (multiple-testing + non-normality) + net of costs. GUARDED kappa: the in-sample "
     "score is GAMEABLE and is NEVER the verdict (C14)."),
    ("causal_claim_did",                "E-CAUSAL",     0.5, "weapon",
     "A difference-in-differences claim: run the pre-trends/placebo test (testable) + a sensitivity "
     "number for the untestable post-period parallel-trends assumption."),
    ("causal_claim_rdd",                "E-CAUSAL",     0.5, "weapon",
     "A regression-discontinuity claim: run the McCrary density (manipulation) test + bandwidth "
     "sensitivity."),
    ("causal_claim_iv",                 "E-CAUSAL",     0.5, "weapon",
     "An instrumental-variables claim: check the first-stage F (weak-instrument / Stock-Yogo); the "
     "exclusion restriction is untestable -> report it as an assumption."),
    ("causal_claim_observational",      "E-CAUSAL",     0.5, "weapon",
     "A causal claim from observational data with no design: report a confounding-sensitivity number "
     "(E-value / Oster delta); never a bare 'X caused Y'."),
    ("finding_rests_on_analytic_choices", "E-ROBUST",   1.0, "weapon",
     "The result depends on defensible-but-arbitrary analytic choices; enumerate the full "
     "specification multiverse (reused socius/multiverse_verify)."),
    ("has_open_data_and_code",          "E-REPRO",      1.0, "weapon",
     "A published economic statistic with open data+code can be re-run and checked within tolerance "
     "(reused socius/repro_verify)."),
    ("is_forecast_or_normative_or_direction", "ARMOR",  0.0, "armor",
     "Forecast the future / 'should' policy / market direction = kappa=0 (the future is unseen, the "
     "normative has no machine truth). GROUND every empirical sub-claim or ABSTAIN; never fabricate a "
     "forecast. A backtest is not a forecast."),
]


def route(task):
    """task: dict of boolean preconditions. Returns the routing plan."""
    fired, seen = [], set()
    for key, weapon, kappa, track, why in RULES:
        if task.get(key):
            if weapon in seen:
                for f in fired:
                    if f["sub_weapon"] == weapon:
                        f["triggers"].append(key)
                continue
            seen.add(weapon)
            fired.append({"sub_weapon": weapon, "kappa": kappa, "track": track,
                          "triggers": [key], "rationale": why})

    has_any_weapon = any(f["track"] == "weapon" for f in fired)
    plan = {
        "fired_sub_weapons": fired,
        "weapon_track": [f for f in fired if f["track"] == "weapon"],
        "armor_track": [f for f in fired if f["track"] == "armor"],
        "kappa0_armor_only": bool(task.get("is_forecast_or_normative_or_direction") and not has_any_weapon),
    }
    if not fired:
        plan["note"] = "No precondition matched — under-specified task; abstain and ask for the data/claim."
    elif not has_any_weapon:
        plan["note"] = ("Pure forecast / normative / market-direction with no checkable empirical "
                        "claim: kappa=0 -> ARMOR ONLY (ground every sub-claim or abstain). ECONOMETRIX "
                        "draws no frozen verifier; it cannot predict the future or manufacture truth.")
    else:
        plan["note"] = ("ECONOMETRIX raises trustworthiness (OOS survival + identification diagnostics); "
                        "it does NOT predict the future or certify truth. An in-sample/backtest score is "
                        "NEVER the verdict. Findings that DIE under stress are the primary valuable output.")
    return plan


# ------------------------------- selftest ---------------------------------- #
def _selftest():
    # canonical full case: a market-edge claim WITH a causal DiD angle, open data+code, analytic
    # choices, AND a forecast rider -> all weapons fire, forecast goes to armor.
    t = {"market_edge_with_price_data": True, "causal_claim_did": True,
         "finding_rests_on_analytic_choices": True, "has_open_data_and_code": True,
         "is_forecast_or_normative_or_direction": True}
    plan = route(t)
    names = {f["sub_weapon"] for f in plan["fired_sub_weapons"]}
    assert names == {"E-BACKTEST", "E-CAUSAL", "E-ROBUST", "E-REPRO", "ARMOR"}, names
    assert plan["kappa0_armor_only"] is False, plan  # weapons fired, so not armor-only
    # the forecast piece is on the ARMOR track with kappa 0
    armor = plan["armor_track"]
    assert len(armor) == 1 and armor[0]["kappa"] == 0.0, armor

    # E-CAUSAL dedupes across DiD + RDD + IV triggers (one sub-weapon, all triggers recorded)
    multi = route({"causal_claim_did": True, "causal_claim_rdd": True, "causal_claim_iv": True})
    ec = [f for f in multi["fired_sub_weapons"] if f["sub_weapon"] == "E-CAUSAL"][0]
    assert set(ec["triggers"]) == {"causal_claim_did", "causal_claim_rdd", "causal_claim_iv"}, ec

    # PURE forecast -> ARMOR ONLY, no weapon (the C14/kappa=0 guard)
    fc = route({"is_forecast_or_normative_or_direction": True})
    assert fc["kappa0_armor_only"] is True and fc["weapon_track"] == [], fc

    # a market edge alone -> only E-BACKTEST, guarded kappa 0.4
    edge = route({"market_edge_with_price_data": True})
    fired = edge["fired_sub_weapons"]
    assert len(fired) == 1 and fired[0]["sub_weapon"] == "E-BACKTEST" and fired[0]["kappa"] == 0.4, edge

    print("econometrix_router selftest: PASS")
    print("  full case fires E-BACKTEST/E-CAUSAL/E-ROBUST/E-REPRO + forecast->ARMOR; "
          "pure forecast -> ARMOR ONLY; market-edge -> guarded-kappa E-BACKTEST")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: econometrix_router.py selftest | <task.json>")
