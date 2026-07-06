# SPEC.md — SHOES_ROUTING: the router-time rails (FOOTING + ROUTE-PLANNER)

*Two distinct components co-located at ONE point — the router decision — built together but kept
SEPARATE, each with its own kappa and its own self-tests. Both are EFFICIENCY/ARMOR, not weapons.
KIT-EXPANSION item #7 (SHOES-a + SHOES-c). Written 2026-06-20, box-style.*

## 0. The one-line claim (and its honest ceiling)
ROUTE-PLANNER picks the cheapest ladder rung that clears the bar (execute-for-machine-checkable,
weapon-for-kappa>0, armor-for-kappa=0) and forces a strategy switch when per-track verified-fact-delta
hits zero instead of looping; FOOTING scores a draft's uncertainty from machine signals and routes
up / grounds / abstains before shipping — and **NEITHER ever emits "verified" or "safe"**, both
treating their verdicts as routing judgments (kappa<1) backed by a pre-merge eval gate against silent
quality regression. **They make the box CHEAPER and BETTER-FOOTED, not smarter; they REDUCE cost and
confident-wrongness, they ELIMINATE neither.**

## 1. The two components (separate kappa, separate tests)

### FOOTING (SHOES-a) — the pre-ship footing check ("don't slip")
A cheap (Haiku-tier, ~1/40th of Opus) pre-ship rail that scores a draft's epistemic UNCERTAINTY and,
above threshold, ROUTES UP / triggers a fetch-execute grounding loop / ABSTAINS.

| signal | kappa | how |
|---|---|---|
| unverified-load-bearing-claim **count** | **kappa=1** (EXACT) | count load-bearing claims with no attached check |
| structured-output field **mismatch** | **kappa=1** (EXACT) | required field missing / wrong type vs a schema |
| input character-level **distance** | **kappa=1** (EXACT) | normalized Levenshtein from nearest known-good exemplar |
| cross-paraphrase **disagreement rate** | **kappa<1** (AUDIT FIX) | whether two paraphrased answers AGREE needs a MODEL to judge → the *comparison* is kappa<1, NOT kappa=1 |
| the **"uncertain?"** verdict | **kappa<1** | a judgment that ROUTES; never a certification |

**Action vocabulary (the ONLY verdicts FOOTING may emit):** `SHIP_OK_LOW_UNCERTAINTY`, `ROUTE_UP`,
`GROUND_THEN_RECHECK`, `ABSTAIN`. **Forbidden words (the wording rail):** "verified", "safe", "correct",
"proven", "guaranteed", "certified" — matched at WORD BOUNDARIES so "unverified" (a legitimate uncertainty
word) is allowed but "verified" as a claim is not. A machine scrubber (`_assert_no_forbidden_wording`)
runs on every verdict and FAILS the gate if violated.

### ROUTE-PLANNER (SHOES-c) — the cheapest-rung meta-controller + stuck-detector
A lightweight meta-controller that (a) classifies complexity → ladder tier and (b) classifies
verifiability → weapon (kappa>0) vs armor (kappa=0), picks the cheapest path that clears the bar, and —
EXTENDING the saturation tripwire — forces a STRATEGY SWITCH when per-track verified-fact-delta=0 for N
iterations (anti-loop hard cap).

| signal | kappa | how |
|---|---|---|
| token/complexity **class** → tier | **kappa=1** (EXACT bucket) | machine-checkable→EXECUTE($0) · routine→Haiku · hard-but-executable→solver+EXECUTE · hard-unexecutable→Opus |
| kappa-of-the-task (cheap exact verifier?) → track | **kappa=1** (EXACT bucket) | has_exact_verifier → weapon; interpretation/no-verifier → armor |
| **verified-fact-delta=0** stuck signal | **kappa=1** (EXACT count) | per-track count comparison (see §2) |
| "cheapest-that-clears?" / "is it stuck?" | **kappa<1** | routing judgments, not certifications |

