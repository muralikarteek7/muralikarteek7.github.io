#!/usr/bin/env python3
"""P-MODEL (full) — the executable psychometric MODEL engine for PSYMETRIX.

Fits and COMPARES latent-variable models and reports fit against grounded cutoffs:
  - CFA / SEM (semopy): CFI / TLI / RMSEA / SRMR / chi2-df + a fit verdict
  - model comparison (the discriminating test): does the claimed structure fit
    BETTER than a misspecified alternative? (delta-CFI etc.)
  - EFA dimensionality (factor_analyzer): Kaiser + Horn/Glorfeld parallel analysis
  - McDonald's omega (from the 1-factor congeneric loadings) vs Cronbach alpha
  - IRT 2PL (girth): item discrimination/difficulty + TEST INFORMATION + SE(theta)
  - local dependence: Yen's Q3 (residual correlations after conditioning on theta)

GROUNDED cutoffs (see GROUNDING_MODEL.md, fetched not asserted):
  Hu & Bentler (1999) GOOD fit: CFI>=.95 AND RMSEA<=.06 AND SRMR<=.08 (joint).
  Two-tier ACCEPTABLE: CFI>=.90, RMSEA<=.08, SRMR<=.10.
  Invariance: dCFI<=.01 (Cheung-Rensvold 2002), dRMSEA<=.015 (Chen 2007); RMSEA
  unreliable at small df (Kenny-Kaniskan-McCoach 2015) -> lean on dCFI there.
  Yen's Q3 local dependence: |Q3 - mean(Q3)| > 0.2 (Chen-Thissen; mean-corrected).
  Parallel analysis: Glorfeld (1995) 95th-percentile reference.

HONESTY (non-waivable): this certifies FIT / DIMENSIONALITY / CONSISTENCY, NEVER
TRUTH. A model that fits is NOT "the right theory" — at best it is "not rejected,
and better than the alternatives tested." Fit cutoffs are benchmarks, NOT golden
rules (Marsh, Hau & Wen 2004); the verifier reports the numbers and the verdict
relative to them, it does not pretend a passing model is true.

Every function has an adversarial _selftest: a correctly-specified model on clean
data PASSES; a misspecified model is CAUGHT (worse fit, flagged).
"""
import sys, json, warnings
import numpy as np
warnings.filterwarnings("ignore")

GOOD = {"CFI": 0.95, "RMSEA": 0.06, "SRMR": 0.08}
ACCEPTABLE = {"CFI": 0.90, "RMSEA": 0.08, "SRMR": 0.10}


# --------------------------------------------------------------------------- #
#  CFA / SEM via semopy  (+ hand-computed SRMR, cross-checked vs lavaan)
# --------------------------------------------------------------------------- #
def _srmr(model):
    """Standardized Root Mean Square Residual from the fitted semopy model."""
    sigma, _ = model.calc_sigma()
    obs = model.mx_cov                       # sample covariance semopy used
    d = np.sqrt(np.diag(obs))
    Rs = obs / np.outer(d, d)                # sample correlation
    Ri = sigma / np.outer(d, d)              # implied correlation
    p = obs.shape[0]
    resid = Rs - Ri
    idx = np.tril_indices(p)                 # incl. diagonal (lavaan convention)
    return float(np.sqrt((resid[idx] ** 2).sum() / (p * (p + 1) / 2)))


def _validate_cfa_input(data):
    """Guard inputs before fitting (caught by the cross-model audit, 2026-06-20):
    NaNs and zero-variance columns silently corrupt the fit. Return an abstain dict
    if the data is unfit, else None."""
    import pandas as pd
    df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    nan_n = int(df.isna().sum().sum())
    if nan_n > 0:
        return {"test": "CFA/SEM", "fit_verdict": None, "n_missing": nan_n,
                "note": f"UNDEFINED: {nan_n} missing value(s) — handle NaNs (listwise/FIML) "
                        "before fitting; ABSTAIN rather than fit silently-imputed data."}
    zero_var = [c for c in df.columns if float(df[c].var(ddof=1)) <= 1e-12]
    if zero_var:
        return {"test": "CFA/SEM", "fit_verdict": None, "constant_columns": zero_var,
                "note": f"UNDEFINED: zero-variance column(s) {zero_var} — covariance is "
                        "singular; ABSTAIN (cannot fit)."}
    # Bartlett's test of sphericity — the standard precondition for factor analysis
    # (audit D1): if the correlation matrix is indistinguishable from identity, there
    # is NO covariance structure to model and CFA fit indices are meaningless. On
    # random noise this fires; on real factorable data (HS: p~1e-166) it passes.
    from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
    _chi, bart_p = calculate_bartlett_sphericity(df)
    if not np.isfinite(bart_p) or bart_p > 0.05:
        return {"test": "CFA/SEM", "fit_verdict": None,
                "bartlett_p": None if not np.isfinite(bart_p) else round(float(bart_p), 4),
                "note": "UNDEFINED: data is NOT factorable — the correlation matrix is "
                        "indistinguishable from identity (Bartlett's test p>0.05), so CFA "
                        "fit indices are uninterpretable. ABSTAIN (no structure to model)."}
    return None


