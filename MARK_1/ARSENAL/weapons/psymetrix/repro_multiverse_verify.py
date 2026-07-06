#!/usr/bin/env python3
"""P-REPRO + P-MULTIVERSE — reproduce a published effect from open data and stress
it across the analytic multiverse (specification curve; Simonsohn, Simmons & Nelson
2020 "Specification Curve Analysis", Nat. Hum. Behav.).

P-REPRO certifies a statistic by RE-COMPUTING it two INDEPENDENT ways (statsmodels
GLM vs a hand-rolled numpy IRLS/normal-equations solver): if the two agree to
tolerance, the reported number is machine-reproduced — no trust in either path
alone. Optionally also checks the recomputed value against a stated published value.

P-MULTIVERSE enumerates the defensible analytic forks (outcome operationalization,
covariate sets, sample exclusions), fits the focal effect under EACH, and reports
the distribution: % significant, sign consistency, median effect, and a robustness
verdict. The significant specs' p-values feed p-curve (forensics) for evidential value.

HONESTY (non-waivable): reproduction != truth; a robust effect across the multiverse
is NOT proven causal or true — it is "not an artifact of the analytic choices tested."
A FRAGILE effect (dies under the multiverse) is the primary valuable output. We
certify CONSISTENCY / ROBUSTNESS, never TRUTH.

Each function has an adversarial _selftest: a robust true effect SURVIVES; a null
effect is correctly shown FRAGILE; the dual-path reproduction agrees on known data.
"""
import sys, os, json, warnings, itertools
import numpy as np
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import forensics_verify as F


# --------------------------------------------------------------------------- #
#  Independent (numpy) solvers — the SECOND path for reproduction
# --------------------------------------------------------------------------- #
def _design(X):
    X = np.asarray(X, float)
    return np.column_stack([np.ones(len(X)), X])


def _ols_np(X, y):
    Xd = _design(X)
    beta, *_ = np.linalg.lstsq(Xd, np.asarray(y, float), rcond=None)
    return beta


def _logit_irls_np(X, y, iters=100, tol=1e-10):
    """Maximum-likelihood logistic regression via Newton-Raphson / IRLS (independent
    of statsmodels). Returns the coefficient vector incl. intercept."""
    Xd = _design(X); y = np.asarray(y, float)
    beta = np.zeros(Xd.shape[1])
    for _ in range(iters):
        eta = np.clip(Xd @ beta, -30, 30)
        mu = 1.0 / (1.0 + np.exp(-eta))
        W = np.clip(mu * (1 - mu), 1e-9, None)
        H = (Xd.T * W) @ Xd
        g = Xd.T @ (y - mu)
        step = np.linalg.solve(H, g)
        beta = beta + step
        if np.max(np.abs(step)) < tol:
            break
    return beta


# --------------------------------------------------------------------------- #
#  P-REPRO : reproduce a focal coefficient two independent ways
# --------------------------------------------------------------------------- #
def reproduce_coefficient(data, outcome, predictors, focal, family="logit",
                          claimed=None, tol=1e-4):
    """Fit `outcome ~ predictors` two ways (statsmodels GLM + numpy) and certify the
    focal coefficient is reproduced. data: DataFrame; predictors: list incl. focal."""
    import statsmodels.api as sm
    X = data[predictors].to_numpy(float)
    y = data[outcome].to_numpy(float)
    fidx = predictors.index(focal) + 1                 # +1 for intercept column
    if family == "logit":
        sm_res = sm.GLM(y, sm.add_constant(X), family=sm.families.Binomial()).fit()
        np_beta = _logit_irls_np(X, y)
    elif family == "ols":
        sm_res = sm.OLS(y, sm.add_constant(X)).fit()
        np_beta = _ols_np(X, y)
    else:
        raise ValueError("family must be 'logit' or 'ols'")
    sm_coef = float(sm_res.params[fidx]); np_coef = float(np_beta[fidx])
    p = float(sm_res.pvalues[fidx])
    dual_ok = abs(sm_coef - np_coef) < tol
    matches_claimed = None if claimed is None else abs(sm_coef - claimed) < max(tol, 5e-3)
    return {"test": "P-REPRO", "focal": focal, "family": family,
            "coef_statsmodels": round(sm_coef, 6), "coef_numpy_independent": round(np_coef, 6),
            "p_value": p, "dual_path_agree": bool(dual_ok),
            "claimed_value": claimed, "matches_claimed": matches_claimed,
            "reproduced": bool(dual_ok and (matches_claimed in (None, True))),
            "note": ("REPRODUCED: two independent computations agree"
                     + ("" if claimed is None else
                        (" and match the stated value" if matches_claimed else
                         " but DIVERGE from the stated value (check the spec/value)"))
                     + ". Reproduction != truth." if dual_ok else
                     "NOT reproduced: the two independent paths DISAGREE — a numerical/spec bug.")}


