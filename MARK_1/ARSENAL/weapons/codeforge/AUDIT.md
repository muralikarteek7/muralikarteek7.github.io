# CODEFORGE — independent cross-model audit (red-team)

**Generator:** Opus 4.8 (built the weapon).
**Auditor:** **Sonnet 4.6** — a model **≠ the generator** (never Opus-audits-Opus; Fable inactive 2026-06-12).
**Date:** 2026-06-20. **Scope:** re-derive the certificates with independent code; try to GAME every gate;
red-team the contamination defense; check the honesty rails; run the gate + demos independently.
**Auditor's raw artifacts:** [`audit_independent/`](audit_independent/) (`FINDINGS.md` + 4 independent
checkers + 4 result JSONs — fresh code, no import of the weapon's verifier logic).

## Top-line verdict: **SOUND-WITH-CAVEATS** → caveats FIXED, re-gated green.
The mathematical certificates are independently confirmed and the honesty framing is accurate. The auditor
found **two real false-accept vulnerabilities** in the test-set-relative verifiers (SYNTH-VERIFY, SUPEROPT)
— both **now fixed and the fixes machine-proven** by strengthened self-tests.

## 1. Independent re-derivation (the auditor wrote its OWN checkers — different method)
| object | weapon's claim | auditor's independent method | result | agree? |
|---|---|---|---|---|
| n=8 Batcher sorting net | valid, 19 comparators | **all 40,320 permutations** of distinct values (≠ the 0/1 method) | valid, 19 | ✅ |
| n=8 Batcher (2nd method) | valid | fresh 0/1 binary sweep (256 inputs) | valid | ✅ |
| n=6 / n=7 discovered nets | valid, 13 / 18 | 720 / 5,040 permutations | valid, 13 / 18 | ✅ |
| Strassen 7-mult 2×2 | valid, R=7 | **10,000 random numeric** matrix trials | 0 failures | ✅ |
| Strassen 7-mult 2×2 (2nd) | valid, R=7 | independent symbolic sympy expansion | 0 mismatches | ✅ |

**Every independent re-derivation agreed.** The auditor also confirmed the MATMUL non-commutative check is
**strictly stronger** than a commutative check (it catches an A/B left-right product swap that commutative
sympy misses) — a design strength, not a bug.

## 2. Gaming attempts → 2 false accepts found (the load-bearing findings), both FIXED
| # | gate | attack | severity | status |
|---|---|---|---|---|
| **D1** | **SYNTH-VERIFY** | the fuzzer's seed was a fixed **public** constant (`seed=7`/`4242`); a source-reading attacker pre-computes all held-out fuzz inputs into a lookup table → **VERIFIED on a provably wrong function** (wrong on 621/1000 unseen inputs) | MED-HIGH | **FIXED** |
| **D2** | **SUPEROPT** (self-test only) | the self-test's `diff` set was 9 fixed values; a lookup table over those 9 + the bench input passes — the "rejects-gaming" self-test under-covered (real callers pass fuzzed inputs, so production was safe) | LOW-MED | **FIXED** |

**Fix for D1 (`synth_verify.py`):** the fuzz seed now defaults to **`os.urandom`** (unpredictable; recorded
as `seed_used`); a seed is pinned only to reproduce a recorded run. New self-test PROVES the defense: a
lookup-table candidate keyed to seed `S1` **passes under S1** (showing why fixed public seeds are unsafe)
but is **CAUGHT under a different/unpredictable seed**. → `selftest_all.py` green.

**Fix for D2 (`superopt_verify.py`):** the self-test's `diff` set is now **9 fixed + 200 fuzzed** inputs,
and a new gaming candidate that hard-codes the 9 fixed values is **caught by the fuzzed inputs**; the
docstring now states `diff_inputs` MUST be adversarial+fuzzed (not a tiny fixed set). → green.

**Not fooled:** SORTNET (the exhaustive 0/1 sweep is exact — no black-box attack found) and MATMUL (the
non-commutative symbolic identity is exact — numeric-only tuning is caught). These are the κ=1 ALGO-DISCOVER
certificates; the auditor could not break either.

## 3. Contamination red-team
- **Feedback vs scoring disjoint** (the anti-overfit fix): **CLEAN** — both synth tasks confirmed disjoint at code level.
- **Self-reports ignored:** **CONFIRMED** — the harness re-verifies with the frozen verifier; a candidate
  with a "# verified correct" comment but wrong output is caught.
- **+0pp negative honestly derived:** **CONFIRMED** — the n7 trajectory (oneshot=0, bestof4=1, iterate=1)
  is internally consistent; the "tie at equal compute" narrative is accurate.
- **Memorization risk (a fair caveat):** `y_countsmaller` ≈ LeetCode #315 (direction-reversed); SORTNET
  n≤5 are textbook. These are HIGH memorization-risk — **which is exactly why they SATURATED** in the A/B.
  The honest finding stands: saturation IS the memorization trap manifesting, and the load-bearing in-band
  result (n7) is far less memorization-prone. Now acknowledged explicitly in `ab/RESULT.md`.

## 4. Honesty rails — accurate throughout
No "record" / "open problem solved" / "world first" claim anywhere. All reproductions labeled as
reproductions (source+date). Router correctly sends all κ=0 tasks (design/taste/proxy/conflict-rule) to
ARMOR. Every verdict carries its ceiling note. The "rejects-gaming" language in `SPEC.md` was **tightened**
(it now states the defense precisely: the gate catches hard-coding; its strength = the **secrecy + size**
of the held-out battery; with an unpredictable seed, seed-prediction is dead).

## 5. Independent live runs (auditor's machine)
`selftest_all.py`, all three `demo_*/run_demo.py`, and `ab/harness.py selftest` → **all exit 0** on the
auditor's independent run.

## Net
Two genuine verifier weaknesses caught by the independent model and **fixed + re-gated** (the exact value of
cross-model audit: the generator's self-review would not have found the seed-prediction attack). The κ=1
ALGO-DISCOVER certificates (SORTNET, MATMUL) are unbreakable as designed. The honesty framing and the A/B
negative are accurate. **Post-fix status: SOUND.** No record, no promotion, no open-problem claim.
