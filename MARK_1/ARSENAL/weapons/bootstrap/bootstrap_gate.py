#!/usr/bin/env python3
"""BOOTSTRAP frozen gate — the gate-OF-the-gate.

BOOTSTRAP stands up a NEW department's exact verifier semi-automatically. The
ONLY thing that promotes a domain to kappa>0 is a candidate verifier that, when
RUN on known-answer cases, passes the SAME bar every weapon gate passes:

    (a) ACCEPT a known-good input,
    (b) CATCH a known-broken input  (and >=1 broken per declared violation type),
    (c) ABSTAIN on a malformed input,

BEFORE registration. Step (1) of the pipeline ("an LLM proposed this verifier")
is 0%-TRUSTED: LLM-proposed constructions/tools are fabrication-prone (registry
W4: "LLM constructions are fabrication-prone (Haiku+Sonnet fabricated 100% raw)
-> checker mandatory"; see GROUNDING.md). The RUN, not the proposal, earns kappa.

Doctrine ("a gate that can't fail is not a gate"):
  - A candidate that only ACCEPTS-good (never tested on a broken input) is
    REJECTED — a verifier that cannot fail is not a verifier.
  - A candidate that is SOUNDNESS-INCOMPLETE — passes good cases but MISSES a
    planted broken one (e.g. a Sudoku checker that skips the 3x3 boxes) — is
    REJECTED. Hence the broken set MUST contain >=1 instance of each declared
    violation type (kickoff audit fix #2).
  - A HALLUCINATED / non-running verifier (raises on import/call) is REJECTED at
    the run step, never registered on its say-so (kickoff self-test (c)).
  - A judgment-only domain (essay quality) has NO exact verifier -> kappa=0
    ARMOR-ONLY; BOOTSTRAP must NOT invent a fake gate to look capable.

The kappa=1 slice is exactly this validation RUN (machine-checkable). The
"I found a verifier" search step is kappa<1 LLM judgment and carries no authority.

_selftest() is non-waivable: it requires the gate to (1) ACCEPT a sound complete
verifier on a real domain, (2) REJECT a hallucinated/non-running candidate, (3)
REJECT a can't-fail candidate, (4) REJECT a soundness-incomplete candidate, and
(5) ABSTAIN/route a malformed harness. All must pass or NOTHING BOOTSTRAP says
about a domain's kappa is trusted.
"""
import sys
import traceback


# --------------------------------------------------------------------------- #
#  outcome / verdict vocabulary  (frozen)
# --------------------------------------------------------------------------- #
FOUND = "KAPPA>0_VERIFIER_FOUND"          # validated -> register a department
ARMOR_ONLY = "KAPPA=0_ARMOR_ONLY"         # no exact verifier -> route to armor
ABSTAIN = "ABSTAIN_NEED_INPUT"            # under-specified to even search

# candidate-level verdicts (a single candidate's run result)
CAND_VALIDATED = "VALIDATED"
CAND_REJECTED = "REJECTED"

# reject reasons (frozen, machine-readable)
REJ_HALLUCINATED = "HALLUCINATED_NONRUNNING"        # raised on import/call
REJ_REJECTS_GOOD = "REJECTS_KNOWN_GOOD"             # fails an accept-good case
REJ_CANT_FAIL = "ACCEPTS_KNOWN_BROKEN_OR_NO_BROKEN_TESTED"   # can't fail
REJ_INCOMPLETE = "SOUNDNESS_INCOMPLETE_MISSED_VIOLATION_TYPE"  # missed a class
REJ_BAD_ABSTAIN = "DID_NOT_ABSTAIN_ON_MALFORMED"   # accepted/crashed on garbage
REJ_NO_KNOWN_CASES = "NO_KNOWN_ANSWER_CASES_SUPPLIED"  # nothing to validate on
REJ_NO_MALFORMED_CASE = "NO_MALFORMED_CASE_SUPPLIED"   # abstain bar untested (Defect A)
REJ_NO_DECLARED_TYPES = "NO_DECLARED_VIOLATION_TYPES"  # coverage check disabled (Defect B)
REJ_UNTYPED_BROKEN = "BROKEN_CASE_MISSING_VIOLATION_TYPE"  # broken w/o a class (Defect B)


