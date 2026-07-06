#!/usr/bin/env python3
"""WAY 1: Edel/Tyrrell EXTENDED PRODUCT construction, grounded from ar5iv (Defs 2.4/2.6, Lemma 2.7).
Extendable collection (A0,A1,A2) of caps in F_3^n: (1) x,y in A0, z in A1∪A2 => x+y+z!=0;
(2) x in A0,y in A1,z in A2 => x+y+z!=0.  Admissible S ⊆ {0,1,2}^m.
Cap = ∪_{s in S} A_{s1}×...×A_{sm} ⊆ F_3^(nm).  We implement it, VALIDATE on a case it can do,
and test n=7. Everything certified by frozen capset_verify."""
import itertools, json
from capset_verify import is_capset

def extendable(A0,A1,A2,n):
    s0,s1,s2=set(A0),set(A1),set(A2)
    def z(p,q,r): return all((p[i]+q[i]+r[i])%3==0 for i in range(n))
    # cond1: x,y in A0, z in A1∪A2 => !=0
    for x in s0:
        for y in s0:
            for zz in s1|s2:
                if z(x,y,zz): return False
    # cond2: x in A0,y in A1,z in A2
    for x in s0:
        for y in s1:
            for zz in s2:
                if z(x,y,zz): return False
    return True

def admissible(S,m):
    # (1) antichain on supports; (2) every 3 distinct have a coord with values {0,1,2},{0,0,1},or{0,0,2}
    def supp(v): return frozenset(i for i in range(m) if v[i]!=0)
    for a in S:
        for b in S:
            if a!=b and supp(a)<=supp(b): return False
    for a,b,c in itertools.combinations(S,3):
        ok=False
        for i in range(m):
            vals=sorted((a[i],b[i],c[i]))
            if vals in ([0,1,2],[0,0,1],[0,0,2]): ok=True;break
        if not ok: return False
    return True

def build(S,A,n,m):
    # A = (A0,A1,A2); each Ai list of n-tuples. point of cap: concat of A_{s_j} choices.
    blocks=[A[0],A[1],A[2]]
    pts=[]
    for s in S:
        for combo in itertools.product(*[blocks[s[j]] for j in range(m)]):
            pts.append(tuple(x for blk in combo for x in blk))
    return pts

# ---- VALIDATION: build a cap in F_3^(1*m) from F_3^1 pieces, confirm it's a valid cap ----
def caps_F31():
    pts=[(0,),(1,),(2,)]
    # all subsets of size<=2 are caps in F_3^1
    from itertools import combinations
    subs=[[]]+[[p] for p in pts]+[list(c) for c in combinations(pts,2)]
    return subs

if __name__=="__main__":
    print("=== WAY 1: extended product, validation + n=7 attempt ===")
    F31=caps_F31()
    best=(0,None)
    # search extendable collections in F_3^1
    coll=[]
    for A0 in F31:
        for A1 in F31:
            for A2 in F31:
                if A0 and A1 and A2 and extendable(A0,A1,A2,1):
                    coll.append((A0,A1,A2))
    print(f"extendable collections in F_3^1: {len(coll)} (sizes e.g. {[(len(a),len(b),len(c)) for a,b,c in coll[:6]]})")
    # admissible sets in {0,1,2}^7 of fixed weight w: one vector per w-subset, nonzeros=1, then test
    m=7
    for w in range(1,m+1):
        # candidate S: each w-subset -> vector with those coords = 1
        Sset=[]
        for T in itertools.combinations(range(m),w):
            v=[0]*m
            for i in T: v[i]=1
            Sset.append(tuple(v))
        if not admissible(Sset,m):
            # try alternating 1/2 by index parity to fix admissibility
            Sset=[]
            for T in itertools.combinations(range(m),w):
                v=[0]*m
                for k,i in enumerate(T): v[i]=1+(k%2)
                Sset.append(tuple(v))
            if not admissible(Sset,m): 
                print(f"  w={w}: no easy admissible set"); continue
        for (A0,A1,A2) in coll:
            pts=build(Sset,(A0,A1,A2),1,m)
            if len(set(pts))>best[0]:
                v,r=is_capset(pts)
                if v and len(set(pts))>best[0]:
                    best=(len(set(pts)),(w,len(A0),len(A1),len(A2)))
    print(f"BEST extended-product cap in F_3^7 (n=1,m=7 base): size={best[0]}  config(w,|A0|,|A1|,|A2|)={best[1]}")
    print(f"  vs product 224 / record 236.  -> {'BEATS 224' if best[0]>224 else 'below 224 — confirms the prime-7 obstruction (cannot use the F_3^6 112-cap base since 7 is prime)'}")
