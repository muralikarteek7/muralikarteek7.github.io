#!/usr/bin/env python3
"""INDEPENDENT SORTNET AUDIT — adversarial re-derivation.

Written by the auditor (Sonnet) without importing any codeforge verifier code.
Goal: independently verify the three networks in demo_sortnet/RESULT.json using
TWO methods:
  (1) Exhaustive permutation test — test ALL n! permutations of distinct integers
      (different approach from their 0/1 binary method; a genuine cross-check)
  (2) 0/1 binary sweep — same concept as theirs but written fresh from scratch

Also attempts to game the sortnet verifier.
"""
import itertools
import json
import random

# ---- The networks from demo_sortnet/RESULT.json ----
N8_BATCHER = [
    (0,1),(2,3),(0,2),(1,3),(1,2),
    (4,5),(6,7),(4,6),(5,7),(5,6),
    (0,4),(2,6),(2,4),(1,5),(3,7),(3,5),
    (1,2),(3,4),(5,6)
]

N6_GREEDY = [
    (0,5),(1,4),(2,5),(1,3),(2,3),(0,2),(3,4),(2,3),(0,1),(1,2),(4,5),(3,4),(2,3)
]

N7_GREEDY = [
    (0,6),(1,5),(2,4),(0,3),(3,5),(4,6),(1,4),(3,4),(2,3),(0,2),(1,2),(2,3),(3,4),(4,5),(5,6),(4,5),(3,4),(0,1)
]


# ---- Independent implementations (written fresh, no import of theirs) ----

def apply_network_audit(network, arr):
    """Run comparator network on array. (i,j) means: ensure arr[i] <= arr[j]."""
    a = list(arr)
    for (i, j) in network:
        # always put min at i, max at j regardless of input order
        lo, hi = (i, j) if i < j else (j, i)
        if a[lo] > a[hi]:
            a[lo], a[hi] = a[hi], a[lo]
    return a


def is_sorted_audit(arr):
    return all(arr[k] <= arr[k+1] for k in range(len(arr)-1))


def verify_by_permutations(network, n):
    """METHOD 1: test ALL n! permutations of [0..n-1]. Fully independent of 0/1 approach."""
    values = list(range(n))
    total = 0
    failures = []
    for perm in itertools.permutations(values):
        perm = list(perm)
        result = apply_network_audit(network, perm)
        total += 1
        if not is_sorted_audit(result):
            failures.append(perm)
            if len(failures) >= 3:
                break
    return {
        "method": "PERMUTATION (n! distinct)",
        "n": n,
        "permutations_tested": total,
        "valid": len(failures) == 0,
        "first_failures": failures[:3],
        "num_comparators": len(network),
    }


def verify_by_binary_sweep(network, n):
    """METHOD 2: exhaustive 0/1 sweep (written fresh, independent code)."""
    failures = []
    for mask in range(1 << n):
        vec = [(mask >> k) & 1 for k in range(n)]
        result = apply_network_audit(network, vec)
        if not is_sorted_audit(result):
            failures.append(vec)
            if len(failures) >= 3:
                break
    return {
        "method": "BINARY SWEEP (2^n)",
        "n": n,
        "binary_inputs_tested": 1 << n,
        "valid": len(failures) == 0,
        "first_failures": failures[:3],
        "num_comparators": len(network),
    }


def count_comparators(network):
    return len(network)


# ---- GAMING ATTEMPTS ----

def attempt_game_sortnet_partial_sample():
    """Attempt 1: craft a network that sorts a large sample but NOT all inputs.
    Use n=4. Known minimal sorter is 5 comparators. We try a broken 4-comparator
    network and check if a sample-based verifier would pass it (while ours catches it).
    """
    # This network does NOT sort all inputs for n=4 (drop the merge step)
    broken_n4 = [(0,1), (2,3), (0,2), (1,3)]  # missing (1,2) to complete the sort

    # How many of the 2^4=16 binary inputs does it sort?
    binary_passes = 0
    binary_failures = []
    for mask in range(16):
        vec = [(mask >> k) & 1 for k in range(4)]
        result = apply_network_audit(broken_n4, vec)
        if is_sorted_audit(result):
            binary_passes += 1
        else:
            binary_failures.append(vec)

    # How many of the 4!=24 permutations does it sort?
    perm_passes = 0
    perm_failures = []
    for perm in itertools.permutations(range(4)):
        perm = list(perm)
        result = apply_network_audit(broken_n4, perm)
        if is_sorted_audit(result):
            perm_passes += 1
        else:
            perm_failures.append(perm)

    # A sample-based verifier using 10 random inputs
    rng = random.Random(42)
    sample_10 = [[rng.randint(0,9) for _ in range(4)] for _ in range(10)]
    sample_passed = all(is_sorted_audit(apply_network_audit(broken_n4, s)) for s in sample_10)

    return {
        "game_attempt": "craft broken n=4 network, check if sample verifier fooled",
        "network": broken_n4,
        "binary_passed": binary_passes,
        "binary_total": 16,
        "binary_failures_count": len(binary_failures),
        "perm_passed": perm_passes,
        "perm_total": 24,
        "perm_failures_count": len(perm_failures),
        "sample_10_random_all_passed": sample_passed,
        "conclusion": (
            "GAME SUCCEEDED vs sample-checker" if sample_passed and len(binary_failures) > 0
            else "GAME FAILED: the broken network also fails random samples"
        ),
        "exhaustive_catches_it": len(binary_failures) > 0,
    }


