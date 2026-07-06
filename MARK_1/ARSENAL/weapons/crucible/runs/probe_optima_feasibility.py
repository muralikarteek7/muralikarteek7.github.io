#!/usr/bin/env python3
"""CRUCIBLE probe -- TARGET: optima_feasibility (the OPTIMA-GATE feasibility/optimality
certificate).  COVERAGE: metamorphic-only + abstain-crash.

WHY metamorphic-only (no false-accept hunt): the gate's kappa=1 optimality engine is itself
an EXHAUSTIVE enumeration / exact-dual / IIS-enumeration certifier.  Any independent oracle
strong enough to adjudicate feasibility+optimality on these integer-box models would be a
SECOND brute-force enumerator -- the SAME mechanism the gate already uses internally
(`_enumerate_feasible`).  A false-accept hunt judged by the gate's own class of engine is
CIRCULAR (proves nothing), so per CRUCIBLE doctrine we DROP to metamorphic + abstain only.

The metamorphic transforms below are CLAIMED meaning-preserving on the feasibility/optimality
verdict.  NO oracle is supplied, so meaning-preservation is CALLER-ASSERTED -- reported as
residual risk, not machine-verified.

  T1  variable relabeling      -- rename every variable consistently (model + solution + cert).
  T2  constraint reordering    -- reverse the constraints list (and any best-effort label use).
  T3  objective + constant shift -- add a constant K to objective.constant AND to every claimed
                                    objective number (claim.objective, best_bound, independent
                                    value, witness objective is recomputed).  argmax/argmin and
                                    thus the OPTIMAL verdict are invariant under a constant shift.
  T4  uniform positive scaling -- multiply objective coeffs + constant by s>0 and the claimed
                                  objective by s (and dual y by s).  argmax/argmin invariant;
                                  exact-integer so no rounding.

The gate is BLACK-BOX: this probe imports and calls the REAL `certify` from the sibling
optima weapon dir; it does NOT re-implement the gate.
"""
import sys
import os
import json
import copy

HERE = os.path.dirname(os.path.abspath(__file__))
CRUCIBLE_DIR = os.path.dirname(HERE)
ARSENAL_DIR = os.path.dirname(CRUCIBLE_DIR)
OPTIMA_DIR = os.path.join(ARSENAL_DIR, "optima")

# import the REAL gate (black-box) and the FROZEN harness
sys.path.insert(0, OPTIMA_DIR)
sys.path.insert(0, CRUCIBLE_DIR)

import optima_gate                       # the REAL weapon gate
from crucible_harness import (GateAdapter, metamorphic_hunt, abstain_crash_hunt,
                              ACCEPT, REJECT, ABSTAIN, ERROR)

print("REAL gate imported from:", optima_gate.__file__)
print("entrypoint: optima_gate.certify(model, claim)")
print("=" * 78)


# --------------------------------------------------------------------------- #
#  ADAPTER -- map the REAL gate's native verdict string onto ACCEPT/REJECT/ABSTAIN.
#  The gate is BLACK-BOX: we call optima_gate.certify and read result["verdict"].
#  ACCEPT  = the gate AFFIRMS the solver's claim (certified optimal/feasible/infeasible).
#  REJECT  = the gate REFUSES the claim (infeasible solution / wrong obj / gap / no proof).
# --------------------------------------------------------------------------- #
ACCEPT_VERDICTS = {
    "OPTIMAL_CERTIFIED",
    "INFEASIBLE_PROVEN",
    "FEASIBLE_VERIFIED (feasibility problem, no objective)",
}

def to_verdict(raw):
    v = raw.get("verdict", "")
    if v in ACCEPT_VERDICTS:
        return ACCEPT
    # every REJECTED_* and FEASIBLE_WITH_GAP* is the gate REFUSING to certify the claim.
    if v.startswith("REJECTED") or v.startswith("FEASIBLE_WITH_GAP"):
        return REJECT
    # any unrecognized / new verdict string -> ABSTAIN (loud, never a silent ACCEPT)
    return ABSTAIN

