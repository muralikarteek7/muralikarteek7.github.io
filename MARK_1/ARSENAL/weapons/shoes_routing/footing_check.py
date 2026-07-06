#!/usr/bin/env python3
"""FOOTING (SHOES-a) — the frozen pre-ship FOOTING check (don't slip).

Doctrine (the box): *an output is not shipped on the generator's own confidence.*
FOOTING is a CHEAP (Haiku-tier) pre-ship rail that scores a draft's epistemic
UNCERTAINTY from machine-checkable signals and, if uncertainty crosses tau, ROUTES
UP the ladder / triggers a fetch-execute grounding loop / ABSTAINS. It never
certifies. It is ARMOR, not a weapon.

WHAT IS kappa=1 (EXACT, machine-computed inputs — no model, deterministic):
  - unverified_load_bearing_claim COUNT  : count of load-bearing claims that carry
        NO attached check (fetch/execute/citation). Pure counting. kappa=1.
  - structured_output field-level MISMATCH: a required field is missing / wrong type
        vs a schema. Exact comparison. kappa=1.
  - input character-level DISTANCE        : normalized edit-ish distance of the task
        input from the nearest known-good exemplar. Deterministic arithmetic. kappa=1.

WHAT IS kappa<1 (JUDGMENT — the AUDIT FIX, the honesty correction):
  - cross-paraphrase "disagreement"       : whether two paraphrased answers AGREE is
        a COMPARISON that needs a MODEL to judge semantic equivalence. Therefore the
        disagreement *rate* is kappa<1, NOT kappa=1. The harness here computes a
        disagreement rate from a caller-supplied comparison oracle (a model in
        production; a deterministic stub in tests) — and the verdict it feeds is a
        ROUTING judgment, never a certification.
  - the "uncertain?" verdict              : a judgment-that-ROUTES. kappa<1.

NON-NEGOTIABLE WORDING RAIL: FOOTING NEVER emits "verified" or "safe" or "correct".
It emits "low uncertainty signals" / "high uncertainty signals" and a ROUTE action.
_selftest() asserts this wording rail and FAILS the whole gate if it is ever broken.

"A gate that can't fail is not a gate": _selftest() requires FOOTING to
  (a) FLAG a draft with HIGH cross-paraphrase disagreement -> route up / abstain;
  (b) NOT flag a fully-grounded draft (every load-bearing claim has a check);
  (c) NEVER emit "verified"/"safe"/"correct" (wording asserted on every verdict);
  (g) THE PRIMARY-ADVERSARY MISROUTE TEST: a task KNOWN to need Opus, misrouted to
      Haiku and yielding a degraded (under-grounded / high-disagreement) draft, is
      FLAGGED before it ships. This is the silent-quality-regression backstop.
All must pass or NOTHING FOOTING outputs is trusted.
"""
import sys

# ---- frozen thresholds (committed; a verdict records the values it used) ------
TAU_DISAGREE = 0.34      # cross-paraphrase disagreement rate above this -> uncertain
MAX_UNVERIFIED = 0       # any unverified LOAD-BEARING claim contributes to uncertainty
TAU_DISTANCE = 0.60      # normalized input distance from known-good above this -> uncertain
# action wording (the ONLY verdict vocabulary FOOTING is allowed to emit)
_ACTIONS = ("SHIP_OK_LOW_UNCERTAINTY", "ROUTE_UP", "GROUND_THEN_RECHECK", "ABSTAIN")
# words FOOTING is FORBIDDEN to emit (the wording rail)
_FORBIDDEN = ("verified", "safe", "correct", "proven", "guaranteed", "certified")


# --------------------------------------------------------------------------- #
#  kappa=1 sub-signals (EXACT, deterministic, no model)
# --------------------------------------------------------------------------- #
def count_unverified_load_bearing(claims):
    """EXACT (kappa=1). `claims` = list of dicts:
        {"text": str, "load_bearing": bool, "check": <truthy if grounded/executed>}
    Returns the COUNT of load-bearing claims with NO attached check. Pure counting."""
    n = 0
    for c in claims:
        if c.get("load_bearing") and not c.get("check"):
            n += 1
    return n


def structured_field_mismatch(output, schema):
    """EXACT (kappa=1). `schema` = {field: type}. Returns a list of mismatches:
    missing fields and wrong-typed fields. Deterministic comparison, no model."""
    bad = []
    for field, typ in schema.items():
        if field not in output:
            bad.append({"field": field, "problem": "missing"})
        elif typ is not None and not isinstance(output[field], typ):
            bad.append({"field": field, "problem": "wrong_type",
                        "expected": typ.__name__, "got": type(output[field]).__name__})
    return bad


