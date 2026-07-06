# GROUNDING — TRIAGE (failure-class taxonomy)

*Every load-bearing fact below was FETCHED via WebFetch/WebSearch on 2026-06-20 (not asserted from
memory). Where a fetch failed or was not attempted, it is stated. The point of grounding is to check
that the home-grown taxonomy (seeded from the box's REAL caught failures) is **not parochial** —
i.e. it lines up with published external risk/failure taxonomies — and to record what the box's own
history adds that the generic lists miss.*

---

## G1. NIST AI RMF 1.0 — trustworthy-AI characteristics
**Fetched:** <https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/> (2026-06-20).

Exact list quoted from the source — characteristics of trustworthy AI systems:
> "valid and reliable, safe, secure and resilient, accountable and transparent, explainable and
> interpretable, privacy-enhanced, and fair with harmful bias managed."

Definitions quoted from the source:
- **Validation:** "confirmation, through the provision of objective evidence, that the requirements
  for a specific intended use or application have been fulfilled."
- **Reliability:** "ability of an item to perform as required, without failure, for a given time
  interval, under given conditions."
- Testing: "Validity and reliability for deployed AI systems are often assessed by ongoing testing
  or monitoring that confirms a system is performing as intended." and "Human judgment should be
  employed when deciding on the specific metrics related to AI trustworthiness characteristics and
  the precise threshold values for those metrics."

**Reconciliation:** NIST's *valid-and-reliable* maps onto our **overconfidence** + **distribution-shift**
rows (a system "performing as intended" only under "given conditions" = our calibration/OOS framing).
NIST explicitly says trustworthiness requires *human judgment on thresholds* — that grounds our κ<1 rows
(they are routed judgments, not certifications). NIST has no row for **circular measurement** or
**branch-cut/numeric-domain** — those are box-specific additions (see G4).

## G2. OWASP Top 10 for LLM Applications (v1.1)
**Fetched:** <https://owasp.org/www-project-top-10-for-large-language-model-applications/> (2026-06-20).

Categories quoted from the source (v1.1):
- LLM01 Prompt Injection · LLM02 Insecure Output Handling · LLM03 Training Data Poisoning ·
  LLM04 Model Denial of Service · LLM05 Supply Chain Vulnerabilities · LLM06 Sensitive Information
  Disclosure · LLM07 Insecure Plugin Design · LLM08 Excessive Agency · **LLM09 Overreliance** ·
  LLM10 Model Theft.

**Reconciliation:** OWASP **LLM09 Overreliance** — *"Failing to critically assess LLM outputs can lead
to compromised decision making"* — is exactly our **overconfidence** + **fabrication** rows (it names
hallucinated/fabricated output as the harm). OWASP is a *security* taxonomy: most of its rows
(prompt-injection, plugin design, model theft) are out of TRIAGE's scope (TRIAGE checks the box's own
*reasoning/output* failures, not an adversary's attack surface) — recorded here so we do NOT overclaim
coverage of OWASP. The one overlapping row (LLM09) confirms our overconfidence/fabrication rows are not
parochial.

## G3. Hallucination survey — Huang et al. 2023 (factuality vs faithfulness)
**Fetched (search):** "A Survey on Hallucination in Large Language Models: Principles, Taxonomy,
Challenges, and Open Questions", arXiv:2311.05232 (2023); also ACM TOIS <https://dl.acm.org/doi/10.1145/3703155>.

Quoted taxonomy split:
- **Factuality hallucination:** "the discrepancy between generated content and verifiable real-world
  facts." → maps to our **fabrication** row (a quote/number/cite not in source) and **overconfidence**.
