#!/usr/bin/env python3
"""CRUCIBLE — the BOX's first META-WEAPON: an adversarial / differential / metamorphic
tester of the box's OWN verifiers (gates).

Every other weapon TRUSTS its gate. CRUCIBLE is the only thing that tests whether that
trust is earned. It takes a weapon's FROZEN gate (black-box, via a uniform adapter) and
tries to BREAK it — to exhibit an object the gate is wrong about.

THE FOUR PROBE MODES (the KILL is always a kappa=1 exhibit; absence-of-kill is CONFIDENCE only):
  FALSE-ACCEPT  needs oracle: X with gate(X)=ACCEPT  AND oracle(X)=WRONG     (gameable gate)
  FALSE-REJECT  needs oracle: X with gate(X)=REJECT  AND oracle(X)=CORRECT   (over-strict gate)
  METAMORPHIC   no oracle:    meaning-preserving T(X) where gate(T(X)) != gate(X) (instability)
  ABSTAIN/CRASH no oracle:    malformed input where the gate silently passes/crashes (robustness)

THE HONEST FRAMING (do not skip):
  - A KILL is a machine-checked PROOF a gate has a bug (re-runnable contradiction). kappa=1.
  - NO-KILL is NOT a soundness proof. "Survived B probes" raises CONFIDENCE, never proves sound
    (Dijkstra: testing shows the presence of bugs, never their absence -- GROUNDING.md). We report
    budget + transform classes + oracle coverage + residual risk, and the word "sound"/"proven"
    is BANNED from a survived report (machine-asserted in selftest_all.py case (e)).
  - The ORACLE must be INDEPENDENT of the gate (a different engine). A false-accept hunt judged by
    the same engine is circular -> proves nothing. No oracle => metamorphic/abstain only, labeled.
  - THE ORACLE CAN BE WRONG TOO. A buggy oracle yields a SPURIOUS KILL. So every KILL is
    double-checked: (1) the oracle is confirmed SANE on a known-good control first, (2) the exhibit
    is re-run. A KILL ships only when gate-vs-oracle DISAGREE *and* the oracle passed its control.

CRUCIBLE never reads a gate's internals (black-box) so a gate bug can't hide CRUCIBLE's eyes.
This module is the FROZEN harness: the adapter, the oracle-registry plumbing, the search, the
four modes, the KILL/SURVIVED verdict objects, and a full adversarial _selftest().
"""
import sys
import json
import traceback
from dataclasses import dataclass, field, asdict
from typing import Callable, Any, Optional

# --------------------------------------------------------------------------- #
#  Verdict vocabulary — the uniform black-box language CRUCIBLE speaks.
#  Every adapted gate maps its native return onto exactly one of these.
# --------------------------------------------------------------------------- #
ACCEPT = "ACCEPT"     # the gate says the object is correct / valid / consistent
REJECT = "REJECT"     # the gate says the object is wrong / invalid / inconsistent
ABSTAIN = "ABSTAIN"   # the gate declines (undefined / too-large / powerless) -- loud
ERROR = "ERROR"       # the gate raised an exception (crash) on the input
VERDICTS = {ACCEPT, REJECT, ABSTAIN, ERROR}

# Banned words in any SURVIVED report's risk/label fields (skimmer-safety rail §6).
_BANNED_IN_SURVIVED = ("sound", "proven", "proof of soundness", "verified sound", "bug-free")


# --------------------------------------------------------------------------- #
#  The uniform GATE ADAPTER. CRUCIBLE only ever calls .verdict(obj) -> str.
#  The mapping fn turns a gate's native dict/bool into ACCEPT/REJECT/ABSTAIN.
#  We catch every exception and turn it into ERROR -- a crash is itself a probe
#  result (the ABSTAIN/CRASH mode), never an uncaught explosion of the harness.
# --------------------------------------------------------------------------- #
class GateAdapter:
    """Black-box wrapper around one weapon gate's public verdict function."""

    def __init__(self, name: str, fn: Callable[..., Any], to_verdict: Callable[[Any], str]):
        self.name = name
        self._fn = fn
        self._to_verdict = to_verdict

    def verdict(self, obj: dict) -> str:
        """obj is a kwargs dict for the underlying gate fn. Returns a VERDICT string.
        A raised exception is reported as ERROR (a crash IS a probe result)."""
        try:
            raw = self._fn(**obj)
        except Exception:                       # noqa: BLE001 -- a crash is a finding
            return ERROR
        try:
            v = self._to_verdict(raw)
        except Exception:                       # noqa: BLE001 -- mapping failure
            return ERROR
        if v not in VERDICTS:
            raise ValueError(f"adapter {self.name}: bad verdict {v!r} not in {VERDICTS}")
        return v


# --------------------------------------------------------------------------- #
#  The independent ORACLE. The TRUTH function, an engine DIFFERENT from the gate.
#  Returns CORRECT / WRONG for objects on which truth is independently decidable,
#  or None when the oracle has no opinion (out of its domain) -- never guesses.
# --------------------------------------------------------------------------- #
CORRECT = "CORRECT"
WRONG = "WRONG"
ORACLE_VERDICTS = {CORRECT, WRONG, None}


# Minimum number of EACH polarity (good + bad) control required before an oracle is
# allowed to ship a KILL. A 2-point check (one good, one bad) is the AUDIT's confirmed
# cry-wolf hole (A2): a subtly-wrong oracle that happens to agree on exactly 2 points but
# lies elsewhere passes a 2-point check and produces a SPURIOUS kill on a good gate. We
# require a CONTROL GRID -- multiple good AND multiple bad controls spanning the probed
# regime -- and REFUSE (not "True, sanity-not-established") when too few are registered.
MIN_CONTROLS_PER_POLARITY = 3


