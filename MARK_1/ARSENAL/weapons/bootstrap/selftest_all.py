#!/usr/bin/env python3
"""BOOTSTRAP frozen gate — run EVERY non-waivable self-test. Exits 0 ONLY if:
  - the candidate-validation gate ACCEPTS a sound+complete verifier (kappa=1),
    CATCHES a hallucinated/non-running one, a can't-fail one, a soundness-
    incomplete one, a reject-good one, and one that fails to abstain on malformed,
  - the router routes exact-decidable->SEARCH, judgment->ARMOR(kappa=0),
    under-specified->ABSTAIN, and never promotes from routing alone.

Doctrine ("a gate that can't fail is not a gate"): if this exits non-zero, NO
BOOTSTRAP verdict about any domain's kappa is trustworthy.
"""
import sys
import bootstrap_gate, bootstrap_router

CHECKS = [
    ("VALIDATION-GATE (accept sound+complete / reject hallucinated / reject can't-fail / "
     "reject soundness-incomplete / reject-good / abstain-malformed / "
     "REGRESSION: reject no-malformed-case [Defect A] / reject empty-declared-types + "
     "untyped-broken [Defect B])",
     bootstrap_gate._selftest),
    ("ROUTER          (exact->SEARCH no-kappa-from-routing / judgment->ARMOR / "
     "dressed->ARMOR / under-specified->ABSTAIN)",
     bootstrap_router._selftest),
]

if __name__ == "__main__":
    print("=" * 78)
    print("BOOTSTRAP frozen validation-gate — adversarial self-tests")
    print("=" * 78)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}\n    *** SELF-TEST FAILED (gate broken) ***  {e}")
            failures += 1
        except Exception as e:  # noqa: BLE001
            print(f"  {name}\n    *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    print("=" * 78)
    if failures:
        print(f"GATE: {failures} self-test(s) failed — DO NOT TRUST any BOOTSTRAP verdict.")
        sys.exit(1)
    print("GATE: validation-gate accepts sound+complete verifiers AND catches "
          "hallucinated / can't-fail / soundness-incomplete / reject-good / "
          "no-abstain ones; router routes correctly and never promotes from routing. OK.")
