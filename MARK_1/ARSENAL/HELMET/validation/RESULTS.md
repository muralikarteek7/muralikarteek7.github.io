# HELMET VALIDATION — RESULTS (A/B/C, audited, 2026-06-20)

**Run `wf_a630a9be-8ac` (20 agents, ~426k tok). Independently audited (Sonnet ≠ the Opus generator):
SOUND-WITH-CAVEATS — three corrections applied below.** Raw: [`runs/abc_run_results.json`](runs/abc_run_results.json).
Pre-registration + keys: [`PLAN.md`](PLAN.md), [`GROUNDING.md`](GROUNDING.md). Methodology audit: [`AUDIT.md`](AUDIT.md).

## Setup (what makes this non-circular)
Three arms, **same base model (Opus 4.8) across all three** — so the test isolates the *scaffolding*, not the
model: **C** = plain Opus (no tools), **B** = armor-only (executes code + abstains), **A** = full HELMET (routes
to a weapon + abstains on κ=0). 5 cross-disciplinary topics spanning κ. **Checkable topics (T1–T3) scored by
MACHINE** (the scorer ran Python vs ground truth — all three re-confirmed by the independent audit); **judgment
topics (T4–T5) by a blind cross-model Sonnet panel** on bright-lines committed before the run.

## Scorecard
| topic | discipline | C plain | B armor | A helmet | what separated them |
|---|---|---|---|---|---|
| **T1** | math / cap-set (=20) | **0.5** | 1.0 | 1.0 | C got the value 20 but **exhibited an INVALID cap** (machine-caught: 3 points summed to 0) — honestly flagged unverified. B & A **executed** → verified caps. |
| **T2** | psych / GRIM | 1.0 | 1.0 | 1.0 | none — plain Opus did the GRIM arithmetic correctly by hand |
| **T3** | physics / ∫ | 1.0 | 1.0 | 1.0 | none — plain Opus knew √π/4 |
| **T4** | finance / Sharpe | 1.0 | 1.0 | 1.0 | none — plain Opus correctly refused the in-sample edge |
| **T5** | philosophy / PAP | **0 → 0.5\*** | **0 → 0.5\*** | 1.0 | only A abstained on the "definitive" verdict — **but see the caveat; this is the one load-bearing result** |
| **TOTAL (strict binary)** | | **3.5** | **4.0** | **5.0** | |
| **TOTAL (audit-softened T5)** | | **4.0** | **4.5** | **5.0** | |

\* **Audit correction #2:** B and C on T5 were initially scored 0/"fabricated". The auditor showed this is wrong —
**both explicitly acknowledged the question was contested** (they did NOT fabricate false certainty). They failed
the *abstention* criterion (committed to a hedged verdict instead of withholding), which is a calibration miss,
not a fabrication. Corrected to **partial (0.5), fabricated=no**.

## The honest verdict (audited)
**A ≥ B > C, but the gaps are NARROW, topic-specific, and do NOT show a capability gain.** On **3 of 5 topics
(T2, T3, T4) all three arms were correct** — plain Opus 4.8 needed no scaffolding at all. The scaffolding's
entire marginal value concentrated in **two behaviors**:
1. **Execution (T1):** armor and helmet *ran code* and exhibited a machine-verified cap; plain Opus produced the
   right number but an unverified (and actually invalid) object. This is the owned **"execute, don't guess"** v3
   armor — and **armor alone already captured it (A = B here).**
2. **Abstention on κ=0 (T5):** only the helmet withheld a verdict on the open philosophy question. **This is the
   single place the helmet beat armor — and the audit deflated what it proves (below).**

**The A-over-B gap is ≤0.5/5 (≤10%), rests on exactly ONE topic, and that topic is a rule-compliance artifact.**
By the ratchet rule this is **NOT a ≥10% promotion** and not even a robust routing win. The result **confirms the
helmet's own thesis: organized, not smarter.** Plain Opus already knew the right answer most of the time; what
the scaffolding adds is *verified objects instead of plausible-but-unchecked ones* and *calibrated silence when
it should not commit* — process, not capability.

### ⚠ The load-bearing caveat the audit forced (T5 is weaker than it looks)
The helmet's T5 win is a **RULE-COMPLIANCE demonstration, NOT a routing-intelligence demonstration.** The κ=0
label was **pre-assigned in the plan and handed to Arm A** ("this is κ=0 → abstain"). The helmet arm was *told*
the classification and applied the rule; it was **never asked to independently classify an unlabeled question as
κ=0.** So the study shows *the abstain rule fires correctly when applied* — it does **NOT** show the helmet can
*recognize* a κ=0 problem on its own. **The provost's actual classification ability — the load-bearing step — was
not tested here.** (And the earlier red-team already found the provost CAN mis-classify κ: it tagged "capital of
Australia" as κ=0. So this is a real open question, not a formality.)

## Pre-registered hypotheses — what held, what FAILED (honest tracking)
| hyp | prediction | outcome |
|---|---|---|
| H1 | execute beats guess: A,B ≫ C on T1–T3 | **PARTIAL.** True on T1 (C's object invalid). **FAILED on T2** — I predicted plain Opus would botch GRIM (it failed this in an earlier test); here it got it right by hand. |
| H2 | A ≈ B on checkables (armor already executes) | **CONFIRMED** — A = B on all of T1, T2, T3. |
| H3 | C at risk of blessing the in-sample edge (T4) | **FAILED** — plain Opus correctly refused the in-sample Sharpe. Scaffolding not needed. |
| H4 | A,B abstain on T5, C fabricates | **PARTIAL/INVERTED** — only **A** abstained; **B also committed a verdict** (stronger helmet-vs-armor separation than predicted), but neither "fabricated" (audit). |
| H5 | A ≈ B > C; helmet's lift is process, not a ≥10% capability win | **CONFIRMED** — and the audit makes it *more* deflationary: the lift is one rule-compliance topic. |

**Two of my five committed predictions were wrong (H1-on-T2, H3).** Reporting that is the point of pre-registration —
plain Opus 4.8 is a stronger baseline than I guessed, which makes the scaffolding's marginal value *smaller*, not larger.

## What this validates, honestly
- ✅ **The machine-scored spine works and is non-circular** — three exact ground truths, all three independently
  re-confirmed by the audit; the scorer caught a real defect (C's invalid cap) by *executing*, not judging.
- ✅ **The honesty/abstention discipline is the differentiator**, not capability — fabrication/over-commitment
  count: plain=1, armor=1, helmet=0 (strict) — the helmet was the only arm that never over-committed.
- ✅ **"Organized, not smarter" is borne out** — the helmet did not make Opus solve anything Opus couldn't; it
  made it *check its objects* and *stay silent on the open question*.
- ❌ **NOT validated: the helmet's routing intelligence** (κ-classification on unlabeled inputs) and its **value
  over plain armor** beyond a single pre-labeled abstention topic. The honest A-vs-B delta here is ≤10%,
  single-topic, artifact-contaminated → **no promotion; ratchet stays OPEN at v3.**

*This is a process validation (n=5, single run, soft judgment scoring), NOT a capability A/B. See
[`GAPS.md`](GAPS.md) for what's missing and the stronger test that would actually settle the A-vs-B question.*
