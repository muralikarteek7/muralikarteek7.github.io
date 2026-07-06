#!/usr/bin/env python3
"""FACTHARNESS killer demo: ground 6 claims against a REAL fetched source.
Catches a fabricated quote, a fabricated number, a wrong-author cite; grounds two
faithful claims; abstains on a genuine entailment ambiguity. Predictions committed
in PREDICTION.md BEFORE this ran.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factharness import ground
from factharness_router import firewall

# Verbatim source text fetched 2026-06-20 from Wikipedia "Strassen algorithm".
SRC = ("It is faster than the standard matrix multiplication algorithm for large "
       "matrices, with a better asymptotic complexity O(n^log2 7) versus O(n^3). "
       "Volker Strassen first published this algorithm in 1969 and thereby proved "
       "that the n^3 general matrix multiplication algorithm was not optimal. The "
       "Strassen algorithm defines instead new values using only 7 multiplications "
       "(one for each Mk) instead of 8. A 2010 study found that even a single step "
       "of Strassen's algorithm is often not beneficial on current architectures, "
       "compared to a highly optimized traditional multiplication, until matrix "
       "sizes exceed 1000 or more.")
META = {"authors": "Volker Strassen", "year": 1969}

claims = [
    # 1 faithful quote + real number -> GROUNDED
    {"text": "Strassen published the algorithm in 1969.",
     "source_text": SRC, "quote": "Volker Strassen first published this algorithm in 1969",
     "numbers": [{"value": "1969", "context": "published"}]},
    # 2 FABRICATED quote (source says 7, not "six") -> FABRICATION_FLAG
    {"text": "Strassen requires only six multiplications.",
     "source_text": SRC, "quote": "the algorithm requires only six multiplications instead of eight"},
    # 3 FABRICATED number -> FABRICATION_FLAG
    {"text": "Strassen uses 11 multiplications.",
     "source_text": SRC, "numbers": [{"value": "11", "context": "multiplications"}]},
    # 4 WRONG-AUTHOR cite -> FABRICATION_FLAG
    {"text": "Per Williams and Page (1969), ...",
     "source_text": SRC, "claimed_authors": "Williams and Page", "claimed_year": 1969,
     "source_metadata": META},
    # 5 faithful real numbers -> GROUNDED
    {"text": "Strassen uses 7 multiplications instead of 8.",
     "source_text": SRC, "numbers": [{"value": "7", "context": "multiplications"},
                                      {"value": "1969", "context": "published"}]},
    # 6 genuine entailment ambiguity, judge uncertain, no verbatim quote -> ABSTAIN
    {"text": "Strassen changes the asymptotic behaviour of matrix multiplication.",
     "source_text": SRC,
     "entailment_verdict": {"verdict": "uncertain", "judge_model": "sonnet (cross-model, != generator)",
                            "rationale": "the source states a better asymptotic complexity but the "
                                         "phrasing 'changes the asymptotic behaviour' is a paraphrase "
                                         "the source neither verbatim states nor clearly refutes"}},
]

PRED = ["GROUNDED", "FABRICATION_FLAG", "FABRICATION_FLAG", "FABRICATION_FLAG",
        "GROUNDED", "ABSTAIN"]

results = []
print("=== FACTHARNESS demo: 6 claims vs real Wikipedia source ===\n")
allok = True
for i, (c, pred) in enumerate(zip(claims, PRED), 1):
    r = ground(c)
    got = r["overall"]
    match = "OK " if got == pred else "** MISMATCH **"
    if got != pred:
        allok = False
    print(f"[{i}] predicted={pred:18s} got={got:18s} {match}  | {c['text']}")
    results.append({"claim": c["text"], "predicted": pred, "overall": got, "detail": r})

fw = firewall(claims)
print(f"\nFirewall over batch: ship_ok={fw['ship_ok']} "
      f"(grounded={len(fw['grounded'])}, needs_label={len(fw['needs_label'])}, "
      f"blocked={len(fw['blocked'])})")
print("Predicted: ship_ok=False, grounded=2, needs_label=1, blocked=3")

ok = (allok and fw["ship_ok"] is False and len(fw["grounded"]) == 2
      and len(fw["needs_label"]) == 1 and len(fw["blocked"]) == 3)
json.dump({"results": results, "firewall": fw, "all_predictions_matched": ok},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"), "w"),
          indent=2)
print("\n" + ("DEMO PASS: all 6 predictions matched + firewall as predicted." if ok
              else "DEMO MISMATCH: see above."))
sys.exit(0 if ok else 1)