def gate_fn(model, claim):
    return optima_gate.certify(model, claim)

gate = GateAdapter("OPTIMA-feasibility", gate_fn, to_verdict)


# --------------------------------------------------------------------------- #
#  SEED MODELS+CLAIMS spanning the certified verdict classes.  Each seed is the
#  kwargs dict {"model": ..., "claim": ...} that the adapter feeds to certify().
#  We cover: OPTIMAL via exhaustive, OPTIMAL via lp_dual, OPTIMAL via independent,
#  INFEASIBLE_PROVEN (IIS), and REJECTED variants -- so a transform that flips ANY
#  certified verdict to a different definite verdict is caught.
# --------------------------------------------------------------------------- #
def toy():
    return {
        "vars": {"x": [0, 10], "y": [0, 10]},
        "constraints": [{"coeffs": {"x": 1, "y": 1}, "op": "<=", "rhs": 7, "label": "cap"}],
        "objective": {"sense": "max", "coeffs": {"x": 3, "y": 2}, "constant": 0},
    }

def toy_min():
    return {
        "vars": {"a": [0, 8], "b": [0, 8]},
        "constraints": [{"coeffs": {"a": 1, "b": 1}, "op": ">=", "rhs": 5, "label": "lo"}],
        "objective": {"sense": "min", "coeffs": {"a": 2, "b": 3}, "constant": 4},
    }

def inf_model():
    return {"vars": {"z": [0, 10]},
            "constraints": [{"coeffs": {"z": 1}, "op": ">=", "rhs": 5, "label": "lo"},
                            {"coeffs": {"z": 1}, "op": "<=", "rhs": 3, "label": "hi"}]}

SEEDS = []

# S1: OPTIMAL via exhaustive  (max 3x+2y; opt 21 @ (7,0))
SEEDS.append({"model": toy(),
              "claim": {"status": "OPTIMAL", "solution": {"x": 7, "y": 0}, "objective": 21,
                        "optimality_certificate": {"type": "exhaustive"}}})

# S2: OPTIMAL via lp_dual (tight dual cap=3, lb_y=1 -> bound meets primal 21)
SEEDS.append({"model": toy(),
              "claim": {"status": "OPTIMAL", "solution": {"x": 7, "y": 0}, "objective": 21,
                        "optimality_certificate": {"type": "lp_dual", "y": {"cap": 3, "lb_y": 1}}}})

# S3: OPTIMAL via independent (different exact method's optimum + feasible witness)
SEEDS.append({"model": toy(),
              "claim": {"status": "OPTIMAL", "solution": {"x": 7, "y": 0}, "objective": 21,
                        "optimality_certificate": {"type": "independent", "value": 21,
                                                   "witness": {"x": 7, "y": 0}}}})

# S4: OPTIMAL via exhaustive on a MIN problem with a nonzero constant
#     min 2a+3b+4 s.t. a+b>=5, 0<=a,b<=8.  optimum: a+b=5 -> min 2a+3b = 2*5+3*0=10 @ (5,0); +4 = 14
SEEDS.append({"model": toy_min(),
              "claim": {"status": "OPTIMAL", "solution": {"a": 5, "b": 0}, "objective": 14,
                        "optimality_certificate": {"type": "exhaustive"}}})

# S5: INFEASIBLE_PROVEN (real IIS lo & hi)
SEEDS.append({"model": inf_model(),
              "claim": {"status": "INFEASIBLE", "iis": ["lo", "hi"]}})

# S6: a REJECTED verdict (feasible point but WRONG objective) -- must STAY rejected
SEEDS.append({"model": toy(),
              "claim": {"status": "OPTIMAL", "solution": {"x": 7, "y": 0}, "objective": 999,
                        "optimality_certificate": {"type": "exhaustive"}}})

