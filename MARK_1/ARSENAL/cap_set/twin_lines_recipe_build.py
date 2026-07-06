#!/usr/bin/env python3
"""
TWIN-LINES + APEX construction per the specified recipe.

Recipe summary:
  Split F_3^7 as F_3^2 x F_3^5.
  Cells: u_i=(i,0), v_j=(j,1) for i,j in {0,1,2}, apex w=(0,2).
  L1 line: assign u_i the slice A_i of alpha (slices of CF alpha-112-cap by coord 1).
  L2 line: assign v_j a GL(5,3)-twisted and shifted slice of beta.
  Apex: max cap inside complement of 3 negation-matched sumset-avoidance constraints.
  Goal: assemble full 7-dim point set and verify with frozen verifier.

This script:
  1. Loads the CF 236-cap and slices into alpha(112), beta(112), gamma(12).
  2. Sub-slices alpha by next coord: A_0, A_1, A_2 in F_3^5.
  3. For L2: scans hyperplanes h in F_3^6 (182 directions), projects beta slices
     to F_3^5, applies M in GL(5,3) (identity + random samples), slice-permutation
     rho in S_3, and shift s in F_3^5.
  4. Computes allowed apex set (complement of 3 sumsets) and max cap inside it.
  5. Assembles and verifies with the FROZEN verifier (is_capset).
  6. Reports the verified size.
"""
import json, itertools, sys, time
import numpy as np

sys.path.insert(0, '/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set')
from capset_verify import is_capset

# ---- F_3^5 encoding ----
N = 5; Q = 3**N
POW = np.array([3**i for i in range(N)], dtype=np.int32)
ALLV = np.zeros((Q, N), dtype=np.int8)
for r in range(Q):
    x = r
    for i in range(N):
        ALLV[r, i] = x % 3; x //= 3

# addition table: ADD[d][p] = p+d (as index)
ADD = np.zeros((Q, Q), dtype=np.int32)
for d in range(Q):
    ADD[d] = ((ALLV + ALLV[d]) % 3) @ POW
NEG = ((-ALLV) % 3) @ POW  # negation map

def enc5(v):
    """Encode a 5-tuple to int."""
    return int(sum(int(v[i]) * POW[i] for i in range(N)))

# ---- Load CF 236-cap ----
CF_PATH = '/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/cap_n7_size236_CF.json'
CF_data = json.load(open(CF_PATH))
CF = CF_data['7'] if isinstance(CF_data, dict) else CF_data
print(f"CF cap size: {len(CF)}")

# Slice by first coordinate
sl = {0: [], 1: [], 2: []}
for p in CF:
    sl[p[0]].append(p[1:])  # p[1:] is a 6-tuple in F_3^6
sizes = {k: len(v) for k, v in sl.items()}
print(f"Slice sizes by coord 0: {sizes}")

# alpha = largest slice (112), beta = second (112), gamma = smallest (12)
names = sorted(sl, key=lambda k: -len(sl[k]))
alpha_pts = sl[names[0]]  # 112 points in F_3^6
beta_pts  = sl[names[1]]  # 112 points in F_3^6
print(f"alpha slice index={names[0]}, beta slice index={names[1]}, gamma={names[2]}")

# Sub-slice alpha by ITS first coord (p[0] in the 6-tuple) into A_0, A_1, A_2 in F_3^5
A = {i: [] for i in range(3)}
for p in alpha_pts:
    A[p[0]].append(enc5(p[1:]))  # p[1:] is a 5-tuple
A = {i: np.array(v, dtype=np.int32) for i, v in A.items()}
print(f"alpha sub-slices sizes: {dict((i,len(A[i])) for i in range(3))}")

# beta as numpy array in F_3^6
beta_arr = np.array(beta_pts, dtype=np.int8)  # shape (112, 6)
print(f"beta shape: {beta_arr.shape}")

# ---- Geometry: negation matching (sigma(i) = -i mod 3) ----
# From recipe step 1: lines through w=(0,2) pair (u_0,v_0), (u_1,v_2), (u_2,v_1)
# sigma: 0->0, 1->2, 2->1  (negation in F_3)
MATCH = [(0, 0), (1, 2), (2, 1)]  # (i, sigma(i))

def sumset_neg(Aidx, Bidx):
    """Compute mask of -(a+b) for a in A, b in B."""
    m = np.zeros(Q, dtype=bool)
    for a in Aidx:
        m[ADD[a][Bidx]] = True
    out = np.zeros(Q, dtype=bool)
    out[NEG[np.nonzero(m)[0]]] = True
    return out

def apply_M(M, idx_arr):
    """Apply linear map M in GL(5,3) to points given as F_3^5 indices."""
    pts = ALLV[idx_arr]  # shape (k, 5)
    return ((pts @ M.T) % 3) @ POW

