#!/usr/bin/env python3
"""CRUCIBLE killer demo. Predictions are committed in PREDICTION.md BEFORE this runs.

Four parts:
  (i)   BLIND-planted false-accept in a COPY of the REAL codeforge sortnet gate -> predict KILL.
  (ii)  planted metamorphic instability in a GRIM copy -> predict verdict-flip KILL.
  (iii) the REAL, unmodified codeforge + psymetrix gates -> predict NO false alarm (SURVIVED).
  (iv)  the real-arsenal sweep over the two real gates, all four modes -> predict clean sweep.

Writes RESULTS.md and results.json. Exits 0 on success (predictions met / honest report).
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
CRUCIBLE = os.path.dirname(HERE)
ARSENAL = os.path.dirname(CRUCIBLE)

# import the frozen harness + oracles
sys.path.insert(0, CRUCIBLE)
sys.path.insert(0, os.path.join(CRUCIBLE, "oracles"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ARSENAL, "codeforge"))
sys.path.insert(0, os.path.join(ARSENAL, "psymetrix"))

import crucible_harness as ch
from crucible_harness import (GateAdapter, Oracle, ACCEPT, REJECT, ABSTAIN, ERROR,
                              CORRECT, WRONG, Kill, Survived, LCG,
                              false_accept_hunt, false_reject_hunt,
                              metamorphic_hunt, abstain_crash_hunt)
import sortnet_oracle
import grim_oracle
import sortnet_verify                       # the REAL codeforge gate
import forensics_verify                     # the REAL psymetrix gate
from planted_sortnet_gate import verify_sorting_network_PLANTED


# --------------------------------------------------------------------------- #
#  candidate generators
# --------------------------------------------------------------------------- #
def sortnet_candidates(n=4, seed=7, count=4000):
    """Random small comparator networks on n wires, plus a near-optimal seed and its
    one-comparator-dropped mutants (boundary-rich: a dropped comparator is the classic
    'almost a sorter' that a sweep off-by-one might wrongly ACCEPT)."""
    rng = LCG(seed)
    pairs = [(i, j) for i in range(n) for j in range(n) if i < j]
    optimal4 = [(0, 1), (2, 3), (0, 2), (1, 3), (1, 2)]
    out = []
    # the optimal sorter itself (oracle: CORRECT) and each single-drop mutant (oracle: likely WRONG)
    out.append({"network": list(optimal4), "n": n})
    for d in range(len(optimal4)):
        out.append({"network": [c for k, c in enumerate(optimal4) if k != d], "n": n})
    # random networks of varied length -- many will NOT sort; the hunt seeks one the
    # buggy gate ACCEPTS but the oracle rejects
    for _ in range(count):
        length = rng.randint(3, 7)
        net = [rng.choice(pairs) for _ in range(length)]
        out.append({"network": net, "n": n})
    return out


def grim_candidates():
    """Reuse the harness's boundary-rich GRIM candidate stream (small n, 2-dp means)."""
    return ch._grim_candidates()


def grim_metamorphic_seeds():
    cands = grim_candidates()
    return [c for c in cands if int(c["n"]) % 2 == 0]


# --------------------------------------------------------------------------- #
#  adapters / oracles for the real + planted gates
# --------------------------------------------------------------------------- #
def sortnet_to_verdict(raw):
    v = raw.get("valid")
    if v is None:
        return ABSTAIN
    if raw.get("verdict") == "MALFORMED":
        return REJECT
    return ACCEPT if v else REJECT


def grim_to_verdict(raw):
    c = raw.get("consistent")
    if c is None:
        return ABSTAIN
    return ACCEPT if c else REJECT


