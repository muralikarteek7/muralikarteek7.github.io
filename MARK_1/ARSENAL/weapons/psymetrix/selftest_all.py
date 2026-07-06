#!/usr/bin/env python3
"""PSYMETRIX frozen-verifier gate — run EVERY sub-weapon's adversarial self-test.

Doctrine: "A verifier that can't fail is not a verifier." Each kappa>0 check is
tested on a known-good input (must PASS) AND a known-broken input (must be CAUGHT).
This is the single gate: it exits 0 only if all verifiers behave correctly on both.
If this exits non-zero, NO PSYMETRIX number is trustworthy.
"""
import sys
import forensics_verify, psychometrics_verify, psymetrix_router

CHECKS = [
    ("P-FORENSICS  (GRIM/GRIMMER/SPRITE/TIVA/p-curve/Benford)", forensics_verify._selftest),
    ("P-PSYCHO     (reliability/dim/DIF/meta/power/items)     ", psychometrics_verify._selftest),
    ("ROUTER       (kappa-routing + ceiling)                  ", psymetrix_router._selftest),
]
try:                                          # P-REPRO/P-MULTIVERSE need statsmodels
    import repro_multiverse_verify
    CHECKS.append(
        ("P-REPRO/MV   (dual-path reproduction + spec curve)      ", repro_multiverse_verify._selftest))
except Exception as _re:
    print(f"  P-REPRO/MV   *** SKIPPED — {type(_re).__name__}: install statsmodels ***")
try:                                          # P-MODEL needs semopy/factor_analyzer/girth
    import model_verify
    CHECKS.append(
        ("P-MODEL      (CFA/SEM/EFA/omega/IRT-2PL/Yen-Q3)         ", model_verify._selftest))
    _MODEL_OK = True
except Exception as _e:                       # honest: if packages absent, say so, don't hide
    _MODEL_OK = False
    _MODEL_ERR = _e

if __name__ == "__main__":
    print("=" * 74)
    print("PSYMETRIX frozen-verifier gate — adversarial self-tests")
    print("=" * 74)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}  *** SELF-TEST FAILED (verifier broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  {name}  *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    if not _MODEL_OK:
        print(f"  P-MODEL      *** SKIPPED — packages absent ({type(_MODEL_ERR).__name__}); "
              "install semopy/factor_analyzer/girth to enable full IRT/CFA/SEM ***")
    print("=" * 74)
    if failures:
        print(f"GATE: {failures} verifier(s) failed — DO NOT TRUST any PSYMETRIX output.")
        sys.exit(1)
    print("GATE: all frozen verifiers pass good inputs AND catch broken inputs. OK."
          + ("" if _MODEL_OK else "  (P-MODEL skipped — see above)"))
