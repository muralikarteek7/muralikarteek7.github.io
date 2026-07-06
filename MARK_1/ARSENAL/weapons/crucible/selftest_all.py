#!/usr/bin/env python3
"""CRUCIBLE frozen gate-of-the-gate — run EVERY adversarial self-test. Exits 0 ONLY if
the meta-verifier:
  (a)/(b) CATCHES a SUBTLE planted false-accept (off-by-one / too-wide tolerance) LOCATION-BLIND
          (the SEARCH is not told where the hole is; NOTE per AUDIT A8 the fixture is
          builder-authored, NOT a different-agent plant -- the auditor supplies the stronger one);
  (c)     CATCHES a planted metamorphic instability (verdict flips under a meaning-
          preserving relabel/items-split);
  (+)     CATCHES a planted silent-pass on a malformed input;
  (d)     raises NO FALSE ALARM on a KNOWN-GOOD frozen gate;
  (e)     LABELS "no counterexample found" as CONFIDENCE, never PROOF (the word
          "sound"/"proven" is machine-banned from a SURVIVED report);
  (+)     REFUSES to ship a KILL from a buggy oracle (spurious-kill rail) and REFUSES a
          non-independent oracle for a false-accept hunt (circularity rail);
  and the router routes (independent->4 modes / no-oracle->metamorphic-only / guarded-κ
  ->DECLINE / unknown->abstain) over a scope table covering all 12 weapons.

Doctrine: "A meta-verifier that can't catch a planted hole is theater." If this exits
non-zero, NO CRUCIBLE soundness-confidence claim is trustworthy.
"""
import sys
import crucible_harness
import crucible_router

CHECKS = [
    ("HARNESS gate-of-the-gate (catch subtle false-accept / metamorphic / silent-pass; "
     "no-false-alarm; confidence-not-proof labeling; spurious-kill + circularity rails)",
     crucible_harness._selftest),
    ("ROUTER (independent->4 modes; no-oracle->metamorphic-only; guarded-κ->DECLINE; "
     "unknown->abstain; scope covers all 12)",
     crucible_router._selftest),
]

if __name__ == "__main__":
    print("=" * 78)
    print("CRUCIBLE frozen meta-verifier — gate-of-the-gate adversarial self-tests")
    print("=" * 78)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}\n    *** SELF-TEST FAILED (meta-gate broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  {name}\n    *** ERROR ***  {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            failures += 1
    print("=" * 78)
    if failures:
        print(f"META-GATE: {failures} self-test(s) failed — DO NOT TRUST any CRUCIBLE output.")
        sys.exit(1)
    print("META-GATE: CRUCIBLE catches BLIND subtle planted bugs (false-accept / metamorphic / "
          "silent-pass), raises no false alarm on a good gate, refuses buggy/dependent oracles, "
          "and labels no-kill as CONFIDENCE not PROOF; router routes correctly. OK.")
