#!/usr/bin/env python3
"""SYMBOLICA frozen agreement gate — the whole game.

Doctrine (the box): *a single-engine answer is a CLAIM, not a result.* SYMBOLICA
ships an exact closed form / identity / special value ONLY when >=2 INDEPENDENT
methods agree, with a methodologically-DIFFERENT 3rd check on load-bearing cases.

The three independent method FAMILIES used here (chosen so a shared library bug is
unlikely to fool all of them):
  - SYMBOLIC   : sympy's symbolic engine (integrate / simplify / summation).
                 Heuristic — can fail to simplify a true zero, or pick a wrong
                 branch. ONE symbolic answer is a claim.
  - NUMERIC-AP : mpmath arbitrary-precision evaluation / tanh-sinh quadrature
                 (mp.quad), driven through sympy.lambdify(..., 'mpmath') so the
                 special-function *implementations* are mpmath's, not sympy's.
  - NUMERIC-DP : scipy QUADPACK (adaptive Gauss-Kronrod, double precision) and/or
                 a SERIES expansion — a DIFFERENT algorithm family from NUMERIC-AP
                 (Romberg/tanh-sinh vs Gauss-Kronrod vs Taylor coefficients).

Agreement of SYMBOLIC + NUMERIC-AP is the two-method floor. Agreement of two
*same-family* numeric methods is a shared-blind-spot RISK, recorded as such; a
load-bearing claim must add the diversified 3rd family.

LABELS ARE NOT INTERCHANGEABLE:
  - "symbolically proven (simplify->0)"  : sympy.simplify(lhs-rhs) collapses to an
       UNCONDITIONAL exact 0. Strong — but sympy.simplify is NOT a trusted proof
       kernel (PROOFSMITH is). So even this is "machine-simplified to 0", weaker
       than a Lean term. We say so.
  - "verified to D digits at K points"   : empirical multi-point high-precision
       agreement. Very strong evidence (transcendental functions agreeing to 30+
       digits at 20 independent points is not coincidence) but NOT a proof.
Never upgrade the second wording to "proven".

"A gate that can't fail is not a gate": _selftest() requires the gate to (a) ACCEPT
a correct closed form, (b) REJECT a closed form off by a constant/factor, (c) REJECT
a domain-restricted form presented as global, (d) REJECT a non-convergent sum given
a fake finite closed form. All four must pass or NOTHING SYMBOLICA outputs is trusted.
"""
import sys, math, random
import sympy as sp
import mpmath as mp

# scipy is the diversified DP-numeric family; optional but present in this infra.
try:
    import scipy.integrate as _spi
    _HAVE_SCIPY = True
except Exception:                                   # honest: say so, don't fake it
    _HAVE_SCIPY = False

# Default rigor knobs (committed; a result records the actual values it used).
DPS = 50            # mpmath working precision (decimal places)
DIGITS = 30         # agreement digit floor a result must clear
KPTS = 20           # sampled points for an identity over a domain


# --------------------------------------------------------------------------- #
#  agreement primitive
# --------------------------------------------------------------------------- #
def _agree(a, b, digits):
    """True iff mpmath values a,b agree to `digits` significant decimals.

    Relative test with an absolute floor so 0 vs ~0 is handled. Returns
    (ok: bool, achieved_digits: float)."""
    a = mp.mpf(a) if not isinstance(a, mp.mpf) else a
    b = mp.mpf(b) if not isinstance(b, mp.mpf) else b
    diff = abs(a - b)
    scale = max(abs(a), abs(b))
    # ABSOLUTE-TOLERANCE FLOOR for "both values are numerically zero".
    # A rearranged true identity (e.g. sin(x)**2 + cos(x)**2 - 1 == 0) leaves a
    # roundoff residue of order machine-epsilon (~1e-51 at dps=50) instead of an
    # exact 0.0. Then scale becomes that residue, rel = diff/scale collapses to ~1,
    # and the point is WRONGLY rejected (CRUCIBLE metamorphic KILL, 2026-06-20).
    # Fix: fire the absolute floor whenever the LARGER magnitude is itself at the
    # machine-noise level, not only when scale == 0 exactly. abs_floor is a few
    # billion * eps — astronomically above pure cancellation noise yet astronomically
    # BELOW any genuine value, so this swallows roundoff WITHOUT accepting any real
    # disagreement (a wrong closed form has scale O(1), never near abs_floor).
    abs_floor = mp.eps * mp.mpf(2) ** 32
    if scale <= abs_floor:
        ok = diff <= abs_floor
        return ok, (mp.inf if ok else mp.mpf(0))
    rel = diff / scale
    if rel == 0:
        return True, mp.inf
    achieved = -mp.log10(rel)
    return achieved >= digits, achieved