def rand_gl5(rng):
    """Sample a random invertible matrix over F_3."""
    while True:
        M = rng.integers(0, 3, (N, N))
        Ac = M.copy() % 3
        det = 1
        for c in range(N):
            piv = None
            for r in range(c, N):
                if Ac[r, c] % 3:
                    piv = r; break
            if piv is None: det = 0; break
            if piv != c:
                Ac[[c, piv]] = Ac[[piv, c]]; det = -det
            det = (det * Ac[c, c]) % 3
            inv_c = 1 if Ac[c, c] % 3 == 1 else 2
            Ac[c] = (Ac[c] * inv_c) % 3
            for r in range(c + 1, N):
                Ac[r] = (Ac[r] - Ac[r, c] * Ac[c]) % 3
        if det % 3:
            return M % 3

def max_cap_in(allowed_arr):
    """Exact maximum cap (branch-and-bound) inside the allowed point set."""
    pts = sorted(int(p) for p in allowed_arr)
    n = len(pts)
    best = []
    pset = set(pts)
    sys.setrecursionlimit(100000)
    def bb(i, cur, curset):
        nonlocal best
        if len(cur) + (n - i) <= len(best): return
        if i == n:
            if len(cur) > len(best): best = cur[:]
            return
        p = pts[i]; ok = True
        for a in cur:
            t = int(NEG[ADD[a][p]])
            if t in curset and t != a and t != p: ok = False; break
        if ok:
            cur.append(p); curset.add(p)
            bb(i + 1, cur, curset)
            curset.discard(p); cur.pop()
        bb(i + 1, cur, curset)
    bb(0, [], set())
    return best

def gen_hyperplane_directions():
    """Generate all 182 distinct hyperplane normal directions in F_3^6 (up to scalar)."""
    seen = set()
    for h in itertools.product(range(3), repeat=6):
        if all(c == 0 for c in h): continue
        # canonical form: first nonzero entry = 1
        first_nz = next(c for c in h if c != 0)
        inv = 1 if first_nz == 1 else 2  # inverse of first_nz in F_3
        hc = tuple((inv * c) % 3 for c in h)
        if hc in seen: continue
        seen.add(hc)
        yield np.array(hc, dtype=np.int8)

def scan(num_gl_matrices=0, seed=42):
    """
    Main scan: h x rho x s with M=Identity first, then GL(5,3) twists.
    Returns best (allowed_size, assembled_7d_points).
    """
    rng = np.random.default_rng(seed)

    # Pre-enumerate hyperplanes
    print("Enumerating hyperplane directions...", flush=True)
    hdirs = list(gen_hyperplane_directions())
    print(f"  {len(hdirs)} distinct hyperplane directions", flush=True)

    perms = list(itertools.permutations(range(3)))

    # GL(5,3) matrices to try: identity + random samples
    Ms = [np.eye(N, dtype=np.int32)]
    for _ in range(num_gl_matrices):
        Ms.append(rand_gl5(rng))
    print(f"Will try {len(Ms)} GL(5,3) matrices", flush=True)

    best = {
        'allowed': -1,
        'total': -1,
        'h': None, 'rho': None, 's': None, 'M': None,
        'apex_cap': [],
        'pts7': [],
    }

    t0 = time.time()
    total_configs = len(hdirs) * len(perms) * Q * len(Ms)
    print(f"Total (h x rho x s x M) configs: {total_configs}", flush=True)

    for mi, M in enumerate(Ms):
        for hi, h in enumerate(hdirs):
            # Slice beta by hyperplane h: hv[k] = h . beta[k] mod 3
            hv = (beta_arr.astype(np.int32) @ h.astype(np.int32)) % 3
            # Find a coordinate k with h[k] != 0 to drop (projection bijective on slices)
            k = int(np.nonzero(h)[0][0])
            keep = [c for c in range(6) if c != k]
            # Project slices to F_3^5
            S_raw = {}
            ok_h = True
            for c in range(3):
                mask = (hv == c)
                if not np.any(mask):
                    ok_h = False; break
                proj = beta_arr[mask][:, keep]  # shape (count, 5)
                # Apply M
                twisted = (proj.astype(np.int32) @ M.T) % 3
                S_raw[c] = (twisted @ POW).astype(np.int32)
            if not ok_h: continue

            # Pre-compute all sumsets needed for this (h, M)
            SUM = {}
            for i in range(3):
                for m in range(3):
                    SUM[(i, m)] = sumset_neg(A[i], S_raw[m])

            for rho in perms:
                # base forbidden: for each matching (i, sigma(i)), use slice rho[sigma(i)] of beta
                base = [SUM[(i, rho[sj])] for (i, sj) in MATCH]
                nz_base = [np.nonzero(b)[0] for b in base]

                for s_idx in range(Q):
                    # Shifts: v_j gets +j*s; forbidden for matching pair shifts by -(j*s)
                    # j = sigma(i) in MATCH: pairs (j=0, j=2, j=1) for MATCH [(0,0),(1,2),(2,1)]
                    # shift for j=0: 0, j=1: -s = NEG[s], j=2: -2s = s (since -2 = 1 mod 3)
                    m_forbidden = np.zeros(Q, dtype=bool)
                    for idx_m, ((i, sj), b, nz) in enumerate(zip(MATCH, base, nz_base)):
                        if sj == 0:
                            d = 0
                        elif sj == 1:
                            d = int(NEG[s_idx])
                        else:  # sj == 2
                            d = s_idx
                        if d == 0:
                            m_forbidden |= b
                        else:
                            m_forbidden[ADD[d][nz]] = True

                    free = Q - int(m_forbidden.sum())
                    if free > best['allowed']:
                        allowed_pts = np.nonzero(~m_forbidden)[0]
                        best['allowed'] = free
                        best['h'] = tuple(int(x) for x in h)
                        best['rho'] = rho
                        best['s'] = s_idx
                        best['M'] = M.copy()
                        best['allowed_pts'] = allowed_pts.copy()
                        elapsed = time.time() - t0
                        print(f"  NEW BEST allowed={free} h={best['h']} rho={rho} s={s_idx} M#{mi} t={elapsed:.1f}s", flush=True)

        print(f"M#{mi} done. Best allowed so far: {best['allowed']}", flush=True)

    return best

