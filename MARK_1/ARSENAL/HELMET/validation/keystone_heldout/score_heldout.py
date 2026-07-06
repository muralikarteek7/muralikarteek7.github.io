#!/usr/bin/env python3
"""Aggregate the held-out Provost benchmark: routing-verdict accuracy per (doctrine,tier),
mean over reps, scored via the REAL provost.route() against the committed held-out key.
Usage: python3 agg_heldout.py <workflow_output.json>"""
import sys, json, os
from collections import defaultdict
HELMET = "/Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/HELMET"
sys.path.insert(0, HELMET)
import provost
KEY = json.load(open(os.path.join(HELMET,"validation/keystone_heldout/COMMITTED_KEY.json")))
gold = {it["id"]: it["gold"] for it in KEY["items"]}

def derive_verdict(plan):
    if plan["kappa_effective"] > 0: return "WEAPON"
    if plan["must_end_in_abstention_if_unverifiable"]: return "ARMOR_ABSTAIN"
    return "GROUND_AND_ANSWER"

import os as _os; out = json.load(open(sys.argv[1] if len(sys.argv)>1 else _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),"classifications.json")))
cls = out["result"]["classifications"] if "result" in out else out["classifications"]

# (doctrine,tier,rep) -> list of (id, verdict_ok strict-only), and failure tallies
cell = defaultdict(lambda: {"strict":[0,0], "amb":[0,0], "fails":defaultdict(int), "byverdict":defaultdict(lambda:[0,0])})
for c in cls:
    d,t,r = c["doctrine"], c["tier"], c["rep"]
    g = gold[c["id"]]
    try:
        plan = provost.route(c["descriptor"])
        v = derive_verdict(plan)
    except Exception as e:
        v = "ROUTE_ERR"
    ok = (v == g["routing_verdict"])
    key = (d,t,r)
    if g.get("ambiguous"):
        cell[key]["amb"][0]+=ok; cell[key]["amb"][1]+=1
    else:
        cell[key]["strict"][0]+=ok; cell[key]["strict"][1]+=1
        cell[key]["byverdict"][g["routing_verdict"]][0]+=ok
        cell[key]["byverdict"][g["routing_verdict"]][1]+=1
        if not ok:
            cell[key]["fails"][f'{c["id"]}:{g["routing_verdict"]}->{v}']+=1

# aggregate over reps
print("="*78)
print("HELD-OUT PROVOST BENCHMARK — routing-verdict accuracy (strict, n=40), mean over reps")
print("="*78)
agg = defaultdict(list)   # (doctrine,tier) -> [strict% per rep]
ambagg = defaultdict(list)
for (d,t,r),v in sorted(cell.items()):
    s=v["strict"]; pct=100*s[0]/s[1] if s[1] else 0
    agg[(d,t)].append(pct)
    a=v["amb"]; ambagg[(d,t)].append(100*a[0]/a[1] if a[1] else 0)
for (d,t) in sorted(agg):
    reps=agg[(d,t)]
    mean=sum(reps)/len(reps)
    print(f"  {d:10s} {t:7s}: strict reps={['%.0f%%'%x for x in reps]} mean={mean:.1f}%  | ambiguous reps={['%.0f%%'%x for x in ambagg[(d,t)]]}")
print()
# per-verdict breakdown + failure modes, aggregated across reps per (doctrine,tier)
print("Per-verdict accuracy + failure modes (summed across reps):")
v2=defaultdict(lambda: defaultdict(lambda:[0,0])); f2=defaultdict(lambda: defaultdict(int))
for (d,t,r),v in cell.items():
    for verd,(c,n) in v["byverdict"].items():
        v2[(d,t)][verd][0]+=c; v2[(d,t)][verd][1]+=n
    for f,ct in v["fails"].items(): f2[(d,t)][f]+=ct
for (d,t) in sorted(v2):
    print(f"  --- {d}/{t} ---")
    for verd in ("WEAPON","GROUND_AND_ANSWER","ARMOR_ABSTAIN"):
        c,n=v2[(d,t)][verd]
        if n: print(f"       {verd:18s} {c}/{n} = {100*c/n:.0f}%")
    if f2[(d,t)]:
        fails=sorted(f2[(d,t)].items(), key=lambda x:-x[1])
        print(f"       fails: " + ", ".join(f"{k}(x{v})" for k,v in fails))