# --------------------------------------------------------------------------- #
#  the candidate-verifier contract
# --------------------------------------------------------------------------- #
# A candidate verifier is a python callable verifier(instance) -> str in
# {"VALID", "INVALID", "MALFORMED"}.  It must be TOTAL on the supplied cases:
# it may NOT raise on a well-formed-but-broken input (that would be a crash, not
# a verdict). It SHOULD return "MALFORMED" — not raise, not "VALID" — on garbage.
#
# A "known-answer case" is a dict:
#   {"input": <instance>, "label": "GOOD"|"BROKEN"|"MALFORMED",
#    "violation_type": <str or None>}   # required str for every BROKEN case
#
# The harness the searcher hands BOOTSTRAP is a dict:
#   {"domain": str,
#    "declared_violation_types": [str, ...],   # what the verifier CLAIMS to check
#    "verifier": callable,
#    "cases": [known-answer case, ...]}
VALID, INVALID, MALFORMED = "VALID", "INVALID", "MALFORMED"
_LEGAL_VERDICTS = {VALID, INVALID, MALFORMED}


def _safe_call(verifier, instance):
    """Run a candidate verifier under guard. Returns (ok, verdict_or_exc).

    A verifier that RAISES on a well-formed case is treated as non-running
    (hallucinated / broken) at THAT case — the run, not the claim, decides.
    """
    try:
        out = verifier(instance)
    except Exception as e:  # noqa: BLE001 — a raising verifier is a failed run
        return (False, f"{type(e).__name__}: {e}")
    if out not in _LEGAL_VERDICTS:
        return (False, f"ILLEGAL_VERDICT:{out!r}")
    return (True, out)


