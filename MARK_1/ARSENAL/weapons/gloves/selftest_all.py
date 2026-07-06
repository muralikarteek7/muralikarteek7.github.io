#!/usr/bin/env python3
"""GLOVES frozen actuation-gate — run EVERY non-waivable gate-of-the-gate self-test.

Exits 0 only if the gate ACCEPTS a safe AUTO action, CATCHES every unsafe one
(no-token / param-drift / expiry / replay / scope-mismatch / no-dry-run /
unknown-tool / forged-token), HARD-BLOCKS the self-downgrade (CVE-2025-53773),
FAILS CLOSED on any exception, HONESTLY labels its infra-limited tamper-resistance,
and the router routes correctly.

Doctrine (kickoff §3): "A gate that can't FAIL (block a bad action) is not a gate."
If this exits non-zero, NO GLOVES action is trustworthy and NOTHING is allowed.

The twelve gate-of-the-gate tests (a..l) live in gloves_gate._selftest:
  (a) AUTO-allow R0/local read           (g) BLOCK unknown/unregistered tool (default-deny)
  (b) BLOCK STEP-UP w/ no token          (h) BLOCK on injected exception (fail-closed)
  (c) REJECT param-mismatched token      (i) REJECT tier-scope mismatch
  (d) REJECT expired + replayed token    (j) BLOCK commit w/ no dry-run reference
  (e) BLOCK+ALARM self-downgrade         (k) infra write-scope confirmed OR rail labeled ARMOR-class
  (f) ABSTAIN on unclassifiable tier     (l) agent-forged token FAILS the gate
"""
import sys
import tool_risk_registry
import infra_check
import gloves_gate
import gloves_router

CHECKS = [
    ("TOOL-RISK-REGISTRY (frozen tiers; unknown->None; self-protect surface)",
     tool_risk_registry._selftest),
    ("INFRA-CHECK        (self-protection rail honestly labeled kappa=1 OR ARMOR-class) [test k]",
     infra_check._selftest),
    ("ACTUATION-GATE     (the 12 gate-of-the-gate tests a..l: allow-safe / catch-every-unsafe / "
     "self-downgrade-BLOCK / fail-closed / forged-token-FAILS)",
     gloves_gate._selftest),
    ("ROUTER             (tier routing + abstain-on-unknown + self-edit-block + ceiling)",
     gloves_router._selftest),
]

if __name__ == "__main__":
    print("=" * 78)
    print("GLOVES frozen actuation-safety gate — non-waivable gate-of-the-gate self-tests")
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
        print(f"GATE: {failures} self-test(s) failed — DO NOT TRUST GLOVES; NOTHING is allowed.")
        sys.exit(1)
    print("GATE: allows the safe AUTO action AND catches every unsafe one "
          "(no-token/param-drift/expiry/replay/scope/no-dry-run/unknown/forged); "
          "hard-blocks the self-downgrade (CVE-2025-53773); fails closed on exception; "
          "tamper-resistance honestly labeled; router routes correctly. OK.")
    sys.exit(0)
