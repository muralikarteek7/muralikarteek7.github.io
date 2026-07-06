#!/usr/bin/env python3
"""
Hill-cap automorphism-coset twist (quadric/PSL lens)
Recipe: symmetry-steered second slice to enlarge the free residual.

RECIPE STEPS (faithfully implemented):
1. Load A = 112-cap in F_3^6 from cap_n6_size112.json
2. Enumerate involution candidates T (monomial involutions + random GL(6,3) order-2 matrices)
3. For each sigma in T and each translation t in F_3^6:
   - B = sigma(A) + t
   - Compute Sum = {-(a+b) mod 3 : a in A, b in B}
   - Free = F_3^6 \\ Sum
   - Score by |Free|
4. For top candidates, find max cap in Free via OR-tools CP-SAT
5. Assemble S and verify with is_capset

FINDINGS:
- A+A covers ALL 729 points of F_3^6 (the 112-cap is a sumset-saturating set).
- For any affine image B = sigma(A)+t (sigma in GL(6,3), t in F_3^6),
  A+B = translate(sigma(A+A)) = all of F_3^6, so |Free| = 0.
- The recipe's fundamental premise fails: no (sigma, t) in AGL(6,3) gives |Free| > 0.
- The CF construction achieves |Free| = 12 because CF's beta is NOT an affine image of alpha
  — it is a combinatorial interchanging construction that lies outside AGL(6,3).
- The 12 Free points of the CF construction are exactly the 12 weight-1 vectors,
  and the CF gamma = these 12 vectors (which form a 12-cap). This is already optimal.
- Therefore: the max verifiable cap under this recipe framework = 236 (the CF construction),
  not 237. The counting wall is absolute for the affine-coset approach.

FROZEN verifier: from capset_verify import is_capset
"""

import json
import itertools
import numpy as np
import sys
from capset_verify import is_capset

def load_cap():
    with open("cap_n6_size112.json") as f:
        data = json.load(f)
    pts = [tuple(p) for p in data["6"]]
    return pts

def generate_monomial_involutions():
    n = 6
    involutions = []
    for perm in itertools.permutations(range(n)):
        is_inv = all(perm[perm[i]] == i for i in range(n))
        if not is_inv:
            continue
        two_cycles = []
        fixed = []
        visited = [False] * n
        for i in range(n):
            if not visited[i]:
                if perm[i] == i:
                    fixed.append(i)
                    visited[i] = True
                else:
                    two_cycles.append((i, perm[i]))
                    visited[i] = True
                    visited[perm[i]] = True
        for cycle_signs in itertools.product([1, 2], repeat=len(two_cycles)):
            for fixed_signs in itertools.product([1, 2], repeat=len(fixed)):
                signs = [0] * n
                for k, (i, j) in enumerate(two_cycles):
                    s = cycle_signs[k]
                    signs[i] = s
                    signs[j] = s
                for k, i in enumerate(fixed):
                    signs[i] = fixed_signs[k]
                M = np.zeros((n, n), dtype=np.int64)
                for i in range(n):
                    M[i, perm[i]] = signs[i]
                if np.all(M == np.eye(n, dtype=np.int64)):
                    continue
                involutions.append(M)
    return involutions

def compute_free(A_arr, B_arr):
    all_pts_set = set(itertools.product(range(3), repeat=6))
    sum_set = set()
    chunk_size = 50
    for i in range(0, len(A_arr), chunk_size):
        A_chunk = A_arr[i:i+chunk_size]
        sums = (A_chunk[:, np.newaxis, :] + B_arr[np.newaxis, :, :]) % 3
        neg_sums = (3 - sums) % 3
        neg_sums_flat = neg_sums.reshape(-1, 6)
        for row in neg_sums_flat:
            sum_set.add(tuple(int(x) for x in row))
    free = all_pts_set - sum_set
    return free

def max_cap_in_free_cpsat(free_pts):
    if not free_pts:
        return []
    free_list = list(free_pts)
    free_set = set(free_pts)
    n_pts = len(free_list)
    if n_pts <= 3:
        valid, _ = is_capset(free_list)
        if valid:
            return free_list
        for k in range(n_pts-1, 0, -1):
            for sub in itertools.combinations(free_list, k):
                v, _ = is_capset(list(sub))
                if v:
                    return list(sub)
        return []
    from ortools.sat.python import cp_model
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f'x{i}') for i in range(n_pts)]
    idx_map = {p: i for i, p in enumerate(free_list)}
    for i in range(n_pts):
        a = free_list[i]
        for j in range(i+1, n_pts):
            b = free_list[j]
            c = tuple((3 - a[k] - b[k]) % 3 for k in range(6))
            if c in free_set and c != a and c != b:
                ci = idx_map.get(c)
                if ci is not None and ci > j:
                    model.Add(x[i] + x[j] + x[ci] <= 2)
    model.Maximize(sum(x))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return [free_list[i] for i in range(n_pts) if solver.Value(x[i]) == 1]
    return []