def validate_candidate(harness):
    """RUN a candidate verifier on its known-answer cases and decide if it earns
    kappa>0. Returns a machine-readable dict. THIS is the kappa=1 slice — the
    only authority. No self-report is consulted.

    Hard requirements to be VALIDATED:
      - import/call never raises on a well-formed case (else HALLUCINATED),
      - accepts EVERY GOOD case as VALID,
      - catches EVERY BROKEN case as INVALID,
      - at least ONE declared violation type exists (an empty declared list would
        make the coverage check vacuous — REJ_NO_DECLARED_TYPES; Defect B fix),
      - EVERY BROKEN case carries a non-None violation_type (an untyped broken
        case cannot prove coverage of any class — REJ_UNTYPED_BROKEN; Defect B fix),
      - >=1 BROKEN case exists for EACH declared violation type (audit fix #2),
      - at least ONE MALFORMED case was supplied AND the verifier returns MALFORMED
        (not VALID, not INVALID, not a raise) on every one of them. The SPEC
        contract is ">=1 good + >=1 broken per declared type + >=1 malformed"; a
        harness that omits malformed cases leaves the abstain bar UNTESTED, so a
        verifier that would CRASH on garbage in production could otherwise sneak
        through (Defect A fix — REJ_NO_MALFORMED_CASE),
      - at least one GOOD and one BROKEN case were actually supplied.
    """
    domain = harness.get("domain", "<unnamed>")
    verifier = harness.get("verifier")
    cases = harness.get("cases", [])
    declared = list(harness.get("declared_violation_types", []))

    rec = {
        "domain": domain,
        "candidate_verdict": None,
        "reject_reason": None,
        "n_good": 0, "n_broken": 0, "n_malformed": 0,
        "declared_violation_types": declared,
        "violation_types_exercised": [],
        "per_case": [],
        "kappa": None,
    }

    if not callable(verifier):
        rec["candidate_verdict"] = CAND_REJECTED
        rec["reject_reason"] = REJ_HALLUCINATED
        rec["per_case"].append({"note": "verifier is not callable", "ok": False})
        rec["kappa"] = 0.0
        return rec

    good = [c for c in cases if c.get("label") == "GOOD"]
    broken = [c for c in cases if c.get("label") == "BROKEN"]
    malformed = [c for c in cases if c.get("label") == "MALFORMED"]
    rec["n_good"], rec["n_broken"], rec["n_malformed"] = len(good), len(broken), len(malformed)

    # Must have something to validate against — no cases => not a validated verifier.
    if not good or not broken:
        rec["candidate_verdict"] = CAND_REJECTED
        rec["reject_reason"] = (REJ_CANT_FAIL if good and not broken
                                else REJ_NO_KNOWN_CASES)
        rec["kappa"] = 0.0
        return rec

    # --- Defect B fix: the coverage check is only meaningful with declared types. #
    # An EMPTY declared_violation_types list makes `missing = []` trivially, so a
    # verifier that merely MEMORIZES the test cases (no real soundness) would pass.
    # Refuse: with nothing declared there is no class whose coverage was proven.
    if not declared:
        rec["candidate_verdict"] = CAND_REJECTED
        rec["reject_reason"] = REJ_NO_DECLARED_TYPES
        rec["kappa"] = 0.0
        return rec

    # --- Defect B fix: every BROKEN case must name the class it exercises. An ---- #
    # untyped (violation_type=None) broken case proves no declared class, so it
    # cannot count toward coverage; allowing it would re-open the memorizer bypass.
    untyped_broken = [c for c in broken if c.get("violation_type") is None]
    if untyped_broken:
        rec["candidate_verdict"] = CAND_REJECTED
        rec["reject_reason"] = REJ_UNTYPED_BROKEN
        rec["n_untyped_broken"] = len(untyped_broken)
        rec["kappa"] = 0.0
        return rec

    # --- accept-good: every GOOD case must be VALID, no raises -------------- #
    for c in good:
        ok, out = _safe_call(verifier, c["input"])
        rec["per_case"].append({"label": "GOOD", "ok": ok, "out": out})
        if not ok:                       # raised / illegal -> non-running
            rec["candidate_verdict"] = CAND_REJECTED
            rec["reject_reason"] = REJ_HALLUCINATED
            rec["kappa"] = 0.0
            return rec
        if out != VALID:                 # rejects a known-good input
            rec["candidate_verdict"] = CAND_REJECTED
            rec["reject_reason"] = REJ_REJECTS_GOOD
            rec["kappa"] = 0.0
            return rec

    # --- catch-broken: every BROKEN case must be INVALID ------------------- #
    exercised = set()
    for c in broken:
        ok, out = _safe_call(verifier, c["input"])
        vt = c.get("violation_type")
        rec["per_case"].append({"label": "BROKEN", "violation_type": vt,
                                "ok": ok, "out": out})
        if not ok:                       # raised on a well-formed broken input
            rec["candidate_verdict"] = CAND_REJECTED
            rec["reject_reason"] = REJ_HALLUCINATED
            rec["kappa"] = 0.0
            return rec
        if out != INVALID:               # MISSED a violation -> incomplete
            rec["candidate_verdict"] = CAND_REJECTED
            rec["reject_reason"] = REJ_INCOMPLETE
            rec["kappa"] = 0.0
            return rec
        if vt is not None:
            exercised.add(vt)
    rec["violation_types_exercised"] = sorted(exercised)

    # --- coverage: >=1 broken per declared violation type (audit fix #2) ---- #
    # A verifier claiming to check N violation types must have been EXERCISED on
    # each — else its soundness for the un-exercised class is unproven.
    missing = [vt for vt in declared if vt not in exercised]
    if missing:
        rec["candidate_verdict"] = CAND_REJECTED
        rec["reject_reason"] = REJ_INCOMPLETE
        rec["missing_violation_types"] = missing
        rec["kappa"] = 0.0
        return rec

    # --- Defect A fix: the abstain bar must actually be EXERCISED. The SPEC ---- #
    # contract requires >=1 malformed case; an empty `malformed` list silently
    # no-ops this loop, leaving abstain UNTESTED. A verifier that would CRASH (or
    # return VALID) on garbage in production would then earn kappa=1 without ever
    # proving it abstains. Require >=1 malformed case; absence => REJECTED.
    if not malformed:
        rec["candidate_verdict"] = CAND_REJECTED
        rec["reject_reason"] = REJ_NO_MALFORMED_CASE
        rec["kappa"] = 0.0
        return rec

    # --- abstain-malformed: garbage -> MALFORMED, never VALID, never a raise  #
    for c in malformed:
        ok, out = _safe_call(verifier, c["input"])
        rec["per_case"].append({"label": "MALFORMED", "ok": ok, "out": out})
        # A raise here OR a VALID/INVALID verdict on garbage = not abstaining.
        if (not ok) or (out != MALFORMED):
            rec["candidate_verdict"] = CAND_REJECTED
            rec["reject_reason"] = REJ_BAD_ABSTAIN
            rec["kappa"] = 0.0
            return rec

    # Passed every bar on actual RUNS -> earns kappa=1 (exact verifier).
    rec["candidate_verdict"] = CAND_VALIDATED
    rec["kappa"] = 1.0
    return rec


