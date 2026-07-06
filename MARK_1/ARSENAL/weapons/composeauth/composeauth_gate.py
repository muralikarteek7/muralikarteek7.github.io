#!/usr/bin/env python3
"""COMPOSEAUTH (G3) frozen compositional-authorization gate — the LEDGER-BUDGET rail.

GLOVES gates each ACTION; G3 gates the SEQUENCE. A stream of individually-safe,
individually-authorized steps must not silently compose into a catastrophe (100 small
reversible deletes = one irreversible wipe; 50 authorized $20 charges = $1000 nobody
approved). G3 keeps an EXACT running blast-radius budget per ENUMERATED resource class
over GLOVES' allowed actions and, the moment a COMMITTED threshold is crossed,
escalates the tier of the NEXT action or HALTs + escalates to a human.

    decide(entry) -> {
        "decision":   OK | ESCALATE | HALT,
        "tier_escalation": None | "STEP-UP",   # set when ESCALATE
        "tripped":    [ {class, level, running, threshold}, ... ],  # what crossed
        "uncovered":  { class: amount, ... },   # blast G3 does NOT track (honesty rail)
        "counters":   { class: running_total }, # the persisted per-class budget
        "blast_score":int,                      # Σ weighted composite
        "reason":     str,
        "policy_banner": str,                   # thresholds+weights are POLICY not truth
        "tracked_classes": (...),               # what IS budgeted (the rest is uncovered)
    }

κ HONESTY (kickoff §1, §6):
  - The accumulation (Σ per class) + threshold comparison is κ=1 exact arithmetic — a
    sum crossing a frozen threshold is a machine fact (like the Registrar's token
    budget, like OPTIMA's objective recompute).
  - "Is this composition MALICIOUS?" is κ=0 intent — G3 ESCALATES/HALTs, it does NOT
    accuse. It never judges intent.
  - The effect-EXTRACTOR (mock_gloves_ledger.extract_effects) is κ=1 within its policy
    table, κ<1 across tool population — an unknown tool / novel blast class is routed
    to UNCOVERED, never silently counted as "within budget."

MONOTONICITY IS ENFORCED, not just asserted (audit fix Defect 1 + honesty over-claim):
counters are non-decreasing within a session because (a) the extractor REFUSES negative /
NaN / Inf / un-parseable blast at the source (raises MalformedBlast) and (b) BudgetStore.add
REJECTS any negative delta — both fail closed to HALT. The old wording ("counters only ever
increase; there is no decrement API, so a runaway cannot spend down its way back under a
threshold") was a FALSE security claim: add() applied a negative delta with no sign check, so
a -$80 charge decremented a $100 budget back to $20. That is now blocked + regression-tested.

PERSISTENCE IS LOAD-BEARING (kickoff §3d, §6): counters survive a process restart. A budget
that resets on crash is defeated by "crash-and-resume." The store is a JSON file; each accepted
entry is committed BEFORE the next decision so a crash cannot lose budget. A corrupt / tampered
/ negative persisted store does NOT reset to zero and does NOT crash __init__ open — it POISONS
the store so every decide() HALTs (audit fix: corrupt-store init no longer bypasses the gate).
(INFRA LIMIT, same as GLOVES: in a pure-software box the store is not guaranteed outside the
agent's write scope — true tamper-resistance needs fs-perms / a separate process / the harness.
Stated, not faked.)

FAIL CLOSED: any uncaught exception in the decision path -> HALT (never OK), AND a poisoned
store -> HALT, AND a malformed (negative/NaN/Inf/unparseable) blast amount -> HALT. A budget
gate that crashes-open, resumes-empty, or swallows a malformed amount to $0 is no gate.
"""
import json
import os

import composeauth_policy as POLICY
from mock_gloves_ledger import extract_effects, TRACKED_CLASSES


