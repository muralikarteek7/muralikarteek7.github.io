# KICKOFF — build the KIT pieces: SHOES-a (FOOTING) + SHOES-c (ROUTE-PLANNER) — the router-time rails
*Paste into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written 2026-06-20. These are
items **#7 (SHOES sub-components a + c)** of the KIT-EXPANSION plan (`Next/KIT_EXPANSION_PROPOSAL.md`, §4). Two
distinct components co-located at ONE point — the router decision — so built together, but kept SEPARATE with their
own κ and own tests (NOT re-bundling the dissolved "SHOES" metaphor). Both are EFFICIENCY/ARMOR, not weapons.*

*Hardened 2026-06-20 after an independent Sonnet audit (verdict NEEDS-REWORK → fixed): cross-paraphrase
disagreement is **κ<1, not κ=1** (the comparison needs a model — the honesty fix); "verified-fact" is now DEFINED
per track for the stuck-detector; a non-waivable **misroute self-test (g)** now guards the silent-quality-regression
adversary; and FOOTING↔TRIAGE share ONE escalation handoff. If building FOOTING and ROUTE-PLANNER separately is
cleaner, split this into two kickoffs — they are two components, deliberately co-located.*

---

You are building the box's **router-time rails**: **FOOTING** (don't slip — a calibration/uncertainty check before
shipping) and **ROUTE-PLANNER** (pick the cheapest ladder rung that clears the bar + detect when a search is
stuck). Work BOX-style: plan → produce → **verify INDEPENDENTLY** → ground → be honest; **these REDUCE confident-
wrongness and cost; they do NOT eliminate either — claim no win, only a cheaper, better-footed router.**

## 0. ORIENT
`CLAUDE.md`, `RESUME.md`, **`Next/KIT_EXPANSION_PROPOSAL.md`** (§4 SHOES-a + SHOES-c), **`Next/BOX_V4.md`** (the
MODEL LADDER these extend: machine-checkable→execute · routine→Haiku · hard→Opus · escalate→Fable), the existing
**saturation tripwire** (the STRUCTURAL_GAP detector — ROUTE-PLANNER extends it), and `Next/BOX_V5.md` v5.1
(selective-context decomposition — a sibling efficiency option). Both rails are κ<1 (judgment-reducing), with small
κ=1 sub-signals.

