#!/usr/bin/env python3
"""SYNTH-VERIFY — frozen verifier for code synthesized to a spec.  kappa = 1 (on the
held-out test set; see ceiling).

The armor++ floor: never ship code the verifier hasn't passed. A candidate (Python
source) is gated on a battery the GENERATOR NEVER SEES:
  * HIDDEN unit tests        — held-out (i,o) pairs, disjoint from the visible examples;
  * PROPERTY-based tests     — N fuzzed inputs (deterministic LCG) checked against a
                               structural predicate (the Hypothesis idea; we hand-roll a
                               deterministic fuzzer so there is no external dependency and
                               runs are reproducible — see GROUNDING.md);
  * DIFFERENTIAL tests       — N fuzzed/adversarial inputs compared against an independent
                               REFERENCE ORACLE.
A candidate counts as VERIFIED only if it passes the HIDDEN + PROPERTY + DIFFERENTIAL
sets. Visible examples are informational only.

Anti-gaming (the contamination/reward-hack defense): the generator sees the spec + a few
VISIBLE example tests; it never sees the hidden/property/differential inputs. So a
candidate that HARD-CODES outputs for the visible tests passes the visible set but FAILS
hidden/differential -> verdict GAMING_DETECTED (see _selftest rejects-gaming).

** SEED SECRECY (hardening from the 2026-06-20 cross-model audit).** The fuzz inputs are
reproducible from a SEED. If that seed is a fixed PUBLIC constant, a source-reading
attacker can pre-compute every held-out input and pass a lookup table (a real false-accept
the audit demonstrated). DEFENSE: when spec["seed"] is None (the DEFAULT) the seed is drawn
UNPREDICTABLY from os.urandom and recorded as `seed_used`; a candidate cannot pre-compute
inputs it cannot predict. Pin a seed ONLY to reproduce a recorded run. _selftest proves it:
a candidate hard-coded to one seed's fuzz inputs PASSES under that seed but is CAUGHT under a
different (unpredictable) seed.

Honest ceiling: kappa=1 *relative to the held-out battery*. It certifies "passes these
hidden + property + differential checks", NOT "correct for all inputs" unless the
property/differential cover the spec exhaustively. A spec whose verifier is weak is a
weak certificate — sharpen the property + reference oracle, do not over-read a pass.
Tasks must be NON-MEMORIZED (mutation / compositional novelty) or a pass proves nothing
(a memorized classic is one-shot, no offense demonstrated — see the v5 saturation lesson).

Sandbox note (honest): candidate code is exec'd with a restricted builtins map + an
import whitelist + a wall-clock SIGALRM timeout. This is a RESEARCH harness, not a
hardened security sandbox; only run code from sources you would run anyway.
"""
import sys
import os
import json
import signal


# ---------------- deterministic fuzzer (no external dependency) ----------------
class LCG:
    """Tiny deterministic PRNG (numerical-recipes LCG) so fuzzing is reproducible."""
    def __init__(self, seed=1):
        self.s = seed & 0xFFFFFFFF

    def _next(self):
        self.s = (1664525 * self.s + 1013904223) & 0xFFFFFFFF
        return self.s

    def randint(self, a, b):
        return a + self._next() % (b - a + 1)

    def choice(self, seq):
        return seq[self._next() % len(seq)]


# ---------------- restricted execution sandbox ----------------
_SAFE_IMPORTS = {"math", "collections", "itertools", "functools", "heapq",
                 "bisect", "re", "string", "operator"}
_SAFE_BUILTINS = {k: __builtins__[k] if isinstance(__builtins__, dict)
                  else getattr(__builtins__, k)
                  for k in ["abs", "all", "any", "bool", "dict", "divmod",
                            "enumerate", "filter", "float", "frozenset", "int",
                            "len", "list", "map", "max", "min", "next", "pow",
                            "range", "reversed", "round", "set", "slice", "sorted",
                            "str", "sum", "tuple", "zip", "ord", "chr", "isinstance",
                            "True", "False", "None", "print", "Exception",
                            "ValueError", "IndexError", "KeyError", "TypeError"]
                  if (k in __builtins__ if isinstance(__builtins__, dict)
                      else hasattr(__builtins__, k))}


def _guarded_import(name, *a, **k):
    root = name.split(".")[0]
    if root not in _SAFE_IMPORTS:
        raise ImportError(f"import of {name!r} blocked by SYNTH sandbox")
    return __import__(name, *a, **k)


class _Timeout(Exception):
    pass


