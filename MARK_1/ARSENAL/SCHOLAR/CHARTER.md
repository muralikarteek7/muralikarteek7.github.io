# SCHOLAR — the Marks' research + article modes · CHARTER

*Two modes wired into Mark 1 so that "do deep research" and "write an article" engage the operator's proven,
phased, team-based methodology BY DEFAULT — instead of the Helmet quietly minimizing the team to one. Grounded in
the operator's own ground zero (the Rohini research/article workflows + the "Five Templates, One Spine" ARTICLE.md
+ the making_article playbook), then validated/refreshed against current (2026) best practice by the
`scholar-validation-research` workflow.*

> **Honest tier (Mark 2):** Scholar is capability-EXPANSION + integration — new task classes wired into the suit
> with the operator's discipline. It is **NOT a ≥10% capability promotion**; the ratchet stays **OPEN at v3**.

---

## 1. The integration thesis (why this composes, not bolts on)
The operator's 10 design principles ARE the Mark 1 armor, specialized for scholarship:

| Operator principle | = Mark 1 |
|---|---|
| Separate the hand that writes from the eyes that check; the **blind independent re-deriver** is load-bearing | **Verify INDEPENDENTLY** (a *different model* ≠ the generator) |
| Freeze the spine before anyone writes | **Plan before producing** |
| Evidence beats headcount (a cited falsifiable block vetoes) | The **honesty floor** |
| Quality is a checkable predicate with a named audience | The **κ-gate** + execute-don't-vote |
| Adaptive depth + diminishing-returns stop | **Calibrate cost to stakes** |

So Scholar is the **Helmet, specialized for research + writing** — the same orchestrator, with a roster, a phased
pipeline, and a "done" definition tuned per domain. The one thing it must do that the stock Helmet does NOT: for a
genuine research/writing task it **sizes the team UP to the topic's real breadth**, overriding the Registrar's
default minimization (which exists to protect one-liners, and wrongly suppresses scholarship).

## 2. The two modes
- **`/mark1research`** — literature survey / research on a topic. Pipeline: review-type + domain intake →
  auditable search (Recon: offline library + online, concept-block string + **mandatory backward+forward citation
  chaining**) → **N charter-driven domain-expert seats** (sized to distinct sub-domains) → consolidate
  load-bearing claims + **structured gap analysis** → adaptive **cross-model + retrieval verify-or-ABSTAIN** →
  single-pen write → provenance/argument/de-AI review. Auto-engages on "research X / literature survey / survey
  the work on…".
- **`/mark1article`** — write a scholarly article/paper/chapter. Pipeline: **intake gate** (deliverable-type,
  target venue, **style-anchor +sample**, source-of-truth, length, domain) → Freeze (frozen skeleton + **measured
  style-sheet** + venue tex-spec + empty-required compliance slots) → Components (eqns/tables/refs, **no fabricated
  DOIs**) → one-pen Draft → retrieval-gated Verify (domain lenses) → Review loop → **surgical diff-gated de-AI +
  style-mimic (content FROZEN)** → venue-reviewer gate → **numeric-diff proof that only presentation moved**.
  Auto-engages on "write an article/paper/chapter on…".
- **`/mark1article2`** — **ARTICLE 2.0**, the zero-to-draft stage-gated build for making a journal-worthy paper
  FROM SCRATCH out of real findings (proven end-to-end on Parameśvara Paper 1). Wraps the `mark1article` engine
  (which becomes the inner loop of each prose stage) with the OUTER process the engine lacked: a living `plans/`
  spine (tiered claims + progress-with-resume + framing), verified **code as source of truth built first**, a
  **data backbone before prose**, per-section cross-model audit loops, **citation grounding against held sources**,
  and a **venue-spec-driven faithful md→tex** pipeline. Doctrine: `ARTICLE_PIPELINE_V2.md` + `CASE_STUDIES/`.
  Use it (over plain `/mark1article`) for big, computation-/source-backed, multi-session builds.

Both inherit the full Mark 1 armor + Mark 2 tiering, and both run as **parameterized Workflows**
(`research.workflow.js` / `article.workflow.js`) — generalized from the operator's two scripts.

## 3. What survived validation (the principles, with verdicts)
All **10 design principles SURVIVE** (P1 evidence-beats-headcount, P2 separate-write-from-check + blind
re-deriver, P3 adaptive-depth-stop, P4 value≠difficulty, P5 selective-context, P6 freeze-the-spine, P7
hard-termination, P8 thin-slice + size-contract, P9 sane-defaults, P10 quality=checkable-predicate). Several are
*strengthened* — they re-derive the bias controls of dual-reviewer screening (PRESS / protocol-freeze /
pre-registered inclusion).

- **CLAIM A (multi-agent returns are concave, saturate ~5–10 per reasoning task): HOLDS** (verified, with
  mechanism). Saturation comes from **output correlation** among homogeneous same-model agents collapsing the
  effective independent channels; homogeneous panels plateau ~N=4, and **2 diverse agents ≈ 16 homogeneous**.
  → **the lever is DIVERSITY, not count.**