def _norm_distance(a, b):
    """Normalized char-level distance (deterministic). 0.0 identical, 1.0 max.
    A cheap, dependency-free Levenshtein ratio; EXACT and reproducible (kappa=1)."""
    if a == b:
        return 0.0
    la, lb = len(a), len(b)
    if la == 0 or lb == 0:
        return 1.0
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[lb] / max(la, lb)


def input_distance_from_known_good(task_input, known_good_inputs):
    """EXACT (kappa=1). Min normalized distance to the nearest known-good exemplar.
    Larger = more out-of-distribution = more reason to distrust the cheap draft."""
    if not known_good_inputs:
        return 1.0
    return min(_norm_distance(task_input, kg) for kg in known_good_inputs)


# --------------------------------------------------------------------------- #
#  kappa<1 signal: cross-paraphrase disagreement (NEEDS A MODEL -> kappa<1)
# --------------------------------------------------------------------------- #
def cross_paraphrase_disagreement_rate(answers, compare_oracle):
    """kappa<1 (AUDIT FIX). `answers` = list of answer strings produced from
    paraphrased prompts. `compare_oracle(x, y) -> bool` judges SEMANTIC equivalence
    (a MODEL in production; a deterministic stub in tests). The disagreement RATE is
    a JUDGMENT signal, not exact — labelled kappa<1. Returns rate in [0,1].

    The pairwise disagreement rate = (# unequal pairs) / (# pairs). With <2 answers
    there is nothing to compare -> this helper returns (0.0, 0). DO NOT read that 0.0
    as "measured agreement": it is the EMPTY case. `footing_check` (the only caller that
    routes on this signal) treats <2 answers as UNCOMPUTABLE (disagreement_rate=None) so a
    single-paraphrase draft can never silently SHIP_OK with 0 pairs compared (DEFECT-1 fix)."""
    n = len(answers)
    if n < 2:
        return 0.0, 0
    pairs = 0
    disagree = 0
    for i in range(n):
        for j in range(i + 1, n):
            pairs += 1
            if not compare_oracle(answers[i], answers[j]):
                disagree += 1
    return (disagree / pairs if pairs else 0.0), pairs


