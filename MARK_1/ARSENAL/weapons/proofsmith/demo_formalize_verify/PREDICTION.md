# DEMO — FORMALIZE-VERIFY: committed predictions (written BEFORE running the gate)

*Box discipline: predictions are committed here BEFORE `run_demo.py` is executed. The gate's
machine output (`results.json`) is then compared to these. Generator = Opus 4.8; the JUDGE is the
Lean 4.31.0 kernel + `#print axioms` (a machine, not the model).*

## What this demo is
The **FORMALIZE-VERIFY** mode (the FETCH-KNOWN analogue): take theorems with **known** proofs,
formalize them in Lean 4, and **kernel-check** them. Every result is a **labeled reproduction**, not
a discovery. These three are all provable in **pure Lean 4 core (no mathlib)** so the demo is
self-contained and reproducible on a bare Lean install.

## The three target theorems (committed formal statements)
| id | English theorem | committed formal statement | known since |
|---|---|---|---|
| T1 | Conjunction commutes | `∀ (p q : Prop), p ∧ q → q ∧ p` | logic (trivial) |
| T2 | Every natural number is even or odd | `∀ (n : Nat), ∃ k, n = 2 * k ∨ n = 2 * k + 1` | antiquity |
| T3 | Gauss summation: `2·(0+1+…+n) = n·(n+1)` | `∀ (n : Nat), 2 * sumTo n = n * (n + 1)` | Gauss (classic) |

## Predictions (what I expect the gate to report)
1. **P1 — all three PASS all 4 checks** (kernel-accepts, no sorry/admit, axioms ⊆ allow-list,
   statement matches the committed reference). `accepted = true` overall.
2. **P2 — axiom footprints:** T1 uses **no axioms** (`does not depend on any axioms`); T2 and T3
   use only `{propext, Quot.sound}` (pulled in by the `omega`/`simp` tactic machinery) — all on the
   committed classical allow-list. **No `sorryAx`, no rogue axiom on any of the three.**
3. **P3 — the SORRY ATTACK is REJECTED.** A `sorry`-version of T3 (`gauss_sorry`) is fed to the
   gate; it must report `check2_no_sorry_admit = false` and surface `sorryAx`, `accepted = false`.
   *(A proof depending on `sorry` is a FAILURE, not a result.)*
4. **P4 — the BOGUS-AXIOM ATTACK is REJECTED.** A version of T3 proved from a custom
   `axiom gauss_cheat` is fed to the gate; it must report `check3_axiom_allowlist = false` and
   surface the extra axiom `gauss_cheat`, `accepted = false`.
5. **P5 — the WRONG-STATEMENT ATTACK is REJECTED.** T1's real proof is checked against a *different*
   committed reference (`∀ (p q : Prop), p ∧ q → p ∧ q ∧ p`-style mismatch — here we use the
   off-by-one reference `∀ (p q : Prop), p ∨ q → q ∧ p`); the gate must report
   `check4_statement_match = false`, `accepted = false`.
6. **P6 — cross-verifier corroboration (T1):** the propositional content of T1 (`(p ∧ q) → (q ∧ p)`)
   is *independently* confirmed VALID by the **z3 SMT slice** (a different verifier class than the
   Lean kernel) — its negation is UNSAT. This is the "trivial theorem works even in the z3 fallback"
   check.

## Honesty rails for this demo
- Every PASS is a **labeled reproduction of a known theorem**, NOT a discovery and NOT an
  open-problem solve. The formal statements are elementary and long-known.
- Kernel-checked means **the proof proves the committed FORMAL statement**. Whether each formal
  statement *means* its English theorem is an **autoformalization (κ<1) judgment** — checked by the
  cross-model audit (`AUDIT.md`), not asserted here. (These three are simple enough that the
  translation is uncontroversial, but the rail still holds.)
- The three ATTACK cases exist to show the gate **can FAIL** — a gate that only ever passes is theater.
