# KICKOFF — build WEAPON #5: ECONOMETRIX (quant-finance & causal-econ rigor) for the v5 box
*Paste everything below into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written
2026-06-20. ECONOMETRIX is item #5 of `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` — the FIRST **Tier-A,
GUARDED-κ** weapon: its core number (a backtest) is GAMEABLE, so its job is to make a market-edge or causal claim
**survive out-of-sample + robustness + sensitivity**, NOT to manufacture a sharp certificate or predict the future.*

---

You are building **ECONOMETRIX**, a **κ-aware empirical-rigor weapon for economics & finance** — the SOCIUS/
PSYMETRIX sibling for the **ECON_FIN** department. Given a market-edge or economic-causal claim with data, it
routes the **κ>0 (guarded) pieces** to frozen verifiers (out-of-sample/walk-forward backtest with multiple-
testing correction; econometric identification checks; specification-curve; reproduction) and the **κ=0 pieces**
(forecast-the-future, "should we") to **armor (ground + abstain)**. Work BOX-style: plan → produce → **verify
INDEPENDENTLY** → ground → be honest; **no win without proof; an in-sample/backtest score is NEVER the verdict.**

## 0. ORIENT — read first (in order)
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (the κ-router — note **NEGATIVE-list item (4) "proxy-only scorers
(gameable → will be gamed)"** and the **C14 Sharpe-overfit trap** in STAGE 1: *a held-out/backtest score is
"exact" yet GAMEABLE → does NOT qualify as κ=1*). Read the **ECON_FIN** department entry in
`Expanding_Frontiers/HELMET/registry.json` (κ=0.4 guarded; in-sample fit is never the verdict) and the registry
weapon **W6_closed_form_pricer_factor_model** in `Next/WEAPON_REGISTRY.json`. Read **SOCIUS as the template you
are cloning** (`Expanding_Frontiers/weapons/socius/` — `SPEC.md`, the frozen `*_verify.py` set, `selftest_all.py`,
`socius_router.py`, `demo_durante2013/`, `AUDIT.md`); ECONOMETRIX has the **same mixed-κ internal-routing shape**.
The trading arena already exists: `Artifacts/trading/real_world.py` (+ `Artifacts/trading/data/`) — your
E-BACKTEST harness builds on it.

