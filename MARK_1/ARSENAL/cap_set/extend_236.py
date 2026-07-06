#!/usr/bin/env python3
"""Try something more: is the verified 236 cap EXTENDABLE? (236 is a LOWER bound; the true max is open, <=288.)
If any single point can be added keeping the cap property -> 237 > the known record. Frozen-verifier gated."""
import json, itertools
from capset_verify import is_capset
cap=[tuple(p) for p in json.load(open('cap_n7_size236_CF.json'))['7']]
n=7; S=set(cap)
assert is_capset(cap)[0], "seed 236 not valid!"
print(f"seed: {len(cap)} valid cap. Trying to extend over all {3**n} points...")
def addable(p):
    for q in S:
        t=tuple((-(p[i]+q[i]))%3 for i in range(n))
        if t in S and t!=q and t!=p: return False
    return True
ALL=list(itertools.product(range(3),repeat=n))
added=[]
S2=set(S)
for p in ALL:
    if p in S2: continue
    # check against current S2 (greedy growth)
    ok=True
    for q in S2:
        t=tuple((-(p[i]+q[i]))%3 for i in range(n))
        if t in S2 and t!=q and t!=p: ok=False; break
    if ok: S2.add(p); added.append(p)
print(f"greedy points added: {len(added)} -> total {len(S2)}")
v,r=is_capset(list(S2))
print(f"certify extended set: valid={v} ({r}) size={len(S2)}")
if v and len(S2)>236:
    json.dump({"7":[list(x) for x in S2]}, open(f"cap_n7_size{len(S2)}_EXTENDED.json","w"))
    print(f"  >>> {len(S2)} > 236 !! persisted — MUST be independently audited before ANY claim <<<")
else:
    print(f"  236 is MAXIMAL under point-extension (added {len(added)}). Honest negative — expected.")
