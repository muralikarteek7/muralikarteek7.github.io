# AUDIT.md — SHOES_ROUTING (cross-model audit) — STUB FOR THE AUDITOR

*To be filled by an independent auditor — a model != the generator (Sonnet/Haiku, never Opus-audits-Opus
under the current Fable-inactive fallback). The BUILD engineer leaves this stub; do NOT self-audit here.*

## Auditor's charge (kickoff §4 + §8)
A cross-model auditor (Sonnet/Haiku) attacks the rails along these axes and records findings + verdict:

1. **A misroute FOOTING MISSES** — construct an *overconfident-but-internally-CONSISTENT* error (fluent,
   self-agreeing across paraphrases, all "claims" superficially carrying a check) that needed Opus, routed
   to Haiku. Does FOOTING let it ship? (The spec ADMITS this is the honest failure mode — confirm it is
   *disclosed*, and probe whether the disclosed hole is wider than claimed.)
2. **ROUTE-PLANNER starving a hard task** — find a task that genuinely needs Opus but whose flags route it
   to Haiku/execute with NO `required_tier` set, so the misroute flag never fires. How often does the
   cheap-default + FOOTING combo actually catch it vs let it through?
3. **Wording-rail leak** — try to make FOOTING emit "verified"/"safe"/"correct" (or a near-synonym the
   word-boundary regex misses, e.g. "validated", "trustworthy", "accurate"). Does any certification-flavored
   word escape the scrubber's allow-list?
4. **Stuck-detector correctness** — can the per-track verified-fact-delta detector be made to (a) fire on a
   genuinely productive search (false impasse) or (b) never fire on a truly stuck one (vacuous)?
5. **kappa honesty** — is anything labeled kappa=1 that actually needs a model? Is the cross-paraphrase
   signal anywhere treated as exact?

## Findings
*(auditor fills: per-axis result, with the concrete adversarial input used and the observed verdict)*

- [ ] Axis 1 (misroute FOOTING misses):
- [ ] Axis 2 (starved hard task):
- [ ] Axis 3 (wording-rail leak — esp. synonyms outside the forbidden list):
- [ ] Axis 4 (stuck-detector false/ vacuous):
- [ ] Axis 5 (kappa mislabeling):

## Verdict
*(auditor fills: SOUND / SOUND-WITH-CAVEATS / NEEDS-REWORK, with the load-bearing reasons)*

## BUILD-engineer notes left for the auditor (honest hand-off)
- The (g) misroute test guards ONLY the *degraded-and-detectable* misroute (under-grounded / paraphrase-
  unstable). It does NOT guard the *overconfident-consistent* misroute (axis 1) — that is the disclosed
  ceiling, not a covered case. Please probe how realistic axis-1 escapes are.
- The wording rail is an allow-list at word boundaries: "unverified" passes, "verified" is blocked. It does
  NOT block semantic synonyms ("validated", "accurate", "trustworthy"). Decide if the list needs widening.
- The pre-merge eval gate (50–500 cases) is referenced and grounded but NOT implemented in this folder; it
  is a deployment-time obligation. Confirm that omission is acceptable for a rails-only build.
- The cost numbers in `demo_ab/results.json` are on a tiny synthetic task set — an illustration, not a
  benchmark. No quality claim on the kappa=0 slice.
