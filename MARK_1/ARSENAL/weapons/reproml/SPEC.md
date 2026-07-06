# REPRO-ML / BENCHWATCH — SPEC (Weapon #8, CS_ENG eval-rigor facility)

*Mixed-κ "reproduce-and-stress" weapon for ML evaluation rigor. Written 2026-06-20, box-style.
R-REPRO reuses the SOCIUS reproduction shape; the genuinely NEW pieces are R-CONTAM + R-SIGNIF.*

## 1. WHAT IT IS (one line)
Given an ML result/claim, route the **κ>0 pieces** (re-run the eval; detect train/test contamination;
test the significance of a model comparison) to frozen verifiers, and the **κ=0 pieces** ("X is
best / SOTA / more capable") to **armor (ground + abstain)**. A benchmark number is never a capability.

## 2. WHAT IT IS NOT (honesty rails — non-waivable)
- **NOT a SOTA-crowner.** "Model X is best / most capable" is **κ=0** (Goodhart; contamination;
  cherry-picking) → armor + abstain. REPRO-ML reports reproduction + contamination + significance,
  never "X is best."
- **NOT contamination-blind.** The dominant ML-eval failure is the model having SEEN the test set. A
  reproduced number on a contaminated benchmark proves nothing.
- **NOT a significance-free leaderboard.** A 0.3-pt gap on a 500-item test set is usually noise →
  paired significance + CIs required; report intervals, not bare point ranks.
- **NOT smarter than the model** — organized eval rigor, not capability.

## 3. THE SUB-WEAPONS (mixed-κ)
| sub-weapon | κ | what it checks | verifier |
|---|---|---|---|
| **R-REPRO** | ≈0.7 | does the reported metric reproduce from open predictions/data? | recompute the metric from artifacts within tolerance (re-run, not re-quote) |
| **R-CONTAM** ⭐ | ≈0.8 | did the eval set leak into training? | **n-gram overlap (13-gram, GPT-3/Brown 2020 decontam) + char-jaccard near-dup detection** between train corpus and eval set; report contamination RATE + method label |
| **R-SIGNIF** | ≈0.9 | is the A>B gap real, not noise? | **McNemar (paired, Dietterich 1998) + paired bootstrap CI**; Bonferroni multiple-comparison correction across many models |
| **κ=0 residue** | 0 | "X is best / SOTA / more capable / production-ready" | **ARMOR** — ground or abstain; benchmark ≠ capability |

## 4. KEY ENGINEERING PROBLEM — measure contamination + significance HONESTLY
1. **Contamination = overlap, reported as a RATE with a method label** (n-gram order, dedup threshold).
   Never claim "clean" — claim "X% of eval items have a 13-gram collision with train; Y near-dups."
   **Absence of detected overlap ≠ proof of no contamination** (stated on every report).
2. **Significance = paired test + CI**, never a bare point gap; Bonferroni-correct for k models compared.
3. **Reproduction = recompute from artifacts**, not re-quote; a metric you can't recompute is unverified.

## 5. GATE SELF-TESTS (non-waivable)
(a) PASS a faithfully-reproduced clean eval; (b) **CATCH a contaminated eval** (inject test items into
"train" → R-CONTAM flags it); (c) **CALL a noise-level gap insignificant** (tiny gap, small N → not
significant); (d) **flag an unreproducible metric** (predictions don't recompute to the reported number).

## 6. ROUTER (`reproml_router.py`)
reported metric + artifacts → R-REPRO · train+eval sets → R-CONTAM · model comparison → R-SIGNIF ·
"is X best/capable" → κ=0 armor. Each routed piece is labeled with its κ; nothing κ=0 is presented as
machine-verified. Execute, never vote.

## 7. CEILING
Reproduction ≠ a SOTA claim. Contamination is a measured rate, not a verdict of cheating ("no overlap
detected" ≠ "clean"). Significance carries CIs + multiple-comparison correction. κ=0 "best / most
capable" → armor. A weapon ADDED = capability EXPANSION, NOT a ≥10% promotion.
