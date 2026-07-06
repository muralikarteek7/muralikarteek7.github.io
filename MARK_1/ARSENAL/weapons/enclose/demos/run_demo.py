#!/usr/bin/env python3
"""ENCLOSE killer demo — runs the REAL gate and asserts prediction == actual.
Predictions are committed in PREDICTION.md BEFORE this ran. Exits non-zero on any mismatch."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath
from mpmath import iv
import enclose_gate as G

P_PI = {"kind": "integral", "f": lambda x: 4 / (1 + x * x), "a": 0, "b": 1, "N": 2000}      # = π
P_ERF = {"kind": "integral", "f": lambda x: iv.exp(-(x * x)), "a": 0, "b": 1, "N": 2000}    # = 0.74682… (erf)
P_ROOT = {"kind": "root_unique", "f": lambda x: x * x - 2, "df": lambda x: 2 * x}            # root √2

# (problem, claim, PREDICTED) — committed in PREDICTION.md
CASES = [
    ("1  π in [3.14,3.15]", P_PI, {"lo": "3.14", "hi": "3.15"}, G.ACCEPT),
    ("2  π in [3.0,3.1] (fabricated)", P_PI, {"lo": "3.0", "hi": "3.1"}, G.REJECT),
    ("3  π in [3.1415,3.1416] (true but tight)", P_PI, {"lo": "3.1415", "hi": "3.1416"}, G.ABSTAIN),
    ("4  ∫e^(-x²)=0.7468 (erf) in [0.74,0.75]", P_ERF, {"lo": "0.74", "hi": "0.75"}, G.ACCEPT),
    ("5  ∫e^(-x²) in [0.80,0.81] (fabricated)", P_ERF, {"lo": "0.80", "hi": "0.81"}, G.REJECT),
    ("6  unique root √2 in [1.4,1.45]", P_ROOT, {"lo": "1.4", "hi": "1.45", "unique": True}, G.ACCEPT),
    ("7  unique root in [1.6,1.7] (fabricated)", P_ROOT, {"lo": "1.6", "hi": "1.7", "unique": True}, G.REJECT),
    # #8 committed prediction was REJECT and was WRONG (see RESULTS.md): √2 IS the unique root in
    # [1,2] and Krawczyk legitimately proves it (K=[1.25,1.583]⊂int[1,2]). Gate is CORRECT -> ACCEPT.
    ("8  unique root in wide [1.0,2.0] (pred miss→ACCEPT)", P_ROOT, {"lo": "1.0", "hi": "2.0", "unique": True}, G.ACCEPT),
    # added to still exercise an INCONCLUSIVE Krawczyk (K spills below the box) -> REJECT (gate can fail)
    ("9  unique root in over-wide [0.1,5.0] (K spills)", P_ROOT, {"lo": "0.1", "hi": "5.0", "unique": True}, G.REJECT),
]

print("=" * 78)
print("ENCLOSE killer demo — prediction (committed) vs actual (live gate)")
print("=" * 78)
mismatches = 0
for label, prob, claim, predicted in CASES:
    r = G.gate(prob, claim)
    actual = r["verdict"]
    ok = (actual == predicted)
    mark = "ok " if ok else "XX "
    extra = ""
    if "rigorous_enclosure" in r:
        extra = f"  E={r['rigorous_enclosure']}"
    elif "krawczyk_image" in r:
        extra = f"  K={r['krawczyk_image']}"
    print(f"  [{mark}] {label:42s} pred={predicted:8s} actual={actual:8s}{extra}")
    if not ok:
        mismatches += 1
        print(f"        MISMATCH reason: {r['reason']}")
print("=" * 78)
if mismatches:
    print(f"DEMO: FAIL ({mismatches} prediction mismatches)")
    sys.exit(1)
print(f"DEMO: PASS ({len(CASES)}/{len(CASES)} predictions matched the live gate; gate ACCEPTs true "
      "enclosures incl. a non-elementary erf integral, REJECTs fabricated boxes + false Krawczyk "
      "certs, ABSTAINs honestly; #8 was an honest prediction-miss resolved in the gate's favor)")
