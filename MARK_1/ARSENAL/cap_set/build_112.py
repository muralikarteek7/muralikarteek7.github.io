import sys, itertools, json
sys.path.insert(0, "/Users/varunesh/Desktop/AI_agents/Next/benchmarks/math")
from verified_caps_45_90 import construct_45
from capset_verify import is_capset, score

A = [tuple(p) for p in construct_45()]   # 45-cap in F_3^5
Aset = set(A)
ALLV = list(itertools.product(range(3), repeat=5))

def add(u, v): return tuple((u[i]+v[i]) % 3 for i in range(5))
def neg(u): return tuple((-u[i]) % 3 for i in range(5))

def is_cap5(pts):
    S = set(pts)
    for a, b in itertools.combinations(pts, 2):
        c = tuple((-(a[k]+b[k])) % 3 for k in range(5))
        if c != a and c != b and c in S:
            return False
    return True

def try_c(c):
    # slice1 = -c - A  (affine image of A, automatically a cap)
    slice0 = A
    slice1 = [add(neg(c), neg(p)) for p in A]
    s1set = set(slice1)
    if len(s1set) != 45:
        return None
    # forbidden a2: a2 = -(a0+a1) for a0 in slice0, a1 in slice1
    forbidden = set()
    for a0 in slice0:
        for a1 in slice1:
            forbidden.add(neg(add(a0, a1)))
    cand = [v for v in ALLV if v not in forbidden]
    return slice0, slice1, cand

def max_slice2(cand):
    # cand must form a cap among themselves (condition i). Find max cap subset.
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    x = {v: m.NewBoolVar(str(v)) for v in cand}
    cset = set(cand)
    seen = set()
    for a in cand:
        for b in cand:
            if a >= b: continue
            cc = tuple((-(a[k]+b[k])) % 3 for k in range(5))
            if cc in cset and cc != a and cc != b:
                key = tuple(sorted([a,b,cc]))
                if key in seen: continue
                seen.add(key)
                m.Add(x[a] + x[b] + x[cc] <= 2)
    m.Maximize(sum(x.values()))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    solver.parameters.num_search_workers = 8
    st = solver.Solve(m)
    chosen = [v for v in cand if solver.Value(x[v]) == 1]
    return chosen

best = (0, None)
for c in ALLV:
    r = try_c(c)
    if r is None: continue
    slice0, slice1, cand = r
    # quick upper bound: need cand >= 22 to be worth solving
    if len(cand) < 22:
        ub = len(cand)
        if ub <= best[0]: continue
    s2 = max_slice2(cand)
    if len(s2) > best[0]:
        best = (len(s2), (c, slice0, slice1, s2))
        print("c=", c, "cand=", len(cand), "slice2=", len(s2), "total=", 90+len(s2), flush=True)
        if len(s2) >= 22:
            break

sz, data = best
print("BEST slice2 size:", sz, "total:", 90+sz)
if data:
    c, slice0, slice1, s2 = data
    pts = [tuple(p)+(0,) for p in slice0] + [tuple(p)+(1,) for p in slice1] + [tuple(p)+(2,) for p in s2]
    print("Verifier:", score(pts, 6))
    json.dump({"6": [list(p) for p in pts]}, open("/Users/varunesh/Desktop/AI_agents/Next/benchmarks/math/cap_n6_size112.json","w"))
    print("len pts:", len(pts), "unique:", len(set(pts)))
