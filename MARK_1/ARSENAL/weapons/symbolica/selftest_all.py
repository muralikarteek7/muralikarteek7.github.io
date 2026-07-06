#!/usr/bin/env python3
"""SYMBOLICA frozen-gate — run EVERY adversarial self-test. Exits 0 only if the
agreement gate ACCEPTS correct closed forms AND CATCHES wrong / domain-restricted /
non-convergent ones, and the router routes correctly.

Doctrine: "A gate that can't fail is not a gate." If this exits non-zero, NO
SYMBOLICA result is trustworthy.
"""
import sys
import symbolica_gate, symbolica_router


def _regression_crucible_rearrange():
    """FROZEN CRUCIBLE regression (metamorphic KILL, 2026-06-20).

    A rearranged true identity left an O(machine-eps) cancellation residue
    (~1e-51 at dps=50) instead of an exact 0.0; _agree's absolute-tolerance floor
    only fired at scale==0 EXACTLY, so scale became the residue, rel=diff/scale
    collapsed to ~1, and the point was WRONGLY rejected -> the gate FLIPPED its
    verdict under the meaning-preserving rearrange transform (lhs==rhs vs lhs-rhs==0).

    FIX: fire the absolute floor whenever the larger magnitude is itself at the
    machine-noise level. This freezes BOTH halves of the metamorphic pair as
    CERTIFY, AND re-freezes that genuinely-FALSE identities STILL REJECT (the
    soundness risk of loosening the tolerance — the abs floor must never accept a
    real disagreement)."""
    vi = symbolica_gate.verify_identity

    # (1) BOTH halves of the flipped metamorphic pair must CERTIFY now.
    r_base = vi('sin(x)**2 + cos(x)**2', '1', ['x'], (-3, 3))
    assert r_base["verdict"] == "CERTIFIED", r_base
    r_rearr = vi('sin(x)**2 + cos(x)**2 - 1', '0', ['x'], (-3, 3))
    assert r_rearr["verdict"] == "CERTIFIED", r_rearr  # the previously-killing exhibit

    # (2) SOUNDNESS — the loosened tolerance must NOT start accepting wrong forms.
    #     Every genuinely-FALSE identity must STILL be REJECTED.
    for lhs, rhs, dom in [
        ('-x', '0', (1, 4)),          # off by a sign/everything; was named in the rail
        ('sin(x)', 'cos(x)', (-3, 3)),
        ('x + 1', 'x', (-3, 3)),
        ('2*x', 'x', (-3, 3)),
        # extra: a REAL disagreement at small (but above-noise) scale must NOT be
        # swallowed by the absolute floor.
        ('2*x', '3*x', (0.0001, 0.001)),
    ]:
        rf = vi(lhs, rhs, ['x'], dom)
        assert rf["verdict"] == "REJECTED", \
            "FALSE-ACCEPT HOLE: (%s)==(%s) on %s -> %s" % (lhs, rhs, dom, rf)

    print("symbolica_gate regression (CRUCIBLE rearrange KILL): PASS")
    print("  rearranged true identity (sin^2+cos^2-1 == 0) CERTIFIES (eps-residue no longer vetoes)")
    print("  AND all genuinely-FALSE identities STILL REJECT (abs floor opened no new hole)")


CHECKS = [
    ("AGREEMENT-GATE (accept-correct / reject-constant / reject-domain / reject-divergent / branch-cut)",
     symbolica_gate._selftest),
    ("REGRESSION      (CRUCIBLE rearrange KILL: eps-residue false-reject; FALSE still reject)",
     _regression_crucible_rearrange),
    ("ROUTER         (mode routing + numeric-fallback + armor + ceiling)",
     symbolica_router._selftest),
]

if __name__ == "__main__":
    print("=" * 78)
    print("SYMBOLICA frozen agreement-gate — adversarial self-tests")
    print("=" * 78)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}\n    *** SELF-TEST FAILED (gate broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  {name}\n    *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    print("=" * 78)
    if failures:
        print(f"GATE: {failures} self-test(s) failed — DO NOT TRUST any SYMBOLICA output.")
        sys.exit(1)
    print("GATE: agreement gate accepts correct forms AND catches wrong / domain-restricted / "
          "non-convergent ones; router routes correctly. OK.")
