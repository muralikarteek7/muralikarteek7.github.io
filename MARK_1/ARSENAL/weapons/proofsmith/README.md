# PROOFSMITH — the kernel-gated formal-proof weapon (v5 weapon #4)

**What it is.** PROOFSMITH produces **machine-checked formal proofs**. It formalizes and proves
theorems/lemmas where a **proof-assistant kernel is the only judge** — extending the Mathematics &
TCS department from "construct an object" to "**prove a statement**." It is a **κ=1 weapon** with the
**sharpest cheap verifier that exists**: the **Lean 4 kernel** re-checks a fully-elaborated proof
term against a tiny trusted core (the de Bruijn criterion), and PROOFSMITH ships **nothing the kernel
hasn't accepted with a clean `#print axioms`.**

**Infra (machine-verified, 2026-06-20):** Lean 4.31.0 + `elan`/`lake` installed and working; z3 4.16
as the decidable-fragment fallback. The full proof assistant is live — not just the SMT slice.

## The 4-check kernel gate (`proof_gate.py`) — the whole game
A kernel alone is not enough: a proof assistant lets you cheat three ways the kernel does **not**
flag as errors (`lean` exits 0 on a `sorry` proof and on a bogus-axiom proof). So the gate enforces:
1. **kernel accepts** the proof term · 2. **no `sorry`/`admit`** (via `#print axioms` → `sorryAx`,
plus a token scan) · 3. **axiom allow-list** (`#print axioms` shows only committed-allowed axioms) ·
4. **statement matches** a committed reference (kernel-level `example : <ref> := <thm>`).
Plus a pre-check 0 (audit-added): refuse elaboration-time IO commands (`#eval` …).
**Self-tests (`selftest_all.py`, non-waivable):** ACCEPT a good proof; REJECT a sorry-proof, a
bogus-axiom proof, a wrong-statement proof, and a `#eval` bundle; SMT slice accepts/rejects. All green.

## Two value props (kept separate, labeled)
- **(a) FORMALIZE-VERIFY** (reliable floor): formalize a KNOWN theorem + kernel-check it → a **labeled
  reproduction**. `demo_formalize_verify/` reproduces 3 core-Lean theorems (and_comm; every nat
  even-or-odd; Gauss summation) — **7/7 committed predictions confirmed**, with the gate rejecting
  sorry/bogus-axiom/wrong-statement versions and z3 corroborating the propositional one.
  `demo_mathlib_classics/` reproduces **Euclid's infinitude of primes** via mathlib
  (`Nat.exists_infinite_primes`), kernel-checked, clean axioms, sorry-version rejected — **3/3**.
- **(b) The CAPABILITY BET** (open): does kernel-feedback proof-search beat equal-compute best-of-k on
  non-memorized lemmas? `ab/` ran it (Haiku prover, 4 fresh lemmas). **Honest result: CLEAN NEGATIVE
  — one-shot 1/4 = best-of-3 1/4 = repair 1/4, repair − best-of-3 = 0pp.** A first pass produced a
  false +25pp from answer-key leakage + orchestrator hints; **the box caught it** (contamination
  awareness + kernel measurement), and the clean re-run killed it. Consistent with the season's owned
  repair-lever negatives, now extended to the rich-feedback formal-proof domain.

## What it IS NOT (honest framing)
- **NOT** "the model writes a proof in English" — that is unverified prose (armor), not a weapon.
- **NOT** a `sorry`/axiom laundromat — a proof depending on `sorry` or an unlisted axiom is a
  **FAILURE, not a result**. Every proof ships its `#print axioms`.
- **NOT** a wrong-statement trick — check 4 verifies the proof proves the committed formal statement.
- **NOT** an open-problem solver — **never claim to prove an open conjecture**; reproduce known
  theorems and exhibit the kernel-checked term, or report none.
- **Kernel-checked ≠ correct English theorem.** Whether a formal statement *means* its English claim
  is a **κ<1 autoformalization judgment** → cross-model reviewed, not certified by the kernel.

## Verifier scope
- **Lean 4 kernel (primary, κ=1):** all of formalizable mathematics.
- **z3 SMT slice (`smt_gate.py`, secondary, κ=1 on a DECIDABLE fragment ONLY):** propositional + QF/
  linear arithmetic — a decision procedure, not a general proof assistant. Labeled as such.

## Independent audit
`AUDIT.md`: a Sonnet auditor (≠ the Opus generator, 65 tool calls) re-ran every check itself, tried to
sneak `@sorryAx`/`opaque`/macro/`native_decide`/transitive-axiom cheats past the gate (**all caught by
`#print axioms`**), confirmed the demo statements are faithful, and re-tallied the A/B. Verdict:
**SOUND on proof correctness; A/B honest.** One minor finding (`#eval` IO side-channel) — **fixed**
(pre-check 0 + regression self-test).

## Honest ceiling
PROOFSMITH raises **verified-proof throughput** — it reproduces/verifies/extends reliably and invents
the load-bearing new proof idea rarely (same ceiling as the construction engine). **A weapon ADDED is
a capability EXPANSION, NOT a ≥10% promotion** (no shared arena; the A/B was a clean negative). The
≥10% CAPABILITY ratchet stays **OPEN at v3**.

## Files
`SPEC.md` · `GROUNDING.md` (fetched facts + machine infra check) · `proof_gate.py` + `smt_gate.py` +
`selftest_all.py` · `proofsmith_router.py` · `demo_formalize_verify/` · `demo_mathlib_classics/` ·
`ab/` (PREREG + clean runner + RESULT + quarantined contaminated run) · `AUDIT.md`.
Run: `export PATH="$HOME/.elan/bin:$PATH" && python3 selftest_all.py`.
