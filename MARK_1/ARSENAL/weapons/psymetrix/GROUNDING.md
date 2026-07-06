# PSYMETRIX — grounded method specifications (fetched, not asserted from memory)

*Produced by the grounding/survey pass 2026-06-20. Every formula is backed by a fetched source (Sources at
end). Items marked ✓machine were recomputed and confirmed in-session. One sub-agent arithmetic error in the
GRIMMER example was caught by a machine recheck and corrected here.*

---

## 1. GRIM (Granularity-Related Inconsistency of Means)
**Citation:** Brown, N. J. L. & Heathers, J. A. J. (2017). "The GRIM Test…" *Social Psychological and
Personality Science* 8(4): 363–369. DOI: 10.1177/1948550616673876.

Given reported mean `x` to `D` decimals, sample size `N`, scale items `L`: `N_eff = N·L`; granularity
`G = 1/N_eff`. The reported mean is **consistent** iff some integer total `k` gives `k/N_eff` rounding (to `D`
decimals) to `x` — equivalently iff the interval `[x − 0.5·10^−D, x + 0.5·10^−D]` contains a multiple of
`1/N_eff`. Match neither neighbour → **inconsistent / impossible**.
- **Power:** `P(random mean flagged) = max(0, (10^D − N_eff)/10^D)`. When `N_eff ≥ 10^D` the test has **zero
  power** — report "no discriminating power," not "consistent."
- **Worked (✓machine):** mean=5.27, n=43, L=1 → **inconsistent** (226/43=5.2558→5.26, 227/43=5.2791→5.28;
  neither is 5.27). mean=5.90, n=40, L=3 (N_eff=120) → **consistent** (708/120=5.90 exactly).

## 2. GRIMMER (SD extension)
**Citation:** Anaya, J. (2016) *PeerJ Preprints* 4:e2400v1; analytic form = Allard (2018), as in R `scrutiny`.
Uses **sample variance (n−1)**. With GRIM sum `T = round(mean·n)`, `realmean = T/n`, the sum of squares
`SS = (n−1)·SD² + n·realmean²` must be an **integer in the SD-rounding band**
`[(n−1)·Lsig² + n·realmean², (n−1)·Usig² + n·realmean²]` (Lsig/Usig = SD ∓ 0.5·10^−dSD) that (Test 2)
reproduces the reported SD on back-rounding **and** (Test 3, parity) satisfies `SS ≡ T (mod 2)` (since
`x² ≡ x mod 2`). Fail any → **inconsistent**. Known bug: a Test-3-only failure is treated low-confidence.
- **Worked (✓machine):** n=18, mean=3.44, SD=2.47 → only integer `SS=317` reproduces SD 2.47, but 317 is odd
  while `T=62` is even → **parity mismatch → GRIMMER-inconsistent.**

## 3. SPRITE
**Citation:** Heathers, Anaya, van der Zee & Brown (2018) *PeerJ Preprints* 6:e26968v1. Reconstructs candidate
integer sample vectors (length N, in [min,max]) whose mean & SD round to the reported values, via
mean-preserving pair swaps. **Asymmetric:** a *found* vector is constructive proof of **possibility**; "not
found" by bounded search is **not** proof of impossibility. Runs GRIM+GRIMMER as deterministic prechecks first.

## 4. p-curve
**Citations:** Simonsohn, Nelson & Simmons (2014) *JEPG* 143(2):534–547, DOI 10.1037/a0033242; Simonsohn,
Simmons & Nelson (2015) "Better P-Curves," *JEPG* 144(6):1146–1152 (switched to **Stouffer** + half-curve).
Include only **significant** (p<.05) **focal** tests. **Right-skew (evidential value) test:** `pp = p/.05`;
Stouffer `Z = Σ Φ⁻¹(pp)/√k ~ N(0,1)`; evidential value if the **half**-curve (p<.025) right-skew test has
p<.05, OR **both** full & half have p<.1. Binomial test dichotomizes at **.025** vs uniform 50/50. The
**33%-power flatness** test needs the **noncentral** distribution per test statistic (df required), so it is
only run when test statistics + df are supplied; otherwise abstained.

