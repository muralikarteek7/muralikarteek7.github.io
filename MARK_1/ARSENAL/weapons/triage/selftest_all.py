#!/usr/bin/env python3
"""TRIAGE frozen gate — run EVERY self-test. Exits 0 ONLY if:
  * the checklist ACCEPTS a clean grounded output (no false fire),
  * CATCHES a fabricated output (kappa=1 via FACTHARNESS, or honest degrade),
  * CATCHES a branch-cut "identity" sold as global (kappa=1),
  * ABSTAINS LOUDLY on a malformed record (never silent-passes),
  * NEVER emits 'safe'/'all-clear', and always carries uncovered_novel_classes=True,
  * RE-FLAGS >=3 REAL past failures the human audits caught (NON-WAIVABLE proof of value),
  * and the router routes kappa=1 -> machine, kappa<1 -> panel.

Doctrine: "A gate that can't fail is not a gate." If this exits non-zero, NO TRIAGE
report is trustworthy.
"""
import sys
import triage_check, triage_router, triage_retroactive

CHECKS = [
    ("CHECKLIST (accept-good / catch-fabrication k=1 / catch-branch-cut k=1 / abstain-malformed "
     "loud / no-all-clear / uncovered_novel_classes-locked / every k=1 reject case)",
     triage_check._selftest),
    ("RETROACTIVE RE-FLAG (NON-WAIVABLE: >=3 REAL past failures re-fire the human-caught row)",
     triage_retroactive._selftest),
    ("ROUTER (kappa=1 -> machine; kappa<1 -> panel; clean -> no-class-fired; malformed -> abstain)",
     triage_router._selftest),
]

if __name__ == "__main__":
    print("=" * 80)
    print("TRIAGE frozen gate — failure-class -> detector -> mitigation; adversarial self-tests")
    print("=" * 80)
    print(f"  composes FACTHARNESS: {triage_check._HAVE_FACTHARNESS}    "
          f"CRUCIBLE present: {triage_check._HAVE_CRUCIBLE}")
    print("-" * 80)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}\n    *** SELF-TEST FAILED (gate broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  {name}\n    *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    print("=" * 80)
    if failures:
        print(f"GATE: {failures} self-test(s) failed — DO NOT TRUST any TRIAGE output.")
        sys.exit(1)
    print("GATE: checklist accepts clean output AND catches fabrication/branch-cut, abstains loudly "
          "on malformed input, never emits 'safe', re-flags >=3 REAL past failures, router routes "
          "correctly. OK. (ARMOR rail — NOT a capability; novel classes still escape.)")
