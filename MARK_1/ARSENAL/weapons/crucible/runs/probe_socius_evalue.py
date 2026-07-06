#!/usr/bin/env python3
"""CRUCIBLE probe of socius_evalue — the E-value arithmetic slice + the multiverse
spec-reordering metamorphic leg.

TARGET (black-box, real gates):
  socius/eval_verify.py       — the E-value (VanderWeele & Ding 2017) computation.
    The E-value NUMBER is exact (kappa=1) per the gate's own docstring; the verdict
    `robust_to_confounding = governing_E >= benchmark` is exact arithmetic GIVEN a
    declared benchmark (the benchmark VALUE is kappa=0 judgment and is NOT probed —
    we hold it fixed and probe only the arithmetic that turns a reported estimate
    into the governing E-value and compares it to the held-fixed benchmark).
  socius/multiverse_verify.py — the FROZEN kappa=1 spec-curve verdict logic
    `summarize_speccurve`. Per the pre-committed scope there is NO exact oracle for
    the multiverse verdict, so that leg is METAMORPHIC-ONLY (spec-reordering
    invariance; transform meaning-preservation is CALLER-ASSERTED — residual risk).

COVERAGE: PARTIAL.
  * E-value arithmetic: LIMITED DIFFERENTIAL. The oracle is a genuinely FOREIGN
    re-derivation of the E-value — numeric BISECTION on the bias-factor function
    BF(E) = E^2/(2E-1) solved against the observed RR — versus the gate's algebraic
    closed form  E = RR + sqrt(RR*(RR-1)). Foreign scale conversions are re-derived
    from first principles, NOT copied from the gate. Plus metamorphic (inversion +
    OR-reparam, both oracle-validated).
  * Multiverse: METAMORPHIC-ONLY (spec reordering). Stated as such; no differential.

We import and CALL the real gate functions (no reimplementation of the gate logic).
"""
import os
import sys
import json
import math
import itertools

HERE = os.path.dirname(os.path.abspath(__file__))
CRUCIBLE = os.path.dirname(HERE)
ARSENAL = os.path.dirname(CRUCIBLE)
SOCIUS = os.path.join(ARSENAL, "socius")

for p in (CRUCIBLE, SOCIUS):
    if p not in sys.path:
        sys.path.insert(0, p)

import crucible_harness as CH
from crucible_harness import (
    GateAdapter, Oracle, ACCEPT, REJECT, ABSTAIN, ERROR, CORRECT, WRONG,
    false_accept_hunt, false_reject_hunt, metamorphic_hunt, abstain_crash_hunt,
)

# ---- import the REAL socius weapon gates (no reimplementation) ----------------
import eval_verify as EV               # the S-CAUSAL E-value gate
import multiverse_verify as MV         # the S-MULTIVERSE spec-curve gate

# sanity: confirm the callables we wrap are the genuine gate objects
_REAL_ASSESS = EV.assess_sensitivity
_REAL_SPECCURVE = MV.summarize_speccurve
assert _REAL_ASSESS is EV.assess_sensitivity
assert _REAL_SPECCURVE is MV.summarize_speccurve


# =========================================================================== #
#  FOREIGN ORACLE for the E-value arithmetic.
#  truth() recomputes the governing E-value by a DIFFERENT mechanism than the
#  gate (bisection on the bias-factor function, not the gate's closed form), then
#  applies the SAME documented decision rule (governing_E >= benchmark, with the
#  null-crossing-CI collapse rule) and compares to the gate's robust verdict.
#  CORRECT iff gate.robust == foreign.robust; WRONG iff they disagree; None if
#  the foreign engine cannot decide (out of domain).
# =========================================================================== #
def _foreign_e_value(rr):
    """E-value for a risk ratio rr by FOREIGN bisection on BF(E)=E^2/(2E-1).

    VanderWeele-Ding: the bias factor an unmeasured confounder must reach to
    explain away an observed RR is RR itself; the E-value is the confounding
    strength E producing that bias factor, BF(E)=E^2/(2E-1). For rr<1 we invert
    first (the E-value is symmetric under rr->1/rr). This is a NUMERIC root-find,
    methodologically foreign to the gate's algebraic  rr + sqrt(rr*(rr-1)).
    """
    if rr <= 0:
        raise ValueError("risk ratio must be > 0")
    if rr < 1:
        rr = 1.0 / rr
    if rr == 1.0:
        return 1.0
    # BF(E)=E^2/(2E-1) is strictly increasing for E>=1, BF(1)=1, BF->inf.
    lo, hi = 1.0, 2.0
    while (hi * hi / (2 * hi - 1)) < rr:
        hi *= 2.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if (mid * mid / (2 * mid - 1)) < rr:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _foreign_to_rr(estimate, scale):
    """Convert a reported effect to the risk-ratio scale, re-derived from first
    principles (the published VanderWeele-Ding / VanderWeele 2017 conversions).
    Written independently of the gate's to_risk_ratio (same target formulas — they
    ARE the published conversions — but this is the substantive thing the oracle
    must agree on; the genuinely-foreign part is the E-value root-find above)."""
    s = str(scale).lower()
    if s in ("rr", "risk_ratio", "riskratio"):
        return float(estimate)
    if s in ("or", "odds_ratio", "oddsratio"):
        e = float(estimate)
        # RR ~= sqrt(OR), applied on whichever side of 1 the OR sits.
        if e >= 1:
            return math.sqrt(e)
        return 1.0 / math.sqrt(1.0 / e)
    if s in ("hr", "hazard_ratio", "hazardratio"):
        hr = float(estimate)
        return (1 - 0.5 ** math.sqrt(hr)) / (1 - 0.5 ** math.sqrt(1.0 / hr))
    if s in ("d", "smd", "cohen_d", "std_mean_diff"):
        return math.exp(0.91 * float(estimate))
    raise ValueError(f"unknown effect scale: {scale}")


