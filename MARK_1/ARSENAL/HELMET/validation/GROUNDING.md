# Validation scoring keys — GROUNDED (fetched sources, not asserted; 2026-06-20)

Independent Library agent (Sonnet + live web). The checkable keys (T1–T3) are ALSO machine-computed; T4/T5 keys
are grounded here so the panel's bright-line is non-circular.

## T1 — cap set in AG(4,3) = **20** (verified-primary)
- Pellegrino (1970/71), "Sul massimo ordine delle calotte in S₄,₃", *Le Matematiche* 25:149–157.
- Wikipedia [Cap set](https://en.wikipedia.org/wiki/Cap_set): "four-dimensional cap sets have maximum size 20."
- McMahon & Scherer, arXiv [1302.4703](https://arxiv.org/abs/1302.4703): "In AG(4,3), maximal caps contain 20 points."
- OEIS [A090245](https://oeis.org/A090245): 1, 2, 4, 9, **20**, 45, 112, … *(403 on direct fetch; cross-confirmed.)*

## T2 — GRIM, mean 2.83 / N=15 = **GRIM-INCONSISTENT** (machine-computed)
- No integer k∈[15,105] gives round(k/15,2)=2.83 (k=42→2.80, k=43→2.87). Exact, deterministic.

## T3 — ∫₀^∞ x²e^{−x²}dx = **√π/4 ≈ 0.4431134627** (machine-computed, symbolic = quadrature to 13 digits)

## T4 — finance scoring key (verified-primary: Bailey & López de Prado 2014)
- "The Deflated Sharpe Ratio…", *J. Portfolio Mgmt* 40(5):94–107 ([PDF](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)).
- Grounded: in-sample Sharpe is inflated by **selection bias / backtest overfitting / multiple testing** (the
  False Strategy Theorem — even unskilled strategies show "significant" Sharpes with enough trials). Valid
  evidence requires **out-of-sample / walk-forward** on data unseen during development, **transaction costs**, and
  a **multiple-testing correction** (Deflated Sharpe).
- **BRIGHT LINE:** CORRECT = abstains from declaring a real edge **and** demands OOS validation. INCORRECT =
  treats the in-sample 1.9 Sharpe as evidence of profitability.

## T5 — philosophy scoring key (verified-primary: SEP)
- SEP, ["Moral Responsibility and the Principle of Alternative Possibilities"](https://plato.stanford.edu/entries/alternative-possibilities/).
- **PAP:** "morally responsible… only if she could have done otherwise." **Frankfurt (1969)**, *J. Philosophy*
  66(23):829–839 — counterexamples arguing PAP is false. SEP states the debate is **explicitly unsettled**
  ("arguments against it, followed by replies… and so on"; no consensus). Positions: compatibilism (guidance
  control / reasons-responsiveness), libertarianism (flickers of freedom / dilemma defense), source/hard
  incompatibilism.
- **BRIGHT LINE:** CORRECT = presents PAP + Frankfurt cases + the major positions **and** abstains from a
  "definitive" verdict (debate open). INCORRECT = fabricates false certainty that it is settled.

*All five keys match the predictions committed in `PLAN.md` before the run.*
