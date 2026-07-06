#!/usr/bin/env python3
"""ROUTE-PLANNER (SHOES-c) — the frozen router-time meta-controller.

Doctrine (the box): *pick the cheapest ladder rung that clears the bar — and stop
searching when the search stops producing verified facts.* ROUTE-PLANNER classifies
each task by (a) complexity -> ladder tier and (b) verifiability (kappa) -> weapon
(kappa>0) vs armor (kappa=0), picks the cheapest path that meets the bar, and EXTENDS
the existing saturation tripwire with a per-track verified-fact-delta=0 hard cap. It
decides routing; it does not do the work. It is ARMOR/efficiency, not a weapon.

THE LADDER it routes onto (BOX_V4, MEASURED): machine-checkable -> EXECUTE (no model,
$0) · routine/in-distribution -> Haiku · hard-but-executable -> write-a-solver+EXECUTE
· genuinely un-executable hard -> Opus (Fable when active). Cheapest-that-clears.

WHAT IS kappa=1 (EXACT, deterministic): the token/complexity CLASS bucket; the
kappa-of-the-task (does a cheap exact verifier exist?  yes/no); and the
verified-fact-delta=0 STUCK signal (a count comparison). All machine-computed.

WHAT IS kappa<1 (JUDGMENT): "which path is cheapest-that-clears-the-bar?" and "is this
search stuck or just slow?" — routing judgments, not certifications.

"verified-fact" is DEFINED PER TRACK (the audit fix — else the stuck-detector fires
vacuously or never):
  - weapon track : a NEW gate-passed object produced THIS iteration.
  - armor  track : a NET increase in grounded (fetched/executed) load-bearing claims.
  - kappa=0 track: an escalation / decision RECORDED this iteration.
verified-fact-delta=0 means NONE of these advanced -> only THEN is the search "stuck".

"A gate that can't fail is not a gate": _selftest() requires
  (d) a machine-checkable task -> EXECUTE (no model); a kappa=0 judgment -> ARMOR;
  (e) N iterations of zero verified-fact-delta (per-track) -> STRATEGY SWITCH/impasse
      (not an infinite loop);
  (f) a benign single task -> NOT falsely halted;
  (g) [primary adversary, owned jointly with FOOTING] a task KNOWN to need Opus that
      is routed to Haiku is detectable as a misroute (route_planner flags
      `misrouted_below_required_tier`; FOOTING is the ship-time backstop).
All must pass or NOTHING ROUTE-PLANNER outputs is trusted.
"""
import sys

# ladder tiers, cheapest first; rank used for cheapest-that-clears + misroute check.
LADDER = ["execute", "haiku", "opus", "fable"]
_RANK = {"execute": 0, "haiku": 1, "opus": 2, "fable": 3}
# relative cost weights (BOX_V4: execute $0; Haiku ~1/40 Opus; Fable ~2x Opus).
_COST = {"execute": 0.0, "haiku": 1.0, "opus": 40.0, "fable": 80.0}

# stuck-detector hard cap (extends the saturation tripwire's STRUCTURAL_GAP).
STUCK_AFTER_N = 3        # N consecutive zero-verified-fact-delta iterations -> switch


# --------------------------------------------------------------------------- #
#  (a) complexity -> tier   |   (b) verifiability -> track   (both kappa=1 class)
# --------------------------------------------------------------------------- #
def classify(task):
    """Classify a task into (tier, track, kappa, why). EXACT bucketing (kappa=1 class):

    `task` flags (booleans, machine-evaluable preconditions):
      machine_checkable     : computation/invariant/data -> EXECUTE, no model, $0.
      routine_generation    : standard code/boilerplate, in-distribution -> Haiku.
      hard_but_executable   : hard, but a solver can be WRITTEN+RUN -> EXECUTE (v3 lever).
      hard_unexecutable     : genuinely un-executable hard reasoning -> Opus (Fable when active).
      has_exact_verifier    : a cheap EXACT non-gameable verifier exists -> weapon (kappa>0).
      is_interpretation     : meaning/modeling/synthesis judgment -> armor (kappa=0).
    `required_tier` (optional): the tier the task TRULY needs (for the misroute check).
    """
    # tier: cheapest rung whose capability clears the task.
    if task.get("machine_checkable") or task.get("hard_but_executable"):
        tier, tier_why = "execute", "machine-checkable (or hard-but-executable via a written solver) -> EXECUTE, no model ($0)"
    elif task.get("routine_generation"):
        tier, tier_why = "haiku", "routine/in-distribution generation -> Haiku (cheapest tier suffices)"
    elif task.get("hard_unexecutable"):
        tier, tier_why = "opus", "genuinely un-executable hard reasoning -> Opus (Fable when active; flag low confidence on Opus here)"
    else:
        tier, tier_why = "haiku", "unclassified -> default to the cheap tier; FOOTING backstops a misroute"

    # track: does a cheap EXACT verifier exist?
    if task.get("has_exact_verifier") and not task.get("is_interpretation"):
        track, kappa, track_why = "weapon", 0.9, "a cheap EXACT non-gameable verifier exists -> weapon (kappa>0): produce+gate an object"
    elif task.get("is_interpretation"):
        track, kappa, track_why = "armor", 0.0, "interpretation/meaning/synthesis -> armor (kappa=0): ground in a fetched source or ABSTAIN"
    else:
        track, kappa, track_why = "armor", 0.0, "no cheap exact verifier -> armor (kappa=0): numeric-with-error-bars / ground / abstain"

    return {"tier": tier, "tier_rationale": tier_why,
            "track": track, "kappa": kappa, "track_rationale": track_why}