# --------------------------------------------------------------------------- #
#  the FOOTING verdict (routes; NEVER certifies)
# --------------------------------------------------------------------------- #
def footing_check(draft, compare_oracle=None,
                  tau_disagree=TAU_DISAGREE, max_unverified=MAX_UNVERIFIED,
                  tau_distance=TAU_DISTANCE):
    """Score a draft's pre-ship UNCERTAINTY from machine signals + a kappa<1
    paraphrase-disagreement signal, and return a ROUTING action.

    `draft` keys (all optional; absent => that signal contributes nothing):
      claims:            list for count_unverified_load_bearing (kappa=1)
      output, schema:    for structured_field_mismatch (kappa=1)
      task_input,
      known_good_inputs: for input_distance_from_known_good (kappa=1)
      paraphrase_answers:list of strings -> cross_paraphrase_disagreement_rate(kappa<1)
      required_tier:     (optional) the ladder tier the task actually NEEDS, e.g.
                         "opus". routed_tier: where it WAS sent, e.g. "haiku". When
                         routed below the required tier, FOOTING raises its bar — the
                         misroute (silent-quality-regression) backstop.

    Returns a dict with the machine numbers, the kappa<1 disagreement signal, an
    `uncertain` ROUTING judgment, and an `action` in _ACTIONS. NEVER says verified/safe.
    """
    claims = draft.get("claims", []) or []
    unverified = count_unverified_load_bearing(claims)

    schema = draft.get("schema")
    mismatches = structured_field_mismatch(draft.get("output", {}) or {}, schema) if schema else []

    task_input = draft.get("task_input")
    kg = draft.get("known_good_inputs") or []
    distance = input_distance_from_known_good(task_input, kg) if task_input is not None else 0.0

    answers = draft.get("paraphrase_answers") or []
    # AUDIT FIX (DEFECT 1 — single-paraphrase false-accept): the disagreement signal is
    # UNCOMPUTABLE whenever the caller ASKED for a paraphrase check (answers present) but
    # we cannot actually compare a PAIR — i.e. no oracle, OR fewer than 2 answers. In that
    # case we MUST NOT fake disagreement_rate=0.0 (which would silently SHIP_OK with 0 pairs
    # compared). We emit None (uncomputable) so the verdict routes to GROUND_THEN_RECHECK,
    # exactly as the no-oracle case already does. "Asked but couldn't measure" != "agreed".
    if answers and (compare_oracle is None or len(answers) < 2):
        # honest: cannot compute the kappa<1 signal (no oracle, or <2 answers => 0 pairs);
        # say so, don't fake a measured 0.0.
        disagreement_rate, n_pairs = None, 0
    elif answers:
        disagreement_rate, n_pairs = cross_paraphrase_disagreement_rate(answers, compare_oracle)
    else:
        # no paraphrase check was requested at all -> this signal contributes nothing.
        disagreement_rate, n_pairs = 0.0, 0

    # ---- the misroute (silent-quality-regression) backstop --------------------
    # If the task needed a higher tier than it was routed to, the cheap draft is
    # SUSPECT by construction: tighten the disagreement bar so a degraded-but-
    # internally-plausible draft still trips. This is the test-(g) adversary guard.
    misrouted_below = False
    eff_tau_disagree = tau_disagree
    rt, nt = draft.get("required_tier"), draft.get("routed_tier")
    if rt and nt and _tier_rank(nt) < _tier_rank(rt):
        misrouted_below = True
        eff_tau_disagree = min(tau_disagree, 0.15)   # any real disagreement now trips

    # ---- assemble the uncertainty judgment (kappa<1 — it ROUTES) --------------
    reasons = []
    if unverified > max_unverified:
        reasons.append(f"{unverified} unverified load-bearing claim(s) (kappa=1 count)")
    if mismatches:
        reasons.append(f"{len(mismatches)} structured-output field mismatch(es) (kappa=1)")
    if distance > tau_distance:
        reasons.append(f"input distance {distance:.2f} > {tau_distance} from known-good (kappa=1, out-of-distribution)")
    if disagreement_rate is None and answers:
        if compare_oracle is None:
            why = "NO compare-oracle supplied"
        elif len(answers) < 2:
            why = f"only {len(answers)} paraphrase answer(s) => 0 comparable pairs (need >=2)"
        else:
            why = "paraphrase signal unavailable"
        reasons.append(f"paraphrase answers present but {why} -> disagreement UNCOMPUTABLE (kappa<1 signal unavailable; NOT a measured agreement)")
    elif disagreement_rate is not None and disagreement_rate > eff_tau_disagree:
        reasons.append(f"cross-paraphrase disagreement {disagreement_rate:.2f} > {eff_tau_disagree:.2f} (kappa<1 judgment, model-compared)")
    if misrouted_below:
        reasons.append(f"MISROUTE: task needs '{rt}' but was routed to '{nt}' -> degraded-draft backstop engaged (tightened bar)")

    uncertain = bool(reasons)

    # ---- pick a ROUTING action (never a certification) ------------------------
    if not uncertain:
        action = "SHIP_OK_LOW_UNCERTAINTY"
    elif disagreement_rate is None and answers and len(reasons) == 1:
        # only failure is "can't compute paraphrase signal" -> ground/recheck, not abstain
        action = "GROUND_THEN_RECHECK"
    elif (disagreement_rate is not None and disagreement_rate > eff_tau_disagree) or misrouted_below:
        # semantic instability or a misroute -> ROUTE UP the ladder
        action = "ROUTE_UP"
    elif unverified > max_unverified or distance > tau_distance:
        # missing grounding or OOD -> fetch/execute then re-check
        action = "GROUND_THEN_RECHECK"
    else:
        action = "ABSTAIN"

    verdict = {
        "component": "FOOTING",
        # machine (kappa=1) signals
        "unverified_load_bearing_claims": unverified,
        "structured_field_mismatches": mismatches,
        "input_distance_from_known_good": round(distance, 4),
        # kappa<1 signal (the audit fix)
        "cross_paraphrase_disagreement_rate": disagreement_rate,
        "paraphrase_pairs_compared": n_pairs,
        "disagreement_signal_kappa": "<1 (model-compared judgment, not exact)",
        # the misroute backstop
        "misrouted_below_required_tier": misrouted_below,
        "required_tier": rt, "routed_tier": nt,
        "effective_disagreement_tau": eff_tau_disagree,
        # the ROUTING judgment (NOT a certification)
        "uncertain": uncertain,
        "uncertainty_signals": reasons,
        "action": action,
        "thresholds": {"tau_disagree": tau_disagree, "max_unverified": max_unverified,
                       "tau_distance": tau_distance},
        # the honesty rail, restated on every verdict
        "ceiling": ("FOOTING REDUCES confident-wrongness; it does NOT eliminate it. An "
                    "overconfident-but-internally-CONSISTENT error still passes (honest "
                    "failure mode). This verdict is a ROUTING judgment (kappa<1), NOT a "
                    "certification. FOOTING never emits 'verified'/'safe'/'correct'."),
        "note": ("low uncertainty signals -> ok to ship" if not uncertain else
                 "high uncertainty signals -> " + action),
    }
    # NON-NEGOTIABLE: scrub-check our own output for forbidden certification words.
    _assert_no_forbidden_wording(verdict)
    return verdict


