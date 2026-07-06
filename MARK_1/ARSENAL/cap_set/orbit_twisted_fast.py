#!/usr/bin/env python3
"""
orbit-twisted residual-grow — fully vectorized fast version.
All steps 1-7 of the recipe.
"""
import itertools, json, sys, math, random, time
import numpy as np

# Flush stdout immediately
import functools
print = functools.partial(print, flush=True)

sys.path.insert(0, '/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set')
from capset_verify import is_capset

# ──────────────────────────────────────────────────────────────────────────────
# STEP 1: Build alpha and beta
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
beta_base_set = set()
for t in upper: beta_base_set |= set(expand(interchange(t)))
beta_base_set |= D

assert len(alpha_set) == 112
assert len(beta_base_set) == 112

# Verify as caps
def is_6cap(pts):
    pts_s = set(pts)
    for a, b in itertools.combinations(pts, 2):
        c = tuple((-a[i]-b[i])%3 for i in range(6))
        if c in pts_s and c != a and c != b:
            return False
    return True

assert is_6cap(list(alpha_set))
assert is_6cap(list(beta_base_set))
print(f"STEP 1 OK: |alpha|=|beta|=112, both caps")

# ──────────────────────────────────────────────────────────────────────────────
# Infrastructure
# ──────────────────────────────────────────────────────────────────────────────
ALL_POINTS_6 = list(itertools.product(range(3), repeat=6))
POW3 = np.array([243, 81, 27, 9, 3, 1], dtype=np.int32)

def pts_to_idx(pts_arr):
    return (pts_arr * POW3).sum(axis=1)

