# PSYMETRIX — κ-aware Psychometric & Statistical Rigor Engine

A registered **v5 weapon** for **quantitative psychology**. Sibling of SOCIUS, but quant-psych is
**higher-κ** (more is machine-checkable), so PSYMETRIX has a **large executable core** and one genuinely
**sharp EXACT** offensive piece: **statistical forensics**.

## What it is
Given a quant-psych task, PSYMETRIX **routes each claim by κ** (checkability), draws the matching frozen
verifiers where κ>0, and grounds-or-abstains where κ=0. Its sharp end can **mathematically PROVE that reported
summary statistics are impossible** for the stated N and scale — the social sciences' closest analogue to the
cap-set verifier (an exact certificate, not a judgment).

## The honest ceiling (stated every time)
**PSYMETRIX certifies CONSISTENCY / FIT / ROBUSTNESS, never TRUTH.** A model that fits is not "the right
theory"; a GRIM-consistent number is not "correct"; an effect that survives the multiverse is not "true."

## ⚠ The non-waivable rail: INCONSISTENCY ≠ FRAUD
GRIM/GRIMMER/SPRITE flag **mathematical inconsistency**, which can be **rounding, a typo, or a reporting
error**. PSYMETRIX reports *"the reported statistics are inconsistent with the stated N/scale"* **with the
exact arithmetic, and stops.** It **never accuses.** Real reputations are at stake. Every flagged output names
rounding/typo/reporting error as possible explanations; the router appends this ceiling to every plan.

## Sub-weapons
| module | sub-weapon | κ | certifies |
|---|---|---|---|
| `forensics_verify.py` ⭐ | **P-FORENSICS** | **1 (EXACT)** | GRIM/GRIMMER mean–SD–N consistency (exact); SPRITE witness; TIVA; p-curve evidential value; Benford |
| `psychometrics_verify.py` | P-RELIABILITY | 1 | Cronbach α; **disattenuated r>1 = exact inconsistency cert** |
| `model_verify.py` | P-MODEL (full) | 1 | CFA/SEM fit (CFI/TLI/RMSEA/SRMR + "mixed"=index-disagreement verdict) · model comparison · EFA dimensionality · McDonald ω · IRT 2PL (test information, SE(θ)) · Yen Q3; Bartlett-guarded |
| `repro_multiverse_verify.py` | P-REPRO + P-MULTIVERSE | 1 | dual-path reproduction certificate; specification-curve robust/fragile/mixed verdict (+ effect-size spread, OVB & large-n caveats) |
| `psychometrics_verify.py` | P-DIF | 1 | Mantel–Haenszel DIF (exact) |
| `psychometrics_verify.py` | P-META | 1 | fixed/random pooling + Egger funnel-asymmetry |
| `psychometrics_verify.py` | P-DESIGN | 1 | a-priori power; **optimal item selection = argmax test information (constructive)** |
| `psymetrix_router.py` | P-GROUND | armor | κ=0 interpretation → ground or ABSTAIN |

## Run it
```bash
cd MARK_1/ARSENAL/weapons/psymetrix
python3 selftest_all.py            # the GATE — every verifier passes good input AND catches broken input
python3 demo_forensics/run_demo.py # forensics killer demo (prediction in demo_forensics/PREDICTION.md)
python3 demo_model/run_demo.py     # P-MODEL demo on real Holzinger-Swineford 1939 data
python3 demo_multiverse/run_demo.py # P-REPRO+P-MULTIVERSE demo on real Fair's Affairs 1978 data
python3 psymetrix_router.py selftest # routing logic
```
P-MODEL needs `semopy`, `factor_analyzer`, `girth`, `scikit-learn` (`pip install --user ...`). If absent, the
gate **skips** P-MODEL with a notice (forensics + the rest still run); it does not silently pretend it ran.
**Trust nothing if the gate fails.** "A verifier that can't fail is not a verifier" — each κ>0 check is tested
on a known-good input (must pass) AND a known-broken input (must be caught), plus malformed input (must abstain
or raise, never silently mis-answer).