class BudgetStore:
    """Persistent, ENFORCED-monotonic per-class counter store (crash-resume safe).

    State lives in a JSON file. Loading a non-existent file starts at zero; loading an
    existing file RESUMES the budget (the crash-resume defence).

    MONOTONICITY IS ENFORCED, not merely asserted (audit fix — the old docstring claimed
    'counters only ever increase' but `add()` happily applied a negative delta, so a
    runaway COULD spend its way back under a threshold). `add()` now REJECTS any negative
    delta (raises ValueError, which the gate's fail-closed wrapper turns into a HALT) and
    there is no decrement API. Combined with the extractor refusing negative/NaN/Inf
    blast at the source, the per-class total is genuinely non-decreasing within a session.
    """

    def __init__(self, path):
        self.path = path
        self.counters = {c: 0 for c in TRACKED_CLASSES}
        self.n_actions = 0
        # FAIL-CLOSED on a corrupt/unreadable store (audit fix — a JSONDecodeError used to
        # propagate out of __init__, OUTSIDE decide()'s fail-closed wrapper; a caller that
        # wrapped construction in try/except could then skip the gate entirely). We do NOT
        # raise here; instead we mark the store POISONED so every subsequent decide() HALTs.
        self.load_error = None
        self._load()

    def _load(self):
        if self.path and os.path.exists(self.path):
            try:
                with open(self.path, "r") as fh:
                    data = json.load(fh)
                if not isinstance(data, dict):
                    raise ValueError("store root is not a JSON object")
                # resume: take persisted counters; unknown keys ignored, missing -> 0.
                # A persisted counter must be a non-negative int — a tampered/corrupt
                # negative or non-numeric value poisons the store (fail-closed) rather
                # than resuming a budget that has been 'spent down' below a threshold.
                loaded = {}
                for c in TRACKED_CLASSES:
                    raw = data.get("counters", {}).get(c, 0)
                    iv = int(raw)
                    if iv < 0:
                        raise ValueError(f"persisted counter {c}={iv} is negative")
                    loaded[c] = iv
                n = int(data.get("n_actions", 0))
                if n < 0:
                    raise ValueError(f"persisted n_actions={n} is negative")
                self.counters = loaded
                self.n_actions = n
            except Exception as e:
                # Do NOT propagate out of __init__ (that would bypass decide()'s
                # fail-closed wrapper). Mark POISONED -> every decide() HALTs.
                self.load_error = f"{type(e).__name__}: {e}"

    def _persist(self):
        if not self.path:
            return
        tmp = self.path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump({"counters": self.counters, "n_actions": self.n_actions}, fh)
        os.replace(tmp, self.path)  # atomic rename: a crash leaves old OR new, never torn

    def add(self, deltas):
        """Add per-class deltas (ENFORCED-monotonic), persist, return the new totals.

        A negative delta is REJECTED (raises ValueError -> the gate fail-closes to HALT).
        This is the last line of the monotonicity defence: even if a malformed negative
        amount somehow reached here, it can never decrement a running budget. (Audit fix
        Defect 1 — the old code did `self.counters[cls] += int(amt)` with no sign check,
        so amount=-80 dropped financial from $100 to $20 and a later $20 returned OK at a
        real committed total of $120 that should have ESCALATEd.)
        """
        for cls, amt in deltas.items():
            iv = int(amt)
            if iv < 0:
                raise ValueError(
                    f"monotonicity violation: negative delta {cls}={iv} rejected "
                    "(budget counters are non-decreasing; this fails closed -> HALT)")
            if cls in self.counters:
                self.counters[cls] += iv
        self.n_actions += 1
        self._persist()
        return dict(self.counters)