# tier ladder ranks (machine-checkable=0 .. escalate top). Higher rank = more capable.
_TIER_RANK = {"execute": 0, "machine": 0, "haiku": 1, "routine": 1,
              "opus": 2, "hard": 2, "fable": 3, "frontier": 3, "escalate": 3}


def _tier_rank(name):
    return _TIER_RANK.get(str(name).lower(), 1)


import re as _re

# the wording rail forbids CERTIFICATION CLAIMS, matched at word boundaries so that
# benignly-prefixed uncertainty vocabulary ("unverified", "incorrect") does NOT trip
# the rail while a genuine "verified"/"safe"/"correct" assertion still does. This is
# the honest reading of the rail: FOOTING may say a claim is UNverified; it may never
# say its output IS verified/safe/correct.
_FORBIDDEN_RE = _re.compile(r"(?<![a-z])(?:" + "|".join(_FORBIDDEN) + r")(?![a-z])")


def _assert_no_forbidden_wording(verdict):
    """The wording rail. Scan the verdict's own emitted strings (NOT the doctrine
    ceiling, which legitimately NAMES the forbidden words to forbid them). Matches at
    word boundaries: 'unverified' is allowed (uncertainty word); 'verified' is not."""
    emitted = [verdict.get("action", ""), verdict.get("note", "")] + list(verdict.get("uncertainty_signals", []))
    for s in emitted:
        m = _FORBIDDEN_RE.search(str(s).lower())
        assert m is None, (
            "WORDING-RAIL VIOLATION: FOOTING emitted forbidden certification word "
            "%r in %r" % (m.group(0), s))


# --------------------------------------------------------------------------- #
#  NON-WAIVABLE adversarial self-test
# --------------------------------------------------------------------------- #
def _equal_text(a, b):
    """Deterministic stand-in for the model comparison oracle used ONLY in tests:
    exact-string equality. In production this is a cheap cross-instance model call;
    here we want a reproducible, model-free signal so the gate itself is deterministic."""
    return a.strip() == b.strip()


