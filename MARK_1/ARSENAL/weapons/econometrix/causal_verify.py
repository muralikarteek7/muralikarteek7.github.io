#!/usr/bin/env python3
"""E-CAUSAL — frozen verifier for IDENTIFICATION of an observational/quasi-experimental causal claim
(kappa ~= 0.5).

A DiD / RDD / IV design identifies a causal effect ONLY under assumptions. Some of those assumptions
are TESTABLE (kappa>0) and some are fundamentally UNTESTABLE (kappa=0). This verifier runs the testable
diagnostics and, for the untestable assumptions, reports a SENSITIVITY NUMBER (how strong an unobserved
confounder would have to be to overturn the result) — it NEVER emits a bare "X caused Y".

  TESTABLE diagnostics (run + gate):
    - DiD  : pre-trends / placebo — the pre-treatment event-study LEAD coefficients must be jointly ~0
             (Roth 2022). A failed pre-trends test FLAGS the design. NB: parallel trends in the POST
             period is UNTESTABLE -> sensitivity, never a clean pass.
    - RDD  : McCrary (2008) density test — a discontinuity in the running-variable density at the cutoff
             is evidence of manipulation/sorting -> the design is threatened.
    - IV   : first-stage F (Staiger-Stock 1997 F>10; Stock-Yogo 2005 critical values) — a weak first
             stage means 2SLS is biased toward OLS and inference is unreliable.

  UNTESTABLE-assumption SENSITIVITY (report a number, never certify):
    - E-value (VanderWeele & Ding 2017) — REUSED from socius/eval_verify.py.
    - Oster (2019) delta — how strong selection on unobservables (relative to observables) must be to
      drive the effect to zero; |delta|>=1 is the conventional robustness bar.

All thresholds/formulas are GROUNDED in GROUNDING.md (fetched). Self-tests anchor on hand-computed
numbers AND on known-good/known-broken synthetic designs (a clean design passes; a confounded /
manipulated / weak one is CAUGHT).

HONEST CEILING: a passed diagnostic means "consistent with identification," NEVER "proven causal." The
untestable assumptions remain untestable; the sensitivity number bounds, it does not certify.
"""
import sys, os, json, math
import numpy as np
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd

# REUSE SOCIUS's already-audited, self-tested E-value verifier (credit: socius/eval_verify.py)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "socius"))
import eval_verify  # noqa: E402


# --------------------------------------------------------------------------- #
#  DiD — pre-trends / placebo (TESTABLE part of parallel trends)
# --------------------------------------------------------------------------- #
def did_pretrends(df, y="y", unit="unit", time="time", rel_time="rel_time",
                  ref_period=-1, alpha=0.05):
    """Event-study pre-trends test. df is LONG panel with a `rel_time` column (event time relative to
    treatment; the reference period ref_period is OMITTED; control/never-treated rows use a sentinel
    that is dropped from the dummy set, e.g. a large/np.nan value never in the lead/lag window).

    Fits  y ~ C(unit) + C(time) + [rel_time dummies != ref_period]  (two-way fixed effects) and runs a
    JOINT F-test that all PRE-treatment lead coefficients (rel_time < ref_period) equal 0. A small
    p-value => pre-trends differ => parallel-trends assumption is doubtful => the design is FLAGGED.
    """
    d = df.copy()
    # relative-time values that get their own dummy (exclude the reference and any sentinel controls)
    rt_vals = sorted(v for v in d[rel_time].dropna().unique()
                     if v != ref_period and abs(v) < 9000)
    lead_terms = []
    for v in rt_vals:
        name = f"rt_{'m' if v < 0 else 'p'}{abs(int(v))}"
        d[name] = (d[rel_time] == v).astype(float)
        if v < ref_period:
            lead_terms.append(name)
    dummy_cols = [f"rt_{'m' if v < 0 else 'p'}{abs(int(v))}" for v in rt_vals]
    formula = f"{y} ~ C({unit}) + C({time}) + " + " + ".join(dummy_cols)
    res = smf.ols(formula, data=d).fit()
    # joint Wald/F test: all pre-treatment lead coefficients == 0
    if not lead_terms:
        return {"sub_weapon": "E-CAUSAL", "design": "DiD", "kappa": 0.5,
                "error": "no pre-treatment leads to test", "parallel_trends_plausible": None}
    ftest = res.f_test(" = 0, ".join(lead_terms) + " = 0")
    p_joint = float(ftest.pvalue)
    leads = {t: float(res.params[t]) for t in lead_terms}
    plausible = p_joint > alpha
    return {
        "sub_weapon": "E-CAUSAL", "design": "DiD", "kappa": 0.5,
        "lead_coefficients": leads,
        "joint_pretrend_F": float(ftest.fvalue), "joint_pretrend_p": p_joint,
        "parallel_trends_plausible": bool(plausible),
        "verdict": ("pre-trends consistent with parallel trends (NOT a proof — post-period parallel "
                    "trends is untestable)" if plausible
                    else "PRE-TRENDS FAIL: leads jointly != 0 -> parallel-trends doubtful, design FLAGGED"),
        "ceiling_note": "Passing pre-trends is necessary, not sufficient: post-treatment parallel "
                        "trends is fundamentally untestable (Roth 2022). Report with a sensitivity number.",
    }