def _foreign_robust(estimate, scale="RR", ci_limit=None, benchmark_confounding=2.0):
    """The foreign re-derivation of the gate's robust verdict.

    governing E = CI-limit E if a CI limit is given, else point E. If the CI limit
    sits on the opposite side of the null from the point estimate (the interval
    crosses 1) the governing E collapses to 1 (already null-compatible). robust iff
    governing >= benchmark. Returns (governing_e, robust_bool)."""
    rr = _foreign_to_rr(estimate, scale)
    ev_point = _foreign_e_value(rr)
    governing = ev_point
    if ci_limit is not None:
        rr_ci = _foreign_to_rr(ci_limit, scale)
        if (rr >= 1 and rr_ci <= 1) or (rr < 1 and rr_ci >= 1):
            governing = 1.0
        else:
            governing = _foreign_e_value(rr_ci)
    return governing, (governing >= benchmark_confounding)


_BENCHMARK = 2.0   # held FIXED (kappa=0 value NOT probed); the gate's default.


def oracle_truth(obj):
    """The object's INDEPENDENT TRUE verdict, computed entirely by the FOREIGN
    engine (NOT by reading the gate's output — that would be circular).

      CORRECT  -> the object is TRULY robust-to-confounding: the foreign governing
                  E-value is >= the held-fixed benchmark. The true verdict is ACCEPT.
      WRONG    -> the object is TRULY NOT robust: foreign governing E < benchmark.
                  The true verdict is REJECT.
      None     -> the foreign engine is out of domain (non-finite, rr<=0, unknown
                  scale, or a regime where the >=/< decision is numerically ill-posed
                  within a small relative tolerance) -> no opinion, never guess.

    This is the CORRECT differential framing: false_accept = gate ACCEPT (robust)
    on a WRONG object (truly not robust); false_reject = gate REJECT (not robust)
    on a CORRECT object (truly robust). The earlier 'does the gate's number match'
    framing was a probe bug (it conflated 'gate computed correctly' with 'object
    deserves ACCEPT')."""
    # the oracle uses only its own arguments; an unfixed benchmark would change the
    # truth, so we require the live obj to use the same fixed benchmark (or default).
    bm = obj.get("benchmark_confounding", _BENCHMARK)
    if bm != _BENCHMARK:
        return None
    try:
        gov, _rob = _foreign_robust(estimate=obj["estimate"], scale=obj["scale"],
                                    ci_limit=obj.get("ci_limit"),
                                    benchmark_confounding=_BENCHMARK)
    except Exception:
        return None
    if not math.isfinite(gov):
        return None
    # Refuse to opine in a numerically-ambiguous band right at the threshold, so a
    # last-ULP rounding difference between the two engines can never manufacture a
    # spurious kill. A REAL gate bug shows as a verdict that differs OUTSIDE this band.
    if abs(gov - _BENCHMARK) <= 1e-9 * max(1.0, abs(_BENCHMARK)):
        return None
    return CORRECT if gov >= _BENCHMARK else WRONG


