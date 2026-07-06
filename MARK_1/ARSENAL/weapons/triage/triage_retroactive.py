#!/usr/bin/env python3
"""TRIAGE retroactive re-flag — the NON-WAIVABLE proof of value (audit banner #1).

The kickoff's independent audit (READY-WITH-FIXES) made this the load-bearing test:
'make retroactive re-flagging of >=3 known past failures a NON-WAIVABLE self-test (with
committed predictions on which rows fire) -- that IS the proof of value.'

Here we feed >=3 faithful reconstructions of REAL failures the human audits caught by
hand (from Legacy/EVOLUTION_LOG.md) and assert TRIAGE re-fires the SAME row each human
audit named. The committed predictions are in demo_retroactive/PREDICTION.md (written
BEFORE this code was run); they are repeated here as `EXPECTED` so the assertion is
self-contained and machine-checkable.
"""
import triage_check as tc

# (name, builder, the row a HUMAN audit caught by hand) -- committed in PREDICTION.md.
CASES = [
    ("C39 SYMBOLICA branch-cut (log(x^2)=2log(x) certified globally)",
     tc.real_failure_symbolica_branch_cut,        "numeric-branch-cut-convergence"),
    ("C41 PROOFSMITH answer-key LEAK (provers read reference_proofs.lean off disk)",
     tc.real_failure_proofsmith_answer_key_leak,   "circular-measurement"),
    ("C38 OPTIMA malformed-input (missing-var; detector silent-passes junk)",
     tc.real_failure_optima_malformed_crash,       "crash-silent-pass-on-malformed-input"),
]


def run(verbose=False):
    """Return a list of {case, expected_row, fired_rows, reflagged}. Asserts each
    reconstructed real failure re-fires the row the human audit caught."""
    results = []
    for name, build, expected_row in CASES:
        rec = build()
        report = tc.triage_check(rec)
        fired = report["fired_classes"]
        reflagged = expected_row in fired
        results.append({"case": name, "expected_row": expected_row,
                        "fired_rows": fired, "reflagged": reflagged})
        if verbose:
            mark = "RE-FLAGGED" if reflagged else "MISSED"
            print(f"  [{mark}] {name}\n      expected row: {expected_row}\n      fired: {fired}")
    return results


def _selftest():
    results = run(verbose=False)
    assert len(CASES) >= 3, "need >=3 real past failures (non-waivable)"
    for r in results:
        assert r["reflagged"], (f"RETROACTIVE RE-FLAG FAILED: {r['case']} did NOT re-fire "
                                f"{r['expected_row']!r}; fired={r['fired_rows']}")
    print(f"triage_retroactive selftest: PASS ({len(results)}/{len(results)} real past failures "
          "RE-FLAGGED the exact row the human audit caught: " +
          "; ".join(r["expected_row"] for r in results) + ")")


if __name__ == "__main__":
    print("TRIAGE retroactive re-flag of REAL past failures:")
    run(verbose=True)
    _selftest()
