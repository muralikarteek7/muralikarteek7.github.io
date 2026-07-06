#!/usr/bin/env python3
"""OPTIMA router — given an optimization ask, decide WHICH mode fires, or whether it is
kappa=0 (a fuzzy 'optimize our strategy' with no formalizable exact objective) and belongs to
ARMOR, not the weapon. The CS_ENG/OR analogue of the v5 WHEN/WHERE router (BOX_V5.md section 2).

Optimization has a sharp cheap verifier WHEN the problem has a clean discrete model: re-evaluate
every constraint on the returned solution (feasibility) + recompute the objective + a matching
dual/bound (optimality). So a well-posed discrete model is kappa=1, weapon-eligible. Two classes
are NOT, and routing them to the weapon is theater the box forbids:
  * kappa=0 fuzzy objective  — "optimize our business strategy", any goal with no formalizable
    exact objective/constraints, or a deliverable scored by a gameable proxy. -> ARMOR (ground+abstain).
  * the MODELING joint (kappa<1, ALWAYS) — translating words -> vars/constraints/objective is
    JUDGMENT. Even when a clean model exists, the certificate covers the FORMAL MODEL only; the
    modeling needs an independent CROSS-MODEL review. This is flagged on EVERY weapon route.

The three weapon modes (each gated by the independent 4-part certificate, optima_gate.py):
  EXACT-SOLVE   : clean discrete model, tractable -> certified-optimal solution (gap=0 / dual /
                  independent-method certificate).
  BOUND-PROVE   : hard/large -> best feasible solution + a RIGOROUS independent dual/relaxation
                  bound + the honest gap. NEVER 'optimal' on a timeout (the W2 failure-mode rail).
  REPRODUCE-RECORD: a benchmark instance (TSPLIB/MIPLIB) with a published optimum -> reproduce +
                  re-check against the literature, labeled REPRODUCTION. A record needs an audited
                  certificate strictly beating prior art -> honest negative expected.

CONFLICT RULE (BOX_V5): a task matching a POSITIVE trigger AND a NEGATIVE item -> NEGATIVE wins
(weapon OFF) -> route to armor. Deterministic; self-tested.
"""
import sys
import json

# precondition_key -> (MODE, kappa, branch, rationale)
POSITIVE_RULES = [
    ("clean_discrete_model_tractable", "EXACT-SOLVE", 1.0, "EXACT",
     "clean discrete model, small/structured -> certified-optimal via the independent gate "
     "(gap=0 / matching dual / a different exact method)"),
    ("clean_discrete_model_hard", "BOUND-PROVE", 1.0, "BOUND",
     "model is clean but hard/large -> best feasible + a RIGOROUS independent bound + honest "
     "gap; timeout is a BOUND, never optimal (W2 rail)"),
    ("benchmark_instance_known_optimum", "REPRODUCE-RECORD", 1.0, "REPRODUCE",
     "a benchmark (TSPLIB/MIPLIB) with a published optimum -> reproduce + re-check vs the "
     "literature, labeled REPRODUCTION (never a record without an audited strictly-better cert)"),
    ("infeasibility_question", "EXACT-SOLVE", 1.0, "EXACT",
     "a 'does any feasible solution exist?' question -> feasibility/IIS certificate (proof of "
     "infeasibility, not a solver shrug)"),
]

# negative_key -> (kind, rationale).  kind: "kappa0" (no exact objective) or "not_worth_it"
NEGATIVE_RULES = [
    ("fuzzy_objective_no_formal_model", "kappa0",
     "'optimize our strategy' with no formalizable exact objective/constraints -> kappa=0 -> "
     "armor (ground + abstain); do NOT manufacture a certificate"),
    ("proxy_only_scorer", "kappa0",
     "the only scorer is gameable (a soft KPI / in-sample fit / human rating) -> does NOT raise "
     "kappa -> armor; a gameable proxy WILL be gamed"),
    ("trivial_closed_form", "not_worth_it",
     "a closed-form/greedy-optimal special case (e.g. fractional knapsack, a sort) -> armor's "
     "execute-don't-guess already suffices; the solver adds cost and ~0 marginal Q"),
]

CEILING = ("OPTIMA ships ONLY solutions the INDEPENDENT gate re-verified (feasible + objective + "
           "a gap=0/dual certificate). It certifies 'optimal FOR THIS FORMAL MODEL', not optimal "
           "for the real-world problem -- the modeling joint is kappa<1 and is cross-model-reviewed. "
           "Timeouts are reported as bounds-with-gap, never optimal; infeasibility needs an IIS; "
           "fuzzy kappa=0 'optimize our strategy' routes to armor.")

