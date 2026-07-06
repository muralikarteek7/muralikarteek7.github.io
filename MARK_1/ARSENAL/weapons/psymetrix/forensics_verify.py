#!/usr/bin/env python3
"""P-FORENSICS — the EXACT, sharp end of PSYMETRIX (the cap-set verifier of quant-psych).

These checks PROVE, with exact arithmetic, that reported summary statistics are
(in)consistent with the stated N and scale. They certify mathematical CONSISTENCY,
never TRUTH and NEVER FRAUD: a flagged inconsistency can be a rounding error, a
typo, or a reporting mistake. We report the exact arithmetic and stop. (See README
honesty rails. Real reputations are at stake.)

Methods (grounded in GROUNDING.md):
  - GRIM     : a reported mean of N integer responses can only be k/(N*items).
  - GRIMMER  : the implied integer sum-of-squares must exist in the SD-rounding band
               AND share parity with the GRIM integer sum.
  - SPRITE   : construct an integer sample matching (mean, SD, N, min, max). FOUND =
               constructive proof of possibility; NOT FOUND != impossibility.
  - TIVA     : too-small variance of z-scores across a set of p-values.
  - p-curve  : evidential value (right-skew) of a set of significant focal p-values.
  - Benford  : first-digit distribution goodness-of-fit (screening only).

Everything that can be exact is exact (fractions, integers). A verifier that cannot
FAIL is not a verifier: see _selftest() — every check is tested on a known-good
input (must PASS) AND a known-broken input (must be CAUGHT).
"""
import sys, json, math
from fractions import Fraction
from collections import Counter

# --------------------------------------------------------------------------- #
#  GRIM
# --------------------------------------------------------------------------- #
def _decimals(s):
    """Number of decimal places in a numeric string like '5.27' -> 2, '5' -> 0."""
    s = str(s).strip()
    if "." not in s:
        return 0
    return len(s.split(".")[1].rstrip())  # keep trailing zeros: '5.90' -> 2


def grim(mean_str, n, items=1):
    """Exact GRIM test.

    mean_str : reported mean as a STRING (preserves decimal places, e.g. '5.27').
    n        : sample size (int).
    items    : number of scale items averaged per subject (int, default 1).

    Returns a dict. consistent=True/False is exact. If N_eff >= 10^D the test has
    no discriminating power and we say so (consistent is reported True but flagged
    powerless=True so it is never read as evidence).
    """
    # R4 guard: a float loses the reported decimal count (0.1+0.2 -> 17 places),
    # which would produce a SPURIOUS inconsistency. Force the reported mean to be a
    # string (or exact int). Silent-wrong is worse than a loud error.
    if isinstance(mean_str, float):
        raise TypeError("grim: pass the reported mean as a STRING (e.g. '5.27') to "
                        "preserve its reported decimal places; a float loses them.")
    n = int(n); items = int(items)
    if n <= 0 or items <= 0:                              # R1 guard
        return {"test": "GRIM", "mean": str(mean_str), "n": n, "items": items,
                "consistent": None, "powerless": None,
                "note": "UNDEFINED: n and items must be >= 1 — abstain (cannot check)."}
    D = _decimals(mean_str)
    x = Fraction(str(mean_str))
    N_eff = n * items
    tol = Fraction(1, 2 * 10**D)                       # half-ULP rounding tolerance
    # consistent iff some integer k has k/N_eff within [x-tol, x+tol]
    lo = x - tol
    hi = x + tol
    k_lo = math.ceil(lo * N_eff)                        # smallest integer k with k/N_eff >= lo
    k_hi = math.floor(hi * N_eff)                       # largest integer k with k/N_eff <= hi
    consistent = k_lo <= k_hi
    powerless = N_eff >= 10**D
    # nearest achievable means for the report (exact fractions -> floats for display)
    floor_k = math.floor(x * N_eff)
    cands = sorted({floor_k, floor_k + 1})
    nearest = [round(c / N_eff, D + 2) for c in cands]
    return {
        "test": "GRIM", "mean": str(mean_str), "n": n, "items": items,
        "N_eff": N_eff, "decimals": D, "granularity": float(Fraction(1, N_eff)),
        "consistent": bool(consistent),
        "powerless": bool(powerless),
        "nearest_achievable_means": nearest,
        "note": ("no discriminating power (N_eff >= 10^decimals): a mean at this "
                 "precision is always GRIM-consistent" if powerless else
                 ("CONSISTENT with stated N/scale" if consistent else
                  "INCONSISTENT: no integer total k gives this mean for the stated "
                  "N/scale (rounding/typo/reporting error are possible explanations)")),
    }


