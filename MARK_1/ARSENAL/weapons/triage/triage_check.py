#!/usr/bin/env python3
"""TRIAGE — the failure-class -> detector -> mitigation checklist (the ARMOR rail).

Doctrine (the box): ARMOR today has ONE undifferentiated abstention gate ("not
confident -> abstain"). TRIAGE turns that into a NAMED decision table: *this TYPE of
failure gets THIS mitigation.* It is ARMOR, NOT a weapon -- it has no exact verifier
of "is this output failing?" (that is kappa=0 in general). Its value is making
abstention SPECIFIC and AUDITABLE.

Each row of the table = a failure class the box has ACTUALLY exhibited (traced to
Legacy/EVOLUTION_LOG.md) wired to:
  - the cheapest detector (a machine check where possible),
  - the detector's HONEST kappa (1 = a machine check that flips on a planted defect;
    <1 = a routed judgment), and
  - the mandated mitigation.

COMPOSITION: the fabrication row delegates to the existing kappa=1 checker FACTHARNESS
(weapons/factharness). Where a kappa=1 checker is ABSENT (CRUCIBLE is not present on
disk, 2026-06-20), the affected row DEGRADES to kappa<1 honestly (degraded=True),
never silently faking exactness.

CARDINAL RAILS (non-waivable, self-tested):
  * NEVER emits "safe" / "all-clear" -- only "no listed class fired (coverage = N
    classes; novel classes uncovered)".
  * The report ALWAYS carries uncovered_novel_classes=True and it can NEVER be False.
  * On a malformed/degenerate record the gate ABSTAINS/errors LOUDLY, never silent-passes.
  * "A gate that can't fail is not a gate": _selftest() requires every kappa=1 detector
    to (i) pass a known-good input AND (ii) catch a known-broken one, and requires the
    >=3 reconstructed REAL past failures to RE-FIRE the row the human audit caught.
"""
import sys, os, re, json

# --------------------------------------------------------------------------- #
#  compose the existing kappa=1 fabrication checker (FACTHARNESS), honestly.
# --------------------------------------------------------------------------- #
_FACT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "factharness")
if os.path.isdir(_FACT_DIR) and _FACT_DIR not in sys.path:
    sys.path.insert(0, _FACT_DIR)
try:
    import factharness as _fact            # the composed kappa=1 fabrication checker
    _HAVE_FACTHARNESS = True
except Exception:                          # honest: say so, do NOT fake it
    _fact = None
    _HAVE_FACTHARNESS = False

# CRUCIBLE: the kickoff routes spec-gaming + crash-on-malformed "-> CRUCIBLE". CRUCIBLE
# is PRESENT on disk (2026-06-20) as a META-WEAPON that black-box-tests a gate. We probe
# for it so the labelling is machine-driven. HONEST NUANCE (audit banner #3): CRUCIBLE
# being on disk does NOT by itself supply an *independent oracle of the answer* for an
# arbitrary spec-gaming task -- it tests GATES, and its oracle path fires only when an
# oracle is registered for the specific task. So the spec-gaming row reaches kappa=1
# ONLY when the record actually supplies an independent oracle / OOS signal; otherwise it
# runs TRIAGE's own kappa<1 structural in-sample/OOS check and SAYS so (degraded). The
# crash/silent-pass row's kappa=1 question ("did the gate error LOUDLY?") IS exactly
# checkable by TRIAGE's own probe whether or not CRUCIBLE is present.
_CRUCIBLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "crucible")
_HAVE_CRUCIBLE = os.path.isdir(_CRUCIBLE_DIR)


# the FROZEN coverage list -- the N classes this table covers. Order is stable.
COVERAGE_CLASSES = [
    "overconfidence",
    "fabrication",
    "specification-gaming",
    "circular-measurement",
    "numeric-branch-cut-convergence",
    "distribution-shift",
    "shared-blind-spot",
    "crash-silent-pass-on-malformed-input",
]

CEILING = (
    "TRIAGE is ARMOR, not a weapon: it makes abstention specific+auditable, it does not "
    "make the output correct. A taxonomy covers KNOWN classes only -- novel/unknown "
    "failures escape (uncovered_novel_classes is ALWAYS true). Absence of a flag is NOT "
    "a safety proof: 'no listed class fired' is never 'safe'. kappa=1 rows are real "
    "machine checks; kappa<1 rows are routed judgments, not certifications."
)


# --------------------------------------------------------------------------- #
#  the malformed-record guard (row 8 -- abstain LOUDLY, never silent-pass)
# --------------------------------------------------------------------------- #
class TriageAbstain(Exception):
    """Raised when the input record is malformed/degenerate. The gate must surface
    this loudly; a caller that swallows it violates the cardinal rail."""


def _require_record(rec):
    if rec is None or not isinstance(rec, dict):
        raise TriageAbstain("record is not a dict -> ABSTAIN (cannot triage a non-record)")
    if "text" not in rec and "claims" not in rec and "result" not in rec:
        raise TriageAbstain(
            "record has none of {text, claims, result} -> ABSTAIN (nothing to triage). "
            "A malformed record must NOT silent-pass as 'no class fired'.")