# --------------------------------------------------------------------------- #
#  P-MULTIVERSE : specification curve over the defensible analytic forks
# --------------------------------------------------------------------------- #
def specification_curve(data, focal, outcome_options, covariate_pool,
                        exclusion_options=None, family="logit", max_specs=512):
    """Enumerate the multiverse and fit the focal effect under each spec.

    outcome_options: dict name -> column (different operationalizations of the DV).
    covariate_pool : list of covariate columns; every SUBSET is a spec (the focal
                     predictor is always included).
    exclusion_options: dict name -> boolean-mask function(data)->mask (sample forks).
    """
    import statsmodels.api as sm
    if exclusion_options is None:
        exclusion_options = {"full sample": (lambda d: np.ones(len(d), bool))}
    subsets = []
    for r in range(len(covariate_pool) + 1):
        subsets.extend(itertools.combinations(covariate_pool, r))
    specs = []
    for oname, ocol in outcome_options.items():
        for ename, emask in exclusion_options.items():
            for cov in subsets:
                specs.append((oname, ocol, ename, emask, list(cov)))
    if len(specs) > max_specs:
        raise ValueError(f"{len(specs)} specs exceeds max_specs={max_specs}; narrow the forks.")

    coefs, pvals, rows = [], [], []
    for oname, ocol, ename, emask, cov in specs:
        d = data[emask(data)]
        preds = [focal] + cov
        if len(d) < len(preds) + 2:           # too few rows (incl. empty mask) -> skip
            continue
        try:
            X = sm.add_constant(d[preds].to_numpy(float))
            y = d[ocol].to_numpy(float)
            if family == "logit":
                res = sm.GLM(y, X, family=sm.families.Binomial()).fit()
            else:
                res = sm.OLS(y, X).fit()
            c = float(res.params[1]); p = float(res.pvalues[1])
        except Exception:
            continue
        coefs.append(c); pvals.append(p)
        rows.append({"outcome": oname, "exclusion": ename, "n_covariates": len(cov),
                     "coef": round(c, 4), "p": round(p, 5)})
    coefs = np.array(coefs); pvals = np.array(pvals)
    n = len(coefs)
    if n == 0:                                          # audit C1: zero-spec guard
        return {"test": "P-MULTIVERSE", "focal": focal, "n_specifications": 0,
                "robustness_verdict": None,
                "note": "UNDEFINED: no specification converged (check the data, outcome columns, "
                        "and exclusion masks — an all-False mask yields zero specs). ABSTAIN."}
    med = float(np.median(coefs))
    sign_med = np.sign(med)
    pct_sig = float(np.mean(pvals < 0.05))
    pct_sig_samesign = float(np.mean((pvals < 0.05) & (np.sign(coefs) == sign_med)))
    pct_samesign = float(np.mean(np.sign(coefs) == sign_med))
    # effect-SIZE dispersion (audit C5: significance alone is near-automatic at large n;
    # report the spread of the estimate so the reader judges stability, not just p<.05)
    coef_std = float(np.std(coefs, ddof=1)) if n > 1 else 0.0
    coef_cv = float(coef_std / abs(med)) if med != 0 else None
    # robustness verdict: dominant-sign AND a majority of specs significant in that sign
    robust = (pct_samesign >= 0.95) and (pct_sig_samesign >= 0.50)
    fragile = pct_sig < 0.10
    verdict = "robust" if robust else "fragile" if fragile else "mixed"
    # evidential value of the significant specs (p-curve, from forensics) — WITH the
    # non-independence caveat surfaced in the OUTPUT, not just the prediction doc (C4)
    sig_ps = [float(p) for p in pvals if p < 0.05]
    pcurve = F.pcurve(sig_ps) if len(sig_ps) >= 2 else {"evidential_value": None}
    caveats = [
        "ROBUST != TRUE/CAUSAL: a robust verdict means the effect is not an artifact of the "
        "analytic choices TESTED — not that it is causally true (esp. observational data).",
        "CONDITIONAL ON THE COVARIATE POOL: the verifier cannot certify the pool is complete; "
        "omitting a real confounder (omitted-variable bias) can make even a NULL effect look "
        "robust. The pool must be defensibly exhaustive — that is the analyst's burden, not checkable here.",
        "P-CURVE ASSUMES INDEPENDENT TESTS: these specs are NESTED, non-independent subsets of one "
        "dataset, so their p-values are highly correlated — pcurve_evidential_value here is "
        "ILLUSTRATIVE, not a valid independent-evidence test.",
    ]
    if pct_sig >= 0.99 and n >= 5:
        caveats.append(f"LARGE-N SIGNIFICANCE: {int(pct_sig*100)}% of specs are significant — at large "
                       "n almost any nonzero effect is. Judge robustness by the SIGN stability and the "
                       f"effect-size spread (coef CV={round(coef_cv,3) if coef_cv is not None else None}), "
                       "NOT by the significance rate alone.")
    return {"test": "P-MULTIVERSE", "focal": focal, "n_specifications": int(n),
            "median_coef": round(med, 4),
            "coef_min": round(float(coefs.min()), 4), "coef_max": round(float(coefs.max()), 4),
            "coef_std": round(coef_std, 4), "coef_cv": None if coef_cv is None else round(coef_cv, 4),
            "pct_significant": round(pct_sig, 3),
            "pct_same_sign_as_median": round(pct_samesign, 3),
            "pct_significant_in_dominant_sign": round(pct_sig_samesign, 3),
            "robustness_verdict": verdict,
            "pcurve_evidential_value": pcurve.get("evidential_value"),
            "pcurve_caveat": "specs are non-independent (nested subsets) -> illustrative only",
            "caveats": caveats,
            "note": {"robust": "ROBUST: sign-stable across the multiverse and significant in a "
                               "majority of specs — NOT an artifact of the analytic choices TESTED "
                               "(see caveats: conditional on a complete covariate pool). Robust != true.",
                     "fragile": "FRAGILE: the effect largely VANISHES across the multiverse "
                                "(<10% of specs significant) — it depends on specific analytic "
                                "choices. This is the primary valuable finding.",
                     "mixed": "MIXED: sign-stable or partly significant but not robust across the "
                              "multiverse — report the distribution, claim no headline."}[verdict],
            "specs": rows}


