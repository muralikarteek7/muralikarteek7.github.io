# HELMET + ARSENAL — STATE & HANDOFF (paused 2026-06-20)

> **Read this first to resume.** This is the single authoritative reference for the HELMET (University Mode)
> orchestration layer and its 12-weapon arsenal. Built, validated, and **paused at an honest stopping point** —
> not abandoned. Everything below is grounded in a machine-check run on the pause date (gates re-run, not asserted).

---

## 0. TL;DR — what this is and where it stands
The **HELMET** is the third layer of the v5 box (ARMOR + WEAPONS + **HELMET**): a meta-orchestrator that, given
any problem, **triages it → routes to the right specialist/weapon → verifies independently → integrates honestly,
abstaining where no verifier exists.** It **calls** armor + weapons; it does not replace them.

**Status: BUILT + VALIDATED + PAUSED. Honest framing (non-negotiable, holds): the HELMET makes the model
ORGANIZED, not SMARTER — it cannot exceed the model's capability ceiling.** It is a **capability EXPANSION
(process), NOT a ≥10% promotion.** The ≥10% capability ratchet stays **OPEN at v3** (it was never the helmet's
job to move it). Nothing failed against its own spec — the validation *confirmed* the design thesis.

## 1. What is BUILT + VERIFIED (machine-checked on pause date)
**HELMET core** (`Expanding_Frontiers/HELMET/`):
- `provost.py` — deterministic routing brain, **selftest PASS (8 cases)** incl. anti-theater (DESK) + the
  groundable-κ fix from the red-team.
- `registry.json` — **10 departments** + Dean + 6 integrity rules + 4 registrar rules.
- `orchestrator.js` / `redteam.js` — runnable multi-agent Workflows (Provost → department → peer-review ≠ generator).
- `README.md`, `SPEC.md` (grounded in science-of-science sources), `AUDIT.md`, `tests/` (3 committed-prediction runs).

**The 12-weapon arsenal — ALL 11 buildable gates re-run GREEN on pause date** (Frontier engine = the 12th, in `cap_set/`):
| weapon | dept | κ | one-line |
|---|---|---|---|
| Frontier Construction Engine | MATH_TCS | S | construct/reproduce a machine-verified extremal object |
| SOCIUS | SOCIAL_SCI | A | empirical social-science reproduce + multiverse-stress |
| PSYMETRIX | QUANT_PSYCH | A+S | psychometrics + exact GRIM/GRIMMER forensics |
| CODEFORGE | CS_ENG | S | code/algorithm synthesis gated by tests/0-1-principle/symbolic identity |
| PROOFSMITH | MATH_TCS | S | formal proof, Lean kernel + `#print axioms` 4-check gate |
| OPTIMA | CS_ENG_OR | S | exact optimization w/ an independent 4-part certificate |
| SYMBOLICA | NAT_SCI | ~0.9 | exact closed-forms via ≥2-independent-method agreement |
| ECONOMETRIX | ECON_FIN | A(guarded) | finance/causal: OOS-only verdicts (in-sample is gameable) |
| TRIALGUARD | STATS/Bio | A+S | clinical-trial forensics (Carlisle) — inconsistency≠fraud |
| FACTHARNESS | core facility | S | universal grounding/fabrication check (promoted from SOCIUS S-GROUND) |
| REPRO-ML | CS_ENG | A | ML-eval reproduction + contamination + significance |
| REDCELL | CS_ENG_SECURITY | S | authorized/defensive security, fail-closed auth gate |

Registered: `Next/BOX_V5.md` + `registry.json` + `Legacy/EVOLUTION_LOG.md` **C37–C46**. Backlog: `weapons/WEAPONS_BACKLOG.md` (9/9 ✅).
Each weapon has SPEC + README + AUDIT + GROUNDING + demo(s) and an independent cross-model audit.

## 2. What was VALIDATED — the honest findings (`HELMET/validation/`)
An A/B/C study: **C** = plain Opus · **B** = armor-only · **A** = full HELMET, same base model, 5 cross-disciplinary
topics, machine-scored (checkables) + blind cross-model panel (judgment), independently audited (SOUND-WITH-CAVEATS).
- **Scorecard:** A(helmet) 5.0 ≥ B(armor) 4.0–4.5 > C(plain) 3.5–4.0 / 5. **Fabrication/over-commit: plain 1,
  armor 1, helmet 0** — the helmet was the only arm that never over-committed.
