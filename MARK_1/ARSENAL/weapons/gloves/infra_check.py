#!/usr/bin/env python3
"""GLOVES infra reality check (kickoff §4 + self-test k, Finding 3).

The self-protection rail ("the agent cannot edit its own registry/ledger/config")
is kappa=1 ONLY IF those stores are read-only to the agent PROCESS. A pure-software
box cannot self-guarantee that — true tamper-resistance needs an enforcement layer
the agent cannot reach (filesystem perms owned by another uid / a separate process /
the harness).

So this module HONESTLY reports whether write-scope is infra-enforced and LABELS the
rail accordingly. The selftest SUITE (selftest_all.py) consumes this and refuses to
claim kappa=1 for the self-protection rail unless the infra actually backs it. If the
infra does NOT back it, the rail is labeled ARMOR-class (gate-level best-effort), never
silently upgraded. An audit log the agent can rewrite is not an audit log.
"""
import os

# The files whose write-scope is security-load-bearing.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REGISTRY = os.path.join(_THIS_DIR, "tool_risk_registry.py")
_GATE = os.path.join(_THIS_DIR, "gloves_gate.py")


def _agent_can_write(path):
    """True if THIS process (the agent) can write `path`.

    In a pure-software box run by the user's own uid, the agent CAN write its own
    source/registry -> write-scope is NOT infra-enforced -> rail is ARMOR-class.
    True kappa=1 requires the file be owned by a different uid / mounted read-only /
    fronted by a separate-process gate the agent cannot reach."""
    if not os.path.exists(path):
        # absent -> treat as writable (creatable) by the agent: NOT enforced.
        return True
    return os.access(path, os.W_OK)


def write_scope_status():
    """Honest status of the tamper-resistance assumption.

    Returns a dict with:
      registry_read_only_to_agent : bool  (True only if the agent CANNOT write it)
      ledger_read_only_to_agent   : bool
      self_protection_class       : "kappa=1" iff infra-enforced, else "ARMOR-class"
      detail                      : human-readable honest statement
    """
    reg_ro = not _agent_can_write(_REGISTRY)
    gate_ro = not _agent_can_write(_GATE)
    # The ledger store is, in THIS box, an agent-writable file -> not enforced.
    ledger_ro = False  # honest default for a pure-software single-uid box

    enforced = reg_ro and gate_ro and ledger_ro
    cls = "kappa=1" if enforced else "ARMOR-class"
    if enforced:
        detail = ("Registry, gate code, and ledger are read-only to the agent process "
                  "(infra-enforced) -> the self-protection rail is kappa=1.")
    else:
        detail = ("INFRA LIMIT (honest): the agent process CAN write its own "
                  "registry/gate/ledger in this pure-software box (single uid). The "
                  "self-protection rail is therefore ARMOR-class (gate-level best-effort: "
                  "the gate blocks self-edit ACTIONS routed through it, but a process that "
                  "writes the files directly bypasses the gate). True kappa=1 needs the "
                  "stores owned by a different uid / a separate-process gate / the harness. "
                  "An audit log the agent can rewrite is not an audit log (CVE-2025-53773).")
    return {
        "registry_read_only_to_agent": reg_ro,
        "gate_read_only_to_agent": gate_ro,
        "ledger_read_only_to_agent": ledger_ro,
        "infra_enforced": enforced,
        "self_protection_class": cls,
        "detail": detail,
    }


def _selftest():
    s = write_scope_status()
    # The class label MUST be one of the two honest values.
    assert s["self_protection_class"] in ("kappa=1", "ARMOR-class"), s
    # Honesty invariant: if NOT infra-enforced, the class MUST be ARMOR-class.
    if not s["infra_enforced"]:
        assert s["self_protection_class"] == "ARMOR-class", s
    # Conversely, kappa=1 is claimable ONLY when all three stores are read-only.
    if s["self_protection_class"] == "kappa=1":
        assert s["registry_read_only_to_agent"] and s["gate_read_only_to_agent"] \
            and s["ledger_read_only_to_agent"], s
    print(f"infra_check selftest: PASS (self-protection rail honestly labeled "
          f"'{s['self_protection_class']}'; infra_enforced={s['infra_enforced']})")


if __name__ == "__main__":
    import json
    print(json.dumps(write_scope_status(), indent=2))
    _selftest()
