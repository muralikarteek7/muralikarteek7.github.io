#!/usr/bin/env python3
"""S-GROUND end-to-end demo: ground 8 prose claims against 3 real fetched abstracts.

Layer 1 (κ=1, frozen) runs offline against the recorded source text (sources.json).
Layer 2 (κ=0) entailment verdicts for the two paraphrase claims (C7, C8) were
produced by a cross-model judge (Sonnet ≠ the Opus generator) and are recorded
verbatim below with judge_model attribution. Compares to PREDICTION.md.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ground_verify

SRC = json.load(open(os.path.join(HERE, "sources.json")))
DUR = SRC["durante2013"]; STE = SRC["steegen2016"]; SCO = SRC["scott_pound2015"]

# κ=0 entailment verdicts from the cross-model judge (Sonnet), recorded verbatim.
JUDGE = "claude-sonnet-4-6"
ENT_C7 = {"verdict": "entailed", "judge_model": JUDGE,
          "rationale": "Steegen (2016) shows the effect is fragile/sensitive to data "
                       "choices and Scott & Pound (2015, n=2213) found no evidence — "
                       "together the reliability of the effect is broadly questioned."}
ENT_C8 = {"verdict": "not_entailed", "judge_model": JUDGE,
          "rationale": "Scott & Pound (2015) explicitly found 'no evidence of a "
                       "relationship', directly contradicting a 'confirmed' claim."}

CLAIMS = [
    ("C1", {"text": "Durante et al. (2013): ovulation led single women to become more liberal, less religious.",
            "source_text": DUR["abstract"],
            "quote": "Ovulation led single women to become more liberal, less religious",
            "claimed_authors": "Durante Rae Griskevicius", "claimed_year": 2013,
            "source_metadata": {"authors": DUR["authors"], "year": DUR["year"]}}),
    ("C2", {"text": "Steegen et al. (2016): conclusions change because of arbitrary choices in data construction.",
            "source_text": STE["abstract"],
            "quote": "arbitrary choices in data construction",
            "claimed_authors": "Steegen Tuerlinckx Gelman Vanpaemel", "claimed_year": 2016,
            "source_metadata": {"authors": STE["authors"], "year": STE["year"]}}),
    ("C3", {"text": "Scott & Pound (2015): no evidence of a relationship, robust to multiple inclusion/exclusion criteria.",
            "source_text": SCO["abstract"],
            "quote": "no evidence of a relationship",
            "numbers": [{"value": "2213", "context": "women"}],
            "claimed_authors": "Scott Pound", "claimed_year": 2015,
            "source_metadata": {"authors": SCO["authors"], "year": SCO["year"]}}),
    ("C4", {"text": "Durante et al. (2013) concluded the ovulation effect was weak and likely spurious.",
            "source_text": DUR["abstract"],
            "quote": "the ovulation effect was weak and likely spurious"}),   # FABRICATED
    ("C5", {"text": "Smith & Jones (2013) authored 'The Fluctuating Female Vote'.",
            "source_text": DUR["abstract"],
            "claimed_authors": "Smith Jones", "claimed_year": 2013,
            "source_metadata": {"authors": DUR["authors"], "year": DUR["year"]}}),  # wrong author
    ("C6", {"text": "Steegen et al. (2016) reported exactly 7 of 120 significant specifications.",
            "source_text": STE["abstract"],
            "numbers": [{"value": "120", "context": "specifications"}]}),  # number not in abstract
    ("C7", {"text": "The broader literature now questions whether the ovulation-politics effect is reliable.",
            "source_text": STE["abstract"] + " " + SCO["abstract"],
            "entailment_verdict": ENT_C7}),                                # paraphrase, κ=0
    ("C8", {"text": "Scott & Pound (2015) confirmed that ovulation reliably increases conservatism.",
            "source_text": SCO["abstract"],
            "entailment_verdict": ENT_C8}),                                # paraphrase, κ=0
]

PREDICTED = {"C1": "GROUNDED", "C2": "GROUNDED", "C3": "GROUNDED",
             "C4": "FABRICATION_FLAG", "C5": "FABRICATION_FLAG", "C6": "FABRICATION_FLAG",
             "C7": "GROUNDED_BY_JUDGMENT", "C8": "CONTRADICTED_BY_SOURCE"}


def main():
    results = {}
    print("=" * 78)
    print("SOCIUS S-GROUND demo — grounding 8 claims against 3 real fetched abstracts")
    print("=" * 78)
    n_correct = 0
    for cid, claim in CLAIMS:
        out = ground_verify.verify_grounding(claim)
        results[cid] = out
        pred = PREDICTED[cid]
        hit = (out["overall"] == pred)
        n_correct += hit
        print(f"{cid}: {out['overall']:24s} predicted {pred:24s} {'OK' if hit else 'MISS'}")
    print("-" * 78)
    print(f"predictions correct: {n_correct}/8")
    print("RAILS: a FABRICATION_FLAG = 'this quote/number/author does not check against "
          "the SUPPLIED source' — NOT an accusation of fraud (rounding/typo/wrong-source/"
          "paraphrase are all possible). Entailment (C7/C8) is κ=0, judged by "
          f"{JUDGE} ≠ the Opus generator.")
    with open(os.path.join(HERE, "ground_results.json"), "w") as f:
        json.dump({"results": results, "predicted": PREDICTED,
                   "n_correct": n_correct}, f, indent=2, default=str)


if __name__ == "__main__":
    main()
