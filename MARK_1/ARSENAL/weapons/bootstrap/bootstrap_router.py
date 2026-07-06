#!/usr/bin/env python3
"""BOOTSTRAP router — given a NEW problem class, decide WHICH of the three
outcomes to PURSUE, and route accordingly.

Mirrors the other weapon routers (symbolica/socius/...): the decisive question is
the kappa-gate — *does a cheap EXACT, non-gameable verifier plausibly exist for
this property?* The router's verdict is a ROUTING DECISION, NOT a promotion:

  - SEARCH-AND-VALIDATE : there may be an exact decision procedure (a checker, a
        SAT/SMT/constraint solver, a published benchmark with ground truth) ->
        hand the candidate harnesses to bootstrap_gate.validate_candidate, which
        RUNS them. The RUN, not this router, earns kappa>0.
  - ARMOR-ONLY          : the property is a JUDGMENT (essay quality, persuasion,
        helpfulness) with no exact decision procedure -> route to ARMOR. Do NOT
        search for / invent a fake gate.
  - ABSTAIN-NEED-INPUT  : under-specified to even search -> ask for a sharper spec.

CRITICAL HONESTY RAIL: a SEARCH-AND-VALIDATE routing is NOT a claim that a
verifier exists or works — it only says "it is worth RUNNING candidates." The
authority is bootstrap_gate's RUN. The searcher/proposer step is 0%-trusted
(LLM-proposed tools are fabrication-prone; see GROUNDING.md / registry W4).
"""
import sys, json

# routing verdicts (frozen)
SEARCH = "SEARCH-AND-VALIDATE"
ARMOR = "ARMOR-ONLY"
ABSTAIN = "ABSTAIN-NEED-INPUT"

CEILING = ("BOOTSTRAP routes; it does not promote. A SEARCH-AND-VALIDATE verdict "
           "only says 'run candidate verifiers' — the RUN on known-answer cases is "
           "the only authority for kappa>0. ARMOR-ONLY domains stay kappa=0 (no fake "
           "gate). A validated verifier carries only its KNOWN-ANSWER coverage: "
           "toy-passing != frontier-correct, and the new weapon it scaffolds must "
           "STILL pass its own full box build.")


def route(spec):
    """`spec` describes a candidate new problem class:
      {"domain": str,
       "well_specified": bool,           # enough to even search?
       "has_exact_decidable_property": bool,   # plausible EXACT checker exists?
       "is_judgment_only": bool}         # only LLM-judgment can score it?

    Returns a routing plan. The flags are HINTS from the searcher (0%-trusted);
    the routing they produce is checked downstream by the RUN, never here.
    """
    domain = spec.get("domain", "<unnamed>")

    if not spec.get("well_specified", False):
        return {"domain": domain, "verdict": ABSTAIN, "track": "abstain",
                "kappa_hint": None, "ceiling": CEILING,
                "rationale": ("Under-specified to even search for a verifier "
                              "(what exactly is checked?). Ask for a sharper spec; "
                              "do not guess.")}

    # judgment-only OR no plausible exact property -> ARMOR (kappa=0).
    if spec.get("is_judgment_only") or not spec.get("has_exact_decidable_property", False):
        return {"domain": domain, "verdict": ARMOR, "track": "armor",
                "kappa_hint": 0.0, "ceiling": CEILING,
                "rationale": ("No exact, non-gameable decision procedure for this "
                              "property (it is a JUDGMENT). Route to ARMOR; do NOT "
                              "invent a gate to look capable. kappa stays 0.")}

    # plausible exact property -> worth RUNNING candidates (not yet kappa>0).
    return {"domain": domain, "verdict": SEARCH, "track": "search",
            "kappa_hint": None, "ceiling": CEILING,
            "rationale": ("An exact decision procedure plausibly exists. RUN "
                          "candidate verifiers through bootstrap_gate on "
                          "known-answer cases (accept-good / catch-broken-per-"
                          "violation-type / abstain-malformed). The RUN, not this "
                          "routing, earns kappa>0.")}


def _selftest():
    # an exact-decidable domain (Sudoku validity) -> SEARCH (run candidates)
    s = route({"domain": "sudoku-validity", "well_specified": True,
               "has_exact_decidable_property": True, "is_judgment_only": False})
    assert s["verdict"] == SEARCH and s["track"] == "search", s
    assert s["kappa_hint"] is None, s  # NOT promoted by routing

    # graph-coloring check -> SEARCH (an exact checker plausibly exists)
    gc = route({"domain": "graph-coloring-check", "well_specified": True,
                "has_exact_decidable_property": True, "is_judgment_only": False})
    assert gc["verdict"] == SEARCH, gc

    # a judgment-only domain (essay persuasiveness) -> ARMOR, kappa=0
    e = route({"domain": "essay-persuasiveness", "well_specified": True,
               "has_exact_decidable_property": False, "is_judgment_only": True})
    assert e["verdict"] == ARMOR and e["kappa_hint"] == 0.0, e

    # a judgment-domain DRESSED as exact (claims exact but is judgment) -> still
    # ARMOR (is_judgment_only dominates the optimistic has_exact flag)
    dressed = route({"domain": "writing-quality", "well_specified": True,
                     "has_exact_decidable_property": True, "is_judgment_only": True})
    assert dressed["verdict"] == ARMOR, dressed

    # no exact property and not flagged judgment -> still ARMOR (no gate)
    none = route({"domain": "vibes", "well_specified": True,
                  "has_exact_decidable_property": False, "is_judgment_only": False})
    assert none["verdict"] == ARMOR, none

    # under-specified -> ABSTAIN
    a = route({"domain": "??", "well_specified": False})
    assert a["verdict"] == ABSTAIN, a

    # ceiling always present, naming the route-not-promote doctrine
    assert "does not promote" in route({"domain": "x", "well_specified": False})["ceiling"]

    print("bootstrap_router selftest: PASS (exact-decidable->SEARCH (no kappa from "
          "routing); judgment->ARMOR kappa=0; judgment-dressed-as-exact->ARMOR; "
          "no-property->ARMOR; under-specified->ABSTAIN)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: bootstrap_router.py selftest | <spec.json>")
