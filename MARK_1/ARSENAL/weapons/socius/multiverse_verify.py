#!/usr/bin/env python3
"""S-MULTIVERSE — frozen verifier for ROBUSTNESS TO ANALYTIC CHOICES (kappa = 1).

Specification-curve analysis (Simonsohn, Simmons & Nelson, 2020, Nature Human
Behaviour 4:1208-1214) / multiverse analysis (Steegen, Tuerlinckx, Gelman &
Vanpaemel, 2016, Perspectives on Psychological Science 11:702-712).

The single biggest, most documented failure mode in quantitative social science
is a finding that is an artifact of ONE arbitrary analytic path. This verifier
takes a dataset and a *grid* of defensible-but-arbitrary analytic choices
(covariate sets, subsample filters, outcome/predictor operationalisations),
ENUMERATES THE FULL PRODUCT (the producer cannot cherry-pick a path), fits the
focal model in every cell, and reports the distribution of the focal effect.

Frozen / non-gameable: the engine, not the analyst, decides which specifications
exist (exhaustive product) and runs all of them. A finding "survives" only if it
is significant in the hypothesised direction across a stated share of the
multiverse AND its sign is stable. The verdict can FAIL (and is designed to fail
on a null finding that one lucky spec made significant) — see _selftest.

Honest ceiling: robust != true. Surviving the multiverse means the result is not
an artifact of analytic choice; it can still be confounded (-> S-CAUSAL),
mis-measured (-> S-MEASURE) or non-generalisable (-> S-SAMPLE).
"""
import sys, json, itertools
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


def summarize_speccurve(pvals, coefs, hyp_sign=1, alpha=0.05,
                        share_threshold=0.5, sign_stability_threshold=0.95):
    """FROZEN verdict logic for a realised specification curve.

    Given the focal p-values and coefficients from an ALREADY-ENUMERATED
    multiverse (the data-processing grid may be domain-specific, e.g. the Durante
    fertility recodes), apply the single robustness rule used everywhere in
    SOCIUS so the demo and the generic engine cannot diverge. A finding is robust
    iff a majority of specifications are significant IN THE HYPOTHESISED DIRECTION
    AND the coefficient sign is stable AND the dominant sign matches the hypothesis.
    """
    p = np.asarray(pvals, dtype=float); b = np.asarray(coefs, dtype=float)
    n = len(p)
    if n == 0:
        return {"sub_weapon": "S-MULTIVERSE", "kappa": 1, "n_specs": 0,
                "robust": False, "reason": "no specifications ran"}
    share_sig = float(np.mean(p < alpha))
    share_sig_hyp = float(np.mean((p < alpha) & (np.sign(b) == hyp_sign)))
    pos = float(np.mean(b > 0)); neg = float(np.mean(b < 0))
    sign_stability = max(pos, neg)
    dominant_sign = 1 if pos >= neg else -1
    robust = (share_sig_hyp >= share_threshold
              and sign_stability >= sign_stability_threshold
              and dominant_sign == hyp_sign)
    return {
        "sub_weapon": "S-MULTIVERSE", "kappa": 1, "n_specs": n,
        "median_coef": float(np.median(b)),
        "coef_range": [float(b.min()), float(b.max())],
        "share_significant": share_sig,
        "share_significant_hyp_direction": share_sig_hyp,
        "sign_stability": sign_stability,
        "dominant_sign": dominant_sign, "hyp_sign": hyp_sign,
        "decision_rule": f"robust iff share_sig_hyp>={share_threshold} AND "
                         f"sign_stability>={sign_stability_threshold} AND dominant_sign==hyp_sign",
        "robust": bool(robust),
        "ceiling_note": "Robust to analytic choice != true. A surviving finding "
                        "can still be confounded, mis-measured, or non-generalisable.",
    }