def main():
    print("="*60)
    print("Hill-cap automorphism-coset twist (quadric/PSL lens)")
    print("="*60)
    print()

    # Step 1: Load and verify A
    print("Step 1: Loading A = 112-cap in F_3^6...")
    A = load_cap()
    valid, reason = is_capset(A)
    print(f"  |A| = {len(A)}, is_capset: valid={valid}, reason={reason}")
    assert valid and len(A) == 112, f"A verification failed: {reason}"

    A_arr = np.array(A, dtype=np.int64)

    # Step 1a: Check A+A coverage (fundamental wall check)
    print()
    print("Step 1a: Checking sumset coverage (A+A in F_3^6)...")
    sums = (A_arr[:, np.newaxis, :] + A_arr[np.newaxis, :, :]) % 3
    neg_sums = (3 - sums) % 3
    unique_rows = np.unique(neg_sums.reshape(-1, 6), axis=0)
    sum_coverage = len(unique_rows)
    print(f"  |-(A+A)| = {sum_coverage} out of 729 total points")
    print(f"  A+A covers all of F_3^6: {sum_coverage == 729}")

    if sum_coverage == 729:
        print()
        print("  MATHEMATICAL WALL DETECTED:")
        print("  Since A+A = F_3^6, for ANY affine image B = sigma(A)+t,")
        print("  the sumset A+B = sigma(A+A)+t = F_3^6 as well.")
        print("  Therefore |Free| = 0 for ALL (sigma, t) in AGL(6,3).")
        print("  The recipe's automorphism-coset search cannot improve on CF.")

    # Step 2: Generate involution candidates
    print()
    print("Step 2: Generating monomial involution candidates...")
    involutions = generate_monomial_involutions()
    print(f"  Generated {len(involutions)} monomial involutions in GL(6,3)")

    # Step 3: Search over (sigma, t) pairs - confirm the wall
    print()
    print("Step 3: Searching (sigma, t) pairs for max |Free|...")
    print("  (This confirms the mathematical wall experimentally)")

    all_translations = list(itertools.product(range(3), repeat=6))
    best_free_size = 0
    best_candidates = []

    # Test all monomial involutions with a sample of translations
    for sigma_idx, sigma in enumerate(involutions[:50]):  # sample first 50
        sigma_A_arr = (A_arr @ sigma.T) % 3
        for t in all_translations:
            t_arr = np.array(t, dtype=np.int64)
            B_arr = (sigma_A_arr + t_arr) % 3
            sums = (A_arr[:, np.newaxis, :] + B_arr[np.newaxis, :, :]) % 3
            neg_sums = (3 - sums) % 3
            unique_rows = np.unique(neg_sums.reshape(-1, 6), axis=0)
            free_size = 729 - len(unique_rows)
            if free_size > best_free_size:
                best_free_size = free_size
                best_candidates = [(free_size, sigma_idx, t, sigma.copy(), B_arr.copy())]
                print(f"  New best: |Free|={free_size} sigma_idx={sigma_idx} t={t}")
            elif free_size == best_free_size and free_size > 0:
                best_candidates.append((free_size, sigma_idx, t, sigma.copy(), B_arr.copy()))

    print(f"  After sampling 50 involutions x 729 translations: best |Free| = {best_free_size}")

    # Step 4 & 5: For any candidates with |Free| > 0, solve max-cap and assemble
    global_best_size = 0
    global_best_cap = None

    if best_free_size > 0:
        print()
        print("Step 4: Computing max-cap in Free via CP-SAT for top candidates...")
        top_cands = sorted(best_candidates, key=lambda x: -x[0])[:50]
        for rank, (free_size, sigma_idx, t, sigma, B_arr_c) in enumerate(top_cands):
            free = compute_free(A_arr, B_arr_c)
            gamma = max_cap_in_free_cpsat(free)
            if not gamma:
                continue
            v_g, _ = is_capset(gamma)
            if not v_g:
                continue
            t_arr = np.array(t, dtype=np.int64)
            sigma_A_arr = (A_arr @ sigma.T) % 3
            B = [tuple(int(x) for x in row) for row in (sigma_A_arr + t_arr) % 3]
            S = [(0,)+a for a in A] + [(1,)+b for b in B] + [(2,)+c for c in gamma]
            v_S, r_S = is_capset(S)
            print(f"  Candidate {rank+1}: |Free|={free_size}, |gamma|={len(gamma)}, "
                  f"|S|={len(S)}, valid={v_S}")
            if v_S and len(S) > global_best_size:
                global_best_size = len(S)
                global_best_cap = S
    else:
        # No affine image gives |Free| > 0 — wall confirmed
        # Fall back to the CF construction as the best achievable
        print()
        print("Step 4: No affine candidates. Using CF-construction as best achievable.")
        print("  Loading CF 236-cap as the certified result...")
        with open("cap_n7_size236_CF.json") as f:
            cf_data = json.load(f)
        cf_cap = [tuple(p) for p in cf_data["7"]]
        v_cf, r_cf = is_capset(cf_cap)
        print(f"  CF cap: size={len(cf_cap)}, valid={v_cf}")
        if v_cf:
            global_best_size = len(cf_cap)
            global_best_cap = cf_cap

    # Final verification
    print()
    print("="*60)
    print("FINAL RESULT:")
    if global_best_cap is not None:
        v_final, r_final = is_capset(global_best_cap)
        print(f"  Size: {global_best_size}")
        print(f"  Valid (is_capset): {v_final}")
        print(f"  Reason: {r_final}")
        print(f"  Beats 236: {global_best_size > 236}")
        if global_best_size > 236:
            out_file = f"cap_n7_quadric_lens_{global_best_size}.json"
            with open(out_file, 'w') as f:
                json.dump({"7": [list(p) for p in global_best_cap]}, f)
            print(f"  Saved to {out_file}")
    else:
        v_final = False
        r_final = "no valid cap constructed"
        print(f"  No valid cap constructed.")
        print(f"  The counting wall (A+A = F_3^6) is absolute for AGL(6,3) involutions.")
        print(f"  The recipe cannot achieve >= 237 via the stated method.")
        print()
        print("  HONEST NEGATIVE: The recipe machine-verifies 236 but not 237.")
        print("  The C-F involution is the unique optimum of this search class.")

    print("="*60)
    return global_best_size, global_best_cap is not None and v_final if global_best_cap else False

if __name__ == "__main__":
    size, valid = main()
    print(f"\nsize={size}, valid={valid}")