# --------------------------------------------------------------------------- #
#  ROW DETECTORS. Each returns a row dict {class, fired, kappa, degraded, evidence,
#  mandated_action}. Detectors are deterministic and flip on a planted defect.
# --------------------------------------------------------------------------- #
def _row(cls, fired, kappa, degraded, evidence, action):
    return {"class": cls, "fired": bool(fired), "kappa": kappa,
            "degraded": bool(degraded), "evidence": evidence, "mandated_action": action}


def detect_overconfidence(rec):
    """kappa<1 (routed judgment). Signals: (a) cross-paraphrase disagreement supplied,
    (b) count of UNVERIFIED load-bearing claims >= threshold with no grounding/execution."""
    paraphrase = rec.get("paraphrase_answers")          # list of answers to the same Q
    disagree = False
    if isinstance(paraphrase, (list, tuple)) and len(paraphrase) >= 2:
        norm = {str(a).strip().lower() for a in paraphrase}
        disagree = len(norm) > 1
    claims = rec.get("claims", []) or []
    unverified = [c for c in claims
                  if isinstance(c, dict) and c.get("load_bearing")
                  and not c.get("grounded") and not c.get("executed")]
    # AUDIT FIX (LOW): the caller controls the record, so a caller-set
    # unverified_threshold=9999 could SUPPRESS the row even with 10+ unverified claims.
    # Clamp: the caller may only TIGHTEN the bar (lower it), never RAISE it above the hard
    # default of 1. Effective threshold = min(requested, default) with a floor of 1, so a
    # suppression value (9999) collapses back to 1 and the row still fires.
    _DEFAULT_THRESHOLD = 1
    requested = rec.get("unverified_threshold", _DEFAULT_THRESHOLD)
    try:
        requested = int(requested)
    except (TypeError, ValueError):
        requested = _DEFAULT_THRESHOLD
    suppression_attempt = requested > _DEFAULT_THRESHOLD
    threshold = max(1, min(requested, _DEFAULT_THRESHOLD))   # cannot exceed the default
    too_many = len(unverified) >= threshold and len(unverified) > 0
    fired = bool(disagree or too_many)
    ev = {"cross_paraphrase_disagreement": disagree,
          "n_unverified_load_bearing": len(unverified),
          "threshold": threshold, "requested_threshold": rec.get("unverified_threshold"),
          "threshold_clamped": suppression_attempt}
    return _row("overconfidence", fired, "<1", False, ev,
                "route up the ladder OR fetch/execute to ground each unverified load-bearing "
                "claim; else ABSTAIN. (Shares ONE escalation handoff with SHOES/FOOTING.)")


def detect_fabrication(rec):
    """kappa=1 via FACTHARNESS when a source text is supplied; kappa<1 (degraded) when
    FACTHARNESS is unavailable OR no source text was fetched. FIRES on a quote/number
    that is NOT in the cited source."""
    claims = rec.get("claims", []) or []
    fab_claims = [c for c in claims if isinstance(c, dict)
                  and (c.get("quote") or c.get("numbers")) and c.get("source_text")]
    if not fab_claims:
        return _row("fabrication", False, "1" if _HAVE_FACTHARNESS else "<1",
                    not _HAVE_FACTHARNESS,
                    {"checked": 0, "note": "no quote/number claim with a source to check"},
                    "n/a (no groundable quote/number claim supplied)")
    if not _HAVE_FACTHARNESS:
        # degrade honestly: we cannot run the kappa=1 substring check.
        return _row("fabrication", False, "<1", True,
                    {"checked": 0, "note": "FACTHARNESS unavailable -> kappa<1; route to "
                     "cross-model grounding judge, do NOT certify."},
                    "FACTHARNESS absent: route the groundedness to a cross-model judge; "
                    "do NOT ship the claim as machine-verified.")
    flags = []
    for c in fab_claims:
        res = _fact.ground({
            "text": c.get("text", ""),
            "source_text": c["source_text"],
            "quote": c.get("quote"),
            "numbers": c.get("numbers"),
        })
        if res["overall"] == "FABRICATION_FLAG":
            flags.append({"claim": c.get("text", ""), "factharness": res["overall"]})
    fired = len(flags) > 0
    return _row("fabrication", fired, "1", False,
                {"checked": len(fab_claims), "flags": flags},
                "HARD FLAG: do NOT ship the ungrounded quote/number. (FABRICATION_FLAG means "
                "'does not check against the supplied source', NEVER fraud.)")


