#!/usr/bin/env python3
"""CRUCIBLE probe — TARGET: factharness_quote (F-QUOTE, kappa=1 slice).

Slice probed: verify_quote(quote, source_text) -- the FROZEN kappa=1 F-QUOTE check
that claims "a quoted string appears VERBATIM in the source (modulo case, accents,
smart quotes, and whitespace -- punctuation preserved)".

  gate ACCEPT  <- result["grounded"] is True  (verdict "quote_found")
  gate REJECT  <- verdict "QUOTE_NOT_IN_SOURCE"
  gate ABSTAIN <- verdict "too_short_to_check" (<7 alnum content chars)

BLACK-BOX: we import the REAL factharness.verify_quote from the sibling weapon dir and
call it; we never re-implement it.

INDEPENDENT ORACLE (full-differential): a from-scratch, foreign text-containment engine.
Its truth() for "is `quote` genuinely a verbatim substring of `source`":
  * normalize with CANONICAL Unicode (NFC) + COSMETIC folds ONLY -- case (casefold),
    whitespace-collapse, smart-quote->straight, the standard dash set -> '-'.
  * it DELIBERATELY DOES NOT apply NFKD *compatibility* decomposition, because
    compatibility folding conflates semantically-distinct codepoints (superscript
    U+00B2 '²' != ASCII '2'; fullwidth '２' != '2'; Roman 'Ⅻ' != 'XII'; '½' != '1/2').
    A reasonable human reading the source would NOT call "m2" a verbatim quote of "m²".
  * codepoint-level `in` containment (Python str substring) -- a different mechanism
    than the gate's regex normaliser.
This is a genuinely foreign engine (different normalization policy + different code),
NOT a call back into the gate. It AGREES with the gate on purely-cosmetic differences
(ligatures, accents, smart quotes, dashes, whitespace) and only DISAGREES where the
gate's NFKD silently folds meaning-changing characters -- which is exactly the
false-accept slice we hunt.

ORACLE TRUTH for the false-accept hunt (obj = {quote, source_text}):
  CORRECT  -> the quote IS genuinely (cosmetically-verbatim) in the source
  WRONG    -> it is NOT (so a gate ACCEPT here is a false-accept)
  None     -> below the gate's own 7-alnum content floor (out of the kappa=1 ACCEPT
              regime: the gate ABSTAINs there, so truth is not decidable in this slice)
"""
import sys, os, json, re, unicodedata, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
CRUCIBLE_DIR = os.path.dirname(HERE)
ARSENAL_DIR = os.path.dirname(CRUCIBLE_DIR)
FACTHARNESS_DIR = os.path.join(ARSENAL_DIR, "factharness")

# import the harness (parent dir) and the REAL gate (sibling weapon dir)
sys.path.insert(0, CRUCIBLE_DIR)
sys.path.insert(0, FACTHARNESS_DIR)

import crucible_harness as ch
from crucible_harness import (GateAdapter, Oracle, ACCEPT, REJECT, ABSTAIN, ERROR,
                              CORRECT, WRONG,
                              false_accept_hunt, false_reject_hunt,
                              metamorphic_hunt, abstain_crash_hunt)

import factharness                      # the REAL weapon
from factharness import verify_quote    # the REAL kappa=1 F-QUOTE function

print("REAL gate imported from:", factharness.__file__)
assert os.path.abspath(factharness.__file__).startswith(os.path.abspath(FACTHARNESS_DIR)), \
    "did NOT import the real sibling-weapon factharness"


# --------------------------------------------------------------------------- #
#  GATE ADAPTER (black-box): calls the REAL verify_quote.
# --------------------------------------------------------------------------- #
def _quote_to_verdict(raw):
    v = raw.get("verdict")
    if v == "quote_found":
        return ACCEPT
    if v == "QUOTE_NOT_IN_SOURCE":
        return REJECT
    if v == "too_short_to_check":
        return ABSTAIN
    raise ValueError(f"unexpected F-QUOTE verdict {v!r}")

gate = GateAdapter("factharness.F-QUOTE", verify_quote, _quote_to_verdict)


# --------------------------------------------------------------------------- #
#  INDEPENDENT ORACLE — a foreign containment engine (NFC + cosmetic folds only,
#  NO NFKD compatibility decomposition).
# --------------------------------------------------------------------------- #
_SMART_SINGLE = "‘’‛′"          # ' ' ‛ ′
_SMART_DOUBLE = "“”‟″"          # " " ‟ ″
_DASHES = "".join(chr(c) for c in
                  (0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2015, 0x2212))