# Control grid spanning the probed regime: RR/OR/HR/SMD scales, CI handling, rr<1
# inversion, boundary near the benchmark, null-crossing CI. Polarity is the OBJECT'S
# TRUE verdict (independently hand-derived); the harness re-runs is_sane() over them.
#   GOOD  = truly robust  (foreign governing E >= 2.0) -> oracle MUST say CORRECT
#   BAD   = truly NOT robust (foreign governing E < 2.0) -> oracle MUST say WRONG
controls_good = [
    {"estimate": 3.9, "scale": "RR"},                   # E=7.26 >= 2  -> robust
    {"estimate": 10.0, "scale": "RR"},                  # E=19.5 >= 2  -> robust
    {"estimate": 0.5, "scale": "RR"},                   # inversion E(2)=3.41 -> robust
    {"estimate": 4.0, "scale": "OR"},                   # OR4->RR2->E=3.41 -> robust
    {"estimate": 2.0, "scale": "HR"},                   # HR2 (common-outcome) -> robust
    {"estimate": 1.5, "scale": "SMD"},                  # d1.5->RR~3.9->E large -> robust
]
controls_bad = [
    {"estimate": 1.05, "scale": "RR"},                  # E=1.28 < 2  -> NOT robust
    {"estimate": 1.20, "scale": "RR"},                  # E=1.69 < 2  -> NOT robust
    {"estimate": 1.5, "scale": "OR"},                   # OR1.5->RR1.22->E=1.74 -> NOT robust
    {"estimate": 0.85, "scale": "RR"},                  # inversion RR1.18->E=1.66 -> NOT robust
    {"estimate": 0.3, "scale": "SMD"},                  # d0.3->RR1.31->E=1.94 < 2 -> NOT robust
    {"estimate": 1.8, "scale": "RR", "ci_limit": 0.95}, # CI crosses null -> gov=1 < 2 -> NOT robust
]

oracle = Oracle(
    "Evalue-biasfactor-foreign", oracle_truth, is_independent=True,
    method="independent TRUE robust-verdict from a FOREIGN E-value re-derivation by "
           "BISECTION on the bias-factor function BF(E)=E^2/(2E-1) (vs the gate's "
           "algebraic closed form rr+sqrt(rr*(rr-1))); governing E compared to a "
           "held-fixed benchmark=2.0. CORRECT=truly-robust, WRONG=truly-not-robust",
    controls_good=controls_good, controls_bad=controls_bad,
)


# =========================================================================== #
#  GATE ADAPTER for the E-value verdict (the robust_to_confounding decision under
#  a held-fixed benchmark). ACCEPT = gate says robust; REJECT = gate says not
#  robust; a raise -> ERROR (abstain/crash mode).
# =========================================================================== #
def evalue_gate_fn(**obj):
    return _REAL_ASSESS(**obj)


def evalue_to_verdict(raw):
    return ACCEPT if bool(raw["robust_to_confounding"]) else REJECT


eval_gate = GateAdapter("socius_evalue", evalue_gate_fn, evalue_to_verdict)


# =========================================================================== #
#  CANDIDATE STREAM for the E-value differential. Spans:
#   * scales RR / OR / HR / SMD (each estimate read on every scale)
#   * estimates straddling the benchmark=2.0 boundary (so robust flips)
#   * rr<1 (inversion path) and rr>1
#   * CI limits: none, null-crossing, and away-from-null
#  Benchmark held fixed at the gate default 2.0 (kappa=0 value NOT probed).
# =========================================================================== #
def candidates():
    out, seen = [], set()

    def emit(obj):
        key = tuple(sorted((k, str(v)) for k, v in obj.items()))
        if key not in seen:
            seen.add(key)
            out.append(obj)

    # a dense grid of reported estimates around the regions where robust flips
    ests = ([round(1.0 + i * 0.01, 2) for i in range(0, 400)]      # 1.00..4.99 fine
            + [round(0.05 + i * 0.05, 2) for i in range(0, 40)]    # 0.05..1.99 (rr<1 path)
            + [5.0, 7.0, 9.0, 12.0, 20.0, 50.0, 100.0,
               0.5, 0.25, 0.1, 0.02, 0.9, 1.4142135623730951, 3.4142135623730951])
    for scale in ("RR", "OR", "HR", "SMD"):
        for est in ests:
            emit({"estimate": est, "scale": scale})
    # CI-limit objects on the RR scale: away-from-null and null-crossing
    for est in (1.5, 1.8, 2.0, 2.5, 3.9, 0.6, 0.4):
        for ci in (1.05, 1.2, 1.5, 0.95, 0.8, 1.0):
            emit({"estimate": est, "scale": "RR", "ci_limit": ci})
    return out


