#!/usr/bin/env python3
"""CRUCIBLE probe of redcell_ctf: the CTF-SOLVE kappa=1 flag-equality gate.

TARGET: /Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/redcell/flag_verify.py
        function verify_flag(submitted, *, expected=, expected_sha256=, fmt=)
SLICE : the kappa=1 byte/hash-exact flag-equality check (NOT the auth policy).

We BLACK-BOX import and CALL the real gate. The oracle is an INDEPENDENT,
from-scratch re-derivation of the SAME intended meaning:

  A submitted flag is CORRECT iff:
    (1) if fmt=(pre,suf) is given, submitted startswith pre AND endswith suf, AND
    (2a) when `expected` is committed:        submitted == expected         (byte-exact), OR
    (2b) when `expected_sha256` is committed:  hashlib.sha256(submitted) hex == expected_sha256.lower()
  When NEITHER is committed, there is no committed answer -> the gate must NOT say VALID
  (truth = WRONG: nothing can validate against a missing committed answer).

The oracle uses Python's own `==` / from-scratch hashing (and, to be a genuinely FOREIGN
mechanism vs the gate's `hmac.compare_digest`, an independent byte-by-byte compare). It
never calls verify_flag. The gate ACCEPTs iff its returned dict has valid is True.

All inputs are synthetic/benign FLAG{...} strings.
"""
import sys
import os
import json
import hashlib

CRUCIBLE_DIR = "/Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/crucible"
REDCELL_DIR = "/Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/redcell"
sys.path.insert(0, CRUCIBLE_DIR)
sys.path.insert(0, REDCELL_DIR)

from crucible_harness import (  # noqa: E402
    GateAdapter, Oracle,
    false_accept_hunt, false_reject_hunt, metamorphic_hunt, abstain_crash_hunt,
    ACCEPT, REJECT, ABSTAIN, ERROR, CORRECT, WRONG,
)
from flag_verify import verify_flag  # noqa: E402  <-- the REAL gate


# --------------------------------------------------------------------------- #
#  GATE ADAPTER — black-box: call the real verify_flag, map its dict -> verdict
# --------------------------------------------------------------------------- #
def _to_verdict(raw):
    # raw is verify_flag's native dict. valid is True -> ACCEPT (the gate asserts the
    # flag is valid). valid is False -> REJECT. (NO_COMMITTED_ANSWER / WRONG_FORMAT both
    # carry valid=False -> REJECT, i.e. "does NOT validate" -- the gate's own semantics.)
    v = raw.get("valid")
    if v is True:
        return ACCEPT
    if v is False:
        return REJECT
    return ABSTAIN  # should not happen for this gate, but stay loud if it does


gate = GateAdapter("redcell_ctf.verify_flag", verify_flag, _to_verdict)


# --------------------------------------------------------------------------- #
#  INDEPENDENT ORACLE — from-scratch re-derivation of the SAME intended meaning.
#  Foreign mechanism: plain `==`, an explicit byte-by-byte loop, and a fresh
#  hashlib.sha256 invocation. NEVER calls verify_flag.
# --------------------------------------------------------------------------- #
def _bytes_equal(a: bytes, b: bytes) -> bool:
    """Independent (NON-constant-time, deliberately different mechanism) byte compare."""
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x != y:
            return False
    return True


def _independent_sha256_hex(s: str) -> str:
    # a fresh, independent hashing call (the gate also hashes, but truth here is the
    # equality of the *committed digest* to the *recomputed digest* — re-derived, not
    # delegated to the gate).
    return hashlib.sha256(s.encode()).hexdigest()


def _truth(obj):
    """Return CORRECT / WRONG for a flag-verification object, independently.

    obj keys mirror verify_flag kwargs: submitted, expected, expected_sha256, fmt.
    """
    submitted = obj.get("submitted")
    submitted = "" if submitted is None else str(submitted)
    expected = obj.get("expected")
    expected_sha256 = obj.get("expected_sha256")
    fmt = obj.get("fmt")

    # (1) format wrapper gate (mirrors the gate's intended meaning)
    if fmt is not None:
        try:
            pre, suf = fmt
        except Exception:
            return None  # malformed fmt -> oracle declines (gate-robustness, not equality slice)
        if not (submitted.startswith(pre) and submitted.endswith(suf)):
            return WRONG  # fails the committed format -> does not validate

    # (2) committed-answer equality
    if expected is not None:
        return CORRECT if _bytes_equal(submitted.encode(), str(expected).encode()) else WRONG
    if expected_sha256 is not None:
        recomputed = _independent_sha256_hex(submitted)
        committed = str(expected_sha256).lower()
        return CORRECT if _bytes_equal(recomputed.encode(), committed.encode()) else WRONG

    # (3) no committed answer -> nothing can be VALID; the correct verdict is "does not validate".
    return WRONG


