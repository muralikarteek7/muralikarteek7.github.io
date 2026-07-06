#!/usr/bin/env python3
"""
Z3-orbit quotient cap construction (lens: order3-orbit-quotient cap).

Recipe: define order-3 affine map T on F_3^7:
  T(x0,x1,x2,x3,x4,x5,x6) = (x0+1 mod 3, x3+v1, x1+v2, x2+v3, x6+v4, x4+v5, x5+v6)
  where the linear part pi cyclically permutes coordinate blocks (x1 x2 x3) and (x4 x5 x6).

For T^3 = identity, need: v1+v2+v3 = 0 mod 3 AND v4+v5+v6 = 0 mod 3.
NOTE: The recipe states v=(1,0,0,1,0,0) but this does NOT satisfy T^3=id (v1+v2+v3=1 mod 3).
We implement the most faithful reading: use all valid v (81 choices with T^3=id),
prioritizing v with nonzero block contributions.

Every orbit has size exactly 3 (x0 shifts by 1 each step, period 3; blocks cycle too).
"""

import itertools
import sys
import json
import time
import random

def apply_T(p, v):
    """Apply T: (x0,x1,x2,x3,x4,x5,x6) -> (x0+1, x3+v1, x1+v2, x2+v3, x6+v4, x4+v5, x5+v6)"""
    x0, x1, x2, x3, x4, x5, x6 = p
    v1, v2, v3, v4, v5, v6 = v
    return (
        (x0 + 1) % 3,
        (x3 + v1) % 3,
        (x1 + v2) % 3,
        (x2 + v3) % 3,
        (x6 + v4) % 3,
        (x4 + v5) % 3,
        (x5 + v6) % 3,
    )

def compute_orbits(v):
    """Partition all 2187 points of F_3^7 into orbits of T_v."""
    all_points = list(itertools.product(range(3), repeat=7))
    visited = {}
    orbits = []
    for p in all_points:
        if p in visited:
            continue
        orbit = [p]
        cur = apply_T(p, v)
        cnt = 0
        while cur != p and cnt < 10:
            orbit.append(cur)
            cur = apply_T(cur, v)
            cnt += 1
        if cur != p:
            return None, None  # T^3 != id
        if len(orbit) not in (1, 3):
            return None, None
        oid = len(orbits)
        orbits.append(tuple(orbit))
        for q in orbit:
            visited[q] = oid
    if len(orbits) != 729:
        return None, None
    return orbits, visited

def build_constraints(orbits, point_to_orbit):
    """
    For each collinear triple {p,q,r} with p+q+r=0 mod 3, map to orbit constraints.
    - All three in same orbit: ban that orbit.
    - Two distinct orbits {i,j}: x_i + x_j <= 1.
    - Three distinct orbits {i,j,k}: x_i + x_j + x_k <= 2.
    """
    all_points = list(itertools.product(range(3), repeat=7))
    banned = set()
    pair_constraints = set()
    triple_constraints = set()

    # Iterate over all pairs, compute third point
    for idx_a in range(len(all_points)):
        a = all_points[idx_a]
        for idx_b in range(idx_a + 1, len(all_points)):
            b = all_points[idx_b]
            c = tuple((-(a[i] + b[i])) % 3 for i in range(7))
            if c <= b:  # deduplicate: only process each unordered triple once
                continue
            # Now a < b < c in lex order (since c > b)
            oi = point_to_orbit[a]
            oj = point_to_orbit[b]
            ok = point_to_orbit[c]
            s = set([oi, oj, ok])
            if len(s) == 1:
                banned.add(oi)
            elif len(s) == 2:
                pair_constraints.add(tuple(sorted([oi, oj, ok][:2]) if oi==ok or oj==ok else sorted([oi,oj])))
                # Properly extract the pair
                lst = [oi, oj, ok]
                unique = sorted(set(lst))
                pair_constraints.add(tuple(unique))
            else:
                triple_constraints.add(tuple(sorted([oi, oj, ok])))

    # Clean up pair_constraints - make sure they're actual pairs
    actual_pairs = set()
    for item in pair_constraints:
        if len(item) == 2:
            actual_pairs.add(item)

    actual_triples = set()
    for item in triple_constraints:
        if len(item) == 3:
            actual_triples.add(item)

    return banned, actual_pairs, actual_triples

