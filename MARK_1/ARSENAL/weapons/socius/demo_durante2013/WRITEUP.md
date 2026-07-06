# SOCIUS killer demo — Durante (2013) Study 1 religiosity: prediction vs result

**Finding under test:** Durante, Rae & Griskevicius (2013, *Psychological Science* 24:1007–1016),
Study 1 — a Fertility × Relationship-status interaction predicts women's religiosity. The
single-path analysis was significant and widely publicised ("the fluctuating female vote").

**Ground truth:** Steegen, Tuerlinckx, Gelman & Vanpaemel (2016, *Perspectives on Psychological
Science* 11:702–712) showed the religiosity effect is **fragile** — only **7 of 120**
specifications significant. We downloaded their raw data + R code (OSF zj68b), reimplemented the
multiverse in Python, and ran the full SOCIUS battery, **committing predictions before running**
(`PREDICTION.md`).

## Scorecard (5 of 6 committed predictions correct; 1 honest miss)

| # | Prediction | Result | Verdict |
|---|---|---|---|
| P1 | S-REPRO: exactly **120** valid specifications | **120** | ✅ correct |
| P2 | S-REPRO: **5–9** significant (reproduce Steegen's 7/120) | **7** (5.8%) | ✅ correct (exact) |
| P3 | S-MULTIVERSE: finding **DIES** (share sig ≪ 50%) | 5.8% sig → `robust=False` | ✅ correct |
| P4 | S-MEASURE: religiosity scale reliable, α > 0.80 | α = **0.92**, ω = **0.93** | ✅ correct |
| P5 | S-MEASURE: scale measurement-invariant across Single/Relationship (low conf.) | metric ✅ & scalar ✅ invariant (ΔCFI −0.0005/+0.0005) | ✅ correct |
| P6 | S-CAUSAL: single-path effect fragile to confounding (small E-value) | d = **−0.45**, **E-value = 2.39 > 2.0** → robust-to-confounding | ❌ **WRONG** |

**P6 — the honest miss (this is the method working).** I predicted the one significant path's
effect would be trivially explained by confounding (tiny E-value). It is not: among single women,
the High-vs-Low fertility religiosity gap is a *moderate* effect (d ≈ 0.45), giving an E-value of
2.39 — a confounder would need RR ≈ 2.4 with both fertility and religiosity to explain it away.
**So the dominant failure mode is analytic flexibility (S-MULTIVERSE), NOT confounding
(S-CAUSAL).** The finding dies because only ~6% of defensible analytic paths reach significance —
the one significant path is a real-sized but *cherry-picked* effect. The prediction was wrong in a
way that sharpens the diagnosis. (S-CAUSAL caveat: cycle phase is quasi-random, so the E-value's
confounding lens is a secondary concern here; reported for completeness and labelled κ=0.5.)

## A bug the box caught (independent machine-check > self-report)
The first S-MEASURE run flagged the religiosity scale as **non-invariant** — a **false positive**.
Inspecting the fit indices (not trusting the verifier's self-report) showed ΔCFI was ~0 (clearly
invariant) but the verdict was driven by a noisy **ΔRMSEA = 0.037 at df = 2**. RMSEA and its
difference are known to be unstable / over-rejecting at small degrees of freedom (Kenny, Kaniskan
& McCoach 2015). Fixed by making **ΔCFI the binding criterion** (Cheung & Rensvold 2002) and
treating ΔRMSEA as advisory when df < 10, with a regression-guard self-test added. The DIF
self-test (real non-invariance, df = 14/18) still fails on ΔCFI alone, so the fix did not blunt
the verifier.

## Bottom line
The Durante Study-1 religiosity finding **reproduces as a published artifact but does not survive
stress** — it is an artifact of one analytic path. SOCIUS raised trustworthiness (reproduced the
number, measured the scale, bounded confounding, flagged the sampling gap) and **reported the
finding that DIED as the primary output**. It did **not** manufacture truth: nothing here proves
the ovulation–religiosity hypothesis true or false in nature — only that *this dataset does not
robustly support it*. Reproduction ≠ discovery; robust ≠ true.