## 2. "verified-fact" DEFINED PER TRACK (audit fix — else the stuck-detector fires vacuously or never)
- **weapon track:** a NEW gate-passed object produced this iteration (`gate_passed_objects` increments).
- **armor track:** a NET increase in grounded (fetched/executed) load-bearing claims (`grounded_claims`).
- **kappa=0 track:** an escalation / decision RECORDED this iteration (`escalations_recorded`).
`verified-fact-delta=0` means NONE of these advanced for N consecutive iterations — only then is the
search "stuck" → STRATEGY_SWITCH_OR_IMPASSE (not an infinite loop). N = `STUCK_AFTER_N = 3`.

## 3. The self-tests (frozen; `selftest_all.py` exits non-zero on any failure)
FOOTING (`footing_check._selftest`):
- **(a)** a draft with HIGH cross-paraphrase disagreement → flagged uncertain → route up / abstain.
- **(b)** a fully-grounded, in-distribution, paraphrase-agreeing draft → NOT flagged.
- **(c)** the wording rail: never emits "verified"/"safe"/"correct" (asserted on every verdict; scrubber
  catches a poisoned note; "unverified" is correctly allowed).
- (+) kappa=1 unit signals (count / schema-mismatch / distance); honest "no oracle → disagreement
  UNCOMPUTABLE" (no fake pass).

ROUTE-PLANNER (`route_planner._selftest`):
- **(d)** machine-checkable → EXECUTE (no model); kappa=0 interpretation → ARMOR; routine → Haiku;
  hard-unexecutable → Opus.
- **(e)** N iterations of zero per-track verified-fact-delta → STRATEGY_SWITCH / impasse (anti-loop cap).
- **(f)** a benign productive search and a too-short single task → NOT falsely halted.
- (+) per-track verified-fact-delta unit checks.

Joint, NON-WAIVABLE:
- **(g) THE PRIMARY-ADVERSARY MISROUTE TEST** (`selftest_all._misroute_end_to_end`): a task KNOWN to
  require Opus is misrouted to Haiku and yields a degraded draft. **ROUTE-PLANNER flags the misroute at
  routing time** (`misrouted_below_required_tier=True`) **AND FOOTING flags the degraded output at ship
  time** (uncertain → ROUTE_UP/GROUND/ABSTAIN, with the tightened-bar backstop engaged). Without this test
  the spec's main threat — silent quality regression — is unguarded at build time.

## 4. FOOTING ↔ TRIAGE single handoff (cross-cutting audit fix)
FOOTING's uncertainty signal and TRIAGE's "overconfidence" row both fire pre-ship and both route to the
panel/abstention — complementary (signal vs named-class), NOT duplicates. **One routing handoff owns the
final escalate/abstain decision** so they cannot double-escalate or mask each other. (In this build the
handoff contract = FOOTING emits {action ∈ ROUTE_UP/GROUND_THEN_RECHECK/ABSTAIN} as the single signal that
the owning escalation router consumes; it does not itself escalate twice. Wiring into the live TRIAGE owner
is a registration-time step, out of scope for this in-folder build.)

## 5. Honesty rails (non-negotiable)
- **FOOTING reduces confident-wrongness, never eliminates it** — an overconfident-but-internally-CONSISTENT
  error still passes (documented honest failure mode; the (g) test guards the *misroute* variant, not the
  consistent-confident-error variant).
- **Silent quality regression is the adversary** — a misroute degrades without alarm; FOOTING + a pre-merge
  eval gate (50–500 cases) are the non-optional backstops, not decoration (grounded, see GROUNDING.md F2).
- **kappa honesty:** signals are machine-computed (kappa=1 inputs); the uncertainty/route verdicts are
  kappa<1 → they ROUTE, they do not certify. No "verified/safe" from FOOTING.
- **Efficiency, not capability** — any quality lift is weak-dominance at best (point-release class); the
  cost win is the real deliverable. **No ratchet movement.**

## 6. Deliverables (this folder)
`footing_check.py` · `route_planner.py` · `selftest_all.py` (the 6 self-tests + the joint (g)) ·
`SPEC.md` · `GROUNDING.md` · `README.md` · `AUDIT.md` (auditor stub) · `demo_ab/` (committed
`PREDICTION.md` → `run_demo.py` → `results.json`). Registration (BOX_V5 / HELMET / EVOLUTION_LOG) is
handled separately and is NOT edited here.
