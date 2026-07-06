#!/usr/bin/env python3
"""CRUCIBLE probe — frontier_capset gate (capset_verify.is_capset).

TARGET SLICE (kappa=1): "is this set genuinely a cap (3-AP-free) of the stated size?"
A FALSE-ACCEPT = a passing-but-INVALID cap: the gate says valid=True on a set that
actually contains 3 distinct points a,b,c with a+b+c == 0 (mod 3), OR whose distinct
size does not match the stated size.

REAL GATE (black-box, imported, NOT re-implemented):
    /Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/cap_set/capset_verify.py
    is_capset(points) -> (valid: bool, reason: str)
    The gate uses the PAIRWISE "implied-third" method: for each unordered pair (a,b)
    it computes c=(-a-b)%3 and checks c in set, c!=a, c!=b.

INDEPENDENT ORACLE (foreign mechanism, authored from scratch here):
    Method = BRUTE-FORCE enumeration over all C(N,3) ordered-free triples, testing
    (a[d]+b[d]+c[d])%3==0 for all d. This is a DIFFERENT algorithm than the gate's
    pairwise implied-third lookup (different control flow, no "implied c" shortcut),
    so judging the gate with it is non-circular. The oracle ALSO checks the stated
    size and coordinate validity, so it covers the full "cap of stated size" claim.

We run FULL-DIFFERENTIAL: false-accept, false-reject, metamorphic, abstain/crash.
"""
import sys, json, itertools, random

GATE_DIR = "/Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/cap_set"
HARNESS_DIR = "/Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/crucible"
sys.path.insert(0, GATE_DIR)
sys.path.insert(0, HARNESS_DIR)

# --- import the REAL gate (black-box) ---
import capset_verify  # the real weapon gate
from crucible_harness import (
    GateAdapter, Oracle, false_accept_hunt, false_reject_hunt,
    metamorphic_hunt, abstain_crash_hunt,
    ACCEPT, REJECT, ABSTAIN, ERROR, Kill, Survived,
)

REAL_GATE_FN = capset_verify.is_capset  # the kappa=1 verdict function we are testing


# --------------------------------------------------------------------------- #
# GATE OBJECT SHAPE.
#   obj = {"points": [...], "stated_size": int}.
#   The gate fn (is_capset) takes only `points`. To probe the FULL "cap of the
#   stated size" claim with the same real gate, we wrap is_capset in a thin
#   verdict fn that (1) calls the REAL gate for cap-ness and (2) confirms the
#   distinct-point count equals stated_size. This wrapper adds NO cap-logic of
#   its own -- the 3-AP decision is 100% the real gate. (If you prefer the pure
#   cap-ness slice, stated_size==None skips the size check.)
# --------------------------------------------------------------------------- #
def gate_fn(points, stated_size=None):
    valid, reason = REAL_GATE_FN(points)        # <-- the REAL gate decides cap-ness
    if not valid:
        return {"valid": False, "reason": reason}
    if stated_size is not None:
        distinct = len(set(tuple(p) for p in points))
        if distinct != stated_size:
            return {"valid": False, "reason": f"size {distinct} != stated {stated_size}"}
    return {"valid": True, "reason": reason}


def gate_to_verdict(raw):
    # The gate is kappa=1 (exact arithmetic, no abstain): valid -> ACCEPT, else REJECT.
    return ACCEPT if raw["valid"] else REJECT


gate = GateAdapter("frontier_capset", gate_fn, gate_to_verdict)