# --------------------------------------------------------------------------- #
#  RDD — McCrary (2008) density / manipulation test
# --------------------------------------------------------------------------- #
def _local_linear_density_at(x, cutoff, side, bw=None, n_bins=None):
    """Estimate the density of x at the cutoff from one side via a histogram + local-linear fit."""
    x = np.asarray(x, dtype=float)
    if side == "left":
        xs = x[x < cutoff]
    else:
        xs = x[x >= cutoff]
    if len(xs) < 10:
        return np.nan
    lo, hi = x.min(), x.max()
    if n_bins is None:
        n_bins = max(int(np.sqrt(len(x))), 20)
    binw = (hi - lo) / n_bins
    edges = np.arange(lo, hi + binw, binw)
    counts, edges = np.histogram(x, bins=edges)
    mids = (edges[:-1] + edges[1:]) / 2
    dens = counts / (len(x) * binw)            # normalized density per bin
    if side == "left":
        mask = mids < cutoff
    else:
        mask = mids >= cutoff
    mx, my = mids[mask], dens[mask]
    if len(mx) < 2:
        return np.nan
    # local-linear: weight bins by proximity to cutoff (triangular kernel), regress density on midpoint
    if bw is None:
        bw = (hi - lo) / 5.0
    w = np.maximum(1 - np.abs(mx - cutoff) / bw, 0)
    if w.sum() == 0:
        w = np.ones_like(mx)
    X = np.column_stack([np.ones_like(mx), mx - cutoff])
    W = np.diag(w)
    try:
        beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ my)
    except np.linalg.LinAlgError:
        return np.nan
    return float(beta[0])                       # intercept = density extrapolated to the cutoff


def mccrary_density_test(running_var, cutoff=0.0, n_boot=300, seed=0, alpha=0.05):
    """McCrary (2008) manipulation test. theta = log f+ - log f- at the cutoff; SE by bootstrap;
    z = theta/SE, two-sided p. A significant discontinuity => sorting/manipulation => RD design
    threatened. (Bootstrap SE is used in place of the original two-step asymptotic SE — robust and
    self-testable; see GROUNDING.md s4.)"""
    x = np.asarray(running_var, dtype=float)
    x = x[np.isfinite(x)]
    fL = _local_linear_density_at(x, cutoff, "left")
    fR = _local_linear_density_at(x, cutoff, "right")
    if not (np.isfinite(fL) and np.isfinite(fR)) or fL <= 0 or fR <= 0:
        return {"sub_weapon": "E-CAUSAL", "design": "RDD", "kappa": 0.5,
                "error": "density non-positive at cutoff (too few points / bad bandwidth)",
                "manipulation_detected": None}
    theta = math.log(fR) - math.log(fL)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        xb = rng.choice(x, size=len(x), replace=True)
        bL = _local_linear_density_at(xb, cutoff, "left")
        bR = _local_linear_density_at(xb, cutoff, "right")
        if np.isfinite(bL) and np.isfinite(bR) and bL > 0 and bR > 0:
            boots.append(math.log(bR) - math.log(bL))
    se = float(np.std(boots, ddof=1)) if len(boots) > 5 else float("nan")
    z = theta / se if se and se > 0 else float("nan")
    p = float(2 * (1 - stats.norm.cdf(abs(z)))) if np.isfinite(z) else float("nan")
    detected = (np.isfinite(p) and p < alpha)
    # HETEROSCEDASTICITY CAVEAT (audit finding #4, 2026-06-20): a running variable with materially
    # different spread on each side of the cutoff can produce a density-slope discontinuity that this
    # test reads as "manipulation" even when there is NO sorting. Flag it so a detection is not
    # over-claimed. (Modern best practice — Cattaneo-Jansson-Ma rddensity — is more robust here.)
    xl, xr = x[x < cutoff], x[x >= cutoff]
    sd_l = float(np.std(xl)) if len(xl) > 2 else float("nan")
    sd_r = float(np.std(xr)) if len(xr) > 2 else float("nan")
    hetero = (np.isfinite(sd_l) and np.isfinite(sd_r) and min(sd_l, sd_r) > 0
              and max(sd_l, sd_r) / min(sd_l, sd_r) > 1.5)
    verdict = ("MANIPULATION DETECTED: density discontinuous at cutoff -> sorting -> RD design threatened"
               if detected else "no density discontinuity detected (consistent with no manipulation)")
    if detected and hetero:
        verdict += (" -- CAVEAT: running-variable spread differs materially L vs R "
                    f"(sd {sd_l:.2f} vs {sd_r:.2f}); heteroscedasticity, not sorting, may explain this.")
    return {
        "sub_weapon": "E-CAUSAL", "design": "RDD", "kappa": 0.5,
        "density_left": fL, "density_right": fR,
        "log_density_diff_theta": theta, "se_bootstrap": se, "z": z, "p_value": p,
        "sd_left": sd_l, "sd_right": sd_r, "heteroscedastic_running_var": bool(hetero),
        "manipulation_detected": bool(detected) if np.isfinite(p) else None,
        "verdict": verdict,
        "ceiling_note": "No detected discontinuity is supportive, not proof; the local-randomization "
                        "assumption near the cutoff remains an assumption. A detection under "
                        "heteroscedasticity may be a false positive (use Cattaneo-Jansson-Ma rddensity).",
    }