# --------------------------------------------------------------------------- #
#  GRIMMER  (single-item integer responses; n-1 sample SD)
# --------------------------------------------------------------------------- #
def grimmer(mean_str, sd_str, n, items=1):
    """Exact analytic GRIMMER (Anaya/Allard). Requires GRIM to pass first.

    Tests whether a reported SD is achievable: there must be an integer sum-of-
    squares SS in the SD-rounding band that (a) back-rounds to the reported SD and
    (b) has the same parity as the GRIM integer sum T (since x^2 ≡ x mod 2).
    Only implemented for items==1 (integer responses); items>1 is flagged unsupported.
    """
    if isinstance(mean_str, float) or isinstance(sd_str, float):
        raise TypeError("grimmer: pass mean and SD as STRINGS to preserve decimals.")
    n = int(n); items = int(items)
    if n <= 1:                                            # R2 guard: SD undefined for n<=1
        return {"test": "GRIMMER", "consistent": None,
                "note": "UNDEFINED: sample SD needs n >= 2 — abstain (cannot check)."}
    g = grim(mean_str, n, items)
    if items != 1:
        return {"test": "GRIMMER", "supported": False,
                "note": "GRIMMER here supports single-item integer responses only (items==1).",
                "grim": g}
    if not g["consistent"]:
        return {"test": "GRIMMER", "consistent": False, "reason": "GRIM already fails",
                "grim": g, "note": "INCONSISTENT (mean itself is GRIM-impossible)."}

    dSD = _decimals(sd_str)
    sd = float(sd_str)
    mean_f = float(Fraction(str(mean_str)))
    T = round(mean_f * n)                               # GRIM integer sum
    realmean = T / n
    half = 0.5 * 10 ** (-dSD)
    Lsig = max(0.0, sd - half)
    Usig = sd + half
    Lb = (n - 1) * Lsig ** 2 + n * realmean ** 2
    Ub = (n - 1) * Usig ** 2 + n * realmean ** 2
    ss_lo = math.ceil(Lb - 1e-9)
    ss_hi = math.floor(Ub + 1e-9)
    parity = T % 2
    matches = []
    for SS in range(ss_lo, ss_hi + 1):
        var = (SS - n * realmean ** 2) / (n - 1)
        if var < 0:
            continue
        back = math.sqrt(var)
        if round(back, dSD) == round(sd, dSD):
            matches.append({"SS": SS, "parity_ok": SS % 2 == parity,
                            "back_sd": round(back, dSD + 4)})
    parity_ok = any(m["parity_ok"] for m in matches)
    sd_match = len(matches) > 0
    consistent = sd_match and parity_ok
    if consistent:
        note = "CONSISTENT with stated N/scale"
    elif sd_match and not parity_ok:
        note = ("INCONSISTENT (parity): an SS reproduces the SD but its parity "
                "differs from the integer sum — no integer sample can yield both this "
                "mean and SD (rounding/typo/reporting error are possible explanations)")
    else:
        note = ("INCONSISTENT: no integer sum-of-squares in the SD-rounding band "
                "reproduces the reported SD (rounding/typo/reporting error possible)")
    return {"test": "GRIMMER", "mean": str(mean_str), "sd": str(sd_str), "n": n,
            "T_integer_sum": T, "realmean": round(realmean, 6),
            "ss_band": [ss_lo, ss_hi], "ss_matches": matches,
            "sd_match": sd_match, "parity_ok": parity_ok,
            "consistent": bool(consistent), "note": note}


