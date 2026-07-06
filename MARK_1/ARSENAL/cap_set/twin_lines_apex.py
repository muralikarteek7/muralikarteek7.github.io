#!/usr/bin/env python3
"""TWIN-LINES + APEX construction in F_3^7 (2+5 split).

Cells = F_3^2 (coords x1,x2). Support: line L1 (x2=0), line L2 (x2=1),
apex w=(0,2). Collinear cell triples => constraints:
  - within L1: slices = slices of a 112-cap K of F_3^6  (cap condition holds)
  - within L2: slices of an affine image of K: y -> M y + t + x*s, x -> a*x+b
  - apex vs matchings: lines through w hit (u_i, v_sigma(i)), sigma=(0,2,1)... derived below.
Apex set A_w = max cap inside complement of the 3 forbidden sumsets.
Translation freedom (t,s) reduces to a single shift parameter s in F_3^5.
Search over slice-permutation pi (6) x M in {I} U random GL(5,3) x s (243).
"""
import json, itertools, random, sys
import numpy as np

random.seed(7); np.random.seed(7)

# ---- F_3^5 encoding as ints 0..242 ----
N = 5; Q = 3**N
POW = np.array([3**i for i in range(N)])
def enc(v): return int(sum(int(v[i])*POW[i] for i in range(N)))
ALLV = np.array(list(itertools.product(range(3), repeat=N)))[:, ::-1]  # row r decodes int r? build properly:
ALLV = np.zeros((Q, N), dtype=np.int8)
for r in range(Q):
    x = r
    for i in range(N):
        ALLV[r, i] = x % 3; x //= 3
# addition table action: ADD[d] maps point p -> p+d (as index array)
ADD = np.zeros((Q, Q), dtype=np.int32)
for d in range(Q):
    s = (ALLV + ALLV[d]) % 3
    ADD[d] = s @ POW
NEG = ((-ALLV) % 3) @ POW  # negation map

K = json.load(open('/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/cap_n6_size112.json'))['6']
slices = {0: [], 1: [], 2: []}
for p in K:
    slices[p[0]].append(enc(p[1:]))
Kslice = {i: np.array(v) for i, v in slices.items()}

# geometry: cells u_i=(i,0), v_j=(j,1), w=(0,2). Lines through w with one cell in each line:
# dir (0,1): w,(0,0),(0,1) -> pair (u0,v0); dir(1,1): w,(1,0),(2,1) -> (u1,v2); dir(1,2): w,(1,1),(2,0) -> (u2,v1)
MATCH = [(0, 0), (1, 2), (2, 1)]  # (i, sigma(i))

def sumset_neg(Aidx, Bidx):
    """boolean mask over Q of points -(a+b), a in A, b in B."""
    m = np.zeros(Q, dtype=bool)
    s = ADD[np.ix_(Aidx, Bidx)] if False else None
    # vectorized: for each a, points a+B
    for a in Aidx:
        m[ADD[a][Bidx]] = True
    # now m marks a+b; map to -(a+b)
    out = np.zeros(Q, dtype=bool)
    out[NEG[np.nonzero(m)[0]]] = True
    return out

def rand_gl5():
    while True:
        M = np.random.randint(0, 3, (N, N))
        # det over F_3 via gaussian elim
        A = M.copy() % 3; det = 1
        for c in range(N):
            piv = None
            for r in range(c, N):
                if A[r, c] % 3:
                    piv = r; break
            if piv is None: det = 0; break
            if piv != c:
                A[[c, piv]] = A[[piv, c]]; det = -det
            det = (det * A[c, c]) % 3
            inv = 1 if A[c, c] % 3 == 1 else 2
            A[c] = (A[c] * inv) % 3
            for r in range(c+1, N):
                A[r] = (A[r] - A[r, c]*A[c]) % 3
        if det % 3:
            return M % 3

def apply_M(M, idx):
    pts = ALLV[idx]
    return ((pts @ M.T) % 3) @ POW

