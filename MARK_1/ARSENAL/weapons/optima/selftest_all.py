#!/usr/bin/env python3
"""OPTIMA frozen-gate self-test runner — the single gate before any OPTIMA result is trusted.

Doctrine (v5 weapon kickoff): "A verifier that can't fail is not a verifier." The OPTIMA gate
must (a) ACCEPT a known optimal with a valid gap=0 certificate, (b) REJECT an 'OPTIMAL' answer
that is actually INFEASIBLE, (c) REJECT an 'optimal' claim with a non-zero gap (relabel a bound),
(d) REJECT a wrong objective value -- plus prove an IIS and reject a bogus one. This script exits
0 only if the gate AND the router pass all their adversarial self-tests.

If this exits non-zero, NO OPTIMA result is trustworthy.
"""
import sys
import optima_gate
import optima_router

CHECKS = [
    ("OPTIMA-GATE  ", optima_gate._selftest),
    ("OPTIMA-ROUTER", optima_router._selftest),
]

if __name__ == "__main__":
    print("=" * 72)
    print("OPTIMA frozen-gate — adversarial self-tests (accept-optimal / reject-infeasible /")
    print("reject-nonzero-gap / reject-wrong-objective / IIS-proven / bogus-IIS-rejected)")
    print("=" * 72)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}  *** SELF-TEST FAILED (gate is broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  {name}  *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    print("=" * 72)
    if failures:
        print(f"GATE: {failures} check(s) failed — DO NOT TRUST any OPTIMA output.")
        sys.exit(1)
    print("GATE: gate accepts truth AND rejects every broken claim; router routes + abstains. OK.")
