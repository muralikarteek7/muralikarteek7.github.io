#!/usr/bin/env python3
"""CRUCIBLE probe of trialguard_grim — the kappa=1 GRIM exact-arithmetic slice.

TARGET (black-box, real gate): the EXACT GRIM check the trialguard weapon uses.
  trialguard/forensics_trial_verify.py imports the psymetrix GRIM core as `PF`
  (line: `import forensics_verify as PF`). The kappa=1 exact-arithmetic check the
  prompt names ("reported mean achievable as k/(N*items)") IS PF.grim. We reach it
  THROUGH the trialguard module object (forensics_trial_verify.PF.grim) so the
  adapter calls the real gate as the trialguard weapon itself calls it — NOT a
  re-implementation. We do NOT probe the Carlisle heuristic screen (kappa=0.9,
  inconsistency!=fraud rail), per the target note.

ORACLE: the existing independent oracle crucible/oracles/grim_oracle.py — a
  from-scratch exact Fraction GRIM, authored foreign to the psymetrix/trialguard
  gate. We register a control grid (>=3 good, >=3 bad) spanning the probed regime.

Runs all four modes: false-accept, false-reject, metamorphic, abstain/crash.
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
CRUCIBLE = os.path.dirname(HERE)
ARSENAL = os.path.dirname(CRUCIBLE)
PSYMETRIX = os.path.join(ARSENAL, "psymetrix")
TRIALGUARD = os.path.join(ARSENAL, "trialguard")

# psymetrix must be importable because trialguard's module imports `forensics_verify`.
for p in (CRUCIBLE, PSYMETRIX, TRIALGUARD):
    if p not in sys.path:
        sys.path.insert(0, p)

import crucible_harness as CH
from crucible_harness import (
    GateAdapter, Oracle, ACCEPT, REJECT, ABSTAIN, ERROR,
    false_accept_hunt, false_reject_hunt, metamorphic_hunt, abstain_crash_hunt,
)

# ---- import the REAL trialguard weapon module, then reach its GRIM gate -------
import forensics_trial_verify as TG          # the trialguard weapon module
_REAL_GRIM = TG.PF.grim                       # the exact kappa=1 GRIM check it uses

# sanity: confirm we are calling the genuine psymetrix gate object (not a copy)
import forensics_verify as PF
assert _REAL_GRIM is PF.grim, "adapter is NOT bound to the real psymetrix grim gate"

# ---- the independent oracle (foreign from-scratch Fraction GRIM) -------------
from oracles import grim_oracle as ORC
assert ORC.grim_consistent is not _REAL_GRIM, "oracle must not BE the gate"


# --------------------------------------------------------------------------- #
#  GATE ADAPTER — call the REAL gate; map its native dict -> ACCEPT/REJECT/ABSTAIN
# --------------------------------------------------------------------------- #
def grim_gate_fn(mean_str, n, items=1):
    """Calls the REAL trialguard/psymetrix GRIM gate (no reimplementation)."""
    return _REAL_GRIM(mean_str, n, items)


def to_verdict(raw):
    """Map the gate's native return to the CRUCIBLE verdict vocabulary.

    The gate dict has `consistent` in {True, False, None}:
      None  -> ABSTAIN (the gate's n<=0/items<=0 R1 guard, or undefined)
      True  -> ACCEPT  (mean IS GRIM-achievable; includes the `powerless` case where
               the gate reports consistent=True with no discriminating power)
      False -> REJECT  (mean is GRIM-impossible for the stated N/scale)
    """
    c = raw.get("consistent")
    if c is None:
        return ABSTAIN
    return ACCEPT if c else REJECT


gate = GateAdapter("trialguard_grim", grim_gate_fn, to_verdict)


# --------------------------------------------------------------------------- #
#  ORACLE — the independent oracle, with a control grid spanning the regime.
#  truth() comes from the FOREIGN grim_oracle.truth_correct_or_wrong.
# --------------------------------------------------------------------------- #
def oracle_truth(obj):
    # grim_oracle.truth_correct_or_wrong returns "CORRECT"/"WRONG"/None
    return ORC.truth_correct_or_wrong(obj)


# Control grid spanning the probed regime: decimal precision D in {0,1,2,3} and
# items in {1,2,3}. Each control's expected polarity is computed from the FOREIGN
# oracle by hand-verified arithmetic (the harness re-checks them in is_sane()).
controls_good = [
    {"mean_str": "3.0",   "n": 20, "items": 1},   # 1dp, 60/20 exact
    {"mean_str": "3",     "n": 20, "items": 1},   # 0dp
    {"mean_str": "2.50",  "n": 20, "items": 1},   # 2dp, 50/20
    {"mean_str": "0.250", "n": 4,  "items": 1},   # 3dp, 1/4
    {"mean_str": "2.5",   "n": 10, "items": 2},   # items=2, Neff=20
    {"mean_str": "5.90",  "n": 40, "items": 3},   # items=3, Neff=120 (powerless regime)
]
controls_bad = [
    {"mean_str": "5.19",  "n": 28, "items": 1},   # 2dp, no k/28
    {"mean_str": "0.2",   "n": 7,  "items": 1},   # 1dp, band 1/20 misses every k/7
    {"mean_str": "3.001", "n": 20, "items": 1},   # 3dp, no k/20
    {"mean_str": "2.51",  "n": 20, "items": 1},   # 2dp, 50.2/20
    {"mean_str": "0.001", "n": 4,  "items": 1},   # 3dp, no k/4
    {"mean_str": "2.51",  "n": 10, "items": 2},   # items=2, Neff=20, no k/20
]

oracle = Oracle(
    "GRIM-arith-foreign", oracle_truth, is_independent=True,
    method="from-scratch exact Fraction GRIM (crucible/oracles/grim_oracle.py); "
           "foreign to the psymetrix/trialguard gate engine",
    controls_good=controls_good, controls_bad=controls_bad,
)


# --------------------------------------------------------------------------- #
#  CANDIDATE STREAM — boundary-rich GRIM objects across D in {0,1,2,3}, items in
#  {1,2,3}, small discriminating n, achievable + deliberately-off means.
# --------------------------------------------------------------------------- #
def candidates():
    out, seen = [], set()

    def emit(mean_str, n, items):
        key = (mean_str, n, items)
        if key not in seen:
            seen.add(key)
            out.append({"mean_str": mean_str, "n": n, "items": items})

    for items in (1, 2, 3):
        for n in range(3, 40):
            for k in range(0, n * 5 + 1):
                m = k / n                  # an achievable mean at full precision
                off = (k + 0.5) / n        # a deliberately-off mean (likely impossible)
                for D in (0, 1, 2, 3):
                    emit(f"{m:.{D}f}", n, items)
                    emit(f"{off:.{D}f}", n, items)
    return out


COVERAGE = ("decimal precision D in {0,1,2,3}; items in {1,2,3}; n in [3,40); "
            "achievable + deliberately-off means; kappa=1 GRIM exact-arithmetic "
            "slice ONLY (Carlisle heuristic screen NOT probed). NOT probed: D>=4, "
            "items>=4, n>=40, non-decimal means.")


# --------------------------------------------------------------------------- #
#  METAMORPHIC — items-split transform: move a factor of 2 from n into items.
#  GRIM consistency depends only on Neff=n*items, so this is meaning-preserving.
#  The oracle is passed so the A11 transform-validation guard is active.
# --------------------------------------------------------------------------- #
def items_split(obj):
    n, it = int(obj["n"]), int(obj.get("items", 1))
    if n % 2 == 0:
        return {"mean_str": obj["mean_str"], "n": n // 2, "items": it * 2}
    raise ValueError("n not even -- transform inapplicable")


def malformed_inputs():
    safe = {ABSTAIN, REJECT, ERROR}
    return [
        ("n=0 (undefined)",  {"mean_str": "3.0", "n": 0,  "items": 1}, safe),
        ("n=-5 (negative)",  {"mean_str": "3.0", "n": -5, "items": 1}, safe),
        ("n='garbage'",      {"mean_str": "3.0", "n": "garbage", "items": 1}, safe),
        ("items=0",          {"mean_str": "3.0", "n": 10, "items": 0}, safe),
        ("items=-3",         {"mean_str": "3.0", "n": 10, "items": -3}, safe),
        ("mean as float (R4 guard)", {"mean_str": 3.0, "n": 10, "items": 1}, safe),
    ]


def main():
    print("=" * 78)
    print("CRUCIBLE probe: trialguard_grim (kappa=1 GRIM exact-arithmetic slice)")
    print("real gate entrypoint:", f"{TG.__name__}.PF.grim",
          "(is psymetrix.forensics_verify.grim:", _REAL_GRIM is PF.grim, ")")
    print("oracle:", oracle.method)
    print("=" * 78)

    # Pre-flight: confirm the oracle is sane on its control grid (else no KILL ships).
    sane, detail = oracle.is_sane()
    print("ORACLE SANITY:", sane, "--", detail)
    if not sane:
        print("ABORT: oracle not sane; no hunt can ship a KILL.")
        return

    cands = candidates()
    print(f"candidate stream size: {len(cands)}")
    print("-" * 78)

    # ---- (1) FALSE-ACCEPT ----
    fa = false_accept_hunt(gate, oracle, cands, max_probes=200000, coverage_note=COVERAGE)
    print("FALSE-ACCEPT:")
    print(json.dumps(fa.to_dict(), indent=2, default=str))
    print("-" * 78)

    # ---- (2) FALSE-REJECT ----
    fr = false_reject_hunt(gate, oracle, cands, max_probes=200000, coverage_note=COVERAGE)
    print("FALSE-REJECT:")
    print(json.dumps(fr.to_dict(), indent=2, default=str))
    print("-" * 78)

    # ---- (3) METAMORPHIC (items-split, oracle-validated) ----
    even = [c for c in cands if int(c["n"]) % 2 == 0]
    mm = metamorphic_hunt(gate, even, [("items-split (Neff-invariant)", items_split)],
                          max_probes=200000, oracle=oracle)
    print(f"METAMORPHIC (seeds={len(even)} even-n objects, oracle-validated transform):")
    print(json.dumps(mm.to_dict(), indent=2, default=str))
    print("-" * 78)

    # ---- (4) ABSTAIN/CRASH ----
    ac = abstain_crash_hunt(gate, malformed_inputs(), max_probes=100)
    print("ABSTAIN/CRASH:")
    print(json.dumps(ac.to_dict(), indent=2, default=str))
    print("-" * 78)

    any_kill = any(d.to_dict().get("KILL") for d in (fa, fr, mm, ac))
    print("ANY KILL:", any_kill)


if __name__ == "__main__":
    main()
