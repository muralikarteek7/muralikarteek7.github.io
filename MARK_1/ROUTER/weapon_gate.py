#!/usr/bin/env python3
"""weapon_gate.py — the non-waivable honesty wrapper between any WEAPON and emission.

Spec: Next/BOX_ARMOR_WEAPONS.md §7. Every weapon result passes through gate():
  1. VERIFIER-GATED   — re-run the independent verifier on the ACTUAL returned object,
                        never on the weapon's summary. verifier != producer.
  2. NO-SELF-REPORT   — discard every scalar the weapon asserts; recompute from the
                        verified object. No object returned -> ABSTAIN, never the number.
  3. KNOWN-vs-OPEN    — KNOWN cell: 'honest reproduction' iff verified == KNOWN_MAX.
                        OPEN cell: any 'solved/optimal' claim HARD-VETOED unless the
                        object passes the verifier AND strictly beats KNOWN_LB — and even
                        then it is a NEW LOWER BOUND, never 'solved'.
                        verified > KNOWN_MAX -> BUG flag (beats_optimal_IMPOSSIBLE).
  4. AGREEMENT-IS-RISK— a vote-only claim forces a machine/source check before emit.
  5. PROVENANCE       — every emitted claim carries the verifier verdict + cost metrics.
"""
import sys, os, time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "benchmarks", "math"))

EMIT, VETO, ABSTAIN, BUG = "EMIT", "VETO", "ABSTAIN", "BUG"


def gate(arena, returned_object, self_report=None, claims_optimal=False,
         producer="weapon", verifier_fn=None, known=None, provenance=None):
    """Run the honesty gate. Returns a dict {verdict, verified, label, provenance}.

    arena:           'capset' | 'sidon' (selects the independent machine verifier)
    returned_object: the ACTUAL object (list of points / marks) or None
    self_report:     whatever the weapon asserted (size, 'optimal', confidence) — DISCARDED
    claims_optimal:  did the producer claim optimality / a solve?
    verifier_fn:     override verifier (must be independent of the producer)
    known:           dict like {'status':'KNOWN','max':112} or {'status':'OPEN','lb':236}
    """
    t0 = time.time()
    out = {"verdict": None, "self_report_discarded": self_report is not None,
           "producer": producer, "provenance": provenance or {}}

    # rule 2 — no object, no number. The claimed scalar is never emitted.
    if returned_object is None or (hasattr(returned_object, "__len__") and len(returned_object) == 0):
        out["verdict"] = ABSTAIN
        out["label"] = "ABSTAIN: weapon returned no object; its self-reported result is discarded"
        return out

    # rule 1 — independent machine verification of the actual object
    if verifier_fn is None:
        verifier_fn = _default_verifier(arena)
    verified = verifier_fn(returned_object)
    out["verified"] = verified
    out["provenance"].update({"verifier": verifier_fn.__name__, "producer": producer,
                              "producer_is_verifier": False,
                              "verify_secs": round(time.time() - t0, 3)})
    if not verified.get("valid", False):
        out["verdict"] = VETO
        out["label"] = f"VETO: object failed independent verification ({verified.get('reason')})"
        return out

    size = verified["size"] if "size" in verified else verified.get("length")

    # rule 3 — known-vs-open veto
    if known and known.get("status") == "KNOWN":
        kmax = known["max"]
        better = (size > kmax) if known.get("direction", "max") == "max" else (size < kmax)
        if better:
            out["verdict"] = BUG
            out["label"] = (f"BUG (beats_optimal_IMPOSSIBLE): verified {size} beats proven optimum "
                            f"{kmax} — encoding/verifier bug, NOT a win")
            return out
        hit = (size == kmax)
        out["verdict"] = EMIT
        out["label"] = (f"HONEST REPRODUCTION of the proven optimum {kmax}" if hit
                        else f"verified sub-optimal object ({size} vs proven {kmax}); no optimality claim")
        if claims_optimal and not hit:
            out["verdict"] = VETO
            out["label"] = f"VETO: producer claimed optimal but verified {size} != proven {kmax}"
        return out

    if known and known.get("status") == "OPEN":
        lb = known["lb"]
        if claims_optimal:
            if size > lb:
                out["verdict"] = EMIT
                out["label"] = (f"NEW VERIFIED LOWER BOUND {size} > known LB {lb} — a record, "
                                f"NEVER 'solved' (the problem stays OPEN)")
            else:
                out["verdict"] = VETO
                out["label"] = (f"HARD VETO: 'solved/optimal' claimed on an OPEN problem with a "
                                f"verified object of {size} <= known LB {lb}")
            return out
        out["verdict"] = EMIT
        out["label"] = (f"verified object of {size} on an OPEN problem (known LB {lb}); "
                        f"reported as a witness, no record/solve claim"
                        if size <= lb else
                        f"NEW VERIFIED LOWER BOUND {size} > {lb}; problem stays OPEN")
        return out

    # audit D5 fix: an optimality claim with NO known-status consult is never emitted —
    # 'optimal' requires a grounded KNOWN/OPEN context to be checkable at all.
    if claims_optimal:
        out["verdict"] = VETO
        out["label"] = ("VETO: optimality claimed but no known-status (KNOWN/OPEN) context supplied — "
                        "consult known_status_lookup before any optimality claim")
        return out
    out["verdict"] = EMIT
    out["label"] = f"verified object (size {size}); no known peg supplied"
    return out


def _default_verifier(arena):
    if arena == "capset":
        from capset_verify import score as cap_score
        def capset_verifier(obj):
            pts = [tuple(p) for p in obj]
            return cap_score(pts, len(pts[0]))
        return capset_verifier
    if arena == "sidon":
        from arena2_sidon_verify import score as sidon_score
        def sidon_verifier(obj):
            return sidon_score(list(obj))
        return sidon_verifier
    raise ValueError(f"unknown arena {arena}")


if __name__ == "__main__":
    import json
    json_path = os.path.join(_HERE, "benchmarks", "math", "cap_n6_size112.json")
    pts = json.load(open(json_path))["6"]
    r = gate("capset", pts, self_report={"size": 112, "confidence": "high"},
             producer="build_112_pathA", known={"status": "KNOWN", "max": 112})
    print(json.dumps({k: v for k, v in r.items() if k != "verified"} |
                     {"verified_size": r["verified"]["size"]}, indent=2))