# --------------------------------------------------------------------------- #
#  the pipeline: search (0%-trusted) -> validate (the authority) -> outcome
# --------------------------------------------------------------------------- #
def bootstrap_domain(spec):
    """Top-level pipeline for ONE new problem class.

    `spec` (what the searcher/proposer hands in):
      {"domain": str,
       "well_specified": bool,                 # enough to even search?
       "candidate_harnesses": [harness, ...],  # 0%-trusted proposals to RUN
       "is_judgment_only": bool}               # honest signal: no exact property

    Returns one of the THREE OUTCOMES. The RUN decides — never a self-report.
    """
    domain = spec.get("domain", "<unnamed>")

    # ABSTAIN: under-specified to even search.
    if not spec.get("well_specified", False):
        return {"domain": domain, "outcome": ABSTAIN, "kappa": None,
                "why": "Problem class under-specified to search for a verifier. "
                       "Ask for a sharper spec (what exactly is checked?). "
                       "Do not guess."}

    attempts = []
    candidates = spec.get("candidate_harnesses", []) or []
    n_bound = spec.get("n_attempts_bound")
    if n_bound is not None:
        candidates = candidates[:n_bound]

    for h in candidates:
        v = validate_candidate(h)
        attempts.append(v)
        if v["candidate_verdict"] == CAND_VALIDATED:
            return {"domain": domain, "outcome": FOUND, "kappa": 1.0,
                    "validated_by": v,
                    "registration": _registration_record(domain, h, v),
                    "attempts": attempts,
                    "ceiling": ("Toy-passing != frontier-correct. This verifier "
                                "passed its KNOWN-ANSWER cases; the new weapon it "
                                "scaffolds must STILL pass its own full box build "
                                "(gate-first + demo + cross-model audit). BOOTSTRAP "
                                "opens the door; it does not ship the weapon.")}

    # No candidate validated within the committed N-attempts bound -> kappa=0.
    return {"domain": domain, "outcome": ARMOR_ONLY, "kappa": 0.0,
            "attempts": attempts,
            "why": ("No exact verifier found/validated in "
                    f"{len(attempts)} attempt(s) (bound={n_bound}). "
                    + ("Domain is judgment-only (no exact property to decide) -> "
                       "ARMOR-ONLY; do NOT invent a fake gate. "
                       if spec.get("is_judgment_only") else
                       "Either no exact verifier exists or none validated; route to "
                       "ARMOR. ")
                    + "Recorded so the domain is not wastefully re-attempted.")}


def _registration_record(domain, harness, validation):
    """Build a WEAPON_REGISTRY-shaped record for a VALIDATED department.

    Mirrors the registry schema fields. BOOTSTRAP does NOT write the shared
    registry (registration is handled separately) — it produces the record a
    registrar would commit. The verifier earned kappa=1 by RUN, not claim.
    """
    return {
        "name": f"BOOTSTRAPPED_{domain.upper().replace(' ', '_')}",
        "problem_class": domain,
        "verifier": {
            "ground_truth_type": "machine_check",
            "rule": "candidate validated by RUN on known-answer cases "
                    "(accept-good / catch-broken-per-violation-type / abstain-malformed)",
            "declared_violation_types": harness.get("declared_violation_types", []),
            "violation_types_exercised": validation["violation_types_exercised"],
        },
        "kappa": 1.0,
        "status": "VALIDATED_BY_RUN_handoff_to_full_weapon_build",
        "honest_ceiling": "toy-passing != frontier-correct; full box build still required",
    }


