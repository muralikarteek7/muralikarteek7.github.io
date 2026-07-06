# ENCLOSE — SPEC (the certified-numerics weapon)

*Built 2026-06-20 (Phase 2, backlog #10). The one clearly-distinct new weapon that survived the
weapon-gap analysis. Sibling of SYMBOLICA (NAT_SCI), complementary not a replacement.*

## 0. One-line definition
ENCLOSE returns a **guaranteed enclosure `[a,b]` provably containing** the true value of a numeric
quantity, verified by a **containment PROOF** — interval arithmetic with outward (directed) rounding
(Moore's inclusion property) and the Krawczyk existence-uniqueness test — and either **ACCEPTs** a
claimed enclosure it can independently prove, **REJECTs** one it proves false (claim disjoint from the
rigorous enclosure), or **ABSTAINs** when the claim is tighter than independently provable / malformed.

## 1. Why it is distinct from SYMBOLICA (the load-bearing reason it exists)
SYMBOLICA certifies a closed form by **multi-method AGREEMENT** (symbolic + mpmath + scipy/series concur).
Agreement is **corroboration**: a shared blind spot can fool every method (SYMBOLICA's own audit caught a
branch-cut case where all legs agreed and were wrong). ENCLOSE's verifier is a **containment PROOF**: under
the inclusion property, the natural interval extension of `f` over a box is a *guaranteed outer bound* of
`f`'s true range, so the computed interval **provably** contains the answer (INTLAB's guarantee: "any result
is proved to be true under any circumstances, in particular covering rounding errors"). **Agreement is
evidence; containment is proof.** They are complementary — SYMBOLICA keeps the symbolic/algebraic surface;
ENCLOSE adds certified numeric bounds, including for quantities with **no elementary closed form** (e.g.
`∫₀¹ e^(−x²) dx`, an erf value) where SYMBOLICA's symbolic leg has nothing to agree on.

## 2. κ-profile
- **κ = 1** for the COMPUTED quantity under correct directed rounding. The gate's ACCEPT is structural:
  `ACCEPT ⟺ E ⊆ claim`, and `E` provably contains the truth ⟹ `truth ∈ claim`. A false enclosure cannot be
  accepted unless the recompute primitive is unsound.
- **κ = 0 boundary (MODELING):** ENCLOSE certifies the integral of *this* integrand over *this* domain / the
  root of *this* f in *this* box. It does NOT certify that the integrand/f is the right model of the user's
  real-world problem. That step is κ=0 and out of scope.
- **Honest residual on κ=1:** the proof is only as sound as **mpmath.iv's rounding implementation** (trusted,
  widely used, NOT formally verified). Named, not hidden.

## 3. Infrastructure decision (settled by MACHINE probe, not assertion — 2026-06-20)
- `mpmath.iv` basic interval arithmetic (`+ − × ÷`, `sqrt/exp/log`, `pi`) is **genuinely outward-rounded** and
  brackets known constants — probed and confirmed. **No new dependency** (the gap-analysis "needs python-flint"
  claim was contradicted: python-flint absent, mpmath.iv present and sufficient).
- `mpmath.iv.quad` **EXISTS but is BROKEN** (raises empty `ValueError`) → verified quadrature is built **on iv
  arithmetic** (interval rectangle rule), not delegated to it.
- Because mpmath.iv rounds in **software** (arbitrary precision), the C/hardware `-ffast-math degrades κ` caveat
  from the original ENCLOSE plan (which assumed an INTLAB/Arb hardware-float backend) **does not apply** — the
  rounding is deterministic. This is an honest *strength* of the mpmath.iv choice, at the cost of speed.

## 4. The three problem kinds (the surface — MODERATE, not broad)
| kind | recompute (the gate's independent E) | claim | ACCEPT iff |
|---|---|---|---|
| `enclosure` | a 0-arg callable → `iv.mpf` enclosure of Q (e.g. `iv.sqrt(2)`) | `{lo,hi}` | E ⊆ [lo,hi] |
| `integral` | `verified_integral(f,a,b,N)` — interval rectangle rule, outer bound | `{lo,hi}` | E ⊆ [lo,hi] |
| `root_unique` | `krawczyk_operator(f,df,lo,hi)` | `{lo,hi,unique}` | K(X) ⊂ int(X) |

For containment kinds: `claim ∩ E = ∅` → **REJECT** (truth provably outside); overlap-but-`claim ⊉ E` →
**ABSTAIN** (tighter than provable). For `root_unique`: K(X) ⊄ int(X) → **REJECT** (uniqueness not proven —
NOT a proof of no-root); f'(X) ∋ 0 / malformed → **ABSTAIN**.

## 5. The gate is built FIRST and can FAIL (`selftest_all.py`, non-waivable)
The gate-of-the-gate proves the gate: ACCEPTs true/provable enclosures + Krawczyk-unique roots; **REJECTs
false (disjoint) enclosures + false certs**; ABSTAINs on too-tight + malformed (lo>hi, NaN, f'∋0, unknown
kind, missing bounds); and a **soundness invariant** — every ACCEPT's rigorous enclosure brackets an
INDEPENDENT high-precision reference (mpmath.mp, computed a different way than the iv recompute). A verifier
that cannot fail is not a verifier.

**A real bug the gate-first discipline already caught + fixed:** the gate originally REPORTED its enclosure by
rounding endpoints to nearest, which could print an interval narrower than the truth (√2's lower endpoint
rounds *up* past √2) — a soundness-of-reporting hole. Fixed with `_outward_report` (lower endpoint rounded
down, upper up) so the printed `[lo,hi]` is a guaranteed superset. (The verdict *logic* always used exact mpf
endpoints and was sound; only the human-readable report was lossy.)

## 6. Honest ceiling (state every run)
- A containment proof proves containment under directed rounding; it is **not** a claim the answer is
  "interesting" or that the model is right (κ=0).
- The rectangle-rule quadrature is **rigorous but LOOSE** (width O(h)); ENCLOSE will **ABSTAIN** on a true
  claim tighter than its enclosure rather than certify beyond what it proves (case 3 of the demo). Tightening
  needs more subintervals or a higher-order verified rule (Taylor-model / verified Simpson) — future work.
- Surface is moderate: iv-evaluable integrands, Krawczyk roots of differentiable scalar f, recomputable
  constants/expressions. Stiff ODE enclosures, multivariate Krawczyk, and singular integrands are NOT in v0.
- A weapon ADDED = capability **EXPANSION**, not a ≥10% promotion. The ratchet stays **OPEN at v3**.

## 7. Deliverables map
`enclose_gate.py` (primitives + the gate), `selftest_all.py` (gate-of-the-gate, exits non-zero on any fail),
`demos/` (`PREDICTION.md` committed first, `run_demo.py`, `RESULTS.md` incl. an honest prediction-miss),
`GROUNDING.md` (fetched sources: Moore/Hickey inclusion theorem, Zgliczyński Krawczyk Thm 2, Tucker/Lorenz,
INTLAB, mpmath.iv), `SPEC.md` (this), `AUDIT.md` (cross-model Sonnet red-team — false-accept hunt).
