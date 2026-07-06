#!/usr/bin/env python3
"""ECONOMETRIX frozen-verifier gate — run EVERY sub-weapon's adversarial self-test.

Doctrine (the v5 weapon kickoff): "A verifier that can't fail is not a verifier." Each kappa>0
sub-weapon is tested on a known-good input (must pass) AND a known-broken input (must be caught). This
is the single gate: it exits 0 only if all verifiers pass good inputs AND fail broken inputs.

The NON-WAIVABLE four (from the kickoff s3): the gate must (a) PASS a genuine OOS-surviving edge,
(b) KILL an over-fit rule (strong in-sample, no OOS -> DSR ~ 0), (c) CATCH a leakage/look-ahead bug
(inflated OOS from future data), (d) FLAG a DiD whose pre-trends FAIL / an IV with a weak first stage.
All four live inside backtest_verify._selftest (a,b,c) + causal_verify._selftest (d).

E-ROBUST and E-REPRO are REUSED from SOCIUS (socius/multiverse_verify.py, socius/repro_verify.py) —
their self-tests are run here too so the gate covers the full mixed-kappa kit.

Run before trusting any ECONOMETRIX result. If this exits non-zero, NO ECONOMETRIX number is trusted.
"""
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "socius"))

import backtest_verify       # E-BACKTEST (NEW)
import causal_verify         # E-CAUSAL  (NEW)
import multiverse_verify     # E-ROBUST  (reused from SOCIUS)
import repro_verify          # E-REPRO   (reused from SOCIUS)

CHECKS = [
    ("E-BACKTEST  (NEW: walk-forward + Deflated Sharpe + leakage)", backtest_verify._selftest),
    ("E-CAUSAL    (NEW: DiD pre-trends / McCrary / weak-IV / Oster)", causal_verify._selftest),
    ("E-ROBUST    (reused socius/multiverse_verify)", multiverse_verify._selftest),
    ("E-REPRO     (reused socius/repro_verify)", repro_verify._selftest),
]

if __name__ == "__main__":
    print("=" * 74)
    print("ECONOMETRIX frozen-verifier gate — adversarial self-tests")
    print("=" * 74)
    failures = 0
    for name, fn in CHECKS:
        print(f"\n>>> {name}")
        try:
            fn()
        except AssertionError as e:
            print(f"    *** SELF-TEST FAILED (verifier is broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"    *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    print("\n" + "=" * 74)
    if failures:
        print(f"GATE: {failures} verifier(s) failed — DO NOT TRUST any ECONOMETRIX output.")
        sys.exit(1)
    print("GATE: all frozen verifiers pass good inputs AND catch broken inputs. OK.")
    print("  (a) genuine OOS edge PASSES · (b) overfit rule KILLED (DSR~0) · (c) look-ahead CAUGHT ·")
    print("  (d) failed-pre-trends DiD + weak IV FLAGGED. In-sample is never the verdict.")
