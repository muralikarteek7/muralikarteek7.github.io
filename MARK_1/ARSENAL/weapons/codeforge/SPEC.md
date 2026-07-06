# CODEFORGE — code & algorithm discovery (v5 weapon, CS_ENG department)
*One-page spec. Home: `Expanding_Frontiers/weapons/codeforge/`. Registered in `Next/BOX_V5.md`.*

## What it is (and is NOT)
CODEFORGE is the v5 weapon for the **code / algorithm** problem class. Code has the **sharpest cheap
verifier that exists** — it runs or it doesn't; it passes the held-out tests or it doesn't; the symbolic
identity holds or it doesn't. So most code tasks are **κ=1, weapon-eligible**. CODEFORGE *produces* a
machine-verified code/algorithm object and **never ships one the frozen verifier hasn't passed.**

**Two genuinely different value props — kept SEPARATE, every result labeled which one it is:**
- **(a) SYNTH-VERIFY — the reliable armor++ floor.** Synthesize code to a spec, gate it on **hidden +
  property + differential** tests the generator never sees. *Never ship unverified code.* Solid,
  buildable, the FETCH-KNOWN analogue. This is what CODEFORGE reliably delivers.
- **(b) THE CAPABILITY BET — open, likely-hard.** Does **verifier-gated iterate/search beat
  equal-compute best-of-k** on *non-memorized* tasks with rich feedback? This is the untested v5 lever.
  At toy scale it returned an **honest negative** (see `ab/RESULT.md` and the owned season lesson below).
  CODEFORGE builds the contamination-free harness to test it and **reports the negative plainly.**

**IS NOT:** (1) *"the model writes code"* — armor already does that; CODEFORGE's offense is
synthesize/search **until the frozen verifier passes on objects a single shot can't reliably produce**
(superoptimization, algorithm discovery), measured against an equal-compute best-of-k baseline. (2) *a
contamination laundromat* — a passed test on a memorized LeetCode/HumanEval problem proves **nothing**;
every benchmark task must be non-memorized. (3) *gameable* — the generator never sees the held-out
tests; hard-coding to visible tests is the reward-hack designed against. (4) *smarter than the model* —
it raises **verified throughput**, not the model's ceiling.

## ⚠ The owned lesson CODEFORGE is engineered against (do not re-tread)
At toy scale, execution-gated **generate→repair SATURATED**: any problem you can author a reference for
is a memorized classic the model **one-shots**, so repair beat nothing (Haiku −38pp vs resampling;
Sonnet +0pp). See `Next/benchmarks/v5_code_repair/RESULT.md`. **The escape, built into CODEFORGE:**
SUPEROPT and ALGO-DISCOVER are **inherently non-memorizable** — the search finds a *specific* object with
an **exact mathematical certificate** (0/1 principle / symbolic identity), not a test-suite that can be
recalled. The capability A/B uses **non-memorized** tasks (mutation / compositional novelty) + an
**equal-compute** baseline, or its result is void.

## The three modes (each maps to the κ-router; each has a FROZEN exact verifier)
| mode | router analogue | produces | the FROZEN exact verifier (κ=1) | file |
|---|---|---|---|---|
| **SYNTH-VERIFY** | armor++ / FETCH-KNOWN | code meeting a spec | HIDDEN unit tests **+ PROPERTY-based fuzz** **+ DIFFERENTIAL vs a reference oracle** — generator never sees them; hard-coding to visible → `GAMING_DETECTED` | `synth_verify.py` |
| **SUPEROPT** | SEARCH-OPEN | a faster/smaller correct implementation | **DIFFERENTIAL correctness gate (κ=1)** on adversarial+fuzzed inputs **+ a measured benchmark** (speed is *measured*, not certified). "faster-but-wrong" → REJECTED | `superopt_verify.py` |
| **ALGO-DISCOVER** | construction engine | a combinatorial algorithm object | an **EXACT certificate**: sorting network via the **0/1 principle** (all 2ⁿ binary inputs sort); matmul scheme via a **non-commutative symbolic identity** (the bilinear tensor equals the target exactly) | `sortnet_verify.py`, `matmul_verify.py` |

