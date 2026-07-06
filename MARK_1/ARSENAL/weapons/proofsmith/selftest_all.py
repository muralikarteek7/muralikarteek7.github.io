#!/usr/bin/env python3
"""PROOFSMITH frozen-gate self-test — the single non-waivable gate.

Doctrine: "A gate that can't fail is not a gate." The kernel gate (proof_gate.py)
must ACCEPT a known-good kernel-checked proof AND REJECT each of the three cheats
a proof assistant allows (sorry / bogus axiom / wrong statement). The SMT slice
(smt_gate.py) must accept real validities and reject non-validities with a
counter-model.

Run this BEFORE trusting any PROOFSMITH output. If it exits non-zero, no
PROOFSMITH proof is trustworthy.
"""
import sys
import proof_gate
import smt_gate

CHECKS = []

if proof_gate.lean_available():
    CHECKS.append(("KERNEL gate (Lean 4) ", proof_gate._selftest))
else:
    print("  [warn] Lean 4 not found — KERNEL gate self-test SKIPPED. "
          "Only the SMT decidable slice is available; scope is reduced accordingly.")

if smt_gate.z3_available():
    CHECKS.append(("SMT slice (z3)       ", smt_gate._selftest))
else:
    print("  [warn] z3 not found — SMT slice self-test SKIPPED.")


if __name__ == "__main__":
    print("=" * 70)
    print("PROOFSMITH frozen-gate self-tests (accept-good / reject every cheat)")
    print("=" * 70)
    if not CHECKS:
        print("GATE: NO verifier available (neither Lean nor z3). Cannot trust any output.")
        sys.exit(1)
    failures = 0
    for name, fn in CHECKS:
        print(f"\n--- {name} ---")
        try:
            fn()
        except AssertionError as e:
            print(f"  *** SELF-TEST FAILED (gate is broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    print("\n" + "=" * 70)
    if failures:
        print(f"GATE: {failures} self-test(s) FAILED — DO NOT TRUST any PROOFSMITH output.")
        sys.exit(1)
    print("GATE: all gates accept good proofs AND catch every cheat. OK.")
