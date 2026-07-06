#!/usr/bin/env python3
"""GLOVES frozen tool-risk registry.

The action's risk TIER is read from THIS table, never from the model at runtime
(CVE-2025-53773: the agent must not be able to declare an action less risky than
its registered class). Each entry is keyed by an exact `tool_id` and declares:

  tier            : one of AUTO | CONFIRM | STEP-UP   (the *floor*; never lowered)
  reversibility   : R0 (reversible) .. R3 (irreversible-broad)
  blast_radius    : local | project | external
  idempotent      : True if re-running with the same params is a no-op (safe replay)
  needs_dry_run   : True if an R1+ commit must reference a dry-run artifact hash
  blast_units     : an integer "blast-radius weight" added to the per-run accumulator

KAPPA HONESTY (kickoff §1 / Finding 2):
  - The *lookup* below is kappa=1 (exact, mechanical).
  - It is only as honest as the entry. A tool that UNDER-declares its risk, or is
    ABSENT, is the real attack surface. Therefore:
        an UNKNOWN / unregistered tool_id -> the gate ABSTAINS (default-deny).
  - The registry is FROZEN here. The self-protection rail (gate.py) hard-blocks any
    attempt to mutate it at runtime regardless of token.

This file is data + pure lookups. No model, no I/O, no side effects.
"""

# Tiers, ordered. A token's scope must COVER the action's tier (scope index >= tier index).
TIERS = ("AUTO", "CONFIRM", "STEP-UP")
_TIER_RANK = {t: i for i, t in enumerate(TIERS)}

# Frozen registry: a few example tools spanning all tiers + the ABSTAIN boundary.
# (kickoff §3.2: "a small frozen tool-risk registry ... across all four tiers")
REGISTRY = {
    # ---- AUTO: R0 reversible, blast-local: read / dry-run / scratch / query ----
    "fs.read": {
        "tier": "AUTO", "reversibility": "R0", "blast_radius": "local",
        "idempotent": True, "needs_dry_run": False, "blast_units": 0,
        "desc": "read a file (no side effect)",
    },
    "fs.dry_run_diff": {
        "tier": "AUTO", "reversibility": "R0", "blast_radius": "local",
        "idempotent": True, "needs_dry_run": False, "blast_units": 0,
        "desc": "compute a preview diff without writing (produces the dry-run artifact)",
    },
    "fs.scratch_write": {
        "tier": "AUTO", "reversibility": "R0", "blast_radius": "local",
        "idempotent": False, "needs_dry_run": False, "blast_units": 0,
        "desc": "write to a local scratch/tmp path (cheap to discard)",
    },
    "db.query": {
        "tier": "AUTO", "reversibility": "R0", "blast_radius": "local",
        "idempotent": True, "needs_dry_run": False, "blast_units": 0,
        "desc": "read-only SELECT query",
    },

    # ---- CONFIRM: R1-R2 or blast-project/external: needs a param-bound token ----
    "fs.overwrite": {
        "tier": "CONFIRM", "reversibility": "R2", "blast_radius": "project",
        "idempotent": False, "needs_dry_run": True, "blast_units": 2,
        "desc": "overwrite an existing file (R1+ -> dry-run->commit required)",
    },
    "email.send_one": {
        "tier": "CONFIRM", "reversibility": "R2", "blast_radius": "external",
        "idempotent": False, "needs_dry_run": False, "blast_units": 3,
        "desc": "send ONE email to ONE recipient",
    },
    "record.create_one": {
        "tier": "CONFIRM", "reversibility": "R1", "blast_radius": "external",
        "idempotent": False, "needs_dry_run": False, "blast_units": 2,
        "desc": "create ONE record in an external system",
    },

    # ---- STEP-UP: R3 irreversible-broad / financial / admin: human, no self-approve ----
    "email.mass_send": {
        "tier": "STEP-UP", "reversibility": "R3", "blast_radius": "external",
        "idempotent": False, "needs_dry_run": True, "blast_units": 20,
        "desc": "mass-send to many recipients (irreversible, broad)",
    },
    "deploy.production": {
        "tier": "STEP-UP", "reversibility": "R3", "blast_radius": "external",
        "idempotent": False, "needs_dry_run": True, "blast_units": 20,
        "desc": "deploy to production",
    },
    "db.drop_table": {
        "tier": "STEP-UP", "reversibility": "R3", "blast_radius": "project",
        "idempotent": False, "needs_dry_run": True, "blast_units": 15,
        "desc": "delete/drop a table (irreversible)",
    },
    "money.transfer": {
        "tier": "STEP-UP", "reversibility": "R3", "blast_radius": "external",
        "idempotent": False, "needs_dry_run": False, "blast_units": 50,
        "desc": "move money / place a trade (financial; ALWAYS routes to a human)",
    },
    "iam.change_perms": {
        "tier": "STEP-UP", "reversibility": "R3", "blast_radius": "project",
        "idempotent": False, "needs_dry_run": True, "blast_units": 15,
        "desc": "change permissions / admin",
    },
}

