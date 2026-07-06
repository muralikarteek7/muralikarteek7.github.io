#!/usr/bin/env python3
"""test_equip.py — machine check for the EQUIP loadout selector.
Each case = a battle description -> the style we expect equipped. Run: python3 test_equip.py
"""
from equip import equip

# (battle text, expected primary style, expect_warlord)
CASES = [
    ("Should I migrate our Postgres to a managed service? Give me your recommendation.", "SAGE", False),
    ("Brainstorm names for the product and explain the tradeoffs.", "SAGE", False),
    ("Research the literature on diffusion models and survey the state of the art.", "SCHOLAR", False),
    ("Find the prior work and sources on protein folding scoring functions.", "SCHOLAR", False),
    ("Write a journal paper draft on our results, with the right style.", "SCRIBE", False),
    ("Draft a blog article about the launch.", "SCRIBE", False),
    ("Build a REST api and implement the caching feature in this code.", "ARCHITECT", False),
    ("Refactor this script and design the pipeline architecture.", "ARCHITECT", False),
    ("Prove this lemma and construct the exact cap set for n=6.", "PROVER", False),
    ("Optimize this exactly and give me a formal Lean proof.", "PROVER", False),
    ("Reproduce this study and run a multiverse robustness audit on the regression.", "AUDITOR", False),
    ("Fact-check this claim and check the p-value with GRIM.", "AUDITOR", False),
    ("Do a defensive security threat model and harden the auth against injection.", "SENTINEL", False),
    ("Find the attack surface for this CTF and pentest it (authorized).", "SENTINEL", False),
    ("Explore this dataset and visualize the trends with a dashboard.", "ANALYST", False),
    ("Run exploratory data analysis and plot the correlation.", "ANALYST", False),
    # multi-front -> WARLORD
    ("Research the literature, then build the api and prove the algorithm is exact.", None, True),
    ("Audit this study for fraud and write the paper reproducing it.", None, True),
]


ALL_WEAPONS = {"FRONTIER_CONSTRUCTION", "SOCIUS", "PSYMETRIX", "OPTIMA", "SYMBOLICA", "CODEFORGE",
               "PROOFSMITH", "TRIALGUARD", "ECONOMETRIX", "FACTHARNESS", "REDCELL", "REPRO-ML", "ENCLOSE"}
ALL_KIT = {"GLOVES", "SHIELD", "SHOES", "VAULT", "TRIAGE", "CRUCIBLE", "BOOTSTRAP", "COMPOSEAUTH"}


def coverage():
    """Every weapon and every kit piece must be reachable by at least one style/route (audit BLOCKER)."""
    import json, itertools
    from pathlib import Path
    reg = json.loads(Path("LOADOUTS.json").read_text())
    reached_w, reached_k = set(), set(reg["always_equipped"]["kit"])
    for spec in reg["styles"].values():
        reached_w |= set(spec["weapons"]); reached_k |= set(spec["kit"])
    reached_k |= set(reg["WARLORD"].get("meta_kit", []))   # BOOTSTRAP via WARLORD
    miss_w, miss_k = ALL_WEAPONS - reached_w, ALL_KIT - reached_k
    ok = not miss_w and not miss_k
    print(f"coverage: {'OK' if ok else 'FAIL'}  weapons {len(reached_w)}/{len(ALL_WEAPONS)}  kit {len(reached_k)}/{len(ALL_KIT)}")
    if miss_w: print(f"  unreachable weapons: {sorted(miss_w)}")
    if miss_k: print(f"  unreachable kit: {sorted(miss_k)}")
    return ok


def run():
    passed = 0
    failed = []
    for text, expected, expect_warlord in CASES:
        r = equip(text)
        ok_style = (expected is None) or (r["styles"][0] == expected) or (expected in r["styles"])
        ok_war = (r["warlord"] == expect_warlord)
        if ok_style and ok_war:
            passed += 1
        else:
            failed.append((text, expected, expect_warlord, r["styles"], r["warlord"], r["_scores"]))
    print(f"EQUIP test: {passed}/{len(CASES)} passed")
    for text, exp, ew, got, gw, sc in failed:
        print(f"  FAIL: {text!r}\n        expected style~{exp} warlord={ew}; got {got} warlord={gw} scores={sc}")
    return passed == len(CASES)


if __name__ == "__main__":
    import sys
    ok = run() and coverage()
    sys.exit(0 if ok else 1)
