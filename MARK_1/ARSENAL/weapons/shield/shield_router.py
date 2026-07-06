#!/usr/bin/env python3
"""SHIELD router — given an EVENT at the box boundary, decide which rail(s) fire (or route
to abstain/escalate). Mirrors the symbolica/socius/proofsmith router pattern: classify by
whether a cheap EXACT (kappa=1) structural check exists, draw the matching rail, and route
the kappa=0 residue (injection *intent*) to abstain-or-escalate — NEVER to an LLM detector
trusted as truth.

It decides ROUTING; the gate (shield_gate.py) does the exact blocking. SHIELD is
ARMOR-HARDENING, not a weapon. The CEILING (no complete injection defense) is attached to
every plan.
"""
import sys
import json
import shield_gate

# event precondition key -> (rail, kappa, track, rationale)
RULES = [
    ("is_external_input", "PROVENANCE-LABEL+SCAN", 1, "rail",
     "External/untrusted input (user text, tool output, retrieved doc, web, MCP metadata, "
     "memory read, other-agent msg) -> stamp ENV tier (kappa=1 label) AND run the kappa=0 "
     "suspicion scan. The label is exact; obedience to it is kappa<1; the scan ROUTES, "
     "it never clears."),
    ("is_weapon_gate_call", "VERIFIER-TAINT-RAIL", 1, "rail",
     "A weapon-gate call -> enforce the taint-rail: any ENV/attacker NL in the code or spec "
     "slot REJECTS before the gate runs (the candidate object MAY be ENV). The highest-value "
     "rail: it hardens every weapon against being talked into a false certificate."),
    ("has_prior_certificate", "CERT-ANTI-REPLAY", 1, "rail",
     "A prior weapon certificate is being reused -> re-verify the signed {object_hash, "
     "verifier_id, version, ts, result} tuple; a hash-mismatch/forge/stale PASS is REJECTED."),
    ("is_tool_call", "TOOL-CAPE", 1, "rail",
     "A tool call -> enforce the signed per-task allowlist; an out-of-cape tool is BLOCKED "
     "and a runtime self-elevation attempt ALARMS. The model cannot mint a valid expanded "
     "cape (it lacks the box key)."),
    ("is_high_privilege_under_suspicion", "ABSTAIN-OR-ESCALATE", 0, "abstain",
     "A high-privilege op under suspicion (or any op the kappa=0 scan cannot clear) -> "
     "escalate (human review) / downgrade to read-only / hard abstain + log. Never "
     "auto-proceed; never self-certify 'injection-free'."),
    ("is_injection_intent_judgment", "ABSTAIN-OR-ESCALATE", 0, "abstain",
     "Injection/jailbreak/social-engineering INTENT is kappa=0 (an attack is defined by "
     "evading detection — no cheap exact verifier exists). Route to abstain-or-escalate; "
     "NEVER an LLM injection-classifier trusted as ground truth (circular)."),
]

CEILING = shield_gate.CEILING


def route(event):
    fired, seen = [], set()
    for key, rail, kappa, track, why in RULES:
        if event.get(key):
            if rail in seen:
                continue
            seen.add(rail)
            fired.append({"rail": rail, "kappa": kappa, "track": track,
                          "trigger": key, "rationale": why})
    plan = {
        "fired_rails": fired,
        "exact_track": [f for f in fired if f["track"] == "rail"],     # kappa=1 structural
        "abstain_track": [f for f in fired if f["track"] == "abstain"],  # kappa=0
        "ceiling": CEILING,
        "is_weapon": False,           # SHIELD builds nothing
        "label": "ARMOR-HARDENING",
    }
    if not fired:
        plan["note"] = ("No precondition matched — under-specified boundary event. Abstain "
                        "and ask what kind of event this is (external input / weapon-gate "
                        "call / tool call / cert reuse / high-privilege op).")
    elif not plan["exact_track"]:
        plan["note"] = ("kappa=0 only: injection-intent / high-privilege-under-suspicion -> "
                        "abstain-or-escalate. SHIELD does NOT manufacture an exact clearance "
                        "where none exists; it never self-certifies 'injection-free'.")
    else:
        plan["note"] = ("kappa=1 rail(s) fire: exact structural blocking applies. Any kappa=0 "
                        "residue (injection intent) is ALSO routed to abstain-or-escalate. "
                        "Defense-in-depth: ARMOR's fabrication veto + cross-model audit remain.")
    return plan


def _selftest():
    # external input -> PROVENANCE-LABEL+SCAN (kappa=1 rail track)
    r = route({"is_external_input": True})
    assert r["exact_track"][0]["rail"] == "PROVENANCE-LABEL+SCAN", r
    # weapon-gate call -> the taint-rail (the highest-value rail)
    assert route({"is_weapon_gate_call": True})["exact_track"][0]["rail"] == "VERIFIER-TAINT-RAIL"
    # prior cert reuse -> anti-replay
    assert route({"has_prior_certificate": True})["exact_track"][0]["rail"] == "CERT-ANTI-REPLAY"
    # tool call -> tool-cape
    assert route({"is_tool_call": True})["exact_track"][0]["rail"] == "TOOL-CAPE"
    # injection-intent judgment -> abstain track ONLY (kappa=0), NOT an exact rail
    inj = route({"is_injection_intent_judgment": True})
    assert inj["exact_track"] == [] and inj["abstain_track"][0]["rail"] == "ABSTAIN-OR-ESCALATE", inj
    assert inj["abstain_track"][0]["kappa"] == 0, inj
    # high-privilege under suspicion -> abstain/escalate
    hp = route({"is_high_privilege_under_suspicion": True})
    assert hp["abstain_track"][0]["rail"] == "ABSTAIN-OR-ESCALATE", hp
    # empty event -> abstain (no rail fired)
    assert route({})["fired_rails"] == []
    # SHIELD is NEVER labeled a weapon, ceiling always present, label is ARMOR-HARDENING
    e = route({})
    assert e["is_weapon"] is False and e["label"] == "ARMOR-HARDENING", e
    assert "complete injection defense" in e["ceiling"].lower(), e
    assert "unlikely to ever be fully solved" in e["ceiling"].lower(), e
    # the abstain track never claims to clear: the rationale forbids the LLM-detector path
    assert "never an llm injection-classifier" in inj["abstain_track"][0]["rationale"].lower()
    print("shield_router selftest: PASS  (external->PROVENANCE-LABEL+SCAN; "
          "weapon-gate->VERIFIER-TAINT-RAIL; cert-reuse->CERT-ANTI-REPLAY; "
          "tool-call->TOOL-CAPE; injection-intent & high-priv->ABSTAIN-OR-ESCALATE kappa=0; "
          "empty->abstain; never a weapon; ceiling present)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: shield_router.py selftest | <event.json>")
