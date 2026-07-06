#!/usr/bin/env python3
"""SORTNET — frozen EXACT verifier for sorting networks via the 0/1 principle.  kappa = 1.

A sorting network is a fixed sequence of compare-exchange operations (comparators)
that sorts ANY n-element input. The 0/1 principle (Knuth, TAOCP Vol. 3, sec. 5.3.4;
see GROUNDING.md) is the exact certificate:

    *A comparator network sorts all inputs  iff  it sorts all 2^n binary (0/1) inputs.*

So we RE-SIMULATE the candidate network from scratch on EVERY one of the 2^n binary
vectors and check each output is non-decreasing. If all 2^n sort, the network
provably sorts every input over every ordered set — an exact mathematical
certificate, NOT a sampled test.

Why this qualifies as a kappa=1 weapon verifier (the v5 kappa-gate, non-gameable):
  * it re-checks the actual returned OBJECT (the comparator list) from scratch;
  * it is independent of the producer (pure simulation; self-reports are ignored);
  * a false "valid" is structurally impossible — the 2^n sweep is EXHAUSTIVE over the
    0/1 cube, so a network tuned to sort a hand-picked sample is CAUGHT (see _selftest);
  * the score (#comparators, depth) is a STRUCTURAL property of the object, not a
    number returned on seen data -> not overfittable. A valid network with size BELOW
    the proven optimum flags a BUG, never a "win".

Honest ceiling: it certifies "this comparator list sorts all n-element inputs" plus
its size/depth. It does NOT certify OPTIMALITY (smallest). Optimality needs a proven
lower bound from the literature; we carry KNOWN_OPTIMAL_SIZE (fetched, GROUNDING.md)
and LABEL any size-match a reproduction — never a discovery.

A verifier that cannot FAIL is not a verifier: see _selftest() — it passes a
known-good network, CATCHES a known-broken one, and REJECTS a gaming attempt (a
network that sorts a chosen SAMPLE of inputs but not the full 0/1 cube).
"""
import sys
import json

# Proven-OPTIMAL comparator counts (SIZE) for small n — fetched, see GROUNDING.md.
#   n<=8 : Floyd & Knuth 1966 (proved optimal).
#   n=9,10: Codish, Cruz-Filipe, Frank & Schneider-Kamp 2014.
# These are used ONLY to label a valid network as a reproduction-of-optimum or to
# flag an impossible (below-optimum => bug) result. They are never a "win" gate.
KNOWN_OPTIMAL_SIZE = {1: 0, 2: 1, 3: 3, 4: 5, 5: 9, 6: 12, 7: 16, 8: 19, 9: 25, 10: 29}

CEILING = ("SORTNET certifies a comparator list sorts ALL n-element inputs (0/1 principle, "
           "exact) plus its size/depth. It does NOT prove optimality — a size match to "
           "KNOWN_OPTIMAL_SIZE is labeled a reproduction, never a discovery.")


def apply_network(network, vec):
    """Run the comparator list on `vec`; return the network's output.
    A comparator (i, j) is a compare-exchange placing min at i, max at j."""
    v = list(vec)
    for (i, j) in network:
        lo, hi = (i, j) if i < j else (j, i)
        if v[lo] > v[hi]:
            v[lo], v[hi] = v[hi], v[lo]
    return v


def _is_sorted(v):
    return all(v[k] <= v[k + 1] for k in range(len(v) - 1))


def network_depth(network, n):
    """Parallel-layer depth: each comparator enters the earliest layer in which
    neither of its two wires is already busy."""
    free_layer = [0] * n  # earliest layer each wire is free
    depth = 0
    for (i, j) in network:
        layer = max(free_layer[i], free_layer[j])
        free_layer[i] = free_layer[j] = layer + 1
        depth = max(depth, layer + 1)
    return depth