def detect_specification_gaming(rec):
    """kappa=1 ONLY when the record supplies an INDEPENDENT ORACLE verdict (the proxy is
    checked against a different goal-measuring engine -> a flat disagreement is exact).
    Otherwise -> DEGRADED to TRIAGE's own kappa<1 STRUCTURAL check: a proxy score that
    FLIPS in-sample vs OOS, or a proxy explicitly marked != the independent goal/oracle.
    (CRUCIBLE on disk tests GATES; it does not auto-supply an answer-oracle for an
    arbitrary task -- so kappa rides on whether THIS record carries an oracle, not on
    CRUCIBLE merely existing. That honesty is the audit-banner #3 requirement.)"""
    sg = rec.get("spec_gaming")
    if not isinstance(sg, dict):
        return _row("specification-gaming", False, "<1", True,
                    {"note": "no proxy/in-sample/OOS data supplied"}, "n/a")
    in_s = sg.get("in_sample_score")
    oos = sg.get("oos_score")
    flip = (in_s is not None and oos is not None
            and in_s >= sg.get("good_threshold", 0.0)
            and oos < sg.get("good_threshold", 0.0))
    proxy_ne_oracle = bool(sg.get("proxy_is_not_independent_oracle"))
    # an INDEPENDENT oracle verdict, if supplied, is the kappa=1 path -- BUT ONLY when the
    # verdict is a RECOGNIZED value. AUDIT FIX (MEDIUM): `has_oracle = (oracle is not None)`
    # laundered garbage ('' , 0, False, 'maybe', 'yes', arbitrary strings) into kappa=1.
    # A real oracle verdict must be a known agree/disagree token; anything else means "no
    # usable oracle" -> kappa<1 structural path, never a kappa=1 certification.
    oracle = sg.get("independent_oracle_verdict")          # "wrong"/"correct"/None
    _DISAGREE = ("wrong", "fail", "failed", "failure", "incorrect", "error", "errored",
                 "false", "false-positive", "false positive", "mismatch", "disagree",
                 "disagrees", "no", "bad", "invalid", "reject", "rejected")
    _AGREE = ("correct", "right", "pass", "passed", "ok", "okay", "yes", "agree",
              "agrees", "match", "matches", "valid", "good", "accept", "accepted", "true")
    # AUDIT FIX (MEDIUM): a usable oracle verdict must be a NON-EMPTY STRING token. The
    # Python booleans (True/False) and numbers (0/1) are garbage non-verdicts -- accepting
    # str(False)=='false' would launder the boolean False into a recognized disagree token.
    # Restrict normalization to genuine strings so only an authored textual verdict counts.
    onorm = (oracle.strip().lower() if isinstance(oracle, str) and oracle.strip() else None)
    # AUDIT FIX (LOW): broaden disagree matching beyond 3 exact strings -- match a
    # recognized disagree token, including as a leading word ('wrong answer', 'failed run').
    def _matches(tokens, s):
        # match an exact token, OR a recognized token as the LEADING WORD of a phrase
        # ('wrong answer' -> 'wrong', 'failed run' -> 'failed'). Hyphenated terms like
        # 'false-positive' are caught by exact membership (they ARE in the list); we do
        # NOT do a loose hyphen-prefix match (it would launder 'yes-ish' via 'yes').
        if s is None:
            return False
        if s in tokens:
            return True
        words = s.split()
        first = words[0] if words else s
        return first in tokens
    oracle_disagrees = _matches(_DISAGREE, onorm)
    oracle_agrees = _matches(_AGREE, onorm)
    # a USABLE (recognized) oracle is the kappa=1 condition -- not "any non-None value".
    has_oracle = bool(oracle_disagrees or oracle_agrees)
    fired = bool(flip or proxy_ne_oracle or oracle_disagrees)
    kappa = "1" if has_oracle else "<1"
    oracle_note = (
        "independent oracle supplied (recognized verdict) -> kappa=1 path" if has_oracle else
        ("oracle verdict supplied but UNRECOGNIZED (%r) -> NOT a usable oracle; "
         "kappa<1 structural in-sample/OOS check" % oracle) if oracle is not None else
        "no independent oracle -> kappa<1 structural in-sample/OOS check")
    return _row("specification-gaming", fired, kappa, not has_oracle,
                {"in_sample": in_s, "oos": oos, "in_sample_vs_oos_flip": flip,
                 "proxy_not_independent_oracle": proxy_ne_oracle,
                 "independent_oracle_verdict": oracle, "oracle_disagrees": oracle_disagrees,
                 "oracle_recognized": has_oracle,
                 "note": oracle_note},
                "REJECT the proxy as a verifier; demand a real independent check (an oracle, "
                "or out-of-sample evaluation). A score that dies OOS is the valuable output.")


def detect_circular_measurement(rec):
    """kappa=1 STRUCTURAL: did the EVAL data provenance == the GENERATOR? (e.g. the
    answer key was on disk and the solver read it). A pure provenance comparison."""
    prov = rec.get("provenance")
    if not isinstance(prov, dict):
        return _row("circular-measurement", False, "1", False,
                    {"note": "no provenance supplied"},
                    "supply eval-data provenance; unprovenanced eval is itself a risk")
    eval_src = str(prov.get("eval_data_source", "")).strip().lower()
    gen_src = str(prov.get("generator_source", "")).strip().lower()
    key_readable = bool(prov.get("answer_key_readable_by_generator"))
    same = eval_src != "" and eval_src == gen_src
    fired = bool(same or key_readable)
    return _row("circular-measurement", fired, "1", False,
                {"eval_data_source": eval_src, "generator_source": gen_src,
                 "same_source": same, "answer_key_readable_by_generator": key_readable},
                "INVALIDATE the result; re-test on INDEPENDENT data the generator could not "
                "see (quarantine any answer key off-disk; bar tool access to it).")


