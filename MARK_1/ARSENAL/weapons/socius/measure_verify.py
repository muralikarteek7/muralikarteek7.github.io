#!/usr/bin/env python3
"""S-MEASURE — frozen verifier for MEASUREMENT QUALITY (kappa = 1).

Two checks on latent constructs (scales/indices built from multiple items):

A. RELIABILITY
   - Cronbach's alpha = (k/(k-1)) * (1 - sum(item_var)/var(total))
   - McDonald's omega (total, unidimensional) from single-factor standardised
     loadings l_j:  omega = (sum l_j)^2 / [ (sum l_j)^2 + sum(1 - l_j^2) ]
   Conventional floors: alpha/omega >= 0.70 acceptable (Nunnally), >= 0.80 good.

B. MEASUREMENT INVARIANCE across the groups being compared (Cheung & Rensvold
   2002; Chen 2007). If a scale does not measure the same construct on the same
   scale across groups, an observed "group difference" can be a pure measurement
   artifact. We fit a multigroup single-factor CFA in three nested steps and use
   the conventional change-in-fit cutoffs:
       configural : same factor pattern, all parameters free per group (baseline)
       metric     : loadings constrained equal across groups
       scalar     : loadings AND intercepts constrained equal across groups
   Invariance at a step HOLDS iff, relative to the previous step,
       Delta CFI >= -0.010  AND  Delta RMSEA <= 0.015   (Chen 2007).
   A "group difference" in means is trustworthy only if SCALAR invariance holds.

Frozen / independent: fit is by maximum likelihood on the group covariance/mean
structure; the verdict is a deterministic function of the fitted fit indices. The
verifier can FAIL — fed a scale with real differential item functioning it must
reject scalar (and possibly metric) invariance. See _selftest.

KNOWN BLIND SPOT (disclosed by independent audit, 2026-06-20). The ΔCFI-primary
rule with the small-df RMSEA guard (see measurement_invariance) genuinely MUTES
sensitivity to SUBTLE metric non-invariance on SHORT scales (3 items -> metric
df=2, scalar df=4, both below rmsea_min_df). The auditor measured, on 3-item
scales (n=800, 30 seeds), the detection rate for a single deviant loading:
    loading gap 0.10 -> ~3% detected | 0.15 -> ~30% | 0.20 -> ~70% | 0.30 -> 100%.
LARGE DIF is still caught (the 5-item DIF self-test: ΔCFI_scalar=-0.27); intercept
shifts >=0.5 SD are caught 100%. But a small loading difference on a short scale
can pass undetected. This is the price of the Kenny et al. (2015) guard that stops
RMSEA from FALSELY rejecting good 3-item models. Mitigation: for short scales,
treat a 'passed' metric verdict as 'no GROSS non-invariance detected', not proof
of fine-grained equivalence; prefer >=4-5 items where df permits binding RMSEA.

Honest ceiling (kappa=1 on the statistics, but): passing invariance means the
scale behaves equivalently across these groups on these items — it does NOT prove
the scale is valid (measures the intended construct). Validity is kappa=0 -> armor.
"""
import sys, json
import numpy as np
from scipy import optimize


# ----------------------------- reliability --------------------------------- #
def cronbach_alpha(X):
    """X: n x k array of item scores (rows = respondents)."""
    X = np.asarray(X, dtype=float)
    k = X.shape[1]
    item_var = X.var(axis=0, ddof=1)
    total_var = X.sum(axis=1).var(ddof=1)
    return float((k / (k - 1)) * (1 - item_var.sum() / total_var))


def _one_factor_loadings(X):
    """Standardised single-factor loadings via iterated principal-axis factoring
    on the correlation matrix (communalities = SMC, 25 iterations)."""
    R = np.corrcoef(X, rowvar=False)
    p = R.shape[0]
    Rinv = np.linalg.pinv(R)
    h2 = 1 - 1.0 / np.diag(Rinv)            # squared multiple correlations
    for _ in range(50):
        Rh = R.copy()
        np.fill_diagonal(Rh, h2)
        w, v = np.linalg.eigh(Rh)
        idx = np.argmax(w)
        lam = v[:, idx] * np.sqrt(max(w[idx], 1e-9))
        if lam.sum() < 0:
            lam = -lam
        h2_new = np.clip(lam ** 2, 0, 1)
        if np.max(np.abs(h2_new - h2)) < 1e-7:
            h2 = h2_new; break
        h2 = h2_new
    return np.clip(lam, -0.999, 0.999)


