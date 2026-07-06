# ENCLOSE — killer-demo RESULTS (live gate, 2026-06-20)

Run: `python3 demos/run_demo.py` → **PASS**. Predictions committed in `PREDICTION.md` *before* the run.

| # | problem | claim | predicted | actual | match |
|---|---------|-------|-----------|--------|-------|
| 1 | ∫₀¹ 4/(1+x²) (=π) | [3.14,3.15] | ACCEPT | ACCEPT | ✅ |
| 2 | ∫₀¹ 4/(1+x²) | [3.0,3.1] (fab.) | REJECT | REJECT | ✅ |
| 3 | ∫₀¹ 4/(1+x²) | [3.1415,3.1416] (tight) | ABSTAIN | ABSTAIN | ✅ |
| 4 | ∫₀¹ e^(−x²) (=0.7468, erf) | [0.74,0.75] | ACCEPT | ACCEPT | ✅ |
| 5 | ∫₀¹ e^(−x²) | [0.80,0.81] (fab.) | REJECT | REJECT | ✅ |
| 6 | unique root x²−2 in [1.4,1.45] (√2) | unique | ACCEPT | ACCEPT | ✅ |
| 7 | unique root in [1.6,1.7] (fab.) | unique | REJECT | REJECT | ✅ |
| 8 | unique root in wide [1.0,2.0] | unique | ~~REJECT~~ | ACCEPT | ⚠️ **prediction MISS** |
| 9 | unique root in over-wide [0.1,5.0] | unique | REJECT | REJECT | ✅ |

## The honest prediction miss (#8) — recorded, not hidden

I committed **REJECT** for "unique root of x²−2 in `[1.0,2.0]`", guessing Krawczyk would be inconclusive on
a width-1 box. **That prediction was WRONG, and the gate was RIGHT.** √2 ≈ 1.41421 genuinely *is* the unique
root of x²−2 in [1,2] (the other root −√2 lies outside), and the Krawczyk operator legitimately proves it:
`K(X) = [1.250, 1.583] ⊂ int([1.0, 2.0])`, so existence + uniqueness hold. I had underestimated Krawczyk's
contraction strength on a well-conditioned f.

**What I did:** verified independently that √2 is the unique root in [1,2] (trivially: x²=2 ⇒ x=±√2, only +√2
in range) → the gate's ACCEPT is correct → updated the runner's regression expectation to ACCEPT **with this
note**, and added case #9 (`[0.1,5.0]`, where `K=[−0.687,4.02]` spills below the box → REJECT) so the demo
still exercises a genuine Krawczyk failure. The committed `PREDICTION.md` is left intact as the honest record
of the miss. **This is the box working as intended: a committed prediction was falsifiable, got falsified,
and the discrepancy resolved in the gate's favor by an independent check — not by retrofitting the prediction.**

## What the demo establishes
- ENCLOSE ACCEPTs a true enclosure, **REJECTs a fabricated one** (it can FAIL — cases 2, 5, 7, 9),
  and ABSTAINs honestly when it cannot independently prove a true-but-tight claim (case 3).
- It certifies a **non-elementary integral** (∫e^(−x²), an erf value with no elementary closed form) by
  containment proof — the regime where SYMBOLICA's symbolic leg has no answer.
- κ=1 under mpmath.iv software directed rounding; certifies the computed quantity, not the model (κ=0).
- Every ACCEPT's rigorous enclosure brackets an INDEPENDENT high-precision reference (`selftest_all.py` (e)).
