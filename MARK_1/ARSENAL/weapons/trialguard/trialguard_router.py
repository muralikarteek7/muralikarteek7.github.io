#!/usr/bin/env python3
"""TRIALGUARD router — given a clinical-trial / biostat task, choose which sub-weapons fire.

Cloned from psymetrix_router: read the task, classify its claims by checkability
(kappa), draw the kappa>0 sub-weapons whose preconditions hold, route the kappa=0
residue (efficacy / approval / clinical judgment) to ARMOR (ground or abstain). Labels
every routed piece with its kappa, and APPENDS THE INCONSISTENCY!=FRAUD CEILING to
every plan so nothing reads as an accusation and nothing kappa=0 is presented as
machine-verified. It decides WHICH checks apply; it does not run the analysis.
"""
import sys, json

# precondition -> (sub-weapon, kappa, track, rationale)
RULES = [
    ("reports_trial_summary_stats", "T-FORENSICS", 1.0, "weapon",
     "Reported trial means/SDs admit EXACT GRIM/GRIMMER consistency; group sizes & "
     "percentages admit EXACT allocation/count checks."),
    ("reports_baseline_table", "T-FORENSICS", 1.0, "weapon",
     "A baseline (Table 1) of CONTINUOUS variables admits the Carlisle baseline-anomaly "
     "screen (p-values ~ U(0,1) under simple randomization). A SCREEN, never an accusation."),
    ("reports_survival_data", "T-SURVIVAL", 0.7, "weapon",
     "Time-to-event data admits Kaplan-Meier reproduction + Cox PH partial-likelihood HR."),
    ("has_published_effect_with_data", "T-REPRO", 0.6, "weapon",
     "A published effect (HR/OR/RR/mean diff) with data can be RE-COMPUTED -> reproduction cert."),
    ("pools_multiple_studies", "T-META", 0.6, "weapon",
     "A body of studies can be pooled with I2 heterogeneity + Egger + trim-and-fill pub-bias checks."),
    ("finding_rests_on_analytic_choices", "T-MULTIVERSE", 0.5, "weapon",
     "A finding depending on defensible-but-arbitrary analytic choices: run the specification curve."),
    ("observational_causal_claim", "T-EVALUE", 0.5, "weapon",
     "An observational (non-randomized) causal claim gets an E-value SENSITIVITY analysis, "
     "never a bare causal claim (confounding is untestable)."),
    ("asks_efficacy_or_approval", "T-ARMOR", 0.0, "armor",
     "Does the drug WORK / should it be APPROVED / is the benefit worth the harm / "
     "GRADE / risk-of-bias judgment is kappa=0 -> ground in a fetched source or ABSTAIN."),
]

CEILING = ("INCONSISTENCY/ANOMALY != FRAUD. TRIALGUARD certifies CONSISTENCY / FIT / "
           "ROBUSTNESS of reported statistics, never CLINICAL TRUTH or EFFICACY. A "
           "Carlisle/GRIM flag is a mathematical/statistical fact about the reported "
           "numbers with many benign causes (rounding, stratified allocation, "
           "correlated covariates, dropout) -- NEVER a finding of misconduct. "
           "Carlisle 2017: 'Fraud, unintentional error, correlation, stratified "
           "allocation and poor methodology might have contributed to the excess.'")


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
    pure_clinical = task.get("pure_clinical_judgment_no_data") and not any(
        task.get(k) for k, *_ in RULES)
    plan = {
        "fired_sub_weapons": fired,
        "weapon_track": [f for f in fired if f["track"] == "weapon"],
        "armor_track": [f for f in fired if f["track"] == "armor"],
        "kappa0_armor_only": bool(pure_clinical),
        "ceiling": CEILING,
    }
    if pure_clinical:
        plan["note"] = ("Pure clinical/efficacy/approval judgment with no checkable data: "
                        "kappa=0 -> ARMOR ONLY (ground against a fetched source + scored "
                        "abstention). TRIALGUARD draws no frozen verifier; it cannot "
                        "manufacture clinical truth.")
    elif not fired:
        plan["note"] = "No precondition matched — under-specified; abstain and ask for the data/claims."
    else:
        plan["note"] = ("TRIALGUARD raises rigor (EXACT forensics where the arithmetic is "
                        "exact; a calibrated Carlisle SCREEN on continuous baselines; "
                        "reproduction/survival/meta elsewhere). Reported numbers that prove "
                        "INCONSISTENT are reported as inconsistent WITH the arithmetic + "
                        "benign explanations — NEVER as fraud.")
    return plan


def _selftest():
    # full case: a trial paper with summary stats, a baseline table, survival data, a
    # published effect, a meta-analytic body, analytic-choice sensitivity, an
    # observational causal claim, AND an efficacy/approval ask.
    t = {"reports_trial_summary_stats": True, "reports_baseline_table": True,
         "reports_survival_data": True, "has_published_effect_with_data": True,
         "pools_multiple_studies": True, "finding_rests_on_analytic_choices": True,
         "observational_causal_claim": True, "asks_efficacy_or_approval": True}
    plan = route(t)
    names = {f["sub_weapon"] for f in plan["fired_sub_weapons"]}
    assert names == {"T-FORENSICS", "T-SURVIVAL", "T-REPRO", "T-META", "T-MULTIVERSE",
                     "T-EVALUE", "T-ARMOR"}, names
    # T-FORENSICS fired by BOTH summary-stats and baseline-table (deduped, both kept)
    tf = [f for f in plan["fired_sub_weapons"] if f["sub_weapon"] == "T-FORENSICS"][0]
    assert set(tf["triggers"]) == {"reports_trial_summary_stats", "reports_baseline_table"}, tf
    # efficacy/approval routed to ARMOR (kappa=0), never weapon
    assert plan["armor_track"][0]["sub_weapon"] == "T-ARMOR"
    assert plan["armor_track"][0]["kappa"] == 0.0
    # pure clinical judgment -> armor only
    pc = route({"pure_clinical_judgment_no_data": True})
    assert pc["kappa0_armor_only"] is True and pc["weapon_track"] == [], pc
    # a single forensic task -> only T-FORENSICS
    one = route({"reports_trial_summary_stats": True})
    assert {f["sub_weapon"] for f in one["fired_sub_weapons"]} == {"T-FORENSICS"}, one
    # the inconsistency!=fraud ceiling is ALWAYS present
    assert "INCONSISTENCY/ANOMALY != FRAUD" in plan["ceiling"]
    assert "never" in plan["ceiling"].lower() and "fraud" in plan["ceiling"].lower()
    print("trialguard_router selftest: PASS (full case fires 7 sub-weapons; stats+baseline "
          "both trigger T-FORENSICS; efficacy->armor; clinical-judgment->armor only; "
          "inconsistency!=fraud ceiling on every plan)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: trialguard_router.py selftest | <task.json>")
