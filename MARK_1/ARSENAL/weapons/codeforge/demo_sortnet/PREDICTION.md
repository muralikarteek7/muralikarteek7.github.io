# PREDICTION — SORTNET demo (committed BEFORE running)
*Written 2026-06-20, before `run_demo.py` was executed. Frozen forecast; compare to RESULT.json.*

This demo exercises ALGO-DISCOVER on sorting networks, where the frozen verifier is the **0/1
principle** (`sortnet_verify.py`: a network is valid iff it sorts all 2ⁿ binary inputs — exact).

| # | claim | committed prediction | why |
|---|---|---|---|
| P1 | **Reproduce** the optimal n=8 network (Batcher odd-even mergesort, generated programmatically) is a VALID sorting network | **YES (valid)** | 0/1 principle over all 256 binary inputs; Batcher is a correct construction |
| P2 | its comparator count | **19** | odd-even mergesort for n=8 = 19; this equals the proven optimum (Floyd–Knuth 1966) |
| P3 | optimality label the verifier assigns | **MATCHES_KNOWN_OPTIMUM** (labeled reproduction, NOT a discovery) | 19 == KNOWN_OPTIMAL_SIZE[8]; honesty rail forbids calling a known object a discovery |
| P4 | **Discovery:** a verifier-gated greedy search (0/1-eval as the signal) finds a VALID n=6 network from scratch | **YES (valid, 0 unsorted of 64)** | greedy-on-unsorted-count converges; every step machine-checked |
| P5 | discovered n=6 size vs known optimum (12) | **valid, size in [12, 20]; NEVER below 12** | greedy is rarely optimal but always valid; a size<12 valid network would flag a verifier BUG |
| P6 | discovery for n=7 also finds a VALID network | **YES (valid, 0 unsorted of 128); size in [16, 26]** | same mechanism; optimum is 16, greedy lands above |
| P7 | a deliberately BROKEN network (drop a comparator from Batcher-8) | **caught: valid=False, a failing binary input reported** | the gate must be able to fail |

**Falsifiers (what would prove the design wrong):** Batcher-8 verifying as INVALID (construction or
verifier bug); ANY valid network reported with size BELOW the proven optimum (verifier bug —
`beats_optimal_IMPOSSIBLE`); the broken network passing.

**Honesty commitment:** the n=8 result is a **labeled reproduction** of a known optimal object, not a
discovery. The greedy search demonstrates the verifier-gated DISCOVERY mechanism producing a
machine-certified object from scratch — it is NOT claimed to beat any record.