# --------------------------------------------------------------------------- #
#  SPRITE  (constructive possibility; "not found" != impossible)
# --------------------------------------------------------------------------- #
def sprite(mean_str, sd_str, n, vmin, vmax, items=1, max_iter=80000, seed=12345):
    """Construct an integer sample in [vmin,vmax]^n whose mean & SD round to the
    reported values. Deterministic LCG (no global RNG) so the self-test is stable.

    FOUND -> constructive PROOF the stats are possible (exhibits a witness).
    NOT FOUND -> INCONCLUSIVE (heuristic search exhausted), NOT proof of impossibility.
    Runs GRIM/GRIMMER first; if those give an exact impossibility, reports it.
    """
    n = int(n); vmin = int(vmin); vmax = int(vmax)
    pre = grimmer(mean_str, sd_str, n, items) if items == 1 else None
    if pre and not pre.get("consistent", True) and pre.get("sd_match") is not None:
        return {"test": "SPRITE", "found": False, "exact_impossible": True,
                "reason": "GRIM/GRIMMER exact impossibility", "grimmer": pre,
                "note": "Exactly impossible (GRIMMER) — no search needed."}
    dM = _decimals(mean_str); dSD = _decimals(sd_str)
    target_m = float(mean_str); target_sd = float(sd_str)

    def lcg(state):
        while True:
            state = (1103515245 * state + 12345) & 0x7FFFFFFF
            yield state
    rng = lcg(seed)

    def rint(a, b):
        return a + next(rng) % (b - a + 1)

    # seed a vector with the right (rounded) mean
    T = round(target_m * n)
    T = max(n * vmin, min(n * vmax, T))
    vec = [vmin] * n
    rem = T - n * vmin
    i = 0
    while rem > 0:
        add = min(vmax - vec[i], rem)
        vec[i] += add; rem -= add; i = (i + 1) % n
    import statistics as st
    for _ in range(max_iter):
        m = sum(vec) / n
        sd = st.pstdev(vec) if False else (st.stdev(vec) if n > 1 else 0.0)
        if round(m, dM) == round(target_m, dM) and round(sd, dSD) == round(target_sd, dSD):
            return {"test": "SPRITE", "found": True, "witness_summary": {
                        "mean": round(m, dM + 2), "sd": round(sd, dSD + 2),
                        "min": min(vec), "max": max(vec), "n": n,
                        "value_counts": dict(sorted(Counter(vec).items()))},
                    "note": "POSSIBLE — a valid integer sample exists (constructive proof)."}
        # mean-preserving pair swap toward target SD
        a, b = rint(0, n - 1), rint(0, n - 1)
        if a == b:
            continue
        too_low = sd < target_sd
        if too_low:  # spread apart
            lo_i, hi_i = (a, b) if vec[a] <= vec[b] else (b, a)
            if vec[lo_i] > vmin and vec[hi_i] < vmax:
                vec[lo_i] -= 1; vec[hi_i] += 1
        else:        # squeeze together
            lo_i, hi_i = (a, b) if vec[a] <= vec[b] else (b, a)
            if vec[hi_i] > vec[lo_i]:
                vec[lo_i] += 1; vec[hi_i] -= 1
    return {"test": "SPRITE", "found": False, "exact_impossible": False,
            "note": "NOT FOUND by bounded search — INCONCLUSIVE, not a proof of "
                    "impossibility (only GRIM/GRIMMER give exact impossibility)."}