def run_multiverse(df, outcome, focal, choices, hyp_sign=1, alpha=0.05,
                   share_threshold=0.5, sign_stability_threshold=0.95):
    """Enumerate the full specification grid and summarise the focal effect.

    choices: dict of independent analytic-choice dimensions, e.g.
        {"covariates": [[], ["age"], ["age","educ"]],
         "subsample":  [None, ("region","==","north")],
         "outcome_tf": [None, "log"]}
    Each dimension is a list of options; the multiverse is their Cartesian product.
    hyp_sign: +1 or -1, the hypothesised sign of the focal coefficient.
    """
    dims = list(choices.keys())
    grids = [choices[d] for d in dims]
    specs = list(itertools.product(*grids))
    rows = []
    for combo in specs:
        opt = dict(zip(dims, combo))
        d = df.copy()
        # subsample
        sub = opt.get("subsample")
        if sub is not None:
            col, op, val = sub
            if op == "==":
                d = d[d[col] == val]
            elif op == "!=":
                d = d[d[col] != val]
            elif op == ">":
                d = d[d[col] > val]
            elif op == "<":
                d = d[d[col] < val]
        y = outcome
        # outcome transform
        tf = opt.get("outcome_tf")
        if tf == "log":
            d = d[d[outcome] > 0]
            d["_y_tf"] = np.log(d[outcome]); y = "_y_tf"
        elif tf == "rank":
            d["_y_tf"] = d[outcome].rank(); y = "_y_tf"
        covs = opt.get("covariates", [])
        rhs = " + ".join([focal] + list(covs)) if covs else focal
        formula = f"{y} ~ {rhs}"
        if len(d) < (len(covs) + 3):
            continue
        try:
            res = smf.ols(formula, data=d).fit()
            b = res.params.get(focal, np.nan)
            p = res.pvalues.get(focal, np.nan)
        except Exception:
            continue
        if np.isnan(b) or np.isnan(p):
            continue
        rows.append({"spec": opt, "coef": float(b), "p": float(p),
                     "sig": bool(p < alpha),
                     "sig_hyp_dir": bool(p < alpha and np.sign(b) == hyp_sign)})
    if not rows:
        return {"sub_weapon": "S-MULTIVERSE", "kappa": 1, "n_specs": 0,
                "robust": False, "reason": "no specifications ran"}
    return summarize_speccurve([r["p"] for r in rows], [r["coef"] for r in rows],
                               hyp_sign=hyp_sign, alpha=alpha,
                               share_threshold=share_threshold,
                               sign_stability_threshold=sign_stability_threshold)


def _make_robust_data(seed=0):
    rng = np.random.default_rng(seed)
    n = 400
    x = rng.normal(size=n)
    age = rng.normal(size=n); educ = rng.normal(size=n)
    region = rng.choice(["north", "south"], size=n)
    y = 0.8 * x + 0.2 * age + 0.1 * educ + rng.normal(size=n)  # TRUE strong effect
    return pd.DataFrame({"y": y - y.min() + 1, "x": x, "age": age,
                         "educ": educ, "region": region})


def _make_fragile_data(seed=0):
    rng = np.random.default_rng(seed)
    n = 400
    x = rng.normal(size=n)
    age = rng.normal(size=n); educ = rng.normal(size=n)
    region = rng.choice(["north", "south"], size=n)
    y = 0.0 * x + rng.normal(size=n)  # NO true effect — a null finding
    return pd.DataFrame({"y": y - y.min() + 1, "x": x, "age": age,
                         "educ": educ, "region": region})


def _selftest():
    choices = {
        "covariates": [[], ["age"], ["educ"], ["age", "educ"]],
        "subsample": [None, ("region", "==", "north"), ("region", "==", "south")],
        "outcome_tf": [None, "rank"],
    }
    rob = run_multiverse(_make_robust_data(), "y", "x", choices, hyp_sign=1)
    assert rob["robust"] is True, rob
    assert rob["share_significant_hyp_direction"] >= 0.8, rob
    # Known-FRAGILE: a true-null finding must NOT survive the multiverse
    #   (the verifier must be able to FAIL — this is the p-hacked-finding test)
    frag = run_multiverse(_make_fragile_data(), "y", "x", choices, hyp_sign=1)
    assert frag["robust"] is False, frag
    assert frag["share_significant_hyp_direction"] < 0.3, frag
    print(f"multiverse_verify selftest: PASS "
          f"(robust finding survives {rob['share_significant_hyp_direction']:.0%} of specs; "
          f"null finding dies at {frag['share_significant_hyp_direction']:.0%})")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: multiverse_verify.py selftest  (programmatic API: run_multiverse)")
