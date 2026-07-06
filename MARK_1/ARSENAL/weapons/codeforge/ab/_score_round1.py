#!/usr/bin/env python3
"""Score A/B round-1 candidates with the FROZEN verifiers (agent self-reports ignored).
Candidates are the verbatim payloads returned by the Haiku writers (best-of-4 = the 4 arrays/
functions emitted; iterate-r1 = the single attempt). Prints per-task/per-arm scores."""
import json
import harness as H

# ---- BEST-OF-4 payloads (4 independent attempts each) ----
BO = {
    "s_n5b12": [
        "[[0,1],[1,2],[0,1],[2,3],[1,2],[0,1],[3,4],[2,3],[1,2],[0,1]]",
        "[[0,1],[2,3],[1,2],[3,4],[0,1],[2,3],[1,2],[3,4],[0,1],[2,3]]",
        "[[0,1],[2,3],[1,2],[0,1],[3,4],[2,3],[1,2],[2,3],[1,2]]",
        "[[0,1],[2,3],[3,4],[1,2],[0,1],[2,3],[1,2],[2,3]]",
    ],
    "s_n6b16": [
        "[[0,1],[2,3],[4,5],[0,2],[1,3],[0,4],[1,5],[2,4],[3,5],[1,2],[3,4],[2,3]]",
        "[[0,1],[2,3],[4,5],[1,2],[3,4],[0,1],[2,3],[4,5],[1,2],[3,4],[0,1],[2,3],[4,5],[1,2],[3,4]]",
        "[[0,1],[2,3],[4,5],[0,2],[1,4],[3,5],[1,2],[0,3],[4,5],[2,3],[1,4],[2,4],[3,4]]",
        "[[0,1],[2,3],[4,5],[0,2],[1,3],[3,5],[0,4],[1,2],[2,4],[1,5],[3,4],[2,3],[1,4],[2,4]]",
    ],
    "y_reset": [
        "def f(nums):\n    result=[]; m=0\n    for x in nums:\n        if x<0:\n            m=0; result.append(0)\n        else:\n            m=max(m,x); result.append(m)\n    return result\n",
        "def f(nums):\n    result=[]; running_max=0\n    for num in nums:\n        if num<0:\n            running_max=0; result.append(0)\n        else:\n            running_max=max(running_max,num); result.append(running_max)\n    return result\n",
        "def f(nums):\n    output=[]; state=0\n    for val in nums:\n        state = 0 if val<0 else max(state,val)\n        output.append(state)\n    return output\n",
        "def f(nums):\n    result=[]; m=0\n    for x in nums:\n        m = max(m,x) if x>=0 else 0\n        result.append(m)\n    return result\n",
    ],
    "y_countsmaller": [
        "def f(nums):\n    result=[]\n    for i in range(len(nums)):\n        count=0\n        for j in range(i):\n            if nums[j]<nums[i]:\n                count+=1\n        result.append(count)\n    return result\n",
        "def f(nums):\n    result=[]\n    for i in range(len(nums)):\n        count=sum(1 for j in range(i) if nums[j]<nums[i])\n        result.append(count)\n    return result\n",
        "def f(nums):\n    result=[]\n    for i in range(len(nums)):\n        smaller_count=len([nums[j] for j in range(i) if nums[j]<nums[i]])\n        result.append(smaller_count)\n    return result\n",
        "def f(nums):\n    def count_smaller(t):\n        return sum(nums[j]<nums[t] for j in range(t))\n    return [count_smaller(i) for i in range(len(nums))]\n",
    ],
}

# ---- ITERATE round-1 payloads (single attempt each) ----
IT_R1 = {
    "s_n5b12": "[[0,1],[3,4],[2,4],[2,3],[1,4],[0,3],[0,2],[1,3],[1,2]]",
    "s_n6b16": "[[0,1],[2,3],[4,5],[0,2],[1,3],[1,2],[0,4],[1,5],[2,4],[3,5],[1,2],[3,4],[2,3]]",
    "y_reset": "def f(nums):\n    result=[]; m=0\n    for x in nums:\n        if x<0:\n            m=0; result.append(0)\n        else:\n            m=max(m,x); result.append(m)\n    return result\n",
    "y_countsmaller": "def f(nums):\n    result=[]\n    for i in range(len(nums)):\n        count=0\n        for j in range(i):\n            if nums[j]<nums[i]:\n                count+=1\n        result.append(count)\n    return result\n",
}

print("=== BEST-OF-4 (matched-budget control) + ONESHOT (attempt #1) ===")
bo_summary = {}
for tid, cands in BO.items():
    scores = [H.score_for(tid, c) for c in cands]
    oneshot = scores[0]["ok"]
    best4 = any(s["ok"] for s in scores)
    sizes = [s.get("size") for s in scores]
    bo_summary[tid] = {"oneshot": oneshot, "best4": best4,
                       "per_attempt_ok": [s["ok"] for s in scores], "sizes": sizes}
    print(f"  {tid:16s} oneshot={oneshot}  best4={best4}  attempt_ok={[s['ok'] for s in scores]} sizes={sizes}")

print("\n=== ITERATE round 1 (feedback captured for next round on failures) ===")
it_summary = {}
for tid, c in IT_R1.items():
    s = H.score_for(tid, c)
    it_summary[tid] = {"r1_ok": s["ok"], "feedback": s["feedback"], "size": s.get("size")}
    print(f"  {tid:16s} r1_ok={s['ok']}  size={s.get('size')}")
    if not s["ok"]:
        print(f"      feedback -> {s['feedback']}")

json.dump({"best_of_4": bo_summary, "iterate_r1": it_summary},
          open("_round1_scored.json", "w"), indent=2)
print("\n(scored with frozen verifiers; self-reports ignored)")
