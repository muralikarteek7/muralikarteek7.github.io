#!/usr/bin/env python3
"""E-BACKTEST — frozen verifier for OUT-OF-SAMPLE SURVIVAL of a market edge (kappa ~= 0.4, GUARDED).

THE C14 TRAP, made into a gate. In finance the most-reported number — the in-sample / single-split
Sharpe ratio — is the single most GAMEABLE number there is: try enough rules/params and one will look
great by pure chance. So an in-sample backtest score is "exact" yet GAMEABLE and does NOT qualify as a
kappa=1 verifier. This verifier therefore NEVER reports an edge on the fitting window. The verdict is:

  (1) WALK-FORWARD OUT-OF-SAMPLE performance only (params chosen on the past, scored on the strictly-
      later unseen window; no look-ahead), NET OF TRANSACTION COSTS, AND
  (2) the DEFLATED SHARPE RATIO (Bailey & Lopez de Prado 2014) > 0.95 — which corrects the best
      observed Sharpe for (a) the number of trials N that were searched (multiple testing), (b) the
      short sample length T, and (c) non-normal returns (skewness gamma3, kurtosis gamma4).

A strong in-sample Sharpe with no OOS survival -> DSR ~= 0 -> ABSTAIN, NOT "edge found". A leak that
inflates OOS by using future data must be CATCHABLE (detect_lookahead). All formulas are GROUNDED in
GROUNDING.md (fetched, not asserted) and the self-tests anchor on published / hand-computed numbers.

HONEST CEILING (stated every run): survival under historical stress != future profit. This verifier
raises trustworthiness; it is NOT a forecaster. "Will it make money" is kappa=0 -> armor + abstain.
"""
import sys, json, math
import numpy as np
from scipy import stats

EULER_MASCHERONI = 0.5772156649015329


# --------------------------------------------------------------------------- #
#  Sharpe-ratio statistics (per-period / NON-annualized, as the PSR formula needs)
# --------------------------------------------------------------------------- #
def sharpe_stats(returns):
    """Per-period Sharpe ratio + the higher moments the Probabilistic Sharpe Ratio needs.

    Returns dict with: sr (non-annualized per-period Sharpe), skew (gamma3), kurt (gamma4,
    NON-EXCESS so a normal distribution gives 3.0), T (number of observations).
    """
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    T = len(r)
    if T < 3:
        return {"sr": 0.0, "skew": 0.0, "kurt": 3.0, "T": T, "mean": 0.0, "sd": 0.0}
    mean = float(np.mean(r))
    sd = float(np.std(r, ddof=1))
    sr = mean / sd if sd > 0 else 0.0
    skew = float(stats.skew(r, bias=True))          # gamma3
    kurt = float(stats.kurtosis(r, fisher=False, bias=True))  # gamma4 NON-excess (normal=3)
    return {"sr": sr, "skew": skew, "kurt": kurt, "T": T, "mean": mean, "sd": sd}


# --------------------------------------------------------------------------- #
#  Probabilistic Sharpe Ratio  (Bailey & Lopez de Prado 2012)
# --------------------------------------------------------------------------- #
def probabilistic_sharpe_ratio(sr_hat, sr_star, T, skew=0.0, kurt=3.0):
    """PSR(SR*) = Phi[ (SR_hat - SR*) * sqrt(T-1) / sqrt(1 - g3*SR_hat + (g4-1)/4 * SR_hat^2) ].

    sr_hat, sr_star: NON-annualized (per-period) Sharpe ratios. T: number of returns.
    skew=g3, kurt=g4 (NON-excess). Denominator uses the OBSERVED sr_hat (it is the standard error of
    the SR estimator) — the canonical Bailey-LdP / mlfinlab convention (see GROUNDING.md s1).
    Returns the probability that the true Sharpe exceeds sr_star.
    """
    if T < 2:
        return float("nan")
    denom_var = 1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * (sr_hat ** 2)
    if denom_var <= 0:
        # non-normality so severe the variance estimate is degenerate -> cannot certify
        return float("nan")
    z = (sr_hat - sr_star) * math.sqrt(T - 1) / math.sqrt(denom_var)
    return float(stats.norm.cdf(z))


