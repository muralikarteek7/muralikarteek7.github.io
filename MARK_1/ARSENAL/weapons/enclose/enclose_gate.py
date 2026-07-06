#!/usr/bin/env python3
"""ENCLOSE — the certified-numerics weapon: a CONTAINMENT-PROOF verifier.

Sibling of SYMBOLICA, but categorically sharper. SYMBOLICA certifies via multi-method
*agreement* (corroboration — a shared blind spot can fool every method). ENCLOSE returns a
guaranteed enclosure [a,b] **provably containing** the true value, verified by a containment
PROOF built on interval arithmetic with outward (directed) rounding (Moore's inclusion property)
and the Krawczyk existence-uniqueness test. Agreement is evidence; containment is proof.

THE GATE NEVER TRUSTS THE CLAIMED ANSWER. Given a `problem` (how to INDEPENDENTLY recompute a
rigorous enclosure) and a `claim` (the asserted box / uniqueness), the gate recomputes its own
guaranteed enclosure E and adjudicates the claim against E:
  * claim ⊇ E              -> ACCEPT  (true value ∈ E ⊆ claim, so the claim holds; possibly loose)
  * claim ∩ E = ∅          -> REJECT  (true value ∈ E is provably OUTSIDE the claimed box)
  * claim overlaps but ⊉ E -> ABSTAIN (claim is tighter than independently provable — NOT certified)

THE HONEST CEILING (do not skip):
  * κ=1 holds for the COMPUTED quantity under correct directed rounding ONLY. mpmath.iv does its
    rounding in SOFTWARE (arbitrary precision), so the C/hardware "-ffast-math degrades κ" caveat
    does NOT apply here — but the proof is only as sound as mpmath.iv's rounding implementation
    (trusted, widely used, NOT formally verified). That residual is named, not hidden.
  * κ=0 MODELING BOUNDARY: ENCLOSE certifies the integral of THIS integrand over THIS domain / the
    root of THIS f in THIS box. It does NOT certify that the integrand/f models the user's real
    problem. The modeling step is κ=0 and out of scope.
  * Surface is MODERATE, not broad: verified definite integrals of iv-evaluable integrands,
    Krawczyk root existence-uniqueness in a box, and containment of a recomputable constant/expr.
  * A containment proof is a PROOF of containment, not a claim the answer is "interesting".
"""
import math
import mpmath
from mpmath import iv, mpf, mp

ACCEPT = "ACCEPT"
REJECT = "REJECT"
ABSTAIN = "ABSTAIN"


def _set_prec(dps):
    mp.dps = dps
    iv.dps = dps


# --------------------------------------------------------------------------- #
#  Rigorous primitives (every one is a GUARANTEED enclosure, outward-rounded). #
# --------------------------------------------------------------------------- #
def verified_integral(f, a, b, N):
    """Rigorous OUTER enclosure of ∫_a^b f(x) dx via the interval rectangle rule.

    On each subinterval the NATURAL INTERVAL EXTENSION f(X) is a guaranteed outer bound of the
    true range of f over X (Moore's inclusion property), so h·Σ f(X_i) CONTAINS the true integral.
    Loose (width O(h)) but RIGOROUS. f must be an iv-arithmetic callable. Returns an iv.mpf."""
    a = iv.mpf(a)
    b = iv.mpf(b)
    h = (b - a) / N
    total = iv.mpf(0)
    for i in range(N):
        xi = a + h * i
        xj = a + h * (i + 1)
        X = iv.mpf([xi.a, xj.b])          # the whole subinterval as one interval
        total += h * f(X)
    return total


def krawczyk_operator(f, df, lo, hi):
    """The Krawczyk operator K(X). If K(X) ⊆ int(X) then f has a UNIQUE root in X
    (Krawczyk 1969; Neumaier). Returns (K, X) as iv.mpf, or (None, X) if f'(X) ∋ 0
    (the preconditioner C=1/f'(m) cannot be formed -> test inapplicable)."""
    X = iv.mpf([lo, hi])
    m = (X.a + X.b) / 2
    M = iv.mpf(m)
    fpm = df(M)
    if 0 in fpm:
        return None, X
    C = iv.mpf(1) / fpm
    K = M - C * f(M) + (iv.mpf(1) - C * df(X)) * (X - M)
    return K, X


