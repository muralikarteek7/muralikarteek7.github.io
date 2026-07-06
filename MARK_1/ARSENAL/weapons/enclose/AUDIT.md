# ENCLOSE — cross-model adversarial AUDIT (2026-06-20)

**Auditor:** Sonnet 4.6 — an INDEPENDENT model, ≠ the Opus author (Fable 5 inactive → Sonnet is the
cross-model auditor; never Opus-audits-Opus). **Mission:** find a FALSE-ACCEPT (a claim the gate ACCEPTs
that does NOT contain the truth — the cardinal soundness failure). Method: write + RUN independent Python,
attack `verified_integral` soundness and Krawczyk false-uniqueness directly.

## Verdict: **SOUND** — no false-accept found after 17 attack categories.

Both `selftest_all.py` and `demos/run_demo.py` ran clean on the auditor's machine. The auditor independently
re-derived π, e−1, √2, ln2, sin(π/7), cos(π/5), and the erf integral at 200 dps and confirmed every ACCEPT's
enclosure brackets the true value and every REJECT excludes it.

### Attacks that FAILED to break it (selected)
- **Non-monotone integrands** (`sin(10x)`, `(x−0.5)²`): enclosures correctly wide, always contain the truth, tighten with N.
- **Singularity inside domain** (`1/(x−0.5)`, `1/(x(1−x))` on [0,1]): E = [−∞,+∞] → gate correctly **ABSTAINs** (no bogus finite enclosure).
- **Integrable singularity** (`1/√x` on [0,1]): E = [finite, +∞] → ABSTAIN. ENCLOSE *cannot* certify integrable-singular integrals — consistent with the SPEC ceiling, not a false-accept.
- **Krawczyk two roots / double root**: when two roots exist, `f'(X) ∋ 0` (Rolle) → the `0 in fpm` guard ABSTAINs. Never certifies uniqueness when it doesn't hold.
- **Krawczyk no root / boundary root**: REJECTs (strict-interior `<` check; mpmath `None` comparisons are falsy → conservative REJECT).
- **Low precision (dps 5–30), accumulation at N=100k**: every reduced-precision enclosure still *contains* π (wider, never spuriously tight).

### The structural reason false-accept is hard (auditor's argument, matches the SPEC)
`ACCEPT ⟺ E ⊆ claim`, and `E` provably contains the truth by Moore's inclusion property ⟹ `truth ∈ claim`.
The only path to a false-accept is the interval sum rounding **inward** (E too tight) or the inclusion
property failing — neither was observed; mpmath.iv accumulates outward rounding correctly.

## Residual risks the auditor named — and what I did about each

| # | residual | disposition |
|---|----------|-------------|
| 1 | **mpmath.iv rounding correctness** — the whole proof rests on it; not formally verified (no Coq/Isabelle). | **Named in SPEC §2 as the κ=1 residual.** Cannot be removed at the Python level. Accepted, disclosed. |
| 2 | **Footgun integrand** — a non-iv `f` (`math.exp`, `float(x.a)`) could break the inclusion property silently. | **FIXED** — added a runtime guard: the gate probes `f` on an interval input and ABSTAINs if it doesn't return an `iv.mpf`. Regression test `(c8)`. |
| 3 | **`kappa:1` on ABSTAIN** could be misread as claim-confidence. | **FIXED** — `kappa` now reflects verdict determinacy: 1 for ACCEPT/REJECT (proven), **0 for ABSTAIN** (undetermined). Regression tests `(c9)`. |
| 4 | **`_outward_report` loose at tiny magnitudes** (E≈[1e−300,2e−300] printed as [−1e−15,1e−15]). | **FIXED** — scale-relative pad; now prints `[~1e−300, ~2e−300]`. Still a guaranteed outer bound, now tight at every scale. |
| 16 | **"Lying callable"** for `kind='enclosure'` — a `value()` returning a non-rigorous interval → false ACCEPT. | **Documented** as the κ=0 caller/modeling boundary (gate certifies *containment of what value() returns*, not that value() is rigorous). Docstring strengthened. Not a gate soundness bug. |

## Honest bottom line
ENCLOSE's containment-proof gate is **sound within its named surface** (iv-evaluable integrands, Krawczyk
roots of differentiable scalar f, recomputable constants) and **conservatively ABSTAINs outside it** (singular
integrands, ill-conditioned boxes). It is a real κ=1 verifier under mpmath.iv's software directed rounding —
the one residual that cannot be discharged here. **A weapon ADDED = capability EXPANSION, NOT a ≥10%
promotion. Ratchet stays OPEN at v3.** Post-audit, all 4 actionable findings are fixed + frozen as regression
tests; selftest + demo re-run green.