def cfa_fit(data, model_spec):
    """Fit a CFA/SEM model; return fit indices + a verdict vs grounded cutoffs."""
    from semopy import Model, calc_stats
    bad = _validate_cfa_input(data)
    if bad is not None:
        return bad
    m = Model(model_spec)
    m.fit(data)
    s = calc_stats(m)
    cfi = float(s["CFI"].iloc[0]); tli = float(s["TLI"].iloc[0])
    rmsea = float(s["RMSEA"].iloc[0]); chi2 = float(s["chi2"].iloc[0])
    dof = float(s["DoF"].iloc[0]); srmr = _srmr(m)
    # DEGENERACY GUARD (audit D1): on noise / over-parameterized data semopy can
    # return CFI far outside [0,1] (observed -9.7 .. 102.5). Those values are
    # NUMERICALLY MEANINGLESS — never let one tier as "good". Detect and ABSTAIN.
    raw_cfi = cfi
    degenerate = (not (-0.001 <= raw_cfi <= 1.001)) or dof <= 0 or not np.isfinite(rmsea)
    cfi = min(1.0, max(0.0, raw_cfi)); tli = min(1.0, max(0.0, tli))  # clamp for display
    if degenerate:
        return {"test": "CFA/SEM", "CFI_raw": round(raw_cfi, 4), "RMSEA": round(rmsea, 4)
                if np.isfinite(rmsea) else None, "df": int(dof), "degenerate_fit": True,
                "fit_verdict": None,
                "note": "UNDEFINED/DEGENERATE: fit statistics are numerically out of range "
                        "(CFI outside [0,1] or df<=0) — the model is over-parameterized "
                        "relative to the data, or the covariance is not positive-definite. "
                        "ABSTAIN; a degenerate fit is NEVER reported as good."}
    # PER-INDEX tiers, then a holistic verdict that does NOT auto-fail on a single
    # index (Marsh, Hau & Wen 2004). "mixed" = the indices DISAGREE (e.g. Holzinger-
    # Swineford: CFI acceptable, SRMR good, RMSEA poor) — reported honestly, not
    # collapsed to "poor" (which would erase a large advantage over the alternative).
    def tier(val, good_cut, acc_cut, higher_better):
        if higher_better:
            return "good" if val >= good_cut else "acceptable" if val >= acc_cut else "poor"
        return "good" if val <= good_cut else "acceptable" if val <= acc_cut else "poor"
    tiers = {"CFI": tier(cfi, GOOD["CFI"], ACCEPTABLE["CFI"], True),
             "RMSEA": tier(rmsea, GOOD["RMSEA"], ACCEPTABLE["RMSEA"], False),
             "SRMR": tier(srmr, GOOD["SRMR"], ACCEPTABLE["SRMR"], False)}
    vals = list(tiers.values())
    if all(t == "good" for t in vals):
        verdict = "good"
    elif all(t != "poor" for t in vals):
        verdict = "acceptable"
    elif all(t == "poor" for t in vals):
        verdict = "poor"
    else:
        verdict = "mixed"
    notes = {"good": "FITS by joint Hu&Bentler good-fit (CFI>=.95, RMSEA<=.06, SRMR<=.08)",
             "acceptable": "ACCEPTABLE fit (two-tier convention; no index in the poor range)",
             "mixed": "MIXED — fit indices DISAGREE (some acceptable/good, at least one poor); "
                      "report all, do NOT auto-fail on one index (Marsh 2004). NOT the same as uniformly poor",
             "poor": "POOR fit: every conventional index rejects the model"}
    return {"test": "CFA/SEM", "CFI": round(cfi, 4), "TLI": round(tli, 4),
            "RMSEA": round(rmsea, 4), "SRMR": round(srmr, 4),
            "chi2": round(chi2, 3), "df": int(dof),
            "chi2_df": round(chi2 / dof, 3) if dof else None,
            "index_tiers": tiers, "fit_verdict": verdict,
            "note": notes[verdict] + " — fit != truth; cutoffs are benchmarks, not golden rules."}