def assemble_and_verify(best):
    """Assemble the full 7-dim point set and run the frozen verifier."""
    h = np.array(best['h'], dtype=np.int8)
    rho = best['rho']
    s_idx = best['s']
    M = best['M']

    # L1: cells u_i=(i,0) carry A_i (from alpha sub-slices)
    pts7 = []
    for i in range(3):
        for y in A[i]:
            pts7.append((i, 0, *ALLV[y]))

    # L2: cells v_j=(j,1) carry M-twisted projected beta slices with shift j*s
    hv = (beta_arr.astype(np.int32) @ h.astype(np.int32)) % 3
    k = int(np.nonzero(h)[0][0])
    keep = [c for c in range(6) if c != k]
    S_twisted = {}
    for c in range(3):
        mask = (hv == c)
        proj = beta_arr[mask][:, keep].astype(np.int32)
        twisted = (proj @ M.T) % 3
        S_twisted[c] = (twisted @ POW).astype(np.int32)

    # j*s: j=0 -> 0, j=1 -> s, j=2 -> 2s = ADD[s][s]
    js_shift = {0: 0, 1: s_idx, 2: int(ADD[s_idx][s_idx])}
    for j in range(3):
        for y in S_twisted[rho[j]]:
            shifted = int(ADD[js_shift[j]][int(y)])
            pts7.append((j, 1, *ALLV[shifted]))

    # Apex: run exact max cap in allowed set
    print(f"\nComputing max cap in allowed set of size {best['allowed']}...", flush=True)
    if best['allowed'] > 0:
        apex_cap = max_cap_in(best['allowed_pts'])
    else:
        apex_cap = []
    print(f"Max apex cap size: {len(apex_cap)}", flush=True)

    for c in apex_cap:
        pts7.append((0, 2, *ALLV[c]))

    total = 112 + 112 + len(apex_cap)
    print(f"Total assembled: {len(pts7)} points (expected {total})", flush=True)

    # Run frozen verifier
    print("Running frozen verifier (is_capset)...", flush=True)
    valid, reason = is_capset(pts7)
    size = len(set(map(tuple, pts7)))
    print(f"FROZEN VERIFIER: valid={valid} reason={reason} size={size}", flush=True)

    return valid, reason, size, pts7, apex_cap

# ---- MAIN ----
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-gl', type=int, default=0,
                        help='Number of random GL(5,3) matrices to try beyond identity (0=M=I only)')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    print(f"=== TWIN-LINES + APEX RECIPE BUILD ===")
    print(f"GL matrices beyond identity: {args.num_gl}, seed={args.seed}")
    print(f"Scan: h(182) x rho(6) x s(243) x M({1+args.num_gl})")

    best = scan(num_gl_matrices=args.num_gl, seed=args.seed)
    print(f"\n=== BEST ALLOWED SET SIZE: {best['allowed']} ===")

    valid, reason, size, pts7, apex_cap = assemble_and_verify(best)

    print(f"\n=== FINAL RESULT ===")
    print(f"Valid: {valid}")
    print(f"Reason: {reason}")
    print(f"Size: {size}")
    print(f"Beats 236: {valid and size > 236}")

    if valid:
        out_path = '/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/cap_n7_recipe_build.json'
        json.dump({"7": [list(map(int, p)) for p in pts7]}, open(out_path, 'w'))
        print(f"Saved to {out_path}")
    else:
        print(f"Not saving: invalid cap set ({reason})")

    # Print structured result for the orchestrator
    print(f"\nSTRUCTURED_RESULT: implemented=True certified_size={size if valid else 0} valid={valid} beats_236={valid and size > 236}")