# --------------------------------------------------------------------------- #
#  TIVA  (Test of Insufficient Variance)
# --------------------------------------------------------------------------- #
def _norm_isf(p):
    """Inverse survival function of standard normal (one-tailed z for p). scipy-free."""
    # Acklam's rational approximation to the normal quantile; ppf(1-p).
    q = 1.0 - p
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow = 0.02425; phigh = 1 - plow
    if q < plow:
        t = math.sqrt(-2 * math.log(q))
        return (((((c[0]*t+c[1])*t+c[2])*t+c[3])*t+c[4])*t+c[5]) / \
               ((((d[0]*t+d[1])*t+d[2])*t+d[3])*t+1)
    if q <= phigh:
        t = q - 0.5; r = t*t
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*t / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    t = math.sqrt(-2 * math.log(1 - q))
    return -(((((c[0]*t+c[1])*t+c[2])*t+c[3])*t+c[4])*t+c[5]) / \
            ((((d[0]*t+d[1])*t+d[2])*t+d[3])*t+1)


def _chi2_cdf(x, k):
    """Lower-tail CDF of chi-square with k dof via regularized lower incomplete gamma."""
    if x <= 0:
        return 0.0
    a = k / 2.0; xx = x / 2.0
    # series expansion for P(a, xx) (Numerical Recipes gammp)
    if xx < a + 1:
        ap = a; s = 1.0 / a; delv = s
        for _ in range(1000):
            ap += 1; delv *= xx / ap; s += delv
            if abs(delv) < abs(s) * 1e-12:
                break
        return s * math.exp(-xx + a * math.log(xx) - math.lgamma(a))
    # continued fraction for Q(a,xx)
    b = xx + 1 - a; c = 1e300; dd = 1.0 / b; h = dd
    for i in range(1, 1000):
        an = -i * (i - a); b += 2
        dd = an * dd + b
        if abs(dd) < 1e-300: dd = 1e-300
        c = b + an / c
        if abs(c) < 1e-300: c = 1e-300
        dd = 1.0 / dd; delv = dd * c; h *= delv
        if abs(delv - 1) < 1e-12:
            break
    q = math.exp(-xx + a * math.log(xx) - math.lgamma(a)) * h
    return 1.0 - q


def tiva(p_values, two_tailed=True):
    """TIVA: flag insufficient variance of z-scores. one-tailed z = isf(p)."""
    if len(p_values) < 2:                                # R3 guard: var needs k>=2
        return {"test": "TIVA", "k": len(p_values), "insufficient_variance": None,
                "note": "UNDEFINED: TIVA needs >= 2 p-values (variance/df) — abstain."}
    ps = [min(max(float(p), 1e-12), 1 - 1e-12) for p in p_values]
    if two_tailed:
        ps = [p / 2 for p in ps]
    zs = [_norm_isf(p) for p in ps]
    k = len(zs)
    mean_z = sum(zs) / k
    var_z = sum((z - mean_z) ** 2 for z in zs) / (k - 1)     # sample variance
    chi2 = (k - 1) * var_z
    p_left = _chi2_cdf(chi2, k - 1)
    return {"test": "TIVA", "k": k, "var_z": round(var_z, 4),
            "chi2": round(chi2, 4), "df": k - 1, "p_left_tail": round(p_left, 5),
            "insufficient_variance": p_left < 0.05,
            "note": ("INSUFFICIENT VARIANCE flagged (var of z too small; p<.05): "
                     "results are improbably uniform — possible selective reporting. "
                     "Inconsistency, NOT proof of misconduct." if p_left < 0.05 else
                     "variance not improbably small (conservative test).")}


