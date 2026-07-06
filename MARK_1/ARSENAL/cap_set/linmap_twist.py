#!/usr/bin/env python3
"""NEW ANGLE (theory+computation): twist the second slice by a LINEAR map phi in GL(6,3).
The naive product S0=S1=C forces S2=0 because the sumset C+C covers all 729 points.
THEORY: S1=phi(C) is still a 112-cap, but the sumset C+phi(C) may be SMALLER, freeing room
for S2 -> total > 224. We scan many phi (random invertible + structured), measure the free
space, and exact/greedy-solve S2 on the best. Everything certified by frozen capset_verify."""
import json, itertools, random
from capset_verify import is_capset
random.seed(3)
C=[tuple(p) for p in json.load(open('cap_n6_size112.json'))['6']]
ALL6=list(itertools.product(range(3),repeat=6))
def neg(p): return tuple((-x)%3 for x in p)
def matvec(M,v): return tuple(sum(M[i][j]*v[j] for j in range(6))%3 for i in range(6))
def det_ok(M):
    # invertible over F_3 iff row-reduces to full rank
    A=[row[:] for row in M]; n=6; r=0
    for c in range(n):
        piv=None
        for i in range(r,n):
            if A[i][c]%3!=0: piv=i;break
        if piv is None: continue
        A[r],A[piv]=A[piv],A[r]
        inv=pow(A[r][c]%3,-1,3) if A[r][c]%3 in (1,2) else None
        if inv is None: continue
        A[r]=[(x*inv)%3 for x in A[r]]
        for i in range(n):
            if i!=r and A[i][c]%3!=0:
                f=A[i][c]%3; A[i]=[(A[i][j]-f*A[r][j])%3 for j in range(n)]
        r+=1
    return r==n
def rand_invertible():
    while True:
        M=[[random.randint(0,2) for _ in range(6)] for _ in range(6)]
        if det_ok(M): return M

def free_for(S0,S1):
    s0=set(S0); s1=set(S1)
    forb=set(neg(tuple((a[i]+b[i])%3 for i in range(6))) for a in s0 for b in s1)
    return 729-len(forb), forb

def greedy_cap(cands):
    def third(a,b): return tuple((-(a[i]+b[i]))%3 for i in range(6))
    chosen=[]; cs=set()
    for p in cands:
        if all(third(p,q) not in cs for q in chosen):
            chosen.append(p); cs.add(p)
    return chosen

best=(0,None)
print("scanning linear maps phi for S1=phi(C); free>0 means room beyond 224...")
TRIALS=400
maxfree=0
for t in range(TRIALS):
    M=rand_invertible()
    S1=[matvec(M,v) for v in C]
    free,forb=free_for(C,S1)
    maxfree=max(maxfree,free)
    if free>0:
        cand=[p for p in ALL6 if p not in forb]; random.shuffle(cand)
        S2=greedy_cap(cand)
        total=112+112+len(S2)
        if total>best[0]:
            best=(total,(C,S1,S2,M))
            print(f"  [phi {t}] free={free} |S2|={len(S2)} TOTAL={total}")
print(f"scanned {TRIALS} linear maps. max free space seen = {maxfree}. best total = {best[0]} (baseline 224)")
if best[1] and best[0]>224:
    C0,S1,S2,M=best[1]
    full=[p+(0,) for p in C0]+[p+(1,) for p in S1]+[p+(2,) for p in S2]
    v,r=is_capset(full)
    print(f"CERTIFY: valid={v} ({r}) size={len(full)}")
    if v: json.dump({"7":[list(p) for p in full]}, open(f"cap_n7_size{len(full)}_linmap.json","w")); print("persisted")
else:
    print("No linear twist beat 224 -> the sumset C+phi(C) still covers all 729 for every phi tried (honest negative).")
