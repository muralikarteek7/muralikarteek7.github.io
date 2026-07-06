#!/usr/bin/env python3
"""
Quadratic-Offset Parity Grid (two-coordinate slice with non-affine cell grading)
Recipe: lens two-coord-slice

Coordinates (x1,x2; y) with cell index (x1,x2) in F_3^2 and fiber y in F_3^5.
Objects are built with the {1,2}^5 parity language, graded by quadratic offset
v(x1,x2) = x1^2*a + x2^2*b + x1*x2*c (componentwise mod 3).
"""
import itertools, json, time, sys
sys.path.insert(0, '/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set')
from capset_verify import is_capset

# ---- F_3^5 arithmetic ----
def vadd(u, v): return tuple((u[i]+v[i])%3 for i in range(5))
def vscale(k, v): return tuple((k*v[i])%3 for i in range(5))
def vneg(v): return tuple((-v[i])%3 for i in range(5))

# ---- Step 1: Fix a, b, c in F_3^5 ----
a = (1,1,1,1,2)
b = (1,1,1,2,1)
c = (0,0,0,1,1)

def v_offset(x1, x2):
    """v(x1,x2) = x1^2*a + x2^2*b + x1*x2*c (componentwise mod 3)"""
    x1sq = (x1*x1) % 3
    x2sq = (x2*x2) % 3
    x1x2 = (x1*x2) % 3
    return vadd(vadd(vscale(x1sq, a), vscale(x2sq, b)), vscale(x1x2, c))

# ---- Verify the four forbidden targets ----
# directions in F_3^2: (1,0),(0,1),(1,1),(1,2)
# For direction d=(d1,d2), m_L = 2*(d1^2*a + d2^2*b + d1*d2*c)
# t_dir = -m_L = -(2*...) = 1*... = a/b/a+b+c/a+b+2c
def forbidden_target(d1, d2):
    d1sq = (d1*d1) % 3
    d2sq = (d2*d2) % 3
    d1d2 = (d1*d2) % 3
    inner = vadd(vadd(vscale(d1sq, a), vscale(d2sq, b)), vscale(d1d2, c))
    m_L = vscale(2, inner)
    t = vneg(m_L)
    return t

t_dirs = {
    (1,0): forbidden_target(1,0),
    (0,1): forbidden_target(0,1),
    (1,1): forbidden_target(1,1),
    (1,2): forbidden_target(1,2),
}

print("Forbidden fiber targets:")
for d, t in t_dirs.items():
    n2s = sum(1 for x in t if x == 2)
    print(f"  direction {d}: t={t}  #2s={n2s} (odd={n2s%2==1})")

# ---- Step 2: Define D = {1,2}^5 and P0 (even-parity subset) ----
D = list(itertools.product([1,2], repeat=5))
P0 = [y for y in D if sum(1 for yi in y if yi == 1) % 2 == 0]

print(f"\n|D| = {len(D)} (should be 32)")
print(f"|P0| = {len(P0)} (should be 16)")

# Verify: D contains no 3-term AP (i.e., three elements summing to 0 mod 3)
def check_no_AP(pts, name):
    pt_set = set(pts)
    for u, v2 in itertools.combinations(pts, 2):
        c_pt = tuple((-(u[i]+v2[i]))%3 for i in range(5))
        if c_pt in pt_set and c_pt != u and c_pt != v2:
            print(f"  {name}: AP found: {u},{v2},{c_pt}")
            return False
    print(f"  {name}: no 3-term AP (cap-free in F_3^5)")
    return True

print("\nVerifying D and P0 are caps in F_3^5:")
check_no_AP(D, "D={1,2}^5")
check_no_AP(P0, "P0")

# Verify character fact: triples from P0 summing to t have #2s(t) even
print("\nVerifying character fact (P0 triple-sums miss targets):")
p0_sums = set()
for u, v2, w in itertools.product(P0, repeat=3):
    s = tuple((u[i]+v2[i]+w[i])%3 for i in range(5))
    if all(si in (1,2) for si in s):
        p0_sums.add(s)

for d, t in t_dirs.items():
    hits = t in p0_sums
    n2s = sum(1 for x in t if x == 2)
    print(f"  direction {d}: t={t} #2s={n2s} in P0_triple_sums={hits} (should be False)")

# ---- Step 3: Build BASE LAYER B ----
print("\nBuilding base layer B...")
F3_2 = list(itertools.product(range(3), repeat=2))  # all cells (x1,x2)
B = []
for (x1, x2) in F3_2:
    off = v_offset(x1, x2)
    for y in P0:
        fiber = vadd(off, y)
        point = (x1, x2) + fiber  # 7-tuple
        B.append(point)

print(f"|B| = {len(B)} (should be 144)")