# Action-id PREFIXES that target GLOVES' own controls -> hard-blocked, no token overrides
# (CVE-2025-53773 self-protection rail; gate.py enforces, this names the surface).
SELF_PROTECT_PREFIXES = (
    "gloves.",          # any GLOVES-internal control
    "config.gloves",    # editing GLOVES config
    "registry.",        # editing the risk registry
    "ledger.",          # editing the actuation ledger
    "policy.gloves",    # editing GLOVES policy/approval state
)

# Tokens/params that signal a self-downgrade attempt regardless of tool_id
# (e.g. an action that flips an auto-approve flag or lowers a tier).
SELF_DOWNGRADE_PARAM_KEYS = (
    "autoApprove", "auto_approve", "chat.tools.autoApprove",
    "disable_gate", "lower_tier", "set_tier", "override_tier", "yolo",
)


def tier_rank(tier):
    """Exact integer rank of a tier (higher = riskier). KeyError on unknown tier."""
    return _TIER_RANK[tier]


def lookup(tool_id):
    """Return the frozen entry for tool_id, or None if UNREGISTERED (-> caller ABSTAINS).

    Pure, exact (kappa=1 within the registry). No model. Raising/returning-None on
    an unknown id is the default-deny boundary (kickoff Finding 1)."""
    return REGISTRY.get(tool_id)


def _params_have_downgrade_signal(obj, _depth=0):
    """RECURSIVELY scan a params structure (dict/list/tuple, any nesting) for a
    self-downgrade signal in a KEY or a VALUE (audit DEFECT-2/DEFECT-3 fix).

    - KEY match: substring (catches 'my_disable_gate_flag', 'chat.tools.autoApprove').
    - VALUE match: substring TOO (symmetry fix — a value of 'set_autoApprove_flag'
      or 'autoApprove_is_true' now triggers, not only the exact 'autoApprove').
    Recurses into nested dicts AND list/tuple elements so a payload like
    {'settings': {'autoApprove': True}} or {'data': [{'autoApprove': True}]}
    no longer slips through as a top-level-only scan did. Depth-bounded to avoid
    pathological recursion; at the bound we FAIL CLOSED (treat as a signal) rather
    than silently passing a too-deep structure."""
    if _depth > 64:
        # Conservative: an absurdly-deep structure is suspicious -> treat as a hit
        # (false-positive blocks = safe; a silent pass on too-deep = unsafe).
        return True
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            for bad in SELF_DOWNGRADE_PARAM_KEYS:
                if bad.lower() in kl:
                    return True
            if _params_have_downgrade_signal(v, _depth + 1):
                return True
        return False
    if isinstance(obj, (list, tuple)):
        for v in obj:
            if _params_have_downgrade_signal(v, _depth + 1):
                return True
        return False
    # scalar value (str/int/bool/...): substring match on its string form.
    vl = str(obj).lower()
    for bad in SELF_DOWNGRADE_PARAM_KEYS:
        if bad.lower() in vl:
            return True
    return False


