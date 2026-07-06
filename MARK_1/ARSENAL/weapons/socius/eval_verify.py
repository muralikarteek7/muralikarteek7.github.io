#!/usr/bin/env python3
"""S-CAUSAL — frozen verifier for SENSITIVITY TO UNMEASURED CONFOUNDING (kappa ~= 0.5).

Implements the E-value (VanderWeele & Ding, 2017, Annals of Internal Medicine,
167:268-274). The E-value is the minimum strength of association, on the risk-
ratio scale, that an unmeasured confounder would need with BOTH the exposure and
the outcome to fully explain away an observed exposure-outcome association,
conditional on the measured covariates.

Exact formula (RR = point estimate on the risk-ratio scale, RR >= 1):
    E-value = RR + sqrt( RR * (RR - 1) )
For RR < 1, first invert: RR* = 1/RR, then apply the same formula.
For the confidence-interval limit LL (the limit closer to the null = 1):
    if LL <= 1:  E-value(CI) = 1   (already compatible with the null)
    else:        E-value(CI) = LL + sqrt( LL * (LL - 1) )

Approximate conversions to the RR scale (VanderWeele & Ding 2017, Table; and
VanderWeele 2017 for the SMD case):
    odds ratio (common outcome):  RR ~= sqrt(OR)
    hazard ratio (common outcome): RR ~= (1 - 0.5^sqrt(HR)) / (1 - 0.5^sqrt(1/HR))
    standardized mean diff d:      RR ~= exp(0.91 * d)
(For a rare outcome OR ~= RR and HR ~= RR; we use the conservative common-outcome
forms by default and label the conversion used.)

kappa ~= 0.5: the E-value is an EXACT, machine-checkable function of the reported
estimate (that part is kappa=1). But whether the E-value is "large enough" is a
JUDGMENT about how strong a plausible unmeasured confounder could be in this
substantive context — that judgment is kappa=0 and goes to armor. This verifier
computes the number exactly and flags fragility against a *declared* benchmark
confounding strength; it does not certify the causal claim true.
"""
import sys, json, math


def e_value(rr):
    """E-value for a risk ratio rr (rr may be <1; we invert)."""
    # Guard non-finite rr FIRST and consistently with the rr<=0 guard: e_value(inf)
    # silently returns inf and e_value(nan) returns nan, which in callers becomes a
    # confident verdict on nonsense (inf>=benchmark -> robust ACCEPT). nan<=0 is also
    # False, so the rr<=0 guard alone lets nan through. Reject both loudly here so the
    # guarding is consistent at the function itself, not only at assess_sensitivity.
    if not math.isfinite(rr):
        raise ValueError("risk ratio must be finite and > 0")
    if rr <= 0:
        raise ValueError("risk ratio must be > 0")
    if rr < 1:
        rr = 1.0 / rr
    return rr + math.sqrt(rr * (rr - 1.0))


def to_risk_ratio(estimate, scale):
    """Convert a reported effect to the approximate risk-ratio scale."""
    scale = scale.lower()
    if scale in ("rr", "risk_ratio", "riskratio"):
        return estimate
    if scale in ("or", "odds_ratio", "oddsratio"):
        return math.sqrt(estimate) if estimate >= 1 else 1.0 / math.sqrt(1.0 / estimate)
    if scale in ("hr", "hazard_ratio", "hazardratio"):
        hr = estimate
        return (1 - 0.5 ** math.sqrt(hr)) / (1 - 0.5 ** math.sqrt(1.0 / hr))
    if scale in ("d", "smd", "cohen_d", "std_mean_diff"):
        return math.exp(0.91 * estimate)
    raise ValueError(f"unknown effect scale: {scale}")


