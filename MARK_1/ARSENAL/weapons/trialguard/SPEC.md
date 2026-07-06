# TRIALGUARD — a κ-aware Clinical-Trial & Biostatistics Rigor Engine (v5 weapon SPEC)

*Spec stamped 2026-06-20. Sibling of PSYMETRIX/SOCIUS for the **STATS / biomedicine** facility. Clinical
biostatistics is **mixed-κ with one genuinely SHARP κ=1 slice**: reported trial summary statistics obey exact
arithmetic constraints, and **randomization leaves a statistical signature**. Grounding for every method is in
[`GROUNDING.md`](GROUNDING.md) (fetched sources + the Carlisle critiques, not memory).*

## ⚠️ THE CARDINAL, NON-WAIVABLE RAIL — INCONSISTENCY / ANOMALY ≠ FRAUD (read first)

**This is the strictest honesty rail in the arsenal because the domain is clinical — patients and reputations
are at stake.** A statistical anomaly (a Carlisle flag, a GRIM inconsistency, an extreme baseline p-value) is
**NEVER** a finding of misconduct. The method's originator says so himself:

> *"Fraud, unintentional error, correlation, stratified allocation and poor methodology might have contributed
> to the excess."* — **Carlisle 2017** (the originator of the baseline test), *Anaesthesia* 72(8):944–952.

Every forensic output reports **(1) the exact statistic, (2) the candidate benign explanations, (3) the method's
known false-positive modes — and STOPS.** It **never names a person or trial as fraudulent**; it never emits the
word "fraud" as a verdict. Any accusatory phrasing is a **blocking defect**, not a stylistic nit.

## 0. One line
TRIALGUARD reads a clinical/epi task, routes each claim by **κ** (checkability), draws the matching frozen
verifiers where κ>0, and grounds-or-abstains where κ=0. It **certifies CONSISTENCY / FIT / ROBUSTNESS of the
reported statistics, never CLINICAL TRUTH or EFFICACY.** Its sharp end can test whether reported trial statistics
are arithmetically possible and whether the baseline is statistically consistent with randomization — an exact
*anomaly screen*, never an accusation.

## 1. The κ-profile (defines the weapon)
- **κ = 1 (EXACT, non-gameable) — the sharp end:** *trial-statistic forensics.* (a) **GRIM/GRIMMER** on reported
  means/SDs (reused, exact `Fraction` arithmetic); (b) **group-size / allocation-ratio / percentage→count**
  consistency (exact); (c) **Carlisle baseline-anomaly test** — under simple randomization the two-sided
  baseline p-values of *continuous* variables are i.i.d. U(0,1); a systematic departure (too-similar or
  too-different) is an exact distributional anomaly. *The Carlisle slice is κ=1 in arithmetic but its
  INTERPRETATION is guarded by the false-positive modes (correlation, stratification) — it is a screen, not a
  certificate of impossibility.*
- **κ ≈ 0.6–0.7 (executable, guarded):** effect **reproduction** (recompute HR/OR/RR/mean-diff + CI), **survival**
  (Kaplan–Meier + Cox PH partial likelihood), **meta-analysis** (fixed/random pooling + I² + Egger + trim-and-fill).
- **κ ≈ 0.5 (executable, guarded):** **multiverse / specification-curve** robustness (reused from SOCIUS).
- **κ = 0 (armor only):** does the drug **work** / should it be **approved** / is the benefit worth the harm;
  clinical interpretation; GRADE / risk-of-bias judgment; observational **causation** → ground against a fetched
  source or **ABSTAIN** (observational causal → **E-value sensitivity**, never a bare causal claim). Never
  presented as machine-verified.

