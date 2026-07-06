#!/usr/bin/env python3
"""T-FORENSICS — the sharp end of TRIALGUARD (clinical-trial statistic forensics).

THREE families of check on REPORTED trial statistics:
  1. GRIM / GRIMMER   (EXACT, imported from psymetrix/forensics_verify.py): is a
     reported clinical mean/SD arithmetically possible for the stated N/scale?
  2. group-size / allocation-ratio / percentage->count consistency (EXACT): do the
     reported group sizes match the stated randomization ratio? does a reported
     percentage back-compute to an integer count?
  3. Carlisle baseline-anomaly test (STATISTICAL screen, NOT exact): under simple
     randomization the two-sided baseline p-values of CONTINUOUS variables are
     i.i.d. Uniform(0,1); a systematic departure (too-similar OR too-different) is a
     distributional anomaly.

================================ THE CARDINAL RAIL ================================
INCONSISTENCY / ANOMALY != FRAUD.  This is the strictest honesty rail in the arsenal
because the domain is clinical (patients, reputations).  EVERY forensic output here
reports the exact statistic + candidate BENIGN explanations + the method's known
FALSE-POSITIVE modes, and STOPS.  No output ever names a person or trial as
fraudulent; the word "fraud" never appears as a verdict.  In Carlisle's own words
(2017, the originator of the baseline test): "Fraud, unintentional error,
correlation, stratified allocation and poor methodology might have contributed to
the excess."  A flag is a screen for INVESTIGATION, never a conclusion of misconduct.
==================================================================================

Two soundness regimes, stated on every output (they differ in KIND):
  * GRIM/GRIMMER/group-size/percentage are EXACT: a flag is a PROOF of inconsistency
    (benign causes: rounding / typo / dropout / reporting error).  Target: ZERO
    false positives (a false certificate of impossibility is a false accusation).
  * Carlisle is a STATISTICAL SCREEN: a flag means "departs from the U(0,1) expected
    under SIMPLE randomization at level alpha"; its false-positive rate is ~alpha BY
    CONSTRUCTION and is INFLATED by correlated covariates and stratified/cluster
    designs.  It is NOT an exact certificate and is reported as such.

Grounding: GROUNDING.md (Carlisle 2017 + its critiques, all fetched).
"A verifier that cannot FAIL is not a verifier": see _selftest().
"""
import sys, os, math, json

# import the EXACT GRIM/GRIMMER core from PSYMETRIX (reuse, do not rebuild) -------
_PSYMETRIX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "psymetrix")
if _PSYMETRIX not in sys.path:
    sys.path.insert(0, _PSYMETRIX)
import forensics_verify as PF           # grim, grimmer, sprite, tiva, pcurve, benford

import numpy as np
from scipy import stats

# --------------------------------------------------------------------------- #
#  The non-waivable honesty constants — attached to EVERY forensic output.
# --------------------------------------------------------------------------- #
CEILING = ("INCONSISTENCY/ANOMALY != FRAUD. This is a screen, not a verdict. The "
           "statistic below is a mathematical/statistical fact about the REPORTED "
           "numbers; it is NEVER a finding of misconduct about any person or trial. "
           "Carlisle 2017: 'Fraud, unintentional error, correlation, stratified "
           "allocation and poor methodology might have contributed to the excess.'")

# Carlisle's own list (2017) + the appraisal/Bland critiques (GROUNDING.md sec 2).
CARLISLE_FALSE_POSITIVE_MODES = [
    "STRATIFIED / minimized / block randomization makes groups MORE similar than "
    "simple randomization predicts -> a spurious 'too-similar' signal (Carlisle "
    "himself EXCLUDED stratified variables).",
    "CORRELATED baseline variables (e.g. height & weight, age & comorbidity) violate "
    "the independence the combination assumes -> inflated false positives (Bland).",
    "CLUSTER randomization alters the variance structure (design effect).",
    "ROUNDING / truncation of reported means & SDs perturbs the computed p-values.",
    "SMALL number of baseline variables (k) -> the combination is unreliable.",
    "CATEGORICAL variables are UNSOUND for this test (the U(0,1) result holds only "
    "for continuous ~normal independent variables) -> excluded here, never tested.",
    "An unusual-but-REAL sample can depart from uniformity by chance (rate ~ alpha).",
]
CARLISLE_BENIGN_EXPLANATIONS = [
    "stratified / minimized allocation (extremely common and entirely legitimate)",
    "correlated baseline variables",
    "cluster randomization", "rounding / reporting in the published table",
    "post-randomization dropout / per-protocol vs ITT analysis sets",
    "an unusual-but-real sample (chance departure)",
]