# --------------------------------------------------------------------------- #
#  REFERENCE VERIFIERS used by the self-tests (real, pure-python, no deps)
#  These are the domains' EXACT checkers. They double as the "found verifier"
#  in the FOUND self-test and as the source the BROKEN variants are built from.
# --------------------------------------------------------------------------- #
def sudoku_verifier(grid):
    """Exact verifier for a completed 9x9 Sudoku solution. kappa=1.

    Grounded rule (GROUNDING.md, Wikipedia 'Sudoku', fetched 2026-06-20): a valid
    completed grid uses digits 1..9 and each ROW, each COLUMN, and each of the
    nine 3x3 BOXES contains all digits 1..9 exactly once.

    Returns "VALID" / "INVALID" / "MALFORMED". NEVER raises on a 9x9 int grid.
    """
    # --- shape / type guard -> MALFORMED, do not raise -------------------- #
    if not isinstance(grid, (list, tuple)) or len(grid) != 9:
        return MALFORMED
    for row in grid:
        if not isinstance(row, (list, tuple)) or len(row) != 9:
            return MALFORMED
        for v in row:
            if not isinstance(v, int) or isinstance(v, bool):
                return MALFORMED

    want = set(range(1, 10))
    # rows
    for r in range(9):
        if set(grid[r]) != want:
            return INVALID
    # columns
    for c in range(9):
        if set(grid[r][c] for r in range(9)) != want:
            return INVALID
    # 3x3 boxes
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = set(grid[br + i][bc + j] for i in range(3) for j in range(3))
            if box != want:
                return INVALID
    return VALID


def _sudoku_verifier_no_boxes(grid):
    """SOUNDNESS-INCOMPLETE planted candidate: checks rows + columns but SKIPS
    the 3x3 boxes. Passes a valid grid AND passes row/column-broken catches, but
    MISSES a box-only violation (a row/col-valid grid that breaks a box). Used by
    the self-test that a soundness-incomplete verifier is REJECTED."""
    if not isinstance(grid, (list, tuple)) or len(grid) != 9:
        return MALFORMED
    for row in grid:
        if not isinstance(row, (list, tuple)) or len(row) != 9:
            return MALFORMED
        for v in row:
            if not isinstance(v, int) or isinstance(v, bool):
                return MALFORMED
    want = set(range(1, 10))
    for r in range(9):
        if set(grid[r]) != want:
            return INVALID
    for c in range(9):
        if set(grid[r][c] for r in range(9)) != want:
            return INVALID
    return VALID  # BUG: never checks boxes


def _hallucinated_verifier(_instance):
    """A 'verifier' the searcher claims exists but that does not run — calls a
    non-existent tool. RAISES. Must be REJECTED at the run step."""
    import nonexistent_solver_xyz  # noqa: F401 — deliberately unimportable
    return VALID


def _cant_fail_verifier(_instance):
    """A degenerate 'verifier' that ACCEPTS everything (and is never tested on a
    broken input, OR accepts the broken one). A verifier that cannot fail is not
    a verifier. Must be REJECTED."""
    return VALID


# --------------------------------------------------------------------------- #
#  known-answer case fixtures for the self-tests
# --------------------------------------------------------------------------- #
def _valid_sudoku():
    """A genuinely valid completed 9x9 grid (a known solution)."""
    return [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]


def _row_broken_sudoku():
    """Valid grid with one ROW duplicate (1->5 in row 0): rows fail."""
    g = [r[:] for r in _valid_sudoku()]
    g[0][7] = 5  # row 0 now has two 5s, missing 1
    return g


