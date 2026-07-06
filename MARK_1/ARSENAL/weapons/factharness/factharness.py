#!/usr/bin/env python3
"""FACTHARNESS — the Helmet's university-wide grounding / fabrication core facility.

PROMOTED + HARDENED from SOCIUS S-GROUND (socius/ground_verify.py). This is the
institutionalized arm of the Integrity Office: every department + the Provost call
`ground(...)`; every shipped prose claim is routed through it (ground or abstain).

TWO LAYERS, each labelled by its REAL kappa (strict separation, non-waivable):

  LAYER 1 — FABRICATION DETECTOR (kappa=1, FROZEN, offline, self-tested).
    Given a claim + the *fetched* text of its cited source, deterministically check:
      * F-QUOTE  (k=1)   a quoted string appears VERBATIM in the source
      * F-NUMBER (k=1)   a cited number appears in the source (boundary-safe)
      * F-CITE   (k=0.7) claimed authors/year match the source's bibliography (advisory)
    A false "grounded" is detectable: change the quote/number/author and it flips.

  LAYER 2 — ENTAILMENT JUDGMENT (kappa=0, ARMOR, NOT machine-verified).
    "Does the source SUPPORT the paraphrase?" is NLI -> a cross-model judge
    (a model != the generator). This module only RECORDS that verdict and abstains
    when the judge is uncertain. Entailment is ALWAYS reported kappa=0.

HONESTY CEILING (non-waivable):
  * Grounded != true       (checks support by the supplied source, not correctness of the source)
  * FABRICATION_FLAG != fraud (reports "does not check against the supplied source" + candidate causes)
  * Entailment is kappa=0  (cross-model judge; unsure -> ABSTAIN)

The 3 SOCIUS Round-2 audit fixes (A1 quote-normaliser, A3 number boundary,
B-CRITICAL bibliography substring) are carried forward and locked as regression
tests in selftest_all.py. A promotion that drops a fix is a regression.
"""
import sys, json, re, unicodedata


