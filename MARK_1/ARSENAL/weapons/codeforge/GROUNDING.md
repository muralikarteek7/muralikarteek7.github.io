# CODEFORGE — GROUNDING (fetched sources for every load-bearing fact)

*Box rule: a load-bearing fact gets a fetched source or a machine check, not memory. Below, each
fact carries a fetched URL AND (where possible) a note that CODEFORGE's own frozen verifier
machine-checks the actual object — which is stronger than the citation. Fetched 2026-06-20.*

---

## 1. The 0/1 principle (the SORTNET exact certificate)
**Fact:** *A comparator network sorts all inputs iff it sorts all 2ⁿ binary (0/1) inputs.* So a
network's correctness over every ordered set is decided by an EXHAUSTIVE sweep of just the 2ⁿ binary
vectors — not n! permutations. Knuth, *The Art of Computer Programming*, Vol. 3, §5.3.4.
- Fetched: MIT Press, *Introduction to Algorithms* ch. 27 "Sorting Networks" (states the 0–1 principle):
  https://mitp-content-server.mit.edu/books/content/sectbyfn?collid=books_pres_0&fn=Chapter+27.pdf&id=8030
- Fetched: Springer, "The 0/1-Principle": https://link.springer.com/chapter/10.1007/978-1-4614-1851-1_4
- Fetched: complexity of optimal sorting-network *verification* (Parberry): https://ianparberry.com/pubs/snverify.pdf
- **Machine check (stronger):** `sortnet_verify.py` runs the full 2ⁿ sweep from scratch on the returned
  comparator list. A network that sorts only a sampled subset is caught (selftest rejects-gaming).

## 2. Proven-optimal sorting-network SIZE for small n (the reproduction labels)
**Fact (comparator counts, proven optimal):** n=1..8 → **0, 1, 3, 5, 9, 12, 16, 19**; n=9 → **25**, n=10 → **29**.
n≤8 optimality proven by **Floyd & Knuth (1966)**; **n=9 (25) and n=10 (29)** proven optimal by
**Codish, Cruz-Filipe, Frank & Schneider-Kamp (2014)**, "Twenty-Five Comparators Is Optimal When Sorting Nine Inputs."
- Fetched: Codish et al. 2014 (arXiv 1405.5754): https://arxiv.org/pdf/1405.5754
- Fetched: "The Quest for Optimal Sorting Networks" (arXiv 1404.0948): https://arxiv.org/pdf/1404.0948
- Fetched (history of the n≤8 Floyd–Knuth proof, n=8→19): https://jix.one/proving-50-year-old-sorting-networks-optimal-part-1/
- **Use in CODEFORGE:** `KNOWN_OPTIMAL_SIZE` labels a valid network MATCHES_KNOWN_OPTIMUM (a reproduction),
  or flags BELOW_PROVEN_OPTIMUM → BUG (impossible, never a "win"). Optimality is a *label from the
  literature*, never claimed by the verifier itself.

## 3. Strassen 1969 — 7 multiplications for 2×2 (the MATMUL reproduction)
**Fact:** Strassen (1969) multiplies two 2×2 matrices with **7 scalar multiplications instead of 8**.
It is a **bilinear** algorithm (products are (linear form in A)·(linear form in B)); because it never
relies on commutativity of the entries, it applies **recursively to block matrices**, giving
O(n^log₂7) ≈ O(n^2.807). The rank **7 is optimal for 2×2** (Winograd 1971; Hopcroft & Kerr 1971).
- Fetched: "Strassen's 2×2 matrix multiplication algorithm: a conceptual perspective" (arXiv 1708.08083):
  https://arxiv.org/abs/1708.08083  (states 7 vs 8 mults, 18 additions, rank-7 optimal, recursive O(n^log₂7))
- Original: V. Strassen, "Gaussian Elimination is not Optimal," *Numer. Math.* 13 (1969) 354–356.
- **Machine check (stronger):** `matmul_verify.py` certifies the 7-product scheme as an EXACT
  NON-COMMUTATIVE symbolic identity (recursion-safe) — verified this session, R=7, beats_naive=true.

## 4. AlphaTensor (Fawzi et al., Nature 2022) — search-found AND machine-verified schemes
**Fact:** AlphaTensor (DeepMind) used reinforcement learning to **search** for matrix-multiplication
algorithms as **tensor decompositions**, and the discovered algorithms are **verified by checking the
factorization equals the matrix-mult tensor exactly** (an exact algebraic certificate — the same kind
CODEFORGE's MATMUL uses). It found e.g. a rank-47 scheme for 4×4 in 𝔽₂ and 14,236 nonequivalent
algorithms for 4×4. This is the canonical precedent for "verifier-gated SEARCH produces a
machine-verified algorithm object."
- Fetched: Fawzi, A., et al. "Discovering faster matrix multiplication algorithms with reinforcement
  learning." *Nature* 610, 47–53 (2022). https://www.nature.com/articles/s41586-022-05172-4
- Fetched: code + verification (Colab checks nonequivalence/correctness of the decompositions):
  https://github.com/google-deepmind/alphatensor
- **Use in CODEFORGE:** the ALGO-DISCOVER OPEN branch is the AlphaTensor pattern (propose structural
  family → search → frozen exact gate on every candidate). Honest ceiling: AlphaTensor had massive
  compute; CODEFORGE reproduces known schemes and expects an HONEST NEGATIVE on open records.

## 5. Property-based testing (the SYNTH-VERIFY property layer)
**Fact:** "Hypothesis" is the standard Python property-based testing library (generate many inputs,
assert a structural property holds) — the technique the kickoff names for the property layer.
- Reference: https://hypothesis.readthedocs.io/
- **Design choice (honest):** Hypothesis is NOT installed in this environment, and the box prefers
  deterministic/reproducible runs, so `synth_verify.py` HAND-ROLLS a deterministic LCG fuzzer instead
  of depending on Hypothesis. Same idea (fuzz N inputs, check a property), zero external dependency,
  byte-reproducible. The property is checked together with a DIFFERENTIAL test against a reference oracle.

## 6. 3×3 matrix multiplication (carried bound, not a demo target)
**Fact:** Laderman (1976) multiplies 3×3 with **23 multiplications**; the exact rank lower bound for 3×3
is still **open** (best known lower bound 19). So `matmul_verify.py` carries (3,3,3)→23 only as an
upper-bound label and would treat any open 3×3 search as Branch-C OPEN (honest negative expected).
- Fetched: "A New General-Purpose Method to Multiply 3×3 Matrices Using Only 23 Multiplications"
  (arXiv 1108.2830): https://arxiv.org/pdf/1108.2830

---

### What is grounded by FETCH vs by MACHINE (the honest split)
- **Fetched (literature labels):** which sizes/ranks are *optimal/records* (Floyd–Knuth, Codish,
  Winograd/Hopcroft–Kerr, Laderman); that AlphaTensor search-found verified schemes; that the 0/1
  principle is a theorem.
- **Machine-verified (this session, stronger than any citation):** that the specific objects CODEFORGE
  ships are valid — every sorting network via the exhaustive 0/1 sweep, every matmul scheme via the
  exact symbolic identity. The citation says "19 is optimal for n=8"; the machine says "THIS list sorts
  all 256 binary inputs." CODEFORGE only ever ships the machine-checked object, labeled with the fetched
  optimality status.
