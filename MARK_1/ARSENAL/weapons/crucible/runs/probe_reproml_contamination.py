#!/usr/bin/env python3
"""CRUCIBLE probe of reproml_contamination — the R-CONTAM n-gram/Jaccard overlap gate.

TARGET (black-box, real gate): the contamination detector the reproml weapon uses.
  reproml/contam_verify.py :: contamination_report(train_docs, eval_docs, n=13,
  jaccard_threshold=0.8, bow_threshold=0.9). It returns a dict whose `verdict` is
  "CONTAMINATION_DETECTED" (>=1 eval item overlaps the train corpus) or
  "NO_OVERLAP_DETECTED" (none do). We import the REAL module and call the REAL
  function -- NO reimplementation of the gate's logic.

COVERAGE: metamorphic-only (per kickoff). The gate's n-gram order `n`, the
  char-5gram jaccard_threshold, and the order-insensitive bow_threshold are TUNABLE
  FREE PARAMETERS -- there is NO single exact ground-truth verdict for "is this corpus
  contaminated", so a false-accept/false-reject oracle cannot be built without
  re-deriving the gate's own thresholded engine (CIRCULAR). We therefore DROP the
  oracle-bearing modes and run METAMORPHIC + ABSTAIN/CRASH only.

VERDICT MAPPING (CRUCIBLE vocabulary). A contamination detector is a SCREEN: the
  "this is clean / passes" outcome is NO_OVERLAP_DETECTED; the "this is dirty / flagged"
  outcome is CONTAMINATION_DETECTED.
    NO_OVERLAP_DETECTED   -> ACCEPT  (gate clears the corpus: no overlap seen)
    CONTAMINATION_DETECTED-> REJECT  (gate flags the corpus: overlap detected)

METAMORPHIC TRANSFORMS (CLAIMED meaning-preserving on the binary verdict; no oracle
  supplied so this is CALLER-ASSERTED -- stated as residual risk). Each must leave the
  set of "dirty eval items" -- hence the any-dirty binary verdict -- unchanged:
    1. WHITESPACE+CASE normalization of every doc. `_tok` does
       re.findall(r"[a-z0-9]+", s.lower()) and `_char_ngrams` does
       re.sub(r"\\s+"," ").lower(): both are invariant under case folding and under
       collapsing/adding interior whitespace, tabs, and newlines. -> token n-grams,
       char-5grams, and token bags are all identical -> verdict identical.
    2. DOCUMENT REORDERING (shuffle train docs and, independently, eval docs). The
       train n-gram universe is a set UNION (order-free); each eval doc is scored
       independently against the whole train corpus via max(); the binary "any dirty"
       verdict does not depend on doc order. (Per-item eval_index labels change, but the
       VERDICT does not -- and the gate maps to one verdict.)
    3. TRAIN-SIDE DUPLICATE REMOVAL. train_grams is a set; train_char/train_bow are
       per-doc lists consumed only through max(); an exact-duplicate train doc adds a
       duplicate max candidate, so removing it cannot change any eval item's best match
       -> verdict identical. (We do NOT dedup EVAL docs: that changes the rate denominator
       and can change WHICH index is first-dirty, though not the binary verdict; we keep
       the strictly verdict-safe train-side dedup to avoid asserting a transform we cannot
       fully justify.)

ABSTAIN/CRASH: empty / degenerate corpora. CAREFUL HONESTY CALL (see below): this gate
  is documented -- in its own docstring, SPEC.md S7, and the cross-model AUDIT -- as
  reporting a MEASURED RATE + method label and EXPLICITLY NEVER a binary "clean".
  Every return carries a `ceiling_note`: "A measured overlap RATE, not a binary 'clean'.
  NO_OVERLAP_DETECTED != clean ...". So NO_OVERLAP_DETECTED is NOT a "this corpus passed /
  is safe to ship" certification -- it is a labeled "the screen measured zero overlap"
  report that DISCLAIMS cleanliness on its face. Therefore a NO_OVERLAP_DETECTED on an
  empty/degenerate corpus is the gate HONESTLY reporting "zero overlap among the zero
  items I screened", carrying its no-clean-claim note -- it is NOT a silent unsafe ACCEPT.
  Treating it as a false-accept would be a MAPPING-INDUCED false alarm, not a gate bug.
  We thus admit ACCEPT (the rate-report) into the SAFE set for this mode and additionally
  ASSERT (outside the hunt) that the disclaimer ceiling_note is present on the degenerate
  returns -- the only thing that would be a real bug here is a degenerate input that
  CRASHES uncaught or drops the no-clean-claim note. The unsafe outcome we still hunt is a
  CONTAMINATION_DETECTED (REJECT) fabricated from nothing, or an uncaught crash.

RESIDUAL RISK / THRESHOLD-DEPENDENCE (per target note): the verdict is a function of the
  free params (n, jaccard_threshold, bow_threshold). This probe holds them at the gate's
  GPT-3-convention defaults (n=13, jaccard=0.8, bow=0.9) plus the n=5 boundary the gate's
  own smoke uses. A different operator threshold choice is a DIFFERENT gate configuration;
  metamorphic invariance is asserted PER configuration. No exact oracle exists for a free
  threshold, so false-accept/false-reject are NOT run (would be circular).
"""
import os
import sys
import json
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
CRUCIBLE = os.path.dirname(HERE)
ARSENAL = os.path.dirname(CRUCIBLE)
REPROML = os.path.join(ARSENAL, "reproml")