def _contains(outer, inner):
    """True iff interval `inner` ⊆ interval `outer` (both iv.mpf)."""
    return (outer.a <= inner.a) and (inner.b <= outer.b)


def _disjoint(p, q):
    """True iff intervals p and q (iv.mpf) do not overlap."""
    return (p.b < q.a) or (q.b < p.a)


def _outward_report(E):
    """Human-readable [lo,hi] of an iv.mpf E, OUTWARD-rounded (lo toward -inf, hi toward +inf) so
    the printed decimals are a GUARANTEED SUPERSET of E. Rounding endpoints to nearest could print
    an interval narrower than the truth (e.g. √2's lower endpoint rounds UP past √2) — that would
    silently break the containment guarantee in the report. We nudge each endpoint outward by a
    SCALE-RELATIVE amount that dominates the 17-significant-digit print granularity, then print, so
    the report is a guaranteed superset AND stays tight at every magnitude (incl. near zero)."""
    lo = mpf(E.a)
    hi = mpf(E.b)
    scale = max(abs(lo), abs(hi), mpf(10) ** (-308))   # interval's own magnitude (floor for E≈0)
    pad = scale * mpf(10) ** (-15)                       # > |endpoint|*1e-17 print granularity
    return (mpmath.nstr(lo - pad, 17), mpmath.nstr(hi + pad, 17))


def _result(verdict, reason, **extra):
    # kappa reflects VERDICT DETERMINACY, not claim confidence: ACCEPT proves containment, REJECT
    # proves disjointness (both κ=1 determinations); ABSTAIN is UNDETERMINED (the gate makes no κ=1
    # statement about the claim) -> κ=0, so a downstream consumer can't misread it as proof.
    d = {"weapon": "ENCLOSE", "verdict": verdict,
         "kappa": 1 if verdict in (ACCEPT, REJECT) else 0, "reason": reason}
    d.update(extra)
    return d