# --------------------------------------------------------------------------- #
#  p-curve  (right-skew / evidential value; Stouffer + half-curve)
# --------------------------------------------------------------------------- #
def _norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def pcurve(p_values):
    """Evidential-value test (2015 Stouffer + half-curve). Uses only significant
    (p<.05) values; right-skew pp = p/.05. Returns evidential_value per the rule:
    half-curve right-skew p<.05 OR both full & half right-skew p<.1."""
    sig = [float(p) for p in p_values if float(p) < 0.05]
    if len(sig) < 2:
        return {"test": "p-curve", "evidential_value": None,
                "note": "fewer than 2 significant focal p-values — abstain."}
    def stouffer(ps, cutoff):
        sub = [p for p in ps if p < cutoff]
        if len(sub) < 1:
            return None
        pps = [min(max(p / cutoff, 1e-9), 1 - 1e-9) for p in sub]   # right-skew pp
        z = sum(_norm_isf(1 - pp) for pp in pps) / math.sqrt(len(sub))
        # right-skew => pp small => z negative => left-tail p small
        return _norm_cdf(z)
    p_full = stouffer(sig, 0.05)
    p_half = stouffer(sig, 0.025)
    # binomial sign test at .025
    low = sum(1 for p in sig if p < 0.025); k = len(sig)
    binom = sum(math.comb(k, i) for i in range(low, k + 1)) / 2 ** k
    if p_half is not None and p_half < 0.05:
        ev = True
    elif p_half is not None and p_full is not None and p_full < 0.1 and p_half < 0.1:
        ev = True
    else:
        ev = False
    return {"test": "p-curve", "k_significant": k, "k_below_.025": low,
            "right_skew_p_full": None if p_full is None else round(p_full, 5),
            "right_skew_p_half": None if p_half is None else round(p_half, 5),
            "binomial_p_low_at_.025": round(binom, 5),
            "evidential_value": bool(ev),
            "note": ("right-skewed -> the set has evidential value" if ev else
                     "NOT right-skewed -> lacks evidential value (consistent with "
                     "null/selective reporting; not proof of misconduct).")}


# --------------------------------------------------------------------------- #
#  Benford first-digit
# --------------------------------------------------------------------------- #
BENFORD = {d: math.log10(1 + 1 / d) for d in range(1, 10)}


def benford(values):
    """First-digit Benford GoF: chi2 (df=8, crit 15.507) + Nigrini MAD bands."""
    if not values:
        return {"test": "Benford-first-digit", "N": 0, "note": "UNDEFINED: no values — abstain."}
    firsts = []
    for v in values:
        v = abs(float(v))
        if v == 0:
            continue
        while v < 1:
            v *= 10
        while v >= 10:
            v /= 10
        firsts.append(int(v))
    N = len(firsts)
    obs = Counter(firsts)
    chi2 = sum((obs.get(d, 0) - N * BENFORD[d]) ** 2 / (N * BENFORD[d]) for d in range(1, 10))
    mad = sum(abs(obs.get(d, 0) / N - BENFORD[d]) for d in range(1, 10)) / 9
    band = ("close conformity" if mad <= 0.006 else "acceptable" if mad <= 0.012
            else "marginal" if mad <= 0.015 else "nonconformity")
    return {"test": "Benford-first-digit", "N": N, "chi2": round(chi2, 3),
            "df": 8, "chi2_crit_.05": 15.507, "chi2_reject": chi2 > 15.507,
            "MAD": round(mad, 5), "MAD_band": band,
            "note": "screening only; deviation is NOT proof of manipulation."}


