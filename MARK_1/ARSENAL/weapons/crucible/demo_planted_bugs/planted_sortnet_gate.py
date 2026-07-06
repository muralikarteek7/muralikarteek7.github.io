#!/usr/bin/env python3
"""A COPY of the codeforge sorting-network gate with ONE blind-planted SUBTLE bug.

This is a stand-in for "a different agent plants a hole in a copy of a real gate and does
NOT reveal where" (kickoff §3a). The copy is faithful to codeforge/sortnet_verify.py EXCEPT
for a single subtle defect of a class that actually appears in the arsenal's history (an
off-by-one in a range/boundary check).

THE PLANTED BUG (deliberately subtle, low-signal -- an off-by-one in the EXPONENT):
    the exhaustive 0/1 sweep iterates `range(1 << (n - 1))` instead of `range(1 << n)`.
    This looks almost right -- it is a single character off (`n - 1` vs `n`) and the loop
    still "sweeps a power-of-two range of masks". But it only checks the LOWER HALF of the
    2^n binary inputs (those with the top wire = 0). Any network that sorts every lower-half
    input but FAILS on some input with the top bit set is then wrongly ACCEPTED -- a real
    false-accept. The obvious cases (e.g. the optimal 4-sorter) still pass, so the hole is
    low-signal; only an adversarial search over networks surfaces a leaker. (This mirrors a
    real arsenal-history bug class: an off-by-one in a range/boundary check.)

CRUCIBLE is NOT told which masks are skipped. Its FALSE-ACCEPT hunt must EXHIBIT a network
the independent oracle proves is NOT a sorting network but this gate ACCEPTS.

verdict function: verify_sorting_network_PLANTED(network, n) -> dict with 'valid' bool.
"""


def _apply_network(network, vec):
    v = list(vec)
    for (i, j) in network:
        if v[i] > v[j]:
            v[i], v[j] = v[j], v[i]
    return v


def _is_sorted(v):
    return all(v[k] <= v[k + 1] for k in range(len(v) - 1))


def verify_sorting_network_PLANTED(network, n, exhaustive_limit=22):
    """Faithful copy of the codeforge verifier with ONE subtle off-by-one in the sweep."""
    if not isinstance(n, int) or n < 1:
        return {"valid": False, "verdict": "MALFORMED", "note": f"n must be positive int, got {n!r}"}
    for c in network:
        if not isinstance(c, (tuple, list)) or len(c) != 2:
            return {"valid": False, "verdict": "MALFORMED", "note": f"comparator {c!r} not a pair"}
        i, j = c
        if not (0 <= i < n and 0 <= j < n) or i == j:
            return {"valid": False, "verdict": "MALFORMED",
                    "note": f"comparator {(i, j)} out of range or i==j"}
    if n > exhaustive_limit:
        return {"valid": None, "verdict": "ABSTAIN_TOO_LARGE", "n": n}

    failed = None
    # ---- THE PLANTED BUG: should be `range(1 << n)`. Checks only the lower half. ----
    for mask in range(1 << (n - 1)):
        vec = [(mask >> k) & 1 for k in range(n)]
        if not _is_sorted(_apply_network(network, vec)):
            failed = vec
            break
    valid = failed is None
    return {"valid": bool(valid),
            "verdict": "VALID_SORTING_NETWORK" if valid else "NOT_A_SORTING_NETWORK",
            "first_failing_binary_input": failed}
