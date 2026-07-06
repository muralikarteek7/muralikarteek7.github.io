import Mathlib.Data.Nat.Prime.Infinite

-- Reproduction (Euclid, ~300 BC): there are infinitely many primes.
-- For every n there is a prime p >= n. mathlib: Nat.exists_infinite_primes.
theorem infinitude_of_primes : ∀ n : Nat, ∃ p, n ≤ p ∧ Nat.Prime p :=
  Nat.exists_infinite_primes

#print axioms infinitude_of_primes
