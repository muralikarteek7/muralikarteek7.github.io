#!/usr/bin/env python3
"""LNS seeded at the verified 236: destroy k points, EXACT-rebuild the neighborhood with CP-SAT,
keep survivors forced. If the rebuilt cap > 236 -> a genuine improvement (heavy audit required).
Frozen-verifier gated. Honest expectation: 236 is a strong optimum; likely returns 236."""
import json, itertools, random, time
from ortools.sat.python import cp_model
from capset_verify import is_capset
random.seed(20260612)
n=7
ALL=list(itertools.product(range(3),repeat=n)); IDX={p:i for i,p in enumerate(ALL)}
cap0=[tuple(p) for p in json.load(open('cap_n7_size236_CF.json'))['7']]
assert is_capset(cap0)[0]

def third(a,b): return tuple((-(a[i]+b[i]))%3 for i in range(n))

def rebuild(survivors, tlimit=40):
    surv=set(survivors)
    # candidates: points not forbidden by a survivor-pair (necessary condition), excl. survivors
    forb=set()
    sl=list(surv)
    for i in range(len(sl)):
        for j in range(i+1,len(sl)):
            forb.add(third(sl[i],sl[j]))
    cands=[p for p in ALL if p not in surv and p not in forb]
    pool=list(surv)+cands
    pi={p:i for i,p in enumerate(pool)}
    m=cp_model.CpModel()
    x=[m.NewBoolVar(f'x{i}') for i in range(len(pool))]
    for p in surv: m.Add(x[pi[p]]==1)           # force survivors
    # cap constraints among the pool
    seen=set()
    for i in range(len(pool)):
        for j in range(i+1,len(pool)):
            c=third(pool[i],pool[j])
            if c in pi:
                t=frozenset((i,j,pi[c]))
                if len(t)==3: seen.add(t)
    for t in seen: m.Add(sum(x[i] for i in t)<=2)
    m.Maximize(sum(x))
    s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=tlimit; s.parameters.num_search_workers=8
    s.Solve(m)
    return [pool[i] for i in range(len(pool)) if s.Value(x[i])==1]

best=list(cap0); t0=time.time(); BUDGET=420; rounds=0
while time.time()-t0<BUDGET:
    rounds+=1
    k=random.choice([12,18,25,35])
    survivors=random.sample(best, len(best)-k)
    rebuilt=rebuild(survivors, tlimit=35)
    v,r=is_capset(rebuilt)
    if v and len(rebuilt)>len(best):
        best=rebuilt
        print(f"  [round {rounds}, destroy {k}] IMPROVED -> {len(best)} (valid)")
        if len(best)>236:
            json.dump({"7":[list(p) for p in best]},open(f"cap_n7_size{len(best)}_LNS.json","w"))
            print(f"  >>> {len(best)} > 236 — persisted; MUST be independently audited <<<")
    elif rounds%5==0:
        print(f"  [round {rounds}] best still {len(best)} (t={time.time()-t0:.0f}s)")
print(f"\nLNS done: {rounds} rounds, best certified = {len(best)} (vs 236).")
print("  236 not beaten by LNS — strong local optimum (honest)." if len(best)<=236 else "  >236 FOUND — audit before any claim.")
