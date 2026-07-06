#!/usr/bin/env python3
"""VAULT frozen entry gate — the whole game.

Doctrine (the box): *only a MACHINE-VERIFIED (or fetched-source) result enters as a
FACT.* Everything else is a clearly-labeled LEAD that is NEVER returned as truth.
A recalled FACT carries a freshness check; a high-stakes entry past its TTL is FLAGGED
stale on read, never silently served. The VAULT FLAGS staleness — it does NOT model
temporal change (the mem0-2026 open problem; see GROUNDING.md).

THE GATE IS A FUNCTION OF THE RECORD, NOT A MODEL JUDGMENT. The kappa=1 core is
`validate_verification_record`: a FACT-tier write is admitted ONLY if it ships with a
STRUCTURALLY VALID verification record (method / artifact / result, all NON-EMPTY).
This is the defense against the in-place LEAD-promotion attack: attaching
`{"verified": true}` or an empty `{"method":"","artifact":"","result":""}` record does
NOT promote a LEAD — the record must have real content.

LABELS / kappa HONESTY:
  - kappa=1 (EXACT, the entry gate): "does this write carry a structurally valid
    verification record?" is a deterministic, non-gameable code check. PASS/FAIL is not
    a matter of opinion. The record-validity check, the tier assignment, and "is this a
    FACT or a LEAD" are all kappa=1.
  - kappa<1 (JUDGMENT, NOT decided here): whether a FETCHED fact's *content* is still
    TRUE in the world after its TTL is a judgment / requires a fresh fetch. The VAULT
    does NOT adjudicate that — it FLAGS the entry stale and routes to re-verify. "High
    stakes" is a COMMITTED ENUM (see STAKES), not a model's guess.

"A gate that can't fail is not a gate": _selftest() requires the gate to
  (a) ACCEPT a result WITH a valid machine-verification record as a VERIFIED FACT,
  (b) REJECT a record-less FACT write -> demote to LEAD,
  (c) REJECT a present-but-EMPTY record (the in-place LEAD-promotion attack) -> LEAD,
  (d) FLAG a FETCHED entry past its TTL as stale on read (high-stakes -> RE-VERIFY),
  (e) NEVER return a LEAD in a facts query (only in a leads/hypotheses query),
  (f) preserve PROVENANCE round-trip (trace any fact back to its verification),
  plus every named reject case. All must pass or NOTHING the VAULT stores is trusted.
"""
import sys
import json
import os
import datetime

# --------------------------------------------------------------------------- #
#  committed constants — TTL per tier, stakes ENUM (NOT model judgments)
# --------------------------------------------------------------------------- #
# tier -> default TTL in days. None means "does not decay" (machine proofs are
# timeless: burma14's optimal tour length does not change with the calendar).
TTL_DAYS = {
    "VERIFIED_FACT": None,   # machine proof / certified object: no calendar decay
    "FETCHED_FACT": 30,      # a fetched source + URL + date: shorter TTL, re-fetch
    "LEAD": None,            # leads never expire into facts; they are never facts
}

# committed stakes ENUM. "high_stakes" is a property the WRITER must declare from this
# closed set; it is NOT inferred by a model at read time. A high-stakes stale read
# escalates to RE-VERIFY; a low-stakes stale read is FLAGged but may be served-with-flag.
STAKES = ("low", "high")

# the three required, NON-EMPTY fields of a minimum verification record.
REQUIRED_RECORD_FIELDS = ("method", "artifact", "result")

VALID_TIERS = ("VERIFIED_FACT", "FETCHED_FACT", "LEAD")


# --------------------------------------------------------------------------- #
#  time helpers (injectable `now` so TTL self-tests are deterministic)
# --------------------------------------------------------------------------- #
def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def _parse_ts(s):
    """Parse an ISO-8601 UTC timestamp (with or without trailing Z)."""
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def _iso(dt):
    return dt.astimezone(datetime.timezone.utc).isoformat()


