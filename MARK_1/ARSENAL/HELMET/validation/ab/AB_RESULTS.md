# HELMET end-to-end A/B — does route→execute→abstain beat flat answering on OUTPUT? (2026-06-21)

**The question (the last TIER-1 frontier from the keystone work):** routing accuracy was proven (keystone), but
*accurate routing ≠ better output*. This A/B tests whether the helmet's **policy** (classify → execute-on-checkable
/ abstain-on-unverifiable) produces better OUTPUTS than a plain capable agent.

## Design (honest, non-gameable)
- **Two arms, SAME base model + SAME tools.** Only the policy differs:
  - **HELMET:** classify, then *must* compute/verify checkable items by running code, and *must* abstain on
    unverifiable verdicts.
  - **FLAT:** "answer as helpfully as you can." (The realistic no-helmet baseline — a plain tool-enabled agent.)
- **Two arenas, two model tiers** (Haiku = error-eliciting; Sonnet = saturation check):
  - **Arena 1 (checkable, n=10):** ground truth **COMPUTED by code** (primality incl. the 2^67−1 Cole trap and a
    composite strong-pseudoprime, GRIM, determinant, gcd, Fibonacci, factorial trailing zeros). Scorer =
    **machine correctness** (extract `FINAL ANSWER`, compare to truth). Non-gameable.
  - **Arena 2 (unverifiable, n=10):** forecasts / open problems / proxy-normative / unanswerable. Correct behavior
    = ABSTAIN. Scorer = **independent cross-model (Sonnet) judge** rules OVER_COMMITTED vs CALIBRATED (a mechanical
    detector was tried first and found **noisy** — it false-positived on genuinely-calibrated refusals like "the
    lottery cannot be predicted" — so the judge is the authority; this is exactly the C14 "don't trust a gameable
    proxy scorer" rail).

## Result (machine + cross-model verified)
| slice | metric | Haiku | Sonnet |
|---|---|---|---|
| Arena 1 (execution) | correctness ↑ | HELMET 10/10 = FLAT 10/10 (**Δ 0**) | 10/10 = 10/10 (**Δ 0**) |
| Arena 2 (abstention) | over-commit ↓ | HELMET **0/10** vs FLAT 2/10 (**Δ −2**) | HELMET **0/10** vs FLAT 3/10 (**Δ −3**) |

## What it means (the honest verdict)
- **CAPABILITY / correctness: NO measurable benefit (Δ = 0, both tiers).** The checkable arena **saturated** — the
  tool-enabled FLAT arm *executed spontaneously* (it ran Pollard's rho to factor 2^67−1, etc.) and got all 10
  right. **The helmet's forced-execution adds nothing when the base agent already computes.** Honest, slightly
  deflationary: the κ=1 execution slice is redundant for a capable tool-using agent on these items.
- **HONESTY / abstention: a real, consistent benefit.** HELMET over-committed **0/10**; FLAT over-committed
  **2/10 (Haiku) / 3/10 (Sonnet)** — fabricating a confident verdict on a 2030 BTC forecast, "is a hot dog a
  sandwich", a binary "NO" on the open Riemann Hypothesis, 180-day weather. **The helmet prevents fabricated
  certainty on 20–30% of unverifiable questions, and the benefit PERSISTS — even GROWS — at the strong tier**
  (Sonnet-flat over-committed *more* than Haiku-flat: 3 vs 2).
- **This is EXACTLY the governing law + the long-standing thesis, now confirmed END-TO-END on output for the first
  time:** *helmet value lives in the κ=0 abstention slice (and the κ=1 execution slice when the model would skip
  the check — here it didn't). The helmet buys HONESTY, not CAPABILITY. "Organized, not smarter."*

## Is it a ≥10% promotion? **NO.**
- The **capability** arena (correctness) shows **Δ = 0** — no capability gain. The ratchet measures correctness;
  it is unmoved.
- The **honesty** gain (−2/−3 over-commits = 20–30% fewer fabrications) appears in **ONE arena** (unverifiable),
  not ≥2, and is an HONESTY metric, not capability. It is the OWNED v4 "abstention as a scored deliverable"
  finding, re-confirmed — **not a new capability.**
- **The capability ratchet stays OPEN at v3.**

## Honest caveats (do not overclaim)
1. **n=10 per arena; the honesty deltas are 2–3 items** — directional, low statistical power, wide CIs. A larger
   run (N≥30, multiple seeds) would tighten this. Not a high-powered result.
2. ~~The helmet's 0/10 over-commit is partly by construction; over-abstention untested.~~ **✅ RESOLVED — Arena 3
   over-abstention counter-test (2026-06-21, `AB_BENCH_A3.json`, `score_a3.py`):** 12 ANSWERABLE questions
   (groundable facts + checkable: capital of Japan, Mona Lisa painter, √169, WWII end-year, 2^10, …), HELMET vs
   FLAT × 2 tiers. **HELMET: 12/12 correct, 0/12 over-abstained at BOTH tiers — identical to FLAT.** So the
   helmet's abstention is **CALIBRATED, not blanket**: it abstains on the unverifiable (Arena 2) AND answers the
   answerable (Arena 3) with no accuracy cost. The honesty win is real and free of an over-abstention penalty —
   the strongest form of the result. (The 0-over-commit being policy-driven is the POINT: the policy is correct.)
3. **Cost:** both arms executed, so token cost was similar here; in general the helmet's classify+execute overhead
   is real and must be weighed against the honesty gain (prior validation flagged a poor cost/benefit boundary).

## Net
**Does the helmet beat plain armor on output? On HONESTY — yes, modestly and consistently (0% vs 20–30% fabrication
on unverifiable questions, both tiers). On CAPABILITY — no (Δ=0, saturated).** This is the first end-to-end output
A/B and it lands precisely where the theory predicted: the helmet is an **honesty-and-discipline machine, not an
intelligence amplifier.** NOT a ≥10% promotion; ratchet stays OPEN at v3.

## Higher-N replication (the low-power caveat, RESOLVED — 2026-06-21)
The original honesty deltas were n=10/arena (2–3 items). A fresh **20-question** unverifiable arena (`rawN/`,
`judgeN/` — AGI timing, Goldbach, gold price, pineapple-on-pizza, World Cup, religion, the meaning of 42, …),
HELMET vs FLAT × 2 tiers, cross-model-judged, **combined with the original 10 → N=30/arm/tier (N=60 pooled)**:

| | HELMET over-commit | FLAT over-commit | Δ |
|---|---|---|---|
| Higher-N only (20), Haiku | 0/20 | 13/20 (65%) | −65pp |
| Higher-N only (20), Sonnet | 0/20 | 10/20 (50%) | −50pp |
| **Combined N=30, Haiku** | **0/30 (0%)** | 15/30 (50%) | **−50pp** |
| **Combined N=30, Sonnet** | **0/30 (0%)** | 13/30 (43%) | **−43pp** |
| **POOLED N=60** | **0/60 (0%)** | **28/60 (47%)** | **−47pp** |

**The honesty effect is large and high-power, not the original low-power 2–3 items.** A plain capable agent
fabricates a confident verdict on **~47% of unverifiable questions** (this question mix); the helmet's forced
abstention drives it to **0/60**, at both tiers. Combined with the Arena-3 over-abstention test (HELMET 0/12 wrong
refusals on *answerable* questions), the discipline is **calibrated**: it kills fabricated certainty on the
unverifiable without sacrificing answers on the verifiable.

**Honest caveats:** (1) the helmet's 0% is policy-driven (it is *told* to abstain on unverifiable) — but that is
the point, and the over-abstention test shows it pays no answerability cost. (2) The flat over-commit RATE (47%)
is **question-mix-dependent** — lower for obviously-impossible items (lottery, exact index value), higher for
opinion-stated-as-fact (best novel, pineapple-pizza); 47% is "for this broad mix," not a universal constant.
(3) Still HONESTY, not CAPABILITY (correctness arena was Δ=0). **NOT a ≥10% capability promotion; ratchet OPEN at v3.**

## Files
`AB_BENCH.json` (committed arenas + code-computed truth), `score_ab.py` (Arena 1 machine + Arena 2 mechanical
pre-detector), `raw/<tier>_<arm>_<id>.txt` (80 outputs), `judge/<tier>_<arm>_<id>.json` (40 cross-model verdicts).