# --------------------------------------------------------------------------- #
#  CONTROL GRID — >=3 known-good (CORRECT) and >=3 known-bad (WRONG), spanning
#  the regime: literal-expected path, hash path, format-wrapper path, empty,
#  long, unicode. Each control's truth is OBVIOUS by inspection.
# --------------------------------------------------------------------------- #
_F1 = "FLAG{x0r_15_n0t_crypt0}"
_F2 = "FLAG{a}"
_F3 = "CTF{unicode_éè}"
_F1_SHA = hashlib.sha256(_F1.encode()).hexdigest()
_F2_SHA = hashlib.sha256(_F2.encode()).hexdigest()

controls_good = [
    {"submitted": _F1, "expected": _F1},                         # literal exact
    {"submitted": _F2, "expected": _F2, "fmt": ("FLAG{", "}")},  # literal + format ok
    {"submitted": _F1, "expected_sha256": _F1_SHA},              # hash path exact
    {"submitted": _F3, "expected": _F3},                         # unicode exact
    {"submitted": "", "expected": ""},                           # empty == empty (edge)
]
controls_bad = [
    {"submitted": "FLAG{wrong}", "expected": _F1},               # literal mismatch
    {"submitted": _F2, "expected_sha256": _F1_SHA},              # hash mismatch
    {"submitted": "nope", "expected": _F2, "fmt": ("FLAG{", "}")},  # fails format
    {"submitted": "anything"},                                   # no committed answer
    {"submitted": _F1 + "x", "expected": _F1},                   # one-char-too-long
]

oracle = Oracle(
    "flageq-independent",
    _truth,
    is_independent=True,
    method=("from-scratch byte-by-byte equality + fresh hashlib.sha256 re-derivation of "
            "the committed-flag meaning; foreign to the gate's hmac.compare_digest engine; "
            "never calls verify_flag"),
    controls_good=controls_good,
    controls_bad=controls_bad,
)


# --------------------------------------------------------------------------- #
#  CANDIDATE STREAM — boundary-rich, deterministic. Spans: exact matches, single
#  byte/char flips, length deltas, prefix/suffix relationships, hash path,
#  format-wrapper path, empty/None, unicode, case, whitespace.
# --------------------------------------------------------------------------- #
def _candidates():
    out = []
    seen = set()

    def emit(obj):
        key = json.dumps(obj, sort_keys=True, default=str)
        if key not in seen:
            seen.add(key)
            out.append(obj)

    base_flags = [
        "FLAG{x0r_15_n0t_crypt0}",
        "FLAG{a}",
        "FLAG{}",
        "CTF{deadbeef}",
        "x",
        "",
        "FLAG{é}",
        "FLAG{A}",
        "FLAG{ab}",
        "key123",
    ]

    for exp in base_flags:
        exp_sha = hashlib.sha256(exp.encode()).hexdigest()
        # exact match (literal + hash)
        emit({"submitted": exp, "expected": exp})
        emit({"submitted": exp, "expected_sha256": exp_sha})
        # exact match + format wrapper (when it actually wraps FLAG{...})
        if exp.startswith("FLAG{") and exp.endswith("}"):
            emit({"submitted": exp, "expected": exp, "fmt": ("FLAG{", "}")})
            emit({"submitted": exp, "expected_sha256": exp_sha, "fmt": ("FLAG{", "}")})

        # near-misses: single-char mutations, length deltas, case, whitespace
        muts = set()
        if exp:
            muts.add(exp[:-1])                       # drop last
            muts.add(exp + "x")                      # append
            muts.add("x" + exp)                      # prepend
            muts.add(exp.upper())                    # case
            muts.add(exp.lower())
            muts.add(exp + " ")                      # trailing space
            muts.add(" " + exp)                      # leading space
            for i in range(min(len(exp), 6)):        # flip a few chars
                muts.add(exp[:i] + "_" + exp[i + 1:])
        else:
            muts.add("x")
        muts.discard(exp)  # keep these as NON-matches vs exp
        for m in muts:
            emit({"submitted": m, "expected": exp})
            emit({"submitted": m, "expected_sha256": exp_sha})
            if exp.startswith("FLAG{") and exp.endswith("}"):
                emit({"submitted": m, "expected": exp, "fmt": ("FLAG{", "}")})

        # cross pairs: submitted=base_flag vs a DIFFERENT expected
        for other in base_flags:
            if other != exp:
                emit({"submitted": exp, "expected": other})

        # None / missing-committed-answer / hash-case variants
        emit({"submitted": exp})                                  # no committed answer
        emit({"submitted": None, "expected": exp})                # None submitted
        emit({"submitted": exp, "expected_sha256": exp_sha.upper()})  # UPPER hash (gate lowercases committed)
        # format-wrapper edge: correct value but wrong wrapper claimed
        emit({"submitted": exp, "expected": exp, "fmt": ("XXX{", "}")})

    return out


