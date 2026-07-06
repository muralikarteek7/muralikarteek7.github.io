# REPRO-ML / BENCHWATCH — ML-eval reproducibility weapon (Weapon #8, CS_ENG)

A mixed-κ "reproduce-and-stress" weapon for ML evaluation rigor. **A benchmark number is never a capability.**

## Sub-weapons
- **R-REPRO (κ≈0.7)** — recompute a reported metric (accuracy / macro-F1) from open predictions+labels within tolerance. Reproduction = recompute, not re-quote.
- **R-CONTAM (κ≈0.8)** ⭐ — measure train/test overlap: **13-gram word collision** (GPT-3/Brown 2020 decontam convention) + **char-5gram Jaccard near-dup** + an **order-insensitive token-set Jaccard** (catches word-reordering). Reported as a **rate + method label**.
- **R-SIGNIF (κ≈0.9)** — is an A>B gap real? **McNemar** (paired, Dietterich 1998) + **paired bootstrap CI**, **Bonferroni** for k comparisons.
- **κ=0 residue** → **armor**: "X is best / SOTA / most capable" is not machine-checkable → ground or abstain.

## Run
```
python3 selftest_all.py                     # gate: 20 assertions (the 4 mandatory + hardening + 5 audit regressions)
python3 contam_verify.py / signif_verify.py / repro_verify.py   # per-verifier smoke
python3 reproml_router.py                    # routing smoke
python3 demo_reproml/run_reproml.py          # real sklearn `digits` + contamination headline; all predictions matched
```
Demo result: LogReg 0.954 / shallow-DT 0.441 on digits both **REPRODUCE**; an inflated number is
flagged; contamination rate goes **0.0 → 0.5** when 3/6 eval items are leaked into train; the real
LogReg–DT gap is **SIGNIFICANT** (p≈4e-60, CI [0.47,0.56]) while a ~0.6pp gap on N=500 is **NOT**;
"LogReg is best" routes to **armor**.

## Ceiling (honesty — non-waivable)
- **Benchmark ≠ capability** — never crown a SOTA/best/most-capable; that's κ=0 → armor.
- **Contamination is a measured rate, not a verdict** — `NO_OVERLAP_DETECTED` ≠ "clean": pure n-gram
  misses rephrased/translated leakage. Always reported with its method label.
- **Significance with CIs + multiple-comparison correction** — no bare point-rank leaderboards.
  `NOT_SIGNIFICANT` means the data can't distinguish the models, not that they're equal.
- **Reproduction = recompute from artifacts**, not re-quote.
- A weapon ADDED = **capability EXPANSION, NOT a ≥10% promotion**. Can also harden the box's own
  hidden-test hygiene (the v5 contamination gate).
