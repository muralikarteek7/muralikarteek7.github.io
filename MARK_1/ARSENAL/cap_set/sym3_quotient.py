#!/usr/bin/env python3
"""Order-3 symmetric cap search in F_3^7: find max cap invariant under
T(x0, x1..x6) = (x0+1, pi(x) + v) with pi = coordinate 3-cycles (x1 x2 x3)(x4 x5 x6).
Cap = union of T-orbits (all size 3). Search orbits via CP-SAT."""
import itertools, sys, json
from ortools.sat.python import cp_model

V = list(itertools.product(range(3), repeat=7))
idx = {p:i for i,p in enumerate(V)}
vlist = [(0,0,0,0,0,0)]
if len(sys.argv)>1: vlist=[tuple(map(int,sys.argv[1]))]

def run(v, tlimit):
    def T(p):
        x0 = (p[0]+1)%3
        x = p[1:]
        px = (x[2], x[0], x[1], x[5], x[3], x[4])  # pi: cycle within each block
        return (x0,) + tuple((px[i]+v[i])%3 for i in range(6))
    # orbits
    orb = [-1]*len(V)
    orbits = []
    for i,p in enumerate(V):
        if orb[i]!=-1: continue
        o = [p, T(p), T(T(p))]
        oid = len(orbits)
        for q in o: orb[idx[q]] = oid
        orbits.append(o)
    # check all orbits size 3
    assert all(len(set(o))==3 for o in orbits), "fixed points!"
    nO = len(orbits)
    # forbidden orbit sets from lines: for each line {p,q,r} p+q+r=0 distinct
    m = cp_model.CpModel()
    x = [m.new_bool_var(f'o{i}') for i in range(nO)]
    seen = set()
    banned = set()
    for i,p in enumerate(V):
        for j in range(i+1, len(V)):
            q = V[j]
            r = tuple((-p[k]-q[k])%3 for k in range(7))
            if r==p or r==q: continue
            k3 = idx[r]
            if k3 < j: continue
            os_ = frozenset((orb[i], orb[j], orb[k3]))
            if os_ in seen: continue
            seen.add(os_)
            l = sorted(os_)
            if len(l)==1: banned.add(l[0])
            elif len(l)==2: m.add(x[l[0]] + x[l[1]] <= 1)
            else: m.add(x[l[0]] + x[l[1]] + x[l[2]] <= 2)
    for b in banned: m.add(x[b]==0)
    m.maximize(sum(x))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = tlimit
    s.parameters.num_workers = 8
    st = s.solve(m)
    cnt = int(s.objective_value)
    print(f"v={v} status={s.status_name(st)} orbits={cnt} cap size={3*cnt} bound={s.best_objective_bound}")
    if 3*cnt > 236:
        pts = [p for i,o in enumerate(orbits) if s.value(x[i]) for p in o]
        from capset_verify import is_capset
        ok,reason = is_capset(pts)
        print("VERIFY:", ok, reason, len(pts))
        if ok: json.dump({"7":[list(p) for p in pts]}, open(f"cap_n7_sym3_{len(pts)}.json","w"))
    return cnt

for v in vlist:
    run(v, 240.0)
