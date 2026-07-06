#!/usr/bin/env python3
"""TRIALGUARD frozen-verifier gate — run EVERY sub-weapon's adversarial self-test.

Doctrine: "A verifier that can't fail is not a verifier." Each kappa>0 check is tested
on a known-good input (must PASS), a known-broken input (must be CAUGHT), and malformed
input (must ABSTAIN). For the FORENSIC slice the bar is heightened (the domain is
clinical): the gate also asserts the 4 CARDINAL tests from the kickoff —
  (a) a clean properly-randomized trial PASSES with ZERO false flags (soundness),
  (b) a GRIM-impossible reported mean is CAUGHT,
  (c) a clearly-anomalous (too-similar) baseline is FLAGGED WITH benign explanations,
  (d) a legitimately STRATIFIED trial is NOT flagged as fraud (it names stratification),
and that NO forensic output ever AFFIRMS misconduct.

This is the single gate: it exits 0 only if all verifiers behave correctly. If this
exits non-zero, NO TRIALGUARD number is trustworthy.
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# reused SOCIUS verifiers live in ../socius
_SOCIUS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "socius")
if _SOCIUS not in sys.path:
    sys.path.insert(0, _SOCIUS)

import forensics_trial_verify as TF
import survival_verify as SV
import meta_trial_verify as MT
import trialguard_router as RT

CHECKS = [
    ("T-FORENSICS  (Carlisle + GRIM/GRIMMER + group/percentage + E-value)", TF._selftest),
    ("T-SURVIVAL   (Kaplan-Meier + Cox PH vs independent statsmodels)     ", SV._selftest),
    ("T-META       (reuse PSYMETRIX pool/I2/Egger + trim-and-fill)        ", MT._selftest),
    ("ROUTER       (kappa-routing + inconsistency!=fraud ceiling)         ", RT._selftest),
]
# reused, already-frozen SOCIUS verifiers (T-REPRO / T-MULTIVERSE)
try:
    import repro_verify
    CHECKS.append(("T-REPRO      (reused socius/repro_verify)                     ",
                   repro_verify._selftest))
except Exception as _e:
    print(f"  T-REPRO      *** SKIPPED — {type(_e).__name__}: {_e} ***")
try:
    import multiverse_verify
    CHECKS.append(("T-MULTIVERSE (reused socius/multiverse_verify)                ",
                   multiverse_verify._selftest))
except Exception as _e:
    print(f"  T-MULTIVERSE *** SKIPPED (needs statsmodels) — {type(_e).__name__} ***")


def _cardinal_forensic_tests():
    """The 4 heightened cardinal tests, asserted directly at the gate (in addition to
    the module self-tests), because they are the load-bearing clinical-safety claims."""
    import numpy as np
    rng = np.random.default_rng(11)
    # (a) clean randomized trial -> not flagged + non-accusatory
    clean = TF._sim_clean_trial(rng, k=8)
    ra = TF.carlisle_baseline_test(clean, alpha=0.001, design="simple")
    assert ra["anomaly"] is False, "(a) a clean randomized trial must not be flagged"
    assert not TF.affirms_misconduct(ra["verdict"])
    # (b) GRIM-impossible reported clinical mean -> caught (reused exact GRIM)
    assert TF.PF.grim("5.27", 43)["consistent"] is False, "(b) GRIM 5.27/43 must be caught"
    # (c) too-similar baseline -> flagged WITH benign explanations attached
    fake = [{"name": f"v{j}", "type": "continuous", "mean1": 50.0, "sd1": 10.0, "n1": 60,
             "mean2": 50.02, "sd2": 10.0, "n2": 60} for j in range(8)]
    rc = TF.carlisle_baseline_test(fake, alpha=0.001, design="unknown")
    assert rc["anomaly"] is True and rc["direction"] == "too_similar", "(c) must flag too-similar"
    assert rc["candidate_benign_explanations"] and rc["false_positive_modes"], \
        "(c) flag must attach benign explanations + false-positive modes"
    assert not TF.affirms_misconduct(rc["verdict"]), "(c) flag must not affirm misconduct"
    # (d) stratified trial -> not called fraud; names stratification
    rd = TF.carlisle_baseline_test(fake, alpha=0.001, design="stratified")
    assert not TF.affirms_misconduct(rd["verdict"])
    assert rd.get("design_caveat") and "stratified" in rd["design_caveat"].lower(), \
        "(d) stratified design must carry a stratification caveat"
    print("  CARDINAL     (a) clean PASSES  (b) GRIM-impossible CAUGHT  "
          "(c) too-similar FLAGGED+explained  (d) stratified NOT accused — all OK")


if __name__ == "__main__":
    print("=" * 78)
    print("TRIALGUARD frozen-verifier gate — adversarial self-tests")
    print("=" * 78)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}  *** SELF-TEST FAILED (verifier broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  {name}  *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    try:
        _cardinal_forensic_tests()
    except AssertionError as e:
        print(f"  CARDINAL     *** CARDINAL FORENSIC TEST FAILED ***  {e}")
        failures += 1
    print("=" * 78)
    if failures:
        print(f"GATE: {failures} check(s) failed — DO NOT TRUST any TRIALGUARD output.")
        sys.exit(1)
    print("GATE: all frozen verifiers pass good inputs, catch broken inputs, abstain on "
          "malformed input, and NO forensic output affirms misconduct. OK.")