- **CLAIM B (naive de-AI "polishing" flips human text to AI-classified ~75–85%): NOT VERIFIED → treated as
  refuted.** That number is **humanizer tools *evading* detectors** (false negatives), not human text being
  false-flagged. The well-supported facts instead: AI detectors have high false-positive rates on human prose
  (0–30%, and **61.3% on non-native-English essays**, Liang 2023), paraphrasing evades them, and **retrieval is
  the only durable defense.** This makes the rail *stronger*: see §4.

## 4. The honesty rails (non-waivable — Mark 1 + the operator's method + the 2026 refresh)
1. **Never fabricate** a number, citation, DOI, or quote. Citations are **retrieval-gated**; in no-tool/paste
   contexts emit a **human VERIFY-IT-YOURSELF gate** listing every load-bearing reference + number. **ABSTAIN** on
   the unresolved — never smooth uncertainty into confident prose.
2. **Source-of-truth first.** Re-run engines (don't trust stale stored outputs); the article is downstream of a
   truth you do not invent. **Diff the numbers** to prove only presentation moved.
3. **Verify INDEPENDENTLY, cross-MODEL.** The load-bearing checker is a *different model family* ≠ the generator
   (same-model "audit" carries ~10–25% self-preference bias — partly theater). Retrieval-gate every check.
4. **De-AI is surgical + diff-gated, content FROZEN** — never a blind humanizer (those mutate facts/citations).
   **Never use an AI detector as an acceptance gate** (unreliable, biased against non-native + plain academic
   prose). The goal is *correct, clear prose for a named audience*, NOT a low detector score. *(Do not cite the
   "75–85% flip" figure — it was not verified.)*
5. **AI-use disclosure is a first-class artifact**, venue-routed (ICMJE: writing-assistance → Acknowledgments;
   data/analysis/figures → Methods; routine grammar/copy-edit exempt). An LLM **cannot be an author**.
6. **Human-in-the-loop for evidence work.** An LLM may rank/prioritize records and act as a *second-pass*
   independent checker, but may **not** be the sole includer/excluder nor the sole risk-of-bias/synthesis source.
7. **Declare the exhaustiveness contract.** A Mark research run is realistically a *rapid* or *narrative* review —
   say which corners were cut (rapid reviews have **no validated reporting guideline**), never imply systematic
   exhaustiveness you didn't perform.

## 5. The team-sizing rule (the honest answer to "team of 20–30")
> **Default 3–5 seats per reasoning task; extend toward 9–10 ONLY when the added seats are deliberately
> HETEROGENEOUS (different model, prompt, or framing).** Returns are concave because output correlation among
> homogeneous same-model agents collapses the effective number of independent channels — so two diverse seats
> beat many identical ones, and past a strong single-agent baseline (~>45% on the task) extra seats give
> diminishing or **negative** returns and uncoordinated fan-out amplifies errors. **The lever is DIVERSITY, not
> COUNT.** Prefer one blind cross-MODEL re-deriver over three more same-model agents; add a seat only if it brings
> a genuinely independent evidence channel; stop at the diminishing-returns knee.

A broad survey with 10–30 **genuinely distinct sub-domains** (your Rohini survey had 10 real charters) legitimately
fans out that wide — the count tracks *breadth of distinct charters*, surfaced and overridable, never a fixed 30 of
redundant debaters. This is the operator's own `ARTICLE.md` finding, now externally re-verified.

## 6. The humanities / history-of-science profile (the biggest new piece)
Selectable at intake (your Indus-Valley / Parvad / Ganita territory). Swaps the RCT-shaped machinery for:
- a hard **PRIMARY vs SECONDARY** source split, appraised by **provenance / edition / context** (NOT RoB/GRADE);
- discipline discovery: HSTM index, JSTOR, HathiTrust, Internet Archive, subject bibliographies + citation chaining
  (not PRISMA exhaustiveness) + the operator's offline `Books_Folder` library;
- a **meta-narrative / RAMESES** synthesis skeleton — trace how successive scholarly paradigms framed the question
  — instead of pooled-effect synthesis. **Never force a PRISMA flow diagram onto a historiographic essay.**

## 7. Architecture + where things live
`SKILL (intake gate, auto-trigger + code-word)` → `parameterized Workflow template (the engine)` →
`artifact(s) on disk` → `Mark 1 rails + Mark 2 tiering`.
- Doctrine: this `CHARTER.md` · operational reference `INTAKE_AND_RUBRICS.md` (intake question sets + journal /
  deliverable rubrics + de-AI spec) · build state `STATE.md`.
- Engines: `research.workflow.js` + `article.workflow.js`.
- Skills: `.claude/skills/mark1research/` + `.claude/skills/mark1article/` (+ globalized to `~/.claude/skills/`).
- Validation evidence: workflow `scholar-validation-research` (full verified output retained).

## 8. Status
- ✅ Ground zero read · validation research done · doctrine written.
- ✅ Operational reference (`INTAKE_AND_RUBRICS.md`) + the two skills + the two workflow engines — built, syntax-checked, globalized.
- ✅ Cross-model (Sonnet) audit done (CONDITIONAL PASS; blockers + minors fixed).
- ☐ A small end-to-end dry run of each engine · wire the auto-trigger note into CLAUDE.md/SUIT.
- Open risk to revisit (operator's own caution applies): the humanities profile is a genuinely new subsystem —
  validate it on a real artifact before fully trusting it.
