# RULES — the non-waivable laws (carried forward from RATCHET.md)

*The full version ladder + history is archived in `MARK_0/02_ladder_history/RATCHET.md`. These are the rules
that still govern, stated once, cleanly.*

## 1. The ≥10% promotion threshold
Only call something a **promotion** — only advance the capability ratchet — if it is **at least 10% better than
the current best**, measured by a **real, non-circular A/B + ablation across ≥2 arenas**, without regressing
honesty. **Below 10%, or weak-dominance-only, or single-arena / single-model / no-ablation → it is a POINT
RELEASE, not a version bump, and the ratchet does not move.** "Can't do worse" is not a promotion.

## 2. The research flow (mandatory order — no early exit, no mid-loop promotion)
1. **Stand on the suit** — pick up the live system; never rebuild from scratch.
2. **Research loop:** build → benchmark → update, repeated. Every measurement non-circular.
3. **Break only at the ≥10% bar** (rule 1). Until met, you do not promote.
4. **Prove on the products** (`../../Artifacts/`) before promotion — improve to N+1, never regress the scorer.
5. **Promote** — then archive the surviving idea and re-seed the next bet.

## 3. No circular measurement
A result scored on data you hand-authored to produce it proves nothing. Truth must be a machine check, a fetched
source, or a **different** model — never the generator's self-report.

## 4. Cross-model > cross-instruction
Real independence needs a **different model**, not a re-prompt. The auditor is never the generator. (With Fable
inactive: use Sonnet/Haiku as auditors — never Opus-audits-Opus.)

## 5. The honesty rails (F11)
- Flag the unverified; report negatives plainly; claim **no win without proof**.
- **Never claim to solve an open problem** — exhibit a machine-verified object or report you didn't.
- **A verifier that can't fail is not a verifier** — any shipped check must be proven able to reject corrupted input.

## 6. Cost is part of the discipline
Calibrate cost to stakes: `value × open-defects ÷ cost`. Trivial tasks get a cheap proportionate response;
reserve cross-model agents, fetching, and ablations for load-bearing claims, promotions, and anything written
down. Permission to stop when the marginal value is low.

## Current ratchet position
**OPEN at v3.** v4 (ladder/efficiency), v5 (weapons), the helmet, and the v5.1/v5.2 options are all expansion
or efficiency stamps — **not** ≥10% capability promotions. See `STATE.md`.
