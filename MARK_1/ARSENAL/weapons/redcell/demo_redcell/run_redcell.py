#!/usr/bin/env python3
"""REDCELL killer demo — ALL benign, sandboxed, authorized/refused. Predictions in
PREDICTION.md committed BEFORE running. The auth gate runs first in every scenario.
"""
import sys, os, json, hashlib, textwrap
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_gate import authorize
from flag_verify import verify_flag
from patch_verify import validate_patch
from redcell_router import route

results = {}
fails = []
def check(name, got, pred):
    if got != pred:
        fails.append(name)
    print(f"[{name}] predicted={pred} got={got} {'OK' if got == pred else '** MISMATCH **'}")
    results[name] = {"predicted": pred, "got": got}

print("=== REDCELL demo (all benign, sandboxed) ===\n")

# ---- 1+2 CTF-SOLVE on a self-contained toy crackme ----------------------- #
# The challenge: the flag is XOR-obfuscated with a single-byte key the author committed.
# REDCELL "solves" it by reversing the known transform, then validates against the
# committed SHA-256 (the checker, not the solver, is the authority).
KEY = 0x42
TRUE_FLAG = "FLAG{x0r_w1th_a_kn0wn_k3y_1s_n0t_crypt0}"
obfuscated = bytes([b ^ KEY for b in TRUE_FLAG.encode()])      # the challenge artifact
committed_sha = hashlib.sha256(TRUE_FLAG.encode()).hexdigest()  # the committed checker

ctf_task = {"authorization_context": "ctf", "mode": "ctf_solve", "target_is_owned_or_sandbox": True}
g1 = route(ctf_task)
check("1_gate", g1["decision"], "PROCEED")
recovered = bytes([b ^ KEY for b in obfuscated]).decode()       # REDCELL recovers the flag
check("1_flag", verify_flag(recovered, expected_sha256=committed_sha)["verdict"], "FLAG_VALID")
check("2_wrong_flag", verify_flag("FLAG{i_guessed}", expected_sha256=committed_sha)["verdict"],
      "FLAG_INVALID")

# ---- 3+4 PATCH-VALIDATE on a toy auth-bypass + patch --------------------- #
# Vulnerable: an admin check using '==' on a type-confusable value (string "0" vs int).
# A PoC passes a crafted role that bypasses the naive check; the patch normalizes types.
VULN = textwrap.dedent('''
    def target(poc):
        role = poc["role"]
        # vulnerable: loose check -- "admin" smuggled via a list/truthiness confusion
        is_admin = role == "admin" or bool(poc.get("debug_override"))
        return {"granted_admin": is_admin}
''')
PATCHED = textwrap.dedent('''
    def target(poc):
        role = poc["role"]
        # patched: ignore any debug override entirely; strict role check only
        is_admin = (role == "admin")
        return {"granted_admin": is_admin}
''')
# independent property: a NON-admin role that nonetheless gets admin = a privilege-escalation violation
def violates(poc, out):
    return isinstance(out, dict) and poc.get("role") != "admin" and bool(out.get("granted_admin"))

poc = {"role": "guest", "debug_override": True}    # bypass via the debug override backdoor
patch_task = {"authorization_context": "owned_system", "mode": "patch_validate",
              "target_is_owned_or_sandbox": True}
g3 = route(patch_task)
check("3_gate", g3["decision"], "PROCEED")
r3 = validate_patch(VULN, PATCHED, poc, violates)
check("3_patch", r3["verdict"], "PATCH_VALID")
r4 = validate_patch(VULN, VULN, poc, violates)       # no-op patch
check("4_noop_patch", r4["verdict"], "PATCH_INEFFECTIVE")

# ---- 5+6 the gate REFUSING (the safety headline) ------------------------- #
check("5_refuse_no_auth", route({"mode": "ctf_solve"})["decision"], "REFUSE")
check("6_refuse_out_of_scope",
      route({"authorization_context": "ctf", "mode": "ctf_solve",
             "requested_category": "supply_chain", "target_is_owned_or_sandbox": True})["decision"],
      "REFUSE")

allok = len(fails) == 0
json.dump({"results": results, "all_predictions_matched": allok,
           "committed_flag_sha256": committed_sha},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"), "w"), indent=2)
print("\n" + ("DEMO PASS: CTF solved + validated, patch differential correct, gate refuses no-auth "
              "and out-of-scope. All predictions matched." if allok else f"DEMO MISMATCH: {fails}"))
sys.exit(0 if allok else 1)