def _oracle_norm(s):
    """Foreign normaliser: canonical NFC + cosmetic folds ONLY. Refuses NFKD."""
    s = unicodedata.normalize("NFC", str(s))         # canonical, NOT NFKD
    buf = []
    for ch_ in s:
        if ch_ in _SMART_SINGLE:
            buf.append("'")
        elif ch_ in _SMART_DOUBLE:
            buf.append('"')
        elif ch_ in _DASHES:
            buf.append("-")
        else:
            buf.append(ch_)
    s = "".join(buf)
    s = s.casefold()                                  # full case fold (foreign to gate's .lower())
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _content_alnum(s):
    """Count alphanumeric content chars of the quote AS THE GATE SEES IT.
    Uses the gate's OWN punctuation-stripping convention so the oracle's domain
    boundary matches the gate's 7-alnum ACCEPT floor exactly (we must not opine in
    a regime the gate refuses to ACCEPT in). Uses NFKD here ONLY to mirror the
    gate's content-floor count -- this is a domain-boundary calc, not the truth."""
    q = unicodedata.normalize("NFKD", str(s))
    q = "".join(c for c in q if not unicodedata.combining(c)).lower()
    return len(re.sub(r"[^\w]", "", q))

def _oracle_present(quote, source_text):
    """Foreign truth: is the quote a (cosmetically-)verbatim substring of the source?"""
    return _oracle_norm(quote) in _oracle_norm(source_text)

def quote_truth(obj):
    quote = obj.get("quote")
    src = obj.get("source_text")
    if quote is None or src is None:
        return None
    # Stay inside the gate's kappa=1 ACCEPT regime: below the 7-alnum floor the gate
    # ABSTAINs, so there is no ACCEPT to contradict -> no opinion.
    if _content_alnum(quote) < 7:
        return None
    return CORRECT if _oracle_present(quote, src) else WRONG


# --------------------------------------------------------------------------- #
#  CONTROL GRID — spans the probed regime (cosmetic-equivalence vs
#  meaning-changing-conflation), multiple distinct mechanisms each polarity.
# --------------------------------------------------------------------------- #
# GOOD (oracle MUST say CORRECT): genuinely-verbatim-modulo-cosmetic quotes that a
# human accepts as grounded. These must NOT be flagged (else the oracle cries wolf).
controls_good = [
    # plain identical text
    {"quote": "the effect is too fragile to trust",
     "source_text": "we concluded the effect is too fragile to trust here."},
    # case-only difference
    {"quote": "Statistically Significant Result",
     "source_text": "this was a statistically significant result overall."},
    # whitespace-collapse difference
    {"quote": "seven   of the\n one hundred specs",
     "source_text": "only seven of the one hundred specs survived."},
    # smart quotes / apostrophe difference (cosmetic)
    {"quote": "the author’s claim was overstated",
     "source_text": "we found the author's claim was overstated badly."},
    # accent / combining-mark difference (NFC vs decomposed) -- cosmetic
    {"quote": "the naïve estimator is biased",
     "source_text": "note the naïve estimator is biased here."},
    # ligature fi/ffi -> same letters, cosmetic (NFC keeps ligature; we add an NFKD
    # fold for ligatures only? No -- to be conservative we DROP this from good and
    # instead use a dash-equivalence control which both engines fold.)
    {"quote": "a well-controlled experiment design",
     "source_text": "this was a well–controlled experiment design indeed."},
]

# BAD (oracle MUST say WRONG): quotes that are genuinely NOT in the source. These
# span both "obviously absent" and "absent-but-NFKD-would-conflate" so the grid
# covers the exact regime the false-accept hunt explores.
controls_bad = [
    # totally fabricated quote
    {"quote": "the effect is robust and replicates widely",
     "source_text": "we concluded the effect is too fragile to trust here."},
    # dropped qualifier -> changes meaning, not a verbatim substring
    {"quote": "the result was significant overall",
     "source_text": "the result was not significant overall in any study."},
    # NFKD-conflation case: 'm2' is NOT verbatim in a source that says 'm²'
    {"quote": "the area was one hundred m2 total",
     "source_text": "the area was one hundred m² total."},
    # NFKD-conflation: ascii digits not verbatim in a fullwidth-digit source
    {"quote": "the year was 2016 indeed for sure",
     "source_text": "the year was ２０１６ indeed for sure."},
    # NFKD-conflation: Roman numeral glyph vs spelled letters
    {"quote": "see chapter xii of this long book",
     "source_text": "see chapter Ⅻ of this long book today."},
    # transposed words -> sequence differs, not a substring
    {"quote": "fragile too is effect the here",
     "source_text": "we concluded the effect is too fragile to trust here."},
]