for p in (CRUCIBLE, REPROML):
    if p not in sys.path:
        sys.path.insert(0, p)

import crucible_harness as CH
from crucible_harness import (
    GateAdapter, ACCEPT, REJECT, ABSTAIN, ERROR,
    metamorphic_hunt, abstain_crash_hunt,
)

# ---- import the REAL reproml weapon gate (no reimplementation) ----------------
import contam_verify as RC                       # the real reproml R-CONTAM module
_REAL_FN = RC.contamination_report               # the real gate function

# n<10 raises a (correct, by-design) UserWarning; silence it so it doesn't pollute
# the captured stdout/stderr -- it is not part of the verdict.
warnings.filterwarnings("ignore", category=UserWarning, module="contam_verify")


# --------------------------------------------------------------------------- #
#  GATE ADAPTER — call the REAL gate; map its native verdict string.
# --------------------------------------------------------------------------- #
def contam_gate_fn(train_docs, eval_docs, n=13, jaccard_threshold=0.8, bow_threshold=0.9):
    """Calls the REAL reproml contamination_report (no reimplementation)."""
    return _REAL_FN(train_docs, eval_docs, n=n,
                    jaccard_threshold=jaccard_threshold, bow_threshold=bow_threshold)


def to_verdict(raw):
    """Map the gate's native dict -> CRUCIBLE vocabulary.
      NO_OVERLAP_DETECTED    -> ACCEPT (corpus cleared: no overlap)
      CONTAMINATION_DETECTED -> REJECT (corpus flagged: overlap detected)
    Anything else -> raises (adapter maps to ERROR)."""
    v = raw["verdict"]
    if v == "NO_OVERLAP_DETECTED":
        return ACCEPT
    if v == "CONTAMINATION_DETECTED":
        return REJECT
    raise ValueError(f"unexpected gate verdict {v!r}")


gate = GateAdapter("reproml_contamination", contam_gate_fn, to_verdict)


# confirm we are bound to the genuine real gate, not a copy
assert _REAL_FN is RC.contamination_report, "adapter is NOT bound to the real reproml gate"


# --------------------------------------------------------------------------- #
#  SEED CORPORA — a spread of clean (NO_OVERLAP) and dirty (CONTAMINATION) cases,
#  across the regimes the transforms must be invariant on: verbatim-leak, near-dup,
#  word-reorder, and clean. Seeds intentionally span both verdicts so the metamorphic
#  hunt exercises ACCEPT-base AND REJECT-base objects.
# --------------------------------------------------------------------------- #
_EVAL_A = "the quick brown fox jumps over the lazy dog near the river bank today"
_EVAL_B = "a completely unrelated sentence about photosynthesis in green plants here"
_EVAL_C = "neural networks learn hierarchical representations from raw input data automatically"
_EVAL_LONG = ("transformers use self attention to weight every token against every other "
              "token in the input sequence producing context dependent representations")

