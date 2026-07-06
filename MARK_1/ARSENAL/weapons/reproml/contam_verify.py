#!/usr/bin/env python3
"""R-CONTAM (kappa~0.8) — train/test contamination detector.

Measures overlap between a training corpus and an eval set two ways:
  * N-GRAM COLLISION (default 13-gram, GPT-3/Brown 2020 decontamination convention):
    an eval item is "dirty" if ANY of its token n-grams also occurs anywhere in the
    training corpus. Reported as a RATE over eval items.
  * CHAR-JACCARD NEAR-DUP: catches lightly-edited copies (an eval item whose character
    n-gram set is >= threshold Jaccard-similar to some train item).

HONESTY: contamination is reported as a MEASURED RATE + a method label, NEVER a binary
"clean". Absence of detected overlap != proof of no contamination — pure n-gram misses
rephrased/translated leakage (documented; stated on every report).
"""
import re


def _tok(s):
    return re.findall(r"[a-z0-9]+", str(s).lower())


def _word_ngrams(tokens, n):
    if len(tokens) < n:
        # short item: use the whole thing as one gram so it can still collide
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def _char_ngrams(s, n=5):
    s = re.sub(r"\s+", " ", str(s).lower()).strip()
    if len(s) < n:
        return {s} if s else set()
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def _jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def contamination_report(train_docs, eval_docs, n=13, jaccard_threshold=0.8,
                         bow_threshold=0.9):
    """Returns a contamination report over the eval set.

    train_docs, eval_docs: lists of strings.
    n: word n-gram order for collision (default 13, GPT-3 convention).
       WARNING: n < 10 risks FALSE POSITIVES on common English phrases (audit A6);
       a warning is emitted. The GPT-3 standard is n=13.
    jaccard_threshold: char-5gram Jaccard >= this counts as a near-duplicate (lightly-edited copy).
    bow_threshold: ORDER-INSENSITIVE token-set Jaccard >= this counts as a near-dup too
       (audit fix A5: catches word-REORDERING, which evades both n-gram order and char-5gram).
    """
    if n < 10:
        import warnings
        warnings.warn(f"R-CONTAM: n={n} < 10 risks false positives on common phrases; "
                      "GPT-3 standard is n=13.", stacklevel=2)
    # build the train n-gram universe once
    train_grams = set()
    for d in train_docs:
        train_grams |= _word_ngrams(_tok(d), n)
    train_char = [_char_ngrams(d) for d in train_docs]
    train_bow = [set(_tok(d)) for d in train_docs]

    dirty_ngram, dirty_neardup, dirty_reorder, dirty_items = 0, 0, 0, []
    for idx, d in enumerate(eval_docs):
        eg = _word_ngrams(_tok(d), n)
        ngram_hit = bool(eg & train_grams)
        ec = _char_ngrams(d)
        best_j = max((_jaccard(ec, tc) for tc in train_char), default=0.0)
        neardup_hit = best_j >= jaccard_threshold
        ebow = set(_tok(d))
        best_bow = max((_jaccard(ebow, tb) for tb in train_bow), default=0.0)
        # only count a bag-of-words hit as REORDER evidence when the char-similarity is
        # low (i.e. it is NOT already a verbatim/near-verbatim copy) -- a high word-set
        # overlap with a different surface form is the reorder/shuffle signature.
        reorder_hit = best_bow >= bow_threshold
        if ngram_hit:
            dirty_ngram += 1
        if neardup_hit:
            dirty_neardup += 1
        if reorder_hit and not (ngram_hit or neardup_hit):
            dirty_reorder += 1
        if ngram_hit or neardup_hit or reorder_hit:
            dirty_items.append({"eval_index": idx,
                                "ngram_collision": ngram_hit,
                                "near_dup_jaccard": round(best_j, 3),
                                "near_dup": neardup_hit,
                                "bow_jaccard": round(best_bow, 3),
                                "word_reorder": bool(reorder_hit and not neardup_hit)})
    total = len(eval_docs)
    dirty = len(dirty_items)
    rate = dirty / total if total else 0.0
    return {
        "sub_weapon": "R-CONTAM", "kappa": 0.8,
        "method": f"{n}-gram word collision (GPT-3/Brown 2020 convention) + "
                  f"char-5gram Jaccard near-dup >= {jaccard_threshold} + "
                  f"order-insensitive token-set Jaccard >= {bow_threshold} (reorder)",
        "n_eval": total, "n_train": len(train_docs),
        "contaminated_items": dirty,
        "contamination_rate": round(rate, 4),
        "by_ngram_collision": dirty_ngram, "by_near_dup": dirty_neardup,
        "by_word_reorder": dirty_reorder,
        "dirty_items": dirty_items,
        "verdict": ("CONTAMINATION_DETECTED" if dirty else "NO_OVERLAP_DETECTED"),
        "ceiling_note": "A measured overlap RATE, not a binary 'clean'. NO_OVERLAP_DETECTED "
                        "!= clean: n-gram + char-Jaccard + token-set catch verbatim, "
                        "lightly-edited, and word-REORDERED leakage, but still MISS rephrased/"
                        "translated/paraphrased leakage (different words). Reported with its "
                        "method label so it is reproducible.",
    }


if __name__ == "__main__":
    # smoke: inject eval items into 'train' -> must detect overlap
    eval_set = ["the quick brown fox jumps over the lazy dog near the river bank today",
                "a completely unrelated sentence about photosynthesis in green plants here"]
    train_clean = ["machine learning models are trained on large corpora of varied text data"]
    train_dirty = train_clean + [eval_set[0]]   # leaked the first eval item
    clean = contamination_report(train_clean, eval_set, n=5)
    dirty = contamination_report(train_dirty, eval_set, n=5)
    print("clean train:", clean["verdict"], clean["contamination_rate"])
    print("dirty train:", dirty["verdict"], dirty["contamination_rate"])
    assert clean["contaminated_items"] == 0
    assert dirty["contaminated_items"] == 1
    print("contam_verify smoke: PASS")