# --------------------------------------------------------------------------- #
#  THE GATE — recompute independently, then adjudicate the claim against it.   #
# --------------------------------------------------------------------------- #
def gate(problem, claim, *, dps=30):
    """Verify a numeric ENCLOSURE / root-uniqueness certificate.

    problem: dict with 'kind' in {'enclosure','integral','root_unique'} describing how to
             INDEPENDENTLY recompute a rigorous enclosure (the gate never reads the claimed answer
             to build E).
    claim:   the asserted result. For 'enclosure'/'integral': {'lo':..,'hi':..}. For 'root_unique':
             {'lo':..,'hi':..,'unique':True} — the cert ASSERTS f has a unique root in [lo,hi].
    Returns {verdict, reason, ...}. A recompute crash / malformed input -> ABSTAIN (loud, never a
    silent ACCEPT)."""
    try:
        _set_prec(dps)
        kind = problem.get("kind")

        # ---- containment kinds: recompute E, adjudicate the claimed box against it ----
        if kind in ("enclosure", "integral"):
            if kind == "enclosure":
                # NOTE (κ=0 caller boundary): the gate certifies CONTAINMENT of whatever rigorous
                # enclosure value() returns; it cannot verify value() is itself rigorous. A caller
                # that returns a non-rigorous (too-narrow) interval is the modeling-step risk named
                # in the SPEC — not a gate soundness bug. value() MUST be built from iv operations.
                E = problem["value"]()          # 0-arg callable -> iv.mpf enclosure of Q
            else:
                f = problem["f"]
                # GUARD (audit #2): the inclusion property holds only if f is evaluated in INTERVAL
                # arithmetic. A footgun integrand (math.exp instead of iv.exp, float(x.a), ...) would
                # silently break it. Probe f on an interval input; if it does not return an iv.mpf,
                # ABSTAIN loudly rather than build an unsound E.
                probe = f(iv.mpf([problem["a"], problem["b"]]))
                if not isinstance(probe, iv.mpf):
                    return _result(ABSTAIN,
                                   "integrand did not return an mpmath.iv interval on an interval "
                                   "input -> the inclusion property is not guaranteed; the integrand "
                                   "must be composed of mpmath.iv operations (e.g. iv.exp, not math.exp)")
                E = verified_integral(f, problem["a"], problem["b"], problem.get("N", 1000))
            if not isinstance(E, iv.mpf):
                return _result(ABSTAIN, "recompute did not return an interval enclosure")
            if "lo" not in claim or "hi" not in claim:
                return _result(ABSTAIN, "claim missing lo/hi bounds")
            try:
                lo, hi = mpf(str(claim["lo"])), mpf(str(claim["hi"]))
            except Exception:
                return _result(ABSTAIN, "claimed bounds are not parseable numbers")
            if not (math.isfinite(float(lo)) and math.isfinite(float(hi))):
                return _result(ABSTAIN, "claimed bounds are non-finite (NaN/inf)")
            if lo > hi:
                return _result(ABSTAIN, "claimed bounds malformed (lo > hi)")
            claimI = iv.mpf([lo, hi])
            E_str = _outward_report(E)
            if _disjoint(claimI, E):
                return _result(REJECT,
                               "claimed box is DISJOINT from the rigorous enclosure E -> the true "
                               "value (∈ E) is provably OUTSIDE the claim (false enclosure)",
                               rigorous_enclosure=E_str)
            if _contains(claimI, E):
                return _result(ACCEPT,
                               "rigorous enclosure E ⊆ claimed box -> true value ∈ claim, certified "
                               "by containment proof (outward-rounded interval arithmetic)",
                               rigorous_enclosure=E_str)
            return _result(ABSTAIN,
                           "claimed box overlaps E but does NOT contain it -> the claim is tighter "
                           "than independently provable; NOT certified (would need higher precision "
                           "or a sharper method)",
                           rigorous_enclosure=E_str)

        # ---- Krawczyk existence-uniqueness ----
        if kind == "root_unique":
            if "lo" not in claim or "hi" not in claim:
                return _result(ABSTAIN, "claim missing root-box bounds")
            try:
                lo, hi = mpf(str(claim["lo"])), mpf(str(claim["hi"]))
            except Exception:
                return _result(ABSTAIN, "root-box bounds are not parseable numbers")
            if not (math.isfinite(float(lo)) and math.isfinite(float(hi))) or lo >= hi:
                return _result(ABSTAIN, "root-box bounds malformed (non-finite or lo >= hi)")
            K, X = krawczyk_operator(problem["f"], problem["df"], lo, hi)
            if K is None:
                return _result(ABSTAIN,
                               "f'(X) contains 0 on the box -> Krawczyk preconditioner cannot be "
                               "formed; existence-uniqueness not decidable here (loud abstain)")
            unique = (X.a < K.a) and (K.b < X.b)     # K strictly inside X
            K_str = _outward_report(K)
            if unique:
                return _result(ACCEPT,
                               "Krawczyk K(X) ⊂ int(X) -> f has a UNIQUE root in the box "
                               "(existence AND uniqueness proven)", krawczyk_image=K_str)
            return _result(REJECT,
                           "Krawczyk test fails (K(X) ⊄ int(X)) -> the asserted unique root is NOT "
                           "proven for this box (uncertified; not a proof of no-root)",
                           krawczyk_image=K_str)

        return _result(ABSTAIN, f"unknown problem kind {kind!r}")
    except Exception as e:                            # a crash is a loud abstain, never a silent pass
        return _result(ABSTAIN, f"recompute raised {type(e).__name__}: {e}")


if __name__ == "__main__":
    # smoke: verified ∫_0^1 4/(1+x^2) = π in a correct box; reject a fabricated box
    _set_prec(30)
    p = {"kind": "integral", "f": lambda x: 4 / (1 + x * x), "a": 0, "b": 1, "N": 2000}
    print("true box   :", gate(p, {"lo": "3.14", "hi": "3.15"})["verdict"])      # ACCEPT
    print("false box  :", gate(p, {"lo": "3.0", "hi": "3.1"})["verdict"])        # REJECT
    print("too-tight  :", gate(p, {"lo": "3.1415", "hi": "3.1416"})["verdict"])  # ABSTAIN (E wider than claim)
