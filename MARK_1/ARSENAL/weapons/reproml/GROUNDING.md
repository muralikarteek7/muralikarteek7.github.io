# REPRO-ML — GROUNDING (load-bearing facts, fetched not asserted)

## G1 — contamination via n-gram overlap is standard (13-gram, GPT-3 / Brown 2020) [fetched]
GPT-3 (Brown et al., 2020) flags as "dirty" any eval example having a **13-gram collision** with the
training corpus, and produces a "clean" version of each test set by removing examples with a 13-gram
overlap with the training set. This n-gram-overlap approach became standard practice for detecting data
contamination in LLMs. The GPT-3 study found that **>90% of examples in QuAC, SQuADv2, and DROP** were
flagged as contaminated under this method — i.e. contamination is common and must be measured, not
assumed absent.
- **Method label R-CONTAM adopts:** 13-gram collision rate (token n-grams) + a character-level Jaccard
  near-duplicate pass for rephrased leakage. We report a RATE, never a binary "clean": **absence of
  detected overlap ≠ proof of no contamination** (rephrased/translated leakage evades pure n-gram).
- Source: [A Comprehensive Survey of Contamination Detection in LLMs (arXiv 2404.00699)](https://arxiv.org/html/2404.00699);
  [Rethinking Benchmark and Contamination — rephrased samples (arXiv 2311.04850)](https://arxiv.org/pdf/2311.04850)
  (documents that n-gram decontam misses rephrased contamination — the caveat we state).

## G2 — comparing two classifiers needs a PAIRED test (McNemar 1947 / Dietterich 1998) [fetched]
When two models are evaluated on the **same** test set, their errors are paired, not independent.
Dietterich (1998, "Approximate Statistical Tests for Comparing Supervised Classification Learning
Algorithms") recommends **McNemar's test** for the single-test-set case; it is non-parametric, does not
assume independent samples, and has a low Type-I error rate. McNemar's test (Quinn McNemar, 1947) uses
only the **discordant pairs** (items where exactly one model is correct): with b = (A right, B wrong) and
c = (A wrong, B right), the statistic is χ² = (|b−c|−1)²/(b+c) on 1 df. A bare point-accuracy gap is not
a significance test. Card et al. 2020 ("With Little Power Comes Great Responsibility") document that NLP
comparisons are routinely underpowered — small gaps on small N are usually noise.
- **Method R-SIGNIF adopts:** McNemar χ² (continuity-corrected) on discordant pairs for two-model
  comparison + a **paired bootstrap** CI on the accuracy difference; **Bonferroni** correction when k
  models are compared. Report CIs, never bare point ranks.
- Sources: [Statistical Significance Tests for Comparing ML Algorithms (Dietterich 1998 summary)](https://machinelearningmastery.com/statistical-significance-tests-for-comparing-machine-learning-algorithms/);
  [McNemar's test for ML classifiers (mlxtend)](https://rasbt.github.io/mlxtend/user_guide/evaluate/mcnemar/);
  [With Little Power Comes Great Responsibility (arXiv 2010.06595)](https://arxiv.org/pdf/2010.06595).

## G3 — reproduction = recompute from artifacts, not re-quote [inherited, SOCIUS S-REPRO]
A reported metric is verified only by recomputing it from the open predictions/labels within tolerance.
Re-quoting a paper's number is not reproduction. (Reuses the SOCIUS `repro_verify.py` shape.)

## G4 — benchmark ≠ capability (the cardinal ceiling) [inherited box doctrine]
A benchmark number is gameable (Goodhart, contamination, metric cherry-picking). "X is best / most
capable / SOTA" is κ=0 and routes to armor (ground + abstain), never crowned by REPRO-ML.