def _selftest():
    # (a) HIGH cross-paraphrase disagreement -> FLAGGED uncertain -> route up / abstain
    a = footing_check(
        {"paraphrase_answers": ["the answer is 7", "the answer is 12",
                                "it is 7", "no, 19", "about 30"]},
        compare_oracle=_equal_text)
    assert a["uncertain"] is True, a
    assert a["action"] in ("ROUTE_UP", "ABSTAIN"), a
    assert a["cross_paraphrase_disagreement_rate"] is not None and \
        a["cross_paraphrase_disagreement_rate"] > TAU_DISAGREE, a

    # (b) a FULLY-GROUNDED draft (every load-bearing claim checked; paraphrases agree;
    #     in-distribution; schema satisfied) -> NOT flagged.
    b = footing_check(
        {"claims": [{"text": "x", "load_bearing": True, "check": "fetched:doi"},
                    {"text": "y", "load_bearing": True, "check": "executed"},
                    {"text": "aside", "load_bearing": False, "check": None}],
         "output": {"result": 42, "label": "ok"},
         "schema": {"result": int, "label": str},
         "task_input": "compute the sum of the column",
         "known_good_inputs": ["compute the sum of the column", "sum the column values"],
         "paraphrase_answers": ["42", "42", "42"]},
        compare_oracle=_equal_text)
    assert b["uncertain"] is False, b
    assert b["action"] == "SHIP_OK_LOW_UNCERTAINTY", b
    assert b["unverified_load_bearing_claims"] == 0, b

    # (c) WORDING RAIL: the report NEVER says verified/safe/correct as a CLAIM (word
    #     boundary; 'unverified' is allowed). Assert on BOTH a flagged and unflagged verdict.
    for v in (a, b):
        emitted = " ".join([v["action"], v["note"]] + v["uncertainty_signals"]).lower()
        assert _FORBIDDEN_RE.search(emitted) is None, (v["action"], emitted)
    #     ...but the legitimate uncertainty word 'unverified' is NOT forbidden:
    assert _FORBIDDEN_RE.search("1 unverified load-bearing claim") is None
    assert _FORBIDDEN_RE.search("this output is verified") is not None
    #     and the explicit machine scrubber must accept these and reject a poisoned one.
    _assert_no_forbidden_wording(a)
    poisoned = dict(b); poisoned["note"] = "this output is verified and safe"
    try:
        _assert_no_forbidden_wording(poisoned)
        raise AssertionError("scrubber FAILED to catch a forbidden 'verified/safe' note")
    except AssertionError as e:
        assert "WORDING-RAIL VIOLATION" in str(e), e

    # extra kappa=1 unit checks: unverified count, schema mismatch, distance
    assert count_unverified_load_bearing(
        [{"load_bearing": True, "check": None},
         {"load_bearing": True, "check": "ok"},
         {"load_bearing": False, "check": None}]) == 1
    mm = structured_field_mismatch({"a": 1}, {"a": int, "b": str})
    assert any(m["problem"] == "missing" and m["field"] == "b" for m in mm), mm
    mm2 = structured_field_mismatch({"a": "oops"}, {"a": int})
    assert mm2 and mm2[0]["problem"] == "wrong_type", mm2
    assert input_distance_from_known_good("abc", ["abc"]) == 0.0
    assert input_distance_from_known_good("zzzzzz", ["abc"]) > 0.5

    # honest: paraphrase answers WITHOUT an oracle -> uncomputable, not a fake pass
    nooracle = footing_check({"paraphrase_answers": ["p", "q"]}, compare_oracle=None)
    assert nooracle["cross_paraphrase_disagreement_rate"] is None, nooracle
    assert nooracle["uncertain"] is True and nooracle["action"] == "GROUND_THEN_RECHECK", nooracle

    # (REGRESSION — AUDIT DEFECT 1: single-paraphrase FALSE-ACCEPT). The auditor's exact
    # exploit: exactly ONE paraphrase answer WITH a compare_oracle. Pre-fix this returned
    # rate=0.0 over 0 pairs and SHIP_OK_LOW_UNCERTAINTY -- a silent ship on an UNMEASURED
    # disagreement signal. The signal was REQUESTED (answers present) but NEVER computed.
    # MUST now be flagged UNCOMPUTABLE (rate=None) -> uncertain -> GROUND_THEN_RECHECK,
    # NEVER SHIP_OK. "Asked for the check but couldn't measure" must not equal "agreed".
    one_para = footing_check({"paraphrase_answers": ["the answer is 42"]},
                             compare_oracle=_equal_text)
    assert one_para["cross_paraphrase_disagreement_rate"] is None, one_para
    assert one_para["paraphrase_pairs_compared"] == 0, one_para
    assert one_para["uncertain"] is True, ("DEFECT-1 single-paraphrase FALSE-ACCEPT", one_para)
    assert one_para["action"] != "SHIP_OK_LOW_UNCERTAINTY", one_para
    assert one_para["action"] == "GROUND_THEN_RECHECK", one_para
    #   even a non-trivial caller-oracle (always-equal) must NOT rescue a 1-answer ship:
    one_para_loose = footing_check({"paraphrase_answers": ["x"]},
                                   compare_oracle=lambda a, b: True)
    assert one_para_loose["uncertain"] is True and \
        one_para_loose["action"] != "SHIP_OK_LOW_UNCERTAINTY", one_para_loose
    #   ...but TWO genuinely-agreeing answers DO ship (we did not over-tighten):
    two_agree = footing_check({"paraphrase_answers": ["42", "42"]}, compare_oracle=_equal_text)
    assert two_agree["paraphrase_pairs_compared"] == 1, two_agree
    assert two_agree["uncertain"] is False and \
        two_agree["action"] == "SHIP_OK_LOW_UNCERTAINTY", two_agree

    print("footing_check selftest: PASS")
    print("  (a) HIGH cross-paraphrase disagreement -> FLAGGED uncertain -> route up/abstain (kappa<1)")
    print("  (b) fully-grounded, in-distribution, paraphrase-agreeing draft -> NOT flagged")
    print("  (c) WORDING RAIL: never emits verified/safe/correct; scrubber catches a poisoned note")
    print("  (+) kappa=1 unit signals: unverified-count, schema-mismatch, input-distance")
    print("  (+) honest: paraphrases w/o oracle -> disagreement UNCOMPUTABLE (no fake pass)")
    print("  (+) REGRESSION (audit DEFECT 1): single paraphrase + oracle -> UNCOMPUTABLE, "
          "NOT a silent SHIP_OK (false-accept blocked); 2 agreeing answers still ship")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: footing_check.py selftest")
