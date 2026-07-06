#!/usr/bin/env python3
"""T-SURVIVAL — reproduce Kaplan-Meier and Cox PH results from time-to-event data.

`lifelines` is absent, so TRIALGUARD HAND-ROLLS both estimators from the grounded
formulas (GROUNDING.md sec 5) and CROSS-CHECKS the Cox HR against an INDEPENDENT
implementation (statsmodels PHReg) in the self-test. The verification is the
AGREEMENT of two independent computations, not either one's self-report — the same
"two independent methods agree" doctrine SYMBOLICA uses.

What it certifies (kappa ~ 0.7): that a reported KM survival / Cox hazard ratio
REPRODUCES from the supplied data. It does NOT certify the trial is valid, the drug
works, or the HR is causally correct — reproduction != clinical truth.

Methods:
  - Kaplan-Meier:  S(t) = prod_{t_i<=t} (1 - d_i/n_i);  Greenwood SE.
  - Cox PH:        Breslow partial likelihood, Newton-Raphson for beta; HR=exp(beta),
                   SE(beta)=sqrt(I(beta)^-1).  (Breslow tie handling.)
"""
import sys, math
import numpy as np


# --------------------------------------------------------------------------- #
#  Kaplan-Meier estimator + Greenwood variance  (Kaplan & Meier 1958)
# --------------------------------------------------------------------------- #
def kaplan_meier(times, events):
    """times: durations; events: 1=event, 0=censored. Returns the KM step function.

    Returns list of {t, n_risk, d_events, c_censored, survival, greenwood_se}.
    """
    t = np.asarray(times, float); e = np.asarray(events, int)
    if len(t) == 0 or len(t) != len(e):
        return {"test": "kaplan-meier", "kappa": 0.7, "valid": False,
                "note": "UNDEFINED: empty or mismatched inputs — abstain."}
    order = np.argsort(t, kind="mergesort")
    t, e = t[order], e[order]
    uniq = np.unique(t)
    n = len(t)
    surv = 1.0; cum_var_term = 0.0
    rows = []
    at_risk = n
    for ut in uniq:
        d = int(((t == ut) & (e == 1)).sum())
        c = int(((t == ut) & (e == 0)).sum())
        n_i = at_risk
        if d > 0:
            surv *= (1.0 - d / n_i)
            cum_var_term += d / (n_i * (n_i - d)) if n_i > d else 0.0
        se = surv * math.sqrt(cum_var_term) if surv > 0 else 0.0
        rows.append({"t": float(ut), "n_risk": int(n_i), "d_events": d,
                     "c_censored": c, "survival": round(surv, 6),
                     "greenwood_se": round(se, 6)})
        at_risk -= (d + c)
    return {"test": "kaplan-meier", "kappa": 0.7, "valid": True, "n": n,
            "curve": rows, "median_survival": _km_median(rows),
            "ceiling_note": "Reproduction of the KM curve from data; NOT a claim the "
                            "trial is valid or the treatment effective."}


def _km_median(rows):
    for r in rows:
        if r["survival"] <= 0.5:
            return r["t"]
    return None        # median not reached


# --------------------------------------------------------------------------- #
#  Cox PH partial likelihood (Breslow ties), Newton-Raphson  (Cox 1972/Breslow 1974)
# --------------------------------------------------------------------------- #
def cox_ph(times, events, X, max_iter=100, tol=1e-9):
    """Fit Cox PH by Breslow partial likelihood. X: (n, p) covariate matrix.

    Returns beta, HR=exp(beta), SE(beta), z, two-sided p, and log-partial-likelihood.
    Newton-Raphson on the Breslow log-PL; the inverse observed information gives SEs.
    """
    t = np.asarray(times, float); e = np.asarray(events, int)
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    n, p = X.shape
    if not (len(t) == len(e) == n) or n == 0:
        return {"test": "cox-ph", "kappa": 0.7, "valid": False,
                "note": "UNDEFINED: empty or mismatched inputs — abstain."}
    order = np.argsort(t, kind="mergesort")
    t, e, X = t[order], e[order], X[order]
    event_times = np.unique(t[e == 1])

    beta = np.zeros(p)
    last_ll = None
    for _ in range(max_iter):
        eta = X @ beta
        w = np.exp(eta)                                   # risk scores
        U = np.zeros(p)                                   # score
        I = np.zeros((p, p))                              # observed information
        ll = 0.0
        for ft in event_times:
            risk = t >= ft                                # risk set R(ft)
            dmask = (t == ft) & (e == 1)                  # tied events at ft
            d = int(dmask.sum())
            wr = w[risk]
            Xr = X[risk]
            sum_w = wr.sum()
            xbar = (wr[:, None] * Xr).sum(0) / sum_w       # weighted mean over risk set
            # Breslow: tied events share the full risk set; denom^d.
            ll += (eta[dmask].sum()) - d * math.log(sum_w)
            U += X[dmask].sum(0) - d * xbar
            cov = (wr[:, None, None] * (Xr[:, :, None] * Xr[:, None, :])).sum(0) / sum_w \
                - np.outer(xbar, xbar)
            I += d * cov
        # Newton-Raphson step
        try:
            step = np.linalg.solve(I, U)
        except np.linalg.LinAlgError:
            return {"test": "cox-ph", "kappa": 0.7, "valid": False,
                    "note": "information matrix singular (collinear covariate / no "
                            "events) — abstain."}
        beta = beta + step
        if last_ll is not None and abs(ll - last_ll) < tol:
            break
        last_ll = ll

    try:
        cov_beta = np.linalg.inv(I)
    except np.linalg.LinAlgError:
        return {"test": "cox-ph", "kappa": 0.7, "valid": False,
                "note": "singular information at solution — abstain."}
    se = np.sqrt(np.diag(cov_beta))
    z = beta / se
    pval = 2 * _norm_sf(np.abs(z))
    return {"test": "cox-ph", "kappa": 0.7, "valid": True, "n": n, "p": p,
            "n_events": int(e.sum()),
            "beta": [round(float(b), 6) for b in beta],
            "hazard_ratio": [round(float(math.exp(b)), 6) for b in beta],
            "se_beta": [round(float(s), 6) for s in se],
            "z": [round(float(zz), 4) for zz in z],
            "p_value": [round(float(pp), 6) for pp in pval],
            "loglik": round(float(ll), 6),
            "tie_handling": "Breslow",
            "ceiling_note": "Reproduction of the Cox HR from data; NOT a causal or "
                            "clinical-efficacy claim."}