# S7: FEASIBLE_WITH_GAP (no certificate) -- must STAY a bound under relabel/reorder/shift/scale
SEEDS.append({"model": toy(),
              "claim": {"status": "OPTIMAL", "solution": {"x": 6, "y": 1}, "objective": 20}})


# --------------------------------------------------------------------------- #
#  METAMORPHIC TRANSFORMS.  Each takes the kwargs dict {"model","claim"} and
#  returns a new one CLAIMED to carry the same feasibility/optimality verdict.
# --------------------------------------------------------------------------- #
def _all_var_names(obj):
    return list(obj["model"]["vars"].keys())


def T_relabel(obj):
    """T1: rename every variable v -> v+'__r' consistently across vars, constraints,
    objective, solution, dual cert ub_/lb_ labels, and independent witness.  A pure
    consistent renaming cannot change feasibility or optimality."""
    o = copy.deepcopy(obj)
    m, c = o["model"], o["claim"]
    rn = {v: v + "__r" for v in m["vars"]}
    m["vars"] = {rn[v]: b for v, b in m["vars"].items()}
    for con in m.get("constraints", []):
        con["coeffs"] = {rn[v]: a for v, a in con["coeffs"].items()}
    if m.get("objective"):
        m["objective"]["coeffs"] = {rn[v]: a for v, a in m["objective"]["coeffs"].items()}
    if "solution" in c:
        c["solution"] = {rn.get(v, v): val for v, val in c["solution"].items()}
    cert = c.get("optimality_certificate")
    if cert:
        if cert.get("type") == "independent" and "witness" in cert:
            cert["witness"] = {rn.get(v, v): val for v, val in cert["witness"].items()}
        if cert.get("type") == "lp_dual" and isinstance(cert.get("y"), dict):
            # the box-bound dual labels are ub_<var>/lb_<var>; rename them with the vars.
            newy = {}
            for k, val in cert["y"].items():
                nk = k
                for v in rn:
                    if k == "ub_" + v:
                        nk = "ub_" + rn[v]
                    elif k == "lb_" + v:
                        nk = "lb_" + rn[v]
                newy[nk] = val
            cert["y"] = newy
    return o


def T_reorder(obj):
    """T2: reverse the order of the constraints list.  Constraint set is order-independent
    for feasibility; the IIS uses labels (not positions) so an infeasibility proof is also
    order-invariant.  (Reversing also reverses var-dict order, exercising enumeration order.)"""
    o = copy.deepcopy(obj)
    cons = o["model"].get("constraints", [])
    o["model"]["constraints"] = list(reversed(cons))
    # also reverse the var insertion order (meaning-preserving; only iteration order changes)
    o["model"]["vars"] = dict(reversed(list(o["model"]["vars"].items())))
    return o


def T_const_shift(obj, K=1000):
    """T3: add constant K to the objective constant AND to every claimed objective number.
    A constant shift of the objective preserves argmax/argmin -> the OPTIMAL/REJECT verdict
    is invariant.  Models with no objective (pure feasibility / infeasible) are untouched."""
    o = copy.deepcopy(obj)
    m, c = o["model"], o["claim"]
    if not m.get("objective"):
        return o
    m["objective"]["constant"] = m["objective"].get("constant", 0) + K
    if "objective" in c and c["objective"] is not None:
        c["objective"] = c["objective"] + K
    cert = c.get("optimality_certificate")
    if cert:
        if cert.get("type") == "solver_bound_gap0" and cert.get("best_bound") is not None:
            cert["best_bound"] = cert["best_bound"] + K
        if cert.get("type") == "independent" and cert.get("value") is not None:
            cert["value"] = cert["value"] + K
    return o