def build_constraints_fast(orbits, point_to_orbit):
    """
    Faster constraint building using direct point lookup.
    """
    all_points = list(itertools.product(range(3), repeat=7))
    pts_set = set(all_points)
    banned = set()
    pair_constraints = set()
    triple_constraints = set()

    for i_a, a in enumerate(all_points):
        for i_b in range(i_a + 1, len(all_points)):
            b = all_points[i_b]
            c = tuple((-(a[k] + b[k])) % 3 for k in range(7))
            # Only process triple (a,b,c) once: require c > b in lex
            if c <= b:
                continue
            oi = point_to_orbit[a]
            oj = point_to_orbit[b]
            ok = point_to_orbit[c]
            ids = sorted([oi, oj, ok])
            n_unique = len(set(ids))
            if n_unique == 1:
                banned.add(ids[0])
            elif n_unique == 2:
                pair_constraints.add(tuple(sorted(set(ids))))
            else:
                triple_constraints.add(tuple(ids))

    return banned, pair_constraints, triple_constraints

def greedy_hint(n_orbits, banned, pair_constraints, triple_constraints, n_restarts=1000):
    """Randomized greedy."""
    pair_lookup = {}
    triple_lookup = {}

    for i, j in pair_constraints:
        pair_lookup.setdefault(i, set()).add(j)
        pair_lookup.setdefault(j, set()).add(i)

    for t in triple_constraints:
        for oi in t:
            triple_lookup.setdefault(oi, list()).append(t)

    best = []
    avail_base = list(set(range(n_orbits)) - banned)

    for _ in range(n_restarts):
        avail = avail_base[:]
        random.shuffle(avail)
        chosen = set()
        excluded = set(banned)
        avail_set = set(avail)

        for oi in avail:
            if oi in excluded:
                continue
            chosen.add(oi)
            # Exclude pair partners
            if oi in pair_lookup:
                excluded.update(pair_lookup[oi])
            # Check triples: if 2 others in same triple are chosen, can't add third
            if oi in triple_lookup:
                for t in triple_lookup[oi]:
                    others = [x for x in t if x != oi]
                    n_chosen = sum(1 for o in others if o in chosen)
                    if n_chosen == 1:
                        # Two in triple now chosen, exclude third
                        for o in others:
                            if o not in chosen:
                                excluded.add(o)

        if len(chosen) > len(best):
            best = list(chosen)

    return best

def solve_cpsat(n_orbits, banned, pair_constraints, triple_constraints, hint=None,
                max_time=7200, num_workers=8, verbose=True):
    """Solve with CP-SAT."""
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    x = [model.NewBoolVar(f'x_{i}') for i in range(n_orbits)]

    for i in banned:
        model.Add(x[i] == 0)

    for i, j in pair_constraints:
        model.Add(x[i] + x[j] <= 1)

    for i, j, k in triple_constraints:
        model.Add(x[i] + x[j] + x[k] <= 2)

    model.Maximize(sum(x))

    if hint:
        hint_set = set(hint)
        for i in range(n_orbits):
            model.AddHint(x[i], 1 if i in hint_set else 0)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time
    solver.parameters.num_search_workers = num_workers
    solver.parameters.log_search_progress = verbose

    start = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - start
    if verbose:
        print(f"CP-SAT status: {solver.StatusName(status)}, elapsed: {elapsed:.1f}s",
              file=sys.stderr)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = [i for i in range(n_orbits) if solver.Value(x[i]) == 1]
        if verbose:
            print(f"Chosen orbits: {len(chosen)} -> {len(chosen)*3} points", file=sys.stderr)
        return chosen, solver.StatusName(status)
    return [], solver.StatusName(status)

def run_for_v(v, max_time, num_workers=8, greedy_restarts=500, verbose=True):
    """Run full pipeline for a given v vector."""
    if verbose:
        print(f"\n--- v={v} ---", file=sys.stderr)
    orbits, point_to_orbit = compute_orbits(v)
    if orbits is None:
        if verbose:
            print(f"  Invalid: T^3 != id for v={v}", file=sys.stderr)
        return [], None, None

    if verbose:
        print(f"  Orbits: {len(orbits)}", file=sys.stderr)

    banned, pair_constraints, triple_constraints = build_constraints_fast(orbits, point_to_orbit)
    if verbose:
        print(f"  Banned={len(banned)}, Pairs={len(pair_constraints)}, Triples={len(triple_constraints)}",
              file=sys.stderr)

    hint = greedy_hint(len(orbits), banned, pair_constraints, triple_constraints,
                       n_restarts=greedy_restarts)
    if verbose:
        print(f"  Greedy hint: {len(hint)} orbits -> {len(hint)*3} pts", file=sys.stderr)

    chosen, status = solve_cpsat(len(orbits), banned, pair_constraints, triple_constraints,
                                  hint=hint, max_time=max_time, num_workers=num_workers, verbose=verbose)
    return chosen, orbits, status

