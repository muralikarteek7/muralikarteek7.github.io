# CASE STUDY — Parameśvara Paper 1 (zero → clean Isis draft)

The first real end-to-end run of the SCHOLAR article pipeline, and the evidence
base for `ARTICLE_PIPELINE_V2.md`. Project: `Parvad_code_v2/paramesavara/`.
Honest reconstruction of the exact path, including what each gate **caught**.

## The brief (operator, Stage 0)
"So much findings… write a paper worthy of *Isis*/*Osiris* … build step by step,
keep a presentable file at each step … plain crisp scholarly, non-romanticising,
not-overstating … code from scratch (function-wise, runs in Spyder) … train the
language on top journals (the prior Vedāṅga-Jyotiṣa paper was rejected for register)
… make folder `paramesavara/{code,plans,paramesvara_eclipse,gl_ayanamsa,material}`
… /mark1, do Stage 0 first: a plan in the folder." → 17 enumerated wants.

## What was actually done (stage by stage, with artifacts)
- **Stage 0.** `plans/00_MASTER_PLAN`, `01_CLAIMS` (tiered), `02_PROGRESS` (tracker +
  resume phrase). Structure decision: **two papers, Paper 1 first** (civil-day
  reckoning; ayanāṃśa → Paper 2). The `plans/` folder became the spine.
- **Stage 1.** Anchors (Plofker, Montelle, Keller–Mahesh–Montelle, Neugebauer–
  Pingree) → measured `03_LANGUAGE_PROTOCOL`: mean 18–22 w, median ~15, banned-word
  list, HARD RULE (style-not-ideas, no Eurocentric framing). The rejected-paper
  lesson: register fault was overstatement, not sentence length.
- **Stage 2.** `code/` from scratch (util/constants/ephemeris/records/circumstances/
  reckoning/build_table) + `verify.py`. DE422 via Skyfield. **One OK line per claim.**
- **Stage 2b.** `bhutasamkhya.py` + `verses.py` + `verify_bhutasamkhya.py` —
  independent re-decode of all 13 verse ahargaṇa (closed open-item O2).
- **Stage 3.** `dossier.py → DOSSIER.txt` (per-eclipse data backbone) **before** prose;
  `nasa_crosscheck.py` (independent NASA id of all 13 — **caught a lunar-type mislabel**,
  fixed by adding umbral-magnitude to `circumstances.py`); `figures.py` (3 figures).
  Then `SECTION_03_eclipses.md` via the inner loop.
- **Stages 4–5.** `SECTION_04_chandrahari` + `SECTION_05_core_argument` via the loop.
- **Calibration.** Engaged `mark1article`, read the SCHOLAR doctrine, wrote
  `08_ARTICLE_INTAKE` (formal contract + gap analysis), ran **GRANTHA**.
- **Stage 7.** Pulled the *Isis* author guide → froze the venue spec (Chicago
  footnotes, ≤15k words, no bibliography). Built `paper/` with a faithful `md_to_tex.py`
  (byte-faithfulness proven), `gen_table.py`, the figures; compiled clean (XeLaTeX).
- **Stage 8.** Front matter (intro/conclusion/abstract), plain, last.
- **Stage 9.** Chicago-footnote apparatus rebuild; **citation grounding against held
  sources**; diff-gated de-AI. Final: clean 8-page draft.

## What the gates CAUGHT (why the disciplines exist)
- **Independent-source cross-check (Stage 3):** NASA catalogue showed the 1423 lunar
  event was a shallow *partial-umbral*, not the "total/umbral" the code's coarse label
  implied → added a proper umbral-magnitude classifier.
- **Cross-model audit (per-section):** (a) a derived threshold written 0.921° where the
  sourced value was 0.9235°; (b) an **overclaim** — "the sunset reading can be stated as
  established" conflated *values established* with *interpretation established*; (c) an
  **unearned categorical generalization** in the conclusion (the exact rejected-paper
  failure mode) → hedged.
- **Citation grounding against held sources (Stage 9):** TWO near-fabrications stopped —
  (i) "Shukla 1957, *IJHS*" was impossible (IJHS began 1966); the reading was actually
  Chandra Hari's report → re-attributed; (ii) the **Stone 1985** entry was wrong in title,
  journal, and pages — reading the held offprint corrected it to *Gaṇita Bhāratī* 7,
  nos. 1–4 (1985): 1–12. Also fixed: the *Goladīpikā* editor-led entry (Sarma, Adyar 1957).
- **de-AI measurement:** the draft's burstiness was AI-uniform (CV 0.41 vs human ~0.5–1.0);
  surgical splits lifted it to 0.47, diff-gate PASS (numbers/cites/IAST identical vs backup).

## A correction that emerged late (shows the spine working)
The operator later found the primary text (Jyotirmīmāṃsā §17.i, Sarma 1977 p.44): the
Parameśvara–Nīlakaṇṭha ayanāṃśa rate is the **daśāṃśona** rule = **54″/yr** (1′/yr less
one-tenth), not the 60″/yr the older code/memory assumed; the text's worked value
(14°26′ at ~38 yr before 1435) proves it. Corrected the stale calculator + the project
memory; `final_code/ayanamsa/` already had it right. (Paper-2 material; recorded for
completeness — it is the kind of late primary-source correction the tiered-claims +
held-source-grounding disciplines are built to absorb cleanly.)

## What this run taught the weapon (folded into V2)
1. The `plans/` folder spine (tiered claims + progress-with-resume + settled framing) is
   the thing that made a multi-session build cohere — the stock engine had no such spine.
2. Code-as-source-of-truth FIRST + a data backbone BEFORE prose is what made every number
   defensible and the prose fast to write.
3. The per-section cross-model audit and the held-source citation grounding are not
   ceremony — each caught real, venue-fatal errors.
4. Pulling the venue spec is load-bearing: it forced the Chicago-footnote rebuild that an
   "assume house style" path would have shipped wrong.
5. The faithful `md→tex` pipeline kept the typeset prose provably identical to the audited
   text through the whole apparatus rebuild + de-AI.

Outcome: zero → a complete, clean, verified, venue-shaped 8-page *Isis* draft, fully
reproducible from `paramesavara/README.md` + `paper/build.sh`.