def compare_models(data, spec_better, spec_worse, label_better="A", label_worse="B"):
    """The discriminating test: does spec_better fit better than spec_worse?
    Reports delta-CFI / delta-RMSEA and which model the data prefer."""
    a = cfa_fit(data, spec_better)
    b = cfa_fit(data, spec_worse)
    dcfi = a["CFI"] - b["CFI"]
    drmsea = b["RMSEA"] - a["RMSEA"]
    prefers = label_better if a["CFI"] > b["CFI"] else label_worse
    return {"test": "model_comparison", label_better: a, label_worse: b,
            "delta_CFI": round(dcfi, 4), "delta_RMSEA": round(drmsea, 4),
            "data_prefer": prefers,
            "note": f"data prefer model {prefers}; delta-CFI={dcfi:+.3f}. A model winning "
                    "a comparison is 'less wrong than the alternative tested', not 'true'."}


# --------------------------------------------------------------------------- #
#  EFA dimensionality + omega (factor_analyzer)
# --------------------------------------------------------------------------- #
def efa_dimensionality(data, n_parallel=200, seed=0):
    """Kaiser + Glorfeld-95th parallel analysis on the correlation eigenvalues."""
    from factor_analyzer import FactorAnalyzer
    X = np.asarray(data, dtype=float)
    n, k = X.shape
    R = np.corrcoef(X, rowvar=False)
    eig = np.sort(np.linalg.eigvalsh(R))[::-1]
    rng = np.random.default_rng(seed)
    rand = np.zeros((n_parallel, k))
    for i in range(n_parallel):
        Z = rng.standard_normal((n, k))
        rand[i] = np.sort(np.linalg.eigvalsh(np.corrcoef(Z, rowvar=False)))[::-1]
    pa = np.percentile(rand, 95, axis=0)
    return {"test": "EFA_dimensionality", "n": int(n), "k_items": int(k),
            "eigenvalues": [round(float(e), 3) for e in eig],
            "kaiser_n_factors": int((eig > 1).sum()),
            "parallel_analysis_n_factors": int((eig > pa).sum()),
            "note": "Glorfeld-95 parallel analysis is the primary rule; Kaiser>1 "
                    "over-extracts. Dimensionality, not validity."}


def omega_total(data):
    """McDonald's omega-total from a 1-factor congeneric solution + Cronbach alpha.
    omega = (sum lambda)^2 / ((sum lambda)^2 + sum(1 - lambda^2)). The alpha-omega
    gap diagnoses how badly tau-equivalence (equal loadings) is violated."""
    from factor_analyzer import FactorAnalyzer
    X = np.asarray(data, dtype=float)
    Xs = (X - X.mean(0)) / X.std(0, ddof=1)
    fa = FactorAnalyzer(n_factors=1, rotation=None, method="minres")
    fa.fit(Xs)
    lam = fa.loadings_[:, 0]
    sl = lam.sum()
    omega = sl ** 2 / (sl ** 2 + (1 - lam ** 2).sum())
    # Cronbach alpha
    k = X.shape[1]
    iv = X.var(0, ddof=1); tv = X.sum(1).var(ddof=1)
    alpha = (k / (k - 1)) * (1 - iv.sum() / tv)
    return {"test": "omega_reliability", "k_items": int(k),
            "omega_total": round(float(omega), 4), "cronbach_alpha": round(float(alpha), 4),
            "alpha_omega_gap": round(float(alpha - omega), 4),
            "note": "omega preferred when loadings differ; alpha is a lower bound. "
                    "Reliability != validity."}


# --------------------------------------------------------------------------- #
#  IRT 2PL via girth: test information + SE(theta); Yen's Q3 local dependence
# --------------------------------------------------------------------------- #
def irt_2pl(item_responses):
    """item_responses: (n_items x n_persons) binary array (girth convention).
    Returns discrimination/difficulty, the test information curve, and SE(theta)."""
    from girth import twopl_mml
    R = np.asarray(item_responses)
    est = twopl_mml(R)
    a = np.asarray(est["Discrimination"], float)
    b = np.asarray(est["Difficulty"], float)
    thetas = np.linspace(-3, 3, 13)
    info = np.zeros_like(thetas)
    for ai, bi in zip(a, b):
        P = 1.0 / (1.0 + np.exp(-ai * (thetas - bi)))
        info += ai ** 2 * P * (1 - P)
    se = 1.0 / np.sqrt(info)
    return {"test": "IRT_2PL", "n_items": int(R.shape[0]),
            "discrimination": [round(float(x), 3) for x in a],
            "difficulty": [round(float(x), 3) for x in b],
            "test_information_peak": round(float(info.max()), 3),
            "theta_at_peak_info": round(float(thetas[info.argmax()]), 3),
            "min_SE_theta": round(float(se.min()), 4),
            "note": "test information = measurement precision; SE(theta)=1/sqrt(I). "
                    "Fit of the model != truth of the construct."}