def run_candidate(source, entry, args, timeout_s=2):
    """Exec `source`, call `entry(*args)`, return output. Raises on error/timeout."""
    ns = {"__builtins__": dict(_SAFE_BUILTINS, __import__=_guarded_import)}
    exec(compile(source, "<candidate>", "exec"), ns)
    if entry not in ns or not callable(ns[entry]):
        raise NameError(f"entry point {entry!r} not defined")

    def _alarm(signum, frame):
        raise _Timeout()
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, timeout_s)
    try:
        return ns[entry](*args)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


CEILING = ("SYNTH-VERIFY is kappa=1 RELATIVE TO its held-out battery (hidden + property + "
           "differential). It certifies the candidate passes those checks, not universal "
           "correctness unless the battery is exhaustive. Tasks must be NON-MEMORIZED or a "
           "pass proves nothing.")


def verify_synthesis(candidate_source, spec):
    """Gate a candidate against a spec.

    spec keys:
      entry         : function name (str)
      visible_tests : list of (args_tuple, expected)   # generator SEES these
      hidden_tests  : list of (args_tuple, expected)   # held out
      reference_fn  : callable(args_tuple) -> expected  # differential oracle (optional)
      property_fn   : callable(args_tuple, output) -> bool  # structural predicate (optional)
      input_gen     : callable(LCG) -> args_tuple       # fuzz input generator (optional)
      n_property,n_diff : ints (default 200,200)
      seed : int to PIN the fuzzer (reproduction only). If None/absent (DEFAULT) an
             UNPREDICTABLE seed is drawn from os.urandom so candidates cannot pre-compute
             the held-out inputs; the seed used is recorded as `seed_used` in the result.
    Returns a verdict dict; verdict == "VERIFIED" only if hidden+property+differential pass.
    """
    entry = spec["entry"]
    res = {"sub_weapon": "SYNTH-VERIFY", "kappa": 1, "entry": entry,
           "ceiling_note": CEILING}
    seed = spec.get("seed")
    if seed is None:                       # unpredictable by default (anti seed-prediction)
        seed = int.from_bytes(os.urandom(4), "big")
    res["seed_used"] = seed

    def _safe(args):
        try:
            return True, run_candidate(candidate_source, entry, args), None
        except _Timeout:
            return False, None, "timeout"
        except Exception as e:
            return False, None, f"{type(e).__name__}: {e}"

    # visible (informational)
    vis_pass = 0
    for args, exp in spec.get("visible_tests", []):
        ok, out, err = _safe(args)
        vis_pass += int(ok and out == exp)
    res["visible_pass"] = vis_pass
    res["visible_total"] = len(spec.get("visible_tests", []))

    # hidden (gate)
    hid_fail = []
    for idx, (args, exp) in enumerate(spec.get("hidden_tests", [])):
        ok, out, err = _safe(args)
        if not (ok and out == exp):
            hid_fail.append({"i": idx, "args": args, "expected": exp,
                             "got": out, "error": err})
    res["hidden_total"] = len(spec.get("hidden_tests", []))
    res["hidden_failures"] = hid_fail
    hidden_ok = (len(hid_fail) == 0 and res["hidden_total"] > 0)

    # property (gate, if provided)
    property_ok, prop_fail = True, []
    if spec.get("property_fn") and spec.get("input_gen"):
        rng = LCG(seed)
        for _ in range(spec.get("n_property", 200)):
            args = spec["input_gen"](rng)
            ok, out, err = _safe(args)
            if not ok or not spec["property_fn"](args, out):
                property_ok = False
                prop_fail.append({"args": args, "got": out, "error": err})
                if len(prop_fail) >= 3:
                    break
    res["property_failures"] = prop_fail

    # differential (gate, if provided)
    differential_ok, diff_fail = True, []
    if spec.get("reference_fn") and spec.get("input_gen"):
        rng = LCG(seed ^ 0x5DEECE66)
        for _ in range(spec.get("n_diff", 200)):
            args = spec["input_gen"](rng)
            ok, out, err = _safe(args)
            ref = spec["reference_fn"](args)
            if not ok or out != ref:
                differential_ok = False
                diff_fail.append({"args": args, "got": out, "ref": ref, "error": err})
                if len(diff_fail) >= 3:
                    break
    res["differential_failures"] = diff_fail

    verified = hidden_ok and property_ok and differential_ok
    res["passed"] = bool(verified)
    if verified:
        res["verdict"] = "VERIFIED"
    elif (res["visible_total"] > 0 and vis_pass == res["visible_total"] and not hidden_ok):
        # passes everything it could SEE but fails held-out -> hard-coding signature
        res["verdict"] = "GAMING_DETECTED"
    elif not hidden_ok:
        res["verdict"] = "FAILED_HIDDEN"
    elif not property_ok:
        res["verdict"] = "FAILED_PROPERTY"
    else:
        res["verdict"] = "FAILED_DIFFERENTIAL"
    return res


