# PSYMETRIX — a κ-aware Psychometric & Statistical Rigor Engine (v5 weapon SPEC)

*Spec stamped 2026-06-20. Sibling of SOCIUS; quant-psych is **higher-κ** than sociology, so PSYMETRIX has a
larger executable core and one genuinely sharp **EXACT** offensive piece: statistical forensics. Grounding for
every method is in [`GROUNDING.md`](GROUNDING.md) (fetched sources, not memory).*

## 0. One line
PSYMETRIX reads a quantitative-psychology task, routes each claim by **κ** (checkability), draws the matching
frozen verifiers where κ>0, and grounds-or-abstains where κ=0. It **certifies CONSISTENCY / FIT / ROBUSTNESS,
never TRUTH.** Its sharpest end (forensics) can **mathematically prove** that reported summary statistics are
**impossible** for the stated N and scale — the social sciences' closest analogue to the cap-set verifier.

## 1. The κ-profile (defines the weapon)
- **κ = 1 (EXACT, non-gameable) — the sharp end:** *statistical forensics.* GRIM / GRIMMER / SPRITE / TIVA /
  p-curve / Benford. The arithmetic is exact: a reported mean of N integer responses can only take values
  `k/(N·items)`; a reported SD has an integer sum-of-squares with a forced parity. When the reported number is
  not achievable, that is a **proof of inconsistency**, not a judgment.
- **κ = 1 (executable):** reliability (Cronbach α), **disattenuation** (a corrected r>1 is an exact
  impossibility certificate), dimensionality (eigenvalue / parallel analysis), **Mantel–Haenszel DIF** (exact
  2×J table arithmetic), meta-analysis (fixed/random pooling + Egger funnel-asymmetry), **power & optimal item
  selection** (max test information — a real constructive optimization with an exact objective).
- **κ = 0 (armor only):** what a construct *means*, theory choice, construct-validity *interpretation* → ground
  against a fetched source or ABSTAIN. Never presented as machine-verified.

## 2. Sub-weapon registry (frozen verifier built + adversarially self-tested for each κ>0 piece)
| sub-weapon | fires when | κ | module | what the frozen verifier certifies |
|---|---|---|---|---|
| **P-FORENSICS** ⭐ | reported summary stats on bounded/integer scales; a body of p-values | **1 (EXACT)** | `forensics_verify.py` | GRIM/GRIMMER mean–SD–N consistency (exact); SPRITE witness (constructive possibility); TIVA; p-curve evidential value; Benford |
| **P-RELIABILITY** | a scale / difference score / corrected correlation | 1 | `psychometrics_verify.py` | Cronbach α; disattenuated r (**r>1 ⇒ exact inconsistency certificate**) |
| **P-MODEL** | latent construct, item-level data | 1 | `model_verify.py` | **full CFA/SEM fit** (semopy: CFI/TLI/RMSEA/SRMR + per-index tiers & a "mixed"=disagreement verdict) · **model comparison** (the discriminating test) · EFA dimensionality (Kaiser + Glorfeld-95 parallel analysis) · McDonald ω vs α · **IRT 2PL** (girth: item params + test information + SE(θ)) · Yen's Q3 local dependence. Guarded by Bartlett's sphericity (non-factorable data → abstain) |
| **P-REPRO** | a published effect with open data | 1 | `repro_multiverse_verify.py` | re-computes the statistic **two independent ways** (statsmodels + numpy IRLS/OLS) → reproduction certificate |
| **P-MULTIVERSE** | a finding resting on analytic choices | 1 | `repro_multiverse_verify.py` | specification curve over the analytic forks → robust / fragile / mixed (+ effect-size spread, p-curve, OVB & large-n caveats) |
| **P-DIF** | scores compared across groups | 1 | `psychometrics_verify.py` | Mantel–Haenszel DIF χ²/Δ (exact); flags items functioning differently across groups |
| **P-META** | a body of findings | 1 | `psychometrics_verify.py` | fixed/random-effects pooled effect; Egger's test for funnel asymmetry (pub-bias) |
| **P-DESIGN** | designing/evaluating a study | 1 | `psychometrics_verify.py` | a-priori power (t / r, noncentral); **optimal item selection = argmax test information** (constructive) |
| **P-GROUND** | interpretive/theoretical claims | armor | router → armor | fetch real source + entailment, else ABSTAIN |

## 3. Routing (the chooser)
`psymetrix_router.py` classifies a task's claims (forensic / measurement / reliability / DIF / effect-repro /
design / meta / interpretive) → draws the matching κ>0 sub-weapons → κ=0 residue → ARMOR. Every routed piece is
labelled with its κ so nothing κ=0 is ever presented as machine-verified.

## 4. The killer demo (prediction committed BEFORE running — see `demo_forensics/PREDICTION.md`)
The sharp one: run **P-FORENSICS** on (a) the method papers' **own published worked examples** (real reported
statistics the authors themselves put forward — grounded, non-accusatory) and (b) a **controlled ground-truth
corpus** built from real integer samples (we know the true mean/SD), measuring the verifier's **exact
sensitivity/specificity** on consistent vs. typo-corrupted reports. A GRIM-impossible mean **must** be flagged;
a consistent one **must** pass. Paired with a reliability/disattenuation impossibility check.

## 5. Honesty rails (non-waivable)
1. **INCONSISTENCY ≠ FRAUD.** GRIM/SPRITE flag *mathematical inconsistency* — possibly rounding, typo, or
   reporting error. Report "the reported statistics are inconsistent with the stated N/scale" **with the exact
   arithmetic, and stop.** Never accuse. Real reputations are at stake.
2. **Fit ≠ truth; consistent ≠ correct; robust ≠ true.** State what was and was not certified.
3. **κ-honesty:** label each output by κ; never present a κ=0 judgment as machine-verified.
4. **No fabricated stats/citations.** Every datum and source real and fetched.
5. **Abstain** where neither a check nor grounding exists; abstention is a scored deliverable.
6. **SPRITE asymmetry:** a *found* sample proves possibility (constructive); *not found* by search is **not**
   proof of impossibility — only GRIM/GRIMMER give exact impossibility certificates.

## 6. Ceiling (stated every time)
PSYMETRIX certifies **consistency / fit / robustness**, not **truth**. A model that fits is not "the right
theory." A GRIM-consistent number is not "correct." A statistic that survives the multiverse is not "true." And
an inconsistency is a *mathematical fact about the reported numbers*, never an accusation about the people.
