#!/usr/bin/env python3
"""MOCK GLOVES ledger feed for COMPOSEAUTH (G3).

G3 is the COMPOSITIONAL-authorization rail: it sits downstream of GLOVES and budgets
the SEQUENCE of GLOVES-allowed actions. In production it subscribes to GLOVES'
append-only actuation ledger (weapons/gloves/gloves_gate.py::_ledger_entry). To stay
UNBLOCKED on GLOVES infra (the kickoff: "Build against a MOCK GLOVES ledger feed —
do not block on GLOVES"), this module synthesises ledger entries in the EXACT shape
GLOVES emits, plus the one field the independent audit (Finding 2) requires:

    other_effects : a catch-all map  {resource_class: amount}  for blast-radius types
                    NOT covered by GLOVES' fixed columns. A novel effect lands here so
                    G3 can route it to UNCOVERED instead of silently dropping it.

A real GLOVES ledger entry (verbatim from gloves_gate._ledger_entry):
    {tool_id, params, tier, authorization, dry_run_hash, blast_units, ts, G3_note}

COMPOSEAUTH maps each entry to per-CLASS deltas via the (POLICY) effect-extractor
below. The extractor is the honest seam: it knows how to read a KNOWN tool's effect
into a known resource class; an UNKNOWN tool, or a known tool carrying an effect in a
class G3 doesn't enumerate, surfaces in `other_effects` -> UNCOVERED (never "within
budget"). This module is pure data + pure functions: no model, no real I/O.
"""
import math
import time


class MalformedBlast(ValueError):
    """A blast amount that cannot be safely budgeted (negative / NaN / Inf /
    un-parseable). G3 NEVER silently rounds these to 0 (that is a false-accept: a
    negative blast would *decrement* a running budget, an Inf/NaN would slip past as
    $0). The extractor RAISES this; the frozen gate's fail-closed wrapper turns it into
    a HALT. (Audit fix: Defects 1 & 5 — negative-blast false-accept + NaN/Inf-not-closed.)
    """


# ---------------------------------------------------------------------------
# The resource CLASSES G3 enumerates. "You can only budget what you ENUMERATE."
# Anything not in here is UNCOVERED. (kickoff §6 honesty rail.)
# ---------------------------------------------------------------------------
TRACKED_CLASSES = (
    "financial",      # $ committed this session
    "data_mutation",  # # records created/updated/deleted
    "broadcast",      # # external recipients contacted
    "destruction",    # # irreversible deletes / overwrites
    "external_calls", # # external API calls (rate / denial-of-wallet guard)
)

# ---------------------------------------------------------------------------
# POLICY effect-extractor: how a KNOWN tool's ledger entry maps to per-class deltas.
# This is a POLICY input (a human-owned choice of how to read a tool's blast radius),
# NOT derived truth — flagged as such. A tool absent here whose blast lands outside
# TRACKED_CLASSES is surfaced via other_effects -> UNCOVERED.
#
# Each value is either:
#   - a constant int  (fixed per-call cost in that class), or
#   - a ("param", key) pair  (read the amount from the action's params[key]).
# ---------------------------------------------------------------------------
EFFECT_EXTRACTOR = {
    # financial: a charge/transfer reads its amount from params["amount"]
    "money.transfer":   {"financial": ("param", "amount")},
    "billing.charge":   {"financial": ("param", "amount")},
    # data mutation: each call mutates params["n_records"] (default 1)
    "record.create_one":{"data_mutation": ("param", "n_records")},
    "db.update_rows":   {"data_mutation": ("param", "n_records")},
    # broadcast: each send reaches len(params["to"]) recipients (default 1)
    "email.send_one":   {"broadcast": ("param_len", "to")},
    "email.mass_send":  {"broadcast": ("param_len", "to")},
    # destruction: each delete/overwrite is 1 irreversible op; mass drop = n_records
    "fs.overwrite":     {"destruction": 1},
    "db.drop_table":    {"destruction": ("param", "n_records")},
    # external calls: every external tool costs 1 external call (rate guard)
    "api.call_external":{"external_calls": 1},
}

# Tools that are external API calls in ADDITION to their primary class
# (so a money.transfer also ticks external_calls, for the denial-of-wallet guard).
ALSO_EXTERNAL_CALL = {
    "money.transfer", "billing.charge", "email.send_one", "email.mass_send",
    "record.create_one", "db.update_rows", "api.call_external",
}