def sortnet_oracle_obj():
    # CONTROL GRID (AUDIT A2 fix): >=3 known-good sorters AND >=3 known-bad non-sorters across
    # n in {2,3,4}, so a subtly-wrong oracle cannot pass a 2-point check and ship a spurious kill.
    good = [
        {"network": [(0, 1), (2, 3), (0, 2), (1, 3), (1, 2)], "n": 4},   # optimal 4-sorter
        {"network": [(0, 2), (1, 3), (0, 1), (2, 3), (1, 2)], "n": 4},   # a 2nd valid 4-sorter
        {"network": [(0, 1), (1, 2), (0, 1)], "n": 3},                   # a 3-wire sorter
        {"network": [(0, 1)], "n": 2},                                   # the 2-wire sorter
    ]
    bad = [
        {"network": [(0, 1), (2, 3), (0, 2), (1, 3)], "n": 4},           # missing (1,2)
        {"network": [(0, 1), (2, 3)], "n": 4},                           # only two comparators
        {"network": [(0, 1), (1, 2)], "n": 3},                           # incomplete 3-wire
        {"network": [], "n": 2},                                         # empty -> not a sorter
    ]
    return Oracle("sortnet-0/1-enum", sortnet_oracle.truth_correct_or_wrong,
                  is_independent=True,
                  method="from-scratch exhaustive 0/1 enumeration (foreign to synthesis)",
                  controls_good=good, controls_bad=bad)


def grim_oracle_obj():
    # CONTROL GRID (AUDIT A2 fix): spans decimal precisions {0,1,2,3} AND items {1,2}.
    good = [
        {"mean_str": "3.0", "n": 20, "items": 1},
        {"mean_str": "3", "n": 20, "items": 1},
        {"mean_str": "2.50", "n": 20, "items": 1},
        {"mean_str": "3.000", "n": 20, "items": 1},
        {"mean_str": "2.5", "n": 10, "items": 2},
        {"mean_str": "0.250", "n": 4, "items": 1},
    ]
    bad = [
        {"mean_str": "5.19", "n": 28, "items": 1},
        {"mean_str": "0.2", "n": 7, "items": 1},
        {"mean_str": "3.001", "n": 20, "items": 1},
        {"mean_str": "2.51", "n": 20, "items": 1},
        {"mean_str": "0.001", "n": 4, "items": 1},
        {"mean_str": "2.51", "n": 10, "items": 2},
    ]
    return Oracle("grim-fraction", grim_oracle.truth_correct_or_wrong,
                  is_independent=True,
                  method="from-scratch exact Fraction GRIM (foreign to psymetrix gate)",
                  controls_good=good, controls_bad=bad)


def sortnet_malformed():
    safe = {ABSTAIN, REJECT, ERROR}
    return [
        ("n=0",                {"network": [(0, 1)], "n": 0}, safe),
        ("n=-3",               {"network": [(0, 1)], "n": -3}, safe),
        ("comparator i==j",    {"network": [(0, 0)], "n": 3}, safe),
        ("comparator out-of-range", {"network": [(0, 9)], "n": 3}, safe),
        ("non-pair comparator", {"network": [(0, 1, 2)], "n": 3}, safe),
        ("n too large",        {"network": [(0, 1)], "n": 30}, safe),
    ]


def grim_malformed():
    safe = {ABSTAIN, REJECT, ERROR}
    return [
        ("n=0",        {"mean_str": "3.0", "n": 0, "items": 1}, safe),
        ("n=-5",       {"mean_str": "3.0", "n": -5, "items": 1}, safe),
        ("float mean", {"mean_str": 3.0, "n": 10, "items": 1}, safe),    # real gate raises TypeError
        ("items=0",    {"mean_str": "3.0", "n": 10, "items": 0}, safe),
    ]


# items-split transform for GRIM (Neff-invariant), even-n only
def grim_items_split_transforms():
    return ch._items_split_transforms()


# --------------------------------------------------------------------------- #
#  RUN
# --------------------------------------------------------------------------- #
def serialize(result):
    return result.to_dict() if hasattr(result, "to_dict") else result