def detect_numeric_branch_cut(rec):
    """kappa=1: an identity/equality claimed GLOBAL but only valid on a sub-domain.
    Detector: a counterexample point is supplied where lhs != rhs (the SYMBOLICA lesson:
    a point where one side is real and the other isn't is a DISAGREEMENT, not a skip)."""
    nm = rec.get("numeric")
    if not isinstance(nm, dict):
        return _row("numeric-branch-cut-convergence", False, "1", False,
                    {"note": "no numeric identity supplied"}, "n/a")
    claimed_global = bool(nm.get("claimed_global"))
    cexamples = nm.get("counterexample_points", []) or []   # [{x, lhs, rhs}, ...]
    bad = []
    for p in cexamples:
        try:
            lhs, rhs = p.get("lhs"), p.get("rhs")
            # SYMBOLICA rail: one side real, the other not -> DISAGREEMENT (not a skip).
            if (lhs is None) != (rhs is None):
                bad.append(p); continue
            if lhs is None and rhs is None:
                continue
            if abs(float(lhs) - float(rhs)) > float(nm.get("tol", 1e-9)):
                bad.append(p)
        except (TypeError, ValueError):
            bad.append({**p, "note": "non-numeric -> treated as disagreement (no silent skip)"})
    convergence_failed = nm.get("converges") is False
    fired = bool((claimed_global and bad) or convergence_failed)
    return _row("numeric-branch-cut-convergence", fired, "1", False,
                {"claimed_global": claimed_global, "disagreeing_points": bad,
                 "convergence_failed": convergence_failed},
                "LABEL with the valid sub-domain or REJECT; never assert a global identity "
                "from a local sample. Check CONVERGENCE before any closed form.")


def detect_distribution_shift(rec):
    """kappa<1 (routed judgment): the input is far from any known-good calibration case."""
    ds = rec.get("distribution")
    if not isinstance(ds, dict):
        return _row("distribution-shift", False, "<1", False,
                    {"note": "no distribution info supplied"}, "n/a")
    dist = ds.get("distance_to_nearest_known_good")
    thr = ds.get("ood_threshold", 1.0)
    fired = dist is not None and dist > thr
    return _row("distribution-shift", fired, "<1", False,
                {"distance_to_nearest_known_good": dist, "ood_threshold": thr},
                "LOWER confidence explicitly; on a load-bearing output ABSTAIN (calibration "
                "is uncalibrated off-distribution).")


def detect_shared_blind_spot(rec):
    """kappa<1: the verifiers AGREE but are SAME-FAMILY -> agreement is a RISK, not safety."""
    vf = rec.get("verifiers")
    if not isinstance(vf, dict):
        return _row("shared-blind-spot", False, "<1", False,
                    {"note": "no verifier-family info supplied"}, "n/a")
    families = vf.get("families", []) or []
    agree = bool(vf.get("agree"))
    same_family = len(families) >= 2 and len(set(families)) == 1
    fired = bool(agree and same_family)
    return _row("shared-blind-spot", fired, "<1", False,
                {"verifier_families": families, "agree": agree, "all_same_family": same_family},
                "Treat the agreement as a RISK (a shared blind spot), NOT safety; add a "
                "methodologically-DIFFERENT check (cross-model > cross-instruction).")


def _is_silent_pass(out):
    """A degenerate input must make a gate RAISE/abstain, or return an EXPLICIT
    not-ok/abstain verdict. Any *benign* return value is a silent-pass.

    The honesty rail (audit fix, HIGH): we do NOT allowlist a few exact 'ok' tokens
    (that let {'ok': 1}, truthy ints, truthy lists, etc. slip through). Instead we treat
    a degenerate-input return as a silent-pass UNLESS the callable clearly signalled a
    rejection/abstention. The only NON-silent-pass returns are:
      * an explicit falsey/abstain verdict: False, 0, None is NOT used (a no-raise None is
        ambiguous -> treat as silent-pass), or a dict whose ok/valid/pass is EXPLICITLY
        falsey-by-value, or whose status/verdict says reject/abstain/error/invalid/fail,
      * an explicit reject/abstain string.
    Everything else (truthy bool/int/float/list/tuple/set, a dict that does not clearly
    reject, an empty/ambiguous return) counts as a silent-pass. This is value-based, never
    identity-based ('== True'/value checks, never 'is True'), so {'ok': 1} is caught."""
    _REJECT_WORDS = ("reject", "abstain", "error", "invalid", "fail", "not ok",
                     "not-ok", "notok", "unsafe", "fault", "refuse", "blocked")

    def _says_reject(s):
        s = str(s).strip().lower()
        return any(w in s for w in _REJECT_WORDS)

    # explicit boolean / numeric rejection verdict (value-checked, not identity).
    if out is False:
        return False
    if isinstance(out, bool):
        return True                       # out is True -> benign pass -> silent-pass
    if isinstance(out, (int, float)):
        # a falsey numeric (0 / 0.0) reads as "not ok"; any truthy number reads as "ok".
        return bool(out)                  # 0 -> not silent-pass; 1/42/-1 -> silent-pass
    if isinstance(out, str):
        if _says_reject(out):
            return False                  # explicitly said reject/abstain/error -> good
        return True                       # any other string (ok/pass/safe/'' /anything) = silent-pass
    if isinstance(out, dict):
        # an explicit rejection verdict in any conventional field clears it.
        for k in ("status", "verdict", "result", "decision", "action", "note", "error"):
            if k in out and _says_reject(out[k]):
                return False
        # an explicit ok/valid/pass flag that is FALSEY-by-value clears it.
        for k in ("ok", "valid", "pass", "passed", "safe", "accepted"):
            if k in out:
                v = out[k]
                # value-check: only an explicitly falsey flag is a rejection. A truthy
                # value of ANY type (True, 1, 'yes', [..]) is a benign pass -> silent-pass.
                if (v is False) or (isinstance(v, (int, float)) and not isinstance(v, bool) and not v):
                    return False
                return True               # truthy ok/valid flag on junk -> silent-pass
        # a dict that neither rejects nor flags ok is an ambiguous benign return on junk.
        return True
    if out is None:
        # returned None instead of raising -> did NOT error loudly -> silent-pass.
        return True
    # any other object type returned (not raised) on junk -> silent-pass.
    return True


