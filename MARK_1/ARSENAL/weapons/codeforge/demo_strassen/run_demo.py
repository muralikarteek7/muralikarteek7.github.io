#!/usr/bin/env python3
"""STRASSEN demo — reproduce Strassen's 1969 7-multiplication 2x2 scheme and machine-verify
it as an EXACT non-commutative symbolic identity (matmul_verify.py). Naive-8 control passes;
a broken scheme and a numeric-only GAMING scheme are caught. The Strassen result is a LABELED
REPRODUCTION (source: Strassen 1969; optimality Winograd 1971 — GROUNDING.md). Writes RESULT.json."""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from matmul_verify import (verify_bilinear_scheme, strassen_scheme, naive_scheme,  # noqa: E402
                           _numeric_sample_check)


def main():
    results = {"demo": "strassen", "objects": []}

    # S1-S3: reproduce Strassen 7-mult 2x2, verify symbolically
    U, V, W = strassen_scheme()
    vs = verify_bilinear_scheme(U, V, W, 2, 2, 2)
    results["objects"].append({"name": "reproduce_strassen_7mult", "verdict": vs})

    # S4: naive 8-mult control
    Un, Vn, Wn = naive_scheme(2)
    vn = verify_bilinear_scheme(Un, Vn, Wn, 2, 2, 2)
    results["objects"].append({"name": "naive_8mult_control", "verdict": vn})

    # S5: broken scheme (flip one Strassen W coefficient)
    Wb = [row[:] for row in W]
    Wb[0][0] = 0
    vb = verify_bilinear_scheme(U, V, Wb, 2, 2, 2)
    results["objects"].append({"name": "broken_strassen_flipped_W", "verdict": vb})

    # S6: gaming scheme — drop a product, tuned to pass NUMERIC samples but not the identity
    Ug, Vg, Wg = naive_scheme(2)
    drop = next(r for r in range(len(Ug)) if Ug[r][1] == 1 and Vg[r][2] == 1)  # a01*b10 product
    for t in range(4):
        Wg[t][drop] = 0
    numeric_samples = [([[1, 0], [0, 1]], [[1, 2], [3, 4]]), ([[5, 0], [7, 8]], [[1, 0], [0, 1]])]
    fooled_numeric = _numeric_sample_check(Ug, Vg, Wg, 2, 2, 2, numeric_samples)
    vg = verify_bilinear_scheme(Ug, Vg, Wg, 2, 2, 2)
    results["objects"].append({"name": "gaming_dropped_product",
                               "fooled_a_numeric_sample_checker": fooled_numeric,
                               "verdict": vg})

    checks = {
        "S1_strassen_valid": vs.get("valid") is True,
        "S2_strassen_7_beats_naive": vs.get("num_mults") == 7 and vs.get("beats_naive") is True,
        "S3_strassen_reproduction_label": vs.get("rank_status") == "MATCHES_KNOWN_RANK",
        "S4_naive_valid_8": vn.get("valid") is True and vn.get("num_mults") == 8,
        "S5_broken_caught": vb.get("valid") is False,
        "S6_gaming_caught_by_symbolic": (fooled_numeric is True and vg.get("valid") is False),
        "no_impossible_below_rank": all(
            not o["verdict"].get("beats_optimal_IMPOSSIBLE", False) for o in results["objects"]),
    }
    results["prediction_checks"] = checks
    results["all_predictions_hit"] = all(checks.values())

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RESULT.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("STRASSEN demo:")
    print(f"  reproduce Strassen : valid={vs.get('valid')} mults={vs.get('num_mults')} "
          f"beats_naive={vs.get('beats_naive')} label={vs.get('rank_status')}")
    print(f"  naive-8 control    : valid={vn.get('valid')} mults={vn.get('num_mults')}")
    print(f"  broken scheme      : valid={vb.get('valid')} (must be False) "
          f"mismatches={vb.get('mismatched_C_entries')}")
    print(f"  gaming scheme      : fooled_numeric_checker={fooled_numeric} "
          f"symbolic_valid={vg.get('valid')} (must be False)")
    for k, ok in checks.items():
        print(f"    [{'PASS' if ok else 'MISS'}] {k}")
    print(f"  ALL PREDICTIONS HIT: {results['all_predictions_hit']}")


if __name__ == "__main__":
    main()
