# ECONOMETRIX — κ-aware empirical-rigor engine for economics & finance
*A v5 "ARMOR + WEAPONS" weapon. The FIRST **guarded-κ** weapon. Plugs into the `Next/BOX_V5.md`
when/where router. Clones SOCIUS's mixed-κ shape; reuses its multiverse/repro verifiers.*

## One line
Given a market-edge or economic-causal claim with data, ECONOMETRIX **chooses which rigor checks
apply**, runs the machine-checkable ones (κ>0) through **frozen, adversarially self-tested verifiers**,
**grounds or abstains** on the judgment ones (κ=0), and reports — honestly — what survived and **what
died under stress**. It raises *trustworthiness* (OOS survival + identification diagnostics). **It does
not, and cannot, predict the future or manufacture truth.**

Finance/econ is a **low, GUARDED-κ field (≈0.4–0.6)**: there is no cheap exact verifier for "this edge
is real" or "this policy caused that outcome." So ECONOMETRIX is **not** a record-breaking construction
engine. Its value is catching the field's characteristic failure modes — **backtest overfitting,
look-ahead leakage, multiple testing, fragile causal identification** — and being honest about the κ=0
residue (forecasts, "should" questions, market direction → armor + abstain).

**The cardinal rule (C14): an in-sample / single-split / backtest score is NEVER the verdict.** It is
the single most gameable number in finance. The verdict is the walk-forward OOS Deflated Sharpe net of
costs — and even that certifies *past survival under stress*, never future profit.

## Files
| file | what |
|---|---|
| `SPEC.md` | the one-page spec (sub-weapons, κ table, the no-in-sample-verdict rule, honesty rails) |
| `GROUNDING.md` | the fetched method SOTA (DSR/PSR, purged CV, McCrary, weak-IV F, Oster δ, E-value) — formulas grounded, not asserted |
| `econometrix_router.py` | the chooser: task → which sub-weapons fire (κ-labelled); forecast/"should" → armor |
| `backtest_verify.py` | **E-BACKTEST** ⭐ — walk-forward OOS + **Deflated Sharpe Ratio** + costs + a frozen **look-ahead detector** (κ≈0.4 guarded) |
| `causal_verify.py` | **E-CAUSAL** — DiD pre-trends / McCrary density / weak-IV F / Oster δ / E-value (κ≈0.5) |
| (imported) `../socius/multiverse_verify.py` | **E-ROBUST** — specification-curve / multiverse robustness (κ=1, reused) |
| (imported) `../socius/repro_verify.py` | **E-REPRO** — reproduction within tolerance (κ=1, reused) |
| `selftest_all.py` | the **frozen-verifier gate** — every verifier must pass good AND catch broken; exits 0 or nothing is trusted |
| `demo_overfit_dies/` | killer demo #1 — the C14 headline: a strong in-sample Sharpe that DIES under walk-forward + DSR (ABSTAIN 4/4) + a caught look-ahead bug |
| `demo_causal/` | killer demo #2 — pre-trends placebo catches a confounded DiD + Oster δ + E-value + a real Card-Krueger reproduction |
| `AUDIT.md` | independent cross-model red-team (auditor ≠ generator) |

## Run it
```bash
cd MARK_1/ARSENAL/weapons/econometrix
python3 selftest_all.py                  # the GATE — must print "OK" or NOTHING is trusted
python3 econometrix_router.py selftest    # routing logic
python3 demo_overfit_dies/demo_run.py     # the headline: dies under stress
python3 demo_causal/demo_run.py           # pre-trends placebo + sensitivity + reproduction
```
Dependencies: `numpy`, `scipy`, `pandas`, `statsmodels`. Reuses `Artifacts/trading/real_world.py`
(real data + the sourced cost model) and `../socius/` verifiers.

## The killer demos, in one breath
1. **C14 / dies-under-stress.** 42 SMA rules searched on real SPY/AAPL/BTC/RELIANCE data; the best
   in-sample Sharpe (1.13 on SPY) **collapses to DSR ≈ 0.1–0.3 out-of-sample net of costs → ABSTAIN on
   4/4**. A look-ahead variant's fake **10.1 Sharpe** is caught by the leakage probe. 6/6 directional
   predictions correct.
2. **E-CAUSAL.** A confounded DiD with **no true effect** but a naive estimate of **+3.76 (p≈1e-31)** is
   **FLAGGED** by the pre-trends placebo (p≈1e-53); a clean design passes and carries an E-value of 7.49;
   Oster δ separates robust (12.5) from fragile (0.43); the real Card-Krueger DiD **+2.76** reproduces.
   7/7 committed predictions correct.

## Honest ceiling (binding, stated every run)
- **In-sample / single-split is never the verdict** — only walk-forward OOS, multiple-testing-corrected,
  net of costs. Edge that flips OOS ⇒ **ABSTAIN**.
- **A backtest is not a forecast** — survival under historical stress ≠ future profit; never predict markets.
- **Causal claims carry their assumptions** — testable diagnostics AND a sensitivity number; never a bare
  "X caused Y." Post-period parallel trends / the exclusion restriction stay untestable.
- **Reproduction is labelled reproduction** (source+date). A result that DIES is reported plainly as the
  valuable finding.
- **κ=0 stays armor:** "should the Fed cut," "will this stock rise," "is this policy good" → ground + abstain.
- **Inherit C14 explicitly:** a gameable proxy (in-sample Sharpe, an LLM "this looks profitable") does NOT raise κ.

## Status (honest)
A **new weapon ADDED** to the v5 box = **capability expansion** (a problem class — quant-finance &
causal-econ rigor — the box could not previously serve). **NOT a ≥10% A/B promotion**: there is no
shared arena against a prior ECONOMETRIX, so the ≥10% capability ratchet is untouched (stays open at v3).
See `../../../../MARK_0/02_ladder_history/Legacy/EVOLUTION_LOG.md` and `../../../SPEC/BOX_V5.md`.
