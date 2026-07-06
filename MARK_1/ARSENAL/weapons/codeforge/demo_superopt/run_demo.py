#!/usr/bin/env python3
"""SUPEROPT demo — take a naive O(n^2) correct function and a fast O(n) candidate; the frozen
verifier gates CORRECTNESS by differential test (kappa=1) and REPORTS a measured benchmark
(speed is measured, not certified). A faster-but-WRONG impostor and a benchmark-hardcoding
GAMING impostor are both REJECTED on correctness. Deterministic inputs. Writes RESULT.json."""
import sys
import os
import json
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from superopt_verify import verify_superopt  # noqa: E402

ENTRY = "count_pairs_with_sum"

REFERENCE = """
def count_pairs_with_sum(a, target):
    n = len(a); c = 0
    for i in range(n):
        for j in range(i + 1, n):
            if a[i] + a[j] == target:
                c += 1
    return c
"""

FAST = """
def count_pairs_with_sum(a, target):
    from collections import Counter
    seen = Counter(); c = 0
    for x in a:
        c += seen[target - x]
        seen[x] += 1
    return c
"""

WRONG = """
def count_pairs_with_sum(a, target):
    from collections import Counter
    seen = Counter(); c = 0
    for x in a:
        seen[x] += 1          # increment BEFORE the lookup -> counts x with itself: WRONG
        c += seen[target - x]
    return c
"""


def build_inputs():
    rng = random.Random(20260620)
    diff = [
        ([], 0), ([5], 5), ([0, 0], 0), ([3, 3, 3], 6),          # edges
        ([-2, 2, -2, 2, 0], 0), ([1, 1, 1, 1], 2),               # adversarial: many collisions
        ([10] * 6, 20), ([7, -7, 7, -7], 0),                     # all-equal / sign mix
    ]
    for _ in range(120):                                          # fuzz
        n = rng.randint(0, 30)
        arr = [rng.randint(-8, 8) for _ in range(n)]
        diff.append((arr, rng.randint(-16, 16)))
    bench_n = 3000
    bench_arr = [rng.randint(-50, 50) for _ in range(bench_n)]
    bench = [(bench_arr, 0)] * 2
    return diff, bench, bench_n, bench_arr


def main():
    diff, bench, bench_n, bench_arr = build_inputs()
    results = {"demo": "superopt", "task": "count_pairs_with_sum (O(n^2) -> O(n))", "objects": []}

    # U1-U2: fast candidate is correct AND faster
    rfast = verify_superopt(REFERENCE, FAST, ENTRY, diff, bench, margin=2.0, trials=5)
    results["objects"].append({"name": "fast_On_candidate", "verdict": rfast})

    # U3: faster-but-wrong impostor -> rejected on correctness
    rwrong = verify_superopt(REFERENCE, WRONG, ENTRY, diff, bench, margin=2.0, trials=2)
    results["objects"].append({"name": "wrong_impostor", "verdict": rwrong})

    # U4: gaming impostor — hard-code the benchmark size, wrong elsewhere
    precomp = sum(1 for i in range(bench_n) for j in range(i + 1, bench_n)
                  if bench_arr[i] + bench_arr[j] == 0)
    gaming = (f"def {ENTRY}(a, target):\n"
              f"    if len(a) == {bench_n} and target == 0:\n"
              f"        return {precomp}\n"
              f"    return 0\n")
    rgame = verify_superopt(REFERENCE, gaming, ENTRY, diff, bench, margin=2.0, trials=2)
    results["objects"].append({"name": "gaming_hardcodes_benchmark",
                               "precomputed_bench_answer": precomp, "verdict": rgame})

    checks = {
        "U1_fast_correct": rfast.get("correct") is True,
        "U2_fast_win_ge_2x": rfast.get("win") is True and rfast.get("speedup_measured", 0) >= 2.0,
        "U3_wrong_rejected": (rwrong.get("correct") is False
                              and rwrong.get("verdict") == "REJECTED_INCORRECT"),
        "U4_gaming_rejected": (rgame.get("correct") is False
                               and rgame.get("verdict") == "REJECTED_INCORRECT"),
    }
    results["prediction_checks"] = checks
    results["all_predictions_hit"] = all(checks.values())

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RESULT.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("SUPEROPT demo (count_pairs_with_sum, O(n^2) -> O(n)):")
    print(f"  fast candidate : correct={rfast.get('correct')} "
          f"speedup={rfast.get('speedup_measured'):.1f}x verdict={rfast.get('verdict')}")
    print(f"  wrong impostor : correct={rwrong.get('correct')} verdict={rwrong.get('verdict')} "
          f"(timing never consulted)")
    print(f"  gaming impostor: correct={rgame.get('correct')} verdict={rgame.get('verdict')} "
          f"(caught by differential on fuzzed inputs)")
    for k, ok in checks.items():
        print(f"    [{'PASS' if ok else 'MISS'}] {k}")
    print(f"  ALL PREDICTIONS HIT: {results['all_predictions_hit']}")


if __name__ == "__main__":
    main()