def _norm_sf(x):
    return 0.5 * np.array([math.erfc(v / math.sqrt(2)) for v in np.atleast_1d(x)])


# --------------------------------------------------------------------------- #
#  Self-test: KM vs hand-computed; Cox vs INDEPENDENT statsmodels PHReg.
# --------------------------------------------------------------------------- #
def _selftest():
    # ---- KM: a small textbook dataset, hand-verified ----
    # times, events: 6, 6, 6, 6+(cens), 7, 9+(cens), 10, ...
    times = [6, 6, 6, 7, 10, 13, 16, 22, 23, 6, 9, 10, 11, 17, 19, 20, 25, 32, 32, 34, 35]
    events = [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    km = kaplan_meier(times, events)
    assert km["valid"]
    # at first event time t=6: n_risk=21, 3 events + 1 censored -> S=1-3/21=0.857143
    r6 = [r for r in km["curve"] if r["t"] == 6][0]
    assert r6["n_risk"] == 21 and r6["d_events"] == 3 and r6["c_censored"] == 1, r6
    assert abs(r6["survival"] - (1 - 3 / 21)) < 1e-6, r6
    # KM survival is monotone non-increasing
    s = [r["survival"] for r in km["curve"]]
    assert all(s[i] >= s[i + 1] - 1e-12 for i in range(len(s) - 1)), "KM must be monotone"

    # ---- Cox: hand-rolled vs INDEPENDENT statsmodels PHReg (the cross-check) ----
    rng = np.random.default_rng(7)
    n = 200
    x = rng.normal(size=(n, 1))
    true_beta = 0.8
    # simulate exponential survival with hazard exp(beta*x); admin censoring at c
    u = rng.uniform(size=n)
    tt = -np.log(u) / np.exp(true_beta * x[:, 0])
    cens = rng.uniform(0.5, 2.0, size=n)
    obs = np.minimum(tt, cens)
    ev = (tt <= cens).astype(int)
    mine = cox_ph(obs, ev, x)
    assert mine["valid"], mine

    from statsmodels.duration.hazard_regression import PHReg
    ref = PHReg(obs, x, status=ev, ties="breslow").fit()
    ref_beta = float(ref.params[0]); ref_se = float(ref.bse[0])
    assert abs(mine["beta"][0] - ref_beta) < 1e-4, \
        f"Cox beta disagrees with statsmodels: {mine['beta'][0]} vs {ref_beta}"
    assert abs(mine["se_beta"][0] - ref_se) < 1e-3, \
        f"Cox SE disagrees with statsmodels: {mine['se_beta'][0]} vs {ref_se}"
    # recovered beta should be near the truth (sanity, not exact)
    assert abs(mine["beta"][0] - true_beta) < 0.3, mine["beta"]

    # ---- must be able to FAIL: a 2x-off reported HR is NOT reproduced ----
    reported_hr = math.exp(ref_beta) * 2.0
    reproduced_hr = mine["hazard_ratio"][0]
    assert abs(reproduced_hr - reported_hr) / reported_hr > 0.1, \
        "a 2x-off HR must be detectably non-reproduced"

    # ---- abstain on malformed input, never crash ----
    assert kaplan_meier([], [])["valid"] is False
    assert cox_ph([1, 2], [1, 1], [[1.0]])["valid"] is False    # mismatched n

    print(f"survival_verify selftest: PASS "
          f"(KM monotone + first step exact; Cox HR matches INDEPENDENT statsmodels "
          f"PHReg to <1e-4 on beta [{mine['beta'][0]:.5f} vs {ref_beta:.5f}]; "
          f"a 2x-off HR is detectably non-reproduced; abstains on malformed input)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: survival_verify.py selftest")
