#!/usr/bin/env python3
"""CODEFORGE router — given a code/algorithm task, decide WHICH mode fires (or whether
the task is kappa=0 and belongs to ARMOR, not the weapon).

This is the CS_ENG analogue of the v5 WHEN/WHERE router (BOX_V5.md §2). Code has the
sharpest cheap verifier there is — it runs or it doesn't — so most code tasks are
kappa=1 weapon-eligible. But two classes are NOT, and routing them to the weapon is
theater the box explicitly forbids:
  * kappa=0 judgment   — "design this architecture", "is this code good/clean", any
    deliverable scored by a gameable proxy (LLM-judge / in-sample / human rating).
  * kappa=1-but-not-worth-it — routine codegen where armor's test-runner already
    suffices; the weapon adds cost and ~0 marginal Q.

The three weapon modes (each with an EXACT or held-out verifier):
  SYNTH-VERIFY  : synthesize code to a spec; gate on HIDDEN + PROPERTY + DIFFERENTIAL
                  tests the generator never sees (synth_verify.py).
  SUPEROPT      : search a faster/smaller variant of a correct function; DIFFERENTIAL
                  correctness gate + measured benchmark (superopt_verify.py).
  ALGO-DISCOVER : produce a combinatorial algorithm object with an EXACT certificate —
                  sorting network via the 0/1 principle (sortnet_verify.py) or a
                  matrix-mult bilinear scheme via a symbolic identity (matmul_verify.py).
                  KNOWN target -> reproduce-and-verify (labeled reproduction);
                  OPEN target  -> verifier-gated search, cross-model-audited, honest
                  negative expected (records are hard; never claim one without an
                  audited certificate strictly beating prior art).

CONFLICT RULE (BOX_V5): if a task matches a POSITIVE trigger AND a NEGATIVE item, the
NEGATIVE wins (weapon off) — route to armor. Deterministic; self-tested.
"""
import sys
import json

# precondition_key -> (MODE, kappa, branch, rationale)
POSITIVE_RULES = [
    ("spec_with_hidden_tests", "SYNTH-VERIFY", 1.0, "SYNTH",
     "synthesize code to a spec; gate on hidden+property+differential tests the "
     "generator never sees"),
    ("optimize_existing_function", "SUPEROPT", 1.0, "SEARCH",
     "search a faster/smaller variant; differential-correctness gate (kappa=1) + a "
     "measured benchmark (speed is measured, not certified)"),
    ("sorting_network_target", "ALGO-DISCOVER", 1.0, "ALGO",
     "sorting network -> EXACT 0/1-principle certificate (all 2^n binary inputs sort)"),
    ("matmul_scheme_target", "ALGO-DISCOVER", 1.0, "ALGO",
     "matrix-mult bilinear scheme -> EXACT non-commutative symbolic identity certificate"),
    ("exact_cert_combinatorial_object", "ALGO-DISCOVER", 1.0, "ALGO",
     "a combinatorial algorithm object with a cheap exact certificate"),
]

# negative_key -> (kind, rationale).  kind: "kappa0" (no real verifier) or "not_worth_it"
NEGATIVE_RULES = [
    ("design_or_architecture_judgment", "kappa0",
     "'good design/architecture' has no exact verifier -> kappa=0 -> armor (ground+abstain)"),
    ("code_quality_taste", "kappa0",
     "maintainability/readability/style is taste -> kappa=0 -> armor"),
    ("proxy_only_scorer", "kappa0",
     "the only scorer is gameable (LLM-judge / in-sample / human rating) -> does NOT "
     "raise kappa -> armor; a gameable proxy WILL be gamed"),
    ("routine_codegen_armor_suffices", "not_worth_it",
     "armor's test-runner already suffices; the weapon adds cost and ~0 marginal Q "
     "(kappa=1 but not worth drawing the weapon)"),
]

CEILING = ("CODEFORGE ships ONLY frozen-verifier-passed objects. It raises VERIFIED "
           "THROUGHPUT, not the model's ceiling. Reproductions are labeled reproductions; "
           "no record without an audited certificate strictly beating prior art; never "
           "claims to solve an open problem. kappa=0 'is this code good' -> armor.")


