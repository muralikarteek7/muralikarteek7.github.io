# ECONOMETRIX — GROUNDING (fetched sources, not asserted from memory)

*Every load-bearing formula below was FETCHED from a live source and cross-checked across ≥2
independent authorities (Opus generator + a Sonnet "Library" grounding agent, 2026-06-20). Where a
primary PDF returned binary, the formula was triangulated across ≥2 secondary authorities and an
internal-consistency check applied. Honest flags are kept at the bottom. No citation is fabricated.*

The frozen verifiers' `_selftest()`s anchor on the **published worked numbers** below — that is how we
machine-check that the implementation matches the source (the cap-set/SOCIUS doctrine: the machine, not
the model, carries the result).

---

## 1. Probabilistic Sharpe Ratio (PSR) and Deflated Sharpe Ratio (DSR) ⭐ (the C14-trap core)

**Citations.**
- Bailey, D. H., & López de Prado, M. (2012). "The Sharpe Ratio Efficient Frontier." *Journal of Risk*
  15(2): 3–44. (PSR introduced.)
- Bailey, D. H., & López de Prado, M. (2014). "The Deflated Sharpe Ratio: Correcting for Selection
  Bias, Backtest Overfitting, and Non-Normality." *Journal of Portfolio Management* 40(5): 94–107.

**PSR — exact formula (canonical Bailey–LdP convention).**
```
PSR(SR*) = Φ[ (SR̂ − SR*) · √(T − 1) / √( 1 − γ̂₃·SR̂ + ((γ̂₄ − 1)/4)·SR̂² ) ]
```
- `Φ` = standard-normal CDF.
- `SR̂` = **observed, NON-annualized** (per-period) Sharpe ratio of the returns.
- `SR*` = benchmark Sharpe being tested against (0 for plain PSR).
- `T` = number of return observations. Numerator uses **√(T−1)** (Bessel), confirmed.
- `γ̂₃` = **skewness** of the per-period returns (3rd standardized moment). Sign in denominator is **−**.
- `γ̂₄` = **kurtosis, NON-EXCESS** (normal ⇒ 3). Self-consistency: for normal returns `(γ̂₄−1)=2`, the
  denominator collapses to `√(1 + SR̂²/2)` — exactly the Lo (2002) Gaussian SR standard error. This
  reduction is the check that γ̂₄ is non-excess.
- The denominator uses the **OBSERVED** `SR̂` (it is the standard error of the SR estimator), **not** `SR*`.

**DSR — exact formula.** The Deflated Sharpe Ratio is the PSR with the benchmark set to the
**Expected Maximum Sharpe Ratio** SR₀ across the N trials that were searched (the multiple-testing
deflation):
```
DSR = PSR(SR₀)
SR₀ = √V · [ (1 − γ_E)·Φ⁻¹(1 − 1/N) + γ_E·Φ⁻¹(1 − 1/(N·e)) ]
```
- `V` = variance of the (per-period) Sharpe ratios across the N trials, `V[{SR̂ₙ}]`.
- `γ_E` ≈ 0.5772156649 = **Euler–Mascheroni** constant. `e` = Euler's number. `Φ⁻¹` = inverse normal CDF.
- `N` = number of independent trials (configs/rules) tried. This is the number that must NOT be
  under-counted — under-counting N inflates DSR (the classic cheat; the auditor checks this).
- Worked anchor (machine-checked in `backtest_verify._selftest`): for N=100, V=1.0, with
  `Φ⁻¹(0.99)=2.32635` and `Φ⁻¹(1−1/(100·e))=2.68021` (e=2.718281828), `SR₀ = 0.42278·2.32635 +
  0.57722·2.68021 = 2.5306`. *(An earlier draft of this note rounded the second term to 2.68158 / SR₀ to
  2.5316 using e≈2.71815 — a 4th-significant-digit annotation slip caught by the cross-model audit; the
  CODE always used `math.e` and is correct. Corrected here.)*

