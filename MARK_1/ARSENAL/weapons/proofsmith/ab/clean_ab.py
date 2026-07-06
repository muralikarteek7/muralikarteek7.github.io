#!/usr/bin/env python3
"""CLEAN AB — answer key quarantined off-disk; provers ran with NO tools (verified
tool_uses=0); repair feedback = PURE verbatim kernel output (NO orchestrator hints).
The Lean kernel judges. Gates blind attempts + carries repair chains. Saves clean_results.json.

Blind attempts are the 12 no-tools Haiku responses (markdown fences stripped). Repair
attempts are appended as they are produced (see RESULT.md for provenance per round)."""
import json, os, re, sys
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

def strip(code):
    return re.sub(r"```(?:lean)?", "", code).strip()

# 12 clean (no-tools) blind attempts, verbatim (fences stripped on load)
BLIND = {
 "L1": [
  "theorem L1 (n : Nat) : ps_f1 n = n * n := by\n  induction n with\n  | zero => simp only [ps_f1]\n  | succ n ih => simp only [ps_f1]; omega",
  "theorem L1 (n : Nat) : ps_f1 n = n * n := by\n  induction n with\n  | zero => rw [ps_f1]\n  | succ n ih =>\n    rw [ps_f1]\n    rw [ih]\n    ring",
  "theorem L1 (n : Nat) : ps_f1 n = n * n := by\n  induction n with\n  | zero => simp only [ps_f1]; rfl\n  | succ n ih =>\n    simp only [ps_f1]\n    rw [ih]\n    omega",
 ],
 "L2": [
  "theorem L2 (n : Nat) : ps_g n = 3 * n := by\n  induction n with\n  | zero => simp only [ps_g]\n  | succ n ih => simp only [ps_g, ih]; omega",
  "theorem L2 (n : Nat) : ps_g n = 3 * n := by\n  induction n with\n  | zero => simp [ps_g]\n  | succ n ih => simp [ps_g, ih, Nat.succ_mul]",
  "theorem L2 (n : Nat) : ps_g n = 3 * n := by\n  induction n with\n  | zero => simp [ps_g]\n  | succ n ih => simp [ps_g, ih]; omega",
 ],
 "L3": [
  "theorem L3 (n : Nat) : 2 * ps_t n = n * (n + 1) := by\n  induction n with\n  | zero => rfl\n  | succ n ih =>\n    simp only [ps_t]\n    omega",
  "theorem L3 (n : Nat) : 2 * ps_t n = n * (n + 1) := by\n  induction n with\n  | zero => simp [ps_t]\n  | succ n ih =>\n    rw [ps_t, Nat.succ_mul, Nat.mul_succ, ih]\n    ring",
  "theorem L3 (n : Nat) : 2 * ps_t n = n * (n + 1) := by\n  induction n with\n  | zero => simp [ps_t]\n  | succ n ih =>\n    simp [ps_t]\n    omega",
 ],
 "L4": [
  "theorem L4 (n : Nat) : ps_d (n + 1) = ps_t n := by\n  induction n with\n  | zero => rfl\n  | succ n ih =>\n    show ps_d (n + 1 + 1) = ps_t (n + 1)\n    rw [show n + 1 + 1 = n + 2 by omega]\n    simp only [ps_d]\n    rw [show ps_d (n + 1) = ps_t n from ih]\n    simp only [ps_t]\n    omega",
  "theorem L4 (n : Nat) : ps_d (n + 1) = ps_t n := by\n  induction n with\n  | zero => rfl\n  | succ n ih =>\n    unfold ps_d ps_t\n    rw [ih]\n    ring",
  "theorem L4 (n : Nat) : ps_d (n + 1) = ps_t n := by\n  induction n with\n  | zero =>\n    simp [ps_d, ps_t]\n  | succ n ih =>\n    simp [ps_d, ps_t]\n    omega",
 ],
}

def gate_one(lemma, code):
    src = PRE + "\n" + strip(code) + "\n"
    g = proof_gate.gate(src, [{"name": lemma, "reference_statement": REF[lemma],
                               "allowed_axioms": CLA}], timeout=60)
    t = g["targets"].get(lemma, {})
    return {"accepted": g["accepted"], "axioms": t.get("axioms_used"),
            "full_output": None, "errors": g.get("errors", [])[:3]}

def verbatim_feedback(lemma, code):
    src = PRE + "\n" + strip(code) + "\n"
    rc, o = proof_gate._run_lean(src)
    return o.strip()

if __name__ == "__main__":
    res = {"blind": {}, "REF": REF}
    print("=" * 72); print("CLEAN AB — blind attempts (no tools, key quarantined), kernel judge"); print("=" * 72)
    for L in ("L1", "L2", "L3", "L4"):
        res["blind"][L] = [gate_one(L, c) for c in BLIND[L]]
        verds = ["PASS" if r["accepted"] else "fail" for r in res["blind"][L]]
        print(f"  {L}: {verds}  one-shot={'PASS' if verds[0]=='PASS' else 'fail'}"
              f"  best-of-3={'PASS' if 'PASS' in verds else 'fail'}")
    json.dump({**res, "BLIND_SOURCES": BLIND}, open(os.path.join(HERE, "clean_results.json"), "w"), indent=2)
    print("saved clean_results.json")
