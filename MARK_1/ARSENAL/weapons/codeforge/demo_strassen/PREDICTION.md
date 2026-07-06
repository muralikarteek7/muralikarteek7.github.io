# PREDICTION — STRASSEN demo (committed BEFORE running)
*Written 2026-06-20, before `run_demo.py` was executed. Frozen forecast; compare to RESULT.json.*

This demo exercises ALGO-DISCOVER on matrix-multiplication schemes, where the frozen verifier is the
**exact non-commutative symbolic identity** (`matmul_verify.py`: the bilinear tensor must equal the
matmul tensor exactly).

| # | claim | committed prediction | why |
|---|---|---|---|
| S1 | **Reproduce** Strassen's 1969 7-multiplication 2×2 scheme verifies as a VALID bilinear scheme | **YES (valid)** | the symbolic identity holds; this is a 50-year-old proven algorithm |
| S2 | its multiplication count | **7** (vs naive 8) → `beats_naive = true` | Strassen's defining property |
| S3 | rank label the verifier assigns | **MATCHES_KNOWN_RANK** (labeled reproduction) | 7 == KNOWN_RANK[(2,2,2)] (optimal, Winograd 1971); honesty rail: reproduction, not discovery |
| S4 | the naive 8-mult scheme (control) | **valid, num_mults = 8, beats_naive = false** | sanity that the verifier passes the textbook truth too |
| S5 | a BROKEN scheme (flip one Strassen W coefficient) | **caught: valid=False, mismatched C entry reported** | the gate must be able to fail |
| S6 | a GAMING scheme (drop a product; tuned to pass a few NUMERIC matrices) | **caught: valid=False by the symbolic identity** | numeric sampling is gameable; the symbolic identity is not |

**Falsifiers:** Strassen verifying INVALID (verifier bug); the broken/gaming schemes passing; any valid
scheme reported with num_mults BELOW the proven rank bound 7 (`beats_optimal_IMPOSSIBLE` → bug).

**Honesty commitment:** Strassen = a **labeled reproduction** of a known optimal object (source: Strassen,
Numer. Math. 13, 1969; optimality Winograd 1971 — see GROUNDING.md). No record, no open-problem claim.
The recursion-safe non-commutative certificate is what AlphaTensor-style search would gate candidates on.
