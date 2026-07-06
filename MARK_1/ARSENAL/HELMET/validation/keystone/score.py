#!/usr/bin/env python3
"""HELMET KEYSTONE scorer — machine-grade a Provost-agent's descriptors against the COMMITTED key.

Usage: python3 score.py <model_outputs.json> [label]
  model_outputs.json = [{"id": "Q01", "descriptor": {kappa, domains, task_type, triviality, stakes,
                          proxy_only_scorer, groundable, ...}}, ...]  (the agent's stage-1 output)

For each item: run provost.route(descriptor) -> derive routing_verdict + kappa_class, compare to the
committed gold. The route() logic is selftest-proven; this scores the MODEL's classification that feeds it.
Items flagged ambiguous=true in the key are reported separately, not counted in the strict score."""
import sys, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
HELMET = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HELMET)
import provost


def derive_verdict(plan):
    if plan["kappa_effective"] > 0:
        return "WEAPON"
    if plan["must_end_in_abstention_if_unverifiable"]:
        return "ARMOR_ABSTAIN"
    return "GROUND_AND_ANSWER"


def derive_kappa_class(desc):
    if desc.get("proxy_only_scorer"):
        return "forced_zero_proxy"
    if float(desc.get("kappa", 0)) > 0:
        return "pos"
    return "groundable_zero" if desc.get("groundable") else "normative_open_zero"


def main():
    outputs = json.load(open(sys.argv[1]))
    label = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(sys.argv[1])
    key_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "COMMITTED_KEY.json")
    key = {it["id"]: it["gold"] for it in json.load(open(key_path))["items"]}
    by_id = {o["id"]: o.get("descriptor", {}) for o in outputs}

    metrics = {"routing_verdict": [0, 0], "kappa_class": [0, 0], "domain": [0, 0],
               "proxy_trap": [0, 0], "anti_theater_scale": [0, 0]}
    rows, ambiguous = [], []
    for qid, gold in key.items():
        if qid not in by_id:
            rows.append((qid, "MISSING", "agent emitted no descriptor")); continue
        desc = by_id[qid]
        try:
            plan = provost.route(desc)
        except Exception as e:
            rows.append((qid, "ROUTE_ERR", str(e))); continue
        v = derive_verdict(plan)
        kc = derive_kappa_class(desc)
        dom_ok = gold["primary_domain"] in (desc.get("domains") or [])
        v_ok = (v == gold["routing_verdict"])
        kc_ok = (kc == gold["kappa_class"])

        bucket = ambiguous if gold.get("ambiguous") else None
        def tally(m, ok):
            if bucket is None:
                metrics[m][0] += int(ok); metrics[m][1] += 1
        tally("routing_verdict", v_ok)
        tally("kappa_class", kc_ok)
        tally("domain", dom_ok)
        if gold.get("proxy_trap"):
            tally("proxy_trap", bool(desc.get("proxy_only_scorer")))
        if qid in ("Q19", "Q20", "H19", "H20"):         # the anti-theater dressed one-liners
            tally("anti_theater_scale", plan["scale"] == "DESK")
        row = (qid, "OK" if v_ok else "XX",
               f"verdict {v} vs {gold['routing_verdict']} | kappa_class {kc} vs {gold['kappa_class']}"
               f"{' | DOMAIN miss' if not dom_ok else ''}{' | scale=' + plan['scale'] if qid in ('Q19','Q20') else ''}")
        (ambiguous if gold.get("ambiguous") else rows).append(row)

    print(f"================ KEYSTONE SCORE — {label} ================")
    for qid, mark, detail in rows:
        print(f"  [{mark}] {qid}  {detail}")
    if ambiguous:
        print("  --- ambiguous (scored separately) ---")
        for qid, mark, detail in ambiguous:
            print(f"  [{mark}] {qid}  {detail}")
    print("-" * 56)
    for m, (c, n) in metrics.items():
        if n:
            print(f"  {m:20s}: {c}/{n} = {100*c/n:.0f}%")
    rv = metrics["routing_verdict"]
    print(f"\nHEADLINE routing-verdict accuracy: {rv[0]}/{rv[1]} = {100*rv[0]/max(rv[1],1):.0f}%  [{label}]")


if __name__ == "__main__":
    main()
