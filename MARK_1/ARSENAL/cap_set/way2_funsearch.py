#!/usr/bin/env python3
"""WAY 2: FunSearch-style evolutionary PROGRAM search (DeepMind's actual cap-set method).
A 'program' = a priority function priority(v)->float; greedy adds points of F_3^7 in priority
order, keeping the cap property. We evolve priority functions (island GA over feature weights +
hand-seeded structured priorities from this session's insights). Best cap certified by frozen verifier.
Honest expectation: greedy-priority reached 512 at n=8 for DeepMind; n=7 (prime) is the hard case."""
import itertools, random, math, json, time
from capset_verify import is_capset
random.seed(2027)
n=7
ALL=list(itertools.product(range(3),repeat=n))
def third(a,b): return tuple((-(a[i]+b[i]))%3 for i in range(n))

# ---- feature vector for a point (the 'inputs' the evolved priority sees) ----
LIN=[tuple(random.randint(0,2) for _ in range(n)) for _ in range(4)]  # random linear functionals
def feats(v):
    w=sum(1 for x in v if x!=0)
    c0=v.count(0); c1=v.count(1); c2=v.count(2)
    s=sum(v)%3
    lf=[sum(v[i]*L[i] for i in range(n))%3 for L in LIN]
    adj=sum(1 for i in range(n-1) if v[i]==v[i+1])
    return [w,c0,c1,c2,s,lf[0],lf[1],lf[2],lf[3],adj,1.0]
NF=len(feats((0,)*n))
FEAT={v:feats(v) for v in ALL}

def greedy(score):
    order=sorted(ALL, key=lambda v:-score(v))
    S=set(); chosen=[]
    for p in order:
        if all(third(p,q) not in S for q in chosen):
            chosen.append(p); S.add(p)
    return chosen

def lin_score(weights):
    return lambda v: sum(weights[k]*FEAT[v][k] for k in range(NF))

# ---- hand-seeded structured priorities (my insights as 'programs') ----
def seed_scores():
    seeds=[]
    seeds.append(("low-weight", lambda v: -sum(1 for x in v if x!=0)))
    seeds.append(("balanced", lambda v: -abs(v.count(1)-v.count(2))))
    seeds.append(("sum0", lambda v: 0 if sum(v)%3==0 else -1))
    seeds.append(("lexish", lambda v: -sum(v[i]*(3**i) for i in range(n))))
    seeds.append(("quad", lambda v: -sum((v[i]*v[j]) for i in range(n) for j in range(i+1,n))%3))
    return seeds

if __name__=="__main__":
    t0=time.time(); BUDGET=420
    best=(0,None,None)
    # evaluate hand seeds
    for name,sc in seed_scores():
        c=greedy(sc); 
        if len(c)>best[0]: best=(len(c),name,c)
    print(f"hand-seeded best: {best[0]} ({best[1]})")
    # island GA over linear-feature weights
    ISLANDS=4; POP=12
    islands=[[ [random.uniform(-2,2) for _ in range(NF)] for _ in range(POP)] for _ in range(ISLANDS)]
    scores=[[len(greedy(lin_score(w))) for w in isl] for isl in islands]
    gen=0
    while time.time()-t0<BUDGET:
        gen+=1
        for a in range(ISLANDS):
            # tournament select parent, mutate
            i,j=random.sample(range(POP),2)
            parent=islands[a][i] if scores[a][i]>=scores[a][j] else islands[a][j]
            child=[x+random.gauss(0,0.6) if random.random()<0.4 else x for x in parent]
            sc=len(greedy(lin_score(child)))
            worst=min(range(POP),key=lambda k:scores[a][k])
            if sc>=scores[a][worst]:
                islands[a][worst]=child; scores[a][worst]=sc
            if sc>best[0]:
                best=(sc,f"GA-gen{gen}-isl{a}",greedy(lin_score(child)))
                print(f"  [gen {gen}] NEW BEST {sc} (island {a}, t={time.time()-t0:.0f}s)")
        if gen%50==0:  # migration
            for a in range(ISLANDS):
                b=(a+1)%ISLANDS; bi=max(range(POP),key=lambda k:scores[a][k])
                wj=min(range(POP),key=lambda k:scores[b][k])
                islands[b][wj]=islands[a][bi][:]; scores[b][wj]=scores[a][bi]
    print(f"\nFunSearch finished {gen} generations. BEST cap size = {best[0]} (method: {best[1]})")
    v,r=is_capset(best[2]); print(f"CERTIFY (frozen verifier): valid={v} ({r}) size={len(set(best[2]))}")
    print(f"  vs product 224 / record 236 -> {'BEATS 224!' if best[0]>224 else 'did not beat the structured product 224 (honest)'}")
    if v and best[0]>224:
        json.dump({"7":[list(p) for p in best[2]]},open(f"cap_n7_size{best[0]}_funsearch.json","w")); print("  persisted")
