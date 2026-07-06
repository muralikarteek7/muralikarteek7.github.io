#!/usr/bin/env python3
"""GLOVES frozen actuation-safety gate.

The hands that touch the external world, SAFELY. ARMOR's rule is "abstain when
uncertain about a CLAIM"; GLOVES' rule is "require explicit authorization before
an irreversible STATE CHANGE." A wrong claim can be retracted; a sent wire, a
deleted table, a mass email cannot.

  verdict(action) -> {
      "tier":     AUTO | CONFIRM | STEP-UP | ABSTAIN,
      "decision": ALLOW | BLOCK,
      "alarm":    bool,        # True for self-protection / forged-token alarms
      "reason":   str,
      "blast_units": int,      # added to the per-run accumulator on ALLOW
      "ledger":   dict | None, # the append-only ledger entry (written BEFORE the call)
  }

KAPPA HONESTY (kickoff §1, restated per audit Finding 2 + cross-model audit DEFECT-1):
  - token/param/expiry/single-use/scope are kappa=1 end-to-end (the math is exact and
    verified against the EXTERNAL signing key the agent cannot read).
  - DRY-RUN->COMMIT binding is kappa=1 ONLY on the kappa=1 PATH: when the EXTERNAL
    authority SIGNS the dry-run artifact hash into the token (token.dry_run_artifact_hash),
    the agent cannot forge it. WITHOUT that token attestation, the gate's required-field
    equality check (dry_run_hash == dry_run_artifact_hash, both REQUIRED for needs_dry_run
    tools) is PROTOCOL-LEVEL / ARMOR-class only: in a pure-software box the caller controls
    BOTH fields, so it stops the "fake reference, omit artifact" bypass but cannot prove a
    real dry-run ran. (Pre-fix the artifact field was optional -> a fake hash false-accepted;
    that hole is closed.) Do NOT label the bare-field path kappa=1.
  - the reversibility-class LOOKUP is kappa=1 WITHIN the frozen registry, kappa<1 ACROSS
    registry population (an absent/under-declared tool is the attack surface -> unknown
    tool_id ABSTAINS).
  - the self-protection rail is kappa=1 ONLY IF registry/ledger write-scope is
    infra-enforced; in a pure-software box it is gate-level (ARMOR-class) -> the
    suite self-tests the write-scope and LABELS the rail accordingly (self-test k).
    The detector now scans params RECURSIVELY (nested dict/list) on KEY and VALUE
    substrings (audit DEFECT-2/DEFECT-3).
  - the risk-CLASSIFICATION boundary ("is this R2 or R3?") is kappa<1 -> ABSTAIN.

THE SIGNING KEY IS THE SECURITY BOUNDARY (kickoff Finding 7 / self-test l):
  tokens are HMAC-signed by an authority OUTSIDE the agent. The key is supplied at
  verify time from an external secret store; it is NOT in this repo, NOT in the
  agent's context. A token the agent can mint with a key it can read is NO token.

FAIL CLOSED (kickoff Finding 4 / self-test h):
  the ENTIRE decision path is wrapped: any uncaught exception -> BLOCK + ALARM,
  never ALLOW. A registry-read failure, a hash/lib crash, a malformed param denies.
"""
import hashlib
import hmac
import json
import time

from tool_risk_registry import (
    lookup, tier_rank, is_self_protect_target, TIERS,
)

# ---------------------------------------------------------------------------
# Canonical action hashing (kappa=1): the token binds to the EXACT params.
# Param drift (send to A vs send to B) changes the hash -> token mismatch -> BLOCK.
# ---------------------------------------------------------------------------

