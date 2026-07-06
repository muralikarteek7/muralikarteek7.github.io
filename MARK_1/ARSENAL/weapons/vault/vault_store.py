#!/usr/bin/env python3
"""VAULT store — persistence + the read CONTRACT on top of the frozen gate.

The store is thin on purpose: ALL admission logic lives in vault_gate (kappa=1). The
store adds (1) a JSON-backed persistent record set, and (2) the READ CONTRACT:

  - query_facts(query)   -> ONLY FACT-tier entries (VERIFIED_FACT / FETCHED_FACT),
                            each annotated with its freshness (FRESH / FLAG_STALE /
                            REVERIFY). A LEAD is NEVER returned here. This is the
                            cardinal rule — an unverified belief must never masquerade
                            as a fact.
  - query_leads(query)   -> ONLY LEAD-tier entries, surfaced as hypotheses-to-test,
                            never as truth.

Self-tests (vault_store._selftest) assert the read contract directly: a LEAD written
into the store is invisible to query_facts and visible to query_leads; a stale fact is
returned WITH its flag, not silently; provenance survives the round-trip through disk.
"""
import sys
import os
import json
import tempfile

import vault_gate as G


class Vault:
    def __init__(self, path=None):
        # path=None -> in-memory only (tests); a path persists to JSON.
        self.path = path
        self.entries = []
        if path and os.path.exists(path):
            with open(path) as fh:
                self.entries = json.load(fh)
            self._reload_integrity_check()

    # ---- persistence ------------------------------------------------------- #
    def _flush(self):
        if not self.path:
            return
        # atomic write
        d = os.path.dirname(os.path.abspath(self.path))
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
        with os.fdopen(fd, "w") as fh:
            json.dump(self.entries, fh, indent=2)
        os.replace(tmp, self.path)

    # ---- reload integrity gate (audit fix 2026-06-21) ---------------------- #
    def _reload_integrity_check(self):
        """On RELOAD, on-disk entries are UNTRUSTED: a hand-edited JSON could flip a LEAD's
        tier to a FACT tier (the gate otherwise only runs on write). Re-derive — any
        fact-tier entry whose verification_record is missing/invalid is DEMOTED to LEAD (the
        same invariant gate_write enforces on write), so query_facts can never serve a
        tampered fact. (Closes the independent-audit reload-trust defect.)"""
        for s in self.entries:
            if (isinstance(s, dict) and G.is_fact_tier(s)
                    and not G.validate_verification_record(s.get("verification_record"))[0]):
                s["tier"] = "LEAD"
                s["record_valid"] = False
                s["integrity_note"] = ("DEMOTED on reload: fact tier without a valid "
                                       "verification_record (tamper guard)")

    # ---- write (delegates admission to the frozen gate) -------------------- #
    def write(self, entry, now=None):
        """Gate the write, persist the NORMALIZED stored entry, return a COPY. The gate
        may DEMOTE a record-less FACT request to a LEAD; the store stores whatever tier
        the gate assigned — it never overrides the gate.

        COPY-ON-RETURN (audit fix — Defect 1): the dict appended to self.entries and the
        dict returned to the caller MUST be DISTINCT objects. Previously they were the
        same object, so a caller holding the returned reference could mutate the live
        stored entry in place (e.g. flip tier LEAD->VERIFIED_FACT, record_valid->True)
        and have it instantly visible to query_facts() — promoting a LEAD to a FACT with
        no gate. The disk-backed Vault was incidentally safe (a fresh reload re-serializes
        from JSON), but the in-memory Vault was not. We now JSON round-trip the gate's
        output so the stored copy and the returned copy share no references; mutating
        either one cannot affect the other. (gate output is always JSON-serializable —
        the same shape we flush to disk.)
        """
        stored = G.gate_write(entry, now=now)
        stored = json.loads(json.dumps(stored))   # detach from the gate's object
        self.entries.append(stored)
        self._flush()
        return json.loads(json.dumps(stored))     # return a SEPARATE copy (Defect 1)

    # ---- read contract ----------------------------------------------------- #
    def _match(self, stored, query):
        """Cheap keying: substring match on domain or result. Multi-scope keying
        (domain + free text) is supported; precise retrieval is out of scope (see
        README ceiling — literal-key retrieval, not semantic)."""
        if not query:
            return True
        q = query.lower()
        return (q in str(stored.get("domain", "")).lower()
                or q in str(stored.get("result", "")).lower())

    def query_facts(self, query="", now=None):
        """Return ONLY fact-tier entries matching `query`, each annotated with freshness.
        A LEAD is NEVER returned here — the cardinal invariant, asserted in _selftest."""
        out = []
        for s in self.entries:
            if not G.is_fact_tier(s):
                continue                      # <-- the LEAD is filtered out HERE
            if not self._match(s, query):
                continue
            is_stale, action = G.staleness(s, now=now)
            out.append({
                "result": s["result"],
                "domain": s["domain"],
                "tier": s["tier"],
                "stakes": s["stakes"],
                "freshness": action,           # FRESH / FLAG_STALE / REVERIFY
                "is_stale": is_stale,
                "verification_method": (s.get("verification_record") or {}).get("method"),
                "provenance": s.get("provenance"),
                "valid_until": s.get("valid_until"),
            })
        return out

    def query_leads(self, query="", now=None):
        """Return ONLY lead-tier entries, surfaced as hypotheses-to-test (never truth)."""
        out = []
        for s in self.entries:
            if s.get("tier") != "LEAD":
                continue
            if not self._match(s, query):
                continue
            out.append({
                "hypothesis": s["result"],
                "domain": s["domain"],
                "tier": "LEAD",
                "status": "UNVERIFIED — surfaced as a hypothesis to TEST, never as a fact",
                "demotion_reason": s.get("demotion_reason"),
                "provenance": s.get("provenance"),
            })
        return out

    def reverify_queue(self, now=None):
        """High-stakes fact-tier entries whose freshness == REVERIFY — the to-do list
        the box must clear (re-fetch / re-run) before reusing them."""
        return [f for f in self.query_facts(now=now) if f["freshness"] == "REVERIFY"]


