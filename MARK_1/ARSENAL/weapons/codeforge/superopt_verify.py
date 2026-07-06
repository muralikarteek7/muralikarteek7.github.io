#!/usr/bin/env python3
"""SUPEROPT — frozen verifier for superoptimization: "faster AND still correct".
kappa = 1 on CORRECTNESS (the gate); the speedup is a MEASUREMENT, not a certificate.

A superopt candidate claims to compute the same function as a reference (often naive)
implementation, but faster/smaller. The win is a NON-GAMEABLE structural property only
because the gate is split:

  * CORRECTNESS (kappa=1, the gate): DIFFERENTIAL test — candidate(x) must equal
    reference(x) for ALL x in a large adversarial + fuzzed input set. A faster-but-WRONG
    candidate is REJECTED (see _selftest catches-broken). This is exact relative to the
    input distribution, and a candidate that special-cases the benchmark inputs but is
    wrong on fuzzed inputs is CAUGHT (see _selftest rejects-gaming).
  * SPEED (a measurement, NOT kappa=1): a timed benchmark, best-of-trials, reported with
    the honest caveat that wall-clock timing is noisy and machine-dependent.

A WIN = correctness passes AND measured speedup >= margin. The correctness gate is what
makes "superoptimization" safe; the speedup is reported, never trusted as a certificate.

Honest ceiling: certifies the candidate agrees with the reference on the tested input set
and reports a measured speedup. It does NOT prove correctness on inputs outside that set,
nor that the speedup holds on other hardware/inputs. Sharpen the input generator
(adversarial + edge + fuzz) to sharpen the certificate.
"""
import sys
import json
import time
import signal


class LCG:
    def __init__(self, seed=1):
        self.s = seed & 0xFFFFFFFF

    def _n(self):
        self.s = (1664525 * self.s + 1013904223) & 0xFFFFFFFF
        return self.s

    def randint(self, a, b):
        return a + self._n() % (b - a + 1)


class _Timeout(Exception):
    pass


def _load(source, entry):
    ns = {"__builtins__": __builtins__}
    exec(compile(source, "<impl>", "exec"), ns)
    return ns[entry]


def _call(fn, args, timeout_s=5):
    def _alarm(s, f):
        raise _Timeout()
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, timeout_s)
    try:
        return fn(*args)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


CEILING = ("SUPEROPT gates CORRECTNESS by differential test (kappa=1 relative to the "
           "tested input set) and REPORTS a measured speedup (noisy, machine-dependent, "
           "NOT a certificate). A win requires correctness AND speedup>=margin. It does "
           "not prove correctness outside the tested inputs.")


def verify_superopt(reference_src, candidate_src, entry,
                    diff_inputs, bench_inputs, margin=1.10, trials=5):
    """reference_src/candidate_src: Python source defining `entry`.
    diff_inputs : list of args-tuples (adversarial + edge + fuzz) for the correctness gate.
    bench_inputs: list of args-tuples for the timed benchmark.
    margin      : required speedup (e.g. 1.10 = at least 10% faster).
    Returns a verdict dict; 'win' is True only if correct AND speedup>=margin.
    """
    ref = _load(reference_src, entry)
    cand = _load(candidate_src, entry)

    # --- CORRECTNESS gate (kappa=1, differential over the whole input set) ---
    mismatches = []
    for args in diff_inputs:
        try:
            r = _call(ref, args)
            c = _call(cand, args)
        except Exception as e:
            mismatches.append({"args": args, "error": f"{type(e).__name__}: {e}"})
            continue
        if r != c:
            mismatches.append({"args": args, "ref": r, "cand": c})
            if len(mismatches) >= 5:
                break
    correct = (len(mismatches) == 0)

    res = {"sub_weapon": "SUPEROPT", "kappa": 1, "entry": entry,
           "correct": bool(correct), "correctness_mismatches": mismatches,
           "diff_inputs_checked": len(diff_inputs), "ceiling_note": CEILING}

    if not correct:
        res["verdict"] = "REJECTED_INCORRECT"
        res["win"] = False
        res["note"] = ("candidate disagrees with the reference -> NOT a valid "
                       "superoptimization (faster-but-wrong is not a win)")
        return res

    # --- SPEED measurement (NOT a certificate) ---
    def _bench(fn):
        best = float("inf")
        for _ in range(trials):
            t0 = time.perf_counter()
            for args in bench_inputs:
                fn(*args)
            best = min(best, time.perf_counter() - t0)
        return best

    t_ref = _bench(ref)
    t_cand = _bench(cand)
    speedup = (t_ref / t_cand) if t_cand > 0 else float("inf")
    res.update({
        "ref_seconds_best": t_ref, "cand_seconds_best": t_cand,
        "speedup_measured": speedup, "margin_required": margin,
        "win": bool(speedup >= margin),
        "verdict": "SUPEROPT_WIN" if speedup >= margin else "CORRECT_BUT_NOT_FASTER",
        "note": (f"correct (differential over {len(diff_inputs)} inputs) AND "
                 f"{speedup:.2f}x faster (measured, noisy)" if speedup >= margin else
                 f"correct but only {speedup:.2f}x (< {margin}x required)"),
    })
    return res


