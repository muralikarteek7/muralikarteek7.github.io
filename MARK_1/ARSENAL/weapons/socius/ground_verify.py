#!/usr/bin/env python3
"""S-GROUND — grounding & fabrication detection for empirical prose claims.

Grounding is NOT uniformly machine-checkable, so S-GROUND is deliberately split
into two layers, each labelled by its real κ:

  LAYER 1 — FABRICATION DETECTOR (κ=1, FROZEN, offline, self-tested).
    The part that genuinely IS exact. Given a claim and the *fetched* text of its
    cited source, deterministically check:
      * QUOTE   — a quoted string actually appears in the source (normalised exact
                  substring). Catches fabricated/altered quotes EXACTLY.
      * NUMBER  — a cited statistic actually appears in the source text.
      * BIB     — the claimed authors/year match the source's own metadata
                  (token overlap + exact year). Catches fabricated citations
                  (wrong author, wrong year — a documented AI failure mode).
    A false "grounded" is detectable: change the quote/number/author and the
    verdict flips. This layer can FAIL (and must — see _selftest).

  LAYER 2 — ENTAILMENT JUDGMENT (κ=0, ARMOR, NOT machine-verified).
    Does the source actually SUPPORT a paraphrased claim? This is natural-language
    inference — a judgment. It is performed OUTSIDE this verifier by a cross-model
    judge (a model ≠ the generator); this module only RECORDS that verdict and
    enforces the rule: if the source could not be fetched, OR the judge is
    uncertain, AND no Layer-1 check grounded the claim → the verdict is ABSTAIN.
    Entailment is ALWAYS reported as κ=0; it is never presented as machine-verified.

Honest ceiling: grounding raises *traceability* (the claim is anchored to a real,
fetched source that contains the asserted quote/number), NOT truth. A source can
be real, correctly quoted, and itself wrong. Layer 1 proves a claim is not
fabricated; it does not prove the claim is correct.
"""
import sys, json, re, unicodedata


