#!/usr/bin/env python3
"""Independent ORACLE for the psymetrix GRIM gate.

From-scratch exact GRIM arithmetic (Fraction), authored independently of psymetrix's
forensics_verify.grim. GRIM: a reported mean of N integer responses (items averaged) can
only equal k/(N*items) for some integer k, within half-ULP rounding tolerance at the
reported decimal precision (GROUNDING.md). Re-implementing the exact Fraction arithmetic
from scratch is methodologically foreign to the psymetrix gate -> a genuine oracle.
"""
from fractions import Fraction
import math


def grim_consistent(mean_str, n, items=1):
    """TRUTH: is the reported mean GRIM-consistent for the stated N/items? (exact bool).
    Independent re-impl: explicit integer-band search, not the gate's ceil/floor pair."""
    s = str(mean_str).strip()
    D = len(s.split(".")[1]) if "." in s else 0
    x = Fraction(s)
    Neff = int(n) * int(items)
    tol = Fraction(1, 2 * 10 ** D)
    lo, hi = x - tol, x + tol
    # smallest k with k/Neff >= lo, largest k with k/Neff <= hi (independent derivation)
    k_min = math.ceil(lo * Neff)
    k_max = math.floor(hi * Neff)
    return k_min <= k_max


def truth_correct_or_wrong(obj):
    """Oracle interface: obj={'mean_str':..., 'n':..., 'items':...}.
    CORRECT (mean IS achievable) / WRONG (NOT achievable) / None (malformed)."""
    try:
        n, items = int(obj["n"]), int(obj.get("items", 1))
    except Exception:
        return None
    if n <= 0 or items <= 0:
        return None
    try:
        return "CORRECT" if grim_consistent(obj["mean_str"], n, items) else "WRONG"
    except Exception:
        return None


if __name__ == "__main__":
    assert grim_consistent("3.0", 20, 1) is True        # 60/20 = 3.0
    assert grim_consistent("5.19", 28, 1) is False       # no integer k/28 rounds to 5.19
    print("grim_oracle smoke: PASS (3.0@n20 CORRECT; 5.19@n28 WRONG)")
