# CRUCIBLE — AUDIT (cross-model red-team) — STUB, auditor to fill

*This is a STUB created by the BUILD engineer (Opus 4.8). The independent audit must be done
by a model ≠ the generator (Sonnet or Haiku; **never Opus-audits-Opus**; Fable 5 inactive).
Self-review is theater — do not let the builder fill this in.*

## Audit charge (kickoff §5 / §8)
The auditor must, with its OWN code (not by trusting this report):

1. **Re-check each shipped KILL exhibit independently.** Does the gate-under-test REALLY accept
   the wrong object?
   - [ ] (i) Re-run `demo_planted_bugs/planted_sortnet_gate.verify_sorting_network_PLANTED` on the
         exhibited network `[(0,3),(2,3),(1,3),(1,2),(1,3),(1,2)]`, n=4 → confirm it returns
         `valid=True`. Then, with a from-scratch (auditor-authored) 0/1 enumerator, confirm the
         network does NOT sort all inputs (e.g. fails on `[1,0,0,1]`). The KILL is real iff both hold.
   - [ ] (ii) Re-run `crucible_harness._grim_gate_METAMORPHIC_BUG` on `0.10`@n10@items1 and
         `0.10`@n5@items2 → confirm the verdict FLIPS (ACCEPT vs REJECT) under a Neff-invariant split.

2. **Attack CRUCIBLE itself.**
   - [ ] **Make it MISS a planted bug.** Plant a NEW subtle hole (a different class — e.g. a precision
         threshold one digit too loose, a dict-key ordering dependency) in a copy of a real gate WITHOUT
         telling the builder where, and check whether `false_accept_hunt`/`metamorphic_hunt`/
         `abstain_crash_hunt` exhibit it within budget. Report any miss (a class CRUCIBLE's search does
         not cover) as a residual-risk finding.
   - [ ] **Make it CRY WOLF.** Feed a genuinely-good gate (the auditor's own correct re-impl) and check
         no KILL is produced. Also try to trick the spurious-kill rail: register a subtly-WRONG oracle
         that still passes its controls — does CRUCIBLE ship a spurious KILL? (The control set may be
         too small; report if so.)

3. **Police the labels.**
   - [ ] Confirm no `SURVIVED` report anywhere (RESULTS.md, results.json, registry text) contains
         "sound"/"proven"/"bug-free". (`Survived.to_dict()` raises on these, but check the prose too.)
   - [ ] Confirm the router's coverage summary names buckets (6 full / 5 partial / 1 declined) and never
         claims a blanket "all 12 survived".
   - [ ] Confirm guarded-κ (econometrix) is DECLINED, not silently swept.

## Known limitations the builder flags for the auditor to pressure-test
- **The BLIND plant in `selftest_all.py` is builder-authored** (a hermetic GRIM fixture). The DEMO
  uses a separately-authored copy of a REAL gate (sortnet), which is closer to a true blind plant, but
  the strongest test is a third-party plant the builder never saw. The auditor should supply one.
- **The search is a deterministic LCG mutator**, not property-based (`hypothesis` absent). It may miss
  bug classes a smarter generator would find. Residual risk: a bug reachable only by inputs the LCG
  stream + structured-mutation does not generate.
- **Oracle sanity controls are 2 points each** (one good, one bad). A subtly-wrong oracle that agrees
  on those 2 points but is wrong elsewhere could still ship a spurious KILL. The auditor should test a
  larger control set.
- **Demo full-differential coverage is 2 of 6** (codeforge sortnet, psymetrix GRIM). The other four
  full-differential targets are scoped but not run in the hermetic demo (need fetch / fixture / module).

## Auditor verdict
- Model used: ____________  (must be ≠ Opus 4.8)
- KILL (i) independently reproduced: ____
- KILL (ii) independently reproduced: ____
- Could CRUCIBLE be made to MISS a planted bug? ____  (detail: __________)
- Could CRUCIBLE be made to CRY WOLF? ____  (detail: __________)
- Any SURVIVED secretly worded as "sound/proven"? ____
- Overall: [ ] READY  [ ] READY-WITH-FIXES (list)  [ ] NOT-READY
- Notes:

---

## RESOLUTION of the 2026-06-20 cross-model audit (defects fixed in code)

A cross-model (Sonnet) audit confirmed real defects (including false-accept/spurious-kill
bypasses). All are now addressed in the frozen harness with permanent regressions in
`crucible_harness._selftest_audit_regressions` (run by `selftest_all.py`):

- **A2 — cry-wolf / SPURIOUS KILL via subtly-wrong oracle (false-accept) → FIXED.** `Oracle` now
  requires a CONTROL GRID (≥3 known-good AND ≥3 known-bad controls spanning the probed regime —
  GRIM: decimal precision {0,1,2,3} × items {1,2}). `is_sane()` REFUSES (not free-passes) when too
  few controls are registered. The auditor's "lies on all 3dp means" oracle now fails a 3dp good
  control and is refused; the old 2-point form is refused for too-few controls. Regression: `(A2)`.
- **A11 — SPURIOUS METAMORPHIC KILL via fake (non-meaning-preserving) transform → FIXED.**
  `metamorphic_hunt` now takes an `oracle=` and, before shipping a flip, confirms the transform
  preserved the object's ground-truth (`oracle.truth(obj)==oracle.truth(T(obj))`). The auditor's
  "add 1/n to the mean" transform now has its flip suppressed. Regression: `(A11)`.
- **A3 / A9 — candidate-stream blindspot (1dp-only / items≥2-only bugs survived) → FIXED.** The
  candidate stream now spans decimal precision {0,1,2,3} × items {1,2,3}; both planted bugs are now
  CAUGHT. SURVIVED reports carry `_grim_candidate_coverage()` so the probed regime is named.
  Regression: `(A3/A9)`.
- **A1 — circularity undetectable → FIXED (tripwire) + RELABELED HONESTLY.** A literal same-callable
  oracle is now refused (`_refuse_trivially_circular`); deeper methodological independence is
  documented as an OPERATOR INVARIANT the harness cannot enforce (SPEC §3, README). Regression: `(A1)`.
- **A10 — metamorphic DEFINITE→ABSTAIN coverage gap → FIXED (optional) + DOCUMENTED.** Suppressed by
  default (no false alarm) but CATCHABLE via `flag_definite_to_abstain=True`, still gated by the A11
  meaning-preservation check. Regression: `(A10)`.
- **A8 — BLIND-plant authorship honesty gap → RELABELED HONESTLY.** All in-repo plants are
  builder-authored; the selftest, SPEC §6, and README now say "LOCATION-blind, NOT author-blind",
  and explicitly state the stronger different-agent plant is the cross-model auditor's job. No
  "BLIND-equivalent" over-claim remains.