# Sensitive tokens that, if AFFIRMED (not negated) about a specific trial, would cross
# the inconsistency!=fraud line. Used to police our own verdict strings AND offered to
# the cross-model auditor as a reusable honesty checker. A token is allowed when it is
# (a) negated/disclaimed ("NOT fraud", "fraud remains unconfirmed"), (b) part of a
# larger word (anti-fraud), or (c) inside a grounded CITATION / LIST-of-possible-causes
# context (Carlisle's quote lists fraud as one of FIVE possible contributors — that is
# grounding, not an accusation). An un-exempt affirmation is a BLOCKING defect.
# (Hardened 2026-06-20 after the cross-model audit F1/F2: clause-level negation, word
# boundaries, postceding negators, and a citation/list exemption.)
import re

_SENSITIVE = ("fraud", "fabricat", "falsif", "misconduct", "manipulat",
              "faked", "rigged", "cheat", "dishonest")
_NEGATORS = ("not", "never", "n't", "no ", "isn", "without", "rather than", "!=", "≠",
             "rule out", "cannot", "can't", "does not", "do not", "didn't", "unconfirmed",
             "unproven", "unclear", "alleged", "awaiting", "not established", "neither")
# grounded citation / "one of several possible causes" markers — NOT an accusation.
_CITATION_OR_LIST = ("carlisle", "might have contributed", "may have contributed",
                     "one of", "possible explanation", "candidate", "such as", "e.g.",
                     "unintentional error", "among the", "for example", "could be due",
                     "possible cause", "benign explanation")


def affirms_misconduct(text):
    """True iff `text` AFFIRMS misconduct about a trial. Negated/disclaimed mentions,
    word-internal matches (anti-fraud), and grounded citation/list contexts are exempt.
    A reusable honesty gate: any verdict for which this returns True is a blocking defect."""
    s = str(text).lower()
    for tok in _SENSITIVE:
        for m in re.finditer(re.escape(tok), s):
            i = m.start()
            if i > 0 and s[i - 1].isalpha():
                continue                                   # word-internal (anti-fraud)
            # the surrounding CLAUSE (back to the last sentence/quote boundary).
            cstart = max((s.rfind(d, 0, i) for d in ".:;'\""), default=-1) + 1
            pre = s[cstart:i]
            post = s[i + len(tok): i + len(tok) + 28]
            ctx = pre + " " + post
            if any(neg in ctx for neg in _NEGATORS):
                continue                                   # negated / disclaimed
            if any(c in (s[max(0, i - 48):i] + post) for c in _CITATION_OR_LIST):
                continue                                   # grounded citation / list
            return True                                    # an un-exempt affirmation
    return False


def _two_sided_p_from_summary(m1, sd1, n1, m2, sd2, n2, use="z"):
    """Two-sided p for the between-group mean difference from REPORTED summary stats.

    Carlisle used a normal comparison of summary statistics (use='z'); we also offer
    Welch's t (use='t', Welch-Satterthwaite df). Under simple randomization with
    continuous ~normal independent variables, this p ~ Uniform(0,1).
    """
    se = math.sqrt(sd1 ** 2 / n1 + sd2 ** 2 / n2)
    if se == 0:
        # identical, zero-variance report -> maximally "too similar"; p -> 1.
        return 1.0 - 1e-12
    stat = (m1 - m2) / se
    if use == "t":
        num = (sd1 ** 2 / n1 + sd2 ** 2 / n2) ** 2
        den = (sd1 ** 2 / n1) ** 2 / (n1 - 1) + (sd2 ** 2 / n2) ** 2 / (n2 - 1)
        df = num / den if den > 0 else (n1 + n2 - 2)
        return float(2 * stats.t.sf(abs(stat), df))
    return float(2 * stats.norm.sf(abs(stat)))


