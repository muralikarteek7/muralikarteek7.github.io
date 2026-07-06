#!/usr/bin/env python3
"""CRUCIBLE probe — SYMBOLICA frozen agreement gate (multi-method cross-agreement:
SYMBOLIC[sympy] + NUMERIC-AP[mpmath] + NUMERIC-DP[scipy]/SERIES).

SCOPE / kappa=1 slice (stated up front, non-waivable):
  * The gate's kappa=1 CERTIFIED verdict is the AGREEMENT of >=2 INDEPENDENT method
    families (symbolic simplify->0, mpmath high-precision sampling, scipy/series 3rd
    family). That IS the gate. We probe the CERTIFIED/REJECTED boundary of:
        - verify_identity(lhs, rhs, syms, domain)   [IDENTITY-PROVE mode]
        - verify_definite_integral(integrand, var, a, b, claimed) [CLOSED-FORM mode]

  * NO INDEPENDENT ORACLE. Any third decision procedure we could build (re-derive the
    integral / re-check the identity) would re-use one of the gate's OWN legs (sympy,
    mpmath, or scipy) => CIRCULAR. The task therefore runs METAMORPHIC + ABSTAIN-CRASH
    ONLY (oracle=None). Transform meaning-preservation is CALLER-ASSERTED — residual
    risk, exactly as crucible_harness documents for oracle=None.

THE METAMORPHIC PRINCIPLE (meaning-preserving rewrites that must NOT flip the verdict):
  IDENTITY-PROVE: "is lhs == rhs as functions over the domain?" is invariant under —
    - SYMMETRY:        swap lhs<->rhs (a==b iff b==a)
    - ADD-CONSTANT:    lhs+C == rhs+C  iff  lhs==rhs  (add same C to both sides)
    - SCALE:           k*lhs == k*rhs  iff  lhs==rhs  (k != 0)
    - VAR-RENAME:      rename the free symbol x->y (the statement is the same identity)
  CLOSED-FORM: "is integral_a^b f == claimed?" is invariant under —
    - SCALE-BOTH:      integral of k*f over [a,b] == k*claimed  iff  integral f==claimed
    - NEGATE-BOTH:     integral of -f == -claimed
  Each transform is applied to BOTH sides so the mathematical TRUTH of the assertion is
  preserved; a sound agreement gate must return the SAME verdict on the transformed
  problem. A FLIP (CERTIFIED<->REJECTED) under any of these is a metamorphic KILL.

ABSTAIN/CRASH: malformed math (unparseable expr, undefined integrand, empty syms) must
  not yield a silent CERTIFIED. SAFE = {REJECT, ABSTAIN(=here REJECTED w/o agreement),
  ERROR}. The harness maps a raised exception to ERROR (safe). A KILL = garbage ->
  CERTIFIED.

The adapter IMPORTS AND CALLS the real symbolica_gate functions. It re-implements
NOTHING — the verdict comes entirely from the real gate's own engines.
"""
import sys
import json

# --- wire the REAL weapon gate (black-box import from the sibling weapon dir) -------
SYMBOLICA_DIR = "/Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/symbolica"
CRUCIBLE_DIR = "/Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/crucible"
sys.path.insert(0, SYMBOLICA_DIR)
sys.path.insert(0, CRUCIBLE_DIR)

import sympy as sp
import symbolica_gate as SG               # the REAL SYMBOLICA agreement gate
from crucible_harness import (
    GateAdapter, ACCEPT, REJECT, ABSTAIN, ERROR,
    metamorphic_hunt, abstain_crash_hunt,
)


# =========================================================================== #
#  ADAPTERS — call the REAL gate functions black-box; map native dict->verdict
# =========================================================================== #
def _identity_fn(lhs, rhs, syms, domain):
    """Call the REAL gate's verify_identity (kappa=1 IDENTITY-PROVE mode)."""
    return SG.verify_identity(lhs, rhs, syms, domain=domain)


