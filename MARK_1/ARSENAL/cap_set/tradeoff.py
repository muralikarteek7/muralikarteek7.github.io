import json, itertools, random
C=[tuple(p) for p in json.load(open('cap_n6_size112.json'))['6']]
ALL6=list(itertools.product(range(3),repeat=6)); sC=set(C)
def neg(p): return tuple((-x)%3 for x in p)
def add(p,q): return tuple((p[i]+q[i])%3 for i in range(6))
random.seed(0)
# S1=C fixed. S0 = C minus k points. free_for_S2 = points not forbidden = upper bound on |S2|.
# total_ub = |S0| + |S1| + free  = (112-k) + 112 + free. Beat 224 iff free > k.
print("k  |S0| free_for_S2  total_UB(=224-k+free)  best_over_trials")
for k in [0,5,10,20,30,40,60]:
    best=-1
    for trial in range(8):
        rem=set(random.sample(C,k)) if k>0 else set()
        S0=[p for p in C if p not in rem]
        forb=set(neg(add(a,b)) for a in S0 for b in C)
        free=729-len(forb)
        best=max(best, free-k)  # net gain over 224
    print(f"{k:3d} {112-k:4d}  ~{free:4d}        {224-k+free:4d}            net_best={best:+d}")