# Verify base layer with frozen verifier
t0 = time.time()
valid_base, reason_base = is_capset(B)
print(f"is_capset(B) = {valid_base} ({reason_base}) in {time.time()-t0:.2f}s")

# ---- Step 4: CP-SAT ENLARGEMENT ----
print("\nSetting up CP-SAT enlargement...")
try:
    from ortools.sat.python import cp_model
except ImportError:
    print("ortools not available; skipping CP-SAT step")
    sys.exit(1)

ALL5 = list(itertools.product(range(3), repeat=5))
IDX5 = {v: i for i, v in enumerate(ALL5)}

# Build full 7-dim candidate set
# For each cell s=(x1,x2) and each y in F_3^5, the point is s ++ (v(s)+y mod 3)
# We index by (cell_idx, fiber_idx)
cells = F3_2
n_cells = 9
n_fiber = 243

def cell_fiber_to_point(ci, fi):
    x1, x2 = cells[ci]
    off = v_offset(x1, x2)
    fiber = ALL5[fi]
    translated_fiber = vadd(off, fiber)
    return (x1, x2) + translated_fiber

# Precompute point for each (cell, fiber)
all_points = {}
for ci in range(n_cells):
    for fi in range(n_fiber):
        all_points[(ci, fi)] = cell_fiber_to_point(ci, fi)

# Base set: which (ci, fi) pairs are in B?
base_set = set()
for (x1, x2) in F3_2:
    ci = cells.index((x1, x2))
    off = v_offset(x1, x2)
    for y in P0:
        fi = IDX5[y]
        base_set.add((ci, fi))

print(f"Base set size: {len(base_set)}")

# All lines in F_3^5 (for per-cell cap constraints)
print("Precomputing F_3^5 lines...")
lines5 = []
seen5 = set()
for p in ALL5:
    for d in ALL5:
        if d == (0,)*5: continue
        tri = tuple(sorted([p, tuple((p[i]+d[i])%3 for i in range(5)),
                            tuple((p[i]+2*d[i])%3 for i in range(5))]))
        if len(set(tri)) == 3 and tri not in seen5:
            seen5.add(tri)
            lines5.append(tri)
print(f"  {len(lines5)} lines in F_3^5")

# All lines in F_3^2 (for cross-cell constraints)
lines2 = []
seen2 = set()
for p in F3_2:
    for d in F3_2:
        if d == (0,0): continue
        tri = tuple(sorted([p, tuple((p[i]+d[i])%3 for i in range(2)),
                            tuple((p[i]+2*d[i])%3 for i in range(2))]))
        if len(set(tri)) == 3 and tri not in seen2:
            seen2.add(tri)
            lines2.append(tri)
print(f"  {len(lines2)} lines in F_3^2")

# Build CP-SAT model
m = cp_model.CpModel()
# Variables: z[ci][fi] = 1 if point (ci,fi) included
z = [[m.NewBoolVar(f"z_{ci}_{fi}") for fi in range(n_fiber)] for ci in range(n_cells)]

# Fix base points to 1
for (ci, fi) in base_set:
    m.Add(z[ci][fi] == 1)

# Per-cell cap constraints: for every 3-AP {y1,y2,y3} in F_3^5,
# z[s,fi1]+z[s,fi2]+z[s,fi3] <= 2
print("Adding per-cell cap constraints...")
n_cap_constraints = 0
for ci in range(n_cells):
    for (y1, y2, y3) in lines5:
        fi1, fi2, fi3 = IDX5[y1], IDX5[y2], IDX5[y3]
        m.Add(z[ci][fi1] + z[ci][fi2] + z[ci][fi3] <= 2)
        n_cap_constraints += 1
print(f"  {n_cap_constraints} per-cell constraints")

# Cross-cell line constraints:
# For each line {u,v,w} in F_3^2 (cells) and each fiber triple (y1,y2,y3) with
# y1+y2+y3 = -(v_offset(u)+v_offset(v)+v_offset(w)) mod 3,
# z[u,fi1]+z[v,fi2]+z[w,fi3] <= 2
print("Adding cross-cell constraints...")
n_cross_constraints = 0
for (u, v2, w) in lines2:
    cu = cells.index(u)
    cv = cells.index(v2)
    cw = cells.index(w)
    # Required fiber sum target: -(v(u)+v(v)+v(w))
    offset_sum = vadd(vadd(v_offset(*u), v_offset(*v2)), v_offset(*w))
    target = vneg(offset_sum)
    # Enumerate all fiber triples (y1,y2,y3) with y1+y2+y3 = target mod 3
    # Outer loop over y1,y2, compute y3 = target - y1 - y2
    for fi1 in range(n_fiber):
        y1 = ALL5[fi1]
        for fi2 in range(n_fiber):
            y2 = ALL5[fi2]
            y3 = tuple((target[i] - y1[i] - y2[i]) % 3 for i in range(5))
            fi3 = IDX5[y3]
            # Allow repeats when cells differ (as stated in recipe)
            m.Add(z[cu][fi1] + z[cv][fi2] + z[cw][fi3] <= 2)
            n_cross_constraints += 1

