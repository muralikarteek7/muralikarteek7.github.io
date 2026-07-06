#!/usr/bin/env python3
"""CRUCIBLE router — given a weapon to probe, decide WHICH probe modes fire.

The decisive question is the ORACLE-INDEPENDENCE gate (kickoff §1a):
  * weapon WITH a genuinely-independent oracle  -> ALL FOUR modes (full differential).
  * weapon WITHOUT an independent oracle         -> metamorphic + abstain/crash ONLY,
                                                    labeled "partial coverage".
  * a kappa=0 "gate" that is actually ARMOR / a guarded-kappa verdict
                                                 -> CRUCIBLE DECLINES (you cannot
                                                    adversarially falsify a judgment that
                                                    never claimed an exact verifier).

This mirrors the symbolica/socius/psymetrix router pattern: classify, draw the matching
modes, and DECLINE the residue. It decides routing; the harness runs the probes.

The per-weapon scope is PRE-COMMITTED here (the demo-with-predictions rule applied to
CRUCIBLE) -- the audit-estimated §4a buckets, NOT silently expanded. Each entry records
the κ=1 slice probed, the planned oracle, the modes, and the reason.
"""
import sys
import json

# Probe-mode names
ALL_FOUR = ["FALSE-ACCEPT", "FALSE-REJECT", "METAMORPHIC", "ABSTAIN-CRASH"]
NO_ORACLE = ["METAMORPHIC", "ABSTAIN-CRASH"]

# coverage labels
FULL = "full-differential"
PARTIAL = "metamorphic-only (partial)"
DECLINED = "DECLINED"

# --------------------------------------------------------------------------- #
#  THE PRE-COMMITTED SCOPE TABLE (kickoff §4a). oracle_independent drives modes.
#  "slice" = the exact gate-self-declared κ=1 part CRUCIBLE probes (mixed-κ weapons
#  probe ONLY the exact slice; guarded-κ verdicts are DECLINED).
# --------------------------------------------------------------------------- #
SCOPE = {
    "codeforge_sortnet": dict(
        oracle_independent=True, oracle="exhaustive 0/1 enumeration (foreign to the synthesis engine)",
        slice="comparator-list sorts all 2^n inputs (0/1 principle)", coverage=FULL,
        reason="0/1 enumeration is a different mechanism than the network synthesizer -> genuine oracle."),
    "psymetrix_grim": dict(
        oracle_independent=True, oracle="from-scratch exact Fraction GRIM arithmetic",
        slice="reported mean achievable as k/(N*items)", coverage=FULL,
        reason="re-implementing the exact Fraction arithmetic from scratch is methodologically foreign."),
    "trialguard_grim": dict(
        oracle_independent=True, oracle="from-scratch exact Fraction GRIM (same as psymetrix)",
        slice="Carlisle/GRIM exact-arithmetic slice", coverage=FULL,
        reason="same exact-arithmetic re-impl; the κ=1 slice only (NOT the heuristic fraud screen)."),
    "factharness_quote": dict(
        oracle_independent=True, oracle="2nd fetch + a different text extractor",
        slice="quote-substring / number-equality against committed source", coverage=FULL,
        reason="a second independent fetch + a different extractor is foreign to the gate's extractor."),
    "redcell_ctf": dict(
        oracle_independent=True, oracle="flag==expected (independently checkable)",
        slice="submitted flag byte-exact / hash-exact match", coverage=FULL,
        reason="exact equality is trivially independently checkable -> genuine oracle."),
    "frontier_capset": dict(
        oracle_independent=True, oracle="independent capset_verify re-check (already κ=1)",
        slice="claimed cap set is genuinely 3-AP-free of stated size", coverage=FULL,
        reason="re-running the κ=1 verify from scratch catches a passing-but-invalid cap."),
    "optima_feasibility": dict(
        oracle_independent=False, oracle="needs a separately-authored solver (PuLP/GLPK) + independent dual check",
        slice="feasibility/optimality certificate", coverage=PARTIAL,
        reason="OPTIMA's gate already runs exhaustive enum + Held-Karp/Hungarian -> brute-force oracle "
               "is its OWN mechanism (not independent). Metamorphic + limited differential only."),
    "proofsmith_wrapper": dict(
        oracle_independent=False, oracle="Lean kernel is near-oracle; probe the wrapper/axiom-scan, not the kernel",
        slice="wrapper / axiom-scan around the kernel", coverage=PARTIAL,
        reason="the kernel itself is the oracle -> probe the wrapper for crash/relabel instability only."),
    "reproml_contamination": dict(
        oracle_independent=False, oracle="n-gram re-impl feasible but the threshold is a free param",
        slice="n-gram overlap above a threshold", coverage=PARTIAL,
        reason="the threshold is a tunable free parameter -> no exact truth; metamorphic + limited diff."),
    "symbolica_agreement": dict(
        oracle_independent=False, oracle="WEAK -- all 3 method-families are ALREADY gate certificate legs",
        slice="multi-method cross-agreement", coverage=PARTIAL,
        reason="the gate IS multi-method agreement (symbolic+mpmath+scipy/series); a 'third method' is "
               "already one of its legs -> circular. Metamorphic + abstain ONLY unless a foreign CAS is found."),
    "socius_evalue": dict(
        oracle_independent=False, oracle="E-value arithmetic re-implementable; multiverse is metamorphic",
        slice="E-value arithmetic + multiverse", coverage=PARTIAL,
        reason="§4a: differential on the E-value arithmetic slice, metamorphic on multiverse -> "
               "treated as PARTIAL (the multiverse leg has no exact oracle). Matches the pre-committed table."),
    "econometrix_walkforward": dict(
        oracle_independent=False, oracle="NONE -- guarded-κ (~0.4), no exact oracle",
        slice="(none -- guarded-κ verdict)", coverage=DECLINED,
        reason="walk-forward DSR is a guarded-κ (~0.4) probabilistic verdict, NOT a κ=1 claim. A "
               "'false-accept' on a probabilistic verdict is UNDEFINED -> DECLINE (probe nothing)."),
}

