#!/usr/bin/env python3
"""SYMBOLICA killer demo runner — executes the 5 committed predictions in
PREDICTION.md through the FROZEN agreement gate and writes results.json.

The gate (not this script, not any single engine) is the judge. We only collect
its verdicts and compare them to the frozen predictions.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sympy as sp
import symbolica_gate as G

x = sp.Symbol('x', real=True)
n = sp.Symbol('n', positive=True, integer=True)

PREDICTIONS = {
    1: "CERTIFIED", 2: "CERTIFIED", 3: "CERTIFIED", 4: "REJECTED", 5: "REJECTED",
}

results = {}

# 1. Gaussian integral  ∫₀^∞ e^{−x²} dx = √π/2  (triple-method agreement)
results[1] = G.verify_definite_integral(sp.exp(-x**2), x, 0, sp.oo, sp.sqrt(sp.pi)/2)

# 2. Basel  Σ 1/n² = π²/6  (convergence-gated series) + reproduction label
results[2] = G.verify_series_closed_form(1/n**2, n, sp.pi**2/6, lo=1)
# cross-check the closed form against mpmath's INDEPENDENT zeta(2) implementation
import mpmath as mp
mp.mp.dps = 50
results["2_reproduction"] = G.verify_special_value(
    sp.pi**2/6, str(mp.nstr(mp.zeta(2), 45)),
    source="mpmath.zeta(2) independent special-function impl; closed form zeta(2)=pi^2/6 (Euler, Basel)")

# 3. triple-angle identity  sin(3x) = 3sin(x) − 4sin³(x)  (symbolic collapse expected)
results[3] = G.verify_identity(sp.sin(3*x), 3*sp.sin(x) - 4*sp.sin(x)**3, [x], domain=(-3, 3))

# 4. ADVERSARIAL: wrong closed form  ∫₀^∞ e^{−x²} dx = √π  (off by ×2) -> must REJECT
results[4] = G.verify_definite_integral(sp.exp(-x**2), x, 0, sp.oo, sp.sqrt(sp.pi))

# 5. ADVERSARIAL branch-cut: √(x²) = x sold as global -> REJECT; restricted x>0 -> CERTIFY
results[5] = G.verify_identity(sp.sqrt(x**2), x, [x], domain=(-3, 3))
results["5_restricted_pos"] = G.verify_identity(
    sp.sqrt(x**2), x, [x], domain=(sp.Rational(1, 10), 3))

# ---- compare to frozen predictions -----------------------------------------
print("=" * 76)
print("SYMBOLICA demo — verdicts vs FROZEN predictions (the gate is the judge)")
print("=" * 76)
passed = 0
summary = []
for k in (1, 2, 3, 4, 5):
    got = results[k]["verdict"]
    want = PREDICTIONS[k]
    ok = got == want
    passed += ok
    summary.append({"case": k, "predicted": want, "got": got, "pass": ok,
                    "label": results[k]["label"]})
    print(f"  case {k}: predicted {want:10s} got {got:10s}  {'PASS' if ok else '*** FAIL ***'}")
    print(f"          label: {results[k]['label']}")

# extra guarded checks (label honesty + reproduction + restricted-domain)
extra = []
# case 1 & 2 must NOT be labeled 'proven'
c1_ok = "proven" not in results[1]["label"].lower()
c3_proven = "proven" in results[3]["label"].lower()
repro_ok = results["2_reproduction"]["verdict"] == "REPRODUCED"
restricted_ok = results["5_restricted_pos"]["verdict"] == "CERTIFIED"
n_methods_1 = results[1]["n_independent_methods"] >= 2
extra = [
    ("case1 NOT labeled 'proven' (numeric-strong, not symbolic collapse)", c1_ok),
    ("case3 IS labeled 'proven' (unconditional symbolic collapse)", c3_proven),
    ("case2 reproduction matches fetched reference", repro_ok),
    ("case5 CERTIFIED only when restricted to x>0 sub-domain", restricted_ok),
    ("case1 agreement on >=2 independent methods", n_methods_1),
]
print("-" * 76)
for desc, ok in extra:
    passed += ok
    print(f"  EXTRA: {desc}: {'PASS' if ok else '*** FAIL ***'}")

total = 5 + len(extra)
print("=" * 76)
print(f"RESULT: {passed}/{total} committed predictions confirmed by the machine judge.")

out = {"predictions": PREDICTIONS, "summary": summary, "extra": extra,
       "passed": passed, "total": total, "results": {str(k): v for k, v in results.items()}}
def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, bool) or o is None or isinstance(o, (int, float, str)):
        return o
    return str(o)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"), "w") as fh:
    json.dump(_clean(out), fh, indent=2)
print("wrote results.json")
sys.exit(0 if passed == total else 1)
