#!/usr/bin/env python3
"""Ablate the C-F 236 construction: which structural CHOICES are load-bearing?
This exposes 'the original idea' as a small set of specific decisions a de-novo engine would
have to discover. Each variant certified by the frozen verifier (no self-report trusted)."""
import itertools, random
from capset_verify import is_capset
random.seed(1)
def expand(t):
    star=[i for i,c in enumerate(t) if c=='*']; out=[]
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
ALL6=list(itertools.product(range(3),repeat=6))

def assemble(alpha,beta,gamma):
    full=[(0,)+a for a in alpha]+[(1,)+b for b in beta]+[(2,)+c for c in gamma]
    v,r=is_capset(full); return len(full),v,r

upper=block1()+block2()
delta_even=set(v for v in itertools.product([1,2],repeat=6) if sum(x==1 for x in v)%2==0)
gamma_w1=set((0,)*i+(x,)+(0,)*(5-i) for i in range(6) for x in (1,2))
def mk_alpha(D):
    a=set();  [a.update(expand(t)) for t in upper]; a|=D; return a
def mk_beta(D):
    b=set();  [b.update(expand(interchange(t))) for t in upper]; b|=D; return b

print("ABLATION — does the 236 cap survive each change? (size, valid)")
# 0) baseline
a,b=mk_alpha(delta_even),mk_beta(delta_even)
print(" 0 baseline (C-F exact)                :", assemble(a,b,gamma_w1))
# 1) swap delta(even-parity core) -> random 32-set of all-nonzero vectors
allnz=[v for v in itertools.product([1,2],repeat=6)]
Drand=set(random.sample(allnz,32))
print(" 1 delta -> random 32 all-nonzero set  :", assemble(mk_alpha(Drand),mk_beta(Drand),gamma_w1))
# 2) swap delta -> odd-parity class (the 'other' canonical core)
Dodd=set(v for v in allnz if sum(x==1 for x in v)%2==1)
print(" 2 delta -> ODD-parity core (32)       :", assemble(mk_alpha(Dodd),mk_beta(Dodd),gamma_w1))
# 3) gamma (weight-1) -> random 12 vectors
grand=set(random.sample([v for v in ALL6 if v not in a and v not in b],12))
print(" 3 gamma -> random 12-set              :", assemble(a,b,grand))
# 4) NO swap: beta = alpha (the 'natural/symmetric' choice I kept trying)
print(" 4 beta = alpha (no 0<->* swap)        :", assemble(a,a,gamma_w1))
# 5) random non-affine 'swap' on the templates (permute which positions flip)
def rand_flip(t):
    import random as R; return [('*' if c=='0' else '0') if R.random()<0.5 else c for c in t]
brand=set(); [brand.update(expand(rand_flip(t))) for t in upper]; brand|=delta_even
print(" 5 beta = alpha+RANDOM flips (not the swap):", assemble(a,brand,gamma_w1))