def expected_max_sharpe(n_trials, var_trial_sr):
    """Expected MAXIMUM Sharpe Ratio across N independent trials (the DSR deflation benchmark SR0).

    SR0 = sqrt(V) * [ (1-gamma_E)*Phi^-1(1 - 1/N) + gamma_E*Phi^-1(1 - 1/(N*e)) ]
    (Bailey & Lopez de Prado 2014). V = variance of the per-period trial Sharpes; gamma_E = Euler-
    Mascheroni. This is the highest Sharpe you'd EXPECT from N unskilled strategies by chance alone —
    the bar the real strategy must clear. More trials searched -> higher SR0 -> harder to clear.
    """
    N = max(int(n_trials), 1)
    V = max(float(var_trial_sr), 0.0)
    if N < 2 or V == 0.0:
        # with 0 or 1 trial there is no multiple-testing inflation to deflate
        return 0.0
    z1 = stats.norm.ppf(1.0 - 1.0 / N)
    z2 = stats.norm.ppf(1.0 - 1.0 / (N * math.e))
    return float(math.sqrt(V) * ((1 - EULER_MASCHERONI) * z1 + EULER_MASCHERONI * z2))


def deflated_sharpe_ratio(returns, n_trials, trial_sharpes=None, trial_sharpe_var=None):
    """DSR = PSR(SR0): probability the strategy's true Sharpe beats the multiple-testing benchmark SR0.

    returns: the SELECTED strategy's realized (ideally OUT-OF-SAMPLE) per-period returns.
    n_trials: the number of configurations/rules searched to find this one (N — do NOT under-count;
              under-counting N is the classic cheat that inflates DSR).
    trial_sharpes: the per-period Sharpes of all N trials (used to estimate V exactly); OR pass
                   trial_sharpe_var directly. If neither is given, V is estimated from `returns` alone
                   (conservative-ish: var of a single track record), and that is flagged.
    """
    st = sharpe_stats(returns)
    if trial_sharpe_var is not None:
        V = float(trial_sharpe_var)
        v_source = "supplied"
    elif trial_sharpes is not None and len(trial_sharpes) > 1:
        V = float(np.var(np.asarray(trial_sharpes, dtype=float), ddof=1))
        v_source = "trial_sharpes"
    else:
        # fallback: asymptotic variance of a single SR estimate (Lo 2002) — flagged as weaker
        V = (1.0 + 0.5 * st["sr"] ** 2) / max(st["T"] - 1, 1)
        v_source = "single-estimate-fallback"
    # FLOOR V (audit findings #2 & #5, 2026-06-20): when N>1 trials were searched but the trial Sharpes
    # are degenerate/correlated (e.g. an SMA-rule grid on one asset -> V~0), an un-floored V makes SR0~0
    # and the multiple-testing deflation VANISHES -> a false edge can clear. The Bailey-LdP SR0 assumes
    # ~independent trials; that is violated for correlated rule families. We floor V at the Lo(2002)
    # single-SR sampling variance so even correlated trials keep at least one SR's worth of deflation
    # (CONSERVATIVE: it can only make the bar HARDER, never easier).
    v_floor = (1.0 + 0.5 * st["sr"] ** 2) / max(st["T"] - 1, 1)
    if n_trials > 1 and V < v_floor:
        V = v_floor
        v_source += f"+floored(Lo2002={v_floor:.2e})"
    sr0 = expected_max_sharpe(n_trials, V)
    dsr = probabilistic_sharpe_ratio(st["sr"], sr0, st["T"], st["skew"], st["kurt"])
    return {
        "sub_weapon": "E-BACKTEST", "kappa": 0.4,
        "observed_sharpe_per_period": st["sr"], "T": st["T"],
        "skew": st["skew"], "kurt_nonexcess": st["kurt"],
        "n_trials": int(n_trials), "var_trial_sharpe": V, "var_source": v_source,
        "expected_max_sharpe_SR0": sr0,
        "deflated_sharpe_ratio": dsr,
        "ceiling_note": "DSR is computed on the realized (ideally OOS) track record and deflated by "
                        "the best-of-N benchmark. A backtest is not a forecast; survival != future profit.",
    }


