#!/usr/bin/env python3
"""W-EVOLVE x W-LIFT (first real OFFENSE build, 2026-06-10).
Theory (THEORY.md): n=7 is rho-dominant -> TWIST the naive product. The naive product
S0=S1=112cap forces S2=empty -> 224 (proven in N7_PLATEAU). Lever: evolve THREE mutually
transversal-free caps S0,S1,S2 in F_3^6 whose total beats 224. Every candidate is scored
by a fast greedy cap-builder; the FINAL best is certified by the frozen capset_verify.py.

Honest expectation (per audit + survey): no AI has beaten the n=7 affine bound; reaching
Edel's 236 needs his specific admissible structure. This is a genuine attempt + an honest
measured number for evolutionary twisting, NOT a promised record.
"""
import json, itertools, random
from capset_verify import is_capset

random.seed(12345)  # fixed seed (Date/random banned in some envs; reproducible)
ALL6 = list(itertools.product(range(3), repeat=6))
IDX = {p:i for i,p in enumerate(ALL6)}
cap112 = [tuple(p) for p in json.load(open('cap_n6_size112.json'))['6']]

def neg(p): return tuple((-x)%3 for x in p)
def add(p,q): return tuple((p[i]+q[i])%3 for i in range(6))

# precompute the unique third point of every pair (for fast cap maintenance)
def third(a,b): return tuple((-(a[i]+b[i]))%3 for i in range(6))

def greedy_cap(cands, order):
    """Largest cap we can greedily pull from `cands` (a set) following `order`."""
    chosen=[]; cs=set()
    for p in order:
        if p not in cands: continue
        ok=True
        for q in chosen:
            t=third(p,q)
            if t in cs:  # p,q,t would be a line (t already chosen)
                ok=False; break
        if ok:
            chosen.append(p); cs.add(p)
    return chosen

def total_for(S0, S1, order2):
    """Given caps S0,S1, build best S2 avoiding transversals, return total + parts."""
    s0=set(S0); s1=set(S1)
    forbidden=set(neg(add(a,b)) for a in s0 for b in s1)
    cand2=set(p for p in ALL6 if p not in forbidden)
    S2=greedy_cap(cand2, order2)
    return len(S0)+len(S1)+len(S2), S2

def random_cap_near(base, k_remove, k_add_order):
    """Perturb a cap: drop k random points, then greedily re-fill (keeps cap property)."""
    s=set(base)
    for _ in range(k_remove):
        if s: s.discard(random.choice(list(s)))
    # greedily try to re-add points in random order (stay a cap)
    order=list(ALL6); random.shuffle(order)
    chosen=list(s)
    for p in order:
        if p in s: continue
        ok=all(third(p,q) not in s for q in chosen)
        if ok: chosen.append(p); s.add(p)
    return chosen

best_total=224; best=None
rounds=4000
order2_base=list(ALL6)
for it in range(rounds):
    # ISLAND of strategies for the twist:
    r=random.random()
    if r<0.34:
        S0=cap112; S1=[neg(p) for p in cap112]                 # negation twist
    elif r<0.67:
        S0=random_cap_near(cap112, random.randint(2,40), None) # perturb S0
        S1=random_cap_near(cap112, random.randint(2,40), None) # perturb S1 independently
    else:
        S0=random_cap_near(cap112, random.randint(20,70), None)
        S1=list(S0)                                            # symmetric but shrunk
    order2=list(ALL6); random.shuffle(order2)
    tot,S2=total_for(S0,S1,order2)
    if tot>best_total:
        best_total=tot; best=(list(S0),list(S1),list(S2))
        print(f"  [it {it}] NEW BEST total={tot}  (|S0|={len(S0)} |S1|={len(S1)} |S2|={len(S2)})")
print(f"\nW-EVOLVE finished {rounds} candidates. best_total={best_total} (baseline 224, known LB 236)")
if best and best_total>224:
    S0,S1,S2=best
    full=[p+(0,) for p in S0]+[p+(1,) for p in S1]+[p+(2,) for p in S2]
    v,reason=is_capset(full)   # FROZEN independent verifier, from scratch
    print(f"CERTIFY via capset_verify: valid={v} ({reason}) size={len(full)}")
    if v and len(full)>224:
        json.dump({"7":[list(p) for p in full]}, open(f"cap_n7_size{len(full)}_evolve.json","w"))
        print(f"  persisted cap_n7_size{len(full)}_evolve.json  (still < 236 = reproduction territory, NOT a record)")
else:
    print("No candidate beat 224. Honest negative: evolutionary twisting did not exceed the product cap.")