def _selftest():
    """passes-good / catches-broken / rejects-gaming."""
    entry = "f"
    ref = "def f(n):\n    return sum(range(n + 1))\n"           # O(n)
    fast = "def f(n):\n    return n * (n + 1) // 2\n"           # O(1), correct
    wrong = "def f(n):\n    return n * (n + 1) // 2 + 1\n"      # O(1) but WRONG
    bench = [(120000,)] * 3
    # diff_inputs MUST be adversarial + FUZZED (not a tiny fixed set) or a lookup table over the
    # fixed values games the gate (the audit's defect #2). Enlarge with fuzzed/unpredictable inputs:
    diff_small = [(k,) for k in (0, 1, 2, 3, 7, 50, 999, 1000, 12345)]
    rng = LCG(2026)
    diff = diff_small + [(rng.randint(0, 200000),) for _ in range(200)]

    # passes-good: correct AND faster -> WIN
    rg = verify_superopt(ref, fast, entry, diff, bench, margin=1.10)
    assert rg["correct"] is True, rg
    assert rg["win"] is True and rg["verdict"] == "SUPEROPT_WIN", rg
    assert rg["speedup_measured"] > 1.10, rg

    # catches-broken: faster but WRONG -> rejected on correctness (timing never trusted)
    rb = verify_superopt(ref, wrong, entry, diff, bench, margin=1.10)
    assert rb["correct"] is False and rb["win"] is False, rb
    assert rb["verdict"] == "REJECTED_INCORRECT", rb

    # rejects-gaming: hard-code the benchmark inputs, wrong elsewhere -> differential catches
    closed = 120000 * (120000 + 1) // 2
    gaming = (f"def f(n):\n    return {{120000: {closed}}}.get(n, 0)\n")
    # gaming would look correct+fast on the bench workload (all n=120000), but...
    rga = verify_superopt(ref, gaming, entry, diff, bench, margin=1.10)
    assert rga["correct"] is False, rga       # ...differential on fuzzed n catches it
    assert rga["verdict"] == "REJECTED_INCORRECT", rga

    # rejects-gaming #2 (audit defect #2): a lookup table over the SMALL fixed diff values +
    # bench is CAUGHT once diff includes fuzzed/unpredictable inputs -> the fixed set alone is
    # not what stands between a lookup table and a false WIN.
    tbl = {k: k * (k + 1) // 2 for (k,) in diff_small}
    tbl[120000] = closed
    gaming2 = ("def f(n):\n    return {"
               + ", ".join(f"{k}: {v}" for k, v in tbl.items()) + "}.get(n, 0)\n")
    rga2 = verify_superopt(ref, gaming2, entry, diff, bench, margin=1.10)
    assert rga2["correct"] is False and rga2["verdict"] == "REJECTED_INCORRECT", rga2

    print("SUPEROPT  selftest: PASS (correct+faster->WIN, faster-but-wrong->REJECTED, "
          "hardcode-benchmark->caught, hardcode-fixed-diff-set->caught by fuzzed inputs)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: superopt_verify.py selftest")
