# P-MODEL demo PREDICTIONS — committed BEFORE running (2026-06-20)

Demo dataset: **Holzinger-Swineford 1939** (real, ships in semopy: 301 students, 9 cognitive tests x1–x9, known
3-factor structure visual/textual/speed). This is the canonical CFA teaching dataset — using it is grounded and
non-accusatory (no real modern paper's claim is being judged).

The point of the demo: show P-MODEL fits the TRUE structure, CATCHES a misspecified alternative, and reports
fit HONESTLY against grounded cutoffs (including the honest fact that even the correct model is only
"acceptable," not strict-good-fit).

## Committed predictions
1. **3-factor CFA** (visual=~x1+x2+x3; textual=~x4+x5+x6; speed=~x7+x8+x9): I predict
   **CFI ≈ 0.93, TLI ≈ 0.90, RMSEA ≈ 0.09, SRMR ≈ 0.065** → verdict **"acceptable" (two-tier), NOT strict
   Hu & Bentler good-fit** (CFI<.95 and RMSEA>.06). This is the grounded lavaan reference and the honest lesson:
   the textbook-correct model does not clear the strict cutoffs.
2. **1-factor CFA** (all 9 on one factor): I predict **POOR fit** — CFI well below .90, RMSEA well above .10.
3. **Model comparison:** the data **prefer the 3-factor model**, ΔCFI > 0.10 (large). This is the discriminating
   test the verifier exists to make.
4. **EFA parallel analysis:** I predict it recovers **3 factors** (matching the known structure) — though I flag
   uncertainty: real cognitive data has correlated factors, so PA could return 2 or 3. Committed point estimate: **3**.
5. **Reliability (omega/alpha) of the full 9-item scale:** since the 9 items span 3 distinct factors (NOT
   unidimensional), I predict a **moderate omega (~0.7–0.8)** and that treating all 9 as one scale is a
   reliability mistake the per-factor structure should expose.

## Falsifiers
- If the 1-factor model fits as well as the 3-factor (ΔCFI≈0) → the verifier/data contradict the known
  structure → investigate (would be a bug or a dataset surprise).
- If the 3-factor model is reported as strict "good" fit → the cutoff logic is wrong (it should say "acceptable").
- If SRMR ≠ ~0.065 (lavaan reference) → SRMR computation bug.
