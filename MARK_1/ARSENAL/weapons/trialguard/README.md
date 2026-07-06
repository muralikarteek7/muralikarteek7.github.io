# TRIALGUARD — κ-aware Clinical-Trial & Biostatistics Rigor Engine

A registered **v5 weapon** for **clinical trials & biostatistics** (the STATS / biomedicine facility). The
PSYMETRIX/SOCIUS sibling for biomedicine: a **mixed-κ rigor weapon** with one genuinely **sharp κ=1 exact slice**
(GRIM/GRIMMER + group-size/percentage arithmetic) plus a **calibrated Carlisle baseline-anomaly screen**, and
κ-guarded reproduction / survival / meta / multiverse pieces. **Highest-stakes weapon in the arsenal — patient
safety and reputations — so the inconsistency≠fraud rail is non-negotiable and airtight.**

## ⚠️ THE CARDINAL, NON-WAIVABLE RAIL — INCONSISTENCY / ANOMALY ≠ FRAUD
A statistical anomaly (a Carlisle flag, a GRIM inconsistency, an extreme baseline p-value) is **NEVER** a finding
of misconduct. Every forensic output reports **the exact statistic + candidate BENIGN explanations + the
method's FALSE-POSITIVE modes — and STOPS.** It never names a person or trial as fraudulent; the word "fraud"
never appears as a verdict. In the originator's own words:

> *"Fraud, unintentional error, correlation, stratified allocation and poor methodology might have contributed
> to the excess."* — **Carlisle 2017**, *Anaesthesia* 72(8):944–952.

Any accusatory phrasing is a **blocking defect**. An automated honesty gate (`affirms_misconduct()`) scans every
emitted verdict; the independent cross-model audit confirmed **zero** outputs affirm misconduct.

## What it is
Given a clinical/epi task, TRIALGUARD **routes each claim by κ** (checkability), draws the matching frozen
verifiers where κ>0, and grounds-or-abstains where κ=0. It **certifies CONSISTENCY / FIT / ROBUSTNESS of the
reported statistics, never CLINICAL TRUTH or EFFICACY.**

## The honest ceiling (stated every time)
A trial whose statistics are arithmetically consistent and baseline-uniform is **not** "valid" or "effective"; a
flagged anomaly is a **statistical fact about the reported numbers, with many benign causes — never an accusation
about the people.** Reproduction ≠ truth; robust ≠ true; consistent ≠ correct; HR reproduced ≠ drug works.

## Sub-weapons
| module | sub-weapon | κ | certifies |
|---|---|---|---|
| `forensics_trial_verify.py` ⭐ | **T-FORENSICS** | **1 (EXACT)** for GRIM/allocation/percentage; **≈0.9 SCREEN** for Carlisle | GRIM/GRIMMER mean–SD–N consistency (reused, exact `Fraction`); allocation-ratio & percentage→count consistency (exact); **Carlisle baseline-p-value uniformity** (Stouffer Z + KS vs U(0,1)) with every false-positive mode + benign explanation attached; E-value (observational causal → sensitivity) |
| `survival_verify.py` | **T-SURVIVAL** | ≈0.7 | Kaplan–Meier + Greenwood SE; **Cox PH partial-likelihood HR** (Breslow ties, Newton–Raphson), cross-checked vs statsmodels PHReg |
| `meta_trial_verify.py` | **T-META** | ≈0.6 | fixed/random pooling + I² + Egger (reused from PSYMETRIX) + **trim-and-fill** publication-bias correction |
| `repro_verify.py` (reused, `../socius`) | **T-REPRO** | ≈0.6 | recompute a published effect → reproduction certificate (a 3× coding error flips it) |
| `multiverse_verify.py` (reused, `../socius`) | **T-MULTIVERSE** | ≈0.5 | specification-curve robust / fragile / mixed verdict |
| `trialguard_router.py` | **T-ARMOR** | 0 | efficacy / approval / risk–benefit / clinical judgment → ground or ABSTAIN |