**ALGO-DISCOVER is the cleanest non-contaminated offense** (mirrors the cap-set weapon): **KNOWN** target →
reproduce the optimal object (optimal n=8 sorting network; Strassen's 7-mult 2×2) and machine-verify =
a **labeled reproduction**; **OPEN** target → verifier-gated search, cross-model-audited — **honest
negative expected** (records are hard; never claim one without a machine-certified object strictly
beating prior art + an independent audit).

## The contamination / gaming defenses (this is the whole game — §3 of the kickoff)
1. **Non-memorized tasks** for the capability bet: mutation (perturb a base spec so the memorized answer
   fails), compositional novelty, and SUPEROPT/ALGO-DISCOVER (inherently non-memorizable). No raw
   HumanEval/MBPP/LeetCode.
2. **Hidden + adversarial verification:** generator sees the spec + a few *example* tests; the frozen
   verifier holds the hidden tests, property tests, adversarial/fuzzed inputs, and a differential
   reference. A solution counts only if it passes the held-out set. **The held-out fuzz seed is
   UNPREDICTABLE by default** (drawn from `os.urandom`, recorded as `seed_used`; pinned only to reproduce
   a recorded run) — a source-reading attacker cannot pre-compute inputs it cannot predict (the audit's
   D1 fix). The certificate's strength = the **secrecy + size** of the held-out battery; sharpen the
   property + reference oracle to sharpen it.
3. **The gate must be able to FAIL** (non-waivable): every verifier passes a known-good input, CATCHES a
   known-broken one, AND rejects GAMING attempts — hard-coded-to-visible *and* **seed-prediction** (synth),
   faster-but-wrong *and* fixed-diff-set lookup (superopt), numeric-only tuning (matmul), sample-not-cube
   (sortnet). Proven by `selftest_all.py` (exits 0 only if all hold for all verifiers).
4. **Equal-compute A/B:** the capability claim is non-circular only as verifier-gated iterate/search **vs
   best-of-k at matched compute**, on the non-memorized set, ≥2 families, feedback isolated.

## Router (`codeforge_router.py`)
Deterministic. SYNTH-VERIFY / SUPEROPT / ALGO-DISCOVER fire on their κ=1 preconditions; ALGO-DISCOVER
splits KNOWN→reproduce vs OPEN→search (when in doubt, OPEN). **κ=0 → armor, not weapon:** "design this
architecture", "is this code *good*/clean", any deliverable scored by a **gameable proxy** (LLM-judge /
in-sample / human rating). CONFLICT RULE: positive trigger + negative item → **negative wins, weapon off.**

## Killer demos (committed prediction → run → compare)
- `demo_sortnet/` — **reproduce** the optimal n=8 sorting network (19 comparators) + machine-verify via
  the 0/1 principle (labeled reproduction); **plus** a from-scratch verifier-gated **search** that
  discovers a valid small network (ALGO-DISCOVER, non-memorized).
- `demo_strassen/` — **reproduce** Strassen's 7-mult 2×2 scheme + verify by exact symbolic identity;
  reject a broken scheme; confirm naive-8 as a control.
- `demo_superopt/` — take a naive correct function, search a faster correct variant, show the benchmark
  delta with the frozen differential-correctness gate intact; reject a faster-but-wrong impostor.
- `ab/` — the pre-registered **capability A/B** (verifier-gated iterate vs equal-compute best-of-k on
  non-memorized tasks); **honest result reported, negative or positive.**

## Honesty rails (non-waivable, CODEFORGE-specific)
- **A passed test on a memorized task proves nothing** — every result names whether the task is
  non-memorized and how that was ensured.
- **Reproduction is labeled reproduction** (optimal sorting net / Strassen = known objects, source+date).
  **Never claim an algorithm-discovery record** without a machine-certified object strictly beating prior
  art + an independent cross-model audit. **Never claim to solve an open problem.**
- **The gate that can't fail is not a gate** — no verifier ships without its passes-good / catches-broken
  / rejects-gaming self-test.
- **κ=0 stays armor** — "is this code good" (taste, maintainability, strategy) has no exact verifier →
  ground + abstain; CODEFORGE does NOT pretend to certify it.
- **Equal-compute or it's not an A/B** — any "iterate beats one-shot" claim is void without the
  matched-budget best-of-k baseline.

## Ceiling (stated every run)
CODEFORGE ships only frozen-verifier-passed objects; it **reproduces** known optimal objects and
machine-verifies them, and on non-memorized tasks it either beats equal-compute best-of-k by a
pre-registered margin (a real capability result, audit-confirmed) **or reports an honest negative.** It
raises **verified throughput**, not the model's capability ceiling; it certifies only what its verifiers
can EXECUTE; κ=0 judgments route to armor.