def _integral_fn(integrand, var, a, b, claimed):
    """Call the REAL gate's verify_definite_integral (kappa=1 CLOSED-FORM mode)."""
    return SG.verify_definite_integral(integrand, var, a, b, claimed)


def _to_verdict(raw):
    """Map the REAL gate's native dict onto CRUCIBLE's vocabulary.
       verdict == 'CERTIFIED' -> ACCEPT  (the gate certified the claim)
       verdict == 'REJECTED'  -> REJECT  (the gate refused the claim)
       anything else          -> ABSTAIN (e.g. CERTIFIED-SINGLE-FAMILY / unknown)
    """
    v = raw.get("verdict")
    if v == "CERTIFIED":
        return ACCEPT
    if v == "REJECTED":
        return REJECT
    return ABSTAIN


gate_identity = GateAdapter("SYMBOLICA-agreement(IDENTITY)", _identity_fn, _to_verdict)
gate_integral = GateAdapter("SYMBOLICA-agreement(CLOSED-FORM)", _integral_fn, _to_verdict)


# =========================================================================== #
#  SEEDS — well-posed problems the gate decides via multi-method AGREEMENT.
#  A mix of TRUE identities (-> CERTIFIED) and FALSE ones (-> REJECTED), each with a
#  single real free symbol so the metamorphic transforms apply cleanly. Domains are
#  chosen so the functions are real-defined across the box.
# =========================================================================== #
x = sp.Symbol('x', real=True)

# IDENTITY seeds. (lhs, rhs, domain) — caller-asserted truth noted in comments.
IDENTITY_SEEDS = [
    # --- TRUE identities (gate should CERTIFY) ---
    {"lhs": sp.sin(x)**2 + sp.cos(x)**2, "rhs": sp.Integer(1),
     "syms": [x], "domain": (-3, 3)},                          # Pythagorean (true)
    {"lhs": sp.sin(2*x), "rhs": 2*sp.sin(x)*sp.cos(x),
     "syms": [x], "domain": (-2, 2)},                          # double-angle (true)
    {"lhs": sp.expand((x + 1)**3), "rhs": (x + 1)**3,
     "syms": [x], "domain": (-2, 2)},                          # expand (true)
    {"lhs": sp.cosh(x)**2 - sp.sinh(x)**2, "rhs": sp.Integer(1),
     "syms": [x], "domain": (-2, 2)},                          # hyperbolic (true)
    {"lhs": sp.log(sp.exp(x)), "rhs": x,
     "syms": [x], "domain": (-2, 2)},                          # log-exp inverse (true on R)
    {"lhs": (x**2 - 1), "rhs": (x - 1)*(x + 1),
     "syms": [x], "domain": (-3, 3)},                          # factoring (true)
    # --- FALSE identities (gate should REJECT) ---
    {"lhs": 2*x, "rhs": 3*x,
     "syms": [x], "domain": (1, 4)},                           # off by a factor (false)
    {"lhs": sp.sin(x), "rhs": x,
     "syms": [x], "domain": (1, 3)},                           # sin x != x (false off 0)
    {"lhs": sp.cos(x), "rhs": sp.Integer(1) - x**2/2,
     "syms": [x], "domain": (1, 3)},                           # truncated Taylor (false)
    {"lhs": x**2, "rhs": x**3,
     "syms": [x], "domain": (2, 4)},                           # different powers (false)
]