def _box_only_broken_sudoku():
    """A grid that is ROW-valid and COLUMN-valid but breaks a 3x3 BOX. This is the
    case that catches a no-boxes (soundness-incomplete) verifier: swap two cells
    in the same column-band but different boxes so each row and each column is
    still a permutation of 1..9, yet two top-left-box rows now share a value.

    Built by swapping grid[2] and grid[3] partially is fragile; instead we
    construct a Latin-square-valid grid whose top-left box repeats. We start from
    a row/column-valid arrangement that is NOT box-valid."""
    # A cyclic Latin square: row r is [((r + c) % 9) + 1]. Every row and every
    # column is a permutation of 1..9 (verified: rows-valid, columns-valid), but
    # the 3x3 boxes REPEAT values (boxes-broken). This is the case that exposes a
    # verifier which checks rows+columns but skips the boxes.
    g = [[((r + c) % 9) + 1 for c in range(9)] for r in range(9)]
    return g


def _malformed_sudoku():
    """Garbage that is not a 9x9 int grid -> verifier must return MALFORMED."""
    return [[1, 2, 3], "not-a-grid", 42]


def _good_cases():
    return [{"input": _valid_sudoku(), "label": "GOOD", "violation_type": None}]


def _broken_cases_full():
    """Broken cases covering BOTH declared violation types: a row violation and a
    box violation. (Column is exercised structurally by the box-only case being
    column-valid; we add an explicit column case for completeness.)"""
    # column-broken: transpose the row-broken grid so a COLUMN has a duplicate.
    rb = _row_broken_sudoku()
    col_broken = [[rb[c][r] for c in range(9)] for r in range(9)]
    return [
        {"input": _row_broken_sudoku(), "label": "BROKEN", "violation_type": "row_duplicate"},
        {"input": col_broken, "label": "BROKEN", "violation_type": "column_duplicate"},
        {"input": _box_only_broken_sudoku(), "label": "BROKEN", "violation_type": "box_duplicate"},
    ]


def _malformed_cases():
    return [{"input": _malformed_sudoku(), "label": "MALFORMED", "violation_type": None}]


def _full_harness(verifier):
    return {
        "domain": "sudoku-solution-validity",
        "declared_violation_types": ["row_duplicate", "column_duplicate", "box_duplicate"],
        "verifier": verifier,
        "cases": _good_cases() + _broken_cases_full() + _malformed_cases(),
    }