def carlisle_baseline_test(variables, alpha=0.001, design="unknown", p_stat="z"):
    """Carlisle baseline-anomaly test on a SINGLE trial's Table-1 continuous variables.

    variables: list of dicts. Continuous vars need
        {"name", "type":"continuous", "mean1","sd1","n1","mean2","sd2","n2",
         "stratum": bool (optional, default False)}.
      type=="categorical" -> EXCLUDED (the test is unsound for categorical vars).
      stratum==True        -> EXCLUDED (Carlisle's own practice).
      A var may instead supply a precomputed "p" (already two-sided) for continuous data.
    alpha: two-sided level for the combined-Z screen (default 1e-3 -> conservative,
           specificity ~ 1-alpha; soundness is cardinal so the default is strict).
    design: "simple" | "stratified" | "cluster" | "unknown" — if stratified/cluster,
            a prominent design_caveat is attached and the verdict is softened to
            "expected under this design," because those designs PRODUCE this signature.

    Returns the exact statistic + direction + BENIGN explanations + FALSE-POSITIVE
    modes + the inconsistency!=fraud ceiling. It NEVER returns a fraud verdict.
    """
    used, excluded = [], []
    for v in variables:
        nm = v.get("name", "?")
        if v.get("type") == "categorical":
            excluded.append({"name": nm, "reason": "categorical: Carlisle test is "
                             "UNSOUND for categorical variables (p not U(0,1)) — excluded"})
            continue
        if v.get("stratum"):
            excluded.append({"name": nm, "reason": "declared stratification factor — "
                             "excluded (stratified vars are balanced by design; "
                             "Carlisle excluded them too)"})
            continue
        if "p" in v and v["p"] is not None:
            p = float(v["p"])
        else:
            try:
                p = _two_sided_p_from_summary(float(v["mean1"]), float(v["sd1"]),
                                              float(v["n1"]), float(v["mean2"]),
                                              float(v["sd2"]), float(v["n2"]), use=p_stat)
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                excluded.append({"name": nm, "reason": "insufficient/invalid summary "
                                 "stats to recompute a baseline p — abstain on this var"})
                continue
        used.append({"name": nm, "p": min(max(p, 1e-12, ), 1 - 1e-12)})

    k = len(used)
    base = {"test": "Carlisle-baseline-anomaly", "kappa": 0.9,
            "kappa_note": "kappa=0.9 NOT 1.0: the Stouffer arithmetic is exact, but a "
                          "Carlisle flag is a calibrated STATISTICAL SCREEN, NOT an exact "
                          "certificate of impossibility like GRIM/allocation/percentage "
                          "(those are the true kappa=1 slice). FP rate ~ alpha by design.",
            "regime": "STATISTICAL SCREEN (not an exact certificate; FP rate ~ alpha, "
                      "inflated by correlation/stratification)",
            "design": design, "p_statistic": p_stat,
            "variables_used": [u["name"] for u in used],
            "variables_excluded": excluded,
            "k_continuous_tested": k, "alpha": alpha,
            "false_positive_modes": CARLISLE_FALSE_POSITIVE_MODES,
            "candidate_benign_explanations": CARLISLE_BENIGN_EXPLANATIONS,
            "ceiling": CEILING}

    if k == 0:
        base.update({"anomaly": None, "verdict": "ABSTAIN — no continuous, "
                     "non-stratified baseline variable available to test (categorical "
                     "and stratified variables are excluded by design)."})
        return base
    if k < 3:
        base["low_power_warning"] = ("k<3 continuous variables: the within-trial "
                                     "combination is unreliable (appraisal limitation).")

    ps = np.array([u["p"] for u in used], float)
    # Carlisle–Stouffer: z_i = Phi^{-1}(p_i) ~ N(0,1) under H0; Z = sum/sqrt(k).
    zi = stats.norm.ppf(ps)
    Z = float(zi.sum() / math.sqrt(k))
    p_combined = float(2 * stats.norm.sf(abs(Z)))           # two-sided
    z_crit = float(stats.norm.isf(alpha / 2))
    # Fisher (sensitive to SMALL p -> the too-DIFFERENT direction), as a cross-check.
    fisher = float(-2 * np.log(ps).sum())
    p_fisher = float(stats.chi2.sf(fisher, 2 * k))
    # KS test of the p-values against Uniform(0,1) (distribution-shape cross-check).
    ks_p = float(stats.kstest(ps, "uniform").pvalue) if k >= 2 else None

    anomaly = abs(Z) > z_crit
    if not anomaly:
        direction, verdict = None, ("CONSISTENT with simple randomization — the "
                                    "baseline p-values do not depart from U(0,1) at "
                                    f"alpha={alpha}. (Not a certificate of validity.)")
    elif Z > 0:
        direction = "too_similar"
        verdict = ("ANOMALY: baseline groups are MORE SIMILAR than expected under "
                   "SIMPLE randomization (excess of high baseline p-values). This is a "
                   "SCREEN for investigation, NOT fraud — see candidate_benign_"
                   "explanations (stratified allocation is the most common cause).")
    else:
        direction = "too_different"
        verdict = ("ANOMALY: baseline groups are MORE DIFFERENT than expected under "
                   "simple randomization (excess of low baseline p-values / imbalance). "
                   "A SCREEN, NOT fraud — chance imbalance, correlated covariates, or "
                   "reporting issues are candidate causes.")

    design_caveat = None
    if design in ("stratified", "cluster", "minimized"):
        design_caveat = (f"DESIGN = {design}: this design PRODUCES more-similar groups "
                         "by construction, so a 'too-similar' signal is EXPECTED and is "
                         "NOT an anomaly requiring explanation. The Carlisle test is "
                         "mis-calibrated for non-simple randomization; interpret with "
                         "this in mind (Carlisle excluded stratified variables).")
        base["design_caveat"] = design_caveat

    base.update({"stouffer_Z": round(Z, 4), "p_combined_two_sided": round(p_combined, 8),
                 "z_critical": round(z_crit, 4),
                 "fisher_stat": round(fisher, 4), "p_fisher_too_different": round(p_fisher, 8),
                 "ks_p_vs_uniform": None if ks_p is None else round(ks_p, 6),
                 "anomaly": bool(anomaly), "direction": direction, "verdict": verdict})
    return base