def max_cap_in(allowed_idx, cap_to_beat):
    """exact-ish max cap (3-AP-free subset) inside allowed_idx via branch&bound."""
    pts = list(allowed_idx); n = len(pts)
    pset = set(pts)
    best = []
    pts.sort()
    def third(a, b):
        return int(NEG[ADD[a][b]])
    sys.setrecursionlimit(10000)
    def bb(i, cur, curset):
        nonlocal best
        if len(cur) + (n - i) <= len(best):
            return
        if i == n:
            if len(cur) > len(best): best = cur[:]
            return
        p = pts[i]
        ok = True
        for a_j in range(len(cur)):
            a = cur[a_j]
            t = third(a, p)
            if t in curset and t != a and t != p:
                ok = False; break
            if t == p or t == a:  # t==p means 2p+a=0 -> p=a impossible; skip
                pass
        if ok:
            cur.append(p); curset.add(p)
            bb(i+1, cur, curset)
            curset.discard(p); cur.pop()
        bb(i+1, cur, curset)
    bb(0, [], set())
    return best

def evaluate(M, pi, full=False):
    """pi: permutation of slices for L2. Returns best (apex_size, s, apex_set)."""
    MK = {j: apply_M(M, Kslice[pi[j]]) for j in range(3)}
    # base forbidden sumsets per matching, before the s-shift: F_i = -(K_i + MK_{sigma(i)})
    base = [sumset_neg(Kslice[i], MK[sj]) for (i, sj) in MATCH]
    # shifts: v_j gets +(t + j*s); WLOG absorb t so matching with sigma(i)=0 unshifted.
    # forbidden_i shifted by -(sigma(i)*s) then negated... careful: b in MK+t+js => -(a+b) = base_pt - t - j*s.
    # WLOG choose t s.t. shift for j=0 is 0; then shifts are -(j*s) for j=1,2 i.e. (0, -s, s) by sigma(i).
    results = []
    for s in range(Q):
        sh = {0: 0, 1: int(NEG[s]), 2: s}  # -1*s = NEG[s], -2*s = s
        m = np.zeros(Q, dtype=bool)
        for (i, sj), b in zip(MATCH, base):
            d = sh[sj]
            if d == 0:
                m |= b
            else:
                m[ADD[d][np.nonzero(b)[0]]] = True
        free = Q - int(m.sum())
        results.append((free, s, m))
    results.sort(key=lambda r: -r[0])
    return results[:3]

def main():
    perms = list(itertools.permutations(range(3)))
    Ms = [np.eye(N, dtype=int)] + [rand_gl5() for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 60)]
    best_overall = (0, None)
    for mi, M in enumerate(Ms):
        for pi in perms:
            for free, s, m in evaluate(M, pi):
                if free > best_overall[0]:
                    best_overall = (free, (mi, M.copy(), pi, s, m.copy()))
                    print(f"new best FREE={free} (M#{mi}, pi={pi}, s={s})", flush=True)
    free, (mi, M, pi, s, m) = best_overall
    allowed = np.nonzero(~m)[0]
    print(f"\nBest allowed-set size: {free}. Now exact max cap inside...")
    cap = max_cap_in(allowed, 12)
    print(f"max apex cap size = {len(cap)}  -> TOTAL = {224 + len(cap)}")
    if len(cap) > 12:
        print("BEATS 236?! assembling full 7-dim set for the frozen verifier...")
    # assemble full point set regardless, verify validity & size
    pts7 = []
    for i in range(3):
        for yidx in Kslice[i]:
            pts7.append((i, 0, *ALLV[yidx]))
    MK = {j: apply_M(M, Kslice[pi[j]]) for j in range(3)}
    # shifts: j=0:0, j=1: ?, j=2: ? -- replicate evaluate's convention: shift applied to forbidden was -(j s);
    # that corresponds to v_j translated by + (j*s) with t=0 for j... b' = b + j*s => -(a+b') = -(a+b) - j*s. yes t=0.
    for j in range(3):
        for yidx in MK[j]:
            y = int(ADD[(j * s) % Q if j == 0 else (s if j == 1 else int(ADD[s][s]))][yidx]) if j else int(yidx)
            # j*s in the group = s added j times
            pts7.append((j, 1, *ALLV[y]))
    for c in cap:
        pts7.append((0, 2, *ALLV[c]))
    sys.path.insert(0, '/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set')
    from capset_verify import is_capset
    ok, reason = is_capset(pts7)
    print(f"FROZEN VERIFIER: valid={ok} reason={reason} size={len(set(map(tuple,pts7)))}")
    json.dump({"7": [list(map(int, p)) for p in pts7]}, open('cap_n7_twinlines.json', 'w'))

main()