# --------------------------------------------------------------------------- #
#  IV — first-stage F (weak instrument)
# --------------------------------------------------------------------------- #
# Stock-Yogo (2005) critical values, 1 endogenous regressor & 1 instrument (maximal IV size):
STOCK_YOGO_1x1 = {0.10: 16.38, 0.15: 8.96, 0.20: 6.66, 0.25: 5.53}


def iv_first_stage_F(endog, instruments, exog=None, weak_threshold=10.0):
    """First-stage F for IV: regress the endogenous regressor on the excluded instrument(s) (+ exog),
    joint F-test on the instrument coefficients. F < weak_threshold (Staiger-Stock 1997 rule-of-thumb
    10) => WEAK instrument => 2SLS biased toward OLS, inference unreliable. Also reported against the
    Stock-Yogo 10%-maximal-size value (16.38 for the 1x1 case)."""
    X = np.asarray(endog, dtype=float).reshape(-1)
    Z = np.asarray(instruments, dtype=float)
    if Z.ndim == 1:
        Z = Z.reshape(-1, 1)
    n, k = Z.shape
    cols = {f"z{j}": Z[:, j] for j in range(k)}
    if exog is not None:
        E = np.asarray(exog, dtype=float)
        if E.ndim == 1:
            E = E.reshape(-1, 1)
        for j in range(E.shape[1]):
            cols[f"w{j}"] = E[:, j]
    d = pd.DataFrame(cols)
    d["X"] = X
    rhs = list(cols.keys())
    res = smf.ols("X ~ " + " + ".join(rhs), data=d).fit()
    instr_names = [f"z{j}" for j in range(k)]
    ftest = res.f_test(" = 0, ".join(instr_names) + " = 0")
    F = float(ftest.fvalue)
    weak = F < weak_threshold
    return {
        "sub_weapon": "E-CAUSAL", "design": "IV", "kappa": 0.5,
        "first_stage_F": F, "n_instruments": k,
        "weak_threshold_rule_of_thumb": weak_threshold,
        "stock_yogo_10pct_size_1x1": STOCK_YOGO_1x1[0.10],
        "weak_instrument": bool(weak),
        "verdict": ("WEAK INSTRUMENT: first-stage F < 10 -> 2SLS biased toward OLS, inference "
                    "unreliable -> IV claim FLAGGED" if weak
                    else f"first stage strong (F={F:.1f} > 10); note modern effective-F bar is higher"),
        "ceiling_note": "F>10 is the CLASSIC rule; Lee et al. 2022 / Olea-Pflueger argue the valid 5% "
                        "threshold is far higher (effective-F). A strong first stage does not make the "
                        "exclusion restriction (untestable) hold.",
    }


