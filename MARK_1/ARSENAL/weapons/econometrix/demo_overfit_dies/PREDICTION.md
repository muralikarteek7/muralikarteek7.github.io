# COMMITTED PREDICTION — the C14 "dies under stress" backtest demo
*Written BEFORE running the demo. Frozen. The point of the box is that some of these predictions will
be WRONG — that is the method working, not failing. This is the headline ECONOMETRIX demo: a plausible
trading rule with a STRONG in-sample Sharpe that DIES out-of-sample under the Deflated Sharpe gate.*

**The setup.** Real daily price history (Yahoo Finance, downloaded 2026-06-07) for **SPY, AAPL, BTC-USD,
RELIANCE_NS**. We search a LARGE grid of SMA-crossover (fast, slow) rules — `N = 38` configurations —
and pick the one with the best **in-sample** Sharpe (the single most gameable number in finance, the
C14 trap). Then we judge it the ONLY honest way: **walk-forward out-of-sample, net of the sourced
transaction-cost model** (`Artifacts/trading/real_world.py`), and apply the **Deflated Sharpe Ratio**
(Bailey & López de Prado 2014) with the TRUE trial count (a large SMA grid, `N ≈ 40` configurations). Edge is reported only if
`DSR > 0.95` **and** OOS Sharpe > 0; else **ABSTAIN**.

| # | Question | Committed prediction | Why |
|---|---|---|---|
| P1 | Does grid search find an attractive **in-sample** Sharpe? | **YES** — best in-sample annualized Sharpe **> 0.6** on a majority of the 4 assets (some > 1.0). | With ~40 trials on ~1500 bars, the best-of-N in-sample number is inflated by selection — that is exactly the trap. |
| P2 | Does that rule **survive walk-forward OOS**? | **NO for the majority** — mean walk-forward OOS Sharpe collapses far below the in-sample number; **≥3 of 4 assets** show OOS ≪ in-sample. | Out-of-sample is where overfit dies; the in-sample edge was mostly selection. |
| P3 | Does the **Deflated Sharpe Ratio** gate the edge? | **ABSTAIN on ≥3 of 4 assets** (`DSR < 0.95`). At most 1 asset *might* clear, and I am NOT confident any will. | Deflating the best-of-~40 by the expected-max-Sharpe benchmark should sink a luck-driven winner. |
| P4 | **Headline:** in-sample says "edge," the gate says — | **"DIES UNDER STRESS / ABSTAIN"** is the dominant verdict across assets. | The whole point of the weapon: an in-sample score is never the verdict. |
| P5 | Does the gate **CATCH an injected look-ahead bug**? | **YES** — a strategy variant that peeks at tomorrow's price inflates the in-sample Sharpe dramatically, and `detect_lookahead` flags it (leaked=True) while the clean rule is not flagged. | The leakage probe perturbs the future and checks the past signal; a future-peeking rule must change. |
| P6 | Honest miss I'm allowing for | One asset (most likely **SPY**, a trending broad index) *could* show a positive OOS Sharpe — but I predict even then DSR likely keeps it below the 0.95 bar. If any asset clears DSR, I will report it plainly as "survived THIS backtest" with the explicit caveat **survival ≠ future profit**. | Broad equity indices have a real long-run drift; a long/flat trend rule can ride it. But surviving a backtest is not a forecast. |

**Overall predicted ECONOMETRIX verdict:** the strong in-sample Sharpe is an artifact of searching 38
rules; under walk-forward + Deflated Sharpe net of costs, the "edge" **dies / ABSTAIN** on the majority
of assets. The look-ahead variant is caught by the leakage probe.

**Honesty note (binding):** A backtest is NOT a forecast. ECONOMETRIX never says "this will make money"
or "this rule is good going forward." Even an asset that *survives* this historical stress test has only
demonstrated **past survival under stress**, not future profit — that (the unseen future) is κ=0 →
armor + abstain. "Dies under the Deflated Sharpe" is the valuable output; it is what stops a gameable
in-sample number from being mistaken for an edge.
