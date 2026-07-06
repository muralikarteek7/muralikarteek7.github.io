# PROOFSMITH capability A/B — PRE-REGISTRATION (written BEFORE any model arm runs)

*The open bet (kickoff §5): does **kernel-feedback proof-search beat equal-compute best-of-k** on
**non-memorized** lemmas? Formal proof is the rich-feedback domain the season flagged as "one of the
few honest places left to test" the repair lever (`V5_INTERIM_VERDICT_2026-06-12.md`). **A negative is
a valid, expected outcome** — the owned probes already showed repair loses to / ties resampling on
construction (Haiku −38pp, Sonnet +0pp) and saturates on code. This re-tests it where feedback is
RICHEST: the kernel's exact error messages.*

## The question
Holding the prover model + compute budget fixed, does **execution-gated repair** (attempt → run the
KERNEL → feed the error back → repair) reach a kernel-checked proof that **independent resampling**
(best-of-k) does not?

## Non-memorization (the contamination guard)
Lemmas are stated over **freshly-named custom recursive functions** (`ps_f1/ps_g/ps_t/ps_d`, see
`preamble.lean`) so the exact statements are **not verbatim in any training corpus**. Ground truth is
established by **verified reference proofs** (`reference_proofs.lean`, all 4 kernel-checked, NOT shown
to the prover). The prover sees only the preamble + one lemma statement.

## Lemmas (4; each TRUE & kernel-proven in reference_proofs.lean; require induction)
- **L1** `∀ n, ps_f1 n = n * n`            (sum of odds; nonlinear closing step)
- **L2** `∀ n, ps_g n = 3 * n`             (linear)
- **L3** `∀ n, 2 * ps_t n = n * (n + 1)`   (Gauss; nonlinear closing step)
- **L4** `∀ n, ps_d (n + 1) = ps_t n`      (cross-function recurrence)

## Prover model
**M = Haiku** (claude-haiku-4-5). Chosen for **one-shot-failure headroom** — capable models saturate
toy proofs (the season's recurring lesson), leaving no band where feedback can matter. **HONEST SCOPE
(committed): this answers "does kernel-feedback rescue a WEAK prover on fresh lemmas?" — NOT "does it
give a STRONG prover a capability boost" (that is infra-gated: Fable inactive; faithful scale needs
API + budget control we lack).** Fable-down ⇒ no frontier prover available.

## Arms (budget-matched at 3 model calls/lemma; prover is BLIND to the kernel except via repair feedback)
- **ONE-SHOT**: 1 blind attempt (= attempt a1).
- **BEST-OF-3**: 3 independent blind attempts (a1,a2,a3); PASS iff any kernel-checks.
- **REPAIR**: attempt r1 (blind); if it fails the gate, feed back the **verbatim kernel error** and
  ask for a repair (r2); if r2 fails, feed its error → r3. ≤3 calls; PASS iff any kernel-checks.

## Truth (zero trust in self-reports)
The **PROOFSMITH kernel gate** (`proof_gate.py`, target = the exact lemma statement, allowed axioms =
`{propext, Classical.choice, Quot.sound}`, no sorry) judges every returned proof. Agent prose like
"this works" is IGNORED; the proof text is extracted and the kernel decides. A proof that uses `sorry`
or an extra axiom is scored FAIL even if it "compiles."

## The decisive comparison (the active ingredient)
**REPAIR − BEST-OF-3.** Best-of-3 controls for "more attempts"; the only thing repair adds over it is
**informative kernel feedback**. 
- Pre-registered POSITIVE claim: **repair − best-of-3 ≥ +10pp** (≥1/4 lemmas) ⇒ feedback is the active
  ingredient → a real (if small) capability signal → escalate to a powered, audited test.
- Otherwise (≤0, or saturated/uniform-fail with no discriminating band): **HONEST NEGATIVE / NO SIGNAL**
  — consistent with the owned construction + code results. Reported plainly. **No promotion.**

## Honesty rails
Report the raw per-lemma table (which arm solved what, repair rounds used). If one-shot already solves
everything → **SATURATION, lever untestable here** (report as such, don't manufacture a band). If
nothing solves → **uniform-fail, no signal** (don't claim a repair win on noise). **This A/B cannot,
by itself, promote the box** — a weapon ADDED is a capability EXPANSION, not a ≥10% promotion; only a
powered, cross-model-audited ≥10% beat over best-of-k on non-memorized lemmas would move the ratchet,
and that is not what this small probe is powered to show.