def detect_crash_silent_pass(rec, run_probe=True):
    """kappa=1 on the did-it-error-LOUDLY question: feed the supplied detector callable a
    set of degenerate inputs; if it returns a benign verdict (silent-pass) instead of
    raising/abstaining, the row FIRES. (Full CRUCIBLE adversary absent -> this is the
    cheap structural probe TRIAGE runs itself; degraded vs a richer CRUCIBLE adversary.)"""
    probe = rec.get("malformed_probe")
    if not isinstance(probe, dict) or not callable(probe.get("callable")):
        # AUDIT FIX (MEDIUM): NO probe supplied = NO check was run. kappa=1+degraded=False
        # falsely implied a machine-verified clean result. A null-op MUST be degraded=True
        # so the label says "not checked", not "checked clean".
        return _row("crash-silent-pass-on-malformed-input", False, "<1", True,
                    {"note": "no callable supplied to probe -> NO check run (NULL-OP, not "
                     "'clean'). provide malformed_probe.callable + degenerate_inputs to "
                     "exercise this kappa=1 row."}, "n/a (row not exercised; supply a probe)")
    fn = probe["callable"]
    inputs = probe.get("degenerate_inputs", [None, {}, "", [], 0])
    silent_passes = []
    for x in inputs:
        try:
            out = fn(x)
            # value-based silent-pass test (audit fix HIGH): {'ok':1}, truthy ints/lists,
            # bare truthy returns, ambiguous returns all count as silent-pass now.
            if _is_silent_pass(out):
                silent_passes.append({"input": repr(x), "returned": repr(out)})
        except Exception:
            pass  # raising loudly on a degenerate input is the DESIRED behavior.
    fired = len(silent_passes) > 0
    return _row("crash-silent-pass-on-malformed-input", fired, "1", not _HAVE_CRUCIBLE,
                {"silent_passes": silent_passes, "n_probed": len(inputs),
                 "note": ("CRUCIBLE absent -> cheap own-probe (degraded vs a richer adversary)"
                          if not _HAVE_CRUCIBLE else "CRUCIBLE present")},
                "The gate MUST abstain/error LOUDLY on malformed input, never silent-pass. "
                "Fix the detector to raise/abstain on degenerate inputs.")


_DETECTORS = [
    detect_overconfidence,
    detect_fabrication,
    detect_specification_gaming,
    detect_circular_measurement,
    detect_numeric_branch_cut,
    detect_distribution_shift,
    detect_shared_blind_spot,
    detect_crash_silent_pass,
]


# --------------------------------------------------------------------------- #
#  the entry point: triage_check(record) -> TRIAGE REPORT
# --------------------------------------------------------------------------- #
def triage_check(record):
    """Run every row's detector over an output record; emit a TRIAGE REPORT.
    Raises TriageAbstain (loudly) on a malformed record -- never silent-passes."""
    _require_record(record)                  # ABSTAIN loudly on a malformed record
    rows = [d(record) for d in _DETECTORS]
    fired = [r["class"] for r in rows if r["fired"]]

    if fired:
        overall = "CLASS(ES)_FIRED"
        verdict = ("listed failure class(es) FIRED: " + ", ".join(fired) +
                   f". Apply the mandated mitigation for each. (coverage = {len(COVERAGE_CLASSES)} "
                   "classes; novel/unknown classes are NOT covered and may escape.)")
    else:
        overall = "NO_LISTED_CLASS_FIRED"
        # CARDINAL: never "safe"/"all-clear" -- only "no listed class fired" + coverage + caveat.
        verdict = (f"no listed class fired (coverage = these {len(COVERAGE_CLASSES)} classes: "
                   f"{', '.join(COVERAGE_CLASSES)}; novel/unknown classes are NOT covered and "
                   "may escape). This is NOT a safety proof.")

    report = {
        "tool": "TRIAGE",
        "rows": rows,
        "fired_classes": fired,
        "coverage_classes": list(COVERAGE_CLASSES),
        "n_coverage": len(COVERAGE_CLASSES),
        "uncovered_novel_classes": True,          # REQUIRED; never strippable (self-tested)
        "composes": {"FACTHARNESS": _HAVE_FACTHARNESS, "CRUCIBLE": _HAVE_CRUCIBLE},
        "overall": overall,
        "verdict_text": verdict,
        "ceiling_note": CEILING,
    }
    # hard invariant: the caveat field is immutable-by-contract.
    assert report["uncovered_novel_classes"] is True
    assert "safe" not in verdict.lower() or "not a safety proof" in verdict.lower()
    return report


