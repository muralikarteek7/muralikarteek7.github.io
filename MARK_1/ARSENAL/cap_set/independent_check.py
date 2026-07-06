"""
Independent cap set verifier — written from scratch.
No imports from any existing repo code.

A cap set in F_3^n means a set S where NO three DISTINCT points a, b, c satisfy
    a[i] + b[i] + c[i] ≡ 0  (mod 3)   for all coordinates i.

Two verification methods are used and their results compared:
  Method A: Brute-force over all C(N,3) triples.
  Method B: Pair-implies-third.  For each ordered pair (a,b), compute the unique
            c = (-a - b) mod 3 that would complete a line.  If c is in the set and
            c != a and c != b, that's a violation.
            (Each unordered triple is generated 6 times as ordered pairs, so any
             hit found here matches Method A.)
"""

import json
import itertools

# ── Load ──────────────────────────────────────────────────────────────────────
with open("cap_n7_size236_CF.json") as f:
    data = json.load(f)

raw_points = data["7"]           # list of lists

# ── Basic sanity checks ───────────────────────────────────────────────────────
N = len(raw_points)
print(f"Points loaded          : {N}")

# Check all points are in {0,1,2}^7
bad_values = []
for idx, pt in enumerate(raw_points):
    if len(pt) != 7:
        bad_values.append((idx, pt, "wrong length"))
    elif any(v not in (0, 1, 2) for v in pt):
        bad_values.append((idx, pt, "value out of range"))

if bad_values:
    print(f"INVALID POINTS (first 5): {bad_values[:5]}")
else:
    print("All points in {0,1,2}^7  : YES")

# Check distinctness
tuples = [tuple(p) for p in raw_points]
unique_set = set(tuples)
print(f"Distinct points        : {len(unique_set)}")
if len(unique_set) != N:
    print(f"WARNING: {N - len(unique_set)} duplicate(s) found!")
else:
    print("All points distinct    : YES")

# ── Method A: Brute-force over all C(N,3) triples ────────────────────────────
print(f"\n=== Method A: Brute-force over C({N},3) = {N*(N-1)*(N-2)//6} triples ===")

violations_A = []
for i, j, k in itertools.combinations(range(N), 3):
    a, b, c = raw_points[i], raw_points[j], raw_points[k]
    if all((a[d] + b[d] + c[d]) % 3 == 0 for d in range(7)):
        violations_A.append((a, b, c))
        if len(violations_A) <= 3:   # show first few
            print(f"  Violation triple: {a}  +  {b}  +  {c}")

print(f"Total violations found (Method A): {len(violations_A)}")

# ── Method B: Pair → implied third ───────────────────────────────────────────
print(f"\n=== Method B: Pair-implies-third ===")
point_set = set(tuples)

violations_B = set()  # store as frozensets to avoid counting same triple twice
for i in range(N):
    for j in range(N):
        if i == j:
            continue
        a = raw_points[i]
        b = raw_points[j]
        # The unique c that completes a line: c = (-a - b) mod 3 = (3-a+3-b) mod 3 = (6-a-b) mod 3
        c = tuple((-(a[d] + b[d])) % 3 for d in range(7))
        if c in point_set and c != tuple(a) and c != tuple(b):
            key = frozenset((tuple(a), tuple(b), c))
            violations_B.add(key)

print(f"Total violations found (Method B): {len(violations_B)}")

if len(violations_B) > 0:
    example = next(iter(violations_B))
    pts = list(example)
    print(f"  Example violation triple: {pts[0]}  {pts[1]}  {pts[2]}")

# ── Cross-check ───────────────────────────────────────────────────────────────
print(f"\n=== Cross-check ===")
print(f"Method A count: {len(violations_A)}")
print(f"Method B count: {len(violations_B)}")
methods_agree = (len(violations_A) == 0) == (len(violations_B) == 0)
print(f"Both methods agree on validity: {methods_agree}")
if len(violations_A) > 0 and len(violations_B) > 0:
    # Check Method B count matches A
    print(f"Counts match: {len(violations_A) == len(violations_B)}")

# ── Final verdict ─────────────────────────────────────────────────────────────
print(f"\n=== FINAL VERDICT ===")
is_valid_size    = (len(unique_set) == 236) and (N == 236)
is_valid_coords  = (len(bad_values) == 0)
is_valid_no_line = (len(violations_A) == 0) and (len(violations_B) == 0)

print(f"Size exactly 236        : {is_valid_size}  (loaded {N}, unique {len(unique_set)})")
print(f"All coords in {{0,1,2}}^7  : {is_valid_coords}")
print(f"No 3-term arithmetic line: {is_valid_no_line}")

if is_valid_size and is_valid_coords and is_valid_no_line:
    print("\nRESULT: VALID cap set of size 236 in F_3^7. ✓")
else:
    print("\nRESULT: NOT a valid cap set of size 236. ✗")
