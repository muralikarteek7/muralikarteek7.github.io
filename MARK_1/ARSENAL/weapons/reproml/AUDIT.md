# REPRO-ML — independent cross-model audit (2026-06-20)

**Auditor:** Claude Sonnet 4.6 (cross-model, ≠ the Opus generator — never Opus-audits-Opus).
**Method:** read all source; ran `selftest_all.py` (11) + demo (7/7) green; then wrote + executed
independent adversarial Python (10 attack classes; 7 resisted, 5 real defects machine-confirmed).

## Verdict: SOUND-WITH-CAVEATS → **math is correct; 5 defects (all disclosure/coverage, no false-verdict risk) FIXED + locked**

The auditor independently re-derived the core math and it holds: **McNemar p-values match a from-scratch
re-implementation bit-for-bit** (and agree with `scipy.stats.binomtest` to the known asymptotic gap); the
**bootstrap is genuinely paired** (same resample index for both arrays); **macro_f1 matches
`sklearn.f1_score(average='macro')` exactly across 200 random trials + edge cases**; the empirical
**Type-I rate is 0.016 at α=0.05** (the AND-logic is conservative); **no κ=0 "best/SOTA" claim can pass as
machine-verified**; the contamination rate has no double-counting. None of the 5 defects can flip a verdict
to a false positive.

| # | defect | severity | fix |
|---|---|---|---|
| **A3** | the AND-logic (SIGNIFICANT requires BOTH McNemar p<α AND CI excludes zero) is conservative (Type-I-safe) but was **undocumented** → ~2% of boundary effects silently called NOT_SIGNIFICANT. | Medium | emit `mcnemar_significant`/`ci_excludes_zero`/`tests_agree` + a `disagreement_note`; document the conservatism in the ceiling note + SPEC |
| **A5** | **word-reordering** (same words shuffled) evaded both n-gram and the char-Jaccard fallback (Jaccard 0.49 < 0.8), yet the SPEC sold char-Jaccard as catching "lightly-edited copies". | Medium | added an **order-insensitive token-set Jaccard** pass (≥0.9) that catches reordering; ceiling note now states reorder is caught but rephrased/translated is still missed |
| **A6** | `contamination_report(n<10)` false-positives on common English phrases, with no guardrail. | Medium | emit a false-positive-risk **warning** for n<10; document the n=13 standard |
| **A1b** | the displayed `chi2` was rounded to 4dp but `p` came from the unrounded value → p not re-derivable from the printed statistic. | Low | report `chi2` to 8dp + a note that p is computed from the unrounded statistic |
| **A9b** | `tol=1e-3` failed a value exactly at `true+tol` (float-addition rounding); the ~0.1pp tolerance window was undocumented. | Low | `delta <= tol + 1e-9`; document the disclosed reporting-rounding window |

All fixes are in `signif_verify.py` / `contam_verify.py` / `repro_verify.py`; break-cases locked in
`selftest_all.py` (11 → **20 assertions**, all green). Demo re-ran clean.

## Attacks RESISTED (selected)
McNemar formula + p-values (independent re-impl, exact match); paired-bootstrap correctness (tighter than
an incorrectly-independent bootstrap); Type-I (0.016) + Type-II (a 10-item edge correctly SIGNIFICANT);
macro_f1 vs sklearn (200 trials, 0 disagreements; class-never-predicted / preds-only / single-class all
match); contamination rate union-counting (no double count); short-item fallback; casing evasion (caught);
the honesty rails (κ=0 "best/SOTA" → armor; `NO_OVERLAP_DETECTED != clean` stated everywhere).

## Honest residual ceiling (cannot be fixed by code, disclosed)
Rephrased/translated/paraphrased contamination (different words) still evades n-gram + char + token-set
overlap — this is the fundamental limit of overlap-based contamination detection and is stated on every
report. The weapon measures a **rate with a method label**, never a binary "clean".