# --------------------------------------------------------------------------- #
#  EXACT consistency checks: allocation ratio / group size / percentage->count
# --------------------------------------------------------------------------- #
def allocation_ratio_consistency(group_sizes, ratio, tol=1):
    """EXACT: do reported group sizes match the stated allocation ratio?

    group_sizes: list of reported per-arm analysed N. ratio: list of ints, e.g.
    [1,1] or [2,1]. A reported split far from the stated ratio is an exact
    inconsistency (benign causes: post-randomization dropout, per-protocol vs ITT,
    typo). tol = allowed per-arm deviation in subjects (rounding slack).
    """
    if len(group_sizes) != len(ratio) or any(r <= 0 for r in ratio):
        return {"test": "allocation-ratio", "kappa": 1, "consistent": None,
                "note": "UNDEFINED: group_sizes/ratio mismatch — abstain.", "ceiling": CEILING}
    total = sum(group_sizes); rsum = sum(ratio)
    expected = [total * r / rsum for r in ratio]
    devs = [gs - ex for gs, ex in zip(group_sizes, expected)]
    consistent = all(abs(d) <= tol for d in devs)
    return {"test": "allocation-ratio", "kappa": 1, "exact": True,
            "group_sizes": group_sizes, "ratio": ratio,
            "expected_sizes": [round(e, 2) for e in expected],
            "deviations": [round(d, 2) for d in devs], "tol_subjects": tol,
            "consistent": bool(consistent),
            "note": ("consistent with the stated ratio" if consistent else
                     "INCONSISTENT with the stated allocation ratio (benign causes: "
                     "post-randomization dropout, per-protocol vs ITT analysis set, or "
                     "a typo — NOT evidence of misconduct)."),
            "ceiling": CEILING}


