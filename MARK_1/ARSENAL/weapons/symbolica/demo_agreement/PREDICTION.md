# SYMBOLICA killer demo — COMMITTED PREDICTIONS (written BEFORE running)
*Box discipline: predictions frozen here before `run_demo.py` is executed. The machine
judge (the agreement gate) decides pass/fail. A prediction that fails is reported as failed.*

Each case is decided by **independent-method agreement**, not by one engine's output.

| # | case | mode | committed prediction | the independent methods that must agree |
|---|---|---|---|---|
| 1 | ∫₀^∞ e^(−x²) dx | CLOSED-FORM | verdict **CERTIFIED**, value = √π/2 ≈ 0.8862269254, ≥2 independent methods (incl. diversified DP/AP families) agree ≥30 digits | sympy.integrate · mpmath.quad (tanh-sinh) · scipy QUADPACK |
| 2 | Σ_{n≥1} 1/n² = ζ(2) | SERIES / SPECIAL-VALUE | verdict **CERTIFIED**, value = π²/6 ≈ 1.6449340668, convergence certified first; **labeled REPRODUCTION** of Basel | sympy.summation · mpmath.nsum · fetched reference π²/6 |
| 3 | sin(3x) = 3sin(x) − 4sin³(x) | IDENTITY-PROVE | verdict **CERTIFIED** with **"symbolically proven (simplify→0)"** label (unconditional collapse) + 20-pt numeric agreement | sympy.simplify→0 · mpmath 20-pt · series→0 |
| 4 | claim ∫₀^∞ e^(−x²) dx = √π (off by ×2) | CLOSED-FORM (adversarial) | verdict **REJECTED** — numeric methods disagree with the wrong claim | same as #1; the wrong value is caught |
| 5 | √(x²) = x sold as global identity | IDENTITY-PROVE (adversarial / branch-cut) | verdict **REJECTED** on domain (−3,3) — disagreement at x<0 (truth is \|x\|); **CERTIFIED** only when restricted to x>0 | mpmath multi-point across the full domain catches the off-domain disagreement |

## Predicted gate behaviour (the shared-blind-spot guard)
- Case 5 is the **diversified-method-matters** case: a series expansion about a positive
  point would wrongly "confirm" √(x²)=x (it's locally true on x>0); only **multi-point
  sampling across the full domain** catches the x<0 disagreement. The gate must REJECT.
- Every CERTIFIED value ships with: which methods agreed, how many digits, how many points.
- Case 2 must be **labeled a reproduction** (Basel is a known result), never an original find.

## What would falsify the weapon
- Any case 1–3 returning REJECTED, or case 4–5 returning CERTIFIED.
- A CERTIFIED label of "proven" on a merely-numeric agreement (case 1, 2 must NOT say "proven").
- Agreement reported on <2 independent methods.
