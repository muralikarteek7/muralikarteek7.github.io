# TRIALGUARD — grounded method specifications (fetched, not asserted from memory)

*Produced by the grounding/survey pass 2026-06-20. Every load-bearing formula is backed by a fetched source
(Sources at end). The genuinely-new piece vs PSYMETRIX/SOCIUS is the **Carlisle baseline-anomaly test**; it is
grounded here **together with its documented critiques and false-positive modes** (the kickoff's non-negotiable
requirement — do NOT overstate the method). GRIM/GRIMMER (reused from `psymetrix/forensics_verify.py`),
repro/multiverse (reused from `socius/`) and meta (`psymetrix/psychometrics_verify.meta_analysis`) are grounded
in their own files; re-confirmed below.*

---

## 0. THE CARDINAL CAVEAT — in Carlisle's OWN words (fetched, primary source)

Carlisle (2017), the originator of the method, **explicitly states a statistical anomaly is NOT proof of fraud**:

> **"Fraud, unintentional error, correlation, stratified allocation and poor methodology might have contributed
> to the excess."** — Carlisle JB, *Anaesthesia* 2017;72(8):944–952 (PMID 28580651).

His analysis is presented as a **screen that flags patterns for investigation, not a verdict of misconduct**. He
lists, beside fabrication: **unintentional error, correlation between variables, stratified allocation, and poor
methodology**. TRIALGUARD encodes this list as the mandatory benign-explanation set attached to every flag.

---

## 1. Carlisle baseline-anomaly test (⭐ the new κ=1 slice) — the method

**Citation:** Carlisle JB. "Data fabrication and other reasons for non-random sampling in 5087 randomised,
controlled trials in anaesthetic and general medical journals." *Anaesthesia* 2017;72(8):944–952.
DOI 10.1111/anae.13938. (Earlier: Carlisle 2012, *Anaesthesia* 67:521–537, the Fujii/Saitoh analysis.)

**Per-variable p-value (CONTINUOUS variables only).** For a baseline continuous variable reported as
(mean₁, SD₁, n₁) vs (mean₂, SD₂, n₂), the between-group difference is tested with the (Welch) two-sample
statistic:

```
t = (mean₁ − mean₂) / sqrt( SD₁²/n₁ + SD₂²/n₂ )
```

converted to a **two-sided** p-value. (Carlisle used a normal/t comparison of the reported summary stats.)

**Combination across variables (Carlisle–Stouffer).** Under proper *simple* randomization, each two-sided
baseline p-value is i.i.d. **Uniform(0,1)**. Convert each to a normal deviate and combine with **Stouffer's
method**:

```
z_i = Φ⁻¹(p_i)              # p_i ~ U(0,1)  ⇒  z_i ~ N(0,1)
Z   = ( Σ z_i ) / sqrt(k)   # ~ N(0,1) under H0
```

- **Too-similar groups** (the fabrication/over-balance signature): means improbably close ⇒ large two-sided
  p-values (near 1) ⇒ z_i large **positive** ⇒ **Z large positive** (upper tail).
- **Too-different groups** (imbalance): p-values near 0 ⇒ z_i large **negative** ⇒ **Z large negative**.
- A **two-sided** test on Z (plus a **Kolmogorov–Smirnov** test of the p-values against U(0,1) and a Fisher
  combination as cross-checks) detects either departure. None of these is an accusation — only a departure of a
  *distribution* from uniformity.

This is exactly the **"Carlisle-Stouffer-Fisher"** family the appraisal paper names.

## 2. Carlisle test — DOCUMENTED FALSE-POSITIVE MODES & CRITIQUES (do not overstate)

Fetched from the appraisal (Bolland et al. 2017, PMID 28786843), the dichotomous-variable critique
(arXiv 2209.00131), and the continuous-vs-categorical study (Bolland 2019). **Every TRIALGUARD Carlisle output
must attach these:**

1. **UNSOUND for dichotomous/categorical variables.** The U(0,1) result holds for *continuous, ~normal,
   independent* variables; for categorical variables (χ²/Fisher on counts) the baseline p-value distribution is
   **not uniform** even under proper randomization (Bolland 2019: "uniform for continuous but **not** categorical
   variables"). **⇒ TRIALGUARD restricts the test to continuous variables and EXCLUDES categorical ones (reports
   them as excluded, never tests them).** Applying Carlisle to dichotomous variables is a known error
   (arXiv 2209.00131).