def attempt_game_sortnet_large_sample_but_invalid():
    """Attempt 2: n=6, build a network that passes 63/64 binary inputs but fails 1."""
    # Start with a valid n=6 sorter and break the very last comparator
    # Known valid n=6 network (Bose-Nelson or similar)
    valid_n6 = [(0,1),(2,3),(4,5),(0,2),(1,3),(0,1),(2,4),(3,5),(2,3),(4,5),(1,4),(0,1),(3,4),(1,2),(3,4)]
    # Verify it is actually valid first
    perm_check = verify_by_binary_sweep(valid_n6, 6)
    if not perm_check["valid"]:
        return {"error": "test network isn't valid to begin with", "debug": perm_check}

    # Drop the last comparator to create a subtly broken version
    almost_valid = valid_n6[:-1]
    binary_check = verify_by_binary_sweep(almost_valid, 6)
    # Count how many pass
    passes = 0
    for mask in range(64):
        vec = [(mask >> k) & 1 for k in range(6)]
        result = apply_network_audit(almost_valid, vec)
        if is_sorted_audit(result):
            passes += 1

    return {
        "game_attempt": "drop last comparator from valid n=6, see how many pass",
        "binary_passes_out_of_64": passes,
        "exhaustive_catches_it": not binary_check["valid"],
        "first_failure": binary_check["first_failures"][:1],
        "conclusion": (
            f"Network passes {passes}/64 binary inputs — a 63/64 sample might miss the failure, "
            "but exhaustive 0/1 sweep catches it"
            if not binary_check["valid"] else "Both still valid after drop"
        ),
    }


if __name__ == "__main__":
    print("=" * 70)
    print("INDEPENDENT SORTNET AUDIT")
    print("=" * 70)

    print("\n--- 1. Re-deriving n=8 Batcher network ---")
    r8_perm = verify_by_permutations(N8_BATCHER, 8)
    r8_bin = verify_by_binary_sweep(N8_BATCHER, 8)
    print(f"  Permutation method: valid={r8_perm['valid']}, tested={r8_perm['permutations_tested']} perms")
    print(f"  Binary sweep:       valid={r8_bin['valid']}, tested={r8_bin['binary_inputs_tested']} inputs")
    print(f"  Comparator count:   {count_comparators(N8_BATCHER)} (claimed: 19, known optimal: 19)")
    print(f"  Agreement: {'AGREE (both valid)' if r8_perm['valid'] and r8_bin['valid'] else 'DISAGREE'}")

    print("\n--- 2. Re-deriving n=6 greedy network ---")
    r6_perm = verify_by_permutations(N6_GREEDY, 6)
    r6_bin = verify_by_binary_sweep(N6_GREEDY, 6)
    print(f"  Permutation method: valid={r6_perm['valid']}, tested={r6_perm['permutations_tested']} perms")
    print(f"  Binary sweep:       valid={r6_bin['valid']}, tested={r6_bin['binary_inputs_tested']} inputs")
    print(f"  Comparator count:   {count_comparators(N6_GREEDY)} (claimed: 13, known optimal: 12)")
    print(f"  Agreement: {'AGREE (both valid)' if r6_perm['valid'] and r6_bin['valid'] else 'DISAGREE'}")

    print("\n--- 3. Re-deriving n=7 greedy network ---")
    r7_perm = verify_by_permutations(N7_GREEDY, 7)
    r7_bin = verify_by_binary_sweep(N7_GREEDY, 7)
    print(f"  Permutation method: valid={r7_perm['valid']}, tested={r7_perm['permutations_tested']} perms")
    print(f"  Binary sweep:       valid={r7_bin['valid']}, tested={r7_bin['binary_inputs_tested']} inputs")
    print(f"  Comparator count:   {count_comparators(N7_GREEDY)} (claimed: 18, known optimal: 16)")
    print(f"  Agreement: {'AGREE (both valid)' if r7_perm['valid'] and r7_bin['valid'] else 'DISAGREE'}")

    print("\n--- 4. Gaming attempts ---")
    g1 = attempt_game_sortnet_partial_sample()
    print(f"\n  Game 1 (broken n=4 network vs sample checker):")
    print(f"    Binary passes: {g1['binary_passed']}/16")
    print(f"    Perm passes: {g1['perm_passed']}/24")
    print(f"    Sample (10 random) passed: {g1['sample_10_random_all_passed']}")
    print(f"    Exhaustive catches it: {g1['exhaustive_catches_it']}")
    print(f"    Conclusion: {g1['conclusion']}")

    g2 = attempt_game_sortnet_large_sample_but_invalid()
    print(f"\n  Game 2 (n=6 almost-valid network):")
    if "error" not in g2:
        print(f"    Binary passes: {g2['binary_passes_out_of_64']}/64")
        print(f"    Exhaustive catches it: {g2['exhaustive_catches_it']}")
        print(f"    Conclusion: {g2['conclusion']}")
    else:
        print(f"    Error: {g2.get('error')}")

    # Save results
    results = {
        "n8_batcher": {"permutation": r8_perm, "binary": r8_bin},
        "n6_greedy": {"permutation": r6_perm, "binary": r6_bin},
        "n7_greedy": {"permutation": r7_perm, "binary": r7_bin},
        "gaming_attempts": [g1, g2],
    }
    with open("/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/weapons/codeforge/audit_independent/sortnet_audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to sortnet_audit_results.json")