# --------------------------------------------------------------------------- #
#  normalisers
# --------------------------------------------------------------------------- #
def _norm(s):
    """Lowercase, strip accents, collapse whitespace, drop most punctuation.
    Used for NUMBER and BIBLIOGRAPHY token matching (not for verbatim quotes)."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    # unicode dashes AND the U+2212 MINUS SIGN -> hyphen (audit fix D2: U+2212 was
    # outside the dash range and got stripped to a space, dropping a number's sign).
    s = re.sub(r"[‐-―−]", "-", s)
    s = re.sub(r"[^\w\s%.\-]", " ", s)                # keep word chars, %, ., -
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _norm_quote(s):
    """PUNCTUATION-PRESERVING normalisation for VERBATIM quote matching.
    Only case, unicode accents, smart quotes/dashes, and whitespace are normalised
    -- structural punctuation (parentheses, <, >, =, commas) is KEPT, so a quote that
    drops a qualifier ('p 0.001' vs '(p < 0.001)') does NOT spuriously match.
    (Carries SOCIUS audit fix A1.)

    NORMALIZATION CONTRACT (the documented kappa=1 'verbatim modulo cosmetics' folds):
      * case            -> lowercase
      * accents/diacritics -> folded via CANONICAL decomposition (NFD) + combining-mark
                          strip, so 'naive' == 'naive-with-diaeresis' ('naïve').
      * smart quotes    -> straight (' " )
      * unicode dashes  -> ASCII hyphen
      * whitespace runs -> single space, trimmed
    DELIBERATELY NOT FOLDED (audit fix A2, CRUCIBLE F-QUOTE false-accept): COMPATIBILITY
    equivalences are NOT applied. We use NFD (canonical) -- never NFKD (compatibility) --
    so semantically-distinct codepoints stay distinct: superscript 'm-squared' (U+00B2)
    is NOT folded to 'm2'; fullwidth digits are NOT folded to ASCII; vulgar fractions
    ('1/2') and Roman-numeral glyphs are NOT folded to letters/ASCII. A reasonable human
    does NOT read 'm2' as a verbatim quote of 'm-squared', so the gate must not ground it."""
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = re.sub(r"[‐-―]", "-", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# --------------------------------------------------------------------------- #
#  F-QUOTE  (kappa = 1)
# --------------------------------------------------------------------------- #
def verify_quote(quote, source_text):
    """Frozen: is the quoted string present VERBATIM in the source (modulo case,
    accents, smart quotes, and whitespace -- punctuation preserved)?"""
    # TYPE GUARD (audit fix B, CRUCIBLE F-QUOTE abstain-crash): a non-str quote or
    # source must NEVER ground. Previously _norm_quote(str(x)) stringified a list to
    # its repr, so a list source could match the quote against its own repr -> a
    # silent false ACCEPT on garbage. Loudly abstain instead.
    if not isinstance(quote, str) or not isinstance(source_text, str):
        return {"check": "F-QUOTE", "kappa": 1, "verdict": "ERROR_NON_STRING_INPUT",
                "grounded": False}
    q = _norm_quote(quote)
    if len(re.sub(r"[^\w]", "", q)) < 7:   # require >=7 alphanumeric chars of content
        return {"check": "F-QUOTE", "kappa": 1, "verdict": "too_short_to_check",
                "grounded": False}
    present = q in _norm_quote(source_text)
    return {"check": "F-QUOTE", "kappa": 1, "quote": quote,
            "grounded": bool(present),
            "verdict": "quote_found" if present else "QUOTE_NOT_IN_SOURCE"}


# --------------------------------------------------------------------------- #
#  F-NUMBER  (kappa = 1)
# --------------------------------------------------------------------------- #
def _strip_thousands(s):
    """Remove digit-grouping commas ('2,213'->'2213'). Cardinal property: NEVER
    falsely accuse -- a true number written with a thousands separator must ground."""
    return re.sub(r"(?<=\d),(?=\d)", "", str(s))


def verify_number(number, source_text, also_require=None):
    """Frozen: does the cited number appear in the source text? boundary-safe so
    '7' does not match inside '17' or '7.5' (carries SOCIUS audit fix A3).
    Optionally require a nearby keyword (`also_require`)."""
    src = _norm(_strip_thousands(source_text))
    num = _norm(_strip_thousands(number))
    pat = r"(?<!\d)(?<!\d\.)" + re.escape(num) + r"(?!\d)(?!\.\d)"
    found = re.search(pat, src) is not None
    ctx_ok = True
    if also_require is not None:
        # word-boundary context match (audit fix D3: a raw substring let 'treat' match
        # inside 'untreated' and 'significant' inside 'not significant').
        ctx_pat = r"(?<!\w)" + re.escape(_norm(also_require)) + r"(?!\w)"
        ctx_ok = re.search(ctx_pat, src) is not None
    return {"check": "F-NUMBER", "kappa": 1, "number": str(number),
            "also_require": also_require,
            "grounded": bool(found and ctx_ok),
            "verdict": "number_found" if (found and ctx_ok) else "NUMBER_NOT_IN_SOURCE"}


# --------------------------------------------------------------------------- #
#  F-CITE  (kappa = 0.7, advisory)
# --------------------------------------------------------------------------- #
# connector / abbreviation words that are NOT author names (audit break
# B-CRITICAL: 'and' was being treated as a valid 3-char author token).
# includes name PARTICLES (audit fix D1: 'van'/'der'/'von' etc. are 3+ chars, were
# NOT stopped, and let a particle-only author ground against 'van der X'). 2-char
# particles (de/la/le/di/du) are already dropped by the len>2 guard below.
_BIB_STOP = {"and", "et", "al", "with", "the", "for",
             "van", "der", "von", "bin", "bint", "ter", "ten", "den", "des", "del"}


def verify_bibliography(claimed_authors, claimed_year, source_metadata):
    """kappa=0.7 (advisory): do the claimed authors/year match the source's metadata?
    EXACT WORD matching (not substring) against the source author word-set, after
    dropping connector words and 1-2 char initials. Every named claimed token must
    be a real source author word -- so 'Smith and Jones' does NOT match
    'Brown and Williams' (carries SOCIUS audit fixes B-CRITICAL/B1/B2). A mismatch
    is a CITATION-MISMATCH to review, NEVER an accusation of fraud."""
    src_words = set(re.findall(r"[a-z]+", _norm(source_metadata.get("authors", ""))))
    claim_tokens = [t for t in re.findall(r"[a-z]+", _norm(claimed_authors))
                    if len(t) > 2 and t not in _BIB_STOP]
    matched = [t for t in claim_tokens if t in src_words]   # EXACT word match
    auth_ok = len(claim_tokens) > 0 and len(matched) == len(claim_tokens)
    year_ok = str(claimed_year).strip() == str(source_metadata.get("year", "")).strip()
    return {"check": "F-CITE", "kappa": 0.7,
            "claimed_authors": claimed_authors, "claimed_year": claimed_year,
            "source_authors": source_metadata.get("authors", ""),
            "source_year": source_metadata.get("year", ""),
            "claimed_name_tokens": claim_tokens, "matched_tokens": matched,
            "authors_match": bool(auth_ok), "year_match": bool(year_ok),
            "grounded": bool(auth_ok and year_ok),
            "verdict": "cite_match" if (auth_ok and year_ok) else "CITE_MISMATCH"}


# --------------------------------------------------------------------------- #
#  the facility entry point:  ground(...)
# --------------------------------------------------------------------------- #
def ground(claim, source_text=None):
    """THE shared-facility API. Combine Layer 1 (frozen kappa=1/0.7) + Layer 2
    (recorded kappa=0 entailment judgment).

    `claim` may be a dict (preferred) or a plain string (then pass source_text=).
    dict fields (all optional except text):
      text, source_text, quote, numbers ([{value, context?}]),
      claimed_authors, claimed_year, source_metadata ({authors, year}),
      entailment_verdict ({verdict: entailed|not_entailed|uncertain, judge_model, rationale})
    """
    if isinstance(claim, str):
        claim = {"text": claim, "source_text": source_text}
    elif source_text is not None and claim.get("source_text") is None:
        claim = {**claim, "source_text": source_text}

    checks = []
    src = claim.get("source_text")
    fetched = src is not None and len(str(src)) > 0

    if claim.get("quote") and fetched:
        checks.append(verify_quote(claim["quote"], src))
    for num in claim.get("numbers", []) or []:
        if fetched:
            checks.append(verify_number(num.get("value"), src, num.get("context")))
    if claim.get("claimed_authors") and claim.get("source_metadata"):
        checks.append(verify_bibliography(claim["claimed_authors"],
                                          claim.get("claimed_year"),
                                          claim["source_metadata"]))

    frozen_checks = [c for c in checks if c["kappa"] >= 1]            # F-QUOTE / F-NUMBER
    any_frozen_grounded = any(c["grounded"] for c in frozen_checks)
    any_frozen_failed = any(not c["grounded"] and "NOT_IN_SOURCE" in c["verdict"]
                            for c in frozen_checks)
    bib = next((c for c in checks if c["check"] == "F-CITE"), None)
    bib_mismatch = bib is not None and not bib["grounded"]

    ent = claim.get("entailment_verdict")
    ent_verdict = ent.get("verdict") if ent else None

    # ---- compose the overall verdict ----
    if any_frozen_failed or bib_mismatch:
        overall = "FABRICATION_FLAG"          # a quote/number/author did NOT check
    elif not fetched:
        overall = "ABSTAIN"                   # could not fetch the source
    elif any_frozen_grounded and ent_verdict in (None, "entailed"):
        overall = "GROUNDED"                  # anchored to source + (if judged) entailed
    elif ent_verdict == "entailed":
        overall = "GROUNDED_BY_JUDGMENT"      # only the kappa=0 judge supports it (weaker)
    elif ent_verdict == "not_entailed":
        overall = "CONTRADICTED_BY_SOURCE"
    else:
        overall = "ABSTAIN"                   # nothing grounded it and judge uncertain

    candidate_causes = None
    if overall == "FABRICATION_FLAG":
        candidate_causes = ["paraphrase mismatch (not verbatim)",
                            "wrong source attached", "OCR/transcription error",
                            "the quote/number/cite was invented"]

    return {
        "facility": "FACTHARNESS", "claim": claim.get("text"),
        "source_fetched": bool(fetched),
        "layer1_frozen_checks_kappa1": frozen_checks,        # F-QUOTE/F-NUMBER (k=1)
        "bibliographic_check_kappa0p7": bib,                 # F-CITE (k=0.7, advisory)
        "layer2_entailment_kappa0": ent,
        "overall": overall,
        "candidate_causes": candidate_causes,                # only on a flag; NEVER "fraud"
        "kappa_note": "F-QUOTE/F-NUMBER are kappa=1 frozen; F-CITE is kappa=0.7 advisory; "
                      "entailment is kappa=0 judgment (a model != generator), reported "
                      "never machine-verified.",
        "ceiling_note": "Grounded means anchored to a real source containing the asserted "
                        "quote/number -- NOT that the claim is true. A FABRICATION_FLAG "
                        "means 'does not check against the supplied source', NOT fraud.",
    }


# back-compat alias for callers used to the SOCIUS name
verify_grounding = ground


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] != "selftest":
        print(json.dumps(ground(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: factharness.py <claim.json>   (run selftest_all.py for the gate)")
