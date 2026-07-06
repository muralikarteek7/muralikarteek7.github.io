# CODEFORGE INDEPENDENT ADVERSARIAL AUDIT
*Auditor: Sonnet (independent model from Opus, the producer). Date: 2026-06-20.*
*All audit code in this directory is written fresh — no import of their verifier logic for re-derivation.*

## TOP-LINE VERDICT: SOUND-WITH-CAVEATS

The core mathematical claims are independently verified and correct. The honesty framing is accurate.
Two real gaming vulnerabilities confirmed via code — both require source-code access (not black-box)
but both produce genuine FALSE ACCEPTS on provably-incorrect functions.

## 1. INDEPENDENT RE-DERIVATION RESULTS

| Object | Their claim | My method | My result | Agreement |
|---|---|---|---|---|
| n=8 Batcher | valid, 19 comp | Permutation test (40,320 perms) | valid, 19 comp | AGREE |
| n=8 Batcher | valid, 19 comp | Fresh 0/1 binary sweep (256 inputs) | valid, 19 comp | AGREE |
| n=6 greedy | valid, 13 comp | Permutation test (720 perms) | valid, 13 comp | AGREE |
| n=7 greedy | valid, 18 comp | Permutation test (5,040 perms) | valid, 18 comp | AGREE |
| Strassen 7-mult | valid, R=7 | Numeric (10,000 random int trials) | valid, 0 failures | AGREE |
| Strassen 7-mult | valid, R=7 | Symbolic sympy (commutative, independent) | valid, 0 mismatches | AGREE |

All re-derivations agree with the weapon's claims. No disagreement found.

## 2. GAMING ATTEMPTS

### 2a. SORTNET — NOT FOOLED
- Broken n=4 network (12/16 binary inputs pass): CAUGHT by exhaustive sweep
- Near-valid n=6 (drop last comp): CAUGHT
- No black-box gaming strategy found against the 0/1 principle sweep

### 2b. MATMUL — NOT FOOLED
- Biased sample (a01=0 inputs only): fools 100-sample checker but random numeric (200 trials) catches it; symbolic identity unconditionally catches it
- Commutative vs non-commutative: confirmed their non-comm check is STRICTLY STRONGER (detects L/R product swap that commutative check misses) — DESIGN STRENGTH, not a vulnerability

### 2c. SYNTH-VERIFY — FALSE ACCEPT CONFIRMED (Defect #1)
Strategy: LCG seeds are fixed public constants in synth_verify.py. Pre-compute ALL 150+150 fuzz inputs by reading the source, build a lookup table with correct outputs, fallback to [] for unseen inputs.

Result: verdict=VERIFIED, passed=True — a FALSE ACCEPT on a function that returns [] for 621/1000 random unseen inputs.

The selftest only tests visible-hardcode gaming; full-seed-prediction attack is not covered.

### 2d. SUPEROPT — FALSE ACCEPT CONFIRMED (Defect #2)
Strategy: the selftest's diff_inputs is only 9 hardcoded values. Hardcode a lookup table for all 9 + bench input, return 0 elsewhere.

Result: verdict=SUPEROPT_WIN, correct=True — a FALSE ACCEPT. With 200 random diff inputs: attack fails (5 mismatches). The selftest's "rejects-gaming" only covers the narrower bench-hardcode attack.

## 3. CONTAMINATION RED-TEAM

- (a) Feedback disjoint from hidden/scoring: CLEAN (y_reset and y_countsmaller both confirmed disjoint)
- (b) Self-reports ignored: CONFIRMED (harness re-verifies with frozen verifier)
- (c) Memorization risk: y_reset LOW-MEDIUM; y_countsmaller HIGH (LC#315 direction variant); SORTNET n<=5 HIGH. PREREG.md acknowledges saturation honestly; +0pp is not undermined.
- (d) +0pp honestly derived: CONFIRMED (n7: oneshot=0, bestof4=1, iterate=1, iter_rounds=2 verified)

## 4. HONESTY RAIL CHECK

| Rail | Result |
|---|---|
| Reproductions labeled as reproductions | PASS |
| No "record" / "open problem solved" claims | PASS (all 5 files scanned, clean) |
| Router sends kappa=0 to ARMOR | PASS (6 cases tested) |
| Conflict rule: negative wins | PASS |
| Honest negative reported plainly | PASS ("+0pp, ratchet stays OPEN") |
| Non-comm cert stronger than commutative | CONFIRMED (design strength) |

## 5. LIVE RUN RESULTS

| Command | Exit Code |
|---|---|
| python3 selftest_all.py | 0 |
| python3 demo_sortnet/run_demo.py | 0 |
| python3 demo_strassen/run_demo.py | 0 |
| python3 demo_superopt/run_demo.py | 0 |
| python3 ab/harness.py selftest | 0 |

## 6. DEFECTS

**Defect #1 — FALSE ACCEPT in SYNTH-VERIFY (Severity: MEDIUM-HIGH)**
File: synth_verify.py (LCG class, fixed seeds); _selftest() missing coverage
Fixed LCG seeds as constants in public source allow pre-computation of all fuzz inputs. Confirmed: lookup-table function (wrong on 621/1000 random inputs) passes VERIFIED.

**Defect #2 — FALSE ACCEPT in SUPEROPT selftest (Severity: LOW-MEDIUM)**
File: superopt_verify.py, _selftest() line 141 (diff variable, only 9 values)
Lookup table hardcoding all 9 diff inputs + bench input passes SUPEROPT_WIN on a function returning 0 everywhere else. In real use with large diff_inputs the attack fails, but the selftest's "rejects-gaming" coverage is incomplete.

**Finding #3 — Memorization risk in y_countsmaller (Informational)**
File: ab/harness.py, SYNTH_TASKS["y_countsmaller"]
Structurally equivalent to LeetCode #315 with direction reversed. HIGH memorization risk. Does not undermine the +0pp result (task saturated anyway) but weakens the "non-memorized" label.
