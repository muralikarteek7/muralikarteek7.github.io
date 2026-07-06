#!/usr/bin/env python3
"""INDEPENDENT MATMUL AUDIT — adversarial re-derivation.

Written by the auditor (Sonnet) without importing any codeforge verifier code.
Strassen's U,V,W coefficients are read from matmul_verify.py (which is permitted
— we're re-deriving the certificate ourselves).

Two independent methods:
  (1) NUMERIC: many random matrix pairs, check candidate == A@B numerically
  (2) SYMBOLIC: independent expansion using sympy, check identity symbolically

Also attempts to game the symbolic verifier.
"""
import json
import random
import sys

# ---- Strassen's coefficients (from matmul_verify.py strassen_scheme()) ----
# These are the raw numbers we're independently verifying
STRASSEN_U = [
    [1, 0, 0, 1],
    [0, 0, 1, 1],
    [1, 0, 0, 0],
    [0, 0, 0, 1],
    [1, 1, 0, 0],
    [-1, 0, 1, 0],
    [0, 1, 0, -1],
]
STRASSEN_V = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [0, 1, 0, -1],
    [-1, 0, 1, 0],
    [0, 0, 0, 1],
    [1, 1, 0, 0],
    [0, 0, 1, 1],
]
STRASSEN_W = [
    [1, 0, 0, 1, -1, 0, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0, 0],
    [1, -1, 1, 0, 0, 1, 0],
]


def matmul_bilinear(U, V, W, A_flat, B_flat):
    """Compute C = A*B using bilinear scheme (U,V,W). A_flat, B_flat are row-major vecs."""
    R = len(U)
    mk = len(U[0])  # m*k
    kp = len(V[0])  # k*p
    # R products
    prods = []
    for r in range(R):
        left = sum(U[r][t] * A_flat[t] for t in range(mk))
        right = sum(V[r][t] * B_flat[t] for t in range(kp))
        prods.append(left * right)
    # Reconstruct C entries
    mp = len(W)  # m*p
    C_flat = [sum(W[t][r] * prods[r] for r in range(R)) for t in range(mp)]
    return C_flat


def naive_matmul_2x2(A_flat, B_flat):
    """Standard 8-multiplication 2x2 matmul. Reference oracle."""
    a00, a01, a10, a11 = A_flat
    b00, b01, b10, b11 = B_flat
    c00 = a00*b00 + a01*b10
    c01 = a00*b01 + a01*b11
    c10 = a10*b00 + a11*b10
    c11 = a10*b01 + a11*b11
    return [c00, c01, c10, c11]


def method1_numeric(U, V, W, n_trials=10000, seed=999):
    """METHOD 1: random numeric matrices."""
    rng = random.Random(seed)
    failures = []
    for _ in range(n_trials):
        # Random integer matrices (avoid floats to avoid precision issues)
        A_flat = [rng.randint(-20, 20) for _ in range(4)]
        B_flat = [rng.randint(-20, 20) for _ in range(4)]
        cand = matmul_bilinear(U, V, W, A_flat, B_flat)
        ref = naive_matmul_2x2(A_flat, B_flat)
        if cand != ref:
            failures.append({"A": A_flat, "B": B_flat, "cand": cand, "ref": ref})
            if len(failures) >= 3:
                break
    return {
        "method": "NUMERIC (random integer matrices)",
        "trials": n_trials,
        "valid": len(failures) == 0,
        "failures": failures,
    }


def method2_symbolic(U, V, W):
    """METHOD 2: symbolic expansion using sympy. Independent implementation."""
    try:
        import sympy as sp
    except ImportError:
        return {"method": "SYMBOLIC", "error": "sympy not available"}

    # Use commutative symbols (sufficient for 2x2 numerical equivalence check;
    # theirs use non-commutative for recursive safety — we note this distinction)
    a00, a01, a10, a11 = sp.symbols('a00 a01 a10 a11')
    b00, b01, b10, b11 = sp.symbols('b00 b01 b10 b11')
    A_flat = [a00, a01, a10, a11]
    B_flat = [b00, b01, b10, b11]

    R = len(U)
    mk = len(U[0])
    kp = len(V[0])

    prods = []
    for r in range(R):
        left = sum(sp.Rational(U[r][t]) * A_flat[t] for t in range(mk))
        right = sum(sp.Rational(V[r][t]) * B_flat[t] for t in range(kp))
        prods.append(left * right)

    C_flat_cand = [sp.expand(sum(sp.Rational(W[t][r]) * prods[r] for r in range(R)))
                   for t in range(4)]

    # True A@B
    C_true = [
        sp.expand(a00*b00 + a01*b10),   # c00
        sp.expand(a00*b01 + a01*b11),   # c01
        sp.expand(a10*b00 + a11*b10),   # c10
        sp.expand(a10*b01 + a11*b11),   # c11
    ]

    mismatches = []
    for t, (cand_expr, true_expr) in enumerate(zip(C_flat_cand, C_true)):
        diff = sp.expand(cand_expr - true_expr)
        if diff != 0:
            mismatches.append({"entry": t, "residual": str(diff)})

    return {
        "method": "SYMBOLIC (commutative sympy, independent expansion)",
        "valid": len(mismatches) == 0,
        "mismatches": mismatches,
        "num_mults": R,
        "note": "commutative; their verifier uses non-commutative for recursive safety",
    }


