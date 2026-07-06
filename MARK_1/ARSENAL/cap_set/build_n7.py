#!/usr/bin/env python3
"""n=7 cap (OPEN frontier: exact max unknown; best known LB=236). DERIVE-MODE, not search.
Structure (derived from first principles, no paper): slice F_3^7 by the last coord into
three F_3^6 caps S0,S1,S2 (last coord 0,1,2). Cap condition: each Si a cap; AND no
transversal x0+x1+x2=0 with xi in Si (since 0+1+2=0 mod3). Build S0,S1 from the verified
112-cap; find the largest compatible S2 EXACTLY with CP-SAT. Every result machine-verified.
"""
import json, itertools, sys
from ortools.sat.python import cp_model
from capset_verify import is_capset, KNOWN_LB

cap6 = [tuple(p) for p in json.load(open('cap_n6_size112.json'))['6']]
ALL6 = list(itertools.product(range(3), repeat=6))

def neg(p): return tuple((-x)%3 for x in p)
def add(p,q): return tuple((p[i]+q[i])%3 for i in range(6))

def max_slice2(S0, S1, tlimit=120):
    s0=set(S0); s1=set(S1)
    forbidden=set(neg(add(a,b)) for a in s0 for b in s1)   # transversal a0+a1+a2=0 -> a2=-(a0+a1)
    cand=[p for p in ALL6 if p not in forbidden]
    # max cap among candidates (no internal 3-term line)
    idx={p:i for i,p in enumerate(cand)}
    m=cp_model.CpModel(); x=[m.NewBoolVar(f'x{i}') for i in range(len(cand))]
    seen=set()
    for i in range(len(cand)):
        for j in range(i+1,len(cand)):
            c=tuple((-(cand[i][k]+cand[j][k]))%3 for k in range(6))
            if c in idx:
                t=frozenset((i,j,idx[c]))
                if len(t)==3: seen.add(t)
    for t in seen: m.Add(sum(x[i] for i in t)<=2)
    m.Maximize(sum(x))
    s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=tlimit; s.parameters.num_search_workers=8
    s.Solve(m)
    S2=[cand[i] for i in range(len(cand)) if s.Value(x[i])==1]
    return S2, len(cand)

def assemble(S0,S1,S2):
    return [p+(0,) for p in S0]+[p+(1,) for p in S1]+[p+(2,) for p in S2]

if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else 'product'  # 'product' (S1=S0) or 'neg' (S1=-S0)
    S0=cap6
    S1=cap6 if mode=='product' else [neg(p) for p in cap6]
    S2,ncand=max_slice2(S0,S1)
    full=assemble(S0,S1,S2)
    v,r=is_capset(full)
    total=len(full)
    print(f"mode={mode}: |S0|={len(S0)} |S1|={len(S1)} cand_for_S2={ncand} |S2|={len(S2)} -> TOTAL={total}")
    print(f"  verify: valid={v} ({r})  size={total}  vs known LB n=7 = {KNOWN_LB[7]}")
    if v and total>224:
        json.dump({"7":[list(p) for p in full]}, open(f"cap_n7_size{total}.json","w"))
        print(f"  persisted cap_n7_size{total}.json")
