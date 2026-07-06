# ENCLOSE — the certified-numerics weapon (containment PROOF)

**Built 2026-06-20** (Phase 2, backlog #10). NAT_SCI dept, sibling of SYMBOLICA — complementary, not a
replacement. The one clearly-distinct new weapon that survived the weapon-gap analysis.

## What it does
Returns a **guaranteed enclosure `[a,b]` provably containing** the true value of a numeric quantity, and
verifies a claimed enclosure by a **containment proof** — interval arithmetic with outward (directed) rounding
(Moore's inclusion property) + the Krawczyk existence-uniqueness test. The gate **never trusts the claimed
answer**: it recomputes its own rigorous enclosure `E` and adjudicates.

| verdict | when | meaning |
|---|---|---|
| **ACCEPT** | `E ⊆ claim` | truth ∈ E ⊆ claim → the enclosure is certified (κ=1) |
| **REJECT** | `claim ∩ E = ∅`, or Krawczyk `K(X) ⊄ int(X)` | claim provably false / uniqueness not proven (κ=1 determination) |
| **ABSTAIN** | claim tighter than provable, or malformed / footgun / singular | undetermined (κ=0) — never a silent pass |

## Why it's distinct from SYMBOLICA (the reason it exists)
SYMBOLICA certifies by **multi-method AGREEMENT** (corroboration — a shared blind spot can fool every method).
ENCLOSE's verifier is a **containment PROOF**: the natural interval extension of `f` over a box is a
*guaranteed outer bound* of its true range, so the result provably contains the answer — including for
quantities with **no elementary closed form** (e.g. `∫₀¹ e^(−x²) dx`, an erf value). **Agreement is evidence;
containment is proof.**

## Run it
```
cd MARK_1/ARSENAL/weapons/enclose
python3 selftest_all.py        # gate-of-the-gate — ACCEPT true / REJECT false / ABSTAIN unprovable+malformed
python3 demos/run_demo.py      # killer demo (predictions committed in demos/PREDICTION.md first)
```

## Honest ceiling (read this)
- **κ=1 under directed rounding** for the COMPUTED quantity. Because `mpmath.iv` rounds in **software**, the
  `-ffast-math` hardware caveat does NOT apply — but the proof rests on **mpmath.iv's rounding correctness**
  (trusted, widely used, NOT formally verified). That residual is named, not hidden.
- **κ=0 modeling boundary:** certifies the integral of *this* integrand / the root of *this* f — NOT that the
  model is the right one for your real problem.
- **Loose by design:** the rectangle-rule quadrature is rigorous but wide; ENCLOSE **ABSTAINs** on a true claim
  tighter than its own enclosure rather than certify beyond what it proves. Tightening (Taylor-model / verified
  Simpson) is future work.
- **Surface = moderate:** iv-evaluable integrands, Krawczyk roots of differentiable scalar f, recomputable
  constants. Singular integrands, stiff-ODE enclosures, and multivariate Krawczyk are NOT in v0 (ABSTAINed).
- A weapon ADDED = capability **EXPANSION**, not a ≥10% promotion. **Ratchet stays OPEN at v3.**

## Files
`enclose_gate.py` (interval primitives + Krawczyk + the gate), `selftest_all.py` (gate-of-the-gate), `demos/`
(`PREDICTION.md`, `run_demo.py`, `RESULTS.md` incl. an honest prediction-miss), `GROUNDING.md` (fetched
sources), `SPEC.md`, `AUDIT.md` (cross-model Sonnet red-team — verdict SOUND, no false-accept).
