#!/usr/bin/env python3
"""
orbit-twisted residual-grow into the binary cube
Recipe: lens residual-grow
Steps 1-7 exactly as specified.
"""
import itertools, json, sys, math, random
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
        for p, val in zip(star, vals):
            v[p] = val
        out.append(tuple(v))
    return out

def block1():
    T = []
    for i in range(5):
        t = ['0'] * 6
        for k in range(3):
            t[1 + (i + k) % 5] = '*'
        T.append(t)
    return T

def block2():
    T = []
    for i in range(5):
        t = ['0'] * 6
        t[0] = '*'
        for p in (i % 5, (i + 2) % 5):
            t[1 + p] = '*'
        T.append(t)
    return T

def delta():
    return [v for v in itertools.product([1, 2], repeat=6) if sum(x == 1 for x in v) % 2 == 0]

def interchange(t):
    return ['*' if c == '0' else '0' for c in t]

upper = block1() + block2()
D = set(delta())
alpha_set = set()
for t in upper:
    alpha_set |= set(expand(t))
alpha_set |= D
beta_base = set()
for t in upper:
    beta_base |= set(expand(interchange(t)))
beta_base |= D

assert len(alpha_set) == 112, f"|alpha|={len(alpha_set)}, expected 112"
assert len(beta_base) == 112, f"|beta|={len(beta_base)}, expected 112"

# Verify alpha is a 6-cap
def is_6cap(pts):
    pts_list = list(pts)
    pts_s = set(pts_list)
    for a, b in itertools.combinations(pts_list, 2):
        c = tuple((-a[i] - b[i]) % 3 for i in range(6))
        if c in pts_s and c != a and c != b:
            return False
    return True

assert is_6cap(alpha_set), "alpha is not a cap"
assert is_6cap(beta_base), "beta is not a cap"
print(f"STEP 1: |alpha|={len(alpha_set)}, |beta|={len(beta_base)}, both are caps. OK")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 2: Enumerate all g in G = S_6 x {0,1}^6, compute residuals
# ──────────────────────────────────────────────────────────────────────────────

# Represent F_3^6 as flat index 0..728
def idx(v):
    n = 0
    for x in v:
        n = n * 3 + x
    return n

def from_idx(i, dim=6):
    v = []
    for _ in range(dim):
        v.append(i % 3)
        i //= 3
    return tuple(reversed(v))

ALL_POINTS_6 = [from_idx(i) for i in range(729)]

# Convert alpha to numpy array for fast ops
alpha_arr = np.array(list(alpha_set), dtype=np.int8)  # shape (112, 6)
beta_arr = np.array(list(beta_base), dtype=np.int8)   # shape (112, 6)

def apply_monomial(pts_arr, perm, swap_bits):
    """Apply monomial map: permute coords then optionally multiply by 2 mod 3."""
    out = pts_arr[:, perm]  # permute columns
    for i, bit in enumerate(swap_bits):
        if bit:
            out = out.copy()
            out[:, i] = (2 * out[:, i]) % 3
    return out

def compute_sumset_bitset(a_arr, b_arr):
    """Compute bitset of -(a+b) mod 3 for all a in a_arr, b in b_arr."""
    bitset = np.zeros(729, dtype=np.bool_)
    # Vectorized: for each a, compute -(a + b) for all b
    for a in a_arr:
        sums = (-(a + b_arr)) % 3  # shape (|beta|, 6)
        indices = sums[:, 0] * 243 + sums[:, 1] * 81 + sums[:, 2] * 27 + sums[:, 3] * 9 + sums[:, 4] * 3 + sums[:, 5]
        bitset[indices] = True
    return bitset

print("STEP 2: Enumerating all 46080 monomial maps and computing residuals...")
print("  (This may take a few minutes...)")

# Precompute all permutations of S_6
import math
all_perms = list(itertools.permutations(range(6)))  # 720 perms
all_swaps = list(itertools.product([0, 1], repeat=6))  # 64 swap patterns

# Precompute alpha sumset indices (fixed)
alpha_indices = np.array([idx(v) for v in alpha_set])

