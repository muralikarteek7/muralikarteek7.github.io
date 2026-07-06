# SYMBOLICA — cross-model audit (red-team ≠ the generator)
*Box rule: verify INDEPENDENTLY. Generator = Opus 4.8. Auditor = **Sonnet** (Fable inactive →
audit on Sonnet, never Opus-audits-Opus). The auditor wrote its OWN independent numeric code and
attacked the gate; it did not trust any self-report. Date: 2026-06-20.*

## Mandate given to the auditor
(a) Re-evaluate every shipped demo result with independent mpmath/scipy code written from scratch.
(b) Attack the gate: wrong-but-close closed forms, domain-restricted/branch-cut identities, a
non-convergent series with a finite closed form, and a near-coincidence (not a real identity).
(c) Police the exactness labels ("proven" vs "verified to D digits"; the scipy DP floor).
(d) Run `selftest_all.py` and the demo.

## What the auditor independently CONFIRMED (its own code)
- **All 3 demo math claims reproduced** at/beyond stated precision with fresh code:
  Gaussian ∫₀^∞e^(−x²)=√π/2 (mpmath+scipy, ≥50 / 16 digits), Basel Σ1/n²=π²/6 (mpmath.nsum +
  **scipy.special.zeta**, ≥50 digits), sin(3x) identity (max error 6.7e-51 over 50 random points).
- **Wrong-by-1e-9 and wrong-by-1e-13** integrals correctly REJECTED — mpmath holds the 30-digit line
  even where scipy's double-precision floor passes (combined gate rejects). Wrong **factor** caught at
  digit ~0.3.
- **Branch-cut / domain attacks all FAILED to fool the gate:** `atan(x)+atan(1/x)=π/2`,
  `acos(cos(x))=x`, `sqrt(x)·sqrt(x+1)=sqrt(x(x+1))`, `sqrt(x²)/x=1` — every one REJECTED with explicit
  disagreements; default seed samples balanced ±x so branch cuts are reliably hit.
- **Divergent series** `Σ 1/(n·log n)` REJECTED before any value check (convergence gate fires first).
- **Near-coincidence** exp(π√163) vs the integer 262537412640768744 → **MISMATCH** at the 30-digit
  floor (it is not a function identity, and the gate does not treat a single-point coincidence as one).
- **Label honesty:** "proven" appears ONLY for the symbolic-collapse case (sin 3x), always with the
  "not kernel-grade" disclaimer; scipy's 12-digit floor is disclosed per-method, never inflated to 30.
- `selftest_all.py` PASS; `run_demo.py` 10/10.

## DEFECT the auditor found → FIXED before ship
**Defect 1 (moderate, doctrine inconsistency).** In `verify_series_closed_form`, when sympy's
`summation` returns no closed form, only ONE family (mpmath.nsum) confirms the value, yet the verdict
was the bare `CERTIFIED` — overstating the module's own "≥2 independent methods" doctrine (the label was
honest — "single-family" — but the *verdict field* was not). The convergence partial-sums are the SAME
numeric-AP family as nsum, so a shared nsum bug could fool both.
**Fix (applied):** the SERIES verdict is now tiered — `CERTIFIED` only when ≥2 independent families
confirm the value (e.g. Basel: mpmath.nsum + sympy.summation); otherwise the explicit
**`CERTIFIED-SINGLE-FAMILY`** ("numeric-strong, does NOT meet the ≥2 floor"). A non-waivable self-test
now asserts a sympy-unclosable convergent series never returns bare `CERTIFIED`. Re-run after fix:
gate green, demo 10/10.

## Noted, not a shipped defect
- **Thin-margin near-coincidence:** exp(π√163) clears the 30-digit floor by only ~0.46 digits at 50 dps.
  Correct behavior at the configured precision; a reminder that the digit floor is a *committed
  threshold*, not infinite resolution. Working precision is committed (DPS=50, DIGITS=30).
- **Designed limit (disclosed):** a wrong value below the 30-digit floor (off by <1e-30) would pass —
  the floor is finite by construction. The gate certifies "verified to D digits", and says exactly D.

## Verdict (auditor's words)
**SOUND-WITH-CAVEATS** → the one real inconsistency (SERIES single-family verdict) is now FIXED.
Core claim holds: **exact by ≥2-independent-method agreement, honest labels, catches
wrong / domain-restricted / non-convergent claims.** Empirically very strong; not kernel-proven
(PROOFSMITH is the kernel weapon) — and the docs say so.