# ---------------- self-test spec ----------------
def _spec_sorted_unique():
    return {
        "entry": "f",
        "visible_tests": [(([3, 1, 2],), [1, 2, 3]), (([1, 1],), [1])],
        "hidden_tests": [(([2, 2, 1, 3, 3],), [1, 2, 3]), (([],), []),
                         (([5, 4, 4, 5],), [4, 5]), (([0],), [0])],
        "reference_fn": lambda args: sorted(set(args[0])),
        "property_fn": lambda args, out: (isinstance(out, list)
                                          and out == sorted(out)
                                          and set(out) == set(args[0])
                                          and len(out) == len(set(out))),
        "input_gen": lambda rng: ([rng.randint(0, 5) for _ in range(rng.randint(0, 8))],),
        "n_property": 150, "n_diff": 150, "seed": 7,
    }


def _replay_fuzz(spec):
    """Reproduce EXACTLY the fuzz inputs verify_synthesis draws for spec['seed']
    (property stream, then differential stream). Used by _selftest to build the
    seed-prediction attack and prove seed secrecy defeats it."""
    seed = spec["seed"]
    ins = []
    rng = LCG(seed)
    for _ in range(spec.get("n_property", 200)):
        ins.append(spec["input_gen"](rng))
    rng = LCG(seed ^ 0x5DEECE66)
    for _ in range(spec.get("n_diff", 200)):
        ins.append(spec["input_gen"](rng))
    return ins


def _selftest():
    """passes-good / catches-broken / rejects-gaming."""
    spec = _spec_sorted_unique()

    good = "def f(nums):\n    return sorted(set(nums))\n"
    rg = verify_synthesis(good, spec)
    assert rg["verdict"] == "VERIFIED", rg

    # broken: forgets to dedup -> fails property/differential/hidden on duplicates
    broken = "def f(nums):\n    return sorted(nums)\n"
    rb = verify_synthesis(broken, spec)
    assert rb["passed"] is False, rb
    assert rb["verdict"] in ("FAILED_HIDDEN", "GAMING_DETECTED",
                             "FAILED_PROPERTY", "FAILED_DIFFERENTIAL"), rb

    # gaming: hard-code the VISIBLE tests only -> passes visible, fails hidden
    gaming = ("def f(nums):\n"
              "    table = {(3, 1, 2): [1, 2, 3], (1, 1): [1]}\n"
              "    return table.get(tuple(nums), [])\n")
    rga = verify_synthesis(gaming, spec)
    assert rga["passed"] is False, rga
    assert rga["verdict"] == "GAMING_DETECTED", rga
    assert rga["visible_pass"] == rga["visible_total"], rga  # it DID pass everything visible

    # sandbox: a blocked import is caught (does not crash the gate)
    bad = "import os\ndef f(nums):\n    return os.listdir('.')\n"
    rbad = verify_synthesis(bad, spec)
    assert rbad["passed"] is False, rbad

    # rejects SEED-PREDICTION gaming (the audit's MEDIUM-HIGH finding): an attacker who
    # reads the source pre-computes seed S1's fuzz inputs into a lookup table. It PASSES
    # under the known seed S1 (why fixed PUBLIC seeds are unsafe) but is CAUGHT under a
    # different/unpredictable seed -> seed secrecy is the load-bearing defense.
    S1, S2 = 7, 99
    fuzz = _replay_fuzz(dict(spec, seed=S1))
    table = {tuple(a[0]): spec["reference_fn"](a) for a in fuzz}
    for a, o in spec["visible_tests"] + spec["hidden_tests"]:
        table[tuple(a[0])] = o
    seed_pred = ("LOOKUP = " + repr(table) + "\n"
                 "def f(nums):\n    return LOOKUP.get(tuple(nums), [-12345])\n")
    assert verify_synthesis(seed_pred, dict(spec, seed=S1))["verdict"] == "VERIFIED", \
        "lookup-table attack should pass when the seed is KNOWN (shows fixed seeds are unsafe)"
    assert verify_synthesis(seed_pred, dict(spec, seed=S2))["passed"] is False, \
        "a different seed must defeat the seed-prediction attack"
    spec_default = {k: v for k, v in spec.items() if k != "seed"}  # default -> os.urandom
    assert verify_synthesis(seed_pred, spec_default)["passed"] is False, \
        "the unpredictable default seed must defeat the attack"

    print("SYNTH     selftest: PASS (good->VERIFIED, broken->caught, "
          "hardcode-visible->GAMING_DETECTED, seed-prediction->caught under fresh seed, "
          "blocked-import->caught)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: synth_verify.py selftest")
