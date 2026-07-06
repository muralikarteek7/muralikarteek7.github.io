# SOCIUS — a κ-aware empirical-rigor engine for social science (v5 weapon)
*One-page spec. Home: `Expanding_Frontiers/weapons/socius/`. Registered in `Next/BOX_V5.md`.*

## What it is (and is not)
SOCIUS is the v5 weapon for the **social-science / sociology** problem class. Sociology is a
**LOW-κ field**: most claims (theory, meaning, interpretation, normative analysis) have **no
cheap, exact, non-gameable verifier** → by the v5 κ-gate they are **κ=0 → ARMOR ONLY**.
**So SOCIUS is NOT a construction engine** — there are no machine-checkable "records" to break.
It is an **empirical-rigor engine**: it splits a research task by checkability, routes the
**κ>0 executable pieces** (reproduce a statistic, stress it, check a measure, check a causal
assumption, check sampling) to **frozen verifiers**, and the **κ=0 judgment pieces** to armor
(ground every claim in a fetched source or abstain).

**Its offense is trustworthiness (V·G), not truth.** Stated in every output:
**reproduction ≠ discovery; robust ≠ true.** A finding that survives every check can still be
confounded, mis-measured, or non-generalisable. **Findings that DIE under stress are the
primary valuable output.** SOCIUS makes a human's social science more reproducible and honest;
it does not "do sociology" for anyone and cannot manufacture truth where there is no ground truth.

## The sub-weapons (frozen verifier per κ>0; armor where κ=0)
| sub-weapon | fires when | κ | frozen verifier (self-tested to FAIL on broken input) | file |
|---|---|---|---|---|
| **S-REPRO** | a published quantitative finding has open data+code | 1 | re-run pipeline → matches reported statistic within tol; structure exact | `repro_verify.py` |
| **S-MULTIVERSE** | finding rests on defensible-but-arbitrary analytic choices | 1 | enumerate the FULL spec grid → effect distribution + % significant + sign-stability; verdict robust/fragile | `multiverse_verify.py` |
| **S-MEASURE** | constructs are latent (scales/indices) and/or groups compared | 1 | Cronbach α + McDonald ω; multigroup 1-factor CFA configural→metric→scalar invariance (ΔCFI-primary) | `measure_verify.py` |
| **S-CAUSAL** | claim is causal from observational data | 0.5 | E-value (VanderWeele & Ding 2017) for unmeasured confounding; CI-limit E-value; flags fragile vs a declared benchmark | `eval_verify.py` |
| **S-SAMPLE** | inference generalises beyond the sample | 0.5 | representativeness (TV distance) + weight-sensitivity (Kish design effect); flags non-generalisable | `sample_verify.py` |
| **S-GROUND** | any empirical assertion in prose | 1 + armor (0) | **Layer 1 (κ=1 frozen):** quote/number/author actually present in the FETCHED source (catches invented quotes & citations). **Layer 2 (κ=0):** entailment judged by a model ≠ generator, else ABSTAIN | `ground_verify.py` |

Router: `socius_router.py` reads a task, classifies its claims, fires the sub-weapons whose
preconditions hold, sends the κ=0 residue to armor. Self-test gate: `selftest_all.py` (must
exit 0 — every verifier passes a good input AND catches a broken one, or no output is trusted).

## Grounded method SOTA (fetched, not asserted — see grounding report in repo history)
- **Specification curve:** Simonsohn, Simmons & Nelson 2020, *Nature Human Behaviour* 4:1208–1214.
- **Multiverse:** Steegen, Tuerlinckx, Gelman & Vanpaemel 2016, *Perspectives on Psych. Science* 11:702–712.
- **E-value:** VanderWeele & Ding 2017, *Annals of Internal Medicine* 167:268–274. `E = RR + √(RR(RR−1))`,
  RR<1 inverts; CI uses the limit nearest the null; OR(common)→√OR, d→exp(0.91·d).
- **Rosenbaum bounds:** Rosenbaum 2002/2004 — Γ = within-pair treatment-odds bound from hidden bias.
- **Measurement invariance:** Cheung & Rensvold 2002 (ΔCFI ≤ 0.01, primary); Chen 2007 (ΔRMSEA ≤ 0.015);
  Kenny, Kaniskan & McCoach 2015 (RMSEA unreliable at small df → ΔCFI-primary).
- **Reliability:** Cronbach 1951 (α); McDonald 1999 (ω). Floors: ≥0.70 acceptable, ≥0.80 good.
- **Replication crisis (why this weapon exists):** Open Science Collaboration 2015 (36/100 replicated);
  Camerer et al. 2018 (13/21); Many Labs 2 / Klein et al. 2018 (14/28).

## Killer demo (committed prediction → run → compare)
Durante et al. 2013 Study 1 (fertility × relationship → religiosity), reproduced and stressed via
Steegen et al. 2016's own data+R code (OSF zj68b, downloaded). **Result: REPRODUCES exactly
(120 specs / 7 significant = 5.8%) but DIES under the multiverse** — an artifact of one analytic
path. 5/6 committed predictions correct; 1 honest miss (the single significant path's simple
effect is NOT trivially confounded — the failure mode is analytic flexibility, not confounding).
Details: `demo_durante2013/` (`PREDICTION.md`, `socius_run.py`, `socius_results.json`, `WRITEUP.md`).

## Honesty rails (non-waivable)
κ-label every output piece; never present a κ=0 judgment as machine-verified. Reproduction is
labelled reproduction. Never launder a non-robust finding as robust. No fabricated citations/data
(every source fetched, every dataset real). Abstain when neither grounded nor checkable —
abstention is a scored deliverable. **Honest ceiling, every run: raises reproducibility +
grounding; does NOT establish truth.**
