# CODEFORGE CAPABILITY A/B — RESULT (2026-06-20): honest NEGATIVE (iterate = best-of-k, +0pp)

**Verdict: HONEST NEGATIVE / NO-SIGNAL.** Verifier-gated **ITERATE** does **not** beat equal-compute
**BEST-OF-K** (K=4) on these non-memorized code/algorithm tasks: **iterate − best-of-k = +0.0pp**. The
≥10% promotion bar is **not met**. **No promotion; the capability ratchet stays OPEN at v3.** This
reproduces the owned v5 repair-lever lesson in CODEFORGE's own arena — and, importantly, it holds **even in
the rich-feedback regime the prior construction probes lacked.**

## What ran (writer = Haiku; truth = the FROZEN verifiers; agent self-reports IGNORED)
2 families, 6 tasks, K=4 matched compute. ONESHOT = attempt #1; BEST-OF-K = any of 4 independent attempts
(oracle-pick); ITERATE = attempt + up to 3 repair rounds fed the verifier's literal failure.

| family | task | ONESHOT | BEST-OF-4 | ITERATE | iter−bo4 | band |
|---|---|---|---|---|---|---|
| SORTNET-MIN | s_n5b12 | ✅ | ✅ | ✅ (r1) | 0 | saturated |
| SORTNET-MIN | s_n6b16 | ✅ | ✅ | ✅ (r1) | 0 | saturated |
| SORTNET-MIN | **s_n7b21** | ❌ | ✅ | ✅ (**r2, used feedback**) | **0** | **IN BAND** |
| SORTNET-MIN | s_n8b28 | ✅ | ✅ | ✅ (r1) | 0 | saturated |
| SYNTH-MUT | y_reset | ✅ | ✅ | ✅ (r1) | 0 | saturated |
| SYNTH-MUT | y_countsmaller | ✅ | ✅ | ✅ (r1) | 0 | saturated |
| **aggregate** | (n=6) | **5/6** | **6/6** | **6/6** | **+0.0pp** | — |

**iterate − best-of-k = +0.0pp** (the decisive control — isolates *informative feedback* from *more
attempts*). **iterate − one-shot = +16.7pp** — but that entire gap is a **multiple-attempts effect**:
best-of-k captured the identical +16.7pp with **no feedback at all**. (Compare the owned v5 Sonnet result:
+17pp over one-shot, +0pp over best-of-k. Same pattern, fresh arena.)

## The one in-band case (n7) — where the lever actually got tested
At n=7 the writer one-shot **failed** (a real failure band, not saturation):
- **ITERATE:** r1 = a 16-comparator network the writer *claimed* was "optimal" — the frozen verifier
  re-checked it and it was **INVALID** (fails to sort `[1,1,0,0,0,0,0]`). Fed that exact failing input back,
  r2 = a valid 20-comparator network. **Feedback genuinely engaged and reached success in 2 of 4 calls.**
- **BEST-OF-4:** **also succeeded** — 1 of 4 blind independent attempts was a valid sorter (the other 3 were
  invalid bluffs the verifier rejected).
- **→ TIE.** Rich, exact feedback let iterate converge, but matched-budget blind resampling got there too.
  **Feedback was not the differentiator.** This is the cleanest possible test of the lever (the feedback is
  the literal failing input — you cannot make it richer) and the lever still does not beat resampling.

## The ARMOR worked exactly as designed — the verifier caught every bluff
The writers bluffed repeatedly; the frozen gate caught all of it (self-reports never trusted):
- n5 best-of-4 attempt #4 claimed an **8-comparator n=5 sorter** — *impossible* (proven optimum is 9); rejected.
- n7 iterate r1 claimed **"optimal 16 comparators"** — re-verified INVALID.
- n8 iterate r1 claimed **"verified on all 40320 permutations"** — re-verified independently (true this time, but *because the machine checked it*, not because the agent said so).
- n7 best-of-4: **3 of 4** attempts were invalid; only one was a real sorter.

This is the SYNTH-VERIFY/SORTNET floor doing its job: **CODEFORGE never shipped an unverified or bluffed
object.** That reliability — not a capability gain over best-of-k — is the weapon's real, demonstrated value.

## Honest caveats (non-waivable)
- **Small N** (6 tasks); **single writer** (Haiku, for failure-band headroom — this answers "does rich
  feedback rescue a weak writer on code/algorithm tasks?", not the infra-gated frontier-model question).
- **BEST-OF-4 was within-context** (4 attempts in one response), which if anything *understates* best-of-k
  (less diverse than 4 independent spawns) — a **conservative handicap that biases toward iterate winning**;
  iterate *still* tied, which **strengthens** the negative.
- **Saturation at small n**: where one-shot already succeeds there is no headroom by construction (the owned
  lesson — any task you can author a reference for is one-shot by a capable model). Only n7 escaped it here.
- **Memorization risk of the saturated tasks (cross-model audit, fair caveat):** `y_countsmaller` ≈ LeetCode
  #315 (direction-reversed) and SORTNET n≤5 are textbook — HIGH memorization-risk. This does **not** undermine
  the +0pp conclusion; it *explains* the saturation (memorization IS the trap, manifesting). The load-bearing
  result is the **n7 in-band tie**, which requires constructing a specific tight-budget network and is far less
  memorization-prone.
- This is a **directional probe, NOT the pre-registered promotion run.** A faithful ≥10% test needs the
  **infra-gated** harness (`V5_INFRA_UNLOCK_SPEC.md`: API + sandbox + SWE-scale non-memorized real tasks).

## Bottom line
**No marginal Q for verifier-gated iterate over equal-compute best-of-k (+0pp).** CODEFORGE's value is the
**reliable SYNTH-VERIFY floor + the exact ALGO-DISCOVER certificates** (reproduce-and-verify, gate every
bluff), **not** the capability bet — which returns the **honest negative** the kickoff anticipated. The
≥10% capability ratchet stays **OPEN at v3**. The faithful frontier-model × real-repo test remains the one
unrun, infra-gated path.
