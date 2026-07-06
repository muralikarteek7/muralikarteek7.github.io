#!/usr/bin/env python3
"""FACTHARNESS gate self-tests. A gate that can't fail is not a gate.

Covers (per kickoff): (a) PASS a grounded claim, (b) CATCH a fabricated quote,
(c) CATCH a fabricated number / wrong-author cite -- INCL. the 3 SOCIUS audit
break-cases as LOCKED regression tests, (d) ABSTAIN on ambiguous entailment.
Plus new HARDENING tests added in the promotion. Soundness (no false 'grounded')
is cardinal.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from factharness import (ground, verify_quote, verify_number, verify_bibliography)

_SRC = ("Steegen, Tuerlinckx, Gelman and Vanpaemel (2016). Increasing transparency "
        "through a multiverse analysis. We reanalysed Durante et al. (2013). For the "
        "religiosity effect in Study 1, only 7 of the 120 specifications were "
        "statistically significant, leading us to conclude the effect is too fragile.")
_META = {"authors": "Steegen Tuerlinckx Gelman Vanpaemel", "year": 2016}

n = 0
def ok(cond, msg):
    global n
    assert cond, "FAIL: " + msg
    n += 1


# ---- F-QUOTE: grounds real quote; catches fabrication --------------------- #
ok(verify_quote("too fragile", _SRC)["grounded"] is True, "real quote grounds")
ok(verify_quote("the effect is robust and replicates widely", _SRC)["grounded"] is False,
   "fabricated quote caught")
# REGRESSION A1: punctuation-stripped fabrication must NOT match the qualified source
ok(verify_quote("significant effect p 0.001",
                "The results showed a significant effect (p < 0.001).")["grounded"] is False,
   "A1: 'p 0.001' must not match '(p < 0.001)'")
ok(verify_quote("a Significant   Effect (p < 0.001)",
                "showed a significant effect (p < 0.001).")["grounded"] is True,
   "A1: genuine verbatim quote (modulo ws/case) still grounds")
# REGRESSION A2 (CRUCIBLE F-QUOTE false-accept): NFKD compatibility folding made 'm2'
#   match the superscript 'm-squared' (U+00B2). Switched to NFD (canonical only) so
#   meaning-changing compatibility chars are NOT folded to ASCII. Must NOT ground now.
ok(verify_quote("the area was one hundred m2 total",
                "the area was one hundred m² total.")["grounded"] is False,
   "A2: 'm2' must NOT match superscript 'm²' (no NFKD compatibility fold)")
ok(verify_quote("the area was one hundred m2 total",
                "the area was one hundred m2 total.")["grounded"] is True,
   "A2: a genuinely-verbatim 'm2' vs 'm2' source STILL grounds (no over-correction)")
# preserve accent folding under the new NFD path: 'naive' must still match 'naive-with-diaeresis'
ok(verify_quote("the naive estimator is biased",
                "note the naïve estimator is biased here.")["grounded"] is True,
   "A2: accent fold preserved -- 'naive' still matches 'naïve' under NFD")
# REGRESSION B (CRUCIBLE F-QUOTE abstain-crash): a non-str source_text was str()'d to its
#   repr, so a list source matched the quote against the repr -> a false ACCEPT on garbage.
#   Type guard now refuses non-string input; must NEVER ground.
ok(verify_quote("a real quote of words", ["a real quote of words"])["grounded"] is False,
   "B: list source_text must NOT ground (non-string input guarded)")
ok(verify_quote("a real quote of words", ["a real quote of words"])["verdict"] != "quote_found",
   "B: list source_text never returns 'quote_found'")
ok(verify_quote(["a real quote of words"], "a real quote of words is here")["grounded"] is False,
   "B: list quote must NOT ground (non-string input guarded)")
# ---- CRUCIBLE EXACT EXHIBITS (locked verbatim from the CRUCIBLE report) ---- #
# These freeze the precise reproductions CRUCIBLE confirmed, so the exact inputs
# from the report can never silently regress (not just the principle).
# Exhibit 1 (BUG1 / A2): the ellipsis-prefixed superscript pair must REJECT.
ok(verify_quote("… m2 across conditions",
                "… m² across conditions")["grounded"] is False,
   "CRUCIBLE-1: '… m2' must NOT match superscript '… m²' (NFD, no compatibility fold)")
ok(verify_quote("… m2 across conditions",
                "… m² across conditions")["verdict"] != "quote_found",
   "CRUCIBLE-1: superscript pair never returns 'quote_found'")
# Exhibit 2 (BUG2 / B): the list-source case must ABSTAIN/ERROR, never ACCEPT.
ok(verify_quote("a real quote of words",
                ["a real quote of words"])["verdict"] == "ERROR_NON_STRING_INPUT",
   "CRUCIBLE-2: list source_text must return ERROR_NON_STRING_INPUT (abstain, never accept)")

# ---- F-NUMBER: grounds real number; catches fabrication ------------------- #
ok(verify_number("120", _SRC)["grounded"] is True, "real number grounds")
ok(verify_number("999", _SRC)["grounded"] is False, "fabricated number caught")
ok(verify_number("7", _SRC, also_require="significant")["grounded"] is True,
   "number + context grounds")
ok(verify_number("17", "there were 7 of 120 specs")["grounded"] is False,
   "boundary: 7 not inside 17")
# REGRESSION A3: '7' must NOT match inside the decimal '7.5'
ok(verify_number("7", "Effect size was 7.5 points.")["grounded"] is False,
   "A3: 7 not inside 7.5")
ok(verify_number("5", "the mean was 5.8")["grounded"] is False, "A3: 5 not inside 5.8")
ok(verify_number("7", "there were 7 specs")["grounded"] is True, "standalone 7 grounds")
ok(verify_number("7", "the total was 7.")["grounded"] is True, "sentence-final 7. grounds")
# thousands-comma: a TRUE number must ground regardless of grouping (soundness)
ok(verify_number("2213", "we surveyed 2,213 women")["grounded"] is True, "2,213 grounds")
ok(verify_number("2,213", "2213 women provided data")["grounded"] is True, "2213 grounds")
ok(verify_number("5.8", "about 5.8% of specs")["grounded"] is True, "decimal % grounds")

# ---- F-CITE: matches correct cite; catches wrong author/year -------------- #
ok(verify_bibliography("Steegen et al.", 2016, _META)["grounded"] is True, "correct cite matches")
ok(verify_bibliography("Scott Pound", 2015,
                       {"authors": "Isabel M. Scott, Nicholas Pound", "year": 2015})["grounded"] is True,
   "two real authors match")
ok(verify_bibliography("Steegen et al.", 1999, _META)["grounded"] is False, "wrong year caught")
# REGRESSION B-CRITICAL: connector 'and' must NOT bridge different authors
ok(verify_bibliography("Smith and Jones", 2016,
                       {"authors": "Brown and Williams", "year": 2016})["grounded"] is False,
   "B-CRITICAL: Smith and Jones != Brown and Williams")
ok(verify_bibliography("Doe and Roe", 2016, _META)["grounded"] is False, "wrong authors caught")
# REGRESSION B1/B2: 3-char fragments must NOT substring-match real names
ok(verify_bibliography("Fra Gel Van", 2016, _META)["grounded"] is False, "B1: fragments don't match")
ok(verify_bibliography("And Ste Lin", 2016, _META)["grounded"] is False, "B2: fragments don't match")

# ---- END-TO-END overall verdicts ----------------------------------------- #
good = ground({"text": "Steegen found 7 of 120 specs significant.",
               "source_text": _SRC, "quote": "too fragile",
               "numbers": [{"value": "7", "context": "significant"}],
               "claimed_authors": "Steegen et al.", "claimed_year": 2016,
               "source_metadata": _META})
ok(good["overall"] == "GROUNDED", "(a) grounded claim -> GROUNDED")

fab = ground({"text": "Steegen said the effect is robust.", "source_text": _SRC,
              "quote": "the effect is robust and replicates widely"})
ok(fab["overall"] == "FABRICATION_FLAG", "(b) fabricated quote -> FABRICATION_FLAG")
ok(fab["candidate_causes"] is not None and "fraud" not in " ".join(fab["candidate_causes"]).lower(),
   "(b) flag lists candidate causes and NEVER says fraud")

miss = ground({"text": "Some claim.", "source_text": None})
ok(miss["overall"] == "ABSTAIN", "(c) no source -> ABSTAIN")

badcite = ground({"text": "Per Smith 2016 ...", "source_text": _SRC,
                  "claimed_authors": "Smith and Jones", "claimed_year": 2016,
                  "source_metadata": _META})
ok(badcite["overall"] == "FABRICATION_FLAG", "(c) wrong-author cite -> FABRICATION_FLAG")

# (d) ABSTAIN on ambiguous entailment (judge uncertain, nothing frozen grounded)
amb = ground({"text": "paraphrase, no verbatim quote", "source_text": _SRC,
              "entailment_verdict": {"verdict": "uncertain", "judge_model": "sonnet",
                                     "rationale": "cannot tell from the source"}})
ok(amb["overall"] == "ABSTAIN", "(d) uncertain entailment -> ABSTAIN")

ent = ground({"text": "paraphrase, source contradicts", "source_text": _SRC,
              "entailment_verdict": {"verdict": "not_entailed", "judge_model": "sonnet",
                                     "rationale": "source says fragile, claim says strong"}})
ok(ent["overall"] == "CONTRADICTED_BY_SOURCE", "(d) not_entailed -> CONTRADICTED_BY_SOURCE")

# ---- AUDIT REGRESSIONS (cross-model Sonnet audit, 2026-06-20) -------------- #
# D2 (HIGH, kappa=1 breach): unicode MINUS U+2212 was stripped -> a sign-flipped
#   number grounded against a positive source. Must NOT ground now.
ok(verify_number(chr(0x2212) + "7", "The study found 7 cases.")["grounded"] is False,
   "D2: unicode minus -7 must NOT match positive 7 in source")
ok(verify_number(chr(0x2212) + "7", "The study found -7 cases.")["grounded"] is True,
   "D2: unicode minus -7 SHOULD match an ASCII -7 in source")
ok(ground({"text": "study found -7", "source_text": "The study found 7 cases of improvement.",
           "numbers": [{"value": chr(0x2212) + "7"}]})["overall"] != "GROUNDED",
   "D2 end-to-end: sign-flipped number must not yield GROUNDED")
# D3 (kappa=1 context): also_require was a raw substring -> 'treat' matched 'untreated'.
ok(verify_number("7", "The untreated group had 7 participants.", also_require="treat")["grounded"] is False,
   "D3: also_require 'treat' must not match inside 'untreated'")
ok(verify_number("7", "The 7 tests were not significant.", also_require="significant")["grounded"] is True,
   "D3: 'significant' IS a standalone word here (boundary match still finds it)")
ok(verify_number("7", "The 7 tests were insignificant.", also_require="sign")["grounded"] is False,
   "D3: 'sign' must not match inside 'insignificant'")
# D1 (bib): name particles must not ground as author tokens.
ok(verify_bibliography("van", 2016, {"authors": "van der Patten", "year": 2016})["grounded"] is False,
   "D1: particle 'van' alone must not match 'van der Patten'")
ok(verify_bibliography("von", 1836, {"authors": "Alexander von Humboldt", "year": 1836})["grounded"] is False,
   "D1: particle 'von' alone must not match 'von Humboldt'")
ok(verify_bibliography("der", 2016, {"authors": "van der Patten", "year": 2016})["grounded"] is False,
   "D1: particle 'der' alone must not match 'van der Patten'")
# ...but a REAL surname alongside a particle still grounds (no over-correction)
ok(verify_bibliography("Humboldt", 1836, {"authors": "Alexander von Humboldt", "year": 1836})["grounded"] is True,
   "D1: a real surname still grounds (particles dropped, not the whole name)")

# ---- NEW HARDENING tests added in the promotion --------------------------- #
# H1: entailment 'entailed' must NEVER upgrade to a kappa=1 GROUNDED on its own
#     (it is GROUNDED_BY_JUDGMENT -- weaker -- when no frozen check grounded it).
ej = ground({"text": "paraphrase only", "source_text": _SRC,
             "entailment_verdict": {"verdict": "entailed", "judge_model": "sonnet",
                                    "rationale": "supported"}})
ok(ej["overall"] == "GROUNDED_BY_JUDGMENT", "H1: judge-only -> GROUNDED_BY_JUDGMENT, not GROUNDED")
ok(ej["layer1_frozen_checks_kappa1"] == [], "H1: no frozen check fired")

# H2: a FAILED frozen check OVERRIDES an 'entailed' judge -> still FABRICATION_FLAG
#     (the judge cannot launder an invented quote past the frozen gate).
override = ground({"text": "claims a quote", "source_text": _SRC,
                   "quote": "this exact phrase is not in the source at all",
                   "entailment_verdict": {"verdict": "entailed", "judge_model": "sonnet",
                                          "rationale": "gist is fine"}})
ok(override["overall"] == "FABRICATION_FLAG",
   "H2: failed frozen check overrides 'entailed' judge")

# H3: string-form convenience API works and abstains with no source/checks
ok(ground("a bare claim", source_text=None)["overall"] == "ABSTAIN", "H3: string API + no source -> ABSTAIN")

# H4: kappa labels are present and strictly separated on every result
ok(good["kappa_note"] and "kappa=1" in good["kappa_note"] and "kappa=0" in good["kappa_note"],
   "H4: kappa labels reported")
ok(all(c["kappa"] == 1 for c in good["layer1_frozen_checks_kappa1"]), "H4: layer1 strictly k=1")
ok(good["bibliographic_check_kappa0p7"]["kappa"] == 0.7, "H4: F-CITE strictly k=0.7")

print(f"FACTHARNESS selftest_all: PASS ({n} assertions) -- grounds real quote/number/cite; "
      "FLAGS fabricated quote/number/wrong-author cite (incl. 3 SOCIUS audit regressions A1/A3/"
      "B-CRITICAL); ABSTAINS on missing source + uncertain entailment; judge can never launder a "
      "failed frozen check; kappa separation strict.")
