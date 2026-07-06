# KICKOFF — build WEAPON #2: PROOFSMITH (formal proof) for the v5 box
*Paste everything below into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written
2026-06-20. PROOFSMITH is item #2 of `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` — the proof-assistant
kernel is the closest thing in existence to the cap-set verifier (an exact, independent certificate of truth).*

---

You are building **PROOFSMITH**, the box's next **WEAPON** (offense): a kernel-gated engine that **produces
machine-checked formal proofs** — it formalizes and proves theorems/lemmas where a **proof-assistant kernel is
the only judge.** It extends the **Mathematics & TCS** department from "construct an object" to "**prove a
statement**." Work BOX-style: plan → produce → **verify INDEPENDENTLY** (cross-model ≠ generator, or the kernel
itself) → ground → be honest; **no win without proof; never claim to prove an open problem.**

## 0. ORIENT — read first (in order)
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (the κ-router — PROOFSMITH is a κ=1 weapon; KNOWN theorem →
FETCH-KNOWN reproduction, OPEN conjecture → SEARCH-OPEN with an honest-negative expectation),
`Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` (item #2 = this), the two existing weapons as **templates**
(`Expanding_Frontiers/weapons/socius/` and `…/psymetrix/` — copy their shape: `SPEC.md`, a frozen gate, a
`selftest_all.py`, a router, a `demo_*/` with committed predictions, `AUDIT.md`),
`Expanding_Frontiers/FRONTIER_ENGINE_WORKFLOW.md` (the propose→gate→audit loop you generalize), and the sibling
`Expanding_Frontiers/weapons/CODEFORGE_WEAPON_KICKOFF.md` (same weapon-design pattern, one tier over).

**⚠ DO NOT RE-TREAD (read so you don't repeat the lesson):** the repair-lever negatives
(`Next/benchmarks/V5_INTERIM_VERDICT_2026-06-12.md`, `Next/benchmarks/v5_repair_probe/PROBE_LOG.md`). Iterate→
repair **saturated at toy scale** because authorable-reference problems are memorized classics. Formal proof has
a **rich, exact feedback signal** (kernel error messages) and **checkable contamination** (mutate/freshly-state
lemmas) — so it is one of the few honest places left to test "does kernel-feedback iteration beat best-of-k." It
may still return a negative; report it plainly.

## 1. THE HONEST FRAMING — what PROOFSMITH IS and IS NOT (do not skip)
**IS:** a κ=1 weapon with the **sharpest verifier that exists** — a proof-assistant **kernel (Lean 4 / Coq /
Isabelle)** accepts a proof term or rejects it, by the de Bruijn criterion (a tiny trusted core re-checks every
step). PROOFSMITH *produces* a kernel-checked proof object and ships nothing the kernel hasn't accepted. **Two
value props — keep them SEPARATE and labeled:**
- **(a) FORMALIZE-VERIFY (reliable floor):** take a theorem that already has a known proof, formalize it, and
  **kernel-check it** → a labeled **reproduction**. Solid, buildable, the FETCH-KNOWN analogue.
- **(b) The CAPABILITY BET (open):** does **kernel-feedback proof-search beat equal-compute best-of-k** on
  **non-memorized** lemmas? The untested repair lever, in its most favorable (rich-feedback) domain. Honest
  negative is a valid outcome.

**IS NOT:**
- **NOT "the model writes a proof in English" — that is armor (prose), not a weapon.** A weapon's proof is a
  **kernel-checked term**, nothing less. A natural-language "proof" is an unverified claim.
- **NOT a `sorry`/axiom laundromat (THE cardinal trap).** Proof assistants let you cheat: `sorry`/`admit` admits
  a goal unproven; adding a false or non-standard **axiom** closes anything. The gate MUST reject any proof that
  uses `sorry`, `admit`, or axioms beyond a committed allow-list — checked via `#print axioms` (Lean) / `Print
  Assumptions` (Coq). **A proof that depends on `sorry` is a FAILURE, not a result.** This is the proof analogue
  of CODEFORGE's "hard-coded to visible tests."
- **NOT a wrong-statement trick (the "prove `True`" trap).** You can kernel-check a proof of a *restatement* that
  isn't the theorem. The gate MUST verify the **formal statement matches a committed/grounded reference
  statement** — the autoformalization (English → formal) is a **κ<1 judgment slice** and needs an independent
  cross-model check, not blind trust.
- **NOT an open-problem solver.** **Never claim to prove an open conjecture.** Reproduce known theorems; the
  de-novo hard-proof leap is rare (same ceiling as the construction engine — verify/reproduce/extend reliably,
  invent the load-bearing idea rarely).
- **NOT smarter than the model.** It raises *verified-proof throughput*, not the model's ceiling.

## 2. THE THREE MODES (map to the κ-router; the kernel is the exact verifier)
| mode | analogue | what it produces | the FROZEN exact verifier (κ=1) |
|---|---|---|---|
| **FORMALIZE-VERIFY** | FETCH-KNOWN | a formalized + kernel-checked known theorem | the **kernel** accepts the term **+ no-`sorry`/no-extra-axiom check (`#print axioms`) + statement-matches-reference check** |
| **PROOF-SEARCH** | armor++ | a proof of a given formal statement (tactics/automation/hammer) | same kernel gate; counts only if it closes the goal with allowed axioms |
| **LEMMA-EXTEND** | SEARCH-OPEN | auxiliary lemmas / gap-filling in a known development | kernel gate per lemma; the de-novo proof of an OPEN conjecture is the rare frontier → **honest negative expected** |

**FORMALIZE-VERIFY is the cleanest first demo** (mirrors the cap-set FETCH-KNOWN exactly): pick theorems with
**known** formal proofs, reproduce them, kernel-check, label as reproduction. Save the open frontier for last and
expect a negative.

## 3. THE KEY ENGINEERING PROBLEM — the gate must catch every cheat (this is the whole game)
The "gate" wraps the kernel and enforces **four** checks; build it FIRST, with self-tests that prove it can FAIL:
1. **Compiles / kernel-accepts** — the proof term type-checks against the kernel.
2. **No `sorry` / no `admit`** — reject any proof containing them (string + AST check, and the axiom check below).
3. **Axiom allow-list** — `#print axioms <thm>` (Lean) must show only committed-allowed axioms (e.g.
   `propext`, `Classical.choice`, `Quot.sound` if you allow classical mathlib; **nothing else**). Any extra/false
   axiom ⇒ REJECT.
4. **Statement-matches-reference** — the formal statement is diff-checked against a committed reference statement
   (and the autoformalization is independently cross-model-reviewed). A proof of the *wrong* statement ⇒ REJECT.

**Gate self-tests (non-waivable, see `socius/selftest_all.py`):** the gate must (a) ACCEPT a known-good
kernel-checked proof, (b) **REJECT a `sorry`-proof**, (c) **REJECT a proof that adds a bogus axiom**, (d)
**REJECT a proof of a different statement**. A gate that passes all four is trustworthy; one that misses any is
the weapon's biggest risk.

## 4. INFRA REALITY CHECK — ground the toolchain BEFORE designing around it
Formal-proof weapons are **toolchain-gated**. Step 0 of the build is a machine check, not an assumption:
- **Try to install Lean 4 + mathlib** (or `elan`); confirm the kernel independently re-checks a proof and
  `#print axioms` works. If it installs → that's the engine.
- **If Lean/Coq is NOT installable in this environment** (honest negative on buildability), **fall back to a
  proof system that IS available and still kernel-exact:** an **SMT/SAT proof** for the decidable fragments —
  `z3` (pip-installable) emits **UNSAT cores / proofs** for propositional & quantifier-free arithmetic that an
  independent checker can re-verify; or a small Python-checkable natural-deduction kernel for a propositional
  fragment. State the κ honestly: SMT covers a **decidable slice**, not all of mathematics. **Do not pretend a
  full proof assistant is present if it isn't** — pick the sharpest verifier that actually runs, and label its
  scope. (This is the PSYMETRIX "install-or-armor" discipline applied to proof.)

## 5. TO-DOs / STEPS (box order)
1. **PLAN:** `weapons/proofsmith/SPEC.md` — the three modes, the 4-check kernel gate, the autoformalization κ<1
   caveat, the router (`proofsmith_router.py`: KNOWN theorem → FORMALIZE-VERIFY; given formal goal → PROOF-SEARCH;
   "prove this English claim" with no formal statement → autoformalize-then-prove, flag the translation risk;
   κ=0 "is this argument convincing" → armor). **GROUND by FETCH (don't assert):** that the Lean 4 kernel is a
   small trusted core re-checking proof terms (de Bruijn criterion); that `#print axioms` reveals axiom
   dependencies incl. `sorryAx`; that mathlib contains the theorems you'll reproduce (e.g. irrationality of √2,
   infinitude of primes); the z3 UNSAT-proof fallback if used. Cite each fetched source in `GROUNDING.md`.
2. **INFRA CHECK + BUILD THE GATE FIRST** (§4 + §3): install the toolchain (or the fallback), then build
   `proof_gate.*` with all 4 checks + `selftest_all.py` (accept-good / reject-sorry / reject-bogus-axiom /
   reject-wrong-statement). **Gate must go green before any proving.**
3. **BUILD the weapon loop** (generalize `FRONTIER_ENGINE_WORKFLOW`): propose proof/tactics → kernel-gate →
   (survivor) cross-model audit of the *statement* (does the formal stmt mean the English theorem?). Machine-
   checkable → **execute, never vote.**
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` BEFORE running): reproduce **2–3 known
   theorems** end-to-end (formal statement + kernel-checked proof + clean `#print axioms`), labeled reproductions.
   Pick a range: one trivial (a propositional tautology or a small arithmetic identity — works even in the z3
   fallback), one classic (√2 irrational / infinitude of primes if Lean is up). Show the gate REJECTING a
   `sorry`-version of one of them.
5. **THE CAPABILITY A/B (the open bet):** pre-register kernel-feedback proof-search **vs equal-compute
   best-of-k** on **non-memorized** lemmas (mutate/freshly-state so the proof isn't in mathlib verbatim), ≥2
   families, feedback (kernel errors) isolated as the active ingredient. **Report the honest result** — a
   negative is valid; do NOT manufacture a pass.
6. **VERIFY INDEPENDENTLY:** a cross-model audit (Sonnet/Haiku ≠ the Opus generator; **never Opus-audits-Opus**;
   Fable inactive) that (a) re-runs `#print axioms` itself on each shipped proof, (b) tries to sneak a `sorry`/
   bogus-axiom proof past the gate, (c) checks each formal statement actually means its English theorem
   (the autoformalization attack). Fix what's caught — and **expect the auditor to catch a statement-mismatch or
   an axiom leak; that is the highest-value find.**
7. **REGISTER:** add **PROOFSMITH** to `Next/BOX_V5.md` (new Weapon + router branch) and `Expanding_Frontiers/
   HELMET/registry.json` (MATH_TCS gains a "prove" draw alongside the construction engine). Honest
   `EVOLUTION_LOG` entry: **a weapon ADDED = capability EXPANSION, NOT a ≥10% promotion** — UNLESS the step-5 A/B
   clears ≥10% non-circularly over best-of-k on non-memorized lemmas (then flag it loudly; let the audit decide).
   Update `WEAPONS_BACKLOG.md` STATUS ✅. If the toolchain was un-installable, register the **honest negative on
   buildability** + the SMT-fallback scope instead of overstating coverage.

## 6. HONESTY RAILS (non-waivable, specific to PROOFSMITH)
- **A proof depending on `sorry`/`admit` or an unlisted axiom is a FAILURE, not a result** — always ship
  `#print axioms` output with every proof.
- **Kernel-checked ≠ correct theorem** — the formal statement must be shown to mean the intended claim
  (autoformalization is judgment; cross-model-check it). A proof of the wrong statement is worthless.
- **Reproduction is labeled reproduction** (mathlib/known source + date). **Never claim to prove an open
  conjecture** — exhibit the kernel-checked term or report you did not find one.
- **The gate that can't fail is not a gate** — ship no gate without its accept-good / reject-sorry /
  reject-bogus-axiom / reject-wrong-statement self-tests.
- **Honest scope on the verifier** — if you used the SMT fallback, say it covers a *decidable fragment*, not all
  mathematics. Don't dress a propositional checker as a full proof assistant.
- **κ=0 stays armor:** "is this informal argument convincing / is this the right proof strategy" (judgment) →
  ground + abstain, do NOT pretend the kernel certifies it.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/proofsmith/` — `SPEC.md`, `GROUNDING.md` (fetched sources + the infra-check result),
`proof_gate.*` + `selftest_all.py`, `proofsmith_router.py`, `demo_*/` (committed predictions + kernel-checked
proofs + `#print axioms` outputs), the capability-A/B under `…/proofsmith/ab/` (prereg + runner + `RESULT.md`),
`AUDIT.md` (cross-model red-team incl. the sorry/axiom/statement attacks), `README.md` (what it is + honest
ceiling + verifier scope). Registration in `Next/BOX_V5.md` + `HELMET/registry.json` + honest `EVOLUTION_LOG`
entry; `WEAPONS_BACKLOG.md` STATUS updated.

## 8. STAFF THE TEAM (v4 ladder; Fable INACTIVE → its slots on Opus, flag low confidence)
- **Prover / formalizer** = code tier writes Lean/Coq/SMT (it's a code-shaped task); **the kernel, not the model,
  is the gate.** (Note: proof *search* is hard reasoning — where Fable would help and is down; lean on the
  kernel's rich feedback to iterate, the model-agnostic move.)
- **Library** = cheap model: fetch the de-Bruijn/`#print axioms` facts + which theorems are in mathlib.
- **Gate-builder** = code tier; the gate is the kernel + the 4 checks, pure machine.
- **Auditor** = a model ≠ the generator (Sonnet/Haiku; never Opus-audits-Opus) — re-runs `#print axioms`, attacks
  the gate with sorry/axiom/wrong-statement, checks autoformalization fidelity.

## 9. THE ONE-LINE TEST OF SUCCESS
**"PROOFSMITH ships only kernel-checked proofs with a clean `#print axioms` (no `sorry`, no rogue axioms) and a
statement verified to mean its theorem; it reproduces known theorems labeled as reproductions; on non-memorized
lemmas it either beats equal-compute best-of-k by a pre-registered margin (→ a real capability result,
audit-confirmed) or reports an honest negative — it never claims to prove an open problem, and routes κ=0
'is this argument convincing' judgments to armor."** The sharpest verifier in the arsenal, kept honest.