**Genuinely NEW vs PSYMETRIX/SOCIUS:** the **Carlisle baseline-anomaly test** + the hand-rolled **survival**
verifier. GRIM/GRIMMER, repro, multiverse, meta are **REUSED** (imported and credited, not rebuilt).

## Run it
```bash
cd MARK_1/ARSENAL/weapons/trialguard
python3 selftest_all.py            # the GATE — every verifier passes good input AND catches broken input
python3 demo_forensics/run_demo.py # killer demo (predictions in demo_forensics/PREDICTION.md)
python3 trialguard_router.py selftest
```
**Trust nothing if the gate fails.** "A verifier that can't fail is not a verifier" — each κ>0 check is tested on
a known-good input (must pass), a known-broken input (must be caught), and malformed input (must abstain). The
forensic gate additionally asserts the **4 cardinal tests**: a clean randomized trial passes with zero false
flags; a GRIM-impossible mean is caught; a too-similar baseline is flagged **with benign explanations**; a
stratified trial is **not** accused.

## What's proven (grounded + independently verified, not asserted)
- **Killer demo (machine-verified, predictions committed first):** GRIM 5.27/43 caught; exact allocation
  (30/90 ≠ 1:1) and percentage (33.3% of n=7 impossible) caught; on a **controlled ground-truth corpus**
  (300 properly-randomized + 300 fabricated-too-similar trials) the Carlisle screen showed **specificity ~99.7%
  (1/300 clean false flag at α=.001, well-calibrated)** and **86.7% sensitivity** to over-balancing fabrication,
  with **ZERO of ~600 outputs affirming misconduct**; T-META flags funnel asymmetry (Egger p=.012) and
  trim-and-fill pulls the pooled effect toward the null; the stratified-trial guard holds.
- **Independently audited** by a different model (Sonnet ≠ the Opus generator): EXACT core **sound** (zero false
  certificates across exhaustive sweeps), Carlisle screen **well-calibrated** (4/2000 at α=.001), Cox HR matches
  statsmodels PHReg to 5 decimals, honesty framing **clean** (no output affirms misconduct, no κ=0 clinical claim
  smuggled in). 3 meta-layer defects found and fixed (the honesty checker hardened against word-boundary /
  clause-negation / citation-context edge cases; the Carlisle κ label disambiguated). See `AUDIT.md`.

## Honest limitations
- The Carlisle test is a **statistical SCREEN**, not an exact certificate: false-positive rate ≈ α by
  construction, **inflated** by correlated covariates and stratified/cluster designs; it is **restricted to
  continuous variables** (unsound for categorical) and **excludes declared stratification factors** (Carlisle's
  own practice). It **cannot distinguish fabrication from a legitimate stratified design** — it reports the
  anomaly + benign explanations and stops.
- T-SURVIVAL/T-REPRO/T-META **reproduce** reported numbers; reproduction ≠ clinical truth or efficacy.
- Efficacy / approval / risk–benefit / causation are **κ=0** → armor + abstention (E-value for observational
  causal). TRIALGUARD never issues a clinical verdict.

## Files
`SPEC.md` (1-page spec, rail front-and-center) · `GROUNDING.md` (fetched method sources + the Carlisle
critiques/caveats) · `forensics_trial_verify.py` (⭐ Carlisle + GRIM/allocation/percentage + E-value) ·
`survival_verify.py` (KM + Cox PH) · `meta_trial_verify.py` (pool/I²/Egger + trim-and-fill) ·
`trialguard_router.py` · `selftest_all.py` (gate) · `demo_forensics/` (PREDICTION + run + RESULT.json) ·
`AUDIT.md` (cross-model red-team). Reuses `../psymetrix/forensics_verify.py` + `../psymetrix/psychometrics_verify.py`
and `../socius/repro_verify.py` + `../socius/multiverse_verify.py`.
