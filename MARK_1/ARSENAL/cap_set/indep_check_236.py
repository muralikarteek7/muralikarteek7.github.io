#!/usr/bin/env python3
"""INDEPENDENT re-verification of the persisted 236-cap — fresh code, NOT importing capset_verify.
Checks: 236 distinct points, all in {0,1,2}^7, and NO three distinct points sum to 0 mod 3."""
import json, itertools
pts=[tuple(p) for p in json.load(open("cap_n7_size236_CF.json"))["7"]]
S=set(pts)
assert len(S)==len(pts), "duplicates!"
assert all(len(p)==7 and all(c in (0,1,2) for c in p) for p in pts), "bad entries!"
n=len(pts)
# independent triple check via the pair->third method, fresh implementation
bad=0
for a,b in itertools.combinations(pts,2):
    c=tuple((3-(a[i]+b[i])%3)%3 for i in range(7))   # the unique c with a+b+c=0 mod 3
    if c in S and c!=a and c!=b:
        bad+=1
print(f"points={n}  distinct={len(S)}  all_valid_entries=True")
print(f"forbidden triples (3 distinct summing to 0 mod3) found: {bad}")
print("INDEPENDENT VERDICT:", "VALID 236-cap ✓" if (bad==0 and n==236) else "INVALID ✗")