# --------------------------------------------------------------------------- #
#  Adversarial self-test: every check must PASS good input AND CATCH broken input
# --------------------------------------------------------------------------- #
def _selftest():
    # ---- GRIM: grounded literature example (5.27/43 impossible) + ground-truth ----
    assert grim("5.27", 43)["consistent"] is False, "GRIM should flag 5.27/43"
    assert grim("5.26", 43)["consistent"] is True, "GRIM should pass 5.26/43"
    assert grim("5.90", 40, items=3)["consistent"] is True, "GRIM 5.90/40/3items"
    # machine ground truth: real integer sample -> its rounded mean MUST be consistent
    sample = [1, 2, 2, 3, 4, 5, 5, 3, 2, 4, 1, 5, 3, 3, 2]      # n=15 integers
    true_mean = sum(sample) / len(sample)
    ms = f"{true_mean:.2f}"
    assert grim(ms, len(sample))["consistent"] is True, f"GRIM must pass true mean {ms}"
    # corrupt the last digit by a typo that breaks granularity -> must be caught
    bad = f"{true_mean + 0.01:.2f}"
    gb = grim(bad, len(sample))
    assert (gb["consistent"] is False) or gb["powerless"], "GRIM should catch typo or be powerless"
    # powerless regime detected, not silently passed
    assert grim("5.27", 200)["powerless"] is True, "N_eff>=100 at 2dp must be powerless"

    # ---- GRIMMER: grounded parity example + constructive ground truth ----
    gm = grimmer("3.44", "2.47", 18)
    assert gm["consistent"] is False and gm["sd_match"] is True and gm["parity_ok"] is False, \
        f"GRIMMER 3.44/2.47/18 must fail on parity: {gm}"
    # ground truth: compute the EXACT mean/SD of a real integer sample and assert pass
    import statistics as st
    s2 = [2, 3, 3, 4, 5, 1, 2, 4, 5, 3]
    m2 = f"{sum(s2)/len(s2):.2f}"; sd2 = f"{st.stdev(s2):.2f}"
    gg = grimmer(m2, sd2, len(s2))
    assert gg["consistent"] is True, f"GRIMMER must pass real sample {m2}/{sd2}: {gg}"

    # ---- SPRITE: possible -> found witness; exact-impossible -> reported ----
    sp = sprite(m2, sd2, len(s2), 1, 5)
    assert sp["found"] is True, f"SPRITE should construct a witness for {m2}/{sd2}: {sp}"
    sp_imp = sprite("3.44", "2.47", 18, 1, 5)
    assert sp_imp["found"] is False and sp_imp.get("exact_impossible") is True, \
        "SPRITE should defer to GRIMMER exact impossibility"

    # ---- TIVA: honest spread passes; near-identical z's flagged ----
    honest = [0.001, 0.04, 0.2, 0.5, 0.01, 0.3]
    assert tiva(honest)["insufficient_variance"] is False, "TIVA should not flag honest spread"
    suspicious = [0.049, 0.048, 0.047, 0.049, 0.048, 0.047, 0.049, 0.048]
    assert tiva(suspicious)["insufficient_variance"] is True, "TIVA should flag clustered p's"

    # ---- p-curve: strong evidence right-skewed; flat set is not ----
    strong = [0.001, 0.002, 0.008, 0.001, 0.004, 0.01]
    assert pcurve(strong)["evidential_value"] is True, "p-curve should see evidential value"
    flat = [0.049, 0.048, 0.045, 0.047, 0.049, 0.046]
    assert pcurve(flat)["evidential_value"] is False, "p-curve should reject flat/left set"

    # ---- Benford: Fibonacci first digits conform; uniform digits do not ----
    fib = [1, 1]
    for _ in range(200):
        fib.append(fib[-1] + fib[-2])
    assert benford(fib[2:])["MAD_band"] in ("close conformity", "acceptable"), "Fibonacci ~Benford"
    uniform = list(range(1, 10)) * 30   # equal first-digit frequency -> nonconformity
    assert benford([v + 0.0 for v in uniform])["chi2_reject"] is True, "uniform digits must fail"

    # ---- robustness guards (caught by the cross-model audit, 2026-06-20) ----
    # malformed input must ABSTAIN or raise loudly — never crash, never silently wrong.
    assert grim("5.0", 0)["consistent"] is None, "n=0 must abstain, not crash"
    assert grimmer("5.0", "0.0", 1)["consistent"] is None, "n=1 GRIMMER must abstain"
    assert tiva([0.03])["insufficient_variance"] is None, "k=1 TIVA must abstain"
    assert benford([])["N"] == 0, "empty Benford must abstain"
    try:
        grim(0.1 + 0.2, 10)                              # float -> 17 spurious decimals
        raise AssertionError("float mean must raise, not silently mis-handle")
    except TypeError:
        pass

    print("forensics_verify selftest: PASS "
          "(GRIM/GRIMMER/SPRITE/TIVA/p-curve/Benford pass good input, catch broken input, "
          "and abstain/raise on malformed input)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: forensics_verify.py selftest")
