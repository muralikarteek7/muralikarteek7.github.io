import json, itertools
from capset_verify import is_capset
cap6 = [tuple(p) for p in json.load(open('cap_n6_size112.json'))['6']]
ALL6 = list(itertools.product(range(3), repeat=6))
def neg(p): return tuple((-x)%3 for x in p)
def add(p,q): return tuple((p[i]+q[i])%3 for i in range(6))
def addv(p,v): return tuple((p[i]+v[i])%3 for i in range(6))

C = cap6; sC=set(C)
# how much does S0=S1=C forbid?
forb = set(neg(add(a,b)) for a in C for b in C)
print(f"S0=S1=C(112): |forbidden|={len(forb)} of 729, free={729-len(forb)}")

# try translating S1 by v: S1 = C+v
best=None
import random
for v in ALL6:
    s1 = [addv(p,v) for p in C]
    forb = set(neg(add(a,b)) for a in C for b in s1)
    free = 729-len(forb)
    if best is None or free>best[1]:
        best=(v,free)
print(f"best translate of S1: v={best[0]} free_for_S2={best[1]}  (>0 means room beyond 224)")
