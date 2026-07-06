# CODEFORGE CAPABILITY A/B — pre-registration (committed BEFORE running)
*Written 2026-06-20. The open v5 bet: does verifier-gated ITERATE beat equal-compute BEST-OF-K?*

## The question (non-circular)
On **non-memorized** code/algorithm tasks in the **one-shot-failure band**, does **verifier-gated ITERATE**
(feed the frozen verifier's literal failure back to the writer) beat **equal-compute BEST-OF-K**
(K independent attempts, no feedback, oracle-pick) by **≥10 percentage points**? The decisive control is
**ITERATE vs BEST-OF-K** — it isolates *informative feedback* from *more attempts* (this is the exact
control the v5 repair-probe used; reused here, ported to CODEFORGE's frozen verifiers).

## Why this is a FRESH test (not a re-tread of the owned negatives)
The owned negatives killed the lever on (a) **construction with THIN feedback** (no-3-in-line: the only
feedback is "this triple collides" — Haiku −38pp vs best-of-k) and (b) **toy code that SATURATED**
(capable models one-shot any problem you can author a reference for → no headroom). This probe targets the
**untested regime in between: code/algorithm tasks with RICH, actionable feedback** — a sorting network
that "fails to sort input [1,0,1,0,0]" is a precise, patchable signal, unlike a collision. If feedback ever
helps, here is where it should. Honest prior: the owned season says **expect a negative or saturation**;
report it plainly. A faithful ≥10% test at scale remains **INFRA-GATED** (`V5_INFRA_UNLOCK_SPEC.md`: needs
API + sandbox + SWE-scale non-memorized tasks); this is a small, in-budget probe of the same question.

## Families (≥2, machine-scored by FROZEN verifiers; agent self-reports IGNORED)
- **F1 — SORTNET-MIN** (rich feedback): "emit a JSON comparator list that sorts n inputs using ≤ C
  comparators." Verifier: `sortnet_verify.py` (0/1 principle, exact). Non-memorized: a *specific tight
  budget* forces construction; success = **valid AND size ≤ C**. Feedback on fail = the failing binary
  input, or "valid but M > C comparators."
- **F2 — SYNTH-MUTATION** (compositional novelty): a compositional spec (e.g. "running max that resets to
  0 after any negative") + 2 visible examples. Verifier: `synth_verify.py` (HIDDEN + PROPERTY +
  DIFFERENTIAL). Non-memorized: composed rule unlikely to be verbatim in training. Feedback on fail = the
  first failing **FEEDBACK-set** input (DISJOINT from the held-out scoring set — the audit's anti-overfit fix).

## Arms (matched compute K = 4 model calls)
- **ONESHOT** — 1 attempt (= candidate #1 of BEST-OF-K; no extra spend).
- **BEST-OF-K** — K=4 independent attempts, NO feedback; success = ANY of the 4 verifies (oracle-pick). *The matched-budget control.*
- **ITERATE** — 1 attempt + up to K−1=3 repair rounds; each round is fed the frozen verifier's literal failure; success = the final attempt verifies (or any round does). Same 4 calls.

## Writer model
**Haiku** (`claude-haiku-4-5`) — deliberately, for one-shot-failure HEADROOM (the lever can only show value
where the base model errs; a saturated strong model gives no signal — the owned lesson). Honest scope: this
answers *"does rich feedback rescue a weak writer on code/algorithm tasks?"*, the cheap in-budget question —
NOT the infra-gated *"does feedback give a frontier writer a ≥10% capability boost on real-repo code"* (still owed).

## Truth & scoring
The ORCHESTRATOR runs the frozen verifier on every returned object; **agent self-reports are ignored**
(the v5 invariant). Per family per task per arm: success ∈ {0,1}. Report success rate per arm; the
headline is **ITERATE − BEST-OF-K** (pp).

## Decision rule (pre-committed)
- **PROMOTION-grade positive** (flag LOUDLY for the audit): ITERATE − BEST-OF-K ≥ **+10pp**, holding across
  both families, with feedback (not attempts) as the isolated cause. *Expected: NO.*
- **Honest negative** (the expected outcome): ITERATE − BEST-OF-K < +10pp (tie, or worse). Report plainly;
  it confirms the owned lesson in a fresh (rich-feedback) arena and the lever stays INFRA-GATED.
- **No-signal** (uniform fail or saturate): if a family is all-0 or all-1 across arms, declare it
  out-of-band (no power) and say so — do NOT read a tie as a refutation there.

## Honest caveats (pre-committed)
Small N (≤3 tasks/family); single writer (Haiku); not token-matched beyond call-count (ITERATE rounds carry
growing context — if ITERATE *still* doesn't win despite ≥ the budget, that strengthens a negative). This is
a directional probe, NOT the pre-registered promotion run. **No promotion will be claimed from this** unless
the +10pp bar is cleanly met across both families AND survives the independent cross-model audit.
