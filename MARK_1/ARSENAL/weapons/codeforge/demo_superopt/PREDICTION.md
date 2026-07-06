# PREDICTION — SUPEROPT demo (committed BEFORE running)
*Written 2026-06-20, before `run_demo.py` was executed. Frozen forecast; compare to RESULT.json.*

This demo exercises SUPEROPT: take a naive but correct function and a claimed-faster variant; the frozen
verifier (`superopt_verify.py`) gates **correctness by DIFFERENTIAL test** (κ=1, exact over the input
set) and **reports a measured benchmark** (speed is measured, not certified).

Task: `count_pairs_with_sum(a, target)` = number of index pairs i<j with a[i]+a[j]==target.
- **reference** (naive): the O(n²) double loop.
- **candidate** (fast): an O(n) single pass with a hash map (running counts).

| # | claim | committed prediction | why |
|---|---|---|---|
| U1 | the fast O(n) candidate is CORRECT vs the naive reference (differential over adversarial+fuzzed inputs) | **YES (correct)** | the hash-map count is mathematically equivalent; differential over many inputs confirms |
| U2 | measured speedup on a large input (n≈3000, several trials) | **≥ 2× (likely much more); verdict SUPEROPT_WIN** | O(n) vs O(n²); the gap grows with n. Conservative threshold to beat timing noise |
| U3 | a faster-but-WRONG impostor (off-by-one in the count) | **REJECTED_INCORRECT (win=False)** — timing never consulted | correctness gate fires first; faster-but-wrong is not a win |
| U4 | a GAMING impostor (hard-codes the exact benchmark inputs, wrong elsewhere) | **REJECTED_INCORRECT** by differential on fuzzed inputs | hard-coding the benchmark is caught by fuzzed differential inputs |

**Falsifiers:** the fast candidate failing differential (then it is correctly NOT shipped); the
wrong/gaming impostors passing (verifier too weak); a win declared on timing without correctness.

**Honesty commitment:** the speedup is a **measurement** (noisy, machine-dependent), explicitly NOT a
κ=1 certificate; only CORRECTNESS is certified. The win = correct AND measurably faster.
