#!/usr/bin/env python3
"""
orbit-twisted residual-grow into the binary cube — FAST vectorized version
Recipe steps 1-7 exactly as specified.
Uses numpy FFT-based convolution in Z/3^6 for O(|G|*729*log(729)) total.
"""
import itertools, json, sys, math, random, time
import numpy as np
from capset_verify import is_capset

# ──────────────────────────────────────────────────────────────────────────────
# STEP 1: Build alpha and beta exactly as in build_236.py
# ──────────────────────────────────────────────────────────────────────────────

def expand(t):
    star = [i for i, c in enumerate(t) if c == '*']
    out = []
    for vals in itertools.product([1, 2], repeat=len(star)):
        v = [0] * 6
        for p, val in zip(star, vals): v[p] = val
        out.append(tuple(v))
    return out

def block1():
    T = []
    for i in range(5):
        t = ['0'] * 6
        for k in range(3): t[1 + (i + k) % 5] = '*'
        T.append(t)
    return T

def block2():
    T = []
    for i in range(5):
        t = ['0'] * 6; t[0] = '*'
        for p in (i % 5, (i + 2) % 5): t[1 + p] = '*'
        T.append(t)
    return T

def delta():
    return [v for v in itertools.product([1, 2], repeat=6) if sum(x == 1 for x in v) % 2 == 0]

def interchange(t):
    return ['*' if c == '0' else '0' for c in t]

upper = block1() + block2()
D = set(delta())
alpha_set = set()
for t in upper: alpha_set |= set(expand(t))
alpha_set |= D
beta_base = set()
for t in upper: beta_base |= set(expand(interchange(t)))
beta_base |= D

assert len(alpha_set) == 112, f"|alpha|={len(alpha_set)}"
assert len(beta_base) == 112, f"|beta|={len(beta_base)}"

# Verify as 6-caps
def is_6cap_fast(pts_list):
    pts_s = set(pts_list)
    for a, b in itertools.combinations(pts_list, 2):
        c = tuple((-a[i] - b[i]) % 3 for i in range(6))
        if c in pts_s and c != a and c != b:
            return False
    return True

assert is_6cap_fast(list(alpha_set)), "alpha is not a cap"
assert is_6cap_fast(list(beta_base)), "beta is not a cap"
print(f"STEP 1: |alpha|=|beta|=112, both are caps. OK")

# ──────────────────────────────────────────────────────────────────────────────
# Fast infrastructure: integer encoding for F_3^6
# ──────────────────────────────────────────────────────────────────────────────

ALL_POINTS_6 = list(itertools.product(range(3), repeat=6))  # 729 points
pt_to_idx = {p: i for i, p in enumerate(ALL_POINTS_6)}

# Powers of 3 for indexing
POW3 = np.array([243, 81, 27, 9, 3, 1], dtype=np.int32)

def pts_to_idx_arr(pts):
    """Convert list of 6-tuples to array of flat indices."""
    a = np.array(pts, dtype=np.int32)
    return a @ POW3