def gloves_ledger_entry(tool_id, params, tier="AUTO", authorization="policy:AUTO-R0-local",
                        blast_units=0, dry_run_hash=None, other_effects=None, ts=None):
    """Build a single ledger entry in GLOVES' exact emitted shape + the other_effects
    catch-all the audit (Finding 2) requires. `other_effects` is an optional
    {resource_class: amount} map for blast types outside GLOVES' fixed columns."""
    return {
        "tool_id": tool_id,
        "params": dict(params or {}),
        "tier": tier,
        "authorization": authorization,
        "dry_run_hash": dry_run_hash,
        "blast_units": int(blast_units),
        "ts": time.time() if ts is None else ts,
        # The catch-all (audit Finding 2): a novel blast type that GLOVES can't column
        # rides here so G3 routes it to UNCOVERED rather than silently dropping it.
        "other_effects": dict(other_effects or {}),
        "G3_note": "per-action ledger entry; composition gated by G3 (COMPOSEAUTH).",
    }


def extract_effects(entry):
    """POLICY extractor (kappa<1 across population, kappa=1 within the policy table):
    map ONE GLOVES ledger entry -> per-class deltas.

    Returns (deltas, uncovered) where:
      deltas    : {tracked_class: int}  amounts to add to the session counters.
      uncovered : {class_name: amount}  effects G3 does NOT track -> reported, never
                  added to a counter (the honesty rail; no silent "within budget").

    UNCOVERED arises two ways:
      1. a KNOWN tool carries `other_effects` in a class not in TRACKED_CLASSES; OR
         the tool itself is UNKNOWN to the extractor (we cannot read its blast) -> the
         entry's blast_units are reported as an uncovered effect.
      2. an `other_effects` key that IS a tracked class is still treated as uncovered
         here ONLY if the source is the catch-all of an unknown tool (we do not trust
         an un-modelled tool to self-declare into a tracked counter).
    """
    deltas = {}
    uncovered = {}
    tool_id = entry.get("tool_id")
    params = entry.get("params", {}) or {}
    spec = EFFECT_EXTRACTOR.get(tool_id)

    if spec is None:
        # UNKNOWN tool: we cannot map its blast into a tracked class. Report its
        # blast_units (and any other_effects) as UNCOVERED. NEVER silently count it.
        # _num RAISES MalformedBlast on negative/NaN/Inf so a malformed blast on an
        # unknown tool ALSO fails closed (-> HALT) instead of being swallowed to 0.
        bu = _num(entry.get("blast_units", 0))
        if bu:
            uncovered[f"untracked_tool:{tool_id}"] = bu
        for cls, amt in (entry.get("other_effects") or {}).items():
            uncovered[f"untracked_tool:{tool_id}:{cls}"] = _amount(amt, params)
        if not uncovered:
            # no measurable blast, but still flag the tool as unrecognised
            uncovered[f"untracked_tool:{tool_id}"] = 0
        return deltas, uncovered

    # KNOWN tool: map each declared class.
    for cls, rule in spec.items():
        amt = _resolve(rule, params)
        if cls in TRACKED_CLASSES:
            deltas[cls] = deltas.get(cls, 0) + amt
        else:
            uncovered[cls] = uncovered.get(cls, 0) + amt

    # external-call tick (denial-of-wallet guard) for tools that hit the network.
    # FIX (independent audit 2026-06-21): only add the tick if the tool did NOT already
    # declare external_calls in its EFFECT_EXTRACTOR spec — otherwise api.call_external
    # (which is in BOTH the spec and ALSO_EXTERNAL_CALL) double-counts to 2.
    if tool_id in ALSO_EXTERNAL_CALL and "external_calls" not in spec:
        deltas["external_calls"] = deltas.get("external_calls", 0) + 1

    # KNOWN tool, but the ledger carried a novel blast type in other_effects:
    # if that class is NOT tracked -> UNCOVERED (audit Finding 2 catch-all).
    for cls, amt in (entry.get("other_effects") or {}).items():
        a = _amount(amt, params)
        if cls in TRACKED_CLASSES:
            # a tracked class declared via the catch-all by a KNOWN tool is honoured.
            deltas[cls] = deltas.get(cls, 0) + a
        else:
            uncovered[cls] = uncovered.get(cls, 0) + a

    return deltas, uncovered