# --------------------------------------------------------------------------- #
# INDEPENDENT ORACLE — brute-force C(N,3) triple enumeration (foreign mechanism).
# Returns CORRECT iff: all coords in {0,1,2}, all same length, NO duplicate points,
# distinct-size == stated_size (when stated), and NO 3 distinct pts sum 0 mod 3.
# --------------------------------------------------------------------------- #
def oracle_truth(obj):
    points = obj["points"]
    stated_size = obj.get("stated_size", None)
    pts = [tuple(p) for p in points]
    if not pts:
        # empty set: a valid cap of size 0. Independent decision.
        if stated_size is not None and stated_size != 0:
            return "WRONG"
        return "CORRECT"
    n = len(pts[0])
    # coordinate validity + uniform dimension
    for p in pts:
        if len(p) != n or any(c not in (0, 1, 2) for c in p):
            return "WRONG"
    S = set(pts)
    # duplicate check
    if len(S) != len(pts):
        return "WRONG"
    # stated-size check (full "cap of stated size" claim)
    if stated_size is not None and len(S) != stated_size:
        return "WRONG"
    # FOREIGN MECHANISM: brute force over all C(N,3) distinct triples.
    distinct = list(S)
    for a, b, c in itertools.combinations(distinct, 3):
        if all((a[d] + b[d] + c[d]) % 3 == 0 for d in range(n)):
            return "WRONG"   # a forbidden 3-AP exists -> NOT a cap
    return "CORRECT"


# --------------------------------------------------------------------------- #
# CONTROL GRID. >=3 known-good caps + >=3 known-bad sets, spanning the regime
# (different n, different sizes, interior + boundary). Authored independently.
# --------------------------------------------------------------------------- #
def _known_good_controls():
    # n=1: {(0,),(1,)} is a cap (no triple possible with 2 points)
    g1 = {"points": [(0,), (1,)], "stated_size": 2}
    # n=2: a genuine max 4-cap in F_3^2 (verified: no 3 of these sum to 0 mod 3).
    g2 = {"points": [(0, 0), (0, 1), (1, 0), (1, 1)], "stated_size": 4}
    # n=5: the canonical verified 45-cap from verified_caps_45_90.py
    import verified_caps_45_90 as vc
    g3 = {"points": vc.construct_45(), "stated_size": 45}
    # n=6: the verified 90-cap
    g4 = {"points": vc.construct_90(), "stated_size": 90}
    # small: a single point is trivially a cap
    g5 = {"points": [(0, 0, 0)], "stated_size": 1}
    # n=2: a 3-point subset with no line
    g6 = {"points": [(0, 0), (1, 0), (0, 1)], "stated_size": 3}
    return [g1, g2, g3, g4, g5, g6]


def _known_bad_controls():
    # b1: an OBVIOUS line in n=1: 0,1,2 sum to 0 mod 3 -> NOT a cap
    b1 = {"points": [(0,), (1,), (2,)], "stated_size": 3}
    # b2: n=2 line: (0,0),(1,1),(2,2) -> 0+1+2=3==0 each coord -> forbidden triple
    b2 = {"points": [(0, 0), (1, 1), (2, 2)], "stated_size": 3}
    # b3: a valid-looking set but with a planted line in n=3
    b3 = {"points": [(0, 0, 0), (1, 1, 1), (2, 2, 2), (0, 1, 2)], "stated_size": 4}
    # b4: a real cap but WRONG stated size (the size half of the claim)
    b4 = {"points": [(0, 0), (1, 0), (0, 1)], "stated_size": 99}
    # b5: a coordinate out of range (entry =3)
    b5 = {"points": [(0, 0), (3, 0)], "stated_size": 2}
    # b6: duplicate points (size really smaller / not distinct)
    b6 = {"points": [(0, 0), (0, 0), (1, 0)], "stated_size": 3}
    return [b1, b2, b3, b4, b5, b6]


def make_oracle():
    return Oracle(
        "capset-bruteforce-C(N,3)",
        oracle_truth,
        is_independent=True,
        method=("from-scratch BRUTE-FORCE over all C(N,3) distinct triples testing "
                "sum==0 mod 3 per coord (+ coord-validity, distinctness, stated-size). "
                "Foreign to the gate's pairwise implied-third algorithm."),
        controls_good=_known_good_controls(),
        controls_bad=_known_bad_controls(),
    )


