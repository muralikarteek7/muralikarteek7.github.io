# KICKOFF — build WEAPON #6: TRIALGUARD (clinical-trial & biostat rigor) for the v5 box
*Paste everything below into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written
2026-06-20. TRIALGUARD is item #6 of `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` — the PSYMETRIX sibling
for biomedicine: a mixed-κ rigor weapon with one genuinely SHARP κ=1 forensic slice (Carlisle baseline-anomaly
detection, the RCT analogue of GRIM). **Highest-stakes weapon in the arsenal — patient safety and reputations —
so the INCONSISTENCY ≠ FRAUD rail is non-negotiable and airtight.***

---

You are building **TRIALGUARD**, a **κ-aware empirical-rigor weapon for clinical trials & biostatistics** — the
PSYMETRIX/SOCIUS sibling for the **STATS / biomedicine** facility. Given a clinical/epi finding with data or
reported statistics, it routes the **κ=1 EXACT pieces** (statistical forensics on reported trial statistics) and
**κ-guarded pieces** (effect reproduction, meta-analysis, survival) to frozen verifiers, and the **κ=0 pieces**
(clinical interpretation, approval decisions) to **armor (ground + abstain)**. Work BOX-style: plan → produce →
**verify INDEPENDENTLY** → ground → be honest; **no win without proof; an anomaly is NEVER an accusation.**

