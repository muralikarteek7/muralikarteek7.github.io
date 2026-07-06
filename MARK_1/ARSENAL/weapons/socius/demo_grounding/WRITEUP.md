# SOCIUS S-GROUND demo — grounding 8 claims against 3 real abstracts

**What it tests:** the S-GROUND sub-weapon — does a prose claim's quote / number / citation
actually appear in its cited source (κ=1 frozen), and does the source *support* a paraphrase
(κ=0, cross-model judge)? Sources are 3 **real abstracts fetched from OpenAlex** (`sources.json`):
Durante et al. 2013 (the original "fluctuating female vote" claim), Steegen et al. 2016 (the
multiverse reanalysis), Scott & Pound 2015 (an independent large-N refutation, n=2213).

**Committed predictions (`PREDICTION.md`) → result: 8/8 correct.**

| # | claim | verdict | what it shows |
|---|---|---|---|
| C1 | Durante quote "more liberal, less religious" + cite | GROUNDED | real verbatim quote + matching citation |
| C2 | Steegen quote "arbitrary choices in data construction" + cite | GROUNDED | real quote + cite |
| C3 | Scott & Pound "no evidence of a relationship" + n=2213 | GROUNDED | quote + number both present |
| C4 | "Durante concluded the effect was *weak and likely spurious*" | **FABRICATION_FLAG** | a **fabricated quote** (Durante claimed the opposite) is caught |
| C5 | "*Smith & Jones* (2013) authored 'The Fluctuating Female Vote'" | **FABRICATION_FLAG** | a **wrong-author citation** is caught |
| C6 | "Steegen reported 7 of 120 specs" checked vs the *abstract* | **FABRICATION_FLAG** | a TRUE number that is **not in the supplied text** is honestly flagged as a *source-mismatch* (the fix is to supply the paper body / `demo_durante2013`, not relax the check) |
| C7 | "the literature now questions the effect's reliability" (paraphrase) | GROUNDED_BY_JUDGMENT | κ=0 entailment, Sonnet-judged *entailed* vs Steegen+Scott&Pound |
| C8 | "Scott & Pound *confirmed* ovulation increases conservatism" | CONTRADICTED_BY_SOURCE | κ=0 entailment, Sonnet-judged *not-entailed* (the source says the opposite) |

**The two honest layers, on display:**
- **κ=1 frozen** (C1–C6): pure text arithmetic — a quote/number/author is, or is not, in the
  fetched source. Deterministic, no model, can be re-run by anyone.
- **κ=0 judgment** (C7–C8): "does the source *support* this paraphrase?" is natural-language
  inference — done by a cross-model judge (`claude-sonnet-4-6` ≠ the Opus generator), recorded with
  attribution, and **never presented as machine-verified**. Unfetchable source → ABSTAIN.

**Non-accusation rail (binding):** a FABRICATION_FLAG means *"this quote/number/author does not
check against the supplied source"* — NOT fraud. Rounding, typos, paraphrase, and (as in C6)
supplying the wrong source are all possible explanations. The frozen layer stops at the text match.

**Honest ceiling:** S-GROUND raises *traceability* (a claim is anchored to a real source that
contains the asserted quote/number) — NOT truth. A source can be real, correctly quoted, and itself
wrong. Layer 1 proves a claim is **not fabricated**; it does not prove the claim is **correct**.

**Provenance of the verifier (do not hide this):** the first cut of `ground_verify.py` shipped with
**3 real bugs** (a decimal-boundary gap, a critical bibliography connector-word exploit, and an
over-aggressive quote normaliser) that the generator's own self-tests passed. An **independent
Sonnet audit caught all three**; they are fixed and the gate now locks the auditor's exact break
cases as regression tests. See `../AUDIT.md` (Round 2).