def T_scale(obj, s=3):
    """T4: multiply objective coeffs+constant by s>0 and the claimed objective by s (and the
    dual y by s, and any independent value / best_bound by s).  Positive uniform scaling of a
    linear objective preserves argmax/argmin -> the OPTIMAL/REJECT verdict is invariant.
    Integer s keeps everything exact (the gate is integer-exact)."""
    assert s > 0
    o = copy.deepcopy(obj)
    m, c = o["model"], o["claim"]
    if not m.get("objective"):
        return o
    m["objective"]["coeffs"] = {v: a * s for v, a in m["objective"]["coeffs"].items()}
    m["objective"]["constant"] = m["objective"].get("constant", 0) * s
    if "objective" in c and c["objective"] is not None:
        c["objective"] = c["objective"] * s
    cert = c.get("optimality_certificate")
    if cert:
        if cert.get("type") == "lp_dual" and isinstance(cert.get("y"), dict):
            cert["y"] = {k: v * s for k, v in cert["y"].items()}
        if cert.get("type") == "solver_bound_gap0" and cert.get("best_bound") is not None:
            cert["best_bound"] = cert["best_bound"] * s
        if cert.get("type") == "independent" and cert.get("value") is not None:
            cert["value"] = cert["value"] * s
    return o


TRANSFORMS = [
    ("variable-relabel (consistent rename)", T_relabel),
    ("constraint+var reorder (reverse)", T_reorder),
    ("objective constant-shift (+1000)", T_const_shift),
    ("uniform positive scaling (x3)", T_scale),
]


# --------------------------------------------------------------------------- #
#  A small sanity print: the base verdict of each seed (so the report is legible).
# --------------------------------------------------------------------------- #
print("SEED base verdicts (real gate):")
for i, s in enumerate(SEEDS):
    nat = optima_gate.certify(copy.deepcopy(s["model"]), copy.deepcopy(s["claim"]))["verdict"]
    print(f"  S{i+1}: {gate.verdict(copy.deepcopy(s)):7s}  native={nat!r}")
print("=" * 78)


# --------------------------------------------------------------------------- #
#  RUN 1 -- METAMORPHIC HUNT (no oracle; meaning-preservation CALLER-ASSERTED).
#  Default mode: only a flip between two DEFINITE verdicts (ACCEPT/REJECT) is a KILL.
# --------------------------------------------------------------------------- #
mm = metamorphic_hunt(gate, [copy.deepcopy(s) for s in SEEDS], TRANSFORMS,
                      max_probes=10000, oracle=None)
print("METAMORPHIC HUNT (default: definite<->definite flip):")
print(json.dumps(mm.to_dict(), indent=2, default=str))
print("=" * 78)

# --------------------------------------------------------------------------- #
#  RUN 2 -- METAMORPHIC HUNT (strict: also flag DEFINITE->ABSTAIN/ERROR).  A
#  meaning-preserving transform that makes a certified verdict go ABSTAIN/ERROR
#  (e.g. relabel breaks a dual cert label) is ALSO instability worth catching.
# --------------------------------------------------------------------------- #
mm_strict = metamorphic_hunt(gate, [copy.deepcopy(s) for s in SEEDS], TRANSFORMS,
                             max_probes=10000, oracle=None, flag_definite_to_abstain=True)
print("METAMORPHIC HUNT (strict: also definite->abstain/error):")
print(json.dumps(mm_strict.to_dict(), indent=2, default=str))
print("=" * 78)