def _resolve(rule, params):
    if isinstance(rule, int):
        if rule < 0:                              # a negative POLICY constant is a bug
            raise MalformedBlast(f"negative policy constant {rule}")
        return rule
    if isinstance(rule, tuple) and rule[0] == "param":
        return _num(params.get(rule[1], 0))
    if isinstance(rule, tuple) and rule[0] == "param_len":
        v = params.get(rule[1], 1)
        if isinstance(v, (list, tuple, set)):
            return len(v)
        # DEFECT 2 FIX (silent undercount via string 'to'): a NON-list recipient must
        # NOT fall through to _num() and become 0 (15 string-'to' emails silently stayed
        # at broadcast=0 and never tripped the >10 escalate). A bare scalar recipient is
        # AT LEAST one recipient — count it as 1, never 0. (Conservative: we never
        # under-count a contact into invisibility. A real adapter should emit a list;
        # this is the floor so a logging/adapter slip cannot zero-out a broadcast.)
        if v is None:
            return 0
        if isinstance(v, str):
            return 1 if v.strip() else 0       # one named recipient (or empty -> none)
        if isinstance(v, (int, float)):
            return _num(v) if v else 0         # an explicit numeric recipient count
        # any other non-empty scalar (dict, object, ...) is one opaque recipient
        return 1 if v else 0
    return 0


def _amount(amt, params):
    """An other_effects value may be a constant or a ("param", key) reference."""
    if isinstance(amt, bool):                    # bool is an int subclass — block it
        raise MalformedBlast(f"boolean blast amount {amt!r} is not a count")
    if isinstance(amt, (int, float)):
        return _num(amt)
    if isinstance(amt, tuple):
        return _resolve(amt, params)
    return _num(amt)


def _num(v):
    """Parse a blast amount to a non-negative int, or RAISE MalformedBlast.

    NEVER silently returns 0 for a value that *had* a magnitude:
      - NaN / +Inf / -Inf            -> MalformedBlast  (Defect 5: was silently 0)
      - a negative number            -> MalformedBlast  (Defect 1: was a budget DECREMENT)
      - an un-parseable string/object-> MalformedBlast  (was silently 0)
    A genuine absence (None / "" / 0) maps to 0 — that is a real zero, not a swallowed
    magnitude. The frozen gate's fail-closed wrapper turns any MalformedBlast into HALT.
    """
    if v is None:
        return 0
    if isinstance(v, bool):                      # True/False are not blast counts
        raise MalformedBlast(f"boolean blast amount {v!r} is not a count")
    if isinstance(v, str):
        s = v.strip()
        if s == "":
            return 0
        try:
            f = float(s)
        except (TypeError, ValueError):
            raise MalformedBlast(f"un-parseable blast amount {v!r}")
    elif isinstance(v, (int, float)):
        f = float(v)
    else:
        raise MalformedBlast(f"un-parseable blast amount of type {type(v).__name__}")
    if math.isnan(f) or math.isinf(f):
        raise MalformedBlast(f"non-finite blast amount {v!r}")
    # FIX (independent audit 2026-06-21): use CEIL, not banker's round. For a blast/budget
    # guard, under-counting is the unsafe direction (it lets an overage stay "within budget"):
    # int(round(2.5))==2 under-billed a $2.50 charge. ceil makes the guard conservative —
    # any positive fraction counts as >=1 unit; integer amounts are unchanged.
    # check negativity on the FLOAT, before ceil — math.ceil(-0.6)==0 would otherwise
    # silently swallow a negative blast (a budget-decrement attack) instead of raising.
    if f < 0:
        raise MalformedBlast(f"negative blast amount {v!r} (would decrement the budget)")
    return math.ceil(f)


