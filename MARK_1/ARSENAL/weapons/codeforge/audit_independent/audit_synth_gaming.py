#!/usr/bin/env python3
"""INDEPENDENT SYNTH-VERIFY GAMING AUDIT.

Adversarial attempts to get a false accept from synth_verify.py.
Written by auditor (Sonnet) — imports synth_verify only to TEST it (not to build on it).

Strategy: we try to reverse-engineer the LCG seeds used for hidden/property/differential
tests to produce a candidate that HARD-CODES the expected outputs for those inputs, while
also passing visible tests. If successful, this would be a false accept.
"""
import sys
import os
import json

sys.path.insert(0, "/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/weapons/codeforge")
from synth_verify import verify_synthesis, LCG

# ---- Reconstruct the LCG sequence to predict hidden/property/differential inputs ----

def reconstruct_lcg_property_inputs(spec):
    """Reconstruct the property input sequence using the spec's seed and input_gen."""
    rng = LCG(spec.get("seed", 12345))
    n = spec.get("n_property", 200)
    return [spec["input_gen"](rng) for _ in range(n)]


def reconstruct_lcg_diff_inputs(spec):
    """Reconstruct the differential input sequence."""
    rng = LCG(spec.get("seed", 12345) ^ 0x5DEECE66)
    n = spec.get("n_diff", 200)
    return [spec["input_gen"](rng) for _ in range(n)]


# ---- The spec from synth_verify._spec_sorted_unique() ----
def make_spec():
    return {
        "entry": "f",
        "visible_tests": [(([3, 1, 2],), [1, 2, 3]), (([1, 1],), [1])],
        "hidden_tests": [(([2, 2, 1, 3, 3],), [1, 2, 3]), (([],), []),
                         (([5, 4, 4, 5],), [4, 5]), (([0],), [0])],
        "reference_fn": lambda args: sorted(set(args[0])),
        "property_fn": lambda args, out: (isinstance(out, list)
                                          and out == sorted(out)
                                          and set(out) == set(args[0])
                                          and len(out) == len(set(out))),
        "input_gen": lambda rng: ([rng.randint(0, 5) for _ in range(rng.randint(0, 8))],),
        "n_property": 150, "n_diff": 150, "seed": 7,
    }


def attempt_hardcode_visible_only():
    """Gaming attempt 1: hard-code only visible tests (this is the designed-against attack).
    Should be caught as GAMING_DETECTED."""
    spec = make_spec()
    gaming_src = (
        "def f(nums):\n"
        "    table = {(3,1,2):[1,2,3], (1,1):[1]}\n"
        "    return table.get(tuple(nums), [])\n"
    )
    result = verify_synthesis(gaming_src, spec)
    return {
        "attempt": "hardcode_visible_only",
        "verdict": result["verdict"],
        "passed": result["passed"],
        "gamed_expected": True,
        "caught": not result["passed"],
        "verdict_expected": "GAMING_DETECTED",
        "verdict_correct": result["verdict"] == "GAMING_DETECTED",
    }


def attempt_reverse_engineer_lcg():
    """Gaming attempt 2: reverse-engineer the LCG to predict BOTH hidden AND property inputs,
    then hard-code outputs for ALL of them.

    If this works, it means the frozen seed is a weakness: someone who reads the source code
    can pre-compute all fuzz inputs and hard-code a lookup table.

    This is a source-code-level attack, not a black-box attack. We note this as a design issue.
    """
    spec = make_spec()

    # Reconstruct all property inputs
    prop_inputs = reconstruct_lcg_property_inputs(spec)
    diff_inputs = reconstruct_lcg_diff_inputs(spec)
    hidden_tests = spec["hidden_tests"]
    visible_tests = spec["visible_tests"]
    ref = spec["reference_fn"]

    # Build a lookup table of all known inputs -> correct outputs
    table = {}
    for args, exp in visible_tests:
        table[tuple(args[0])] = exp
    for args, exp in hidden_tests:
        table[tuple(args[0])] = exp
    for args in prop_inputs:
        key = tuple(args[0])
        table[key] = sorted(set(args[0]))  # pre-compute correct answer
    for args in diff_inputs:
        key = tuple(args[0])
        table[key] = sorted(set(args[0]))  # pre-compute correct answer

    # Build a hard-coded function that uses the lookup table, falling back to an incorrect answer
    # (to distinguish from the correct implementation)
    table_repr = repr(dict(table))
    gaming_src = (
        f"def f(nums):\n"
        f"    table = {table_repr}\n"
        f"    key = tuple(nums)\n"
        f"    if key in table:\n"
        f"        return table[key]\n"
        f"    # WRONG for unseen inputs: return empty list\n"
        f"    return []\n"
    )

    result = verify_synthesis(gaming_src, spec)
    return {
        "attempt": "reverse_engineer_lcg_hardcode_all_test_inputs",
        "description": (
            "Pre-computed all property+differential inputs by reading the source LCG seed, "
            "built a lookup table. Falls back to [] for unseen inputs."
        ),
        "verdict": result["verdict"],
        "passed": result["passed"],
        "gamed_expected": True,
        "caught_verdict": result["verdict"],
        "analysis": (
            "ATTACK SUCCEEDED: false accept" if result["passed"] else
            "Attack FAILED: verifier still caught it (likely property test with input outside pre-computed set, "
            "or the lookup table construction is incomplete)"
        ),
        "visible_pass": result.get("visible_pass"),
        "hidden_failures": result.get("hidden_failures"),
        "property_failures": result.get("property_failures"),
        "differential_failures": result.get("differential_failures"),
    }