def _mpf_callable(expr, var):
    """sympy expr -> a Python callable using mpmath's own implementations.

    Independence: lambdify(..., 'mpmath') routes exp/log/gamma/etc to mpmath, so
    the numeric path does NOT reuse sympy's symbolic evaluation."""
    return sp.lambdify(var, expr, modules=['mpmath'])


# --------------------------------------------------------------------------- #
#  MODE: IDENTITY-PROVE  (symbolic simplify->0  AND  K-point numeric agreement)
# --------------------------------------------------------------------------- #
def verify_identity(lhs, rhs, syms, domain=(-1, 1), K=KPTS, digits=DIGITS,
                    dps=DPS, series_check=True, seed=20260620, avoid=()):
    """Certify lhs == rhs as functions over a real box `domain`.

    REQUIRED for a CERTIFIED verdict (both must fire):
      (1) numeric: lhs and rhs evaluated INDEPENDENTLY via mpmath at K random
          points across `domain` agree to `digits` digits at EVERY point;
      (2) symbolic: sympy.simplify(lhs-rhs) == 0  (=> 'symbolically proven' label)
          OR series-expansion of (lhs-rhs) is identically 0 (diversified 3rd
          method, methodologically != point-sampling).
    If numeric agrees everywhere but symbolic does NOT collapse, verdict is
    CERTIFIED with the weaker label "verified to D digits at K points".
    If numeric DISAGREES at any sampled point -> REJECTED (this is what catches a
    wrong-constant or domain-restricted claim). Points where lhs/rhs are undefined
    (or non-real) are skipped and counted, never silently passed.
    """
    syms = list(syms) if isinstance(syms, (list, tuple)) else [syms]
    lhs, rhs = sp.sympify(lhs), sp.sympify(rhs)
    mp.mp.dps = dps
    rng = random.Random(seed)

    f_l = _mpf_callable(lhs, syms)
    f_r = _mpf_callable(rhs, syms)
    lo, hi = domain
    pts_tested, worst = 0, mp.inf
    disagreements, skipped = [], 0
    while pts_tested < K and (pts_tested + skipped) < 40 * K:
        vals = [mp.mpf(rng.uniform(lo, hi)) for _ in syms]
        if any(abs(v - a) < mp.mpf('1e-6') for v in vals for a in avoid):
            skipped += 1
            continue
        try:
            vl, vr = f_l(*vals), f_r(*vals)
        except Exception:
            skipped += 1                            # both sides genuinely undefined here
            continue

        # A point is "real-defined" for a side iff that side is finite AND ~real.
        def _real_defined(v):
            try:
                rv, iv = mp.re(v), mp.im(v)
                return mp.isfinite(rv) and mp.isfinite(iv) and abs(iv) <= mp.mpf('1e-20')
            except Exception:
                return False
        l_ok, r_ok = _real_defined(vl), _real_defined(vr)
        if not l_ok and not r_ok:
            skipped += 1                            # neither side defined -> not in domain
            continue
        if l_ok != r_ok:
            # ONE side is real-defined and the OTHER is complex/non-finite IN-DOMAIN:
            # this is a real-function DISAGREEMENT (domain-restricted / branch-cut),
            # NOT a skip. Skipping here is the shared-blind-spot trap (audit 2026-06-20).
            pts_tested += 1
            disagreements.append({"point": [float(v) for v in vals],
                                  "lhs": mp.nstr(vl, 8), "rhs": mp.nstr(vr, 8),
                                  "agreed_digits": 0.0,
                                  "reason": "one side non-real/undefined where the other is real"})
            worst = mp.mpf(0)
            continue
        vl, vr = mp.mpf(mp.re(vl)), mp.mpf(mp.re(vr))
        ok, ach = _agree(vl, vr, digits)
        worst = min(worst, ach)
        pts_tested += 1
        if not ok:
            disagreements.append({"point": [float(v) for v in vals],
                                  "lhs": mp.nstr(vl, 12), "rhs": mp.nstr(vr, 12),
                                  "agreed_digits": float(ach)})
    numeric_ok = pts_tested >= max(3, K // 2) and not disagreements

    # symbolic collapse (the strong label) — guarded; simplify can hang/err.
    symbolic_zero = False
    try:
        symbolic_zero = sp.simplify(lhs - rhs) == 0
    except Exception:
        symbolic_zero = False
    # diversified 3rd method: series of the difference about an interior point.
    series_zero = None
    if series_check and len(syms) == 1:
        try:
            x0 = sp.Rational(1, 7)                  # generic interior point
            d = sp.series(lhs - rhs, syms[0], x0, 8).removeO()
            series_zero = sp.simplify(d) == 0
        except Exception:
            series_zero = None

    if not numeric_ok:
        verdict, label = "REJECTED", "numeric disagreement (not an identity on this domain)"
    elif symbolic_zero:
        verdict, label = "CERTIFIED", "symbolically proven (sympy.simplify->0; not kernel-grade)"
    elif series_zero:
        verdict = "CERTIFIED"
        label = f"verified to {digits} digits at {pts_tested} pts + series->0 (3rd method)"
    else:
        verdict = "CERTIFIED"
        label = f"verified to {digits} digits at {pts_tested} pts (numeric only — symbolic did NOT collapse)"

    return {
        "mode": "IDENTITY-PROVE", "verdict": verdict, "label": label,
        "lhs": str(lhs), "rhs": str(rhs), "domain": list(domain),
        "points_tested": pts_tested, "points_skipped": skipped,
        "worst_agreed_digits": (None if worst == mp.inf else float(worst)),
        "symbolic_simplify_zero": bool(symbolic_zero),
        "series_zero": series_zero,
        "disagreements": disagreements[:5],
        "methods": ["SYMBOLIC(simplify)", "NUMERIC-AP(mpmath@%d)" % dps]
                   + (["SERIES(3rd)"] if series_zero else []),
        "note": ("CERTIFIED by independent agreement; 'proven' label used ONLY on "
                 "an unconditional symbolic collapse (still not kernel-grade)."
                 if verdict == "CERTIFIED" else
                 "REJECTED: methods DISAGREE at >=1 sampled point — not an identity here."),
    }


# --------------------------------------------------------------------------- #
#  MODE: CLOSED-FORM  (definite integral: symbolic vs mpmath-quad vs scipy-quad)
# --------------------------------------------------------------------------- #
def verify_definite_integral(integrand, var, a, b, claimed, digits=DIGITS, dps=DPS):
    """Certify  integral_a^b integrand d(var) == claimed  by THREE independent paths:
      SYMBOLIC : sympy.integrate antiderivative, evaluated at the bounds;
      NUMERIC-AP: mpmath.quad (tanh-sinh, arbitrary precision) of the integrand;
      NUMERIC-DP: scipy QUADPACK (Gauss-Kronrod, double precision) — DIFFERENT
                  algorithm family => the diversified 3rd check.
    The certified value is the AGREEMENT of the numeric methods (and symbolic when
    sympy returns a closed antiderivative); `claimed` is checked against it.
    a,b may be sympy expressions incl. +-oo. REJECTS a wrong `claimed`."""
    var = sp.Symbol(str(var)) if not isinstance(var, sp.Symbol) else var
    integrand = sp.sympify(integrand)
    claimed = sp.sympify(claimed)
    a_s, b_s = sp.sympify(a), sp.sympify(b)
    mp.mp.dps = dps
    claimed_val = mp.mpf(sp.N(claimed, dps))

    f = _mpf_callable(integrand, var)
    a_m = (mp.inf if a_s == sp.oo else -mp.inf if a_s == -sp.oo else mp.mpf(sp.N(a_s, dps)))
    b_m = (mp.inf if b_s == sp.oo else -mp.inf if b_s == -sp.oo else mp.mpf(sp.N(b_s, dps)))

    methods, vals = [], {}
    # NUMERIC-AP (mpmath)
    try:
        v_mp = mp.quad(f, [a_m, b_m]); vals["NUMERIC-AP(mpmath)"] = v_mp
        methods.append("NUMERIC-AP(mpmath)")
    except Exception as e:
        vals["NUMERIC-AP(mpmath)"] = None; methods.append("NUMERIC-AP(mpmath):ERR:%s" % type(e).__name__)
    # NUMERIC-DP (scipy) — diversified family
    if _HAVE_SCIPY:
        try:
            fa = float(a_m) if mp.isfinite(a_m) else (math.inf if a_m > 0 else -math.inf)
            fb = float(b_m) if mp.isfinite(b_m) else (math.inf if b_m > 0 else -math.inf)
            fdp = sp.lambdify(var, integrand, 'numpy')
            v_sp, _err = _spi.quad(lambda t: float(fdp(t)), fa, fb, limit=200)
            vals["NUMERIC-DP(scipy)"] = mp.mpf(v_sp); methods.append("NUMERIC-DP(scipy)")
        except Exception as e:
            vals["NUMERIC-DP(scipy)"] = None; methods.append("NUMERIC-DP(scipy):ERR:%s" % type(e).__name__)
    # SYMBOLIC antiderivative (a claim until it agrees)
    sym_val, sym_closed = None, None
    try:
        F = sp.integrate(integrand, (var, a_s, b_s))
        if F.has(sp.Integral):                      # sympy failed to find closed form
            sym_closed = None
        else:
            sym_closed = sp.simplify(F)
            sym_val = mp.mpf(sp.N(sym_closed, dps))
            vals["SYMBOLIC(integrate)"] = sym_val; methods.append("SYMBOLIC(integrate)")
    except Exception:
        sym_closed = None

    # agreement: every successfully-computed method must agree with `claimed`, each
    # to a floor it can ACHIEVE. scipy QUADPACK is DOUBLE precision (~16 digits max),
    # so holding it to a 30-digit floor is dishonest — it gets a DP floor. mpmath /
    # symbolic are arbitrary-precision and keep the full floor. (A wrong value, e.g.
    # off by a factor, disagrees at digit ~0 and is caught by any floor.)
    DP_DIGITS = 12
    checks, worst = [], mp.inf
    for name, v in vals.items():
        if v is None:
            continue
        floor = DP_DIGITS if "scipy" in name or "DP" in name else digits
        ok, ach = _agree(v, claimed_val, floor)
        worst = min(worst, ach)
        checks.append({"method": name, "value": mp.nstr(v, 15), "digit_floor": floor,
                       "agrees_with_claimed": bool(ok), "digits": float(ach)})
    n_indep = sum(1 for c in checks)
    all_ok = n_indep >= 2 and all(c["agrees_with_claimed"] for c in checks)
    diversified = ("NUMERIC-AP(mpmath)" in vals and vals["NUMERIC-AP(mpmath)"] is not None and
                   _HAVE_SCIPY and vals.get("NUMERIC-DP(scipy)") is not None)

    if all_ok:
        verdict = "CERTIFIED"
        if sym_closed is not None and sp.simplify(sym_closed - claimed) == 0:
            label = "exact closed form (symbolic antiderivative == claimed; verified to %d digits by 2-3 numeric families)" % digits
        else:
            label = "verified to %d digits by %d independent methods%s" % (
                digits, n_indep, " incl. diversified DP/AP families" if diversified else "")
    else:
        verdict = "REJECTED"
        label = "methods disagree with claimed value -> NOT this closed form"

    return {
        "mode": "CLOSED-FORM", "verdict": verdict, "label": label,
        "integral": "integrate(%s, (%s, %s, %s))" % (integrand, var, a_s, b_s),
        "claimed": str(claimed), "claimed_value": mp.nstr(claimed_val, 20),
        "n_independent_methods": n_indep, "diversified_3rd_method": bool(diversified),
        "worst_agreed_digits": (None if worst == mp.inf else float(worst)),
        "symbolic_closed_form": (None if sym_closed is None else str(sym_closed)),
        "checks": checks, "methods": methods,
        "note": ("CERTIFIED: >=2 independent methods (incl. a diversified family) "
                 "agree with the claimed value." if verdict == "CERTIFIED" else
                 "REJECTED: at least one independent method disagrees with `claimed`."),
    }


# --------------------------------------------------------------------------- #
#  MODE: SPECIAL-VALUE / SERIES  (convergence FIRST, then closed form)
# --------------------------------------------------------------------------- #
def verify_convergence(term, n, lo=1):
    """Is sum_{n=lo}^oo term convergent? Two methods:
      SYMBOLIC : sympy Sum(...).is_convergent();
      NUMERIC  : partial sums S(N) for growing N — converging (Cauchy) vs growing.
    Returns convergent: True/False/None(unknown) with both signals."""
    n = sp.Symbol(str(n)) if not isinstance(n, sp.Symbol) else n
    term = sp.sympify(term)
    sym = None
    try:
        sym = bool(sp.Sum(term, (n, lo, sp.oo)).is_convergent())
    except Exception:
        sym = None
    # numeric: compare partial sums at N and 10N; bounded movement => convergent
    mp.mp.dps = 30
    f = _mpf_callable(term, n)
    def partial(N):
        return mp.fsum(f(k) for k in range(lo, N + 1))
    try:
        s1, s2, s3 = partial(2000), partial(20000), partial(200000)
        tail1, tail2 = abs(s2 - s1), abs(s3 - s2)
        # convergent ~ tail shrinks toward 0; divergent ~ tail stays large/grows
        num = (tail2 < tail1) and (tail2 < mp.mpf('1e-2') or tail2 < abs(s3) * mp.mpf('1e-3'))
    except Exception:
        num, s3, tail2 = None, None, None
    if sym is None and num is None:
        convergent = None
    elif sym is None:
        convergent = num
    elif num is None:
        convergent = sym
    else:
        convergent = sym and num                    # agree to claim convergence
    return {"convergent": convergent, "symbolic_is_convergent": sym,
            "numeric_partial_sum_converges": (None if num is None else bool(num)),
            "tail_estimate": (None if tail2 is None else mp.nstr(tail2, 6)),
            "note": ("CONVERGENT by symbolic test + numeric partial sums"
                     if convergent else
                     "NOT certified convergent — a closed form must NOT be issued"
                     if convergent is False else
                     "convergence UNKNOWN — abstain from a closed form")}


def verify_series_closed_form(term, n, claimed, lo=1, digits=DIGITS, dps=DPS):
    """Certify sum_{n=lo}^oo term == claimed. CONVERGENCE is checked FIRST; a
    non-convergent series is REJECTED no matter how nice `claimed` looks. Then the
    claimed value is checked against an INDEPENDENT high-precision partial sum with
    tail control, and against sympy's own summation when it returns a closed form."""
    conv = verify_convergence(term, n, lo)
    if conv["convergent"] is not True:
        return {"mode": "SERIES", "verdict": "REJECTED", "label":
                "non-convergent (or convergence unknown) -> NO closed form issued",
                "claimed": str(claimed), "convergence": conv,
                "note": "REJECTED before any value check: cannot assign a finite "
                        "closed form to a series not certified convergent."}
    n = sp.Symbol(str(n)) if not isinstance(n, sp.Symbol) else n
    term, claimed = sp.sympify(term), sp.sympify(claimed)
    mp.mp.dps = dps
    claimed_val = mp.mpf(sp.N(claimed, dps))
    f = _mpf_callable(term, n)
    # independent high-precision numeric: mpmath.nsum (Richardson/Euler-Maclaurin)
    try:
        num_val = mp.nsum(lambda k: f(k), [lo, mp.inf])
    except Exception:
        num_val = mp.fsum(f(k) for k in range(lo, 500001))
    ok_num, ach_num = _agree(num_val, claimed_val, digits)
    # symbolic summation (a 2nd, different engine path)
    sym_val, sym_ok, sym_closed = None, None, None
    try:
        S = sp.summation(term, (n, lo, sp.oo))
        if not S.has(sp.Sum):
            sym_closed = sp.simplify(S)
            sym_val = mp.mpf(sp.N(sym_closed, dps))
            sym_ok = _agree(sym_val, claimed_val, digits)[0]
    except Exception:
        sym_closed = None
    n_indep = 1 + (1 if sym_val is not None else 0)
    value_ok = ok_num and (sym_ok is None or sym_ok)
    # DOCTRINE (audit 2026-06-20, Defect 1): full CERTIFIED requires >=2 INDEPENDENT
    # methods to confirm the VALUE. mpmath.nsum + the convergence partial-sums are the
    # SAME (numeric-AP) family — a shared nsum bug would fool both. So when sympy
    # returns no closed form (n_indep==1), the verdict is the explicit, weaker
    # CERTIFIED-SINGLE-FAMILY — never the bare CERTIFIED the >=2 doctrine reserves.
    if not value_ok:
        verdict = "REJECTED"
        label = "claimed value disagrees with independent summation -> REJECTED"
    elif n_indep >= 2:
        verdict = "CERTIFIED"
        label = "verified to %d digits (mpmath.nsum + symbolic summation agree — 2 independent families)" % digits
    else:
        verdict = "CERTIFIED-SINGLE-FAMILY"
        label = ("verified to %d digits by ONE family (mpmath.nsum); sympy gave no closed "
                 "form so the >=2-method floor is NOT met — numeric-strong, NOT doctrine-CERTIFIED" % digits)
    return {"mode": "SERIES", "verdict": verdict, "label": label,
            "series": "Sum(%s, (%s, %d, oo))" % (term, n, lo),
            "claimed": str(claimed), "claimed_value": mp.nstr(claimed_val, 20),
            "numeric_value": mp.nstr(num_val, 20), "numeric_agrees": bool(ok_num),
            "numeric_digits": float(ach_num),
            "symbolic_closed_form": (None if sym_closed is None else str(sym_closed)),
            "symbolic_agrees": sym_ok, "n_independent_methods": n_indep,
            "convergence": conv,
            "methods": (["NUMERIC-AP(mpmath.nsum)"] +
                        (["SYMBOLIC(summation)"] if sym_val is not None else [])),
            "note": ("CERTIFIED by convergence + agreement of 2 independent families."
                     if verdict == "CERTIFIED" else
                     "CERTIFIED-SINGLE-FAMILY: convergent + numeric-strong, but sympy gave no "
                     "closed form so only ONE family confirms the value — does NOT meet the >=2 "
                     "floor; treat as numeric-strong, not doctrine-certified."
                     if verdict == "CERTIFIED-SINGLE-FAMILY" else
                     "REJECTED: independent summation disagrees with `claimed`.")}


def verify_special_value(expr, known_value, source, digits=DIGITS, dps=DPS):
    """Reproduce a KNOWN special value (labeled reproduction). `expr` is a symbolic
    expression (e.g. pi**2/6); `known_value` is the fetched reference (string/Rational/
    sympy). Cross-checks the symbolic expr's high-precision value against the fetched
    reference. This is a REPRODUCTION, never an original result."""
    expr = sp.sympify(expr)
    mp.mp.dps = dps
    ev = mp.mpf(sp.N(expr, dps))
    ref = mp.mpf(sp.N(sp.sympify(known_value), dps)) if not isinstance(known_value, str) \
        else mp.mpf(known_value)
    ok, ach = _agree(ev, ref, digits)
    return {"mode": "SPECIAL-VALUE", "verdict": "REPRODUCED" if ok else "MISMATCH",
            "label": "reproduction of a fetched known value (NOT an original result)",
            "expr": str(expr), "expr_value": mp.nstr(ev, 25),
            "reference_value": mp.nstr(ref, 25), "source": source,
            "agrees": bool(ok), "digits": float(ach),
            "note": ("REPRODUCED: symbolic value matches the fetched reference to "
                     "%d digits. Labeled reproduction." % digits if ok else
                     "MISMATCH with the fetched reference — do not ship.")}


# --------------------------------------------------------------------------- #
#  NON-WAIVABLE adversarial self-test (accept-correct / reject 3 ways)
# --------------------------------------------------------------------------- #
def _selftest():
    x = sp.Symbol('x', real=True)

    # (a) ACCEPT a known-correct identity: sin^2+cos^2 = 1 (symbolic should collapse)
    r = verify_identity(sp.sin(x)**2 + sp.cos(x)**2, sp.Integer(1), [x], domain=(-3, 3))
    assert r["verdict"] == "CERTIFIED" and r["symbolic_simplify_zero"], r
    assert "proven" in r["label"], r                # unconditional collapse -> strong label

    # (a2) ACCEPT a numeric-strong identity sympy may not fully auto-collapse but
    #      multi-point agreement certifies: a log identity on the POSITIVE domain.
    r2 = verify_identity(sp.log(x) + sp.log(x + 1), sp.log(x * (x + 1)), [x], domain=(sp.Rational(1,2), 5))
    assert r2["verdict"] == "CERTIFIED", r2

    # (b) REJECT a closed form off by a constant: claim integral_0^1 x dx = 1 (true 1/2)
    rb = verify_definite_integral(x, x, 0, 1, sp.Integer(1))
    assert rb["verdict"] == "REJECTED", rb
    rb_ok = verify_definite_integral(x, x, 0, 1, sp.Rational(1, 2))
    assert rb_ok["verdict"] == "CERTIFIED" and rb_ok["n_independent_methods"] >= 2, rb_ok

    # (b2) REJECT an identity off by a factor: 2x vs 3x (numeric must catch it)
    rbf = verify_identity(2 * x, 3 * x, [x], domain=(1, 4))
    assert rbf["verdict"] == "REJECTED" and rbf["disagreements"], rbf

    # (c) REJECT a domain-restricted form presented as global: sqrt(x^2) == x is
    #     FALSE for x<0 (truth is |x|). Sampling a symmetric domain must catch it.
    rc = verify_identity(sp.sqrt(x**2), x, [x], domain=(-3, 3))
    assert rc["verdict"] == "REJECTED" and rc["disagreements"], rc
    #     and it IS true if restricted to the positive sub-domain (label-with-domain)
    rc_pos = verify_identity(sp.sqrt(x**2), x, [x], domain=(sp.Rational(1, 10), 3))
    assert rc_pos["verdict"] == "CERTIFIED", rc_pos

    # (d) REJECT a non-convergent "sum" with a fake closed form: sum 1/n = 42 (diverges)
    n = sp.Symbol('n', positive=True, integer=True)
    rd = verify_series_closed_form(1 / n, n, sp.Integer(42), lo=1)
    assert rd["verdict"] == "REJECTED" and rd["convergence"]["convergent"] is not True, rd
    #     and a CONVERGENT series with the RIGHT closed form is certified (Basel)
    rd_ok = verify_series_closed_form(1 / n**2, n, sp.pi**2 / 6, lo=1)
    assert rd_ok["verdict"] == "CERTIFIED" and rd_ok["n_independent_methods"] >= 2, rd_ok
    #     ... and the WRONG closed form for a convergent series is rejected
    rd_bad = verify_series_closed_form(1 / n**2, n, sp.pi**2 / 5, lo=1)
    assert rd_bad["verdict"] == "REJECTED", rd_bad
    #     (d2) DOCTRINE: a convergent series sympy can't close -> verdict must be the
    #     explicit CERTIFIED-SINGLE-FAMILY, NOT bare CERTIFIED (audit Defect 1 fix).
    import mpmath as _mp
    _mp.mp.dps = 40
    sf = _mpf_callable(sp.sin(1 / n**2), [n])
    sval = _mp.nsum(lambda k: sf(k), [1, _mp.inf])
    rd_sf = verify_series_closed_form(sp.sin(1 / n**2), n, sp.nsimplify(0) + sp.Float(_mp.nstr(sval, 35), 35),
                                      lo=1, digits=20)
    assert rd_sf["verdict"] in ("CERTIFIED-SINGLE-FAMILY", "REJECTED"), rd_sf
    assert rd_sf["verdict"] != "CERTIFIED", "single-family must NOT claim bare CERTIFIED: %s" % rd_sf

    # (e) branch-cut shared-blind-spot guard: log(x^2) == 2*log(x) is FALSE on x<0.
    re = verify_identity(sp.log(x**2), 2 * sp.log(x), [x], domain=(-3, 3))
    assert re["verdict"] == "REJECTED", re

    # (f) METAMORPHIC REGRESSION (CRUCIBLE KILL fix, 2026-06-20): a TRUE identity
    #     rearranged to (A - B) == 0 leaves a ~1e-51 roundoff residue against an
    #     exact 0.0. The _agree absolute-tolerance floor must read that as agreement,
    #     so the rearrangement CERTIFIES exactly like its A == B twin (case (a)).
    #     Before the floor fix this meaning-preserving rewrite flipped the verdict
    #     CERTIFIED -> REJECTED (worst_agreed_digits collapsed to 0 on the 0-vs-residue
    #     points). This assertion fails if _agree ever reverts to a scale==0-only floor.
    rf = verify_identity(sp.sin(x)**2 + sp.cos(x)**2 - 1, sp.Integer(0), [x], domain=(-3, 3))
    assert rf["verdict"] == "CERTIFIED" and not rf["disagreements"], rf
    #     ... and the floor must NOT mask a genuinely-wrong rearrangement: the FALSE
    #     identity (2x - 3x) == 0 has scale O(1) everywhere on (1,4) -- nowhere near
    #     the floor -- so it must STILL REJECT. This confirms the fix narrows strictly
    #     to 0-vs-residue and never swallows a real disagreement-against-zero.
    rf_bad = verify_identity(2 * x - 3 * x, sp.Integer(0), [x], domain=(1, 4))
    assert rf_bad["verdict"] == "REJECTED" and rf_bad["disagreements"], rf_bad

    print("symbolica_gate selftest: PASS")
    print("  (a) ACCEPT correct identity (symbolic collapse -> 'proven' label)")
    print("  (a2) ACCEPT numeric-strong identity on its valid domain")
    print("  (b) REJECT integral off by a constant; ACCEPT the correct value")
    print("  (b2) REJECT identity off by a factor (numeric disagreement)")
    print("  (c) REJECT domain-restricted form sold as global; ACCEPT on sub-domain")
    print("  (d) REJECT non-convergent sum w/ fake closed form; ACCEPT Basel; REJECT wrong Basel")
    print("  (e) REJECT branch-cut identity log(x^2)=2log(x) off the positive reals")
    print("  (f) METAMORPHIC: rearranged (A-B)==0 true identity CERTIFIES (0-vs-residue floor); false (2x-3x)==0 still REJECTS")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: symbolica_gate.py selftest")