# CLOSED-FORM seeds. (integrand, var, a, b, claimed)
INTEGRAL_SEEDS = [
    # --- TRUE closed forms (gate should CERTIFY) ---
    {"integrand": x, "var": x, "a": 0, "b": 1, "claimed": sp.Rational(1, 2)},        # int x = 1/2
    {"integrand": x**2, "var": x, "a": 0, "b": 1, "claimed": sp.Rational(1, 3)},     # int x^2 = 1/3
    {"integrand": sp.sin(x), "var": x, "a": 0, "b": sp.pi, "claimed": sp.Integer(2)},# int sin = 2
    {"integrand": sp.exp(x), "var": x, "a": 0, "b": 1, "claimed": sp.exp(1) - 1},    # int e^x = e-1
    # --- FALSE closed forms (gate should REJECT) ---
    {"integrand": x, "var": x, "a": 0, "b": 1, "claimed": sp.Integer(1)},            # wrong (true 1/2)
    {"integrand": x**2, "var": x, "a": 0, "b": 1, "claimed": sp.Rational(1, 2)},     # wrong (true 1/3)
    {"integrand": sp.sin(x), "var": x, "a": 0, "b": sp.pi, "claimed": sp.Integer(3)},# wrong (true 2)
]


# =========================================================================== #
#  METAMORPHIC TRANSFORMS — CLAIMED meaning-preserving rewrites (oracle=None).
# =========================================================================== #
# ---- IDENTITY transforms ----
def _t_id_symmetry(obj):
    """SYMMETRY: a == b  iff  b == a. Swap lhs and rhs."""
    return {"lhs": obj["rhs"], "rhs": obj["lhs"], "syms": obj["syms"],
            "domain": obj["domain"]}


def _t_id_add_const(obj):
    """ADD-CONSTANT: lhs+7 == rhs+7  iff  lhs==rhs. Add the SAME constant to both sides."""
    C = sp.Integer(7)
    return {"lhs": obj["lhs"] + C, "rhs": obj["rhs"] + C, "syms": obj["syms"],
            "domain": obj["domain"]}


def _t_id_scale(obj):
    """SCALE: 3*lhs == 3*rhs  iff  lhs==rhs (3 != 0). Multiply BOTH sides by 3."""
    K = sp.Integer(3)
    return {"lhs": K * obj["lhs"], "rhs": K * obj["rhs"], "syms": obj["syms"],
            "domain": obj["domain"]}


def _t_id_var_rename(obj):
    """VAR-RENAME: rename the single free symbol x->y. The identity is the SAME statement
    (a bound/free rename), so the verdict must be invariant. Domain unchanged."""
    syms = obj["syms"]
    if len(syms) != 1:
        raise ValueError("var-rename only defined for single-symbol seeds")
    old = syms[0]
    new = sp.Symbol('y_renamed', real=True)
    return {"lhs": obj["lhs"].subs(old, new), "rhs": obj["rhs"].subs(old, new),
            "syms": [new], "domain": obj["domain"]}


def _t_id_move_to_lhs(obj):
    """REARRANGE: (lhs - rhs) == 0  iff  lhs == rhs. Move everything to one side; the
    asserted equality has the SAME truth value. (rhs becomes the literal 0.)"""
    return {"lhs": obj["lhs"] - obj["rhs"], "rhs": sp.Integer(0), "syms": obj["syms"],
            "domain": obj["domain"]}


IDENTITY_TRANSFORMS = [
    ("symmetry (swap lhs<->rhs)", _t_id_symmetry),
    ("add-constant (+7 both sides)", _t_id_add_const),
    ("scale (x3 both sides)", _t_id_scale),
    ("variable-rename (x->y)", _t_id_var_rename),
    ("rearrange (lhs-rhs == 0)", _t_id_move_to_lhs),
]


# ---- CLOSED-FORM transforms ----
def _t_int_scale(obj):
    """SCALE-BOTH: integral of 5*f == 5*claimed  iff  integral f == claimed (linearity)."""
    K = sp.Integer(5)
    return {"integrand": K * obj["integrand"], "var": obj["var"], "a": obj["a"],
            "b": obj["b"], "claimed": K * sp.sympify(obj["claimed"])}


def _t_int_negate(obj):
    """NEGATE-BOTH: integral of -f == -claimed  iff  integral f == claimed."""
    return {"integrand": -obj["integrand"], "var": obj["var"], "a": obj["a"],
            "b": obj["b"], "claimed": -sp.sympify(obj["claimed"])}