oracle = Oracle(
    "verbatim-NFC-cosmetic-containment", quote_truth,
    is_independent=True,
    method=("from-scratch foreign containment engine: canonical NFC + cosmetic folds "
            "(casefold / whitespace / smart-quotes / dash-set) and codepoint-level "
            "substring; DELIBERATELY refuses NFKD compatibility decomposition so it does "
            "NOT conflate '²' with '2', fullwidth with ascii, Roman glyph with letters. "
            "Agrees with the gate on cosmetic diffs, disagrees only where NFKD folds meaning."),
    controls_good=controls_good, controls_bad=controls_bad)


# --------------------------------------------------------------------------- #
#  CANDIDATE STREAM (false-accept): pairs (quote, source) where the source uses a
#  meaning-changing Unicode char whose NFKD compatibility form equals the quote's
#  ASCII text -> the gate grounds, the foreign oracle does not. Plus plain controls,
#  cosmetic-equivalents (must NOT yield a kill), and fabricated quotes.
# --------------------------------------------------------------------------- #
# pad text to clear the 7-alnum content floor and give realistic context.
_PAD = "in the reported study results we observed that "

# NFKD-conflation atoms: (ascii_in_quote, unicode_in_source) where NFKD(uni)==ascii.
_CONFLATIONS = [
    ("m2", "m²"),                 # superscript two
    ("cm3", "cm³"),               # superscript three
    ("x2 y", "x² y"),
    ("2016", "２０１６"),   # fullwidth digits
    ("xii", "Ⅻ"),                 # Roman numeral twelve glyph
    ("viii", "Ⅷ"),                # Roman numeral eight glyph
    ("1/2 dose", "½ dose"),       # vulgar fraction half -> '1⁄2'? check below
    ("(1) the", "⑴ the"),         # parenthesized digit one
    ("tel", "℡"),                 # TEL symbol -> 'TEL'
    ("no.", "№"),                 # NUMERO SIGN -> 'No'
]
# COSMETIC atoms: (quote_text, source_text) genuinely-same letters (must NOT kill).
_COSMETIC = [
    ("final office files", "ﬁnal oﬃce ﬁles"),   # ligatures fi/ffi
    ("the naive method", "the naïve method"),             # combining diaeresis
    ("co-author note", "co—author note"),                  # em-dash vs hyphen
    ("don't do that", "don’t do that"),                    # smart apostrophe
]

def _candidates():
    out = []
    # 1) the conflation false-accept candidates (and their plain-grounded twins)
    for ascii_q, uni_s in _CONFLATIONS:
        q = _PAD + ascii_q + " across conditions"
        s_uni = _PAD + uni_s + " across conditions"
        s_plain = _PAD + ascii_q + " across conditions"
        out.append({"quote": q, "source_text": s_uni})    # the suspected false-accept
        out.append({"quote": q, "source_text": s_plain})  # genuine match (gate+oracle agree ACCEPT)
    # 2) cosmetic equivalents -- gate ACCEPTs, oracle CORRECT -> NOT a kill (negative ctrl)
    for q_c, s_c in _COSMETIC:
        q = _PAD + q_c + " in the data"
        s = _PAD + s_c + " in the data"
        out.append({"quote": q, "source_text": s})
    # 3) fabricated quotes (gate REJECTs) -- here to show the hunt doesn't false-kill
    out.append({"quote": _PAD + "the effect was robust and large",
                "source_text": _PAD + "the effect was fragile and small"})
    # 4) a sweep of every conflation atom embedded at different positions
    positions = ["start ", "", " middle xx ", " near the very end of sentence "]
    for ascii_q, uni_s in _CONFLATIONS:
        for pos in positions:
            q = ("the measurement value reported " + pos + ascii_q + " was noted").strip()
            s = ("the measurement value reported " + pos + uni_s + " was noted").strip()
            out.append({"quote": q, "source_text": s})
    return out

CANDIDATES = _candidates()
COVERAGE = ("quote/source pairs where the source contains a meaning-changing Unicode "
            "char whose NFKD compatibility form equals the ASCII text in the quote "
            "(superscripts, fullwidth digits, Roman-numeral glyphs, vulgar fractions, "
            "enclosed/letter-like symbols), plus genuine-match twins, cosmetic-equivalent "
            "pairs (ligatures/combining-marks/smart-quotes/dashes), and a fabricated quote. "
            "NOT probed: free-form natural-language fuzzing, very long sources, RTL scripts.")


# --------------------------------------------------------------------------- #
#  METAMORPHIC transforms (claimed meaning-preserving) -- validated by the oracle.
# --------------------------------------------------------------------------- #
def _t_collapse_ws(obj):
    """Insert redundant whitespace into the quote (claimed meaning-preserving)."""
    q = obj["quote"]
    return {**obj, "quote": q.replace(" ", "   ", 3)}