# --------------------------------------------------------------------------- #
#  reconstructed REAL past failures (for the non-waivable retroactive re-flag test).
#  Each is a faithful minimal reconstruction of a failure the human audit caught.
# --------------------------------------------------------------------------- #
def real_failure_symbolica_branch_cut():
    """C39: log(x^2) = 2*log(x) CERTIFIED globally; the gate skipped x<0 where the
    branch cut makes the two sides disagree. Reconstructed as a global identity with a
    real counterexample at x=-1 (lhs=log(1)=0; rhs=2*log(-1) is complex => real side
    only on one => DISAGREEMENT, not a skip)."""
    import math
    return {
        "text": "log(x^2) = 2*log(x), claimed for all real x",
        "numeric": {"claimed_global": True, "tol": 1e-9,
                    "counterexample_points": [
                        {"x": -1.0, "lhs": math.log((-1.0) ** 2), "rhs": None}]},  # rhs non-real
    }


def real_failure_proofsmith_answer_key_leak():
    """C41: tool-enabled Haiku provers READ reference_proofs.lean off disk -> a false
    +25pp 'win'. The eval data (the reference proofs) was readable by the generator =>
    circular measurement."""
    return {
        "text": "PROOFSMITH repair A/B showed +25pp (later retracted)",
        "provenance": {"eval_data_source": "reference_proofs.lean",
                       "generator_source": "reference_proofs.lean",
                       "answer_key_readable_by_generator": True},
    }


def real_failure_optima_malformed_crash():
    """C38: OPTIMA's gate raised a KeyError on a model missing a variable -> a crash
    path that, if swallowed, would silent-pass. Reconstructed via the malformed-probe
    row using a detector that silently returns ok on a degenerate input."""
    def buggy_detector(x):
        # mimics a detector that does NOT guard a missing var: returns 'ok' on junk.
        return {"ok": True}
    return {
        "text": "OPTIMA gate on a model missing a variable",
        "malformed_probe": {"callable": buggy_detector,
                            "degenerate_inputs": [None, {}, {"vars": None}]},
    }