## 2. Sub-weapon registry (frozen verifier built + adversarially self-tested for each κ>0 piece)
| sub-weapon | fires when | κ | module | what the frozen verifier certifies |
|---|---|---|---|---|
| **T-FORENSICS** ⭐ | reported trial summary stats / baseline Table 1 | **1 (EXACT)** | `forensics_trial_verify.py` (+ imports GRIM/GRIMMER from `psymetrix/forensics_verify.py`) | GRIM/GRIMMER mean–SD–N consistency (exact); group-size & allocation-ratio & percentage→count consistency (exact); **Carlisle baseline-p-value uniformity** (Carlisle-Stouffer Z + KS vs U(0,1)) **with every false-positive mode + benign explanation attached** |
| **T-SURVIVAL** | survival / time-to-event data | ≈0.7 | `survival_verify.py` | Kaplan–Meier curve + Greenwood SE; **Cox PH partial-likelihood HR** (Breslow ties, Newton–Raphson), cross-checked vs an independent implementation (statsmodels PHReg) |
| **T-REPRO** | a published effect with data/summary stats | ≈0.6 | `repro_verify.py` (reused from `socius/`) | recompute the effect + CI within tolerance → reproduction certificate (a 3× coding error flips it) |
| **T-META** | a body of studies | ≈0.6 | `meta_trial_verify.py` (reuses `psymetrix` `meta_analysis` + adds trim-and-fill) | fixed/random pooled effect; **I² heterogeneity + Egger funnel asymmetry + trim-and-fill** publication-bias correction |
| **T-MULTIVERSE** | a finding resting on analytic choices | ≈0.5 | `multiverse_verify.py` (reused from `socius/`) | specification-curve robust / fragile / mixed verdict |
| **T-EVALUE** | an observational (non-randomized) causal claim | ≈0.5 | `forensics_trial_verify.py::evalue` | E-value sensitivity (min confounder strength to explain away) — **sensitivity, never a bare causal claim** |
| **κ=0 residue** | efficacy / approval / risk–benefit; clinical interpretation; GRADE/RoB | 0 | router → **ARMOR** | ground every claim against a fetched source or ABSTAIN; never fabricate a clinical verdict |

**The genuinely NEW piece is the Carlisle baseline-anomaly test (+ the hand-rolled survival).** GRIM/GRIMMER,
repro, multiverse, meta are **REUSED** (imported and credited, not rebuilt).

## 3. Routing (the chooser)
`trialguard_router.py` (cloned from `psymetrix_router.py`) classifies a task's claims → draws the matching κ>0
sub-weapons → routes the κ=0 residue (efficacy/approval/clinical judgment) to **ARMOR**. Every routed piece is
labelled with its κ; the **inconsistency≠fraud ceiling is appended to every forensic plan** so nothing reads as
an accusation and nothing κ=0 is presented as machine-verified.

## 4. The killer demo (predictions committed BEFORE running — see `demo_forensics/PREDICTION.md`)
On **simulated trials with KNOWN ground truth** (no real trial is named or accused): (i) a properly-randomized
trial **PASSES** (baseline p-values ~U(0,1), zero false flags) and a **fabricated too-similar** trial is
**FLAGGED with benign explanations attached**; (ii) a **GRIM-impossible** clinical mean is caught; (iii) a
**T-META** reproduction with an Egger publication-bias check; (iv) the gate **does NOT flag** a legitimately
**stratified** trial as fraud (the false-positive guard). Every flagged output reads *"anomalous — here are the
possible explanations,"* **never** *"fraud."*

## 5. Honesty rails (non-waivable, the strictest in the arsenal)
1. **INCONSISTENCY / ANOMALY ≠ FRAUD — airtight** (see the cardinal rail above). Exact statistic + benign
   explanations + false-positive modes, then STOP. No person or trial is ever called fraudulent.
2. **Carlisle is a SCREEN, not a verdict.** Attach its documented false-positive modes — **stratified/cluster
   randomization, correlated covariates, rounding, small k, categorical-variable misuse** — to every flag.
   The test is **restricted to continuous variables** (it is unsound for categorical ones) and **excludes
   declared stratification factors** (as Carlisle himself did).
3. **Certifies consistency / fit / robustness, never CLINICAL TRUTH or EFFICACY.** Approval / risk–benefit is
   κ=0 → armor + abstain.
4. **Observational causal → sensitivity (E-value), never a bare causal claim.**
5. **Soundness is cardinal** — a false certificate of impossibility/anomaly (a false accusation) is the worst
   failure; target **zero false positives** (PSYMETRIX's 100%-specificity bar).
6. **The gate that can't fail is not a gate** — ship no verifier without its pass-clean / catch-broken /
   no-false-accusation / no-flag-on-stratified self-tests.

## 6. Ceiling (stated every time)
TRIALGUARD certifies **consistency / fit / robustness** of reported statistics, not **clinical truth**. A trial
whose statistics are arithmetically consistent and baseline-uniform is **not** "valid" or "effective"; a flagged
anomaly is a **mathematical/statistical fact about the reported numbers, with many benign causes — never an
accusation about the people.** Reproduction ≠ truth; robust ≠ true; consistent ≠ correct; HR reproduced ≠ drug
works.