def main():
    print("=== Z3-Orbit Quotient Cap Construction ===", file=sys.stderr)
    print("Note: recipe's v=(1,0,0,1,0,0) does NOT satisfy T^3=id; using valid v sets.", file=sys.stderr)

    # Valid v values: v1+v2+v3 = 0 mod 3 AND v4+v5+v6 = 0 mod 3
    # All 81 valid choices; prioritize nontrivial ones
    # Priority order:
    # 1. v=(1,1,1,1,1,1) - max translation, all blocks shift
    # 2. v=(0,0,0,1,1,1) - only block2 shifts
    # 3. v=(1,1,1,0,0,0) - only block1 shifts
    # 4. v=(0,0,0,0,0,0) - trivial (pure pi cycling)
    # 5. Other valid v from F_3^6

    # Build list of valid v, prioritizing binary nontrivial
    priority_vs = [
        (1,1,1,1,1,1),
        (0,0,0,1,1,1),
        (1,1,1,0,0,0),
        (2,2,2,2,2,2),
        (1,2,0,1,2,0),
        (2,1,0,2,1,0),
        (0,1,2,0,1,2),
        (0,2,1,0,2,1),
        (1,2,0,0,0,0),
        (0,0,0,1,2,0),
        (2,0,1,2,0,1),
        (0,0,0,0,0,0),  # trivial last
    ]

    # Filter to valid ones
    valid_priority = []
    for v in priority_vs:
        s1 = (v[0]+v[1]+v[2]) % 3
        s2 = (v[3]+v[4]+v[5]) % 3
        if s1 == 0 and s2 == 0:
            valid_priority.append(v)

    # Also add all 81 valid v not already in list
    all_valid = []
    for v in itertools.product(range(3), repeat=6):
        s1 = (v[0]+v[1]+v[2]) % 3
        s2 = (v[3]+v[4]+v[5]) % 3
        if s1 == 0 and s2 == 0:
            all_valid.append(v)

    # Combine: priority first, then rest
    seen = set(valid_priority)
    remaining = [v for v in all_valid if v not in seen]
    vs_to_try = valid_priority + remaining

    print(f"Total valid v values: {len(all_valid)}", file=sys.stderr)
    print(f"Will try up to {len(vs_to_try)} v values", file=sys.stderr)

    best_chosen = []
    best_orbits = None
    best_v = None
    best_size = 0

    # Time budget: 7200s total for primary, distribute across variants
    # Primary v (first few): 1800s each for top 4, then 240s for rest
    time_budgets = [1800, 1800, 1800, 1800] + [240] * (len(vs_to_try) - 4)

    for idx, v in enumerate(vs_to_try):
        t_budget = time_budgets[idx] if idx < len(time_budgets) else 240
        greedy_r = 1000 if idx < 4 else 300

        chosen, orbits, status = run_for_v(v, max_time=t_budget, num_workers=8,
                                            greedy_restarts=greedy_r, verbose=(idx < 10))

        if chosen and len(chosen) > len(best_chosen):
            best_chosen = chosen
            best_orbits = orbits
            best_v = v
            best_size = len(chosen) * 3
            print(f"  ** NEW BEST: v={v}, {len(chosen)} orbits -> {best_size} points **",
                  file=sys.stderr)

        if best_size >= 240:
            print(f"Target reached: {best_size} points. Stopping early.", file=sys.stderr)
            break

    print(f"\n=== BEST SOLUTION: v={best_v}, {len(best_chosen)} orbits -> {best_size} points ===",
          file=sys.stderr)

    if not best_chosen:
        print("No solution found.", file=sys.stderr)
        result = {"size": 0, "valid": False, "reason": "no solution from CP-SAT",
                  "beats_236": False, "n_orbits_chosen": 0, "n": 7}
        print(json.dumps(result))
        return False, 0, False

    # Expand best solution
    points = []
    for oid in best_chosen:
        points.extend(best_orbits[oid])

    print(f"Expanded to {len(points)} points.", file=sys.stderr)

    # Verify with frozen verifier
    sys.path.insert(0, '/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set')
    from capset_verify import is_capset

    valid, reason = is_capset(points)
    size = len(points)
    beats_236 = valid and size > 236

    print(f"\n=== VERIFIER RESULT ===", file=sys.stderr)
    print(f"Size: {size}", file=sys.stderr)
    print(f"Valid: {valid}", file=sys.stderr)
    print(f"Reason: {reason}", file=sys.stderr)
    print(f"Beats 236: {beats_236}", file=sys.stderr)

    result = {
        "size": size,
        "valid": valid,
        "reason": reason,
        "beats_236": beats_236,
        "n_orbits_chosen": len(best_chosen),
        "best_v": list(best_v) if best_v else None,
        "n": 7
    }
    print(json.dumps(result))

    # Save if valid and non-trivial
    if valid and size > 0:
        fname = (f"/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/"
                 f"z3_orbit_cap_size{size}.json")
        with open(fname, 'w') as f:
            json.dump({"7": [list(p) for p in points]}, f)
        print(f"Saved to {fname}", file=sys.stderr)

    return valid, size, beats_236

if __name__ == "__main__":
    main()