class ComposeAuthGate:
    """The frozen budget gate. Subscribes to GLOVES' (mock) ledger; on each ledger entry
    it COMMITS that action's blast to the running per-class budget and THEN returns
    OK / ESCALATE / HALT — i.e. the verdict is for the action that just crossed the line
    (and gates the NEXT action's tier). (Audit note: the verdict is evaluated *after* the
    current entry's blast is committed, which is the correct budget-gate behaviour — the
    crossing action is the one that trips.)"""

    def __init__(self, store_path=None):
        self.store = BudgetStore(store_path)

    # -- κ=1 core: pure threshold comparison over the persisted counters ----------
    def _evaluate(self):
        tripped = []
        for cls, total in self.store.counters.items():
            th = POLICY.THRESHOLDS.get(cls)
            if not th:
                continue
            if total > th["halt"]:
                tripped.append({"class": cls, "level": "HALT",
                                "running": total, "threshold": th["halt"]})
            elif total > th["step_up"]:
                tripped.append({"class": cls, "level": "STEP_UP",
                                "running": total, "threshold": th["step_up"]})
        return tripped

    def _blast_score(self):
        score = 0
        for cls, total in self.store.counters.items():
            score += POLICY.SCORE_WEIGHTS.get(cls, 0) * total
        return score

    def decide(self, entry):
        """Process ONE GLOVES ledger entry: add its effect, then decide the budget
        verdict for the NEXT action. FAIL CLOSED on any exception -> HALT."""
        try:
            return self._decide_inner(entry)
        except Exception as e:
            return {
                "decision": "HALT", "tier_escalation": None, "tripped": [],
                "uncovered": {}, "counters": dict(self.store.counters),
                "blast_score": None,
                "reason": f"FAIL-CLOSED on exception in budget path: "
                          f"{type(e).__name__}: {e}",
                "policy_banner": POLICY.POLICY_BANNER,
                "tracked_classes": TRACKED_CLASSES,
            }

    def _decide_inner(self, entry):
        # FAIL-CLOSED if the persisted store was corrupt/unreadable/tampered at load
        # time. A poisoned store means we cannot trust the resumed budget, so every
        # decision HALTs (never OK) until a human resolves it. (Audit fix: corrupt-store
        # init no longer bypasses the gate by raising out of __init__.)
        if self.store.load_error is not None:
            raise RuntimeError(
                f"store poisoned at load (cannot trust resumed budget): "
                f"{self.store.load_error}")
        if not isinstance(entry, dict):
            raise TypeError("ledger entry must be a dict")

        # 1) map the GLOVES entry -> per-class deltas + UNCOVERED blast (honesty rail).
        deltas, uncovered = extract_effects(entry)

        # 2) accumulate (κ=1) and PERSIST (crash-resume defence) BEFORE deciding.
        self.store.add(deltas)

        # 3) evaluate the committed thresholds (κ=1 comparison).
        tripped = self._evaluate()
        score = self._blast_score()

        halts = [t for t in tripped if t["level"] == "HALT"]
        stepups = [t for t in tripped if t["level"] == "STEP_UP"]
        score_halt = score > POLICY.SCORE_HALT

        if halts or score_halt:
            decision, esc = "HALT", None
            bits = [f"{t['class']} running={t['running']} > HALT={t['threshold']}"
                    for t in halts]
            if score_halt:
                bits.append(f"blast_score={score} > SCORE_HALT={POLICY.SCORE_HALT}")
            reason = ("HALT + escalate to human: committed threshold crossed by the "
                      "COMPOSITION (each step alone may have been authorized) — "
                      + "; ".join(bits))
        elif stepups:
            decision, esc = "ESCALATE", "STEP-UP"
            bits = [f"{t['class']} running={t['running']} > STEP_UP={t['threshold']}"
                    for t in stepups]
            reason = ("ESCALATE the NEXT action to STEP-UP: composition crossed a "
                      "committed STEP-UP threshold — " + "; ".join(bits))
        else:
            decision, esc = "OK", None
            reason = ("OK: running composition under all committed thresholds. "
                      "(No false halt on a benign stream.)")

        # 4) the UNCOVERED honesty rail — ALWAYS reported; never silent "within budget".
        if uncovered:
            reason += (" | UNCOVERED blast outside tracked classes "
                       f"{sorted(uncovered)} reported (NOT counted; you can only budget "
                       "what you enumerate).")

        return {
            "decision": decision,
            "tier_escalation": esc,
            "tripped": tripped,
            "uncovered": uncovered,
            "counters": dict(self.store.counters),
            "blast_score": score,
            "reason": reason,
            "policy_banner": POLICY.POLICY_BANNER,
            "tracked_classes": TRACKED_CLASSES,
        }


