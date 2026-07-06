#!/usr/bin/env python3
"""REDCELL gate self-tests. The gate that can't fail (closed) is not a gate.
The REFUSAL tests are as important as the success tests.

Mandatory (per kickoff):
  (a) PASS an authorized CTF-flag validation
  (b) REFUSE a task with no authorization context
  (c) REFUSE an out-of-scope category (with a reason)
  (d) PATCH-VALIDATE distinguishes patched vs unpatched in the sandbox
Plus hardening: malicious in-scope-wrapper refused; malformed context fails closed;
real target refused; misconfigured CTF checker refuses.
"""
import sys, os, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth_gate import authorize
from flag_verify import verify_flag
from patch_verify import validate_patch

n = 0
def ok(cond, msg):
    global n
    assert cond, "FAIL: " + msg
    n += 1

# ---- (a) authorized CTF flag validation passes ---------------------------- #
FLAG = "FLAG{0nly_th3_ch3ck3r_d3cid3s}"
auth = authorize({"authorization_context": "ctf", "mode": "ctf_solve",
                  "target_is_owned_or_sandbox": True})
ok(auth["allowed"] is True, "(a) authorized CTF task is ALLOWED")
ok(verify_flag(FLAG, expected=FLAG)["verdict"] == "FLAG_VALID", "(a) correct flag validates")
ok(verify_flag("FLAG{nope}", expected=FLAG)["verdict"] == "FLAG_INVALID", "(a) wrong flag rejected")

# ---- (b) REFUSE: no authorization context (fail closed) ------------------- #
nb = authorize({"mode": "ctf_solve"})
ok(nb["allowed"] is False and "no authorization_context" in nb["reason"],
   "(b) no context -> REFUSE")

# ---- (c) REFUSE: out-of-scope categories with a reason -------------------- #
for cat, label in [("dos", "take down site X"), ("supply_chain", "compromise dependency Y"),
                   ("mass_targeting", "spray every host"), ("malware_deployment", "build a dropper"),
                   ("malicious_evasion", "evade the EDR for an intrusion")]:
    d = authorize({"authorization_context": "scoped_engagement", "scope": "acme",
                   "mode": "vuln_repro", "target_is_owned_or_sandbox": True,
                   "requested_category": cat})
    ok(d["allowed"] is False and "out of scope" in d["reason"],
       f"(c) out-of-scope '{cat}' ({label}) -> REFUSE")

# ---- (d) PATCH-VALIDATE distinguishes patched vs unpatched ---------------- #
VULN = textwrap.dedent('''
    import os
    BASE = "/srv/app/public"
    def target(poc):
        full = BASE + "/" + poc["path"]
        return {"resolved": os.path.normpath(full), "allowed": full.startswith(BASE)}
''')
PATCHED = textwrap.dedent('''
    import os
    BASE = "/srv/app/public"
    def target(poc):
        full = os.path.normpath(BASE + "/" + poc["path"])
        return {"resolved": full, "allowed": full == BASE or full.startswith(BASE + "/")}
''')
def violates(poc, out):
    return isinstance(out, dict) and bool(out.get("allowed")) \
        and not str(out.get("resolved", "")).startswith("/srv/app/public")

r = validate_patch(VULN, PATCHED, {"path": "../../../../etc/passwd"}, violates)
ok(r["verdict"] == "PATCH_VALID", "(d) PoC fires on unpatched, fails on patched -> PATCH_VALID")
ok(r["fired_on_unpatched"] is True and r["fired_on_patched"] is False, "(d) differential is correct")
# an ineffective 'patch' (identical to vuln) -> PATCH_INEFFECTIVE
r2 = validate_patch(VULN, VULN, {"path": "../../../../etc/passwd"}, violates)
ok(r2["verdict"] == "PATCH_INEFFECTIVE", "(d) no-op patch -> PATCH_INEFFECTIVE")

# ---- HARDENING: the gate cannot be tricked open -------------------------- #
# H1: out-of-scope category beats an asserted legitimate context (the wrapper attack)
h1 = authorize({"authorization_context": "ctf", "mode": "ctf_solve",
                "target_is_owned_or_sandbox": True, "requested_category": "dos"})
