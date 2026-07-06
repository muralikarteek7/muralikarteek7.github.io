# TRIALGUARD killer-demo PREDICTIONS — committed BEFORE running (2026-06-20)

Box rule: predictions are written down before the run so the result can falsify them.
**No real trial is named or accused** — Demos A/D reproduce the literature's own GRIM
worked example and use SIMULATED trials with KNOWN ground truth (we control whether a
trial is properly randomized or fabricated), so we can measure the verifier's exact
specificity/sensitivity without touching any real author's reputation.

## Demo A — grounded / exact pieces (reproduce literature + exact checks)
| input | check | PREDICTED verdict |
|---|---|---|
| mean=5.27, n=43 | GRIM (reused) | **INCONSISTENT** (literature example) |
| mean=5.26, n=43 | GRIM (reused) | consistent |
| group sizes 30/90, ratio 1:1 | allocation-ratio (exact) | **INCONSISTENT** (benign: dropout/typo) |
| group sizes 60/60, ratio 1:1 | allocation-ratio (exact) | consistent |
| "33.3%" of n=7 | percentage->count (exact) | **INCONSISTENT** (impossible count) |

## Demo B — controlled ground-truth corpus (the cardinal soundness/calibration test)
Build 300 **properly-randomized** trials (both arms drawn from the SAME distribution,
k=8 continuous baseline variables) and 300 **fabricated too-similar** trials (an
over-balancer keeps every standardized between-group difference < ~0.05). We know the
ground truth for each, so we measure the Carlisle screen's specificity and sensitivity.

**THE CARDINAL PREDICTION (soundness / calibration): the clean-trial false-flag rate
is ~ alpha (=0.001), i.e. ≤ ~5/300 — NOT a systematic stream of false accusations.**
The Carlisle test is a *statistical screen*, not an exact certificate, so it CAN fire
by chance at rate ≈ alpha — but it must be well-calibrated, never systematically
flagging clean trials. A false-flag rate far above alpha would be a soundness bug → STOP.

- PREDICTED clean false-flag rate: **≈ 0.1% (0–5 of 300)**.
- PREDICTED fabrication catch rate (sensitivity): **> 85%** (k=8 too-similar vars push
  the Stouffer Z strongly positive). Not 100% — mild over-balancing can stay within chance.
- **PREDICTED affirms-misconduct count across ALL ~600 outputs: 0.** Every flagged
  output must carry benign explanations + false-positive modes + the inconsistency≠fraud
  ceiling. A single output that AFFIRMS misconduct is a BLOCKING defect → STOP.

## Demo C — T-META reproduction + publication-bias screen
An asymmetric body (precise studies near 0.11; small studies inflated to 0.55–0.70).
PREDICTED: **Egger flags funnel asymmetry** (small-study effect) and **trim-and-fill
imputes ≥1 missing study on the suppressed (low) side and pulls the pooled effect DOWN**
toward the null. Reported as a robustness SCREEN, never proof of suppression.

## Demo D — the false-positive guard (stratified design)
A stratified trial whose non-stratified baseline looks too-similar. PREDICTED: the
output may register the too-similar anomaly BUT (1) it carries a `design_caveat` naming
stratification as the expected cause, (2) the verdict does NOT affirm misconduct, and
(3) a declared stratification factor is EXCLUDED from the test. The screen must never
read as fraud for a legitimately stratified trial.

## Falsifiers (what would prove me wrong)
- Clean false-flag rate ≫ alpha → calibration/soundness bug → STOP and fix.
- ANY output affirms misconduct (a Carlisle/GRIM flag presented as fraud) → blocking
  honesty defect → STOP and fix.
- GRIM 5.27/43 not INCONSISTENT → arithmetic bug.
- Fabrication catch rate ≈ 0% → the screen has no power → investigate.
- Trim-and-fill moves the pooled effect the WRONG way (up, away from null) → bug.
