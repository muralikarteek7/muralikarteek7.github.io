# ARTICLE 2.0 — the Zero-to-Draft stage-gated research-paper pipeline

*A SCHOLAR weapon. Distilled from the first real end-to-end run (Parameśvara
Paper 1, zero → clean 8-page Isis draft; case study in `CASE_STUDIES/`). It does
NOT replace `mark1article` / `article.workflow.js` — that 6-phase engine is the
INNER LOOP of each prose stage here. Article 2.0 is the OUTER project process the
engine never modelled: how a verified research build becomes a published-quality
draft, slowly, stage by stage, on a persistent record.*

> **One line.** An article is the *last* artifact of a *verified research build*,
> not a writing task bolted onto findings. You build the truth (runnable code +
> grounded sources), then the prose that reports it — one stage at a time, each
> ending in a presentable artifact, all governed by a living `plans/` folder that
> outlives any single session.

---

## 0. When to engage
A request to take real findings/data and produce a journal-worthy paper (or
thesis chapter) from scratch — especially when (a) the findings rest on
computation or primary sources, (b) the standard is a top venue, and (c) it is too
big for one sitting. For a quick write-up of already-settled prose, the stock
`mark1article` engine alone is enough; Article 2.0 is for the full build.

Engage as **Mark 1 · Article (2.0)**. Inherits all of Mark 1 ARMOR + Mark 2 tiers
+ the SCHOLAR honesty rails (`CHARTER.md §4`, `INTAKE_AND_RUBRICS.md §E`).

---

## 1. THE SPINE — a living `plans/` folder (the single biggest difference-maker)
Create it at Stage 0; **update it at the end of every stage**. It is the contract,
the memory, and the resume point. It is what lets the build span many sessions
without drift. Minimum set:

| file | what it holds | why it carries the build |
|---|---|---|
| `00_MASTER_PLAN.md` | what the project is; the target standard; the build pipeline mapping the operator's points → stages; project-specific honesty rails | the standing plan + decision record |
| `01_CLAIMS.md` | every claim with an **EVIDENCE TIER**: `verified (run)` / `textual (attested in a held source)` / `inferred (not yet read)` / `open` | the tier GOVERNS the prose — no claim is written above its tier |
| `02_PROGRESS.md` | the stage tracker `[ ]/[~]/[x]`, the **current position**, queued tasks, and a one-line **RESUME PHRASE** | any session reads this first and continues exactly where it stopped |
| `03_LANGUAGE_PROTOCOL.md` | the **measured** style sheet (from anchors) + banned-words/overstatement list + the **HARD RULE** | drafting follows it; the de-AI pass checks against it |
| `0N_FRAMING.md` | the **settled thesis**: minimal-fact vs interpretation vs corollary kept visibly distinct; "what we do NOT claim"; the respectful boundary against prior work | stops scope-creep and overclaim at the source |
| topic / audit / source-resolution notes | as needed (e.g. notes on the key prior author; an audit of work-to-date vs the brief; a resolved-coordinate file) | captures what scrutiny changed |

Rule: **if it isn't in `plans/`, it didn't happen.** Decisions, reversals, and the
evidence tier of every claim live here, not only in chat.

---

## 2. THE STAGES (each ends in a presentable artifact saved to disk)

**Stage 0 — Plan + skeleton.** Make the folder skeleton (`code/`, `plans/`,
`<dossier>/`, `material/`). Write `00`/`01`/`02`. Get the operator's structure
decision (one paper / two / two-part). *Artifact: the plan files.*

**Stage 1 — Language training.** Pull 2–3 anchor articles by top authors of the
venue's field into `material/`. **MEASURE** a style sheet from them (sentence-length
mean + **CV/burstiness**, function-word fingerprint, hedging density, a
"never-does-this" list) → `03`. Fix the HARD RULE: *adopt how-it-is-written, never
what-is-claimed; no field-specific interpretive bias.* *Artifact: `03`.*
> Lesson source: the prior paper was rejected for register ("not journal language").
> Sentence length was fine; the fault was overstatement + editorial framing. Bake
> that into `03` as banned words + "state only what the evidence on the page
> supports, once, then stop."

**Stage 2 — Code from scratch = the source of truth.** Self-contained, runnable in
the operator's IDE, **function-per-concern, a VERIFIER PER CLAIM**. Every numerical
claim is machine-checked and **run, not asserted**. Model it on the operator's
`final_code/ayanamsa_study/` style (one folder, flat imports, small functions).
*Artifacts: `code/` + a green `verify.py` (one OK line per claim).*

**Stage 3 — Data backbone + independent cross-check (before any prose).** Generate
the machine-checked **per-item data artifact** (e.g. a `DOSSIER.txt`: one block per
eclipse/sample/case with every figure the prose will cite). Cross-identify against
an **independent source** (e.g. a NASA catalogue, a second edition) — this grounds
the identifications and *catches mislabels the engine alone won't*. Generate the
figures from the verified code. *Artifacts: the dossier, the cross-check table, the
figure files.*

