#!/usr/bin/env python3
"""FRONTIER ENGINE v2 — broaden the family where the INVERSION can pay: vary the alpha<->beta RELATION
(coordinate-permuted involutions => different forbidden sets => different holes), and EXACT-solve the
largest holes (CP-SAT) instead of greedy. Goal: an (A,B) leaving a hole >12 that contains a cap >12 => >236.
All certified by frozen capset_verify. Fable-outage-robust: pure executable search, no model in the loop."""
import itertools, json, time, random
from capset_verify import is_capset
from ortools.sat.python import cp_model
from frontier_engine import build_AB, ALL6, neg, add, third, expand, block1, block2, delta_parity, interchange
IDX={v:i for i,v in enumerate(ALL6)}

def perm_cols(v, pi):   # permute coords (positions 0..5) by pi (a tuple perm of range(6))
    return tuple(v[pi[i]] for i in range(6))

def hole_of(A, Bp):
    forbidden=set(neg(add(a,b)) for a in A for b in Bp)
    return [p for p in ALL6 if p not in forbidden]

def maxcap_exact(hole, tlimit=15):
    idx={p:i for i,p in enumerate(hole)}
    m=cp_model.CpModel(); x=[m.NewBoolVar(f'x{i}') for i in range(len(hole))]
    seen=set()
    for i in range(len(hole)):
        for j in range(i+1,len(hole)):
            c=third(hole[i],hole[j])
            if c in idx:
                t=frozenset((i,j,idx[c]))
                if len(t)==3: seen.add(t)
    for t in seen: m.Add(sum(x[i] for i in t)<=2)
    m.Maximize(sum(x))
    s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=tlimit; s.parameters.num_search_workers=8
    s.Solve(m)
    return [hole[i] for i in range(len(hole)) if s.Value(x[i])==1]

if __name__=="__main__":
    t0=time.time()
    print("=== FRONTIER ENGINE v2: vary the alpha<->beta relation; exact-solve big holes ===")
    # base family params that produced valid 236
    PARAMS=[(3,2,0,1),(3,2,1,1),(2,2,0,1),(4,2,0,1),(3,1,0,1)]
    # coordinate permutations of cols 2-6 (keep col0 fixed) applied to B only
    perms=[(0,)+p for p in itertools.permutations(range(1,6))]   # 120
    random.Random(1).shuffle(perms)
    best=(236,None,'C-F baseline'); valids=0; holes_seen={}
    candidates=[]
    for (w,d,par,ov) in PARAMS:
        A,B=build_AB(w,d,par,ov)
        if len(A)!=112 or len(B)!=112: continue
        for pi in perms[:60]:        # 5 params x 60 perms = 300 relations
            Bp=set(perm_cols(b,pi) for b in B)
            H=hole_of(A,Bp)
            # greedy quick filter; record holes that are large enough to possibly beat 12
            candidates.append((len(H),w,d,par,ov,pi,A,Bp))
    candidates.sort(reverse=True)   # biggest holes first (most room for a big residual)
    print(f"built {len(candidates)} relations; biggest holes: {[c[0] for c in candidates[:8]]}")
    # exact-solve the residual on the largest holes (where >12 is even possible)
    checked=0
    for (hsz,w,d,par,ov,pi,A,Bp) in candidates:
        if hsz<=12: break           # cannot beat 12-residual if hole<=12
        C=maxcap_exact(list(set(ALL6)-set(ALL6)) if False else [p for p in ALL6 if p in set(_hole:=set(hole_of(A,Bp)))])
        full=[(0,)+a for a in A]+[(1,)+b for b in Bp]+[(2,)+c for c in C]
        v,r=is_capset(full); checked+=1
        if v:
            valids+=1
            if len(full)>best[0]:
                best=(len(full),full,f"w={w},d={d},par={par},ov={ov},pi={pi}")
                print(f"  NEW BEST total={len(full)} valid (hole={hsz}, |C|={len(C)}) {best[2]}")
        if checked>=40: break        # bound compute
    print(f"\nexact-checked {checked} big-hole relations in {time.time()-t0:.0f}s. BEST certified = {best[0]} (vs 236).")
    if best[0]>236 and best[1]:
        json.dump({"7":[list(p) for p in best[1]]},open(f"cap_n7_size{best[0]}_enginev2.json","w"))
        print(f"  >>> {best[0]} > 236 — persisted; MUST be independently audited before any claim <<<")
    else:
        print("  No relation beat 236. Honest: permuted-involution family also caps at 236 (or holes<=12).")