def main():
    report = {"parts": {}}
    BUDGET = 5000

    # ---------- Part (i): BLIND-planted false-accept on a COPY of the real sortnet gate
    planted = GateAdapter("codeforge-sortnet-PLANTED", verify_sorting_network_PLANTED,
                          sortnet_to_verdict)
    oracle_s = sortnet_oracle_obj()
    cands_s = sortnet_candidates()
    fa_planted = false_accept_hunt(planted, oracle_s, cands_s, max_probes=BUDGET)
    report["parts"]["i_blind_planted_false_accept"] = serialize(fa_planted)

    # ---------- Part (ii): planted metamorphic instability (GRIM ignores items)
    buggy_mm = GateAdapter("GRIM-metamorphic-PLANTED", ch._grim_gate_METAMORPHIC_BUG,
                           ch._grim_to_verdict)
    # pass the independent oracle so the A11 transform-validation guard confirms the items-split
    # transform is genuinely meaning-preserving before shipping the metamorphic KILL.
    mm_planted = metamorphic_hunt(buggy_mm, grim_metamorphic_seeds(),
                                  grim_items_split_transforms(), max_probes=40000,
                                  oracle=grim_oracle_obj())
    report["parts"]["ii_planted_metamorphic"] = serialize(mm_planted)

    # ---------- Part (iii)+(iv): the REAL, unmodified gates -> predict NO false alarm
    # REAL codeforge sortnet, all four modes
    real_sortnet = GateAdapter("codeforge-sortnet-REAL", sortnet_verify.verify_sorting_network,
                               sortnet_to_verdict)
    real_grim = GateAdapter("psymetrix-grim-REAL", forensics_verify.grim, grim_to_verdict)

    grim_cov = ch._grim_candidate_coverage()
    sweep = {}
    sweep["codeforge_sortnet"] = {
        "false_accept": serialize(false_accept_hunt(real_sortnet, oracle_s, cands_s, max_probes=BUDGET)),
        "false_reject": serialize(false_reject_hunt(real_sortnet, oracle_s, cands_s, max_probes=BUDGET)),
        "metamorphic":  serialize(metamorphic_hunt(real_sortnet,
                                                   [c for c in cands_s][:1000],
                                                   _sortnet_relabel_transforms(), max_probes=BUDGET,
                                                   oracle=oracle_s)),
        "abstain_crash": serialize(abstain_crash_hunt(real_sortnet, sortnet_malformed(), max_probes=50)),
    }
    sweep["psymetrix_grim"] = {
        "false_accept": serialize(false_accept_hunt(real_grim, grim_oracle_obj(), grim_candidates(),
                                                    max_probes=BUDGET, coverage_note=grim_cov)),
        "false_reject": serialize(false_reject_hunt(real_grim, grim_oracle_obj(), grim_candidates(),
                                                    max_probes=BUDGET, coverage_note=grim_cov)),
        "metamorphic":  serialize(metamorphic_hunt(real_grim, grim_metamorphic_seeds(),
                                                   grim_items_split_transforms(), max_probes=40000,
                                                   oracle=grim_oracle_obj())),
        "abstain_crash": serialize(abstain_crash_hunt(real_grim, grim_malformed(), max_probes=50)),
    }
    report["parts"]["iii_iv_real_arsenal_sweep"] = sweep

    # ---------- verdict check vs predictions
    p_i_kill = isinstance(fa_planted, Kill)
    p_ii_kill = isinstance(mm_planted, Kill)
    real_kills = []
    for w, modes in sweep.items():
        for m, r in modes.items():
            if r.get("KILL"):
                real_kills.append((w, m, r))
    no_false_alarm = (len(real_kills) == 0)

    summary = {
        "i_planted_false_accept_caught": p_i_kill,
        "ii_planted_metamorphic_caught": p_ii_kill,
        "iii_iv_real_gates_clean_sweep": no_false_alarm,
        "real_gate_kills": [(w, m) for (w, m, _) in real_kills],
        "predictions_met": p_i_kill and p_ii_kill,   # real-gate outcome reported either way
    }
    report["summary"] = summary

    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(report, f, indent=2, default=str)

    # human-readable RESULTS.md
    _write_results_md(report)

    # ---- console
    print("=" * 78)
    print("CRUCIBLE DEMO RESULTS")
    print("=" * 78)
    print(f"(i)   BLIND-planted false-accept (sortnet copy):  "
          f"{'KILL exhibited' if p_i_kill else 'NOT caught (FAIL)'}")
    if p_i_kill:
        print(f"      exhibit network={fa_planted.obj['network']} n={fa_planted.obj['n']} "
              f"| gate={fa_planted.gate_verdict} oracle={fa_planted.oracle_verdict}")
    print(f"(ii)  planted metamorphic instability (GRIM):     "
          f"{'KILL exhibited' if p_ii_kill else 'NOT caught (FAIL)'}")
    if p_ii_kill:
        print(f"      base={mm_planted.obj} {mm_planted.gate_verdict} -> "
              f"T={mm_planted.transform!r} {mm_planted.obj2} {mm_planted.gate_verdict2}")
    if no_false_alarm:
        print("(iii/iv) REAL gates sweep: CLEAN (no false alarm)")
    else:
        print(f"(iii/iv) REAL gates sweep: KILLS={summary['real_gate_kills']}")
    for w, modes in sweep.items():
        for m, r in modes.items():
            tag = "KILL" if r.get("KILL") else "SURVIVED"
            print(f"      {w:22s} {m:14s} {tag}")
    print("=" * 78)
    # exit 0 if the two planted bugs were caught (the demo's load-bearing claim);
    # a real-gate KILL is reported honestly but does not fail the demo.
    ok = p_i_kill and p_ii_kill
    print("DEMO:", "PASS (both planted bugs caught; real-gate outcome reported honestly)"
          if ok else "FAIL (a planted bug was NOT caught -- CRUCIBLE is theater)")
    sys.exit(0 if ok else 1)