class Oracle:
    """An independent ground-truth, methodologically different from the gate.

    `truth(obj) -> CORRECT|WRONG|None`. `is_independent` records WHETHER a genuine
    foreign oracle exists for this weapon (drives full-differential vs metamorphic-only).

    CONTROLS (the spurious-kill rail). An oracle MUST register a CONTROL GRID: at least
    `MIN_CONTROLS_PER_POLARITY` known-good objects (oracle MUST return CORRECT) AND at
    least that many known-bad objects (oracle MUST return WRONG), chosen to SPAN the regime
    being probed (different decimal precisions, different items, boundary + interior). A
    2-point check is NOT enough (AUDIT A2 cry-wolf): pass `controls_good=[...]` and
    `controls_bad=[...]` (lists), or the legacy `control_good=`/`control_bad=` singletons
    (which are folded into the lists). `is_sane()` runs the WHOLE grid before any KILL and
    REFUSES if the grid is too small.
    """

    def __init__(self, name, truth, *, is_independent, method,
                 control_good=None, control_bad=None,
                 controls_good=None, controls_bad=None):
        self.name = name
        self._truth = truth
        self.is_independent = bool(is_independent)
        self.method = method
        # Fold legacy singletons into the grid lists; de-None.
        self.controls_good = list(controls_good or [])
        self.controls_bad = list(controls_bad or [])
        if control_good is not None:
            self.controls_good.append(control_good)
        if control_bad is not None:
            self.controls_bad.append(control_bad)
        # Back-compat attributes (first of each, or None) for any caller that reads them.
        self.control_good = self.controls_good[0] if self.controls_good else None
        self.control_bad = self.controls_bad[0] if self.controls_bad else None

    def truth(self, obj):
        v = self._truth(obj)
        if v not in ORACLE_VERDICTS:
            raise ValueError(f"oracle {self.name}: bad truth {v!r}")
        return v

    def is_sane(self, *, min_controls=MIN_CONTROLS_PER_POLARITY):
        """Confirm the oracle is sane on its CONTROL GRID (not just 2 points).

        Returns (ok: bool, detail). REFUSES (ok=False) when too FEW controls are registered
        -- "no controls established" is treated as INSUFFICIENT, not as a free pass (AUDIT A2:
        a too-small control set lets a subtly-wrong oracle ship a spurious kill). A KILL may
        ship only when the oracle returns CORRECT on EVERY known-good control and WRONG on
        EVERY known-bad control, AND there are >= min_controls of each polarity."""
        ng, nb = len(self.controls_good), len(self.controls_bad)
        if ng < min_controls or nb < min_controls:
            return (False,
                    f"oracle control grid TOO SMALL ({ng} good, {nb} bad; need >= {min_controls} "
                    "each spanning the probed regime) -- a 2-point check is the AUDIT-confirmed "
                    "cry-wolf hole; REFUSING to certify sanity (no KILL may ship).")
        for c in self.controls_good:
            if self.truth(c) != CORRECT:
                return False, f"oracle FAILED a known-good control {c!r} (calls a correct object WRONG)"
        for c in self.controls_bad:
            if self.truth(c) != WRONG:
                return False, f"oracle FAILED a known-bad control {c!r} (calls a wrong object CORRECT)"
        return (True, f"oracle SANE on a {ng}-good/{nb}-bad control grid "
                      "(every good->CORRECT, every bad->WRONG)")


# --------------------------------------------------------------------------- #
#  Exhibits & reports — the two possible outputs of a probe campaign.
# --------------------------------------------------------------------------- #
@dataclass
class Kill:
    """A kappa=1 bug exhibit: a re-runnable contradiction between gate and truth."""
    weapon: str
    mode: str                 # FALSE-ACCEPT | FALSE-REJECT | METAMORPHIC | ABSTAIN-CRASH
    obj: Any
    gate_verdict: str
    oracle_verdict: Optional[str] = None
    transform: Optional[str] = None      # for metamorphic: the meaning-preserving T
    obj2: Any = None                      # for metamorphic: T(obj)
    gate_verdict2: Optional[str] = None
    oracle_controls_passed: Optional[bool] = None
    kappa: int = 1
    note: str = ""

    def to_dict(self):
        d = asdict(self)
        d["KILL"] = True
        return d


@dataclass
class Survived:
    """A no-kill report. Raises CONFIDENCE, NEVER proves soundness (Dijkstra)."""
    weapon: str
    probes_run: int
    transform_classes: list = field(default_factory=list)
    oracle_coverage: str = "none"        # full | partial | none
    residual_risk: str = ""
    note: str = ""

    def to_dict(self):
        d = asdict(self)
        d["KILL"] = False
        d["label"] = "SURVIVED to budget"   # NEVER "sound"
        # Self-policing: the survived report must not contain banned soundness words.
        blob = json.dumps(d).lower()
        for w in _BANNED_IN_SURVIVED:
            if w in blob:
                raise AssertionError(
                    f"SURVIVED report for {self.weapon} contains banned word {w!r} "
                    "-- a non-kill is CONFIDENCE, never a soundness proof (Dijkstra rail).")
        return d


# --------------------------------------------------------------------------- #
#  THE SEARCH — adversarial generation toward a gate-vs-oracle disagreement.
#  No `hypothesis` available -> a deterministic LCG mutator (reproducible, seeded),
#  exactly the psymetrix/SPRITE fallback the kickoff sanctions. The LLM-proposer is
#  0%-trusted: candidates only suggest WHERE to look; every one is machine-checked.
# --------------------------------------------------------------------------- #
class LCG:
    """Deterministic linear-congruential generator (Numerical Recipes constants).
    Reproducible mutation source -- a fixed seed => a fixed probe sequence."""
    def __init__(self, seed=12345):
        self.s = seed & 0xFFFFFFFF

    def next(self):
        self.s = (1664525 * self.s + 1013904223) & 0xFFFFFFFF
        return self.s

    def randint(self, lo, hi):
        return lo + self.next() % (hi - lo + 1)

    def choice(self, seq):
        return seq[self.next() % len(seq)]


def _refuse_trivially_circular(gate: GateAdapter, oracle: Oracle):
    """AUDIT A1 (partial guard): the harness CANNOT prove a `truth()` is methodologically
    independent of the gate (that is an OPERATOR INVARIANT, see SPEC.md §3 / README) -- a
    caller can register Oracle(is_independent=True) wrapping the gate's own logic and the
    harness has no way to introspect 'this Python closure is secretly the gate'. We DO catch
    the one mechanically-detectable trivially-circular case: the oracle's underlying truth
    callable IS LITERALLY the gate's underlying verdict callable (same object identity, or the
    oracle closes over the exact gate function). This is a best-effort tripwire, NOT a proof
    of independence -- methodological independence remains a trust-the-caller invariant the
    operator must uphold (documented as such, not over-claimed as enforced)."""
    g = getattr(gate, "_fn", None)
    o = getattr(oracle, "_truth", None)
    if g is not None and o is not None and g is o:
        raise ValueError(
            f"oracle {oracle.name} is TRIVIALLY CIRCULAR: its truth() callable IS the gate's "
            f"own verdict callable ({getattr(g, '__name__', g)!r}). A false-accept hunt judged "
            "by the gate's own engine proves nothing. Register a methodologically-foreign oracle. "
            "(NOTE: this tripwire only catches literal same-callable circularity; deeper "
            "methodological circularity is an OPERATOR INVARIANT the harness cannot enforce.)")