# --------------------------------------------------------------------------- #
#  Leakage / look-ahead detector (FROZEN, kappa=1): a signal at time t must NOT
#  depend on data at time > t. We perturb the FUTURE and check the past signal.
# --------------------------------------------------------------------------- #
def detect_lookahead(signal_fn, prices, test_idx=None, seed=0, rtol=1e-7):
    """Catch a look-ahead bug WITHOUT trusting the author's word.

    signal_fn(prices)->array of positions, one per bar; position[t] is the position DECIDED using
    information available at time t (so it may use prices[:t+1] but NEVER prices[t+1:]). We perturb
    prices STRICTLY AFTER index t and recompute; if position[t] changes, the signal used future data.

    HARDENED (audit finding #1, 2026-06-20): small random perturbations failed to flip a binary signal
    when future data entered with LOW WEIGHT (off-by-one in a long-window SMA — the most common
    accidental leak), via a ROBUST statistic (a full-sample median threshold), or in an EARLY burn-in
    region. Fixes: (i) ADVERSARIAL perturbations — large multiplicative shocks up AND down + a ramp, not
    5% noise — so even a diluted future term moves the signal; (ii) probe a WIDE index range INCLUDING
    early indices (burn-in); (iii) a flip under ANY perturbation style flags the point.

    Returns {leaked: bool, leaked_indices: [...]}. This is the gate's (c) "catch a leak" test, plus the
    three audit-regression leaks (off-by-one long SMA, full-sample-median threshold, global-stat).
    """
    rng = np.random.default_rng(seed)
    prices = np.asarray(prices, dtype=float)
    n = len(prices)
    base = np.asarray(signal_fn(prices), dtype=float)
    if test_idx is None:
        # probe a WIDE spread INCLUDING early (burn-in) and interior points
        step = max(n // 60, 1)
        test_idx = list(range(2, n - 2, step))

    def perturbations(flen):
        # large adversarial shocks: any genuine dependence on prices[>t] moves under at least one.
        return [np.full(flen, 5.0),                       # 5x up
                np.full(flen, 0.2),                        # 5x down
                1.0 + np.linspace(0.0, 3.0, flen),         # monotone ramp (catches robust-stat leaks)
                1.0 + rng.normal(0.0, 0.5, flen)]          # large random

    leaked_idx = []
    for t in test_idx:
        if t >= n - 1:
            continue
        flen = n - (t + 1)
        changed = False
        for mult in perturbations(flen):
            p2 = prices.copy()
            p2[t + 1:] = p2[t + 1:] * mult
            s2 = np.asarray(signal_fn(p2), dtype=float)
            if not math.isclose(s2[t], base[t], rel_tol=rtol, abs_tol=1e-9):
                changed = True
                break
        if changed:
            leaked_idx.append(int(t))
    return {"leaked": len(leaked_idx) > 0, "leaked_indices": leaked_idx,
            "n_probed": len(test_idx)}


# --------------------------------------------------------------------------- #
#  Purged & embargoed train-index selection (Lopez de Prado 2018) — frozen helper
# --------------------------------------------------------------------------- #
def purged_embargo_train_idx(n, test_start, test_end, label_horizon=0, embargo=0):
    """Indices kept for TRAINING given a contiguous test fold [test_start, test_end).

    PURGE: drop train observations whose label-formation window [i, i+label_horizon] overlaps the test
    fold. EMBARGO: also drop `embargo` observations immediately AFTER the test fold. Returns the kept
    train indices. (For a plain walk-forward, label_horizon=embargo=0 and train = everything before
    test_start, which this reduces to.)
    """
    keep = []
    purge_lo = test_start - label_horizon
    embargo_hi = test_end + embargo
    for i in range(n):
        if test_start <= i < test_end:
            continue                      # the test fold itself
        if i >= purge_lo and i < test_end:
            continue                      # label window overlaps the test fold -> purge
        if test_end <= i < embargo_hi:
            continue                      # embargo buffer after the test fold
        keep.append(i)
    return keep


# --------------------------------------------------------------------------- #
#  Walk-forward OOS evaluation (leakage-safe by construction)
# --------------------------------------------------------------------------- #
def walk_forward_oos(prices, fit_fn, eval_fn, n_folds=5, test_frac=0.12, min_train=200):
    """Rolling walk-forward. For each fold: fit params on the past (expanding train), score on the
    strictly-later unseen test window. Returns (oos_returns_concat, per_fold_sharpe, fold_info).

    fit_fn(train_prices) -> params chosen on TRAIN ONLY.
    eval_fn(test_prices, params) -> array of per-period returns on the test window.
    No test bar ever informs the params used to score it -> no look-ahead by construction.
    """
    prices = np.asarray(prices, dtype=float)
    n = len(prices)
    test_len = int(n * test_frac)
    oos_all, fold_sharpes, info = [], [], []
    for k in range(n_folds):
        test_start = n - (n_folds - k) * test_len
        test_end = test_start + test_len
        if test_start < min_train or test_end > n:
            continue
        train = prices[:test_start]
        test = prices[test_start:test_end]
        params = fit_fn(train)
        rets = np.asarray(eval_fn(test, params), dtype=float)
        if len(rets) < 2:
            continue
        oos_all.extend(rets.tolist())
        fold_sharpes.append(sharpe_stats(rets)["sr"])
        info.append({"fold": k, "test_start": int(test_start), "params": params,
                     "fold_sharpe_per_period": fold_sharpes[-1]})
    return np.asarray(oos_all, dtype=float), fold_sharpes, info


def backtest_verdict(oos_returns, n_trials, trial_sharpes=None, trial_sharpe_var=None,
                     dsr_threshold=0.95, periods_per_year=252):
    """THE FROZEN VERDICT. Reports an edge ONLY if BOTH hold; else ABSTAIN.

      (1) walk-forward OOS annualized Sharpe > 0  (net of costs — caller nets them before passing), AND
      (2) Deflated Sharpe Ratio > dsr_threshold (default 0.95) given the N trials searched.

    In-sample is never consulted here. This is the C10/C14 guard made executable.
    """
    dsr = deflated_sharpe_ratio(oos_returns, n_trials,
                                trial_sharpes=trial_sharpes, trial_sharpe_var=trial_sharpe_var)
    st = sharpe_stats(oos_returns)
    oos_ann = st["sr"] * math.sqrt(periods_per_year)
    # MIN-T guard (audit finding #6, 2026-06-20): a backtest with too few OOS observations cannot
    # support an edge claim — a handful of returns can show an extreme (meaningless) Sharpe. Require a
    # minimum OOS sample; otherwise ABSTAIN regardless of the in-sample-looking numbers.
    MIN_OOS_T = 30
    if st["T"] < MIN_OOS_T:
        return {
            "sub_weapon": "E-BACKTEST", "kappa": 0.4,
            "oos_sharpe_annualized": oos_ann, "oos_sharpe_per_period": st["sr"], "oos_T": st["T"],
            "deflated_sharpe_ratio": dsr["deflated_sharpe_ratio"],
            "expected_max_sharpe_SR0": dsr["expected_max_sharpe_SR0"],
            "n_trials": int(n_trials), "dsr_threshold": dsr_threshold,
            "verdict": f"ABSTAIN (insufficient OOS sample T={st['T']} < {MIN_OOS_T})", "edge": False,
            "ceiling_note": "Too few out-of-sample observations to support any edge claim.",
        }
    survives = (oos_ann > 0) and (dsr["deflated_sharpe_ratio"] is not None) \
        and (not math.isnan(dsr["deflated_sharpe_ratio"])) \
        and (dsr["deflated_sharpe_ratio"] > dsr_threshold)
    return {
        "sub_weapon": "E-BACKTEST", "kappa": 0.4,
        "oos_sharpe_annualized": oos_ann,
        "oos_sharpe_per_period": st["sr"], "oos_T": st["T"],
        "deflated_sharpe_ratio": dsr["deflated_sharpe_ratio"],
        "expected_max_sharpe_SR0": dsr["expected_max_sharpe_SR0"],
        "n_trials": int(n_trials), "dsr_threshold": dsr_threshold,
        "verdict": "EDGE SURVIVES OOS" if survives else "ABSTAIN (no robust OOS edge)",
        "edge": bool(survives),
        "ceiling_note": "Survival under historical stress is NOT a forecast. ECONOMETRIX never says "
                        "'this will make money'. In-sample score was never the verdict.",
    }


# ============================ SELF-TESTS (must FAIL on broken input) ========= #
def _sma(prices, n):
    p = np.asarray(prices, dtype=float)
    out = np.full(len(p), np.nan)
    if len(p) >= n:
        c = np.cumsum(p)
        out[n - 1:] = (c[n - 1:] - np.concatenate([[0], c[:-n]])) / n
    return out


def _sma_signal_clean(prices, fast=10, slow=50):
    """A CLEAN signal: position[t] uses only bars up to t (yesterday's completed SMA). No look-ahead."""
    f, s = _sma(prices, fast), _sma(prices, slow)
    pos = np.zeros(len(prices))
    for t in range(1, len(prices)):
        if np.isfinite(f[t - 1]) and np.isfinite(s[t - 1]):
            pos[t] = 1.0 if f[t - 1] > s[t - 1] else 0.0
        else:
            pos[t] = pos[t - 1]
    return pos


def _sma_signal_leaky(prices, fast=10, slow=50):
    """A LEAKY signal: position[t] peeks at TOMORROW's price (prices[t+1]) — the classic look-ahead bug."""
    pos = np.zeros(len(prices))
    for t in range(1, len(prices) - 1):
        pos[t] = 1.0 if prices[t + 1] > prices[t] else 0.0   # uses the FUTURE
    return pos


# --- audit-regression leaks (finding #1): the 3 SUBTLE leaks the 5%-noise detector used to MISS ---
def _leak_offbyone_sma(prices, fast=10, slow=50):
    """DILUTED leak: the slow SMA is evaluated one bar ahead (s[t+1]) so it includes tomorrow's price —
    the most common accidental look-ahead, where the future enters a long window with tiny weight."""
    f, s = _sma(prices, fast), _sma(prices, slow)
    pos = np.zeros(len(prices))
    for t in range(1, len(prices) - 1):
        sl = s[t + 1]                                       # slow SMA at t+1 -> uses p[t+1]
        if np.isfinite(f[t - 1]) and np.isfinite(sl):
            pos[t] = 1.0 if f[t - 1] > sl else 0.0
        else:
            pos[t] = pos[t - 1]
    return pos


def _leak_fullsample_median(prices):
    """ROBUST-STAT leak: the threshold is the FULL-SAMPLE median (a robust global stat over future bars)."""
    med = float(np.median(prices))
    pos = np.zeros(len(prices))
    for t in range(1, len(prices)):
        pos[t] = 1.0 if prices[t - 1] > med else 0.0
    return pos


def _leak_global_mean(prices):
    """GLOBAL-STAT leak: normalizes against the full-sample mean (uses all future bars, incl. burn-in)."""
    mu = float(np.mean(prices))
    pos = np.zeros(len(prices))
    for t in range(1, len(prices)):
        pos[t] = 1.0 if prices[t - 1] > mu else 0.0
    return pos


def _selftest():
    # ---- (1) PSR anchors (hand-computable) ----
    # PSR(SR*=0) with SR_hat=0 must be Phi(0) = 0.5 exactly.
    assert abs(probabilistic_sharpe_ratio(0.0, 0.0, 500, 0.0, 3.0) - 0.5) < 1e-9
    # A clearly-good per-period SR=0.15 over T=1000 normal returns -> PSR(0) -> ~1.
    assert probabilistic_sharpe_ratio(0.15, 0.0, 1000, 0.0, 3.0) > 0.999
    # Normal-returns denominator reduction: var term = 1 + SR^2/2 (GROUNDING s1 self-consistency).
    sr = 0.2
    z_manual = (sr - 0.0) * math.sqrt(1000 - 1) / math.sqrt(1 + sr ** 2 / 2)
    assert abs(probabilistic_sharpe_ratio(sr, 0.0, 1000, 0.0, 3.0) - stats.norm.cdf(z_manual)) < 1e-12

    # ---- (2) expected_max_sharpe anchor (hand-computed in GROUNDING) ----
    # N=100, V=1.0: Phi^-1(0.99)=2.32635, Phi^-1(1-1/(100e))=2.68021 (e=2.718281828)
    #   SR0 = (1-0.57722)*2.32635 + 0.57722*2.68021 = 0.98363 + 1.54719 = 2.5306
    sr0 = expected_max_sharpe(100, 1.0)
    assert abs(sr0 - 2.5306) < 5e-4, sr0
    # MONOTONE: more trials searched -> higher bar
    assert expected_max_sharpe(1000, 1.0) > expected_max_sharpe(10, 1.0) > 0

    # ---- (3) DSR KILLS an overfit rule; PASSES a genuine edge (the (a)/(b) gate tests) ----
    # V = variance of the per-period (daily) trial Sharpes — these are SMALL numbers, so a realistic
    # V is ~1e-3 (a per-period SR std ~0.03 ~ an annualized SR std ~0.5). Using a realistic V is what
    # makes the deflation honest (an inflated V would make the bar artificially easy/hard).
    rng = np.random.default_rng(7)
    # OVERFIT: pure-noise OOS track record (SR ~ 0), but N=200 trials were searched -> the best-of-200
    #   benchmark SR0 > 0 while observed SR ~ 0 -> DSR ~ 0 (KILL).
    noise_oos = rng.normal(0.0, 0.01, size=750)
    over = backtest_verdict(noise_oos, n_trials=200, trial_sharpe_var=1e-3)
    assert over["edge"] is False, over
    assert over["deflated_sharpe_ratio"] < 0.5, over
    # GENUINE: a real, strong OOS edge (mean 0.0015/day, sd 0.008, T=1500 -> per-period SR~0.19),
    #   only N=5 trials -> DSR must clear 0.95 (PASS).
    good_oos = rng.normal(0.0015, 0.008, size=1500)
    good = backtest_verdict(good_oos, n_trials=5, trial_sharpe_var=5e-4)
    assert good["edge"] is True, good
    assert good["deflated_sharpe_ratio"] > 0.95, good

    # ---- (4) leakage detector: CLEAN passes, LEAKY is caught (the (c) gate test) ----
    prices = 100 * np.cumprod(1 + rng.normal(0.0003, 0.01, size=600))
    clean = detect_lookahead(_sma_signal_clean, prices)
    assert clean["leaked"] is False, clean
    leak = detect_lookahead(_sma_signal_leaky, prices)
    assert leak["leaked"] is True and len(leak["leaked_indices"]) > 0, leak
    # AUDIT-REGRESSION (finding #1): the three SUBTLE leaks the old 5%-noise detector MISSED must now
    # all be caught, and the clean rule must STILL pass (no false positive).
    assert detect_lookahead(_leak_offbyone_sma, prices)["leaked"] is True, "off-by-one long SMA leak missed"
    assert detect_lookahead(_leak_fullsample_median, prices)["leaked"] is True, "median-threshold leak missed"
    assert detect_lookahead(_leak_global_mean, prices)["leaked"] is True, "global-mean leak missed"
    assert detect_lookahead(_sma_signal_clean, prices)["leaked"] is False, "clean rule false-flagged"

    # ---- (4b) AUDIT-REGRESSION findings #2/#5 (V floor) and #6 (min-T) ----
    # V=0 with N=100 trials must NOT vanish the deflation -> a modest OOS SR must still ABSTAIN.
    modest_oos = rng.normal(0.0008, 0.01, size=800)
    degen = backtest_verdict(modest_oos, n_trials=100, trial_sharpe_var=0.0)
    assert degen["edge"] is False, ("V=0 degenerate must not manufacture an edge", degen)
    # tiny-T must ABSTAIN regardless of an extreme (meaningless) Sharpe
    tiny = backtest_verdict(rng.normal(0.02, 0.005, size=12), n_trials=1)
    assert tiny["edge"] is False and "insufficient OOS" in tiny["verdict"], tiny

    # ---- (5) purge/embargo helper drops the overlapping + buffer indices ----
    keep = purged_embargo_train_idx(n=100, test_start=40, test_end=60, label_horizon=5, embargo=3)
    assert all(not (40 <= i < 60) for i in keep)          # never the test fold
    assert all(not (35 <= i < 60) for i in keep)          # purged label-overlap [35,60)
    assert all(not (60 <= i < 63) for i in keep)          # embargo buffer [60,63)
    assert 34 in keep and 63 in keep                      # boundaries kept

    # ---- (6) walk-forward is leakage-safe: an OOS edge on noise must NOT appear ----
    def fit_best_sma(train):
        grid = [(f, s) for f in (5, 10, 20) for s in (50, 100) if f < s]
        best = max(grid, key=lambda fs: sharpe_stats(_strategy_returns(train, fs))["sr"])
        return best

    def eval_sma(test, params):
        return _strategy_returns(test, params)

    noise_prices = 100 * np.cumprod(1 + rng.normal(0.0, 0.01, size=2500))
    oos, folds, info = walk_forward_oos(noise_prices, fit_best_sma, eval_sma)
    grid_n = len([(f, s) for f in (5, 10, 20) for s in (50, 100) if f < s])
    v = backtest_verdict(oos, n_trials=grid_n, trial_sharpe_var=2e-3)
    assert v["edge"] is False, ("a grid-searched rule on NOISE must ABSTAIN OOS", v)

    print("backtest_verify selftest: PASS")
    print(f"  PSR/DSR anchored (SR0[N=100,V=1]={sr0:.4f}); overfit DSR={over['deflated_sharpe_ratio']:.3f} "
          f"(KILL); genuine DSR={good['deflated_sharpe_ratio']:.3f} (PASS)")
    print(f"  leakage: clean=not-leaked, leaky=CAUGHT ({len(leak['leaked_indices'])} pts); "
          f"walk-forward on noise -> {v['verdict']}")


def _strategy_returns(prices, params, cost_bps=1.0):
    """SMA-crossover long/flat per-period returns, NET of a simple per-side cost in bps on turnover.
    Used only by the self-test; the real demo uses Artifacts/trading/real_world.py sourced costs."""
    fast, slow = params
    pos = _sma_signal_clean(prices, fast, slow)
    p = np.asarray(prices, dtype=float)
    ret = np.zeros(len(p))
    for t in range(1, len(p)):
        gross = pos[t] * (p[t] / p[t - 1] - 1.0)
        turnover = abs(pos[t] - pos[t - 1])
        ret[t] = gross - turnover * (cost_bps / 1e4)
    return ret[1:]


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: backtest_verify.py selftest  (programmatic API: backtest_verdict, "
              "deflated_sharpe_ratio, walk_forward_oos, detect_lookahead)")