def percentage_count_consistency(pct_str, n):
    """EXACT (proportion analogue of GRIM): can a reported percentage of n subjects be
    achieved by an integer count?  A reported pct% with denominator n is consistent iff
    some integer k has round(100*k/n, D) == pct (D = reported decimals)."""
    if isinstance(pct_str, float):
        return {"test": "percentage->count", "kappa": 1, "consistent": None,
                "note": "pass the percentage as a STRING to preserve decimals.",
                "ceiling": CEILING}
    n = int(n)
    if n <= 0:
        return {"test": "percentage->count", "kappa": 1, "consistent": None,
                "note": "UNDEFINED: n<=0 — abstain.", "ceiling": CEILING}
    s = str(pct_str).strip()
    D = 0 if "." not in s else len(s.split(".")[1])
    pct = float(s)
    matches = [k for k in range(0, n + 1) if round(100.0 * k / n, D) == round(pct, D)]
    consistent = len(matches) > 0
    return {"test": "percentage->count", "kappa": 1, "exact": True,
            "percentage": s, "n": n, "decimals": D, "achievable_counts": matches[:8],
            "consistent": bool(consistent),
            "note": ("consistent: an integer count reproduces this percentage" if consistent
                     else "INCONSISTENT: no integer count of n gives this percentage "
                     "(benign causes: rounding/typo/different denominator)."),
            "ceiling": CEILING}


# --------------------------------------------------------------------------- #
#  E-value (observational causal -> SENSITIVITY, never a bare causal claim)
# --------------------------------------------------------------------------- #
def evalue(rr, lo=None, hi=None):
    """E-value (VanderWeele & Ding 2017). rr>0 observed risk ratio. Optional CI (lo,hi).

    Returns the minimum confounder association (with BOTH treatment and outcome) that
    could explain away the point estimate, and the CI E-value (using the limit nearest
    the null; 1 if the CI crosses 1). This is SENSITIVITY analysis: it never asserts a
    causal effect — it quantifies how robust an observational association is to an
    unmeasured confounder.
    """
    def _e(r):
        if r < 1:
            r = 1.0 / r
        return r + math.sqrt(r * (r - 1.0))
    if rr is None or rr <= 0:
        return {"test": "E-value", "kappa": 0.5, "evalue_point": None,
                "note": "UNDEFINED: need a positive risk ratio — abstain.", "ceiling": CEILING}
    out = {"test": "E-value", "kappa": 0.5, "rr": rr, "evalue_point": round(_e(rr), 4)}
    if lo is not None and hi is not None:
        if lo <= 1 <= hi:
            out["evalue_ci"] = 1.0
            out["ci_note"] = "CI includes 1 -> CI E-value = 1 (an arbitrarily weak confounder suffices)."
        else:
            limit = lo if lo > 1 else hi      # the limit nearest the null
            out["evalue_ci"] = round(_e(limit), 4)
    out["note"] = ("SENSITIVITY ONLY: an unmeasured confounder would need associations "
                   f"of at least {out['evalue_point']} (risk-ratio scale) with BOTH "
                   "treatment and outcome to explain away the point estimate. This is "
                   "NOT a causal claim — observational confounding is untestable.")
    out["ceiling"] = CEILING
    return out


