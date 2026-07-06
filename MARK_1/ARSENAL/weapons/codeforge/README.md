# CODEFORGE — code & algorithm discovery (v5 weapon, CS_ENG department)

**One line:** a verifier-gated engine that **produces machine-verified code/algorithm objects** —
synthesized routines, superoptimized implementations, and discovered combinatorial algorithms (sorting
networks, matrix-mult schemes) — where a **frozen, exact verifier is the only judge.** It never ships an
object the verifier hasn't passed.

## What it is (honest framing — two SEPARATE value props)
- **(a) SYNTH-VERIFY — the reliable floor:** synthesize code to a spec, gate on **hidden + property +
  differential** tests the generator never sees. *Never ship unverified code.* This is solid and demonstrated.
- **(b) the CAPABILITY BET — open, tested, NEGATIVE:** does verifier-gated *iterate* beat equal-compute
  *best-of-k*? Tested here (`ab/`): **+0pp** — the honest negative the season predicted (see below).

CODEFORGE raises **verified throughput**, not the model's ceiling. It is the Computer Science & Engineering
department of the HELMET (University Mode).

## Files
| file | role |
|---|---|
| `SPEC.md` | the binding contract: 3 modes, the κ=1 verifiers, contamination/gaming defenses, honesty rails |
| `GROUNDING.md` | fetched sources for every load-bearing fact (0/1 principle, sortnet optima, Strassen, AlphaTensor) |
| `sortnet_verify.py` | **κ=1** sorting-network verifier — the **0/1 principle** (sorts all 2ⁿ binary inputs ⇒ sorts everything) |
| `matmul_verify.py` | **κ=1** matrix-mult scheme verifier — exact **non-commutative symbolic identity** (recursion-safe) |
| `synth_verify.py` | **κ=1** (held-out) synthesis gate — hidden + property + differential; unpredictable fuzz seed |
| `superopt_verify.py` | **κ=1** on correctness (differential) + a **measured** benchmark (speed is measured, not certified) |
| `codeforge_router.py` | deterministic router — which mode fires; κ=0 "is this code good"/design → ARMOR |
| `selftest_all.py` | **the gate** — every verifier passes-good / catches-broken / **rejects-gaming**; exit 0 or nothing is trusted |
| `demo_sortnet/` · `demo_strassen/` · `demo_superopt/` | killer demos (committed `PREDICTION.md` → `run_demo.py` → `RESULT.json`) |
| `ab/` | the pre-registered capability A/B (`PREREG.md`, `harness.py`, `RESULT.md`) |
| `AUDIT.md` · `audit_independent/` | the independent cross-model (Sonnet) red-team + its fresh re-derivation code |

## Run it
```bash
cd MARK_1/ARSENAL/weapons/codeforge
python3 selftest_all.py                 # the gate — must exit 0 (passes-good/catches-broken/rejects-gaming)
python3 demo_sortnet/run_demo.py        # reproduce optimal n=8 net (19 comp) + discover n6/n7 from scratch
python3 demo_strassen/run_demo.py       # reproduce Strassen 7-mult, verify by symbolic identity
python3 demo_superopt/run_demo.py       # naive O(n^2) -> O(n), differential-gated, benchmarked
python3 codeforge_router.py selftest    # routing (incl. kappa=0 -> armor, CONFLICT RULE)
python3 ab/harness.py selftest          # A/B scoring is sound
```
Dependencies: Python 3 + **sympy** (for `matmul_verify`). No other external deps (the fuzzer is hand-rolled).

## The killer demos, in one breath (all machine-verified, predictions committed first)
- **SORTNET:** reproduced the **optimal n=8 sorting network (19 comparators)**, machine-verified via the
  0/1 principle (labeled **reproduction**); a verifier-gated greedy **search discovered** valid n=6 (13
  comparators) and n=7 (18) networks **from scratch** — honestly labeled *above* the known optimum, never below.
- **STRASSEN:** reproduced Strassen's **7-multiplication 2×2** scheme, verified as an **exact non-commutative
  symbolic identity** (`beats_naive`, MATCHES_KNOWN_RANK); a broken scheme and a numeric-only gaming scheme are caught.
- **SUPEROPT:** a naive O(n²) function vs an O(n) candidate → **correct (differential) + ~1820× faster**
  (SUPEROPT_WIN); a faster-but-WRONG impostor and a benchmark-hardcoding impostor are both REJECTED on correctness.

## The capability A/B (the open bet) — HONEST NEGATIVE
Verifier-gated **ITERATE vs equal-compute BEST-OF-K** (K=4, Haiku writer, 2 non-memorized families,
machine-scored by the frozen verifiers, self-reports ignored): **iterate − best-of-k = +0.0pp.** Where
one-shot succeeds, the arms saturate; the one in-band task (n7) is a **tie** — rich feedback engaged
(failed round 1 → fixed round 2) but **did not beat blind resampling at equal budget.** Feedback was never
the active ingredient (attempts were: iterate − one-shot = +16.7pp, all captured by best-of-k). This
reproduces the owned v5 repair-lever lesson in a fresh rich-feedback arena. **No promotion; the ≥10%
capability ratchet stays OPEN at v3.** The faithful at-scale test remains infra-gated (`Next/benchmarks/
V5_INFRA_UNLOCK_SPEC.md`). Detail: `ab/RESULT.md`.

## Honest ceiling (binding, stated every run)
- Ships **only** frozen-verifier-passed objects; **reproductions are labeled reproductions** (source+date).
- **Never** claims an algorithm-discovery record without a machine-certified object strictly beating prior
  art + an independent cross-model audit. **Never** claims to solve an open problem.
- κ=1 **relative to the verifier**: SORTNET/MATMUL are exact certificates; SYNTH/SUPEROPT are as strong as
  their held-out battery (whose strength = secrecy + size). κ=0 "is this code *good*/clean/well-designed" →
  **ARMOR** (ground + abstain); CODEFORGE does not pretend to certify taste.
- It raises **verified throughput**, not the model's capability ceiling.

## Status (honest)
A **new v5 WEAPON = a capability EXPANSION** (a task class the box could not do: *construct* a verified
code/algorithm object; armor only ever *checked* one). **NOT a ≥10% A/B promotion** — the capability A/B
returned **+0pp** (the honest negative), so the ≥10% CAPABILITY ratchet **stays OPEN at v3.** Built BOX-style;
independently audited by Sonnet (≠ the Opus generator) → **SOUND-WITH-CAVEATS**, two false-accept defects
caught and **fixed + re-gated green.** Registered in `Next/BOX_V5.md` (Weapon 6 + router Branch H) +
`HELMET/registry.json` (CS_ENG); `EVOLUTION_LOG.md` C40.