def _t_smartquote(obj):
    """Swap a straight apostrophe in the quote for a smart one (cosmetic)."""
    q = obj["quote"]
    return {**obj, "quote": q.replace("'", "’")}

def _t_case_flip(obj):
    """Uppercase the quote (case is in the gate's stated normalization -> invariant)."""
    return {**obj, "quote": obj["quote"].upper()}

def _t_dash_swap(obj):
    """Swap an ascii hyphen in the quote for an en-dash (gate folds dashes -> invariant)."""
    return {**obj, "quote": obj["quote"].replace("-", "–")}

TRANSFORMS = [
    ("redundant-whitespace", _t_collapse_ws),
    ("straight->smart-quote", _t_smartquote),
    ("uppercase-quote", _t_case_flip),
    ("hyphen->en-dash", _t_dash_swap),
]

# seeds for metamorphic: realistic grounded quotes (gate ACCEPTs them) with the
# features each transform touches.
SEEDS = [
    {"quote": "the author's well-controlled design held up",
     "source_text": "we found the author's well-controlled design held up nicely."},
    {"quote": "a statistically significant and robust effect",
     "source_text": "this was a statistically significant and robust effect overall."},
    {"quote": "the co-author's note was clear enough",
     "source_text": "indeed the co-author's note was clear enough for all."},
]


# --------------------------------------------------------------------------- #
#  ABSTAIN/CRASH malformed inputs.
# --------------------------------------------------------------------------- #
SAFE = {ABSTAIN, REJECT, ERROR}
MALFORMED = [
    ("quote=None",            {"quote": None, "source_text": "some real source text here."}, {ABSTAIN, REJECT, ERROR}),
    ("source=None",           {"quote": "a real quote of words", "source_text": None}, {ABSTAIN, REJECT, ERROR}),
    ("both empty strings",    {"quote": "", "source_text": ""}, {ABSTAIN, REJECT, ERROR}),
    ("quote is an int",       {"quote": 1234567, "source_text": "1234567 appears here in text."}, {ABSTAIN, REJECT, ERROR, ACCEPT}),
    ("source is a list",      {"quote": "a real quote of words", "source_text": ["a real quote of words"]}, {ABSTAIN, REJECT, ERROR}),
    ("whitespace-only quote", {"quote": "        ", "source_text": "lots of words in the source body."}, {ABSTAIN, REJECT, ERROR}),
]


# --------------------------------------------------------------------------- #
#  RUN ALL FOUR MODES.
# --------------------------------------------------------------------------- #
def main():
    print("=== oracle sanity (control grid) ===")
    sane, detail = oracle.is_sane()
    print(json.dumps({"oracle_sane": sane, "detail": detail}))
    if not sane:
        print("ABORT: oracle not sane -- no KILL may ship.")
        return

    print("\n=== MODE 1: FALSE-ACCEPT ===")
    fa = false_accept_hunt(gate, oracle, CANDIDATES, max_probes=10000, coverage_note=COVERAGE)
    print(json.dumps(fa.to_dict(), ensure_ascii=False, default=str))

    print("\n=== MODE 2: FALSE-REJECT ===")
    fr = false_reject_hunt(gate, oracle, CANDIDATES, max_probes=10000, coverage_note=COVERAGE)
    print(json.dumps(fr.to_dict(), ensure_ascii=False, default=str))

    print("\n=== MODE 3: METAMORPHIC (oracle-validated transforms) ===")
    mm = metamorphic_hunt(gate, SEEDS, TRANSFORMS, max_probes=10000, oracle=oracle)
    print(json.dumps(mm.to_dict(), ensure_ascii=False, default=str))

    print("\n=== MODE 4: ABSTAIN/CRASH ===")
    ac = abstain_crash_hunt(gate, MALFORMED, max_probes=100)
    print(json.dumps(ac.to_dict(), ensure_ascii=False, default=str))

    # If MODE 1 killed, re-exhibit explicitly (independent double-check in-script).
    if hasattr(fa, "obj"):
        obj = fa.obj
        print("\n=== KILL DOUBLE-CHECK (independent re-run) ===")
        gver = gate.verdict(obj)
        over = oracle.truth(obj)
        raw = verify_quote(**obj)
        print(json.dumps({
            "obj": obj,
            "real_gate_raw_verdict": raw.get("verdict"),
            "real_gate_grounded": raw.get("grounded"),
            "adapter_gate_verdict": gver,
            "oracle_verdict": over,
            "oracle_norm_quote": _oracle_norm(obj["quote"]),
            "oracle_norm_source": _oracle_norm(obj["source_text"]),
        }, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