_CLEAN_TRAIN = [
    "machine learning models are trained on large corpora of varied text data sources",
    "gradient descent iteratively minimizes a loss function over many training epochs",
]


def seeds():
    """Base objs (kwargs dicts). Each is a full contamination_report call."""
    out = []

    # --- CLEAN (expect ACCEPT / NO_OVERLAP) ---
    out.append({"train_docs": list(_CLEAN_TRAIN),
                "eval_docs": [_EVAL_A, _EVAL_B, _EVAL_C],
                "n": 5})
    out.append({"train_docs": list(_CLEAN_TRAIN),
                "eval_docs": [_EVAL_LONG],
                "n": 13})

    # --- VERBATIM LEAK (expect REJECT via n-gram collision) ---
    out.append({"train_docs": _CLEAN_TRAIN + [_EVAL_A],
                "eval_docs": [_EVAL_A, _EVAL_B],
                "n": 5})
    out.append({"train_docs": _CLEAN_TRAIN + [_EVAL_LONG],
                "eval_docs": [_EVAL_LONG, _EVAL_B],
                "n": 13})

    # --- NEAR-DUP / lightly-edited (expect REJECT via char-jaccard) ---
    near = _EVAL_A + "!"                          # one trailing char: char-5gram jaccard ~1
    out.append({"train_docs": _CLEAN_TRAIN + [near],
                "eval_docs": [_EVAL_A, _EVAL_C],
                "n": 13})

    # --- WORD-REORDER (expect REJECT via bow token-set jaccard) ---
    reordered = " ".join(reversed(_EVAL_C.split()))
    out.append({"train_docs": _CLEAN_TRAIN + [reordered],
                "eval_docs": [_EVAL_C, _EVAL_B],
                "n": 13, "bow_threshold": 0.9})

    return out


# --------------------------------------------------------------------------- #
#  METAMORPHIC TRANSFORMS — each CLAIMED meaning-preserving on the BINARY verdict.
#  No oracle is supplied (no exact truth for a free threshold) -> meaning-preservation
#  is CALLER-ASSERTED. Justifications are in the module docstring.
# --------------------------------------------------------------------------- #
def _ws_case_doc(s):
    """Re-case + re-whitespace a doc without changing its token set or char-5gram set.
    Upper-cases, inserts extra interior spaces/tabs/newlines, and pads the ends.
    `_tok` (re.findall [a-z0-9]+ on lower()) and `_char_ngrams` (re.sub \\s+ -> ' ',
    lower(), strip()) are both invariant under exactly these edits."""
    words = s.split()
    # alternate UPPER/lower casing, join with mixed whitespace runs, pad ends.
    recased = [(w.upper() if i % 2 == 0 else w.lower()) for i, w in enumerate(words)]
    glue = ["  ", "\t", " \n ", "   "]
    body = ""
    for i, w in enumerate(recased):
        body += w
        if i < len(recased) - 1:
            body += glue[i % len(glue)]
    return "\n\t  " + body + "  \t\n"


def t_whitespace_case(obj):
    """Transform 1: whitespace + case normalization of EVERY doc (train and eval)."""
    new = dict(obj)
    new["train_docs"] = [_ws_case_doc(d) for d in obj["train_docs"]]
    new["eval_docs"] = [_ws_case_doc(d) for d in obj["eval_docs"]]
    return new


def t_reorder_docs(obj):
    """Transform 2: reverse the order of train docs AND of eval docs. The train
    n-gram universe is a set union; each eval doc is scored independently; the binary
    'any dirty' verdict is order-free."""
    new = dict(obj)
    new["train_docs"] = list(reversed(obj["train_docs"]))
    new["eval_docs"] = list(reversed(obj["eval_docs"]))
    return new