# --------------------------------------------------------------------------- #
#  Synthetic data (machine ground truth for the self-tests)
# --------------------------------------------------------------------------- #
def _gen(n, beta_focal, seed=0, confound=True):
    """Generate data with a KNOWN focal log-odds effect. confound=True correlates
    some covariates with the focal (a realistic multiverse where omitting a
    confounder biases the focal); confound=False makes covariates independent (so a
    null effect is cleanly non-significant — no omitted-variable artifact)."""
    import pandas as pd
    rng = np.random.default_rng(seed)
    focal = rng.standard_normal(n)
    c1 = (0.5 * focal if confound else 0.0) + rng.standard_normal(n)
    c2 = rng.standard_normal(n)
    c3 = (0.3 * focal if confound else 0.0) + rng.standard_normal(n)
    eta = beta_focal * focal + 0.4 * c1 - 0.3 * c2
    p = 1.0 / (1.0 + np.exp(-eta))
    y = (rng.random(n) < p).astype(int)
    y2 = (rng.random(n) < (p * 0.8 + 0.1)).astype(int)   # a noisier DV operationalization
    return pd.DataFrame({"focal": focal, "c1": c1, "c2": c2, "c3": c3,
                         "y": y, "y2": y2, "grp": (c2 > 0).astype(int)})


