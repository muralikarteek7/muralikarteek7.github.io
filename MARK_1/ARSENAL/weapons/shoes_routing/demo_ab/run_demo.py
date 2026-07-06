#!/usr/bin/env python3
"""SHOES_ROUTING A/B-lite demo. Predictions are COMMITTED in PREDICTION.md BEFORE this
runs. The rails decide pass/fail; this script only tabulates. ILLUSTRATION on a tiny
synthetic task set — NOT a benchmark, no kappa=0 quality claim.

Arm A = always-Opus (expensive baseline).  Arm B = ROUTE-PLANNER (cheapest-that-clears).
Cost = sum of relative-cost weights.

HONESTY (audit DEFECT 2 — corrected): this demo generates NO model output and compares
NONE. P1 (cost) is the ONLY empirical A/B claim — routing produces genuinely different
cost weights. The machine-checkable check (formerly mislabelled "no quality regression")
is a STRUCTURAL INVARIANT that is TRUE BY CONSTRUCTION, NOT an empirical quality result:
both arms invoke the IDENTICAL deterministic Python verifier lambda, so "does the same
function return True?" cannot fail regardless of tier. It demonstrates only that routing
machine-checkable tasks to EXECUTE preserves the exact-verifier pass-path — it is NOT
evidence that routing introduces no quality regression on model-generated output (that
would require actually calling models and comparing; out of scope for this deterministic
in-folder demo, and explicitly NOT claimed). See PREDICTION.md P2.
"""
import sys, os, json

# import the rails from the parent folder (sibling modules)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import footing_check
import route_planner

OPUS_COST = route_planner._COST["opus"]   # always-Opus arm pays this per task


# --------------------------------------------------------------------------- #
#  the synthetic task set (8 tasks). `verifier`/`answer` exist ONLY on the
#  machine-checkable subset (the only place we can score quality).
# --------------------------------------------------------------------------- #
def _make_tasks():
    return [
        # machine-checkable computation: an EXACT verifier exists -> EXECUTE, weapon
        {"id": "t1_sum", "flags": {"machine_checkable": True, "has_exact_verifier": True,
                                   "required_tier": "execute"},
         "verifier": lambda: sum(range(1, 101)) == 5050, "kind": "machine_checkable"},
        {"id": "t2_prime", "flags": {"machine_checkable": True, "has_exact_verifier": True,
                                     "required_tier": "execute"},
         "verifier": lambda: all(97 % d for d in range(2, 97)), "kind": "machine_checkable"},
        # hard-but-executable: write+run a solver -> EXECUTE (still cheap), weapon
        {"id": "t3_gcd", "flags": {"hard_but_executable": True, "has_exact_verifier": True,
                                   "required_tier": "execute"},
         "verifier": lambda: __import__("math").gcd(462, 1071) == 21, "kind": "machine_checkable"},
        # routine generation: in-distribution -> Haiku, armor
        {"id": "t4_boilerplate", "flags": {"routine_generation": True, "required_tier": "haiku"},
         "verifier": None, "kind": "routine"},
        # genuinely un-executable hard reasoning -> Opus, armor
        {"id": "t5_hard_reasoning", "flags": {"hard_unexecutable": True, "required_tier": "opus"},
         "verifier": None, "kind": "hard_unexecutable"},
        # interpretation / meaning -> armor (kappa=0)
        {"id": "t6_interpretation", "flags": {"is_interpretation": True, "required_tier": "haiku"},
         "verifier": None, "kind": "interpretation"},
        # ANOTHER machine-checkable -> EXECUTE
        {"id": "t7_factorial", "flags": {"machine_checkable": True, "has_exact_verifier": True,
                                         "required_tier": "execute"},
         "verifier": lambda: __import__("math").factorial(6) == 720, "kind": "machine_checkable"},
        # THE MISROUTE ADVERSARY: truly needs Opus, but flagged only as routine -> cheap-default
        # would send it to Haiku. required_tier=opus lets us detect the misroute after the fact.
        {"id": "t8_misroute_adversary", "flags": {"routine_generation": True, "required_tier": "opus"},
         "verifier": None, "kind": "misroute_adversary"},
    ]


def run_arm_A(tasks):
    """Always-Opus: every task pays Opus cost; machine-checkable tasks still verify."""
    total_cost, q = 0.0, {"checked": 0, "passed": 0}
    for t in tasks:
        total_cost += OPUS_COST
        if t["verifier"] is not None:
            q["checked"] += 1
            q["passed"] += 1 if t["verifier"]() else 0
    return {"arm": "A_always_opus", "total_cost": total_cost, "quality_machinecheckable": q}


