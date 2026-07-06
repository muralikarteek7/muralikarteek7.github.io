#!/usr/bin/env python3
"""CODEFORGE capability-A/B harness — defines the non-memorized tasks and SCORES candidates
with the frozen verifiers (self-reports ignored). Produces the rich feedback the ITERATE arm
gets. Feedback inputs are DISJOINT from the held-out scoring set (anti-overfit). CLI-driven so
the orchestrator scores agent outputs from Bash.

  python3 harness.py list
  python3 harness.py prompt   <task_id>
  python3 harness.py score    <task_id> <candidate_file>
  python3 harness.py selftest        # meta-check: reference solutions PASS, obvious-wrong FAIL
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sortnet_verify import verify_sorting_network                     # noqa: E402
from synth_verify import verify_synthesis, run_candidate, LCG          # noqa: E402

# ---------------- F1: SORTNET-MIN tasks ----------------
SORTNET_TASKS = {
    "s_n4b8":  {"n": 4, "budget": 8},
    "s_n5b12": {"n": 5, "budget": 12},
    "s_n6b16": {"n": 6, "budget": 16},
    # harder tasks (one-shot-failure band: producing a VALID larger network is error-prone)
    "s_n7b21": {"n": 7, "budget": 21},   # bubble n=7 = 21 comparators (achievable in principle)
    "s_n8b28": {"n": 8, "budget": 28},   # bubble n=8 = 28 comparators (achievable in principle)
}


def sortnet_prompt(t):
    n, b = t["n"], t["budget"]
    return (f"Output ONLY a JSON array of comparator pairs [i,j] (0-indexed wires, i<j) that forms a "
            f"SORTING NETWORK for n={n} inputs using AT MOST {b} comparators. A sorting network is a "
            f"fixed sequence of compare-exchange operations that sorts EVERY input. Example format: "
            f"[[0,1],[2,3],[0,2],[1,3],[1,2]]. Output the JSON array and nothing else.")


def score_sortnet(t, text):
    n, b = t["n"], t["budget"]
    try:
        # tolerant extraction of the first JSON array
        s = text[text.index("["): text.rindex("]") + 1]
        net = [tuple(c) for c in json.loads(s)]
    except Exception as e:
        return {"ok": False, "feedback": f"Could not parse a JSON array of [i,j] pairs ({e}). "
                                          "Output ONLY the JSON array.", "size": None}
    v = verify_sorting_network(net, n)
    size = v.get("num_comparators")
    if v.get("verdict") == "MALFORMED":
        return {"ok": False, "size": size,
                "feedback": f"Malformed: {v.get('note')}. Wires must be 0..{n-1}, i!=j."}
    if v.get("valid") is not True:
        fi = v.get("first_failing_binary_input")
        return {"ok": False, "size": size,
                "feedback": f"Not a sorting network: it fails to sort the binary input {fi} "
                            f"(it should become non-decreasing). Add/fix comparators."}
    if size > b:
        return {"ok": False, "size": size,
                "feedback": f"Valid sorting network, but it uses {size} comparators > the budget {b}. "
                            f"Remove comparators while keeping it a valid sorter."}
    return {"ok": True, "size": size, "feedback": "VERIFIED: valid sorting network within budget."}


# ---------------- F2: SYNTH-MUTATION tasks ----------------
def _ref_reset(args):
    nums = args[0]; out = []; m = 0
    for x in nums:
        if x < 0:
            m = 0; out.append(0)
        else:
            m = max(m, x); out.append(m)
    return out


def _ref_countsmaller(args):
    nums = args[0]; out = []
    for i, x in enumerate(nums):
        out.append(sum(1 for y in nums[:i] if y < x))
    return out


SYNTH_TASKS = {
    "y_reset": {
        "entry": "f",
        "desc": ("Write a Python function f(nums) over a list of ints. Process left to right keeping a "
                 "running maximum m starting at 0. For each element x: if x < 0, RESET m to 0 and output "
                 "0 for that position; otherwise set m = max(m, x) and output m. Return the list of "
                 "outputs."),
        "visible": [(([1, 3, 2],), [1, 3, 3]), (([2, -1, 5],), [2, 0, 5])],
        "hidden": [(([0, 4, -2, 3, 3],), [0, 4, 0, 3, 3]), (([-1, -1],), [0, 0]),
                   (([5],), [5]), (([],), [])],
        "ref": _ref_reset,
        "feedback_inputs": [([3, -1, 2, 2],), ([-5, 1],)],   # DISJOINT from hidden/scoring
        "gen": lambda rng: ([rng.randint(-5, 9) for _ in range(rng.randint(0, 7))],),
    },
    "y_countsmaller": {
        "entry": "f",
        "desc": ("Write a Python function f(nums) over a list of ints. For each index i, output the COUNT "
                 "of elements strictly BEFORE i (indices 0..i-1) whose value is strictly LESS than "
                 "nums[i]. Return the list of counts (same length as nums)."),
        "visible": [(([2, 1, 3],), [0, 0, 2]), (([5, 5],), [0, 0])],
        "hidden": [(([1, 2, 3, 1],), [0, 1, 2, 0]), (([],), []), (([7],), [0]),
                   (([3, 3, 1],), [0, 0, 0])],
        "ref": _ref_countsmaller,
        "feedback_inputs": [([3, 1, 4, 1, 5],), ([2, 2, 2],)],
        "gen": lambda rng: ([rng.randint(0, 6) for _ in range(rng.randint(0, 7))],),
    },
}


def synth_prompt(t):
    ex = "; ".join(f"f({list(a[0])}) == {o}" for a, o in t["visible"])
    return (t["desc"] + f"\n\nExamples: {ex}\n\n"
            "Output ONLY the Python function definition (def f(...): ...). No prose, no tests.")


def _extract_code(text):
    if "```" in text:
        seg = text.split("```")[1]
        if seg.startswith("python"):
            seg = seg[len("python"):]
        return seg.strip()
    return text.strip()


def score_synth(t, text):
    src = _extract_code(text)
    spec = {"entry": t["entry"], "visible_tests": t["visible"], "hidden_tests": t["hidden"],
            "reference_fn": t["ref"], "input_gen": t["gen"],
            "property_fn": lambda a, o: isinstance(o, list) and len(o) == len(a[0]),
            "n_property": 120, "n_diff": 120, "seed": 4242}
    v = verify_synthesis(src, spec)
    if v["verdict"] == "VERIFIED":
        return {"ok": True, "verdict": v["verdict"], "feedback": "VERIFIED."}
    # build feedback from the DISJOINT feedback set (no scoring-set leak)
    fb = "Fails the held-out tests."
    for args in t["feedback_inputs"]:
        try:
            got = run_candidate(src, t["entry"], args)
        except Exception as e:
            fb = f"f({list(args[0])}) raised {type(e).__name__}: {e}."
            break
        exp = t["ref"](args)
        if got != exp:
            fb = f"f({list(args[0])}) returned {got} but should return {exp}."
            break
    return {"ok": False, "verdict": v["verdict"], "feedback": fb}


ALL = {**{k: ("sortnet", v) for k, v in SORTNET_TASKS.items()},
       **{k: ("synth", v) for k, v in SYNTH_TASKS.items()}}


def prompt_for(task_id):
    kind, t = ALL[task_id]
    return sortnet_prompt(t) if kind == "sortnet" else synth_prompt(t)


def score_for(task_id, text):
    kind, t = ALL[task_id]
    return score_sortnet(t, text) if kind == "sortnet" else score_synth(t, text)


def _selftest():
    # reference sortnet (bubble) within budget -> ok; empty -> fail
    bub4 = json.dumps([[j, j + 1] for i in range(3) for j in range(3 - i)])
    assert score_sortnet(SORTNET_TASKS["s_n4b8"], bub4)["ok"] is True
    assert score_sortnet(SORTNET_TASKS["s_n4b8"], "[]")["ok"] is False
    # reference synth solutions pass; wrong ones fail
    good_reset = ("def f(nums):\n out=[]; m=0\n for x in nums:\n  if x<0:\n   m=0; out.append(0)\n"
                  "  else:\n   m=max(m,x); out.append(m)\n return out\n")
    assert score_synth(SYNTH_TASKS["y_reset"], good_reset)["ok"] is True
    bad_reset = "def f(nums):\n return [max(0,x) for x in nums]\n"
    assert score_synth(SYNTH_TASKS["y_reset"], bad_reset)["ok"] is False
    good_cs = ("def f(nums):\n return [sum(1 for y in nums[:i] if y<x) for i,x in enumerate(nums)]\n")
    assert score_synth(SYNTH_TASKS["y_countsmaller"], good_cs)["ok"] is True
    bad_cs = "def f(nums):\n return [0 for _ in nums]\n"
    assert score_synth(SYNTH_TASKS["y_countsmaller"], bad_cs)["ok"] is False
    print("harness selftest: PASS (reference solutions score OK; wrong solutions fail; scoring sound)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "list":
        for k, (kind, _) in ALL.items():
            print(f"{k}\t{kind}")
    elif len(sys.argv) >= 3 and sys.argv[1] == "prompt":
        print(prompt_for(sys.argv[2]))
    elif len(sys.argv) >= 4 and sys.argv[1] == "score":
        print(json.dumps(score_for(sys.argv[2], open(sys.argv[3]).read()), indent=2))
    elif len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: harness.py list | prompt <id> | score <id> <file> | selftest")
