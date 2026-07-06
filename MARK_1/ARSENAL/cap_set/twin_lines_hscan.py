#!/usr/bin/env python3
"""Twin-lines+apex: scan beta's slicing hyperplane h (all 364 directions of F_3^6),
slice-permutation rho (6), and arithmetic shift s (243). alpha fixed = CF alpha
sliced by coord 1. Maximize allowed apex set = complement of 3 matched sumsets."""
import json, itertools, sys
import numpy as np

N = 5; Q = 3**N
POW = np.array([3**i for i in range(N)])
ALLV = np.zeros((Q, N), dtype=np.int8)
for r in range(Q):
    x = r
    for i in range(N):
        ALLV[r, i] = x % 3; x //= 3
ADD = np.zeros((Q, Q), dtype=np.int32)
for d in range(Q):
    ADD[d] = ((ALLV + ALLV[d]) % 3) @ POW
NEG = ((-ALLV) % 3) @ POW
def enc(v): return int(sum(int(v[i]) * POW[i] for i in range(N)))

CF = json.load(open('/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/cap_n7_size236_CF.json'))['7']
sl = {0: [], 1: [], 2: []}
for p in CF: sl[p[0]].append(p[1:])
names = sorted(sl, key=lambda k: -len(sl[k]))
alpha = np.array(sl[names[0]])   # 112 x 6
beta  = np.array(sl[names[1]])
A = {i: np.array([enc(p[1:]) for p in alpha if p[0] == i]) for i in range(3)}

MATCH = [(0, 0), (1, 2), (2, 1)]

def sumset_neg(Aidx, Bidx):
    m = np.zeros(Q, dtype=bool)
    m[ADD[np.ix_(Aidx, Bidx)].ravel()] = True
    out = np.zeros(Q, dtype=bool)
    out[NEG[np.nonzero(m)[0]]] = True
    return out

def directions():
    seen = set()
    for h in itertools.product(range(3), repeat=6):
        if all(c == 0 for c in h): continue
        h2 = tuple((2 * c) % 3 for c in h)
        if h2 in seen: continue
        seen.add(h)
        yield np.array(h)

best = (-1, None)
perms = list(itertools.permutations(range(3)))
for hi, h in enumerate(directions()):
    hv = (beta @ h) % 3
    k = int(np.nonzero(h)[0][0])  # drop coord k (h_k != 0)
    keep = [c for c in range(6) if c != k]
    S = {}
    ok = True
    for c in range(3):
        pts = beta[hv == c][:, keep]
        if len(pts) == 0: ok = False; break
        S[c] = (pts @ POW) if pts.shape[1] == N else None
    if not ok: continue
    SUM = {(i, m): sumset_neg(A[i], S[m]) for i in range(3) for m in range(3)}
    for rho in perms:
        base = [SUM[(i, rho[sj])] for (i, sj) in MATCH]
        nz = [np.nonzero(b)[0] for b in base]
        for s in range(Q):
            m = base[0].copy() if True else None
            # shifts by -(j*s) for cell v_j, j = sigma(i) in MATCH order: j=0,2,1
            m = np.zeros(Q, dtype=bool)
            for (i, sj), b, z in zip(MATCH, base, nz):
                d = 0 if sj == 0 else (int(NEG[s]) if sj == 1 else s)
                if d == 0: m |= b
                else: m[ADD[d][z]] = True
            free = Q - int(m.sum())
            if free > best[0]:
                best = (free, (hi, tuple(h), rho, s, np.nonzero(~m)[0].copy()))
                print(f"allowed={free}  h={tuple(h)} rho={rho} s={s}", flush=True)
print("\nBEST:", best[0])
free, (hi, h, rho, s, allowed) = best

def max_cap_in(pts):
    pts = sorted(int(p) for p in pts); n = len(pts); bst = []
    def bb(i, cur, curset):
        nonlocal bst
        if len(cur) + (n - i) <= len(bst): return
        if i == n:
            if len(cur) > len(bst): bst = cur[:]
            return
        p = pts[i]; ok = True
        for a in cur:
            t = int(NEG[ADD[a][p]])
            if t in curset and t != a and t != p: ok = False; break
        if ok:
            cur.append(p); curset.add(p); bb(i+1, cur, curset); curset.discard(p); cur.pop()
        bb(i+1, cur, curset)
    bb(0, [], set())
    return bst

cap = max_cap_in(allowed)
print(f"max apex cap = {len(cap)}  -> TOTAL = {224 + len(cap)}")

# rebuild and verify
h = np.array(h)
hv = (beta @ h) % 3
k = int(np.nonzero(h)[0][0]); keep = [c for c in range(6) if c != k]
S = {c: (beta[hv == c][:, keep] @ POW) for c in range(3)}
pts7 = []
for i in range(3):
    for y in A[i]: pts7.append((i, 0, *ALLV[y]))
js = {0: 0, 1: s, 2: int(ADD[s][s])}
for j in range(3):
    for y in S[rho[j]]: pts7.append((j, 1, *ALLV[ADD[js[j]][int(y)]]))
for c in cap: pts7.append((0, 2, *ALLV[c]))
sys.path.insert(0, '/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set')
from capset_verify import is_capset
okk, reason = is_capset(pts7)
print(f"FROZEN VERIFIER: valid={okk} reason={reason} size={len(set(map(tuple, pts7)))}")
if okk and len(set(map(tuple, pts7))) > 236:
    json.dump({"7": [list(map(int, p)) for p in pts7]},
              open('/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/cap_n7_GT236.json', 'w'))
    print("SAVED >236 CANDIDATE")
