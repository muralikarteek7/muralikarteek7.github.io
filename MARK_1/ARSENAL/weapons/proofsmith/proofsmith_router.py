#!/usr/bin/env python3
"""PROOFSMITH router — given a proof task, decide the mode, the verifier, and the
honest contract. It does NOT prove anything; it CHOOSES which mode applies and
labels the κ of each piece so nothing κ<1 is presented as kernel-certified.

This is the "be a chooser" capability the v5 box asks of every weapon. The kernel
(or the z3 decidable slice) is the only judge of a proof's validity; the router
decides which judge applies and flags the two κ<1 surfaces a proof task hides:
  * AUTOFORMALIZATION (English → formal statement) — a judgment; cross-model review.
  * "is this argument convincing / is this the right strategy" — κ=0; armor only.

Intake is a structured task descriptor (booleans). In live use these come from an
armor-side reading of the task; here they are explicit so the routing is testable.
"""
import sys
import json

# Modes (map to the κ-router branches in Next/BOX_V5.md):
#   FORMALIZE_VERIFY : FETCH-KNOWN analogue — known theorem, known proof → reproduce + kernel-check.
#   PROOF_SEARCH     : a formal goal is given → search tactics/automation, kernel-gate every candidate.
#   LEMMA_EXTEND     : auxiliary lemmas / gap-filling in a known development; de-novo OPEN conjecture
#                      is the rare frontier → HONEST NEGATIVE EXPECTED, never claim to prove it.
#   AUTOFORMALIZE_THEN_PROVE : English claim, no formal statement → autoformalize (κ<1, FLAG) then prove.
#   ARMOR            : κ=0 judgment ("is this convincing / right strategy") → ground + abstain.


def route(task):
    """task: dict of fields describing the proof task. Returns a routing plan."""
    t = task
    plan = {"flags": [], "kappa_lt_1_surfaces": []}

    # ---- κ=0 first: a judgment about a proof is NOT kernel-certifiable ----
    if t.get("is_judgment_about_proof") or t.get("asks_is_argument_convincing") \
            or t.get("asks_which_strategy"):
        plan.update({
            "mode": "ARMOR", "kappa": 0, "verifier": "none (κ=0)",
            "note": ("Judgment about a proof (convincing? right strategy?) has NO exact "
                     "verifier → ARMOR ONLY: ground in sources + cross-model panel + scored "
                     "ABSTAIN. The kernel does NOT certify this; do not pretend it does."),
            "contract": "grounded analysis + honest abstention; NO kernel certificate.",
        })
        return plan

    # ---- choose the verifier engine ----
    if t.get("decidable_fragment"):
        verifier = ("z3 SMT decision procedure (DECIDABLE slice: propositional / QF & "
                    "linear arithmetic) — exact on this slice, NOT a general proof assistant")
    else:
        verifier = "Lean 4 kernel + #print axioms (the 4-check gate: proof_gate.py)"

    # ---- autoformalization surface ----
    if t.get("english_claim_only") and not t.get("has_formal_statement"):
        plan["kappa_lt_1_surfaces"].append(
            "AUTOFORMALIZATION: English → formal statement is a κ<1 JUDGMENT. The kernel "
            "certifies only that the proof proves the FORMAL statement; whether that formal "
            "statement MEANS the English claim must be cross-model reviewed (≠ generator).")
        plan["flags"].append("autoformalize-first; flag translation risk; do NOT trust blindly")
        mode = "AUTOFORMALIZE_THEN_PROVE"
    elif t.get("target_is_known_theorem"):
        mode = "FORMALIZE_VERIFY"
    elif t.get("target_is_open_conjecture"):
        mode = "LEMMA_EXTEND"
    elif t.get("has_formal_statement"):
        mode = "PROOF_SEARCH"
    else:
        plan.update({"mode": "ABSTAIN", "kappa": None, "verifier": verifier,
                     "note": "Under-specified: no formal statement, not a known theorem, no "
                             "English claim. Abstain and ask for the precise statement."})
        return plan

    plan["mode"] = mode
    plan["kappa"] = 1
    plan["verifier"] = verifier

    # ---- per-mode honest contract ----
    if mode == "FORMALIZE_VERIFY":
        plan["contract"] = ("a kernel-checked LABELED REPRODUCTION of a known theorem "
                            "(source + date) + clean #print axioms. NOT a discovery.")
    elif mode == "PROOF_SEARCH":
        plan["contract"] = ("a kernel-checked proof of the GIVEN formal statement, or an "
                            "honest 'no proof found'. Counts only with allowed axioms + no sorry.")
    elif mode == "LEMMA_EXTEND":
        plan["honest_negative_expected"] = True
        plan["contract"] = ("kernel-checked auxiliary lemmas where reachable; the de-novo proof "
                            "of an OPEN conjecture is the rare frontier → HONEST NEGATIVE EXPECTED. "
                            "NEVER claim to prove an open problem — exhibit the term or report none.")
    elif mode == "AUTOFORMALIZE_THEN_PROVE":
        plan["contract"] = ("autoformalize (cross-model-reviewed translation) → prove the formal "
                            "statement → kernel-check. Ship BOTH the translation-review verdict and "
                            "the #print axioms. A proof of a mis-translated statement is worthless.")

    # ---- universal rails ----
    plan["rails"] = [
        "ship #print axioms with every proof; sorryAx or an unlisted axiom ⇒ FAILURE, not a result",
        "kernel-checked ≠ correct English theorem (statement-match is κ<1 → cross-model review)",
        "reproduction is labeled reproduction; never claim to prove an open conjecture",
    ]
    return plan


# ------------------------------- selftest ---------------------------------- #
def _selftest():
    # known theorem → FORMALIZE_VERIFY, Lean kernel
    r = route({"target_is_known_theorem": True})
    assert r["mode"] == "FORMALIZE_VERIFY" and r["kappa"] == 1 and "Lean" in r["verifier"], r

    # given formal goal → PROOF_SEARCH
    r = route({"has_formal_statement": True})
    assert r["mode"] == "PROOF_SEARCH", r

    # English claim only → AUTOFORMALIZE_THEN_PROVE + κ<1 surface flagged
    r = route({"english_claim_only": True})
    assert r["mode"] == "AUTOFORMALIZE_THEN_PROVE", r
    assert any("AUTOFORMALIZATION" in s for s in r["kappa_lt_1_surfaces"]), r

    # open conjecture → LEMMA_EXTEND with honest-negative expectation
    r = route({"target_is_open_conjecture": True})
    assert r["mode"] == "LEMMA_EXTEND" and r.get("honest_negative_expected") is True, r

    # judgment about a proof → ARMOR (κ=0), no kernel certificate
    r = route({"asks_is_argument_convincing": True})
    assert r["mode"] == "ARMOR" and r["kappa"] == 0 and r["verifier"] == "none (κ=0)", r

    # decidable fragment → z3 SMT slice selected as verifier
    r = route({"has_formal_statement": True, "decidable_fragment": True})
    assert r["mode"] == "PROOF_SEARCH" and "z3" in r["verifier"], r

    # under-specified → ABSTAIN
    r = route({})
    assert r["mode"] == "ABSTAIN", r

    print("proofsmith_router selftest: PASS")
    print("  known→FORMALIZE_VERIFY · formal-goal→PROOF_SEARCH · english→AUTOFORMALIZE(+κ<1 flag)")
    print("  open→LEMMA_EXTEND(honest-neg) · judgment→ARMOR(κ=0) · decidable→z3 · empty→ABSTAIN")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: proofsmith_router.py selftest | <task.json>")
