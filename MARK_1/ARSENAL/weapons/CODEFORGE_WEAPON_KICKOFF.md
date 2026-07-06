# KICKOFF — build WEAPON #1: CODEFORGE (code & algorithm discovery) for the v5 box
*Paste everything below into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written
2026-06-20. CODEFORGE is the top of `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` — the sharpest-verifier,
largest-surface weapon the University is missing.*

---

You are building **CODEFORGE**, the box's next **WEAPON** (offense): a verifier-gated engine that **produces
machine-verified code and algorithm objects** — synthesized routines, superoptimized implementations, and
discovered combinatorial algorithms — where a **frozen, exact verifier is the only judge.** It becomes the
**Computer Science & Engineering** department of the HELMET (University Mode). Work BOX-style: plan → produce →
**verify INDEPENDENTLY** (cross-model ≠ generator, or a machine check) → ground → be honest; **no win without
proof; never claim to solve an open problem.**

## 0. ORIENT — read first (in order)
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (the κ-router — CODEFORGE is a κ=1 weapon, router Branch B/C
analogue), `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` (item #1 = this), and the two existing weapons as
**templates** (`Expanding_Frontiers/weapons/socius/` and `…/psymetrix/` — copy their shape: `SPEC.md`,
frozen `*_verify.py`, a `selftest_all.py` gate, a `*_router.py`, a `demo_*/` with committed predictions, `AUDIT.md`).
Also read `Expanding_Frontiers/FRONTIER_ENGINE_WORKFLOW.md` (the propose→gate→audit loop you generalize).

**⚠ DO NOT RE-TREAD these owned negatives — read them so you don't repeat the season's most expensive lesson:**
`Next/benchmarks/V5_INTERIM_VERDICT_2026-06-12.md`, `Next/benchmarks/v5_repair_probe/PROBE_LOG.md`,
`Next/benchmarks/v5_code_repair/RESULT.md`, `Next/benchmarks/V5_INFRA_UNLOCK_SPEC.md`. **The finding:** at toy
scale, execution-gated **generate→repair SATURATED** — capable models one-shot every problem you can author a
reference for ("any problem you can write a reference for is a memorized classic"), so repair beat nothing
(Haiku −38pp vs resampling; Sonnet +0pp). **CODEFORGE must be engineered against exactly this**, or it is just
armor's test-runner with extra cost.

## 1. THE HONEST FRAMING — what CODEFORGE IS and IS NOT (do not skip)
**IS:** a κ=1 weapon. Code has the sharpest cheap verifier that exists — **it runs or it doesn't; it passes the
tests or it doesn't; the compiler accepts it or it doesn't.** CODEFORGE *produces* a verified code/algorithm
object and never ships one the frozen verifier hasn't passed. **Two genuinely different value props — keep them
SEPARATE and label which one any result is:**
- **(a) SYNTH-VERIFY (reliable, the armor++ floor):** synthesize code to a spec, gate it on **hidden + property +
  differential** tests. Never ship unverified code. This is solid and buildable — the FETCH-KNOWN analogue.
- **(b) The CAPABILITY BET (open, likely-hard):** does **verifier-gated iterate/search beat equal-compute
  best-of-k** on **non-memorized** tasks with rich feedback? This is the untested v5 lever the infra-gate
  demanded. It may return an **honest negative** (it did at toy scale). Build the contamination-free harness to
  finally test it — and report the negative plainly if that's the result.

**IS NOT:**
- **NOT "the model writes code" — armor already does that.** CODEFORGE's offense is **synthesize/search until the
  frozen verifier passes on problems a single shot cannot reliably solve** (superoptimization, algorithm
  discovery, hard synthesis), measured against an **equal-compute best-of-k baseline.** If marginal-Q over
  best-of-k is ~0, say so — that's the honest negative, not a failure to hide.
- **NOT a contamination laundromat.** A passed test on a memorized LeetCode/HumanEval problem proves **nothing**.
  Every benchmark task must be **non-memorized** (freshly generated, mutated, or held-out) or the result is void.
- **NOT gameable.** The generator must **never see the held-out tests.** Hard-coding outputs to visible tests is
  the reward-hack to design against (hidden tests + property-based + adversarial inputs + differential vs a
  reference).
- **NOT smarter than the model.** Like every weapon: it raises *verified throughput*, not the model's ceiling.

## 2. THE THREE MODES (map to the κ-router; each has an EXACT verifier)
| mode | analogue | what it produces | the FROZEN exact verifier (κ=1) |
|---|---|---|---|
| **SYNTH-VERIFY** | armor++ / FETCH-KNOWN | code meeting a spec | hidden unit tests **+ property-based tests (Hypothesis)** **+ differential test vs a reference oracle** — generator never sees them |
| **SUPEROPT** | SEARCH-OPEN | a faster/smaller implementation of a correct function | **frozen correctness gate (differential vs the original on adversarial inputs) + a measured benchmark harness** — "faster AND still correct" is a non-gameable structural win, like a bigger cap |
| **ALGO-DISCOVER** | construction engine | a combinatorial algorithm object: **sorting network**, **matrix-mult scheme**, small fast routine | an **exact mathematical certificate** — sorting network via the **0/1 principle** (check all 2ⁿ binary inputs sort); matrix-mult scheme via **symbolic identity** (the bilinear tensor equals the target exactly) |

**ALGO-DISCOVER is the cleanest non-contaminated offense** (mirrors the cap-set weapon exactly): KNOWN target →
reproduce the optimal object (e.g. the optimal 16-input sorting network, or Strassen's 7-mult 2×2 scheme) and
machine-verify it = a labeled **reproduction**; OPEN target → search for a smaller one, frozen-verifier-gated,
cross-model-audited — **honest negative expected** (these are hard human records; never claim a record without a
machine-certified object strictly beating prior art + an independent audit).

## 3. THE KEY ENGINEERING PROBLEM — kill contamination & gaming (this is the whole game)
1. **Non-memorized tasks.** For the capability bet, do NOT use raw HumanEval/MBPP/LeetCode. Generate tasks via:
   **(i) mutation** (take a base spec, perturb constraints/types/edge-rules so the memorized answer fails),
   **(ii) compositional novelty** (combine 2–3 primitives into a spec unlikely to be verbatim in training),
   **(iii) SUPEROPT/ALGO-DISCOVER** which are inherently non-memorizable (the search finds a *specific* object).
2. **Hidden + adversarial verification.** The generator sees the spec + a few *example* tests; the **frozen
   verifier holds the hidden tests, property tests, and adversarial/fuzzed inputs.** A solution counts only if it
   passes the held-out set. Differential-test against an independent reference oracle where one exists.
3. **The gate must be able to FAIL** (the project's non-waivable rule, see `socius/selftest_all.py`): each
   verifier must pass a known-good solution, **catch a known-broken one**, AND reject a **gaming attempt**
   (hard-coded-to-visible-tests) — prove the verifier isn't fooled.
4. **Equal-compute A/B.** The capability claim is non-circular ONLY as: verifier-gated iterate/search **vs
   best-of-k at matched token/compute budget**, on the non-memorized set, ≥2 task families, feedback isolated as
   the active ingredient. This is the protocol the repair-probe used — reuse it.

## 4. TO-DOs / STEPS (box order)
1. **PLAN:** `weapons/codeforge/SPEC.md` — the three modes, the κ=1 verifiers, the contamination/gaming defenses,
   the router (`codeforge_router.py`: which mode fires, and when a task is κ=0 "design/architecture judgment" →
   armor not weapon). **GROUND** the load-bearing facts by FETCH (don't assert): the **0/1 principle** for sorting
   networks; the **optimal comparator counts** for small sorting networks (n≤16, Knuth/known); that **Strassen =
   7 mults for 2×2** and **AlphaTensor** found verified schemes by gated search (Fawzi et al., Nature 2022);
   Hypothesis for property tests. Cite each with a fetched source.
2. **BUILD the frozen verifiers FIRST** (the gate before the weapon): `sortnet_verify.py` (0/1 principle, exact),
   `matmul_verify.py` (symbolic bilinear identity, exact), `synth_verify.py` (hidden+property+differential
   harness with a gaming-rejection self-test), `superopt_verify.py` (frozen correctness + benchmark). Then
   `selftest_all.py` — every verifier passes-good / catches-broken / rejects-gaming. **Gate must go green.**
3. **BUILD the weapon loop** (generalize `FRONTIER_ENGINE_WORKFLOW`): propose → build → **frozen-gate** → (survivor)
   cross-model audit. Machine-checkable → **execute ($0), never vote.**
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` BEFORE running): (i) **reproduce** the
   optimal n=8 or n=16 sorting network and machine-verify via 0/1 principle (labeled reproduction); (ii)
   **reproduce Strassen's 7-mult 2×2** scheme and verify by symbolic identity; (iii) a **SUPEROPT** win — take a
   naive correct function, search a faster correct variant, show the benchmark delta with the frozen correctness
   gate intact.
5. **THE CAPABILITY A/B (the open bet):** pre-register and run verifier-gated iterate **vs equal-compute
   best-of-k** on the **non-memorized** set, ≥2 families, feedback isolated. **Report the honest result** — a
   negative (no marginal Q over best-of-k) is a valid, publishable outcome; do NOT manufacture a pass.
6. **VERIFY INDEPENDENTLY:** a cross-model audit (Sonnet/Haiku ≠ the Opus generator; **never Opus-audits-Opus**;
   Fable inactive) that (a) re-derives the certificates with its own code, (b) tries to GAME the gate, (c)
   red-teams the contamination defense (can it find a memorized task that leaked in?). Fix what's caught.
7. **REGISTER:** add **CODEFORGE** to `Next/BOX_V5.md` (new Weapon + router branch) and `Expanding_Frontiers/
   HELMET/registry.json` (it becomes the `CS_ENG` department's `draws`). Honest `EVOLUTION_LOG` entry: **a weapon
   ADDED = capability EXPANSION, NOT a ≥10% promotion** (no shared arena) — UNLESS the capability A/B in step 5
   clears ≥10% non-circularly over best-of-k on non-memorized tasks, in which case **that** would be the first
   real capability promotion — flag it loudly and let the audit decide. Update `WEAPONS_BACKLOG.md` STATUS ✅.

## 5. HONESTY RAILS (non-waivable, specific to CODEFORGE)
- **A passed test on a memorized task proves nothing** — every reported result names whether the task is
  non-memorized and how that was ensured.
- **Reproduction is labeled reproduction** (optimal sorting net / Strassen = known objects, source+date).
  **Never claim an algorithm-discovery record** without a machine-certified object strictly beating prior art +
  an independent cross-model audit. **Never claim to solve an open problem.**
- **The gate that can't fail is not a gate** — ship no verifier without its passes-good / catches-broken /
  rejects-gaming self-test.
- **κ=0 stays armor:** "design this architecture / is this code *good*" (taste, maintainability, strategy) has no
  exact verifier → ground + abstain, do NOT pretend the weapon certifies it.
- **Equal-compute or it's not an A/B:** any "iterate beats one-shot" claim is void without the matched-budget
  best-of-k baseline.

## 6. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/codeforge/` — `SPEC.md`, `GROUNDING.md` (fetched sources), the frozen `*_verify.py`
+ `selftest_all.py` gate, `codeforge_router.py`, `demo_*/` (committed predictions + verified objects), the
capability-A/B under `…/codeforge/ab/` (prereg + runner + `RESULT.md`), `AUDIT.md` (cross-model red-team),
`README.md` (what it is + honest ceiling). Registration in `Next/BOX_V5.md` + `HELMET/registry.json` + honest
`EVOLUTION_LOG` entry; `WEAPONS_BACKLOG.md` STATUS updated.

## 7. STAFF THE TEAM (v4 ladder; Fable INACTIVE → its slots on Opus, flag low confidence)
- **Proposer / synthesizer** = code tier (any model writes code — it's the ceiling task); **the frozen verifier,
  not the model, is the gate.**
- **Library** = cheap model: fetch the 0/1-principle, optimal sorting-net counts, Strassen/AlphaTensor facts.
- **Verifier-builder** = code tier; the gate is pure machine.
- **Auditor** = a model ≠ the generator (Sonnet/Haiku; never Opus-audits-Opus while Fable is down) — re-derives
  certificates, tries to game the gate, red-teams contamination.

## 8. THE ONE-LINE TEST OF SUCCESS
**"CODEFORGE produces only frozen-verifier-passed code/algorithm objects; it reproduces known optimal objects
(sorting nets, Strassen) and machine-verifies them; on non-memorized tasks it either beats equal-compute
best-of-k by a pre-registered margin (→ a real capability result, audit-confirmed) or reports an honest negative
— and it never ships an unverified line, never claims a record without an audited certificate, and routes
κ=0 'is this code good' judgments to armor."** Sharp verifier, honest offense, no theater.
