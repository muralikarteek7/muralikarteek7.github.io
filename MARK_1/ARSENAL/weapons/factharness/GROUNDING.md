# FACTHARNESS — GROUNDING (load-bearing facts, fetched not asserted)

FACTHARNESS is a **promotion** of SOCIUS `S-GROUND`. Most of its grounding is already established in the
seed and carried forward; the only genuinely-new fact is the κ=0 entailment-judge framing.

## G1 — the κ=1 fabrication core is inherited + already audited (CITE the seed, not re-fetched)
The exact quote/number/citation matchers come from `socius/ground_verify.py`, which was independently
audited (Round-2 Sonnet ≠ Opus generator, `socius/AUDIT.md`). The audit BROKE the first cut and 3 real
bugs were fixed; their break-cases are locked as regression tests and carried into `factharness.py`:
- **A1 (quote over-normalisation):** a punctuation-stripped fabrication (`p 0.001`) must NOT match a
  source with the qualifier (`(p < 0.001)`) → fixed via `_norm_quote` that preserves structural punctuation.
- **A3 (number boundary):** `7` must NOT match inside the decimal `7.5` → fixed via boundary-safe regex
  `(?<!\d)(?<!\d\.)…(?!\d)(?!\.\d)`.
- **B-CRITICAL (bibliography substring exploit):** the connector `and` + substring matching let
  `Smith and Jones` ground against `Brown and Williams` → fixed via exact-word match + a stop-word list.
These are FETCHED facts in the sense that an independent model exercised the code and the fixes survive
its break-cases (machine-checked, not asserted). See `selftest_all.py` — all three regression tests run.

## G2 — entailment is a JUDGMENT (κ=0), not an exact check  [genuinely new, fetched]
Natural Language Inference (NLI) / Recognizing Textual Entailment (RTE) classifies the semantic relation
between a *premise* (the source) and a *hypothesis* (the paraphrased claim) into **entailment /
contradiction / neutral**. The task "requires semantic understanding, paraphrasing, and sometimes world
knowledge" — i.e. it is a *judgment*, not a deterministic string operation. There is no cheap exact
non-gameable verifier for "does this source SUPPORT this paraphrase," so **F-ENTAIL is κ=0 by
construction**: it is delegated to a cross-model judge (a model ≠ the generator), and when the judge is
uncertain the verdict is **ABSTAIN**, never a confident "supported." A model's self-reported entailment
is never upgraded to a κ=1 fabrication check.
- Source: NLI/RTE is a 3-label semantic task requiring world knowledge — Stanford NLI (SNLI) / MultiNLI
  task definition, summarized in the references below.

## G3 — grounding ≠ truth (the cardinal ceiling)
Even a perfectly grounded claim (verbatim quote present, number present, cite matches) only proves the
claim is *anchored to the supplied source* — the source itself may be wrong or biased. FACTHARNESS raises
**traceability**, never **truth**. This is the inherited S-GROUND ceiling, restated as a non-waivable rail.

## Sources
- SOCIUS S-GROUND seed + its independent Round-2 audit: `socius/ground_verify.py`, `socius/AUDIT.md`.
- Natural Language Inference / Recognizing Textual Entailment task definition (premise/hypothesis →
  entailment/contradiction/neutral; requires semantic understanding + world knowledge):
  [Aman's AI Journal — Textual Entailment](https://aman.ai/primers/ai/textual-entailment/),
  [NLI overview (EmergentMind)](https://www.emergentmind.com/topics/natural-language-inference-nli).
