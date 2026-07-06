#!/usr/bin/env python3
"""R-SIGNIF (kappa~0.9) — is an A>B model-comparison gap real, or noise?

Two paired tests on the SAME test set (errors are paired, not independent):
  * McNEMAR (Dietterich 1998, recommended for the single-test-set case): uses only
    the discordant pairs b=(A right,B wrong), c=(A wrong,B right). Continuity-corrected
    chi^2 = (|b-c|-1)^2 / (b+c) on 1 df.
  * PAIRED BOOTSTRAP CI on the accuracy difference (resample items with replacement).
  * BONFERRONI multiple-comparison correction when k models are compared (alpha/k).

HONESTY: report CIs, never a bare point-rank leaderboard. A small gap on small N is
usually noise. This tests whether a GAP is significant; it never crowns a 'best' model
(that is kappa=0 -> armor).
"""
import numpy as np
from scipy import stats


def mcnemar(correct_a, correct_b):
    """correct_a, correct_b: equal-length 0/1 arrays of per-item correctness on the
    SAME test set. Returns the continuity-corrected McNemar chi^2 + p-value."""
    a = np.asarray(correct_a).astype(int)
    b = np.asarray(correct_b).astype(int)
    assert a.shape == b.shape, "paired arrays must be the same length"
    b_only = int(np.sum((a == 1) & (b == 0)))   # A right, B wrong
    c_only = int(np.sum((a == 0) & (b == 1)))   # A wrong, B right
    n_disc = b_only + c_only
    if n_disc == 0:
        return {"test": "mcnemar", "discordant": 0, "chi2": 0.0, "p_value": 1.0,
                "b_a_right_b_wrong": b_only, "c_a_wrong_b_right": c_only}
    chi2 = (abs(b_only - c_only) - 1) ** 2 / n_disc
    p = float(stats.chi2.sf(chi2, df=1))
    # audit fix A1b: the p-value is computed from the UNROUNDED chi2; report chi2 to
    # enough precision that re-deriving p from the printed statistic matches.
    return {"test": "mcnemar (continuity-corrected, Dietterich 1998)",
            "discordant": n_disc, "b_a_right_b_wrong": b_only,
            "c_a_wrong_b_right": c_only, "chi2": round(chi2, 8),
            "p_value": p,
            "note": "p_value is computed from the unrounded chi2 statistic"}


def paired_bootstrap_ci(correct_a, correct_b, n_boot=10000, alpha=0.05, seed=12345):
    """Paired bootstrap CI on (acc_A - acc_B). Resamples item indices with replacement."""
    a = np.asarray(correct_a).astype(float)
    b = np.asarray(correct_b).astype(float)
    n = len(a)
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        diffs[i] = a[idx].mean() - b[idx].mean()
    lo = float(np.percentile(diffs, 100 * alpha / 2))
    hi = float(np.percentile(diffs, 100 * (1 - alpha / 2)))
    return {"acc_a": round(float(a.mean()), 4), "acc_b": round(float(b.mean()), 4),
            "obs_diff": round(float(a.mean() - b.mean()), 4),
            "ci_lower": round(lo, 4), "ci_upper": round(hi, 4),
            "ci_level": 1 - alpha, "n_boot": n_boot,
            "ci_excludes_zero": bool(lo > 0 or hi < 0)}


def compare(correct_a, correct_b, alpha=0.05, n_comparisons=1, name_a="A", name_b="B"):
    """Full A-vs-B verdict with Bonferroni-corrected alpha."""
    alpha_corr = alpha / max(1, n_comparisons)
    mc = mcnemar(correct_a, correct_b)
    ci = paired_bootstrap_ci(correct_a, correct_b, alpha=alpha_corr)
    # audit fix A3: the AND-logic (BOTH tests must agree) is CONSERVATIVE (Type-I-safe)
    # but was undocumented. Surface each test's verdict + whether they agree, and note
    # disagreement explicitly so a ~2% boundary Type-II is never silent.
    mc_sig = mc["p_value"] < alpha_corr
    ci_sig = ci["ci_excludes_zero"]
    significant = mc_sig and ci_sig
    tests_agree = (mc_sig == ci_sig)
    disagreement = None
    if not tests_agree:
        disagreement = ("McNemar and the bootstrap CI DISAGREE at this alpha "
                        f"(McNemar significant={mc_sig}, CI excludes zero={ci_sig}). The verdict "
                        "is the CONSERVATIVE AND (requires both) -> reported NOT_SIGNIFICANT; this "
                        "is a boundary case, not strong evidence of no effect.")
    return {
        "sub_weapon": "R-SIGNIF", "kappa": 0.9, "models": [name_a, name_b],
        "alpha": alpha, "n_comparisons": n_comparisons,
        "bonferroni_alpha": round(alpha_corr, 6),
        "mcnemar": mc, "bootstrap_ci": ci,
        "mcnemar_significant": bool(mc_sig), "ci_excludes_zero": bool(ci_sig),
        "tests_agree": bool(tests_agree), "disagreement_note": disagreement,
        "significant": bool(significant),
        "verdict": ("SIGNIFICANT_DIFFERENCE" if significant else "NOT_SIGNIFICANT"),
        "ceiling_note": "SIGNIFICANT requires BOTH paired McNemar (p<alpha) AND the bootstrap CI "
                        "to exclude zero (CONSERVATIVE: Type-I-safe, may miss ~2% of boundary "
                        "effects -> see disagreement_note). Bonferroni-corrected. NOT a SOTA/best "
                        "claim (kappa=0 -> armor). NOT_SIGNIFICANT means the data cannot "
                        "distinguish the models, not that they are equal.",
    }


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    n = 500
    # case 1: a TINY gap on n=500 -> should be NOT significant
    base = rng.random(n) < 0.80
    a1 = base.copy()
    b1 = base.copy()
    flip = rng.choice(n, 3, replace=False)   # 3-item difference ~0.6pp
    b1[flip] = ~b1[flip]
    r1 = compare(a1, b1)
    # case 2: a LARGE consistent gap -> should be significant
    a2 = rng.random(n) < 0.90
    b2 = rng.random(n) < 0.65
    r2 = compare(a2, b2)
    print("tiny gap :", r1["verdict"], "p=", round(r1["mcnemar"]["p_value"], 4), r1["bootstrap_ci"]["obs_diff"])
    print("big  gap :", r2["verdict"], "p=", round(r2["mcnemar"]["p_value"], 6), r2["bootstrap_ci"]["obs_diff"])
    assert r1["verdict"] == "NOT_SIGNIFICANT", r1
    assert r2["verdict"] == "SIGNIFICANT_DIFFERENCE", r2
    print("signif_verify smoke: PASS")
