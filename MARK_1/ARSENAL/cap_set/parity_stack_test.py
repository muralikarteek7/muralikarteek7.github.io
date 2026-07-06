#!/usr/bin/env python3
"""Parity-stack hypothesis test: stack F_3 sum-character sigma on the CF parity core.
Wings of alpha/beta get sigma-restricted (per C5-orbit: block1, block2 each get an option
in {full, sigma=0, sigma=1, sigma=2, drop}, independently for alpha and beta);
gamma = 12 weight-1 vectors + greedy completion over odd-weight {1,2}-patterned vectors
(weights 3 and 5) that survive all cross-sum and cap constraints.
Frozen verifier is the judge."""
import itertools, sys
sys.path.insert(0, "/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set")
from capset_verify import is_capset

def expand(t):
    star=[i for i,c in enumerate(t) if c=='*']
    out=[]
    for vals in itertools.product([1,2],repeat=len(star)):
        v=[0]*6
        for p,val in zip(star,vals): v[p]=val
        out.append(tuple(v))
    return out

def block1():
    T=[]
    for i in range(5):
        t=['0']*6
        for k in range(3): t[1+(i+k)%5]='*'
        T.append(t)
    return T
def block2():
    T=[]
    for i in range(5):
        t=['0']*6; t[0]='*'
        for p in (i%5,(i+2)%5): t[1+p]='*'
        T.append(t)
    return T
def interchange(t): return ['*' if c=='0' else '0' for c in t]

D = set(v for v in itertools.product([1,2],repeat=6) if sum(x==1 for x in v)%2==0)
B1, B2 = block1(), block2()
sigma = lambda x: sum(x)%3

def wing(templates, opt):
    """opt in {'full','s0','s1','s2','drop'} applied to every template in the orbit."""
    pts=set()
    if opt=='drop': return pts
    for t in templates:
        for x in expand(t):
            if opt=='full' or sigma(x)==int(opt[1]):
                pts.add(x)
    return pts

# candidate gamma pool: odd-weight {1,2}-patterned vectors (avoid -(D+D) automatically)
W1=[tuple((x if i==j else 0) for j in range(6)) for i in range(6) for x in (1,2)]
GPOOL=[]
for w in (3,5):
    for supp in itertools.combinations(range(6),w):
        for vals in itertools.product([1,2],repeat=w):
            v=[0]*6
            for p,val in zip(supp,vals): v[p]=val
            GPOOL.append(tuple(v))
GPOOL.sort()  # deterministic lexicographic order

OPTS=['full','s0','s1','s2','drop']
best=(0,None)
for oa1,oa2,ob1,ob2 in itertools.product(OPTS,repeat=4):
    alpha = D | wing(B1,oa1) | wing(B2,oa2)
    beta  = D | wing([interchange(t) for t in B1],ob1) | wing([interchange(t) for t in B2],ob2)
    base = len(alpha)+len(beta)
    if base + 12 + 60 < best[0]:  # crude upper prune (max plausible gamma ~ 72)
        continue
    # forbidden gamma points: -(a+b) for a in alpha,b in beta
    forb=set()
    for a in alpha:
        for b in beta:
            forb.add(tuple((-(a[i]+b[i]))%3 for i in range(6)))
    gamma=set()
    for c in W1+GPOOL:
        if c in forb: continue
        # cap condition inside gamma: no a,b in gamma with -(a+b)=existing or c completes AP
        ok=True
        for a in gamma:
            t3=tuple((-(a[i]+c[i]))%3 for i in range(6))
            if t3 in gamma and t3!=a and t3!=c: ok=False; break
        if ok: gamma.add(c)
    tot=base+len(gamma)
    if tot>best[0]:
        full=[(0,)+a for a in alpha]+[(1,)+b for b in beta]+[(2,)+c for c in gamma]
        v,r=is_capset(full)
        if v:
            best=(tot,(oa1,oa2,ob1,ob2,len(alpha),len(beta),len(gamma)))
            print("VALID", tot, best[1], flush=True)
        else:
            print("invalid", tot, (oa1,oa2,ob1,ob2), r[:60], flush=True)
print("BEST:", best)