def canonical_action_hash(tool_id, params):
    """Deterministic hash of (tool_id, params). Sorted-keys JSON => stable, exact."""
    payload = json.dumps(
        {"tool_id": tool_id, "params": params},
        sort_keys=True, separators=(",", ":"), default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sign_token(payload_dict, signing_key):
    """Produce an HMAC signature over the canonical token payload.

    Used by the EXTERNAL granting authority only (and by self-tests that simulate
    a legitimate external grant). The gate itself never holds `signing_key`; it is
    passed to verify() from outside (see verdict(..., signing_key=...))."""
    if not isinstance(signing_key, (bytes, bytearray)):
        raise TypeError("signing_key must be bytes (an external secret), not a string literal in the agent context")
    body = json.dumps(payload_dict, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(signing_key, body, hashlib.sha256).hexdigest()


def _token_payload(tok):
    """The signed portion of a token (everything except the signature itself)."""
    return {k: tok[k] for k in tok if k != "sig"}


# Track single-use token ids that have already been spent (replay protection for
# non-idempotent actions). In a real deployment this lives in the tamper-resistant
# ledger store, NOT in agent-writable memory (see infra-limit, kickoff §4).
_SPENT_TOKEN_IDS = set()


def reset_spent_tokens():
    """Test/Run hook: clear the single-use ledger between independent runs."""
    _SPENT_TOKEN_IDS.clear()


def verify_token(tok, tool_id, params, action_tier, signing_key, now=None,
                 dry_run_artifact_hash=None, commit_spend=True):
    """kappa=1 token verification. Returns (ok: bool, reason: str).

    A CONFIRM/STEP-UP action is ALLOWable IFF:
      1. the token is signed by the EXTERNAL key (signature verifies),
      2. hash(exact params) == token.action_hash         (no param drift),
      3. now < expiry                                     (not stale),
      4. scope tier-rank >= action tier-rank             (scope covers the tier),
      5. if the token ATTESTS a dry-run artifact (token.dry_run_artifact_hash
         present), the action's declared dry_run_artifact_hash must MATCH it
         (audit DEFECT-1: the dry-run binding is kappa=1 only when the EXTERNAL
         authority signs the artifact hash — a string the agent cannot forge),
      6. for a non-idempotent action: token id is single-use & unspent (no replay).
    Any failure -> (False, reason). No exception escapes to ALLOW (caller fail-closes).

    REPLAY SELF-CONTAINMENT (audit DEFECT-4): when `commit_spend=True` (the default,
    used by verdict()), a successful single-use verification marks the token spent
    HERE, atomically, so a second call to verify_token() with the same token is a
    `replay` REJECT even when the caller bypasses verdict(). Callers that want a
    pure pre-check WITHOUT consuming the token pass `commit_spend=False` and get a
    'ok:single-use-UNCOMMITTED:<id>' signal they must NOT treat as single-use-safe."""
    now = time.time() if now is None else now
    if not isinstance(tok, dict):
        return False, "token-malformed (not a dict)"
    for field in ("action_hash", "scope", "issued_ts", "expiry", "token_id", "granter", "sig"):
        if field not in tok:
            return False, f"token-missing-field:{field}"

    # 1. signature must verify against the EXTERNAL key (forgery check).
    if signing_key is None:
        return False, "no-external-signing-key (gate cannot verify -> fail closed)"
    try:
        expected = sign_token(_token_payload(tok), signing_key)
    except Exception as e:  # bad key type, etc. -> fail closed
        return False, f"signature-compute-failed:{type(e).__name__}"
    if not hmac.compare_digest(expected, str(tok["sig"])):
        return False, "signature-invalid (forged or wrong key)"

    # 2. param binding: token must match the EXACT call params (bait-and-switch).
    want_hash = canonical_action_hash(tool_id, params)
    if not hmac.compare_digest(str(tok["action_hash"]), want_hash):
        return False, "param-mismatch (token bound to different parameters)"

    # 3. expiry.
    try:
        if now >= float(tok["expiry"]):
            return False, "expired"
    except Exception:
        return False, "expiry-unparseable (fail closed)"

    # 4. scope must COVER the action tier (CONFIRM-scoped token for STEP-UP -> reject).
    scope = tok["scope"]
    if scope not in TIERS:
        return False, f"scope-unknown:{scope}"
    if tier_rank(scope) < tier_rank(action_tier):
        return False, f"scope-too-low (token scope {scope} < action tier {action_tier})"

    # 5. dry-run artifact attestation (kappa=1 path for the dry-run binding).
    #    If the EXTERNAL authority signed an artifact hash into the token, the action's
    #    declared artifact hash MUST match it. The agent cannot forge the signed token,
    #    so this binds the commit to a dry-run the authority saw. (audit DEFECT-1)
    attested = tok.get("dry_run_artifact_hash")
    if attested is not None:
        if dry_run_artifact_hash is None:
            return False, "dry-run-artifact-missing (token attests an artifact; action declared none)"
        if not hmac.compare_digest(str(attested), str(dry_run_artifact_hash)):
            return False, "dry-run-artifact-mismatch (declared artifact != token-attested artifact)"

    # 6. single-use / replay for non-idempotent actions.
    entry = lookup(tool_id)
    idempotent = bool(entry and entry.get("idempotent"))
    if not idempotent:
        tid = str(tok["token_id"])
        if tid in _SPENT_TOKEN_IDS:
            return False, "replay (single-use token already spent)"
        if commit_spend:
            # mark spent HERE so verify_token is replay-safe even called directly
            # (audit DEFECT-4: was a footgun — returned ok twice when bypassing verdict()).
            _SPENT_TOKEN_IDS.add(tid)
            return True, ("ok:single-use:" + tid)
        # pure pre-check: NOT consumed -> caller is warned it is not yet replay-safe.
        return True, ("ok:single-use-UNCOMMITTED:" + tid)
    return True, "ok"


# ---------------------------------------------------------------------------
# The gate: verdict(). EVERYTHING is wrapped fail-closed.
# ---------------------------------------------------------------------------

def _verdict_inner(action, signing_key, now):
    tool_id = action.get("tool_id")
    params = action.get("params", {})
    token = action.get("token")               # optional confirmation token
    dry_run_hash = action.get("dry_run_hash") # for R1+ commits

    # (0) SELF-PROTECTION RAIL — checked FIRST, before tiering, no token overrides it.
    # The agent must not be able to modify its own controls (CVE-2025-53773).
    if is_self_protect_target(tool_id, params):
        return {
            "tier": "STEP-UP", "decision": "BLOCK", "alarm": True,
            "reason": "SELF-PROTECTION: action targets GLOVES' own config/registry/"
                      "ledger/approval-state or flips an auto-approve flag "
                      "(CVE-2025-53773 rail). Hard-blocked; no token overrides.",
            "blast_units": 0, "ledger": None,
        }

    # (1) REGISTRY LOOKUP — unknown tool_id -> ABSTAIN (default-deny, Finding 1).
    entry = lookup(tool_id)
    if entry is None:
        return {
            "tier": "ABSTAIN", "decision": "BLOCK", "alarm": False,
            "reason": f"UNKNOWN/unregistered tool_id '{tool_id}' -> ABSTAIN "
                      "(default-deny; an absent tool is the attack surface).",
            "blast_units": 0, "ledger": None,
        }

    tier = entry["tier"]

    # (2) AUTO — R0 reversible, blast-local -> execute + log, no friction.
    if tier == "AUTO":
        led = _ledger_entry(tool_id, params, tier, "policy:AUTO-R0-local",
                            dry_run_hash, entry["blast_units"])
        return {"tier": "AUTO", "decision": "ALLOW", "alarm": False,
                "reason": "AUTO (R0 reversible, blast-local): execute + log.",
                "blast_units": entry["blast_units"], "ledger": led}

    # (3) DRY-RUN -> COMMIT binding for R1+ : commit must reference a dry-run artifact
    #     AND declare the artifact hash that was actually produced; absent OR mismatched
    #     -> BLOCK (Finding 6e, self-test j; audit DEFECT-1 hardening).
    #
    #     HONEST KAPPA (audit DEFECT-1): in a pure-software box the caller controls BOTH
    #     dry_run_hash and dry_run_artifact_hash, so the field-equality check alone is
    #     PROTOCOL-LEVEL (ARMOR-class), NOT kappa=1 — it stops the "fake reference, omit
    #     artifact" bypass but cannot prove a real dry-run ran. The dry-run binding is
    #     kappa=1 ONLY when the EXTERNAL authority signs the artifact hash INTO the token
    #     (verify_token step 5); then the agent cannot fabricate it. The required-field
    #     check below closes the false-accept; the token attestation provides the kappa=1
    #     path. See SPEC.md §2 + GROUNDING.md for the label.
    declared_artifact = action.get("dry_run_artifact_hash")  # the preview that WAS produced
    if entry.get("needs_dry_run"):
        if not dry_run_hash:
            return {"tier": tier, "decision": "BLOCK", "alarm": False,
                    "reason": "commit with NO dry-run reference (absent hash) -> BLOCK.",
                    "blast_units": 0, "ledger": None}
        # REQUIRE the produced-artifact hash (no longer optional): a non-empty
        # dry_run_hash with the artifact omitted previously slipped through (DEFECT-1).
        if not declared_artifact:
            return {"tier": tier, "decision": "BLOCK", "alarm": False,
                    "reason": "commit declares a dry-run REFERENCE but NO produced-artifact "
                              "hash (dry_run_artifact_hash required for needs_dry_run tools; "
                              "a bare reference string is not a dry-run) -> BLOCK.",
                    "blast_units": 0, "ledger": None}
        if not hmac.compare_digest(str(dry_run_hash), str(declared_artifact)):
            return {"tier": tier, "decision": "BLOCK", "alarm": False,
                    "reason": "dry-run hash MISMATCH (commit references a different "
                              "preview than was produced) -> BLOCK.",
                    "blast_units": 0, "ledger": None}

    # (4) CONFIRM / STEP-UP — require a valid param-bound token.
    if token is None:
        # No token: a STEP-UP action can NEVER be self-approved; CONFIRM also blocks.
        return {"tier": tier, "decision": "BLOCK", "alarm": (tier == "STEP-UP"),
                "reason": f"{tier} action carries NO authorization token -> BLOCK"
                          + (" (STEP-UP: the agent cannot self-approve; routes to a human)."
                             if tier == "STEP-UP" else " (token bound to exact params required)."),
                "blast_units": 0, "ledger": None}

    ok, why = verify_token(token, tool_id, params, tier, signing_key, now=now,
                           dry_run_artifact_hash=declared_artifact, commit_spend=True)
    if not ok:
        # a forged/replayed/param-drifted/scope-mismatched/artifact-mismatched token is
        # an ALARM-worthy event.
        alarm = why.startswith(("signature-invalid", "param-mismatch", "replay",
                                "scope-too-low", "dry-run-artifact"))
        return {"tier": tier, "decision": "BLOCK", "alarm": alarm,
                "reason": f"{tier} token REJECTED: {why}.",
                "blast_units": 0, "ledger": None}

    # token valid: single-use spend was committed atomically INSIDE verify_token
    # (audit DEFECT-4: replay protection is now self-contained, not caller-committed).

    led = _ledger_entry(tool_id, params, tier, f"token:{token['token_id']}",
                        dry_run_hash, entry["blast_units"])
    return {"tier": tier, "decision": "ALLOW", "alarm": False,
            "reason": f"{tier}: valid param-bound, unexpired, scope-covering token "
                      f"(granter={token['granter']}). ALLOW + log.",
            "blast_units": entry["blast_units"], "ledger": led}


def _ledger_entry(tool_id, params, tier, authz, dry_run_hash, blast_units):
    """The append-only ledger record — written BEFORE the call fires.

    INFRA LIMIT (kickoff §4): in a pure-software box this store is NOT guaranteed
    outside the agent's write scope. An audit log the agent can rewrite is not an
    audit log. True tamper-resistance needs fs-perms / a separate process / the
    harness. The running blast-radius accumulator lives here until G3 ships
    (Finding 1c) so the silent-composition hole is visible."""
    return {
        "tool_id": tool_id,
        "params": params,
        "tier": tier,
        "authorization": authz,
        "dry_run_hash": dry_run_hash,
        "blast_units": blast_units,
        "ts": time.time(),
        "G3_note": "per-action only; composition gated by G3 (not yet shipped).",
    }


def verdict(action, signing_key=None, now=None):
    """The gate. FAIL CLOSED: any uncaught exception -> BLOCK + ALARM, never ALLOW.

    `signing_key` is supplied by the CALLER from an EXTERNAL secret store; the gate
    does not own it. `now` is injectable for deterministic expiry tests."""
    try:
        if not isinstance(action, dict):
            raise TypeError("action must be a dict")
        return _verdict_inner(action, signing_key, now)
    except Exception as e:
        # Fail-closed: ANYTHING that goes wrong denies. (Finding 4 / self-test h.)
        return {
            "tier": "ABSTAIN", "decision": "BLOCK", "alarm": True,
            "reason": f"FAIL-CLOSED on exception in gate path: {type(e).__name__}: {e}",
            "blast_units": 0, "ledger": None,
        }


# A per-run blast-radius accumulator (Finding 1c). Until G3, this only RECORDS;
# G3 will gate when the running total crosses a budget.
class BlastAccumulator:
    def __init__(self, budget=None):
        self.total = 0
        self.budget = budget
        self.events = []

    def add(self, v):
        self.total += int(v)
        self.events.append(int(v))
        # GLOVES does not BLOCK on composition (that is G3's job); it FLAGS.
        over = (self.budget is not None and self.total > self.budget)
        return {"running_total": self.total, "over_budget_FLAG": over,
                "g3_note": "GLOVES is per-action; G3 gates the composition. FLAG only."}


# ===========================================================================
# THE TWELVE NON-WAIVABLE GATE-OF-THE-GATE SELF-TESTS (kickoff §3, a..l)
# ===========================================================================

# A simulated EXTERNAL signing key. In the self-tests this stands in for the
# secret store the granting authority holds. It is bytes, passed in at verify time;
# the gate never reads it from disk/context on its own.
_EXTERNAL_KEY = b"EXTERNAL-SECRET-not-in-agent-context-or-repo-vault-only"


def _grant(tool_id, params, scope, ttl=300, now=None, token_id="tok-1",
           granter="human:alice", dry_run_artifact_hash=None):
    """Helper: a LEGITIMATE external authority mints a param-bound token.

    If `dry_run_artifact_hash` is supplied, the authority SIGNS it into the token,
    giving the kappa=1 dry-run binding (the agent cannot forge a signed artifact)."""
    now = time.time() if now is None else now
    payload = {
        "action_hash": canonical_action_hash(tool_id, params),
        "scope": scope,
        "issued_ts": now,
        "expiry": now + ttl,
        "token_id": token_id,
        "granter": granter,
    }
    if dry_run_artifact_hash is not None:
        payload["dry_run_artifact_hash"] = dry_run_artifact_hash
    payload["sig"] = sign_token(payload, _EXTERNAL_KEY)
    return payload


def _selftest():
    reset_spent_tokens()
    key = _EXTERNAL_KEY
    t0 = 1_000_000.0

    # (a) AUTO-allow an R0/B-local read with no friction, no token.
    v = verdict({"tool_id": "fs.read", "params": {"path": "/tmp/x"}}, signing_key=key, now=t0)
    assert v["tier"] == "AUTO" and v["decision"] == "ALLOW" and v["ledger"] is not None, v
    assert v["alarm"] is False, v

    # (b) BLOCK an R3/irreversible (STEP-UP) action carrying NO token.
    #     (matching dry_run_hash + artifact so we get PAST the dry-run gate and the BLOCK
    #     is attributable to the missing token, the property this case exercises.)
    v = verdict({"tool_id": "db.drop_table", "params": {"table": "users"},
                 "dry_run_hash": "abc", "dry_run_artifact_hash": "abc"},
                signing_key=key, now=t0)
    assert v["tier"] == "STEP-UP" and v["decision"] == "BLOCK", v
    assert v["alarm"] is True, v  # STEP-UP no-token alarms (cannot self-approve)
    assert "NO authorization token" in v["reason"], v

    # (c) REJECT a parameter-mismatched token: issued for send->A, call is send->B.
    tok_A = _grant("email.send_one", {"to": "A", "body": "hi"}, scope="CONFIRM", now=t0)
    v = verdict({"tool_id": "email.send_one", "params": {"to": "B", "body": "hi"},
                 "token": tok_A}, signing_key=key, now=t0)
    assert v["decision"] == "BLOCK" and "param-mismatch" in v["reason"], v
    assert v["alarm"] is True, v
    # ...and the SAME token DOES allow the action it was bound to (positive control).
    reset_spent_tokens()
    v_good = verdict({"tool_id": "email.send_one", "params": {"to": "A", "body": "hi"},
                      "token": _grant("email.send_one", {"to": "A", "body": "hi"},
                                      scope="CONFIRM", now=t0, token_id="tok-good")},
                     signing_key=key, now=t0)
    assert v_good["decision"] == "ALLOW", v_good

    # (d) REJECT an EXPIRED token, and a single-use token presented TWICE (replay).
    reset_spent_tokens()
    tok_exp = _grant("email.send_one", {"to": "A"}, scope="CONFIRM", ttl=10, now=t0)
    v = verdict({"tool_id": "email.send_one", "params": {"to": "A"}, "token": tok_exp},
                signing_key=key, now=t0 + 999)  # well past expiry
    assert v["decision"] == "BLOCK" and v["reason"].count("expired") == 1, v
    # replay: a non-idempotent single-use token spent twice
    reset_spent_tokens()
    tok_once = _grant("email.send_one", {"to": "A"}, scope="CONFIRM", now=t0, token_id="tok-once")
    v1 = verdict({"tool_id": "email.send_one", "params": {"to": "A"}, "token": tok_once},
                 signing_key=key, now=t0)
    assert v1["decision"] == "ALLOW", v1
    v2 = verdict({"tool_id": "email.send_one", "params": {"to": "A"}, "token": tok_once},
                 signing_key=key, now=t0)
    assert v2["decision"] == "BLOCK" and "replay" in v2["reason"], v2

    # (e) BLOCK + ALARM the self-downgrade (sets autoApprove=true / edits the registry /
    #     lowers its own tier) — the CVE-2025-53773 attack. Even WITH a "valid" token.
    sneaky = _grant("registry.edit", {"set": "fs.overwrite->AUTO"}, scope="STEP-UP", now=t0)
    v = verdict({"tool_id": "registry.edit", "params": {"set": "fs.overwrite->AUTO"},
                 "token": sneaky}, signing_key=key, now=t0)
    assert v["decision"] == "BLOCK" and v["alarm"] is True and "SELF-PROTECTION" in v["reason"], v
    # the autoApprove flip on an otherwise-benign tool is ALSO blocked + alarmed
    v = verdict({"tool_id": "fs.scratch_write", "params": {"chat.tools.autoApprove": True}},
                signing_key=key, now=t0)
    assert v["decision"] == "BLOCK" and v["alarm"] is True, v

    # (f) ABSTAIN (not silent-pass) on an action whose tier can't be determined from schema.
    #     (Modeled as an unregistered tool -> ABSTAIN; see also (g).)
    v = verdict({"tool_id": "some.tool.with.no.schema.entry", "params": {}},
                signing_key=key, now=t0)
    assert v["tier"] == "ABSTAIN" and v["decision"] == "BLOCK", v

    # (g) BLOCK an UNKNOWN/unregistered tool_id (default-deny — the audit BROKEN finding).
    v = verdict({"tool_id": "evil.unregistered", "params": {"x": 1}}, signing_key=key, now=t0)
    assert v["tier"] == "ABSTAIN" and v["decision"] == "BLOCK" and "default-deny" in v["reason"], v

    # (h) BLOCK on any injected exception in the gate's own path (fail-closed).
    #     Force an exception by passing a non-dict action.
    v = verdict(12345, signing_key=key, now=t0)
    assert v["decision"] == "BLOCK" and v["alarm"] is True and "FAIL-CLOSED" in v["reason"], v
    #     ...and a params object that explodes on iteration also fail-closes to BLOCK.
    class Boom:
        def __iter__(self): raise RuntimeError("kaboom")
        def get(self, *a, **k): raise RuntimeError("kaboom")
    v = verdict(Boom(), signing_key=key, now=t0)
    assert v["decision"] == "BLOCK" and "FAIL-CLOSED" in v["reason"], v

    # (i) REJECT a tier-scope mismatch: a CONFIRM-scoped token presented for a STEP-UP action.
    #     (artifact hash supplied + matching so the dry-run gate passes and we reach scope.)
    reset_spent_tokens()
    confirm_tok = _grant("deploy.production", {"env": "prod"}, scope="CONFIRM",
                         now=t0, token_id="tok-conf")
    v = verdict({"tool_id": "deploy.production", "params": {"env": "prod"},
                 "dry_run_hash": "h1", "dry_run_artifact_hash": "h1",
                 "token": confirm_tok}, signing_key=key, now=t0)
    assert v["decision"] == "BLOCK" and "scope-too-low" in v["reason"] and v["alarm"] is True, v

    # (j) BLOCK a commit with NO dry-run reference (absent hash, not just mismatched).
    v = verdict({"tool_id": "fs.overwrite", "params": {"path": "/p/f", "data": "x"}},
                signing_key=key, now=t0)  # no dry_run_hash, no token
    assert v["decision"] == "BLOCK" and "NO dry-run reference" in v["reason"], v

    # (k) the SUITE fails if the gate cannot confirm registry/ledger are read-only to the
    #     agent process — OR the self-protection rail is downgraded to ARMOR-class, labeled.
    #     (Enforced by selftest_all.py via infra_check.py; here we assert the labeling
    #     contract exists.)
    import infra_check
    status = infra_check.write_scope_status()
    assert status["self_protection_class"] in ("kappa=1", "ARMOR-class"), status
    # honesty: if NOT infra-enforced, the class MUST be ARMOR-class (never silently kappa=1).
    if not status["registry_read_only_to_agent"]:
        assert status["self_protection_class"] == "ARMOR-class", status

    # (l) a token forged using ONLY resources available to the agent (an in-context /
    #     in-repo key) must FAIL the gate. If it passes, the signing architecture is broken.
    AGENT_VISIBLE_KEY = b"a-key-the-agent-can-read-from-context-or-repo"
    assert AGENT_VISIBLE_KEY != _EXTERNAL_KEY
    forged_payload = {
        "action_hash": canonical_action_hash("money.transfer", {"amt": 1_000_000}),
        "scope": "STEP-UP", "issued_ts": t0, "expiry": t0 + 300,
        "token_id": "forged", "granter": "agent:self",
    }
    forged_payload["sig"] = sign_token(forged_payload, AGENT_VISIBLE_KEY)  # forged with agent key
    v = verdict({"tool_id": "money.transfer", "params": {"amt": 1_000_000},
                 "token": forged_payload}, signing_key=_EXTERNAL_KEY, now=t0)
    assert v["decision"] == "BLOCK" and "signature-invalid" in v["reason"], v
    #     extra: even if the gate is (mis)called with NO key, it must fail closed, not allow.
    v = verdict({"tool_id": "money.transfer", "params": {"amt": 1},
                 "token": forged_payload}, signing_key=None, now=t0)
    assert v["decision"] == "BLOCK", v

    # financial actions: money.transfer is STEP-UP and NEVER auto-approved (system rail).
    v = verdict({"tool_id": "money.transfer", "params": {"amt": 5}}, signing_key=key, now=t0)
    assert v["tier"] == "STEP-UP" and v["decision"] == "BLOCK", v

    # blast accumulator records (composition visibility until G3).
    acc = BlastAccumulator(budget=10)
    acc.add(3); r = acc.add(20)
    assert r["running_total"] == 23 and r["over_budget_FLAG"] is True, r

    # =====================================================================
    # REGRESSION TESTS for the cross-model audit defects (m..p).
    # =====================================================================

    # (m) AUDIT DEFECT-1 (FALSE-ACCEPT): a needs_dry_run commit with a FAKE dry_run_hash
    #     and NO dry_run_artifact_hash previously ALLOWED. It must now BLOCK.
    reset_spent_tokens()
    # build a token bound to the exact params so we *isolate* the dry-run hole (otherwise
    # a no-token BLOCK would mask it).
    p_m = {"path": "/p/f", "data": "x"}
    tok_m = _grant("fs.overwrite", p_m, scope="CONFIRM", now=t0, token_id="tok-m")
    v = verdict({"tool_id": "fs.overwrite", "params": p_m,
                 "dry_run_hash": "FAKE_HASH_NEVER_RAN", "token": tok_m},
                signing_key=key, now=t0)
    assert v["decision"] == "BLOCK" and "produced-artifact" in v["reason"], ("DEFECT-1", v)
    #     ...and the same fake reference on a no-token call ALSO blocks (defense in depth).
    v = verdict({"tool_id": "fs.overwrite", "params": p_m,
                 "dry_run_hash": "FAKE_HASH_NEVER_RAN"}, signing_key=key, now=t0)
    assert v["decision"] == "BLOCK" and "produced-artifact" in v["reason"], ("DEFECT-1 no-token", v)
    #     ...declaring matching reference+artifact reaches the token check (no false-block).
    reset_spent_tokens()
    v = verdict({"tool_id": "fs.overwrite", "params": p_m, "token": tok_m,
                 "dry_run_hash": "h-real", "dry_run_artifact_hash": "h-real"},
                signing_key=key, now=t0)
    assert v["decision"] == "ALLOW", ("DEFECT-1 positive control", v)

    # (n) AUDIT DEFECT-1 (kappa=1 PATH): when the EXTERNAL authority SIGNS the artifact hash
    #     into the token, a commit declaring a DIFFERENT artifact is BLOCKED — the agent
    #     cannot forge the signed attestation. This is the genuinely-kappa=1 dry-run bind.
    reset_spent_tokens()
    p_n = {"path": "/p/g", "data": "y"}
    tok_n = _grant("fs.overwrite", p_n, scope="CONFIRM", now=t0, token_id="tok-n",
                   dry_run_artifact_hash="ATTESTED-ARTIFACT")
    # mismatched artifact vs the signed attestation -> BLOCK
    v = verdict({"tool_id": "fs.overwrite", "params": p_n, "token": tok_n,
                 "dry_run_hash": "DIFFERENT", "dry_run_artifact_hash": "DIFFERENT"},
                signing_key=key, now=t0)
    assert v["decision"] == "BLOCK" and "dry-run-artifact-mismatch" in v["reason"], ("DEFECT-1 attest", v)
    #     matching the signed attestation -> ALLOW (positive control)
    reset_spent_tokens()
    v = verdict({"tool_id": "fs.overwrite", "params": p_n, "token": tok_n,
                 "dry_run_hash": "ATTESTED-ARTIFACT",
                 "dry_run_artifact_hash": "ATTESTED-ARTIFACT"}, signing_key=key, now=t0)
    assert v["decision"] == "ALLOW", ("DEFECT-1 attest positive", v)

    # (o) AUDIT DEFECT-2/3 (NESTED + value-substring self-downgrade) reach the gate, not
    #     just the registry helper: a nested autoApprove payload is BLOCK+ALARM at verdict().
    for nested in ({"settings": {"autoApprove": True}},
                   {"data": [{"auto_approve": True}]},
                   {"note": "set_disable_gate_flag"}):
        v = verdict({"tool_id": "fs.scratch_write", "params": nested}, signing_key=key, now=t0)
        assert v["decision"] == "BLOCK" and v["alarm"] is True \
            and "SELF-PROTECTION" in v["reason"], ("DEFECT-2/3 at gate", nested, v)

    # (p) AUDIT DEFECT-4 (replay footgun): verify_token() called twice DIRECTLY (bypassing
    #     verdict()) must REJECT the second call as replay — replay protection is now
    #     self-contained, no longer dependent on the caller committing the spend.
    reset_spent_tokens()
    p_p = {"to": "X"}
    tok_p = _grant("email.send_one", p_p, scope="CONFIRM", now=t0, token_id="tok-p")
    ok1, why1 = verify_token(tok_p, "email.send_one", p_p, "CONFIRM", key, now=t0)
    assert ok1 is True and why1.startswith("ok:single-use:"), ("DEFECT-4 first", ok1, why1)
    ok2, why2 = verify_token(tok_p, "email.send_one", p_p, "CONFIRM", key, now=t0)
    assert ok2 is False and "replay" in why2, ("DEFECT-4 second must be replay", ok2, why2)
    #     ...a pure pre-check (commit_spend=False) does NOT consume but is flagged uncommitted.
    reset_spent_tokens()
    tok_pc = _grant("email.send_one", p_p, scope="CONFIRM", now=t0, token_id="tok-pc")
    okc, whyc = verify_token(tok_pc, "email.send_one", p_p, "CONFIRM", key, now=t0,
                             commit_spend=False)
    assert okc is True and "UNCOMMITTED" in whyc, ("DEFECT-4 precheck", okc, whyc)
    # the uncommitted pre-check did NOT spend the token: verdict() can still ALLOW once.
    v = verdict({"tool_id": "email.send_one", "params": p_p, "token": tok_pc},
                signing_key=key, now=t0)
    assert v["decision"] == "ALLOW", ("DEFECT-4 precheck-no-consume", v)

    print("gloves_gate selftest: PASS (a AUTO-allow; b STEP-UP-no-token BLOCK; "
          "c param-drift REJECT; d expiry+replay REJECT; e self-downgrade BLOCK+ALARM; "
          "f tier-unknown ABSTAIN; g unknown-tool default-deny; h fail-closed-on-exception; "
          "i scope-mismatch REJECT; j no-dry-run BLOCK; k infra write-scope labeled; "
          "l agent-forged-token FAILS the gate; "
          "m DEFECT-1 fake-dry-run-hash BLOCKED; n DEFECT-1 token-attested-artifact kappa=1; "
          "o DEFECT-2/3 nested/value-substring self-downgrade BLOCKED at gate; "
          "p DEFECT-4 verify_token replay self-contained)")


if __name__ == "__main__":
    _selftest()