# --------------------------------------------------------------------------- #
#  METAMORPHIC TRANSFORMS — claimed meaning-preserving (validated by the oracle
#  via the A11 guard, since we pass oracle=).
# --------------------------------------------------------------------------- #
def _t_literal_to_hash(obj):
    """If committed via `expected`, switch to the equivalent committed sha256.
    Meaning-preserving: the SAME submitted validates iff it equals expected iff its
    hash equals sha256(expected)."""
    if "expected" in obj and obj["expected"] is not None and "expected_sha256" not in obj:
        new = {k: v for k, v in obj.items() if k != "expected"}
        new["expected_sha256"] = hashlib.sha256(str(obj["expected"]).encode()).hexdigest()
        return new
    raise ValueError("transform inapplicable (needs a literal `expected`)")


def _t_hash_case(obj):
    """Uppercase the committed sha256 digest. Hex digests are case-insensitive, and the
    gate explicitly lowercases the committed digest -> meaning-preserving."""
    if obj.get("expected_sha256") is not None:
        new = dict(obj)
        new["expected_sha256"] = str(obj["expected_sha256"]).upper()
        return new
    raise ValueError("transform inapplicable (needs expected_sha256)")


def _t_redundant_fmt(obj):
    """Add a format wrapper the submitted ALREADY satisfies (FLAG{...}). Meaning-preserving
    only when submitted truly is wrapped; applied to such seeds only."""
    s = "" if obj.get("submitted") is None else str(obj["submitted"])
    if s.startswith("FLAG{") and s.endswith("}") and "fmt" not in obj:
        new = dict(obj)
        new["fmt"] = ("FLAG{", "}")
        return new
    raise ValueError("transform inapplicable (submitted not FLAG{...}-wrapped)")


TRANSFORMS = [
    ("literal->equivalent-hash", _t_literal_to_hash),
    ("uppercase-committed-digest", _t_hash_case),
    ("add-already-satisfied-fmt", _t_redundant_fmt),
]


# --------------------------------------------------------------------------- #
#  MALFORMED INPUTS — must ABSTAIN/REJECT/ERROR, never silently ACCEPT (valid=True).
# --------------------------------------------------------------------------- #
def _malformed():
    safe = {ABSTAIN, REJECT, ERROR}
    return [
        ("no committed answer at all", {"submitted": "FLAG{x}"}, safe),
        ("None submitted, no committed", {"submitted": None}, safe),
        ("expected=None expected_sha256=None explicit",
         {"submitted": "FLAG{x}", "expected": None, "expected_sha256": None}, safe),
        ("garbage committed digest (not hex/len)",
         {"submitted": "FLAG{x}", "expected_sha256": "not-a-real-digest"}, safe),
        ("empty committed digest",
         {"submitted": "FLAG{x}", "expected_sha256": ""}, safe),
    ]


# --------------------------------------------------------------------------- #
#  RUN ALL FOUR MODES
# --------------------------------------------------------------------------- #
def main():
    cands = _candidates()
    coverage = ("submitted/expected/expected_sha256/fmt over benign FLAG{{...}} strings: exact "
                "matches, single-char flips, length deltas, case, whitespace, prefix/suffix, "
                "hash path (+UPPER digest), format-wrapper path, empty/None, unicode; "
                "{n} unique candidates. NOT probed: adversarial unicode normalization, "
                "non-str expected types, huge inputs.").format(n=len(cands))

    print(f"[setup] candidates={len(cands)} controls_good={len(controls_good)} "
          f"controls_bad={len(controls_bad)}")
    sane, detail = oracle.is_sane()
    print(f"[setup] oracle.is_sane -> {sane}: {detail}")

    print("\n=== MODE 1: FALSE-ACCEPT (gate ACCEPT, oracle WRONG) ===")
    fa = false_accept_hunt(gate, oracle, cands, max_probes=100000, coverage_note=coverage)
    print(json.dumps(fa.to_dict(), default=str, indent=2))

    print("\n=== MODE 2: FALSE-REJECT (gate REJECT, oracle CORRECT) ===")
    fr = false_reject_hunt(gate, oracle, cands, max_probes=100000, coverage_note=coverage)
    print(json.dumps(fr.to_dict(), default=str, indent=2))

    print("\n=== MODE 3: METAMORPHIC (meaning-preserving transform must not flip) ===")
    # seeds: ACCEPTable & rejectable objs that the transforms can apply to.
    seeds = [c for c in cands if (c.get("expected") is not None) or (c.get("expected_sha256") is not None)]
    mm = metamorphic_hunt(gate, seeds, TRANSFORMS, max_probes=100000, oracle=oracle)
    print(json.dumps(mm.to_dict(), default=str, indent=2))

    print("\n=== MODE 4: ABSTAIN/CRASH (malformed must not silently ACCEPT) ===")
    ac = abstain_crash_hunt(gate, _malformed(), max_probes=1000)
    print(json.dumps(ac.to_dict(), default=str, indent=2))

    any_kill = any(d.get("KILL") for d in
                   (fa.to_dict(), fr.to_dict(), mm.to_dict(), ac.to_dict()))
    print(f"\n[result] ANY_KILL={any_kill}")


if __name__ == "__main__":
    main()