COVERAGE = ("E-value DIFFERENTIAL slice: scales RR/OR/HR/SMD; reported estimates "
            "in [0.02, 100] dense around the benchmark=2.0 flip region and the rr<1 "
            "inversion path; CI limits null-crossing + away-from-null; benchmark held "
            "FIXED at 2.0 (kappa=0 value NOT probed). NOT probed: benchmark != 2.0, "
            "scales outside {RR,OR,HR,SMD}, estimates > 100, CI on non-RR scales.")


# =========================================================================== #
#  METAMORPHIC transforms for the E-value (oracle-validated where the oracle has
#  an opinion). Both preserve the governing E-value, hence the robust verdict:
#   T1 inversion:  RR=r  <->  RR=1/r    (E-value symmetric under inversion)
#   T2 OR-reparam: RR=r (scale RR)  <->  OR=r^2 (scale OR)  (to_risk_ratio maps
#                  OR->sqrt(OR)=r, so the governing RR — hence E — is identical).
# =========================================================================== #
def t_inversion(obj):
    if obj.get("ci_limit") is not None:
        raise ValueError("inversion transform only on point-only objects")
    sc = str(obj["scale"]).lower()
    if sc not in ("rr", "risk_ratio", "riskratio"):
        raise ValueError("inversion transform defined on RR scale only")
    return {"estimate": 1.0 / float(obj["estimate"]), "scale": obj["scale"]}


def t_or_reparam(obj):
    if obj.get("ci_limit") is not None:
        raise ValueError("OR-reparam only on point-only objects")
    sc = str(obj["scale"]).lower()
    if sc not in ("rr", "risk_ratio", "riskratio"):
        raise ValueError("OR-reparam defined on an RR-scale seed only")
    return {"estimate": float(obj["estimate"]) ** 2, "scale": "OR"}


def malformed_inputs():
    safe = {ABSTAIN, REJECT, ERROR}
    return [
        ("estimate=0 (rr<=0)",       {"estimate": 0.0, "scale": "RR"}, safe),
        ("estimate=-1 (negative)",   {"estimate": -1.0, "scale": "RR"}, safe),
        ("unknown scale 'xyz'",      {"estimate": 2.0, "scale": "xyz"}, safe),
        ("estimate NaN",             {"estimate": float("nan"), "scale": "RR"}, safe),
        ("estimate +inf",            {"estimate": float("inf"), "scale": "RR"}, safe),
        ("OR estimate=0",            {"estimate": 0.0, "scale": "OR"}, safe),
        ("HR estimate=0",            {"estimate": 0.0, "scale": "HR"}, safe),
    ]


# =========================================================================== #
#  MULTIVERSE leg — metamorphic-only (spec reordering). NO exact oracle (per the
#  pre-committed scope). summarize_speccurve(pvals, coefs, ...) aggregates over
#  the spec set; the aggregates (mean significant share, sign stability, median)
#  are permutation-invariant, so a JOINT reordering of (pvals, coefs) must NOT
#  change the robust verdict. Transform meaning-preservation is CALLER-ASSERTED
#  (a permutation provably preserves the multiset) — stated as residual risk.
# =========================================================================== #
def mv_gate_fn(**obj):
    return _REAL_SPECCURVE(**obj)


def mv_to_verdict(raw):
    return ACCEPT if bool(raw["robust"]) else REJECT


mv_gate = GateAdapter("socius_multiverse", mv_gate_fn, mv_to_verdict)


def _mv_seeds():
    """Realised spec curves spanning robust and fragile verdicts (the gate must be
    stable under reordering on BOTH). Each seed is a (pvals, coefs) pair."""
    import random
    seeds = []
    rng = random.Random(7)
    # robust-leaning: most specs significant, same sign
    for _ in range(6):
        nsp = rng.randint(8, 40)
        pv = [rng.uniform(0, 0.04) for _ in range(nsp)]
        cf = [rng.uniform(0.2, 1.5) for _ in range(nsp)]
        seeds.append({"pvals": pv, "coefs": cf, "hyp_sign": 1})
    # fragile-leaning: few significant, mixed sign
    for _ in range(6):
        nsp = rng.randint(8, 40)
        pv = [rng.uniform(0.0, 0.9) for _ in range(nsp)]
        cf = [rng.uniform(-1.0, 1.0) for _ in range(nsp)]
        seeds.append({"pvals": pv, "coefs": cf, "hyp_sign": 1})
    # boundary: exactly around the 0.5 significant-share threshold
    for half in (0.45, 0.5, 0.55):
        nsp = 40
        nsig = int(round(half * nsp))
        pv = [0.01] * nsig + [0.2] * (nsp - nsig)
        cf = [0.8] * nsp
        seeds.append({"pvals": pv, "coefs": cf, "hyp_sign": 1})
    return seeds