# --------------------------------------------------------------------------- #
#  Adversarial self-test — pass good input, CATCH broken, NEVER false-accuse.
# --------------------------------------------------------------------------- #
def _sim_clean_trial(rng, k=8, n1=60, n2=60):
    """A genuinely simply-randomized trial: both arms drawn from the SAME distribution.
    Baseline p-values must be ~U(0,1) and the trial must NOT be flagged (calibration)."""
    vs = []
    for j in range(k):
        mu, sd = rng.uniform(20, 80), rng.uniform(5, 15)
        a = rng.normal(mu, sd, n1); b = rng.normal(mu, sd, n2)
        vs.append({"name": f"v{j}", "type": "continuous",
                   "mean1": a.mean(), "sd1": a.std(ddof=1), "n1": n1,
                   "mean2": b.mean(), "sd2": b.std(ddof=1), "n2": n2})
    return vs


def _selftest():
    rng = np.random.default_rng(20260620)

    # (a) CALIBRATION / SOUNDNESS: clean simply-randomized trials must rarely flag.
    #     False-flag rate at alpha must be ~alpha (a Carlisle flag is a SCREEN, not an
    #     exact certificate, so it CAN fire by chance — we verify it fires ~alpha often).
    alpha = 0.001
    n_trials, flags = 600, 0
    for _ in range(n_trials):
        r = carlisle_baseline_test(_sim_clean_trial(rng), alpha=alpha, design="simple")
        flags += int(r["anomaly"])
        assert not affirms_misconduct(r["verdict"]), "no trial verdict may affirm misconduct"
    # expected ~ n_trials*alpha = 0.6; Poisson tail: assert well-calibrated (<= 6).
    assert flags <= 6, f"clean-trial false-flag rate too high ({flags}/{n_trials}) — not sound"

    # (c) CATCH a fabricated TOO-SIMILAR trial (means improbably close across vars) AND
    #     attach benign explanations.
    fake = []
    for j in range(8):
        mu = rng.uniform(20, 80); sd = rng.uniform(5, 15)
        fake.append({"name": f"v{j}", "type": "continuous",
                     "mean1": mu, "sd1": sd, "n1": 60,
                     "mean2": mu + sd * 0.002, "sd2": sd, "n2": 60})   # almost identical
    rc = carlisle_baseline_test(fake, alpha=alpha, design="unknown")
    assert rc["anomaly"] is True and rc["direction"] == "too_similar", rc["verdict"]
    assert not affirms_misconduct(rc["verdict"]), "anomaly verdict must not affirm misconduct"
    assert any("stratified" in e.lower() for e in rc["candidate_benign_explanations"])
    assert rc["false_positive_modes"] and "INCONSISTENCY/ANOMALY != FRAUD" in rc["ceiling"]

    # too-DIFFERENT (imbalanced) trial -> flagged the other direction.
    diff = []
    for j in range(8):
        mu = rng.uniform(20, 80); sd = rng.uniform(5, 15)
        diff.append({"name": f"v{j}", "type": "continuous",
                     "mean1": mu, "sd1": sd, "n1": 60,
                     "mean2": mu + sd * 0.9, "sd2": sd, "n2": 60})      # big gaps
    rd = carlisle_baseline_test(diff, alpha=0.01, design="unknown")
    assert rd["anomaly"] is True and rd["direction"] == "too_different", rd["verdict"]

    # (d) NOT flag a legitimately STRATIFIED trial as fraud, and NAME stratification.
    #   d1: a declared stratification factor is EXCLUDED from the test.
    strat_vars = _sim_clean_trial(rng)
    strat_vars[0]["stratum"] = True
    rs = carlisle_baseline_test(strat_vars, alpha=alpha, design="stratified")
    assert any(e["name"] == "v0" for e in rs["variables_excluded"]), "stratum var must be excluded"
    assert "v0" not in rs["variables_used"]
    #   d2: even a too-similar stratified design must NOT read as fraud and MUST carry
    #       the design caveat naming stratification.
    rs2 = carlisle_baseline_test(fake, alpha=alpha, design="stratified")
    assert not affirms_misconduct(rs2["verdict"])
    assert rs2.get("design_caveat") and "stratified" in rs2["design_caveat"].lower()

    # the honesty checker itself must be sound: it ALLOWS negated mentions, CATCHES
    # affirmations (a verifier that can't fail is not a verifier).
    assert affirms_misconduct("this trial is fraudulent") is True
    assert affirms_misconduct("the data were fabricated") is True
    assert affirms_misconduct("the trial was rigged") is True
    assert affirms_misconduct("data were manipulated by the authors") is True
    assert affirms_misconduct("this is NOT fraud, only an anomaly") is False
    assert affirms_misconduct("never a finding of misconduct") is False
    # ---- hardening regressions caught by the cross-model audit (F1/F2) ----
    assert affirms_misconduct(CEILING) is False, "F1: must not fire on the grounded Carlisle quote"
    assert affirms_misconduct("fraud, unintentional error, or correlation are possible "
                              "causes of the excess") is False, "list-of-causes is not an accusation"
    assert affirms_misconduct("antifraud measures were in place") is False, "F2: word boundary"
    assert affirms_misconduct("fraud remains unconfirmed") is False, "F2: postceding negator"
    assert affirms_misconduct("cannot be concluded to involve fraud") is False, "F2: clause negator"
    # every emitted Carlisle output (clean + flagged) must pass the hardened checker
    for des in ("simple", "stratified", "unknown"):
        for vs in (_sim_clean_trial(rng), fake, diff):
            assert not affirms_misconduct(carlisle_baseline_test(vs, design=des)["verdict"])

    # categorical variables are EXCLUDED (unsound), never tested.
    cat = [{"name": "sex", "type": "categorical", "mean1": 0.5, "sd1": 0.5, "n1": 60,
            "mean2": 0.5, "sd2": 0.5, "n2": 60}] + _sim_clean_trial(rng, k=4)
    rcat = carlisle_baseline_test(cat, alpha=alpha, design="simple")
    assert any(e["name"] == "sex" for e in rcat["variables_excluded"]), "categorical excluded"
    assert "sex" not in rcat["variables_used"]

    # k==0 (all excluded) -> ABSTAIN, never crash, never accuse.
    rab = carlisle_baseline_test([{"name": "sex", "type": "categorical"}], design="simple")
    assert rab["anomaly"] is None and "ABSTAIN" in rab["verdict"]

    # ---- allocation-ratio (EXACT) ----
    assert allocation_ratio_consistency([60, 60], [1, 1])["consistent"] is True
    assert allocation_ratio_consistency([30, 90], [1, 1])["consistent"] is False
    assert allocation_ratio_consistency([80, 40], [2, 1])["consistent"] is True

    # ---- percentage->count (EXACT, GRIM-for-proportions) ----
    # n=50: 30% -> 15/50 exactly -> consistent; 33.3% with n=7 is impossible.
    assert percentage_count_consistency("30.0", 50)["consistent"] is True
    assert percentage_count_consistency("33.3", 7)["consistent"] is False
    assert percentage_count_consistency("28.6", 7)["consistent"] is True       # 2/7=28.57->28.6
    assert percentage_count_consistency("30", 0)["consistent"] is None         # abstain

    # ---- E-value ----
    ev = evalue(2.0)
    assert abs(ev["evalue_point"] - (2 + math.sqrt(2))) < 1e-3, ev          # 3.4142 (4dp)
    assert "NOT a causal claim" in ev["note"]
    evci = evalue(2.0, lo=0.9, hi=4.0)
    assert evci["evalue_ci"] == 1.0                                          # CI crosses 1
    evci2 = evalue(2.0, lo=1.5, hi=2.7)
    assert abs(evci2["evalue_ci"] - (1.5 + math.sqrt(1.5 * 0.5))) < 1e-3

    print(f"forensics_trial_verify selftest: PASS "
          f"(Carlisle calibrated: {flags}/{n_trials} clean trials flagged at alpha={alpha}; "
          f"catches too-similar & too-different; EXCLUDES categorical+stratified; "
          f"allocation/percentage EXACT; E-value correct; NO output ever says fraud)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: forensics_trial_verify.py selftest")