def _selftest():
    # KNOWN financial tool -> financial delta + an external_calls tick
    e = gloves_ledger_entry("money.transfer", {"amount": 20}, tier="STEP-UP")
    d, u = extract_effects(e)
    assert d["financial"] == 20 and d["external_calls"] == 1 and u == {}, (d, u)

    # KNOWN broadcast tool reads recipient count from len(to)
    e = gloves_ledger_entry("email.send_one", {"to": ["a", "b", "c"]})
    d, u = extract_effects(e)
    assert d["broadcast"] == 3 and d["external_calls"] == 1, (d, u)

    # KNOWN destruction tool -> destruction delta
    e = gloves_ledger_entry("fs.overwrite", {"path": "/p/f"})
    d, u = extract_effects(e)
    assert d["destruction"] == 1, (d, u)

    # UNKNOWN tool -> nothing counted; blast reported as UNCOVERED (never silent)
    e = gloves_ledger_entry("quantum.entangle", {"qubits": 9}, blast_units=7)
    d, u = extract_effects(e)
    assert d == {} and any(k.startswith("untracked_tool:") for k in u), (d, u)

    # KNOWN tool carrying a NOVEL blast type in other_effects -> UNCOVERED catch-all
    e = gloves_ledger_entry("fs.overwrite", {"path": "/p/f"},
                            other_effects={"reputation_harm": 5})
    d, u = extract_effects(e)
    assert d["destruction"] == 1 and u.get("reputation_harm") == 5, (d, u)

    # ===================== AUDIT REGRESSION TESTS (extractor level) =====================
    # AUDIT 2026-06-21: api.call_external must NOT double-count external_calls (it is in BOTH
    # EFFECT_EXTRACTOR and ALSO_EXTERNAL_CALL) -> exactly 1, not 2; money.transfer still ticks 1.
    assert extract_effects(gloves_ledger_entry("api.call_external", {}))[0].get("external_calls") == 1, "double-count regression"
    assert extract_effects(gloves_ledger_entry("money.transfer", {"amount": 5}))[0].get("external_calls") == 1, "ext tick regression"
    # AUDIT 2026-06-21: blast rounding is CEIL (fail-safe for a budget), not banker's round.
    assert _num(2.5) == 3 and _num(2.0) == 2 and _num(0) == 0, "ceil-rounding regression"
    # (R1) NEGATIVE blast amount must RAISE, never pass a negative delta through that
    # would decrement a running budget (audit Defect 1). Before: _num(-80) returned -80.
    for bad in (-1, -80, -0.6):
        try:
            _num(bad)
            assert False, f"_num({bad}) must raise MalformedBlast, not pass a negative"
        except MalformedBlast:
            pass
    # the same for a negative param/other_effects amount through the public extractor
    try:
        extract_effects(gloves_ledger_entry("billing.charge", {"amount": -80}))
        assert False, "negative param amount must raise MalformedBlast"
    except MalformedBlast:
        pass

    # (R5) NaN / Inf must RAISE, never silently round to 0 (audit Defect 5).
    for bad in (float("inf"), float("-inf"), float("nan")):
        try:
            _num(bad)
            assert False, f"_num({bad!r}) must raise MalformedBlast, not return 0"
        except MalformedBlast:
            pass

    # (R2) a STRING 'to' (not a list) must count as >=1 recipient, never silently 0
    # (audit Defect 2). Before: _resolve(('param_len','to'), {'to':'a@x'}) -> _num -> 0.
    e = gloves_ledger_entry("email.send_one", {"to": "alice@example.com"})
    d, u = extract_effects(e)
    assert d["broadcast"] == 1, ("string-'to' must count 1 recipient, not 0", d)
    # an empty string is a real zero (genuine absence), not a swallowed magnitude
    e = gloves_ledger_entry("email.send_one", {"to": "   "})
    d, u = extract_effects(e)
    assert d["broadcast"] == 0, ("blank-'to' is a real 0", d)

    # an un-parseable / boolean amount also fails closed (not silently 0)
    for bad in ("not-a-number", True, False):
        try:
            _num(bad)
            assert False, f"_num({bad!r}) must raise MalformedBlast"
        except MalformedBlast:
            pass

    print("mock_gloves_ledger selftest: PASS (known->mapped deltas + external tick; "
          "unknown tool->UNCOVERED; novel other_effects class->UNCOVERED catch-all; "
          "+AUDIT-REGRESSIONS: negative/NaN/Inf/unparseable blast RAISE (never silent 0 or "
          "decrement); string-'to' counts >=1 recipient (no silent undercount))")


if __name__ == "__main__":
    _selftest()
