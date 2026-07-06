#!/usr/bin/env python3
"""ARENA 2 (R1 breadth) — Sidon sets / Golomb rulers: the machine-checked ground
truth, parallel to capset_verify.py. A Sidon set (B_2 set) is a set of integers
with ALL PAIRWISE DIFFERENCES DISTINCT (equivalently all pairwise sums distinct).
A Golomb ruler is exactly a Sidon set viewed by its length (max-min).

Why this is a good 2nd un-saturatable arena (R1, the ≥2-arena promotion bar):
 - validity is a trivial, certain machine check (no model judgment);
 - it has authoritative reference pegs (Optimal Golomb Ruler lengths, proven k≤28);
 - it cannot saturate: larger k is always a bigger frontier (OGR proven only to ~28).

The verifier is model-independent and certain. The reference OGR lengths below are
load-bearing and tagged UNVERIFIED — the Survey dept must fetch/confirm them before
any SCORED run (per the box: don't assert load-bearing facts from memory).
"""
import sys, json, itertools

# Optimal Golomb ruler length L(k) for k marks (min possible length of a k-mark Sidon set).
# ⚠️ UNVERIFIED-pending-fetch — Survey dept confirms vs distributed.net/Shearer before scoring.
OGR_LENGTH_UNVERIFIED = {2:1, 3:3, 4:6, 5:11, 6:17, 7:25, 8:34, 9:44, 10:55,
                          11:72, 12:85, 13:106, 14:127, 15:151, 16:177}

def is_sidon(marks):
    """Return (valid, reason). marks: iterable of distinct integers."""
    m = list(marks)
    if len(set(m)) != len(m):
        return False, "duplicate marks"
    diffs = {}
    for a, b in itertools.combinations(sorted(m), 2):
        d = b - a
        if d in diffs:
            return False, f"repeated difference {d}: ({diffs[d]}) and ({a},{b})"
        diffs[d] = (a, b)
    return True, "ok"

def score(marks):
    m = sorted(set(marks))
    valid, reason = is_sidon(m)
    k = len(m)
    length = (m[-1] - m[0]) if m else 0
    out = {"k_marks": k, "length": length, "valid": valid, "reason": reason}
    if k in OGR_LENGTH_UNVERIFIED:
        opt = OGR_LENGTH_UNVERIFIED[k]
        out["optimal_length_UNVERIFIED"] = opt
        out["is_optimal_if_ref_correct"] = valid and length == opt
        out["beats_optimal_IMPOSSIBLE"] = valid and length < opt   # would mean ref wrong / bug
    return out

def mian_chowla_greedy(k):
    """Baseline: greedy Sidon set (Mian-Chowla sequence) with k marks, starting at 0.
    Always valid by construction; not optimal length."""
    marks = [0]; diffs = set()
    cand = 1
    while len(marks) < k:
        ok = True; newd = []
        for m in marks:
            d = cand - m
            if d in diffs or d in newd:
                ok = False; break
            newd.append(d)
        if ok:
            marks.append(cand); diffs.update(newd)
        cand += 1
    return marks

if __name__ == "__main__":
    if len(sys.argv) > 1:                 # verify a json list of marks
        print(json.dumps(score(json.load(open(sys.argv[1])))))
    else:                                  # demo the baseline + verifier
        for k in (5, 8, 11, 14):
            r = mian_chowla_greedy(k)
            s = score(r)
            print(f"k={k}: Mian-Chowla greedy length={s['length']} "
                  f"(opt≈{OGR_LENGTH_UNVERIFIED.get(k)}) valid={s['valid']}  marks={r}")
