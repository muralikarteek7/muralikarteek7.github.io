"""Joint 3-slice CP-SAT for n=7, warm-started from the 224 product solution.
Variables: x[s][p] for slice s in {0,1,2}, p in F_3^6. Constraints:
 (1) each slice a cap: no 3 distinct collinear within a slice.
 (2) no transversal: a in S0, b in S1, c in S2 with a+b+c=0.
Maximize total. Warm start: S0=S1=C(112), S2=empty (=224).
"""
import json, itertools, time
from ortools.sat.python import cp_model
from capset_verify import is_capset

C = [tuple(p) for p in json.load(open('cap_n6_size112.json'))['6']]
ALL6 = list(itertools.product(range(3), repeat=6))
idx = {p:i for i,p in enumerate(ALL6)}
N = len(ALL6)  # 729

m = cp_model.CpModel()
x = [[m.NewBoolVar(f"x{s}_{i}") for i in range(N)] for s in range(3)]

# within-slice cap constraints: for each unordered collinear triple {i,j,k} (i+j+k=0, distinct), sum<=2
triples = set()
for i in range(N):
    for j in range(i+1, N):
        c = tuple((-(ALL6[i][t]+ALL6[j][t]))%3 for t in range(6))
        k = idx[c]
        if k!=i and k!=j:
            triples.add(frozenset((i,j,k)))
print(f"within-slice triples: {len(triples)}")
for s in range(3):
    for t in triples:
        m.Add(sum(x[s][i] for i in t) <= 2)

# transversal constraints: a+b+c=0, a in S0,b in S1,c in S2. For each (i,j) the k is forced.
# count: 729*729 but k determined -> add x0[i]+x1[j]+x2[k] <= 2
tcount=0
for i in range(N):
    ai=ALL6[i]
    for j in range(N):
        bj=ALL6[j]
        c = tuple((-(ai[t]+bj[t]))%3 for t in range(6))
        k = idx[c]
        m.Add(x[0][i]+x[1][j]+x[2][k] <= 2)
        tcount+=1
print(f"transversal constraints: {tcount}")

m.Maximize(sum(x[s][i] for s in range(3) for i in range(N)))

# warm start: S0=S1=C, S2=empty
sC=set(C)
for s in range(3):
    for i in range(N):
        want = 1 if (s in (0,1) and ALL6[i] in sC) else 0
        m.AddHint(x[s][i], want)

solver=cp_model.CpSolver()
solver.parameters.max_time_in_seconds=240
solver.parameters.num_search_workers=8
t0=time.time()
res=solver.Solve(m)
print(f"status={solver.StatusName(res)} obj={solver.ObjectiveValue()} best_bound={solver.BestObjectiveBound()} t={time.time()-t0:.0f}s")
# extract
S=[[ALL6[i] for i in range(N) if solver.Value(x[s][i])==1] for s in range(3)]
full=[p+(0,) for p in S[0]]+[p+(1,) for p in S[1]]+[p+(2,) for p in S[2]]
v,r=is_capset(full)
print(f"|S0|={len(S[0])} |S1|={len(S[1])} |S2|={len(S[2])} TOTAL={len(full)} valid={v} ({r})")
if v and len(full)>224:
    json.dump({"7":[list(p) for p in full]}, open(f"cap_n7_size{len(full)}_jointopt.json","w"))
    print("BEAT 224 -> persisted")
