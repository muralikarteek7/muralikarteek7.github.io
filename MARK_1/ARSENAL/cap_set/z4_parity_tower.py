#!/usr/bin/env python3
"""Z4 parity-tower core split (stacked-character slices).
Recipe: lift the F_2 parity of CF's core D to Z_4 character phi(x)=#2s(x) mod 4,
splitting {1,2}^6 into K_0..K_3. Try all 13 nonempty PROPER-subset core unions
(size>=16) x 9 wing combos per slice, exact b&b gamma completion, frozen verifier judge.
"""
import itertools
import json
import sys
sys.path.insert(0, "/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set")
from capset_verify import is_capset

# ── helpers identical to build_236.py ────────────────────────────────────────
def expand(t):
    star = [i for i, c in enumerate(t) if c == '*']
    out = []
    for vals in itertools.product([1, 2], repeat=len(star)):
        v = [0] * 6
        for p, val in zip(star, vals):
            v[p] = val
        out.append(tuple(v))
    return out

def B1_templates():
    T = []
    for i in range(5):
        t = ['0'] * 6
        for k in range(3):
            t[1 + (i + k) % 5] = '*'
        T.append(t)
    return T

def B2_templates():
    T = []
    for i in range(5):
        t = ['0'] * 6
        t[0] = '*'
        for p in (i % 5, (i + 2) % 5):
            t[1 + p] = '*'
        T.append(t)
    return T

def interchange(t):
    return ['*' if c == '0' else '0' for c in t]

# ── Z4 classes ────────────────────────────────────────────────────────────────
ALL6 = list(itertools.product([1, 2], repeat=6))

def phi(x):
    return sum(1 for c in x if c == 2) % 4

K = [set(), set(), set(), set()]
for x in ALL6:
    K[phi(x)].add(x)

print("K sizes:", [len(K[r]) for r in range(4)], flush=True)

# ── core menu: nonempty PROPER subsets of {0,1,2,3} with total size >= 16 ────
CORE_MASKS = []
for mask in range(1, 15):  # proper subsets: mask 1..14 (excludes mask=15=all four)
    classes = [r for r in range(4) if (mask >> r) & 1]
    size = sum(len(K[r]) for r in classes)
    if size >= 16:
        CORE_MASKS.append(classes)

print(f"Valid core masks: {len(CORE_MASKS)}", flush=True)  # 13

def core_set(classes):
    s = set()
    for r in classes:
        s |= K[r]
    return frozenset(s)

CORES = [core_set(c) for c in CORE_MASKS]

# ── wing menu per slice: 9 combos (3 x 3) ────────────────────────────────────
B1 = B1_templates()
B2 = B2_templates()
iB1 = [interchange(t) for t in B1]
iB2 = [interchange(t) for t in B2]

def expand_orbit(templates):
    s = set()
    for t in templates:
        s |= set(expand(t))
    return frozenset(s)

W_B1  = expand_orbit(B1)
W_iB1 = expand_orbit(iB1)
W_B2  = expand_orbit(B2)
W_iB2 = expand_orbit(iB2)

B1_OPTIONS = [W_B1, W_iB1, frozenset()]
B2_OPTIONS = [W_B2, W_iB2, frozenset()]

WING_COMBOS = list(itertools.product(range(3), range(3)))  # 9 pairs

def build_slice(core, b1_idx, b2_idx):
    return core | B1_OPTIONS[b1_idx] | B2_OPTIONS[b2_idx]

# Precompute all 13*9 = 117 slices
SLICES = []
for ci, core in enumerate(CORES):
    for b1i, b2i in WING_COMBOS:
        s = build_slice(core, b1i, b2i)
        SLICES.append((ci, b1i, b2i, s))

print(f"Total slice options: {len(SLICES)}", flush=True)  # 117

# Precompute which slices are valid cap sets (in F_3^6)
SLICE_VALID = []
for _, _, _, s in SLICES:
    v, _ = is_capset(list(s))
    SLICE_VALID.append(v)
valid_count = sum(SLICE_VALID)
print(f"Valid cap set slices: {valid_count}/{len(SLICES)}", flush=True)

# ── branch-and-bound max cap with node limit ──────────────────────────────────
MAX_CAP_N6 = 112  # proven maximum cap size in F_3^6
MAX_BNB_NODES = 500_000  # hard node budget per b&b call

