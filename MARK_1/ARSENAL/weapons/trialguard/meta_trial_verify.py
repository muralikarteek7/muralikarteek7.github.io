#!/usr/bin/env python3
"""T-META — pool a body of trials + check heterogeneity & publication bias.

REUSE: the fixed/random pooling + I2 + Egger machinery is imported VERBATIM from
PSYMETRIX (`psychometrics_verify.meta_analysis`, grounded in psymetrix/GROUNDING.md).
ADD: nonparametric trim-and-fill (Duval & Tweedie 2000) for publication-bias
correction (GROUNDING.md sec 6).

What it certifies (kappa ~ 0.6): the pooled effect, the heterogeneity (I2), the
funnel asymmetry (Egger), and a trim-and-fill bias-corrected estimate REPRODUCE from
the supplied per-study effects + SEs. It does NOT certify the underlying trials are
valid or the treatment effective. A publication-bias flag is a ROBUSTNESS caveat, not
proof of suppression; trim-and-fill is a correction, not a verdict.
"""
import sys, os, math
import numpy as np

_PSYMETRIX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "psymetrix")
if _PSYMETRIX not in sys.path:
    sys.path.insert(0, _PSYMETRIX)
import psychometrics_verify as PM        # meta_analysis (fixed/random/I2/Egger) — REUSED


def trim_and_fill(effects, ses, side=None, max_iter=50):
    """Duval & Tweedie (2000) L0 trim-and-fill on a fixed-effect pooled estimate.

    Iterate: center by current pooled mean, rank |centered|, estimate k0 missing
    studies (L0 = (4*Tn - k(k+1))/(2k-1), Tn = sum of ranks of the positive-side
    studies), trim the k0 most extreme on the over-represented side, recompute the
    mean; repeat until k0 stabilizes. Then FILL k0 mirror-image studies and recompute.
    side: 'left' or 'right' = the side suspected to be SUPPRESSED (missing). If None,
    inferred from the sign of the asymmetry (studies missing opposite the bias).
    """
    y = np.asarray(effects, float); se = np.asarray(ses, float)
    k = len(y)
    if k < 3:
        return {"test": "trim-and-fill", "kappa": 0.6, "valid": False,
                "note": "UNDEFINED: need >=3 studies — abstain."}

    def wmean(yy, ss):
        w = 1.0 / ss ** 2
        return float((w * yy).sum() / w.sum())

    # The OVER-represented side holds the asymmetric extreme studies (we trim those);
    # the SUPPRESSED side is the opposite, where missing studies are imputed (filled).
    mu0 = wmean(y, se)
    if side is None:
        over_side = "right" if (y - mu0)[np.argmax(np.abs(y - mu0))] > 0 else "left"
    else:
        # caller passes the SUPPRESSED side directly -> over side is the opposite
        over_side = "left" if side == "right" else "right"
    suppressed_side = "left" if over_side == "right" else "right"
    over = 1 if over_side == "right" else -1     # trim studies with sign==over

    yt, st = y.copy(), se.copy()
    k0 = 0
    for _ in range(max_iter):
        mu = wmean(yt, st)
        c = yt - mu
        ranks = np.argsort(np.argsort(np.abs(c))) + 1     # rank of |centered|, 1..n
        signs = np.sign(c)
        Tn = ranks[signs == over].sum()
        n = len(yt)
        L0 = (4 * Tn - n * (n + 1)) / (2 * n - 1)
        new_k0 = max(0, int(round(L0)))
        if new_k0 == k0:
            break
        k0 = new_k0
        # trim k0 most extreme on the over-represented side from the FULL set
        c_full = y - mu
        cand = [i for i in range(k) if np.sign(c_full[i]) == over]
        cand.sort(key=lambda i: abs(c_full[i]), reverse=True)
        keep = sorted(set(range(k)) - set(cand[:k0]))
        yt, st = y[keep], se[keep]

    mu_trim = wmean(yt, st)
    # FILL: mirror the k0 most-extreme over-side studies across mu_trim
    c_full = y - mu_trim
    cand = [i for i in range(k) if np.sign(c_full[i]) == over]
    cand.sort(key=lambda i: abs(c_full[i]), reverse=True)
    fill_idx = cand[:k0]
    y_filled = list(y) + [2 * mu_trim - y[i] for i in fill_idx]
    se_filled = list(se) + [se[i] for i in fill_idx]
    mu_adj = wmean(np.array(y_filled), np.array(se_filled))

    return {"test": "trim-and-fill", "kappa": 0.6, "valid": True,
            "k_studies": k, "k0_imputed_missing": k0,
            "over_represented_side": over_side, "suppressed_side": suppressed_side,
            "pooled_observed": round(mu0, 5),
            "pooled_adjusted": round(mu_adj, 5),
            "bias_index": round(mu_adj - mu0, 5),
            "note": ("trim-and-fill imputes %d 'missing' study(ies) and shifts the "
                     "pooled effect by %.4f. This is a publication-bias SENSITIVITY "
                     "correction, NOT proof studies were suppressed; trim-and-fill is "
                     "known to over/under-correct under heterogeneity." % (k0, mu_adj - mu0))}


def meta(effects, ses):
    """Full T-META: reuse PSYMETRIX pooling/I2/Egger + add trim-and-fill."""
    base = PM.meta_analysis(effects, ses)        # REUSED verbatim
    base["sub_weapon"] = "T-META"
    base["trim_and_fill"] = trim_and_fill(effects, ses)
    base["ceiling_note"] = ("Pooled effect/I2/Egger/trim-and-fill REPRODUCE from the "
                            "supplied effects+SEs. NOT a claim the trials are valid or "
                            "the treatment effective. Egger/trim-and-fill are robustness "
                            "SCREENS, not proof of publication suppression.")
    return base


def _selftest():
    # symmetric, homogeneous body -> no funnel asymmetry, ~0 imputed studies
    eff = [0.20, 0.25, 0.18, 0.22, 0.19, 0.24, 0.21, 0.23]
    se = [0.05, 0.06, 0.04, 0.05, 0.05, 0.06, 0.04, 0.05]
    m = meta(eff, se)
    assert m["sub_weapon"] == "T-META"
    assert "I2_percent" in m and "egger_p" in m
    tf = m["trim_and_fill"]
    assert tf["valid"] and tf["k0_imputed_missing"] <= 1, tf      # symmetric -> ~0

    # ASYMMETRIC body (small studies all large+positive) -> trim-and-fill imputes
    # missing studies on the LEFT and pulls the pooled effect DOWN.
    eff2 = [0.10, 0.12, 0.11, 0.13, 0.55, 0.60, 0.70]   # 3 small-study outliers high
    se2 = [0.04, 0.05, 0.04, 0.05, 0.18, 0.20, 0.22]
    m2 = meta(eff2, se2)
    tf2 = m2["trim_and_fill"]
    assert tf2["k0_imputed_missing"] >= 1, tf2
    assert tf2["pooled_adjusted"] <= tf2["pooled_observed"] + 1e-9, tf2   # correction pulls down
    assert tf2["suppressed_side"] == "left", tf2

    # must abstain on too few studies
    assert trim_and_fill([0.1, 0.2], [0.05, 0.05])["valid"] is False

    print(f"meta_trial_verify selftest: PASS "
          f"(reuses PSYMETRIX pooling/I2/Egger; trim-and-fill imputes {tf2['k0_imputed_missing']} "
          f"missing study(ies) on the {tf2['suppressed_side']} and corrects "
          f"{tf2['pooled_observed']}->{tf2['pooled_adjusted']}; symmetric body ~0 imputed)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: meta_trial_verify.py selftest")