def verify_sorting_network(network, n, exhaustive_limit=22):
    """EXACT 0/1-principle verifier.

    network: list of (i, j) comparators, 0-indexed wires.
    n      : number of input wires.
    exhaustive_limit: refuse (ABSTAIN) above this n — 2^n would be astronomical.
                      We never SAMPLE (sampling is gameable); we abstain instead.

    Returns a verdict dict; valid=True iff the network sorts all 2^n binary inputs.
    """
    # --- structural validation of the object itself ---
    if not isinstance(n, int) or n < 1:
        return {"sub_weapon": "SORTNET", "kappa": 1, "valid": False,
                "verdict": "MALFORMED", "note": f"n must be a positive int, got {n!r}",
                "ceiling_note": CEILING}
    for c in network:
        if (not isinstance(c, (tuple, list)) or len(c) != 2):
            return {"sub_weapon": "SORTNET", "kappa": 1, "valid": False,
                    "verdict": "MALFORMED", "note": f"comparator {c!r} is not a pair",
                    "ceiling_note": CEILING}
        i, j = c
        if not (0 <= i < n and 0 <= j < n) or i == j:
            return {"sub_weapon": "SORTNET", "kappa": 1, "valid": False,
                    "verdict": "MALFORMED",
                    "note": f"comparator {(i, j)} out of range [0,{n}) or i==j",
                    "ceiling_note": CEILING}

    if n > exhaustive_limit:
        return {"sub_weapon": "SORTNET", "kappa": 1, "valid": None,
                "verdict": "ABSTAIN_TOO_LARGE", "n": n,
                "note": f"2^{n} inputs exceeds exhaustive_limit={exhaustive_limit}; "
                        "refusing to SAMPLE (sampling is gameable). Raise the limit "
                        "deliberately if you can afford the full sweep.",
                "ceiling_note": CEILING}

    # --- exhaustive 0/1 sweep (the exact certificate) ---
    failed = None
    for mask in range(1 << n):
        vec = [(mask >> k) & 1 for k in range(n)]
        if not _is_sorted(apply_network(network, vec)):
            failed = vec
            break

    valid = failed is None
    size = len(network)
    res = {
        "sub_weapon": "SORTNET", "kappa": 1,
        "n": n, "num_comparators": size, "depth": network_depth(network, n),
        "valid": bool(valid),
        "verdict": "VALID_SORTING_NETWORK" if valid else "NOT_A_SORTING_NETWORK",
        "inputs_checked": 1 << n,
        "first_failing_binary_input": failed,
        "note": (f"sorts all {1 << n} binary inputs => sorts every input (0/1 principle)"
                 if valid else
                 f"fails on binary input {failed} -> not a sorting network"),
        "ceiling_note": CEILING,
    }
    # optimality annotation (reproduction labeling / bug flag) — never a discovery claim
    opt = KNOWN_OPTIMAL_SIZE.get(n)
    if valid and opt is not None:
        res["known_optimal_size"] = opt
        if size == opt:
            res["optimality"] = "MATCHES_KNOWN_OPTIMUM"          # labeled reproduction
        elif size > opt:
            res["optimality"] = "VALID_BUT_ABOVE_OPTIMUM"
        else:  # size < proven optimum is IMPOSSIBLE => a bug, not a discovery
            res["optimality"] = "BELOW_PROVEN_OPTIMUM_=>_BUG"
            res["beats_optimal_IMPOSSIBLE"] = True
    return res


def _selftest():
    """passes-good / catches-broken / rejects-gaming / abstains-too-large."""
    # --- passes-good: the optimal 5-comparator 4-sorter ---
    good = [(0, 1), (2, 3), (0, 2), (1, 3), (1, 2)]
    r = verify_sorting_network(good, 4)
    assert r["valid"] is True, r
    assert r["verdict"] == "VALID_SORTING_NETWORK", r
    assert r["num_comparators"] == 5 and r["optimality"] == "MATCHES_KNOWN_OPTIMUM", r

    # --- catches-broken: drop the final comparator -> no longer sorts ---
    broken = [(0, 1), (2, 3), (0, 2), (1, 3)]
    rb = verify_sorting_network(broken, 4)
    assert rb["valid"] is False, rb
    assert rb["first_failing_binary_input"] is not None, rb

    # --- rejects-gaming: a network that sorts a SAMPLE but not the whole cube ---
    # Show a naive SAMPLE-checker would be fooled, but the exhaustive verifier is not.
    # `broken` sorts many binary inputs; collect the sample it DOES sort:
    sample_sorted = [[(m >> k) & 1 for k in range(4)] for m in range(16)
                     if _is_sorted(apply_network(broken, [(m >> k) & 1 for k in range(4)]))]
    assert len(sample_sorted) > 0, "expected some inputs to coincidentally sort"
    # a gameable sample-checker restricted to `sample_sorted` would PASS `broken`...
    naive_sample_pass = all(_is_sorted(apply_network(broken, v)) for v in sample_sorted)
    assert naive_sample_pass is True, "sample-checker should be fooled by construction"
    # ...but the EXHAUSTIVE 0/1 verifier CATCHES it:
    assert verify_sorting_network(broken, 4)["valid"] is False, "exhaustive must catch it"

    # --- malformed: out-of-range comparator ---
    rm = verify_sorting_network([(0, 9)], 4)
    assert rm["verdict"] == "MALFORMED", rm

    # --- abstain when 2^n is too large (never sample) ---
    ra = verify_sorting_network([(0, 1)], 30)
    assert ra["verdict"] == "ABSTAIN_TOO_LARGE", ra

    print("SORTNET   selftest: PASS (good->valid, broken->caught, sample-gaming->caught, "
          "malformed->flagged, too-large->abstain)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 3:
        net = json.load(open(sys.argv[1]))
        n = int(sys.argv[2])
        print(json.dumps(verify_sorting_network([tuple(c) for c in net], n), indent=2))
    else:
        print("usage: sortnet_verify.py selftest | <network.json> <n>")