def false_accept_hunt(gate: GateAdapter, oracle: Oracle, candidates, *, max_probes=10000,
                      coverage_note=None):
    """FALSE-ACCEPT: find X with gate=ACCEPT but oracle=WRONG (a gameable gate).
    Requires an INDEPENDENT oracle. Every KILL is double-checked: oracle controls
    pass first, the exhibit is re-run. `candidates` is an iterable of obj kwargs-dicts.
    `coverage_note` (AUDIT A3/A9) names the candidate-stream regime so a SURVIVED report
    never reads as broader than the inputs actually probed. Returns Kill | Survived."""
    if not oracle.is_independent:
        raise ValueError(f"{oracle.name}: NOT independent -- false-accept hunt is circular "
                         "for this weapon. Use metamorphic/abstain modes instead.")
    _refuse_trivially_circular(gate, oracle)
    sane, detail = oracle.is_sane()
    if not sane:
        raise AssertionError(f"oracle {oracle.name} failed its sanity control: {detail}. "
                             "Refusing to ship a KILL from a buggy oracle (spurious-kill rail).")
    n = 0
    for obj in candidates:
        if n >= max_probes:
            break
        n += 1
        gv = gate.verdict(obj)
        if gv != ACCEPT:
            continue
        ov = oracle.truth(obj)
        if ov == WRONG:
            # double-check: re-run both, controls already passed above.
            if gate.verdict(obj) == ACCEPT and oracle.truth(obj) == WRONG:
                return Kill(weapon=gate.name, mode="FALSE-ACCEPT", obj=obj,
                            gate_verdict=gv, oracle_verdict=ov,
                            oracle_controls_passed=True,
                            note="gate ACCEPTs an object the independent oracle proves WRONG "
                                 "(re-runnable contradiction; oracle sane on controls).")
    risk = (f"no false-accept found in {n} probes; absence of a counterexample is EVIDENCE, "
            "not proof, the gate rejects all wrong objects (Dijkstra: testing shows presence, "
            "not absence).")
    if coverage_note:
        risk += f" CANDIDATE-STREAM REGIME PROBED: {coverage_note} (a bug active only OUTSIDE " \
                "this regime would not be caught here)."
    return Survived(weapon=gate.name, probes_run=n,
                    transform_classes=["structured-mutation:false-accept"],
                    oracle_coverage="full",
                    residual_risk=risk)


def false_reject_hunt(gate: GateAdapter, oracle: Oracle, candidates, *, max_probes=10000,
                      coverage_note=None):
    """FALSE-REJECT: find X with gate=REJECT but oracle=CORRECT (an over-strict gate)."""
    if not oracle.is_independent:
        raise ValueError(f"{oracle.name}: NOT independent -- false-reject hunt is circular.")
    _refuse_trivially_circular(gate, oracle)
    sane, detail = oracle.is_sane()
    if not sane:
        raise AssertionError(f"oracle {oracle.name} failed sanity: {detail}.")
    n = 0
    for obj in candidates:
        if n >= max_probes:
            break
        n += 1
        gv = gate.verdict(obj)
        if gv != REJECT:
            continue
        ov = oracle.truth(obj)
        if ov == CORRECT:
            if gate.verdict(obj) == REJECT and oracle.truth(obj) == CORRECT:
                return Kill(weapon=gate.name, mode="FALSE-REJECT", obj=obj,
                            gate_verdict=gv, oracle_verdict=ov,
                            oracle_controls_passed=True,
                            note="gate REJECTs an object the independent oracle proves CORRECT.")
    risk = f"no false-reject found in {n} probes; evidence, not proof."
    if coverage_note:
        risk += f" CANDIDATE-STREAM REGIME PROBED: {coverage_note}."
    return Survived(weapon=gate.name, probes_run=n,
                    transform_classes=["structured-mutation:false-reject"],
                    oracle_coverage="full",
                    residual_risk=risk)


def _transform_meaning_preserving_on(oracle, obj, tobj):
    """AUDIT A11 guard: confirm a registered transform actually PRESERVES MEANING on this
    pair, using the INDEPENDENT oracle as the arbiter. A transform is meaning-preserving iff
    the oracle assigns the SAME ground-truth to obj and T(obj). Returns:
      True  -> oracle agrees (truth(obj)==truth(tobj), both defined) -> transform is sound here
      False -> oracle DISAGREES (truth(obj)!=truth(tobj)) -> the TRANSFORM changed the object,
               NOT the gate -- a metamorphic flip here is a SPURIOUS kill, suppress it.
      None  -> oracle has no opinion on one/both -> cannot certify; caller decides.
    A fake 'add 1/n to the mean' transform (AUDIT A11) makes the oracle DISAGREE, so this
    returns False and the spurious metamorphic KILL is blocked."""
    if oracle is None:
        return None
    try:
        to, tt = oracle.truth(obj), oracle.truth(tobj)
    except Exception:
        return None
    if to is None or tt is None:
        return None
    return to == tt


