#!/usr/bin/env python3
"""COMPOSEAUTH (G3) committed POLICY inputs.

EVERYTHING in this file is a HUMAN-OWNED POLICY CHOICE, not derived truth
(kickoff §6: "Thresholds are committed POLICY, not derived truth — state them; they
are choices a human owns." and audit Finding 3: "label the blast-radius WEIGHTS as
POLICY inputs (same as the thresholds), not derived truth.").

G3's κ=1 core is the ARITHMETIC: accumulate per-class counters and compare them to
these thresholds. The NUMBERS here are not facts the gate can prove — they encode a
risk appetite a human committed to. The gate is exact about "did the committed sum
cross the committed threshold"; it is silent about whether the threshold is "right".

Two escalation levels per class:
  STEP_UP : the running total crosses this -> the NEXT action is tier-escalated.
  HALT    : the running total crosses this -> HALT + escalate to a human.

Plus a session-wide blast-radius SCORE: Σ (weight_class × count_class). Its weights
AND its HALT bound are policy too.
"""

# === POLICY: per-class thresholds (running total strictly greater than -> trips) ===
# Mirrors the kickoff §2 table. These are EXAMPLE committed values; a deployment owns
# its own. They are choices, not derivations.
THRESHOLDS = {
    # class            STEP_UP    HALT
    "financial":      {"step_up": 100,  "halt": 1000},   # $ committed this session
    "data_mutation":  {"step_up": 50,   "halt": 500},    # records mutated
    "broadcast":      {"step_up": 10,   "halt": 100},    # external recipients
    "destruction":    {"step_up": 5,    "halt": 25},     # irreversible deletes/overwrites
    "external_calls": {"step_up": 100,  "halt": 1000},   # calls (denial-of-wallet guard)
}

# === POLICY: blast-radius SCORE weights (audit Finding 3 — POLICY, not truth) ===
# Σ (weight × class_count) -> a single composite blast score. The weights encode how
# much each class "costs" in the composite; they are a committed risk appetite, NOT a
# derived constant. Destruction & financial weigh heaviest by policy choice.
SCORE_WEIGHTS = {
    "financial":      1,    # per $ (so $1000 -> 1000 score points)
    "data_mutation":  2,    # per record
    "broadcast":      5,    # per recipient
    "destruction":    50,   # per irreversible op (heaviest: hard to undo)
    "external_calls": 1,    # per call
}

# === POLICY: composite blast-score HALT bound ===
SCORE_HALT = 2000   # Σ weighted blast > this -> HALT + human (policy choice)

# A machine-readable banner the gate attaches to EVERY verdict so no consumer can
# mistake these numbers for derived facts.
POLICY_BANNER = (
    "THRESHOLDS and SCORE WEIGHTS are COMMITTED POLICY INPUTS (human-owned risk "
    "appetite), NOT derived truth. G3 is κ=1 ONLY about 'did the committed running "
    "sum cross the committed threshold'; it is silent on whether the threshold is right."
)


def tracked_classes():
    return tuple(THRESHOLDS.keys())


def _selftest():
    # every threshold class has both a step_up and a halt, step_up < halt
    for cls, t in THRESHOLDS.items():
        assert "step_up" in t and "halt" in t, (cls, t)
        assert t["step_up"] < t["halt"], (cls, t)
    # every threshold class has a score weight (no silent un-weighted class)
    for cls in THRESHOLDS:
        assert cls in SCORE_WEIGHTS, cls
    # the banner names them as POLICY, not truth (honesty rail)
    assert "POLICY" in POLICY_BANNER and "NOT derived truth" in POLICY_BANNER
    assert SCORE_HALT > 0
    print("composeauth_policy selftest: PASS (thresholds step_up<halt for every class; "
          "every class weighted; policy banner labels thresholds+weights as POLICY not truth)")


if __name__ == "__main__":
    _selftest()
