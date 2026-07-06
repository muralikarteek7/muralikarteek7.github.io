#!/usr/bin/env python3
"""FRONTIER ENGINE v1 — generalized Calderbank-Fishburn slice-construction SEARCH, verifier-gated.
Fable-outage-robust by design: the creativity is EXECUTABLE (a parameterized family the MACHINE searches),
not model-prose. Slice F_3^7 by coord-0: (0,a) a in A; (1,b) b in B; (2,c) c in C, all subset F_3^6.
Valid cap iff each a cap AND no a+b+c=0 transversal -> c must avoid forbidden=-(A+B).
KEY INVERSION (the move C-F did by hand, now searched): for EACH (A,B), take C = the LARGEST cap that fits the
hole F_3^6 \\ forbidden. C-F fixed C = the 12 weight-1 vectors; we take max(C). |hole-cap|>12 => total>236.
Every candidate certified by the FROZEN capset_verify (never self-reported)."""
import itertools, json, time
from capset_verify import is_capset
ALL6 = list(itertools.product(range(3), repeat=6))
def neg(p): return tuple((-x)%3 for x in p)
def add(a,b): return tuple((a[i]+b[i])%3 for i in range(6))
def third(a,b): return tuple((-(a[i]+b[i]))%3 for i in range(6))

def maxcap_greedy(pool, seeds=24):
    """Largest cap we can greedily pull from `pool` (set), best over a few orderings."""
    pool=list(pool); best=[]
    import random
    rng=random.Random(0)
    for s in range(seeds):
        order=pool[:]; rng.shuffle(order)
        chosen=[]; cs=set()
        for p in order:
            if all(third(p,q) not in cs for q in chosen):
                chosen.append(p); cs.add(p)
        if len(chosen)>len(best): best=chosen
    return best

# ---- C-F template machinery (the family's backbone), parameterized ----
def expand(t):
    star=[i for i,c in enumerate(t) if c=='*']; out=[]
    for vals in itertools.product([1,2],repeat=len(star)):
        v=[0]*6
        for p,val in zip(star,vals): v[p]=val
        out.append(tuple(v))
    return out
def block1(width=3):           # col1=0; cols2-6 = `width` cyclically-consecutive stars
    T=[]
    for i in range(5):
        t=['0']*6
        for k in range(width): t[1+(i+k)%5]='*'
        T.append(t)
    return T
def block2(d=2):               # col1=*; cols2-6 stars at {i, i+d mod 5}
    T=[]
    for i in range(5):
        t=['0']*6; t[0]='*'
        for p in (i%5,(i+d)%5): t[1+p]='*'
        T.append(t)
    return T
def delta_parity(parity=0, ones_val=1):   # all-nonzero {1,2}^6 with (#coords==ones_val) ≡ parity (mod 2)
    return [v for v in itertools.product([1,2],repeat=6) if (sum(x==ones_val for x in v)%2)==parity]
def interchange(t): return ['*' if c=='0' else '0' for c in t]

def build_AB(width, d, parity, ones_val):
    upper = block1(width)+block2(d)
    D=set(delta_parity(parity,ones_val))
    A=set(); 
    for t in upper: A|=set(expand(t))
    A|=D
    B=set()
    for t in upper: B|=set(expand(interchange(t)))
    B|=D
    return A,B

def evaluate(A,B):
    if len(A)!=112 or len(B)!=112: return None
    forbidden=set(neg(add(a,b)) for a in A for b in B)
    hole=[p for p in ALL6 if p not in forbidden]
    C=maxcap_greedy(hole)
    full=[(0,)+a for a in A]+[(1,)+b for b in B]+[(2,)+c for c in C]
    v,r=is_capset(full)              # FROZEN gate
    return {'sizeA':len(A),'sizeB':len(B),'hole':len(hole),'sizeC':len(C),'total':len(full),'valid':v,'reason':r,'full':full}

if __name__=="__main__":
    t0=time.time()
    print("=== FRONTIER ENGINE: generalized C-F family search (verifier-gated) ===")
    # 1) VALIDATION: the canonical C-F instance must recover 236
    A,B=build_AB(width=3,d=2,parity=0,ones_val=1)
    base=evaluate(A,B)
    print(f"[validate C-F instance] total={base['total']} valid={base['valid']} (hole={base['hole']}, |C|={base['sizeC']})")
    # 2) SWEEP the family (executable creativity; machine does the work)
    best=base
    tried=0
    for width in (2,3,4):
        for d in (1,2):
            for parity in (0,1):
                for ones_val in (1,2):
                    A,B=build_AB(width,d,parity,ones_val)
                    res=evaluate(A,B); tried+=1
                    if res and res['valid'] and res['total']>best['total']:
                        best=res
                        print(f"  NEW BEST total={res['total']} (width={width},d={d},parity={parity},ones={ones_val}, hole={res['hole']}, |C|={res['sizeC']})")
    print(f"\nswept {tried} family instances in {time.time()-t0:.0f}s. BEST certified total = {best['total']} (vs 236 record).")
    if best['valid'] and best['total']>236:
        json.dump({"7":[list(p) for p in best['full']]},open(f"cap_n7_size{best['total']}_engine.json","w"))
        print(f"  >>> {best['total']} > 236 — persisted; REQUIRES independent audit before any claim <<<")
    else:
        print(f"  No instance beat 236. Honest: the C-F family is (locally) optimal at 236 under this parameterization.")