def idx_to_pt(i):
    v = []
    for k in range(6):
        v.append(i // POW3[k] % 3)
    return tuple(v)

# alpha as indicator vector (729-bit)
alpha_arr_pts = np.array(list(alpha_set), dtype=np.int32)
alpha_idx = alpha_arr_pts @ POW3  # shape (112,)
alpha_vec = np.zeros(729, dtype=np.bool_)
alpha_vec[alpha_idx] = True

beta_arr_pts = np.array(list(beta_base), dtype=np.int32)
beta_idx = beta_arr_pts @ POW3
beta_vec = np.zeros(729, dtype=np.bool_)
beta_vec[beta_idx] = True

# Reshape to 3^6 tensor for convolution
def vec_to_tensor(v):
    return v.reshape([3]*6).astype(np.float32)

def tensor_to_vec(t):
    return t.reshape(729)

# Sumset via "convolution" in Z_3^6:
# S[x] = 1 iff exists a,b: a+b = -x mod 3
# = 1 iff exists a,b: a+b+x = 0 mod 3
# Compute using tensor approach:
# sum_{a,b} alpha[a]*beta[b]*delta(x = -(a+b)) = sum_{a} alpha[a]*beta[-x-a]
# This is a cross-correlation. Use numpy's n-dimensional approach.

def compute_sumset_vec(alpha_v, beta_v):
    """
    Compute S: S[x] = 1 iff -(a+b)=x for some a in alpha, b in beta.
    Equivalently, we convolve alpha and beta in Z_3^6 and check > 0.
    """
    # Reverse beta (negate in Z_3^6): neg_beta[x] = beta[-x mod 3]
    # Then S = alpha conv neg_beta
    # But we need S[x] = (alpha * beta_shifted)[x] where shift is negation

    # Use direct approach: for each a in support of alpha,
    # mark (a + beta_pts) mod 3 as in alpha+beta
    # Then S[x] = 1 iff -x in alpha+beta

    alpha_pts = np.where(alpha_v)[0]
    beta_pts = np.where(beta_v)[0]

    # Convert to coordinate arrays
    alpha_coords = np.array([idx_to_pt(i) for i in alpha_pts], dtype=np.int32)  # (|A|, 6)
    beta_coords = np.array([idx_to_pt(i) for i in beta_pts], dtype=np.int32)    # (|B|, 6)

    # Compute all sums: (|A|, 1, 6) + (1, |B|, 6) = (|A|, |B|, 6)
    sums = (alpha_coords[:, None, :] + beta_coords[None, :, :]) % 3  # (|A|, |B|, 6)
    flat = sums.reshape(-1, 6) @ POW3  # (|A|*|B|,)

    # S[x] = 1 iff x (= a+b) is in flat, i.e., -x is the forbidden zone
    apb_vec = np.zeros(729, dtype=np.bool_)
    apb_vec[flat] = True

    # -(a+b) = x means a+b = -x mod 3
    # Create S where S[x] = 1 iff x = -(a+b) for some pair
    # = apb_vec[(-x) mod 3] for each x
    neg_idx = np.array([pt_to_idx[tuple((-np.array(ALL_POINTS_6[i])) % 3)] for i in range(729)])
    S = apb_vec[neg_idx]  # S[x] = apb_vec[-x] = 1 iff -x in a+b, i.e., -(a+b)=x
    return S

# Test on base alpha, beta
print("Computing base sumset...")
t0 = time.time()
S_base = compute_sumset_vec(alpha_vec, beta_vec)
print(f"  Sumset computed in {time.time()-t0:.2f}s, |S|={S_base.sum()}, |R|={(~S_base).sum()}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 2: Enumerate all g in G = S_6 x {0,1}^6
# ──────────────────────────────────────────────────────────────────────────────

print("\nSTEP 2: Enumerating 46080 monomial maps...")
t0 = time.time()

all_perms = list(itertools.permutations(range(6)))
all_swaps = list(itertools.product([0, 1], repeat=6))

# Precompute negation index map
neg_idx = np.array([pt_to_idx[tuple((-np.array(p)) % 3)] for p in ALL_POINTS_6])

# Binary cube non-zero points (as 2x mod 3 indices)
binary_cube_2_idx = []
for v in itertools.product([0, 1], repeat=6):
    if any(x != 0 for x in v):
        v2 = tuple((2*x) % 3 for x in v)
        binary_cube_2_idx.append(pt_to_idx[v2])
binary_cube_2_idx = np.array(binary_cube_2_idx)

# For each monomial g, we need beta_g = g(beta).
# g acts as: w_i = v_{pi(i)}, then w_i -> 2*w_i if s_i=1
# This permutes and scales the beta array.

# Precompute: for each permutation, what's the permuted beta?
# Then for each swap pattern, apply the scaling.

# We'll store top results by (residual_size, free_g)
N_TOP = 50
# Use list of (R_size, free_g, perm_idx, swap_bits, beta_g_indices)
top_entries = []

# To apply g to all 729 points at once:
# First permute coordinates (column permutation on the 6-coord array)
all_coords = np.array(ALL_POINTS_6, dtype=np.int32)  # (729, 6)

# Precompute a "permutation action" on point indices:
# For perm pi: ALL_POINTS_6[g_map[i]] = pi-permuted version of ALL_POINTS_6[i]
# Similarly for swaps.

def compute_perm_map(perm):
    """For each point index i, return index of pi(point_i)."""
    # pi(v)[j] = v[perm^{-1}(j)] -- but we defined g as w_i = v_{pi(i)}
    # So g(v)[i] = v[pi(i)], i.e., the new i-th coord is the old pi(i)-th coord
    permuted_coords = all_coords[:, list(perm)]  # (729, 6)
    return permuted_coords @ POW3  # (729,) - indices of permuted points

def compute_swap_map(swap_bits, base_indices):
    """Apply swap (multiply coords by 2 mod 3) to points given by base_indices."""
    # Start from the coordinates of base_indices points
    coords = all_coords[base_indices].copy()  # (??, 6)
    for i, bit in enumerate(swap_bits):
        if bit:
            coords[:, i] = (2 * coords[:, i]) % 3
    return coords @ POW3

processed = 0
TOTAL_G = len(all_perms) * len(all_swaps)

for pi_idx, perm in enumerate(all_perms):
    # Compute permuted beta indices (apply perm to beta_arr_pts)
    beta_perm_coords = beta_arr_pts[:, list(perm)]  # (112, 6)

    for swap_bits in all_swaps:
        # Apply swaps
        beta_g_coords = beta_perm_coords.copy()
        for i, bit in enumerate(swap_bits):
            if bit:
                beta_g_coords[:, i] = (2 * beta_g_coords[:, i]) % 3

        beta_g_idx = beta_g_coords @ POW3  # (112,) flat indices

        # Compute sumset: all alpha_coords + beta_g_coords mod 3
        # (112, 1, 6) + (1, 112, 6) -> (112, 112, 6)
        sums_coords = (alpha_arr_pts[:, None, :] + beta_g_coords[None, :, :]) % 3
        flat_sums = sums_coords.reshape(-1, 6) @ POW3  # (112*112,)

        apb_vec = np.zeros(729, dtype=np.bool_)
        apb_vec[flat_sums] = True

        # S[x] = apb_vec[-x]
        S = apb_vec[neg_idx]

        R_size = (~S).sum()
        free_g = (~S[binary_cube_2_idx]).sum()

        processed += 1

        # Store if good enough
        entry = (int(R_size), int(free_g), pi_idx, swap_bits, beta_g_coords.copy())
        if len(top_entries) < N_TOP:
            top_entries.append(entry)
            if len(top_entries) == N_TOP:
                top_entries.sort(key=lambda x: -x[0])
        elif R_size > top_entries[-1][0]:
            top_entries[-1] = entry
            top_entries.sort(key=lambda x: -x[0])

    if (pi_idx + 1) % 72 == 0:
        elapsed = time.time() - t0
        best_R = top_entries[0][0] if top_entries else 0
        print(f"  {processed}/{TOTAL_G} ({100*processed/TOTAL_G:.1f}%) "
              f"elapsed={elapsed:.1f}s best_R={best_R}")

elapsed = time.time() - t0
print(f"STEP 2 done in {elapsed:.1f}s. Top |R_g|: {[e[0] for e in top_entries[:10]]}")
print(f"Top free_g: {[e[1] for e in sorted(top_entries, key=lambda x: -x[1])[:10]]}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3: Exact branch-and-bound max cap in R_g
# ──────────────────────────────────────────────────────────────────────────────

def max_cap_bb(pts_list):
    """Branch-and-bound maximum cap. pts_list: list of 6-tuples."""
    if not pts_list:
        return []
    n = len(pts_list)
    pts_set = set(pts_list)

    best_cap = [[]]
    best_size = [0]

    def bb(idx, chosen, chosen_set):
        remaining = n - idx
        if len(chosen) + remaining <= best_size[0]:
            return
        if idx == n:
            if len(chosen) > best_size[0]:
                best_size[0] = len(chosen)
                best_cap[0] = list(chosen)
            return

        p = pts_list[idx]

        # Check if p can be added
        ok = True
        for q in chosen:
            c = tuple((-p[i] - q[i]) % 3 for i in range(6))
            if c in chosen_set:
                ok = False
                break

        if ok:
            chosen.append(p)
            chosen_set.add(p)
            bb(idx + 1, chosen, chosen_set)
            chosen.pop()
            chosen_set.discard(p)

        bb(idx + 1, chosen, chosen_set)

    bb(0, [], set())
    return best_cap[0]

print("\nSTEP 3: Branch-and-bound max cap on top 50...")

best_total = 0
best_result = None

# Also combine top by free_g
top_by_free = sorted(top_entries, key=lambda x: -x[1])[:10]
combined = list(top_entries)
for e in top_by_free:
    if e not in combined:
        combined.append(e)
# Sort by R_size desc
combined.sort(key=lambda x: -x[0])

for rank, entry in enumerate(combined[:N_TOP]):
    R_size, free_g, pi_idx, swap_bits, beta_g_coords = entry
    residual_vec = ~compute_sumset_vec(alpha_vec, np.zeros(729, dtype=np.bool_))  # placeholder

    # Recompute S for this g
    sums_coords = (alpha_arr_pts[:, None, :] + beta_g_coords[None, :, :]) % 3
    flat_sums = sums_coords.reshape(-1, 6) @ POW3
    apb_vec = np.zeros(729, dtype=np.bool_)
    apb_vec[flat_sums] = True
    S = apb_vec[neg_idx]

    residual_indices = np.where(~S)[0]
    residual_pts = [ALL_POINTS_6[i] for i in residual_indices]

    t1 = time.time()
    gamma = max_cap_bb(residual_pts)
    total = 224 + len(gamma)
    t2 = time.time()

    print(f"  Rank {rank+1}: |R|={R_size}, free={free_g}, |gamma|={len(gamma)}, total={total} ({t2-t1:.2f}s)")

    if total > best_total:
        best_total = total
        beta_g_list = [tuple(int(x) for x in row) for row in beta_g_coords]
        best_result = (beta_g_list, gamma, total)

    if total >= 237:
        beta_g_list = [tuple(int(x) for x in row) for row in beta_g_coords]
        full = ([(0,) + a for a in alpha_set] +
                [(1,) + b for b in beta_g_list] +
                [(2,) + tuple(c) for c in gamma])
        valid, reason = is_capset(full)
        print(f"  >>> VERIFIER: valid={valid}, size={len(full)}, reason={reason}")
        if valid and len(full) > 236:
            print(f"  *** BEATS 236! ***")
            json.dump({"7": [list(p) for p in full]},
                      open("orbit_twisted_result.json", "w"))
            print("  Saved to orbit_twisted_result.json")
            print(f"\nFINAL: valid=True, size={len(full)}, beats_236=True")
            sys.exit(0)

print(f"\nSTEP 3 done. Best total (B&B) = {best_total}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 4: Binary-cube retarget (already computed as free_g in step 2)
# ──────────────────────────────────────────────────────────────────────────────
print(f"\nSTEP 4: free_g values (top 10): {sorted([e[1] for e in top_entries], reverse=True)[:10]}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 5: Residual-grow trade loop
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 5: Trade loop...")

# Target zone Z
def build_target_zone():
    Z_pts = []
    for v in ALL_POINTS_6:
        # binary cube or weight <= 2
        is_binary = all(x in (0, 1) for x in v) and any(x != 0 for x in v)
        w = sum(x != 0 for x in v)
        if is_binary or w <= 2:
            Z_pts.append(v)
    return Z_pts

target_zone_pts = build_target_zone()
target_zone_set = set(target_zone_pts)
print(f"  |Z| = {len(target_zone_pts)}")

def build_mult_table(alpha_pts, beta_pts):
    """Build multiplicity table cnt[(-(a+b))] = # pairs."""
    cnt = {}
    for a in alpha_pts:
        for b in beta_pts:
            x = tuple((-a[i] - b[i]) % 3 for i in range(6))
            cnt[x] = cnt.get(x, 0) + 1
    return cnt

# Pick top 5 candidates (best by R_size and by free_g)
top5_by_R = combined[:5]
top5_by_free = sorted(top_entries, key=lambda x: -x[1])[:5]
all_top5 = []
seen_k = set()
for e in top5_by_R + top5_by_free:
    key = (e[2], e[3])  # (perm_idx, swap_bits)
    if key not in seen_k:
        seen_k.add(key)
        all_top5.append(e)
    if len(all_top5) >= 10:
        break

trade_best_total = best_total
trade_best_full = None

for cand_idx, entry in enumerate(all_top5):
    R_size, free_g, pi_idx, swap_bits, beta_g_coords = entry
    beta_g_list = [tuple(int(x) for x in row) for row in beta_g_coords]
    alpha_list = list(alpha_set)

    print(f"\n  Candidate {cand_idx+1}: |R|={R_size}, free={free_g}")

    # Build multiplicity table
    t1 = time.time()
    cnt = build_mult_table(alpha_list, beta_g_list)
    t2 = time.time()
    print(f"    Mult table built in {t2-t1:.2f}s")

    alpha_cur = list(alpha_list)
    beta_cur = list(beta_g_list)

    def get_residual_Z():
        in_sum = set(x for x, c in cnt.items() if c > 0)
        return [v for v in target_zone_pts if v not in in_sum]

    base_res = get_residual_Z()
    gamma_base = max_cap_bb(base_res)
    curr_total = len(alpha_cur) + len(beta_cur) + len(gamma_base)
    print(f"    Base: |res_Z|={len(base_res)}, |gamma|={len(gamma_base)}, total={curr_total}")

    for k in range(1, 9):
        # Find point p in alpha U beta maximizing newly unlocked Z-points
        best_unlock = 0
        best_p = None
        best_from = None

        for p in alpha_cur:
            u = sum(1 for b in beta_cur
                    if (x := tuple((-p[i]-b[i])%3 for i in range(6))) in target_zone_set
                    and cnt.get(x, 0) == 1)
            if u > best_unlock:
                best_unlock = u; best_p = p; best_from = 'alpha'

        for b in beta_cur:
            u = sum(1 for a in alpha_cur
                    if (x := tuple((-a[i]-b[i])%3 for i in range(6))) in target_zone_set
                    and cnt.get(x, 0) == 1)
            if u > best_unlock:
                best_unlock = u; best_p = b; best_from = 'beta'

        if best_p is None or best_unlock == 0:
            print(f"    k={k}: no unlock possible, stopping")
            break

        # Apply deletion
        if best_from == 'alpha':
            alpha_cur.remove(best_p)
            for b in beta_cur:
                x = tuple((-best_p[i]-b[i])%3 for i in range(6))
                cnt[x] = cnt.get(x, 0) - 1
                if cnt[x] == 0: del cnt[x]
        else:
            beta_cur.remove(best_p)
            for a in alpha_cur:
                x = tuple((-a[i]-best_p[i])%3 for i in range(6))
                cnt[x] = cnt.get(x, 0) - 1
                if cnt[x] == 0: del cnt[x]

        new_res = get_residual_Z()
        gamma_new = max_cap_bb(new_res)
        new_total = len(alpha_cur) + len(beta_cur) + len(gamma_new)
        print(f"    k={k}: unlocked {best_unlock} Z-pts, |gamma|={len(gamma_new)}, total={new_total}")

        if new_total > trade_best_total:
            trade_best_total = new_total
            full = ([(0,)+a for a in alpha_cur] +
                    [(1,)+b for b in beta_cur] +
                    [(2,)+tuple(c) for c in gamma_new])
            trade_best_full = full

        if new_total >= 237:
            full = ([(0,)+a for a in alpha_cur] +
                    [(1,)+b for b in beta_cur] +
                    [(2,)+tuple(c) for c in gamma_new])
            valid, reason = is_capset(full)
            print(f"    VERIFIER: valid={valid}, size={len(full)}")
            if valid and len(full) > 236:
                print(f"    *** BEATS 236! ***")
                json.dump({"7": [list(p) for p in full]},
                          open("orbit_twisted_result.json", "w"))
                print(f"\nFINAL: valid=True, size={len(full)}, beats_236=True")
                sys.exit(0)

print(f"\nSTEP 5 done. Trade best total = {trade_best_total}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 6: 2-swap simulated annealing
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 6: Simulated annealing (2000 iterations)...")

# Start from best base g
best_entry = combined[0]
R_size, free_g, pi_idx, swap_bits, beta_g_coords = best_entry
beta_g_list = [tuple(int(x) for x in row) for row in beta_g_coords]

alpha_sa = list(alpha_set)
beta_sa = list(beta_g_list)
cnt_sa = build_mult_table(alpha_sa, beta_sa)

def get_gamma_sa():
    in_sum = set(x for x, c in cnt_sa.items() if c > 0)
    res = [v for v in target_zone_pts if v not in in_sum]
    return max_cap_bb(res)

gamma_sa = get_gamma_sa()
sa_total = len(alpha_sa) + len(beta_sa) + len(gamma_sa)
sa_best = sa_total
sa_best_state = (list(alpha_sa), list(beta_sa), list(gamma_sa))
deleted_sa = []  # (point, 'alpha'/'beta')

print(f"  SA start: total={sa_total}")

random.seed(42)
for it in range(2000):
    T = 0.5 * (1 - it / 2000)

    # Pick action: re-insert+delete or just delete
    if deleted_sa and random.random() < 0.4:
        # Re-insert one, delete another
        ri = random.randrange(len(deleted_sa))
        p_ins, src_ins = deleted_sa[ri]

        if src_ins == 'alpha' and alpha_sa:
            # Re-insert p_ins to alpha, delete random alpha
            j = random.randrange(len(alpha_sa))
            p_del = alpha_sa[j]

            # Update cnt: remove p_del contribution, add p_ins contribution
            for b in beta_sa:
                x = tuple((-p_del[i]-b[i])%3 for i in range(6))
                cnt_sa[x] = cnt_sa.get(x, 0) - 1
                if cnt_sa[x] == 0: del cnt_sa[x]
                x2 = tuple((-p_ins[i]-b[i])%3 for i in range(6))
                cnt_sa[x2] = cnt_sa.get(x2, 0) + 1

            alpha_sa[j] = p_ins
            deleted_sa[ri] = (p_del, 'alpha')

        elif src_ins == 'beta' and beta_sa:
            j = random.randrange(len(beta_sa))
            p_del = beta_sa[j]

            for a in alpha_sa:
                x = tuple((-a[i]-p_del[i])%3 for i in range(6))
                cnt_sa[x] = cnt_sa.get(x, 0) - 1
                if cnt_sa[x] == 0: del cnt_sa[x]
                x2 = tuple((-a[i]-p_ins[i])%3 for i in range(6))
                cnt_sa[x2] = cnt_sa.get(x2, 0) + 1

            beta_sa[j] = p_ins
            deleted_sa[ri] = (p_del, 'beta')
        else:
            continue
    else:
        # Delete random point
        which = 'alpha' if random.random() < 0.5 else 'beta'
        if which == 'alpha' and alpha_sa:
            j = random.randrange(len(alpha_sa))
            p = alpha_sa.pop(j)
            deleted_sa.append((p, 'alpha'))
            for b in beta_sa:
                x = tuple((-p[i]-b[i])%3 for i in range(6))
                cnt_sa[x] = cnt_sa.get(x, 0) - 1
                if cnt_sa[x] == 0: del cnt_sa[x]
        elif which == 'beta' and beta_sa:
            j = random.randrange(len(beta_sa))
            p = beta_sa.pop(j)
            deleted_sa.append((p, 'beta'))
            for a in alpha_sa:
                x = tuple((-a[i]-p[i])%3 for i in range(6))
                cnt_sa[x] = cnt_sa.get(x, 0) - 1
                if cnt_sa[x] == 0: del cnt_sa[x]
        else:
            continue

    g_sa = get_gamma_sa()
    new_total = len(alpha_sa) + len(beta_sa) + len(g_sa)
    dE = new_total - sa_total

    if dE > 0 or (T > 0 and random.random() < math.exp(dE / T)):
        sa_total = new_total
        if new_total > sa_best:
            sa_best = new_total
            sa_best_state = (list(alpha_sa), list(beta_sa), list(g_sa))
            print(f"  SA iter {it}: new best={sa_best}")

            if sa_best >= 237:
                a_b, b_b, g_b = sa_best_state
                full = [(0,)+a for a in a_b] + [(1,)+b for b in b_b] + [(2,)+tuple(c) for c in g_b]
                valid, reason = is_capset(full)
                print(f"  VERIFIER: valid={valid}, size={len(full)}")
                if valid and len(full) > 236:
                    print(f"  *** BEATS 236! ***")
                    json.dump({"7": [list(p) for p in full]},
                              open("orbit_twisted_result.json", "w"))
                    print(f"\nFINAL: valid=True, size={len(full)}, beats_236=True")
                    sys.exit(0)

print(f"\nSTEP 6 done. SA best = {sa_best}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 7: Final verdict
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 7: HONEST NEGATIVE REPORT")
overall_best = max(best_total, trade_best_total, sa_best)
print(f"Best total achieved: {overall_best}")
print(f"  B&B best: {best_total}")
print(f"  Trade loop best: {trade_best_total}")
print(f"  SA best: {sa_best}")
print(f"Did NOT beat 236. certified_size=0 (no valid cap >236 found).")
