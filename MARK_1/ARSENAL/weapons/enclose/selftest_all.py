#!/usr/bin/env python3
"""ENCLOSE gate-of-the-gate — non-waivable self-tests. Exits non-zero on ANY failure.

A verifier that cannot FAIL is not a verifier. These prove the ENCLOSE gate:
  (a) ACCEPTs a genuinely-true, independently-provable enclosure / a Krawczyk-unique root,
  (b) REJECTs a FALSE enclosure (claim provably disjoint from the rigorous enclosure) and a
      FALSE Krawczyk cert (asserted unique root in a box where the test fails),
  (c) ABSTAINs (never ACCEPTs) on a true-but-not-independently-provable tight claim, and on
      malformed input (lo>hi, NaN, f'∋0, unknown kind, missing bounds),
  (d) raises NO false alarm on known-good enclosures,
  (e) SOUNDNESS INVARIANT: every ACCEPT genuinely contains the truth (ACCEPT ⟺ E⊆claim, and the
      rigorous enclosure E provably contains the true value), spot-checked against high-precision
      reference values from an INDEPENDENT computation (mpmath.mp, not the iv recompute).
"""
import sys
import mpmath
from mpmath import iv, mpf, mp
import enclose_gate as G

FAILS = []


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} :: {detail}")
        FAILS.append(name)


# ---- problems (how the gate INDEPENDENTLY recomputes; never reads the claim) ----
P_INT_PI = {"kind": "integral", "f": lambda x: 4 / (1 + x * x), "a": 0, "b": 1, "N": 2000}      # = π
P_INT_E = {"kind": "integral", "f": lambda x: iv.exp(x), "a": 0, "b": 1, "N": 2000}             # = e-1
P_SQRT2 = {"kind": "enclosure", "value": lambda: iv.sqrt(2)}                                     # = √2
P_ROOT2 = {"kind": "root_unique", "f": lambda x: x * x - 2, "df": lambda x: 2 * x}               # root √2
P_BADDF = {"kind": "root_unique", "f": lambda x: x * x - 2, "df": lambda x: 2 * x}               # f'∋0 on [-1,1]


def V(problem, claim):
    return G.gate(problem, claim)["verdict"]


print("=" * 78)
print("ENCLOSE gate-of-the-gate self-tests")
print("=" * 78)

# (a) ACCEPT genuinely-true, independently-provable enclosures
check("(a1) ∫4/(1+x²)=π in [3.14,3.15] -> ACCEPT", V(P_INT_PI, {"lo": "3.14", "hi": "3.15"}) == G.ACCEPT)
check("(a2) ∫e^x=e-1 in [1.71,1.72] -> ACCEPT", V(P_INT_E, {"lo": "1.71", "hi": "1.72"}) == G.ACCEPT)
check("(a3) √2 in [1.41,1.415] -> ACCEPT", V(P_SQRT2, {"lo": "1.41", "hi": "1.415"}) == G.ACCEPT)
check("(a4) unique root of x²-2 in [1.4,1.45] -> ACCEPT (Krawczyk)",
      V(P_ROOT2, {"lo": "1.4", "hi": "1.45", "unique": True}) == G.ACCEPT)

# (b) REJECT false enclosures (provably disjoint) + false Krawczyk certs
check("(b1) FALSE: π claimed in [3.0,3.1] (excludes π) -> REJECT",
      V(P_INT_PI, {"lo": "3.0", "hi": "3.1"}) == G.REJECT)
check("(b2) FALSE: √2 claimed in [1.5,1.6] (excludes √2) -> REJECT",
      V(P_SQRT2, {"lo": "1.5", "hi": "1.6"}) == G.REJECT)
check("(b3) FALSE: e-1 claimed in [2.0,2.1] (excludes e-1) -> REJECT",
      V(P_INT_E, {"lo": "2.0", "hi": "2.1"}) == G.REJECT)
check("(b4) FALSE Krawczyk: 'unique root in [1.6,1.7]' (no root there) -> REJECT",
      V(P_ROOT2, {"lo": "1.6", "hi": "1.7", "unique": True}) == G.REJECT)

# (c) ABSTAIN (never ACCEPT) on true-but-not-provable + malformed
check("(c1) true-but-too-tight: π in [3.1415,3.1416] (E wider than claim) -> ABSTAIN",
      V(P_INT_PI, {"lo": "3.1415", "hi": "3.1416"}) == G.ABSTAIN)
check("(c2) malformed lo>hi -> ABSTAIN", V(P_SQRT2, {"lo": "2", "hi": "1"}) == G.ABSTAIN)
check("(c3) malformed NaN bound -> ABSTAIN", V(P_SQRT2, {"lo": "nan", "hi": "2"}) == G.ABSTAIN)
check("(c4) missing bounds -> ABSTAIN", V(P_SQRT2, {}) == G.ABSTAIN)
check("(c5) Krawczyk f'∋0 on [-1,1] -> ABSTAIN",
      V(P_BADDF, {"lo": "-1", "hi": "1", "unique": True}) == G.ABSTAIN)