- **Faithfulness hallucination:** "the divergence of generated content from user input or the lack of
  self-consistency within the generated content." → maps to our **overconfidence** (cross-paraphrase
  disagreement = self-inconsistency detector) and to **specification-gaming** (output diverges from the
  user's actual goal while passing a proxy).

**Reconciliation:** the survey's two-way split (factuality / faithfulness) is *subsumed* by our table:
factuality → fabrication (κ=1 when a source is supplied) + overconfidence; faithfulness → overconfidence
+ spec-gaming. The survey has no analogue of our **circular-measurement** or **shared-blind-spot** rows
(those are evaluation-methodology failures, not generation failures) — box-specific (G4).

## G4. What the box's REAL history adds that the generic lists MISS
Mined from `Legacy/EVOLUTION_LOG.md` (the season's actually-caught failures = the taxonomy's ground truth):

| box-caught failure (real) | EVOLUTION_LOG ref | covered by NIST/OWASP/Huang? |
|---|---|---|
| SYMBOLICA branch-cut skip (`log(x²)=2log(x)` certified on positive-only residue) | C39 | **NO** — numeric/branch-cut is box-specific |
| false +25pp PROOFSMITH answer-key LEAK (provers read `reference_proofs.lean` off disk) | C41 | **NO** — circular-measurement / data-provenance is box-specific |
| SOCIUS S-GROUND fabrication bugs (number-boundary `7∈7.5`; "and"+substring bib match) | C34 | partial — Huang *factuality*, but the EXACT κ=1 detector is ours |
| OPTIMA missing-var KeyError crash (silent on malformed input) | C38 | **NO** — crash/silent-pass on malformed input is box-specific |
| ECONOMETRIX in-sample Sharpe = gameable proxy (dies OOS) | C42 | partial — spec-gaming; the in-sample/OOS *flip* test is ours |
| CODEFORGE predictable public fuzz seed (false-accept) | C40 | **NO** — proxy-gaming via known test inputs is box-specific |
| symmetry-frame 41<90 negative (a real reported negative) | kickoff §0 | n/a — honest-negative discipline, not a failure class |

**Net:** the generic external taxonomies confirm the *general* rows (overconfidence, fabrication,
spec-gaming) are not parochial, but **4 of the box's most expensive real failures (branch-cut,
answer-key leak, malformed-input silent-pass, known-test-input gaming) are NOT in the generic LLM lists**
— they are evaluation/verification-methodology failures the box discovered the hard way. That is the
value-add the kickoff asked us to record.

## G5. Infra grounded by machine (not fetched — checked locally on 2026-06-20)
- **FACTHARNESS present** (`../factharness/factharness.py`, `ground()` + `verify_quote`/`verify_number`,
  κ=1 frozen) — composed by TRIAGE's fabrication row. Verified importable (see selftest_all.py output:
  `composes FACTHARNESS: True`).
- **CRUCIBLE present** (`../crucible/crucible_harness.py`, the box's gate-testing META-WEAPON) — it
  appeared during this build session (it was NOT in `weapons/` at the first `ls`, then was). **HONEST
  nuance the audit-banner #3 requires:** CRUCIBLE being on disk does NOT auto-supply an *independent
  oracle of the answer* for an arbitrary task — it tests GATES (black-box), and its oracle path fires
  only when an oracle is registered for the specific task. So TRIAGE's κ logic does NOT key off
  "CRUCIBLE exists":
  - **specification-gaming** reaches **κ=1 ONLY when the record actually supplies an independent oracle
    verdict / OOS signal**; with no oracle it runs TRIAGE's own **κ<1 structural in-sample/OOS check**
    (`degraded: True`), explicitly labeled. (Keying κ off the supplied oracle, not off CRUCIBLE-on-disk,
    is the non-parochial honesty the banner demands — CRUCIBLE-present must not silently launder a κ<1
    judgment into a κ=1 certification.)
  - **crash/silent-pass on malformed input** is **κ=1 on the exactly-checkable question** "did the
    detector error/abstain LOUDLY vs silent-pass?" — TRIAGE runs that probe itself; CRUCIBLE would
    supply a *richer* adversary, but the loud-vs-silent question is the κ=1 floor TRIAGE owns.
  - **fabrication** drops to κ<1 (`degraded: True`) if FACTHARNESS were unavailable OR no source text is
    supplied (degraded behavior stated, per the banner).
  *(An earlier draft of this file asserted CRUCIBLE was absent — corrected here after a machine check
  found `../crucible/` on disk; the κ logic was reworked to key off the supplied oracle, not the dir.)*
