#!/usr/bin/env python3
"""PROOFSMITH FORMALIZE-VERIFY demo runner.

Feeds the three good proofs (Proofs.lean) + three ATTACK proofs (sorry / bogus-axiom /
wrong-statement) through the frozen kernel gate, plus the z3 cross-check on T1.
Writes results.json and prints a comparison to the committed PREDICTION.md.

The JUDGE is the Lean kernel + #print axioms + z3 — machines, not the model. No
self-report is trusted.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import proof_gate
import smt_gate

HERE = os.path.dirname(os.path.abspath(__file__))
GOOD = open(os.path.join(HERE, "Proofs.lean")).read()

# Committed classical allow-list for T2/T3 (tactic machinery pulls these in).
CLA = ["propext", "Classical.choice", "Quot.sound"]

GOOD_TARGETS = [
    {"name": "and_comm_demo",  "reference_statement": "forall (p q : Prop), p ∧ q → q ∧ p", "allowed_axioms": []},
    {"name": "even_or_odd_demo", "reference_statement": "forall (n : Nat), ∃ k, n = 2 * k ∨ n = 2 * k + 1", "allowed_axioms": CLA},
    {"name": "gauss_demo",     "reference_statement": "forall (n : Nat), 2 * sumTo n = n * (n + 1)", "allowed_axioms": CLA},
]

# ---- ATTACK proofs (must be REJECTED) ----
ATTACK_SORRY = GOOD + "\ntheorem gauss_sorry (n : Nat) : 2 * sumTo n = n * (n + 1) := by sorry\n"
ATTACK_BOGUS = GOOD + "\naxiom gauss_cheat : ∀ (n : Nat), 2 * sumTo n = n * (n + 1)\ntheorem gauss_via_axiom (n : Nat) : 2 * sumTo n = n * (n + 1) := gauss_cheat n\n"


def main():
    out = {"demo": "FORMALIZE-VERIFY", "judge": "Lean 4.31.0 kernel + #print axioms + z3",
           "lean_available": proof_gate.lean_available()}

    # P1/P2 — the three good reproductions
    out["good"] = proof_gate.gate(GOOD, GOOD_TARGETS)

    # P3 — sorry attack
    out["attack_sorry"] = proof_gate.gate(ATTACK_SORRY, [
        {"name": "gauss_sorry", "reference_statement": "forall (n : Nat), 2 * sumTo n = n * (n + 1)", "allowed_axioms": CLA}])

    # P4 — bogus-axiom attack
    out["attack_bogus_axiom"] = proof_gate.gate(ATTACK_BOGUS, [
        {"name": "gauss_via_axiom", "reference_statement": "forall (n : Nat), 2 * sumTo n = n * (n + 1)", "allowed_axioms": CLA}])

    # P5 — wrong-statement attack: T1's real proof vs a DIFFERENT committed reference
    out["attack_wrong_statement"] = proof_gate.gate(GOOD, [
        {"name": "and_comm_demo", "reference_statement": "forall (p q : Prop), p ∨ q → q ∧ p", "allowed_axioms": []}])

    # P6 — z3 cross-verifier corroboration of T1's propositional content
    import z3
    def t1_neg():
        p, q = z3.Bool("p"), z3.Bool("q")
        return z3.Not(z3.Implies(z3.And(p, q), z3.And(q, p)))
    out["z3_cross_check_T1"] = smt_gate.check_valid(t1_neg)

    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f, indent=2)

    # ----- compare to committed predictions -----
    g = out["good"]
    checks = [
        ("P1 all three good proofs PASS all 4 checks",
         g["accepted"] is True),
        ("P2a T1 uses NO axioms",
         g["targets"]["and_comm_demo"]["axioms_used"] == []),
        ("P2b T2,T3 axioms ⊆ {propext,Classical.choice,Quot.sound}, no sorryAx",
         all(set(g["targets"][n]["axioms_used"]) <= set(CLA)
             for n in ("even_or_odd_demo", "gauss_demo"))),
        ("P3 sorry attack REJECTED (sorryAx surfaced)",
         out["attack_sorry"]["accepted"] is False and
         "sorryAx" in (out["attack_sorry"]["targets"]["gauss_sorry"]["axioms_used"] or [])),
        ("P4 bogus-axiom attack REJECTED (gauss_cheat surfaced)",
         out["attack_bogus_axiom"]["accepted"] is False and
         "gauss_cheat" in (out["attack_bogus_axiom"]["targets"]["gauss_via_axiom"]["extra_axioms"] or [])),
        ("P5 wrong-statement attack REJECTED (check4 false)",
         out["attack_wrong_statement"]["accepted"] is False and
         out["attack_wrong_statement"]["targets"]["and_comm_demo"]["check4_statement_match"] is False),
        ("P6 z3 independently confirms T1 VALID",
         out["z3_cross_check_T1"]["valid"] is True),
    ]
    print("=" * 72)
    print("FORMALIZE-VERIFY demo — prediction vs machine verdict")
    print("=" * 72)
    npass = 0
    for label, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        npass += int(ok)
    print("-" * 72)
    print(f"  {npass}/{len(checks)} committed predictions confirmed by the machine judge.")
    print(f"  results.json written to {os.path.join(HERE, 'results.json')}")
    # exit nonzero if any prediction missed, so this is itself a machine gate
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
