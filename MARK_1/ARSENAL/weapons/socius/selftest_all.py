#!/usr/bin/env python3
"""SOCIUS frozen-verifier gate — run EVERY sub-weapon's adversarial self-test.

Doctrine (from the v5 weapon kickoff): "A verifier that can't fail is not a
verifier." Each kappa>0 sub-weapon is tested on BOTH a known-good input (must
pass) AND a known-broken input (must be caught). This script is the single gate:
it exits 0 only if all verifiers pass on good inputs and FAIL on broken inputs.

Run before trusting any SOCIUS result. If this exits non-zero, no SOCIUS number
is trustworthy.
"""
import sys
import repro_verify, eval_verify, multiverse_verify, sample_verify, measure_verify
import ground_verify

def _evalue_nonfinite_regression():
    """FROZEN CRUCIBLE regression (socius_evalue ABSTAIN/CRASH kill, 2026-06-20).

    The probe exhibited estimate=+inf -> robust_to_confounding=True: e_value(inf)=inf
    and inf>=benchmark made a CONFIDENT ACCEPT on nonsense. nan gave a confident
    False (REJECT on nonsense). A non-finite estimate (or ci_limit) must now be
    REJECTED loudly (ValueError), NEVER return a verdict dict. This is the exhibit
    frozen at the gate entry point itself, independent of eval_verify._selftest."""
    for bad in (float("inf"), float("nan"), float("-inf")):
        try:
            r = eval_verify.assess_sensitivity(bad, "RR", benchmark_confounding=2.0)
        except ValueError:
            continue  # SAFE: loud guard
        raise AssertionError(
            "non-finite estimate %r returned a verdict (robust_to_confounding=%r) "
            "instead of raising — CRUCIBLE non-finite hole reopened." % (
                bad, r.get("robust_to_confounding")))
    try:
        eval_verify.assess_sensitivity(3.9, "RR", ci_limit=float("inf"),
                                       benchmark_confounding=2.0)
    except ValueError:
        pass  # SAFE
    else:
        raise AssertionError("non-finite ci_limit did not raise — hole reopened.")


CHECKS = [
    ("S-REPRO     ", repro_verify._selftest),
    ("S-CAUSAL    ", eval_verify._selftest),
    ("S-CAUSAL-REG", _evalue_nonfinite_regression),
    ("S-MULTIVERSE", multiverse_verify._selftest),
    ("S-SAMPLE    ", sample_verify._selftest),
    ("S-MEASURE   ", measure_verify._selftest),
    ("S-GROUND    ", ground_verify._selftest),
]

if __name__ == "__main__":
    print("=" * 70)
    print("SOCIUS frozen-verifier gate — adversarial self-tests")
    print("=" * 70)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}  *** SELF-TEST FAILED (verifier is broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  {name}  *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    print("=" * 70)
    if failures:
        print(f"GATE: {failures} verifier(s) failed — DO NOT TRUST any SOCIUS output.")
        sys.exit(1)
    print("GATE: all frozen verifiers pass good inputs AND catch broken inputs. OK.")
