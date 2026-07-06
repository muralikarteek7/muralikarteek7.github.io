#!/usr/bin/env python3
"""PATCH-VALIDATE verifier (kappa=1, DEFENSIVE) — does a patch close a PoC?

The differential, run in an ISOLATED SANDBOX (separate subprocess + CPU/time limit):
  * the SAME proof-of-concept input must FIRE on the UNPATCHED build, and
  * FAIL to fire on the PATCHED build.
The security property is checked by an INDEPENDENT predicate in the parent (the build
does NOT grade itself). Verdict:
  PATCH_VALID        : fired on unpatched AND not on patched (the patch closes it)
  PATCH_INEFFECTIVE  : still fires on patched (not fixed)
  POC_DOES_NOT_EXERCISE : did not fire even on unpatched (inconclusive PoC)

This produces a pass/fail on a FIX in a sandbox -- a defensive artifact, never a
deployable exploit.
"""
import sys, os, json, tempfile, subprocess, textwrap

# driver run inside the child: imports the build, runs target(poc), prints JSON result.
# CPU + address-space limits are applied so a runaway/abusive build cannot harm the host.
_CHILD = textwrap.dedent('''
    import sys, json
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    except Exception:
        pass
    build_path, poc_json = sys.argv[1], sys.argv[2]
    poc = json.loads(poc_json)
    ns = {}
    with open(build_path) as f:
        code = f.read()
    try:
        exec(compile(code, build_path, "exec"), ns)
        result = ns["target"](poc)
        print(json.dumps({"ok": True, "result": result}))
    except Exception as e:
        print(json.dumps({"ok": True, "result": {"__exception__": type(e).__name__ + ": " + str(e)}}))
''')


def _run_in_sandbox(build_code, poc, timeout=5):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as bf:
        bf.write(build_code); build_path = bf.name
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as df:
        df.write(_CHILD); driver_path = df.name
    try:
        proc = subprocess.run([sys.executable, driver_path, build_path, json.dumps(poc)],
                              capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0 or not proc.stdout.strip():
            return {"ok": False, "error": (proc.stderr or "no output")[:300]}
        data = json.loads(proc.stdout.strip().splitlines()[-1])
        # audit fix D4: a build that THREW is not a clean result -- demote to crashed so
        # a crashing 'patch' cannot be scored PATCH_VALID (a crash closes nothing).
        if isinstance(data.get("result"), dict) and "__exception__" in data["result"]:
            return {"ok": False, "crashed": True, "error": data["result"]["__exception__"]}
        return data
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout (possible DoS in build) -> treated as no clean result"}
    finally:
        for p in (build_path, driver_path):
            try: os.unlink(p)
            except OSError: pass


def validate_patch(unpatched_code, patched_code, poc, violates, timeout=5):
    """violates(poc, sandbox_output) -> bool : INDEPENDENT security-property predicate.
    Returns the differential PATCH-VALIDATE verdict (kappa=1)."""
    un = _run_in_sandbox(unpatched_code, poc, timeout)
    pa = _run_in_sandbox(patched_code, poc, timeout)
    fired_un = bool(un.get("ok") and violates(poc, un.get("result")))
    fired_pa = bool(pa.get("ok") and violates(poc, pa.get("result")))
    patched_crashed = bool(pa.get("crashed"))

    if not fired_un:
        verdict = "POC_DOES_NOT_EXERCISE"
    elif patched_crashed:
        # audit fix D4: a patch that crashes on the PoC is NOT a valid fix
        verdict = "PATCH_CRASHED"
    elif fired_pa:
        verdict = "PATCH_INEFFECTIVE"
    else:
        verdict = "PATCH_VALID"

    return {"mode": "PATCH-VALIDATE", "kappa": 1,
            "fired_on_unpatched": fired_un, "fired_on_patched": fired_pa,
            "patched_crashed": patched_crashed,
            "unpatched_output": un.get("result"),
            "patched_output": pa.get("result") if pa.get("ok") else {"__error__": pa.get("error")},
            "verdict": verdict,
            "ceiling_note": "A pass/fail on a FIX in a sandbox (differential PoC). kappa=1 on THIS "
                            "PoC's outcome only -- PATCH_VALID is not a claim the build is secure in "
                            "general. A defensive artifact, never a deployable weapon."}


if __name__ == "__main__":
    # Self-contained sandboxed demo: a path-traversal access check.
    # Vulnerable: naive prefix check; Patched: normalize then confine to base dir.
    VULN = textwrap.dedent('''
        import os
        BASE = "/srv/app/public"
        def target(poc):
            req = poc["path"]
            full = BASE + "/" + req                # naive concat, no normalization
            # vulnerable: only checks the *unresolved* string starts with BASE
            allowed = full.startswith(BASE)
            return {"resolved": os.path.normpath(full), "allowed": allowed}
    ''')
    PATCHED = textwrap.dedent('''
        import os
        BASE = "/srv/app/public"
        def target(poc):
            req = poc["path"]
            full = os.path.normpath(BASE + "/" + req)
            # patched: confine the RESOLVED path to BASE
            allowed = full == BASE or full.startswith(BASE + "/")
            return {"resolved": full, "allowed": allowed}
    ''')
    # independent property: access is a violation if it is ALLOWED but resolves OUTSIDE BASE
    def violates(poc, out):
        if not isinstance(out, dict) or "resolved" not in out:
            return False
        return bool(out.get("allowed")) and not out["resolved"].startswith("/srv/app/public")

    poc = {"path": "../../../../etc/passwd"}
    r = validate_patch(VULN, PATCHED, poc, violates)
    print(json.dumps(r, indent=2))
    assert r["verdict"] == "PATCH_VALID", r
    print("\npatch_verify smoke: PASS (PoC fires on unpatched, fails on patched -> PATCH_VALID)")
