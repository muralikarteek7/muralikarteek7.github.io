#!/usr/bin/env python3
"""TRIAGE router — given a failure-class flag, decide WHERE it goes.

Mirrors the box's other routers (symbolica/factharness/...): the decisive question is
the kappa of the row's detector.
  * kappa=1 row  -> a MACHINE check (run/compose the frozen checker; the verdict is the
                    result).
  * kappa<1 row  -> the CROSS-MODEL panel (a model != the generator) OR a scored
                    abstention -- a routed JUDGMENT, never a certification.
  * no class fired -> "no listed class fired" (NEVER 'safe'); novel classes still escape.

It decides routing; it does not run the math. It is ARMOR plumbing, not a weapon.
"""
import sys, json
import triage_check as tc

# class -> (track, destination, rationale). Tracks: "machine" (kappa=1) | "panel" (kappa<1).
ROUTE = {
    "fabrication":                          ("machine", "FACTHARNESS ground() (kappa=1; degrades to cross-model judge if absent)"),
    "circular-measurement":                 ("machine", "structural provenance check (kappa=1): eval-data source != generator"),
    "numeric-branch-cut-convergence":       ("machine", "full-domain / multi-point sampling (kappa=1; SYMBOLICA lesson)"),
    "crash-silent-pass-on-malformed-input": ("machine", "adversarial-input probe (kappa=1 on 'errored loudly?'; CRUCIBLE for a richer adversary)"),
    "specification-gaming":                 ("machine", "in-sample/OOS-provenance check (kappa=1 WITH a CRUCIBLE oracle; else kappa<1 structural)"),
    "overconfidence":                       ("panel",   "cross-model audit (model != generator) OR fetch/execute; else abstain"),
    "distribution-shift":                   ("panel",   "lower confidence explicitly; abstain on load-bearing"),
    "shared-blind-spot":                    ("panel",   "add a methodologically-DIFFERENT check (cross-model > cross-instruction)"),
}

CEILING = tc.CEILING


def route(record):
    """Run triage_check, then assign each FIRED class to a track. Returns a routing plan.
    Raises TriageAbstain (loudly) on a malformed record."""
    report = tc.triage_check(record)
    routed = []
    for cls in report["fired_classes"]:
        track, dest = ROUTE.get(cls, ("panel", "unknown class -> cross-model panel + abstain"))
        # honest downgrade: if a 'machine' row ran degraded (checker absent), it is panel-grade.
        row = next(r for r in report["rows"] if r["class"] == cls)
        if track == "machine" and row.get("degraded"):
            track = "panel"
            dest = "DEGRADED (frozen checker absent) -> cross-model panel; do NOT certify. " + dest
        routed.append({"class": cls, "track": track, "destination": dest,
                       "kappa": row["kappa"], "mandated_action": row["mandated_action"]})
    plan = {
        "tool": "TRIAGE-ROUTER",
        "fired": report["fired_classes"],
        "machine_track": [r for r in routed if r["track"] == "machine"],
        "panel_track":   [r for r in routed if r["track"] == "panel"],
        "overall": report["overall"],
        "uncovered_novel_classes": report["uncovered_novel_classes"],   # always True
        "ceiling": CEILING,
    }
    if not report["fired_classes"]:
        plan["note"] = ("no listed class fired (coverage = these %d classes; novel/unknown "
                        "classes are NOT covered and may escape). NOT a safety proof."
                        % report["n_coverage"])
    return plan


def _selftest():
    # a kappa=1 class (branch-cut) -> the MACHINE track
    r = route(tc.real_failure_symbolica_branch_cut())
    assert any(x["class"] == "numeric-branch-cut-convergence" for x in r["machine_track"]), r
    assert r["machine_track"][0]["track"] == "machine"

    # a kappa=1 class (circular measurement) -> MACHINE track
    r = route(tc.real_failure_proofsmith_answer_key_leak())
    assert any(x["class"] == "circular-measurement" for x in r["machine_track"]), r

    # a kappa<1 class (overconfidence) -> the PANEL track
    over = {"text": "x", "claims": [{"text": "load-bearing unverified", "load_bearing": True}]}
    r = route(over)
    assert any(x["class"] == "overconfidence" for x in r["panel_track"]), r
    assert not r["machine_track"], r

    # a kappa<1 class (shared-blind-spot) -> PANEL track
    sbs = {"text": "x", "verifiers": {"families": ["numeric", "numeric"], "agree": True}}
    r = route(sbs)
    assert any(x["class"] == "shared-blind-spot" for x in r["panel_track"]), r

    # empty/clean record -> no class fired, note carries coverage + novel caveat, NEVER 'safe'
    r = route({"text": "clean", "provenance": {"eval_data_source": "holdout",
                                               "generator_source": "model"}})
    assert r["fired"] == [], r
    assert "may escape" in r["note"] and "all-clear" not in r["note"].lower(), r
    assert r["uncovered_novel_classes"] is True

    # malformed -> abstain LOUDLY (router must not swallow)
    try:
        route(None)
        assert False, "router did not abstain on malformed record"
    except tc.TriageAbstain:
        pass

    # ceiling always present, naming the armor-not-weapon doctrine
    assert "ARMOR, not a weapon" in route({"text": "x"})["ceiling"]

    print("triage_router selftest: PASS (branch-cut->machine; circular->machine; overconfidence->panel; "
          "shared-blind-spot->panel; clean->no-class-fired+coverage caveat (never 'safe'); "
          "malformed->abstain loud; degraded-machine->downgraded to panel)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2, default=str))
    else:
        print("usage: triage_router.py selftest | <record.json>")