# ---- GAMING ATTEMPTS ----

def attempt_game_matmul_numeric_tuning():
    """Attempt to craft a scheme that passes a small numeric sample but isn't correct symbolically.

    Strategy: Take naive 8-mult scheme, zero out one product (a01*b10 contribution to c00).
    For any A with a01=0 or B with b10=0, it still gives correct c00 numerically.
    We check: does this pass 100 random samples with a01=0? Yes. Does it pass full numeric? No.
    """
    # Drop product r=5 from naive: U[5]=[0,1,0,0] (picks a01), V[5]=[0,0,1,0] (picks b10)
    # naive scheme for 2x2:
    # r=0: a00*b00 -> C00
    # r=1: a00*b01 -> C01
    # r=2: a01*b10 -> C00
    # r=3: a01*b11 -> C01
    # r=4: a10*b00 -> C10
    # r=5: a10*b01 -> C11 (note: this is a10*b01, not a01*b10)
    # r=6: a11*b10 -> C10
    # r=7: a11*b11 -> C11
    # For 2x2, row-major: A=[a00,a01,a10,a11], B=[b00,b01,b10,b11]
    U_naive = [
        [1,0,0,0],[1,0,0,0],[0,1,0,0],[0,1,0,0],
        [0,0,1,0],[0,0,1,0],[0,0,0,1],[0,0,0,1]
    ]
    V_naive = [
        [1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],
        [1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]
    ]
    W_naive = [
        [1,0,1,0,0,0,0,0],  # C00 = r0 + r2
        [0,1,0,1,0,0,0,0],  # C01 = r1 + r3
        [0,0,0,0,1,0,1,0],  # C10 = r4 + r6
        [0,0,0,0,0,1,0,1],  # C11 = r5 + r7
    ]
    # Drop r2 (a01*b10 that contributes to C00)
    W_gamed = [row[:] for row in W_naive]
    W_gamed[0][2] = 0  # remove r2's contribution to C00

    # Check: does this pass when a01=0?
    rng = random.Random(777)
    sample_a01_zero = [[rng.randint(-10,10) if i!=1 else 0 for i in range(4)] for _ in range(100)]
    B_samples = [[rng.randint(-10,10) for _ in range(4)] for _ in range(100)]
    sample_passes = all(
        matmul_bilinear(U_naive, V_naive, W_gamed, A_flat, B_flat) == naive_matmul_2x2(A_flat, B_flat)
        for A_flat, B_flat in zip(sample_a01_zero, B_samples)
    )

    # Now try the RANDOM tests from method1 — does it fail?
    numeric_result = method1_numeric(U_naive, V_naive, W_gamed, n_trials=200, seed=12345)

    return {
        "game_attempt": "drop a01*b10 product from naive scheme, check if biased sample passes",
        "biased_sample_100_a01_zero_passed": sample_passes,
        "random_numeric_200_valid": numeric_result["valid"],
        "random_numeric_failures": len(numeric_result["failures"]),
        "conclusion": (
            "GAME partially succeeded: biased sample (a01=0) passed, but random numeric caught it"
            if sample_passes and not numeric_result["valid"]
            else "GAME failed even the biased sample"
        ),
    }