## 1. THE HONEST FRAMING — what ECONOMETRIX IS and IS NOT (do not skip)
**IS:** a **mixed, GUARDED-κ (≈0.4–0.6) trustworthiness weapon.** Finance/economics is **low-κ** — there is no
cheap exact verifier for "this edge is real" or "this policy caused that outcome," because the future is unseen
and identification rests on assumptions. So ECONOMETRIX does NOT certify truth; it **stress-tests** a claim:
does the edge survive **out-of-sample / walk-forward** (net of costs, multiple-testing-corrected)? does the
causal effect survive **placebo / pre-trends / sensitivity-to-unobservables**? **A claim that DIES under these
checks is the primary valuable output** (exactly SOCIUS's doctrine).

**IS NOT:**
- **NOT a backtest-blesser. In-sample / single-split Sharpe is the single most GAMEABLE number in finance** — it
  proves nothing (C14). The verifier is **out-of-sample/walk-forward + a multiple-testing correction (deflated
  Sharpe) + transaction costs**. A high in-sample score with no OOS survival ⇒ **ABSTAIN**, not "edge found."
- **NOT a forecaster.** A backtest is not a prediction; ECONOMETRIX never says "this will make money" or "rates
  will rise" — those are κ=0 (unseen future) → armor + abstain. It certifies **past survival under stress**, with
  the explicit caveat that survival ≠ future profit.
- **NOT a causal oracle.** DiD/RDD/IV identify an effect ONLY under assumptions; some are **testable (κ>0:
  pre-trends, McCrary density, first-stage F)** and some are **untestable (κ=0: exclusion, parallel-trends in the
  post-period)** → the latter get **sensitivity analysis (E-value / Rosenbaum / Oster δ)**, never a bare causal claim.
- **NOT a record/construction engine** — markets are low-κ; there is nothing to "break." It raises trustworthiness.
- **NOT smarter than the model.** It is organized rigor, not capability.

## 2. THE SUB-WEAPONS (mixed-κ internal routing, à la SOCIUS)
| sub-weapon | κ | what it checks | the frozen verifier |
|---|---|---|---|
| **E-BACKTEST** ⭐ (the C14-trap weapon) | ≈0.4 guarded | does a trading/market edge survive OUT of sample? | **walk-forward / purged-&-embargoed CV** (no leakage) + **Deflated Sharpe Ratio** (corrects multiple-testing + non-normality) + **net of transaction costs/slippage**. In-sample is never the verdict |
| **E-CAUSAL** | ≈0.5 | is an observational/quasi-experimental causal claim identified? | testable: **DiD pre-trends/placebo, RDD McCrary density + bandwidth sensitivity, IV first-stage F (weak-instrument)**; untestable → **sensitivity (E-value, Rosenbaum bounds, Oster δ)** |
| **E-ROBUST** (shared w/ SOCIUS) | ≈0.5 | is the result one lucky specification? | **specification-curve / multiverse** across defensible analytic choices (reuse `socius/multiverse_verify.py`) |
| **E-REPRO** (shared w/ SOCIUS) | ≈0.6 | does a published economic statistic reproduce from open data+code? | **re-run the author's code/data within tolerance** (reuse `socius/repro_verify.py` shape) |
| **κ=0 residue** | 0 | forecast the future; "should" policy; market direction | **ARMOR** — ground every empirical sub-claim or abstain; never fabricate a forecast |

**The genuinely NEW pieces vs SOCIUS are E-BACKTEST + E-CAUSAL** (finance OOS gauntlet + econometric
identification); E-ROBUST/E-REPRO **reuse** SOCIUS's verifiers — don't rebuild them, import/adapt and credit.

## 3. THE KEY ENGINEERING PROBLEM — defeat overfit, leakage, and multiple testing
Build the frozen verifiers FIRST, each able to FAIL:
1. **No in-sample verdicts.** E-BACKTEST's gate refuses to report any edge on the fitting window; the verdict is
   the **walk-forward OOS** performance only.
2. **Multiple-testing correction.** If many rules/parameters were tried, the best in-sample Sharpe is inflated →
   apply the **Deflated Sharpe Ratio** (needs the number of trials, skew, kurtosis, sample length). Report it.
3. **Leakage/look-ahead guards.** Purged + embargoed splits; point-in-time data only; no survivorship bias; costs
   netted. A leak that inflates OOS must be catchable.
4. **Causal assumption checks.** E-CAUSAL runs the testable diagnostics and, for the untestable assumptions,
   **reports a sensitivity number** (how strong must an unobserved confounder be to overturn the result) — never
   a bare "X caused Y."

**Gate self-tests (non-waivable, see `socius/selftest_all.py`):** the gate must (a) PASS a genuine OOS-surviving
edge / a well-identified effect, (b) **KILL an over-fit rule** (strong in-sample, no OOS survival — Deflated
Sharpe ≈ 0), (c) **CATCH a leakage/look-ahead bug** (inflated OOS from future data), (d) **flag a DiD whose
pre-trends FAIL** / an IV with a weak first stage. A gate that catches all four is trustworthy.

## 4. TO-DOs / STEPS (box order)
1. **PLAN:** `weapons/econometrix/SPEC.md` — the 5 sub-weapons + the κ table, the no-in-sample-verdict rule, the
   testable-vs-untestable causal split, the router (`econometrix_router.py`, cloned from `socius_router.py`:
   market-edge+price-data → E-BACKTEST; quasi-experimental causal claim → E-CAUSAL; many analytic choices →
   E-ROBUST; published stat + open data+code → E-REPRO; forecast/"should"/market-direction → **κ=0 armor**).
   **GROUND by FETCH (don't assert):** **Deflated Sharpe Ratio** (Bailey & López de Prado 2014); **purged &
   embargoed CV** (López de Prado, *Advances in Financial ML*); **DiD parallel-trends/pre-trends**; **McCrary
   (2008) density test** for RDD; **weak-instrument first-stage F / Stock-Yogo**; **Oster (2019) δ** for selection
   on unobservables; **E-value** (VanderWeele & Ding 2017 — already used in SOCIUS). Cite each in `GROUNDING.md`.
2. **BUILD THE VERIFIERS FIRST** (§3) on top of `Artifacts/trading/real_world.py`: `backtest_verify.py`
   (walk-forward + Deflated Sharpe + costs), `causal_verify.py` (DiD/RDD/IV diagnostics + sensitivity), and
   **import** `socius/multiverse_verify.py` + `socius/repro_verify.py` for E-ROBUST/E-REPRO. Then
   `selftest_all.py` with the 4 reject tests. **Gate green before any verdict counts.**
3. **BUILD the weapon loop / router** (clone SOCIUS): route → run κ>0 verifiers → κ=0 to armor → label every piece
   with its κ. Machine-checkable → **execute, never vote.**
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` BEFORE running): (i) **the C14 demo** — a
   plausible trading rule with a STRONG in-sample Sharpe that **DIES** under walk-forward + Deflated Sharpe (the
   "dies under stress" headline, the weapon's whole point); (ii) **an E-CAUSAL demo** — reproduce a known
   DiD/event-study and run the **pre-trends placebo** (report whether parallel-trends holds + an E-value); (iii)
   show the gate **CATCHING a look-ahead/leakage bug** injected into a backtest.
5. **VERIFY INDEPENDENTLY:** a cross-model audit (Sonnet/Haiku ≠ the Opus generator; **never Opus-audits-Opus**;
   Fable inactive) that (a) re-runs the walk-forward with its OWN split code, (b) attacks E-BACKTEST with a
   subtly-leaking strategy, (c) checks the Deflated-Sharpe trial-count isn't under-counted (the classic cheat),
   (d) checks no κ=0 forecast was smuggled in as a verified result. Fix what's caught.
6. **REGISTER:** add **ECONOMETRIX** to `Next/BOX_V5.md` (new Weapon + router branch — a mixed-κ branch like
   SOCIUS's Branch D) and update the **ECON_FIN** `draws` in `Expanding_Frontiers/HELMET/registry.json`. Honest
   `EVOLUTION_LOG` entry: **a weapon ADDED = capability EXPANSION, NOT a ≥10% promotion** (raises trustworthiness,
   not capability). Update `WEAPONS_BACKLOG.md` STATUS ✅.

## 5. HONESTY RAILS (non-waivable, specific to ECONOMETRIX)
- **In-sample / single-split is never the verdict** — only walk-forward OOS, multiple-testing-corrected, net of
  costs. Edge that flips OOS ⇒ **ABSTAIN**.
- **A backtest is not a forecast** — survival under historical stress ≠ future profit; never predict markets.
- **Causal claims carry their assumptions** — report the testable diagnostics AND a sensitivity number for the
  untestable ones; never a bare "X caused Y."
- **Reproduction is labeled reproduction** (source+date); a result that DIES under stress is reported plainly as
  the valuable finding.
- **The gate that can't fail is not a gate** — ship no verifier without its kill/catch self-tests.
- **κ=0 stays armor:** "should the Fed cut," "will this stock rise," "is this policy good" → ground + abstain.
- **Inherit C14 explicitly:** a gameable proxy (in-sample Sharpe, an LLM "this looks profitable") does NOT raise κ.

## 6. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/econometrix/` — `SPEC.md`, `GROUNDING.md` (fetched sources), the frozen
`backtest_verify.py` + `causal_verify.py` (+ imported multiverse/repro) + `selftest_all.py`,
`econometrix_router.py`, `demo_*/` (committed predictions + the dies-under-stress result + diagnostics),
`AUDIT.md` (cross-model red-team incl. the leakage / trial-undercount / smuggled-forecast attacks), `README.md`
(what it is + honest ceiling: raises trustworthiness, does NOT predict the future or manufacture truth).
Registration in `Next/BOX_V5.md` + `HELMET/registry.json` (ECON_FIN draws) + honest `EVOLUTION_LOG` entry;
`WEAPONS_BACKLOG.md` STATUS updated.

## 7. STAFF THE TEAM (v4 ladder; Fable INACTIVE → its slots on Opus, flag low confidence)
- **Quant/econometrician** = code tier writes the backtest/causal harnesses (**the frozen OOS/diagnostic gate,
  not the model, is the verdict**).
- **Library** = cheap model: fetch Deflated-Sharpe / purged-CV / McCrary / weak-IV / Oster / E-value sources.
- **Auditor** = a model ≠ the generator (Sonnet/Haiku; never Opus-audits-Opus) — re-runs walk-forward
  independently, attacks for leakage and trial-undercount, polices smuggled forecasts.

## 8. THE ONE-LINE TEST OF SUCCESS
**"ECONOMETRIX reports a market edge ONLY if it survives walk-forward OOS net of costs and multiple-testing
correction (else ABSTAIN), reports a causal effect ONLY with its testable diagnostics + a sensitivity number for
the untestable assumptions, reuses SOCIUS's multiverse/repro verifiers, makes the 'dies under stress' result its
headline, never predicts the future, and routes κ=0 'should/will' questions to armor."** Trustworthiness raised,
truth not manufactured, the future left unforecast.