# --------------------------------------------------------------------------- #
#  kappa=1 CORE — record validity (the gate-of-the-gate)
# --------------------------------------------------------------------------- #
def validate_verification_record(record):
    """Return (ok: bool, reason: str).

    A verification record is VALID iff it is a dict carrying every field in
    REQUIRED_RECORD_FIELDS, where EACH field is a NON-EMPTY STRING (after strip). This is
    the kappa=1 non-gameable check: a missing/empty/whitespace field FAILS. `{"verified":
    True}` FAILS (no method/artifact/result). This is the defense against in-place
    LEAD-promotion.

    TYPE RAIL (audit fix — Defect 2): each field MUST be a `str`. method/artifact/result
    are textual provenance ("how it was verified", "where the artifact lives", "what the
    result was"); a non-string value is semantically contentless even when it is "truthy".
    Without this rail, falsy-but-non-empty (`False`, int `0`) AND truthy-non-string
    (`42`, `3.14`, `True`) values slipped through the old emptiness predicate and were
    admitted as VERIFIED_FACT. `isinstance(v, bool)` is checked FIRST because in Python
    `bool` is a subclass of `int` and `True`/`False` are NOT acceptable record content.
    """
    if record is None:
        return False, "no verification record (None) — cannot enter as a FACT"
    if not isinstance(record, dict):
        return False, f"verification record must be a dict, got {type(record).__name__}"
    missing, empty, wrong_type = [], [], []
    for f in REQUIRED_RECORD_FIELDS:
        if f not in record:
            missing.append(f)
            continue
        v = record[f]
        # TYPE RAIL: must be a string. bool is checked explicitly (bool ⊂ int in Python,
        # so False/True would otherwise be classed as non-string-but-not-bool). This
        # rejects False, 0, 42, 3.14, True, [], {}, None — anything that is not real text.
        if isinstance(v, bool) or not isinstance(v, str):
            wrong_type.append((f, type(v).__name__))
            continue
        # non-empty after strip; reject "", "   " as contentless
        if v.strip() == "":
            empty.append(f)
    if missing:
        return False, f"verification record missing required field(s): {missing}"
    if wrong_type:
        return False, (f"verification record field(s) must be NON-EMPTY STRINGS, got "
                       f"non-string/contentless type(s): {wrong_type} — a falsy or "
                       f"non-text value (False/0/42/None/[]) does NOT verify anything; "
                       f"this is the type-confusion LEAD-promotion attack; REJECTED")
    if empty:
        return False, (f"verification record present-but-EMPTY field(s): {empty} "
                       f"— this is the in-place LEAD-promotion attack; REJECTED")
    return True, "valid verification record (method/artifact/result all non-empty strings)"


