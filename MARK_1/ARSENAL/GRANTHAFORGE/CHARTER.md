# GRANTHAFORGE — the treatise-to-engine weapon · CHARTER

*A Mark 1 weapon that turns a **grantha** — a computational treatise (karaṇa, siddhānta, algorithm book,
numerical-methods text, technical spec, any step-by-step computational source) — into a self-contained,
**verse-by-verse, verified code engine**, stage by stage, phase by phase, without losing the path. Distilled
from the operator's Grahalāghava build (`Parvad_code_v2/grahalaghava_code_and_example/`: Ch.1–8, 60/60 worked
examples, NASA-validated). The deep verification doctrine — the heart — is `VERIFICATION_LADDER.md`; the reusable
folder + render/OCR/verify harness is `SCAFFOLD.md`.*

> **Honest tier (Mark 2):** GRANTHAFORGE is capability-EXPANSION + integration — a new task class (book → engine)
> wired into the suit with the operator's discipline. It is **NOT a ≥10% capability promotion**; ratchet stays OPEN.

---

## 1. The integration thesis (why this composes, not bolts on)
GRANTHAFORGE is Mark 1's ARMOR specialized for one task class — coding a computation book:

| Mark 1 armor | = GRANTHAFORGE |
|---|---|
| **Execute, don't vote** (run the checkable thing) | a verse is DONE only when the engine **runs** and its output is **anchored** |
| **Verify INDEPENDENTLY** (a checker ≠ the maker) | the **worked example** (or the explanation's ladder) is the verifier; self-review is theater |
| **Ground, don't assert** | every number is **OCR'd or computed**, never from memory; load-bearing facts get a source |
| **Be honest** (flag the unverified, report negatives) | **tiers** VERIFIED/DERIVED/CODED/TODO; **errata** + **commentator divergences** catalogued, never fudged |
| **Plan → produce smallest correct thing** | scaffold + page map + **pilot a few verses**, then take off |
| **Calibrate to stakes** | tolerances = the text's own rounding; effort tracks how load-bearing the verse is |

The operator's own build principles ARE this weapon: *the example is the backbone; one function per verse;
self-contained folder; OCR load-bearing; flag the commentator's divergences clearly.*

---

## 2. The thesis in one line
> A treatise is a sequence of rules. Code each rule as it reads — one function per verse-step — and **anchor**
> every rule to its verifier: a worked **example** if one exists, else the **explanation** climbed up the
> verification ladder. Build self-contained, pilot first, take off chapter by chapter, and keep a living plan so
> the build never loses the path across context resets.

---

## 3. The method (six movements)

**① SCAFFOLD.** Create the project folder with four sub-folders — engine / ground-truth / plan / source_material
— and drop in the render→OCR→verify harness. (Exact templates: `SCAFFOLD.md`.) Self-contained, Spyder/CLI-runnable,
no dependency on the rest of the repo.

**② MAP.** Establish the source's coordinate system — for a scan: the scan-page ↔ printed-page offset and the
chapter openers (confirm by reading openers, treat any index as approximate). Record in `plan/PAGE_MAP.md`.

**③ PILOT.** Run the full per-verse loop on the first few verses end-to-end (date/setup → first computation →
first verified example). This proves the harness and the page map before scale. Only then take off.

**④ TAKE OFF — the per-verse loop**, repeated for every verse/section (render → read/OCR → transcribe rule+numbers
→ record anchor → code one function per step → **verify & tier** → flag divergences/errata → update the board).
Keep ALL prior anchors green at every step (one verify command is the heartbeat).

**⑤ ANCHOR (two modes — the heart, `VERIFICATION_LADDER.md`).** Pick the verifier the text affords:
- **EXAMPLE-GOLD:** reproduce the printed example to the text's precision; prefer two examples (small/large
  multiplier) — exposes hidden constants and book slips.
- **EXPLANATION-GROUND:** build to the stated rule faithfully, then climb the ladder (units → limiting cases →
  derivation-closure → cross-source → inter-section closure → synthetic equivalent → external oracle) until ≥2
  independent rungs bind the *numbers*. Tier honestly; never call CODED "VERIFIED."

**⑥ GROUND & HAND OFF.** Where a modern oracle exists (ephemeris, dataset, reference solver), validate the
engine's real outputs against it (it catches bugs the engine's own number hides). Produce visual artifacts the
text constructs (diagrams/figures). At milestones write `BUILD_REPORT.md` (the method) + `HANDOFF_PROMPT.md`
(resume exactly here) so a fresh session follows the same footsteps.

---

## 4. Honesty rails (Mark 1, non-waivable)
- Never a number from memory — OCR a scan (its text layer is usually corrupt — distrust it) or compute it.
- The verifier (example or ladder) is the only authority on "done."
- **Two book-internal things, always catalogued, never smoothed:** (a) **errata** — the book's own arithmetic
  slips (the engine follows the stated rule/table; the slip is logged; look for a second example that
  corroborates the engine); (b) **divergences** — where a commentator differs from the base text (code both,
  record which the example uses, flag it; the operator specifically tracks these).
- **Independent-build-then-cross-check:** if reference notes/solutions exist, build WITHOUT reading them, then
  compare — convergent agreement (both independently catching the same subtlety) is the strongest signal.
- Keep `plan/01_PROGRESS.md` current so the build survives context loss; report at each chapter boundary.

---

## 5. When to engage / not engage
**Engage** when the task is "turn this computational text/spec into code that reproduces it" — a karaṇa,
siddhānta, algorithm book, numerical-methods text, a dense technical spec with worked examples or precise rules,
or any verse/section-structured computational source the user wants faithfully encoded and verified.
**Don't engage** for: ordinary feature coding (no external text being reproduced), a one-off formula, research
prose with no computational rules, or a task better served by REPRO-ML (reproduce a paper's ML pipeline) or
PROOFSMITH (formal proof). When the source is research *and* you must also build an engine, GRANTHAFORGE handles
the engine; SCHOLAR/`mark1research` handles the survey.

---

## 6. Canonical case study (the build this is distilled from)
`Parvad_code_v2/grahalaghava_code_and_example/` — the verse-by-verse Grahalāghava engine. Ch.1–8 complete,
**60/60 worked examples** reproduced, NASA/DE422-validated, with 2 book errata + several Viśvanātha-vs-Gaṇeśa
divergences logged, two parilekha figure styles (one validated against a printed Hindi-commentary figure), a
date→engine→parilekha walkthrough, and `plan/BUILD_REPORT.md` + `plan/HANDOFF_PROMPT.md`. Read its
`plan/BUILD_REPORT.md` for a worked instance of every movement above.

*Engage with `/granthaforge`. Scaffold, pilot, take off — and never lose the path.*
