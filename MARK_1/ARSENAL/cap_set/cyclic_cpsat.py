#!/usr/bin/env python3
"""Cyclic construction, CORRECT-by-construction via CP-SAT (the greedy version had a bug the
verifier caught). Find max S in F_3^6 with: S a cap, and no s0+sigma(s1)+sigma2(s2)=0 (s_i in S).
Then slices S,sigma(S),sigma2(S) -> a 7-cap of size 3|S|. Certified by frozen capset_verify."""
import json, itertools, time, sys
from ortools.sat.python import cp_model
from capset_verify import is_capset
ALL6=list(itertools.product(range(3),repeat=6)); IDX={v:i for i,v in enumerate(ALL6)}; N=729

def matvec(M,v): return tuple(sum(M[i][j]*v[j] for j in range(6))%3 for i in range(6))
def sigma_variants():
    # a few order-3 maps to try
    out=[]
    # (a) three unipotent Jordan blocks
    M=[[0]*6 for _ in range(6)]
    for b in range(3): M[2*b][2*b]=1;M[2*b][2*b+1]=1;M[2*b+1][2*b+1]=1
    out.append(("unipotent3",M))
    # (b) one Jordan block + identity elsewhere
    M2=[[1 if i==j else 0 for j in range(6)] for i in range(6)]; M2[0][1]=1
    out.append(("unipotent1",M2))
    return out

def solve(name,M,tlimit):
    sig=[IDX[matvec(M,v)] for v in ALL6]
    sig2=[sig[sig[i]] for i in range(N)]
    m=cp_model.CpModel(); x=[m.NewBoolVar(f"x{i}") for i in range(N)]
    # cap constraints on S
    seen=set()
    for i in range(N):
        for j in range(i+1,N):
            c=tuple((-(ALL6[i][k]+ALL6[j][k]))%3 for k in range(6)); kk=IDX[c]
            if kk!=i and kk!=j:
                t=frozenset((i,j,kk))
                if len(t)==3: seen.add(t)
    for t in seen: m.Add(sum(x[i] for i in t)<=2)
    # cyclic transversal: for all (i,j): a = -(sigma(i)+sigma2(j)); forbid x[i]+x[j]+x[a]<=2
    for i in range(N):
        si=ALL6[sig[i]]
        for j in range(N):
            s2j=ALL6[sig2[j]]
            a=tuple((-(si[k]+s2j[k]))%3 for k in range(6))
            m.Add(x[i]+x[j]+x[IDX[a]]<=2)
    m.Maximize(sum(x))
    s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=tlimit; s.parameters.num_search_workers=8
    t0=time.time(); st=s.Solve(m)
    S=[ALL6[i] for i in range(N) if s.Value(x[i])==1]
    full=[t+(0,) for t in S]+[matvec(M,t)+(1,) for t in S]+[matvec(M,matvec(M,t))+(2,) for t in S]
    v,r=is_capset(full)
    print(f"[{name}] |S|={len(S)} total={len(full)} status={s.StatusName(st)} valid={v} ({r}) t={time.time()-t0:.0f}s  (224 base / 236 rec)")
    if v and len(full)>224:
        json.dump({"7":[list(p) for p in full]},open(f"cap_n7_size{len(full)}_cyclic.json","w")); print("  >>> BEAT 224, persisted <<<")
    return len(full),v

if __name__=="__main__":
    for name,M in sigma_variants():
        solve(name,M,tlimit=200)
