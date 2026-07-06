#!/usr/bin/env python3
"""COMPOSEAUTH (G3) frozen compositional-authorization gate — run EVERY non-waivable
gate-of-the-gate self-test. Exits 0 ONLY if the budget gate:
  - CATCHES the just-under-threshold SALAMI attack (N steps each below the per-action
    GLOVES trigger AND below the session threshold, whose SUM crosses it -> ESCALATE),
  - HALTS a delete-burst past the destruction threshold,
  - does NOT false-halt a single small legitimate action,
  - does NOT reset the budget on a simulated crash-resume (persistence),
  - REPORTS effect in an untracked class as UNCOVERED (never silent 'within budget'),
  - FAILS CLOSED on a malformed entry,
  - and the router routes BUDGET / UNCOVERED / ABSTAIN correctly.

Doctrine (kickoff §3): "the gate must be able to FAIL (halt a runaway sequence) or it
is not a gate." If this exits non-zero, NO COMPOSEAUTH budget verdict is trustworthy.
"""
import sys

import composeauth_policy
import mock_gloves_ledger
import composeauth_gate
import composeauth_router

CHECKS = [
    ("POLICY            (thresholds step_up<halt every class; every class weighted; "
     "thresholds+WEIGHTS labeled POLICY not truth)",
     composeauth_policy._selftest),
    ("MOCK-GLOVES-LEDGER (known tool->mapped deltas + external tick; unknown tool->"
     "UNCOVERED; novel other_effects class->UNCOVERED catch-all)",
     mock_gloves_ledger._selftest),
    ("BUDGET-GATE       (the 5 gate-of-the-gate tests a..e: SALAMI->ESCALATE / "
     "delete-burst->HALT / single-small->OK no-false-halt / crash-resume persistence / "
     "untracked-class->UNCOVERED; + fail-closed + policy banner)",
     composeauth_gate._selftest),
    ("ROUTER            (BUDGET/UNCOVERED/ABSTAIN routing + ceiling + policy banner)",
     composeauth_router._selftest),
]

if __name__ == "__main__":
    print("=" * 78)
    print("COMPOSEAUTH (G3) frozen compositional-authorization gate — non-waivable self-tests")
    print("=" * 78)
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
    print("=" * 78)
    if failures:
        print(f"GATE: {failures} self-test(s) failed — DO NOT TRUST COMPOSEAUTH; "
              "the composition budget is not enforced.")
        sys.exit(1)
    print("GATE: catches the just-under-threshold SALAMI (ESCALATE) AND the delete-burst "
          "(HALT); no false halt on a benign action; budget SURVIVES crash-resume; "
          "untracked-class effect reported UNCOVERED (never silent); fails closed on bad "
          "input; router routes BUDGET/UNCOVERED/ABSTAIN correctly. OK.")
    sys.exit(0)
