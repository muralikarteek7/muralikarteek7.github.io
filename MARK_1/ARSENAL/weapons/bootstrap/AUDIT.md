# AUDIT — BOOTSTRAP (stub for the cross-model auditor)

*Independent audit per the BOX: the thing that checks the work must DIFFER from the thing that made
it. Generator = Opus 4.8 (Fable INACTIVE → Opus fallback). Auditor MUST be a different model
(Sonnet/Haiku), never Opus-audits-Opus.*

## How to run the audit
```
cd /Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/weapons/bootstrap
python3 selftest_all.py                       # must exit 0
python3 demo_sudoku_vs_essay/run_demo.py      # must exit 0, all predictions held
```

## Attacks the auditor MUST attempt (kickoff §4)
1. **Plausible-but-fake verifier** — feed BOOTSTRAP a candidate that *claims* to verify a real
   domain but does not import/run (a hallucinated tool). EXPECT: REJECTED at the run step
   (`HALLUCINATED_NONRUNNING`), never registered. [self-test (c) + demo Domain A cand 1 cover this;
   auditor should try a fresh variant.]
2. **κ=0 domain dressed as κ>0** — feed a judgment domain (e.g. "rate this essay") with
   `has_exact_decidable_property: True` set optimistically. EXPECT: ARMOR-ONLY (κ=0); the
   `is_judgment_only` flag must dominate. [router self-test `dressed` + demo Domain B cover this.]
3. **Over-sell check** — confirm no toy-passing verifier is reported as frontier-correct (the FOUND
   outcome must carry the "toy-passing != frontier-correct" ceiling string).
4. **Soundness-incompleteness** — feed a verifier that passes good + some broken but MISSES a
   declared violation type (the no-boxes sudoku checker). EXPECT: REJECTED
   (`SOUNDNESS_INCOMPLETE_MISSED_VIOLATION_TYPE`). [self-test (d) + demo Domain A cand 2.]
5. **Can't-fail** — feed an accept-everything verifier with only GOOD cases. EXPECT: REJECTED
   (`ACCEPTS_KNOWN_BROKEN_OR_NO_BROKEN_TESTED`).
6. **Reproducibility** — run the demo twice; confirm the κ=0 ARMOR-ONLY verdict is identical (the
   committed candidate-source list + N-attempts bound in SPEC.md make it deterministic).

## Findings (cross-model auditor = Sonnet ≠ Opus generator)
- [x] selftest_all.py exits 0: yes
- [x] demo predictions all held: yes (A=κ>0 after 2 rejections, B=ARMOR-ONLY κ=0, C=ABSTAIN)
- [x] attack 1 (fake verifier rejected): HOLDS — HALLUCINATED_NONRUNNING
- [x] attack 2 (κ=0 dressed → ARMOR-ONLY): HOLDS — is_judgment_only dominates
- [x] attack 3 (no over-sell / ceiling carried): HOLDS — no over-claims found in output layer
- [x] attack 4 (soundness-incomplete rejected): HOLDS — SOUNDNESS_INCOMPLETE_MISSED_VIOLATION_TYPE
- [x] attack 5 (can't-fail rejected): HOLDS
- [x] attack 6 (reproducible): HOLDS — two runs identical
- Verdict: SOUND-WITH-CAVEATS → two REAL false-accepts found (below), now FIXED.

## Defects found by the independent audit, and their resolution (FIXED 2026-06-20)
- **Defect A — malformed-case bypass (FALSE-ACCEPT, FIXED).** SPEC contracted "≥1 malformed" but
  the code's `for c in malformed:` loop silently no-op'd on an empty list, so the abstain bar was
  OPTIONAL. Exploit: a verifier that RAISES on garbage (production-real) + a harness with no
  malformed case → CAND_VALIDATED κ=1, despite crashing in production.
  **Fix:** `validate_candidate` now REJECTS `NO_MALFORMED_CASE_SUPPLIED` when no malformed case is
  supplied (`bootstrap_gate.py`). Regression test added to `_selftest()` (the crash-on-garbage
  verifier with no malformed case → asserted REJECTED, and the verifier is shown to really raise).
- **Defect B — empty-declared-types bypass (FALSE-ACCEPT, FIXED).** The coverage check
  `missing = [vt for vt in declared if vt not in exercised]` is vacuously empty when
  `declared_violation_types=[]`, so a verifier that merely MEMORIZES the test cases passed with κ=1.
  **Fix:** `validate_candidate` now REJECTS `NO_DECLARED_VIOLATION_TYPES` on an empty declared list,
  and `BROKEN_CASE_MISSING_VIOLATION_TYPE` if any broken case is untyped (the second leak path).
  Regression tests added to `_selftest()` for both (memorizer with empty declared → REJECTED;
  declared-but-untyped-broken → REJECTED).
- Note on the auditor's attack #3 (judgment-dressed-as-exact with a fake proxy verifier): the
  auditor classed this as PARTLY architectural — the gate checks harness *consistency*, not the
  ground-truth *correctness of the labels*. This is the existing, disclosed "toy-passing !=
  frontier-correct" ceiling (a malicious/careless harness-author with wrong labels undermines the
  κ claim at its root). It is NOT a code-fixable false-accept at this layer; it remains an honest
  ceiling (see README + SPEC) — the downstream full-box build is the mitigation.

## Known honest caveats the generator declares up front (do not re-discover as "defects")
- The cheap tier of independence here is **cross-INSTANCE / machine**, not cross-MODEL, *inside* the
  validation RUN — the RUN is a deterministic machine check, which is the point (it is κ=1).
- The "≥1 broken per declared violation type" coverage cannot catch an **undeclared** violation
  class — honest ceiling, mitigated only by the downstream full-box build.
- Graph-coloring was fetched/grounded (`GROUNDING.md` G3) as the kickoff's alternative κ>0 domain
  but the demo used Sudoku as the primary; they are interchangeable.