# --------------------------------------------------------------------------- #
#  Adversarial self-test
# --------------------------------------------------------------------------- #
def _selftest():
    # ---- dual-path reproduction agrees on known data (logit + ols) ----
    d = _gen(2000, beta_focal=1.0, seed=1)
    rep = reproduce_coefficient(d, "y", ["focal", "c1", "c2"], "focal", family="logit")
    assert rep["dual_path_agree"] and rep["reproduced"], f"dual-path logit must agree: {rep}"
    rep_ols = reproduce_coefficient(d, "focal", ["c1", "c2", "c3"], "c1", family="ols")
    assert rep_ols["dual_path_agree"], f"dual-path OLS must agree: {rep_ols}"
    # a wrong claimed value is caught
    repc = reproduce_coefficient(d, "y", ["focal", "c1"], "focal", family="logit", claimed=99.0)
    assert repc["matches_claimed"] is False, "a wrong claimed value must NOT match"

    # ---- multiverse: a REAL effect survives ----
    outc = {"y": "y", "y2": "y2"}
    excl = {"full": (lambda x: np.ones(len(x), bool)),
            "grp1": (lambda x: x["grp"].to_numpy() == 1)}
    mv_real = specification_curve(d, "focal", outc, ["c1", "c2", "c3"], excl, family="logit")
    assert mv_real["robustness_verdict"] == "robust", f"true effect must be robust: {mv_real['robustness_verdict']}, {mv_real['pct_significant']}"
    assert mv_real["pct_same_sign_as_median"] >= 0.95

    # ---- multiverse: a NULL effect (no confounding) is shown FRAGILE ----
    d0 = _gen(2000, beta_focal=0.0, seed=2, confound=False)
    mv_null = specification_curve(d0, "focal", outc, ["c1", "c2", "c3"], excl, family="logit")
    assert mv_null["robustness_verdict"] == "fragile", \
        f"null effect must be fragile, got {mv_null['robustness_verdict']} ({mv_null['pct_significant']})"

    # ---- audit C6: the DANGEROUS case — a true NULL WITH confounding. When the
    # confounder is IN the pool, the verifier must NOT certify it robust (the forks
    # that include the confounder break the spurious effect). Locks the failure mode
    # the original selftest skipped.
    dN = _gen(2000, beta_focal=0.0, seed=5, confound=True)
    mv_confnull = specification_curve(dN, "focal", outc, ["c1", "c2", "c3"], excl, family="logit")
    assert mv_confnull["robustness_verdict"] != "robust", \
        f"true null (confounder in pool) must NOT be 'robust': {mv_confnull['robustness_verdict']}"

    # ---- audit C1: zero specs (all-False mask) -> ABSTAIN, not crash ----
    empty = {"none": (lambda x: np.zeros(len(x), bool))}
    mv_empty = specification_curve(d, "focal", outc, ["c1"], empty, family="logit")
    assert mv_empty["robustness_verdict"] is None, "all-False mask must abstain (no crash)"

    # ---- audit C3/C4/C5: the load-bearing caveats must be in the OUTPUT ----
    cav = " ".join(mv_real["caveats"]).lower()
    assert "robust != true" in cav and "omitted-variable" in cav and "non-independent" in cav, \
        "robust!=true, OVB, and p-curve-non-independence caveats must be in the output"

    print("repro_multiverse_verify selftest: PASS "
          "(dual-path reproduction agrees + catches wrong claim; real effect survives the "
          "multiverse; null effect fragile; confounded-null not certified robust; empty mask "
          "abstains; honesty caveats present in output)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: repro_multiverse_verify.py selftest")
