#!/usr/bin/env python3
"""CODEFORGE frozen-verifier gate — run EVERY verifier's adversarial self-test.

Doctrine (v5 weapon kickoff, non-waivable): "A verifier that can't fail is not a
verifier." Each frozen verifier is tested on a KNOWN-GOOD input (must pass), a
KNOWN-BROKEN input (must be caught), AND a GAMING attempt (must be rejected). This
script is the single gate: it exits 0 only if all verifiers pass good inputs, catch
broken inputs, and reject gaming attempts.

Run BEFORE trusting any CODEFORGE result. If this exits non-zero, NO CODEFORGE
object is trustworthy. (The router self-tests itself; it is included here too.)
"""
import sys
import sortnet_verify
import matmul_verify
import synth_verify
import superopt_verify
import codeforge_router

CHECKS = [
    ("SORTNET      ", sortnet_verify._selftest),
    ("MATMUL       ", matmul_verify._selftest),
    ("SYNTH-VERIFY ", synth_verify._selftest),
    ("SUPEROPT     ", superopt_verify._selftest),
    ("ROUTER       ", codeforge_router._selftest),
]

if __name__ == "__main__":
    print("=" * 74)
    print("CODEFORGE frozen-verifier gate — adversarial self-tests "
          "(passes-good / catches-broken / rejects-gaming)")
    print("=" * 74)
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
    print("=" * 74)
    if failures:
        print(f"GATE: {failures} verifier(s) failed — DO NOT TRUST any CODEFORGE output.")
        sys.exit(1)
    print("GATE: all frozen verifiers pass good inputs, catch broken inputs, AND reject "
          "gaming attempts. OK.")