check("(c6) unknown problem kind -> ABSTAIN", V({"kind": "bogus"}, {"lo": "0", "hi": "1"}) == G.ABSTAIN)
# (c8) AUDIT #2 GUARD: a footgun integrand evaluated in NON-interval arithmetic (math.exp) breaks the
# inclusion property -> the gate must ABSTAIN, never build an unsound enclosure and ACCEPT.
import math as _math
P_FOOTGUN = {"kind": "integral", "f": lambda x: _math.exp(x), "a": 0, "b": 1, "N": 100}
check("(c8) non-iv integrand (math.exp) -> ABSTAIN (inclusion property not guaranteed)",
      V(P_FOOTGUN, {"lo": "1.71", "hi": "1.72"}) == G.ABSTAIN)
# (c9) AUDIT #3: kappa reflects verdict determinacy — ACCEPT/REJECT are κ=1, ABSTAIN is κ=0.
check("(c9) ACCEPT carries kappa=1", G.gate(P_INT_PI, {"lo": "3.14", "hi": "3.15"})["kappa"] == 1)
check("(c9) REJECT carries kappa=1", G.gate(P_INT_PI, {"lo": "3.0", "hi": "3.1"})["kappa"] == 1)
check("(c9) ABSTAIN carries kappa=0 (undetermined, not proof)",
      G.gate(P_INT_PI, {"lo": "3.1415", "hi": "3.1416"})["kappa"] == 0)

# (c7) the cardinal NON-falsifiability: a claim that is a STRICT SUBSET of E but excludes the truth
#      must ABSTAIN (the gate cannot prove disjointness), NEVER falsely REJECT a possibly-true claim
#      and NEVER ACCEPT. [3.1410,3.1414] ⊂ E≈[3.141,3.142], excludes π=3.14159 -> ABSTAIN.
check("(c7) sub-E claim excluding π [3.1410,3.1414] -> ABSTAIN (not REJECT, not ACCEPT)",
      V(P_INT_PI, {"lo": "3.1410", "hi": "3.1414"}) == G.ABSTAIN)

# (e) SOUNDNESS INVARIANT — every ACCEPT's rigorous enclosure E genuinely brackets an INDEPENDENT
#     high-precision reference (mpmath.mp, computed a different way than the iv recompute).
mp.dps = 50
refs = [
    ("π", P_INT_PI, mpmath.pi),
    ("e-1", P_INT_E, mpmath.e - 1),
    ("√2", P_SQRT2, mpmath.sqrt(2)),
]
for name, prob, ref in refs:
    r = G.gate(prob, {"lo": "0", "hi": "1000"})   # a deliberately huge box -> ACCEPT, exposes E
    lo_s, hi_s = r["rigorous_enclosure"]
    elo, ehi = mpf(lo_s), mpf(hi_s)
    contains = elo <= ref <= ehi
    check(f"(e:{name}) rigorous enclosure E=[{lo_s},{hi_s}] brackets independent ref {mpmath.nstr(ref,12)}",
          contains, f"ref {ref} not in [{elo},{ehi}]")

# (e2) the structural guarantee in action: an ACCEPT can ONLY happen when E ⊆ claim. Verify the gate
#      refuses to ACCEPT any box that does not contain its own recomputed E (probe a grid).
mp.dps = 30
import enclose_gate as _g
_g._set_prec(30)
E = _g.verified_integral(P_INT_PI["f"], 0, 1, 2000)
elo, ehi = mpf(E.a), mpf(E.b)
# a box that contains E -> ACCEPT; nudge either endpoint inside E -> must NOT be ACCEPT
acc = V(P_INT_PI, {"lo": str(elo - mpf("0.001")), "hi": str(ehi + mpf("0.001"))})
narrow_hi = V(P_INT_PI, {"lo": str(elo - mpf("0.001")), "hi": str((elo + ehi) / 2)})  # cuts E in half
check("(e2a) box ⊇ E -> ACCEPT", acc == G.ACCEPT)
check("(e2b) box cutting E (⊉ E) -> NOT ACCEPT", narrow_hi != G.ACCEPT, f"got {narrow_hi}")

print("=" * 78)
if FAILS:
    print(f"GATE: FAIL ({len(FAILS)} failed: {FAILS})")
    sys.exit(1)
print("GATE: ENCLOSE accepts true/provable enclosures + Krawczyk-unique roots; REJECTs false "
      "(disjoint) enclosures + false certs; ABSTAINs on too-tight + malformed; every ACCEPT's "
      "enclosure brackets an independent high-precision reference (soundness invariant holds). OK.")