# --------------------------------------------------------------------------- #
#  Oster (2019) delta — selection on unobservables (untestable-assumption sensitivity)
# --------------------------------------------------------------------------- #
def oster_delta(beta_short, R_short, beta_controlled, R_controlled, R_max=None):
    """Oster (2019) delta = how strong selection on unobservables must be (relative to observables) to
    drive the treatment effect to zero. delta = b~(Rmax - R~) / [(b. - b~)(R~ - R.)]. |delta|>=1 is the
    conventional robustness bar. Default R_max = min(1.3*R~, 1) (Oster's calibration)."""
    bdot, Rdot = float(beta_short), float(R_short)
    btil, Rtil = float(beta_controlled), float(R_controlled)
    if R_max is None:
        R_max = min(1.3 * Rtil, 1.0)
    R_max = float(R_max)
    # INPUT GUARD (audit finding #3, 2026-06-20): R_max must be >= R_controlled BY DEFINITION (adding
    # the unobservables can only raise R2). An invalid R_max < R_controlled flips the numerator sign and
    # silently produces a misleading delta = -1 -> "robust". Reject it rather than emit a false verdict.
    if R_max < Rtil:
        return {"sub_weapon": "E-CAUSAL", "design": "Oster-delta", "kappa": 0.5,
                "error": f"invalid R_max={R_max} < R_controlled={Rtil}; R_max must be >= R_controlled",
                "delta": None, "robust_to_selection": None}
    if R_max > 1.0:
        return {"sub_weapon": "E-CAUSAL", "design": "Oster-delta", "kappa": 0.5,
                "error": f"invalid R_max={R_max} > 1.0 (R2 cannot exceed 1)",
                "delta": None, "robust_to_selection": None}
    denom = (bdot - btil) * (Rtil - Rdot)
    if denom == 0:
        return {"sub_weapon": "E-CAUSAL", "design": "Oster-delta", "kappa": 0.5,
                "error": "denominator zero (coefficient/ R2 did not move with controls)", "delta": None}
    delta = btil * (R_max - Rtil) / denom
    beta_star = btil - 1.0 * (bdot - btil) * (R_max - Rtil) / (Rtil - Rdot)  # bias-adj at delta=1
    robust = abs(delta) >= 1.0
    return {
        "sub_weapon": "E-CAUSAL", "design": "Oster-delta", "kappa": 0.5,
        "beta_short": bdot, "R_short": Rdot, "beta_controlled": btil, "R_controlled": Rtil,
        "R_max": R_max, "delta": float(delta), "beta_star_at_delta1": float(beta_star),
        "robust_to_selection": bool(robust),
        "verdict": (f"robust: |delta|={abs(delta):.2f} >= 1 (unobservables must be at least as important "
                    f"as observables to kill the effect)" if robust
                    else f"FRAGILE: |delta|={abs(delta):.2f} < 1 (modest unobserved selection could "
                         f"drive the effect to zero)"),
        "ceiling_note": "delta is a sensitivity number under an assumed R_max, NOT a proof of causality.",
    }


def e_value_sensitivity(estimate, scale="RR", ci_limit=None, benchmark_confounding=2.0):
    """Thin wrapper over SOCIUS's audited E-value verifier (eval_verify.assess_sensitivity)."""
    out = eval_verify.assess_sensitivity(estimate, scale=scale, ci_limit=ci_limit,
                                         benchmark_confounding=benchmark_confounding)
    out["design"] = "E-value (reused from SOCIUS)"
    return out


# ============================ SELF-TESTS (must FAIL on broken input) ========= #
def _make_panel(n_units=40, n_time=12, treat_start=7, effect=3.0, pretrend=0.0, seed=0):
    """Synthetic DiD panel. Half the units are treated at treat_start; `pretrend` injects a divergent
    PRE-treatment slope into treated units (0 => parallel pre-trends; >0 => pre-trends VIOLATED)."""
    rng = np.random.default_rng(seed)
    rows = []
    for u in range(n_units):
        treated = u < n_units // 2
        u_fe = rng.normal(0, 1)
        for t in range(n_time):
            t_fe = 0.3 * t
            rel = (t - treat_start) if treated else 9999  # sentinel for never-treated controls
            post = treated and t >= treat_start
            y = u_fe + t_fe + rng.normal(0, 0.5)
            if treated:
                y += pretrend * t                      # divergent trend if pretrend>0
            if post:
                y += effect
            rows.append({"unit": u, "time": t, "y": y, "rel_time": rel})
    return pd.DataFrame(rows)