# the modeling caveat is attached to EVERY weapon route (it is never kappa=1)
MODEL_CAVEAT = ("MODELING IS kappa<1: the formulation (words -> vars/constraints/objective) is "
                "judgment and may be wrong even when the solve is exact. Cross-model-review the "
                "model; the certificate covers the FORMAL MODEL only.")


def route(task):
    """task: dict of boolean preconditions. Returns the deterministic routing plan."""
    negatives = [(k, kind, why) for (k, kind, why) in NEGATIVE_RULES if task.get(k)]
    positives = [(k, mode, kap, branch, why)
                 for (k, mode, kap, branch, why) in POSITIVE_RULES if task.get(k)]

    weapon_suppressed = len(negatives) > 0 and len(positives) > 0   # CONFLICT RULE
    armor_track = [{"trigger": k, "kappa": 0.0 if kind == "kappa0" else 1.0,
                    "kind": kind, "rationale": why} for (k, kind, why) in negatives]

    weapon_track = []
    if not weapon_suppressed:
        for (k, mode, kap, branch, why) in positives:
            entry = {"trigger": k, "mode": mode, "kappa": kap, "branch": branch,
                     "rationale": why, "modeling_caveat": MODEL_CAVEAT}
            if mode == "REPRODUCE-RECORD":
                entry["sub_branch"] = ("FETCH the published optimum -> reproduce + re-check; "
                                       "labeled REPRODUCTION. A record needs an audited cert "
                                       "strictly beating prior art (honest negative expected).")
            weapon_track.append(entry)

    plan = {"weapon": "OPTIMA", "weapon_track": weapon_track, "armor_track": armor_track,
            "weapon_suppressed_by_negative": bool(weapon_suppressed),
            "kappa0_armor_only": bool(negatives and not weapon_track),
            "ceiling": CEILING}
    if weapon_suppressed:
        plan["note"] = ("CONFLICT RULE fired: task matched a positive trigger AND a negative item "
                        "-> negative wins, weapon OFF, routed to armor.")
    elif not positives and not negatives:
        plan["note"] = "no precondition matched -> underdefined; FREEZE the model spec, then re-route."
    elif not positives:
        plan["note"] = "kappa=0 task -> ARMOR ONLY (no formalizable exact objective)."
    return plan


def _selftest():
    # EXACT-SOLVE
    p = route({"clean_discrete_model_tractable": True})
    assert [w["mode"] for w in p["weapon_track"]] == ["EXACT-SOLVE"], p
    assert p["weapon_track"][0]["kappa"] == 1.0 and "kappa<1" in p["weapon_track"][0]["modeling_caveat"], p

    # BOUND-PROVE
    p = route({"clean_discrete_model_hard": True})
    assert p["weapon_track"][0]["mode"] == "BOUND-PROVE" and p["weapon_track"][0]["branch"] == "BOUND", p

    # REPRODUCE-RECORD
    p = route({"benchmark_instance_known_optimum": True})
    w = p["weapon_track"][0]
    assert w["mode"] == "REPRODUCE-RECORD" and "REPRODUCTION" in w["sub_branch"], p

    # infeasibility question -> EXACT-SOLVE (IIS branch)
    p = route({"infeasibility_question": True})
    assert p["weapon_track"][0]["mode"] == "EXACT-SOLVE", p

    # kappa=0 fuzzy objective -> armor only
    p = route({"fuzzy_objective_no_formal_model": True})
    assert p["weapon_track"] == [] and p["kappa0_armor_only"] is True, p
    assert p["armor_track"][0]["kappa"] == 0.0, p

    # proxy-only scorer alone -> armor only
    p = route({"proxy_only_scorer": True})
    assert p["weapon_track"] == [] and p["armor_track"][0]["kind"] == "kappa0", p

    # trivial closed form alone -> armor (kappa=1 but not worth it)
    p = route({"trivial_closed_form": True})
    assert p["weapon_track"] == [] and p["armor_track"][0]["kind"] == "not_worth_it", p

    # CONFLICT RULE: positive + negative -> negative wins, weapon OFF
    p = route({"clean_discrete_model_tractable": True, "proxy_only_scorer": True})
    assert p["weapon_suppressed_by_negative"] is True and p["weapon_track"] == [], p

    # underdefined
    p = route({})
    assert p["weapon_track"] == [] and "underdefined" in p["note"], p

    print("OPTIMA-ROUTER selftest: PASS (EXACT/BOUND/REPRODUCE + IIS routed w/ modeling caveat; "
          "kappa=0 fuzzy/proxy + trivial-closed-form -> armor; CONFLICT RULE negative-wins; "
          "underdefined -> freeze)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: optima_router.py selftest | <task.json>")