def _sortnet_relabel_transforms():
    """A meaning-preserving transform for sorting networks: a sorting network is NOT
    invariant under arbitrary wire relabels (that changes the object), so we use a
    TRUE invariant: a no-op duplicate-then-dedup is identity. For metamorphic on sortnet
    we use the identity transform (verdict must be stable on a re-presented object) and a
    benign reordering of INDEPENDENT comparators is NOT generally safe, so we keep the
    conservative identity check (catches a nondeterministic gate)."""
    def identity(obj):
        return {"network": list(obj["network"]), "n": obj["n"]}
    return [("identity (determinism check)", identity)]


def _write_results_md(report):
    lines = ["# CRUCIBLE DEMO RESULTS (generated by run_demo.py)", "",
             "Predictions were committed in `PREDICTION.md` BEFORE this ran. Compare below.", ""]
    s = report["summary"]
    lines += ["## Summary", "",
              f"- (i) BLIND-planted false-accept caught: **{s['i_planted_false_accept_caught']}**",
              f"- (ii) planted metamorphic instability caught: **{s['ii_planted_metamorphic_caught']}**",
              f"- (iii/iv) real gates CLEAN sweep (no false alarm): **{s['iii_iv_real_gates_clean_sweep']}**",
              f"- real-gate KILLs (reported honestly, none expected): `{s['real_gate_kills']}`", ""]
    fa = report["parts"]["i_blind_planted_false_accept"]
    if fa.get("KILL"):
        lines += ["## (i) κ=1 KILL — blind-planted false-accept exhibit", "",
                  "```json", json.dumps(fa, indent=2, default=str), "```", ""]
    mm = report["parts"]["ii_planted_metamorphic"]
    if mm.get("KILL"):
        lines += ["## (ii) κ=1 KILL — planted metamorphic-instability exhibit", "",
                  "```json", json.dumps(mm, indent=2, default=str), "```", ""]
    lines += ["## (iii)+(iv) real-arsenal sweep (SURVIVED-to-budget, with residual risk)", ""]
    for w, modes in report["parts"]["iii_iv_real_arsenal_sweep"].items():
        lines += [f"### {w}", ""]
        for m, r in modes.items():
            tag = "KILL" if r.get("KILL") else "SURVIVED"
            rr = r.get("residual_risk", r.get("note", ""))
            lines += [f"- **{m}**: {tag} — {rr}"]
        lines += [""]
    lines += ["## Honesty rail", "",
              "A SURVIVED report is CONFIDENCE, not a soundness proof (Dijkstra). The word "
              "'sound'/'proven' is machine-banned from these reports (selftest_all.py case e). "
              "Coverage here is the two real κ=1 gates with importable hermetic oracles; "
              "FACTHARNESS/REDCELL/Frontier are full-differential in the scope table but need a "
              "fetch / committed-answer fixture / capset module, out of this hermetic demo."]
    with open(os.path.join(HERE, "RESULTS.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