**Stages 4…N — prose sections, ONE AT A TIME, via the INNER LOOP.** For each
section run the stock engine's phases at section scale:
1. **FREEZE** a paragraph-level skeleton: each ¶ bound to its load-bearing
   number(s) + the exact source, plus the section's honesty rails. (A small
   `SECTION_x.FREEZE.md`.)
2. **ONE-PEN DRAFT** to the freeze + the `03` style sheet + the length budget.
   Mark every load-bearing number with unit + source.
3. **MECHANICAL REGISTER CHECK** (cheap, runs): sentence-length mean + CV,
   em-dash count, banned-word grep. Tighten to target.
4. **CROSS-MODEL AUDIT** (a *different* model than the drafter): fact-check every
   number against the source-of-truth (re-run the code), and check the
   project + section honesty rails. *The auditor returns findings; the
   orchestrator is the single hand that edits.*
5. **APPLY FIXES**, re-check, update `01`/`02`.
> This loop earns its keep: on the real run it caught a wrong derived threshold,
> an "established" overclaim (values vs interpretation conflated), and an unearned
> categorical generalization (the rejected-paper failure mode) — each fixed before
> it reached the venue.

**Stage 7 — LaTeX, venue-shaped.** **PULL the venue's author guide** (length cap,
reference style, data/AI policy) and **freeze a venue tex-spec** — this is
load-bearing (it drove a full Chicago-footnote rebuild on the real run, replacing
author–date). Build a **faithful `md→tex` pipeline**: author prose in readable
Markdown, convert mechanically, and **prove byte-faithfulness** (the prose must be
unchanged once apparatus is stripped). Generate the table + figures from the code.
Add the compliance slots (Data/Code, AI-use disclosure, Competing Interests).
**Compile and SEE it** — never claim a clean build you did not run (target: 0
overfull, 0 undefined). *Artifact: a compiling PDF.*

**Stage 8 — Front matter LAST.** Introduction, conclusion, abstract — written
plain, after the body exists, to the same inner loop. *Artifact: complete draft.*

**Stage 9 — Venue gate.** (a) **Ground every citation against the HELD source**
(κ=1: read the actual offprint/edition — this caught two near-fabricated citations
on the real run); Indic/Sanskrit → run **GRANTHA** (`GRANTHA_INDIC_CITATION_LENS.md`).
(b) **de-AI as MEASUREMENT**: measure the anchor's burstiness/CV, lift the draft's
toward it by surgical sentence-boundary edits, **diff-gate content-frozen** (numbers
+ entities + cite-keys identical vs a pre-de-AI **backup**), prove only presentation
moved. Never gate on an AI detector. *Artifact: the venue-ready draft + the
numeric-diff proof.*

---

## 3. THE NON-NEGOTIABLE DISCIPLINES (the weapon's edge — keep all ten)
1. **Living `plans/` folder** as the spine — plan + tiered claims + progress(+resume) + language + framing, updated every stage. Resumable across sessions.
2. **Code = source of truth, built FIRST.** Every number runs (`execute, don't assert`); one verifier per claim.
3. **Data backbone before prose**, cross-checked against an independent source.
4. **Per-section freeze → draft → register → cross-model audit → fix.** The auditor ≠ the drafter.
5. **Evidence tiers govern the prose.** Keep minimal-fact / interpretation / corollary visibly distinct; never write a claim above its tier.
6. **Ground citations against held sources;** abstain on the unconfirmed; never ship a plausible guess (it caught 2 fabrications). GRANTHA for Indic.
7. **Pull + freeze the venue spec;** let it drive the apparatus (footnotes vs author–date, length, AI policy).
8. **Faithful `md→tex`** so the typeset prose never drifts from the audited text; prove it.
9. **de-AI = measured + diff-gated + content-frozen;** back up before the pass.
10. **Slow, stage-gated, one artifact per stage.** Never overwhelmed; never skip a gate.

---

## 4. How it composes with the rest of SCHOLAR
- **`mark1article` / `article.workflow.js`** — the 6-phase engine (Freeze→Components→Draft→Verify→Review→DeAI) = the **inner loop** of each prose stage (4…N, 8). Article 2.0 supplies the missing **outer process** (Stages 0–3, 7, 9 + the spine). Keep both; 2.0 calls the engine.
- **`mark1research`** — if the findings don't exist yet, run research mode first; its survey + tiered claims seed `01_CLAIMS.md`.
- **`CHARTER.md` / `INTAKE_AND_RUBRICS.md`** — the intake gate, deliverable/venue rubrics, de-AI spec all still apply; Article 2.0 records the intake as `08_ARTICLE_INTAKE.md` in `plans/`.
- **`GRANTHA_INDIC_CITATION_LENS.md`** — the Stage-9 citation lens for Sanskrit/Indic work.
- **Honesty rails** — Mark 1 + Mark 2 + SCHOLAR §4, non-waivable: never fabricate; abstain on the unresolved; AI-use disclosed; no AI-detector gate; de-AI never touches the evidence layer.

Ratchet: capability **EXPANSION** (the proven outer process, now reusable), not a ≥10% promotion — ratchet stays OPEN at v3.
