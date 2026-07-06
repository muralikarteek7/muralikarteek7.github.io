#!/usr/bin/env python3
"""router.py — the v4 ROUTER: GATE 1 intake classifier + GATE 2 saturation tripwire.

Spec: Next/BOX_ARMOR_WEAPONS.md §6. This is a DETERMINISTIC classifier (no LLM judgment)
so it is unit-testable on the cap-set replay. It routes on the PRESENCE of a checker
(kappa as a binary gate), not a fitted kappa*rho score (the cycle-2 negative: rho is
split-sensitive and does not transfer at small N).

ARMOR boundary: the router decides WHEN to draw and hands off to WEAPONS (weapon_draw).
It never produces or verifies an object itself.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# CONFIG — ⚠️ ALL constants PROVISIONAL: tuned on the single cap-set episode
# (n-of-1, per the 2026-06-10 audit). Re-tune per arena; never hard-code into
# a universal rule without cross-arena evidence.
# ---------------------------------------------------------------------------
TRIPWIRE_CONFIG = {
    "K_FAMILIES": 2,          # distinct method families clustered... (spec says "≥2–3";
                              #   2 matches the historical ILS-88/exact-89 signature — n-of-1 tuned)
    "PLATEAU_BAND": 0.05,     # ...within this relative band of each other...
    "BELOW_BOUND": True,      # ...and below the known/target bound
    "HARD_STOP_RUNS": 2,      # > this many runs of >= HARD_STOP_RUN_SECS with no gain
    "HARD_STOP_RUN_SECS": 700,
    "HARD_STOP_AGENT_SECS": 1800,  # any single agent run > 30 min with no gain
}

# GATE 1 known-object detector (spec: regex + a named integer target)
# G2.1 fix (2026-06-10): word boundaries added — bare 'OGR' matched inside 'prOGRamming'
# and misrouted a judgment item in the G2 run (confirmed defect, see V4_G2_RESULTS).
KNOWN_OBJECT_RE = re.compile(
    r"proven\s+max(imum)?|\boptimal\b|known\s+max|\bHill\b|\bGolomb\b|\bOGR\b|AG\(|\bSidon\b|cap\s*set",
    re.IGNORECASE)

PROBLEM_CLASSES = ("KNOWN_RESULT_REPRODUCTION", "OPEN_FRONTIER_DISCOVERY",
                   "CHECKABLE_COMPUTATION", "FETCHABLE_FACT", "JUDGMENT_ONLY")


@dataclass
class TaskSignature:
    named_optimum: bool = False        # the target is a single named/proven extremal value
    known_object_ref: str | None = None  # e.g. "AG(6,3) cap set", "Golomb ruler k=12"
    has_cheap_verifier: bool = False   # a machine verifier for the object exists
    claim_checkable: bool = False      # code / construction / numeric / invariant
    fetchable_fact: bool = False
    judgment_only: bool = False
    target_is_open: bool = False       # the bound/optimum is genuinely OPEN (overrides ground-first)


@dataclass
class Route:
    problem_class: str
    gate: str                  # the gate behavior the caller MUST obey
    search_blocked: bool       # True => search budget gated behind a completed structure-fetch
    rule: str                  # priority rule that matched (S1..S4)


def known_status_lookup(arena, param, fetched_pegs=None):
    """AUTONOMOUS known-vs-open resolution against the box's GROUNDED knowledge tables
    (audit D2 fix: the harness must NOT inject the answer; the router consults the same
    machine tables the verifier uses — capset KNOWN_MAX/KNOWN_LB; OGR pegs FETCHED in-run).
    Returns (status, peg): ('KNOWN', optimum) | ('OPEN', lower_bound) | ('UNKNOWN', None)."""
    if arena == "capset":
        import importlib
        cv = importlib.import_module("capset_verify")
        if param in cv.KNOWN_MAX:
            return "KNOWN", cv.KNOWN_MAX[param]
        if param in cv.KNOWN_LB:
            return "OPEN", cv.KNOWN_LB[param]
        return "UNKNOWN", None
    if arena == "sidon":
        pegs = fetched_pegs or {}
        if param in pegs:                  # pegs must come from an in-run fetch, never LLM memory
            return "KNOWN", pegs[param]
        return "UNKNOWN", None
    return "UNKNOWN", None


def classify(text, arena=None, param=None, fetched_pegs=None):
    """The router's full intake: build the signature from the task TEXT, then resolve
    known-vs-open AUTONOMOUSLY via known_status_lookup. The table verdict overrides the
    text regex (the regex alone would misclassify open problems that *name* a known object,
    e.g. 'cap set' at n=7). Returns (Route, status, peg)."""
    sig = signature_from_text(text)
    status, peg = (known_status_lookup(arena, param, fetched_pegs)
                   if arena is not None else ("UNKNOWN", None))
    if status == "KNOWN":
        sig.named_optimum = True
        sig.target_is_open = False
    elif status == "OPEN":
        sig.named_optimum = False
        sig.target_is_open = True
    else:
        # no grounded table entry: be conservative — do NOT fetch-gate on a regex hunch
        sig.named_optimum = False
        sig.target_is_open = True if sig.known_object_ref else sig.target_is_open
    return route(sig), status, peg


def signature_from_text(text, known_status=None):
    """Cheap helper: build a TaskSignature from a task description string.
    known_status: optional override 'KNOWN' | 'OPEN' from the arena's ground-truth table
    (e.g. capset_verify KNOWN_MAX vs KNOWN_LB) — the table, when present, beats the regex."""
    sig = TaskSignature()
    if KNOWN_OBJECT_RE.search(text):
        sig.known_object_ref = KNOWN_OBJECT_RE.search(text).group(0)
        sig.has_cheap_verifier = True
        sig.claim_checkable = True
    if re.search(r"\b(proven|known)\s+(max(imum)?|optimal)\b.*\d+|\bmax(imum)?\s*=\s*\d+", text, re.I):
        sig.named_optimum = True
    if known_status == "KNOWN":
        sig.named_optimum = True
        sig.target_is_open = False
    elif known_status == "OPEN":
        sig.named_optimum = False
        sig.target_is_open = True
    return sig


def route(sig: TaskSignature) -> Route:
    """GATE 1 — priority-ordered, first match wins (spec §6 S1–S4)."""
    # S1 — KNOWN-RESULT: ground-first; search BLOCKED until a structure-fetch returns coordinates.
    if (sig.named_optimum or sig.known_object_ref is not None) and not sig.target_is_open:
        return Route("KNOWN_RESULT_REPRODUCTION",
                     gate="GROUND_FIRST: mandatory literature-fetch before any solver; "
                          "a no-coordinates fetch ESCALATES to the primary paper, never to search",
                     search_blocked=True, rule="S1")
    # S1b — open frontier with a cheap verifier: search/derive is the LEGITIMATE first move.
    if sig.target_is_open and (sig.has_cheap_verifier or sig.claim_checkable):
        return Route("OPEN_FRONTIER_DISCOVERY",
                     gate="VERIFIER_ONLY: no answer key exists; every construction is a claim "
                          "until machine-certified; report plateaus plainly",
                     search_blocked=False, rule="S1b")
    # S2 — checkable claim: execute, never let the panel be the final word.
    if sig.claim_checkable or sig.has_cheap_verifier:
        return Route("CHECKABLE_COMPUTATION",
                     gate="EXECUTE: run the check; panel FORBIDDEN as final word",
                     search_blocked=False, rule="S2")
    # S3 — fetchable fact.
    if sig.fetchable_fact:
        return Route("FETCHABLE_FACT", gate="FETCH with as-of date",
                     search_blocked=False, rule="S3")
    # S4 — judgment only: PURE_ARMOR (weapon=NONE), auditable.
    return Route("JUDGMENT_ONLY",
                 gate="PURE_ARMOR: weapon=NONE; un-pipelined cross-model panel + scored abstention",
                 search_blocked=False, rule="S4")


# ---------------------------------------------------------------------------
# GATE 2 — runtime saturation tripwire
# ---------------------------------------------------------------------------
@dataclass
class RunRecord:
    family: str            # method family name (greedy / ILS / exact / LNS ...)
    best: float            # best verified incumbent this family reached
    run_secs: float        # wall-clock of the run
    improved: bool         # did it improve the global incumbent?
    self_certified_max: bool = False  # result came WITH a proof of its own maximality


def saturation_tripwire(records, known_bound=None, config=TRIPWIRE_CONFIG):
    """Return (fired: bool, reason: str). Fire STRUCTURAL_GAP when any holds:
    (a) >= K distinct families plateau within PLATEAU_BAND of each other AND below known_bound;
    (b) any result self-certifies its own maximality (class exhausted);
    (c) compute-without-gain hard stop crossed.
    Firing must BLOCK further same-weapon escalation and force a re-route to S1 (fetch)."""
    if any(r.self_certified_max for r in records):
        return True, "STRUCTURAL_GAP: a result arrived WITH a proof of its own maximality — class exhausted"
    # (a) plateau cluster below the bound
    best_by_family = {}
    for r in records:
        best_by_family[r.family] = max(best_by_family.get(r.family, float("-inf")), r.best)
    bests = sorted(best_by_family.values(), reverse=True)
    if known_bound is not None and len(bests) >= config["K_FAMILIES"]:
        top = bests[:config["K_FAMILIES"]]
        lo, hi = min(top), max(top)
        if hi < known_bound and hi > 0 and (hi - lo) / hi <= config["PLATEAU_BAND"]:
            return True, (f"STRUCTURAL_GAP: {config['K_FAMILIES']} families plateau at "
                          f"{top} (band <= {config['PLATEAU_BAND']*100:.0f}%) below bound {known_bound}")
    # (c) compute-without-gain
    long_runs_no_gain = [r for r in records
                         if r.run_secs >= config["HARD_STOP_RUN_SECS"] and not r.improved]
    if len(long_runs_no_gain) > config["HARD_STOP_RUNS"]:
        return True, f"STRUCTURAL_GAP: {len(long_runs_no_gain)} runs >= {config['HARD_STOP_RUN_SECS']}s with no gain"
    if any(r.run_secs > config["HARD_STOP_AGENT_SECS"] and not r.improved for r in records):
        return True, "STRUCTURAL_GAP: single agent run > hard stop with no gain"
    return False, "no tripwire"


if __name__ == "__main__":
    import json
    demo = signature_from_text("Find a maximum cap set in AG(6,3); the proven maximum is 112.",
                               known_status="KNOWN")
    r = route(demo)
    print(json.dumps({"route": r.__dict__}, indent=2))