# --------------------------------------------------------------------------- #
#  WRITE gate — decide the tier from the RECORD, never from a self-claim
# --------------------------------------------------------------------------- #
def gate_write(entry, now=None):
    """Verifier-gated write. Returns a NORMALIZED stored entry (a dict) with the tier
    the gate ASSIGNED — which may DEMOTE the requested tier. Raises ValueError only on
    structurally unusable input (missing result/domain). The cardinal behavior: a
    FACT-tier request without a valid record is DEMOTED to LEAD (not raised) and the
    demotion reason is recorded.

    `entry` fields:
      result        (required, non-empty)   the claim/value being stored
      domain        (required, non-empty)   keying scope, e.g. "optimization.tsp"
      requested_tier (optional)             one of VALID_TIERS; default inferred
      verification_record (optional)        the method/artifact/result record
      stakes        (optional)              "low"|"high"; default "low"
      provenance    (optional)              free-form trace string/dict
      fetched_at    (optional)              ISO ts for FETCHED_FACT TTL anchor
    """
    now = now or _utcnow()

    # structural minimum: a result and a domain key, both non-empty
    result = entry.get("result")
    if result is None or (isinstance(result, str) and result.strip() == ""):
        raise ValueError("entry.result is required and must be non-empty")
    domain = entry.get("domain")
    if domain is None or (isinstance(domain, str) and domain.strip() == ""):
        raise ValueError("entry.domain is required and must be non-empty (keying scope)")

    stakes = entry.get("stakes", "low")
    if stakes not in STAKES:
        raise ValueError(f"stakes must be one of {STAKES} (committed ENUM), got {stakes!r}")

    requested = entry.get("requested_tier")
    if requested is not None and requested not in VALID_TIERS:
        raise ValueError(f"requested_tier must be one of {VALID_TIERS}, got {requested!r}")

    record = entry.get("verification_record")
    rec_ok, rec_reason = validate_verification_record(record)

    # ---- TIER ASSIGNMENT: the record decides, not the request -------------- #
    # A write asking for VERIFIED_FACT or FETCHED_FACT is admitted at that tier
    # ONLY if it carries a structurally valid record. Otherwise it is DEMOTED to LEAD.
    assigned_tier = "LEAD"
    demotion_reason = None

    if requested in ("VERIFIED_FACT", "FETCHED_FACT"):
        if rec_ok:
            assigned_tier = requested
        else:
            assigned_tier = "LEAD"
            demotion_reason = f"requested {requested} but {rec_reason}"
    elif requested == "LEAD":
        assigned_tier = "LEAD"
    else:
        # no explicit request: a valid record -> VERIFIED_FACT; else LEAD.
        assigned_tier = "VERIFIED_FACT" if rec_ok else "LEAD"
        if not rec_ok:
            demotion_reason = f"no requested tier and {rec_reason}"

    # ---- TTL anchoring ----------------------------------------------------- #
    written_at = _iso(now)
    valid_until = None
    ttl_days = TTL_DAYS[assigned_tier]
    if ttl_days is not None:
        if assigned_tier == "FETCHED_FACT":
            anchor = entry.get("fetched_at")
            anchor_dt = _parse_ts(anchor) if anchor else now
        else:
            anchor_dt = now
        valid_until = _iso(anchor_dt + datetime.timedelta(days=ttl_days))

    stored = {
        "result": result,
        "domain": domain,
        "tier": assigned_tier,
        "stakes": stakes,
        "verification_record": record if rec_ok else None,
        "record_valid": rec_ok,
        "record_check": rec_reason,
        "demotion_reason": demotion_reason,
        "provenance": entry.get("provenance"),
        "written_at": written_at,
        "fetched_at": entry.get("fetched_at"),
        "valid_until": valid_until,
        "ttl_days": ttl_days,
        # a LEAD carries the *unverified claim text* but NEVER a verification record;
        # keep the original requested tier for transparency/audit.
        "requested_tier": requested,
    }
    return stored


# --------------------------------------------------------------------------- #
#  READ — staleness check (kappa<1 routing: flag, don't reconcile)
# --------------------------------------------------------------------------- #
def staleness(stored, now=None):
    """Return (is_stale: bool, action: str). action in:
      'FRESH'              not expired (or non-decaying)
      'FLAG_STALE'        expired, low-stakes -> serve WITH a stale flag
      'REVERIFY'          expired, high-stakes -> must re-verify before reuse
    A LEAD is never 'fresh-as-fact'; staleness is only meaningful for FACT tiers.
    """
    now = now or _utcnow()
    vu = stored.get("valid_until")
    if vu is None:
        return False, "FRESH"  # non-decaying (VERIFIED_FACT proof / LEAD)
    expired = now > _parse_ts(vu)
    if not expired:
        return False, "FRESH"
    if stored.get("stakes") == "high":
        return True, "REVERIFY"
    return True, "FLAG_STALE"


def is_fact_tier(stored):
    return stored.get("tier") in ("VERIFIED_FACT", "FETCHED_FACT")


def trace_provenance(stored):
    """Provenance round-trip: from a stored FACT, return the verification trail. A FACT
    you cannot trace to its verification is NOT a fact -> returns None for a LEAD."""
    if not is_fact_tier(stored):
        return None
    return {
        "result": stored["result"],
        "tier": stored["tier"],
        "verification_method": (stored.get("verification_record") or {}).get("method"),
        "verification_artifact": (stored.get("verification_record") or {}).get("artifact"),
        "verification_result": (stored.get("verification_record") or {}).get("result"),
        "provenance": stored.get("provenance"),
        "written_at": stored.get("written_at"),
        "valid_until": stored.get("valid_until"),
    }