def assess_sensitivity(estimate, scale="RR", ci_limit=None,
                       benchmark_confounding=2.0):
    """Compute the E-value and flag fragility.

    benchmark_confounding: the RR-scale confounder strength considered plausibly
    present in this substantive area (declared up front, kappa=0 judgment). The
    finding is flagged FRAGILE if the E-value is below this benchmark, i.e. a
    confounder no stronger than already-known confounders in the field could
    explain the result away.
    """
    # Guard non-finite inputs, consistent with the e_value() rr<=0 guard. A non-
    # finite estimate (inf/nan) carries no information: e_value(inf)=inf would make
    # inf>=benchmark a confident "robust" ACCEPT on nonsense, and nan>=benchmark a
    # confident "not robust" verdict — both are unsafe. Reject loudly instead.
    if not math.isfinite(estimate):
        raise ValueError("estimate must be a finite number")
    if ci_limit is not None and not math.isfinite(ci_limit):
        raise ValueError("ci_limit must be a finite number")
    rr = to_risk_ratio(estimate, scale)
    # Guard a non-finite COMPUTED risk ratio. A finite estimate can still overflow
    # inside to_risk_ratio for some scales -> a non-finite rr makes e_value(inf)=inf,
    # and inf>=benchmark a confident "robust" ACCEPT on effectively-nonsense input.
    # The finite-INPUT guard above does not catch this computed-overflow path.
    if not math.isfinite(rr):
        raise ValueError("effect estimate overflows the risk-ratio scale (non-finite); "
                         "not finitely assessable")
    ev_point = e_value(rr)
    ev_ci = None
    if ci_limit is not None:
        rr_ci = to_risk_ratio(ci_limit, scale)
        if not math.isfinite(rr_ci):
            raise ValueError("ci_limit overflows the risk-ratio scale (non-finite); "
                             "not finitely assessable")
        if (rr >= 1 and rr_ci <= 1) or (rr < 1 and rr_ci >= 1):
            ev_ci = 1.0
        else:
            ev_ci = e_value(rr_ci)
    governing = ev_ci if ev_ci is not None else ev_point
    # Backstop: even a FINITE rr can overflow e_value (rr*(rr-1) -> inf) for an
    # astronomically large but finite estimate (CRUCIBLE socius_evalue overflow
    # false-accept: smd 500 -> rr=exp(455) finite, but e_value(rr) -> inf -> robust
    # =True on nonsense). Never decide robustness on a non-finite governing E-value.
    if not math.isfinite(governing):
        raise ValueError("computed E-value is non-finite (effect estimate too large to "
                         "assess finitely); not assessable")
    robust = governing >= benchmark_confounding
    return {
        "sub_weapon": "S-CAUSAL", "kappa": 0.5,
        "reported_estimate": estimate, "scale": scale,
        "approx_risk_ratio": rr,
        "e_value_point": ev_point,
        "e_value_ci_limit": ev_ci,
        "benchmark_confounding_RR": benchmark_confounding,
        "robust_to_confounding": bool(robust),
        "interpretation": (
            f"An unmeasured confounder would need to be associated with both "
            f"exposure and outcome by a risk ratio of {governing:.2f}-fold each "
            f"(beyond measured covariates) to explain away the "
            f"{'CI limit' if ev_ci is not None else 'point estimate'}."),
        "ceiling_note": "The E-value is exact (kappa=1); the verdict 'robust' "
                        "depends on the declared benchmark, a kappa=0 judgment. "
                        "A large E-value does NOT prove the claim is causal.",
    }