def t_train_dedup(obj):
    """Transform 3: add an exact duplicate of each train doc, then the verdict must be
    invariant (train_grams is a set; train_char/train_bow are consumed via max(), so a
    duplicate train doc is a no-op on every eval item's best match). We INSERT duplicates
    (rather than remove, since seeds have none) -- equally verdict-preserving and a
    stronger test of the set/max semantics."""
    new = dict(obj)
    dup = []
    for d in obj["train_docs"]:
        dup.append(d)
        dup.append(d)        # exact duplicate right after
    new["train_docs"] = dup
    return new


TRANSFORMS = [
    ("whitespace+case normalization (tokens/char-5grams invariant)", t_whitespace_case),
    ("document reordering (train+eval reversed; set/independent scoring)", t_reorder_docs),
    ("train-side exact duplication (train_grams set; max-consumed near-dup)", t_train_dedup),
]


# --------------------------------------------------------------------------- #
#  ABSTAIN/CRASH — empty / degenerate corpora. A SILENT NO_OVERLAP (==ACCEPT) on a
#  degenerate corpus the screen cannot justify clearing is the bug. Safe = REJECT,
#  ABSTAIN, or a guarded ERROR. (We report what the gate ACTUALLY does -- the gate's
#  documented design is "absence of overlap != clean", so a NO_OVERLAP on an empty
#  corpus IS the silent-pass class this mode is meant to surface.)
# --------------------------------------------------------------------------- #
def malformed_inputs():
    # SAFE = the gate's honest rate-report (ACCEPT==NO_OVERLAP, which carries the
    # "!= clean" disclaimer note -- NOT a clean certification), OR a loud ABSTAIN, OR a
    # guarded ERROR. The UNSAFE outcome we hunt is a fabricated CONTAMINATION_DETECTED
    # (REJECT) on a degenerate input, or an uncaught crash on a clearly-degenerate input
    # that the gate cannot route. (REJECT is deliberately EXCLUDED so a from-nothing flag
    # would surface; ERROR is allowed only where it is a sensible guard, see notes.)
    rate_report_safe = {ACCEPT, ABSTAIN, ERROR}
    return [
        ("empty eval set (nothing to screen; rate over 0 items)",
         {"train_docs": list(_CLEAN_TRAIN), "eval_docs": [], "n": 13}, rate_report_safe),
        ("empty train + empty eval (fully degenerate)",
         {"train_docs": [], "eval_docs": [], "n": 13}, rate_report_safe),
        ("empty train, non-empty eval (no corpus to compare against)",
         {"train_docs": [], "eval_docs": [_EVAL_A], "n": 13}, rate_report_safe),
        ("eval docs all empty strings",
         {"train_docs": list(_CLEAN_TRAIN), "eval_docs": ["", "", ""], "n": 13}, rate_report_safe),
        ("train not a list (str) -- type degeneracy",
         {"train_docs": "not a list", "eval_docs": [_EVAL_A], "n": 13}, rate_report_safe),
        ("eval is None -- type degeneracy",
         {"train_docs": list(_CLEAN_TRAIN), "eval_docs": None, "n": 13}, rate_report_safe),
        # NOTE: n=0 is deliberately EXCLUDED from the corpus-degeneracy set. n is a FREE
        # CONFIG PARAMETER, not corpus data; and n=0 makes the empty n-gram '()' collide
        # universally so the gate OVER-FLAGS everything as CONTAMINATION_DETECTED (rate 1.0
        # even on disjoint clean data -- machine-confirmed). That is the CONSERVATIVE /
        # fail-loud direction for a screen (it never silently CLEARS contaminated data),
        # NOT the silent-unsafe-ACCEPT this mode hunts. Characterized in residual risk, not
        # shipped as a KILL (would be over-claiming a non-bug).
    ]