def attempt_game_symbolic_nonzero_residual():
    """Attempt to construct a scheme where residual cancels symbolically if commutative,
    but not non-commutative. (Testing whether their non-comm requirement matters here.)

    For 2x2 scalar matrices, commutativity holds, so the distinction only matters for
    recursive/block matrix application. We try to show this distinction.
    """
    # The naive scheme for 2x2 IS commutative-safe, so there's no attack here.
    # We construct a scheme that WORKS for commutative but NOT non-commutative:
    # Swap the order of left/right factors for product r=0.
    # M1 = (a00+a11)*(b00+b11) -> normally left=a00+a11, right=b00+b11
    # If we swap: right*left = (b00+b11)*(a00+a11) != left*right for non-commutative
    # For scalar numbers they're equal, but for matrices they differ.

    try:
        import sympy as sp
    except ImportError:
        return {"error": "sympy not available"}

    # Non-commutative symbols
    a00,a01,a10,a11 = sp.symbols('a00 a01 a10 a11', commutative=False)
    b00,b01,b10,b11 = sp.symbols('b00 b01 b10 b11', commutative=False)

    # Swap M1: use right*left instead of left*right
    # Normal: M1 = (a00+a11)*(b00+b11)
    # Swapped: M1_swap = (b00+b11)*(a00+a11)
    M1_normal = (a00+a11)*(b00+b11)
    M1_swap = (b00+b11)*(a00+a11)

    # Compute difference of expansions
    diff = sp.expand(M1_normal - M1_swap)
    diff_is_zero = (diff == 0)

    # Now check commutative
    a00c,a01c,a10c,a11c = sp.symbols('a00 a01 a10 a11', commutative=True)
    b00c,b01c,b10c,b11c = sp.symbols('b00 b01 b10 b11', commutative=True)
    M1_nc_comm = (a00c+a11c)*(b00c+b11c)
    M1_swap_comm = (b00c+b11c)*(a00c+a11c)
    diff_comm = sp.expand(M1_nc_comm - M1_swap_comm)
    diff_comm_is_zero = (diff_comm == 0)

    return {
        "game_attempt": "check if swapping L/R product factors fools commutative vs non-commutative checker",
        "noncommutative_M1_swap_equals_normal": diff_is_zero,
        "commutative_M1_swap_equals_normal": diff_comm_is_zero,
        "conclusion": (
            "The swap IS caught by non-commutative check but NOT by commutative check — "
            "their non-comm approach is strictly stronger for recursive safety"
            if not diff_is_zero and diff_comm_is_zero
            else "Both agree — no attack here"
        ),
    }


if __name__ == "__main__":
    print("=" * 70)
    print("INDEPENDENT MATMUL AUDIT")
    print("=" * 70)

    print("\n--- Method 1: Numeric verification (10,000 random trials) ---")
    r_num = method1_numeric(STRASSEN_U, STRASSEN_V, STRASSEN_W)
    print(f"  Trials: {r_num['trials']}")
    print(f"  Valid:  {r_num['valid']}")
    print(f"  Failures: {len(r_num['failures'])}")
    print(f"  Num mults: {len(STRASSEN_U)}")

    print("\n--- Method 2: Symbolic verification (independent sympy) ---")
    r_sym = method2_symbolic(STRASSEN_U, STRASSEN_V, STRASSEN_W)
    if "error" in r_sym:
        print(f"  Error: {r_sym['error']}")
    else:
        print(f"  Valid: {r_sym['valid']}")
        print(f"  Mismatches: {r_sym['mismatches']}")
        print(f"  Num mults: {r_sym['num_mults']}")
        print(f"  Note: {r_sym['note']}")

    both_agree = r_num.get("valid") and r_sym.get("valid")
    print(f"\n  AGREEMENT: {'AGREE (both valid)' if both_agree else 'DISAGREE'}")

    print("\n--- Gaming Attempt 1: Numerically biased sample ---")
    g1 = attempt_game_matmul_numeric_tuning()
    print(f"  {g1.get('conclusion', g1)}")
    print(f"  Biased sample (a01=0) passed: {g1.get('biased_sample_100_a01_zero_passed')}")
    print(f"  Random 200 trials valid: {g1.get('random_numeric_200_valid')}")

    print("\n--- Gaming Attempt 2: Commutative vs non-commutative ---")
    g2 = attempt_game_symbolic_nonzero_residual()
    if "error" not in g2:
        print(f"  Non-comm M1 swap == normal: {g2.get('noncommutative_M1_swap_equals_normal')}")
        print(f"  Comm M1 swap == normal:     {g2.get('commutative_M1_swap_equals_normal')}")
        print(f"  Conclusion: {g2.get('conclusion')}")

    results = {
        "numeric": r_num,
        "symbolic": r_sym,
        "gaming_attempts": [g1, g2],
    }
    with open("/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/weapons/codeforge/audit_independent/matmul_audit_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\nResults saved to matmul_audit_results.json")
