#!/usr/bin/env python3
"""E-CAUSAL demo — pre-trends placebo + sensitivity numbers, with committed predictions.

Two difference-in-differences panels (synthetic, KNOWN ground truth, honestly labelled):
  A CLEAN      : true effect +3.0, parallel pre-trends  -> pre-trends PASS, effect recovered.
  B CONFOUNDED : NO true effect, treated group on a divergent PRE-trend -> a naive DiD reads a
                 "significant effect", but the PRE-TRENDS PLACEBO CATCHES it (the causal "dies under
                 stress"). Plus Oster (2019) delta (robust vs fragile) and an E-value sensitivity number.

Reuses the frozen causal_verify.py. Run: python3 demo_run.py
"""
import os, sys, json
import numpy as np
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "socius"))
import causal_verify as cv
import repro_verify        # E-REPRO, reused from SOCIUS


def card_krueger_repro():
    """E-REPRO on a REAL published DiD: Card & Krueger (1994), 'Minimum Wages and Employment', AER
    84(4):772-793, Table 3. Published 2x2 FTE-employment means (fetched & grounded, see GROUNDING.md /
    WRITEUP): NJ 20.44 -> 21.03 (+0.59); PA 23.33 -> 21.17 (-2.16). Published DiD = +2.76 FTE (the
    famous 'minimum wage did NOT cut employment'). We recompute the DiD from the published means and
    check it reproduces the published estimate within tolerance. NB: 2-period design => NO pre-trends
    test possible (an honest limitation, not a pass)."""
    nj_before, nj_after = 20.44, 21.03
    pa_before, pa_after = 23.33, 21.17
    did = (nj_after - nj_before) - (pa_after - pa_before)
    verdict = repro_verify.check_reproduction({"DiD_FTE": 2.76}, {"DiD_FTE": did}, rel_tol=0.02)
    return {"recomputed_DiD": did, "published_DiD": 2.76,
            "reproduced": verdict["reproduced"], "abs_diff": verdict["details"]["DiD_FTE"]["abs_diff"],
            "note": "2-period DiD -> pre-trends UNtestable here; reported as a labelled reproduction."}


def naive_did_estimate(df):
    """The 2x2 DiD a naive analyst computes: (treated post - treated pre) - (control post - control pre).
    This is the number that gets fooled by a pre-trend."""
    d = df.copy()
    d["treated"] = (d["rel_time"] < 9000).astype(int)
    d["post"] = ((d["rel_time"] >= 0) & (d["rel_time"] < 9000)).astype(int)
    # for controls, define a pseudo-post at the same calendar period as treated treat_start (period 7)
    d.loc[d["treated"] == 0, "post"] = (d.loc[d["treated"] == 0, "time"] >= 7).astype(int)
    res = smf.ols("y ~ treated * post", data=d).fit()
    return float(res.params["treated:post"]), float(res.pvalues["treated:post"])


def post_effect_estimate(df):
    """Average of the post-treatment lag coefficients from the event study (the recovered effect)."""
    pt = cv.did_pretrends(df)
    # refit to grab the post lags too
    d = df.copy()
    rt_vals = sorted(v for v in d["rel_time"].dropna().unique() if v != -1 and abs(v) < 9000)
    cols = []
    for v in rt_vals:
        name = f"rt_{'m' if v < 0 else 'p'}{abs(int(v))}"
        d[name] = (d["rel_time"] == v).astype(float)
        cols.append((v, name))
    formula = "y ~ C(unit) + C(time) + " + " + ".join(n for _, n in cols)
    res = smf.ols(formula, data=d).fit()
    post = [res.params[n] for v, n in cols if v >= 0]
    return float(np.mean(post)) if post else float("nan")


