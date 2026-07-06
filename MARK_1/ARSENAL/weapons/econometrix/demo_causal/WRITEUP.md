# RESULT — the E-CAUSAL pre-trends / placebo demo

*Run `python3 demo_run.py`. Compares the committed `PREDICTION.md` against the machine result.*

## What ran
Two difference-in-differences panels (synthetic, KNOWN ground truth, honestly labelled — NOT a
reproduction of a published number; that is the separate E-REPRO piece below), plus an Oster δ
sensitivity and a real published-number reproduction.

## Result
**Scenario A — CLEAN** (true effect +3.0, parallel pre-trends):
- pre-trends placebo **p = 0.492 → parallel-trends plausible = True** (PASS)
- recovered post effect **= 3.38** (true 3.0); Cohen d = 1.53; **E-value = 7.49** (sensitivity number)

**Scenario B — CONFOUNDED** (NO true effect, divergent pre-trend):
- naive 2×2 DiD **= +3.76 (p = 4.8e-31)** — a naive analyst would call this a "significant effect"
- pre-trends placebo **p = 1.1e-53 → parallel-trends plausible = False**
- **==> ECONOMETRIX FLAGS the design: the confound is CAUGHT, not laundered into a causal effect.**

This is the causal "dies under stress": a confounded correlation that looks overwhelmingly significant
(p≈1e-31) is **killed by the pre-trends placebo**. The testable assumption fails → the design is flagged.

**Oster δ** (selection-on-unobservables sensitivity for the UNtestable assumptions):
- robust design: **δ = 12.46 → robust = True** (unobservables must be ≥12× as important as observables)
- fragile design: **δ = 0.43 → robust = False** (modest unobserved selection could kill the effect)

**E-REPRO — Card & Krueger (1994)** minimum-wage DiD (a REAL published number, means grounded by fetch —
NJ 20.44→21.03, PA 23.33→21.17): recomputed DiD **= +2.75 FTE** reproduces the **published +2.76**
within tolerance (|diff| = 0.010). Labelled reproduction; 2-period design ⇒ pre-trends untestable here.

## Predictions vs result (committed before running)
| # | prediction | outcome |
|---|---|---|
| C1 | Scenario A pre-trends PASS (p > 0.05) | ✅ p = 0.492 |
| C2 | Scenario A effect recovered ≈ +3.0 (±0.5) | ✅ 3.38 |
| C3 | Scenario B pre-trends FAIL (p < 0.01) → FLAGGED | ✅ p = 1.1e-53 |
| C4 | a naive DiD would report a "significant effect" in B | ✅ +3.76, p = 4.8e-31 |
| C5 | Oster δ robust ≥ 1, fragile < 1 | ✅ 12.46 / 0.43 |
| C6 | E-value on clean effect > 2 | ✅ 7.49 |
| C7 | directions hold even if point values differ | ✅ |

**7/7 committed predictions correct.**

## Honest ceiling (binding)
Passing pre-trends is **necessary, not sufficient** — post-period parallel trends is fundamentally
untestable (Roth 2022). ECONOMETRIX reports the testable diagnostic AND a sensitivity number, and
**NEVER emits a bare "the treatment caused the outcome."** A FLAGGED design is the valuable output: it
stops a confounded correlation from being sold as a causal effect. Reproduction is labelled reproduction.