def mcdonald_omega(X):
    lam = _one_factor_loadings(X)
    sl = lam.sum()
    uniq = np.sum(1 - lam ** 2)
    return float(sl ** 2 / (sl ** 2 + uniq))


# ------------------------- multigroup 1-factor CFA -------------------------- #
def _model_implied(lam, theta, nu, alpha, phi):
    Sigma = phi * np.outer(lam, lam) + np.diag(theta)
    mu = nu + lam * alpha
    return Sigma, mu


def _group_fit_fn(S, xbar, p):
    logdetS = np.linalg.slogdet(S)[1]

    def F(Sigma, mu):
        sign, logdet = np.linalg.slogdet(Sigma)
        if sign <= 0:
            return 1e6
        Sinv = np.linalg.inv(Sigma)
        d = xbar - mu
        return logdet + np.trace(S @ Sinv) - logdetS - p + d @ Sinv @ d
    return F


def _fit_multigroup(groups, model="configural"):
    """groups: list of (S, xbar, n). Single factor, p items.
    Returns dict(chi2, df, cfi, rmsea, npar)."""
    G = len(groups)
    p = groups[0][0].shape[0]
    N = sum(g[2] for g in groups)
    fitfns = [_group_fit_fn(S, xbar, p) for (S, xbar, n) in groups]
    var0 = [np.clip(np.diag(S), 1e-3, None) for (S, _, _) in groups]
    mean0 = [xbar for (_, xbar, _) in groups]

    # ---- parameter layout depends on the invariance model ----
    # common pieces: loadings lam (p). residual theta (p) per group (always free).
    # configural: nu per group (p), alpha=0 all, phi=1 all, lam per group.
    # metric: lam shared; nu per group; alpha=0 all; phi=1 ref, free others.
    # scalar: lam shared; nu shared; theta per group; alpha=0 ref free others; phi=1 ref free others.
    def unpack(params):
        i = 0
        out = []
        if model == "configural":
            for g in range(G):
                lam = params[i:i+p]; i += p
                nu = params[i:i+p]; i += p
                logth = params[i:i+p]; i += p
                out.append((lam, np.exp(logth), nu, 0.0, 1.0))
        elif model == "metric":
            lam = params[i:i+p]; i += p
            for g in range(G):
                nu = params[i:i+p]; i += p
                logth = params[i:i+p]; i += p
                phi = 1.0 if g == 0 else np.exp(params[i]); i += (0 if g == 0 else 1)
                out.append((lam, np.exp(logth), nu, 0.0, phi))
        elif model == "scalar":
            lam = params[i:i+p]; i += p
            nu = params[i:i+p]; i += p
            for g in range(G):
                logth = params[i:i+p]; i += p
                if g == 0:
                    alpha = 0.0; phi = 1.0
                else:
                    alpha = params[i]; i += 1
                    phi = np.exp(params[i]); i += 1
                out.append((lam, np.exp(logth), nu, alpha, phi))
        return out

    def obj(params):
        gp = unpack(params)
        tot = 0.0
        for g in range(G):
            lam, theta, nu, alpha, phi = gp[g]
            Sigma, mu = _model_implied(lam, theta, nu, alpha, phi)
            tot += (groups[g][2] / N) * fitfns[g](Sigma, mu)
        return tot

    # ---- initial values ----
    lam0 = _one_factor_loadings_from_S(groups[0][0])
    init = []
    if model == "configural":
        for g in range(G):
            l0 = _one_factor_loadings_from_S(groups[g][0])
            init += list(l0) + list(mean0[g]) + list(np.log(0.5 * var0[g]))
    elif model == "metric":
        init += list(lam0)
        for g in range(G):
            init += list(mean0[g]) + list(np.log(0.5 * var0[g]))
            if g > 0:
                init += [0.0]
    elif model == "scalar":
        init += list(lam0) + list(mean0[0])
        for g in range(G):
            init += list(np.log(0.5 * var0[g]))
            if g > 0:
                init += [0.0, 0.0]
    init = np.array(init, dtype=float)

    res = optimize.minimize(obj, init, method="L-BFGS-B",
                            options={"maxiter": 2000, "ftol": 1e-10})
    Fmin = max(res.fun, 0.0)
    npar = len(init)
    moments = G * (p + p * (p + 1) // 2)   # means + nonredundant covariances
    df = moments - npar
    chi2 = N * Fmin

    # baseline (independence) model: free variances+means, zero covariances
    F_base = 0.0
    for (S, xbar, n) in groups:
        d = np.diag(np.diag(S))
        sign, logdet = np.linalg.slogdet(d)
        F_base += (n / N) * (logdet - np.linalg.slogdet(S)[1])  # tr term = p cancels -p
    chi2_base = N * max(F_base, 0.0)
    df_base = G * (p * (p - 1) // 2)

    cfi = 1 - max(chi2 - df, 0) / max(chi2_base - df_base, 1e-9)
    cfi = float(min(max(cfi, 0.0), 1.0))
    rmsea = float(np.sqrt(G) * np.sqrt(max((chi2 - df), 0) / max(df * (N - 1), 1)))
    return {"model": model, "chi2": float(chi2), "df": int(df),
            "cfi": cfi, "rmsea": rmsea, "npar": int(npar),
            "converged": bool(res.success or Fmin < 1e3)}


def _one_factor_loadings_from_S(S):
    d = np.sqrt(np.clip(np.diag(S), 1e-9, None))
    R = S / np.outer(d, d)
    w, v = np.linalg.eigh(R)
    idx = np.argmax(w)
    lam_std = v[:, idx] * np.sqrt(max(w[idx], 1e-9))
    if lam_std.sum() < 0:
        lam_std = -lam_std
    return np.clip(lam_std * d, -10, 10)   # unstandardise to covariance scale


def _moments(Xg):
    X = np.asarray(Xg, dtype=float)
    n = X.shape[0]
    xbar = X.mean(axis=0)
    S = np.cov(X, rowvar=False, bias=True)   # MLE covariance (/n)
    return S, xbar, n


def measurement_invariance(group_data, delta_cfi_cut=0.010, delta_rmsea_cut=0.015,
                           rmsea_min_df=10):
    """group_data: list of n_g x p item-score arrays, one per group.

    Decision rule (deliberately ΔCFI-PRIMARY):
      * BINDING: ΔCFI >= -delta_cfi_cut  (Cheung & Rensvold 2002 — the most robust
        index for invariance testing, insensitive to model size).
      * ΔRMSEA <= delta_rmsea_cut (Chen 2007) is BINDING only when the constrained
        model has df >= rmsea_min_df. When df is small, RMSEA and its difference
        are KNOWN to be unstable and to falsely reject well-fitting models
        (Kenny, Kaniskan & McCoach 2015, 'The performance of RMSEA in models with
        small degrees of freedom'). Below the threshold ΔRMSEA is reported as an
        ADVISORY flag, not a veto. This guard was added after an independent
        machine-check caught a false 'non-invariance' verdict on a 3-item scale
        (df=2) driven purely by a noisy ΔRMSEA while ΔCFI was ~0.
    """
    groups = [_moments(Xg) for Xg in group_data]
    conf = _fit_multigroup(groups, "configural")
    metr = _fit_multigroup(groups, "metric")
    scal = _fit_multigroup(groups, "scalar")
    d_cfi_metric = metr["cfi"] - conf["cfi"]
    d_rmsea_metric = metr["rmsea"] - conf["rmsea"]
    d_cfi_scalar = scal["cfi"] - metr["cfi"]
    d_rmsea_scalar = scal["rmsea"] - metr["rmsea"]

    metric_rmsea_reliable = metr["df"] >= rmsea_min_df
    scalar_rmsea_reliable = scal["df"] >= rmsea_min_df
    metric_rmsea_ok = (d_rmsea_metric <= delta_rmsea_cut) or (not metric_rmsea_reliable)
    scalar_rmsea_ok = (d_rmsea_scalar <= delta_rmsea_cut) or (not scalar_rmsea_reliable)

    metric_ok = (d_cfi_metric >= -delta_cfi_cut) and metric_rmsea_ok
    scalar_ok = metric_ok and (d_cfi_scalar >= -delta_cfi_cut) and scalar_rmsea_ok

    advisories = []
    if not metric_rmsea_reliable and d_rmsea_metric > delta_rmsea_cut:
        advisories.append(f"metric ΔRMSEA={d_rmsea_metric:.3f} exceeds cutoff but "
                          f"df={metr['df']}<{rmsea_min_df}: RMSEA unreliable at small df, "
                          f"ΔCFI={d_cfi_metric:.4f} governs (advisory only).")
    if not scalar_rmsea_reliable and d_rmsea_scalar > delta_rmsea_cut:
        advisories.append(f"scalar ΔRMSEA={d_rmsea_scalar:.3f} exceeds cutoff but "
                          f"df={scal['df']}<{rmsea_min_df}: RMSEA unreliable at small df, "
                          f"ΔCFI={d_cfi_scalar:.4f} governs (advisory only).")
    return {
        "sub_weapon": "S-MEASURE", "kappa": 1,
        "fit": {"configural": conf, "metric": metr, "scalar": scal},
        "delta_cfi_metric": float(d_cfi_metric), "delta_rmsea_metric": float(d_rmsea_metric),
        "delta_cfi_scalar": float(d_cfi_scalar), "delta_rmsea_scalar": float(d_rmsea_scalar),
        "metric_invariance": bool(metric_ok),
        "scalar_invariance": bool(scalar_ok),
        "rmsea_advisories": advisories,
        "cutoffs": {"delta_cfi_BINDING": delta_cfi_cut, "delta_rmsea": delta_rmsea_cut,
                    "rmsea_binding_min_df": rmsea_min_df,
                    "source": "Cheung & Rensvold 2002 (ΔCFI, primary); Chen 2007 (ΔRMSEA); "
                              "Kenny et al. 2015 (RMSEA unreliable at small df)"},
        "group_mean_comparison_trustworthy": bool(scalar_ok),
        "ceiling_note": "Invariance != validity. Equivalent measurement across "
                        "groups does not prove the scale measures the intended "
                        "construct (validity is kappa=0 -> armor).",
    }


# --------------------------------- selftest -------------------------------- #
def _simulate_scale(n, loadings, intercepts, factor_mean=0.0, seed=0):
    rng = np.random.default_rng(seed)
    eta = rng.normal(factor_mean, 1.0, size=n)
    p = len(loadings)
    X = np.empty((n, p))
    for j in range(p):
        X[:, j] = intercepts[j] + loadings[j] * eta + rng.normal(0, 0.6, size=n)
    return X


def _selftest():
    # reliability anchors: a strongly-loaded scale has high alpha/omega
    Xrel = _simulate_scale(500, [0.8, 0.8, 0.8, 0.8, 0.8],
                            [0, 0, 0, 0, 0], seed=1)
    a = cronbach_alpha(Xrel); w = mcdonald_omega(Xrel)
    assert a > 0.70 and w > 0.70, (a, w)
    # a junk scale (near-zero loadings) must have LOW alpha (verifier can fail)
    Xjunk = _simulate_scale(500, [0.05, 0.05, 0.05, 0.05, 0.05],
                            [0, 0, 0, 0, 0], seed=2)
    assert cronbach_alpha(Xjunk) < 0.5, cronbach_alpha(Xjunk)

    load = [0.8, 0.75, 0.7, 0.72, 0.78]
    inter = [0.0, 0.1, -0.1, 0.2, 0.0]
    # INVARIANT: both groups share loadings + intercepts -> scalar must HOLD
    g1 = _simulate_scale(600, load, inter, factor_mean=0.0, seed=10)
    g2 = _simulate_scale(600, load, inter, factor_mean=0.3, seed=11)
    inv = measurement_invariance([g1, g2])
    assert inv["scalar_invariance"] is True, inv
    # NON-INVARIANT: group 2 has differential item functioning (different loadings
    # AND shifted intercepts on 3 items) -> scalar (and likely metric) must FAIL.
    load2 = [0.2, 0.25, 0.7, 0.72, 0.30]
    inter2 = [1.2, 1.1, -0.1, 0.2, 0.9]
    h1 = _simulate_scale(600, load, inter, factor_mean=0.0, seed=20)
    h2 = _simulate_scale(600, load2, inter2, factor_mean=0.0, seed=21)
    noninv = measurement_invariance([h1, h2])
    assert noninv["scalar_invariance"] is False, noninv
    # REGRESSION GUARD (the bug an independent machine-check caught): a 3-item
    # (low-df, df=2) INVARIANT scale must be judged invariant even if ΔRMSEA is
    # noisy — ΔCFI must govern, not a small-df RMSEA artifact.
    l3 = [0.8, 0.75, 0.7]; i3 = [0.0, 0.1, -0.1]
    a3 = _simulate_scale(800, l3, i3, factor_mean=0.0, seed=30)
    b3 = _simulate_scale(800, l3, i3, factor_mean=0.2, seed=31)
    inv3 = measurement_invariance([a3, b3])
    assert inv3["scalar_invariance"] is True, inv3
    print(f"measure_verify selftest: PASS "
          f"(alpha={a:.2f}/omega={w:.2f}; invariant scale -> scalar HOLDS; "
          f"DIF scale -> scalar REJECTED, dCFI_scalar={noninv['delta_cfi_scalar']:.3f})")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: measure_verify.py selftest  (API: cronbach_alpha, mcdonald_omega, measurement_invariance)")
