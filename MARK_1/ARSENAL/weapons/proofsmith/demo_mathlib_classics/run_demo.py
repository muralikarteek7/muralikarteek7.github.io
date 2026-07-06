#!/usr/bin/env python3
"""PROOFSMITH mathlib-classics demo — gate a GENUINE famous theorem.

Reproduces Euclid's infinitude of primes via mathlib's `Nat.exists_infinite_primes`,
kernel-checked through the 4-check gate, and shows the gate REJECTING a sorry-version.

Requires a local mathlib build (the _mathlib_build/ lake project). The self-contained,
runs-anywhere demo is ../demo_formalize_verify/; this one is the headline LIBRARY
reproduction and needs mathlib present. The judge is the Lean kernel + #print axioms.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import proof_gate

HERE = os.path.dirname(os.path.abspath(__file__))
LAKE = os.path.join(os.path.dirname(HERE), "_mathlib_build")
CLA = ["propext", "Classical.choice", "Quot.sound"]

IMPORT = "import Mathlib.Data.Nat.Prime.Infinite\n"
GOOD = IMPORT + (
    "theorem infinitude_of_primes : ∀ n : Nat, ∃ p, n ≤ p ∧ Nat.Prime p :=\n"
    "  Nat.exists_infinite_primes\n")
ATTACK_SORRY = IMPORT + (
    "theorem primes_sorry : ∀ n : Nat, ∃ p, n ≤ p ∧ Nat.Prime p := by sorry\n")

REF = "forall (n : Nat), ∃ p, n ≤ p ∧ Nat.Prime p"


def main():
    if not os.path.isdir(os.path.join(LAKE, ".lake")):
        print(f"SKIP: mathlib build not found at {LAKE} (run lake exe cache get there).")
        sys.exit(2)

    out = {"demo": "MATHLIB-CLASSICS (infinitude of primes, Euclid ~300 BC)",
           "source": "mathlib Nat.exists_infinite_primes", "judge": "Lean kernel + #print axioms"}
    out["good"] = proof_gate.gate(GOOD, [
        {"name": "infinitude_of_primes", "reference_statement": REF, "allowed_axioms": CLA}],
        timeout=180, lake_project=LAKE)
    out["attack_sorry"] = proof_gate.gate(ATTACK_SORRY, [
        {"name": "primes_sorry", "reference_statement": REF, "allowed_axioms": CLA}],
        timeout=180, lake_project=LAKE)

    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f, indent=2)

    g = out["good"]["targets"]["infinitude_of_primes"]
    checks = [
        ("Infinitude of primes PASSES all 4 checks (labeled reproduction)",
         out["good"]["accepted"] is True),
        ("axioms ⊆ {propext, Classical.choice, Quot.sound}, no sorryAx",
         set(g["axioms_used"] or []) <= set(CLA)),
        ("sorry-version REJECTED (sorryAx surfaced)",
         out["attack_sorry"]["accepted"] is False and
         "sorryAx" in (out["attack_sorry"]["targets"]["primes_sorry"]["axioms_used"] or [])),
    ]
    print("=" * 72)
    print("MATHLIB-CLASSICS demo — infinitude of primes (REPRODUCTION)")
    print("=" * 72)
    npass = 0
    for label, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        npass += int(ok)
    print(f"  axioms_used = {g['axioms_used']}")
    print("-" * 72)
    print(f"  {npass}/{len(checks)} confirmed. Labeled reproduction of a KNOWN theorem — NOT a discovery.")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