def _selftest():
    import datetime
    fixed = datetime.datetime(2026, 6, 20, 12, 0, 0, tzinfo=datetime.timezone.utc)
    v = Vault(path=None)

    good = {"method": "SYMBOLICA agreement gate (sympy+mpmath+scipy, 30 digits)",
            "artifact": "weapons/symbolica/demo_agreement/results.json",
            "result": "zeta(2) = pi^2/6 ~= 1.6449340668"}

    # write a VERIFIED FACT, a FETCHED FACT, and a LEAD
    v.write({"result": "zeta(2) = pi^2/6", "domain": "math.special_values",
             "requested_tier": "VERIFIED_FACT", "verification_record": good,
             "provenance": "SYMBOLICA, season 2026-06"}, now=fixed)
    v.write({"result": "library X version = 1.14", "domain": "infra.versions",
             "requested_tier": "FETCHED_FACT", "stakes": "high",
             "fetched_at": "2026-03-01T00:00:00Z",
             "verification_record": {"method": "WebFetch", "artifact": "https://x/releases",
                                     "result": "1.14"}}, now=fixed)
    lead = v.write({"result": "decomposition might cut cost 5x", "domain": "method.cost",
                    "requested_tier": "LEAD", "provenance": "session hunch"}, now=fixed)
    assert lead["tier"] == "LEAD"
    # a record-less FACT request also lands as a LEAD
    sneaky = v.write({"result": "I believe approach Z is optimal", "domain": "method.cost",
                      "requested_tier": "VERIFIED_FACT"}, now=fixed)
    assert sneaky["tier"] == "LEAD", sneaky

    # (d-read) cardinal rule: NO lead in a facts query, even when text matches
    facts = v.query_facts(query="", now=fixed)
    fact_results = [f["result"] for f in facts]
    assert "zeta(2) = pi^2/6" in fact_results
    assert "decomposition might cut cost 5x" not in fact_results, "LEAD leaked into facts!"
    assert "I believe approach Z is optimal" not in fact_results, "demoted FACT leaked!"
    assert all(f["tier"] in ("VERIFIED_FACT", "FETCHED_FACT") for f in facts)
    # a domain query that overlaps a lead's domain still returns no leads
    cost_facts = v.query_facts(query="method.cost", now=fixed)
    assert cost_facts == [], "facts query returned a lead via domain match"

    # leads are visible ONLY in the leads query, labeled as hypotheses
    leads = v.query_leads(query="", now=fixed)
    lead_h = [l["hypothesis"] for l in leads]
    assert "decomposition might cut cost 5x" in lead_h
    assert "I believe approach Z is optimal" in lead_h
    assert all(l["tier"] == "LEAD" and "never as a fact" in l["status"] for l in leads)

    # (c-mutation) AUDIT REGRESSION (Defect 1): the dict returned by write() must NOT be
    # the same object stored in v.entries. A caller mutating the returned reference must
    # NOT be able to promote a stored LEAD to a FACT (or tamper with a stored fact's
    # verification record). Before the copy-on-return fix this BYPASSED the gate on the
    # in-memory Vault: stored['tier']='VERIFIED_FACT' made query_facts() return the LEAD.
    vm = Vault(path=None)
    ret_lead = vm.write({"result": "promote-me-by-mutation", "domain": "attack.mutate",
                         "requested_tier": "VERIFIED_FACT",
                         "provenance": "no record -> demoted to LEAD"}, now=fixed)
    assert ret_lead["tier"] == "LEAD", ret_lead
    # attacker mutates the returned reference, trying to flip the live stored entry
    ret_lead["tier"] = "VERIFIED_FACT"
    ret_lead["record_valid"] = True
    ret_lead["verification_record"] = {"method": "forged", "artifact": "f", "result": "f"}
    leaked = [f for f in vm.query_facts(query="attack.mutate")]
    assert leaked == [], f"Defect 1: returned-dict mutation promoted a LEAD to a FACT: {leaked}"
    assert "promote-me-by-mutation" in [l["hypothesis"] for l in vm.query_leads(query="attack.mutate")], \
        "Defect 1: the entry should still be a LEAD after the bypass attempt"
    # and mutating a real fact's returned record must not tamper with the stored fact
    ret_fact = vm.write({"result": "untampered-fact", "domain": "attack.mutate2",
                         "requested_tier": "VERIFIED_FACT",
                         "verification_record": {"method": "real-method",
                                                 "artifact": "a", "result": "r"}}, now=fixed)
    assert ret_fact["tier"] == "VERIFIED_FACT", ret_fact
    ret_fact["verification_record"]["method"] = "TAMPERED"
    ret_fact["result"] = "TAMPERED"
    sf = vm.query_facts(query="attack.mutate2")
    assert len(sf) == 1 and sf[0]["verification_method"] == "real-method", \
        f"Defect 1: nested-dict mutation tampered the stored fact: {sf}"
    assert sf[0]["result"] == "untampered-fact", f"Defect 1: stored result tampered: {sf}"

    # (c-reload) AUDIT REGRESSION (2026-06-21): on-disk entries are UNTRUSTED. A hand-edited
    # JSON flipping a LEAD to a FACT tier (no real record) must be DEMOTED on reload, never
    # served by query_facts.
    _p = tempfile.mktemp(suffix=".json")
    _v = Vault(_p)
    _v.write({"domain": "attack.reload", "result": "reload-hunch",
              "requested_tier": "LEAD", "provenance": "session hunch"})
    _raw = json.load(open(_p)); _raw[0]["tier"] = "VERIFIED_FACT"; _raw[0]["record_valid"] = True
    json.dump(_raw, open(_p, "w"))
    _v2 = Vault(_p)
    assert _v2.query_facts(query="attack.reload") == [], "reload tamper: forged fact served after reload!"
    assert _v2.entries[0]["tier"] == "LEAD", "reload tamper: forged fact not demoted"
    os.remove(_p)

    # (d-stale) high-stakes fetched fact past TTL -> returned WITH a REVERIFY flag,
    # never silently served; it shows up on the reverify queue.
    late = datetime.datetime(2026, 6, 10, 0, 0, 0, tzinfo=datetime.timezone.utc)
    # (note: written at 'fixed', fetched_at 2026-03-01, TTL 30d -> expires ~2026-03-31)
    flate = v.query_facts(query="infra.versions", now=late)
    assert len(flate) == 1 and flate[0]["freshness"] == "REVERIFY" and flate[0]["is_stale"]
    rq = v.reverify_queue(now=late)
    assert len(rq) == 1 and rq[0]["result"] == "library X version = 1.14"
    # before TTL it is FRESH
    early = datetime.datetime(2026, 3, 10, 0, 0, 0, tzinfo=datetime.timezone.utc)
    fearly = v.query_facts(query="infra.versions", now=early)
    assert fearly[0]["freshness"] == "FRESH" and not fearly[0]["is_stale"]

    # (e) provenance survives a round-trip THROUGH DISK
    tmp = tempfile.mktemp(suffix=".json")
    try:
        vd = Vault(path=tmp)
        vd.write({"result": "burma14 optimal = 3323", "domain": "optimization.tsp",
                  "requested_tier": "VERIFIED_FACT",
                  "verification_record": {"method": "CP-SAT==Held-Karp==TSPLIB",
                                          "artifact": "optima/RESULT.json",
                                          "result": "3323"},
                  "provenance": "OPTIMA 2026-06"}, now=fixed)
        reloaded = Vault(path=tmp)
        rf = reloaded.query_facts(query="burma14", now=fixed)
        assert len(rf) == 1
        assert rf[0]["verification_method"] == "CP-SAT==Held-Karp==TSPLIB"
        assert rf[0]["provenance"] == "OPTIMA 2026-06"
        # the demoted-lead also survives disk and stays out of facts
        reloaded.write({"result": "untraceable claim", "domain": "x",
                        "requested_tier": "VERIFIED_FACT"}, now=fixed)
        r2 = Vault(path=tmp)
        assert "untraceable claim" not in [f["result"] for f in r2.query_facts(now=fixed)]
        assert "untraceable claim" in [l["hypothesis"] for l in r2.query_leads(now=fixed)]
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    print("vault_store selftest: PASS (facts query returns FACT tiers only — NO lead leak "
          "even on domain match; leads query returns hypotheses-only; returned-dict mutation "
          "CANNOT promote a LEAD or tamper a stored fact [copy-on-return, Defect 1]; "
          "high-stakes stale FETCHED fact -> REVERIFY flag + reverify_queue, never silent; "
          "FRESH before TTL; provenance + tier survive disk round-trip)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    else:
        print("usage: vault_store.py selftest")
