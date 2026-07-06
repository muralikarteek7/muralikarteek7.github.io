# FACTHARNESS — SPEC (Weapon #7, cross-cutting Integrity-Office core facility)

*Status: PROMOTED + HARDENED from SOCIUS `S-GROUND` (`socius/ground_verify.py`), not built from
scratch. Carries the 3 Round-2 audit fixes + their regression tests forward. Written 2026-06-20, box-style.*

## 1. WHAT IT IS (one line)
A **university-wide grounding / fabrication-check facility** every department + the Provost call:
given any prose claim with a cited source, answer the **κ=1 question "is the quote / number / citation
actually IN the fetched source?"** (exact fabrication check) and the **κ=0 question "does the source
SUPPORT the paraphrase?"** (entailment → cross-model judge, else ABSTAIN).

## 2. WHAT IT IS NOT (honesty rails — non-waivable)
- **NOT a truth oracle.** "Grounded" = "supported by the supplied source," NOT "true." A perfectly
  grounded claim can cite a wrong/biased source. FACTHARNESS checks **grounding**, never **truth**.
- **NOT a fraud detector.** A `FABRICATION_FLAG` = "this quote/number/cite does NOT appear in the
  supplied source," with candidate causes (paraphrase mismatch, wrong source attached, OCR error). It
  **never** accuses a person of fabricating.
- **NOT an entailment certifier.** Entailment is **κ=0 judgment** → a cross-model judge (≠ generator);
  judge unsure → **ABSTAIN**, never a confident "supported."
- **NOT a from-scratch build.** The κ=1 verifier exists (S-GROUND); we promote + harden + integrate it.

## 3. THE PIECES
| piece | κ | what it checks | verifier |
|---|---|---|---|
| **F-QUOTE** | 1.0 | is the quoted text verbatim in the source? | punctuation-preserving normalized substring (SOCIUS quote-normaliser fixes; don't over-normalize) |
| **F-NUMBER** | 1.0 | does the cited number appear in the source? | exact numeric match, **boundary-safe** (the `7`∈`7.5` bug — fixed; regression test locked) |
| **F-CITE** | 0.7 | does the attributed author/year match the source's bibliography? | structured exact-word match, **NOT naive substring** (the `Smith and Jones`↔`Brown and Williams` exploit — fixed; test locked) |
| **F-ENTAIL** | 0.0 | does the source SUPPORT the paraphrase (beyond verbatim)? | cross-model judge (≠ generator); unsure → **ABSTAIN** |

κ separation is **strict**: F-QUOTE/F-NUMBER return exact κ=1 verdicts; F-CITE is advisory κ=0.7 (a
mismatch is a CITATION-MISMATCH to review, never an accusation); F-ENTAIL is labeled κ=0 and may abstain.
Never present an entailment judgment as a κ=1 fabrication check.

## 4. THE SHARED-FACILITY API (the promotion)
```python
from factharness import ground
result = ground(claim, source_text=None)   # claim is a dict (see below) OR (text, source_text)
# -> {overall, source_fetched, layer1_frozen_checks_kappa1, bibliographic_check_kappa0p7,
#     layer2_entailment_kappa0, kappa_note, ceiling_note}
```
`claim` dict fields (all optional except `text`): `text`, `source_text`, `quote`, `numbers`
(`[{value, context?}]`), `claimed_authors`, `claimed_year`, `source_metadata` ({authors, year}),
`entailment_verdict` ({verdict: entailed|not_entailed|uncertain, judge_model, rationale}).

`overall` ∈ {`GROUNDED`, `GROUNDED_BY_JUDGMENT`, `FABRICATION_FLAG`, `CONTRADICTED_BY_SOURCE`, `ABSTAIN`}.

**Batch + firewall hook** (`factharness_router.py`): `ground_all(claims)` routes a list and returns a
ship/abstain decision per claim — the institutionalized fabrication firewall every shipped prose claim
passes (ground or abstain). `firewall(claims)` returns `{"ship": bool, "flagged": [...], "abstained": [...]}`
so the orchestrator can BLOCK shipping any claim that flags or fails to ground.

## 5. THE KEY ENGINEERING PROBLEM — shared facility WITHOUT weakening the gate
1. Clean API the whole Helmet calls; wire the firewall so every shipped prose claim is grounded-or-abstained.
2. **Carry ALL three SOCIUS audit fixes + regression tests** (number boundary `7`∉`7.5`; bibliography
   substring `Smith and Jones`∌`Brown and Williams`; quote normaliser that keeps structural punctuation).
   A promotion that drops a fix is a regression — the tests are locked.
3. κ separation strict (see §3). Soundness (no false "grounded") is cardinal.

## 6. GATE SELF-TESTS (non-waivable — a gate that can't fail is not a gate)
(a) PASS a genuinely-grounded claim; (b) CATCH a fabricated quote; (c) CATCH a fabricated number /
wrong-author cite — incl. the 3 audit break-cases as locked regression tests; (d) ABSTAIN on an
ambiguous entailment rather than guessing. Plus new hardening tests added in promotion (see
`selftest_all.py`). Soundness (no false "grounded") is cardinal.

## 7. CEILING
Grounded ≠ true. FABRICATION_FLAG ≠ fraud. Entailment is κ=0. F-CITE is advisory (κ=0.7). The κ=1 core
proves a claim is anchored to a real source containing the asserted quote/number — not that it is correct.