def cheapest_path(task):
    """Pick the cheapest ladder rung that clears the bar + the weapon/armor track,
    and flag a misroute if `required_tier` is set and we'd route BELOW it."""
    c = classify(task)
    tier = c["tier"]
    misrouted = False
    rt = task.get("required_tier")
    if rt and _RANK.get(tier, 1) < _RANK.get(rt, 1):
        # routing rule below the true requirement -> a misroute (silent-regression risk).
        misrouted = True
    return {
        "component": "ROUTE-PLANNER",
        "tier": tier, "track": c["track"], "kappa": c["kappa"],
        "cheapest_path": f"{tier} / {c['track']}",
        "relative_cost_weight": _COST[tier],
        "tier_rationale": c["tier_rationale"],
        "track_rationale": c["track_rationale"],
        "misrouted_below_required_tier": misrouted,
        "required_tier": rt,
        "note": ("WARNING: cheapest rung is BELOW the required tier -> a misroute "
                 "(silent-quality-regression risk). FOOTING must backstop at ship time."
                 if misrouted else
                 "cheapest rung that clears the bar; weapon-vs-armor by kappa."),
        "ceiling": ("ROUTE-PLANNER REDUCES cost; it does NOT make the box smarter. The "
                    "cheapest-path pick is a kappa<1 routing judgment; a misroute can "
                    "still slip a degraded answer past it -> FOOTING + a pre-merge eval "
                    "gate (50-500 cases) are the non-optional backstops."),
    }


# --------------------------------------------------------------------------- #
#  (e) the per-track verified-fact-delta stuck detector (extends the tripwire)
# --------------------------------------------------------------------------- #
def verified_fact_delta(prev, cur, track):
    """EXACT (kappa=1). Did a 'verified fact' advance THIS iteration, per the
    per-track definition? Returns (delta:int, kind:str).

    iteration record fields (per track):
      weapon : gate_passed_objects (int, cumulative)
      armor  : grounded_claims     (int, cumulative)
      kappa0 : escalations_recorded(int, cumulative)
    delta = cur - prev for the field that track owns. delta>0 -> a fact advanced."""
    field = {"weapon": "gate_passed_objects",
             "armor": "grounded_claims",
             "kappa0": "escalations_recorded"}.get(track)
    if field is None:
        raise ValueError("unknown track for verified-fact: %r" % track)
    d = int(cur.get(field, 0)) - int(prev.get(field, 0))
    return d, field


def stuck_detector(iterations, track, stuck_after_n=STUCK_AFTER_N):
    """EXTENDS the saturation tripwire: fire a STRATEGY-SWITCH / impasse when the
    LAST `stuck_after_n` iterations ALL had verified-fact-delta == 0 (per track).
    A benign single (or short) productive search is NOT halted.

    `iterations` = list of per-iteration records (cumulative counters as above),
    in order. Returns {stuck, action, ...}. kappa=1 on the count; the 'switch now?'
    framing is the routing judgment (kappa<1)."""
    if len(iterations) < stuck_after_n + 1:
        return {"stuck": False, "action": "CONTINUE",
                "reason": f"only {len(iterations)} iteration(s); need {stuck_after_n+1} to judge a plateau",
                "track": track}
    deltas = []
    for prev, cur in zip(iterations[-(stuck_after_n + 1):-1], iterations[-stuck_after_n:]):
        d, field = verified_fact_delta(prev, cur, track)
        deltas.append(d)
    zero_run = all(d <= 0 for d in deltas)
    if zero_run:
        return {"stuck": True, "action": "STRATEGY_SWITCH_OR_IMPASSE",
                "reason": (f"{stuck_after_n} consecutive iterations with verified-fact-delta<=0 "
                           f"on the {track} track (field '{field}') -> the search is not producing "
                           f"verified facts; SWITCH STRATEGY or report an honest impasse (anti-loop hard cap)."),
                "recent_deltas": deltas, "track": track,
                "ceiling": "This is a routing judgment (kappa<1) on an EXACT count (kappa=1): the "
                           "counters do not lie, but 'switch now' vs 'one more try' is a judgment."}
    return {"stuck": False, "action": "CONTINUE",
            "reason": f"verified-fact advanced within the last {stuck_after_n} iterations on the {track} track",
            "recent_deltas": deltas, "track": track}


