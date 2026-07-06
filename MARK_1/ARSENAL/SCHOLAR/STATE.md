# SCHOLAR — research + article modes for the Marks · BUILD STATE

*Code-red integration (started 2026-06-22): wire the operator's proven research + article methodology into the
Marks so "deep research" / "write an article" engage the right team + phased process by DEFAULT. This file is the
stable spec; the refinable specifics (exact intake questions, journal/deliverable rubrics, de-AI spec, team-sizing
numbers) are filled from the `scholar-validation-research` workflow report.*

---

## Why this exists (the diagnosis — grounded in the operator's own files)
The method was never missing — it was built twice (`Rohini Sankat/*_workflow.js`) and meta-researched once
(`ARTICLE.md` — "Five Templates, One Spine"). It just wasn't wired into the Marks. Three seams:
1. **The Helmet's Registrar minimizes team size** ("anti-theater") — so "deep research" gets sized DOWN, never up
   to the operator's 10-charter team. Scholar mode **overrides** that minimization for genuine research breadth.
2. **The templates were never registered as Mark modes** — no trigger maps "research X" → the survey workflow or
   "write an article" → the academic-writing workflow.
3. **The decision-gates + the operator's standing writing-rules were never captured** (venue, chapter-vs-paper,
   style-anchor, source-of-truth; the "capture every owner rule in a traceability table or it gets dropped" rule).

## The integration thesis (why it composes cleanly)
The operator's 10 design principles ≈ the Mark 1 ARMOR. "Separate the hand that writes from the eyes that check" =
verify independently; "blind re-deriver / a *different* model" = cross-model audit; "freeze the spine" =
plan-before-produce; "evidence beats headcount" = the honesty floor; "quality = a checkable predicate" = the
κ-gate. **The five templates ARE the Helmet, specialized per domain.** Both workflows are already in the
Workflow-script format the Marks run — so this is wiring, not new machinery.

## Locked decisions (operator, 2026-06-22)
- **Trigger:** BOTH — auto-default (the Marks detect a research/article request and engage the mode, running the
  intake gate) **and** explicit code-words `/mark1research` · `/mark1article`.
- **Scope (now):** Research + Article only. Article mode covers journal-paper / review-synthesis / book-chapter /
  thesis-chapter via the intake gate. (Content/App/Designer/Project-Improver = later.)
- **Naming / home:** `/mark1research` + `/mark1article`, homed here in `MARK_1/ARSENAL/SCHOLAR/`, globalized to
  `~/.claude/skills/` like the other Mark skills.
- **External research:** focused validation + refresh (the operator's `ARTICLE.md` is already the 24-expert deep
  research) — running as workflow `scholar-validation-research` (wf_8fd5e5bb-2eb).

## Architecture
```
user says "research X" / "write an article on Y"   (or /mark1research · /mark1article)
        │  auto-detect (Mark doctrine routes research/writing requests here) OR explicit code-word
        ▼
  SKILL: intake gate  ── asks the missing dials (research vs article set) ──► fills the run contract
        ▼
  reusable parameterized Mark WORKFLOW template  (research.workflow / article.workflow — generalized from the
  operator's two scripts)  →  runs the phased pipeline (team sized to the topic) → writes artifact(s) to disk
        ▼
  Mark 1 honesty rails + Mark 2 tiering over the output
```
Build artifacts (this folder): `CHARTER.md` (doctrine) · `INTAKE_AND_RUBRICS.md` (intake question sets + journal /
deliverable rubrics + de-AI spec + the owner writing-rules guidance) · `research.workflow.js` +
`article.workflow.js` (the reusable engines). Skills: `.claude/skills/mark1research/` +
`.claude/skills/mark1article/` (+ globalized to `~/.claude/skills/`).

## Honesty rails (inherited from Mark 1 + the operator's method — non-waivable)
- **Never fabricate** a number, citation, DOI, or quote; **abstain** on the unresolved.
- **Source-of-truth first**; re-run engines (don't trust stale stored outputs); diff numbers to prove only
  presentation moved.
- **Verify independently / cross-model** (a different family ≠ the generator) + retrieval-gated checks.
- **De-AI is surgical + diff-gated** (never a blind humanizer); **no AI-detector used as an acceptance gate**;
  produce an **AI-use disclosure**; in no-tool/paste contexts, a **human VERIFY-IT-YOURSELF gate**.
- **Team size = breadth of genuinely DISTINCT sub-domains, NOT a fixed count** (the canonical rule is CHARTER §5):
  default **3–5 seats** per reasoning task; extend toward **9–10 ONLY when the seats are deliberately heterogeneous**
  (different model/prompt/framing). Verified: homogeneous same-model agents are correlated and saturate (~N=4); the
  lever is **DIVERSITY, not count** (Rohini had 10 *distinct* charters — never 30 redundant debaters). Visible + overridable.

## Status
- ✅ Ground zero read · decisions locked · validation research done (`scholar-validation-research`, all verdicts folded in).
- ✅ Doctrine (`CHARTER.md` + `INTAKE_AND_RUBRICS.md`) · the two skills · the two reusable engines — built, syntax-checked, globalized.
- ✅ Cross-model (Sonnet) audit done → CONDITIONAL PASS, fixes applied.
- ✅ **End-to-end run DONE** — Parameśvara Paper 1 (`Parvad_code_v2/paramesavara/`): zero → clean 8-page *Isis*
  draft. The real dry run; it exposed the stock 6-phase engine's gap (no OUTER project process: spine + code-first
  + data-backbone + venue-driven LaTeX + held-source citation grounding).
- ✅ **ARTICLE 2.0 weapon authored** from that run: `ARTICLE_PIPELINE_V2.md` (zero-to-draft stage-gated pipeline) +
  `CASE_STUDIES/paramesvara_paper1.md` (evidence + what each gate caught) + skill `~/.claude/skills/mark1article2/`.
  **`mark1article` is KEPT** — its 6-phase engine is the inner loop of each prose stage in 2.0; 2.0 adds the outer process.
- ☐ Wire the auto-trigger note into CLAUDE.md/SUIT (note `mark1article2` for full from-scratch builds).
- Ratchet OPEN at v3 — this is integration + capability-EXPANSION (new task classes wired in), not a ≥10%
  capability promotion.