def idx_to_coords(i):
    return np.array([(i//p)%3 for p in [243,81,27,9,3,1]], dtype=np.int32)

all_coords = np.array(ALL_POINTS_6, dtype=np.int32)  # (729, 6)
pt_to_idx_map = {p: i for i, p in enumerate(ALL_POINTS_6)}

# Negation map: neg_map[i] = index of -ALL_POINTS_6[i] mod 3
neg_map = np.array([pt_to_idx_map[tuple((-all_coords[i])%3)] for i in range(729)], dtype=np.int32)

alpha_np = np.array(sorted(alpha_set), dtype=np.int32)  # (112, 6)
beta_np = np.array(sorted(beta_base_set), dtype=np.int32)  # (112, 6)

# Compute sumset as indicator vector (very fast with broadcasting)
def compute_sumset(a_np, b_np):
    """a_np: (Na, 6), b_np: (Nb, 6) -> (729,) bool indicator of {-(a+b) mod 3}"""
    # (Na, Nb, 6) sums
    sums = (a_np[:, None, :] + b_np[None, :, :]) % 3  # (Na, Nb, 6)
    flat = (sums.reshape(-1, 6) * POW3).sum(axis=1)    # (Na*Nb,)
    # -(a+b): apply neg_map
    neg_flat = neg_map[flat]
    result = np.zeros(729, dtype=np.bool_)
    result[neg_flat] = True
    return result

# Test
print("Computing base sumset...")
t0 = time.time()
S_base = compute_sumset(alpha_np, beta_np)
print(f"  Done in {time.time()-t0:.3f}s, |S|={S_base.sum()}, |R|={(~S_base).sum()}")

# Binary cube non-zero -> 2x mod 3 indices
binary_cube_2_indices = []
for v in ALL_POINTS_6:
    if all(x in (0,1) for x in v) and any(x!=0 for x in v):
        v2 = tuple((2*x)%3 for x in v)
        binary_cube_2_indices.append(pt_to_idx_map[v2])
binary_cube_2_indices = np.array(binary_cube_2_indices, dtype=np.int32)
print(f"  Binary cube (non-zero): {len(binary_cube_2_indices)} points")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 2: Enumerate all 46080 monomial maps
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 2: Enumerating 46080 monomial maps (S_6 x {0,1}^6)...")
t0 = time.time()

all_perms = list(itertools.permutations(range(6)))  # 720
all_swaps = list(itertools.product([0,1], repeat=6))  # 64

N_TOP = 50
top_entries = []  # list of (R_size, free_g, perm_idx, swap_tuple, beta_g_np)

processed = 0
TOTAL = 720 * 64

for pi_i, perm in enumerate(all_perms):
    perm_list = list(perm)
    # Permute beta
    beta_perm = beta_np[:, perm_list]  # (112, 6)

    for swap in all_swaps:
        # Apply coordinate scaling (2x mod 3 where bit=1)
        beta_g = beta_perm.copy()
        for i, bit in enumerate(swap):
            if bit:
                beta_g[:, i] = (2 * beta_g[:, i]) % 3

        # Sumset
        S = compute_sumset(alpha_np, beta_g)
        R_size = int((~S).sum())
        free_g = int((~S[binary_cube_2_indices]).sum())

        processed += 1

        entry = (R_size, free_g, pi_i, swap, beta_g)
        if len(top_entries) < N_TOP:
            top_entries.append(entry)
            if len(top_entries) == N_TOP:
                top_entries.sort(key=lambda x: -x[0])
        elif R_size > top_entries[-1][0]:
            top_entries[-1] = entry
            top_entries.sort(key=lambda x: -x[0])

    if (pi_i + 1) % 144 == 0:
        e = time.time() - t0
        pct = 100 * processed / TOTAL
        best_R = top_entries[0][0] if top_entries else 0
        print(f"  {processed}/{TOTAL} ({pct:.1f}%) t={e:.1f}s best_R={best_R}")

elapsed = time.time() - t0
print(f"STEP 2 done in {elapsed:.1f}s")
print(f"  Top |R_g|: {[e[0] for e in top_entries[:10]]}")
print(f"  Top free_g: {sorted([e[1] for e in top_entries], reverse=True)[:10]}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3: Exact B&B max cap in R_g for top 50
# ──────────────────────────────────────────────────────────────────────────────
def max_cap_bb(pts):
    """Branch-and-bound maximum cap in F_3^6."""
    if not pts:
        return []
    n = len(pts)
    best = [0]
    best_set = [[]]

    def bb(idx, chosen, cset):
        if len(chosen) + (n - idx) <= best[0]:
            return
        if idx == n:
            if len(chosen) > best[0]:
                best[0] = len(chosen)
                best_set[0] = list(chosen)
            return
        p = pts[idx]
        ok = True
        for q in chosen:
            c = tuple((-p[i]-q[i])%3 for i in range(6))
            if c in cset:
                ok = False; break
        if ok:
            chosen.append(p); cset.add(p)
            bb(idx+1, chosen, cset)
            chosen.pop(); cset.discard(p)
        bb(idx+1, chosen, cset)

    bb(0, [], set())
    return best_set[0]

print("\nSTEP 3: B&B max cap on top 50 residuals...")
best_total = 0
best_full = None

# Compute residuals on-the-fly
for rank, entry in enumerate(top_entries):
    R_size, free_g, pi_i, swap, beta_g = entry

    # Recompute S
    S = compute_sumset(alpha_np, beta_g)
    residual_idx = np.where(~S)[0]
    residual_pts = [ALL_POINTS_6[i] for i in residual_idx]

    t1 = time.time()
    gamma = max_cap_bb(residual_pts)
    t2 = time.time()
    total = 224 + len(gamma)

    print(f"  Rank {rank+1}: |R|={R_size}, free={free_g}, |gamma|={len(gamma)}, "
          f"total={total} ({t2-t1:.2f}s)")

    if total > best_total:
        best_total = total
        beta_g_list = [tuple(int(x) for x in row) for row in beta_g]
        best_full = (beta_g_list, gamma)

    if total >= 237:
        beta_g_list = [tuple(int(x) for x in row) for row in beta_g]
        full = ([(0,)+a for a in alpha_set] +
                [(1,)+b for b in beta_g_list] +
                [(2,)+tuple(c) for c in gamma])
        valid, reason = is_capset(full)
        print(f"  VERIFIER: valid={valid}, size={len(full)}, reason={reason}")
        if valid and len(full) > 236:
            print(f"*** BEATS 236! size={len(full)} ***")
            json.dump({"7": [list(p) for p in full]},
                      open("/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/orbit_twisted_result.json", "w"))
            print("Saved to orbit_twisted_result.json")
            sys.exit(0)

print(f"\nB&B best total = {best_total}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 4: free_g retarget summary
# ──────────────────────────────────────────────────────────────────────────────
print(f"\nSTEP 4: Binary-cube free_g metric (top values): "
      f"{sorted([e[1] for e in top_entries], reverse=True)[:10]}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 5: Trade loop
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 5: Trade loop (delete to unlock residual Z-points)...")

# Target zone Z
target_zone_pts = []
for v in ALL_POINTS_6:
    is_bin = all(x in (0,1) for x in v) and any(x!=0 for x in v)
    w = sum(x!=0 for x in v)
    if is_bin or w <= 2:
        target_zone_pts.append(v)
target_zone_set = set(target_zone_pts)
print(f"  |Z| = {len(target_zone_pts)}")

def build_cnt(alpha_pts, beta_pts):
    cnt = {}
    for a in alpha_pts:
        for b in beta_pts:
            x = tuple((-a[i]-b[i])%3 for i in range(6))
            cnt[x] = cnt.get(x, 0) + 1
    return cnt

# Get top 10 candidates (combining best by R and free)
all_top_combined = list(top_entries)
for e in sorted(top_entries, key=lambda x: -x[1]):
    if e not in all_top_combined:
        all_top_combined.append(e)
all_top_combined = all_top_combined[:10]

trade_best = best_total

for ci, entry in enumerate(all_top_combined):
    R_size, free_g, pi_i, swap, beta_g = entry
    beta_g_list = [tuple(int(x) for x in row) for row in beta_g]

    print(f"\n  Candidate {ci+1}: |R|={R_size}, free={free_g}")

    alpha_cur = list(alpha_set)
    beta_cur = list(beta_g_list)

    t1 = time.time()
    cnt = build_cnt(alpha_cur, beta_cur)
    t2 = time.time()
    print(f"    Mult table: {t2-t1:.2f}s")

    def get_res_Z():
        in_s = set(x for x, c in cnt.items() if c > 0)
        return [v for v in target_zone_pts if v not in in_s]

    base_res = get_res_Z()
    g0 = max_cap_bb(base_res)
    base_total = len(alpha_cur) + len(beta_cur) + len(g0)
    print(f"    Base: |res_Z|={len(base_res)}, |gamma|={len(g0)}, total={base_total}")

    if base_total > trade_best:
        trade_best = base_total

    for k in range(1, 9):
        # Find best deletion
        best_u = 0; best_p = None; best_from = None

        for p in alpha_cur:
            u = sum(1 for b in beta_cur
                    if (x := tuple((-p[i]-b[i])%3 for i in range(6))) in target_zone_set
                    and cnt.get(x, 0) == 1)
            if u > best_u:
                best_u = u; best_p = p; best_from = 'alpha'

        for b in beta_cur:
            u = sum(1 for a in alpha_cur
                    if (x := tuple((-a[i]-b[i])%3 for i in range(6))) in target_zone_set
                    and cnt.get(x, 0) == 1)
            if u > best_u:
                best_u = u; best_p = b; best_from = 'beta'

        if best_u == 0 or best_p is None:
            print(f"    k={k}: no unlock, stopping")
            break

        if best_from == 'alpha':
            alpha_cur.remove(best_p)
            for b in beta_cur:
                x = tuple((-best_p[i]-b[i])%3 for i in range(6))
                cnt[x] = cnt.get(x,0) - 1
                if cnt[x] == 0: del cnt[x]
        else:
            beta_cur.remove(best_p)
            for a in alpha_cur:
                x = tuple((-a[i]-best_p[i])%3 for i in range(6))
                cnt[x] = cnt.get(x,0) - 1
                if cnt[x] == 0: del cnt[x]

        new_res = get_res_Z()
        gk = max_cap_bb(new_res)
        new_total = len(alpha_cur) + len(beta_cur) + len(gk)
        print(f"    k={k}: unlock={best_u}, from={best_from}, |gamma|={len(gk)}, total={new_total}")

        if new_total > trade_best:
            trade_best = new_total

        if new_total >= 237:
            full = [(0,)+a for a in alpha_cur] + [(1,)+b for b in beta_cur] + [(2,)+tuple(c) for c in gk]
            valid, reason = is_capset(full)
            print(f"    VERIFIER: valid={valid}, size={len(full)}")
            if valid and len(full) > 236:
                print("*** BEATS 236 (trade loop)! ***")
                json.dump({"7": [list(p) for p in full]},
                          open("/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/orbit_twisted_result.json","w"))
                sys.exit(0)

print(f"\nSTEP 5 done. Trade best = {trade_best}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 6: Simulated annealing
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 6: Simulated annealing (2000 iters)...")

best_entry = top_entries[0]
R_size, free_g, pi_i, swap, beta_g = best_entry
beta_g_list = [tuple(int(x) for x in row) for row in beta_g]

alpha_sa = list(alpha_set)
beta_sa = list(beta_g_list)
cnt_sa = build_cnt(alpha_sa, beta_sa)

def get_gamma():
    in_s = set(x for x, c in cnt_sa.items() if c > 0)
    res = [v for v in target_zone_pts if v not in in_s]
    return max_cap_bb(res)

g_sa = get_gamma()
sa_total = len(alpha_sa) + len(beta_sa) + len(g_sa)
sa_best = sa_total
deleted_sa = []

print(f"  SA start: total={sa_total}")

random.seed(42)
for it in range(2000):
    T = 0.5 * (1 - it / 2000)

    if deleted_sa and random.random() < 0.35:
        ri = random.randrange(len(deleted_sa))
        p_ins, src = deleted_sa[ri]
        if src == 'alpha' and alpha_sa:
            j = random.randrange(len(alpha_sa))
            p_del = alpha_sa[j]
            for b in beta_sa:
                x = tuple((-p_del[i]-b[i])%3 for i in range(6))
                cnt_sa[x] = cnt_sa.get(x,0) - 1
                if cnt_sa[x] == 0: del cnt_sa[x]
                x2 = tuple((-p_ins[i]-b[i])%3 for i in range(6))
                cnt_sa[x2] = cnt_sa.get(x2,0) + 1
            alpha_sa[j] = p_ins
            deleted_sa[ri] = (p_del, 'alpha')
        elif src == 'beta' and beta_sa:
            j = random.randrange(len(beta_sa))
            p_del = beta_sa[j]
            for a in alpha_sa:
                x = tuple((-a[i]-p_del[i])%3 for i in range(6))
                cnt_sa[x] = cnt_sa.get(x,0) - 1
                if cnt_sa[x] == 0: del cnt_sa[x]
                x2 = tuple((-a[i]-p_ins[i])%3 for i in range(6))
                cnt_sa[x2] = cnt_sa.get(x2,0) + 1
            beta_sa[j] = p_ins
            deleted_sa[ri] = (p_del, 'beta')
        else:
            continue
    else:
        which = 'alpha' if random.random() < 0.5 else 'beta'
        if which == 'alpha' and alpha_sa:
            j = random.randrange(len(alpha_sa))
            p = alpha_sa.pop(j)
            deleted_sa.append((p, 'alpha'))
            for b in beta_sa:
                x = tuple((-p[i]-b[i])%3 for i in range(6))
                cnt_sa[x] = cnt_sa.get(x,0) - 1
                if cnt_sa[x] == 0: del cnt_sa[x]
        elif which == 'beta' and beta_sa:
            j = random.randrange(len(beta_sa))
            p = beta_sa.pop(j)
            deleted_sa.append((p, 'beta'))
            for a in alpha_sa:
                x = tuple((-a[i]-p[i])%3 for i in range(6))
                cnt_sa[x] = cnt_sa.get(x,0) - 1
                if cnt_sa[x] == 0: del cnt_sa[x]
        else:
            continue

    g_new = get_gamma()
    new_total = len(alpha_sa) + len(beta_sa) + len(g_new)
    dE = new_total - sa_total

    if dE > 0 or (T > 0 and random.random() < math.exp(dE/T)):
        sa_total = new_total
        if new_total > sa_best:
            sa_best = new_total
            print(f"  SA iter {it}: new best={sa_best}")
            if sa_best >= 237:
                full = [(0,)+a for a in alpha_sa] + [(1,)+b for b in beta_sa] + [(2,)+tuple(c) for c in g_new]
                valid, reason = is_capset(full)
                print(f"  VERIFIER: valid={valid}, size={len(full)}")
                if valid and len(full) > 236:
                    print("*** BEATS 236 (SA)! ***")
                    json.dump({"7": [list(p) for p in full]},
                              open("/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/orbit_twisted_result.json","w"))
                    sys.exit(0)

print(f"\nSTEP 6 done. SA best = {sa_best}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 7: Final verdict
# ──────────────────────────────────────────────────────────────────────────────
overall_best = max(best_total, trade_best, sa_best)
print(f"\nSTEP 7: FINAL VERDICT")
print(f"  B&B best: {best_total}")
print(f"  Trade loop best: {trade_best}")
print(f"  SA best: {sa_best}")
print(f"  Overall best: {overall_best}")
print(f"  Did NOT beat 236. Honest negative — no valid cap >236 found.")
print(f"  certified_size=0  beats_236=False")
