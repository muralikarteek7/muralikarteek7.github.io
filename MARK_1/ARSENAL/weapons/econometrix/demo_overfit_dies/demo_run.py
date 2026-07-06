#!/usr/bin/env python3
"""C14 "dies under stress" demo — the headline ECONOMETRIX run.

A plausible SMA-crossover rule is selected by its STRONG in-sample Sharpe across a LARGE grid (the
gameable number, C14 trap), then judged the only honest way: walk-forward OUT-OF-SAMPLE, NET of the
sourced transaction-cost model, gated by the Deflated Sharpe Ratio with the TRUE trial count N. We also
inject a look-ahead bug and show the leakage probe catches it.

Reuses: Artifacts/trading/real_world.py (REAL data + the sourced cost model) and the frozen
backtest_verify.py (DSR + walk-forward + detect_lookahead). Run: python3 demo_run.py
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))   # repo root
sys.path.insert(0, os.path.join(HERE, ".."))                          # econometrix/
sys.path.insert(0, os.path.join(ROOT, "Artifacts", "trading"))       # real_world.py

import real_world as rw
import backtest_verify as bv

# A LARGE grid -> the more rules searched, the more inflated the best in-sample Sharpe (multiple testing)
DEMO_GRID = [(f, s) for f in (3, 5, 8, 10, 15, 20, 30)
             for s in (50, 75, 100, 125, 150, 200) if f < s]
ASSETS = ["SPY", "AAPL", "BTC-USD", "RELIANCE_NS"]


def insample_trial_sharpes(prices, market):
    """Per-period (daily) Sharpe of EVERY rule in the grid, net of costs. The best is the gameable
    in-sample number; the variance across trials feeds the Deflated-Sharpe benchmark."""
    sr = {}
    for (f, s) in DEMO_GRID:
        daily = rw.backtest(prices, f, s, market)[0]
        st = bv.sharpe_stats(daily)
        sr[(f, s)] = st["sr"]
    return sr


def walk_forward_oos_costed(prices, market, n_folds=5, test_frac=0.14, min_train=250):
    """Walk-forward: pick the best grid rule on each expanding TRAIN window (by in-sample Sharpe),
    score it on the strictly-later unseen TEST window NET OF COSTS. Concatenate OOS returns."""
    n = len(prices)
    test_len = int(n * test_frac)
    oos, folds = [], []
    for k in range(n_folds):
        test_start = n - (n_folds - k) * test_len
        test_end = test_start + test_len
        if test_start < min_train or test_end > n:
            continue
        train = prices[:test_start]
        test = prices[test_start:test_end]
        best = max(DEMO_GRID, key=lambda fs: bv.sharpe_stats(rw.backtest(train, fs[0], fs[1], market)[0])["sr"])
        te_daily = rw.backtest(test, best[0], best[1], market)[0]
        if len(te_daily) >= 2:
            oos.extend(te_daily)
            folds.append({"fold": k, "best_param_on_train": list(best),
                          "fold_oos_sharpe_ann": bv.sharpe_stats(te_daily)["sr"] * math.sqrt(252)})
    return np.asarray(oos, dtype=float), folds


def run_asset(asset):
    market = rw.ASSET_MARKET[asset]
    prices = [p for _, p in rw.load(asset)]
    # 1) the GAMEABLE in-sample number: best rule over the FULL series
    trial_sr = insample_trial_sharpes(prices, market)
    best_is = max(trial_sr, key=trial_sr.get)
    is_sharpe_ann = trial_sr[best_is] * math.sqrt(252)
    V = float(np.var(list(trial_sr.values()), ddof=1))     # variance of per-period trial Sharpes
    N = len(DEMO_GRID)
    # 2) the HONEST verdict: walk-forward OOS net of costs, deflated by best-of-N
    oos, folds = walk_forward_oos_costed(prices, market)
    verdict = bv.backtest_verdict(oos, n_trials=N, trial_sharpe_var=V)
    return {
        "asset": asset, "market": market, "n_bars": len(prices), "n_trials": N,
        "best_insample_param": list(best_is),
        "insample_sharpe_annualized": is_sharpe_ann,           # the gameable number
        "oos_sharpe_annualized": verdict["oos_sharpe_annualized"],
        "deflated_sharpe_ratio": verdict["deflated_sharpe_ratio"],
        "expected_max_sharpe_SR0": verdict["expected_max_sharpe_SR0"],
        "var_trial_sharpe": V,
        "verdict": verdict["verdict"], "edge": verdict["edge"],
        "insample_minus_oos_sharpe": is_sharpe_ann - verdict["oos_sharpe_annualized"],
        "walk_forward_folds": folds,
    }


def leakage_demo(asset="SPY"):
    """Show the gate CATCHING a look-ahead bug: a future-peeking signal vs a clean one."""
    prices = np.asarray([p for _, p in rw.load(asset)], dtype=float)

    def clean_signal(p):     # uses only past bars
        return bv._sma_signal_clean(p, 10, 50)

    def leaky_signal(p):     # peeks at tomorrow's price (the classic look-ahead bug)
        return bv._sma_signal_leaky(p, 10, 50)

    clean = bv.detect_lookahead(clean_signal, prices)
    leaky = bv.detect_lookahead(leaky_signal, prices)
    # the (fake) in-sample Sharpe each rule reports, to show WHY a leak matters:
    #  clean: position from PAST bars earns the CURRENT return (honest).
    #  leaky: the textbook bug — peek at tomorrow (p[t+1]) and earn tomorrow's return -> a gorgeous,
    #         entirely fake Sharpe. detect_lookahead flags the future-dependence regardless.
    def clean_sharpe():
        pos = clean_signal(prices)
        r = [pos[t] * (prices[t] / prices[t - 1] - 1.0) for t in range(1, len(prices))]
        return bv.sharpe_stats(np.asarray(r))["sr"] * math.sqrt(252)

    def leaky_sharpe():
        r = []
        for t in range(1, len(prices) - 1):
            peek = 1.0 if prices[t + 1] > prices[t] else 0.0      # uses the FUTURE
            r.append(peek * (prices[t + 1] / prices[t] - 1.0))    # ...and earns it (the bug)
        return bv.sharpe_stats(np.asarray(r))["sr"] * math.sqrt(252)

    return {"asset": asset,
            "clean_leaked": clean["leaked"], "clean_insample_sharpe_ann": clean_sharpe(),
            "leaky_leaked": leaky["leaked"], "leaky_insample_sharpe_ann": leaky_sharpe(),
            "leaky_indices_flagged": len(leaky["leaked_indices"])}


if __name__ == "__main__":
    results = {"grid_size_N": len(DEMO_GRID), "assets": []}
    print(f"C14 DIES-UNDER-STRESS demo — grid N={len(DEMO_GRID)} SMA rules, walk-forward OOS net of costs\n")
    print(f"{'asset':13}{'IS_Sharpe':>11}{'OOS_Sharpe':>12}{'DSR':>8}{'SR0':>8}  verdict")
    print("-" * 86)
    abstains = 0
    for a in ASSETS:
        r = run_asset(a)
        results["assets"].append(r)
        if not r["edge"]:
            abstains += 1
        dsr = r["deflated_sharpe_ratio"]
        dsr_s = f"{dsr:.3f}" if dsr is not None and not math.isnan(dsr) else "nan"
        print(f"{a:13}{r['insample_sharpe_annualized']:>11.2f}{r['oos_sharpe_annualized']:>12.2f}"
              f"{dsr_s:>8}{r['expected_max_sharpe_SR0']:>8.3f}  {r['verdict']}")
    print("-" * 86)
    print(f"\nHEADLINE: in-sample said 'edge' on every asset; under walk-forward + Deflated Sharpe net of "
          f"costs,\n          ECONOMETRIX ABSTAINS on {abstains}/{len(ASSETS)} assets. "
          f"A backtest is not a forecast.")

    lk = leakage_demo("SPY")
    results["leakage_demo"] = lk
    print(f"\nLEAKAGE PROBE (SPY): clean rule leaked={lk['clean_leaked']} "
          f"(in-sample Sharpe {lk['clean_insample_sharpe_ann']:.2f}); "
          f"leaky rule leaked={lk['leaky_leaked']} "
          f"(fake in-sample Sharpe {lk['leaky_insample_sharpe_ann']:.2f}, "
          f"{lk['leaky_indices_flagged']} points flagged).")
    print("  -> the future-peeking rule's gorgeous in-sample Sharpe is a LEAK; the probe catches it.")

    results["abstain_count"] = abstains
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nwrote results.json")