def run_arm_B(tasks):
    """ROUTE-PLANNER: cheapest rung that clears the bar. Machine-checkable tasks route to
    EXECUTE and are verified by the SAME exact verifier as Arm A. NOTE (audit DEFECT 2):
    this is a STRUCTURAL invariant (same deterministic function on both arms), NOT a
    model-output quality comparison -- no model is called in either arm."""
    total_cost, q = 0.0, {"checked": 0, "passed": 0}
    routes, misroutes = [], []
    for t in tasks:
        plan = route_planner.cheapest_path(t["flags"])
        total_cost += plan["relative_cost_weight"]
        routes.append({"id": t["id"], "tier": plan["tier"], "track": plan["track"],
                       "cost": plan["relative_cost_weight"],
                       "misrouted": plan["misrouted_below_required_tier"]})
        if plan["misrouted_below_required_tier"]:
            misroutes.append(t["id"])
        if t["verifier"] is not None:
            # Arm B routed it to EXECUTE -> the executed answer is the verifier-passing one.
            q["checked"] += 1
            q["passed"] += 1 if t["verifier"]() else 0
    return {"arm": "B_route_planner", "total_cost": total_cost,
            "quality_machinecheckable": q, "routes": routes,
            "misroutes_flagged": misroutes}


def footing_on_drafts():
    """P3 + P4: FOOTING must flag injected bad drafts and pass matched clean ones, and
    flag the degraded misrouted draft (the (g) backstop at ship time)."""
    oracle = footing_check._equal_text
    bad = [
        # under-grounded: a load-bearing claim with no check
        {"name": "under_grounded",
         "draft": {"claims": [{"text": "the bound is 14", "load_bearing": True, "check": None}]}},
        # paraphrase-unstable: answers disagree
        {"name": "paraphrase_unstable",
         "draft": {"paraphrase_answers": ["7", "12", "20", "3"]}},
        # out-of-distribution input
        {"name": "ood_input",
         "draft": {"task_input": "qz!!~~unseen gibberish prompt xx",
                   "known_good_inputs": ["compute the sum of the column"]}},
    ]
    clean = [
        {"name": "grounded",
         "draft": {"claims": [{"text": "x", "load_bearing": True, "check": "fetched"},
                              {"text": "y", "load_bearing": True, "check": "executed"}]}},
        {"name": "paraphrase_stable",
         "draft": {"paraphrase_answers": ["42", "42", "42"]}},
        {"name": "in_distribution",
         "draft": {"task_input": "compute the sum of the column",
                   "known_good_inputs": ["compute the sum of the column"]}},
    ]
    # the (g) degraded-misroute draft (needs Opus, routed Haiku, under-grounded + unstable)
    misroute_draft = {"claims": [{"text": "lb", "load_bearing": True, "check": None}],
                      "paraphrase_answers": ["the bound is 14", "the bound is 9", "roughly 20"],
                      "required_tier": "opus", "routed_tier": "haiku"}

    bad_results = [{"name": b["name"],
                    "uncertain": footing_check.footing_check(b["draft"], oracle)["uncertain"],
                    "action": footing_check.footing_check(b["draft"], oracle)["action"]} for b in bad]
    clean_results = [{"name": c["name"],
                      "uncertain": footing_check.footing_check(c["draft"], oracle)["uncertain"],
                      "action": footing_check.footing_check(c["draft"], oracle)["action"]} for c in clean]
    mv = footing_check.footing_check(misroute_draft, oracle)
    return {"bad": bad_results, "clean": clean_results,
            "misroute_draft": {"uncertain": mv["uncertain"], "action": mv["action"],
                               "misrouted_below_required_tier": mv["misrouted_below_required_tier"]}}


def stuck_demo():
    """P5: a dead search ends; a productive one continues."""
    flat = [{"gate_passed_objects": 3}] * (route_planner.STUCK_AFTER_N + 1)
    prod = [{"gate_passed_objects": i} for i in range(route_planner.STUCK_AFTER_N + 2)]
    return {"stuck_search": route_planner.stuck_detector(flat, "weapon"),
            "productive_search": route_planner.stuck_detector(prod, "weapon")}


