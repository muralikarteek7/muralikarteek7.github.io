#!/usr/bin/env python3
"""FACTHARNESS router / firewall -- the institutionalized fabrication firewall.

Every shipped prose claim is routed through FACTHARNESS: ground or abstain.
Departments call ground() directly for one claim; the orchestrator calls
firewall() over the full set of claims it is about to ship and BLOCKS shipping if
any claim flags fabrication or fails to ground.

A claim is shippable iff its overall verdict is in SHIPPABLE. FABRICATION_FLAG and
CONTRADICTED_BY_SOURCE block; ABSTAIN means "ship only with an explicit unverified
label" (the orchestrator decides) -- it is NOT silently treated as grounded.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from factharness import ground

# verdicts the firewall will let ship without an unverified-label
SHIPPABLE = {"GROUNDED"}
# verdicts that ship ONLY behind an explicit unverified / weaker-evidence label
NEEDS_LABEL = {"GROUNDED_BY_JUDGMENT", "ABSTAIN"}
# verdicts that BLOCK shipping outright
BLOCKING = {"FABRICATION_FLAG", "CONTRADICTED_BY_SOURCE"}


def ground_all(claims):
    """Route a list of claim dicts; return [(claim_text, result), ...]."""
    return [(c.get("text") if isinstance(c, dict) else c, ground(c)) for c in claims]


def firewall(claims):
    """The shipping gate. Returns a ship/block decision over a batch of prose claims.

    {
      "ship_ok": bool,                 # True iff NOTHING is BLOCKING
      "grounded":  [...],              # GROUNDED -> ship freely
      "needs_label": [...],            # GROUNDED_BY_JUDGMENT / ABSTAIN -> ship behind unverified label
      "blocked": [...],                # FABRICATION_FLAG / CONTRADICTED -> must NOT ship as stated
    }
    """
    grounded, needs_label, blocked = [], [], []
    for c in claims:
        r = ground(c)
        rec = {"text": r["claim"], "overall": r["overall"],
               "candidate_causes": r.get("candidate_causes")}
        if r["overall"] in BLOCKING:
            blocked.append(rec)
        elif r["overall"] in NEEDS_LABEL:
            needs_label.append(rec)
        else:
            grounded.append(rec)
    return {"ship_ok": len(blocked) == 0,
            "grounded": grounded, "needs_label": needs_label, "blocked": blocked,
            "rule": "FACTHARNESS firewall: GROUNDED ships; GROUNDED_BY_JUDGMENT/ABSTAIN ship "
                    "ONLY behind an explicit unverified label; FABRICATION_FLAG/CONTRADICTED "
                    "BLOCK shipping. Grounded != true; flag != fraud."}


if __name__ == "__main__":
    if len(sys.argv) == 2:
        claims = json.load(open(sys.argv[1]))
        print(json.dumps(firewall(claims), indent=2))
    else:
        # tiny smoke test of the firewall on mixed claims
        _SRC = ("Only 7 of the 120 specifications were significant; the effect is too fragile.")
        demo = [
            {"text": "real quote", "source_text": _SRC, "quote": "too fragile"},
            {"text": "invented quote", "source_text": _SRC, "quote": "the effect is rock solid"},
            {"text": "no source", "source_text": None},
        ]
        out = firewall(demo)
        assert out["ship_ok"] is False, out
        assert len(out["blocked"]) == 1 and len(out["grounded"]) == 1 and len(out["needs_label"]) == 1, out
        print("factharness_router smoke: PASS (1 grounded ships, 1 flagged blocks, 1 abstain needs label; "
              "ship_ok=False because a fabrication was caught)")
