# ECONOMETRIX — independent cross-model audit (auditor ≠ generator)

**Generator:** Opus 4.8 (orchestrator). **Auditor:** Sonnet 4.6 (a different model — Fable 5 inactive,
so never Opus-audits-Opus). **Date:** 2026-06-20. The auditor read the weapon, **re-derived the math
with its own code**, **attacked E-BACKTEST with subtly-leaking strategies**, checked the Deflated-Sharpe
trial-count for the under-count cheat, **independently re-ran the walk-forward with its own split code**,
and hunted false-accepts/false-rejects. Full charge + transcript in session history.

## Top-line verdict (auditor): **SOUND-WITH-CAVEATS**
> "The weapon is architecturally sound. The core C14 doctrine is enforced correctly: in-sample SR is
> never the verdict, walk-forward OOS is required, N is not under-counted in the demo, and all outputs
> carry honest κ labels and ceiling notes. Math is correct. ABSTAIN 4/4 independently reproduced."

## Independently re-derived (auditor's own arithmetic — all matched)
| quantity | auditor re-derivation | ECONOMETRIX output | match |
|---|---|---|---|
| PSR(SR*=0, SR̂=0) | Φ(0) = 0.5 exactly | 0.5 | ✅ |
| normal-returns denom | `1 − 0·SR + (3−1)/4·SR² = 1 + SR²/2` | same | ✅ |
| SR₀ (N=100, V=1) | 2.5306 (with e=2.71828) | 2.5306 | ✅ |
| SR₀ monotonic in N | 0.52→1.57→2.53→3.26→3.86 (N=2→10⁴) | same | ✅ |
| E-value(3.9) | 3.9+√(3.9·2.9)=7.2630 | 7.263 | ✅ |
| Oster δ hand-example | 0.24/0.04 = 6.0 exactly | 6.0 | ✅ |
| walk-forward OOS Sharpe (4 assets) | reproduced to 4+ dp with own split code | identical | ✅ |

**The headline (ABSTAIN 4/4) is NOT an artifact of the generator's implementation** — the auditor's
independent split code reproduced every per-asset OOS Sharpe and verdict. **No κ=0 forecast was found
smuggled in as a verified result**; every backtest verdict carries κ=0.4 (GUARDED) + a "survival ≠
future profit" ceiling note; the router sends forecast/normative/direction to ARMOR. **N is not
under-counted** (the demo uses the true N=42, not 1).

## Findings (7) and what was done about each
| # | auditor finding | severity | resolution (machine-verified) |
|---|---|---|---|
| **1** | **`detect_lookahead` systematic BLIND SPOT.** The 5%-random-perturbation + binary-flip test MISSED three real leak classes: an **off-by-one in a long-window SMA** (the most common accidental look-ahead — future enters with tiny weight), a **full-sample-median threshold** (robust statistic), and **EWM future-initialization** (early burn-in, probed too late). 90% of probe points had margins too large to flip under 5% noise. | **real-bounded** | **FIXED.** Rewrote `detect_lookahead` to use **adversarial perturbations** (×5 up, ×5 down, a monotone ramp, large random) over a **wide probe range including early indices**. **Three regression self-tests** added (`_leak_offbyone_sma`, `_leak_fullsample_median`, `_leak_global_mean`) — all now **CAUGHT**; the clean rule still passes (no false positive). The classic leak now flags 60 points (was 16). |
| **2 & 5** | **V=0 / correlated-trials kills the deflation.** Passing `trial_sharpe_var=0` (or a correlated rule grid → V≈0) makes SR₀≈0, so the multiple-testing correction VANISHES and a modest positive OOS SR clears 0.95. Bailey-LdP assumes ~independent trials; an SMA family violates it (V=5.8e-5 for SPY ⇒ SR₀≈0.017, near-trivial deflation). | **real-bounded** (inherent to Bailey-LdP) | **FIXED.** `deflated_sharpe_ratio` now **floors V** at the Lo (2002) single-SR sampling variance `(1+½·SR̂²)/(T−1)` when N>1 — conservative (can only make the bar harder). Regression self-test: V=0 with N=100 + a modest OOS SR now **ABSTAINS**. The demo DSRs dropped from 0.11–0.34 to ≤0.03 (still ABSTAIN, now stricter). Documented in `GROUNDING.md` §1 + `SPEC.md`. |
| **3** | **Oster δ: no guard for `R_max < R_controlled`.** Economically invalid input (R_max below the controlled R²) flips the numerator sign → `δ = −1` → silently reports **robust=True** (a false-robust verdict). | **real-bounded** | **FIXED.** `oster_delta` now validates `R_controlled ≤ R_max ≤ 1`, returns an explicit error otherwise. Regression self-test added (invalid R_max → error, δ=None, robust=None). |
| **6** | **Tiny-T false accept.** `backtest_verdict` had no minimum-sample guard; T=10 with an extreme (meaningless) Sharpe returned edge=True. | **real-bounded** | **FIXED.** Added a **min OOS sample guard (T ≥ 30 ⇒ else ABSTAIN)**. Regression self-test added. |
| **4** | **McCrary false-positive under heteroscedasticity.** A running variable more dispersed on one side of the cutoff (no sorting) yields a density discontinuity the test reads as "manipulation." (Known limitation; CJM `rddensity` is more robust.) | **real-bounded** (known) | **FIXED (disclosure).** `mccrary_density_test` now computes left/right spread; a detection under `sd-ratio>1.5×` carries an explicit **heteroscedasticity caveat** in the verdict + a `heteroscedastic_running_var` flag. Regression self-test added. Documented in `GROUNDING.md` §4. |
| **7** | **GROUNDING annotation rounding.** `Φ⁻¹(1−1/(100e))` was annotated 2.68158 / SR₀ 2.5316 using e≈2.71815; true values 2.68021 / 2.5306. **Code was always correct** (uses `math.e`). | **trivial** | **FIXED.** Annotation corrected in `GROUNDING.md` §1 and the self-test comment + anchor (now `abs(SR₀−2.5306)<5e-4`). |

**Clean bills of health (attacks that did NOT break anything):** centered-MA / full-sample-normalization
/ rank leaks were already caught; the N-undercount cheat cannot manufacture an edge on the demo's
all-negative OOS Sharpes; no realistic false-rejection of a genuinely strong strategy was found; the IV
F-test boundary is clean; McCrary low-power at small n is correct (expected) behaviour; no κ=0 smuggling.

## Net
The auditor found **no verdict-changing bug and no dishonesty** — the headline (overfit dies, ABSTAIN
4/4; confound caught by pre-trends) stands under independent re-execution. It found **six real-bounded
defects + one trivial** that the generator's own self-tests had missed — **exactly why a different model
must check.** All six are now **fixed and locked by regression self-tests**; the full gate + both demos
re-run green; the demo headline is unchanged (and the DSR bar is now stricter, not looser). This is the
verify-independently loop working as intended on the tool.
