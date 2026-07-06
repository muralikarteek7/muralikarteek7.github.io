# SYMBOLICA — agreement-gated symbolic-exact numerics (v5 weapon #4)
*One-page spec. Home: `Expanding_Frontiers/weapons/symbolica/`. Promotes registry **W7**. Registered in
`Next/BOX_V5.md`. Department: NAT_SCI (exact-computation facility).*

## What it is (and is not)
SYMBOLICA is the v5 weapon for the **closed-form / tight-bound computation** problem class. It produces
**exact** closed-form integrals, infinite sums, limits, ODE solutions, special values and identities —
where the verifier is **two-or-more INDEPENDENT methods agreeing**, never one CAS's self-report. It is
the high-κ (≈0.9) "exactness at near-zero cost where sampling would only give error bars" weapon.

**The certificate is the AGREEMENT, not the engine output.** A single sympy answer is a **CLAIM**;
sympy `integrate`/`simplify` are heuristic (no completeness guarantee, partial Risch — see
`GROUNDING.md §A`) and can be wrong. The result counts only when independent families agree.

**IS NOT:**
- ❌ "sympy said so" — one engine = a claim. The result is the cross-method agreement.
- ❌ **kernel-grade** like PROOFSMITH. `simplify(lhs-rhs)==0` is strong but **not a trusted proof
  kernel** — even the strongest label, *"symbolically proven (simplify→0)"*, carries a **"not
  kernel-grade"** disclaimer. "Proven" ≠ "verified to D digits" — the two words are never swapped.
- ❌ safe just because two engines agree — agreement of two **same-family** methods is a
  **shared-blind-spot RISK** (a shared library bug), recorded as such; load-bearing results add a
  methodologically-**different** 3rd check (quadrature vs series vs symbolic).
- ❌ exact when it isn't — non-convergent sums, domain-restricted forms, branch cuts are **detected
  and flagged**, never papered over. No closed form ⇒ **numeric WITH error bars**, never a fake exact.

## The independent method FAMILIES (chosen so a shared bug is unlikely to fool all)
- **SYMBOLIC** — sympy `integrate` / `simplify` / `summation` (heuristic; one answer = a claim).
- **NUMERIC-AP** — mpmath arbitrary-precision eval + `mp.quad` (tanh-sinh) / `mp.nsum`, driven via
  `lambdify(...,'mpmath')` so the special-function *implementations* are mpmath's, not sympy's.
- **NUMERIC-DP / SERIES** — scipy QUADPACK (Gauss-Kronrod, double precision) and/or sympy `series` —
  a **different algorithm family** ⇒ the diversified 3rd check. (DP methods get a 12-digit floor,
  honestly — double precision can't deliver 30; a wrong value disagrees at digit ~0 regardless.)

## The four modes (map to the κ-router; agreement is the frozen verifier, κ≈0.9)
| mode | analogue | produces | frozen verifier |
|---|---|---|---|
| **CLOSED-FORM** | FETCH/armor++ | definite integral / ODE in closed form | sympy.integrate **vs** mpmath.quad **vs** scipy.quad agree to D digits (≥2 indep families) |
| **IDENTITY-PROVE** | PROOFSMITH-lite | an equality certified | `simplify(lhs-rhs)→0` (strong label) **AND** K-point mpmath agreement; series→0 = diversified 3rd |
| **SERIES** | construction-lite | an infinite sum's closed form | **CONVERGENCE checked FIRST** (sympy `is_convergent` + numeric partial sums), then mpmath.nsum + sympy.summation agree |
| **SPECIAL-VALUE** | FETCH-KNOWN | a known value (ζ(2)=π²/6, √π) | **REPRODUCE** vs a fetched reference + cross-method numeric — labeled reproduction |

κ=0 (what a result *means* physically / which model to use) → **ARMOR** (ground + abstain). No closed
form → **NUMERIC-FALLBACK** (high-precision value + explicit error bars). Router: `symbolica_router.py`.

## The agreement GATE (`symbolica_gate.py`) — built FIRST, the whole game
Frozen functions: `verify_identity`, `verify_definite_integral`, `verify_convergence`,
`verify_series_closed_form`, `verify_special_value`. Each returns a verdict + an **honest label** +
the methods that agreed + digits + points. Key rules enforced:
1. **Two-method floor** — ≥2 independent methods must agree to a committed digit count before CERTIFIED.
2. **Domain / branch-cut catch** — multi-point sampling across the FULL domain; a point where one side
   is real-defined and the other is complex/undefined is a **DISAGREEMENT, not a skip** (the
   shared-blind-spot trap, fixed during build — without it the branch-cut case `log(x²)=2log(x)` was
   wrongly certified). A form valid only on a sub-domain is REJECTED globally, CERTIFIED on its domain.
3. **Convergence before closed form** — a series not certified convergent gets **no** closed form.
4. **Honest verdict tiers** — `CERTIFIED` (≥2 families) vs `CERTIFIED-SINGLE-FAMILY` (one family, sympy
   gave no closed form — numeric-strong, NOT the ≥2 standard; added after the cross-model audit) vs
   `REJECTED` vs `REPRODUCED`/`MISMATCH`.

**Gate self-tests (non-waivable, `selftest_all.py`):** (a) ACCEPT a correct closed form, (b) REJECT one
off by a constant/factor, (c) REJECT a domain-restricted form sold as global (+ branch-cut `log(x²)`),
(d) REJECT a non-convergent sum with a fake closed form, (+ ACCEPT Basel, REJECT wrong Basel, downgrade
single-family). **All pass on real sympy/mpmath/scipy** or no output is trusted.

## Killer demo (committed predictions → run → judged): `demo_agreement/`
5 frozen predictions in `PREDICTION.md` BEFORE running: (1) ∫₀^∞e^(−x²)=√π/2 triple-agreement;
(2) Basel ζ(2)=π²/6 reproduction; (3) sin(3x) identity symbolic-collapse; (4) REJECT √π (off ×2);
(5) REJECT √(x²)=x global / CERTIFY on x>0. **Result: 10/10 confirmed by the machine judge.**

## Honesty rails (non-waivable, specific to SYMBOLICA)
A single-engine answer is a **claim**, not a result (every value ships its agreement: methods/digits/
points). **Agreement is a RISK, not proof** — load-bearing ⇒ a methodologically-different 3rd check.
**"Proven" (unconditional symbolic collapse, still not kernel-grade) ≠ "verified to D digits"** —
never upgrade the wording. **Flag domain / convergence / branch-cut.** **No closed form ⇒ numeric WITH
error bars.** The gate without its reject self-tests does not ship.

## Honest ceiling (every run)
SYMBOLICA delivers **exactness by independent agreement** at near-zero cost — deterministic compute, the
"execute, don't guess" rung. Its new value is the **exact answer + the multi-method certificate**, NOT a
model-quality delta. It is **empirically very strong but NOT kernel-proven** (PROOFSMITH is the kernel
weapon). It reproduces/verifies/certifies reliably; it does not invent the closed form that doesn't exist.
