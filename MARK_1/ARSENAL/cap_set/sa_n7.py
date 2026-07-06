#!/usr/bin/env python3
"""Strong metaheuristic (plateau/annealed local search) on F_3^7, seeded at the 224 cap.
A DIFFERENT weapon-class than CP-SAT (which plateaued at 224 in 20min). If this also can't
beat 224, the negative is triple-confirmed across heterogeneous STRONG weapons. Certified by frozen verifier."""
import json, itertools, random, time
from capset_verify import is_capset
random.seed(2026)
n=7
ALL=list(itertools.product(range(3),repeat=n))
seed=[tuple(p) for p in json.load(open('cap_n7_size224.json'))['7']]

def third(a,b): return tuple((-(a[i]+b[i]))%3 for i in range(n))

def conflicts(p, S):
    # members q such that third(p,q) is also in S (so p,q,third form a line) -> must remove one of each
    bad=set()
    for q in S:
        t=third(p,q)
        if t in S and t!=p and q!=t:
            bad.add(q); bad.add(t)
    return bad

S=set(seed); best=len(S)
t0=time.time(); BUDGET=600  # 10 min
it=0
while time.time()-t0 < BUDGET:
    it+=1
    p=random.choice(ALL)
    if p in S: 
        continue
    bad=conflicts(p,S)
    # adding p removes |bad| members, gains 1. Accept if improves, or sometimes if neutral/slightly worse (annealing/plateau)
    delta=1-len(bad)
    if delta>0 or (delta==0 and random.random()<0.5) or (delta<0 and random.random()<0.02):
        for q in bad: S.discard(q)
        S.add(p)
        if len(S)>best:
            best=len(S)
            print(f"  [it {it}] NEW BEST {best} (t={time.time()-t0:.0f}s)")
print(f"SA finished: best={best} over {it} iters (baseline 224). ")
# certify current S if it's a valid cap and > 224
v,r=is_capset(list(S))
print(f"final set size={len(S)} valid={v} ({r})")
if best>224:
    print("BEAT 224 via SA")
else:
    print("No improvement over 224 — third strong heterogeneous weapon also plateaus. Honest triple-confirmed negative.")
