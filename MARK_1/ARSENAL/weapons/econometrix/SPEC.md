# ECONOMETRIX — a κ-aware empirical-rigor engine for economics & finance (v5 weapon)
*One-page spec. Home: `Expanding_Frontiers/weapons/econometrix/`. The FIRST **guarded-κ** weapon.
Registered in `Next/BOX_V5.md`. Clones SOCIUS's mixed-κ internal-routing shape; reuses its
multiverse/repro verifiers; builds the OOS gauntlet on `Artifacts/trading/real_world.py`.*

## What it is (and is not)
ECONOMETRIX is the v5 weapon for the **economics & finance** problem class. Finance/econ is a
**LOW, GUARDED-κ field (≈0.4–0.6)**: there is **no cheap exact verifier for "this edge is real" or
"this policy caused that outcome,"** because the future is unseen and identification rests on
assumptions. So ECONOMETRIX does **NOT certify truth** and is **NOT a construction engine** (there is
no record to break). It **stress-tests** a market-edge or causal claim: does the edge survive
**out-of-sample / walk-forward, net of costs, multiple-testing-corrected**? does the causal effect
survive **placebo / pre-trends / sensitivity-to-unobservables**?

**The cardinal rule (C14 trap): an in-sample / single-split / backtest score is NEVER the verdict.**
In-sample Sharpe is the single most gameable number in finance. The verdict is the **walk-forward OOS
Deflated Sharpe net of costs** — and even that certifies *past survival under stress*, never future
profit. **A claim that DIES under these checks is the primary valuable output** (SOCIUS's doctrine).

**IS NOT, explicitly:** not a backtest-blesser; not a forecaster (a backtest is not a prediction —
"will it make money / will rates rise" is **κ=0 → armor + abstain**); not a causal oracle (designs
identify an effect *only under assumptions* — testable ones get diagnostics, untestable ones get a
sensitivity number, never a bare causal claim); not smarter than the model — it is organized rigor.

## The sub-weapons (frozen verifier per κ>0; armor where κ=0)
| sub-weapon | fires when | κ | frozen verifier (self-tested to FAIL on broken input) | file |
|---|---|---|---|---|
| **E-BACKTEST** ⭐ | a trading/market-edge claim with price data | ≈0.4 *guarded* | **walk-forward OOS** (no leakage; purge/embargo aware) + **Deflated Sharpe Ratio** (Bailey & López de Prado 2014 — corrects multiple-testing + skew/kurtosis) + **net of transaction costs**. In-sample is NEVER the verdict; DSR>0.95 AND OOS>0 net ⇒ edge, else ABSTAIN | `backtest_verify.py` |
| **E-CAUSAL** | a quasi-experimental causal claim (DiD/RDD/IV) from observational data | ≈0.5 | **testable**: DiD pre-trends/placebo joint test, RDD **McCrary** density + bandwidth sensitivity, IV **first-stage F** (Stock–Yogo weak-instrument); **untestable** → **sensitivity** (E-value, Oster δ). Reports diagnostics + a sensitivity number, never a bare "X caused Y" | `causal_verify.py` |
| **E-ROBUST** (shared) | the result rests on defensible-but-arbitrary analytic choices | 1 | **specification-curve / multiverse** across the full grid (reuse `socius/multiverse_verify.py`) | imports `socius/multiverse_verify.py` |
| **E-REPRO** (shared) | a published economic statistic has open data+code | 1 | re-run pipeline → matches reported statistic within tol (reuse `socius/repro_verify.py`) | imports `socius/repro_verify.py` |
| **κ=0 residue** | forecast the future; "should" policy; market direction | 0 | **ARMOR** — ground every empirical sub-claim or abstain; never fabricate a forecast | router → armor |

**Genuinely NEW vs SOCIUS:** E-BACKTEST (finance OOS gauntlet) + E-CAUSAL (econometric identification).
E-ROBUST / E-REPRO **reuse** SOCIUS's frozen verifiers (imported + credited, not rebuilt).

## The key engineering problem — defeat overfit, leakage, multiple testing
The frozen verifiers are built FIRST, each able to FAIL:
1. **No in-sample verdicts.** E-BACKTEST refuses any edge on the fitting window; the verdict is the
   walk-forward OOS only. A high in-sample Sharpe with no OOS survival ⇒ **ABSTAIN**.
2. **Multiple-testing correction.** If many rules/params were tried, the best in-sample Sharpe is
   inflated → apply the **Deflated Sharpe Ratio** (needs #trials N, skew, kurtosis, sample length T).
   Under-counting N is the classic cheat → the auditor checks it; ECONOMETRIX takes N from the *actual*
   search grid size, not "1".
3. **Leakage / look-ahead guards.** Signals use only past bars; walk-forward (purge/embargo aware);
   costs netted. A leak that inflates OOS must be CATCHABLE (the gate self-test injects one).
4. **Causal assumption checks.** Run the testable diagnostics; for untestable assumptions report a
   **sensitivity number** (how strong an unobserved confounder must be to overturn the result).

**Gate self-tests (non-waivable, `selftest_all.py`):** the gate must (a) **PASS** a genuine
OOS-surviving edge / a well-identified effect, (b) **KILL** an over-fit rule (strong in-sample, no OOS,
DSR≈0), (c) **CATCH** a leakage/look-ahead bug (inflated OOS from future data), (d) **flag** a DiD whose
pre-trends FAIL / an IV with a weak first stage. A gate that catches all four is trustworthy.

## The router (`econometrix_router.py`, cloned from `socius_router.py`)
Reads structured task booleans, fires the κ>0 sub-weapons whose preconditions hold, routes κ=0 to armor:
- market-edge + price-data → **E-BACKTEST** · quasi-experimental causal claim → **E-CAUSAL**
- many analytic choices → **E-ROBUST** · published stat + open data+code → **E-REPRO**
- forecast / "should" / market-direction → **κ=0 ARMOR** (ground every sub-claim or abstain)
Every routed piece is κ-labelled so nothing κ=0 is ever presented as machine-verified.

## Grounded method SOTA (fetched — see `GROUNDING.md`)
Deflated/Probabilistic Sharpe (Bailey & López de Prado 2012/2014); purged & embargoed CV (López de
Prado 2018); DiD pre-trends + untestability (Roth 2022); McCrary (2008) density test; weak-IV F /
Stock–Yogo (1997/2005); Oster (2019) δ; E-value (VanderWeele & Ding 2017, reused from SOCIUS).

## Killer demos (committed prediction → run → compare)
1. **C14 / "dies under stress" (the headline):** a plausible trading rule with a STRONG in-sample
   Sharpe that **DIES** under walk-forward + Deflated Sharpe → ABSTAIN. (`demo_overfit_dies/`)
2. **E-CAUSAL:** a DiD/event-study with the **pre-trends placebo** (parallel-trends holds? + an E-value
   for the untestable residue) — a clean design PASSES, a confounded one is FLAGGED. (`demo_causal/`)
3. **Leakage catch:** the gate CATCHING an injected look-ahead/leakage bug in a backtest. (in `selftest_all.py` + `demo_overfit_dies/`)

## Honesty rails (non-waivable, specific to ECONOMETRIX)
- **In-sample / single-split is never the verdict** — only walk-forward OOS, multiple-testing-corrected,
  net of costs. Edge that flips OOS ⇒ **ABSTAIN**.
- **A backtest is not a forecast** — survival under historical stress ≠ future profit; never predict markets.
- **Causal claims carry their assumptions** — testable diagnostics AND a sensitivity number for the
  untestable ones; never a bare "X caused Y."
- **Reproduction is labelled reproduction** (source+date); a result that DIES is reported plainly as the
  valuable finding.
- **The gate that can't fail is not a gate** — no verifier ships without its kill/catch self-tests.
- **κ=0 stays armor:** "should the Fed cut," "will this stock rise," "is this policy good" → ground + abstain.
- **Inherit C14 explicitly:** a gameable proxy (in-sample Sharpe, an LLM "this looks profitable") does
  NOT raise κ. **Honest ceiling, every run: raises trustworthiness; does NOT predict the future or
  manufacture truth.**
- **Method limits, disclosed (audit-hardened):** the Deflated Sharpe assumes ~independent trials —
  correlated rule families (an SMA grid) collapse the trial variance, so ECONOMETRIX **floors V** to
  keep the deflation conservative (effective-N ≤ raw N). The bootstrap McCrary test can false-positive
  under **heteroscedasticity across the cutoff** → a detection carries that caveat. F>10 is the classic
  weak-IV bar; the modern effective-F bar is higher (reported, not buried). A min OOS sample (T≥30) is
  required before any edge claim. These are surfaced, not hidden — see `GROUNDING.md` + `AUDIT.md`.
