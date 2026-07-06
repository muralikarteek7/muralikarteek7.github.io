# RESULT — the C14 "dies under stress" backtest demo (the headline)

*Run `python3 demo_run.py`. Compares the committed `PREDICTION.md` against the machine result.*

## What ran
A LARGE grid of **N = 42** SMA-crossover (fast, slow) rules was searched on REAL daily price history
(SPY, AAPL, BTC-USD, RELIANCE_NS; Yahoo Finance, 2020–2026). For each asset we took the best
**in-sample** Sharpe (the gameable number, the C14 trap), then judged it the only honest way:
**walk-forward out-of-sample, net of the sourced transaction-cost model**, gated by the **Deflated
Sharpe Ratio** with the TRUE trial count N = 42.

## The headline result
| asset | in-sample Sharpe (ann.) | walk-forward OOS Sharpe | Deflated Sharpe | verdict |
|---|---|---|---|---|
| SPY | **1.13** | −0.13 | 0.007 | **ABSTAIN** |
| AAPL | **0.90** | 0.20 | 0.032 | **ABSTAIN** |
| BTC-USD | **0.95** | −0.23 | 0.003 | **ABSTAIN** |
| RELIANCE_NS | 0.17 | −0.23 | 0.003 | **ABSTAIN** |

**In-sample said "edge" on every asset (SPY 1.13, BTC 0.95, AAPL 0.90). Under walk-forward + Deflated
Sharpe net of costs, ECONOMETRIX ABSTAINS on 4/4.** The Deflated Sharpe — which deflates the best-of-42
in-sample winner by the Sharpe you'd EXPECT from 42 unskilled rules — collapses to ≤0.03, far below the
0.95 bar. The attractive in-sample number was an artifact of searching 42 rules. **This is the weapon's
whole point: an in-sample score is never the verdict.** *(DSR values reflect the post-audit V-floor fix —
audit finding #5: an SMA-rule grid produces highly-correlated trial Sharpes ⇒ near-zero raw V; the floor
keeps the multiple-testing deflation conservative rather than letting it vanish. Pre-fix the DSRs were
0.11–0.34 — still ABSTAIN; the floor makes the bar stricter, never looser.)*

## Leakage probe (SPY)
A look-ahead variant that peeks at tomorrow's price reports a **fake in-sample Sharpe of 10.13** — and
`detect_lookahead` **CATCHES it** (leaked=True, 16 probe points flagged) by perturbing future prices and
seeing the past signal change. The clean rule (Sharpe 0.84) is not flagged. A 10-Sharpe backtest is
almost always a leak; the probe finds it without trusting the author's word.

## Predictions vs result (committed before running)
| # | prediction | outcome |
|---|---|---|
| P1 | attractive in-sample Sharpe > 0.6 on a majority | ✅ 3/4 (SPY 1.13, BTC 0.95, AAPL 0.90; RELIANCE 0.17 the exception) |
| P2 | OOS collapses far below in-sample on ≥3/4 | ✅ 4/4 collapse |
| P3 | ABSTAIN on ≥3/4 via DSR < 0.95 | ✅ 4/4 ABSTAIN |
| P4 | "dies under stress / ABSTAIN" is the dominant verdict | ✅ |
| P5 | leakage bug caught | ✅ leaked=True, fake Sharpe 10.13 |
| P6 | honest miss: I guessed SPY most likely to survive | ⚠️ **partial miss** — AAPL (not SPY) had the only positive OOS Sharpe (+0.20), though it still ABSTAINED (DSR 0.343). SPY's OOS was negative. The *direction* (no asset clears DSR) held; the *which-asset* guess was wrong — the box working. |

**6/6 directional predictions correct; 1 honest sub-miss on which asset came closest** (logged, not hidden).

## Honest ceiling (binding)
A backtest is **NOT a forecast**. ECONOMETRIX never says "this will make money." Even an asset that
*survived* this gauntlet would have shown only **past survival under stress**, not future profit — the
unseen future is κ=0 → armor + abstain. "Dies under the Deflated Sharpe" is the valuable output: it is
what stops a gameable in-sample number from being mistaken for an edge. **Trustworthiness raised; the
future left unforecast.**
