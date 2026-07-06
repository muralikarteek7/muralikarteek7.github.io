/-
PROOFSMITH demo — FORMALIZE-VERIFY (labeled reproductions of KNOWN theorems).
Pure Lean 4 core (no mathlib). The Lean 4.31.0 kernel + `#print axioms` is the judge.
-/

-- T1: conjunction commutes (propositional, constructive — depends on NO axioms)
theorem and_comm_demo (p q : Prop) : p ∧ q → q ∧ p :=
  fun h => ⟨h.2, h.1⟩

-- T2: every natural number is even or odd (induction; linear; core Lean)
theorem even_or_odd_demo (n : Nat) : ∃ k, n = 2 * k ∨ n = 2 * k + 1 := by
  induction n with
  | zero => exact ⟨0, Or.inl rfl⟩
  | succ m ih =>
    obtain ⟨k, hk⟩ := ih
    cases hk with
    | inl h => exact ⟨k, Or.inr (by omega)⟩
    | inr h => exact ⟨k + 1, Or.inl (by omega)⟩

-- T3: Gauss summation, 2·(0+1+…+n) = n·(n+1), by induction.
def sumTo : Nat → Nat
  | 0 => 0
  | (n + 1) => sumTo n + (n + 1)

theorem gauss_demo (n : Nat) : 2 * sumTo n = n * (n + 1) := by
  induction n with
  | zero => rfl
  | succ k ih =>
    show 2 * (sumTo k + (k + 1)) = (k + 1) * (k + 1 + 1)
    simp only [Nat.mul_add, Nat.add_mul, Nat.mul_one, Nat.one_mul, Nat.mul_comm] at *
    omega