print(f"  {n_cross_constraints} cross-cell constraints")

# Maximize total
m.Maximize(sum(z[ci][fi] for ci in range(n_cells) for fi in range(n_fiber)))

print("\nSolving CP-SAT (WITH base fixed, time limit 300s)...")
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 300
solver.parameters.num_search_workers = 8

t0 = time.time()
status = solver.Solve(m)
elapsed = time.time() - t0
print(f"  Status: {solver.StatusName(status)} in {elapsed:.1f}s")
print(f"  Objective (size): {solver.ObjectiveValue()}")

# Extract solution
points_fixed = [all_points[(ci, fi)]
                for ci in range(n_cells) for fi in range(n_fiber)
                if solver.Value(z[ci][fi]) == 1]
print(f"  Points collected: {len(points_fixed)}")

valid_fixed, reason_fixed = is_capset(points_fixed)
size_fixed = len(set(points_fixed))
print(f"  is_capset = {valid_fixed} ({reason_fixed}), size={size_fixed}")

# ---- Step 5: Also run WITHOUT fixing base (base as warm start only) ----
print("\nSolving CP-SAT (WITHOUT base fixed, base as hint, time limit 300s)...")
m2 = cp_model.CpModel()
z2 = [[m2.NewBoolVar(f"z2_{ci}_{fi}") for fi in range(n_fiber)] for ci in range(n_cells)]

# Add hints from base
for ci in range(n_cells):
    for fi in range(n_fiber):
        m2.AddHint(z2[ci][fi], 1 if (ci, fi) in base_set else 0)

# Per-cell cap constraints
for ci in range(n_cells):
    for (y1, y2, y3) in lines5:
        fi1, fi2, fi3 = IDX5[y1], IDX5[y2], IDX5[y3]
        m2.Add(z2[ci][fi1] + z2[ci][fi2] + z2[ci][fi3] <= 2)

# Cross-cell constraints
for (u, v2, w) in lines2:
    cu = cells.index(u)
    cv = cells.index(v2)
    cw = cells.index(w)
    offset_sum = vadd(vadd(v_offset(*u), v_offset(*v2)), v_offset(*w))
    target = vneg(offset_sum)
    for fi1 in range(n_fiber):
        y1 = ALL5[fi1]
        for fi2 in range(n_fiber):
            y2 = ALL5[fi2]
            y3 = tuple((target[i] - y1[i] - y2[i]) % 3 for i in range(5))
            fi3 = IDX5[y3]
            m2.Add(z2[cu][fi1] + z2[cv][fi2] + z2[cw][fi3] <= 2)

m2.Maximize(sum(z2[ci][fi] for ci in range(n_cells) for fi in range(n_fiber)))

solver2 = cp_model.CpSolver()
solver2.parameters.max_time_in_seconds = 300
solver2.parameters.num_search_workers = 8

t0 = time.time()
status2 = solver2.Solve(m2)
elapsed2 = time.time() - t0
print(f"  Status: {solver2.StatusName(status2)} in {elapsed2:.1f}s")
print(f"  Objective (size): {solver2.ObjectiveValue()}")

points_free = [all_points[(ci, fi)]
               for ci in range(n_cells) for fi in range(n_fiber)
               if solver2.Value(z2[ci][fi]) == 1]
print(f"  Points collected: {len(points_free)}")

valid_free, reason_free = is_capset(points_free)
size_free = len(set(points_free))
print(f"  is_capset = {valid_free} ({reason_free}), size={size_free}")

# ---- Report best result ----
print("\n=== FINAL RESULTS ===")
print(f"Base layer: valid={valid_base}, size=144")
print(f"CP-SAT (fixed base): valid={valid_fixed}, size={size_fixed}")
print(f"CP-SAT (free, hint): valid={valid_free}, size={size_free}")

# Pick best valid result
best_size = 0
best_points = []
if valid_fixed:
    if size_fixed > best_size:
        best_size = size_fixed
        best_points = points_fixed
if valid_free:
    if size_free > best_size:
        best_size = size_free
        best_points = points_free
if not best_points and valid_base:
    best_size = len(B)
    best_points = B

print(f"\nBest certified size: {best_size}")
print(f"Beats 236: {best_size > 236}")

# Save best result
if best_points:
    out = {"7": [list(p) for p in best_points]}
    fname = f"/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/cap_n7_qopg_size{best_size}.json"
    json.dump(out, open(fname, "w"))
    print(f"Saved to {fname}")
