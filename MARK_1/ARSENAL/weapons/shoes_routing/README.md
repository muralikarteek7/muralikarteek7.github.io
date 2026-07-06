# SHOES_ROUTING — the box's router-time rails (FOOTING + ROUTE-PLANNER)

Two EFFICIENCY/ARMOR components co-located at the router decision, kept separate with their own kappa
and their own tests. **Not weapons.** They make the box cheaper and better-footed; they do **not** make
it smarter.

## What's here
- `footing_check.py` — **FOOTING (SHOES-a)**: a cheap pre-ship uncertainty rail. Scores a draft from
  machine signals (unverified-claim count, schema mismatch, input distance — all kappa=1) plus a
  cross-paraphrase disagreement signal (kappa<1, needs a model to compare) and ROUTES UP / GROUNDS /
  ABSTAINS. Never certifies. Never emits "verified"/"safe".
- `route_planner.py` — **ROUTE-PLANNER (SHOES-c)**: picks the cheapest ladder rung that clears the bar,
  classifies weapon (kappa>0) vs armor (kappa=0), flags a misroute below the required tier, and — extending
  the saturation tripwire — fires a STRATEGY-SWITCH when per-track verified-fact-delta=0 for N iterations.
- `selftest_all.py` — runs every adversarial self-test for both; **exits non-zero on any failure.**
- `SPEC.md` · `GROUNDING.md` (fetched facts) · `AUDIT.md` (cross-model auditor's findings) · `demo_ab/`.

## Run the gate (do this first; nothing else counts until it's green)
```
cd MARK_1/ARSENAL/weapons/shoes_routing && python3 selftest_all.py   # must exit 0
```
Then the A/B-lite demo:
```
cd MARK_1/ARSENAL/weapons/shoes_routing/demo_ab && python3 run_demo.py
```

## THE HONEST CEILING (read this)
- **FOOTING REDUCES confident-wrongness; it does NOT eliminate it.** An overconfident-but-internally-
  CONSISTENT error passes FOOTING undetected — that is the documented honest failure mode. FOOTING catches
  *under-grounding, instability, OOD inputs, and misroutes*, not a fluent wrong answer that agrees with
  itself.
- **The verdicts are kappa<1 routing judgments, NOT certifications.** The machine numbers feeding them are
  kappa=1; the "uncertain?" / "cheapest-path" / "stuck?" calls are judgments. No "verified"/"safe" wording
  is ever emitted (enforced by a machine scrubber that fails the gate on violation).
- **Silent quality regression is the adversary.** A misroute (a task that needed Opus sent to Haiku) can
  degrade silently. The backstops are FOOTING at ship time + ROUTE-PLANNER's misroute flag at routing time
  + a **pre-merge eval gate (50–500 cases)** at deploy time. The eval gate is **non-optional and is a
  DEPLOYMENT-time responsibility, not implemented in this folder** — this folder ships the rails and the
  executable (g) backstop test, not the 50–500-case corpus.
- **Efficiency, not capability.** Any quality lift is weak-dominance at best (point-release class). The
  real deliverable is the COST win. **No ratchet movement.** The cost figures in the demo are on a tiny
  synthetic task set — a measured *illustration*, not a benchmark claim.
- **kappa<1 means a MODEL is in the loop for the paraphrase signal.** In tests the comparison oracle is a
  deterministic string-equality stub (so the gate itself stays deterministic); in production it is a cheap
  cross-instance model call (Haiku, != the generator where possible). Cross-paraphrase disagreement being
  kappa<1 is the audit fix — do not relabel it kappa=1.

## Grounding
Routing cost/quality (RouteLLM: ~14% to frontier, ~95% quality, large cost cut), the silent-quality-
regression hazard + the pre-merge eval-gate mitigation, and uncertainty-for-routing methods are FETCHED in
`GROUNDING.md` (with an honest flag that the kickoff's exact "~67%" number is not reproduced by the primary
source — direction grounded, that specific figure not).