def _selftest():
    # Anchor on the published worked example: VanderWeele & Ding 2017 report that
    # an observed RR of 3.9 has an E-value of 7.26 (smoking-lung-cancer style).
    assert abs(e_value(3.9) - 7.26) < 0.01, e_value(3.9)
    # RR = 2 -> E = 2 + sqrt(2) = 3.4142...
    assert abs(e_value(2.0) - (2 + math.sqrt(2))) < 1e-9
    # symmetry under inversion: E(0.5) == E(2)
    assert abs(e_value(0.5) - e_value(2.0)) < 1e-9
    # e_value() rejects non-finite rr directly (defense-in-depth at the function, not
    # only at assess_sensitivity): inf/-inf/nan must raise, never return a non-finite.
    for bad in (float("inf"), float("-inf"), float("nan")):
        raised = False
        try:
            e_value(bad)
        except ValueError:
            raised = True
        assert raised, "REGRESSION: e_value(%r) did not raise on non-finite rr." % bad
    # Known-FRAGILE: a barely-there RR=1.05 must be flagged not-robust against a
    # plausible benchmark of 2.0 (the verifier must be able to FAIL a weak claim)
    weak = assess_sensitivity(1.05, "RR", benchmark_confounding=2.0)
    assert weak["robust_to_confounding"] is False, weak
    # Known-ROBUST: a strong RR=10 must pass
    strong = assess_sensitivity(10.0, "RR", benchmark_confounding=2.0)
    assert strong["robust_to_confounding"] is True, strong
    # CI that crosses the null collapses the governing E-value to 1 -> fragile
    crosses = assess_sensitivity(1.8, "RR", ci_limit=0.95, benchmark_confounding=2.0)
    assert crosses["e_value_ci_limit"] == 1.0 and not crosses["robust_to_confounding"]
    # FROZEN REGRESSION (CRUCIBLE socius_evalue ABSTAIN/CRASH kill, 2026-06-20): a
    # non-finite estimate must NEVER yield a confident verdict. Before the fix,
    # e_value(inf)=inf and inf>=2.0 made robust_to_confounding=True — a confident
    # ACCEPT on nonsense; nan>=2.0 made it a confident False (REJECT on nonsense).
    # The guard must REJECT (raise ValueError) both, never return a verdict dict.
    for bad in (float("inf"), float("nan"), float("-inf")):
        raised = False
        try:
            assess_sensitivity(bad, "RR", benchmark_confounding=2.0)
        except ValueError:
            raised = True
        assert raised, ("REGRESSION: non-finite estimate %r did not raise — the "
                        "CRUCIBLE non-finite false-accept hole has reopened." % bad)
    # the guard also covers a non-finite CI limit (it feeds the governing E-value).
    raised = False
    try:
        assess_sensitivity(3.9, "RR", ci_limit=float("inf"), benchmark_confounding=2.0)
    except ValueError:
        raised = True
    assert raised, "REGRESSION: non-finite ci_limit did not raise."
    # FROZEN REGRESSION (CRUCIBLE socius_evalue OVERFLOW false-accept, 2026-06-20):
    # a large but FINITE estimate whose COMPUTED E-value overflows to inf must also
    # REJECT, never certify robust=True on the resulting inf. smd 500 -> rr=exp(455)
    # is finite but e_value(rr) -> inf; rr-scale 1e200 -> e_value -> inf. The
    # finite-INPUT guard does not catch these; the computed-rr / governing guards must.
    for est, scale in ((500.0, "smd"), (1e200, "rr")):
        raised = False
        try:
            assess_sensitivity(est, scale, benchmark_confounding=2.0)
        except ValueError:
            raised = True
        assert raised, ("REGRESSION: finite-but-overflowing estimate %r (%s) did not "
                        "raise — the CRUCIBLE overflow false-accept hole has reopened."
                        % (est, scale))
    print("eval_verify selftest: PASS (anchored to RR=3.9->7.26; FAILS weak/CI-crossing "
          "claims; REJECTS non-finite estimate/ci_limit AND finite-overflow estimate "
          "[CRUCIBLE regressions])")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 3:
        est = float(sys.argv[2]); scale = sys.argv[1]
        ci = float(sys.argv[3]) if len(sys.argv) > 3 else None
        print(json.dumps(assess_sensitivity(est, scale, ci), indent=2))
    else:
        print("usage: eval_verify.py selftest | <scale> <estimate> [ci_limit]")