# ===========================================================================
# THE FIVE NON-WAIVABLE GATE-OF-THE-GATE SELF-TESTS (kickoff §3 a..e)
#   (a) N individually-AUTO small charges that SUM past the financial threshold
#       -> the (N+1)th is ESCALATED, not auto-allowed   [the SALAMI attack]
#   (b) a burst of deletes past the destruction threshold -> HALT
#   (c) a single legitimate small action well under all thresholds -> OK (no false halt)
#   (d) the counter does NOT reset on a simulated session-restart (persistence)
#   (e) effect spread across a class G3 doesn't track -> reported UNCOVERED, never
#       silently "within budget"  (the honesty rail)
# Plus: fail-closed-on-exception, and a per-action SUB-trigger control proving the
# salami steps were each individually under the per-action bar.
# ===========================================================================
import tempfile


def _charge(amount):
    """A GLOVES ledger entry for a small, individually-AUTO-ish financial charge."""
    return {"tool_id": "billing.charge", "params": {"amount": amount},
            "tier": "CONFIRM", "authorization": "token:auto-small",
            "blast_units": amount, "other_effects": {}, "G3_note": ""}


def _delete():
    return {"tool_id": "fs.overwrite", "params": {"path": "/scratch/f"},
            "tier": "CONFIRM", "authorization": "token:auto-small",
            "blast_units": 2, "other_effects": {}}


# The per-action GLOVES trigger we simulate: a single charge >= this would itself be
# STEP-UP at the GLOVES layer. The salami uses charges STRICTLY BELOW it, so each step
# is individually fine and only the COMPOSITION trips G3.
_PER_ACTION_GLOVES_TRIGGER = 50  # $ (a single charge >= $50 would step up at GLOVES)


