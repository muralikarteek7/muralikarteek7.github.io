# PREDICTION — demo_sudoku_vs_essay (COMMITTED BEFORE RUNNING)

*Written before `run_demo.py` is executed. The RUN is the judge.*

The demo feeds BOOTSTRAP two FRESH problem classes (not the gate's own self-test calls), plus
adversarial candidates, and lets the pipeline decide. I commit these predictions:

## Domain A — "sudoku-solution-validity" (SHOULD yield κ>0)
Candidate harnesses handed to the pipeline, in order (N-attempts bound = 3):
1. a **hallucinated** verifier (claims a tool that does not import/run);
2. a **soundness-incomplete** verifier (checks rows+columns, SKIPS the 3×3 boxes);
3. the **real** sudoku verifier (rows + columns + boxes).

Router verdict prediction: **SEARCH-AND-VALIDATE** (an exact decision procedure plausibly exists;
`kappa_hint` is `None` — routing does not promote).

Pipeline outcome prediction: **KAPPA>0_VERIFIER_FOUND**, but ONLY after the first two candidates
are REJECTED at the run step:
- candidate 1 (hallucinated) → REJECTED, reason `HALLUCINATED_NONRUNNING`;
- candidate 2 (no-boxes) → REJECTED, reason `SOUNDNESS_INCOMPLETE_MISSED_VIOLATION_TYPE`
  (it slips the box-only-broken case);
- candidate 3 (real) → VALIDATED, κ=1, all three violation types (`row_duplicate`,
  `column_duplicate`, `box_duplicate`) exercised → a registration record is produced.
The final outcome carries the honest ceiling string ("toy-passing != frontier-correct").

## Domain B — "essay-persuasiveness-quality" (SHOULD NOT yield a gate)
Router verdict prediction: **ARMOR-ONLY** (judgment-only; `kappa_hint` = 0.0).
Pipeline outcome prediction: **KAPPA=0_ARMOR_ONLY** — no exact verifier; BOOTSTRAP records
"armor-only + why" and does NOT invent a fake gate. (Even if a "judge" candidate were proposed, it
is judgment, not an exact decision procedure; the honest outcome is κ=0.)

## Domain C — "an under-specified problem class" (control)
Router verdict prediction: **ABSTAIN-NEED-INPUT** (under-specified to even search).
Pipeline outcome prediction: **ABSTAIN_NEED_INPUT** — asks for a sharper spec, does not guess.

## What would FALSIFY the design
- If the hallucinated candidate were registered → catastrophic (faked κ on a non-running tool).
- If the no-boxes candidate validated → soundness-incomplete verifier promoted (audit fix #2 failed).
- If the essay domain returned anything but κ=0 ARMOR-ONLY → a fake gate (faked κ).
- If routing alone set κ>0 (a non-None positive `kappa_hint` on the SEARCH verdict) → promote-by-claim.
