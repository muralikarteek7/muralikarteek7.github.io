#!/usr/bin/env python3
"""SORTNET demo — reproduce the optimal n=8 sorting network (0/1-verified) AND run a
verifier-gated greedy DISCOVERY from scratch. Every object is machine-checked by the
frozen sortnet_verify.py. The n=8 result is a LABELED REPRODUCTION; no record is claimed.
Deterministic (seeded LCG). Writes RESULT.json."""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sortnet_verify import verify_sorting_network, _is_sorted  # noqa: E402


# ---- deterministic PRNG (reproducible discovery) ----
class LCG:
    def __init__(self, seed=1):
        self.s = seed & 0xFFFFFFFF

    def _n(self):
        self.s = (1664525 * self.s + 1013904223) & 0xFFFFFFFF
        return self.s

    def shuffle(self, xs):
        for i in range(len(xs) - 1, 0, -1):
            j = self._n() % (i + 1)
            xs[i], xs[j] = xs[j], xs[i]
        return xs


# ---- Batcher odd-even mergesort (canonical; n a power of 2) ----
def batcher_oddeven_mergesort(length):
    cmps = []

    def merge(lo, hi, r):
        step = r * 2
        if step < hi - lo:
            merge(lo, hi, step)
            merge(lo + r, hi, step)
            for i in range(lo + r, hi - r, step):
                cmps.append((i, i + r))
        else:
            cmps.append((lo, lo + r))

    def sort(lo, hi):
        if hi - lo >= 1:
            mid = lo + (hi - lo) // 2
            sort(lo, mid)
            sort(mid + 1, hi)
            merge(lo, hi, 1)

    sort(0, length - 1)
    return cmps


def bubble_network(n):
    """A guaranteed-valid sorting network for any n (bubble order). n(n-1)/2 comparators."""
    net = []
    for i in range(n - 1):
        for j in range(n - 1 - i):
            net.append((j, j + 1))
    return net


# ---- verifier-gated greedy DISCOVERY (0/1-eval is the search signal) ----
def greedy_discover(n, seed=1, restarts=60):
    from itertools import combinations
    pairs = list(combinations(range(n), 2))
    base = [[(m >> k) & 1 for k in range(n)] for m in range(1 << n)]
    rng = LCG(seed)
    max_cmps = n * (n - 1) // 2 + 4
    best_net = None

    def apply_pair(state, i, j):
        out = []
        for v in state:
            if v[i] > v[j]:
                w = list(v); w[i], w[j] = w[j], w[i]; out.append(w)
            else:
                out.append(v)
        return out

    def unsorted(state):
        return sum(0 if _is_sorted(v) else 1 for v in state)

    for _ in range(restarts):
        state = [list(v) for v in base]
        net = []
        cur = unsorted(state)
        order = list(pairs)
        while cur > 0 and len(net) < max_cmps:
            rng.shuffle(order)  # random tie-break / restart diversity
            best_pair, best_state, best_cnt = None, None, cur
            for (i, j) in order:
                ns = apply_pair(state, i, j)
                c = unsorted(ns)
                if c < best_cnt:
                    best_cnt, best_pair, best_state = c, (i, j), ns
            if best_pair is None:  # stuck: take a random progressing-or-neutral move
                i, j = order[0]
                best_pair, best_state, best_cnt = (i, j), apply_pair(state, i, j), cur
            net.append(best_pair); state = best_state; cur = best_cnt
        if cur == 0 and (best_net is None or len(net) < len(best_net)):
            best_net = net
    return best_net


def main():
    results = {"demo": "sortnet", "objects": []}

    # P1-P3: reproduce optimal n=8 via Batcher, verify by 0/1 principle
    net8 = batcher_oddeven_mergesort(8)
    v8 = verify_sorting_network(net8, 8)
    results["objects"].append({"name": "reproduce_n8_batcher", "network": net8, "verdict": v8})

    # P4-P5: discover a valid n=6 network from scratch, gated by the 0/1 verifier
    d6 = greedy_discover(6, seed=12345)
    v6 = verify_sorting_network(d6, 6) if d6 else {"valid": None, "verdict": "SEARCH_FAILED"}
    results["objects"].append({"name": "discover_n6_greedy", "network": d6, "verdict": v6})

    # P6: discover a valid n=7 network from scratch
    d7 = greedy_discover(7, seed=999)
    v7 = verify_sorting_network(d7, 7) if d7 else {"valid": None, "verdict": "SEARCH_FAILED"}
    results["objects"].append({"name": "discover_n7_greedy", "network": d7, "verdict": v7})

    # P7: a deliberately broken network must be caught
    broken8 = net8[:-1]  # drop the last comparator
    vb = verify_sorting_network(broken8, 8)
    results["objects"].append({"name": "broken_n8_dropped_comparator", "verdict": vb})

    # ---- prediction scorecard ----
    checks = {
        "P1_n8_valid": v8.get("valid") is True,
        "P2_n8_size_19": v8.get("num_comparators") == 19,
        "P3_n8_reproduction_label": v8.get("optimality") == "MATCHES_KNOWN_OPTIMUM",
        "P4_n6_valid": v6.get("valid") is True,
        "P5_n6_size_in_range_not_below_opt": (v6.get("valid") is True
                                              and 12 <= v6.get("num_comparators", 0) <= 20),
        "P6_n7_valid": v7.get("valid") is True,
        "P7_broken_caught": vb.get("valid") is False,
        "no_impossible_below_optimum": all(
            not o["verdict"].get("beats_optimal_IMPOSSIBLE", False)
            for o in results["objects"] if isinstance(o["verdict"], dict)),
    }
    results["prediction_checks"] = checks
    results["all_predictions_hit"] = all(checks.values())

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RESULT.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("SORTNET demo:")
    print(f"  reproduce n=8 (Batcher): valid={v8.get('valid')} "
          f"size={v8.get('num_comparators')} depth={v8.get('depth')} "
          f"label={v8.get('optimality')}")
    print(f"  discover  n=6 (greedy) : valid={v6.get('valid')} "
          f"size={v6.get('num_comparators')} (known opt 12) label={v6.get('optimality')}")
    print(f"  discover  n=7 (greedy) : valid={v7.get('valid')} "
          f"size={v7.get('num_comparators')} (known opt 16) label={v7.get('optimality')}")
    print(f"  broken n=8             : valid={vb.get('valid')} "
          f"(must be False) first_fail={vb.get('first_failing_binary_input')}")
    for k, ok in checks.items():
        print(f"    [{'PASS' if ok else 'MISS'}] {k}")
    print(f"  ALL PREDICTIONS HIT: {results['all_predictions_hit']}")


if __name__ == "__main__":
    main()