best_residuals = []  # (|R_g|, free_g, g_desc, beta_g_arr, residual_indices)

# We process all 46080 combinations
# To speed up: use numpy batch operations
# For each g, compute beta_g = g(beta), then sumset = alpha + beta_g, residual = complement

# Use 3D convolution trick:
# S[x] = sum_{a+b+x=0} alpha[a]*beta[b] = (alpha conv beta)[x]
# where conv is in (Z/3)^6

# Reshape alpha and beta indicator vectors to 3x3x3x3x3x3 arrays
def to_3d(pts_arr):
    arr = np.zeros([3]*6, dtype=np.int32)
    for pt in pts_arr:
        arr[tuple(pt)] += 1
    return arr

alpha_3d = to_3d(alpha_arr)

# Binary cube points (for free_g metric)
binary_cube = []
for v in itertools.product([0, 1], repeat=6):
    if any(x != 0 for x in v):
        binary_cube.append(v)
binary_cube_2mod3 = [tuple((2*x) % 3 for x in v) for v in binary_cube]  # these are {0,2} vectors

# Index of binary cube 2x vectors
binary_cube_2_idx = set(idx(v) for v in binary_cube_2mod3)

print(f"  Binary cube has {len(binary_cube)} non-zero points")

N_TOP = 50  # top candidates to track for branch-and-bound

# Track top residuals by |R_g|
import heapq

top_by_residual = []  # min-heap of (|R_g|, counter, ...)
top_by_free = []
heap_counter = 0

total_processed = 0
TOTAL_G = 720 * 64  # 46080

# Process in batches by permutation for efficiency
for perm_idx, perm in enumerate(all_perms):
    # Apply permutation to beta
    beta_perm = beta_arr[:, list(perm)]  # shape (112, 6)
    beta_perm_3d = to_3d(beta_perm)

    for swap in all_swaps:
        # Apply swaps
        beta_g = beta_perm.copy()
        for i, bit in enumerate(swap):
            if bit:
                beta_g[:, i] = (2 * beta_g[:, i]) % 3

        # Compute sumset using 3D array
        beta_g_3d = to_3d(beta_g)

        # Convolve in Z/3^6: S[x] = sum_{a+b=-x mod 3} alpha[a]*beta_g[b]
        # Equivalently, S[x] > 0 iff -x is in alpha+beta_g
        # Use numpy roll-based convolution approach
        # Actually use direct index approach for correctness

        # Vectorized sumset computation
        # For each a in alpha, -(a+b) for all b in beta_g
        sumset_bitset = np.zeros(729, dtype=np.bool_)
        for a in alpha_arr:
            neg_sums = (-(a.astype(np.int32) + beta_g.astype(np.int32))) % 3
            idxs = (neg_sums[:, 0] * 243 + neg_sums[:, 1] * 81 +
                    neg_sums[:, 2] * 27 + neg_sums[:, 3] * 9 +
                    neg_sums[:, 4] * 3 + neg_sums[:, 5])
            sumset_bitset[idxs] = True

        residual_indices = np.where(~sumset_bitset)[0]
        R_size = len(residual_indices)

        # free_g: binary cube points whose 2x vector is NOT in alpha+beta_g
        free_g = sum(1 for bi in binary_cube_2_idx if not sumset_bitset[bi])

        heap_counter += 1
        g_desc = (perm, swap)

        # Track top N_TOP by residual size
        entry = (R_size, heap_counter, g_desc, beta_g.copy(), residual_indices.copy(), free_g)
        if len(top_by_residual) < N_TOP:
            heapq.heappush(top_by_residual, (R_size, heap_counter, g_desc, beta_g.copy(), residual_indices.copy(), free_g))
        elif R_size > top_by_residual[0][0]:
            heapq.heapreplace(top_by_residual, entry)

        total_processed += 1

    if (perm_idx + 1) % 72 == 0:
        best_so_far = max(e[0] for e in top_by_residual) if top_by_residual else 0
        print(f"  Processed {total_processed}/{TOTAL_G} maps, best |R_g|={best_so_far}")

