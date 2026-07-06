#!/usr/bin/env python3
"""VAULT backfill demo runner — ingests REAL season results into a fresh VAULT, then
exercises the read contract against the FROZEN predictions in PREDICTION.md.

The gate + store (not this script, not any narrative) are the judge. We only collect
verdicts and compare them to the frozen predictions. Exits 0 iff all predictions hold.
"""
import sys
import os
import json
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import vault_store

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "vault_backfill.json")
if os.path.exists(DB):
    os.remove(DB)  # fresh VAULT each run

NOW = datetime.datetime(2026, 6, 20, 12, 0, 0, tzinfo=datetime.timezone.utc)
LATE = datetime.datetime(2026, 9, 28, 0, 0, 0, tzinfo=datetime.timezone.utc)  # ~100d later

v = vault_store.Vault(path=DB)

# ---- ingest the 6 entries (A..F) -------------------------------------------- #
A = v.write({
    "result": "burma14 optimal tour length = 3323",
    "domain": "optimization.tsp",
    "requested_tier": "VERIFIED_FACT", "stakes": "low",
    "verification_record": {
        "method": "CP-SAT optimal == Held-Karp DP == TSPLIB literature (3 independent)",
        "artifact": "weapons/optima/demo_reproduce/RESULT.json",
        "result": "burma14 optimal tour length = 3323"},
    "provenance": "OPTIMA weapon, season 2026-06"}, now=NOW)

B = v.write({
    "result": "zeta(2) = pi^2/6 ~= 1.6449340668",
    "domain": "math.special_values",
    "requested_tier": "VERIFIED_FACT", "stakes": "low",
    "verification_record": {
        "method": "SYMBOLICA agreement gate: sympy.summation + mpmath.nsum + mpmath.zeta, 30-digit cross-method agreement",
        "artifact": "weapons/symbolica/demo_agreement/results.json",
        "result": "zeta(2) = pi^2/6 ~= 1.6449340668 (CERTIFIED + reproduction)"},
    "provenance": "SYMBOLICA weapon, season 2026-06"}, now=NOW)

C = v.write({
    "result": "sqlite3 library version = 3.51.0 (this machine)",
    "domain": "infra.versions",
    "requested_tier": "FETCHED_FACT", "stakes": "high",
    "fetched_at": "2026-06-20T00:00:00Z",
    "verification_record": {
        "method": "machine probe: python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'",
        "artifact": "stdout: 3.51.0; probed 2026-06-20 on darwin",
        "result": "3.51.0"},
    "provenance": "VAULT build session 2026-06-20"}, now=NOW)

D = v.write({
    "result": "selective-context decomposition might cut cost ~5x",
    "domain": "method.cost",
    "requested_tier": "LEAD", "stakes": "low",
    "provenance": "session hunch (v5.1 framing, pre-benchmark)"}, now=NOW)

# E: record-less FACT request (the record-less FACT attack)
E = v.write({
    "result": "approach Z is probably optimal",
    "domain": "method.cost",
    "requested_tier": "VERIFIED_FACT", "stakes": "low",
    "provenance": "session belief, no run"}, now=NOW)

# F: present-but-EMPTY record (the in-place LEAD-promotion attack)
F = v.write({
    "result": "promote me to a fact",
    "domain": "attack.promotion",
    "requested_tier": "VERIFIED_FACT", "stakes": "low",
    "verification_record": {"verified": True}}, now=NOW)

# ---- evaluate the 7 committed predictions ----------------------------------- #
checks = []


def check(desc, ok):
    checks.append({"check": desc, "pass": bool(ok)})
    print(f"  {'PASS' if ok else '*** FAIL ***'}  {desc}")


facts_now = v.query_facts(now=NOW)
fact_results = [f["result"] for f in facts_now]
leads_now = v.query_leads(now=NOW)
lead_hyps = [l["hypothesis"] for l in leads_now]

# P1: A,B admit VERIFIED_FACT, read back with method + provenance, non-decaying
check("P1: A (burma14) is VERIFIED_FACT in facts query with its method",
      A["tier"] == "VERIFIED_FACT" and any(
          f["result"] == A["result"] and "Held-Karp" in (f["verification_method"] or "")
          for f in facts_now))
check("P1: B (zeta(2)) is VERIFIED_FACT in facts query with its method",
      B["tier"] == "VERIFIED_FACT" and any(
          f["result"] == B["result"] and "agreement gate" in (f["verification_method"] or "")
          for f in facts_now))
