#!/usr/bin/env python3
"""FROZEN exact verifier for the no-three-in-line problem (COLD-TEST arena, 2026-06-10).
Place points on the k x k integer grid so that no 3 are collinear. Exact integer arithmetic
(cross-product = 0 test) — no floating point, so it cannot be gamed by near-misses (Tao discipline).
Ground truth: the max is at most 2k (pigeonhole on rows); 2k is achievable at least up to k=46
(known results). This verifier is the only thing that certifies any claim.
"""
import itertools

def collinear(a, b, c):
    # exact: area of triangle == 0  <=>  (b-a) x (c-a) == 0
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]) == 0

def is_valid(points, k):
    pts = [tuple(p) for p in points]
    S = set(pts)
    if len(S) != len(pts):
        return False, "duplicate points"
    for (x, y) in pts:
        if not (0 <= x < k and 0 <= y < k):
            return False, f"point {(x,y)} off the {k}x{k} grid"
    for a, b, c in itertools.combinations(pts, 3):
        if collinear(a, b, c):
            return False, f"3 collinear: {a},{b},{c}"
    return True, "ok"

def score(points, k):
    valid, reason = is_valid(points, k)
    n = len(set(tuple(p) for p in points))
    out = {"k": k, "size": n, "valid": valid, "reason": reason,
           "max_possible_2k": 2*k, "matches_2k": valid and n == 2*k}
    return out

# adversarial self-test of the verifier (must reject known-bad, accept known-good)
if __name__ == "__main__":
    # known-bad: (0,0),(1,1),(2,2) collinear
    v,_ = is_valid([(0,0),(1,1),(2,2)], 3); assert v is False, "verifier FALSE-NEGATIVE on collinear"
    # known-good small: a valid set on 2x2 (all 4 corners: but (0,0),(1,0),... check) -> 4 points, any 3 collinear? no
    v,r = is_valid([(0,0),(0,1),(1,0),(1,1)], 2); assert v is True, f"verifier rejected valid 2x2 set: {r}"
    # impossible spec test: ask for an off-grid point -> reject
    v,_ = is_valid([(5,5)], 2); assert v is False, "verifier accepted off-grid"
    print("verifier self-test PASSED (rejects collinear + off-grid, accepts valid)")