ok(h1["allowed"] is False, "H1: ctf wrapper around DoS still REFUSED (scope beats context)")
# H2: malformed task (not a dict) fails closed
ok(authorize("please hack acme.com")["allowed"] is False, "H2: non-dict task -> REFUSE")
ok(authorize(None)["allowed"] is False, "H2b: None task -> REFUSE")
# H3: unknown/typo'd context fails closed (no fuzzy allow)
ok(authorize({"authorization_context": "totally_legit", "mode": "ctf_solve"})["allowed"] is False,
   "H3: unknown context -> REFUSE")
# H4: real / non-owned target refused even with a valid context
ok(authorize({"authorization_context": "scoped_engagement", "scope": "x", "mode": "vuln_repro",
              "target_is_owned_or_sandbox": False})["allowed"] is False, "H4: real target -> REFUSE")
# H5: scoped_engagement with empty scope fails closed
ok(authorize({"authorization_context": "scoped_engagement", "scope": "", "mode": "ctf_solve",
              "target_is_owned_or_sandbox": True})["allowed"] is False, "H5: empty scope -> REFUSE")
# H6: unknown mode fails closed
ok(authorize({"authorization_context": "ctf", "mode": "exfiltrate_everything",
              "target_is_owned_or_sandbox": True})["allowed"] is False, "H6: unknown mode -> REFUSE")
# H7: a misconfigured CTF checker (no committed answer) refuses, never auto-passes
ok(verify_flag("anything")["verdict"] == "NO_COMMITTED_ANSWER", "H7: no committed answer -> no pass")

# ---- AUDIT REGRESSIONS (cross-model Sonnet red-team, 2026-06-20) ----------- #
# D1 (HIGH, fail-open): the real-target guard was `owned is False` (identity), so an
#   ABSENT key / None / 0 / "false" bypassed it. Now requires explicit True.
ok(authorize({"authorization_context": "ctf", "mode": "ctf_solve"})["allowed"] is False,
   "D1: absent target_is_owned_or_sandbox -> REFUSE (fail closed)")
ok(authorize({"authorization_context": "ctf", "mode": "ctf_solve",
              "target_is_owned_or_sandbox": "false"})["allowed"] is False,
   "D1: string 'false' -> REFUSE")
ok(authorize({"authorization_context": "ctf", "mode": "ctf_solve",
              "target_is_owned_or_sandbox": 0})["allowed"] is False, "D1: int 0 -> REFUSE")
ok(authorize({"authorization_context": "ctf", "mode": "ctf_solve",
              "target_is_owned_or_sandbox": None})["allowed"] is False, "D1: None -> REFUSE")
ok(authorize({"authorization_context": "ctf", "mode": "ctf_solve",
              "target_is_owned_or_sandbox": True})["allowed"] is True, "D1: explicit True still ALLOWs")
# D2 (MED-HIGH): category blocklist was exact-match; aliases / spacing / non-string slipped through.
for alias in ["ddos", "denial_of_service", "denial-of-service", "supply chain", "supply-chain",
              "malware deployment", "mass targeting", "ransomware", "lateral_movement", "edr_evasion"]:
    ok(authorize({"authorization_context": "ctf", "mode": "ctf_solve",
                  "target_is_owned_or_sandbox": True, "requested_category": alias})["allowed"] is False,
       f"D2: out-of-scope alias '{alias}' -> REFUSE")
ok(authorize({"authorization_context": "ctf", "mode": "ctf_solve", "target_is_owned_or_sandbox": True,
              "requested_category": ["dos"]})["allowed"] is False, "D2: list category -> REFUSE (type guard)")
ok(authorize({"authorization_context": "ctf", "mode": "ctf_solve", "target_is_owned_or_sandbox": True,
              "requested_category": {"c": "dos"}})["allowed"] is False, "D2: dict category -> REFUSE (type guard)")
# D4 (MED): a crashing patched build must NOT score PATCH_VALID.
CRASH = "def target(poc):\n    raise RuntimeError('boom')\n"
rc = validate_patch(VULN, CRASH, {"path": "../../../../etc/passwd"}, violates)
ok(rc["verdict"] != "PATCH_VALID", "D4: crashing patch must not score PATCH_VALID")
ok(rc["verdict"] == "PATCH_CRASHED", "D4: crashing patch -> PATCH_CRASHED")

print(f"REDCELL selftest_all: PASS ({n} assertions) -- authorized CTF + PATCH-VALIDATE work (kappa=1); "
      "REFUSES no-context, out-of-scope categories, the in-scope-wrapper trick, malformed/unknown "
      "context, real targets, empty scope, unknown mode; misconfigured checker never auto-passes. "
      "The gate fails CLOSED.")