def main():
    tasks = _make_tasks()
    A = run_arm_A(tasks)
    B = run_arm_B(tasks)
    cost_ratio = B["total_cost"] / A["total_cost"] if A["total_cost"] else None
    foot = footing_on_drafts()
    stuck = stuck_demo()

    # --- score the committed predictions (machine decides) ---
    p1 = cost_ratio is not None and cost_ratio < 0.50
    # P2 (audit DEFECT 2 — RELABELLED honestly): this is a STRUCTURAL INVARIANT, true by
    # construction, NOT an empirical no-quality-regression result. Both arms run the SAME
    # deterministic verifier; no model output is generated or compared. It demonstrates
    # only that routing machine-checkable tasks to EXECUTE preserves the exact-verifier
    # pass-path. It is, by design, not falsifiable by model behaviour (there is none) —
    # so it carries NO quality claim. (The old key over-claimed "no_quality_regression".)
    qa, qb = A["quality_machinecheckable"], B["quality_machinecheckable"]
    p2 = (qa["checked"] == qb["checked"] and qb["checked"] > 0 and
          qb["passed"] == qb["checked"] and qa["passed"] == qa["checked"])
    p3 = (all(b["uncertain"] for b in foot["bad"]) and
          all(not c["uncertain"] for c in foot["clean"]))
    md = foot["misroute_draft"]
    planner_flagged = "t8_misroute_adversary" in B["misroutes_flagged"]
    p4 = (planner_flagged and md["uncertain"]) or planner_flagged or md["uncertain"]
    p4_both = planner_flagged and md["uncertain"]
    p5 = (stuck["stuck_search"]["stuck"] is True and
          stuck["stuck_search"]["action"] == "STRATEGY_SWITCH_OR_IMPASSE" and
          stuck["productive_search"]["stuck"] is False)

    results = {
        "note": "ILLUSTRATION on a tiny synthetic task set — NOT a benchmark. No kappa=0 quality claim.",
        "honesty_audit_DEFECT2": ("This demo generates NO model output and compares none. P1 (cost) is the "
                                  "only empirical A/B claim. P2 is a STRUCTURAL INVARIANT (same deterministic "
                                  "verifier on both arms) that is TRUE BY CONSTRUCTION — NOT evidence of "
                                  "'no quality regression' on model output (that is explicitly NOT claimed)."),
        "arm_A_always_opus": A, "arm_B_route_planner": B,
        "cost_ratio_B_over_A": cost_ratio,
        "cost_cut_pct": (None if cost_ratio is None else round((1 - cost_ratio) * 100, 1)),
        "footing_on_drafts": foot, "stuck_detector": stuck,
        "predictions": {
            "P1_cost_cut_over_50pct": bool(p1),
            # RELABELLED (audit DEFECT 2): the old key claimed "no quality regression",
            # which over-claimed. This is a by-construction structural invariant, NOT a quality result.
            "P2_execute_preserves_exact_verifier_pass_BY_CONSTRUCTION_not_a_quality_claim": bool(p2),
            "P3_footing_flags_all_bad_none_clean": bool(p3),
            "P4_misroute_caught_by_at_least_one_rail": bool(p4),
            "P4_misroute_caught_by_BOTH_rails": bool(p4_both),
            "P5_stuck_detector_ends_dead_search": bool(p5),
        },
    }
    all_pass = p1 and p2 and p3 and p4 and p5
    results["ALL_PREDICTIONS_PASS"] = bool(all_pass)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(json.dumps(results, indent=2, default=str))
    print("\n" + "=" * 70)
    print("PREDICTION SCORECARD (machine-decided):")
    for k, v in results["predictions"].items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    print(f"  cost: Arm A={A['total_cost']:.0f}  Arm B={B['total_cost']:.0f}  "
          f"(B is {results['cost_cut_pct']}% cheaper)")
    print("=" * 70)
    print("HONESTY (audit DEFECT 2): P1 (cost) is the ONLY empirical A/B claim. P2 is a")
    print("BY-CONSTRUCTION structural invariant (identical deterministic verifier on both")
    print("arms; NO model output generated/compared) -- NOT a 'no quality regression' result.")
    if not all_pass:
        print("DEMO: at least one committed prediction FAILED — reported as failed (honest).")
        sys.exit(1)
    print("DEMO: all committed predictions hold on this tiny synthetic set (illustration, not a benchmark).")


if __name__ == "__main__":
    main()