# --------------------------------------------------------------------------- #
# CANDIDATE STREAM for FALSE-ACCEPT: try hard to slip an INVALID cap past the gate.
# These are the adversarial cases that would expose a pairwise-method bug:
#   * sets containing a 3-AP where two of the three points coincide structurally
#   * the a==c / b==c edge cases (the gate excludes c==a and c==b -- probe whether
#     a degenerate "AP" with a repeated point fools it)
#   * lines where the "implied third" equals one of the generating pair
#   * near-caps: a known cap PLUS one extra point that creates exactly one line
#   * sets with duplicates that still secretly host a line
#   * larger random near-caps in n=4..7 with an injected line
# --------------------------------------------------------------------------- #
def _all_points(n):
    return list(itertools.product((0, 1, 2), repeat=n))


def _random_cap(n, target, rng, tries=20000):
    """Greedy random cap builder (independent of the gate)."""
    allp = _all_points(n)
    rng.shuffle(allp)
    cap = []
    S = set()
    for p in allp:
        ok = True
        for a in cap:
            c = tuple((-(a[d] + p[d])) % 3 for d in range(n))
            if c in S and c != a and c != p:
                ok = False
                break
        if ok:
            cap.append(p)
            S.add(p)
        if len(cap) >= target:
            break
    return cap


def false_accept_candidates():
    rng = random.Random(20260620)
    out = []

    # (1) Direct lines (must be REJECTED) across several n.
    for n in (1, 2, 3, 4):
        zero = tuple(0 for _ in range(n))
        one = tuple(1 for _ in range(n))
        two = tuple(2 for _ in range(n))
        out.append({"points": [zero, one, two], "stated_size": 3})

    # (2) The degenerate-AP edge cases: a triple where the "third" coincides with a
    #     generator. e.g. a=(0,0), b=(0,0) duplicate -> c=(0,0). The gate's c!=a/c!=b
    #     guard should NOT let a real line through; probe sets engineered so that the
    #     ONLY forbidden triple has a near-coincidence.
    # a+a+a = 0 mod 3 always (3a==0): {(1,1)} alone -> a,a,a not 3 distinct, fine.
    # But {(0,),(1,),(2,)} already covered. Add: a set where c==a for one pair but a
    # genuine OTHER triple exists.
    out.append({"points": [(0, 0), (1, 1), (2, 2), (0, 1), (1, 2), (2, 0)],
                "stated_size": 6})  # two full lines -> must REJECT

    # (3) Known caps with ONE extra point injected to create exactly one line.
    for n in (3, 4, 5, 6, 7):
        target = {3: 9, 4: 20, 5: 45, 6: 90, 7: 50}[n]
        cap = _random_cap(n, target, rng)
        if len(cap) >= 3:
            S = set(cap)
            # find a point NOT in cap that completes a line with some pair -> inject it.
            injected = None
            for a, b in itertools.combinations(cap, 2):
                c = tuple((-(a[d] + b[d])) % 3 for d in range(n))
                if c not in S and c != a and c != b:
                    injected = c
                    break
            if injected is not None:
                bad = cap + [injected]
                out.append({"points": bad, "stated_size": len(set(bad))})
                # also the same but claiming the cap's original (pre-injection) size
                out.append({"points": bad, "stated_size": len(cap)})

    # (4) Sets with a duplicate that ALSO host a line (does the gate's dup-check fire
    #     before/after the line check matters? oracle says WRONG either way).
    out.append({"points": [(0, 0, 0), (0, 0, 0), (1, 1, 1), (2, 2, 2)], "stated_size": 4})
    out.append({"points": [(0, 0, 0), (1, 1, 1), (1, 1, 1), (2, 2, 2)], "stated_size": 3})

    # (5) Larger random near-caps in n=7 with an injected line (the frontier cell).
    for _ in range(8):
        cap = _random_cap(7, 60, rng)
        S = set(cap)
        injected = None
        for a, b in itertools.combinations(cap, 2):
            c = tuple((-(a[d] + b[d])) % 3 for d in range(7))
            if c not in S and c != a and c != b:
                injected = c
                break
        if injected is not None:
            bad = cap + [injected]
            out.append({"points": bad, "stated_size": len(set(bad))})

    # (6) Many small random multisets/subsets in n=2..4 -- pure noise, oracle decides.
    for _ in range(300):
        n = rng.choice([2, 3, 4])
        allp = _all_points(n)
        k = rng.randint(3, min(12, len(allp)))
        pts = rng.sample(allp, k)
        out.append({"points": pts, "stated_size": len(set(pts))})

    return out