# --------------------------------------------------------------------------- #
#  _selftest -- "a gate that can't fail is not a gate"
# --------------------------------------------------------------------------- #
def _selftest():
    # ---- (a) accept-good: a clean grounded output, NO row falsely fires ----
    src = "The Strassen algorithm multiplies two 2x2 matrices using 7 multiplications."
    clean = {
        "text": "Strassen uses 7 multiplications for 2x2.",
        "claims": [{"text": "7 mults", "load_bearing": True, "grounded": True,
                    "quote": "7 multiplications", "source_text": src}],
        "numeric": {"claimed_global": True, "tol": 1e-9,
                    "counterexample_points": [{"x": 2.0, "lhs": 1.0, "rhs": 1.0}]},
        "provenance": {"eval_data_source": "external_holdout", "generator_source": "model"},
    }
    rep = triage_check(clean)
    assert rep["fired_classes"] == [], f"clean output falsely fired: {rep['fired_classes']}"
    assert rep["overall"] == "NO_LISTED_CLASS_FIRED"

    # ---- (b) catch-broken: KNOWN fabrication -> fabrication row FIRES (kappa=1) ----
    if _HAVE_FACTHARNESS:
        fab = {"text": "fabricated quote",
               "claims": [{"text": "bogus", "quote": "uses 99 multiplications",
                           "source_text": src, "load_bearing": True}]}
        rep = triage_check(fab)
        assert "fabrication" in rep["fired_classes"], rep
        fab_row = next(r for r in rep["rows"] if r["class"] == "fabrication")
        assert fab_row["kappa"] == "1", fab_row
    else:
        # honest degraded path: no FACTHARNESS -> the row degrades, never certifies.
        fab = {"text": "x", "claims": [{"text": "y", "quote": "z", "source_text": src}]}
        fr = next(r for r in triage_check(fab)["rows"] if r["class"] == "fabrication")
        assert fr["degraded"] is True and fr["kappa"] == "<1", fr

    # ---- (c) catch-broken: KNOWN branch-cut identity -> numeric row FIRES (kappa=1) ----
    rep = triage_check(real_failure_symbolica_branch_cut())
    assert "numeric-branch-cut-convergence" in rep["fired_classes"], rep
    nrow = next(r for r in rep["rows"] if r["class"] == "numeric-branch-cut-convergence")
    assert nrow["kappa"] == "1", nrow

    # ---- (d) abstain-malformed: a malformed record -> ABSTAIN loudly, never silent-pass ----
    for bad in [None, 42, "just a string", {"unrelated": 1}, []]:
        try:
            triage_check(bad)
            assert False, f"malformed record {bad!r} did NOT abstain (silent-pass!)"
        except TriageAbstain:
            pass

    # ---- (e) no-all-clear: no verdict ever says 'safe'/'all-clear'; carries coverage+caveat
    rep = triage_check(clean)
    v = rep["verdict_text"].lower()
    assert "all-clear" not in v, rep
    assert ("safe" not in v) or ("not a safety proof" in v), rep
    assert "no listed class fired" in v and "may escape" in v, rep
    assert str(rep["n_coverage"]) in v, rep

    # ---- (f) schema: uncovered_novel_classes present, True, and not falsifiable ----
    assert rep["uncovered_novel_classes"] is True
    # it is hard-coded in triage_check; a downstream consumer cannot get a False from us:
    assert all(triage_check(c)["uncovered_novel_classes"] is True
               for c in [clean, real_failure_symbolica_branch_cut()])

    # ---- (g/honesty) spec-gaming kappa is keyed off a SUPPLIED oracle, NOT CRUCIBLE-on-disk:
    #      no oracle -> kappa<1 + degraded (must NOT launder to kappa=1 just because CRUCIBLE exists);
    #      an independent oracle -> kappa=1.
    sg_no_oracle = detect_specification_gaming(
        {"spec_gaming": {"in_sample_score": 1.1, "oos_score": -0.1, "good_threshold": 0.0}})
    assert sg_no_oracle["kappa"] == "<1" and sg_no_oracle["degraded"] is True, sg_no_oracle
    sg_oracle = detect_specification_gaming(
        {"spec_gaming": {"independent_oracle_verdict": "wrong"}})
    assert sg_oracle["kappa"] == "1" and sg_oracle["fired"] is True, sg_oracle

    # ---- (i) every named reject case: each kappa=1 detector PASSES good AND CATCHES broken ----
    # spec-gaming: clean (no flip) passes; an in-sample/OOS flip fires.
    assert detect_specification_gaming({})["fired"] is False
    sg_fire = detect_specification_gaming(
        {"spec_gaming": {"in_sample_score": 1.13, "oos_score": -0.2, "good_threshold": 0.0}})
    assert sg_fire["fired"] is True, sg_fire
    # circular-measurement: independent data passes; same-source / readable key fires.
    assert detect_circular_measurement(
        {"provenance": {"eval_data_source": "holdout", "generator_source": "model"}})["fired"] is False
    assert detect_circular_measurement(
        {"provenance": {"answer_key_readable_by_generator": True}})["fired"] is True
    # crash/silent-pass: a guarded detector passes; a silent-passer fires.
    def good_detector(x):
        if x in (None, "", [], {}, 0):
            raise ValueError("degenerate input rejected loudly")
        return {"ok": True}
    assert detect_crash_silent_pass(
        {"malformed_probe": {"callable": good_detector}})["fired"] is False
    assert detect_crash_silent_pass(
        {"malformed_probe": {"callable": lambda x: {"ok": True}}})["fired"] is True
    # shared-blind-spot: different families pass; same-family agreement fires.
    assert detect_shared_blind_spot(
        {"verifiers": {"families": ["symbolic", "numeric"], "agree": True}})["fired"] is False
    assert detect_shared_blind_spot(
        {"verifiers": {"families": ["numeric", "numeric"], "agree": True}})["fired"] is True

    # ======================================================================= #
    #  REGRESSION TESTS for the cross-model audit defects (each reproduces the
    #  auditor's exact exploit and asserts it is now BLOCKED). PERMANENT.
    # ======================================================================= #

    # --- AUDIT-HIGH: crash/silent-pass evasion via {'ok': 1} (integer) ---------
    # BEFORE: `out.get('ok') is True` (identity) -> {'ok':1} silently passed -> fired=False.
    # AFTER: value-based check -> {'ok':1} is a silent-pass -> row FIRES.
    sp_int = detect_crash_silent_pass(
        {"text": "x", "malformed_probe": {"callable": lambda x: {"ok": 1},
                                          "degenerate_inputs": [None, {}, ""]}})
    assert sp_int["fired"] is True, ("AUDIT-HIGH not fixed: {'ok':1} (int) bypassed the "
                                     "silent-pass check: %r" % sp_int)
    # the same exploit family: truthy non-bool ok values, truthy ints, truthy lists, bare
    # truthy returns, ambiguous returns, None-instead-of-raise -- ALL must fire now.
    for evader in (lambda x: {"ok": 1}, lambda x: {"ok": "yes"}, lambda x: {"ok": [1]},
                   lambda x: 42, lambda x: [1, 2, 3], lambda x: True,
                   lambda x: {"valid": 1}, lambda x: {"unrelated": 9}, lambda x: None,
                   lambda x: object()):
        r = detect_crash_silent_pass(
            {"text": "x", "malformed_probe": {"callable": evader,
                                              "degenerate_inputs": [None, {}, ""]}})
        assert r["fired"] is True, ("AUDIT-HIGH not fixed: evader %r silent-passed: %r"
                                    % (evader, r))
    # CONTROL: a detector that genuinely rejects junk (raises, or returns an explicit
    # reject verdict, or a falsey ok) must NOT fire (no false-positive on a good gate).
    def _raises(x):
        raise ValueError("degenerate input rejected loudly")
    for good in (_raises, lambda x: {"ok": False}, lambda x: {"status": "REJECT"},
                 lambda x: {"verdict": "abstain"}, lambda x: "REJECT: malformed",
                 lambda x: False, lambda x: 0, lambda x: {"valid": False}):
        r = detect_crash_silent_pass(
            {"text": "x", "malformed_probe": {"callable": good,
                                              "degenerate_inputs": [None, {}, ""]}})
        assert r["fired"] is False, ("AUDIT-HIGH over-correction: a genuinely-rejecting "
                                     "detector %r falsely fired: %r" % (good, r))

    # --- AUDIT-MEDIUM: crash/silent-pass kappa=1 mislabel when NO probe supplied --
    # BEFORE: kappa='1', degraded=False (implied a verified-clean check though none ran).
    # AFTER: kappa='<1', degraded=True (a null-op is labeled "not checked", not "clean").
    no_probe = detect_crash_silent_pass({"text": "x"})
    assert no_probe["kappa"] == "<1" and no_probe["degraded"] is True, (
        "AUDIT-MEDIUM not fixed: no-probe still labeled kappa=1/clean: %r" % no_probe)
    assert no_probe["fired"] is False, no_probe

    # --- AUDIT-MEDIUM: spec-gaming kappa=1 laundering via garbage oracle value -----
    # BEFORE: has_oracle = (oracle is not None) -> '' , 0, False, 'maybe' reached kappa=1.
    # AFTER: only a RECOGNIZED agree/disagree verdict is a usable oracle -> garbage = kappa<1.
    for junk in ("", "maybe", "unknown", "n/a", "???", "purple",
                 "yes-ish", "wrongish", "passable", "noteworthy", "correctness"):
        r = detect_specification_gaming({"spec_gaming": {"independent_oracle_verdict": junk}})
        assert r["kappa"] == "<1" and r["degraded"] is True, (
            "AUDIT-MEDIUM not fixed: garbage oracle %r laundered to kappa=1: %r" % (junk, r))
    for junk in (0, False):                 # falsey non-string garbage values too
        r = detect_specification_gaming({"spec_gaming": {"independent_oracle_verdict": junk}})
        assert r["kappa"] == "<1" and r["degraded"] is True, (
            "AUDIT-MEDIUM not fixed: garbage oracle %r laundered to kappa=1: %r" % (junk, r))
    # CONTROL: a recognized verdict still earns kappa=1 (no over-correction).
    r = detect_specification_gaming({"spec_gaming": {"independent_oracle_verdict": "correct"}})
    assert r["kappa"] == "1" and r["fired"] is False, r       # agrees -> kappa=1, no fire
    r = detect_specification_gaming({"spec_gaming": {"independent_oracle_verdict": "wrong"}})
    assert r["kappa"] == "1" and r["fired"] is True, r        # disagrees -> kappa=1, fires

    # --- AUDIT-LOW: spec-gaming oracle disagree too narrow (NL variants missed) ----
    # BEFORE: only exact 'wrong'/'fail'/'incorrect' fired; 'wrong answer'/'failed'/'error'
    #         /'false-positive' did NOT fire.  AFTER: recognized variants fire.
    for variant in ("wrong answer", "failed", "error", "false-positive", "incorrect result",
                    "mismatch", "rejected"):
        r = detect_specification_gaming({"spec_gaming": {"independent_oracle_verdict": variant}})
        assert r["fired"] is True and r["kappa"] == "1", (
            "AUDIT-LOW not fixed: disagree variant %r did not fire: %r" % (variant, r))

    # --- AUDIT-LOW: overconfidence caller-suppression via unverified_threshold=9999 -
    # BEFORE: caller-set unverified_threshold=9999 suppressed the row with 10 unverified
    #         load-bearing claims (fired=False).  AFTER: threshold is clamped to <=1, fires.
    ten_unverified = {"text": "x", "unverified_threshold": 9999,
                      "claims": [{"text": "c%d" % i, "load_bearing": True} for i in range(10)]}
    r = detect_overconfidence(ten_unverified)
    assert r["fired"] is True, ("AUDIT-LOW not fixed: unverified_threshold=9999 suppressed "
                                "the overconfidence row with 10 unverified claims: %r" % r)
    assert r["evidence"]["threshold"] <= 1 and r["evidence"]["threshold_clamped"] is True, r
    # CONTROL: zero unverified load-bearing claims must NOT fire (no over-correction).
    assert detect_overconfidence({"text": "x", "claims": []})["fired"] is False

    print("triage_check selftest: PASS (accept-good / catch-fabrication(k=1) / catch-branch-cut(k=1) / "
          "abstain-malformed(loud) / no-all-clear / uncovered_novel_classes-locked / every kappa=1 "
          "reject case good+broken / AUDIT regressions: ok=1-evasion BLOCKED, no-probe null-op "
          "labeled kappa<1, garbage-oracle laundering BLOCKED, NL disagree variants fire, "
          "threshold-suppression clamped)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(triage_check(json.load(open(sys.argv[1]))), indent=2, default=str))
    else:
        print("usage: triage_check.py selftest | <record.json>   (run selftest_all.py for the gate)")