def route(task):
    """task: dict of boolean preconditions. Returns the deterministic routing plan."""
    negatives = [(k, kind, why) for (k, kind, why) in NEGATIVE_RULES if task.get(k)]
    positives = [(k, mode, kap, branch, why)
                 for (k, mode, kap, branch, why) in POSITIVE_RULES if task.get(k)]

    weapon_suppressed = len(negatives) > 0 and len(positives) > 0  # CONFLICT RULE
    armor_track = [{"trigger": k, "kappa": 0.0 if kind == "kappa0" else 1.0,
                    "kind": kind, "rationale": why} for (k, kind, why) in negatives]

    weapon_track = []
    if not weapon_suppressed:
        for (k, mode, kap, branch, why) in positives:
            entry = {"trigger": k, "mode": mode, "kappa": kap, "branch": branch,
                     "rationale": why}
            if mode == "ALGO-DISCOVER":
                # KNOWN vs OPEN: authoritative only via grounded lookup / fetched status.
                # When in doubt -> OPEN (BOX_V5), with structure-fetch as the first step.
                if task.get("known_target"):
                    entry["target"] = "KNOWN"
                    entry["sub_branch"] = "FETCH-KNOWN (reproduce-and-verify; labeled reproduction)"
                else:
                    entry["target"] = "OPEN"
                    entry["sub_branch"] = ("SEARCH-OPEN (verifier-gated search, cross-model "
                                           "audit; honest negative expected — never a record "
                                           "without an audited strictly-better certificate)")
            weapon_track.append(entry)

    plan = {
        "weapon": "CODEFORGE",
        "weapon_track": weapon_track,
        "armor_track": armor_track,
        "weapon_suppressed_by_negative": bool(weapon_suppressed),
        "kappa0_armor_only": bool(negatives and not weapon_track),
        "ceiling": CEILING,
    }
    if weapon_suppressed:
        plan["note"] = ("CONFLICT RULE fired: task matched a positive trigger AND a negative "
                        "item -> negative wins, weapon OFF, routed to armor.")
    elif not positives and not negatives:
        plan["note"] = "no precondition matched -> underdefined; FREEZE the spec, then re-route."
    elif not positives:
        plan["note"] = "kappa=0 task -> ARMOR ONLY (no weapon-eligible piece)."
    return plan


def _selftest():
    # SYNTH-VERIFY
    p = route({"spec_with_hidden_tests": True})
    assert [w["mode"] for w in p["weapon_track"]] == ["SYNTH-VERIFY"], p
    assert p["weapon_track"][0]["kappa"] == 1.0, p

    # SUPEROPT
    p = route({"optimize_existing_function": True})
    assert p["weapon_track"][0]["mode"] == "SUPEROPT" and p["weapon_track"][0]["branch"] == "SEARCH", p

    # ALGO-DISCOVER, KNOWN -> reproduction
    p = route({"sorting_network_target": True, "known_target": True})
    w = p["weapon_track"][0]
    assert w["mode"] == "ALGO-DISCOVER" and w["target"] == "KNOWN", p
    assert "reproduction" in w["sub_branch"], p

    # ALGO-DISCOVER, default OPEN (when-in-doubt)
    p = route({"matmul_scheme_target": True})
    w = p["weapon_track"][0]
    assert w["target"] == "OPEN" and "negative expected" in w["sub_branch"], p

    # kappa=0 design judgment -> armor only
    p = route({"design_or_architecture_judgment": True})
    assert p["weapon_track"] == [] and p["kappa0_armor_only"] is True, p
    assert p["armor_track"][0]["kappa"] == 0.0, p

    # proxy-only scorer alone -> armor only (kappa not raised)
    p = route({"proxy_only_scorer": True})
    assert p["weapon_track"] == [] and p["armor_track"][0]["kind"] == "kappa0", p

    # routine codegen alone -> armor (kappa=1 but not worth it)
    p = route({"routine_codegen_armor_suffices": True})
    assert p["weapon_track"] == [] and p["armor_track"][0]["kind"] == "not_worth_it", p

    # CONFLICT RULE: positive + negative -> negative wins, weapon OFF
    p = route({"spec_with_hidden_tests": True, "proxy_only_scorer": True})
    assert p["weapon_suppressed_by_negative"] is True and p["weapon_track"] == [], p

    # underdefined
    p = route({})
    assert p["weapon_track"] == [] and "underdefined" in p["note"], p

    print("ROUTER    selftest: PASS (SYNTH/SUPEROPT/ALGO known+open routed; kappa=0 design, "
          "proxy, routine -> armor; CONFLICT RULE negative-wins; underdefined -> freeze)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: codeforge_router.py selftest | <task.json>")
