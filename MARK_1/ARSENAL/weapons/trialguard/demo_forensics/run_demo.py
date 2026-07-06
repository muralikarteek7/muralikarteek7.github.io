#!/usr/bin/env python3
"""Killer demo for TRIALGUARD. Predictions committed in PREDICTION.md (BEFORE running).

Demo A: reproduce GRIM literature + exact allocation/percentage checks (grounded).
Demo B: controlled ground-truth corpus -> Carlisle screen specificity (calibration) &
        sensitivity, plus the cardinal honesty scan (NO output affirms misconduct).
Demo C: T-META reproduction + Egger/trim-and-fill publication-bias screen.
Demo D: the false-positive guard -- a stratified trial is NOT accused.

NO real trial is named or accused. Demo A reuses the method paper's own GRIM example;
Demos B/D use SIMULATED trials with KNOWN ground truth. Run AFTER the gate passes.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import forensics_trial_verify as TF
import meta_trial_verify as MT


def demo_A():
    rows = []
    cases = [
        ("GRIM 5.27/n=43", TF.PF.grim("5.27", 43)["consistent"] is False, "INCONSISTENT"),
        ("GRIM 5.26/n=43", TF.PF.grim("5.26", 43)["consistent"] is True, "consistent"),
        ("alloc 30/90 ratio 1:1",
         TF.allocation_ratio_consistency([30, 90], [1, 1])["consistent"] is False, "INCONSISTENT"),
        ("alloc 60/60 ratio 1:1",
         TF.allocation_ratio_consistency([60, 60], [1, 1])["consistent"] is True, "consistent"),
        ("pct 33.3% of n=7",
         TF.percentage_count_consistency("33.3", 7)["consistent"] is False, "INCONSISTENT"),
    ]
    for label, ok, predicted in cases:
        rows.append({"case": label, "predicted": predicted, "matches_prediction": bool(ok)})
    return rows


def _clean_trial(rng, k=8, n=60):
    vs = []
    for j in range(k):
        mu, sd = rng.uniform(20, 80), rng.uniform(5, 15)
        a = rng.normal(mu, sd, n); b = rng.normal(mu, sd, n)
        vs.append({"name": f"v{j}", "type": "continuous",
                   "mean1": a.mean(), "sd1": a.std(ddof=1), "n1": n,
                   "mean2": b.mean(), "sd2": b.std(ddof=1), "n2": n})
    return vs


def _fabricated_too_similar(rng, k=8, n=60, max_std_diff=0.05):
    """An over-balancer: every standardized between-group difference kept small."""
    vs = []
    for j in range(k):
        mu, sd = rng.uniform(20, 80), rng.uniform(5, 15)
        d = rng.uniform(-max_std_diff, max_std_diff) * sd
        vs.append({"name": f"v{j}", "type": "continuous",
                   "mean1": mu, "sd1": sd, "n1": n,
                   "mean2": mu + d, "sd2": sd, "n2": n})
    return vs


def demo_B(n_each=300, alpha=0.001):
    rng = np.random.default_rng(20260620)
    clean_flagged = 0
    fab_caught = 0
    misconduct_affirmations = 0
    examples = {"clean_consistent": None, "fabricated_flagged": None}
    for _ in range(n_each):
        rc = TF.carlisle_baseline_test(_clean_trial(rng), alpha=alpha, design="simple")
        if rc["anomaly"]:
            clean_flagged += 1
        if TF.affirms_misconduct(rc["verdict"]):
            misconduct_affirmations += 1
        if examples["clean_consistent"] is None and not rc["anomaly"]:
            examples["clean_consistent"] = {"verdict": rc["verdict"],
                                            "stouffer_Z": rc["stouffer_Z"]}
    for _ in range(n_each):
        rf = TF.carlisle_baseline_test(_fabricated_too_similar(rng), alpha=alpha, design="unknown")
        if rf["anomaly"] and rf["direction"] == "too_similar":
            fab_caught += 1
        if TF.affirms_misconduct(rf["verdict"]):
            misconduct_affirmations += 1
        if examples["fabricated_flagged"] is None and rf["anomaly"]:
            examples["fabricated_flagged"] = {
                "verdict": rf["verdict"], "stouffer_Z": rf["stouffer_Z"],
                "benign_explanations": rf["candidate_benign_explanations"][:3],
                "false_positive_modes_count": len(rf["false_positive_modes"])}
    return {
        "n_each": n_each, "alpha": alpha,
        "clean_flagged": clean_flagged,
        "clean_false_flag_rate_pct": round(100 * clean_flagged / n_each, 3),
        "fabrication_caught": fab_caught,
        "sensitivity_pct": round(100 * fab_caught / n_each, 2),
        "misconduct_affirmations": misconduct_affirmations,
        "examples": examples,
    }


def demo_C():
    eff = [0.10, 0.12, 0.11, 0.13, 0.55, 0.60, 0.70]
    se = [0.04, 0.05, 0.04, 0.05, 0.18, 0.20, 0.22]
    m = MT.meta(eff, se)
    tf = m["trim_and_fill"]
    return {"k": m["k"], "fixed_effect": m["fixed_effect"], "random_effect": m["random_effect"],
            "I2_percent": m["I2_percent"], "egger_p": m["egger_p"],
            "funnel_asymmetry_flagged": m["funnel_asymmetry_flagged"],
            "trim_fill_k0": tf["k0_imputed_missing"], "suppressed_side": tf["suppressed_side"],
            "pooled_observed": tf["pooled_observed"], "pooled_adjusted": tf["pooled_adjusted"],
            "pulled_toward_null": tf["pooled_adjusted"] < tf["pooled_observed"]}


def demo_D():
    rng = np.random.default_rng(99)
    fake = _fabricated_too_similar(rng)
    fake[0]["stratum"] = True       # a declared stratification factor
    r = TF.carlisle_baseline_test(fake, alpha=0.001, design="stratified")
    return {"anomaly": r["anomaly"], "verdict": r["verdict"],
            "affirms_misconduct": TF.affirms_misconduct(r["verdict"]),
            "has_design_caveat": bool(r.get("design_caveat")),
            "stratum_var_excluded": any(e["name"] == "v0" for e in r["variables_excluded"]),
            "design_caveat": r.get("design_caveat")}


if __name__ == "__main__":
    A = demo_A(); B = demo_B(); C = demo_C(); D = demo_D()

    print("=" * 78)
    print("DEMO A — grounded GRIM + EXACT allocation/percentage checks")
    print("=" * 78)
    for r in A:
        print(f"  [{'OK ' if r['matches_prediction'] else 'XX '}] {r['case']:24s} -> predicted {r['predicted']}")
    a_ok = all(r["matches_prediction"] for r in A)

    print("=" * 78)
    print("DEMO B — controlled ground-truth corpus (Carlisle calibration + honesty scan)")
    print("=" * 78)
    print(f"  SPECIFICITY: clean false-flag rate = {B['clean_false_flag_rate_pct']}% "
          f"({B['clean_flagged']}/{B['n_each']}) at alpha={B['alpha']}  (predicted ~0.1%)")
    print(f"  SENSITIVITY: fabricated too-similar caught = {B['sensitivity_pct']}% "
          f"({B['fabrication_caught']}/{B['n_each']})  (predicted >85%)")
    print(f"  CARDINAL HONESTY: outputs that AFFIRM misconduct = {B['misconduct_affirmations']}"
          f"  <-- MUST be 0")
    if B["examples"]["fabricated_flagged"]:
        ex = B["examples"]["fabricated_flagged"]
        print(f"  example flagged output (Z={ex['stouffer_Z']}): \"{ex['verdict'][:96]}...\"")
        print(f"    -> attaches {ex['false_positive_modes_count']} false-positive modes + "
              f"benign explanations (e.g. {ex['benign_explanations'][0]})")

    print("=" * 78)
    print("DEMO C — T-META reproduction + publication-bias screen")
    print("=" * 78)
    print(f"  k={C['k']} studies; fixed={C['fixed_effect']} random={C['random_effect']} "
          f"I2={C['I2_percent']}%  Egger p={C['egger_p']} (asymmetry={C['funnel_asymmetry_flagged']})")
    print(f"  trim-and-fill: imputed {C['trim_fill_k0']} on the {C['suppressed_side']} side; "
          f"pooled {C['pooled_observed']} -> {C['pooled_adjusted']} "
          f"(toward null: {C['pulled_toward_null']})")

    print("=" * 78)
    print("DEMO D — the false-positive guard (stratified trial is NOT accused)")
    print("=" * 78)
    print(f"  anomaly registered={D['anomaly']}  affirms_misconduct={D['affirms_misconduct']} "
          f"<-- MUST be False")
    print(f"  stratum var excluded={D['stratum_var_excluded']}  has_design_caveat={D['has_design_caveat']}")

    # prediction checks
    spec_ok = B["clean_false_flag_rate_pct"] <= 2.0          # ~ alpha, generous bound
    sens_ok = B["sensitivity_pct"] > 85.0
    honesty_ok = B["misconduct_affirmations"] == 0
    meta_ok = C["funnel_asymmetry_flagged"] and C["trim_fill_k0"] >= 1 and C["pulled_toward_null"]
    guard_ok = (not D["affirms_misconduct"]) and D["has_design_caveat"] and D["stratum_var_excluded"]

    print("=" * 78)
    print("PREDICTION CHECK:")
    print(f"  Demo A exact/grounded all match ........ {'PASS' if a_ok else 'FAIL'}")
    print(f"  Clean false-flag rate ~ alpha .......... {'PASS' if spec_ok else 'FAIL'}")
    print(f"  Fabrication sensitivity > 85% .......... {'PASS' if sens_ok else 'FAIL'}")
    print(f"  ZERO misconduct affirmations (CARDINAL)  {'PASS' if honesty_ok else 'FAIL'}")
    print(f"  T-META Egger+trim-and-fill toward null . {'PASS' if meta_ok else 'FAIL'}")
    print(f"  Stratified guard (not accused) ......... {'PASS' if guard_ok else 'FAIL'}")

    out = {"demo_A": A, "demo_B": B, "demo_C": C, "demo_D": D, "checks": {
        "demoA_exact_grounded": a_ok, "clean_calibrated": spec_ok,
        "sensitivity_gt_85": sens_ok, "zero_misconduct_affirmations": honesty_ok,
        "meta_pubbias_toward_null": meta_ok, "stratified_guard": guard_ok}}
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(out, open(os.path.join(here, "RESULT.json"), "w"), indent=2)
    print("\nwrote RESULT.json")
    if not (a_ok and spec_ok and sens_ok and honesty_ok and meta_ok and guard_ok):
        sys.exit(1)
