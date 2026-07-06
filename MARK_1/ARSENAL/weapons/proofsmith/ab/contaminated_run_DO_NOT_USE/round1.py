#!/usr/bin/env python3
"""AB round 1 — gate the 3 blind Haiku attempts per lemma. The KERNEL judges; agent
prose is ignored (only the extracted proof text is gated). Saves round1_results.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import proof_gate

HERE = os.path.dirname(os.path.abspath(__file__))
PRE = open(os.path.join(HERE, "preamble.lean")).read()
CLA = ["propext", "Classical.choice", "Quot.sound"]

REF = {
    "L1": "forall (n : Nat), ps_f1 n = n * n",
    "L2": "forall (n : Nat), ps_g n = 3 * n",
    "L3": "forall (n : Nat), 2 * ps_t n = n * (n + 1)",
    "L4": "forall (n : Nat), ps_d (n + 1) = ps_t n",
}

# Verbatim proof text extracted from the 12 Haiku round-1 attempts (prose stripped).
ATTEMPTS = {
 "L1": [
  "theorem L1 (n : Nat) : ps_f1 n = n * n := by\n  induction n with\n  | zero => rfl\n  | succ n ih =>\n    simp only [ps_f1]\n    rw [ih]\n    omega",
  "theorem L1 (n : Nat) : ps_f1 n = n * n := by\n  induction n with\n  | zero => rfl\n  | succ n ih =>\n    unfold ps_f1\n    rw [ih]\n    ring",
  "theorem L1 (n : Nat) : ps_f1 n = n * n := by\n  induction n with\n  | zero => rfl\n  | succ k ih => simp only [ps_f1, ih, Nat.mul_add, Nat.mul_comm] at *; omega",
 ],
 "L2": [
  "theorem L2 (n : Nat) : ps_g n = 3 * n := by\n  induction n with\n  | zero => rfl\n  | succ n ih => simp only [ps_g]; rw [ih]; ring",
  "theorem L2 (n : Nat) : ps_g n = 3 * n := by\n  induction n with\n  | zero => rfl\n  | succ n ih =>\n    simp [ps_g]\n    rw [ih]\n    ring",
  "theorem L2 (n : Nat) : ps_g n = 3 * n := by\n  induction n with\n  | zero => simp only [ps_g]\n  | succ k ih => simp only [ps_g, ih]; omega",
 ],
 "L3": [
  "theorem L3 (n : Nat) : 2 * ps_t n = n * (n + 1) := by\n  induction n with\n  | zero => rfl\n  | succ n ih => simp only [ps_t]; omega",
  "theorem L3 (n : Nat) : 2 * ps_t n = n * (n + 1) := by\n  induction n with\n  | zero => rfl\n  | succ n ih =>\n    simp only [ps_t]\n    rw [Nat.mul_add, ih]\n    omega",
  "theorem L3 (n : Nat) : 2 * ps_t n = n * (n + 1) := by\n  induction n with\n  | zero => rfl\n  | succ n ih =>\n    unfold ps_t\n    omega",
 ],
 "L4": [
  "theorem L4 (n : Nat) : ps_d (n + 1) = ps_t n := by\n  induction n with\n  | zero => rfl\n  | succ n ih =>\n    simp only [ps_d, ps_t]\n    rw [ih]\n    rfl",
  "theorem L4 (n : Nat) : ps_d (n + 1) = ps_t n := by\n  induction n with\n  | zero => rfl\n  | succ k ih =>\n    show ps_d (k + 1 + 1) = ps_t (k + 1)\n    rw [ps_d, ih]\n    rw [ps_t]",
  "theorem L4 (n : Nat) : ps_d (n + 1) = ps_t n := by\n  induction n with\n  | zero => rfl\n  | succ n ih =>\n    unfold ps_d ps_t\n    rw [ih]",
 ],
}


def gate_attempt(lemma, code):
    name = lemma  # theorem is named L1.. matching the target
    src = PRE + "\n" + code + "\n"
    g = proof_gate.gate(src, [{"name": name, "reference_statement": REF[lemma],
                               "allowed_axioms": CLA}], timeout=60)
    t = g["targets"].get(name, {})
    return {"accepted": g["accepted"], "axioms": t.get("axioms_used"),
            "checks": {k: t.get(k) for k in
                       ("check1_kernel_accepts", "check2_no_sorry_admit",
                        "check3_axiom_allowlist", "check4_statement_match")},
            "errors": g.get("errors", [])[:2]}


def main():
    results = {}
    print("=" * 72)
    print("AB ROUND 1 — 3 blind Haiku attempts/lemma, judged by the Lean kernel")
    print("=" * 72)
    for lemma in ("L1", "L2", "L3", "L4"):
        results[lemma] = []
        verds = []
        for i, code in enumerate(ATTEMPTS[lemma]):
            r = gate_attempt(lemma, code)
            results[lemma].append(r)
            verds.append("PASS" if r["accepted"] else "fail")
        oneshot = verds[0] == "PASS"
        bestof3 = any(v == "PASS" for v in verds)
        print(f"  {lemma}: attempts={verds}  | one-shot={'PASS' if oneshot else 'fail'}"
              f"  best-of-3={'PASS' if bestof3 else 'fail'}")
    with open(os.path.join(HERE, "round1_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("-" * 72)
    print("saved round1_results.json")


if __name__ == "__main__":
    main()
