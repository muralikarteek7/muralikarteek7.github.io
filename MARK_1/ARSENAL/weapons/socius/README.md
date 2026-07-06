# SOCIUS — κ-aware empirical-rigor engine for social science
*A v5 "ARMOR + WEAPONS" weapon. Plugs into the `Next/BOX_V5.md` when/where router.*

## One line
Given a social-science research task, SOCIUS **chooses which rigor checks apply**, runs the
machine-checkable ones (κ>0) to a **frozen, adversarially self-tested verifier**, **grounds or
abstains** on the judgment ones (κ=0), and reports — honestly — what survived and **what died
under stress**. It raises *trustworthiness* (reproducibility + grounding). **It does not, and
cannot, manufacture truth where there is no ground truth.**

Sociology is a **low-κ field**: most claims have no cheap exact verifier, so SOCIUS is **not** a
record-breaking construction engine (unlike the cap-set Frontier Construction Engine). Its value
is catching the field's characteristic failure modes — irreproducibility, analytic-flexibility
artifacts, measurement non-invariance, fragile causal claims, over-generalisation — and being
honest about the κ=0 residue.

## Files
| file | what |
|---|---|
| `SPEC.md` | the one-page spec (sub-weapons, grounded method SOTA, honesty rails) |
| `socius_router.py` | the chooser: task → which sub-weapons fire (κ-labelled) |
| `repro_verify.py` | **S-REPRO** — reproduction within tolerance (κ=1) |
| `multiverse_verify.py` | **S-MULTIVERSE** — specification-curve / multiverse robustness (κ=1) |
| `measure_verify.py` | **S-MEASURE** — reliability (α, ω) + measurement invariance CFA (κ=1) |
| `eval_verify.py` | **S-CAUSAL** — E-value sensitivity to unmeasured confounding (κ=0.5) |
| `sample_verify.py` | **S-SAMPLE** — representativeness + weighting / generalisability (κ=0.5) |
| `ground_verify.py` | **S-GROUND** — fabrication detector (κ=1: quote/number/citation actually in the fetched source) + entailment judgment (κ=0, model ≠ generator, else ABSTAIN) |
| `selftest_all.py` | the **frozen-verifier gate** — every verifier must pass good AND catch broken |
| `demo_durante2013/` | killer demo #1: reproduce + stress a real published finding |
| `demo_grounding/` | killer demo #2: ground 8 claims vs 3 real abstracts (8/8); catches a fabricated quote, a wrong-author cite, an entailment contradiction |
| `AUDIT.md` | independent cross-model red-team (auditor ≠ generator) |

## Run it
```bash
cd MARK_1/ARSENAL/weapons/socius
python3 selftest_all.py                 # the gate — must print "OK" or NOTHING is trusted
python3 socius_router.py selftest       # routing logic
python3 demo_durante2013/socius_run.py  # the end-to-end killer demo
```
Dependencies: `numpy`, `scipy`, `pandas`, `statsmodels` (pure-Python verifiers; no R).

## The killer demo, in one breath
Durante et al. (2013) "fluctuating female vote" Study 1 (fertility × relationship → religiosity),
reproduced from Steegen et al. (2016)'s own open data + R code (OSF zj68b, downloaded). **It
reproduces exactly — 120 specifications, 7 significant (5.8%) — and then DIES under the
multiverse.** 5 of 6 predictions committed-before-running were correct; the 1 miss sharpened the
diagnosis (the failure is analytic flexibility, not confounding). An independent machine-check of
the fit indices caught a false "non-invariance" verdict (a small-df ΔRMSEA artifact) which was
then fixed. See `demo_durante2013/WRITEUP.md`.

## Honest ceiling (binding, stated every run)
- **Reproduction ≠ discovery.** Reproducing a number proves it follows from the data+code, nothing more.
- **Robust ≠ true.** Surviving the multiverse means not-an-artifact-of-analytic-choice; it can still be
  confounded, mis-measured, or non-generalisable.
- **κ=0 stays κ=0.** Theory, interpretation, and meaning are routed to armor (ground or abstain),
  never presented as machine-verified.
- **Abstention is a deliverable.** Where neither grounding nor a check exists, SOCIUS abstains and says so.
- SOCIUS is an **instrument for a human's social science**, not a replacement for it.

## Status (honest)
A **new weapon ADDED** to the v5 box = **capability expansion** (a problem class — empirical
social-science rigor — the box could not previously serve). **NOT a ≥10% A/B promotion**: there is
no shared arena against a prior SOCIUS, so the ≥10% capability ratchet is untouched (stays open at
v3). See `../../../../MARK_0/02_ladder_history/Legacy/EVOLUTION_LOG.md` and `../../../SPEC/BOX_V5.md`.
