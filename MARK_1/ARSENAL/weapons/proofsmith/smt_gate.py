#!/usr/bin/env python3
"""PROOFSMITH — the SMT decidable-fragment verifier (kappa = 1 on a DECIDABLE slice).

This is the FALLBACK / second-opinion verifier the kickoff (§4) requires: if a full
proof assistant is unavailable, the sharpest verifier that still runs is an
SMT/SAT decision procedure for the DECIDABLE fragments. We have z3 installed, so
this slice is live regardless of Lean's status.

HONEST SCOPE (non-waivable, stated every run): z3 is a DECISION PROCEDURE for a
DECIDABLE fragment — propositional logic and quantifier-free / linear arithmetic.
It is NOT a general proof assistant and covers NOTHING of higher mathematics
(quantified number theory, real analysis, induction over inductive types, …). A
"valid" verdict here means "this formula is a tautology / valid in the theory",
proven by showing its NEGATION is UNSAT. We do not dress this propositional/QFLIA
checker as a full kernel — that mislabel is exactly the dishonesty the kickoff bans.

WHY IT IS STILL kappa=1 ON ITS SLICE: validity in these fragments is DECIDABLE and
the check re-checks the actual claim (negation UNSAT), is independent of the
producer, and a false "valid" is detectable (a counter-model would be returned).
This is the SAT/CP-object-finding analogue applied to logical validity.
"""
import sys

try:
    import z3
    _Z3 = True
except Exception:
    _Z3 = False


def z3_available():
    return _Z3


def check_valid(build_negation, timeout_ms=10000):
    """build_negation: a callable that returns a z3 BoolRef equal to NOT(claim).
    Returns a verdict: the claim is VALID iff its negation is UNSAT.

    A tautology/valid formula has an unsatisfiable negation. If the negation is
    SAT, z3 returns a counter-model => the claim is NOT valid (and we surface the
    model, so a false 'valid' cannot hide).
    """
    if not _Z3:
        raise RuntimeError("z3 not installed (pip install z3-solver)")
    s = z3.Solver()
    s.set("timeout", timeout_ms)
    s.add(build_negation())
    res = s.check()
    out = {"weapon": "PROOFSMITH-SMT", "kappa": 1, "scope": "DECIDABLE fragment "
           "(propositional / QF & linear arithmetic) ONLY — NOT a general proof assistant"}
    if res == z3.unsat:
        out.update({"valid": True, "verdict": "VALID (negation is UNSAT)", "countermodel": None})
    elif res == z3.sat:
        out.update({"valid": False, "verdict": "NOT VALID (counter-model exists)",
                    "countermodel": str(s.model())})
    else:
        out.update({"valid": None, "verdict": f"UNKNOWN ({res}) — timeout/incompleteness; ABSTAIN",
                    "countermodel": None})
    return out


# =============================== SELF-TESTS ================================= #
def _selftest():
    if not _Z3:
        raise RuntimeError("z3 not installed; cannot run the SMT-gate self-test.")

    # (a) ACCEPT a real propositional tautology: p OR NOT p (law of excluded middle)
    def lem_neg():
        p = z3.Bool("p")
        return z3.Not(z3.Or(p, z3.Not(p)))
    a = check_valid(lem_neg)
    assert a["valid"] is True, ("ACCEPT tautology failed", a)

    # (b) REJECT a non-tautology: p -> q  (false when p=true, q=false)
    def imp_neg():
        p, q = z3.Bool("p"), z3.Bool("q")
        return z3.Not(z3.Implies(p, q))
    b = check_valid(imp_neg)
    assert b["valid"] is False and b["countermodel"] is not None, ("REJECT non-taut failed", b)

    # (c) ACCEPT a QF-arithmetic validity: forall x, x + 0 = x
    def arith_ok():
        x = z3.Int("x")
        return z3.Not(x + 0 == x)
    c = check_valid(arith_ok)
    assert c["valid"] is True, ("ACCEPT arith identity failed", c)

    # (d) REJECT a false arithmetic claim: x + 1 = x
    def arith_bad():
        x = z3.Int("x")
        return z3.Not(x + 1 == x)
    d = check_valid(arith_bad)
    assert d["valid"] is False, ("REJECT false arith failed", d)

    print("smt_gate selftest: PASS")
    print("  (a) ACCEPT propositional tautology (LEM)      OK")
    print("  (b) REJECT non-tautology (counter-model)      OK")
    print("  (c) ACCEPT QF-arithmetic identity             OK")
    print("  (d) REJECT false arithmetic claim             OK")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: smt_gate.py selftest   (library: import check_valid)")