def _t_int_var_rename(obj):
    """VAR-RENAME: integral_a^b f(x) dx == integral_a^b f(t) dt (dummy var rename).
    Same definite integral, same claimed value -> verdict invariant."""
    old = obj["var"]
    new = sp.Symbol('t_renamed', real=True)
    return {"integrand": sp.sympify(obj["integrand"]).subs(old, new), "var": new,
            "a": obj["a"], "b": obj["b"], "claimed": obj["claimed"]}


INTEGRAL_TRANSFORMS = [
    ("scale-both (x5 integrand & claimed)", _t_int_scale),
    ("negate-both (-integrand & -claimed)", _t_int_negate),
    ("dummy-var-rename (x->t)", _t_int_var_rename),
]


# =========================================================================== #
#  ABSTAIN/CRASH — malformed math must NOT silently CERTIFY (ACCEPT).
#  SAFE = {REJECT, ABSTAIN, ERROR}. A garbage problem that yields CERTIFIED is the bug.
# =========================================================================== #
_SAFE = {REJECT, ABSTAIN, ERROR}

MALFORMED_IDENTITY = [
    ("unparseable lhs string",
     {"lhs": "this is not @@ math", "rhs": sp.Integer(1), "syms": [x],
      "domain": (-1, 1)}, _SAFE),
    ("empty syms list (no free variable to sample)",
     {"lhs": sp.sin(x), "rhs": sp.cos(x), "syms": [], "domain": (-1, 1)}, _SAFE),
    ("degenerate domain (lo==hi, zero-width box)",
     {"lhs": 2*x, "rhs": 3*x, "syms": [x], "domain": (1, 1)}, _SAFE),
    ("domain reversed (lo>hi)",
     {"lhs": 2*x, "rhs": 3*x, "syms": [x], "domain": (5, -5)}, _SAFE),
    ("None as rhs",
     {"lhs": sp.sin(x), "rhs": None, "syms": [x], "domain": (-1, 1)}, _SAFE),
    ("integrand-only-nan: lhs=1/x*0form is fine; use unparseable rhs",
     {"lhs": sp.sin(x), "rhs": "@@@", "syms": [x], "domain": (-1, 1)}, _SAFE),
]

MALFORMED_INTEGRAL = [
    ("unparseable integrand",
     {"integrand": "%% not math", "var": x, "a": 0, "b": 1,
      "claimed": sp.Integer(0)}, _SAFE),
    ("divergent integral (1/x over [0,1]) claimed finite",
     {"integrand": 1/x, "var": x, "a": 0, "b": 1, "claimed": sp.Integer(1)}, _SAFE),
    ("claimed is unparseable",
     {"integrand": x, "var": x, "a": 0, "b": 1, "claimed": "@@bad"}, _SAFE),
    ("bounds reversed with claimed for forward (a>b)",
     {"integrand": x, "var": x, "a": 1, "b": 0, "claimed": sp.Rational(1, 2)}, _SAFE),
    ("None claimed",
     {"integrand": x, "var": x, "a": 0, "b": 1, "claimed": None}, _SAFE),
]


# =========================================================================== #
def _print_seed_verdicts(name, gate, seeds, fmt):
    print(f"\n[seed verdicts: {name}] (mix of true->ACCEPT and false->REJECT):")
    for i, s in enumerate(seeds):
        try:
            v = gate.verdict(s)
        except Exception as e:
            v = f"<raised {type(e).__name__}>"
        print(f"  seed[{i}] {fmt(s)} -> {v}")


