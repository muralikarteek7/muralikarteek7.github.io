# SCHOLAR — intake gates · decision rubrics · de-AI spec

*The operational reference the two modes drive from. Every list here is validated by the
`scholar-validation-research` workflow (current 2026 practice). The mode asks the intake questions up front —
**"ask if not specified"** — fills sane defaults for blanks (and says so), then freezes the contract.*

---

## A. `/mark1research` — intake gate (ask up front)
1. **REVIEW TYPE** — systematic / scoping / **rapid** / **narrative** / **meta-narrative (historiographic)**? Sets
   the exhaustiveness + honesty contract and the reporting standard *before any search*. (Default for a Mark run:
   **rapid or narrative** — and say which corners are cut. Rapid reviews have **no validated reporting guideline**;
   cite "PRISMA-RR (under development, EQUATOR register)", not a finished standard.)
2. **DOMAIN PROFILE** — STEM-empirical **or** HUMANITIES / history-of-science? Selects appraisal machinery
   (RoB/GRADE vs **primary-vs-secondary + provenance/edition/context**) and the databases/library.
3. **SOURCE OF TRUTH** — your own data, a corpus to re-analyze, or others' published work to synthesize?
4. **QUESTION + CONCEPT BLOCKS** — the falsifiable question, decomposed into concept blocks (PICO / PCC / thematic)
   for the search string.
5. **DATABASES + DISCOVERY SCOPE** — which indices/library (incl. the offline `Books_Folder`), and confirm
   **MANDATORY backward + forward citation chaining** to saturation (keyword-only recall is insufficient).
6. **INCLUSION / EXCLUSION** — the pre-registered predicate for what counts (frozen before screening).
7. **DEPTH / STOP RULE** — target seat count (**default 3–5; heterogeneous to extend toward 9–10**) + the
   diminishing-returns termination.
8. **LOAD-BEARING CLAIM TAGS** — which claims must be cross-model + retrieval verified; what triggers ABSTAIN.
9. **AI-USE BOUNDARY** — which steps an LLM may rank/assist; confirm **no AI is the sole includer/excluder or sole
   RoB/synthesis source** (all AI-touched steps human-verified + disclosed).
10. **GAP-ANALYSIS TARGET** — required output using the taxonomy *(empirical void / contradiction / methodological
    / under-theorized)*, each gap tied to a **falsifiable next claim** (never "more research needed"); evidence-and-
    gap map if map-style.
11. **OUTPUT TYPE + AUDIENCE** — the named audience and the checkable quality predicate that defines "done".

## B. `/mark1article` — intake gate (ask up front)
1. **DELIVERABLE TYPE** — journal-paper / review-synthesis / **book-chapter** / **thesis-chapter**? Picks the
   structural skeleton (see Rubric D). *This is the operator's "chapter or journal paper" question, made explicit.*
2. **TARGET VENUE** — name the 1–2 target venues and **pull their author guide**: article type, word/length
   ceiling, reference style + cap, mandated reporting checklist, data/code policy, AI-use + AI-detector policy.
   Freeze it as the venue tex-spec. *This is the operator's "which journal" question.*
3. **SOURCE OF TRUTH** — the authoritative artifact the draft must not contradict (dataset, results file, prior
   chapters, protocol) — frozen.
4. **STYLE ANCHOR (+ SAMPLE)** — a representative exemplar to **measure** a style-sheet from. **Ask if not
   specified.** Attaching a real sample is the single highest-leverage move (validated: few-shot exemplar
   anchoring ≈ **23.5× style fidelity** vs instruction-only). Without a sample, the style-sheet is declared
   LOW-CONFIDENCE and flagged.
5. **LENGTH + COMPONENT BUDGET** — word/page ceiling + budget for equations / tables / figures / references.
6. **DOMAIN PROFILE** — STEM vs humanities/history-of-science (selects verification lenses; for humanities, the
   primary-vs-secondary handling + RAMESES skeleton if a review).
7. **CITATION SOURCE-OF-TRUTH** — where references come from; hard **NO-fabricated-DOI** rule + paste-mode
   VERIFY-IT-YOURSELF gate for every load-bearing citation/number.
8. **OWNER WRITING RULES** — pull the standing "avoid X / always Y" table (e.g. no em-dash; banned terms) and ask
   for new ones. Capture EVERY rule in the traceability table **or it gets silently dropped** (operator law).
9. **FROZEN-SKELETON SIGN-OFF** — confirm the section spine + measured style-sheet + venue tex-spec + the
   empty-required compliance slots (**CRediT, Data/Code Availability, Competing Interests, AI-use disclosure**) are
   frozen before any prose.
10. **REVIEW LENSES + AI-USE DISCLOSURE** — which domain lenses run (numeric / citation-provenance / argument /
    de-AI / **Indic→GRANTHA** when the work cites Sanskrit sources or uses IAST —
    `SCHOLAR/GRANTHA_INDIC_CITATION_LENS.md`), the numeric-diff proof requirement, the disclosure statement to
    generate, and confirmation **no AI detector is an acceptance gate**.

---

## C. Journal / venue decision rubric (answer before writing)
1. **Source of truth?** own data/experiment · a corpus you re-analyze · a synthesis of others' work — gates whether
   it can be a primary paper at all vs a review.
2. **Contribution type?** new empirical result · new method/artifact · synthesis-and-gap-map · conceptual/
   theoretical · **historiographic reframing** — each maps to a different venue class.