def _selftest():
    # ---- (1) Oster delta hand-computed anchor ----
    # b.=1.0, R.=0.10 ; b~=0.8, R~=0.30 ; Rmax=0.60
    #   delta = 0.8*(0.60-0.30) / [(1.0-0.8)(0.30-0.10)] = 0.8*0.30 / (0.2*0.2) = 0.24/0.04 = 6.0
    od = oster_delta(1.0, 0.10, 0.8, 0.30, R_max=0.60)
    assert abs(od["delta"] - 6.0) < 1e-9, od
    assert od["robust_to_selection"] is True, od
    # FRAGILE: coefficient collapses with controls while R2 barely moves -> small delta
    #   b.=1.0,R.=0.10 ; b~=0.2,R~=0.12 ; Rmax=0.156(=1.3*0.12)
    #   delta = 0.2*(0.156-0.12)/[(1.0-0.2)(0.12-0.10)] = 0.2*0.036/(0.8*0.02)=0.0072/0.016=0.45
    odf = oster_delta(1.0, 0.10, 0.2, 0.12)
    assert abs(odf["delta"] - 0.45) < 1e-9 and odf["robust_to_selection"] is False, odf
    # AUDIT-REGRESSION (finding #3): invalid R_max < R_controlled must ERROR, not return a false "robust"
    bad = oster_delta(1.0, 0.10, 0.8, 0.30, R_max=0.20)   # R_max < R_controlled (0.30)
    assert bad["delta"] is None and "error" in bad and bad["robust_to_selection"] is None, bad

    # ---- (2) DiD pre-trends: clean PASSES, violated is CAUGHT ----
    clean = did_pretrends(_make_panel(pretrend=0.0, seed=1))
    assert clean["parallel_trends_plausible"] is True, clean
    violated = did_pretrends(_make_panel(pretrend=0.6, seed=1))
    assert violated["parallel_trends_plausible"] is False, violated  # the (d) gate test

    # ---- (3) McCrary: no manipulation PASSES, manipulation is CAUGHT ----
    rng = np.random.default_rng(3)
    smooth = rng.normal(0, 1, size=4000)                       # continuous density at 0
    nomanip = mccrary_density_test(smooth, cutoff=0.0)
    assert nomanip["manipulation_detected"] is False, nomanip
    # manipulation: push a chunk of just-below-cutoff units to just-above (sorting)
    manip = rng.normal(0, 1, size=4000)
    below = (manip > -0.5) & (manip < 0.0)
    manip[below] = np.abs(manip[below]) + 0.001                # pile up just above 0
    mres = mccrary_density_test(manip, cutoff=0.0)
    assert mres["manipulation_detected"] is True, mres
    # AUDIT-REGRESSION (finding #4): a running variable that is genuinely more dispersed on one side of
    # the cutoff (tight-left / wide-right, NO sorting) produces a density slope-discontinuity McCrary can
    # read as "manipulation". If flagged, the verdict must carry the heteroscedasticity caveat so the
    # detection is not over-claimed as sorting.
    hetero_x = np.concatenate([-rng.exponential(0.5, 3000), rng.exponential(2.0, 3000)])  # tight L, wide R
    hres = mccrary_density_test(hetero_x, cutoff=0.0)
    assert hres["heteroscedastic_running_var"] is True, hres
    if hres["manipulation_detected"]:
        assert "heteroscedasticity" in hres["verdict"], hres

    # ---- (4) IV first-stage F: strong PASSES, weak is CAUGHT ----
    rng = np.random.default_rng(4)
    n = 1000
    z = rng.normal(0, 1, n)
    strong_x = 2.0 * z + rng.normal(0, 1, n)                   # instrument strongly relevant
    fs_strong = iv_first_stage_F(strong_x, z)
    assert fs_strong["weak_instrument"] is False and fs_strong["first_stage_F"] > 100, fs_strong
    weak_x = 0.03 * z + rng.normal(0, 1, n)                    # barely relevant
    fs_weak = iv_first_stage_F(weak_x, z)
    assert fs_weak["weak_instrument"] is True and fs_weak["first_stage_F"] < 10, fs_weak

    # ---- (5) E-value reuse sanity (anchored in SOCIUS): RR=3.9 -> E=7.26 ----
    ev = e_value_sensitivity(3.9, "RR")
    assert abs(ev["e_value_point"] - 7.26) < 0.01, ev

    print("causal_verify selftest: PASS")
    print(f"  Oster delta anchored (6.0 robust / 0.45 fragile); DiD pre-trends: clean p="
          f"{clean['joint_pretrend_p']:.3f} PASS, violated p={violated['joint_pretrend_p']:.1e} CAUGHT")
    print(f"  McCrary: smooth p={nomanip['p_value']:.3f} (no manip), sorted p={mres['p_value']:.1e} CAUGHT; "
          f"IV F: strong={fs_strong['first_stage_F']:.0f}, weak={fs_weak['first_stage_F']:.2f} CAUGHT")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: causal_verify.py selftest  (API: did_pretrends, mccrary_density_test, "
              "iv_first_stage_F, oster_delta, e_value_sensitivity)")