def max_cap_bnb(candidates, need_at_least):
    """Exact maximum cap subset of candidates via branch-and-bound.
    Returns [] immediately if:
      - len(candidates) < need_at_least
      - need_at_least > MAX_CAP_N6
      - node budget exhausted (returns best found so far, which may be < need_at_least)
    """
    cand = list(candidates)
    lc = len(cand)
    if lc < need_at_least or need_at_least > MAX_CAP_N6:
        return []

    # Quick greedy lower bound to initialize b&b
    greedy_cap = set()
    greedy_list = []
    for p in cand:
        ok = True
        for q in greedy_cap:
            r = tuple((-(p[i] + q[i])) % 3 for i in range(6))
            if r in greedy_cap:
                ok = False
                break
        if ok:
            greedy_cap.add(p)
            greedy_list.append(p)

    if len(greedy_cap) >= need_at_least:
        return greedy_list  # greedy already satisfies need

    # If greedy is far below need, very unlikely b&b will find it with budget
    # Skip if greedy < 80% of need (heuristic to avoid spending budget on hopeless cases)
    if len(greedy_cap) < need_at_least * 0.8:
        return []

    best = [len(greedy_cap) - 1]  # start below greedy so we don't return greedy directly
    best_set = [greedy_list]
    nodes = [0]

    def bnb(idx, current, current_set):
        if nodes[0] > MAX_BNB_NODES:
            return
        nodes[0] += 1
        remaining = lc - idx
        if len(current) + remaining <= best[0]:
            return
        if idx == lc:
            if len(current) > best[0]:
                best[0] = len(current)
                best_set[0] = list(current_set)
            return
        p = cand[idx]
        ok = True
        for q in current:
            r = tuple((-(p[i] + q[i])) % 3 for i in range(6))
            if r in current:
                ok = False
                break
        if ok:
            current.add(p)
            current_set.append(p)
            bnb(idx + 1, current, current_set)
            current.remove(p)
            current_set.pop()
        bnb(idx + 1, current, current_set)

    bnb(0, set(), [])
    return best_set[0] if best[0] >= need_at_least else []

# ── main search ───────────────────────────────────────────────────────────────
F3_6 = list(itertools.product(range(3), repeat=6))

best_total = 236
best_result = None
checked = 0
skipped_size = 0
skipped_cand = 0
skipped_gamma = 0

print("Starting search over 13689 (alpha, beta) pairs (target: >236)...", flush=True)

for ai, (aci, ab1i, ab2i, alpha) in enumerate(SLICES):
    alpha_list = list(alpha)
    la = len(alpha)
    for bi, (bci, bb1i, bb2i, beta) in enumerate(SLICES):
        lb = len(beta)
        # Prune 1: even with max possible gamma = 112, total can't beat best_total
        if la + lb + MAX_CAP_N6 <= best_total:
            skipped_size += 1
            continue

        beta_list = list(beta)

        # compute forbidden = {-(a+b) mod 3 : a in alpha, b in beta}
        forb = set()
        for a in alpha_list:
            for b in beta_list:
                forb.add(tuple((-(a[i] + b[i])) % 3 for i in range(6)))

        CAND = sorted(p for p in F3_6 if p not in forb)
        lc = len(CAND)

        # Prune 2: |alpha| + |beta| + |CAND| <= best_total
        if la + lb + lc <= best_total:
            skipped_cand += 1
            continue

        # Recipe requirement: alpha and beta must individually be cap sets
        if not SLICE_VALID[ai]:
            skipped_gamma += 1
            continue
        if not SLICE_VALID[bi]:
            skipped_gamma += 1
            continue

        need_gamma = best_total - la - lb + 1
        checked += 1
        gamma = max_cap_bnb(CAND, need_gamma)

        if not gamma:
            skipped_gamma += 1
            continue

        total = la + lb + len(gamma)
        if total > best_total:
            full = ([(0,) + a for a in alpha_list] +
                    [(1,) + b for b in beta_list] +
                    [(2,) + c for c in gamma])
            v, reason = is_capset(full)
            if v:
                best_total = total
                best_result = {
                    'total': total,
                    'alpha_size': la,
                    'beta_size': lb,
                    'gamma_size': len(gamma),
                    'alpha_core_classes': CORE_MASKS[aci],
                    'beta_core_classes': CORE_MASKS[bci],
                    'alpha_wings': (ab1i, ab2i),
                    'beta_wings': (bb1i, bb2i),
                    'full': full,
                    'valid': True,
                    'reason': reason,
                }
                print(f"  NEW BEST: {total} (alpha={la}, beta={lb}, gamma={len(gamma)}) "
                      f"core_a={CORE_MASKS[aci]} core_b={CORE_MASKS[bci]} "
                      f"wings_a=({ab1i},{ab2i}) wings_b=({bb1i},{bb2i})", flush=True)
            else:
                print(f"  INVALID at {total}: {reason[:80]}", flush=True)

    if ai % 10 == 0:
        print(f"  alpha slice {ai}/116, checked={checked}, "
              f"skip_size={skipped_size}, skip_cand={skipped_cand}, "
              f"skip_gamma={skipped_gamma}, best={best_total}", flush=True)

print(f"\nSearch complete. Checked {checked} pairs "
      f"(skipped: size={skipped_size}, cand={skipped_cand}, gamma={skipped_gamma}).")
print(f"Best total: {best_total}")

if best_result and best_result['valid'] and best_result['total'] > 236:
    v, r = is_capset(best_result['full'])
    print(f"Final verification: valid={v}, size={len(best_result['full'])}, reason={r}")
    out = {"7": [list(p) for p in best_result['full']]}
    outfile = "/Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/cap_set/z4_tower_best.json"
    with open(outfile, "w") as f:
        json.dump(out, f)
    print(f"  >>> BEATS 236: {best_result['total']} — saved to z4_tower_best.json <<<")
elif best_result and best_result['valid']:
    print(f"  Best valid result: {best_result['total']} (does NOT beat 236)")
else:
    print("No valid cap set beating 236 found by this recipe.")
    print("Recipe executed; honest result: Z4 parity tower collapsed to <=236.")