def _selftest():
    fin_step = POLICY.THRESHOLDS["financial"]["step_up"]   # 100
    dest_halt = POLICY.THRESHOLDS["destruction"]["halt"]   # 25

    # ---- (a) THE SALAMI ATTACK: N charges each < per-action trigger, SUM > threshold.
    # Pick a per-charge amount strictly under the per-action GLOVES trigger AND under
    # the session STEP_UP threshold, so NO single step is individually escalatable.
    per = 20
    assert per < _PER_ACTION_GLOVES_TRIGGER, "salami step must be under the per-action bar"
    assert per < fin_step, "salami step must be under the SESSION step-up too"
    g = ComposeAuthGate(store_path=None)
    n_needed = fin_step // per   # 100 // 20 = 5 -> sum=100 (== threshold, NOT yet >)
    last = None
    for i in range(n_needed):
        last = g.decide(_charge(per))
        # each of the first n_needed steps is individually under the bar -> still OK
        assert last["decision"] == "OK", (i, last)
    # the running total is now exactly the threshold; the NEXT (N+1)th charge crosses it
    nxt = g.decide(_charge(per))
    assert nxt["decision"] == "ESCALATE" and nxt["tier_escalation"] == "STEP-UP", nxt
    assert nxt["counters"]["financial"] == fin_step + per, nxt
    # honesty: each individual charge was UNDER the per-action GLOVES trigger
    assert per < _PER_ACTION_GLOVES_TRIGGER
    # ...and the sum that tripped exceeds the committed session threshold (κ=1 fact)
    assert nxt["counters"]["financial"] > fin_step, nxt

    # ---- (b) DELETE BURST past the destruction threshold -> HALT.
    g = ComposeAuthGate(store_path=None)
    dest_halt = POLICY.THRESHOLDS["destruction"]["halt"]   # 25
    out = None
    for _ in range(dest_halt + 1):       # 26 single-op deletes -> running 26 > 25
        out = g.decide(_delete())
    assert out["decision"] == "HALT", out
    assert out["counters"]["destruction"] > dest_halt, out

    # ---- (c) a single small legitimate action -> OK (NO false halt).
    g = ComposeAuthGate(store_path=None)
    out = g.decide(_charge(5))           # $5, well under everything
    assert out["decision"] == "OK" and out["tier_escalation"] is None, out
    assert out["tripped"] == [], out

    # ---- (d) PERSISTENCE: counters survive a simulated session-restart (crash-resume).
    tmpdir = tempfile.mkdtemp(prefix="composeauth_persist_")
    path = os.path.join(tmpdir, "budget.json")
    g1 = ComposeAuthGate(store_path=path)
    for _ in range(4):                    # 4 x $20 = $80, under step_up=100 -> OK
        r = g1.decide(_charge(20))
    assert r["decision"] == "OK" and g1.store.counters["financial"] == 80, r
    del g1                                # simulate a CRASH (object gone)
    g2 = ComposeAuthGate(store_path=path) # RESUME from the persisted store
    assert g2.store.counters["financial"] == 80, g2.store.counters
    # the resumed budget is NOT reset: 2 more $20 charges -> $120 > 100 -> ESCALATE.
    r = g2.decide(_charge(20))            # 100, == threshold, not yet >
    assert r["decision"] == "OK", r
    r = g2.decide(_charge(20))            # 120 > 100 -> ESCALATE
    assert r["decision"] == "ESCALATE", r
    assert r["counters"]["financial"] == 120, r

    # ---- (e) EFFECT IN AN UNTRACKED CLASS -> reported UNCOVERED, never "within budget".
    g = ComposeAuthGate(store_path=None)
    # an unknown tool whose entire blast is outside the enumerated classes
    out = g.decide({"tool_id": "psyops.influence", "params": {"targets": 9},
                    "blast_units": 9, "other_effects": {"reputation_harm": 9}})
    assert out["uncovered"], out                 # something WAS flagged uncovered
    assert out["decision"] == "OK", out          # nothing tracked tripped...
    # ...but the reason makes the uncovered blast explicit (no silent within-budget)
    assert "UNCOVERED" in out["reason"], out
    # and a KNOWN tool carrying a novel blast type in other_effects is ALSO surfaced
    out2 = g.decide({"tool_id": "fs.overwrite", "params": {"path": "/p"},
                     "other_effects": {"legal_exposure": 3}})
    assert out2["uncovered"].get("legal_exposure") == 3, out2

    # ---- (extra) FAIL CLOSED: a non-dict ledger entry -> HALT, never OK.
    g = ComposeAuthGate(store_path=None)
    out = g.decide(12345)
    assert out["decision"] == "HALT" and "FAIL-CLOSED" in out["reason"], out

    # ---- (extra) every verdict carries the POLICY banner (thresholds = policy not truth)
    g = ComposeAuthGate(store_path=None)
    out = g.decide(_charge(1))
    assert "POLICY" in out["policy_banner"] and "NOT derived truth" in out["policy_banner"], out
    # and every verdict reports WHICH classes are tracked (the rest is uncovered)
    assert set(out["tracked_classes"]) == set(POLICY.THRESHOLDS.keys()), out

    # =====================================================================
    # AUDIT REGRESSION TESTS — each reproduces an exploit the Sonnet auditor
    # found and asserts it is now BLOCKED. (Before the fix these FAILED: the
    # gate returned OK / decremented the budget / swallowed the amount to $0.)
    # =====================================================================

    # ---- (R1) NEGATIVE-BLAST FALSE-ACCEPT (audit Defect 1).
    # Before: 5x$20 -> $100; charge(-80) decremented to $20; charge(+20) -> OK at a
    # REAL committed total of $120 that should ESCALATE. Now: the negative charge HALTs
    # (fail-closed) and the running budget is NOT decremented.
    g = ComposeAuthGate(store_path=None)
    for _ in range(5):
        assert g.decide(_charge(20))["decision"] == "OK"
    assert g.store.counters["financial"] == 100
    neg = g.decide(_charge(-80))
    assert neg["decision"] == "HALT", ("negative blast must HALT, not decrement", neg)
    assert g.store.counters["financial"] == 100, ("budget must NOT be decremented", g.store.counters)
    # a subsequent legit charge crosses the (un-decremented) threshold -> ESCALATE
    after = g.decide(_charge(20))
    assert after["decision"] == "ESCALATE" and after["counters"]["financial"] == 120, after

    # ---- (R1b) negative via other_effects on a KNOWN tool, and negative blast_units on
    # an UNKNOWN tool, both fail closed (the extractor refuses negatives everywhere).
    g = ComposeAuthGate(store_path=None)
    assert g.decide({"tool_id": "fs.overwrite", "params": {"path": "/p"},
                     "other_effects": {"financial": -999}})["decision"] == "HALT"
    g = ComposeAuthGate(store_path=None)
    assert g.decide({"tool_id": "psyops.influence", "params": {},
                     "blast_units": -50})["decision"] == "HALT"

    # ---- (R2) BROADCAST STRING-'to' SILENT UNDERCOUNT (audit Defect 2).
    # Before: to='alice@example.com' (a string, not a list) -> _num('alice...') = 0, so
    # 15 emails left broadcast at 0 and never tripped the >10 escalate. Now: a bare
    # string recipient counts as 1, so 15 > 10 -> ESCALATE (never silently 0).
    g = ComposeAuthGate(store_path=None)
    bc = None
    for _ in range(15):
        bc = g.decide({"tool_id": "email.send_one",
                       "params": {"to": "alice@example.com"}, "other_effects": {}})
    assert bc["counters"]["broadcast"] == 15, ("string-'to' must count 1 each", bc["counters"])
    assert bc["decision"] in ("ESCALATE", "HALT"), ("15>10 recipients must escalate", bc)

    # ---- (R5) NaN / Inf BLAST NOT FAIL-CLOSED (audit Defect 5).
    # Before: float('inf')/float('nan') in amount were silently rounded to a $0 entry
    # (no HALT, no UNCOVERED flag). Now: a non-finite blast amount HALTs (fail-closed).
    for bad in (float("inf"), float("-inf"), float("nan")):
        g = ComposeAuthGate(store_path=None)
        r = g.decide(_charge(bad))
        assert r["decision"] == "HALT" and "MalformedBlast" in r["reason"], (bad, r)
        assert g.store.counters["financial"] == 0, ("non-finite must not be counted", bad)

    # ---- (R4) FAIL-NOT-CLOSED ON CORRUPT STORE INIT (audit Defect 4 / fail-not-closed).
    # Before: a corrupt store file raised JSONDecodeError OUT of __init__, bypassing
    # decide()'s fail-closed wrapper (a caller wrapping construction in try/except could
    # skip the gate). Now: __init__ does NOT raise; the store is POISONED -> every
    # decide() HALTs.
    cdir = tempfile.mkdtemp(prefix="composeauth_corrupt_")
    cpath = os.path.join(cdir, "budget.json")
    with open(cpath, "w") as fh:
        fh.write("{ not valid json ")
    g = ComposeAuthGate(store_path=cpath)            # must NOT raise
    cv = g.decide(_charge(5))
    assert cv["decision"] == "HALT" and "poisoned" in cv["reason"], cv

    # ---- (R4b) a TAMPERED negative persisted counter must not resume a 'spent-down'
    # budget — it poisons the store -> HALT (not a silent resume below threshold).
    tpath = os.path.join(cdir, "tampered.json")
    with open(tpath, "w") as fh:
        fh.write('{"counters": {"financial": -500}, "n_actions": 1}')
    g = ComposeAuthGate(store_path=tpath)
    assert g.decide(_charge(5))["decision"] == "HALT"

    print("composeauth_gate selftest: PASS (a SALAMI: 5x$20 each<$50 per-action bar & "
          "<$100 session, 6th ESCALATE; b delete-burst 26>25 HALT; c single $5 OK no-false-halt; "
          "d crash-resume budget NOT reset $80->resume->$120 ESCALATE; e untracked class -> "
          "UNCOVERED not silent; +fail-closed on bad entry; +policy banner on every verdict; "
          "+AUDIT-REGRESSIONS: R1 negative-blast HALTs & does NOT decrement (false-accept fixed); "
          "R2 string-'to' counts 1 each so 15>10 ESCALATEs (no silent undercount); R5 NaN/Inf "
          "HALT not silent-$0; R4 corrupt/tampered store -> construct-OK + every decide HALTs)")


if __name__ == "__main__":
    _selftest()