def false_reject_candidates():
    """Genuine caps the gate must ACCEPT (over-strictness hunt)."""
    rng = random.Random(99)
    out = []
    # canonical verified caps
    import verified_caps_45_90 as vc
    out.append({"points": vc.construct_45(), "stated_size": 45})
    out.append({"points": vc.construct_90(), "stated_size": 90})
    # the persisted 236-cap (the frontier object) -- a genuine cap by construction
    try:
        d = json.load(open(GATE_DIR + "/cap_n7_size236_CF.json"))
        out.append({"points": [tuple(p) for p in d["7"]], "stated_size": 236})
    except Exception:
        pass
    # many random caps n=2..7
    for _ in range(120):
        n = rng.choice([2, 3, 4, 5, 6, 7])
        cap = _random_cap(n, 10 ** 9, rng)  # maximal greedy cap
        out.append({"points": cap, "stated_size": len(cap)})
    # edge: empty cap, singletons
    out.append({"points": [], "stated_size": 0})
    out.append({"points": [(0, 0, 0)], "stated_size": 1})
    return out


# --------------------------------------------------------------------------- #
# METAMORPHIC transforms — meaning-preserving symmetries of F_3^n that MUST
# preserve cap-ness (and stated_size):
#   T1: coordinate permutation (relabel axes)
#   T2: affine translation x -> x + v (mod 3) for a fixed v
#   T3: per-coordinate value relabeling by an invertible affine map x -> a*x+b mod3
#       (a in {1,2}, b in {0,1,2}) applied coordinate-wise
#   T4: append a constant new coordinate (lifts cap into F_3^{n+1}, size + cap-ness
#       preserved -- a single fixed value never creates a line)
# Each is a bijection/affine embedding so it maps caps<->caps of the SAME size.
# --------------------------------------------------------------------------- #
def _t_permute(obj):
    pts = [tuple(p) for p in obj["points"]]
    if not pts:
        return dict(obj)
    n = len(pts[0])
    perm = list(range(n))
    rng = random.Random(sum(map(sum, pts)) + n)
    rng.shuffle(perm)
    npts = [tuple(p[perm[i]] for i in range(n)) for p in pts]
    return {"points": npts, "stated_size": obj.get("stated_size")}


def _t_translate(obj):
    pts = [tuple(p) for p in obj["points"]]
    if not pts:
        return dict(obj)
    n = len(pts[0])
    v = tuple((sum(p[i] for p in pts) % 3) for i in range(n))
    npts = [tuple((p[i] + v[i]) % 3 for i in range(n)) for p in pts]
    return {"points": npts, "stated_size": obj.get("stated_size")}


def _t_affine_relabel(obj):
    pts = [tuple(p) for p in obj["points"]]
    if not pts:
        return dict(obj)
    n = len(pts[0])
    # invertible affine x -> 2*x + 1 mod 3 (a=2 is a unit in F_3), per coordinate
    npts = [tuple((2 * p[i] + 1) % 3 for i in range(n)) for p in pts]
    return {"points": npts, "stated_size": obj.get("stated_size")}


def _t_lift(obj):
    pts = [tuple(p) for p in obj["points"]]
    npts = [p + (0,) for p in pts]
    return {"points": npts, "stated_size": obj.get("stated_size")}


def metamorphic_seeds():
    rng = random.Random(7)
    seeds = []
    import verified_caps_45_90 as vc
    seeds.append({"points": vc.construct_45(), "stated_size": 45})
    seeds.append({"points": vc.construct_90(), "stated_size": 90})
    # a non-cap seed too (so the transform must preserve the REJECT verdict)
    seeds.append({"points": [(0, 0), (1, 1), (2, 2)], "stated_size": 3})
    seeds.append({"points": [(0, 0, 0), (1, 1, 1), (2, 2, 2), (0, 1, 2)], "stated_size": 4})
    for _ in range(20):
        n = rng.choice([2, 3, 4, 5])
        cap = _random_cap(n, 10 ** 9, rng)
        seeds.append({"points": cap, "stated_size": len(cap)})
    return seeds


