#!/usr/bin/env python3
"""TWIN-LINES + APEX, CF-interlocked version.

Cells in F_3^2: L1 = {(i,0)}, L2 = {(j,1)}, apex w=(0,2).
L1 cell (i,0) carries alpha_i (slices of CF alpha-112-cap of F_3^6 by 1st coord).
L2 cell (j,1) carries beta_j + j*s (slices of CF beta, with arithmetic shift s).
Apex constraints pair (u_i, v_{-i}) -> forbidden = U_i -(alpha_i + beta_{-i} + (-i)s).
Scan s in F_3^5; exact max cap in allowed set; verify with frozen verifier.
"""
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

CF = json.load(open('/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/cap_n7_size236_CF.json'))
CF = CF['7'] if isinstance(CF, dict) else CF
print("CF size:", len(CF))
sl = {0: [], 1: [], 2: []}
for p in CF:
    sl[p[0]].append(p[1:])
sizes = {k: len(v) for k, v in sl.items()}
print("slice sizes:", sizes)
# alpha = the first 112-slice, beta = second, gamma = 12
names = sorted(sl, key=lambda k: -len(sl[k]))
alpha, beta = sl[names[0]], sl[names[1]]
# sub-slice by next coordinate
A = {i: [] for i in range(3)}; B = {i: [] for i in range(3)}
for p in alpha: A[p[0]].append(enc(p[1:]))
for p in beta:  B[p[0]].append(enc(p[1:]))
A = {i: np.array(v, dtype=int) for i, v in A.items()}
B = {i: np.array(v, dtype=int) for i, v in B.items()}
print("alpha subslices:", {i: len(A[i]) for i in A}, "beta:", {i: len(B[i]) for i in B})

MATCH = [(0, 0), (1, 2), (2, 1)]  # (i, sigma(i)) from cell geometry; sigma = negation

def sumset_neg(Aidx, Bidx):
    m = np.zeros(Q, dtype=bool)
    for a in Aidx:
        m[ADD[a][Bidx]] = True
    out = np.zeros(Q, dtype=bool)
    out[NEG[np.nonzero(m)[0]]] = True
    return out

base = [sumset_neg(A[i], B[sj]) for (i, sj) in MATCH]
print("base forbidden sizes:", [int(b.sum()) for b in base])

best = (-1, None, None)
for s in range(Q):
    sh = {0: 0, 1: int(NEG[s]), 2: s}   # forbidden shift for v_j is -(j*s)
    m = np.zeros(Q, dtype=bool)
    for (i, sj), b in zip(MATCH, base):
        d = sh[sj]
        if d == 0: m |= b
        else:
            mm = np.zeros(Q, dtype=bool); mm[ADD[d][np.nonzero(b)[0]]] = True
            m |= mm
    free = Q - int(m.sum())
    if free > best[0]:
        best = (free, s, m.copy())
        print(f"s={s}: allowed={free}")
free, s, m = best
allowed = np.nonzero(~m)[0]
print(f"\nBEST allowed set size {free} at s={s}")

def max_cap_in(pts):
    pts = sorted(int(p) for p in pts); n = len(pts); best = []
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
            cur.append(p); curset.add(p); bb(i + 1, cur, curset); curset.discard(p); cur.pop()
        bb(i + 1, cur, curset)
    bb(0, [], set())
    return best

cap = max_cap_in(allowed)
print(f"max apex cap = {len(cap)} -> TOTAL = {224 + len(cap)}")

pts7 = []
for i in range(3):
    for y in A[i]: pts7.append((i, 0, *ALLV[y]))
js = {0: 0, 1: s, 2: int(ADD[s][s])}
for j in range(3):
    for y in B[j]: pts7.append((j, 1, *ALLV[ADD[js[j]][y]]))
for c in cap: pts7.append((0, 2, *ALLV[c]))
sys.path.insert(0, '/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set')
from capset_verify import is_capset
ok, reason = is_capset(pts7)
print(f"FROZEN VERIFIER: valid={ok} reason={reason} size={len(set(map(tuple, pts7)))}")
if ok and len(set(map(tuple, pts7))) > 236:
    json.dump({"7": [list(map(int, p)) for p in pts7]},
              open('/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/cap_n7_twinlines_cf.json', 'w'))
    print("SAVED candidate > 236")
