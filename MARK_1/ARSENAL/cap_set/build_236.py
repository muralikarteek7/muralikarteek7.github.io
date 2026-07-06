#!/usr/bin/env python3
"""Calderbank-Fishburn (1994) f(7)>=236 construction, transcribed from the paper (Fig.3, p.208),
placed by the PI. Slice the 1st coord: (0,a) a in alpha(112); (1,b) b in beta(112); (2,c) c in gamma(12).
alpha = block1 (col1=0, cols2-6 three-consecutive-stars) U block2 (col1=*, cols2-6 distance-2 pairs) U delta.
beta  = alpha with 0<->* interchanged above delta (delta unchanged). gamma = 12 weight-1 vectors.
Every '*' ranges over {1,2}. CERTIFIED by the frozen capset_verify (independent, re-run from scratch)."""
import itertools, json
from capset_verify import is_capset, KNOWN_LB

def expand(t):
    star=[i for i,c in enumerate(t) if c=='*']
    out=[]
    for vals in itertools.product([1,2],repeat=len(star)):
        v=[0]*6
        for p,val in zip(star,vals): v[p]=val
        out.append(tuple(v))
    return out

def block1():  # col1=0 (index0); cols2-6 (idx1..5) three cyclically-consecutive stars
    T=[]
    for i in range(5):
        t=['0']*6
        for k in range(3): t[1+(i+k)%5]='*'
        T.append(t)
    return T
def block2():  # col1=* ; cols2-6 stars at {i, i+2 mod 5}
    T=[]
    for i in range(5):
        t=['0']*6; t[0]='*'
        for p in (i%5,(i+2)%5): t[1+p]='*'
        T.append(t)
    return T
def delta():   # all 6 cols in {1,2}, even number of 1s
    return [v for v in itertools.product([1,2],repeat=6) if sum(x==1 for x in v)%2==0]
def interchange(t): return ['*' if c=='0' else '0' for c in t]

upper=block1()+block2()
D=set(delta())
alpha=set(); 
for t in upper: alpha|=set(expand(t))
alpha|=D
beta=set()
for t in upper: beta|=set(expand(interchange(t)))
beta|=D
gamma=set((0,)*i+(x,)+(0,)*(5-i) for i in range(6) for x in (1,2))

print(f"|alpha|={len(alpha)} |beta|={len(beta)} |gamma|={len(gamma)} |delta|={len(D)}")
print(f"alpha∩beta==delta ? {alpha&beta==D}    gamma∩(alpha∪beta)==∅ ? {len(gamma&(alpha|beta))==0}")

full=[(0,)+a for a in alpha]+[(1,)+b for b in beta]+[(2,)+c for c in gamma]
v,r=is_capset(full)
print(f"TOTAL={len(full)}  valid={v} ({r})  vs KNOWN_LB[7]={KNOWN_LB[7]}")
if v and len(full)>=236:
    json.dump({"7":[list(p) for p in full]}, open("cap_n7_size236_CF.json","w"))
    print(f"  >>> VERIFIED {len(full)}-cap in F_3^7 persisted (cap_n7_size236_CF.json) — reproduces Calderbank-Fishburn <<<")
elif not v:
    print("  INVALID — parse needs fixing (verifier caught it). Reason:", r)