**⚠ Independence caveat (audit finding #5).** SR₀ assumes the N trials are approximately INDEPENDENT.
A grid of related rules on one asset (e.g. an SMA family) produces highly-correlated trial Sharpes ⇒
the raw variance `V[{SR̂ₙ}]` collapses toward 0 ⇒ SR₀→0 and the multiple-testing deflation VANISHES.
ECONOMETRIX guards this by **flooring V** at the Lo (2002) single-SR sampling variance
`(1 + ½·SR̂²)/(T−1)` whenever N>1 — so even a correlated grid keeps at least one Sharpe's worth of
deflation (it can only make the bar HARDER, never easier). The honest effective-N is still ≤ the raw N.

**⚠ One discrepancy resolved.** The Wikipedia "Deflated Sharpe ratio" page renders the DSR denominator
with `SR₀` inside the skew/kurtosis terms (`1 − γ̂₃·SR₀ + (γ̂₄−1)·SR₀²/4`). The **canonical Bailey–LdP
PSR** and the reference `mlfinlab` implementation both put the **observed SR̂** in that denominator (it
is the SE of the *estimator*, a function of the realized returns, not of the threshold). We implement
the canonical form (denominator uses observed SR̂). Documented so the choice is auditable.

**Decision rule used by ECONOMETRIX.** A backtest "edge" is reported ONLY if `DSR > 0.95` (the true SR
exceeds the multiple-testing-adjusted benchmark with ≥95% probability) AND the **walk-forward OOS**
Sharpe is positive net of costs. Else **ABSTAIN**. In-sample SR is never the verdict.

Sources: [Wikipedia: Deflated Sharpe ratio](https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio) ·
[SSRN 2460551 (DSR)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551) ·
[SSRN 1821643 (PSR / SR Efficient Frontier)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643) ·
[QuantConnect: PSR](https://www.quantconnect.com/research/17112/probabilistic-sharpe-ratio/).

---

## 2. Purged & Embargoed Cross-Validation (leakage control)

**Citation.** López de Prado, M. (2018). *Advances in Financial Machine Learning.* Wiley. Ch. 7,
"Cross-Validation in Finance" (§7.4 purging, §7.4.1 embargo).

- **The leakage problem.** Financial labels are functions of *future* data over an evaluation window;
  when a test label's window overlaps training observations, the training set is contaminated → inflated,
  non-reproducible OOS. Standard IID K-Fold assumes no such overlap and is over-optimistic in finance.
- **PURGING.** Remove from the TRAIN set any observation whose label-formation window **overlaps in
  time** with the test-set labels' windows.
- **EMBARGO.** Additionally drop a small buffer of training observations **immediately AFTER** each test
  fold (e.g. 1% of the series), to kill residual serial-correlation leakage that purging alone misses.
- **Walk-forward** (the simplest leakage-safe scheme, used in the trading arena): train on the past,
  test on the strictly-later unseen window; never let any test bar inform the params chosen for it.

Sources: [Wikipedia: Purged cross-validation](https://en.wikipedia.org/wiki/Purged_cross-validation) ·
[AFML TOC, ETH Library](https://toc.library.ethz.ch/objects/pdf03/e01_978-1-119-48208-6_01.pdf).

---

## 3. DiD parallel-trends / pre-trends test (E-CAUSAL)

**Citation.** Roth, J. (2022). "Pretest with Caution: Event-Study Estimates after Testing for Parallel
Trends." *American Economic Review: Insights* 4(3): 305–322.

- **Event-study test.** Estimate `Y_it = α_i + λ_t + Σ_{k≠−1} β_k·1{t−E_i=k} + ε_it` with the period
  before treatment (k=−1) as reference. **Pre-trends test** = joint (Wald/F) test that the
  **pre-treatment LEAD coefficients are jointly ≈ 0** (H₀: β_k=0 ∀ k<0). Pass ⇒ data are *consistent
  with* parallel pre-trends.
- **Caveats (non-waivable).** (a) **Low power** — naive tests miss economically meaningful violations.
  (b) **Pre-test distortion** — conditioning on "passed" distorts inference (Roth 2022). (c) **Parallel
  trends in the POST period is fundamentally untestable** — it is an assumption about an unseen
  counterfactual. ECONOMETRIX reports the pre-trends diagnostic AND a sensitivity number (E-value /
  Oster δ); it never emits a bare "X caused Y."

Source: [AEA: Roth (2022)](https://www.aeaweb.org/articles?id=10.1257%2Faeri.20210236).

---

## 4. McCrary (2008) density test (RDD manipulation)

**Citation.** McCrary, J. (2008). "Manipulation of the Running Variable in the Regression Discontinuity
Design: A Density Test." *Journal of Econometrics* 142(2): 698–714.

- **Tests** whether units sort/manipulate the running variable across the cutoff `c`. H₀: density of the
  running variable is **continuous at c** (no manipulation).
- **Statistic.** `θ̂ = log f̂⁺ − log f̂⁻` (log density just above minus just below c), asymptotically
  normal; test `T = θ̂ / SE(θ̂)`. Under H₀, **T ~ N(0,1)**; reject (⇒ manipulation) when **|T| > 1.96**
  (p<0.05).
- **Interpretation.** A significant discontinuity = evidence of sorting → the RD identifying assumption
  is threatened. (Modern best practice: Cattaneo–Jansson–Ma `rddensity`, one-bandwidth local-polynomial.)
- **⚠ Heteroscedasticity caveat (audit finding #4).** A running variable with materially different
  SPREAD on each side of the cutoff (e.g. income more dispersed above a means-test threshold) can
  produce a density slope-discontinuity that this test reads as "manipulation" even with NO sorting.
  ECONOMETRIX flags it: when `sd(left)/sd(right)` differs by >1.5×, a *detection* carries an explicit
  heteroscedasticity caveat in the verdict (and points to CJM `rddensity` as the more robust tool).

Sources: [EconPapers: McCrary 2008](https://econpapers.repec.org/RePEc:eee:econom:v:142:y:2008:i:2:p:698-714) ·
[MetricGate: McCrary density test](https://metricgate.com/docs/mccrary-density-test/).

---

## 5. Weak-instrument first-stage F / Stock–Yogo (IV)

**Citations.** Staiger, D., & Stock, J. H. (1997). "Instrumental Variables Regression with Weak
Instruments." *Econometrica* 65(3): 557–586. · Stock, J. H., & Yogo, M. (2005). "Testing for Weak
Instruments in Linear IV Regression," in *Identification and Inference for Econometric Models* (CUP).

- **First-stage F** tests joint significance of the **excluded instruments** in the first-stage
  regression (H₀: instruments unrelated to the endogenous regressor).
- **Rule of thumb (Staiger–Stock 1997): F < 10 ⇒ weak instruments.** Require **F > 10**.
- **Stock–Yogo (2005) critical values** (1 endogenous regressor, 1 instrument): 10% maximal IV size →
  **16.38**; 15% → 8.96; 20% → 6.66; 25% → 5.53. The popular F>10 ≈ the 15%-maximal-size criterion.
- **A weak first stage** ⇒ 2SLS biased toward OLS, non-normal sampling distribution, unreliable SEs,
  size-distorted Wald tests → IV results untrustworthy.
- **Honest modern note (kept, not hidden).** Lee–McCrary–Moreira–Porter (2022) and Olea–Pflueger (2013)
  argue the valid 5% threshold under homoskedasticity is far higher (F≈104.7) and that the
  heteroskedasticity-robust **effective F** should be used. ECONOMETRIX reports the classic F and flags
  the higher modern bar rather than treating F>10 as a clean pass.

Sources: [Stock–Yogo critical values (MetricGate)](https://metricgate.com/docs/weak-iv-stock-yogo-critical-values/) ·
[NBER t0284 (Stock–Yogo)](https://www.nber.org/system/files/working_papers/t0284/t0284.pdf) ·
[PMC5669336 (weak-IV review)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5669336/).

---

## 6. Oster (2019) δ — selection on unobservables (untestable-assumption sensitivity)

**Citation.** Oster, E. (2019). "Unobservable Selection and Coefficient Stability: Theory and Evidence."
*Journal of Business & Economic Statistics* 37(2): 187–204.

- **Three regressions.** Short (treatment only): coef `β̇`, R² `Ṙ`. Controlled: coef `β̃`, R² `R̃`.
  Hypothetical full (all confounders): R² `R_max`.
- **δ statistic** (proportional selection on unobservables vs observables needed to drive the effect to 0):
```
δ = β̃·(R_max − R̃) / [ (β̇ − β̃)·(R̃ − Ṙ) ]
```
- **Bias-adjusted effect** at a fixed δ (usually δ=1): `β* ≈ β̃ − δ·(β̇ − β̃)·(R_max − R̃)/(R̃ − Ṙ)`.
- **Rules of thumb.** **|δ| ≥ 1 ⇒ robust** (unobservables would have to be at least as important as the
  full observed control set to kill the effect). **|δ| < 1 ⇒ fragile.** Recommended **R_max = min(1.3·R̃, 1)**
  (the 1.3× is Oster's calibration from RCT-vs-observational R² movement; R_max=1 is most conservative).
- Note: Oster's exact β* is a cubic root; the linear approximation above is the standard reported form.

Sources: [Oster δ (MetricGate)](https://metricgate.com/docs/oster-delta/) ·
[Coefficient stability (bookdown)](https://bookdown.org/mike/data_analysis/coefficient-stability.html).

---

## 7. E-value (untestable-confounding sensitivity, REUSED from SOCIUS)

**Citation.** VanderWeele, T. J., & Ding, P. (2017). "Sensitivity Analysis in Observational Research:
Introducing the E-Value." *Annals of Internal Medicine* 167(4): 268–274.

- `E-value = RR + √(RR·(RR−1))` for RR≥1 (RR<1 ⇒ invert first). For a CI limit LL nearest the null:
  `E = 1` if LL crosses the null, else `LL + √(LL·(LL−1))`. Conversions: OR(common)→√OR; d→exp(0.91·d).
- Worked anchor (self-test): RR=3.9 ⇒ E=7.26.
- **REUSED** via `socius/eval_verify.py` (already self-tested + Sonnet-audited in SOCIUS). E-CAUSAL imports it.

---

## Honest flags (kept, per the rails)
- McCrary, Stock–Yogo, and Roth primary PDFs returned binary via fetch → formulas triangulated across
  ≥2 secondary authorities + internal consistency. Volumes/pages cross-checked against EconPapers/AEA/RePEc.
- The DSR denominator convention (observed SR̂ vs SR₀) is a real discrepancy in secondary sources; we
  implement the canonical Bailey–LdP / mlfinlab form and disclose it (§1).
- F>10 is the *classic* rule; the modern effective-F bar is far higher (§5) — reported, not buried.
- These are the SOTA *methods*; using them raises trustworthiness, it does not manufacture truth. A
  backtest is not a forecast; a causal diagnostic that passes is "consistent with," never "proves."
