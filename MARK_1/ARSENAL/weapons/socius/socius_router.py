#!/usr/bin/env python3
"""SOCIUS router — given a social-science task, choose which sub-weapons fire.

This is the "be a chooser" capability the v5 box asks of every weapon: read the
task, classify its claims by checkability (kappa), draw the kappa>0 sub-weapons
whose preconditions hold, and route the kappa=0 residue to ARMOR (ground or
abstain). It does NOT do the analysis — it decides which checks apply, and
labels every routed piece with its kappa so nothing kappa=0 is ever presented as
machine-verified.

Intake is a structured task descriptor (booleans describing the task's claims).
In live use these booleans come from an armor-side reading of the task; here they
are explicit so the routing logic is itself testable.
"""
import sys, json

# precondition -> (sub-weapon, kappa, track, rationale)
RULES = [
    ("has_open_data_and_code",          "S-REPRO",      1.0, "weapon",
     "A published quantitative statistic with open data+code can be re-run and checked."),
    ("finding_rests_on_analytic_choices", "S-MULTIVERSE", 1.0, "weapon",
     "The finding depends on defensible-but-arbitrary analytic choices; enumerate the multiverse."),
    ("constructs_are_latent",           "S-MEASURE",    1.0, "weapon",
     "Latent constructs (scales/indices) require reliability + invariance checks."),
    ("compares_groups",                 "S-MEASURE",    1.0, "weapon",
     "A group comparison is trustworthy only if the measure is invariant across those groups."),
    ("claim_is_causal_observational",   "S-CAUSAL",     0.5, "weapon",
     "A causal claim from observational data needs sensitivity analysis (E-value/Rosenbaum)."),
    ("generalizes_beyond_sample",       "S-SAMPLE",     0.5, "weapon",
     "Inference beyond the sample needs representativeness + weighting checks."),
    ("has_prose_empirical_claims",      "S-GROUND",     0.5, "armor",
     "Every empirical assertion in prose is grounded against a FETCHED source: a "
     "κ=1 FROZEN fabrication layer (quote/number/author actually present in the "
     "source — catches invented quotes & citations) + a κ=0 entailment judgment "
     "(does the source SUPPORT the paraphrase?) by a model != generator, else ABSTAIN."),
]


def route(task):
    """task: dict of boolean preconditions. Returns the routing plan."""
    fired, seen = [], set()
    for key, weapon, kappa, track, why in RULES:
        if task.get(key):
            if weapon in seen:
                # already fired (e.g. S-MEASURE from both latent + group) — note the extra trigger
                for f in fired:
                    if f["sub_weapon"] == weapon:
                        f["triggers"].append(key)
                continue
            seen.add(weapon)
            fired.append({"sub_weapon": weapon, "kappa": kappa, "track": track,
                          "triggers": [key], "rationale": why})

    pure_theory = task.get("pure_theory_no_data") and not any(
        task.get(k) for k, *_ in RULES)
    plan = {
        "fired_sub_weapons": fired,
        "weapon_track": [f for f in fired if f["track"] == "weapon"],
        "armor_track": [f for f in fired if f["track"] == "armor"],
        "kappa0_armor_only": bool(pure_theory),
    }
    if pure_theory:
        plan["note"] = ("Pure theory / interpretation with no data: kappa=0 -> "
                        "ARMOR ONLY (cross-model panel + grounding + scored abstention). "
                        "SOCIUS draws no frozen verifier; it cannot manufacture truth here.")
    elif not fired:
        plan["note"] = "No precondition matched — under-specified task; abstain and ask for the data/claims."
    else:
        plan["note"] = ("SOCIUS raises trustworthiness (reproducibility + grounding); "
                        "it does NOT establish truth. Findings that DIE under these "
                        "checks are the primary valuable output.")
    return plan


# ------------------------------- selftest ---------------------------------- #
def _selftest():
    # canonical case: a causal claim from observational survey data with a latent
    # scale, open data, group comparison, generalisation, and prose claims.
    t = {"has_open_data_and_code": True, "finding_rests_on_analytic_choices": True,
         "constructs_are_latent": True, "compares_groups": True,
         "claim_is_causal_observational": True, "generalizes_beyond_sample": True,
         "has_prose_empirical_claims": True}
    plan = route(t)
    names = {f["sub_weapon"] for f in plan["fired_sub_weapons"]}
    assert names == {"S-REPRO", "S-MULTIVERSE", "S-MEASURE", "S-CAUSAL", "S-SAMPLE", "S-GROUND"}, names
    # S-MEASURE fired by BOTH latent + group triggers (deduped, both recorded)
    sm = [f for f in plan["fired_sub_weapons"] if f["sub_weapon"] == "S-MEASURE"][0]
    assert set(sm["triggers"]) == {"constructs_are_latent", "compares_groups"}, sm

    # pure theory -> armor only, no weapon
    pt = route({"pure_theory_no_data": True})
    assert pt["kappa0_armor_only"] is True and pt["weapon_track"] == [], pt

    # a purely descriptive reproduction -> only S-REPRO
    desc = route({"has_open_data_and_code": True})
    assert {f["sub_weapon"] for f in desc["fired_sub_weapons"]} == {"S-REPRO"}, desc
    print("socius_router selftest: PASS (full case fires 6 sub-weapons; pure theory -> armor only)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: socius_router.py selftest | <task.json>")
