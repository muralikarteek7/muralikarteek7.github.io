#!/usr/bin/env python3
"""GLOVES router — given an action, decide WHICH gate behavior fires.

Mirrors the other weapons' routers (symbolica/optima): classify by the kappa-gate,
then route. For GLOVES the kappa-gate is: *can the action's risk TIER be determined
exactly from the frozen tool-risk registry (the tool's declared schema), NOT the
model?* If yes -> the tier sets the gate (AUTO / CONFIRM / STEP-UP). If the tier
cannot be determined (unknown/unregistered tool) -> ABSTAIN (default-deny). A
read-only / no-side-effect call -> GLOVES is a no-op PASS-THROUGH (still logged).

It DECIDES routing; the FROZEN gate (gloves_gate.verdict) makes the ALLOW/BLOCK
enforcement decision. The router never lowers a tier (CVE-2025-53773); it may only
escalate (e.g. self-protection -> STEP-UP/BLOCK).
"""
import sys, json

from tool_risk_registry import lookup, is_self_protect_target

CEILING = ("GLOVES gates EFFECTS, not wisdom. It bounds catastrophe by construction "
           "(token bound to exact params + expiry; self-edit hard-blocked; "
           "irreversible/broad/financial -> a human) but does NOT confer judgment: a "
           "correctly-authorized action can still be a mistake. kappa=1 on "
           "token/param/expiry/single-use/scope + dry-run->commit; kappa=1 WITHIN the "
           "registry, kappa<1 ACROSS its population (unknown tool -> ABSTAIN). Per-action "
           "only -> a sequence of safe actions can COMPOSE into an unsafe one until G3 "
           "(compositional authorization) ships. Tamper-resistance is infra-limited "
           "(see infra_check). Not an injection detector (that is SHIELD).")


def route(action):
    """Return the routing plan: which gate behavior + why. Does NOT enforce."""
    tool_id = action.get("tool_id")
    params = action.get("params", {})

    # 0) self-protection ALWAYS wins, before anything else (cannot be lowered).
    if is_self_protect_target(tool_id, params):
        return _plan("STEP-UP", "self-protection", "block",
                     "Action targets GLOVES' own config/registry/ledger/approval state "
                     "or flips an auto-approve flag -> hard-block + ALARM "
                     "(CVE-2025-53773). No token overrides.", action)

    entry = lookup(tool_id)

    # 1) unknown/unregistered -> ABSTAIN (default-deny boundary; kappa<1 across registry).
    if entry is None:
        return _plan("ABSTAIN", "kappa<1 boundary", "abstain",
                     f"Unknown/unregistered tool_id '{tool_id}': tier cannot be "
                     "determined from schema -> ABSTAIN (default-deny), never silent-pass.",
                     action)

    tier = entry["tier"]

    # 2) AUTO + idempotent read/query with no side effect -> no-op PASS-THROUGH (logged).
    if tier == "AUTO" and entry.get("idempotent") and entry.get("blast_units", 0) == 0 \
            and entry.get("reversibility") == "R0":
        return _plan("AUTO", "kappa=1 (registry)", "pass-through",
                     "Read-only / no-side-effect (R0 reversible, blast-local): GLOVES is a "
                     "no-op pass-through (execute + log).", action)

    # 3) AUTO scratch write (R0, local but not idempotent) -> AUTO execute + log.
    if tier == "AUTO":
        return _plan("AUTO", "kappa=1 (registry)", "allow-and-log",
                     "R0 reversible, blast-local (scratch): AUTO execute + log.", action)

    # 4) CONFIRM -> require a param-bound + expiry token (machine-checked, kappa=1).
    if tier == "CONFIRM":
        return _plan("CONFIRM", "kappa=1 (registry)", "require-token",
                     "R1-R2 or blast-project/external: require a token bound to the EXACT "
                     "params + expiry (machine-checked by the gate). dry-run->commit if "
                     "the tool declares needs_dry_run.", action)

    # 5) STEP-UP -> elevated human auth; agent CANNOT self-approve.
    if tier == "STEP-UP":
        fin = tool_id == "money.transfer" or entry.get("blast_radius") == "external" and entry.get("reversibility") == "R3"
        return _plan("STEP-UP", "kappa=1 (registry)", "human-approval",
                     "R3 irreversible-broad / financial / admin: ELEVATED auth; the agent "
                     "CANNOT self-approve (block without an external human grant)."
                     + (" Financial -> ALWAYS routes to the human (system rail)." if tool_id == "money.transfer" else ""),
                     action)

    # 6) fall-through (should be unreachable given a frozen registry) -> ABSTAIN.
    return _plan("ABSTAIN", "kappa<1 boundary", "abstain",
                 "Tier present but unhandled -> ABSTAIN (fail safe).", action)


def _plan(tier, kappa_note, gate_behavior, rationale, action):
    return {
        "tool_id": action.get("tool_id"),
        "tier": tier,
        "kappa": kappa_note,
        "gate_behavior": gate_behavior,
        "rationale": rationale,
        "ceiling": CEILING,
        "note": ("Routing only. The FROZEN gloves_gate.verdict() makes the final "
                 "ALLOW/BLOCK decision; the router never lowers a tier."),
    }


def _selftest():
    # read -> AUTO pass-through
    r = route({"tool_id": "fs.read", "params": {"path": "/tmp/x"}})
    assert r["tier"] == "AUTO" and r["gate_behavior"] == "pass-through", r
    # scratch write -> AUTO allow-and-log
    r = route({"tool_id": "fs.scratch_write", "params": {"path": "/tmp/s"}})
    assert r["tier"] == "AUTO" and r["gate_behavior"] == "allow-and-log", r
    # overwrite -> CONFIRM require-token
    r = route({"tool_id": "fs.overwrite", "params": {"path": "/p/f"}})
    assert r["tier"] == "CONFIRM" and r["gate_behavior"] == "require-token", r
    # mass send -> STEP-UP human-approval
    r = route({"tool_id": "email.mass_send", "params": {"to": ["a", "b"]}})
    assert r["tier"] == "STEP-UP" and r["gate_behavior"] == "human-approval", r
    # money transfer -> STEP-UP, financial routes to human
    r = route({"tool_id": "money.transfer", "params": {"amt": 100}})
    assert r["tier"] == "STEP-UP" and "Financial" in r["rationale"], r
    # unknown -> ABSTAIN (default-deny), never silent-pass
    r = route({"tool_id": "evil.unregistered", "params": {}})
    assert r["tier"] == "ABSTAIN" and r["gate_behavior"] == "abstain", r
    # self-protection (registry edit) -> STEP-UP/block, cannot be lowered
    r = route({"tool_id": "registry.edit", "params": {"x": 1}})
    assert r["tier"] == "STEP-UP" and r["gate_behavior"] == "block", r
    # self-downgrade param (autoApprove flip) on a benign tool -> still block
    r = route({"tool_id": "fs.scratch_write", "params": {"chat.tools.autoApprove": True}})
    assert r["gate_behavior"] == "block", r
    # ceiling always names the composition/G3 limit and "gates EFFECTS, not wisdom"
    assert "G3" in r["ceiling"] and "not wisdom" in r["ceiling"], r
    print("gloves_router selftest: PASS (read->AUTO pass-through; scratch->AUTO log; "
          "overwrite->CONFIRM token; mass_send->STEP-UP human; money->STEP-UP financial; "
          "unknown->ABSTAIN default-deny; self-edit & autoApprove->block; ceiling names G3)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: gloves_router.py selftest | <action.json>")
