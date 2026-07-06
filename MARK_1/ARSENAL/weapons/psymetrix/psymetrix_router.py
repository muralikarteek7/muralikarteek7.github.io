#!/usr/bin/env python3
"""PSYMETRIX router — given a quant-psych task, choose which sub-weapons fire.

Mirrors socius_router: read the task, classify its claims by checkability (kappa),
draw the kappa>0 sub-weapons whose preconditions hold, route the kappa=0 residue to
ARMOR (ground or abstain). Labels every routed piece with its kappa so nothing
kappa=0 is presented as machine-verified. It decides WHICH checks apply; it does
not run the analysis.

Intake is a structured task descriptor of booleans (in live use these come from an
armor-side reading of the task; here explicit so the routing is itself testable).
"""
import sys, json

# precondition -> (sub-weapon, kappa, track, rationale)
RULES = [
    ("reports_summary_stats_on_scale", "P-FORENSICS",  1.0, "weapon",
     "Reported means/SDs on bounded/integer scales admit EXACT GRIM/GRIMMER/SPRITE consistency proofs."),
    ("reports_pvalue_set",             "P-FORENSICS",  1.0, "weapon",
     "A body of reported p-values admits TIVA / p-curve evidential-value / Benford forensics."),
    ("uses_scale_or_difference_score", "P-RELIABILITY",1.0, "weapon",
     "A scale/difference/corrected score needs reliability; a disattenuated r>1 is an exact inconsistency."),
    ("claims_latent_structure",        "P-MODEL",      1.0, "weapon",
     "A claimed factor/scale structure can be checked for dimensionality (and IRT/CFA/SEM if available)."),
    ("has_open_data_published_effect", "P-REPRO",      1.0, "weapon",
     "A published effect with open data can be RE-COMPUTED two independent ways (reproduction certificate)."),
    ("finding_rests_on_analytic_choices", "P-MULTIVERSE", 1.0, "weapon",
     "A finding that depends on defensible-but-arbitrary analytic choices: run the specification curve / multiverse."),
    ("compares_groups_on_scale",       "P-DIF",        1.0, "weapon",
     "A cross-group score comparison is trustworthy only if items are free of DIF at matched ability."),
    ("pools_a_body_of_findings",       "P-META",       1.0, "weapon",
     "A body of findings can be meta-analyzed with publication-bias (Egger/funnel) correction."),
    ("designs_or_evaluates_study",     "P-DESIGN",     1.0, "weapon",
     "Study design admits exact a-priori power + constructive optimal item selection (max test information)."),
    ("has_interpretive_theory_claims", "P-GROUND",     0.0, "armor",
     "What a construct MEANS / theory choice is kappa=0 — ground in a fetched source or ABSTAIN."),
]

CEILING = ("PSYMETRIX certifies CONSISTENCY / FIT / ROBUSTNESS, never TRUTH. "
           "A statistical inconsistency is a mathematical fact about the reported "
           "numbers, NEVER an accusation about the people (rounding/typo/reporting "
           "error are always possible).")


def route(task):
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
    pure_theory = task.get("pure_theory_no_data") and not any(
        task.get(k) for k, *_ in RULES)
    plan = {
        "fired_sub_weapons": fired,
        "weapon_track": [f for f in fired if f["track"] == "weapon"],
        "armor_track": [f for f in fired if f["track"] == "armor"],
        "kappa0_armor_only": bool(pure_theory),
        "ceiling": CEILING,
    }
    if pure_theory:
        plan["note"] = ("Pure theory / interpretation with no data: kappa=0 -> ARMOR "
                        "ONLY (cross-model panel + grounding + scored abstention). "
                        "PSYMETRIX draws no frozen verifier; it cannot manufacture truth here.")
    elif not fired:
        plan["note"] = "No precondition matched — under-specified; abstain and ask for the data/claims."
    else:
        plan["note"] = ("PSYMETRIX raises rigor (exact forensics where the math is exact; "
                        "fit/robustness elsewhere). Reported numbers that prove INCONSISTENT "
                        "are reported as inconsistent WITH the arithmetic — never as fraud.")
    return plan


def _selftest():
    # full case: a paper reporting scale stats, p-values, a scale, latent structure,
    # group comparison, a meta-analytic body, a design, and interpretive claims.
    t = {"reports_summary_stats_on_scale": True, "reports_pvalue_set": True,
         "uses_scale_or_difference_score": True, "claims_latent_structure": True,
         "has_open_data_published_effect": True, "finding_rests_on_analytic_choices": True,
         "compares_groups_on_scale": True, "pools_a_body_of_findings": True,
         "designs_or_evaluates_study": True, "has_interpretive_theory_claims": True}
    plan = route(t)
    names = {f["sub_weapon"] for f in plan["fired_sub_weapons"]}
    assert names == {"P-FORENSICS", "P-RELIABILITY", "P-MODEL", "P-REPRO", "P-MULTIVERSE",
                     "P-DIF", "P-META", "P-DESIGN", "P-GROUND"}, names
    # P-FORENSICS fired by BOTH summary-stats and p-value triggers (deduped, both kept)
    pf = [f for f in plan["fired_sub_weapons"] if f["sub_weapon"] == "P-FORENSICS"][0]
    assert set(pf["triggers"]) == {"reports_summary_stats_on_scale", "reports_pvalue_set"}, pf
    # interpretive claim routed to ARMOR (kappa=0), never weapon
    assert plan["armor_track"][0]["sub_weapon"] == "P-GROUND"
    # pure theory -> armor only
    pt = route({"pure_theory_no_data": True})
    assert pt["kappa0_armor_only"] is True and pt["weapon_track"] == [], pt
    # a single forensic task -> only P-FORENSICS
    one = route({"reports_summary_stats_on_scale": True})
    assert {f["sub_weapon"] for f in one["fired_sub_weapons"]} == {"P-FORENSICS"}, one
    # ceiling always present
    assert "never TRUTH" in plan["ceiling"]
    print("psymetrix_router selftest: PASS (full case fires 9 sub-weapons; "
          "p-value+stats both trigger P-FORENSICS; interpretive->armor; theory->armor only)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: psymetrix_router.py selftest | <task.json>")