3. **Field + its norm?** STEM-empirical (IMRaD journal) · CS/ML (conference + arXiv, code+data release) ·
   humanities / history-of-science (historiographic essay, monograph chapter, field journal). Name 1–2 targets.
4. **Venue structural requirements?** pull the author guide → article type, length ceiling, reference style + cap,
   reporting checklist, data/code policy, AI-use + AI-detector policy → freeze as the venue tex-spec.
5. **Review type** (if a review) → bind to the matching standard (PRISMA 2020 / PRISMA-ScR / SANRA / RAMESES);
   **rapid = declare which corners were cut** (no validated guideline — PRISMA-RR is under development, EQUATOR register).
   *(For a review-synthesis article, run `/mark1research` first to produce the survey + structured gap analysis, then
   `/mark1article` to write it to the venue spec — the two modes compose; gap analysis is a research-mode deliverable.)*
6. **Audience + exhaustiveness contract** — who must be convinced; "systematic" vs "illustrative/narrative" (sets
   what "done" means; don't imply systematic rigor you didn't do).
7. **Legitimacy / policy fit** — **positive-index inclusion FIRST** (DOAJ / Scopus / WoS / PubMed + COPE/OASPA
   membership) + **Think-Check-Submit**; Beall's List is **defunct since Jan 2017** (anonymous archive only) — use
   Cabells Predatory Reports as the maintained cross-check, never as the sole signal. APC/licence/preprint fit.
   *(History-of-science note: contribution TYPE — source edition vs historiographic argument vs technical
   reconstruction — selects the venue more than impact factor; for humanities, JIF is often absent/meaningless —
   weight indexing + society backing. IJHS-INSA accepts critical editions/translations + manuscript supplements.)*

## D. Deliverable-type rubric (the "chapter vs paper" answer)
| Type | When | Structure |
|---|---|---|
| **journal-paper** | one focused, novel, falsifiable contribution with its own source of truth, fitting a venue's scope; length-bounded | IMRaD (empirical) / Problem-Approach-Evaluation-Related-work + code&data (method); one spine, one claim, tight; reporting checklist if applicable; numeric-diff proof on every number |
| **review-synthesis** | mapping/synthesizing existing literature, not new primary data; pick sub-type (systematic/scoping/rapid/narrative/meta-narrative) = the honesty contract | bound by the matching standard (PRISMA 2020 + flow + PRISMA-S; PRISMA-ScR + JBI ch.10; rapid=declare cuts; SANRA; RAMESES); **gap analysis (4-way taxonomy) required**; map-style adds evidence-and-gap map; humanities profile: primary-vs-secondary, no forced PRISMA diagram |
| **book-chapter** | edited-volume/handbook: synthesizing/didactic/positioning piece, broad audience, often invited, more latitude, longer budget, no strict novelty bar | thematic/argumentative (not IMRaD): framing → organized synthesis of sub-themes → author's positioning → implications; heavier narrative cohesion + citation breadth; follow the editor's spec as the frozen venue-spec |
| **thesis-chapter** | a unit of a dissertation: self-contained yet bridged to adjacent chapters + the thesis question; examination standard, not a journal cap | self-contained mini-IMRaD / argument-chapter with explicit bridges to prior/next chapters + the central claim; fuller methods/limitations (examiners reward demonstrated rigor + reflexivity); a lit-review chapter follows review-synthesis; institutional formatting = frozen venue-spec |

## E. De-AI + disclosure spec (default ON in article mode; available in research mode)
1. **DISCLOSE, don't hide** — an explicit **AI-USE statement** as a first-class artifact: which tool/model, which
   steps it touched, and that a human verified all AI-touched outputs against source. Venue-routed placement.
2. **NEVER gate on an AI detector** — not to self-gate, not to accept a venue gating you that way without a human
   appeal. Detectors are unreliable (0–30% FPR on human prose, **61.3% on non-native essays**) and penalize exactly
   the features of good plain/ESL academic prose. *(The "75–85% flip" figure is unverified — do not state it.)*
3. **Surgical + diff-gated, content FROZEN** — edit voice/style only; prove content-invariance with a numeric/
   string diff (no number, claim, citation, or quote changed). De-AI never touches the evidence layer, and **must
   not strip a necessary hedge** (guard against the overclaiming-drift trend).
4. **Never fabricate** a DOI/citation/number/quote; retrieval-gate citations; paste-mode → human VERIFY-IT-YOURSELF
   gate. **ABSTAIN** on the unresolved.
5. **Provenance-as-defense** — retain a draft/version trail + reproducible source/citation trail. In 2026 that, not
   stylistic humanizing, is the real protection against a false AI accusation (and it matches "ground, don't
   assert").
6. **Style fidelity ≠ detector-dodging** — *measure* the anchor's burstiness/CV + function-word fingerprint to
   match a real voice; do **not** tune burstiness to "beat a detector" (legacy + gamed). Scope fidelity to scholarly
   register; **ABSTAIN** on claiming a faithful personal-voice clone (LLMs miss deep stylometric signatures). No
   recognizable living-author voice on novel claims without consent + disclosure.
7. **Match appraisal vocabulary to the deliverable** — GRADE-style certainty for empirical claims, **SANRA**'s 6
   checkpoints for a narrative survey, **AMSTAR-2** spirit for systematic claims — so the honesty tier is externally
   checkable, not bespoke.