CEILING = ("CRUCIBLE proves a gate BROKEN (a κ=1 re-runnable exhibit) or reports it SURVIVED "
           "to an explicit budget with explicit oracle coverage + residual risk. It NEVER calls "
           "a gate 'sound' or 'proven' without an exhibit (Dijkstra: testing shows the presence "
           "of bugs, never their absence), NEVER judges a false-accept with the same engine it "
           "is testing, and DECLINES κ=0 armor and guarded-κ verdicts.")


def route(weapon_key):
    """Return the probe plan for a weapon. Unknown weapon -> abstain (ask for the κ=1 slice)."""
    entry = SCOPE.get(weapon_key)
    if entry is None:
        return {"weapon": weapon_key, "modes": [], "coverage": "UNKNOWN",
                "note": "weapon not in the pre-committed scope table -- abstain; register its "
                        "κ=1 slice + an independent oracle (or declare metamorphic-only) first.",
                "ceiling": CEILING}
    if entry["coverage"] == DECLINED:
        modes = []
        note = ("DECLINED: this is a guarded-κ / κ=0 verdict, not a gate-self-declared κ=1 claim. "
                "CRUCIBLE cannot adversarially falsify a judgment that never claimed an exact "
                "verifier. " + entry["reason"])
    elif entry["oracle_independent"]:
        modes = list(ALL_FOUR)
        note = ("INDEPENDENT oracle exists -> FULL DIFFERENTIAL (all four modes). " + entry["reason"])
    else:
        modes = list(NO_ORACLE)
        note = ("NO independent oracle -> METAMORPHIC + ABSTAIN/CRASH ONLY (partial coverage; "
                "false-accept/reject hunts would be CIRCULAR). " + entry["reason"])
    return {"weapon": weapon_key, "kappa1_slice": entry["slice"], "oracle": entry["oracle"],
            "oracle_independent": entry["oracle_independent"], "modes": modes,
            "coverage": entry["coverage"], "note": note, "ceiling": CEILING}


def coverage_summary():
    """The honest per-bucket breakdown -- NEVER a blanket 'all 12 survived'."""
    full = [k for k, v in SCOPE.items() if v["coverage"] == FULL]
    partial = [k for k, v in SCOPE.items() if v["coverage"] == PARTIAL]
    declined = [k for k, v in SCOPE.items() if v["coverage"] == DECLINED]
    return {"full_differential": full, "metamorphic_only": partial, "declined": declined,
            "counts": {"full": len(full), "partial": len(partial), "declined": len(declined)}}


def _selftest():
    # a weapon WITH an independent oracle -> all four modes, full coverage
    r = route("codeforge_sortnet")
    assert r["modes"] == ALL_FOUR and r["coverage"] == FULL, r
    assert r["oracle_independent"] is True
    # a weapon WITHOUT an independent oracle -> metamorphic + abstain only, partial
    r = route("symbolica_agreement")
    assert r["modes"] == NO_ORACLE and r["coverage"] == PARTIAL, r
    assert "CIRCULAR" in r["note"]
    r = route("optima_feasibility")
    assert r["modes"] == NO_ORACLE and r["coverage"] == PARTIAL, r
    # a guarded-κ / κ=0 verdict -> DECLINED (probe nothing)
    r = route("econometrix_walkforward")
    assert r["modes"] == [] and r["coverage"] == DECLINED, r
    assert "DECLINE" in r["note"]
    # an unknown weapon -> abstain
    r = route("nonexistent_weapon")
    assert r["modes"] == [] and r["coverage"] == "UNKNOWN", r
    # ceiling always present, naming the no-sound-without-exhibit doctrine + Dijkstra
    assert "never their absence" in route("codeforge_sortnet")["ceiling"]
    assert "Dijkstra" in CEILING
    # coverage summary is honest: NOT a blanket all-survived; named buckets sum to 12
    s = coverage_summary()
    total = s["counts"]["full"] + s["counts"]["partial"] + s["counts"]["declined"]
    assert total == 12, f"scope table must cover all 12 weapons, got {total}"
    assert s["counts"]["full"] >= 5, s          # ~5-6 full per the audit estimate
    assert s["counts"]["declined"] >= 1, s      # at least econometrix declined
    print(f"crucible_router selftest: PASS (independent->4 modes; no-oracle->metamorphic-only; "
          f"guarded-κ->DECLINED; unknown->abstain; coverage {s['counts']})")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2 and sys.argv[1] == "summary":
        print(json.dumps(coverage_summary(), indent=2))
    elif len(sys.argv) >= 2:
        print(json.dumps(route(sys.argv[1]), indent=2))
    else:
        print("usage: crucible_router.py selftest | summary | <weapon_key>")