def metamorphic_hunt(gate: GateAdapter, seeds, transforms, *, max_probes=10000,
                     oracle=None, require_oracle_meaning_check=False,
                     flag_definite_to_abstain=False):
    """METAMORPHIC: a meaning-preserving transform T must NOT change the verdict.
    `seeds` = base objs (kwargs dicts); `transforms` = list of (name, T) where T(obj)->obj'
    is CLAIMED to preserve the gate's intended verdict. A KILL = gate(obj) != gate(T(obj)).

    AUDIT A11 FIX -- the transform itself must be validated, or a fake non-meaning-preserving
    transform (e.g. 'add 1/n to the mean') manufactures a SPURIOUS metamorphic KILL on a
    GOOD gate. Two guards:
      * If an INDEPENDENT `oracle` is supplied, every candidate flip is cross-checked: the
        KILL ships ONLY if the oracle assigns the SAME truth to obj and T(obj) (the transform
        really IS meaning-preserving on this pair). If the oracle DISAGREES, the transform --
        not the gate -- changed the object: the flip is suppressed (no spurious kill).
      * If `require_oracle_meaning_check=True` and NO oracle (or the oracle has no opinion on
        the pair) is available, the hunt REFUSES to certify the transform and skips the pair
        rather than shipping an unvalidated metamorphic KILL (fail-closed).

    NOTE: an (ABSTAIN/ABSTAIN) or (ERROR/ERROR) pair is invariant (not a flip). By default we
    only flag a flip between two DEFINITE verdicts (both base AND transformed in {ACCEPT,
    REJECT}) to avoid false alarms.

    AUDIT A10 (documented design gap, now OPTIONAL): a gate that goes DEFINITE -> ABSTAIN under
    a genuinely meaning-preserving transform IS unstable, but the default suppresses that as a
    'safe' abstain. Pass `flag_definite_to_abstain=True` to ALSO treat a DEFINITE->ABSTAIN
    (or DEFINITE->ERROR) flip as a KILL -- still gated by the A11 transform-validation check so
    it cannot fire on a non-meaning-preserving transform. Default stays False (conservative)."""
    n = 0
    definite_safe = (ACCEPT, REJECT)
    kill_set = definite_safe if not flag_definite_to_abstain else (ACCEPT, REJECT, ABSTAIN, ERROR)
    for obj in seeds:
        base = gate.verdict(obj)
        if base not in (ACCEPT, REJECT):
            continue
        for tname, T in transforms:
            if n >= max_probes:
                break
            n += 1
            try:
                tobj = T(obj)
            except Exception:                   # a transform that can't apply -> skip
                continue
            tv = gate.verdict(tobj)
            if tv in kill_set and tv != base:
                # AUDIT A11: validate the transform is meaning-preserving on this pair.
                mp = _transform_meaning_preserving_on(oracle, obj, tobj)
                if mp is False:
                    # the transform CHANGED the object's truth -> not meaning-preserving.
                    # This is a broken TRANSFORM, not a gate bug. Suppress (no spurious kill).
                    continue
                if mp is None and require_oracle_meaning_check:
                    # cannot certify the transform without an oracle opinion -> fail-closed.
                    continue
                # re-run to confirm reproducible
                if gate.verdict(obj) == base and gate.verdict(tobj) == tv:
                    note = (f"meaning-preserving transform {tname!r} FLIPS the verdict "
                            f"({base}->{tv}); a sound gate must be invariant under it.")
                    if mp is True:
                        note += " (transform confirmed meaning-preserving by the independent oracle.)"
                    elif oracle is None:
                        note += (" (NO oracle supplied: transform meaning-preservation is "
                                 "CALLER-ASSERTED, not machine-verified -- residual risk.)")
                    return Kill(weapon=gate.name, mode="METAMORPHIC", obj=obj,
                                gate_verdict=base, transform=tname, obj2=tobj,
                                gate_verdict2=tv, oracle_verdict=None, note=note)
    risk = (f"verdict stable under {len(transforms)} transform classes across {n} probes; "
            "evidence of invariance, not a proof.")
    if oracle is None:
        risk += (" NO oracle supplied -> transform meaning-preservation was CALLER-ASSERTED "
                 "(a fake non-meaning-preserving transform could not be machine-rejected here).")
    return Survived(weapon=gate.name, probes_run=n,
                    transform_classes=[t[0] for t in transforms],
                    oracle_coverage=("oracle-validated transforms" if oracle is not None
                                     else "none (metamorphic; transforms caller-asserted)"),
                    residual_risk=risk)


def abstain_crash_hunt(gate: GateAdapter, malformed_inputs, *, max_probes=10000):
    """ABSTAIN/CRASH: a malformed/degenerate input must ABSTAIN loudly or ERROR-with-a-guard,
    never silently ACCEPT. A KILL = a malformed input the gate silently ACCEPTs (or returns a
    confident verdict it has no basis for). We treat ABSTAIN and a guarded ERROR (the gate
    raised a *deliberate* guard) as the SAFE outcomes; a silent ACCEPT on garbage is the bug.
    Each malformed_inputs item is (description, obj, expected_safe) where expected_safe is the
    set of acceptable verdicts (e.g. {ABSTAIN, REJECT, ERROR})."""
    n = 0
    for desc, obj, expected_safe in malformed_inputs:
        if n >= max_probes:
            break
        n += 1
        v = gate.verdict(obj)
        if v not in expected_safe:
            if gate.verdict(obj) == v:          # reproducible
                return Kill(weapon=gate.name, mode="ABSTAIN-CRASH", obj=obj,
                            gate_verdict=v, oracle_verdict=None,
                            note=f"malformed/degenerate input ({desc}) yields {v}, "
                                 f"expected one of {sorted(expected_safe)} -- a silent/unsafe "
                                 "verdict on garbage instead of a loud abstain.")
    return Survived(weapon=gate.name, probes_run=n,
                    transform_classes=["malformed-input-robustness"],
                    oracle_coverage="none (robustness needs no oracle)",
                    residual_risk=f"{n} malformed inputs all abstained/rejected/guarded safely; "
                                  "evidence of robustness, not a proof.")


# =========================================================================== #
#  GATE-OF-THE-GATE — CRUCIBLE's own non-waivable self-tests (§3 of kickoff).
#  These use PLANTED bugs in COPIES of real-gate logic (re-implemented inline so
#  the self-test is hermetic and frozen). Each planted hole is SUBTLE -- of a class
#  that actually appears in the arsenal's history -- never a max-signal deletion.
# =========================================================================== #

# -- A faithful, independent re-implementation of GRIM (the oracle / known-good gate).
#    Exact Fraction arithmetic, authored from scratch -- methodologically the GRIM
#    truth, used both as the oracle AND as the "known-good gate" control.
from fractions import Fraction
import math as _math


def _grim_truth(mean_str, n, items=1):
    """Independent exact GRIM: is the reported mean achievable as k/(n*items) within
    half-ULP rounding? Returns True/False. (This is the ORACLE -- a from-scratch
    re-impl, NOT a call into psymetrix.)"""
    s = str(mean_str)
    D = len(s.split(".")[1]) if "." in s else 0
    x = Fraction(s)
    Neff = int(n) * int(items)
    tol = Fraction(1, 2 * 10 ** D)
    k_lo = _math.ceil((x - tol) * Neff)
    k_hi = _math.floor((x + tol) * Neff)
    return k_lo <= k_hi


def _grim_gate_good(mean_str, n, items=1):
    """KNOWN-GOOD GRIM gate (the control). Mirrors the REAL psymetrix gate: it GUARDS
    malformed input (n<=0 / items<=0 -> abstain with consistent=None; non-int n -> a
    deliberate ValueError guard, which the adapter maps to ERROR=safe). On well-formed
    input its arithmetic equals the oracle truth -> it must SURVIVE every hunt."""
    ni, it = int(n), int(items)                # non-int n -> ValueError (a loud guard)
    if ni <= 0 or it <= 0:
        return {"consistent": None}            # ABSTAIN on degenerate N (the real gate's R1 guard)
    return {"consistent": _grim_truth(mean_str, ni, it)}


