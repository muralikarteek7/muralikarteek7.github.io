#!/usr/bin/env python3
"""SHOES_ROUTING frozen rails — run EVERY adversarial self-test for BOTH components
(FOOTING + ROUTE-PLANNER). Exits 0 ONLY if:
  FOOTING      flags high-disagreement drafts, passes grounded ones, NEVER emits
               'verified'/'safe'/'correct', and FLAGS the misroute-degraded draft (g);
  ROUTE-PLANNER routes machine-checkable->EXECUTE / interpretation->ARMOR, fires the
               per-track verified-fact-delta=0 stuck-detector, does NOT halt a benign
               search, and FLAGS the Opus-needed-routed-to-Haiku misroute (g).

Doctrine: "A gate that can't fail is not a gate." If this exits non-zero, NO
SHOES_ROUTING verdict is trustworthy. These rails REDUCE cost + confident-wrongness;
they do NOT eliminate either — and they never say 'verified' or 'safe'.

The non-waivable misroute self-test (g) lives in BOTH: route_planner flags the
misroute at routing time; footing_check flags the degraded output at ship time. Both
must pass — that is the silent-quality-regression backstop made executable.
"""
import sys
import footing_check
import route_planner


def _misroute_end_to_end():
    """(g) THE PRIMARY-ADVERSARY TEST, end to end and NON-WAIVABLE:
    a task KNOWN to require Opus is misrouted to Haiku and yields a degraded draft
    (under-grounded + paraphrase-unstable). ROUTE-PLANNER must flag the misroute AND
    FOOTING must flag the degraded output before it ships."""
    # 1) routing time: planner flags routing a known-Opus task to the cheap tier.
    plan = route_planner.cheapest_path({"routine_generation": True, "required_tier": "opus"})
    assert plan["tier"] == "haiku", plan
    assert plan["misrouted_below_required_tier"] is True, ("planner missed the misroute", plan)

    # 2) ship time: the degraded Haiku draft (unverified claims + unstable paraphrases),
    #    carrying the required/routed tiers, MUST be flagged by FOOTING before shipping.
    degraded = {
        "claims": [{"text": "load-bearing assertion", "load_bearing": True, "check": None}],
        "paraphrase_answers": ["the bound is 14", "the bound is 9", "roughly 20"],
        "required_tier": "opus", "routed_tier": "haiku",
    }
    fv = footing_check.footing_check(degraded, compare_oracle=footing_check._equal_text)
    assert fv["uncertain"] is True, ("FOOTING missed the degraded misrouted draft", fv)
    assert fv["misrouted_below_required_tier"] is True, fv
    assert fv["action"] in ("ROUTE_UP", "GROUND_THEN_RECHECK", "ABSTAIN"), fv
    # and it must NOT have leaked any certification wording while flagging.
    footing_check._assert_no_forbidden_wording(fv)

    print("misroute (g) end-to-end selftest: PASS")
    print("  routing time: ROUTE-PLANNER flags Opus-needed task routed to Haiku (misrouted_below_required_tier)")
    print("  ship   time: FOOTING flags the degraded Haiku draft -> %s (no 'verified'/'safe' leak)" % fv["action"])


def _demo_honesty_no_overclaim():
    """(REGRESSION — AUDIT DEFECT 2: quality-claim tautology in the demo). The demo
    generates NO model output and compares none; both arms call the SAME deterministic
    verifier, so the machine-checkable check is TRUE BY CONSTRUCTION and carries NO
    quality claim. This test locks in the honest RELABEL: the over-claiming prediction
    key must be GONE, the by-construction key must be present, and the results must carry
    the explicit 'no model output / not a quality claim' disclaimer. It does NOT weaken
    any rail -- it only forbids the over-statement from creeping back."""
    import os
    import importlib.util
    demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_ab", "run_demo.py")
    spec = importlib.util.spec_from_file_location("_shoes_demo_under_test", demo_path)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    tasks = demo._make_tasks()
    A = demo.run_arm_A(tasks)
    B = demo.run_arm_B(tasks)

    # 1) The arms must NOT produce or compare any model output: the quality dict is filled
    #    purely from the per-task deterministic verifier lambda (identical on both arms).
    #    We prove "by construction" by checking BOTH arms report the SAME machine-checkable
    #    tally AND that the demo exposes no model-call surface (no 'model_output' anywhere).
    assert A["quality_machinecheckable"] == B["quality_machinecheckable"], (A, B)
    for arm in (A, B):
        assert "model_output" not in arm, ("demo must not claim model output", arm)

    # 2) The honestly-relabelled prediction key must be present and the over-claiming one GONE.
    #    (Re-derive the predictions dict via the module so a future rename is caught.)
    #    We read the source as the single source of truth for the committed key names.
    with open(demo_path, "r") as fh:
        src = fh.read()
    assert "P2_no_quality_regression_on_machinecheckable" not in src, (
        "AUDIT DEFECT 2 REGRESSION: the over-claiming prediction key "
        "'P2_no_quality_regression_on_machinecheckable' is back -- the demo must NOT claim "
        "'no quality regression' (no model output is generated; the check is by construction).")
    assert "P2_execute_preserves_exact_verifier_pass_BY_CONSTRUCTION_not_a_quality_claim" in src, (
        "the honestly-relabelled by-construction P2 key is missing")

    # 3) The results JSON and the demo docstring must state plainly: no model output is
    #    generated/compared, and P2 is NOT a quality claim (the auditor's required disclosure).
    assert "honesty_audit_DEFECT2" in src and "TRUE BY CONSTRUCTION" in src, src[:0]
    doc = (demo.__doc__ or "")
    assert "generates NO model output" in doc and "NOT an empirical quality result" in doc, (
        "the demo docstring must state plainly that no model output is generated and P2 is "
        "not an empirical quality result")

    print("demo honesty (DEFECT 2) selftest: PASS")
    print("  both arms run the SAME deterministic verifier -> P2 is TRUE BY CONSTRUCTION, NOT a quality claim")
    print("  over-claiming key 'no_quality_regression' is GONE; demo states plainly no model output is generated")


CHECKS = [
    ("FOOTING       (flag-high-disagreement / pass-grounded / wording-rail / uncomputable-honesty)",
     footing_check._selftest),
    ("ROUTE-PLANNER (execute/armor routing / per-track stuck-detector / no-false-halt / misroute-flag)",
     route_planner._selftest),
    ("MISROUTE (g)  (PRIMARY ADVERSARY, end-to-end: planner flags + FOOTING backstops — NON-WAIVABLE)",
     _misroute_end_to_end),
    ("DEMO HONESTY  (audit DEFECT 2 regression: P2 is by-construction, NOT a quality claim; no over-claim)",
     _demo_honesty_no_overclaim),
]

if __name__ == "__main__":
    print("=" * 80)
    print("SHOES_ROUTING frozen router-time rails — adversarial self-tests")
    print("=" * 80)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}\n    *** SELF-TEST FAILED (rail broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  {name}\n    *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    print("=" * 80)
    if failures:
        print(f"RAILS: {failures} self-test(s) failed — DO NOT TRUST any SHOES_ROUTING output.")
        sys.exit(1)
    print("RAILS: FOOTING flags under-grounded/unstable drafts & never says 'verified'/'safe'; "
          "ROUTE-PLANNER picks the cheapest rung, fires the per-track stuck-detector, and flags "
          "misroutes. Both backstop the misroute adversary (g). OK. (Reduces cost + confident-"
          "wrongness; eliminates neither.)")