- **On 3 of 5 topics all arms were correct** — plain Opus needed no scaffolding. The scaffolding's value
  concentrated in two behaviors: **execution** (T1: A/B exhibited a verified object, plain Opus's was invalid)
  and **κ=0 abstention** (T5: only the helmet withheld a verdict on an open question).
- **The keystone caveat (audit-forced):** the helmet's one win over armor (T5) was a **RULE-COMPLIANCE** result —
  the κ=0 label was *pre-assigned*; the helmet's actual **routing/classification on unlabeled inputs was NEVER
  tested.** And 2 of 5 of my own predictions were wrong (plain Opus is a stronger baseline than expected).
- **Verdict: A>B>C but NARROW, single-topic, NOT a ≥10% promotion. The result confirms "organized, not smarter."**

## 3. The GOVERNING LAW (from the "other helmets" analysis, `HELMET/other_helmets/`)
> **Helmet value ≈ κ-density × economic-work-density × base-model-failure-rate.** Value lives ONLY in the κ=1
> execution slice (forcing the frozen check the model would skip/fake) and the κ=0 abstention slice. Everything
> in between (routing to same-model "specialists," multi-agent deliberation) is **structured theater.**

Cross-domain tiering (DESIGN argument, not benchmarked): **REAL weapon-helmets** = Software engineering (~8.5,
seed = CODEFORGE) + Data/BI (~6). **Mostly-armor** = legal, ops/SRE, clinical, education. **Theater-risk** =
writing, design/UX. **Best untested next helmet = a systematic-review / scientific-literature helmet** (high κ:
DOI/citation/stat-arithmetic all κ=1; adjacent to the research helmet + FACTHARNESS).

## 4. What's MISSING — gaps to fix when improving (ranked; full detail in `validation/GAPS.md`)
**TIER 1 (load-bearing — these decide if the helmet is real):**
1. ✅ **THE KEYSTONE — TESTED 2026-06-21 (gap NARROWED, not fully closed).** Ran a 24-problem unlabeled
   routing-accuracy benchmark (`validation/keystone/`, committed key, cross-model-audited 22/24 defensible/0 wrong),
   at 2 tiers. **Baseline: Sonnet 88% / Haiku 79% routing-verdict accuracy (95% / 86% on the 22 unambiguous
   items).** The load-bearing decisions are robust at both tiers (weapon-vs-abstain, proxy-trap 4/4, anti-theater
   2/2, open-problem rails). The dominant failure was the one the red-team predicted — over-tagging a **factual
   lookup** as κ=1 WEAPON instead of κ=0 GROUND_AND_ANSWER (worst at Haiku). **A principled fix (doctrine:
   "lookup ≠ κ=1"; + route() hardening: proxy_only ⇒ abstain regardless of groundable) lifted Haiku to 100%
   in-sample — AND GENERALIZES: on a FRESH held-out 24-problem set (cross-model-audited) with the FROZEN
   doctrine, BOTH Sonnet and Haiku scored 100% (22/22 unambiguous).** Net: the keystone gap is **substantially
   CLOSED on classification** — routing on unlabeled inputs is accurate and the fix is not overfit. Caveats:
   n=24/author-correlated set; routing accuracy ≠ end-to-end output quality. Full: `validation/keystone/RESULTS.md`.
2. ✅ **End-to-end auto-dispatch — CLOSED (v0, 2026-06-21): `helmet_run.py`.** The pipeline `descriptor →
   provost.route() → AUTO-DISPATCH to the matched weapon's REAL gate → unified delivery` is now wired + selftest-
   green: WEAPON→OPTIMA (ACCEPTs the optimum, REJECTs an infeasible claim), WEAPON→ENCLOSE (certifies a verified
   integral), plus GROUND_AND_ANSWER / ARMOR_ABSTAIN / honest NO_ADAPTER paths. Adapters call the actual gates (no
   re-impl). **Remaining:** wire the rest of the 13 weapons' adapters (3 wired so far: optima, enclose, psymetrix-stub).
3. **Helmet-over-armor advantage is ≤10%, one topic, artifact-contaminated** → no promotion.

**TIER 2 (coverage):** n=5 single-run validation (need N≥20, held-out, ≥3 seeds, topics plain Opus actually
fails); each weapon rests on ~1 demo+audit (in-the-wild robustness uncharacterized); the Dean/CROSS integration
is unexercised end-to-end.

**TIER 3 (known/external):** the capability lever is a confirmed +0pp negative (infra-gated — needs SWE-bench-scale
contamination-free harness); no live cost/registrar accounting (this validation spent ~426k tokens to beat one
Opus call by ≤1.5/5 — the cost/benefit boundary is uncharacterized); toolchain fragility (OPTIMA's CBC was
x86-blocked on this ARM Mac; PROOFSMITH needs Lean); Fable 5 inactive (degrades the un-executable creative slice).

## 5. RESUME PLAN — exact next steps, in priority order
1. ✅ **THE KEYSTONE — DONE + GENERALIZATION-CONFIRMED 2026-06-21** (routing benchmark built + run + fixed +
   held-out-validated; see TIER-1 #1 and `validation/keystone/RESULTS.md`). Baseline Sonnet 88% / Haiku 79% →
   fix → in-sample Haiku 100% → **held-out (fresh 24, frozen doctrine): Sonnet 100% / Haiku 100% (22/22 clean)**.
   The fix generalizes; the gap is substantially closed on classification.
   **(a) ✅ THE END-TO-END A/B — DONE 2026-06-21** (`validation/ab/AB_RESULTS.md`): HELMET (route→execute/abstain)
   vs FLAT (answer directly), same model+tools, 2 arenas × 2 tiers, machine + cross-model-judge scored. **Result:
   CAPABILITY/correctness Δ=0 both tiers** (checkable arena SATURATED — tool-enabled FLAT executed spontaneously,
   10/10; forced-execution redundant for a capable agent). **HONESTY/abstention: HELMET 0/10 over-commit vs FLAT
   2/10 (Haiku) / 3/10 (Sonnet)** — prevents fabricated certainty on 20–30% of unverifiable questions, benefit
   PERSISTS at the strong tier. **Confirms "honesty, not capability" end-to-end; NOT a ≥10% promotion (correctness
   unchanged); ratchet OPEN at v3.** Caveats: n=10/arena (low power); helmet's 0-over-commit partly by-construction;
   over-abstention on *answerable* items untested here.
   **Remaining follow-ups (lower priority):** (b) higher-N/multi-seed A/B to tighten the honesty-delta CI + an
   over-abstention counter-test; (c) a larger FULLY INDEPENDENT / adversarial routing set (n>24, non-author-correlated).
2. **Wire the end-to-end auto-dispatch** (gap #2): a runnable `helmet_run(problem)` that calls `provost.py` →
   dispatches to the matched `<weapon>_router.py` / verifier → delivers. Closes the loop.
3. **Harden the validation:** N≥20 topics (incl. ones plain Opus fails), ≥3 seeds, held-out selection.
4. **Build the SWE helmet** (highest-value next per the law; CODEFORGE is the seed) — and/or the **systematic-review
   helmet** (best untested candidate).
5. **Exercise Dean / CROSS** end-to-end on a real ≥2-weapon problem.
6. **Verify the 2 unconfirmed facts** before designing the clinical/legal helmets (DDI cross-DB κ≈0.01;
   30–88% legal-citation hallucination range).

## 6. FILE MAP (where everything lives)
- **Orchestrator:** `Expanding_Frontiers/HELMET/` (`provost.py`, `registry.json`, `orchestrator.js`, `SPEC.md`, `README.md`, `AUDIT.md`, `tests/`)
- **Validation study:** `Expanding_Frontiers/HELMET/validation/` (`PLAN.md`, `GROUNDING.md`, `RESULTS.md`, `AUDIT.md`, `GAPS.md`, `runs/`)
- **Other-helmets map + the law:** `Expanding_Frontiers/HELMET/other_helmets/OTHER_HELMETS.md`
- **Weapons:** `Expanding_Frontiers/weapons/<name>/` (each self-contained) + `WEAPONS_BACKLOG.md` (status) + `*_WEAPON_KICKOFF.md` (build specs) + `BUILD_REMAINING_DRIVER.md`
- **Frontier engine (12th weapon):** `Expanding_Frontiers/cap_set/`
- **Box version + ladder:** `Next/BOX_V5.md`, `RATCHET.md`; lineage `Legacy/EVOLUTION_LOG.md` C37–C46.

## 7. The honest one-paragraph epitaph (so future-you isn't misled)
The HELMET + 12-weapon arsenal is **real, individually verified, and behaves exactly as specified: it is an
honesty-and-execution machine, not an intelligence amplifier.** Its measured advantage over plain armor is small
and its load-bearing mechanism (routing on raw inputs) is **not yet proven** — that is the #1 thing to fix. This
is a process layer (expansion, not promotion); the capability ratchet stays open at v3 by design. Nothing here is
a loss — it is a clearly-mapped, honestly-bounded foundation, paused at the right place to resume.