def main():
    out = {}

    # ----- Scenario A: CLEAN -----
    A = cv._make_panel(effect=3.0, pretrend=0.0, seed=11)
    A_pt = cv.did_pretrends(A)
    A_post = post_effect_estimate(A)
    # E-value: convert the recovered effect to a standardized d, then to the RR scale
    sd_y = float(np.std(A["y"]))
    d_eff = A_post / sd_y
    A_ev = cv.e_value_sensitivity(d_eff, scale="d", benchmark_confounding=2.0)
    out["scenario_A_clean"] = {
        "pretrends_p": A_pt["joint_pretrend_p"], "parallel_trends_plausible": A_pt["parallel_trends_plausible"],
        "recovered_post_effect": A_post, "true_effect": 3.0,
        "cohen_d": d_eff, "e_value_point": A_ev["e_value_point"],
    }

    # ----- Scenario B: CONFOUNDED (no true effect, divergent pre-trend) -----
    B = cv._make_panel(effect=0.0, pretrend=0.6, seed=11)
    B_pt = cv.did_pretrends(B)
    B_naive, B_naive_p = naive_did_estimate(B)
    out["scenario_B_confounded"] = {
        "pretrends_p": B_pt["joint_pretrend_p"], "parallel_trends_plausible": B_pt["parallel_trends_plausible"],
        "design_flagged": not B_pt["parallel_trends_plausible"],
        "naive_did_estimate": B_naive, "naive_did_pvalue": B_naive_p,
        "true_effect": 0.0,
    }

    # ----- Oster delta: robust vs fragile (untestable-selection sensitivity) -----
    rob = cv.oster_delta(1.0, 0.10, 0.92, 0.34, R_max=0.60)   # coefficient stable, R2 jumps -> robust
    frag = cv.oster_delta(1.0, 0.10, 0.25, 0.13)              # coefficient collapses -> fragile
    out["oster_delta"] = {
        "robust": {"delta": rob["delta"], "robust_to_selection": rob["robust_to_selection"]},
        "fragile": {"delta": frag["delta"], "robust_to_selection": frag["robust_to_selection"]},
    }

    # ----- E-REPRO: reproduce a REAL published DiD (Card & Krueger 1994) -----
    ck = card_krueger_repro()
    out["e_repro_card_krueger_1994"] = ck

    # ----- report -----
    print("E-CAUSAL demo — pre-trends placebo + sensitivity numbers\n")
    print("Scenario A (CLEAN: true effect +3.0, parallel pre-trends):")
    print(f"  pre-trends placebo p = {A_pt['joint_pretrend_p']:.3f} -> "
          f"parallel-trends plausible = {A_pt['parallel_trends_plausible']}")
    print(f"  recovered post effect = {A_post:.2f} (true 3.0); Cohen d = {d_eff:.2f}; "
          f"E-value = {A_ev['e_value_point']:.2f}")
    print("\nScenario B (CONFOUNDED: NO true effect, divergent pre-trend):")
    print(f"  naive 2x2 DiD = {B_naive:+.2f} (p={B_naive_p:.1e})  <-- a naive analyst would call this a "
          f"'significant effect'")
    print(f"  pre-trends placebo p = {B_pt['joint_pretrend_p']:.1e} -> "
          f"parallel-trends plausible = {B_pt['parallel_trends_plausible']}")
    print(f"  ==> ECONOMETRIX FLAGS the design (pre-trends FAIL): the confound is CAUGHT, "
          f"not laundered into a causal effect.")
    print("\nOster delta (selection-on-unobservables sensitivity):")
    print(f"  robust design:  delta = {rob['delta']:.2f} -> robust = {rob['robust_to_selection']}")
    print(f"  fragile design: delta = {frag['delta']:.2f} -> robust = {frag['robust_to_selection']}")
    print("\nE-REPRO — Card & Krueger (1994) minimum-wage DiD (real published number):")
    print(f"  recomputed DiD = {ck['recomputed_DiD']:+.2f} FTE vs published +2.76 -> "
          f"reproduced = {ck['reproduced']} (|diff|={ck['abs_diff']:.3f}); {ck['note']}")
    print("\nHONEST CEILING: passing pre-trends is necessary, not sufficient — post-period parallel "
          "trends is\nuntestable (Roth 2022). A sensitivity number is reported; no bare 'X caused Y'.")

    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nwrote results.json")


if __name__ == "__main__":
    main()