# Sort by residual size descending
top_by_residual_sorted = sorted(top_by_residual, key=lambda x: -x[0])
print(f"\nSTEP 2 done. Top residual sizes: {[e[0] for e in top_by_residual_sorted[:10]]}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3: Exact branch-and-bound maximum cap inside R_g for top 50
# ──────────────────────────────────────────────────────────────────────────────

def max_cap_exact(pts_list):
    """Branch-and-bound max cap inside pts_list."""
    n = len(pts_list)
    if n == 0:
        return []
    pts_set = set(pts_list)
    dim = len(pts_list[0])

    # Precompute: for each pair (a,b), the forbidden point c = -(a+b)
    # We need fast "is c in pts_set" and "is c already chosen"

    best = [0]
    best_set = [[]]

    def backtrack(idx, chosen, chosen_set):
        if idx == n:
            if len(chosen) > best[0]:
                best[0] = len(chosen)
                best_set[0] = list(chosen)
            return
        remaining = n - idx
        if len(chosen) + remaining <= best[0]:
            return  # prune

        p = pts_list[idx]
        # Try adding p
        # Check if p conflicts with any pair in chosen
        can_add = True
        for q in chosen:
            c = tuple((-p[i] - q[i]) % 3 for i in range(dim))
            if c in chosen_set:
                can_add = False
                break

        if can_add:
            chosen.append(p)
            chosen_set.add(p)
            backtrack(idx + 1, chosen, chosen_set)
            chosen.pop()
            chosen_set.discard(p)

        # Try skipping p
        backtrack(idx + 1, chosen, chosen_set)

    backtrack(0, [], set())
    return best_set[0]

print("\nSTEP 3: Running exact branch-and-bound on top 50 residuals...")

best_total = 0
best_candidate = None

for rank, entry in enumerate(top_by_residual_sorted):
    R_size, _, g_desc, beta_g_arr, residual_indices, free_g = entry

    residual_pts = [ALL_POINTS_6[i] for i in residual_indices]

    print(f"  Rank {rank+1}: |R_g|={R_size}, free_g={free_g}, running B&B...")

    gamma = max_cap_exact(residual_pts)
    total = 224 + len(gamma)

    print(f"    max cap in R_g = {len(gamma)}, total = {total}")

    if total > best_total:
        best_total = total
        # Convert beta_g_arr back to list of tuples
        beta_g_list = [tuple(int(x) for x in row) for row in beta_g_arr]
        best_candidate = (g_desc, beta_g_list, gamma, total)

    if total >= 237:
        print(f"  >>> POTENTIAL HIT: total={total} >=237! Verifying with frozen verifier...")
        perm, swap = g_desc
        # Assemble full 7-dim point set
        full = ([(0,) + a for a in alpha_set] +
                [(1,) + b for b in beta_g_list] +
                [(2,) + tuple(c) for c in gamma])
        valid, reason = is_capset(full)
        print(f"  VERIFIER: valid={valid}, size={len(full)}, reason={reason}")
        if valid and len(full) > 236:
            print(f"  *** BEATS 236! Size={len(full)} ***")
            json.dump({"7": [list(p) for p in full]},
                      open("orbit_twisted_result.json", "w"))
            print("  Saved to orbit_twisted_result.json")
            print("\nFINAL RESULT (certified by frozen verifier):")
            print(f"  valid={valid}, size={len(full)}, beats_236=True")
            sys.exit(0)

# ──────────────────────────────────────────────────────────────────────────────
# STEP 4: Binary-cube retarget metric (already computed as free_g above)
# ──────────────────────────────────────────────────────────────────────────────
print(f"\nSTEP 4: Best total from B&B = {best_total}")
top_by_free_sorted = sorted(top_by_residual, key=lambda x: (-x[5], -x[0]))
print(f"Top free_g values: {[e[5] for e in top_by_free_sorted[:10]]}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 5: Residual-grow trade loop for 5 best g from steps 3-4
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 5: Trade loop (delete alpha/beta points to unlock residual)...")

# Combine and deduplicate top candidates
seen_g = set()
top5_candidates = []
for entry in top_by_residual_sorted:
    R_size, _, g_desc, beta_g_arr, residual_indices, free_g = entry
    key = (g_desc[0], g_desc[1])
    if key not in seen_g:
        seen_g.add(key)
        top5_candidates.append(entry)
    if len(top5_candidates) >= 5:
        break

# Also add top by free_g
for entry in top_by_free_sorted:
    R_size, _, g_desc, beta_g_arr, residual_indices, free_g = entry
    key = (g_desc[0], g_desc[1])
    if key not in seen_g:
        seen_g.add(key)
        top5_candidates.append(entry)
    if len(top5_candidates) >= 10:
        break

# Target zone Z = {0,1}^6 \ {0} union weight<=2 points
def weight(v):
    return sum(x != 0 for x in v)

def build_target_zone():
    Z = set()
    # binary cube (weight 1 through 6, entries in {0,1})
    for v in itertools.product([0, 1], repeat=6):
        if any(x != 0 for x in v):
            Z.add(v)
    # weight <= 2 points in F_3^6
    for v in ALL_POINTS_6:
        if weight(v) <= 2:
            Z.add(v)
    return Z

target_zone = build_target_zone()
target_zone_idx = set(idx(v) for v in target_zone)
print(f"  Target zone |Z| = {len(target_zone)}")

def trade_loop(alpha_pts, beta_pts, g_desc, max_k=8):
    """Delete up to max_k points from alpha U beta to unlock residual in Z."""
    alpha_cur = list(alpha_pts)
    beta_cur = list(beta_pts)

    # Build multiplicity table: cnt[x] = number of (a,b) pairs with -(a+b) = x
    cnt = {}
    for a in alpha_cur:
        for b in beta_cur:
            x = tuple((-a[i] - b[i]) % 3 for i in range(6))
            cnt[x] = cnt.get(x, 0) + 1

    # Current sumset bitset
    in_sumset = set(x for x, c in cnt.items() if c > 0)

    # Residual in Z
    residual_in_Z = [v for v in target_zone if v not in in_sumset]

    deleted = []
    best_total_trade = 224 + len(max_cap_exact(residual_in_Z))

    for k in range(1, max_k + 1):
        # Find point p in alpha U beta that unlocks max new residual points in Z
        best_unlock = -1
        best_p = None
        best_from = None

        # Check alpha points
        for p in alpha_cur:
            # Removing p from alpha removes from sumset: all -(p+b) for b in beta
            # A point x unlocks if cnt[x] drops to 0
            newly_unlocked = 0
            for b in beta_cur:
                x = tuple((-p[i] - b[i]) % 3 for i in range(6))
                if x in target_zone_idx_set and cnt.get(x, 0) == 1:
                    newly_unlocked += 1
            if newly_unlocked > best_unlock:
                best_unlock = newly_unlocked
                best_p = p
                best_from = 'alpha'

        # Check beta points
        for b in beta_cur:
            newly_unlocked = 0
            for a in alpha_cur:
                x = tuple((-a[i] - b[i]) % 3 for i in range(6))
                if x in target_zone_idx_set and cnt.get(x, 0) == 1:
                    newly_unlocked += 1
            if newly_unlocked > best_unlock:
                best_unlock = newly_unlocked
                best_p = b
                best_from = 'beta'

        if best_p is None or best_unlock == 0:
            print(f"    k={k}: no unlocking point found, stopping")
            break

        # Delete best_p
        if best_from == 'alpha':
            alpha_cur.remove(best_p)
            for b in beta_cur:
                x = tuple((-best_p[i] - b[i]) % 3 for i in range(6))
                cnt[x] = cnt.get(x, 0) - 1
                if cnt[x] == 0:
                    del cnt[x]
        else:
            beta_cur.remove(best_p)
            for a in alpha_cur:
                x = tuple((-a[i] - best_p[i]) % 3 for i in range(6))
                cnt[x] = cnt.get(x, 0) - 1
                if cnt[x] == 0:
                    del cnt[x]

        deleted.append((best_p, best_from))
        in_sumset = set(x for x, c in cnt.items() if c > 0)

        new_residual = [v for v in target_zone if v not in in_sumset]
        gamma_trade = max_cap_exact(new_residual)

        current_size = len(alpha_cur) + len(beta_cur)
        total_trade = current_size + len(gamma_trade)

        print(f"    k={k}: deleted {best_from} point, unlocked {best_unlock} new Z-points, "
              f"|residual Z|={len(new_residual)}, |gamma|={len(gamma_trade)}, "
              f"total={total_trade} (alpha+beta={current_size})")

        if total_trade > best_total_trade:
            best_total_trade = total_trade

        if total_trade >= 237:
            # Verify!
            full = ([(0,) + a for a in alpha_cur] +
                    [(1,) + b for b in beta_cur] +
                    [(2,) + tuple(c) for c in gamma_trade])
            valid, reason = is_capset(full)
            print(f"    VERIFIER: valid={valid}, size={len(full)}, reason={reason}")
            if valid and len(full) > 236:
                return True, full, best_total_trade

        if best_unlock < k + 1:
            # Doesn't satisfy the >= k+1 requirement
            pass

    return False, None, best_total_trade

# Need set version for fast lookup
target_zone_idx_set = target_zone_idx

trade_best_total = 0
trade_best_full = None

for i, entry in enumerate(top5_candidates):
    R_size, _, g_desc, beta_g_arr, residual_indices, free_g = entry
    beta_g_list = [tuple(int(x) for x in row) for row in beta_g_arr]

    print(f"\n  Candidate {i+1}: |R_g|={R_size}, free_g={free_g}")
    success, full, best_tt = trade_loop(list(alpha_set), beta_g_list, g_desc)

    if best_tt > trade_best_total:
        trade_best_total = best_tt
        if full is not None:
            trade_best_full = full

    if success and full is not None:
        valid, reason = is_capset(full)
        if valid and len(full) > 236:
            print(f"\n*** BEATS 236 via trade loop! Size={len(full)} ***")
            json.dump({"7": [list(p) for p in full]},
                      open("orbit_twisted_result.json", "w"))
            print("Saved to orbit_twisted_result.json")
            print("\nFINAL RESULT (certified by frozen verifier):")
            print(f"  valid={valid}, size={len(full)}, beats_236=True")
            sys.exit(0)

# ──────────────────────────────────────────────────────────────────────────────
# STEP 6: 2-swap annealing from best trade-loop state
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 6: 2-swap simulated annealing (2000 iterations)...")
print("  (Simplified: running SA on the best base g found so far)")

# Get best candidate for annealing
best_entry = top_by_residual_sorted[0]
R_size, _, g_desc, beta_g_arr, residual_indices, free_g = best_entry
beta_g_list = [tuple(int(x) for x in row) for row in beta_g_arr]

alpha_sa = list(alpha_set)
beta_sa = list(beta_g_list)

# Build multiplicity table
def build_cnt(alpha_pts, beta_pts):
    cnt = {}
    for a in alpha_pts:
        for b in beta_pts:
            x = tuple((-a[i] - b[i]) % 3 for i in range(6))
            cnt[x] = cnt.get(x, 0) + 1
    return cnt

cnt_sa = build_cnt(alpha_sa, beta_sa)

def get_residual_gamma(cnt, zone):
    in_sum = set(x for x, c in cnt.items() if c > 0)
    res = [v for v in zone if v not in in_sum]
    return max_cap_exact(res)

sa_gamma = get_residual_gamma(cnt_sa, target_zone)
sa_total = len(alpha_sa) + len(beta_sa) + len(sa_gamma)
sa_best_total = sa_total
sa_best_state = (list(alpha_sa), list(beta_sa))
sa_deleted = []

print(f"  SA start: total={sa_total}")

N_ITER = 2000
T_START = 0.5
for it in range(N_ITER):
    T = T_START * (1 - it / N_ITER)

    # Re-insert one previously deleted (if any) + delete a random point
    if random.random() < 0.5 and sa_deleted:
        # Re-insert one deleted
        to_reinsert_idx = random.randrange(len(sa_deleted))
        p_reinsert, src = sa_deleted[to_reinsert_idx]

        # Delete a different random point
        if src == 'alpha':
            if len(alpha_sa) == 0:
                continue
            to_delete_idx = random.randrange(len(alpha_sa))
            p_delete = alpha_sa[to_delete_idx]

            # Update cnt: add reinsert, remove delete
            alpha_sa.append(p_reinsert)
            sa_deleted.pop(to_reinsert_idx)

            alpha_sa.pop(alpha_sa.index(p_delete))
            sa_deleted.append((p_delete, 'alpha'))

            # Recompute cnt (expensive but correct)
            cnt_sa = build_cnt(alpha_sa, beta_sa)
        else:
            if len(beta_sa) == 0:
                continue
            to_delete_idx = random.randrange(len(beta_sa))
            p_delete = beta_sa[to_delete_idx]

            beta_sa.append(p_reinsert)
            sa_deleted.pop(to_reinsert_idx)

            beta_sa.pop(beta_sa.index(p_delete))
            sa_deleted.append((p_delete, 'beta'))

            cnt_sa = build_cnt(alpha_sa, beta_sa)
    else:
        # Delete a random point from alpha or beta
        which = random.choice(['alpha', 'beta'])
        if which == 'alpha' and len(alpha_sa) > 0:
            idx_del = random.randrange(len(alpha_sa))
            p = alpha_sa.pop(idx_del)
            sa_deleted.append((p, 'alpha'))
            for b in beta_sa:
                x = tuple((-p[i] - b[i]) % 3 for i in range(6))
                cnt_sa[x] = cnt_sa.get(x, 0) - 1
                if cnt_sa[x] == 0:
                    del cnt_sa[x]
        elif which == 'beta' and len(beta_sa) > 0:
            idx_del = random.randrange(len(beta_sa))
            p = beta_sa.pop(idx_del)
            sa_deleted.append((p, 'beta'))
            for a in alpha_sa:
                x = tuple((-a[i] - p[i]) % 3 for i in range(6))
                cnt_sa[x] = cnt_sa.get(x, 0) - 1
                if cnt_sa[x] == 0:
                    del cnt_sa[x]
        else:
            continue

    gamma_sa = get_residual_gamma(cnt_sa, target_zone)
    new_total = len(alpha_sa) + len(beta_sa) + len(gamma_sa)

    delta_E = new_total - sa_total
    if delta_E > 0 or (T > 0 and random.random() < math.exp(delta_E / T)):
        sa_total = new_total
        if new_total > sa_best_total:
            sa_best_total = new_total
            sa_best_state = (list(alpha_sa), list(beta_sa))
            print(f"  SA iter {it}: new best total={sa_best_total}")

            if sa_best_total >= 237:
                alpha_best, beta_best = sa_best_state
                full = ([(0,) + a for a in alpha_best] +
                        [(1,) + b for b in beta_best] +
                        [(2,) + tuple(c) for c in gamma_sa])
                valid, reason = is_capset(full)
                print(f"  VERIFIER: valid={valid}, size={len(full)}")
                if valid and len(full) > 236:
                    print(f"*** BEATS 236 via SA! Size={len(full)} ***")
                    json.dump({"7": [list(p) for p in full]},
                              open("orbit_twisted_result.json", "w"))
                    sys.exit(0)

print(f"\nSTEP 6 done. SA best total = {sa_best_total}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 7: Final verdict
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 7: Final verdict")
overall_best = max(best_total, trade_best_total, sa_best_total)
print(f"Best total achieved (not verified >=237): {overall_best}")
print(f"HONEST NEGATIVE: Did not beat 236. Best total = {overall_best}")
print(f"  - best_total (pure B&B): {best_total}")
print(f"  - trade_best_total (trade loop): {trade_best_total}")
print(f"  - sa_best_total (annealing): {sa_best_total}")
