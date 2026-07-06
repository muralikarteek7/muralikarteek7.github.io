# Killer-demo PREDICTIONS — committed BEFORE running (2026-06-20)

Box rule: predictions are written down before the run so the result can falsify them.
The demo runs P-FORENSICS on (A) the method papers' OWN published worked examples
(grounded, non-accusatory) and (B) a controlled ground-truth corpus where we KNOW the
true mean/SD (so we can measure the verifier's exact sensitivity/specificity).

## Demo A — reproduce the literature's published worked examples (grounded)
| input | source | PREDICTED verdict |
|---|---|---|
| mean=5.27, n=43 | Brown & Heathers 2017 (GRIM) | **GRIM-INCONSISTENT** |
| mean=5.26, n=43 | (achievable neighbour) | GRIM-consistent |
| mean=5.90, n=40, 3 items | (multi-item granularity) | GRIM-consistent |
| mean=3.44, SD=2.47, n=18 | Anaya/Allard GRIMMER example | **GRIMMER-INCONSISTENT (parity)** |

## Demo B — controlled ground-truth corpus (the exact sens/spec test)
Build 400 fake "reported" rows from REAL integer Likert (1–7) samples, n drawn in
[20,80], means/SDs rounded to 2 decimals. Half the rows are reported CORRECTLY; half
get a planted transcription typo (mean's last decimal shifted by ±0.01).

**The cardinal prediction (soundness): SPECIFICITY = 100% — ZERO false positives.**
A correctly-reported statistic must NEVER be flagged. A false positive here would be a
false accusation; the verifier is built to be sound (it only flags the provably
impossible), so I predict not a single clean row is flagged.

**Sensitivity (incompleteness is expected and honest):** GRIM cannot catch every typo —
a perturbed mean is only caught when it lands on a non-achievable value. The detection
rate for a random ±0.01 typo at 2 decimals, single item, is ≈ `1 − N_eff/10^D = 1 − n/100`.
- PREDICTED overall sensitivity: **strictly between 0% and 100%**, in the **~40–70%** band
  (since n averages ~50 → caught fraction ≈ 1 − 0.5 = 0.5), and **monotonically decreasing
  in n** (small-n rows caught more often than large-n rows).
- This incompleteness is the honest ceiling: GRIM is SOUND (no false positives) but not
  COMPLETE (misses typos that happen to land on achievable values). That mirrors the
  cap-set verifier: it certifies, it does not catch everything.

## Falsifiers (what would prove me wrong)
- Any clean row flagged inconsistent → soundness bug → STOP and fix (specificity < 100%).
- Demo A verdicts not matching the literature → arithmetic bug.
- Sensitivity at 100% → suspicious (would contradict GRIM's known power limit) → investigate.