def metamorphic_transforms():
    return [
        ("coord-permute", _t_permute),
        ("affine-translate", _t_translate),
        ("affine-relabel(2x+1)", _t_affine_relabel),
        ("lift-to-F3^{n+1}", _t_lift),
    ]


# --------------------------------------------------------------------------- #
# ABSTAIN/CRASH — malformed inputs. The gate has NO abstain; the SAFE outcomes
# are REJECT (it catches the malformation) or ERROR (a guarded crash). A silent
# ACCEPT on garbage is the bug.
# --------------------------------------------------------------------------- #
def malformed_inputs():
    safe = {ABSTAIN, REJECT, ERROR}
    return [
        ("coordinate value =3 (out of F_3)", {"points": [(0, 0), (3, 0)]}, safe),
        ("coordinate value =-1", {"points": [(0, 0), (-1, 0)]}, safe),
        ("ragged dimensions", {"points": [(0, 0), (0, 0, 0)]}, safe),
        ("non-int coordinate", {"points": [(0, 0), (0.5, 0)]}, safe),
        ("string coordinate", {"points": [(0, 0), ("a", 0)]}, safe),
        ("None in points", {"points": [(0, 0), None]}, safe),
        ("points is None", {"points": None}, safe),
        ("points is int", {"points": 5}, safe),
        ("nested wrong type", {"points": [[0, [1]], [1, 0]]}, safe),
    ]


# --------------------------------------------------------------------------- #
def main():
    oracle = make_oracle()
    sane, detail = oracle.is_sane()
    print("=== ORACLE SANITY ===")
    print(json.dumps({"sane": sane, "detail": detail}))
    if not sane:
        print("ORACLE NOT SANE -> cannot ship a KILL from false-accept/reject hunts.")

    cov = ("lines + injected-line near-caps (n=1..7) + dup-with-line + random "
           "subsets n=2..4 + frontier n=7 near-caps + size-mismatch claims")

    print("\n=== FALSE-ACCEPT HUNT ===")
    fa_cands = false_accept_candidates()
    print(json.dumps({"candidates": len(fa_cands)}))
    fa = false_accept_hunt(gate, oracle, fa_cands, coverage_note=cov)
    print(json.dumps(fa.to_dict()))

    print("\n=== FALSE-REJECT HUNT ===")
    fr_cands = false_reject_candidates()
    print(json.dumps({"candidates": len(fr_cands)}))
    fr = false_reject_hunt(gate, oracle, fr_cands,
                           coverage_note="verified 45/90/236-caps + random maximal caps n=2..7 + empty/singleton")
    print(json.dumps(fr.to_dict()))

    print("\n=== METAMORPHIC HUNT (oracle-validated transforms) ===")
    seeds = metamorphic_seeds()
    print(json.dumps({"seeds": len(seeds), "transforms": 4}))
    mm = metamorphic_hunt(gate, seeds, metamorphic_transforms(), oracle=oracle)
    print(json.dumps(mm.to_dict()))

    print("\n=== ABSTAIN/CRASH HUNT ===")
    ac = abstain_crash_hunt(gate, malformed_inputs())
    print(json.dumps(ac.to_dict()))

    # overall
    kills = [r for r in (fa, fr, mm, ac) if isinstance(r, Kill)]
    print("\n=== SUMMARY ===")
    print(json.dumps({
        "any_kill": bool(kills),
        "fa": "KILL" if isinstance(fa, Kill) else "SURVIVED",
        "fr": "KILL" if isinstance(fr, Kill) else "SURVIVED",
        "mm": "KILL" if isinstance(mm, Kill) else "SURVIVED",
        "ac": "KILL" if isinstance(ac, Kill) else "SURVIVED",
    }))


if __name__ == "__main__":
    main()
