#!/usr/bin/env python3
"""S-SAMPLE — frozen verifier for SAMPLING / GENERALIZABILITY (kappa ~= 0.5).

A "group difference" or population estimate generalises only as far as the sample
represents the target population. Two machine-checkable diagnostics:

1. REPRESENTATIVENESS: compare the sample's marginal distribution on key strata
   (e.g. age x sex x region) against KNOWN target-population marginals. Report the
   total-variation distance and a chi-square goodness-of-fit. Large divergence =>
   the unweighted estimate describes the sample, not the target.

2. WEIGHT SENSITIVITY: if post-stratification weights bring the sample to the
   population, does the WEIGHTED estimate differ materially from the UNWEIGHTED
   one? If weighting moves the estimate a lot, the unweighted "finding" is partly
   a composition artifact. Also report the design effect (Kish) implied by the
   weights — the effective-sample-size penalty.

kappa ~= 0.5: the divergence and the weighted/unweighted shift are exact
(kappa=1); whether the target population the user wants to generalise to is the
right one, and whether the strata used capture the relevant heterogeneity, are
kappa=0 judgments routed to armor. A representative sample does NOT make a finding
true — only potentially generalisable.
"""
import sys, json
import numpy as np


def representativeness(sample_props, pop_props):
    """sample_props, pop_props: dict {stratum: proportion}, each summing ~1.
    Returns total-variation distance and chi-square-style divergence."""
    keys = sorted(set(sample_props) | set(pop_props))
    s = np.array([sample_props.get(k, 0.0) for k in keys])
    p = np.array([pop_props.get(k, 0.0) for k in keys])
    s = s / s.sum(); p = p / p.sum()
    tvd = 0.5 * np.abs(s - p).sum()
    # chi-square divergence sum((s-p)^2/p), guard zero-population cells
    mask = p > 0
    chisq = float(np.sum((s[mask] - p[mask]) ** 2 / p[mask]))
    return {"strata": keys, "tv_distance": float(tvd),
            "chi_square_divergence": chisq}


def weight_sensitivity(estimate_unweighted, estimate_weighted, weights=None,
                       rel_shift_threshold=0.10):
    """Compare weighted vs unweighted point estimates; report Kish design effect."""
    base = abs(estimate_unweighted) if estimate_unweighted != 0 else 1.0
    rel_shift = abs(estimate_weighted - estimate_unweighted) / base
    deff = None; n_eff_ratio = None
    if weights is not None:
        w = np.asarray(weights, dtype=float)
        deff = float((w.mean() ** 2 + w.var()) / (w.mean() ** 2))  # 1 + CV^2
        n_eff_ratio = float(1.0 / deff)
    return {"estimate_unweighted": estimate_unweighted,
            "estimate_weighted": estimate_weighted,
            "relative_shift": float(rel_shift),
            "weighting_changes_conclusion": bool(rel_shift > rel_shift_threshold),
            "design_effect_kish": deff, "effective_n_ratio": n_eff_ratio}


def assess_generalizability(sample_props, pop_props,
                            estimate_unweighted=None, estimate_weighted=None,
                            weights=None, tvd_threshold=0.10):
    rep = representativeness(sample_props, pop_props)
    out = {"sub_weapon": "S-SAMPLE", "kappa": 0.5, "representativeness": rep}
    misrep = rep["tv_distance"] > tvd_threshold
    weight_flag = False
    if estimate_unweighted is not None and estimate_weighted is not None:
        ws = weight_sensitivity(estimate_unweighted, estimate_weighted, weights)
        out["weight_sensitivity"] = ws
        weight_flag = ws["weighting_changes_conclusion"]
    out["generalizable"] = bool(not misrep and not weight_flag)
    out["flags"] = {
        "sample_unrepresentative": bool(misrep),
        "estimate_sensitive_to_weighting": bool(weight_flag)}
    out["ceiling_note"] = ("Representative != true. Generalizability is necessary "
                           "for population inference, not sufficient for a causal "
                           "or valid claim. Target population is a kappa=0 choice.")
    return out


def _selftest():
    pop = {"young_m": 0.25, "young_f": 0.25, "old_m": 0.25, "old_f": 0.25}
    # Known-GOOD: representative sample + weighting barely moves estimate
    good = assess_generalizability(
        {"young_m": 0.24, "young_f": 0.26, "old_m": 0.25, "old_f": 0.25}, pop,
        estimate_unweighted=0.50, estimate_weighted=0.51,
        weights=[1.0, 1.02, 0.98, 1.0])
    assert good["generalizable"] is True, good
    # Known-BAD: skewed sample (90% young) AND weighting flips the estimate
    #   -> MUST flag not-generalizable (the verifier must be able to FAIL)
    bad = assess_generalizability(
        {"young_m": 0.45, "young_f": 0.45, "old_m": 0.05, "old_f": 0.05}, pop,
        estimate_unweighted=0.50, estimate_weighted=0.30,
        weights=[0.2, 0.2, 5.0, 5.0])
    assert bad["generalizable"] is False, bad
    assert bad["flags"]["sample_unrepresentative"] and bad["flags"]["estimate_sensitive_to_weighting"]
    print("sample_verify selftest: PASS (passes representative sample; FAILS skewed/weight-sensitive sample)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: sample_verify.py selftest  (programmatic API: assess_generalizability)")
