#!/usr/bin/env python3
"""Independent ORACLE for the codeforge sorting-network gate.

This is a FROM-SCRATCH exhaustive 0/1 enumerator, authored independently of the codeforge
synthesis engine AND of the codeforge verifier. By the 0/1 principle (Knuth TAOCP vol.3,
GROUNDING.md), a comparator network sorts all inputs IFF it sorts all 2^n binary inputs.
Re-implementing this enumeration is methodologically foreign to the network synthesizer ->
a genuine independent oracle for the FALSE-ACCEPT hunt.

It is deliberately written DIFFERENTLY from the codeforge verifier (different loop shape,
different sortedness check) so a shared coding blind-spot is unlikely.
"""


def _apply(network, vec):
    """Apply the comparator list; comparator (i,j) puts min at i, max at j.
    Independent re-impl: build a fresh list, swap in place by value comparison."""
    v = list(vec)
    for (i, j) in network:
        a, b = v[i], v[j]
        if a > b:                       # min->i, max->j
            v[i], v[j] = b, a
    return v


def _is_nondecreasing(v):
    """Independent sortedness check: compare adjacent via a fold, not all()."""
    prev = None
    for x in v:
        if prev is not None and x < prev:
            return False
        prev = x
    return True


def sorts_all_binary(network, n):
    """TRUTH: does `network` sort every one of the 2^n binary inputs? (exact)."""
    for mask in range(2 ** n):
        vec = [(mask >> k) & 1 for k in range(n)]
        if not _is_nondecreasing(_apply(network, vec)):
            return False
    return True


def truth_correct_or_wrong(obj):
    """Oracle interface for crucible_harness.Oracle: obj={'network':..., 'n':...}.
    Returns 'CORRECT' (it IS a valid sorting network) / 'WRONG' (it is NOT) / None
    (out of the oracle's hermetic domain -- malformed / too large)."""
    network, n = obj.get("network"), obj.get("n")
    if not isinstance(n, int) or n < 1 or n > 12:
        return None                     # oracle declines outside its safe enumeration range
    try:
        for c in network:
            i, j = c
            if not (0 <= i < n and 0 <= j < n) or i == j:
                return None             # malformed comparator -> oracle has no opinion
    except Exception:
        return None
    return "CORRECT" if sorts_all_binary(network, n) else "WRONG"


if __name__ == "__main__":
    good = [(0, 1), (2, 3), (0, 2), (1, 3), (1, 2)]      # optimal 4-sorter
    assert sorts_all_binary(good, 4) is True
    bad = [(0, 1), (2, 3), (0, 2), (1, 3)]               # missing (1,2) -> not a sorter
    assert sorts_all_binary(bad, 4) is False
    print("sortnet_oracle smoke: PASS (good 4-sorter CORRECT; missing-(1,2) WRONG)")
