# P-REPRO + P-MULTIVERSE demo PREDICTIONS — committed BEFORE running (2026-06-20)

Dataset: **Fair's Affairs (Fair 1978, "A Theory of Extramarital Affairs", J. Polit. Econ.)** — ships in
statsmodels (`sm.datasets.fair`), 6366 respondents, real survey data on extramarital affairs with predictors
(rate_marriage, age, yrs_married, children, religious, educ, occupation). Public, well-documented, non-accusatory.

Focal effect: **does religiousness predict (lower) probability of having an affair?** This is a documented
finding (Fair 1978; reproduced across the econometrics literature). Outcome operationalized as `any_affair`
(affairs > 0).

This demo is the counterpoint to SOCIUS's Durante demo (which DIED in the multiverse): I expect a **robust**
effect here, to show PSYMETRIX certifies robustness honestly in both directions.

## Committed predictions
1. **P-REPRO (dual-path):** the focal logit coefficient for `religious` (with the standard covariate set) is
   reproduced by two independent computations (statsmodels GLM + a hand-rolled numpy IRLS) agreeing to < 1e-4.
   Predicted coefficient ≈ **−0.37 to −0.38**, p < .001 (negative: more religious → less likely to have an affair).
2. **P-MULTIVERSE robustness:** across the multiverse of analytic forks — covariate subsets (age, yrs_married,
   children, educ, occupation) × outcome operationalizations (any-affair vs frequent-affair) × sample exclusions
   (full vs married >1yr) — I predict the `religious` effect is **ROBUST**: **negative in ≥95% of specs** and
   **significant (p<.05) in ≥50%** of specs. Verdict: "robust".
3. **Median coefficient** across the multiverse: negative, in the **−0.25 to −0.45** band.
4. **p-curve of the significant specs:** evidential value present (right-skewed) — the significant specs are not
   just noise. (Flagged lower-confidence: multiverse specs are non-independent, so p-curve here is illustrative.)
5. **Contrast control — rate_marriage:** as a sanity check I also expect `rate_marriage` (marital happiness) to
   be an even stronger robust negative predictor than religiousness.

## Falsifiers
- Dual-path coefficients disagree (>1e-4) → reproduction bug.
- The religious effect comes out "fragile" (<10% specs significant) → either the effect isn't robust (honest
  negative, report it) or a multiverse bug.
- Reproduced coefficient far from −0.37 → spec/repro error.

## Honesty note
A "robust" verdict means the effect is **not an artifact of the analytic choices tested** — it does NOT prove
the effect is causal or true (this is observational survey data; religiousness is confounded with many things).
Robust ≠ true. The verifier certifies robustness, not truth.
