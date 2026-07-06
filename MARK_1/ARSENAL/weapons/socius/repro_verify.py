#!/usr/bin/env python3
"""S-REPRO — frozen verifier for REPRODUCIBILITY (kappa = 1).

A reproduction is verified iff an independently re-run analysis pipeline returns
a statistic numerically equal (within tolerance) to the value reported in the
source. This verifier does NOT trust the producer's word that "it reproduced" —
it compares the re-run number against the reported number and returns a verdict.

Honest ceiling: reproduction != truth. Reproducing a reported coefficient proves
the published number follows from the published data+code; it says NOTHING about
whether the finding is robust, causal, validly measured, or generalizable. Those
are separate sub-weapons (S-MULTIVERSE / S-CAUSAL / S-MEASURE / S-SAMPLE).

Independence: the checker is a pure numeric comparator; it is given (a) the
reported targets from the paper and (b) the values produced by a re-run that the
checker did not author. A false "reproduced" is detectable: change either number
and the verdict flips. This is what makes it a frozen verifier and not theater.
"""
import sys, json, math


def check_reproduction(reported, reproduced, rel_tol=0.02, abs_tol=1e-6):
    """reported, reproduced: dict {stat_name: value}. Returns a verdict dict.

    A statistic reproduces iff |repro - reported| <= max(abs_tol, rel_tol*|reported|).
    rel_tol default 2% — tight enough to catch a coding error (e.g. a 3x-off
    coefficient) but loose enough to absorb solver/library float differences.
    """
    details = {}
    all_ok = True
    missing = []
    for k, rep in reported.items():
        if k not in reproduced:
            missing.append(k)
            all_ok = False
            continue
        got = reproduced[k]
        tol = max(abs_tol, rel_tol * abs(rep))
        diff = abs(got - rep)
        ok = diff <= tol
        details[k] = {"reported": rep, "reproduced": got, "abs_diff": diff,
                      "tol": tol, "reproduced_ok": ok}
        all_ok = all_ok and ok
    return {
        "sub_weapon": "S-REPRO", "kappa": 1,
        "reproduced": bool(all_ok and not missing),
        "missing_statistics": missing,
        "rel_tol": rel_tol,
        "details": details,
        "ceiling_note": "Reproduction != discovery. A reproduced number is not "
                        "evidence the finding is robust/causal/valid/generalizable.",
    }


def _selftest():
    # Known-good: matching numbers within tolerance -> MUST report reproduced=True
    good = check_reproduction({"beta": 0.421, "se": 0.110},
                              {"beta": 0.420, "se": 0.111})
    assert good["reproduced"] is True, good
    # Known-broken: a 3x-off coefficient (a real coding-error signature)
    #   -> MUST report reproduced=False (the verifier must be able to FAIL)
    bad = check_reproduction({"beta": 0.421}, {"beta": 1.263})
    assert bad["reproduced"] is False, bad
    # Missing statistic -> not reproduced
    miss = check_reproduction({"beta": 0.4, "r2": 0.1}, {"beta": 0.4})
    assert miss["reproduced"] is False and miss["missing_statistics"] == ["r2"]
    print("repro_verify selftest: PASS (passes on match, FAILS on 3x-off + missing)")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) == 3:
        reported = json.load(open(sys.argv[1]))
        reproduced = json.load(open(sys.argv[2]))
        print(json.dumps(check_reproduction(reported, reproduced), indent=2))
    else:
        print("usage: repro_verify.py selftest | <reported.json> <reproduced.json>")
