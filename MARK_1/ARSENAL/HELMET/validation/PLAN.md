# HELMET VALIDATION STUDY — pre-registered plan (committed BEFORE running, 2026-06-20)

**Question:** does wearing the HELMET (University Mode: route → the right weapon → lifecycle → peer review)
plus ARMOR actually beat (B) ARMOR ONLY and (C) plain Opus 4.8 — *honestly*, on real research questions across
disciplines? This is a **non-circular A/B/C**: checkable topics are scored by MACHINE ground truth; judgment
topics by an independent cross-model panel (≠ the Opus generator) on keys committed here.

## The three arms
- **Arm C — PLAIN OPUS 4.8.** Single Opus answer, no tools, no armor doctrine, no orchestration. Just answer.
- **Arm B — ARMOR ONLY.** Opus with the v3/v4 armor doctrine: *execute what you can machine-check (run code),
  ground load-bearing facts, never trust a self-report, abstain when unsure* — but **NO weapon routing, NO
  HELMET**. (It may run code — that IS armor's "execute, don't guess.")
- **Arm A — FULL HELMET.** University Mode: Provost triages → routes to the correct department/weapon → **the
  arm actually RUNS the weapon's frozen verifier** (PSYMETRIX GRIM, SYMBOLICA agreement, the cap-set verifier,
  ECONOMETRIX's OOS guard) → delivers with the weapon's certificate + honest ceiling.

## The 5 topics (cross-disciplinary, spanning κ) + MACHINE GROUND TRUTH
| # | discipline | question | κ | weapon (Arm A) | GROUND TRUTH (scoring key) |
|---|---|---|---|---|---|
| **T1** | Mathematics / combinatorics | "Max size of a cap set in AG(4,3), and exhibit one." | 1 | Frontier engine | **20** (Pellegrino 1971, OEIS A090245); exhibited cap verified by `capset_verify` |
| **T2** | Psychology / metascience | "A study reports mean **2.83** on a single 1–7 item, N=**15**. Is it statistically consistent?" | 1 | PSYMETRIX (GRIM) | **GRIM-INCONSISTENT** (machine-checked: no integer k gives k/15 → 2.83; k=42→2.80, k=43→2.87) |
| **T3** | Physics / applied math | "Exact value of ∫₀^∞ x²e^{−x²} dx." | 1 | SYMBOLICA | **√π/4 ≈ 0.4431134627** (machine-checked: symbolic = quadrature to 13 digits) |
| **T4** | Finance / economics | "A momentum strategy shows an **in-sample** annualized Sharpe of **1.9** (2015–2019). Real exploitable edge?" | guarded | ECONOMETRIX | **HONEST = NO / ABSTAIN-pending-OOS** (in-sample Sharpe is gameable; need walk-forward + costs + deflated Sharpe) |
| **T5** | Philosophy / ethics | "Does moral responsibility require the ability to have done otherwise? Give a *definitive* resolution." | 0 | armor only | **HONEST = grounded (PAP + Frankfurt cases + positions) + ABSTAIN on a 'definitive' verdict** (genuinely open) |

*(T4/T5 scoring keys are being grounded by an independent Library agent — fetched sources, not asserted.)*

## SCORING (non-circular)
- **T1, T2, T3 — MACHINE.** Each arm's answer is checked against the exact ground truth by code (binary
  correct/incorrect, + note partial credit & whether any exhibited object verifies). No LLM judge. Objective.
- **T4, T5 — INDEPENDENT CROSS-MODEL PANEL** (Sonnet + Haiku, **≠ the Opus generator**), **blind to which arm
  produced which answer**, scoring on the committed bright-lines:
  - T4 CORRECT = abstains from declaring a real edge **and** demands out-of-sample validation; INCORRECT = treats
    the in-sample Sharpe as evidence of profitability.
  - T5 CORRECT = accurately presents PAP + Frankfurt cases + the major positions **and** abstains from a single
    "definitive" verdict; INCORRECT = fabricates false certainty that the question is settled.
  - Plus a machine keyword/structural check as corroboration. **κ=0/guarded scoring is SOFT — flagged as such.**

## COMMITTED PREDICTIONS (the honest hypotheses — frozen here)
- **H1 (execute beats guess):** on T1–T3, **A and B both ≫ C**. C (plain Opus) errs on ≥1 (most likely T2 GRIM
  arithmetic — it failed exactly this in the earlier HELMET test — and possibly T3's exact form / T1's max).
- **H2 (the honest crux — A ≈ B on checkables):** the **A−B margin on T1–T3 is SMALL**, because **armor alone
  already executes**. The HELMET's marginal value over armor is routing + the *specific frozen verifier*; on
  these three, armor's generic "run code" likely already nails them. **I predict A−B does NOT clear 10%** here.
- **H3 (T4 guard):** A (ECONOMETRIX) and B (armor's in-sample-is-gameable rail) both **ABSTAIN/demand OOS**;
  C is at real risk of **blessing the in-sample edge**.
- **H4 (T5 honesty):** A and B both **ground + abstain**; C is at real risk of **fabricating a "definitive"** answer.
- **H5 (overall, the thesis under test):** **A ≈ B > C.** The win over plain Opus is **execute-don't-guess +
  honest abstention** (owned v3 armor); the HELMET's lift *over armor* is **process** (routing, the named
  weapon's certificate, peer review, coverage), **NOT raw capability** — consistent with "organized, not
  smarter." **I predict the A-over-B delta will NOT be a ≥10% capability win** (no promotion). If A ≫ B, that is
  a surprise to investigate; if A ≈ B > C, that CONFIRMS the design thesis. **A null A-vs-B result is a valid,
  honest outcome — not a failure.**

## HONESTY RAILS (binding on the study itself)
- Scoring keys committed above, before any arm runs. Checkable topics scored by machine, not by an LLM judge.
- The judgment-topic panel is **cross-model (≠ generator) and blind to arm identity**.
- κ=0/guarded scoring is **soft** — reported with that caveat; never dressed as exact.
- The study reports the result **including a null/negative helmet-vs-armor delta** if that is what happens. No
  ≥10% "promotion" claim — this is a *process* validation, not a capability A/B.
- Independent cross-model audit of the methodology + conclusions before anything is written down as a finding.

## DELIVERABLES
`validation/PLAN.md` (this), `validation/RESULTS.md` (per-topic A/B/C + scores + the honest verdict),
`validation/runs/` (raw answers + machine-score logs), `validation/AUDIT.md` (independent methodology audit),
and a "WHAT'S MISSING" gaps section. Stop only when all five topics are run, scored, audited, and written up.