def _norm(s):
    """Lowercase, strip accents, collapse whitespace, drop most punctuation.
    Used for NUMBER and BIBLIOGRAPHY token matching (not for verbatim quotes)."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    # unicode dashes AND the U+2212 MINUS SIGN -> hyphen (audit fix D2: U+2212 was
    # outside the dash range and got stripped to a space, dropping a number's sign,
    # so a sign-flipped '−7' grounded against a positive '7').
    s = re.sub(r"[‐-―−]", "-", s)         # unicode dashes + U+2212 -> hyphen
    s = re.sub(r"[^\w\s%.\-]", " ", s)               # keep word chars, %, ., -
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _norm_quote(s):
    """PUNCTUATION-PRESERVING normalisation for VERBATIM quote matching.
    Only case, unicode accents, smart quotes/dashes, and whitespace are normalised
    — structural punctuation (parentheses, <, >, =, commas) is KEPT, so a quote
    that drops a qualifier (e.g. 'p 0.001' vs the source's '(p < 0.001)') does NOT
    spuriously match. (Fixes audit break A1.)"""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = re.sub(r"[‐-―]", "-", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def verify_quote(quote, source_text):
    """Frozen: is the quoted string present VERBATIM in the source (modulo case,
    accents, smart quotes, and whitespace — punctuation preserved)?"""
    q = _norm_quote(quote)
    if len(re.sub(r"[^\w]", "", q)) < 7:   # require >=7 alphanumeric chars of content
        return {"check": "quote", "kappa": 1, "verdict": "too_short_to_check",
                "grounded": False}
    present = q in _norm_quote(source_text)
    return {"check": "quote", "kappa": 1, "quote": quote,
            "grounded": bool(present),
            "verdict": "quote_found" if present else "QUOTE_NOT_IN_SOURCE"}


def _strip_thousands(s):
    """Remove digit-grouping commas ('2,213'->'2213') so comma-formatted numbers
    in a source are not falsely flagged as fabricated. Cardinal property: NEVER
    falsely accuse — a true number written with a thousands separator must ground."""
    return re.sub(r"(?<=\d),(?=\d)", "", str(s))


def verify_number(number, source_text, also_require=None):
    """Frozen: does the cited number appear in the source text? `number` may be a
    string like '7', '120', '36', '5.8', '2,213'. Optionally require a nearby keyword."""
    src = _norm(_strip_thousands(source_text))
    num = _norm(_strip_thousands(number))
    # numeric-boundary match: reject if the number is part of a LARGER number.
    # lookbehind blocks a preceding digit OR digit-then-dot ('2.7' must not match '7');
    # lookahead blocks a following digit OR dot-then-digit ('7.5' must not match '7').
    # A sentence-final '7.' still matches (the '.' is not followed by a digit).
    # (Fixes audit break A3: '7' no longer matches inside '7.5'.)
    pat = r"(?<!\d)(?<!\d\.)" + re.escape(num) + r"(?!\d)(?!\.\d)"
    found = re.search(pat, src) is not None
    ctx_ok = True
    if also_require is not None:
        # word-boundary context match (audit fix D3: a raw substring let 'treat' match
        # inside 'untreated' and 'sign' inside 'insignificant').
        ctx_pat = r"(?<!\w)" + re.escape(_norm(also_require)) + r"(?!\w)"
        ctx_ok = re.search(ctx_pat, src) is not None
    return {"check": "number", "kappa": 1, "number": str(number),
            "also_require": also_require,
            "grounded": bool(found and ctx_ok),
            "verdict": "number_found" if (found and ctx_ok) else "NUMBER_NOT_IN_SOURCE"}


# connector / abbreviation words that are NOT author names (audit break B-CRITICAL:
# 'and' was being treated as a valid 3-char author token).
_BIB_STOP = {"and", "et", "al", "with", "the", "for"}


def verify_bibliography(claimed_authors, claimed_year, source_metadata):
    """κ≈0.7: do the claimed authors/year match the source's own metadata?
    source_metadata: dict with 'authors' (str) and 'year' (int/str).

    EXACT WORD matching (not substring) against the source author word-set, after
    dropping connector words and 1-2 char initials. Requires EVERY named claimed
    token to be a real source author word — so 'Smith and Jones' does NOT match
    'Brown and Williams', and 'Fra Gel Van' does NOT match 'Francis ... Gelman ...
    Vanpaemel'. (Fixes audit breaks B-CRITICAL, B1, B2.) κ=0.7: advisory — a
    mismatch is a CITATION-MISMATCH to review, never an accusation."""
    # extract alphabetic words only (drops trailing periods like 'al.', initials, digits)
    src_words = set(re.findall(r"[a-z]+", _norm(source_metadata.get("authors", ""))))
    claim_tokens = [t for t in re.findall(r"[a-z]+", _norm(claimed_authors))
                    if len(t) > 2 and t not in _BIB_STOP]
    matched = [t for t in claim_tokens if t in src_words]   # EXACT word match
    auth_ok = len(claim_tokens) > 0 and len(matched) == len(claim_tokens)
    year_ok = str(claimed_year).strip() == str(source_metadata.get("year", "")).strip()
    return {"check": "bibliography", "kappa": 0.7,
            "claimed_authors": claimed_authors, "claimed_year": claimed_year,
            "source_authors": source_metadata.get("authors", ""),
            "source_year": source_metadata.get("year", ""),
            "claimed_name_tokens": claim_tokens, "matched_tokens": matched,
            "authors_match": bool(auth_ok), "year_match": bool(year_ok),
            "grounded": bool(auth_ok and year_ok),
            "verdict": "bib_match" if (auth_ok and year_ok) else "BIB_MISMATCH"}


def verify_grounding(claim):
    """Combine Layer 1 (frozen) + Layer 2 (recorded entailment judgment).

    claim: dict, any of:
      text                : the prose assertion (for the record)
      source_text         : fetched source text (None if fetch failed)
      quote               : a direct quote attributed to the source (optional)
      numbers             : list of {value, context?} cited from the source (optional)
      claimed_authors, claimed_year, source_metadata : for the bib check (optional)
      entailment_verdict  : {'verdict': 'entailed'|'not_entailed'|'uncertain',
                             'judge_model': str, 'rationale': str}  (κ=0, external)
    """
    checks = []
    source_text = claim.get("source_text")
    fetched = source_text is not None and len(str(source_text)) > 0

    if claim.get("quote") and fetched:
        checks.append(verify_quote(claim["quote"], source_text))
    for num in claim.get("numbers", []) or []:
        if fetched:
            checks.append(verify_number(num.get("value"), source_text,
                                        num.get("context")))
    if claim.get("claimed_authors") and claim.get("source_metadata"):
        checks.append(verify_bibliography(claim["claimed_authors"],
                                          claim.get("claimed_year"),
                                          claim["source_metadata"]))

    frozen_checks = [c for c in checks if c["kappa"] >= 1]
    any_frozen_grounded = any(c["grounded"] for c in frozen_checks)
    any_frozen_failed = any(not c["grounded"] and "NOT_IN_SOURCE" in c["verdict"]
                            for c in frozen_checks)
    bib = next((c for c in checks if c["check"] == "bibliography"), None)
    bib_mismatch = bib is not None and not bib["grounded"]

    # Layer 2 (κ=0) entailment — recorded, never machine-verified
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
        overall = "GROUNDED_BY_JUDGMENT"      # only the κ=0 judge supports it (weaker)
    elif ent_verdict == "not_entailed":
        overall = "CONTRADICTED_BY_SOURCE"
    else:
        overall = "ABSTAIN"                   # nothing grounded it and judge uncertain

    return {
        "sub_weapon": "S-GROUND", "claim": claim.get("text"),
        "source_fetched": bool(fetched),
        "layer1_frozen_checks_kappa1": frozen_checks,        # quote/number only (κ=1)
        "bibliographic_check_kappa0p7": bib,                  # citation match (κ=0.7, advisory)
        "layer2_entailment_kappa0": ent,
        "overall": overall,
        "kappa_note": "Layer 1 (quote/number/bib) is κ=1 frozen; entailment is κ=0 "
                      "judgment (a model ≠ generator), reported never machine-verified.",
        "ceiling_note": "Grounding proves the claim is anchored to a real source "
                        "containing the asserted quote/number — NOT that the claim "
                        "is true. Real, correctly-quoted sources can still be wrong.",
    }


# --------------------------------- selftest -------------------------------- #
_SRC = ("Steegen, Tuerlinckx, Gelman and Vanpaemel (2016). Increasing transparency "
        "through a multiverse analysis. We reanalysed Durante et al. (2013). For the "
        "religiosity effect in Study 1, only 7 of the 120 specifications were "
        "statistically significant, leading us to conclude the effect is too fragile.")
_META = {"authors": "Steegen Tuerlinckx Gelman Vanpaemel", "year": 2016}


def _selftest():
    # QUOTE: a real quote grounds; a fabricated quote is caught (must FAIL)
    assert verify_quote("too fragile", _SRC)["grounded"] is True
    assert verify_quote("the effect is robust and replicates widely", _SRC)["grounded"] is False
    # REGRESSION (audit break A1): a punctuation-stripped fabrication must NOT match
    #   a source whose real text has the qualifier ('p 0.001' vs '(p < 0.001)').
    assert verify_quote("significant effect p 0.001",
                        "The results showed a significant effect (p < 0.001).")["grounded"] is False
    # a genuinely verbatim quote (modulo whitespace/case) still grounds
    assert verify_quote("a Significant   Effect (p < 0.001)",
                        "showed a significant effect (p < 0.001).")["grounded"] is True
    # NUMBER: real number grounds; fabricated number caught
    assert verify_number("120", _SRC)["grounded"] is True
    assert verify_number("999", _SRC)["grounded"] is False
    assert verify_number("7", _SRC, also_require="significant")["grounded"] is True
    # word-boundary: '7' must not match inside '17'
    assert verify_number("17", "there were 7 of 120 specs")["grounded"] is False
    # REGRESSION (audit break A3): '7' must NOT match inside the decimal '7.5'
    assert verify_number("7", "Effect size was 7.5 points.")["grounded"] is False
    assert verify_number("5", "the mean was 5.8")["grounded"] is False
    # ...but a standalone integer and a sentence-final '7.' still ground
    assert verify_number("7", "there were 7 specs")["grounded"] is True
    assert verify_number("7", "the total was 7.")["grounded"] is True
    # thousands-comma: a TRUE number must ground regardless of grouping commas
    #   (cardinal soundness: never falsely flag a real number as fabricated)
    assert verify_number("2213", "we surveyed 2,213 women")["grounded"] is True
    assert verify_number("2,213", "2213 women provided data")["grounded"] is True
    # decimals/percentages survive normalisation
    assert verify_number("5.8", "about 5.8% of specs")["grounded"] is True
    # REGRESSION (audit fix D2, HIGH κ=1 breach): the unicode MINUS U+2212 must
    #   normalise to a hyphen, so a sign-flipped '−7' does NOT ground against a
    #   positive '7' in the source, but DOES ground against an ASCII '-7'.
    assert verify_number(chr(0x2212) + "7", "The study found 7 cases.")["grounded"] is False
    assert verify_number(chr(0x2212) + "7", "The study found -7 cases.")["grounded"] is True
    assert verify_grounding({"text": "study found -7",
                             "source_text": "The study found 7 cases of improvement.",
                             "numbers": [{"value": chr(0x2212) + "7"}]})["overall"] != "GROUNDED"
    # REGRESSION (audit fix D3, κ=1 context): also_require is a word-boundary match,
    #   so 'treat' must NOT match inside 'untreated' and 'sign' not inside 'insignificant',
    #   while a genuine standalone keyword still grounds.
    assert verify_number("7", "The untreated group had 7 participants.",
                         also_require="treat")["grounded"] is False
    assert verify_number("7", "The 7 tests were insignificant.",
                         also_require="sign")["grounded"] is False
    assert verify_number("7", "The 7 tests were not significant.",
                         also_require="significant")["grounded"] is True
    # BIB: correct cite matches; wrong author/year caught
    assert verify_bibliography("Steegen et al.", 2016, _META)["grounded"] is True
    assert verify_bibliography("Scott Pound", 2015,
                               {"authors": "Isabel M. Scott, Nicholas Pound", "year": 2015})["grounded"] is True
    assert verify_bibliography("Steegen et al.", 1999, _META)["grounded"] is False
    # REGRESSION (audit break B-CRITICAL): connector 'and' must NOT bridge totally
    #   different authors.
    assert verify_bibliography("Smith and Jones", 2016,
                               {"authors": "Brown and Williams", "year": 2016})["grounded"] is False
    assert verify_bibliography("Doe and Roe", 2016, _META)["grounded"] is False
    # REGRESSION (audit breaks B1/B2): 3-char fragments must NOT substring-match real names
    assert verify_bibliography("Fra Gel Van", 2016, _META)["grounded"] is False
    assert verify_bibliography("And Ste Lin", 2016, _META)["grounded"] is False
    assert verify_bibliography("Smith and Jones", 2016, _META)["grounded"] is False

    # END-TO-END verdicts:
    # (a) grounded claim with a real quote + real number -> GROUNDED
    good = verify_grounding({"text": "Steegen found 7 of 120 specs significant.",
                             "source_text": _SRC, "quote": "too fragile",
                             "numbers": [{"value": "7", "context": "significant"}],
                             "claimed_authors": "Steegen et al.", "claimed_year": 2016,
                             "source_metadata": _META})
    assert good["overall"] == "GROUNDED", good
    # (b) FABRICATED quote -> FABRICATION_FLAG (the verifier must catch invention)
    fab = verify_grounding({"text": "Steegen said the effect is robust.",
                            "source_text": _SRC,
                            "quote": "the effect is robust and replicates widely"})
    assert fab["overall"] == "FABRICATION_FLAG", fab
    # (c) source could not be fetched + no grounding -> ABSTAIN
    miss = verify_grounding({"text": "Some claim.", "source_text": None})
    assert miss["overall"] == "ABSTAIN", miss
    # (d) wrong-author citation -> FABRICATION_FLAG
    badcite = verify_grounding({"text": "Per Smith 2016 ...", "source_text": _SRC,
                                "claimed_authors": "Smith and Jones", "claimed_year": 2016,
                                "source_metadata": _META})
    assert badcite["overall"] == "FABRICATION_FLAG", badcite
    # (e) κ=0 entailment recorded but never upgraded past its judge
    ent = verify_grounding({"text": "paraphrase with no quote", "source_text": _SRC,
                            "entailment_verdict": {"verdict": "not_entailed",
                                                   "judge_model": "sonnet",
                                                   "rationale": "source says fragile, claim says strong"}})
    assert ent["overall"] == "CONTRADICTED_BY_SOURCE", ent
    print("ground_verify selftest: PASS (grounds real quote/number/cite; FLAGS fabricated "
          "quote + wrong-author cite; ABSTAINS on no source; entailment stays κ=0)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) == 2:
        print(json.dumps(verify_grounding(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: ground_verify.py selftest | <claim.json>")
