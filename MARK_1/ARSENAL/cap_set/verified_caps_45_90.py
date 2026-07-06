# Cap sets in F_3^n. See module docstring for the honesty disclosure on n=6.
#
# VERIFIED (machine-checked here): construct_45() returns a valid 45-cap in F_3^5
# (= proven maximum A_5), and construct_90() returns a valid 90-cap in F_3^6
# built as the direct product (45-cap) x {0,1}.
#
# NOT DELIVERED: an explicit verified 112-cap. I could not produce coordinates I can
# stand behind. See note at bottom. construct_112() raises rather than return a bluff.

CAP45 = [
 [0,0,0,0,0],[1,1,2,1,0],[1,1,2,1,2],[0,0,0,1,2],[1,2,0,0,2],[1,2,0,1,0],
 [0,0,1,0,2],[0,0,1,2,0],[0,0,2,0,0],[0,0,2,0,2],[1,2,1,1,2],[1,2,2,0,2],
 [0,1,0,1,0],[1,2,2,2,0],[0,1,0,1,2],[1,2,2,2,1],[0,1,0,2,1],[2,0,0,0,1],
 [2,0,0,1,2],[0,1,2,0,2],[0,1,2,1,0],[0,1,2,1,1],[0,2,0,0,1],[0,2,0,1,0],
 [2,0,2,2,2],[2,1,0,0,0],[0,2,1,0,0],[0,2,1,0,2],[2,1,0,1,2],[0,2,2,1,1],
 [0,2,2,1,2],[1,0,0,0,0],[1,0,0,0,1],[2,1,2,2,0],[1,0,0,2,2],[1,0,1,0,1],
 [1,0,1,2,0],[2,2,1,1,0],[1,0,2,2,0],[2,2,2,1,0],[1,1,0,0,2],[1,1,0,1,0],
 [2,2,2,1,2],[1,1,1,0,2],[1,1,2,0,1],
]

def _is_cap(points):
    d = len(points[0]); S = set(map(tuple, points)); P = list(S)
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            a, b = P[i], P[j]
            c = tuple((-(a[k] + b[k])) % 3 for k in range(d))
            if c != a and c != b and c in S:
                return False
    return True

def construct_45():
    """Returns a verified maximum cap of size 45 in F_3^5."""
    return [tuple(p) for p in CAP45]

def construct_90():
    """Returns a verified 90-cap in F_3^6 = (45-cap) x {0,1} on the last coordinate.
    Valid because the last-coordinate set {0,1} contains no 3-term line."""
    return [tuple(p) + (e,) for p in CAP45 for e in (0, 1)]

def construct_112():
    raise NotImplementedError(
        "No verified explicit 112-cap available; see module note. "
        "Best verified objects: construct_45() (=45) and construct_90() (=90)."
    )

if __name__ == "__main__":
    c45 = construct_45()
    assert len(c45) == 45 and _is_cap(c45)
    c90 = construct_90()
    assert len(c90) == 90 and _is_cap(c90)
    print("45-cap OK:", len(c45), "valid:", _is_cap(c45))
    print("90-cap OK:", len(c90), "valid:", _is_cap(c90))
