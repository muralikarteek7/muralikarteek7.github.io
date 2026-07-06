#!/usr/bin/env python3
"""
Verifier for Sidon set (B2 set) problem.
A Sidon set: all pairwise sums a+b (a <= b) are distinct.
Goal: find a Sidon set of size 8 in {1,...,35} and check if 8 is the max.
"""

def is_sidon(S):
    """Check if set S is a Sidon set (all pairwise sums distinct)."""
    S = sorted(S)
    sums = []
    for i in range(len(S)):
        for j in range(i, len(S)):
            sums.append(S[i] + S[j])
    return len(sums) == len(set(sums))

def all_pairwise_sums(S):
    """Return all pairwise sums (with repetition for a+a)."""
    S = sorted(S)
    sums = {}
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                sums[s].append((S[i], S[j]))
            else:
                sums[s] = [(S[i], S[j])]
    return sums

# Candidate Sidon set of size 8 in {1,...,35}
# Known construction: use a Singer difference set or exhaust search.
# One known example: {1, 2, 3, 5, 11, 19, 24, 30} - let's verify
# Another well-known: {0,1,3,7,12,20,22,25} shifted to start at 1

# Let's try a known Sidon set of size 8 in [1,35]
# From literature: {2, 6, 13, 15, 27, 29, 32, 34} — need to verify
# Let's search computationally for a valid one

from itertools import combinations

def find_sidon_greedy(n, target_size):
    """Greedy search for a Sidon set in {1,...,n}."""
    S = []
    sums_seen = set()
    for x in range(1, n+1):
        # Check if x can be added
        new_sums = set()
        valid = True
        for s in S:
            pair_sum = s + x
            if pair_sum in sums_seen or pair_sum in new_sums:
                valid = False
                break
            new_sums.add(pair_sum)
        # Also check x+x
        if x + x in sums_seen or x + x in new_sums:
            valid = False
        else:
            new_sums.add(x + x)
        if valid:
            S.append(x)
            sums_seen |= new_sums
        if len(S) == target_size:
            break
    return S

def exhaustive_search_size(n, target_size):
    """Search for any Sidon set of given size in {1,...,n}."""
    for combo in combinations(range(1, n+1), target_size):
        if is_sidon(combo):
            return list(combo)
    return None

print("="*60)
print("SIDON SET VERIFIER: B2 set of size 8 in {1,...,35}")
print("="*60)

# Step 1: Find a Sidon set of size 8 via exhaustive search (pruned)
# Use a backtracking approach for efficiency
def backtrack_sidon(n, target_size, current=None, sums_seen=None, start=1):
    if current is None:
        current = []
        sums_seen = set()
    if len(current) == target_size:
        return list(current)
    remaining = n - start + 1
    if remaining < target_size - len(current):
        return None  # prune
    for x in range(start, n+1):
        new_sums = []
        valid = True
        # Check x+x
        xx = x + x
        if xx in sums_seen:
            valid = False
        else:
            new_sums.append(xx)
        if valid:
            for s in current:
                sx = s + x
                if sx in sums_seen or sx in new_sums:
                    valid = False
                    break
                new_sums.append(sx)
        if valid:
            current.append(x)
            for ns in new_sums:
                sums_seen.add(ns)
            result = backtrack_sidon(n, target_size, current, sums_seen, x+1)
            if result is not None:
                return result
            current.pop()
            for ns in new_sums:
                sums_seen.discard(ns)
    return None

print("\nSearching for Sidon set of size 8 in {1,...,35}...")
S8 = backtrack_sidon(35, 8)

if S8 is None:
    print("No Sidon set of size 8 found in {1,...,35}!")
else:
    print(f"Found: {S8}")
    print(f"Size: {len(S8)}")
    print(f"Range check: min={min(S8)}, max={max(S8)}, all in [1,35]: {all(1 <= x <= 35 for x in S8)}")

    # Verify it's a Sidon set
    sums = all_pairwise_sums(S8)
    all_distinct = all(len(v) == 1 for v in sums.values())
    print(f"\nAll pairwise sums distinct: {all_distinct}")

    if not all_distinct:
        print("COLLISION FOUND:")
        for s, pairs in sums.items():
            if len(pairs) > 1:
                print(f"  Sum {s}: {pairs}")
    else:
        print("VERIFIED: This is a valid Sidon set of size 8.")
        print(f"\nAll {len(sums)} pairwise sums (a+b, a<=b):")
        for s in sorted(sums.keys()):
            print(f"  {sums[s][0][0]} + {sums[s][0][1]} = {s}")

# Step 2: Check if size 9 is achievable in {1,...,35}
print("\n" + "="*60)
print("Checking if size 9 is achievable in {1,...,35}...")
print("(This may take a moment)")
S9 = backtrack_sidon(35, 9)
if S9 is None:
    print("No Sidon set of size 9 exists in {1,...,35}.")
    print("=> 8 IS the maximum size for Sidon sets in {1,...,35}.")
else:
    print(f"Found size 9: {S9}")
    print("=> 8 is NOT the maximum; 9 is achievable.")
