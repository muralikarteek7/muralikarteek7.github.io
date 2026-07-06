# SYMBOLICA — exact-by-agreement symbolic numerics (University arsenal, weapon #4)

**What it is.** An agreement-gated engine that produces **exact** closed-form integrals, infinite
sums, limits, ODE solutions, special values and identities — where the judge is **≥2 INDEPENDENT
computations agreeing**, never a single CAS's self-report. Promotes registry **W7**
(`CLOSED_FORM_OR_TIGHT_BOUND_COMPUTATION`). Department: NAT_SCI exact-computation facility. κ≈0.9.

**The one rule.** *A single-engine answer is a CLAIM, not a result.* sympy `integrate`/`simplify` are
heuristic (no completeness guarantee — `GROUNDING.md §A`) and can be wrong. SYMBOLICA ships a value
only when independent method **families** agree: SYMBOLIC (sympy) · NUMERIC-AP (mpmath arbitrary
precision) · NUMERIC-DP/SERIES (scipy QUADPACK / sympy series — a different algorithm family). Two
**same-family** methods agreeing is a **shared-blind-spot RISK**, not safety — load-bearing results add
a methodologically-different 3rd check.

## Run it
```
cd MARK_1/ARSENAL/weapons/symbolica
python3 selftest_all.py                 # the frozen gate's accept/reject self-tests — MUST be green
cd demo_agreement && python3 run_demo.py # 10/10 committed predictions, judged by the gate
```

## Files
- `symbolica_gate.py` — the frozen agreement gate (built FIRST): `verify_identity`,
  `verify_definite_integral`, `verify_convergence`, `verify_series_closed_form`, `verify_special_value`.
- `selftest_all.py` — non-waivable adversarial self-tests (accept-correct / reject wrong-constant /
  reject domain-restricted / reject branch-cut / reject non-convergent / single-family downgrade).
- `symbolica_router.py` — routes a task to a mode or to ARMOR (no closed form → numeric + error bars;
  interpretation → ground+abstain).
- `SPEC.md` · `GROUNDING.md` (fetched sources + infra) · `AUDIT.md` (cross-model red-team) ·
  `demo_agreement/` (PREDICTION.md committed before running + results.json).

## Honest ceiling
Exactness **by independent agreement** at near-zero cost — deterministic compute, the "execute, don't
guess" rung. The new value is the **exact answer + the multi-method certificate**, NOT a model-quality
delta (a weapon ADDED = capability EXPANSION, **not** a ≥10% promotion). **Empirically very strong but
NOT kernel-proven** — even the strongest label, "symbolically proven (simplify→0)", is *not* a Lean
kernel term (PROOFSMITH is the kernel weapon); "proven" ≠ "verified to D digits" and the gate never
swaps the words. No closed form ⇒ numeric **with error bars**, never a faked exact.

Independently audited (Sonnet ≠ the Opus generator): SOUND-WITH-CAVEATS; one real defect (SERIES
single-family verdict) caught and FIXED before ship. See `AUDIT.md`.