def is_self_protect_target(tool_id, params):
    """True if the action targets GLOVES' own controls (self-protection rail).

    Matches by tool_id prefix OR by a self-downgrade param key/value, scanned
    RECURSIVELY through nested dicts and lists (audit DEFECT-2: nested-params
    bypass; audit DEFECT-3: value-match was exact-only, now substring). Conservative
    by design: a false-positive blocks an action (safe); a false-negative would let a
    self-edit through (unsafe), so we err toward blocking."""
    tid = (tool_id or "").lower()
    for pfx in SELF_PROTECT_PREFIXES:
        if tid.startswith(pfx):
            return True
    if isinstance(params, (dict, list, tuple)):
        return _params_have_downgrade_signal(params)
    return False


def _selftest():
    # AUTO read is registered AUTO
    assert lookup("fs.read")["tier"] == "AUTO"
    # CONFIRM overwrite needs a dry-run
    assert lookup("fs.overwrite")["tier"] == "CONFIRM"
    assert lookup("fs.overwrite")["needs_dry_run"] is True
    # STEP-UP money transfer is STEP-UP and financial-broad
    assert lookup("money.transfer")["tier"] == "STEP-UP"
    # UNKNOWN tool -> None (caller must ABSTAIN)
    assert lookup("totally.unknown.tool") is None
    # tier ranks strictly increase
    assert tier_rank("AUTO") < tier_rank("CONFIRM") < tier_rank("STEP-UP")
    # self-protection: prefix match
    assert is_self_protect_target("gloves.set_config", {}) is True
    assert is_self_protect_target("registry.edit", {}) is True
    # self-protection: param-key match (the CVE-2025-53773 autoApprove flip)
    assert is_self_protect_target("fs.scratch_write",
                                  {"chat.tools.autoApprove": True}) is True
    assert is_self_protect_target("config.update", {"auto_approve": True}) is True
    # a benign action is NOT flagged
    assert is_self_protect_target("fs.read", {"path": "/tmp/x"}) is False

    # --- REGRESSION (audit DEFECT-2): NESTED self-downgrade payloads must be caught.
    # Before the fix these were top-level-only scanned -> passed through as AUTO.
    for nested in (
        {"settings": {"autoApprove": True}},
        {"config": {"auto_approve": True}},
        {"update": {"chat.tools.autoApprove": True}},
        {"data": [{"autoApprove": True}]},
        {"x": {"y": {"disable_gate": True}}},
    ):
        assert is_self_protect_target("fs.scratch_write", nested) is True, ("DEFECT-2 nested", nested)

    # --- REGRESSION (audit DEFECT-3): a VALUE carrying a downgrade flag as a SUBSTRING
    # must be caught (was exact-match only -> 'set_autoApprove_flag' slipped through).
    assert is_self_protect_target("fs.read", {"config": "set_autoApprove_flag"}) is True, "DEFECT-3 value-substring"
    assert is_self_protect_target("fs.read", {"note": "autoApprove_is_true"}) is True, "DEFECT-3 value-substring"
    # exact-value still caught (no regression of the original behavior)
    assert is_self_protect_target("fs.read", {"config": "autoApprove"}) is True
    # a truly-benign nested structure is still NOT flagged (no over-block regression)
    assert is_self_protect_target("fs.scratch_write",
                                  {"settings": {"theme": "dark", "items": ["a", "b"]}}) is False

    print("tool_risk_registry selftest: PASS (AUTO/CONFIRM/STEP-UP entries; unknown->None; "
          "tier ranks ordered; self-protect by prefix AND by autoApprove param; "
          "DEFECT-2 nested-payload caught; DEFECT-3 value-substring caught)")


if __name__ == "__main__":
    _selftest()
