/-
AB preamble — FRESH, non-memorized recursive functions (custom names + framings,
so the exact lemma statements are not verbatim in any training corpus). The PROVER
is given ONLY this preamble + a single lemma STATEMENT (never the reference proof).
Pure Lean 4 core (no mathlib) so the test runs on a bare kernel.
-/

-- ps_f1 n = sum of the first n odd numbers (= n*n), freshly framed
def ps_f1 : Nat → Nat
  | 0 => 0
  | (n + 1) => ps_f1 n + (2 * n + 1)

-- ps_g n = 3n, by a fresh recurrence
def ps_g : Nat → Nat
  | 0 => 0
  | (n + 1) => ps_g n + 3

-- ps_t n = triangular number 0+1+...+n
def ps_t : Nat → Nat
  | 0 => 0
  | (n + 1) => ps_t n + (n + 1)

-- ps_d n = number of ordered pairs (i,j), i<j, in {0..n} = n*(n-1)/2 framing via recurrence
def ps_d : Nat → Nat
  | 0 => 0
  | (n + 1) => ps_d n + n