def _mv_reorder_transforms():
    """JOINT permutations of (pvals, coefs) — provably multiset-preserving, hence
    verdict-preserving for any permutation-invariant aggregate rule."""
    import random

    def make_perm(seed):
        def T(obj):
            pv = list(obj["pvals"]); cf = list(obj["coefs"])
            idx = list(range(len(pv)))
            random.Random(seed).shuffle(idx)
            return {**obj,
                    "pvals": [pv[i] for i in idx],
                    "coefs": [cf[i] for i in idx]}
        return T

    def reverse(obj):
        return {**obj, "pvals": list(reversed(obj["pvals"])),
                "coefs": list(reversed(obj["coefs"]))}

    return [("reverse-order", reverse),
            ("shuffle-seed-1", make_perm(1)),
            ("shuffle-seed-2", make_perm(2)),
            ("shuffle-seed-99", make_perm(99))]


def main():
    print("=" * 78)
    print("CRUCIBLE probe: socius_evalue (E-value arithmetic slice + multiverse leg)")
    print("real gate entrypoints:",
          f"eval_verify.assess_sensitivity (is real: {evalue_gate_fn.__doc__ is None and True or (_REAL_ASSESS is EV.assess_sensitivity)})",
          "| multiverse_verify.summarize_speccurve (is real:",
          _REAL_SPECCURVE is MV.summarize_speccurve, ")")
    print("oracle:", oracle.method)
    print("=" * 78)

    sane, detail = oracle.is_sane()
    print("ORACLE SANITY:", sane, "--", detail)
    if not sane:
        print("ABORT: oracle not sane; no hunt can ship a KILL.")
        return

    cands = candidates()
    print(f"E-value candidate stream size: {len(cands)}")
    print("-" * 78)

    # ---- (1) FALSE-ACCEPT (gate says robust, foreign arithmetic says not) ----
    fa = false_accept_hunt(eval_gate, oracle, cands, max_probes=200000, coverage_note=COVERAGE)
    print("E-VALUE FALSE-ACCEPT:")
    print(json.dumps(fa.to_dict(), indent=2, default=str))
    print("-" * 78)

    # ---- (2) FALSE-REJECT (gate says not robust, foreign arithmetic says robust) ----
    fr = false_reject_hunt(eval_gate, oracle, cands, max_probes=200000, coverage_note=COVERAGE)
    print("E-VALUE FALSE-REJECT:")
    print(json.dumps(fr.to_dict(), indent=2, default=str))
    print("-" * 78)

    # ---- (3) METAMORPHIC (inversion + OR-reparam, oracle-validated) ----
    point_only = [c for c in cands if c.get("ci_limit") is None
                  and str(c["scale"]).lower() in ("rr", "risk_ratio", "riskratio")]
    mm = metamorphic_hunt(eval_gate, point_only,
                          [("inversion (E-value symmetric)", t_inversion),
                           ("OR-reparam (RR=r <-> OR=r^2)", t_or_reparam)],
                          max_probes=200000, oracle=oracle)
    print(f"E-VALUE METAMORPHIC (seeds={len(point_only)} RR point objects, oracle-validated):")
    print(json.dumps(mm.to_dict(), indent=2, default=str))
    print("-" * 78)

    # ---- (4) ABSTAIN/CRASH ----
    ac = abstain_crash_hunt(eval_gate, malformed_inputs(), max_probes=100)
    print("E-VALUE ABSTAIN/CRASH:")
    print(json.dumps(ac.to_dict(), indent=2, default=str))
    print("-" * 78)

    # ---- (5) MULTIVERSE METAMORPHIC (spec reordering; NO oracle) ----
    mv_seeds = _mv_seeds()
    mv_mm = metamorphic_hunt(mv_gate, mv_seeds, _mv_reorder_transforms(),
                             max_probes=200000, oracle=None)
    print(f"MULTIVERSE METAMORPHIC (seeds={len(mv_seeds)} spec-curves, spec-reorder, NO oracle):")
    print(json.dumps(mv_mm.to_dict(), indent=2, default=str))
    print("-" * 78)

    any_kill = any(d.to_dict().get("KILL") for d in (fa, fr, mm, ac, mv_mm))
    print("ANY KILL:", any_kill)


if __name__ == "__main__":
    main()
