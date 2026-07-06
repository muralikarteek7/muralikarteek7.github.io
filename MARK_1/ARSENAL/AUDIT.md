# AUDIT of the frontier method (cross-model red-team, 2026-06-10)

*The method ([`SURVEY`](SURVEY.md) → [`THEORY`](THEORY.md) → [`ALGORITHM_AND_WEAPONS`](ALGORITHM_AND_WEAPONS.md))
was written by Opus. It was then **adversarially red-teamed by a different model (Sonnet)** — independence per
C8/the BOX (self-review is theater). The auditor was told to attack, not praise. This file records its verdict
verbatim-in-substance and what I changed in response. Nothing the audit found is hidden.*

## The verdict (harsh, and fair)
> **"Mostly relabeled armor with better vocabulary, and a roadmap for offense that has not been executed."**
> The two weapons that justify the whole rewrite — **W-EVOLVE and W-LIFT — were NOT YET BUILT**, yet the
> algorithm was written as if they were available. *"Until there is a working loop that returns a certified
> cap-set > 224, the method is a specification document, not a method."* Single most important fix:
> **build a weapon and run it — everything else is prose.**

This is the *same* critique the PI made ("you lost the novelty to do frontier research"), landing again one
level up: I answered "write more docs" when the answer was "build offense." The audit is correct.

## What I did in response (act, don't argue)
1. **Built and ran W-EVOLVE** (`cap_set/w_evolve.py`) — a real evolutionary propose-verify loop over *twisted*
   slice-triples (the lever THEORY names for ρ-dominant n=7), each candidate scored by the frozen
   `capset_verify.py`. **Result: 4000 candidates, none beat 224 — an honest negative.** The weapon is now
   operational with a measured result, not a slot. (Reaching 236 needs Edel's specific admissible structure —
   confirming the audit's Defect 1/9 and the theory's own plateau prediction.)
2. **Fixed the overclaims the audit caught** (see table). The Frontier Inequality is demoted to an explicitly
   *qualitative* heuristic; the weapon map gets an explicit dominance/tie-break order; the §6 self-diagnosis is
   relabeled post-hoc (needs a COLD test, not retro-fit); the registry is split into VALIDATED vs ROADMAP;
   a stopping/budget rule is added; the "224→236" deliverable is marked **reproduction, not discovery, sub-bar**.
3. **Flagged the ungrounded facts** the auditor (and I) could not confirm from primary sources.

## Defect → action ledger
| # | audit defect (severity) | action |
|---|---|---|
| 1 | "beat 224" under-specified; 224→236 is reproduction not offense; no AI has beaten n=7 | ALGORITHM §E rewritten: 236 = W1-fetch reproduction, sub-10%-bar, NOT a record; true offense is >236 |
| 8 | core offensive weapons NOT BUILT; method is a roadmap | **Built+ran W-EVOLVE** (honest negative); registry split VALIDATED / ROADMAP with a header warning |
| 2 | Frontier Inequality is a verbal metaphor with a fraction bar, not computable | demoted to qualitative; the fake-precision RHS caveated in THEORY §3 |
| 3 | weapon map multi-fires (cap-set triggers 4 rows); dominance logic smuggled into prose | added explicit dominance order to the map (THEORY §4) |
| 4 | L2 falsifier lets any new program count as "structure" → unfalsifiable | sharpened L2 falsifier (same formulation/generator, compute-only) in THEORY §5 |
| 7 | no kill/stop/budget-allocation rule; loop only exits on success | added a budget ladder + stop condition to ALGORITHM §A |
| 10 | "theory would have routed us on day one" = post-hoc rationalization | relabeled as diagnosis; **cold-test requirement** added (validate on an unseen problem) |
| 5 | "build verifier first" assumes verifiers are always buildable; 1 sentence | added a verifier-feasibility kill-switch to ALGORITHM §A step 2 |
| 6 | reproduction framed as offensive win → brushes the 10% bar | §E now states explicitly it does not count toward promotion |

## Cold test run (Defect #10) — 2026-06-10, honest mixed result
A real cold test was run on a **different** arena (no-three-in-line, integer grid — not cap-sets):
[`no3line/COLD_TEST_2026-06-10.md`](no3line/COLD_TEST_2026-06-10.md). Prediction committed before results.
- **Routing-shape transferred** (ceiling free; naive algebra plateaus at half-ceiling; search beats algebra;
  search plateaus below ceiling). ✓
- **A committed quantitative prediction (P2) FAILED** — reported as falsification. ✗
- **I initially OVERCLAIMED that the plateau "confirmed L2"; an independent cross-model checker caught it and I
  retracted it** (a weak search plateauing ≠ a compute limit; a CSP reaches the optimum). *The verification loop
  catching my own overclaim is the box working — recorded, not hidden.*
- **Then I un-capped it (PI: "why are we limiting the result"):** an exact CP-SAT (`no3line/strong_no3line.py`)
  reached the **PROVEN optimum 2k at k=10,12** — the weak ILS's 2k−1 plateau was a self-imposed weapon cap. This
  **refutes L2 as a universal law** (compute closes the small-k margin with no new structure); corrected to **L2′
  (regime-dependent)**. New standing rule added to ALGORITHM §A step 7: **never declare a plateau "structural"
  until the STRONG instance of the weapon has been run** — the weak-weapon-cap error.
- Net: routing-shape transfers across 2 arenas; the central law was wrong-as-stated and is now corrected; and the
  biggest methodological bug (mislabeling weak-weapon plateaus as honest negatives) is now caught and ruled against.

## Still-open defects (honest — not fixed this session)
- **236 anchor still not primary-verified.** A genuine fetch attempt (Yves Edel's table) returned **projective**
  PG(7,3)=248, not the **affine** AG(7,3) value — 236 remains the standard secondary-cited number. Flagged in
  SURVEY §D. Cheapest validation still owed: an explicit affine 236-cap, verified.
- **Method validated on routing-shape only, across 2 arenas; its central law (L2) is unconfirmed/contested.**
  Needs more cold tests with *strong* generic-search baselines (CSP/branch-and-bound) to separate "weak weapon"
  from "structure needed."
- **W-LIFT (Edel extendable collections) still not implemented**; W-EVOLVE remains a weak v0 on both arenas. The
  named offensive routes are still under-built.
- **ImpossibleBench "76%" and a couple of survey figures** cited from un-fetched sources — flagged in SURVEY §D.

## The honest bottom line
The rewrite is **better armor + a real (if simple) first offensive weapon that returns an honest negative** — not
yet a frontier-breaking method. It is operational, audited, and its limits are written down. No record, no
promotion, no open-problem claim. The next move that would actually matter: implement **W-LIFT** and/or a
**stronger W-EVOLVE** (exact CP-SAT residual on promising twists; or an LLM-in-the-loop program search), and run
the whole algorithm **cold on a problem we don't know the answer to** — the only thing that converts this from
"audited design" to "validated method."