def _grim_gate_OFFBYONE(mean_str, n, items=1):
    """PLANTED SUBTLE BUG (class: off-by-one in a boundary check, like the FACTHARNESS
    7-in-7.5 boundary). The tolerance band uses a STRICTLY-less comparison that drops
    the upper boundary integer, so SOME genuinely-inconsistent means get ACCEPTED (a
    false-accept) -- NO, wait: this widens? We make it a FALSE-ACCEPT by using a tol of
    1/10^D (a full ULP) instead of the correct 1/(2*10^D) (half-ULP). The band is twice
    too wide -> it ACCEPTs means that are actually GRIM-INCONSISTENT. Subtle: passes all
    the obvious cases; only certain boundary means leak."""
    s = str(mean_str)
    D = len(s.split(".")[1]) if "." in s else 0
    x = Fraction(s)
    Neff = int(n) * int(items)
    tol = Fraction(1, 10 ** D)                 # BUG: should be 1/(2*10**D)
    k_lo = _math.ceil((x - tol) * Neff)
    k_hi = _math.floor((x + tol) * Neff)
    return {"consistent": k_lo <= k_hi}


def _grim_gate_METAMORPHIC_BUG(mean_str, n, items=1):
    """PLANTED METAMORPHIC INSTABILITY. GRIM consistency is INVARIANT under splitting one
    scale item into `items` (mean fixed, Neff = n*items): mean '3.0', n=20, items=1 and
    mean '3.0', n=10, items=2 have the SAME Neff=20 and MUST give the same verdict. This
    buggy copy ignores `items` entirely (treats Neff=n), so the items-split transform
    flips the verdict on means where n alone is too coarse but n*items is fine."""
    s = str(mean_str)
    D = len(s.split(".")[1]) if "." in s else 0
    x = Fraction(s)
    Neff = int(n)                              # BUG: ignores items
    tol = Fraction(1, 2 * 10 ** D)
    k_lo = _math.ceil((x - tol) * Neff)
    k_hi = _math.floor((x + tol) * Neff)
    return {"consistent": k_lo <= k_hi}


def _grim_gate_SILENT_PASS(mean_str, n, items=1):
    """PLANTED ABSTAIN/CRASH BUG (class: silent-pass on a malformed input type). On a
    nonsensical n<=0 it should ABSTAIN; this copy silently returns consistent=True."""
    try:
        ni = int(n)
    except Exception:
        return {"consistent": True}            # BUG: silent pass on garbage n
    if ni <= 0:
        return {"consistent": True}            # BUG: should abstain on n<=0
    return {"consistent": _grim_truth(mean_str, ni, items)}


def _grim_to_verdict(raw):
    c = raw.get("consistent")
    if c is None:
        return ABSTAIN
    return ACCEPT if c else REJECT


def _grim_control_grid():
    """A CONTROL GRID spanning the probed regime (AUDIT A2 fix): multiple known-good and
    known-bad GRIM objects across DIFFERENT decimal precisions (0/1/2/3 dp) AND different
    `items`, so a subtly-wrong oracle that lies on any one regime (e.g. 'all 3dp means
    WRONG') is caught by a control in that regime instead of passing a 2-point check."""
    good = [
        {"mean_str": "3.0", "n": 20, "items": 1},      # 1dp, exact 60/20
        {"mean_str": "3", "n": 20, "items": 1},        # 0dp
        {"mean_str": "2.50", "n": 20, "items": 1},     # 2dp, 50/20
        {"mean_str": "3.000", "n": 20, "items": 1},    # 3dp, still 60/20
        {"mean_str": "2.5", "n": 10, "items": 2},      # items=2, Neff=20
        {"mean_str": "0.250", "n": 4, "items": 1},     # 3dp, 1/4
    ]
    bad = [
        {"mean_str": "5.19", "n": 28, "items": 1},     # 2dp, not k/28
        {"mean_str": "0.2", "n": 7, "items": 1},       # 1dp, not k/7 (band 1/20 misses every k/7)
        {"mean_str": "3.001", "n": 20, "items": 1},    # 3dp, not k/20
        {"mean_str": "2.51", "n": 20, "items": 1},     # 2dp, not k/20 (50.2/20)
        {"mean_str": "0.001", "n": 4, "items": 1},     # 3dp, not k/4
        {"mean_str": "2.51", "n": 10, "items": 2},     # items=2, Neff=20, not k/20
    ]
    return good, bad


def _grim_oracle():
    """The from-scratch GRIM oracle with a multi-point sanity control GRID (A2 fix)."""
    def truth(obj):
        try:
            return CORRECT if _grim_truth(**obj) else WRONG
        except Exception:
            return None
    good, bad = _grim_control_grid()
    return Oracle("GRIM-arith", truth, is_independent=True,
                  method="from-scratch exact Fraction GRIM (foreign to psymetrix gate)",
                  controls_good=good, controls_bad=bad)


def _grim_candidates():
    """Boundary-rich GRIM objects across MULTIPLE decimal precisions AND items (AUDIT A3/A9
    fix). The original stream only emitted 2dp means with items=1, so a bug active only on
    0dp/1dp/3dp means or on items>=2 SURVIVED silently. This stream now spans:
      * decimal precision D in {0,1,2,3} (covers the 1dp/3dp blindspots)
      * items in {1,2,3} (covers the items>=2 blindspot; Neff = n*items)
      * small discriminating n + both achievable and deliberately-off means.
    Deterministic, ordered by likelihood-to-break. See `_grim_candidate_coverage()` for the
    coverage descriptor that the SURVIVED report carries so the regime is never silently
    narrow."""
    out = []
    seen = set()

    def emit(mean_str, n, items):
        key = (mean_str, n, items)
        if key not in seen:
            seen.add(key)
            out.append({"mean_str": mean_str, "n": n, "items": items})

    for items in (1, 2, 3):
        for n in range(3, 40):
            for k in range(0, n * 5 + 1):
                m = k / n                       # an ACHIEVABLE mean (at full precision)
                off = (k + 0.5) / n             # a deliberately-OFF mean (likely inconsistent)
                for D in (0, 1, 2, 3):
                    emit(f"{m:.{D}f}", n, items)
                    emit(f"{off:.{D}f}", n, items)
    return out


