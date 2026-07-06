#!/usr/bin/env python3
"""Killer demo for PSYMETRIX P-FORENSICS. Predictions committed in PREDICTION.md.

Demo A: reproduce the method papers' own published worked examples (grounded).
Demo B: controlled ground-truth corpus -> exact sensitivity/specificity of GRIM.

Run AFTER the gate (selftest_all.py) passes. Writes RESULT.json + prints a report.
The data in Demo B is generated from REAL integer samples (we control the ground
truth); no published author's numbers are accused. Demo A reproduces examples the
authors themselves published as method illustrations.
"""
import sys, os, json, statistics as st
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import forensics_verify as F

# deterministic LCG so the corpus is reproducible without touching global RNG
def lcg(seed):
    s = seed
    while True:
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        yield s
RNG = lcg(20260620)
def randint(a, b):
    return a + next(RNG) % (b - a + 1)


def demo_A():
    cases = [
        ("GRIM 5.27/n=43",      F.grim("5.27", 43),               "INCONSISTENT"),
        ("GRIM 5.26/n=43",      F.grim("5.26", 43),               "consistent"),
        ("GRIM 5.90/n=40/3item",F.grim("5.90", 40, items=3),      "consistent"),
        ("GRIMMER 3.44/2.47/18",F.grimmer("3.44", "2.47", 18),    "INCONSISTENT"),
    ]
    rows = []
    for label, res, predicted in cases:
        verdict = "consistent" if res["consistent"] else "INCONSISTENT"
        rows.append({"case": label, "predicted": predicted, "verdict": verdict,
                     "matches_prediction": verdict == predicted, "detail": res["note"]})
    return rows


def demo_B(n_rows=400):
    """Half correctly reported, half with a ±0.01 mean typo. Measure sens/spec."""
    clean_flagged = 0; clean_total = 0
    typo_caught = 0; typo_total = 0
    by_n_caught = {}; by_n_total = {}
    rows_detail = []
    for i in range(n_rows):
        n = randint(20, 80)
        sample = [randint(1, 7) for _ in range(n)]
        true_mean = sum(sample) / n
        ms = f"{true_mean:.2f}"
        corrupt = (i % 2 == 1)
        if corrupt:
            # planted transcription typo: shift last decimal by +/-0.01
            delta = 0.01 if (next(RNG) % 2 == 0) else -0.01
            reported = f"{true_mean + delta:.2f}"
            typo_total += 1
            by_n_total[n] = by_n_total.get(n, 0) + 1
            res = F.grim(reported, n)
            caught = (not res["consistent"]) and (not res["powerless"])
            typo_caught += int(caught)
            by_n_caught[n] = by_n_caught.get(n, 0) + int(caught)
        else:
            reported = ms
            clean_total += 1
            res = F.grim(reported, n)
            if not res["consistent"]:
                clean_flagged += 1
                rows_detail.append({"FALSE_POSITIVE": True, "n": n, "reported": reported,
                                    "true_mean": ms})
    specificity = 1 - clean_flagged / clean_total            # clean correctly passed
    sensitivity = typo_caught / typo_total                   # typos correctly caught
    # sensitivity by n bucket (small n should be higher)
    buckets = {"20-40": [0, 0], "41-60": [0, 0], "61-80": [0, 0]}
    for n in by_n_total:
        b = "20-40" if n <= 40 else "41-60" if n <= 60 else "61-80"
        buckets[b][0] += by_n_caught.get(n, 0); buckets[b][1] += by_n_total[n]
    sens_by_bucket = {b: (round(c / t, 3) if t else None) for b, (c, t) in buckets.items()}
    return {
        "n_rows": n_rows, "clean_total": clean_total, "clean_flagged": clean_flagged,
        "specificity_pct": round(100 * specificity, 2),
        "typo_total": typo_total, "typo_caught": typo_caught,
        "sensitivity_pct": round(100 * sensitivity, 2),
        "sensitivity_by_n_bucket": sens_by_bucket,
        "false_positives": rows_detail,
    }


if __name__ == "__main__":
    A = demo_A()
    B = demo_B()
    print("=" * 74)
    print("DEMO A — reproduce literature worked examples (grounded, non-accusatory)")
    print("=" * 74)
    for r in A:
        flag = "OK " if r["matches_prediction"] else "XX "
        print(f"  [{flag}] {r['case']:24s} predicted={r['predicted']:12s} -> {r['verdict']}")
    a_ok = all(r["matches_prediction"] for r in A)

    print("=" * 74)
    print("DEMO B — controlled ground-truth corpus (exact sensitivity/specificity)")
    print("=" * 74)
    print(f"  SPECIFICITY = {B['specificity_pct']}%  ({B['clean_total']-B['clean_flagged']}/{B['clean_total']} clean rows correctly passed)")
    print(f"  false positives (false accusations): {B['clean_flagged']}   <-- MUST be 0")
    print(f"  SENSITIVITY = {B['sensitivity_pct']}%  ({B['typo_caught']}/{B['typo_total']} typos caught)")
    print(f"  sensitivity by n: {B['sensitivity_by_n_bucket']}  (should DECREASE with n)")

    # check predictions
    spec_ok = B["clean_flagged"] == 0
    sens_ok = 0 < B["sensitivity_pct"] < 100
    sb = B["sensitivity_by_n_bucket"]
    mono_ok = sb["20-40"] >= sb["41-60"] >= sb["61-80"]
    print("=" * 74)
    print("PREDICTION CHECK:")
    print(f"  Demo A all match literature ........ {'PASS' if a_ok else 'FAIL'}")
    print(f"  Specificity == 100% (zero FP) ...... {'PASS' if spec_ok else 'FAIL'}")
    print(f"  0% < Sensitivity < 100% (incomplete) {'PASS' if sens_ok else 'FAIL'}")
    print(f"  Sensitivity decreases with n ....... {'PASS' if mono_ok else 'FAIL'}")
    out = {"demo_A": A, "demo_B": B, "checks": {
        "demoA_matches_literature": a_ok, "specificity_100": spec_ok,
        "sensitivity_strictly_between": sens_ok, "sensitivity_monotone_in_n": mono_ok}}
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(out, open(os.path.join(here, "RESULT.json"), "w"), indent=2)
    print("\nwrote RESULT.json")
    if not (a_ok and spec_ok and sens_ok):
        sys.exit(1)