## 1. THE HONEST FRAMING — what these ARE and ARE NOT
**FOOTING (SHOES-a) IS:** a cheap pre-ship check (Haiku-tier, ~1/40th of Opus) that scores a draft's epistemic
uncertainty from **machine-checkable signals** — cross-paraphrase disagreement rate, count of unverified
load-bearing claims, distance-from-known-good-input — and, if uncertainty > τ, routes UP the ladder, triggers a
fetch/execute grounding loop, or ABSTAINS.
**ROUTE-PLANNER (SHOES-c) IS:** a lightweight meta-controller that classifies each task by (a) complexity → ladder
tier and (b) verifiability → κ>0 weapon vs κ=0 armor, picks the cheapest path that meets the bar, and — extending
the saturation tripwire — forces a **strategy switch when verified-fact-delta = 0** for N iterations (anti-loop
hard cap).
**They ARE NOT:** ❌ weapons (no exact verifier of "is this well-calibrated?" — calibration needs held-out ground
truth you don't have at inference; κ=0). ❌ a cure for confident-wrongness — FOOTING *reduces* it; an
overconfident-but-internally-consistent error still passes (honest failure mode). ❌ free of the routing hazard —
**silent quality regression** on a misroute (a task sent to Haiku that needed Opus, degraded but un-alarmed) is the
documented adversary; FOOTING is the backstop, plus a pre-merge eval gate over 50–500 cases. ❌ a capability — they
make the box cheaper and better-footed, not smarter.

## 2. THE TWO RAILS (separate κ, separate tests)
| rail | the κ=1 sub-signals (machine, EXACT) | the κ<1 signals/verdict (judgment) | action |
|---|---|---|---|
| **FOOTING** | unverified-load-bearing-claim **count**; structured-output field-**mismatch**; input character-level distance | **cross-paraphrase "disagreement"** (the *comparison* needs a model → κ<1, NOT κ=1 — audit fix); "is this output uncertain?" | route up / ground / abstain |
| **ROUTE-PLANNER** | token/complexity class; κ of the task (does a verifier exist?); **verified-fact-delta=0** (per the per-track definition below) | "which path is cheapest-that-clears-the-bar?"; "is this stuck?" | pick rung; weapon-vs-armor; force strategy switch / honest impasse |

**"verified-fact" is defined PER TRACK (audit fix — else the stuck-detector fires vacuously or never):** weapon
track = a NEW gate-passed object this iteration; armor track = a NET increase in grounded (fetched/executed)
load-bearing claims; κ=0 track = an escalation/decision recorded. `verified-fact-delta=0` means none of these
advanced — only then is the search "stuck."

## 3. THE KEY ENGINEERING PROBLEM — cheap, and itself honest about its limits
- `footing_check.*`: emit `{disagreement_rate, unverified_claims, distance, uncertain?, action}`. The numbers are
  machine-computed; the `uncertain?` verdict is a judgment-that-routes (never a certification). **Self-tests:**
  (a) a draft with HIGH cross-paraphrase disagreement → flagged uncertain → routed up/abstain; (b) a fully-grounded
  draft (every load-bearing claim has a check) → NOT flagged; (c) the report NEVER says "verified correct" — only
  "low/high uncertainty signals" (assert the wording).
- `route_planner.*`: emit `{tier, track (weapon|armor), cheapest_path, stuck?}`. **Self-tests:** (d) a
  machine-checkable task routes to execute (no model); a κ=0 judgment routes to armor; (e) a search with N
  iterations of zero verified-fact-delta (per the per-track definition) triggers a STRATEGY SWITCH / impasse report
  (not an infinite loop); (f) a benign single task is NOT falsely halted;
  **(g) THE PRIMARY-ADVERSARY TEST (audit fix — non-waivable): a task KNOWN to require Opus is misrouted to Haiku;
  FOOTING must FLAG the degraded output before it ships** (this is the silent-quality-regression backstop — without
  this test the spec's main threat is unguarded at build time). Plus the deployment-time pre-merge eval gate (50–500
  cases) remains mandatory.

**FOOTING ↔ TRIAGE single handoff (cross-cutting audit fix):** FOOTING's uncertainty signal and TRIAGE's
"overconfidence" row both fire pre-ship and both route to the panel/abstention — they are complementary (signal vs
named-class), NOT duplicates, but **one routing handoff owns the final escalate/abstain decision** so they cannot
double-escalate or mask each other. Wire both into that single owner.

## 4. INFRA + GROUND-BY-FETCH
- **Confirm:** the ladder + tripwire exist to extend; a cheap tier (Haiku) for FOOTING. State what's present.
- **FETCH-confirm (cite `GROUNDING.md`):** LLM model-routing cost/quality evidence (e.g. ~67% cost cut routing
  ~14% to frontier at no quality loss) AND the **silent-quality-regression** hazard + the pre-merge eval-gate
  mitigation; uncertainty-estimation-for-routing methods. Don't assert from memory.

## 5. TO-DOs (box order)
1. **PLAN** `armor/shoes_routing/SPEC.md` — FOOTING and ROUTE-PLANNER as TWO components, each with its κ=1 signals
   vs κ<1 verdict, the silent-regression backstop (FOOTING + an eval gate), the stuck-detector extending the
   tripwire. **GROUND** routing evidence + the regression hazard in `GROUNDING.md`.
2. **BUILD** `footing_check.*` + `route_planner.*` + `selftest_all.py` (the 6 self-tests). Green first.
3. **A/B-LITE, committed predictions** (`PREDICTION.md` first): on a small task set, show ROUTE-PLANNER cuts cost
   vs always-Opus at no quality regression on the κ>0 (machine-checkable) subset, and FOOTING flags the injected
   under-grounded drafts. **Honest:** quality is judged by machine checks where they exist; where they don't, report
   the limit (no κ=0 quality claim).
4. **VERIFY INDEPENDENTLY:** cross-model audit (Sonnet/Haiku ≠ Opus generator) — finds a misroute FOOTING misses
   (an overconfident-consistent error), checks ROUTE-PLANNER doesn't starve a hard task to a cheap tier, checks no
   "verified/safe" wording leaks from FOOTING. Fix what's caught.
5. **REGISTER:** `Next/BOX_V5.md` (ARMOR/efficiency: the router-time rails; sibling to v5.1 decomposition),
   `HELMET/registry.json` (Registrar's routing logic), honest `EVOLUTION_LOG` (**efficiency/armor; weak-dominance
   at best → point-release class, NOT a ≥10% promotion**). Update plan §7 + backlog.

## 6. HONESTY RAILS
- **FOOTING reduces confident-wrongness, never eliminates it** — an overconfident-consistent error passes; say so.
- **Silent quality regression is the adversary** — a misroute degrades without alarm; FOOTING + a pre-merge eval
  gate (50–500 cases) are the non-optional backstops, not decoration.
- **κ honesty:** the signals are machine-computed (κ=1 inputs); the uncertainty/route verdicts are κ<1 → they ROUTE,
  they do not certify. No "verified/safe" wording from FOOTING.
- **Efficiency, not capability** — any quality lift is weak-dominance at best (point-release class); the cost win is
  the real deliverable. No ratchet movement.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/shoes_routing/` (or `armor/shoes_routing/`) — `SPEC.md`, `GROUNDING.md`,
`footing_check.*` + `route_planner.*` + `selftest_all.py`, `demo_ab/` (committed predictions + the cost/flag
results), `AUDIT.md`, `README.md` (honest ceiling: reduces cost + confident-wrongness; eliminates neither).
Registration in `Next/BOX_V5.md` (ARMOR) + `HELMET/registry.json` + honest `EVOLUTION_LOG`; plan §7 + backlog.

## 8. STAFF (v4 ladder; Fable INACTIVE → Opus, flag low confidence)
- **Signals + planner** = code tier (paraphrase-disagreement, claim-count, fact-delta — machine-computed).
- **FOOTING verdict** = a CHEAP tier (Haiku) scores uncertainty — cross-instance, ≠ the generator where possible.
- **Library** = cheap model: fetch routing cost/quality + the silent-regression hazard.
- **Auditor** = a model ≠ generator (Sonnet/Haiku) — misroute-FOOTING-misses + starved-hard-task + wording attacks.

## 9. THE ONE-LINE TEST OF SUCCESS
**"ROUTE-PLANNER picks the cheapest ladder rung that clears the bar (execute-for-machine-checkable, weapon-for-κ>0,
armor-for-κ=0) and forces a strategy switch when verified-fact-delta hits zero instead of looping; FOOTING scores a
draft's uncertainty from machine signals and routes up / grounds / abstains before shipping — and NEITHER ever
emits 'verified' or 'safe', both treating their verdicts as routing judgments (κ<1) backed by a pre-merge eval gate
against silent quality regression."** Cheaper and better-footed; honest that it reduces, not removes, cost and
confident-wrongness.
