#!/usr/bin/env python3
"""SHIELD frozen-gate — run EVERY non-waivable self-test. Exits 0 ONLY if all four kappa=1
structural rails accept-good / catch-broken / abstain-malformed correctly, the kappa=0
abstain rail FLAGS-and-routes without ever self-certifying 'injection-free', the
NON-SYNTACTIC semantically-embedded injection correctly routes to ABSTAIN, and the router
routes every boundary event correctly.

Doctrine: "A gate that can't fail is not a gate." SHIELD is ARMOR-HARDENING, not a weapon.
If this exits non-zero, NO SHIELD rail is trustworthy.

The six gate-of-the-gate self-tests (kickoff 3):
  (a) external text CANNOT relabel itself to SYSTEM/USER
  (b) a verifier fed an ENV string in a code/spec slot REJECTS before running
  (c) a tool outside the cape is BLOCKED and a self-elevation attempt ALARMS
  (d) a certificate replayed onto a different object (hash-mismatch) is REJECTED
  (e) the ABSTAIN rail FLAGS a planted obvious-injection and never emits 'injection-free'
  (f) the NON-SYNTACTIC semantically-embedded injection -> ABSTAIN (no detect/clear claim)
"""
import sys
import shield_gate
import shield_router

CHECKS = [
    ("GATE  (a relabel-block / b taint-rail / c tool-cape+self-elevation / "
     "d cert-anti-replay / e abstain-no-overclaim / f NON-SYNTACTIC-injection->ABSTAIN)",
     shield_gate._selftest),
    ("ROUTER (boundary-event routing + abstain-or-escalate + never-a-weapon + ceiling)",
     shield_router._selftest),
]

if __name__ == "__main__":
    print("=" * 78)
    print("SHIELD frozen gate — non-waivable adversarial self-tests (ARMOR-HARDENING)")
    print("=" * 78)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}\n    *** SELF-TEST FAILED (rail broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  {name}\n    *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    print("=" * 78)
    if failures:
        print(f"GATE: {failures} self-test(s) failed — DO NOT TRUST any SHIELD rail.")
        sys.exit(1)
    print("GATE: 4 kappa=1 rails accept-good/catch-broken/abstain-malformed; kappa=0 rail "
          "FLAGS+routes without self-certifying 'injection-free'; non-syntactic injection "
          "-> ABSTAIN; router routes correctly. OK. (Hardening, NOT a weapon. NIST ceiling "
          "stated: no complete injection defense.)")