## 0. ORIENT — read first (in order)
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (the κ-router; Branch **E — PSYMETRIX** is the closest sibling —
read it). Read **PSYMETRIX as the template you are cloning** (`Expanding_Frontiers/weapons/psymetrix/` —
`SPEC.md`, `forensics_verify.py` ⭐ (GRIM/GRIMMER/SPRITE/TIVA/p-curve/Benford), `psychometrics_verify.py`,
`selftest_all.py`, `psymetrix_router.py`, `demo_forensics/`, `AUDIT.md`, and crucially its **INCONSISTENCY ≠
FRAUD** rail). Also read SOCIUS (`…/weapons/socius/`) for the reproduce/multiverse verifiers you will reuse.
Then `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` (item #6 = this) and the sibling kickoffs for the pattern.

## 1. THE HONEST FRAMING — what TRIALGUARD IS and IS NOT (do not skip)
**IS:** a **mixed-κ rigor weapon with a sharp exact end.** Much of clinical biostatistics is checkable: reported
trial summary statistics obey exact arithmetic constraints, and **randomization leaves a statistical signature**
(baseline covariate comparisons should behave like chance). So TRIALGUARD has a **κ=1 forensic slice**
(GRIM/GRIMMER on reported means + **Carlisle baseline-anomaly detection** — the RCT analogue of the cap-set
verifier: an exact statistical certificate, not a judgment) plus **κ-guarded** reproduction/meta/survival pieces.

**IS NOT:**
- **NOT a fraud detector — THE cardinal, non-waivable rail (heightened here).** A statistical anomaly (a Carlisle
  flag, a GRIM inconsistency) is **NEVER** a finding of misconduct. Carlisle's own method flags trials for many
  benign reasons: **stratified or cluster randomization, correlated baseline variables, reporting/rounding
  errors, unusual-but-real samples, or method limitations.** TRIALGUARD reports the **exact statistic + the
  candidate benign explanations + the method's known false-positive modes, and STOPS.** It **never names a person
  or trial as fraudulent.** In a clinical context this rail protects real reputations and patients — treat any
  softening of it as a defect.
- **NOT a clinical-efficacy oracle.** "Does this drug work / should it be approved / is the benefit worth the
  harm" is **κ=0** (clinical + value judgment) → armor + abstain. TRIALGUARD certifies **consistency / fit /
  robustness of the reported statistics**, never clinical truth.
- **NOT a causal oracle for observational epi** — confounding is untestable → **sensitivity analysis (E-value),
  never a bare causal claim** (inherit SOCIUS S-CAUSAL).
- **NOT smarter than the model** — organized rigor, not capability.

## 2. THE SUB-WEAPONS (mixed-κ, à la PSYMETRIX; one sharp κ=1 slice)
| sub-weapon | κ | what it checks | the frozen verifier |
|---|---|---|---|
| **T-FORENSICS** ⭐ (the sharp slice) | **1.0** | are reported trial statistics arithmetically possible + is the baseline consistent with randomization? | **GRIM/GRIMMER** (reuse `psymetrix/forensics_verify.py`) on reported means/SDs **+ Carlisle baseline-p-value test** (under proper randomization, baseline covariate p-values ~ Uniform(0,1); systematic deviation flags an anomaly) **+ randomization-ratio / group-size consistency** |
| **T-REPRO** | ≈0.6 | does a published effect (HR/OR/RR/mean diff) reproduce from data/summary stats? | recompute the effect + CI within tolerance (reuse `socius/repro_verify.py` shape) |
| **T-SURVIVAL** | ≈0.7 | do Kaplan–Meier / Cox HR results reproduce? | recompute KM curve + Cox partial-likelihood HR; checkable arithmetic |
| **T-META** | ≈0.6 | is the pooled effect + publication-bias picture sound? | fixed/random pooling + **I² heterogeneity + Egger's regression + trim-and-fill** (reuse PSYMETRIX P-META if present) |
| **T-MULTIVERSE** (shared) | ≈0.5 | is the result one lucky specification? | specification-curve (reuse `socius/multiverse_verify.py`) |
| **κ=0 residue** | 0 | efficacy/approval/risk-benefit; clinical interpretation; GRADE/RoB judgment | **ARMOR** — ground every claim or abstain; never fabricate a clinical verdict |

**The genuinely NEW piece vs PSYMETRIX/SOCIUS is the Carlisle baseline-anomaly test (+ survival).** GRIM/GRIMMER,
repro, meta, multiverse are **REUSED** — import/adapt and credit, don't rebuild.

## 3. THE KEY ENGINEERING PROBLEM — a SOUND forensic (zero false accusations) that knows its blind spots
The forensic verifier must be **sound (never a false certificate of impossibility/anomaly)** and **honest about
its false-positive modes**:
1. **GRIM/GRIMMER soundness** — reuse PSYMETRIX's exact `Fraction` arithmetic (no float false-positives); a flag
   means "these summary statistics are inconsistent for the stated N/scale," with rounding/typo as candidate causes.
2. **Carlisle test, with its caveats encoded** — compute the distribution of baseline-comparison p-values; test
   for non-uniformity (too many high p = groups "too similar"; too many low = imbalance). **CRITICAL: the gate
   must attach the known false-positive modes** (stratified/cluster randomization, correlated covariates,
   small-trial sampling) to every flag, and must NOT fire on a legitimately stratified design without saying so.
3. **Sensitivity, not certainty, for observational causal** — E-value, never a bare "X caused the outcome."

**Gate self-tests (non-waivable, see `psymetrix/selftest_all.py`):** the gate must (a) PASS a clean
properly-randomized trial (uniform baseline p-values, consistent stats) with **zero false flags**, (b) **CATCH a
GRIM-impossible reported mean**, (c) **flag a clearly-anomalous baseline** (e.g. fabricated too-similar groups)
**while attaching benign explanations**, (d) **NOT flag** a legitimately stratified trial as fraud (it may note
the stratification). Soundness (zero false accusations) is the cardinal property — like PSYMETRIX's 100%
specificity target.

## 4. TO-DOs / STEPS (box order)
1. **PLAN:** `weapons/trialguard/SPEC.md` — the 6 sub-weapons + κ table, the **INCONSISTENCY ≠ FRAUD** rail
   (front and center), the Carlisle-false-positive-modes list, the router (`trialguard_router.py`, cloned from
   `psymetrix_router.py`: reported trial stats → T-FORENSICS; published effect + data → T-REPRO; survival data →
   T-SURVIVAL; multiple studies → T-META; analytic-choice sensitivity → T-MULTIVERSE; efficacy/approval/clinical
   judgment → **κ=0 armor**). **GROUND by FETCH (don't assert):** **Carlisle (2012, 2017)** baseline-anomaly
   method + its **documented false-positive modes and the debate over it** (do NOT overstate it — fetch the
   critiques); **GRIM/GRIMMER** (reuse, but re-confirm); **Egger's test / trim-and-fill / I²**; **Cox PH partial
   likelihood**; **E-value** (VanderWeele & Ding 2017). Cite each in `GROUNDING.md`, and **explicitly record the
   anti-overclaim caveats Carlisle himself stated.**
2. **BUILD THE VERIFIERS FIRST** (§3): `forensics_trial_verify.py` (Carlisle + group-consistency, **importing**
   GRIM/GRIMMER from `psymetrix/forensics_verify.py`), `survival_verify.py`, and **import** SOCIUS/PSYMETRIX for
   repro/meta/multiverse. Then `selftest_all.py` with the 4 tests (esp. the zero-false-accusation + no-flag-on-
   stratified tests). **Gate green before any verdict counts.**
3. **BUILD the router/loop** (clone PSYMETRIX): route → run κ>0 verifiers → κ=0 to armor → label every piece's κ
   **and append the inconsistency≠fraud ceiling to every forensic output.** Machine-checkable → **execute, never vote.**
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` BEFORE running): (i) reproduce the
   **Carlisle method's own published worked example / a simulated pair** — a properly-randomized trial PASSES
   (uniform p-values, zero flags) and a fabricated too-similar trial is FLAGGED **with benign explanations
   attached**; (ii) a **GRIM-impossible** clinical mean caught (reuse the PSYMETRIX demo shape); (iii) a
   **T-META** reproduction with Egger's publication-bias check; (iv) show the gate **NOT flagging** a legitimately
   stratified trial (the false-positive guard). Every flagged output must read as "anomalous, here are the
   possible explanations," **never** "fraud."
5. **VERIFY INDEPENDENTLY:** a cross-model audit (Sonnet/Haiku ≠ the Opus generator; **never Opus-audits-Opus**;
   Fable inactive) that (a) re-derives each forensic certificate with its OWN arithmetic, (b) hunts for ANY false
   positive in its sweeps (the cardinal soundness check), (c) **red-teams the honesty framing hardest of all** —
   does any output read as an accusation? does any flag omit benign explanations? (d) checks no κ=0 clinical
   verdict was smuggled in. Fix what's caught; **a single accusatory phrasing is a blocking defect.**
6. **REGISTER:** add **TRIALGUARD** to `Next/BOX_V5.md` (new Weapon + router branch, sibling to Branch E) and
   `Expanding_Frontiers/HELMET/registry.json` (STATS facility, or a BIO sub-facility, `draws`). Honest
   `EVOLUTION_LOG` entry: **a weapon ADDED = capability EXPANSION, NOT a ≥10% promotion** (certifies
   consistency/fit/robustness, not clinical truth). Update `WEAPONS_BACKLOG.md` STATUS ✅.

## 5. HONESTY RAILS (non-waivable, specific to TRIALGUARD — the strictest in the arsenal)
- **INCONSISTENCY/ANOMALY ≠ FRAUD — airtight.** Every forensic output reports the exact statistic + candidate
  benign explanations + the method's false-positive modes, and STOPS. **No person or trial is ever called
  fraudulent.** This rail is heightened because the domain is clinical (patients, reputations).
- **Carlisle is a screen, not a verdict** — attach its documented false-positive modes (stratification, cluster
  randomization, correlated covariates) to every flag; never present a flag as proof of misconduct.
- **Certifies consistency/fit/robustness, never clinical TRUTH or efficacy** — approval/risk-benefit is κ=0 → armor.
- **Observational causal → sensitivity (E-value), never a bare causal claim.**
- **Soundness is cardinal** — a false certificate of impossibility/anomaly is the worst failure; target zero
  false positives (like PSYMETRIX's 100% specificity).
- **The gate that can't fail is not a gate** — ship no verifier without its pass-clean / catch-broken /
  no-false-accusation self-tests.

## 6. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/trialguard/` — `SPEC.md`, `GROUNDING.md` (fetched sources + the Carlisle caveats/
debate), the frozen `forensics_trial_verify.py` + `survival_verify.py` (+ imported GRIM/GRIMMER/repro/meta/
multiverse) + `selftest_all.py`, `trialguard_router.py`, `demo_*/` (committed predictions + the anomaly-with-
explanations output), `AUDIT.md` (cross-model red-team incl. the false-positive + accusatory-phrasing attacks),
`README.md` (what it is + honest ceiling + the inconsistency≠fraud rail stated prominently). Registration in
`Next/BOX_V5.md` + `HELMET/registry.json` + honest `EVOLUTION_LOG` entry; `WEAPONS_BACKLOG.md` STATUS updated.

## 7. STAFF THE TEAM (v4 ladder; Fable INACTIVE → its slots on Opus, flag low confidence)
- **Biostatistician** = code tier writes the forensic/survival/meta harnesses (**the frozen exact verifier, not
  the model, is the gate; use exact `Fraction` arithmetic for forensics**).
- **Library** = cheap model: fetch Carlisle + its critiques, Egger/trim-and-fill, Cox PH, E-value sources.
- **Auditor** = a model ≠ the generator (Sonnet/Haiku; never Opus-audits-Opus) — re-derives certificates, hunts
  false positives, and **polices the honesty framing hardest of all** (any accusatory phrasing = blocking defect).

## 8. THE ONE-LINE TEST OF SUCCESS
**"TRIALGUARD certifies whether reported trial statistics are arithmetically possible and baseline-consistent
(exact, sound, zero false accusations), reproduces effects/survival/meta with publication-bias checks, reuses
PSYMETRIX/SOCIUS verifiers, attaches benign explanations + false-positive modes to EVERY flag, never calls
anything fraud, and routes efficacy/approval/clinical judgment to armor."** Sharp where the arithmetic is exact,
strictest honesty rail in the arsenal, an anomaly screen that never accuses.