def yen_q3(item_responses):
    """Yen's Q3 local-dependence check. Compute 2PL residuals r = x - P(theta),
    correlate residual pairs; flag |Q3 - mean(Q3)| > 0.2 (mean-corrected, grounded
    in Christensen 2017 / Chen-Thissen). High Q3 => items share variance beyond the
    latent trait (local independence violated)."""
    from girth import twopl_mml, ability_eap
    Ri = np.asarray(item_responses).astype(int)      # girth needs integer responses
    est = twopl_mml(Ri)
    a = np.asarray(est["Discrimination"], float)
    b = np.asarray(est["Difficulty"], float)
    theta = np.asarray(ability_eap(Ri, est["Difficulty"], est["Discrimination"]), float)
    n_items = Ri.shape[0]
    resid = np.zeros((n_items, Ri.shape[1]), float)
    for i in range(n_items):
        P = 1.0 / (1.0 + np.exp(-a[i] * (theta - b[i])))
        resid[i] = Ri[i] - P
    Q = np.corrcoef(resid)
    iu = np.triu_indices(n_items, 1)
    offdiag = Q[iu]
    mean_q3 = float(offdiag.mean())
    corrected = Q - mean_q3
    flagged = []
    for ii in range(n_items):
        for jj in range(ii + 1, n_items):
            if abs(corrected[ii, jj]) > 0.2:
                flagged.append({"items": [ii, jj], "Q3": round(float(Q[ii, jj]), 3),
                                "Q3_corrected": round(float(corrected[ii, jj]), 3)})
    return {"test": "Yen_Q3_local_dependence", "n_items": int(n_items),
            "mean_Q3": round(mean_q3, 4),
            "locally_dependent_pairs": flagged,
            "any_local_dependence": bool(flagged),
            "note": "|Q3 - mean(Q3)| > 0.2 flags a pair sharing variance beyond the "
                    "latent trait (local-independence violation), a measurement issue."}


# --------------------------------------------------------------------------- #
#  Synthetic-data generators (machine ground truth for the self-tests)
# --------------------------------------------------------------------------- #
def _gen_factor_data(n, loadings_by_factor, seed=0):
    """Generate continuous item data from a known multi-factor structure.
    loadings_by_factor: list of lists, one per factor, each = item loadings.
    Returns a DataFrame with columns x1..xk."""
    import pandas as pd
    rng = np.random.default_rng(seed)
    n_factors = len(loadings_by_factor)
    F = rng.standard_normal((n, n_factors))
    cols = {}
    idx = 1
    for f, loads in enumerate(loadings_by_factor):
        for lam in loads:
            uniq = np.sqrt(max(1e-6, 1 - lam ** 2))
            cols[f"x{idx}"] = lam * F[:, f] + uniq * rng.standard_normal(n)
            idx += 1
    return pd.DataFrame(cols)


def _gen_2pl(n_items, n_persons, a, b, seed=0):
    rng = np.random.default_rng(seed)
    theta = rng.standard_normal(n_persons)
    R = np.zeros((n_items, n_persons), int)
    for i in range(n_items):
        P = 1.0 / (1.0 + np.exp(-a[i] * (theta - b[i])))
        R[i] = (rng.random(n_persons) < P).astype(int)
    return R, theta