## 5. TIVA (Test of Insufficient Variance)
**Citation:** Schimmack, Replicability-Index (2014); ref impl `nicebread/p-checker/TIVA.R`. p→z is
**one-tailed, directionally consistent:** `z = qnorm(p, lower.tail=FALSE)` (two-tailed input → halve first).
Expected `var(z)=1`. Statistic `χ² = (k−1)·var(z)`, `df=k−1`; decision is **lower-tail**
`pchisq(χ², df, lower.tail=TRUE)`; flag insufficient variance when p<.05. Conservative (heterogeneity inflates
variance → false negatives, not false positives).

## 6. Benford first-digit
**Citations:** Benford (1938); Hill (1995); Nigrini (2012). `P(d) = log₁₀(1+1/d)` (✓machine, sums to 1).
χ² GoF with **df=8**, α=.05 crit **15.507**. Nigrini first-digit **MAD** bands: ≤0.006 close, ≤0.012
acceptable, ≤0.015 marginal, **>0.015 nonconformity**. Screening tool, not proof. Needs data spanning several
orders of magnitude; exclude assigned/sequential numbers.

## 7. Implementation landscape
R is mature (`scrutiny` = GRIM/GRIMMER; `rsprite2` = SPRITE; `dmetar::pcurve`). Python is sparse: `grim`,
`benfordslaw`, `benford_py` exist; **no** Python SPRITE/p-curve/TIVA/scrutiny equivalent → PSYMETRIX
**hand-rolls all forensic verifiers from the formulas above** (each is short, exact arithmetic). This repo has
numpy/scipy/pandas/statsmodels; `factor_analyzer`/`semopy`/`pingouin`/`girth`/`sklearn` are ABSENT (so full
IRT/CFA/SEM is flagged → install-or-armor; dimensionality is done with numpy eigenvalues + parallel analysis).

## Top gotchas baked into the verifiers
1. TIVA p→z is **one-tailed** and the χ² test is **left-tail**; halve two-tailed inputs.
2. GRIMMER uses **(n−1)** variance and a **parity** check keyed to GRIM's integer sum.
3. GRIM/GRIMMER share `N_eff = N·L`; gate on `N_eff < 10^D` or report "no power."
4. p-curve right-skew `pp = p/.05`; 2015+ uses **Stouffer** + **half-curve** rule.
5. Benford df=8, crit 15.507; first-digit MAD cutoffs 0.006/0.012/0.015.

## Sources (URLs fetched)
- scrutiny GRIM/GRIMMER vignettes — https://lhdjung.github.io/scrutiny/articles/grim.html ,
  https://lhdjung.github.io/scrutiny/articles/grimmer.html
- Allard Analytic-GRIMMER — https://aurelienallard.netlify.app/post/anaytic-grimmer-possibility-standard-deviations/
- Wikipedia GRIM — https://en.wikipedia.org/wiki/GRIM_test
- SPRITE — https://peerj.com/preprints/26968/ ; rsprite2 — https://lukaswallrich.github.io/rsprite2/ ;
  pysprite — https://github.com/QuentinAndre/pysprite
- p-curve 2014 — https://pages.ucsd.edu/~cmckenzie/Simonsohnetal2014JEPGeneral.pdf ; "Better P-Curves" 2015 —
  https://urisohn.com/sohn_files/wp/wordpress/wp-content/uploads/2019/01/better-p-curves-published.pdf ;
  dmetar — https://dmetar.protectlab.org/reference/pcurve
- TIVA — https://replicationindex.com/2014/12/30/tiva/ ; code https://raw.githubusercontent.com/nicebread/p-checker/master/TIVA.R
- Benford — https://en.wikipedia.org/wiki/Benford%27s_law ; https://www.metricgate.com/docs/benford-law-analysis

## Honest grounding caveats
- Primary PDFs of GRIM (2017), GRIMMER (2016), SPRITE (2018) returned 403; their algorithms are grounded in the
  canonical *implementations* (scrutiny, rsprite2, Allard) + Wikipedia, with DOIs search-verified. The
  load-bearing arithmetic is independently ✓machine-verified in the verifier self-tests.
- The p-curve 33%-power noncentral mechanism is grounded but its worked pp-values were not independently
  recomputed; PSYMETRIX therefore runs the exact right-skew (evidential-value) test by default and abstains on
  the 33%-power test unless test statistics+df are supplied.
