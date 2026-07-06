#!/usr/bin/env python3
"""R-REPRO (kappa~0.7) — does the reported metric RECOMPUTE from open artifacts?

Reproduction = recompute from predictions+labels, NOT re-quote a paper's number.
Supports accuracy and macro-F1. A metric you cannot recompute from artifacts is
UNVERIFIED (not 'reproduced'). Reuses the SOCIUS S-REPRO doctrine (re-run, not re-cite).
"""
import numpy as np


def accuracy(preds, labels):
    p = np.asarray(preds); y = np.asarray(labels)
    return float((p == y).mean())


def macro_f1(preds, labels):
    p = np.asarray(preds); y = np.asarray(labels)
    classes = sorted(set(y.tolist()) | set(p.tolist()))
    f1s = []
    for c in classes:
        tp = int(np.sum((p == c) & (y == c)))
        fp = int(np.sum((p == c) & (y != c)))
        fn = int(np.sum((p != c) & (y == c)))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        f1s.append(f1)
    return float(np.mean(f1s)) if f1s else 0.0


_METRICS = {"accuracy": accuracy, "macro_f1": macro_f1}


def reproduce(reported_value, preds, labels, metric="accuracy", tol=1e-3):
    """Recompute `metric` from preds+labels; compare to the reported value within tol.

    NOTE (audit A9b): tol=1e-3 intentionally tolerates up to ~0.1pp of paper-to-digit
    reporting rounding -> an inflation up to ~0.1pp will still pass as REPRODUCED. This
    is a disclosed design window, not a bug. A tiny FP epsilon is added to the boundary
    so a value exactly at `true + tol` is not failed by float-addition rounding."""
    if metric not in _METRICS:
        return {"sub_weapon": "R-REPRO", "kappa": 0.7, "verdict": "UNSUPPORTED_METRIC",
                "metric": metric, "reproduced": False}
    recomputed = _METRICS[metric](preds, labels)
    delta = abs(recomputed - float(reported_value))
    ok = delta <= tol + 1e-9
    return {"sub_weapon": "R-REPRO", "kappa": 0.7, "metric": metric,
            "reported": float(reported_value), "recomputed": round(recomputed, 6),
            "abs_delta": round(delta, 6), "tolerance": tol,
            "reproduced": bool(ok),
            "verdict": "REPRODUCED" if ok else "DOES_NOT_REPRODUCE",
            "ceiling_note": f"Recomputed from artifacts (not re-quoted). REPRODUCED means the "
                            f"number checks out within tol={tol} (~{tol*100:.1f}pp reporting "
                            "rounding is tolerated by design); it is NOT a claim the benchmark "
                            "is uncontaminated or that the model is best."}


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    labels = rng.integers(0, 3, 200)
    preds = labels.copy()
    flip = rng.choice(200, 40, replace=False)   # 20% wrong -> acc 0.80
    preds[flip] = (preds[flip] + 1) % 3
    true_acc = accuracy(preds, labels)
    good = reproduce(true_acc, preds, labels, "accuracy")
    bad = reproduce(0.95, preds, labels, "accuracy")   # over-claimed
    print("faithful:", good["verdict"], good["recomputed"])
    print("inflated:", bad["verdict"], bad["reported"], "vs", bad["recomputed"])
    assert good["reproduced"] is True
    assert bad["reproduced"] is False
    print("repro_verify smoke: PASS")
