#!/usr/bin/env python3
"""Consolidate the A/B rounds into RESULT.json (per-task per-arm success, frozen-verified)."""
import json

# per task: ONESHOT (attempt#1 of best-of-4), BEST-OF-4 (any of 4), ITERATE (final verified), rounds used
TASKS = {
    # family F1 = SORTNET-MIN
    "s_n5b12": {"family": "sortnet", "oneshot": 1, "bestof4": 1, "iterate": 1, "iter_rounds": 1, "band": "saturated"},
    "s_n6b16": {"family": "sortnet", "oneshot": 1, "bestof4": 1, "iterate": 1, "iter_rounds": 1, "band": "saturated"},
    "s_n7b21": {"family": "sortnet", "oneshot": 0, "bestof4": 1, "iterate": 1, "iter_rounds": 2, "band": "IN_BAND"},
    "s_n8b28": {"family": "sortnet", "oneshot": 1, "bestof4": 1, "iterate": 1, "iter_rounds": 1, "band": "saturated"},
    # family F2 = SYNTH-MUTATION
    "y_reset":        {"family": "synth", "oneshot": 1, "bestof4": 1, "iterate": 1, "iter_rounds": 1, "band": "saturated"},
    "y_countsmaller": {"family": "synth", "oneshot": 1, "bestof4": 1, "iterate": 1, "iter_rounds": 1, "band": "saturated"},
}

n = len(TASKS)
agg = {
    "oneshot_success": sum(t["oneshot"] for t in TASKS.values()),
    "bestof4_success": sum(t["bestof4"] for t in TASKS.values()),
    "iterate_success": sum(t["iterate"] for t in TASKS.values()),
    "n_tasks": n,
}
agg["iterate_minus_bestof4_pp"] = round(100 * (agg["iterate_success"] - agg["bestof4_success"]) / n, 1)
agg["iterate_minus_oneshot_pp"] = round(100 * (agg["iterate_success"] - agg["oneshot_success"]) / n, 1)

in_band = {k: t for k, t in TASKS.items() if t["band"] == "IN_BAND"}
result = {
    "experiment": "CODEFORGE capability A/B (verifier-gated iterate vs equal-compute best-of-k)",
    "writer": "claude-haiku-4-5", "K": 4, "scoring": "frozen verifiers; agent self-reports ignored",
    "per_task": TASKS,
    "aggregate": agg,
    "in_band_tasks": list(in_band.keys()),
    "n7_iterate_trajectory": {
        "r1": "16-comparator network — INVALID (fails to sort [1,1,0,0,0,0,0]); feedback given",
        "r2": "20-comparator network — VALID (used the rich feedback). 2 of 4 calls used.",
        "bestof4_on_n7": "VALID via blind resampling (1 of 4 independent attempts valid)",
        "verdict": "iterate USED feedback and reached success, but best-of-4 ALSO succeeded at equal budget -> +0pp",
    },
    "verifier_caught_bluffs": [
        "n5 best-of-4 attempt #4: claimed 8-comparator n=5 sorter — IMPOSSIBLE (proven optimum 9); rejected.",
        "n7 iterate r1: agent claimed 'optimal 16 comparators' — INVALID (re-verified, fails [1,1,0,0,0,0,0]).",
        "n8 iterate r1: agent claimed 'verified on all 40320 permutations' — re-verified independently (true this time).",
        "n7 best-of-4: 3 of 4 attempts INVALID; only attempt #2 a real sorter. self-reports never trusted.",
    ],
    "VERDICT": ("HONEST NEGATIVE / NO-SIGNAL. iterate - best-of-k = +0pp. Where one-shot succeeds "
                "(n<=6, n8, both synth) the arms saturate; the ONE in-band task (n7) is a TIE — feedback "
                "engaged but did not beat matched-budget resampling. Feedback was never the active "
                "ingredient (attempts were). The >=10% bar is NOT met. NO promotion; capability ratchet "
                "stays OPEN at v3. Reproduces the owned v5 lesson in a fresh RICH-feedback code arena; "
                "the faithful at-scale test remains INFRA-GATED (V5_INFRA_UNLOCK_SPEC.md)."),
}
json.dump(result, open("RESULT.json", "w"), indent=2)
print(json.dumps(agg, indent=2))
print("VERDICT:", result["VERDICT"])
