# REPRO-ML demo — committed PREDICTIONS (written BEFORE running)

Real open dataset: **sklearn `load_digits`** (1797 samples, 10 classes), a fixed 70/30 split (seed 0).
Two real classifiers: **Logistic Regression** vs a **shallow Decision Tree (max_depth=3)**. Plus
controlled synthetic cases for the contamination headline and the significance floor.

| # | piece | setup | PREDICTED verdict |
|---|---|---|---|
| 1 | **R-REPRO** | report each model's test accuracy, recompute from its predictions (tol 1e-3) | **both REPRODUCED** |
| 2 | **R-REPRO (negative)** | report LogReg accuracy inflated by +0.10 | **DOES_NOT_REPRODUCE** |
| 3 | **R-CONTAM clean** | eval text set vs an unrelated train corpus, 13-gram | **NO_OVERLAP_DETECTED, rate 0.0** |
| 4 | **R-CONTAM headline** ⭐ | inject 3 of 6 eval items verbatim into the train corpus, 13-gram | **CONTAMINATION_DETECTED, rate 0.5** |
| 5 | **R-SIGNIF real gap** | LogReg vs shallow DT on digits (same test set), paired McNemar + bootstrap CI | **SIGNIFICANT_DIFFERENCE** (shallow DT is much weaker) |
| 6 | **R-SIGNIF noise floor** | controlled ~0.6pp gap on N=500 | **NOT_SIGNIFICANT** |
| 7 | **κ=0 residue** | "LogReg is the best model / production-ready" | **routed to ARMOR (abstain), NOT crowned** |

Honesty: the contamination in #4 is injected BY US to test the detector; a real number on a
contaminated benchmark proves nothing. We never say "LogReg is best" — that is κ=0.
