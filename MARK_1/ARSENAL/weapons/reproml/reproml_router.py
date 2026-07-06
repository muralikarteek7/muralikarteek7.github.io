#!/usr/bin/env python3
"""REPRO-ML router — given an ML-eval task, choose which sub-weapons fire.

Reads a structured task descriptor and routes:
  reported metric + open artifacts  -> R-REPRO   (kappa~0.7)  recompute from artifacts
  train corpus + eval set provided  -> R-CONTAM  (kappa~0.8)  measure overlap rate
  two models' per-item correctness  -> R-SIGNIF  (kappa~0.9)  paired test + CI
  "is X best / SOTA / most capable" -> ARMOR     (kappa=0)    ground or ABSTAIN

Execute the kappa>0 verifiers, never vote. Label every routed piece with its kappa so
nothing kappa=0 is presented as machine-verified. A benchmark number is never a capability.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# precondition -> (sub-weapon, kappa, track, rationale)
RULES = [
    ("has_reported_metric_and_artifacts", "R-REPRO", 0.7, "weapon",
     "A reported metric with open predictions/labels can be recomputed within tolerance."),
    ("has_train_and_eval_sets", "R-CONTAM", 0.8, "weapon",
     "With both train corpus and eval set, measure n-gram + near-dup overlap as a rate."),
    ("compares_two_models_same_testset", "R-SIGNIF", 0.9, "weapon",
     "Two models on the same test set -> paired McNemar + bootstrap CI (Bonferroni for k)."),
    ("claims_best_or_sota_or_capable", "ARMOR", 0.0, "armor",
     "'X is best / SOTA / most capable' is kappa=0 (Goodhart, contamination, cherry-picking) "
     "-> ground or ABSTAIN. A benchmark number is NEVER a capability."),
]


def route(task):
    plan = []
    for key, weapon, kappa, track, why in RULES:
        if task.get(key):
            plan.append({"sub_weapon": weapon, "kappa": kappa, "track": track,
                         "rationale": why})
    routed_keys = {p["sub_weapon"] for p in plan}
    return {
        "weapon": "REPRO-ML", "task": task, "plan": plan,
        "fires_weapons": sorted(k for k in routed_keys if k != "ARMOR"),
        "routes_to_armor": "ARMOR" in routed_keys,
        "note": "Execute kappa>0 verifiers (never vote). kappa=0 capability/SOTA claims -> armor "
                "(ground or abstain). Contamination is a measured rate, not 'clean'; significance "
                "carries CIs + Bonferroni; reproduction recomputes from artifacts.",
    }


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        # smoke: a full eval-paper task hits all 3 weapons + armor
        t = {"has_reported_metric_and_artifacts": True, "has_train_and_eval_sets": True,
             "compares_two_models_same_testset": True, "claims_best_or_sota_or_capable": True}
        r = route(t)
        assert r["fires_weapons"] == ["R-CONTAM", "R-REPRO", "R-SIGNIF"], r
        assert r["routes_to_armor"] is True, r
        # a bare "model X is best" claim with no artifacts -> armor only
        t2 = {"claims_best_or_sota_or_capable": True}
        r2 = route(t2)
        assert r2["fires_weapons"] == [] and r2["routes_to_armor"] is True, r2
        print("reproml_router smoke: PASS (full task -> 3 weapons + armor; bare SOTA claim -> armor only)")
