#!/usr/bin/env python3
"""VAULT router — given a candidate result, decide WHICH tier it is ELIGIBLE for
before it ever reaches the gate. It decides routing; the gate (vault_gate) decides
admission. The router never writes; it classifies.

Mirrors the symbolica/socius router pattern: classify by the kappa-gate — *does this
result carry, or can it carry, a MACHINE-VERIFICATION or FETCHED-SOURCE record?* If a
machine proof / certified object exists -> VERIFIED_FACT eligible (kappa=1 entry). If
only a fetched source + URL + date backs it -> FETCHED_FACT eligible (kappa=1 entry,
but DECAYS — TTL). If it is a belief / "the session concluded" / a model judgment with
no record -> LEAD (kappa=0; surfaced as a hypothesis, never a fact).

The decisive question is NOT "do we believe it?" but "is there a NON-CIRCULAR record
that a different process (a machine run, a fetched source) produced?" That is what
separates a fact from a lead in the VAULT.
"""
import sys
import json

# precondition key -> (tier, kappa, track, rationale)
RULES = [
    ("has_machine_verification_record", "VERIFIED_FACT", 1.0, "fact",
     "A machine proof / certified object / cross-method agreement record exists "
     "(e.g. CP-SAT==Held-Karp, SYMBOLICA 30-digit agreement, a Lean term). kappa=1: "
     "the record-validity check is exact and non-gameable. Enters as a VERIFIED FACT; "
     "does NOT decay on the calendar."),
    ("has_fetched_source_record", "FETCHED_FACT", 1.0, "fact",
     "Backed ONLY by a fetched source + URL + date (e.g. a library version). kappa=1 "
     "at WRITE (the record exists), but the CONTENT can go stale -> shorter TTL, "
     "re-fetch on a stale high-stakes read. The world changing is the kappa<1 residue "
     "the VAULT FLAGS, not models."),
    ("is_unverified_belief_or_conclusion", "LEAD", 0.0, "lead",
     "'The session concluded X' / 'approach Y looked promising' with NO machine or "
     "fetched record. kappa=0: there is nothing exact to check. Enters as a LEAD — a "
     "labeled hypothesis to TEST, NEVER returned as a fact."),
    ("is_judgment_or_interpretation", "LEAD", 0.0, "lead",
     "A synthesis / interpretation / 'what it MEANS' result has no exact verifier. "
     "kappa=0 -> LEAD. The VAULT certifies records, never interpretations."),
]

CEILING = ("The VAULT stores as a FACT only what shipped with a VALID machine or "
           "fetched-source verification record (method/artifact/result, all non-empty "
           "— an empty record does NOT promote a lead). Everything unverified is a "
           "LEAD, never returned as truth. It FLAGS staleness via TTL; it does NOT "
           "model temporal change (a fetched fact true in March can be stale in June — "
           "the mem0-2026 open problem). It is INFRA that stops rework, NOT a weapon "
           "and NOT a ratchet move.")


def route(candidate):
    fired, seen = [], set()
    for key, tier, kappa, track, why in RULES:
        if candidate.get(key):
            tag = (tier, key)
            if tag in seen:
                continue
            seen.add(tag)
            fired.append({"tier": tier, "kappa": kappa, "track": track,
                          "trigger": key, "rationale": why})
    # eligibility: the HIGHEST fact tier wins if any fact-track rule fired; else LEAD.
    fact_track = [f for f in fired if f["track"] == "fact"]
    lead_track = [f for f in fired if f["track"] == "lead"]
    if fact_track:
        # VERIFIED_FACT beats FETCHED_FACT if both somehow fire (a machine proof is
        # stronger than a fetched claim).
        verified = [f for f in fact_track if f["tier"] == "VERIFIED_FACT"]
        eligible = (verified[0] if verified else fact_track[0])["tier"]
    else:
        eligible = "LEAD"

    plan = {
        "fired": fired,
        "eligible_tier": eligible,
        "fact_track": fact_track,
        "lead_track": lead_track,
        "ceiling": CEILING,
    }
    if not fired:
        plan["note"] = ("No precondition matched — under-specified. Default to LEAD: a "
                        "claim with no declared verification path is NOT a fact.")
        plan["eligible_tier"] = "LEAD"
    elif not fact_track:
        plan["note"] = ("kappa=0: no machine/fetched record -> LEAD. The VAULT does NOT "
                        "manufacture a fact where no non-circular record exists.")
    elif eligible == "VERIFIED_FACT":
        plan["note"] = ("kappa=1 machine record present -> VERIFIED_FACT eligible (gate "
                        "still validates the record's contents). Non-decaying.")
    else:
        plan["note"] = ("kappa=1 fetched-source record -> FETCHED_FACT eligible, but "
                        "DECAYS: TTL set, stale high-stakes reads re-verify.")
    return plan


def _selftest():
    # a machine-verified result -> VERIFIED_FACT eligible (kappa=1)
    m = route({"has_machine_verification_record": True})
    assert m["eligible_tier"] == "VERIFIED_FACT" and m["fact_track"][0]["kappa"] == 1.0, m

    # a fetched-source result -> FETCHED_FACT eligible (kappa=1, decays)
    f = route({"has_fetched_source_record": True})
    assert f["eligible_tier"] == "FETCHED_FACT", f
    assert "DECAYS" in f["note"], f

    # an unverified belief -> LEAD (kappa=0), NOT a fact
    b = route({"is_unverified_belief_or_conclusion": True})
    assert b["eligible_tier"] == "LEAD" and b["fact_track"] == [], b
    assert b["lead_track"][0]["kappa"] == 0.0, b

    # a judgment/interpretation -> LEAD (kappa=0)
    j = route({"is_judgment_or_interpretation": True})
    assert j["eligible_tier"] == "LEAD" and j["fact_track"] == [], j

    # a machine record BEATS a coincidentally-also-fetched flag -> VERIFIED_FACT
    both = route({"has_machine_verification_record": True,
                  "has_fetched_source_record": True})
    assert both["eligible_tier"] == "VERIFIED_FACT", both

    # a "belief" that ALSO claims a machine record is fact-ELIGIBLE at routing
    # (the GATE then checks the record is real — defense in depth; router != gate)
    mixed = route({"has_machine_verification_record": True,
                   "is_unverified_belief_or_conclusion": True})
    assert mixed["eligible_tier"] == "VERIFIED_FACT", mixed

    # empty candidate -> defaults to LEAD (no verification path declared), never a fact
    e = route({})
    assert e["eligible_tier"] == "LEAD" and e["fired"] == [], e

    # ceiling always present, naming the staleness limit + infra-not-weapon honesty
    assert "does NOT" in route({})["ceiling"] and "temporal change" in route({})["ceiling"]
    assert "NOT a weapon" in route({})["ceiling"]

    print("vault_router selftest: PASS (machine-record->VERIFIED_FACT kappa=1; "
          "fetched->FETCHED_FACT kappa=1 decays; belief->LEAD kappa=0; judgment->LEAD; "
          "machine beats fetched; empty->LEAD default; ceiling names staleness + "
          "infra-not-weapon)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: vault_router.py selftest | <candidate.json>")
