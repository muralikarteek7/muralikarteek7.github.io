#!/usr/bin/env python3
"""CRUCIBLE-v2 — DIFFERENTIAL test of REPROML's EXACT n-gram contamination leg.

REPROML's R-CONTAM detects verbatim leakage via word-n-gram SET INTERSECTION. That leg is exact (set
membership), so it is differentially testable. Independent oracle = SUBSTRING SEARCH on the space-joined
token stream (a genuinely different collision mechanism; shares only the tokenizer _tok, a separately-
trusted primitive). For each eval doc both methods must agree on "shares an n-gram with the train set".
A disagreement = a real implementation bug in the exact leg. Deterministic, seeded."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/reproml")
import contam_verify as RC


class LCG:
    def __init__(s, seed): s.x = seed & 0xFFFFFFFF
    def nx(s): s.x = (1103515245 * s.x + 12345) & 0x7FFFFFFF; return s.x
    def ri(s, lo, hi): return lo + s.nx() % (hi - lo + 1)
    def pick(s, seq): return seq[s.nx() % len(seq)]


VOCAB = [f"w{i}" for i in range(60)]


def rand_doc(r, lo, hi):
    return " ".join(r.pick(VOCAB) for _ in range(r.ri(lo, hi)))


def oracle_ngram_hit(eval_doc, train_docs, n):
    """INDEPENDENT: does any n-consecutive-token span of eval appear (as a contiguous span) in any train
    doc? Implemented by SUBSTRING SEARCH on the space-padded token stream (NOT set intersection)."""
    et = RC._tok(eval_doc)
    if len(et) < n:
        return False
    train_streams = [" " + " ".join(RC._tok(t)) + " " for t in train_docs]
    for j in range(len(et) - n + 1):
        span = " " + " ".join(et[j:j + n]) + " "
        if any(span in ts for ts in train_streams):
            return True
    return False


def run(rounds=4000, seed=20260621, n=4):
    r = LCG(seed)
    kills = []; cases = 0; dirty_seen = 0
    for _ in range(rounds):
        ntrain = r.ri(2, 6)
        train = [rand_doc(r, n, n + 8) for _ in range(ntrain)]
        eval_docs = []
        for _ in range(r.ri(2, 5)):
            if r.ri(0, 1):                                   # plant a verbatim span from a train doc
                src = RC._tok(r.pick(train))
                if len(src) >= n:
                    start = r.ri(0, max(0, len(src) - n))
                    span = src[start:start + n]
                    pad = [r.pick(VOCAB) for _ in range(r.ri(0, 4))]
                    eval_docs.append(" ".join(pad + span + pad))
                    continue
            eval_docs.append(rand_doc(r, 1, n + 6))          # random (maybe accidentally overlapping)
        rep = RC.contamination_report(train, eval_docs, n=n, jaccard_threshold=2.0, bow_threshold=2.0)
        # thresholds set to 2.0 (impossible) so ONLY the n-gram leg can flag -> isolates the exact leg.
        rep_hit = {d["eval_index"]: d["ngram_collision"] for d in rep["dirty_items"]}
        for i, ed in enumerate(eval_docs):
            cases += 1
            gate = bool(rep_hit.get(i, False))               # reproml: ngram_collision (False if not flagged)
            truth = oracle_ngram_hit(ed, train, n)
            if truth: dirty_seen += 1
            if gate != truth:
                kills.append(("NGRAM-DISAGREE", "gate", gate, "oracle", truth, ed, train))
    print(f"CRUCIBLE-v2 REPROML n-gram leg differential — INDEPENDENT oracle = substring-search collision")
    print(f"  seed={seed} n={n} rounds={rounds} eval-docs={cases} (true-dirty={dirty_seen})")
    if kills:
        print(f"  *** {len(kills)} KILL(s) ***")
        for k in kills[:8]:
            print("   -", k[:5], "| eval=", repr(k[5])[:60])
    else:
        print("  RESULT: SURVIVED — reproml's exact n-gram collision detector AGREED with the independent")
        print("          substring-search oracle on EVERY eval doc (verbatim leaks caught, clean items not")
        print("          flagged). The exact leg is now differential-tested (was metamorphic-only).")
        print("          (NOTE: the fuzzy char-Jaccard/BOW legs + the paraphrase-evasion ceiling are NOT")
        print("           covered here — those are threshold-dependent, no exact oracle, by design.)")
    return kills


if __name__ == "__main__":
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    ks = run(rounds)
    sys.exit(1 if ks else 0)
