# COMMITTED PREDICTION — S-GROUND demo (written BEFORE running)
*Grounding 8 prose claims against 3 real fetched abstracts (Durante 2013, Steegen
2016, Scott & Pound 2015; `sources.json`). The κ=0 entailment claims are judged by
a cross-model agent (Sonnet ≠ the Opus generator). Some predictions WILL be wrong —
that is the method working.*

| # | Claim | Grounding offered | Predicted verdict |
|---|---|---|---|
| C1 | "Durante et al. (2013) reported that ovulation led single women to become *more liberal, less religious*." | real quote + Durante cite | **GROUNDED** |
| C2 | "Steegen et al. (2016) found the conclusions change because of *arbitrary choices in data construction*." | real quote + Steegen cite | **GROUNDED** |
| C3 | "Scott & Pound (2015) found *no evidence of a relationship* between cyclical fertility and conservatism, *robust to multiple inclusion/exclusion criteria*." | real quotes + cite | **GROUNDED** |
| C4 | "Durante et al. (2013) concluded the ovulation effect was *weak and likely spurious*." | FABRICATED quote (Durante actually claimed a real effect) | **FABRICATION_FLAG** |
| C5 | "Smith & Jones (2013) authored 'The Fluctuating Female Vote'." | wrong-author cite vs Durante metadata | **FABRICATION_FLAG** |
| C6 | "Steegen et al. (2016) reported exactly 7 of 120 significant specifications." | number "120" checked **against the Steegen ABSTRACT** (which does not state it) | **FABRICATION_FLAG** (honest false-alarm: the number is real but lives in the paper body/code, not the abstract — see note) |
| C7 | "The broader literature now questions whether the ovulation–politics effect is reliable." (paraphrase, no quote) | κ=0 entailment judged vs all 3 sources | **GROUNDED_BY_JUDGMENT** (entailed) |
| C8 | "Scott & Pound (2015) confirmed that ovulation reliably increases conservatism." (paraphrase, no quote) | κ=0 entailment judged vs Scott & Pound | **CONTRADICTED_BY_SOURCE** (not entailed) |

**Note on C6 (the deliberate honest-tension case):** the claim "7 of 120" is TRUE
of the study, but the *abstract* I grounded it against does not contain those
numbers. S-GROUND checks the claim against the *supplied source text*; grounding a
body-level number against an abstract SHOULD flag it as not-found. This is the
correct, conservative behaviour: **S-GROUND proves a claim is anchored to the
specific text given, and will (rightly) refuse to "find" a number that is not in
that text** — the fix is to supply the correct source (the paper body / the R
code / `demo_durante2013`), not to relax the check. I predict FABRICATION_FLAG and
will report it as a *source-mismatch*, not an accusation.

**Honesty rail:** a FABRICATION_FLAG means "this quote/number/author does not check
against the cited source" — NOT "the author committed fraud." Rounding, paraphrase,
wrong-source-supplied, and honest error are all possible explanations. The frozen
layer stops at the arithmetic of text matching; entailment is κ=0 and abstains when
uncertain.