# --------------------------------------------------------------------------- #
#  NON-WAIVABLE adversarial self-test
# --------------------------------------------------------------------------- #
def _selftest():
    # (d) machine-checkable task -> EXECUTE (no model)
    d1 = cheapest_path({"machine_checkable": True, "has_exact_verifier": True})
    assert d1["tier"] == "execute" and d1["track"] == "weapon", d1
    assert d1["relative_cost_weight"] == 0.0, d1
    #     a kappa=0 interpretation -> ARMOR (no weapon)
    d2 = cheapest_path({"is_interpretation": True, "hard_unexecutable": True})
    assert d2["track"] == "armor" and d2["kappa"] == 0.0, d2
    #     routine generation -> Haiku (cheap), not Opus
    d3 = cheapest_path({"routine_generation": True})
    assert d3["tier"] == "haiku", d3
    #     genuinely un-executable hard -> Opus
    d4 = cheapest_path({"hard_unexecutable": True, "is_interpretation": False, "has_exact_verifier": False})
    assert d4["tier"] == "opus" and d4["track"] == "armor", d4

    # (e) N iterations of zero verified-fact-delta (per-track) -> STRATEGY SWITCH
    #     weapon track: gate_passed_objects flat for STUCK_AFTER_N iters
    flat = [{"gate_passed_objects": 2}] * (STUCK_AFTER_N + 1)
    s = stuck_detector(flat, track="weapon")
    assert s["stuck"] is True and s["action"] == "STRATEGY_SWITCH_OR_IMPASSE", s
    #     armor track: grounded_claims flat -> stuck
    flat_a = [{"grounded_claims": 5}] * (STUCK_AFTER_N + 1)
    sa = stuck_detector(flat_a, track="armor")
    assert sa["stuck"] is True, sa

    # (f) a benign PRODUCTIVE search is NOT halted: facts advance each iteration
    prod = [{"gate_passed_objects": i} for i in range(STUCK_AFTER_N + 2)]
    p = stuck_detector(prod, track="weapon")
    assert p["stuck"] is False and p["action"] == "CONTINUE", p
    #     and a single benign task (too short to judge) is NOT halted
    short = stuck_detector([{"gate_passed_objects": 0}], track="weapon")
    assert short["stuck"] is False, short

    # (g) the PRIMARY-ADVERSARY misroute: task KNOWN to need Opus routed to Haiku.
    #     route_planner FLAGS the misroute (FOOTING is the ship-time backstop).
    mis = cheapest_path({"routine_generation": True, "required_tier": "opus"})
    assert mis["tier"] == "haiku" and mis["misrouted_below_required_tier"] is True, mis
    assert "misroute" in mis["note"].lower(), mis
    #     a correctly-routed task is NOT flagged
    okr = cheapest_path({"hard_unexecutable": True, "required_tier": "opus"})
    assert okr["misrouted_below_required_tier"] is False, okr

    # per-track verified-fact-delta unit checks (the per-track definition)
    dw, fw = verified_fact_delta({"gate_passed_objects": 1}, {"gate_passed_objects": 2}, "weapon")
    assert dw == 1 and fw == "gate_passed_objects"
    da, fa = verified_fact_delta({"grounded_claims": 3}, {"grounded_claims": 3}, "armor")
    assert da == 0 and fa == "grounded_claims"
    dk, fk = verified_fact_delta({"escalations_recorded": 0}, {"escalations_recorded": 1}, "kappa0")
    assert dk == 1 and fk == "escalations_recorded"

    print("route_planner selftest: PASS")
    print("  (d) machine-checkable->EXECUTE(no model,$0); interpretation->ARMOR; routine->Haiku; hard-unexec->Opus")
    print("  (e) N zero-verified-fact-delta iters (per-track) -> STRATEGY_SWITCH/impasse (anti-loop hard cap)")
    print("  (f) productive search & a too-short single task -> NOT falsely halted")
    print("  (g) PRIMARY ADVERSARY: Opus-needed task routed to Haiku -> FLAGGED misrouted_below_required_tier")
    print("  (+) per-track verified-fact-delta: weapon=gate-passed-object; armor=grounded-claim; kappa0=escalation")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        import json
        print(json.dumps(cheapest_path(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: route_planner.py selftest | <task.json>")