# --------------------------------------------------------------------------- #
#  Adversarial self-test
# --------------------------------------------------------------------------- #
def _selftest():
    # clean 3-factor data, high loadings -> correct model fits well, 1-factor fails
    loads = [[0.8, 0.78, 0.82], [0.8, 0.79, 0.81], [0.78, 0.8, 0.82]]
    data = _gen_factor_data(400, loads, seed=1)
    spec3 = "f1 =~ x1 + x2 + x3\nf2 =~ x4 + x5 + x6\nf3 =~ x7 + x8 + x9"
    spec1 = "f =~ x1 + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9"
    fit3 = cfa_fit(data, spec3)
    fit1 = cfa_fit(data, spec1)
    assert fit3["fit_verdict"] == "good", f"correct 3-factor should fit well: {fit3}"
    assert fit1["fit_verdict"] == "poor", f"misspecified 1-factor should be POOR: {fit1}"
    cmp = compare_models(data, spec3, spec1, "3factor", "1factor")
    assert cmp["data_prefer"] == "3factor" and cmp["delta_CFI"] > 0.1, f"data must prefer 3-factor: {cmp}"

    # "mixed" verdict: indices must be allowed to DISAGREE (Marsh 2004), not collapse
    # to poor. Real Holzinger-Swineford 3-factor = CFI acceptable, SRMR good, RMSEA
    # poor -> "mixed", and crucially NOT the same label as the uniformly-poor 1-factor.
    from semopy.examples import holzinger39
    hs = holzinger39.get_data()[[f"x{i}" for i in range(1, 10)]]
    hs_fit = cfa_fit(hs, spec3)
    assert hs_fit["fit_verdict"] == "mixed", f"HS 3-factor should be 'mixed': {hs_fit}"
    assert cfa_fit(hs, spec1)["fit_verdict"] == "poor", "HS 1-factor should be uniformly poor"

    # EFA dimensionality recovers the true count
    d3 = efa_dimensionality(data, n_parallel=60)
    assert d3["parallel_analysis_n_factors"] == 3, f"PA should find 3 factors: {d3}"
    one = _gen_factor_data(400, [[0.8, 0.8, 0.8, 0.78, 0.81, 0.79]], seed=2)
    d1 = efa_dimensionality(one, n_parallel=60)
    assert d1["parallel_analysis_n_factors"] == 1, f"PA should find 1 factor: {d1}"

    # omega: high-loading congeneric scale -> high omega, close to alpha
    om = omega_total(one)
    assert om["omega_total"] > 0.85, f"high-loading scale should have high omega: {om}"
    assert abs(om["alpha_omega_gap"]) < 0.1, f"near-tau-equivalent -> small gap: {om}"

    # IRT 2PL: recovers discrimination ORDER; more info where designed
    a_true = [2.0, 1.5, 1.0, 0.6, 1.8]; b_true = [0.0, -0.5, 0.5, 1.0, -1.0]
    R, _ = _gen_2pl(5, 1500, a_true, b_true, seed=3)
    irt = irt_2pl(R)
    # highest-discrimination item (index 0) should be estimated highest
    assert np.argmax(irt["discrimination"]) == 0, f"should recover top discrimination: {irt}"

    # Yen Q3: independent items -> no local dependence; a cloned pair -> flagged
    Rind, _ = _gen_2pl(6, 1500, [1.2]*6, [0.0, 0.5, -0.5, 1.0, -1.0, 0.2], seed=4)
    q_ind = yen_q3(Rind)
    assert q_ind["any_local_dependence"] is False, f"independent items: no LD expected: {q_ind}"
    Rdep = Rind.copy(); Rdep[5] = Rind[0]            # item 5 is a clone of item 0
    q_dep = yen_q3(Rdep)
    assert q_dep["any_local_dependence"] is True, f"cloned pair must flag LD: {q_dep}"

    # ---- degeneracy + input guards (caught by the cross-model audit, 2026-06-20) ----
    import pandas as pd
    rng2 = np.random.default_rng(99)
    # random noise must NEVER be rated good/acceptable -> degenerate -> abstain
    noise = pd.DataFrame(rng2.standard_normal((120, 9)), columns=[f"x{i}" for i in range(1, 10)])
    noise_fit = cfa_fit(noise, spec3)
    assert noise_fit["fit_verdict"] is None, \
        f"random data must ABSTAIN (not factorable / degenerate), never a fit verdict: {noise_fit}"
    # constant column -> abstain, not crash
    const = pd.DataFrame({"x1": [1.0]*100, "x2": rng2.standard_normal(100),
                          "x3": rng2.standard_normal(100)})
    assert cfa_fit(const, "f =~ x1 + x2 + x3")["fit_verdict"] is None, "constant column must abstain"
    # NaN -> abstain, not silent imputation
    nan_d = data.copy(); nan_d.iloc[0, 0] = np.nan
    assert cfa_fit(nan_d, spec3)["fit_verdict"] is None, "NaN input must abstain"

    print("model_verify selftest: PASS "
          "(CFA fit+comparison, EFA dimensionality, omega, IRT-2PL info, Yen-Q3 LD "
          "pass correct models, catch misspecification, AND abstain on degenerate/bad input)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: model_verify.py selftest")
