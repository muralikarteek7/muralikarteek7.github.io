import json, itertools
from capset_verify import is_capset

cap = [tuple(p) for p in json.load(open('cap_n7_size224.json'))['7']]
n = 7
S = set(cap)
ALL = list(itertools.product(range(3), repeat=n))

def addable(S, p):
    # p addable iff for no pair (a,b) in S does a+b+p=0, i.e. p != -(a+b) for a,b in S, a!=b
    # equivalently: the point -(a+b) for distinct a,b; if p equals any such -> not addable
    # faster: for each a in S, b = -(p+a); if b in S and b!=a and b!=p -> violation
    for a in S:
        b = tuple((-(p[i]+a[i]))%3 for i in range(n))
        if b in S and b != a and b != p:
            return False
    return True

# greedy extension over remaining points
cands = [p for p in ALL if p not in S]
added = []
for p in cands:
    if addable(S, p):
        S.add(p); added.append(p)
print("added by greedy:", len(added), "-> total", len(S))
v,r = is_capset(list(S))
print("valid:", v, r, "size", len(S))