# --------------------------------------------------------------------------- #
#  NON-WAIVABLE SELF-TESTS
# --------------------------------------------------------------------------- #
def _selftest():
    # ---- sanity: the reference verifier itself decides the fixtures right --- #
    assert sudoku_verifier(_valid_sudoku()) == VALID
    assert sudoku_verifier(_row_broken_sudoku()) == INVALID
    assert sudoku_verifier(_box_only_broken_sudoku()) == INVALID, \
        "box-only-broken fixture must be caught by the real verifier"
    assert sudoku_verifier(_malformed_sudoku()) == MALFORMED
    # the box-only fixture MUST be row-valid and column-valid (else it doesn't
    # isolate the box check) — verify the no-boxes verifier accepts it:
    assert _sudoku_verifier_no_boxes(_box_only_broken_sudoku()) == VALID, \
        "box-only fixture must slip past a no-boxes verifier (else it can't expose incompleteness)"

    # ---- (a) FOUND: a sound, complete verifier on a real domain is VALIDATED  #
    r = validate_candidate(_full_harness(sudoku_verifier))
    assert r["candidate_verdict"] == CAND_VALIDATED, r
    assert r["kappa"] == 1.0, r
    assert set(r["violation_types_exercised"]) == {"row_duplicate", "column_duplicate", "box_duplicate"}, r

    # ---- (c) HALLUCINATED: a non-running candidate is REJECTED at the run step #
    rh = validate_candidate(_full_harness(_hallucinated_verifier))
    assert rh["candidate_verdict"] == CAND_REJECTED, rh
    assert rh["reject_reason"] == REJ_HALLUCINATED, rh

    # ---- can't-fail: a verifier never tested on a broken input is REJECTED --- #
    #      (only good cases supplied -> REJ_CANT_FAIL)
    only_good = {"domain": "x", "declared_violation_types": [],
                 "verifier": _cant_fail_verifier, "cases": _good_cases()}
    rcf = validate_candidate(only_good)
    assert rcf["candidate_verdict"] == CAND_REJECTED, rcf
    assert rcf["reject_reason"] == REJ_CANT_FAIL, rcf
    #      and an accept-everything verifier that IS handed broken cases is caught
    #      as soundness-incomplete (it returns VALID on a broken input -> missed)
    rcf2 = validate_candidate(_full_harness(_cant_fail_verifier))
    assert rcf2["candidate_verdict"] == CAND_REJECTED, rcf2
    assert rcf2["reject_reason"] == REJ_INCOMPLETE, rcf2

    # ---- (d) SOUNDNESS-INCOMPLETE: passes good + row/col-broken but MISSES the  #
    #      box-only violation -> REJECTED (audit fix #2: >=1 broken per type)     #
    ri = validate_candidate(_full_harness(_sudoku_verifier_no_boxes))
    assert ri["candidate_verdict"] == CAND_REJECTED, ri
    assert ri["reject_reason"] == REJ_INCOMPLETE, ri

    # ---- (b->ABSTAIN) a verifier that crashes/accepts on MALFORMED is REJECTED  #
    def _no_abstain(instance):
        # returns VALID even on garbage (never abstains)
        return VALID if not (isinstance(instance, (list, tuple)) and len(instance) == 9) \
            else sudoku_verifier(instance)
    # build a harness where good/broken pass but malformed is mis-handled:
    bad_abstain = {
        "domain": "x", "declared_violation_types": ["row_duplicate"],
        "verifier": lambda g: (MALFORMED if False else sudoku_verifier(g)),  # real verifier handles malformed OK
        "cases": _good_cases()
                 + [{"input": _row_broken_sudoku(), "label": "BROKEN", "violation_type": "row_duplicate"}]
                 + [{"input": _malformed_sudoku(), "label": "MALFORMED", "violation_type": None}],
    }
    # real verifier DOES abstain -> this should VALIDATE (control)
    rok = validate_candidate(bad_abstain)
    assert rok["candidate_verdict"] == CAND_VALIDATED, rok
    # now a verifier that returns VALID on malformed -> REJ_BAD_ABSTAIN
    bad_abstain2 = dict(bad_abstain, verifier=_no_abstain)
    rba = validate_candidate(bad_abstain2)
    assert rba["candidate_verdict"] == CAND_REJECTED, rba
    assert rba["reject_reason"] == REJ_BAD_ABSTAIN, rba

    # ---- reject-good: a verifier that rejects a known-GOOD input is REJECTED -- #
    rg = validate_candidate({
        "domain": "x", "declared_violation_types": ["row_duplicate"],
        "verifier": lambda g: INVALID,  # rejects everything incl. the good grid
        "cases": _full_harness(None)["cases"],
    })
    assert rg["candidate_verdict"] == CAND_REJECTED, rg
    assert rg["reject_reason"] == REJ_REJECTS_GOOD, rg

    # ---- REGRESSION (audit Defect A): MALFORMED-CASE BYPASS --------------------- #
    # The SPEC contract requires >=1 malformed case. A harness that OMITS malformed
    # cases left the abstain bar UNTESTED, so a verifier that CRASHES on garbage in
    # production could earn kappa=1. (Before the fix this VALIDATED; now it MUST be
    # REJECTED with NO_MALFORMED_CASE_SUPPLIED.)
    def _crash_on_garbage(grid):
        # correct on well-formed grids, but RAISES on garbage (no MALFORMED branch)
        if not (isinstance(grid, (list, tuple)) and len(grid) == 9
                and all(isinstance(r, (list, tuple)) and len(r) == 9 for r in grid)):
            raise ValueError("garbage input — would crash in production")
        return sudoku_verifier(grid)
    no_malformed_harness = {
        "domain": "crash-test", "declared_violation_types": ["row_duplicate"],
        "verifier": _crash_on_garbage,
        "cases": _good_cases() + [{"input": _row_broken_sudoku(), "label": "BROKEN",
                                   "violation_type": "row_duplicate"}],  # NO malformed case
    }
    rdefA = validate_candidate(no_malformed_harness)
    assert rdefA["candidate_verdict"] == CAND_REJECTED, rdefA
    assert rdefA["reject_reason"] == REJ_NO_MALFORMED_CASE, rdefA
    # ...and the verifier really WOULD have crashed in production (proves the risk):
    try:
        _crash_on_garbage("garbage")
        raise AssertionError("crash-on-garbage verifier should have raised")
    except ValueError:
        pass

    # ---- REGRESSION (audit Defect B): EMPTY-DECLARED-TYPES BYPASS --------------- #
    # With declared_violation_types=[] the coverage check (`missing`) is vacuously
    # empty, so a verifier that merely MEMORIZES the test cases would pass. (Before
    # the fix this VALIDATED with kappa=1; now it MUST be REJECTED.)
    _GOOD_G, _BROKEN_G = _valid_sudoku(), _row_broken_sudoku()
    def _memorizer(grid):
        if grid == _GOOD_G:
            return VALID
        if grid == _BROKEN_G:
            return INVALID
        return MALFORMED  # no real soundness — just memorized the two cases
    empty_declared_harness = {
        "domain": "memorize-test", "declared_violation_types": [],
        "verifier": _memorizer,
        "cases": [{"input": _GOOD_G, "label": "GOOD", "violation_type": None},
                  {"input": _BROKEN_G, "label": "BROKEN", "violation_type": None},
                  {"input": _malformed_sudoku(), "label": "MALFORMED", "violation_type": None}],
    }
    rdefB = validate_candidate(empty_declared_harness)
    assert rdefB["candidate_verdict"] == CAND_REJECTED, rdefB
    assert rdefB["reject_reason"] == REJ_NO_DECLARED_TYPES, rdefB

    # ---- REGRESSION (Defect B, second leak path): UNTYPED BROKEN CASE ----------- #
    # Even WITH a declared type, an untyped (violation_type=None) broken case proves
    # no class and would re-open the memorizer bypass. MUST be REJECTED.
    untyped_broken_harness = {
        "domain": "untyped-broken-test", "declared_violation_types": ["row_duplicate"],
        "verifier": _memorizer,
        "cases": [{"input": _GOOD_G, "label": "GOOD", "violation_type": None},
                  {"input": _BROKEN_G, "label": "BROKEN", "violation_type": None},
                  {"input": _malformed_sudoku(), "label": "MALFORMED", "violation_type": None}],
    }
    rdefB2 = validate_candidate(untyped_broken_harness)
    assert rdefB2["candidate_verdict"] == CAND_REJECTED, rdefB2
    assert rdefB2["reject_reason"] == REJ_UNTYPED_BROKEN, rdefB2

    print("bootstrap_gate selftest: PASS")
    print("  (a) sound+complete sudoku verifier -> VALIDATED (kappa=1), all 3 "
          "violation types exercised")
    print("  (c) hallucinated/non-running verifier -> REJECTED @ run "
          "(HALLUCINATED_NONRUNNING)")
    print("  can't-fail (only-good / accepts-broken) -> REJECTED "
          "(CANT_FAIL / SOUNDNESS_INCOMPLETE)")
    print("  (d) soundness-incomplete (no-boxes) -> REJECTED "
          "(SOUNDNESS_INCOMPLETE_MISSED_VIOLATION_TYPE)")
    print("  abstain: VALID-on-malformed -> REJECTED (DID_NOT_ABSTAIN); "
          "reject-good -> REJECTED (REJECTS_KNOWN_GOOD)")
    print("  REGRESSION (audit Defect A) no-malformed-case + crash-on-garbage "
          "verifier -> REJECTED (NO_MALFORMED_CASE_SUPPLIED)")
    print("  REGRESSION (audit Defect B) empty-declared-types memorizer -> "
          "REJECTED (NO_DECLARED_VIOLATION_TYPES); untyped-broken -> REJECTED "
          "(BROKEN_CASE_MISSING_VIOLATION_TYPE)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: bootstrap_gate.py selftest")
        print(__doc__)