# --------------------------------------------------------------------------- #
#  RUN 3 -- ABSTAIN/CRASH HUNT.  Malformed / degenerate certificate inputs MUST
#  abstain loudly, reject, or raise a deliberate guard (ERROR) -- never silently
#  ACCEPT garbage.  A silent ACCEPT on a malformed input is a KILL.
# --------------------------------------------------------------------------- #
SAFE = {ABSTAIN, REJECT, ERROR}
malformed = [
    # objective claim missing entirely on an OPTIMAL claim
    ("OPTIMAL claim with no 'objective' field",
     {"model": toy(), "claim": {"status": "OPTIMAL", "solution": {"x": 7, "y": 0},
                                "optimality_certificate": {"type": "exhaustive"}}}, SAFE),
    # solution missing entirely
    ("OPTIMAL claim with no 'solution' field",
     {"model": toy(), "claim": {"status": "OPTIMAL", "objective": 21,
                                "optimality_certificate": {"type": "exhaustive"}}}, SAFE),
    # incomplete solution (missing var y) -- gate's BUG-1 path
    ("incomplete solution (missing var y)",
     {"model": toy(), "claim": {"status": "OPTIMAL", "solution": {"x": 7}, "objective": 21,
                                "optimality_certificate": {"type": "exhaustive"}}}, SAFE),
    # non-integer solution value
    ("non-integer solution value x=7.5",
     {"model": toy(), "claim": {"status": "OPTIMAL", "solution": {"x": 7.5, "y": 0},
                                "objective": 22.5,
                                "optimality_certificate": {"type": "exhaustive"}}}, SAFE),
    # unknown optimality certificate type
    ("unknown optimality_certificate type 'magic'",
     {"model": toy(), "claim": {"status": "OPTIMAL", "solution": {"x": 7, "y": 0}, "objective": 21,
                                "optimality_certificate": {"type": "magic"}}}, SAFE),
    # missing status entirely
    ("claim with no 'status' field",
     {"model": toy(), "claim": {"solution": {"x": 7, "y": 0}, "objective": 21,
                                "optimality_certificate": {"type": "exhaustive"}}}, SAFE),
    # INFEASIBLE claim with a BOGUS (satisfiable) IIS -- must NOT be accepted as proven
    ("INFEASIBLE claim with bogus satisfiable IIS ['lo']",
     {"model": inf_model(), "claim": {"status": "INFEASIBLE", "iis": ["lo"]}}, SAFE),
    # INFEASIBLE claim naming a non-existent constraint label
    ("INFEASIBLE claim with non-existent IIS label",
     {"model": inf_model(), "claim": {"status": "INFEASIBLE", "iis": ["nope"]}}, SAFE),
    # constraint with an UNKNOWN op -> gate raises ValueError (deliberate guard = ERROR, safe)
    ("constraint with unknown op '!='",
     {"model": {"vars": {"x": [0, 5]},
                "constraints": [{"coeffs": {"x": 1}, "op": "!=", "rhs": 2, "label": "q"}],
                "objective": {"sense": "max", "coeffs": {"x": 1}, "constant": 0}},
      "claim": {"status": "OPTIMAL", "solution": {"x": 5}, "objective": 5,
                "optimality_certificate": {"type": "exhaustive"}}}, SAFE),
    # empty-vars model: a WELL-POSED degenerate case, NOT garbage.  Exactly one feasible
    # point exists (the empty assignment {}); its objective equals the constant 0; the
    # claimed objective 0 matches, and the gate's exhaustive enumeration confirms
    # true_optimum == 0 == claimed.  So OPTIMAL_CERTIFIED (ACCEPT) is the SOUND verdict --
    # not a hole.  ACCEPT is therefore allowed here IN ADDITION to the abstain/reject/error
    # safe set.  (Gate behavior is correct; the prior SAFE-only expectation was the bug.)
    ("empty-vars model with OPTIMAL claim (legitimately certifiable)",
     {"model": {"vars": {}, "constraints": [], "objective": {"sense": "max", "coeffs": {}, "constant": 0}},
      "claim": {"status": "OPTIMAL", "solution": {}, "objective": 0,
                "optimality_certificate": {"type": "exhaustive"}}}, SAFE | {ACCEPT}),
]
ac = abstain_crash_hunt(gate, malformed, max_probes=1000)
print("ABSTAIN/CRASH HUNT (malformed certificate inputs):")
print(json.dumps(ac.to_dict(), indent=2, default=str))
print("=" * 78)

# explicit machine-readable summary line for the harness/orchestrator
def _kind(r):
    return "KILL" if r.to_dict().get("KILL") else "SURVIVED"
print("SUMMARY:", json.dumps({
    "metamorphic_default": _kind(mm),
    "metamorphic_strict": _kind(mm_strict),
    "abstain_crash": _kind(ac),
}))