def attempt_lcg_seed_prediction_analysis():
    """Analysis: can we predict the EXACT LCG output? Yes, the LCG is deterministic.
    This is a structural weakness: anyone reading synth_verify.py can pre-compute all fuzz inputs.
    The question is whether this constitutes a security vulnerability or just a design note."""
    spec = make_spec()
    prop_inputs = reconstruct_lcg_property_inputs(spec)
    diff_inputs = reconstruct_lcg_diff_inputs(spec)

    # Verify our reconstruction matches what the verifier would use
    # by testing a correct implementation and seeing if property/diff pass
    good_src = "def f(nums):\n    return sorted(set(nums))\n"
    result_good = verify_synthesis(good_src, spec)

    # The LCG is deterministic, so we CAN predict every fuzz input.
    # Sample the first 5 property inputs for audit evidence.
    sample_prop = [list(a[0]) for a in prop_inputs[:5]]
    sample_diff = [list(a[0]) for a in diff_inputs[:5]]

    return {
        "analysis": "LCG_seed_determinism",
        "seed": spec.get("seed", 12345),
        "n_property": spec.get("n_property", 200),
        "n_diff": spec.get("n_diff", 200),
        "can_predict_all_inputs": True,
        "sample_first5_property_inputs": sample_prop,
        "sample_first5_diff_inputs": sample_diff,
        "good_impl_verified": result_good["verdict"],
        "implication": (
            "The LCG seed is a FIXED CONSTANT in source code. An attacker who reads synth_verify.py "
            "can pre-compute ALL fuzz inputs and hard-code a lookup table. "
            "This is a source-code-level weakness, not a black-box security issue. "
            "Mitigations: randomized seeds per run (not reproducible), or truly hidden test inputs not in source."
        ),
    }


if __name__ == "__main__":
    print("=" * 70)
    print("INDEPENDENT SYNTH-VERIFY GAMING AUDIT")
    print("=" * 70)

    print("\n--- Gaming Attempt 1: Hard-code visible tests only ---")
    g1 = attempt_hardcode_visible_only()
    print(f"  Verdict: {g1['verdict']}")
    print(f"  Passed (false accept): {g1['passed']}")
    print(f"  Correctly caught: {g1['caught']}")
    print(f"  Verdict matches expected GAMING_DETECTED: {g1['verdict_correct']}")

    print("\n--- Gaming Attempt 2: Reverse-engineer LCG, hardcode all test inputs ---")
    g2 = attempt_reverse_engineer_lcg()
    print(f"  Verdict: {g2['verdict']}")
    print(f"  Passed (false accept): {g2['passed']}")
    print(f"  Analysis: {g2['analysis']}")
    if g2.get("property_failures"):
        print(f"  Property failures: {g2['property_failures'][:1]}")
    if g2.get("differential_failures"):
        print(f"  Differential failures: {g2['differential_failures'][:1]}")

    print("\n--- Analysis: LCG seed predictability ---")
    g3 = attempt_lcg_seed_prediction_analysis()
    print(f"  Can predict all inputs: {g3['can_predict_all_inputs']}")
    print(f"  Sample property inputs (first 5): {g3['sample_first5_property_inputs']}")
    print(f"  Implication: {g3['implication']}")

    results = {"gaming_attempts": [g1, g2, g3]}
    with open("/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/weapons/codeforge/audit_independent/synth_gaming_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\nResults saved to synth_gaming_results.json")
