# PROOFSMITH — GROUNDING (fetched sources + the machine-verified infra check)

*Box rule: a load-bearing fact gets a fetched source or a machine check, not memory. The
strongest grounding for a proof weapon is **executing the kernel** — so the infra check below is
itself the primary evidence; the fetched sources corroborate it.*

## A. INFRA REALITY CHECK (machine-verified, 2026-06-20) — the load-bearing result

**Lean 4 INSTALLED and the kernel works.** Not the SMT-only fallback — the full proof-assistant
kernel is live.

| item | result | how verified |
|---|---|---|
| `elan` (Lean toolchain manager) | **4.2.3** installed via `elan-init.sh` | `elan --version` |
| Lean kernel | **4.31.0** (`leanprover/lean4:v4.31.0`) | `lean --version` |
| `lake` build tool | **5.0.0** | `lake --version` |
| z3 (SMT fallback / decidable slice) | **4.16.0** (`pip install z3-solver`) | `import z3` |

**Kernel behaviour the gate depends on (each machine-verified directly):**
1. A correct proof type-checks: `theorem t : 2 + 2 = 4 := rfl` → `'t' does not depend on any axioms`.
2. **`lean` exits 0 even on a `sorry` proof and on a bogus-axiom proof** (they are warnings / fiat,
   not errors). ⇒ **the gate must NOT trust the exit code; it must parse `#print axioms`.** This is
   the single most important infra fact and it is why CHECK 2/CHECK 3 exist.
3. `theorem c : 2 + 2 = 5 := by sorry` → `'c' depends on axioms: [sorryAx]` (+ "declaration uses
   `sorry`" warning). ⇒ sorry is detectable.
4. `axiom bogus : (2:Nat)+2=5; theorem c := bogus` → `'c' depends on axioms: [bogus]`. ⇒ a rogue
   axiom is detectable by name.
5. A type-incorrect proof → `error: Type mismatch`, **exit 1**. ⇒ genuine wrong proofs are rejected.
6. **Statement-match at kernel level:** `example : <ref> := <thm>` type-checks **iff** `<thm>`'s type
   is defeq to `<ref>`; a proof of a different statement yields `error: Type mismatch … expected to
   have type …`, exit 1. ⇒ CHECK 4 (statement match) is itself kernel-enforced, not a string diff.

The gate's four self-tests (`selftest_all.py`) exercise 1–6 on real Lean and pass.

## B. FETCHED SOURCES (corroborating the kernel facts)

1. **`#print axioms` tracks axiom dependencies, incl. quotient/choice/sorry.**
   *Theorem Proving in Lean 4*, "Axioms and Computation"
   (https://lean-lang.org/theorem_proving_in_lean4/axioms_and_computation.html, fetched 2026-06-20):
   > "If a theorem or definition makes use of `Quot.sound`, it will show up in the `#print axioms`
   > command." `#print axioms` "displays which axioms a theorem or definition depends on."

2. **The three standard classical axioms** (same source, fetched verbatim):
   - `propext {a b : Prop} : (a ↔ b) → a = b` — propositional extensionality.
   - `Quot.sound : r a b → Quot.mk r a = Quot.mk r b` — quotient soundness (also yields funext).
   - `Classical.choice` — choice (the third of the mathlib trio; standard "classical" stance).
   These three are the committed `CLASSICAL_AXIOMS` allow-list in `proof_gate.py`. `sorryAx` is
   NEVER allowed.

3. **The Lean kernel is a trusted core that independently checks proof terms.**
   Lean Reference Manual, *The Type System* (https://lean-lang.org/doc/reference/latest/, fetched
   2026-06-20): proof terms are "sufficient evidence of the truth of a theorem and are amenable to
   independent verification." (The infra check §A directly demonstrates this independent re-checking.)

4. **The de Bruijn criterion** (concept; attributed): a proof assistant satisfies it when the proofs
   it produces can be re-checked by a **small, simple program a skeptic could in principle verify by
   hand** — separating a large untrusted elaborator from a tiny trusted checker (Barendregt &
   Geuvers, "Proof-checking using dependent type systems"; popularized by Wiedijk). *Honest note:*
   the canonical PDF did not render through the fetch tool, so this is cited as the standard
   formulation of a well-known concept; the **load-bearing claim — that Lean's kernel does
   re-check the actual proof term — is machine-verified in §A, not taken on this citation.**

## C. Theorems reproduced in the demo (all KNOWN, all pre-mathlib-era classics)
- **Conjunction commutes** — propositional logic; trivial, also confirmed by z3.
- **Every natural number is even or odd** — antiquity; proved here by induction in core Lean.
- **Gauss summation** `2·(0+1+…+n) = n·(n+1)` — Gauss; proved here by induction in core Lean.

All three are formalized in **pure Lean 4 core (no mathlib)**, so the demo reproduces on a bare
Lean install. They are **labeled reproductions of known theorems**, not discoveries. (If the
mathlib build — attempted this session — completes, genuine library classics such as
`Nat.exists_infinite_primes` and `irrational_sqrt_two` become available as additional labeled
reproductions; see `demo_mathlib_classics/` if present.)

## D. Honest scope of each verifier
- **Lean kernel (primary, κ=1):** covers anything expressible + provable in Lean 4 / mathlib —
  effectively all of formalizable mathematics. The judge is the kernel; PROOFSMITH ships nothing it
  hasn't accepted with a clean `#print axioms`.
- **z3 SMT slice (secondary, κ=1 on a DECIDABLE fragment ONLY):** propositional logic + QF/linear
  arithmetic. A decision procedure, **not** a general proof assistant. Labeled as such every run.
