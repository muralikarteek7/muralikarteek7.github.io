#!/usr/bin/env python3
"""Cap set verifier — the machine-checked ground truth for the MATH EFFICIENT arena.

A cap set in (Z/3)^n is a set of points with NO three distinct points a,b,c
such that a+b+c ≡ 0 (mod 3) (equivalently, no 3-term arithmetic progression /
no 3 collinear points). This is the Erdős-adjacent extremal problem DeepMind's
FunSearch made progress on. Every box-proposed construction is checked here —
no claim is trusted unless this script returns valid=True.

Known maximum cap set sizes (literature):
  n: 0  1  2  3   4   5    6     (all proven optimal)
     1  2  4  9   20  45   112
  n=7: exact max OPEN; best known lower bound 236 (Calderbank–Fishburn / Edel).
  n=8: best known lower bound 496 → 512 (FunSearch, 2023).
"""
import sys, json, itertools

KNOWN_MAX = {0:1, 1:2, 2:4, 3:9, 4:20, 5:45, 6:112}      # proven optimal
KNOWN_LB  = {7:236, 8:512}                                # best known lower bounds (open)

def is_capset(points):
    """Return (valid, reason). points: iterable of n-tuples with entries in {0,1,2}."""
    pts = [tuple(p) for p in points]
    if not pts:
        return True, "empty"
    n = len(pts[0])
    S = set(pts)
    # validity of entries + dimension consistency + no duplicates
    if len(S) != len(pts):
        return False, "duplicate points"
    for p in pts:
        if len(p) != n or any(c not in (0,1,2) for c in p):
            return False, f"bad point {p}"
    # check no 3 distinct points sum to 0 mod 3.
    # Fast: for each unordered pair (a,b), the unique c making a+b+c=0 is
    # c = (-a-b) mod 3; if c is in the set and c != a and c != b -> violation.
    pts_set = S
    for a, b in itertools.combinations(pts, 2):
        c = tuple((-(a[i]+b[i])) % 3 for i in range(n))
        if c in pts_set and c != a and c != b:
            return False, f"AP found: {a},{b},{c}"
    return True, "ok"

def score(points, n):
    valid, reason = is_capset(points)
    size = len(set(tuple(p) for p in points))
    out = {"n": n, "size": size, "valid": valid, "reason": reason}
    if n in KNOWN_MAX:
        out["known_max"] = KNOWN_MAX[n]
        out["matches_optimal"] = valid and size == KNOWN_MAX[n]
        out["beats_optimal_IMPOSSIBLE"] = valid and size > KNOWN_MAX[n]  # would mean a bug
    elif n in KNOWN_LB:
        out["known_lower_bound"] = KNOWN_LB[n]
        out["beats_known_LB"] = valid and size > KNOWN_LB[n]  # the only real "breakthrough" cell
        out["matches_known_LB"] = valid and size == KNOWN_LB[n]
    return out

if __name__ == "__main__":
    # usage: python3 capset_verify.py <json file of {n: [[point],...]}>
    data = json.load(open(sys.argv[1]))
    for n_str, pts in data.items():
        print(json.dumps(score(pts, int(n_str))))