def _grim_candidate_coverage():
    """Honest descriptor of what regime `_grim_candidates()` actually probes -- carried into
    the SURVIVED residual-risk so a 'no kill' is never read as broader than it is (AUDIT A3/A9:
    a SURVIVED must name its candidate-stream regime, not imply it covered everything)."""
    return ("decimal precision D in {0,1,2,3}; items in {1,2,3}; n in [3,40); achievable + "
            "deliberately-off means. NOT probed: D>=4, items>=4, n>=40, non-decimal means.")


def _items_split_transforms():
    """Meaning-preserving transform: move a factor f from n into items (Neff invariant)."""
    def split(obj):
        n, it = int(obj["n"]), int(obj.get("items", 1))
        if n % 2 == 0:
            return {"mean_str": obj["mean_str"], "n": n // 2, "items": it * 2}
        raise ValueError("n not even -- transform inapplicable")
    return [("items-split (Neff-invariant)", split)]


def _malformed_grim_inputs():
    safe = {ABSTAIN, REJECT, ERROR}
    return [
        ("n=0 (undefined)",        {"mean_str": "3.0", "n": 0, "items": 1}, safe),
        ("n=-5 (negative)",        {"mean_str": "3.0", "n": -5, "items": 1}, safe),
        ("n='garbage'",            {"mean_str": "3.0", "n": "garbage", "items": 1}, safe),
        ("items=0",                {"mean_str": "3.0", "n": 10, "items": 0}, safe),
    ]


def _selftest():
    """The gate-of-the-gate. The five non-waivable cases from kickoff §3.
    Exits via AssertionError on any failure (selftest_all.py converts to exit 1)."""
    oracle = _grim_oracle()

    # Pre-flight: the oracle itself must be SANE on its controls (else any KILL is spurious).
    sane, detail = oracle.is_sane()
    assert sane, f"oracle is NOT sane on controls: {detail}"

    cands = _grim_candidates()

    # ---- (d) NO FALSE ALARM on a KNOWN-GOOD gate (run this FIRST -- a crying-wolf
    #          meta-verifier is worse than useless). The good gate == the oracle logic,
    #          so false-accept + false-reject must BOTH SURVIVE.
    good = GateAdapter("GRIM-good", _grim_gate_good, _grim_to_verdict)
    fa = false_accept_hunt(good, oracle, cands, max_probes=20000)
    assert isinstance(fa, Survived), f"FALSE ALARM: known-good gate flagged a false-accept: {fa}"
    fr = false_reject_hunt(good, oracle, cands, max_probes=20000)
    assert isinstance(fr, Survived), f"FALSE ALARM: known-good gate flagged a false-reject: {fr}"
    mm_good = metamorphic_hunt(good, [c for c in cands if int(c["n"]) % 2 == 0][:2000],
                               _items_split_transforms(), max_probes=20000, oracle=oracle)
    assert isinstance(mm_good, Survived), f"FALSE ALARM: known-good gate metamorphic-flagged: {mm_good}"
    print("  (d) no-false-alarm on KNOWN-GOOD gate: PASS (false-accept/reject/metamorphic all SURVIVED)")

    # ---- (a)+(b) CATCH a SUBTLE planted FALSE-ACCEPT (off-by-one / too-wide tolerance).
    #      HONESTY (AUDIT A8): this is a LOCATION-blind plant -- the SEARCH has no knowledge
    #      of where the hole is and must EXHIBIT a counterexample by machine. It is NOT an
    #      author-blind / different-agent plant: this fixture is builder-authored (Opus 4.8),
    #      which is WEAKER than the kickoff §3a 'different agent plants and does not reveal'
    #      requirement. The strongest test (a third-party plant the builder never saw) must be
    #      supplied by the cross-model auditor; AUDIT.md tracks this as an open honesty gap.
    buggy_fa = GateAdapter("GRIM-offbyone", _grim_gate_OFFBYONE, _grim_to_verdict)
    kill_fa = false_accept_hunt(buggy_fa, oracle, cands, max_probes=20000)
    assert isinstance(kill_fa, Kill), "FAILED to catch the planted SUBTLE false-accept (off-by-one tol)"
    assert kill_fa.gate_verdict == ACCEPT and kill_fa.oracle_verdict == WRONG
    assert kill_fa.oracle_controls_passed is True
    # double-check the exhibit ourselves: re-run gate and oracle on the exhibited object
    assert buggy_fa.verdict(kill_fa.obj) == ACCEPT
    assert oracle.truth(kill_fa.obj) == WRONG
    print(f"  (a)/(b) CATCH SUBTLE planted false-accept: PASS (exhibit {kill_fa.obj}, "
          f"gate=ACCEPT oracle=WRONG)")

    # ---- (c) CATCH a planted METAMORPHIC instability (verdict flips under items-split).
    buggy_mm = GateAdapter("GRIM-metamorphic", _grim_gate_METAMORPHIC_BUG, _grim_to_verdict)
    even = [c for c in cands if int(c["n"]) % 2 == 0]
    # pass the oracle: the items-split transform is GENUINELY meaning-preserving (oracle agrees),
    # so the A11 transform-validation guard does NOT suppress this REAL kill.
    kill_mm = metamorphic_hunt(buggy_mm, even, _items_split_transforms(), max_probes=40000,
                               oracle=oracle)
    assert isinstance(kill_mm, Kill), "FAILED to catch the planted metamorphic instability"
    assert kill_mm.gate_verdict != kill_mm.gate_verdict2
    # double-check the flip ourselves
    assert buggy_mm.verdict(kill_mm.obj) != buggy_mm.verdict(kill_mm.obj2)
    print(f"  (c) CATCH planted metamorphic instability: PASS (transform={kill_mm.transform!r}, "
          f"{kill_mm.gate_verdict}->{kill_mm.gate_verdict2})")

    # ---- ABSTAIN/CRASH: CATCH a planted silent-pass on malformed input.
    buggy_sp = GateAdapter("GRIM-silentpass", _grim_gate_SILENT_PASS, _grim_to_verdict)
    kill_sp = abstain_crash_hunt(buggy_sp, _malformed_grim_inputs(), max_probes=100)
    assert isinstance(kill_sp, Kill), "FAILED to catch the planted silent-pass on malformed input"
    assert kill_sp.gate_verdict == ACCEPT
    print(f"  (+) CATCH planted silent-pass on malformed input: PASS (exhibit {kill_sp.obj} -> ACCEPT)")
    # and the GOOD gate must NOT trip the abstain/crash hunt on the same malformed inputs
    # (the good gate's adapter turns the n<=0 TypeError-guard into ERROR, which is SAFE):
    sp_good = abstain_crash_hunt(good, _malformed_grim_inputs(), max_probes=100)
    assert isinstance(sp_good, Survived), f"FALSE ALARM: good gate tripped abstain/crash: {sp_good}"

    # ---- ORACLE-CAN-BE-WRONG rail: a BUGGY oracle must REFUSE to ship a kill (raises).
    #      Use the FULL control grid so this exercises the grid-failure path (a calls-
    #      everything-WRONG oracle fails every GOOD control), not just the too-few path.
    good_ctl, bad_ctl = _grim_control_grid()
    def _bad_truth(obj):
        return WRONG                            # a broken oracle that calls everything WRONG
    bad_oracle = Oracle("BAD-oracle", _bad_truth, is_independent=True, method="deliberately broken",
                        controls_good=good_ctl, controls_bad=bad_ctl)
    raised = False
    try:
        false_accept_hunt(good, bad_oracle, cands[:10], max_probes=10)
    except AssertionError:
        raised = True
    assert raised, "BUGGY oracle did NOT refuse to ship a kill -- spurious-kill rail broken"
    print("  (+) spurious-kill rail: PASS (a buggy oracle that fails its control is REFUSED)")

    # ---- (e) LABEL "no counterexample" as CONFIDENCE, never PROOF. The Survived report
    #          must serialize WITHOUT any banned soundness word, and carry a residual-risk.
    d = fa.to_dict()                            # to_dict() raises if a banned word leaks
    assert d["KILL"] is False and d["label"] == "SURVIVED to budget"
    assert d["residual_risk"] and "evidence" in d["residual_risk"].lower()
    blob = json.dumps(d).lower()
    for w in _BANNED_IN_SURVIVED:
        assert w not in blob, f"SURVIVED report leaked banned word {w!r}"
    # and a non-independent oracle must be REFUSED for a false-accept hunt (circularity rail)
    dep_oracle = Oracle("dep", lambda o: None, is_independent=False, method="same engine")
    refused = False
    try:
        false_accept_hunt(good, dep_oracle, cands[:5], max_probes=5)
    except ValueError:
        refused = True
    assert refused, "non-independent oracle was NOT refused -- circularity rail broken"
    print("  (e) confidence-not-proof labeling + circularity rail: PASS "
          "(no 'sound'/'proven' in SURVIVED; non-independent oracle refused)")

    _selftest_audit_regressions(oracle, good, cands)

    print("crucible_harness selftest: PASS (5/5 gate-of-the-gate cases + spurious-kill + "
          "circularity rails + 6 AUDIT regressions A1/A2/A3/A9/A10/A11)")


def _selftest_audit_regressions(oracle, good, cands):
    """REGRESSION tests reproducing the cross-model auditor's confirmed exploits, each
    asserting the exploit is now BLOCKED. Each test FAILED before the fix and PASSES after.
    Permanent -- a regression here means a real-defect fix was reverted."""

    # ===== AUDIT A2 (cry-wolf / SPURIOUS KILL via subtly-wrong oracle) =====
    # The auditor registered an oracle correct on the OLD 2 controls but lying on a regime
    # (here: 'all 3-decimal-place means WRONG') and produced a SPURIOUS KILL on the GOOD gate.
    # FIX 1: a too-small control set (the old 2-point check) is now REFUSED outright.
    g2, b2 = _grim_control_grid()
    def _subtly_wrong_3dp(obj):
        s = str(obj["mean_str"])
        D = len(s.split(".")[1]) if "." in s else 0
        if D >= 3:
            return WRONG                          # the lie
        return CORRECT if _grim_truth(**obj) else WRONG
    # (A2a) old 2-point form -> REFUSED for too-few controls (no spurious kill can ship).
    cry2pt = Oracle("cry-wolf-2pt", _subtly_wrong_3dp, is_independent=True, method="lies on 3dp",
                    control_good={"mean_str": "3.0", "n": 20, "items": 1},
                    control_bad={"mean_str": "5.19", "n": 28, "items": 1})
    refused = False
    try:
        false_accept_hunt(good, cry2pt, [{"mean_str": "3.000", "n": 20, "items": 1}], max_probes=5)
    except AssertionError:
        refused = True
    assert refused, "A2a REGRESSION: a 2-point oracle was NOT refused (cry-wolf hole reopened)"
    # (A2b) full-grid form -> the grid SPANS 3dp, so the subtly-wrong oracle FAILS a 3dp good
    #       control and is REFUSED instead of shipping a spurious kill on the good gate.
    crygrid = Oracle("cry-wolf-grid", _subtly_wrong_3dp, is_independent=True, method="lies on 3dp",
                     controls_good=g2, controls_bad=b2)
    sane, _ = crygrid.is_sane()
    assert sane is False, "A2b REGRESSION: subtly-wrong (3dp-lying) oracle passed the control grid"
    refused = False
    try:
        false_accept_hunt(good, crygrid, [{"mean_str": "3.000", "n": 20, "items": 1}], max_probes=5)
    except AssertionError:
        refused = True
    assert refused, "A2b REGRESSION: cry-wolf oracle produced a SPURIOUS KILL on the good gate"
    print("  (A2) cry-wolf rail: PASS (subtly-wrong oracle REFUSED by control grid + min-controls; "
          "no spurious kill on the good gate)")

    # ===== AUDIT A11 (SPURIOUS METAMORPHIC KILL via a fake, non-meaning-preserving transform) =====
    # The auditor registered a transform that adds 1/n to the mean (CHANGES the object) and
    # produced a spurious metamorphic KILL on the GOOD gate. FIX: the oracle arbitrates whether
    # the transform preserved meaning; a flip under a meaning-CHANGING transform is suppressed.
    def _fake_transform(obj):
        from fractions import Fraction
        n = int(obj["n"])
        x = Fraction(str(obj["mean_str"])) + Fraction(1, n)   # NOT meaning-preserving
        return {"mean_str": f"{float(x):.2f}", "n": n, "items": int(obj.get("items", 1))}
    even = [c for c in cands if int(c["n"]) % 2 == 0]
    # without the guard (no oracle) the fake transform WOULD manufacture a kill; assert that
    # WITH the oracle it is suppressed (Survived), proving the A11 guard works.
    mm_fake_unguarded = metamorphic_hunt(good, even, [("fake-add-1/n", _fake_transform)],
                                         max_probes=40000)             # no oracle -> caller-asserted
    assert isinstance(mm_fake_unguarded, Kill), ("A11 setup: the fake transform should manufacture "
        "a flip when UNGUARDED (else the test proves nothing)")
    mm_fake_guarded = metamorphic_hunt(good, even, [("fake-add-1/n", _fake_transform)],
                                       max_probes=40000, oracle=oracle)
    assert isinstance(mm_fake_guarded, Survived), ("A11 REGRESSION: a fake non-meaning-preserving "
        "transform produced a SPURIOUS metamorphic KILL on the good gate (oracle guard failed)")
    print("  (A11) fake-transform rail: PASS (oracle rejects the meaning-CHANGING transform; "
          "spurious metamorphic kill suppressed; real meaning-preserving kill still fires)")

    # ===== AUDIT A3 (1-decimal-only bug) + A9 (items>=2-only bug): candidate-stream blindspot =====
    # The auditor planted bugs active ONLY on 1dp means / ONLY on items>=2; both SURVIVED the
    # old 2dp-items=1-only stream. FIX: the candidate stream now spans D in {0,1,2,3} and items
    # in {1,2,3}, so both planted bugs are now CAUGHT.
    from fractions import Fraction as _Fr
    def _gate_1dp_bug(mean_str, n, items=1):
        s = str(mean_str); D = len(s.split(".")[1]) if "." in s else 0
        x = _Fr(s); Neff = int(n) * int(items)
        tol = _Fr(1, 10 ** D) if D == 1 else _Fr(1, 2 * 10 ** D)   # BUG only on 1dp
        return {"consistent": _math.ceil((x - tol) * Neff) <= _math.floor((x + tol) * Neff)}
    g1 = GateAdapter("GRIM-1dp-bug", _gate_1dp_bug, _grim_to_verdict)
    k1 = false_accept_hunt(g1, oracle, cands, max_probes=200000, coverage_note=_grim_candidate_coverage())
    assert isinstance(k1, Kill), "A3 REGRESSION: a 1-decimal-only bug SURVIVED (stream blindspot reopened)"
    assert len(str(k1.obj["mean_str"]).split(".")[-1]) == 1, "A3: exhibit should be a 1dp mean"

    def _gate_items_bug(mean_str, n, items=1):
        s = str(mean_str); D = len(s.split(".")[1]) if "." in s else 0
        x = _Fr(s); Neff = int(n) * int(items)
        # BUG: a too-wide (full-ULP) tolerance band ONLY when items>=2 -> false-ACCEPTs some
        # genuinely-inconsistent items>=2 means; correct (half-ULP) elsewhere. A bug class that
        # the old items=1-only candidate stream could never reach.
        tol = _Fr(1, 10 ** D) if int(items) >= 2 else _Fr(1, 2 * 10 ** D)
        return {"consistent": _math.ceil((x - tol) * Neff) <= _math.floor((x + tol) * Neff)}
    g9 = GateAdapter("GRIM-items-bug", _gate_items_bug, _grim_to_verdict)
    k9 = false_accept_hunt(g9, oracle, cands, max_probes=200000, coverage_note=_grim_candidate_coverage())
    assert isinstance(k9, Kill), "A9 REGRESSION: an items>=2-only bug SURVIVED (stream blindspot reopened)"
    assert int(k9.obj.get("items", 1)) >= 2, "A9: exhibit should have items>=2"
    # and the SURVIVED report on the GOOD gate now NAMES its candidate-stream regime (no silent blindspot)
    fa_named = false_accept_hunt(good, oracle, cands, max_probes=20000,
                                 coverage_note=_grim_candidate_coverage())
    assert "CANDIDATE-STREAM REGIME PROBED" in fa_named.residual_risk, \
        "A3/A9 honesty: SURVIVED must name the candidate-stream regime probed"
    print(f"  (A3/A9) candidate-stream coverage: PASS (1dp-only bug CAUGHT {k1.obj}; "
          f"items>=2-only bug CAUGHT {k9.obj}; SURVIVED names its regime)")

    # ===== AUDIT A1 (trivially-circular oracle tripwire) =====
    # The harness cannot PROVE methodological independence, but it now refuses the literal
    # same-callable case. Register an oracle whose truth() IS the gate's own verdict callable.
    def _shared_engine(mean_str, n, items=1):
        return {"consistent": _grim_truth(mean_str, n, items)}
    shared_gate = GateAdapter("shared", _shared_engine, _grim_to_verdict)
    circular = Oracle("secretly-the-gate", _shared_engine, is_independent=True,
                      method="secretly wraps the gate", controls_good=g2, controls_bad=b2)
    refused = False
    try:
        false_accept_hunt(shared_gate, circular, cands[:5], max_probes=5)
    except ValueError as e:
        refused = "TRIVIALLY CIRCULAR" in str(e)
    assert refused, "A1 REGRESSION: a trivially-circular (same-callable) oracle was NOT refused"
    print("  (A1) trivial-circularity tripwire: PASS (same-callable oracle refused; deeper "
          "methodological independence remains a documented OPERATOR INVARIANT)")

    # ===== AUDIT A10 (DEFINITE->ABSTAIN metamorphic flip is now catchable when enabled) =====
    # The auditor's gate abstained on T(X) instead of flipping to a different definite verdict;
    # the default suppresses it. With flag_definite_to_abstain=True it is caught -- still gated
    # by the A11 meaning-preservation check (the items-split transform IS meaning-preserving).
    def _gate_abstain_on_split(mean_str, n, items=1):
        ni, it = int(n), int(items)
        if it >= 2 and ni < 8:                    # after an even-n items-split, small n -> ABSTAIN
            return {"consistent": None}
        return {"consistent": _grim_truth(mean_str, ni, it)}
    g10 = GateAdapter("GRIM-abstain-on-split", _gate_abstain_on_split, _grim_to_verdict)
    seeds10 = [c for c in cands if int(c["n"]) % 2 == 0 and int(c["n"]) < 16 and int(c.get("items", 1)) == 1]
    mm_default = metamorphic_hunt(g10, seeds10, _items_split_transforms(), max_probes=40000, oracle=oracle)
    mm_strict = metamorphic_hunt(g10, seeds10, _items_split_transforms(), max_probes=40000,
                                 oracle=oracle, flag_definite_to_abstain=True)
    assert isinstance(mm_default, Survived), "A10 setup: DEFINITE->ABSTAIN should be SAFE by default"
    assert isinstance(mm_strict, Kill), ("A10 REGRESSION: DEFINITE->ABSTAIN flip not caught even with "
        "flag_definite_to_abstain=True (the documented gap is no longer closeable)")
    assert mm_strict.gate_verdict2 == ABSTAIN
    print("  (A10) definite->abstain gap: PASS (suppressed by default for no-false-alarm; "
          "CATCHABLE via flag_definite_to_abstain=True, still meaning-preservation-gated)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: crucible_harness.py selftest")