# --------------------------------------------------------------------------- #
#  the FROZEN self-test — adversarial, non-waivable
# --------------------------------------------------------------------------- #
def _selftest():
    fixed = datetime.datetime(2026, 6, 20, 12, 0, 0, tzinfo=datetime.timezone.utc)

    good_record = {
        "method": "CP-SAT optimal + Held-Karp DP + TSPLIB literature (3 independent)",
        "artifact": "weapons/optima/demo_reproduce/RESULT.json",
        "result": "burma14 optimal tour length = 3323",
    }

    # (a) ACCEPT-GOOD: a result WITH a valid machine-verification record -> VERIFIED FACT
    a = gate_write({"result": "burma14 optimal = 3323", "domain": "optimization.tsp",
                    "requested_tier": "VERIFIED_FACT", "verification_record": good_record,
                    "provenance": "OPTIMA weapon, season 2026-06"}, now=fixed)
    assert a["tier"] == "VERIFIED_FACT", a
    assert a["record_valid"] is True, a
    # reads back WITH its method (provenance round-trip)
    tr = trace_provenance(a)
    assert tr is not None and "CP-SAT" in tr["verification_method"], tr
    assert tr["verification_result"] == "burma14 optimal tour length = 3323", tr

    # (b) CATCH-BROKEN / record-less FACT write -> DEMOTED to LEAD (never a fact)
    b = gate_write({"result": "approach Y looked promising", "domain": "method.search",
                    "requested_tier": "VERIFIED_FACT"}, now=fixed)
    assert b["tier"] == "LEAD", b
    assert b["record_valid"] is False, b
    assert b["demotion_reason"] is not None, b
    assert trace_provenance(b) is None, "a LEAD must NOT yield a provenance trail"

    # (c) ABSTAIN-MALFORMED / the in-place LEAD-PROMOTION ATTACK:
    #     a present-but-EMPTY record must NOT promote a LEAD to a FACT.
    for bad_record, tag in [
        ({"verified": True}, "verified:true with no method/artifact/result"),
        ({"method": "", "artifact": "", "result": ""}, "all-empty-strings record"),
        ({"method": "   ", "artifact": "x", "result": "y"}, "whitespace-only method"),
        ({"method": "m", "artifact": "a"}, "missing result field"),
        ({"method": "m", "artifact": [], "result": "r"}, "empty-list artifact"),
        ({"method": None, "artifact": "a", "result": "r"}, "None method"),
        # --- AUDIT REGRESSION (Defect 2): type-confusion LEAD-promotion attack. A
        # falsy-but-non-empty (False / int 0) OR truthy-non-string (True / 42 / 3.14)
        # value used to pass the old emptiness predicate and be admitted as a FACT.
        # All must now FAIL validation and DEMOTE to LEAD. ---
        ({"method": False, "artifact": "x", "result": "y"}, "bool False method (Defect 2)"),
        ({"method": 0, "artifact": "x", "result": "y"}, "int 0 method (Defect 2)"),
        ({"method": True, "artifact": "x", "result": "y"}, "bool True method (Defect 2)"),
        ({"method": "m", "artifact": 42, "result": "r"}, "int 42 artifact (Defect 2)"),
        ({"method": "m", "artifact": "a", "result": 3.14}, "float result (Defect 2)"),
    ]:
        ok, reason = validate_verification_record(bad_record)
        assert ok is False, f"empty/partial/typed record wrongly accepted: {tag}"
        c = gate_write({"result": "promote me to a fact", "domain": "attack.promotion",
                        "requested_tier": "VERIFIED_FACT",
                        "verification_record": bad_record}, now=fixed)
        assert c["tier"] == "LEAD", f"LEAD-promotion attack SUCCEEDED via {tag}: {c}"
        assert c["verification_record"] is None, f"empty record stored as valid via {tag}"

    # a fully VALID record must PASS validation (the gate is not just always-reject)
    ok, _ = validate_verification_record(good_record)
    assert ok is True, "valid record wrongly rejected — gate is broken (always-reject)"

    # (d) STALE FETCHED FACT: a FETCHED entry past its TTL is FLAGGED on read.
    fetched_record = {
        "method": "WebFetch of vendor release page",
        "artifact": "https://example.org/releases (fetched 2026-03-01)",
        "result": "library X version = 1.14",
    }
    f_low = gate_write({"result": "library X version = 1.14", "domain": "infra.versions",
                        "requested_tier": "FETCHED_FACT", "stakes": "low",
                        "fetched_at": "2026-03-01T00:00:00Z",
                        "verification_record": fetched_record}, now=fixed)
    assert f_low["tier"] == "FETCHED_FACT" and f_low["valid_until"] is not None
    # fresh read right at fetch time
    fresh_now = _parse_ts("2026-03-10T00:00:00Z")
    stale0, act0 = staleness(f_low, now=fresh_now)
    assert stale0 is False and act0 == "FRESH", (stale0, act0)
    # read 100 days later (past the 30-day TTL) -> stale; low stakes -> FLAG_STALE
    late = _parse_ts("2026-06-10T00:00:00Z")
    stale1, act1 = staleness(f_low, now=late)
    assert stale1 is True and act1 == "FLAG_STALE", (stale1, act1)
    # high-stakes stale read -> must RE-VERIFY (not serve)
    f_high = gate_write({"result": "library X version = 1.14", "domain": "infra.versions",
                         "requested_tier": "FETCHED_FACT", "stakes": "high",
                         "fetched_at": "2026-03-01T00:00:00Z",
                         "verification_record": fetched_record}, now=fixed)
    stale2, act2 = staleness(f_high, now=late)
    assert stale2 is True and act2 == "REVERIFY", (stale2, act2)
    # a non-decaying VERIFIED_FACT is never stale, even years later
    s3, a3 = staleness(a, now=_parse_ts("2030-01-01T00:00:00Z"))
    assert s3 is False and a3 == "FRESH", (s3, a3)

    # (e) structural: a LEAD is a non-fact tier (the store layer enforces query routing;
    #     here we assert the gate never tags a record-less write as a fact tier)
    assert not is_fact_tier(b), "a LEAD must not be a fact tier"
    assert is_fact_tier(a), "a verified write must be a fact tier"

    # committed-constant sanity: TTL + stakes ENUM are committed, not model-judged
    assert TTL_DAYS["FETCHED_FACT"] == 30 and TTL_DAYS["VERIFIED_FACT"] is None
    assert STAKES == ("low", "high")
    try:
        gate_write({"result": "x", "domain": "d", "stakes": "CRITICAL"}, now=fixed)
        raise AssertionError("stakes outside the committed ENUM was accepted")
    except ValueError:
        pass
    # structural minimums enforced
    for bad in [{"domain": "d"}, {"result": "  ", "domain": "d"}, {"result": "r"}]:
        try:
            gate_write(bad, now=fixed)
            raise AssertionError(f"structurally-invalid entry accepted: {bad}")
        except ValueError:
            pass

    print("vault_gate selftest: PASS (accept-good VERIFIED FACT w/ provenance round-trip; "
          "record-less FACT->LEAD; in-place LEAD-promotion attack [verified:true / empty / "
          "whitespace / missing / empty-list / None] all REJECTED->LEAD; type-confusion "
          "attack [bool False/True / int 0 / int 42 / float] all REJECTED->LEAD (Defect 2); "
          "valid record still ACCEPTED; FETCHED stale->FLAG_STALE; high-stakes stale->REVERIFY; "
          "verified-fact never decays; stakes ENUM + structural minimums enforced)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(gate_write(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: vault_gate.py selftest | <entry.json>")
