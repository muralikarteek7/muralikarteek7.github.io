#!/usr/bin/env python3
"""REDCELL router — authorization-classify FIRST, then (if allowed) run the mode.

Order is non-negotiable: the authorization gate runs BEFORE any security logic and
refuses by default. Only an ALLOWed task reaches a mode; every mode runs in a sandbox
against owned/authorized targets and is verified by a kappa=1 checker. Refuse otherwise.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth_gate import authorize

MODES = {
    "ctf_solve":      ("CTF-SOLVE",      "flag_verify.verify_flag -- flag validates (kappa=1)"),
    "patch_validate": ("PATCH-VALIDATE", "patch_verify.validate_patch -- differential PoC in sandbox (kappa=1)"),
    "vuln_repro":     ("VULN-REPRO",     "sandboxed repro -> detection signature (kappa=1 trigger; artifact is a detection)"),
}


def route(task):
    """Returns the routing decision. REFUSE-by-default: the gate decides first."""
    gate = authorize(task)
    if not gate["allowed"]:
        return {"weapon": "REDCELL", "decision": "REFUSE", "authorized": False,
                "reason": gate["reason"], "ran_any_security_logic": False,
                "note": "The authorization gate fails closed: no mode runs unless an explicit, "
                        "recognized context is present and nothing out-of-scope is requested."}
    mode_key = gate["mode"]
    mode_name, verifier = MODES[mode_key]
    return {"weapon": "REDCELL", "decision": "PROCEED", "authorized": True,
            "authorization_context": gate["authorization_context"],
            "mode": mode_name, "verifier": verifier,
            "sandbox": "isolated subprocess + resource limits; owned/authorized target only",
            "note": "Produces a verification artifact (flag/patch-pass/detection), NEVER a deployable "
                    "weapon. kappa=1 is on the artifact's outcome, not a general 'secure' claim."}


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        # smoke: authorized CTF proceeds; everything dubious refuses
        ok_task = {"authorization_context": "ctf", "mode": "ctf_solve", "target_is_owned_or_sandbox": True}
        assert route(ok_task)["decision"] == "PROCEED"
        assert route({"mode": "ctf_solve"})["decision"] == "REFUSE"          # no context
        assert route({"authorization_context": "ctf", "mode": "ctf_solve",
                      "requested_category": "supply_chain"})["decision"] == "REFUSE"  # out of scope
        assert route("hack acme.com")["decision"] == "REFUSE"               # malformed
        print("redcell_router smoke: PASS (authorized CTF -> PROCEED; no-context / out-of-scope / "
              "malformed -> REFUSE; gate runs before any security logic)")
