# SYMBOLICA — GROUNDING (fetched sources + infra check)
*Load-bearing facts are FETCHED or MACHINE-CHECKED here, not asserted from memory. Box rule:
ground, don't assert.*

## Infra reality check (run 2026-06-20, this machine)
```
sympy  1.14.0
mpmath 1.3.0   (ships with sympy; arbitrary precision + mp.quad / mp.nsum)
scipy  1.13.1  (QUADPACK adaptive Gauss-Kronrod — the diversified DOUBLE-precision family)
numpy  2.0.2
```
All four present — no `pip install` needed. The three independent method FAMILIES the gate
relies on are all available: SYMBOLIC (sympy), NUMERIC-AP (mpmath, arbitrary precision),
NUMERIC-DP / SERIES (scipy QUADPACK + sympy.series — a different algorithm family).

## §A — sympy `integrate` / `simplify` are HEURISTIC (the design premise)
**Fetched:** sympy integrals docs (docs.sympy.org/latest/modules/integrals/integrals.html), 2026-06-20.
- *"Algorithms are tried in order until one produces an answer."* — outcome depends on which
  heuristic fires first; **no completeness guarantee**.
- The **Risch algorithm** implementation *"only supports a small subset of the full algorithm"*
  (part of the transcendental exp/log case); `risch_integrate` accepts only purely transcendental
  exp/log functions.
- When it cannot integrate, sympy **returns an unevaluated `Integral`** rather than erroring — the
  gate must detect `.has(Integral)` (it does) and fall back, never treat a non-result as 0.

**Why this matters:** this is exactly why **a single CAS answer is a CLAIM, not a result**. sympy
can return a wrong/partial/unsimplified antiderivative or fail to collapse a true zero. SYMBOLICA's
certificate is therefore **independent-method AGREEMENT**, not `integrate`'s say-so. (Machine-checked
corollary: in the demo, `integrate(exp(-x**2),(x,0,oo))` is cross-checked against mpmath.quad AND
scipy.quad — the agreement, not sympy, is the judge.)

## §B — multi-point high-precision numeric agreement is strong evidence of an identity
- **Polynomial / rational case:** Schwartz–Zippel — a nonzero polynomial of degree d over a field
  agrees with 0 at a random point with probability ≤ d/|S|. K independent random points drive the
  false-accept probability to (d/|S|)^K. (Standard; the basis of polynomial identity testing.)
- **Transcendental case:** no finite-sample theorem makes it a *proof*, but two genuinely different
  closed forms that are NOT equal as functions will differ on a set of full measure — so agreement
  to 30 digits at 20 independent points is overwhelming empirical evidence (and the gate *labels it
  as such* — "verified to D digits", never "proven"). The honest gap from proof is stated everywhere.
- **The trap we DON'T fall into:** a *near-coincidence* (e.g. exp(π√163) ≈ 262537412640768744) is NOT
  a function identity — it agrees at a single point, not across a domain. The gate's multi-point /
  reference-digit floor REJECTS it (audit-confirmed: MISMATCH at the 30-digit floor).

## §C — known closed forms used in the demo (reproductions, labeled)
| object | closed form | independent reference cross-check |
|---|---|---|
| Gaussian integral ∫₀^∞ e^(−x²)dx | √π/2 ≈ 0.8862269254527580… | mpmath.quad + scipy QUADPACK (both independent of sympy.integrate) |
| Basel problem Σ_{n≥1} 1/n² | ζ(2) = π²/6 ≈ 1.6449340668… | mpmath.zeta(2) (independent special-fn impl) + mpmath.nsum + sympy.summation |
| triple-angle | sin(3x)=3sin(x)−4sin³(x) | sympy.simplify→0 (unconditional) + 20-pt mpmath + series→0 |

Basel: Euler (1735), ζ(2)=π²/6 — a *known* result. SYMBOLICA **reproduces** it (labeled
reproduction via `verify_special_value`, cross-checked against mpmath's independent `zeta(2)`),
it does NOT claim it as an original find. (The Gaussian value √π/2 and the triple-angle identity
are likewise standard.)

## §D — honest gap from a proof kernel (stated, not hidden)
`sympy.simplify(lhs-rhs)==0` is strong but **NOT a trusted proof kernel** (that is PROOFSMITH's Lean
gate, κ=1). simplify can (rarely) fail to collapse a true zero, or mis-handle a branch cut. So even
SYMBOLICA's strongest label — "symbolically proven (simplify→0)" — carries the explicit "not
kernel-grade" disclaimer in code and docs. Exact **by agreement**, honest about the gap from proof.

## Independent verification of this weapon
- `selftest_all.py` — the agreement gate's own accept/reject self-tests (machine).
- `demo_agreement/` — 10/10 committed predictions confirmed by the gate (machine).
- `AUDIT.md` — a cross-model (Sonnet ≠ the Opus generator) red-team that re-evaluated every result
  with its OWN independent numeric code and attacked the gate. One real defect (SERIES single-family
  verdict) was caught and FIXED before ship.