check("P1: A,B are non-decaying (no TTL -> FRESH even years later)",
      A["valid_until"] is None and B["valid_until"] is None
      and all(f["freshness"] == "FRESH"
              for f in v.query_facts(query="optimization.tsp",
                                     now=datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc))))

# P2: C admits FETCHED_FACT, FRESH today, REVERIFY + on reverify_queue at +100d
fresh_c = [f for f in v.query_facts(query="infra.versions", now=NOW)]
late_c = [f for f in v.query_facts(query="infra.versions", now=LATE)]
rq = v.reverify_queue(now=LATE)
check("P2: C is FETCHED_FACT with a TTL set",
      C["tier"] == "FETCHED_FACT" and C["valid_until"] is not None)
check("P2: C reads FRESH within its TTL (today)",
      len(fresh_c) == 1 and fresh_c[0]["freshness"] == "FRESH")
check("P2: C reads REVERIFY 100 days later (high-stakes stale, not served silently)",
      len(late_c) == 1 and late_c[0]["freshness"] == "REVERIFY" and late_c[0]["is_stale"])
check("P2: C appears on the reverify_queue at +100d",
      any(r["result"] == C["result"] for r in rq))

# P3: D is a LEAD; never in facts (even on domain overlap); in leads as hypothesis
cost_facts = v.query_facts(query="method.cost", now=NOW)
check("P3: D admits as a LEAD", D["tier"] == "LEAD")
check("P3: D NEVER in query_facts (no lead leak, even on domain 'method.cost')",
      D["result"] not in fact_results and cost_facts == [])
check("P3: D appears in query_leads as a hypothesis-to-test",
      D["result"] in lead_hyps)

# P4: E (record-less FACT request) demoted to LEAD
check("P4: E (record-less FACT request) DEMOTED to LEAD",
      E["tier"] == "LEAD" and E["demotion_reason"] is not None)
check("P4: E NOT in facts, IS in leads with a demotion reason",
      E["result"] not in fact_results and E["result"] in lead_hyps
      and any(l["hypothesis"] == E["result"] and l["demotion_reason"] for l in leads_now))

# P5: F (present-but-EMPTY record) demoted to LEAD; record stored as None
check("P5: F (in-place LEAD-promotion attack, {verified:true}) DEMOTED to LEAD",
      F["tier"] == "LEAD" and F["verification_record"] is None)
check("P5: F NOT in facts (the LEAD-promotion attack FAILED)",
      F["result"] not in fact_results)

# P6: final counts — exactly 3 facts {A,B,C}, exactly 3 leads {D,E,F}
fact_set = set(fact_results)
lead_set = set(lead_hyps)
check("P6: exactly 3 facts == {A,B,C}",
      fact_set == {A["result"], B["result"], C["result"]} and len(facts_now) == 3)
check("P6: exactly 3 leads == {D,E,F}",
      lead_set == {D["result"], E["result"], F["result"]} and len(leads_now) == 3)
check("P6: zero overlap between facts and leads",
      fact_set.isdisjoint(lead_set))

# P7: provenance survives a disk round-trip
reloaded = vault_store.Vault(path=DB)
rf = reloaded.query_facts(query="burma14", now=NOW)
check("P7: after re-opening the persisted JSON, A still traces to its method+provenance",
      len(rf) == 1 and "Held-Karp" in (rf[0]["verification_method"] or "")
      and rf[0]["provenance"] == "OPTIMA weapon, season 2026-06")
reloaded_facts = set(f["result"] for f in reloaded.query_facts(now=NOW))
check("P7: re-opened VAULT still has exactly the 3 facts (no lead leaked through disk)",
      reloaded_facts == {A["result"], B["result"], C["result"]})

# ---- summary ---------------------------------------------------------------- #
passed = sum(1 for c in checks if c["pass"])
total = len(checks)
print("=" * 76)
print(f"RESULT: {passed}/{total} committed predictions confirmed by the machine judge.")

out = {
    "now": NOW.isoformat(), "late_read": LATE.isoformat(),
    "ingested": {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F},
    "facts_now": facts_now, "leads_now": leads_now,
    "reverify_queue_at_late": rq,
    "checks": checks, "passed": passed, "total": total,
}
with open(os.path.join(HERE, "results.json"), "w") as fh:
    json.dump(out, fh, indent=2, default=str)
print("wrote results.json and vault_backfill.json")
sys.exit(0 if passed == total else 1)