def main():
    print("=" * 78)
    print("CRUCIBLE probe: SYMBOLICA frozen agreement gate")
    print("REAL gate: symbolica_gate.verify_identity / verify_definite_integral")
    print("kappa=1 slice: the CERTIFIED/REJECTED multi-method AGREEMENT verdict")
    print("modes: METAMORPHIC + ABSTAIN-CRASH only | oracle: NONE")
    print("  (an independent oracle would re-use one of the gate's OWN legs -> circular;")
    print("   transform meaning-preservation is CALLER-ASSERTED -> residual risk)")
    print("=" * 78)

    # show seed verdicts so the metamorphic base verdicts are auditable
    _print_seed_verdicts("IDENTITY", gate_identity, IDENTITY_SEEDS,
                         lambda s: f"({s['lhs']}) == ({s['rhs']}) on {s['domain']}")
    _print_seed_verdicts("CLOSED-FORM", gate_integral, INTEGRAL_SEEDS,
                         lambda s: f"int_{s['a']}^{s['b']} ({s['integrand']}) d{s['var']} =? {s['claimed']}")

    # ---- MODE 1: METAMORPHIC (IDENTITY) -------------------------------------------
    print("\n" + "-" * 78)
    print("MODE 1a: METAMORPHIC (IDENTITY-PROVE) — verdict invariant under")
    print("         symmetry / add-constant / scale / var-rename / rearrange")
    print("-" * 78)
    mm_id = metamorphic_hunt(gate_identity, IDENTITY_SEEDS, IDENTITY_TRANSFORMS,
                             max_probes=10000, oracle=None)
    print(json.dumps(mm_id.to_dict(), indent=2, default=str))

    # ---- MODE 1b: METAMORPHIC (CLOSED-FORM) ---------------------------------------
    print("\n" + "-" * 78)
    print("MODE 1b: METAMORPHIC (CLOSED-FORM) — verdict invariant under")
    print("         scale-both / negate-both / dummy-var-rename")
    print("-" * 78)
    mm_int = metamorphic_hunt(gate_integral, INTEGRAL_SEEDS, INTEGRAL_TRANSFORMS,
                              max_probes=10000, oracle=None)
    print(json.dumps(mm_int.to_dict(), indent=2, default=str))

    # ---- MODE 2: ABSTAIN/CRASH ----------------------------------------------------
    print("\n" + "-" * 78)
    print("MODE 2a: ABSTAIN/CRASH (IDENTITY) — malformed math must not CERTIFY")
    print("-" * 78)
    ac_id = abstain_crash_hunt(gate_identity, MALFORMED_IDENTITY, max_probes=1000)
    print(json.dumps(ac_id.to_dict(), indent=2, default=str))

    print("\n" + "-" * 78)
    print("MODE 2b: ABSTAIN/CRASH (CLOSED-FORM) — malformed math must not CERTIFY")
    print("-" * 78)
    ac_int = abstain_crash_hunt(gate_integral, MALFORMED_INTEGRAL, max_probes=1000)
    print(json.dumps(ac_int.to_dict(), indent=2, default=str))

    # ---- summary ------------------------------------------------------------------
    from crucible_harness import Kill
    results = {"metamorphic-identity": mm_id, "metamorphic-integral": mm_int,
               "abstain-identity": ac_id, "abstain-integral": ac_int}
    kills = {k: r for k, r in results.items() if isinstance(r, Kill)}
    print("\n" + "=" * 78)
    if kills:
        print(f"RESULT: {len(kills)} KILL(s) found: {list(kills.keys())}")
        for k, r in kills.items():
            print(f"\n--- KILL EXHIBIT [{k}] ---")
            print(json.dumps(r.to_dict(), indent=2, default=str))
    else:
        print("RESULT: SURVIVED to budget on all 4 hunts (NO kill).")
        print("  Regime probed: hand-curated true+false IDENTITY/CLOSED-FORM seeds with a")
        print("  single real free symbol; 5 identity + 3 integral CLAIMED meaning-preserving")
        print("  transforms; malformed-input robustness. Meaning-preservation CALLER-ASSERTED")
        print("  (no independent oracle — would re-use a gate leg). NOT a soundness claim.")
    print("=" * 78)


if __name__ == "__main__":
    main()