2. **Correlated baseline variables** (e.g. height & weight, age & comorbidity) violate the independence the
   combination assumes ⇒ **inflated false positives**. (Appraisal limitation #1; Bland.) The combined Z is
   anticonservative when variables are correlated.
3. **Stratified / minimized / block randomization** makes groups **more similar than simple randomization
   predicts** ⇒ excess high p-values ⇒ a spurious "too-similar" signal. **Carlisle himself EXCLUDED stratified
   variables from his analysis.** ⇒ TRIALGUARD excludes declared stratification factors and names stratification
   as the FIRST candidate explanation of any "too-similar" signal.
4. **Cluster randomization** alters the variance structure (design effect) ⇒ mis-calibrated p-values.
5. **Rounding / truncation** of reported means and SDs in Table 1 perturbs the computed p-values.
6. **Small k** (few baseline variables) ⇒ the within-trial combination is unreliable (appraisal limitation #6).
7. **Arbitrary cutoffs** for "extreme" (appraisal #3) — TRIALGUARD reports the exact statistic and a
   conventional threshold, never a binary fraud/no-fraud label.
8. **Not all baseline p-values are recomputable** from published summaries (appraisal #5) — abstain when inputs
   are insufficient.

**Honest framing baked in:** the test certifies *"the reported baseline summary statistics are (in)consistent
with the distribution expected under simple randomization."* A departure is an **anomaly with many benign
causes**, **never** a finding of misconduct.

## 3. Group-size / randomization-ratio consistency (κ=1, exact)

If a trial states an allocation ratio r:1 with total N analysed, the group sizes must be the integers nearest
N·r/(r+1) and N/(r+1) (±1 for rounding). A reported split far from the stated ratio is an **exact arithmetic
inconsistency** (candidate causes: dropout/exclusions after randomization, per-protocol vs ITT, typo). A
reported **percentage** p% of n must be achievable as an integer count `round(p·n/100)` back-rounding to p%
— the proportion analogue of GRIM. Exact, sound; flags are reported with benign causes, never as fraud.

## 4. GRIM / GRIMMER on reported clinical means (κ=1, REUSED)

Imported verbatim from `psymetrix/forensics_verify.py` (grounded in `psymetrix/GROUNDING.md`): a reported mean
of N integer responses can only equal k/(N·items); a reported SD has an integer sum-of-squares with forced
parity. A flag = "inconsistent with the stated N/scale," candidate causes rounding/typo/reporting error. **Exact
`Fraction` arithmetic — no float false positives.** Re-confirmed: GRIM 5.27/n=43 impossible; 5.26/43 consistent.

## 5. Survival — Kaplan–Meier + Cox PH partial likelihood (κ≈0.7, hand-rolled exact)

`lifelines` is absent, so TRIALGUARD **hand-rolls** KM and Cox from the formulas below and **cross-checks Cox
against `statsmodels.duration.hazard_regression.PHReg`** (an independent implementation) in the gate — agreement
of two independent computations is the verification, not either one's self-report.

**Kaplan–Meier** (Kaplan & Meier 1958, *JASA* 53:457–481): with distinct event times t_i, d_i events, n_i at
risk, `Ŝ(t) = Π_{t_i ≤ t} (1 − d_i/n_i)`. **Greenwood variance:**
`Var(Ŝ(t)) ≈ Ŝ(t)²·Σ d_i/(n_i(n_i−d_i))`.

**Cox PH partial likelihood** (Cox 1972, *JRSS-B* 34:187–220; ties: Breslow 1974, *Biometrics* 30:89–99):
```
ℓ(β) = Σ_{i:event} [ β·x_i − log Σ_{j∈R(t_i)} exp(β·x_j) ]      (Breslow: tied denom raised to #ties)
U(β) = Σ_{i:event} [ x_i − x̄_i(β) ],   x̄_i = Σ_R e^{βx_j}x_j / Σ_R e^{βx_j}
I(β) = Σ_{i:event} weighted-cov of x over R(t_i)
β ← β + I⁻¹U  (Newton–Raphson);   HR = exp(β),  SE(β) = sqrt(I(β̂)⁻¹)
```

## 6. Meta-analysis — pooling + heterogeneity + publication bias (κ≈0.6, REUSE + extend)

REUSE `psymetrix/psychometrics_verify.meta_analysis` (inverse-variance fixed effect; **DerSimonian–Laird**
random effects τ²; Cochran's Q; **I² = max(0,(Q−df)/Q)·100**; **Egger's** intercept test). **ADD trim-and-fill.**

- **Egger** (Egger et al. 1997, *BMJ* 315:629–634): regress (yᵢ/SEᵢ) on (1/SEᵢ); nonzero intercept ⇒ funnel
  asymmetry / small-study effects.
- **I²** (Higgins & Thompson 2002, *Stat Med* 21:1539–1558).
- **DerSimonian–Laird** τ² (1986, *Control Clin Trials* 7:177–188):
  `τ² = max(0, (Q−(k−1)) / (Σwᵢ − Σwᵢ²/Σwᵢ))`.
- **Trim-and-fill** (Duval & Tweedie 2000, *Biometrics* 56:455–463): rank-based estimate of "missing" studies
  (`L₀ = (4·Tₙ − k(k+1))/(2k−1)`, Tₙ = Wilcoxon positive-side rank sum), impute mirror-image studies, recompute
  the pooled effect. **Bias index = adjusted − observed pooled effect.** A correction, not a verdict.

## 7. Observational causal → sensitivity, never a bare causal claim (E-value)

**E-value** (VanderWeele & Ding 2017, *Ann Intern Med* 167(4):268–274, DOI 10.7326/M16-2607): for an observed
risk ratio RR≥1, `E = RR + sqrt(RR·(RR−1))` (invert RR<1); for the CI, apply to the limit nearest the null
(=1 if the CI crosses 1). Meaning: the minimum association an unmeasured confounder would need with **both**
treatment and outcome to explain away the result. TRIALGUARD inherits SOCIUS's S-CAUSAL rail: report the
E-value, **never a bare "X caused Y"** for observational data.

## Sources (URLs fetched 2026-06-20)
- Carlisle 2017 method — https://pubmed.ncbi.nlm.nih.gov/28580651/ ; Wiley https://onlinelibrary.wiley.com/doi/abs/10.1111/anae.13938
- Appraisal / critique (Bolland, Avenell, Gamble, Grey 2017) — https://pubmed.ncbi.nlm.nih.gov/28786843/
- Dichotomous-variable misuse critique — https://arxiv.org/pdf/2209.00131
- Continuous-vs-categorical uniformity (Bolland 2019) — https://www.sciencedirect.com/science/article/abs/pii/S0895435619302409
- Cox PH / Breslow ties — https://en.wikipedia.org/wiki/Proportional_hazards_model ; Breslow record https://pubmed.ncbi.nlm.nih.gov/4813387/
- Kaplan–Meier — https://en.wikipedia.org/wiki/Kaplan%E2%80%93Meier_estimator
- E-value — VanderWeele & Ding 2017 PDF https://hrr.w.uib.no/files/2019/01/VanderWeeleDing_2017_e_-value.pdf ; calculator https://www.evalue-calculator.com/evalue/
- Trim-and-fill — Stata metatrimfill https://www.stata.com/manuals/metametatrimfill.pdf ; metafor https://wviechtb.github.io/metafor/reference/trimfill.html ; Biometrics record https://academic.oup.com/biometrics/article-abstract/56/2/455/7263515
- Egger / I² / DL τ² — Egger 1997 *BMJ* 315:629; Higgins & Thompson 2002 *Stat Med* 21:1539; DerSimonian & Laird 1986 *Control Clin Trials* 7:177

## Honest grounding caveats
- Several primary PDFs (Carlisle 2017, the appraisal) sit behind paywalls; the method + its critiques are
  grounded in the fetched abstracts + the open-access arXiv critique + the canonical formula references, with
  the load-bearing arithmetic **independently ✓machine-verified** in the verifier self-tests (and Cox
  cross-checked against statsmodels PHReg). Carlisle's own anti-overclaim sentence (§0) is quoted from the
  fetched 2017 abstract.
- The Carlisle test's calibration (U(0,1) under simple randomization) is **only** valid for continuous,
  approximately-normal, **independent** baseline variables — TRIALGUARD enforces the continuous restriction and
  surfaces correlation/stratification as false-positive modes on every output rather than assuming them away.