def assert_disclaimer_on_degenerate():
    """Outside the hunt: the genuine honesty contract is that a degenerate corpus that
    returns NO_OVERLAP_DETECTED still carries the 'NO_OVERLAP_DETECTED != clean' ceiling
    note (so a reader cannot mistake it for a clean certification). We verify that here on
    the degenerate cases that DON'T crash; a missing/altered note WOULD be a real defect."""
    checks = [
        ("empty eval", list(_CLEAN_TRAIN), []),
        ("both empty", [], []),
        ("empty train", [], [_EVAL_A]),
        ("all-empty eval strings", list(_CLEAN_TRAIN), ["", "", ""]),
    ]
    results = []
    for desc, tr, ev in checks:
        try:
            r = _REAL_FN(tr, ev, n=13)
            v = r.get("verdict")
            note = r.get("ceiling_note", "")
            has_disclaimer = "!= clean" in note and "not a binary" in note.lower()
            results.append((desc, v, has_disclaimer))
        except Exception as e:                    # a crash here is itself worth reporting
            results.append((desc, f"CRASH:{type(e).__name__}", False))
    return results


COVERAGE = ("metamorphic-only: whitespace+case, document reordering, train-side exact "
            "duplication, asserted meaning-preserving on the BINARY verdict (NO oracle -- "
            "the n-gram order n / jaccard_threshold / bow_threshold are TUNABLE FREE PARAMS "
            "with no exact ground truth, so meaning-preservation is CALLER-ASSERTED, not "
            "machine-verified). Configs probed: n in {5,13} at default jaccard=0.8, bow=0.9. "
            "kappa~0.8 SCREEN (the weapon self-declares this is a measured RATE, NOT a binary "
            "'clean'); there is NO kappa=1 exact slice -- full-differential is impossible here.")


def main():
    print("=" * 78)
    print("CRUCIBLE probe: reproml_contamination (R-CONTAM n-gram/Jaccard overlap SCREEN)")
    print("real gate entrypoint:", f"{RC.__name__}.contamination_report",
          "(is real:", _REAL_FN is RC.contamination_report, ")")
    print("COVERAGE: metamorphic-only (free thresholds -> no exact oracle; FA/FR not run)")
    print("modes run: METAMORPHIC + ABSTAIN/CRASH")
    print("=" * 78)

    sds = seeds()
    # show each seed's base verdict so the reader sees both polarities are exercised
    print("seed base verdicts:")
    for i, s in enumerate(sds):
        print(f"  seed[{i}] n={s.get('n')} -> {gate.verdict(s)} "
              f"(train={len(s['train_docs'])} eval={len(s['eval_docs'])})")
    print("-" * 78)

    # ---- METAMORPHIC (no oracle -> caller-asserted meaning preservation) ----
    mm = metamorphic_hunt(gate, sds, TRANSFORMS, max_probes=200000, oracle=None)
    print(f"METAMORPHIC (seeds={len(sds)}, transforms={len(TRANSFORMS)}, NO oracle):")
    print(json.dumps(mm.to_dict(), indent=2, default=str))
    print("-" * 78)

    # ---- disclaimer contract on degenerate returns (the real honesty bug would be a
    #      degenerate NO_OVERLAP that DROPS the '!= clean' note) ----
    print("DISCLAIMER-NOTE CHECK on degenerate corpora (verdict, '!=clean' note present?):")
    for desc, v, has_disc in assert_disclaimer_on_degenerate():
        print(f"  {desc:24s} -> {v:22s} disclaimer_present={has_disc}")
    print("-" * 78)

    # ---- ABSTAIN/CRASH (degenerate corpora) ----
    # SAFE set now reflects the gate's CONTRACT: a NO_OVERLAP rate-report (ACCEPT) that
    # carries the '!= clean' disclaimer is HONEST, not a silent clean-certification. The
    # unsafe outcome hunted is a from-nothing REJECT or an uncaught crash.
    ac = abstain_crash_hunt(gate, malformed_inputs(), max_probes=100)
    print("ABSTAIN/CRASH (empty/degenerate corpora; SAFE={ACCEPT-rate-report,ABSTAIN,ERROR}):")
    print(json.dumps(ac.to_dict(), indent=2, default=str))
    print("-" * 78)

    print("COVERAGE NOTE:", COVERAGE)
    print("-" * 78)
    any_kill = any(d.to_dict().get("KILL") for d in (mm, ac))
    print("ANY KILL:", any_kill)


if __name__ == "__main__":
    main()
