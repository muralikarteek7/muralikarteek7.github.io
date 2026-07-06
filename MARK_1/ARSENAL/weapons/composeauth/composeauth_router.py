#!/usr/bin/env python3
"""COMPOSEAUTH (G3) router — decide WHICH compositional-budget behaviour fires.

Mirrors the other weapons' routers (gloves/symbolica/optima): classify by the κ-gate,
then route. For G3 the κ-gate is: *can this action's blast-radius be mapped EXACTLY
into an ENUMERATED resource class whose running sum can be compared to a committed
threshold?*

  - If the tool's effect maps to a tracked class  -> BUDGET  (κ=1: accumulate + compare;
    the FROZEN composeauth_gate.decide() then returns OK / ESCALATE / HALT).
  - If the effect lands OUTSIDE every tracked class (unknown tool / novel blast type)
    -> UNCOVERED  (κ<1 across population: report it, never silently count as
    'within budget' — the honesty rail).
  - "Is this composition MALICIOUS?" -> ABSTAIN/ESCALATE, never accuse (κ=0 intent).

It DECIDES routing; the FROZEN gate makes the OK/ESCALATE/HALT enforcement decision.
The router never lowers a threshold or un-tracks a class.
"""
import sys, json

import composeauth_policy as POLICY
from mock_gloves_ledger import EFFECT_EXTRACTOR, TRACKED_CLASSES, extract_effects

CEILING = (
    "G3 keeps an EXACT running blast-radius budget per ENUMERATED resource class over "
    "GLOVES' allowed actions and escalates/halts the moment a COMMITTED threshold is "
    "crossed — so individually-authorized safe steps cannot silently compose into a "
    "catastrophe. CEILING: it budgets ONLY what it counts (effect outside the tracked "
    "classes is reported UNCOVERED, never 'within budget'); the thresholds AND weights "
    "are human-owned POLICY, not derived truth; it is NOT an intent judge ('is this "
    "composition malicious?' is κ=0 -> escalate, never accuse); it needs GLOVES' "
    "per-action classification; it is complete only against classes it enumerates. "
    "κ=1 on the accumulation+comparison; κ<1 across tool population (unknown tool -> "
    "UNCOVERED). Persistence is load-bearing — a budget that resets on restart is "
    "defeated by crash-resume."
)


def route(action):
    """Return the routing plan: BUDGET (which class) / UNCOVERED / abstain + why.
    `action` is a GLOVES-shaped ledger entry (tool_id, params, [other_effects, ...])."""
    if not isinstance(action, dict):
        return _plan("ABSTAIN", "κ<1 boundary", "abstain",
                     "Malformed action (not a dict) -> ABSTAIN (fail safe).", action)

    tool_id = action.get("tool_id")
    deltas, uncovered = extract_effects(action)

    # 1) effect maps into >=1 tracked class -> BUDGET it (the gate then OK/ESCALATE/HALT).
    if deltas:
        classes = sorted(deltas.keys())
        return _plan("BUDGET", "κ=1 (exact accumulation+compare)", "accumulate-and-gate",
                     f"Action '{tool_id}' maps to tracked class(es) {classes}: add to the "
                     "running per-class budget; the FROZEN gate compares the sum to the "
                     "committed threshold -> OK / ESCALATE (next action STEP-UP) / HALT.",
                     action, classes=classes, uncovered=uncovered)

    # 2) no tracked effect, but blast WAS detected outside the enumerated classes
    #    -> UNCOVERED (honesty rail; never silent 'within budget').
    if uncovered:
        return _plan("UNCOVERED", "κ<1 (blast outside enumerated classes)", "report-uncovered",
                     f"Action '{tool_id}' has blast in class(es) G3 does NOT enumerate "
                     f"{sorted(uncovered)}: REPORTED as uncovered, NEVER counted as "
                     "'within budget'. You can only budget what you enumerate.",
                     action, uncovered=uncovered)

    # 3) no measurable blast at all -> nothing to budget (still names the limit).
    return _plan("NO-EFFECT", "κ=1 (no enumerated blast)", "pass-through",
                 f"Action '{tool_id}' carries no measurable blast in any enumerated "
                 "class: nothing to add to the budget (pass-through).", action)


def _plan(route_kind, kappa_note, behavior, rationale, action, classes=None, uncovered=None):
    return {
        "tool_id": action.get("tool_id") if isinstance(action, dict) else None,
        "route": route_kind,
        "kappa": kappa_note,
        "behavior": behavior,
        "classes_budgeted": classes or [],
        "uncovered": uncovered or {},
        "tracked_classes": list(TRACKED_CLASSES),
        "rationale": rationale,
        "ceiling": CEILING,
        "policy_banner": POLICY.POLICY_BANNER,
        "note": ("Routing only. The FROZEN composeauth_gate.decide() makes the final "
                 "OK/ESCALATE/HALT decision; the router never lowers a threshold or "
                 "un-tracks a class."),
    }


def _selftest():
    # a financial charge -> BUDGET, financial class
    r = route({"tool_id": "billing.charge", "params": {"amount": 20}})
    assert r["route"] == "BUDGET" and "financial" in r["classes_budgeted"], r
    assert r["behavior"] == "accumulate-and-gate", r

    # a delete -> BUDGET, destruction class
    r = route({"tool_id": "fs.overwrite", "params": {"path": "/p"}})
    assert r["route"] == "BUDGET" and "destruction" in r["classes_budgeted"], r

    # a mass send -> BUDGET, broadcast class (recipient count from len(to))
    r = route({"tool_id": "email.mass_send", "params": {"to": ["a", "b", "c"]}})
    assert r["route"] == "BUDGET" and "broadcast" in r["classes_budgeted"], r

    # an UNKNOWN tool with blast -> UNCOVERED (never silent within-budget)
    r = route({"tool_id": "psyops.influence", "params": {"t": 1}, "blast_units": 9})
    assert r["route"] == "UNCOVERED" and r["uncovered"], r
    assert r["behavior"] == "report-uncovered", r

    # a KNOWN tool carrying a NOVEL blast class in other_effects -> still BUDGET its
    # tracked part, but the uncovered part is surfaced in the plan.
    r = route({"tool_id": "fs.overwrite", "params": {"path": "/p"},
               "other_effects": {"reputation_harm": 4}})
    assert r["route"] == "BUDGET" and r["uncovered"].get("reputation_harm") == 4, r

    # malformed -> ABSTAIN (fail safe), never silent pass
    r = route(12345)
    assert r["route"] == "ABSTAIN" and r["behavior"] == "abstain", r

    # every plan names the tracked classes (what IS budgeted; rest uncovered)
    r = route({"tool_id": "billing.charge", "params": {"amount": 1}})
    assert set(r["tracked_classes"]) == set(TRACKED_CLASSES), r

    # ceiling always names the budget-only-what-you-count + policy-not-truth + intent limits
    assert "UNCOVERED" in r["ceiling"] and "POLICY" in r["ceiling"] and "malicious" in r["ceiling"], r
    # policy banner present on every plan (thresholds+weights are policy not truth)
    assert "NOT derived truth" in r["policy_banner"], r

    print("composeauth_router selftest: PASS (charge->BUDGET financial; delete->BUDGET "
          "destruction; mass_send->BUDGET broadcast; unknown->UNCOVERED not silent; "
          "known+novel-class->BUDGET+uncovered surfaced; malformed->ABSTAIN; ceiling names "
          "budget-only-what-you-count + policy-not-truth + not-an-intent-judge)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: composeauth_router.py selftest | <action.json>")