## What's proven (grounded, not asserted)
- **Killer demo (machine-verified):** reproduced all 4 of the method papers' **own published worked examples**
  (GRIM 5.27/43 impossible; GRIMMER 3.44/2.47/18 impossible via parity; two consistent controls), and on a
  **controlled ground-truth corpus** (400 rows from real integer Likert samples) measured GRIM at
  **100% specificity (zero false positives)** and **71.5% sensitivity**, with detection rate tracking the
  `1−n/100` power law (98.5% → 87.1% → 32.4% by n-bucket). The verifier is **sound** (never a false accusation)
  and honestly **incomplete** (misses typos that land on achievable values) — exactly the cap-set verifier's
  shape: it certifies, it does not catch everything.
- **Independently audited** by a different model (Sonnet): zero false positives in its own sweeps; all
  certificates re-derived independently; 4 robustness bugs found and fixed; honesty rails clean. See `AUDIT.md`.

## P-MODEL (full) — what's proven
- Built on `semopy`/`factor_analyzer`/`girth` (installed 2026-06-20). **Demo on the real Holzinger-Swineford 1939
  dataset** (`demo_model/`, predictions committed first): the known 3-factor model's fit indices **match lavaan
  to 4 sig figs** (CFI .931, RMSEA .092, SRMR .065); the data **prefer the 3-factor over a 1-factor model by
  ΔCFI=+0.254** (the discriminating test); EFA parallel analysis recovers **3 factors**. One honest forecast
  miss, kept visible: the 3-factor verdict is **"mixed"** (CFI/SRMR ok, RMSEA poor) — the textbook case of
  fit-index disagreement — not the "acceptable" I predicted.
- **Independently audited (round 2):** CFA numbers re-derived and matched; IRT 2PL recovery r≈0.996; Yen Q3 clean;
  the "mixed"-verdict change confirmed grounded (Marsh 2004), not goalpost-moving; **1 critical gaming vector
  fixed** (noise data could be rated "good" — now Bartlett-sphericity-guarded, 0/40 leaks) + 2 robustness fixes.
  See `AUDIT.md` (round 2).

## P-REPRO + P-MULTIVERSE — what's proven
- **Demo on the real Fair's Affairs 1978 dataset** (`demo_multiverse/`, predictions committed first): the focal
  religiousness→affair logit coefficient is **reproduced by two independent computations** (statsmodels GLM +
  hand-rolled numpy IRLS, agreeing to −0.375646); the auditor's third/fourth paths (sklearn, scipy) also match.
  Across a **256-spec multiverse** the effect is **ROBUST** — negative in 100% of specs, effect-size CV 7.3% —
  the honest counterpoint to SOCIUS's Durante effect that *died* in its multiverse.
- **Independently audited (round 3):** reproduction re-derived two more ways; **5 findings fixed** (zero-spec
  crash; and the honesty gaps — OVB/cherry-picked-pool can game "robust", p-curve non-independence, large-n
  significance vs effect size — now surfaced as **output caveats**, locked by self-tests). See `AUDIT.md` (round 3).
- **Ceiling:** "robust" = not an artifact of the analytic choices *tested*; it is **conditional on a complete
  covariate pool** (the tool cannot certify no omitted confounder) and **not** proof the effect is true/causal.

## Honest limitations
- P-MODEL fits/compares CFA/SEM/IRT and reports fit vs grounded cutoffs; it does **not** auto-search model space
  or do bifactor/ESEM — route those to a human modeler. **Fit ≠ truth:** a winning model is "not rejected and
  beats the alternative tested," never "true."
- SPRITE "not found" is **inconclusive**, NOT a proof of impossibility; only GRIM/GRIMMER give exact
  impossibility certificates.
- The p-curve 33%-power flatness test needs per-test noncentral distributions (test statistics + df); PSYMETRIX
  runs the exact right-skew evidential-value test by default and abstains on the 33%-power test unless those are
  supplied.

## Files
`SPEC.md` (1-page spec) · `GROUNDING.md` + `GROUNDING_MODEL.md` (fetched method sources) ·
`forensics_verify.py` (⭐ exact core) · `psychometrics_verify.py` (reliability/DIF/meta/power) ·
`model_verify.py` (full CFA/SEM/EFA/IRT) · `repro_multiverse_verify.py` (P-REPRO + P-MULTIVERSE) ·
`psymetrix_router.py` · `selftest_all.py` (gate) · `demo_forensics/` + `demo_model/` + `demo_multiverse/`
(prediction + run + RESULT.json) · `AUDIT.md` (cross-model red-team, 3 rounds).
