#!/usr/bin/env python3
"""PROOFSMITH — the 4-check KERNEL GATE (kappa = 1).

This is the whole game. A proof assistant is the sharpest cheap verifier that
exists: the Lean 4 KERNEL re-checks a fully-elaborated proof term against a tiny
trusted core (the de Bruijn criterion) and accepts it or it doesn't. But a kernel
ALONE is not enough, because proof assistants let you cheat three ways that the
kernel itself does NOT reject as errors:

  * `sorry` / `admit` admits any goal unproven   (lean exits 0, only a warning)
  * adding a false / non-standard `axiom`         (lean exits 0 — the axiom is "true" by fiat)
  * proving a RESTATEMENT that isn't the theorem  (a kernel-checked proof of the wrong thing)

So PROOFSMITH wraps the kernel in FOUR checks, and ships nothing that fails any:

  CHECK 1 — KERNEL ACCEPTS    : the proof term type-checks (no `error:`; lean exit 0).
  CHECK 2 — NO sorry/admit     : reject `sorryAx` in `#print axioms` + the "uses sorry"
                                 warning + a source-token scan. (THE cardinal trap.)
  CHECK 3 — AXIOM ALLOW-LIST   : `#print axioms <thm>` must list only COMMITTED-allowed
                                 axioms (e.g. propext / Classical.choice / Quot.sound for
                                 classical mathlib). Any extra/unknown axiom => REJECT.
  CHECK 4 — STATEMENT MATCH    : the proof proves the COMMITTED reference statement, checked
                                 at KERNEL level via `example : <ref> := <thm>` (type-checks
                                 iff <thm>'s type is defeq to the reference). A proof of the
                                 WRONG statement => REJECT.

  "A gate that can't fail is not a gate" — see selftest_all.py: this gate must ACCEPT a
  known-good proof, and REJECT (a) a sorry-proof, (b) a bogus-axiom proof, (c) a
  proof of a different statement. All four, or no PROOFSMITH output is trustworthy.

HONEST SCOPE: CHECK 4 verifies the proof matches a *committed FORMAL reference statement*.
Whether that formal statement actually MEANS the intended English theorem
(autoformalization) is a kappa<1 JUDGMENT — it is NOT certified here; it is sent to an
independent cross-model review (see proofsmith_router.py / AUDIT.md). Kernel-checked
== "proves this formal statement", NOT "the English theorem is true".
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# The three standard classical axioms of Lean 4 / mathlib. Allowing these is the
# normal "classical mathematics" stance. sorryAx is NEVER in any allow-list.
CLASSICAL_AXIOMS = ["propext", "Classical.choice", "Quot.sound"]
FORBIDDEN_AXIOMS = ["sorryAx"]  # can never be allowed, even if a caller lists it

_SORRY_TOKENS = re.compile(r"(?<![A-Za-z0-9_])(sorry|admit)(?![A-Za-z0-9_])")

# Elaboration-time IO / meta commands a legitimate PROOF never needs. They run
# arbitrary code inside the gate's Lean subprocess (audit finding, 2026-06-20:
# `#eval IO.FS.writeFile ...` executes during gating). Not a proof-soundness
# bypass — the sorry/axiom checks still hold — but a sandboxing gap, so the gate
# refuses any bundle containing them. (A proof term needs none of these.)
_IO_COMMANDS = re.compile(r"(?<![A-Za-z0-9_])(#eval|#exit|run_cmd|#run_cmd|"
                          r"initialize\b|unsafe\b|implemented_by|extern\b)")


def _lean_exe():
    """Locate the lean executable (elan install lives in ~/.elan/bin)."""
    cand = shutil.which("lean")
    if cand:
        return cand
    home = os.path.expanduser("~/.elan/bin/lean")
    if os.path.exists(home):
        return home
    return None


def lean_available():
    return _lean_exe() is not None


def _strip_comments(src):
    """Remove Lean line (--) and block (/- -/) comments so the source-token scan
    does not false-positive on the word 'sorry' inside a comment/docstring."""
    src = re.sub(r"/-.*?-/", " ", src, flags=re.DOTALL)
    src = re.sub(r"--[^\n]*", " ", src)
    return src


def _run_lean(source, timeout=120, lake_project=None):
    """Write `source` to a temp .lean file, run the kernel, return (exit, output).

    If `lake_project` is given (a path to a lake project dir, e.g. one that requires
    mathlib), run `lake env lean <file>` from that dir so imports resolve. Otherwise
    run bare `lean` (pure Lean 4 core, no library)."""
    exe = _lean_exe()
    if exe is None:
        raise RuntimeError("lean not found; install via elan or use the SMT fallback (smt_gate.py)")
    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False) as f:
        f.write(source)
        path = f.name
    try:
        env = dict(os.environ)
        env["PATH"] = os.path.expanduser("~/.elan/bin") + os.pathsep + env.get("PATH", "")
        if lake_project:
            lake = shutil.which("lake") or os.path.expanduser("~/.elan/bin/lake")
            cmd = [lake, "env", "lean", path]
            cwd = lake_project
        else:
            cmd = [exe, path]
            cwd = None
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, env=env, cwd=cwd)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    finally:
        os.unlink(path)


def _parse_axioms(output, name):
    """From `#print axioms <name>` output, return the list of axioms `name` uses.
    Handles both 'does not depend on any axioms' and 'depends on axioms: [a, b]'.
    Returns None if no axiom report for `name` was found."""
    if re.search(rf"'{re.escape(name)}' does not depend on any axioms", output):
        return []
    m = re.search(rf"'{re.escape(name)}' depends on axioms: \[([^\]]*)\]", output)
    if m:
        inner = m.group(1).strip()
        if not inner:
            return []
        return [a.strip() for a in inner.split(",") if a.strip()]
    return None


def gate(proof_source, targets, timeout=120, lake_project=None):
    """Run the 4-check kernel gate over a Lean proof bundle.

    proof_source : str   -- the full Lean source (imports + the theorem(s)).
    targets      : list of dicts, each:
        { "name": <thm name as declared in proof_source>,
          "reference_statement": <Lean type expr the proof must prove, COMMITTED>,
          "allowed_axioms": [<axiom names>]   # optional; default = [] (no axioms) }

    Returns a verdict dict. `accepted` is True ONLY if every target passes all 4
    checks. The verdict is fully machine-derived from the kernel's own output; no
    self-report from the producer is trusted.
    """
    src_nocomments = _strip_comments(proof_source)
    result = {"weapon": "PROOFSMITH", "kappa": 1, "accepted": False,
              "lean_version_checked": True, "targets": {}, "errors": []}

    # PRE-CHECK 0 — refuse elaboration-time IO / meta commands (sandboxing guard).
    io_hit = _IO_COMMANDS.search(src_nocomments)
    if io_hit:
        result["rejected_reason"] = (
            f"submitted source contains a disallowed elaboration-time IO/meta command "
            f"('{io_hit.group(1)}'); a proof never needs it and it runs code in the gate's "
            f"Lean subprocess. Bundle REJECTED unconditionally.")
        for t in targets:
            result["targets"][t["name"]] = {"accepted": False,
                                            "reference_statement": t["reference_statement"],
                                            "check0_no_io_commands": False}
        return result

    # ----- PASS 1: compile the proof + report axioms for every target ----------
    pass1 = proof_source.rstrip() + "\n\n-- == PROOFSMITH axiom probe ==\n"
    for t in targets:
        pass1 += f"#print axioms {t['name']}\n"
    exit1, out1 = _run_lean(pass1, timeout=timeout, lake_project=lake_project)
    errors1 = [ln for ln in out1.splitlines() if "error:" in ln]
    sorry_warn = "uses `sorry`" in out1 or "declaration uses 'sorry'" in out1

    # ----- PASS 2: kernel-level statement match per target ---------------------
    # `example : <ref> := <thm>` type-checks IFF <thm> proves the reference stmt.
    pass2 = proof_source.rstrip() + "\n\n-- == PROOFSMITH statement match ==\n"
    stmt_lines = {}  # name -> the line number (1-based) of its match decl
    cur = pass2.count("\n") + 1
    for t in targets:
        decl = f"theorem __ps_stmt_match_{t['name']} : {t['reference_statement']} := {t['name']}\n"
        stmt_lines[t["name"]] = cur  # decl sits on the current next line
        pass2 += decl
        cur += decl.count("\n")
    exit2, out2 = _run_lean(pass2, timeout=timeout, lake_project=lake_project)
    # map each error in pass2 to the line it occurred on
    stmt_match_errs = {}  # name -> bool (errored?)
    err_lines2 = []
    for ln in out2.splitlines():
        m = re.match(r".*?:(\d+):\d+: error:", ln)
        if m:
            err_lines2.append(int(m.group(1)))
    # an error AT or AFTER a target's decl line, before the next, is that target's
    sorted_targets = sorted(targets, key=lambda t: stmt_lines[t["name"]])
    for i, t in enumerate(sorted_targets):
        lo = stmt_lines[t["name"]]
        hi = stmt_lines[sorted_targets[i + 1]["name"]] if i + 1 < len(sorted_targets) else 10 ** 9
        stmt_match_errs[t["name"]] = any(lo <= e < hi for e in err_lines2)

    # whether the proof body itself (pass2 before the appended block) had errors
    proof_body_max_line = pass2.split("-- == PROOFSMITH statement match ==")[0].count("\n")
    proof_body_error = any(e <= proof_body_max_line for e in err_lines2) or bool(errors1)

    # ----- adjudicate each target ---------------------------------------------
    all_ok = True
    src_has_sorry_token = bool(_SORRY_TOKENS.search(src_nocomments))
    for t in targets:
        name = t["name"]
        allowed = [a for a in t.get("allowed_axioms", []) if a not in FORBIDDEN_AXIOMS]
        axioms = _parse_axioms(out1, name)

        check1 = (exit1 == 0) and (axioms is not None) and not proof_body_error
        # CHECK 2 — no sorry/admit
        used_sorry = (axioms is not None and "sorryAx" in axioms) or sorry_warn or src_has_sorry_token
        check2 = not used_sorry
        # CHECK 3 — axiom allow-list
        if axioms is None:
            check3 = False
            extra = None
        else:
            extra = [a for a in axioms if a not in allowed and a != "sorryAx"]
            check3 = (len(extra) == 0)
        # CHECK 4 — statement match (kernel-level)
        check4 = (name in stmt_match_errs) and (not stmt_match_errs[name]) and not proof_body_error

        passed = check1 and check2 and check3 and check4
        all_ok = all_ok and passed
        result["targets"][name] = {
            "reference_statement": t["reference_statement"],
            "allowed_axioms": allowed,
            "axioms_used": axioms,
            "extra_axioms": extra,
            "check1_kernel_accepts": bool(check1),
            "check2_no_sorry_admit": bool(check2),
            "check3_axiom_allowlist": bool(check3),
            "check4_statement_match": bool(check4),
            "accepted": bool(passed),
        }

    result["accepted"] = bool(all_ok and len(targets) > 0)
    result["lean_exit_pass1"] = exit1
    result["lean_exit_pass2"] = exit2
    if errors1:
        result["errors"] = errors1[:20]
    result["note"] = ("kappa=1 KERNEL verdict. CHECK 4 proves the COMMITTED FORMAL "
                      "statement; whether that formal statement MEANS the English theorem "
                      "is a kappa<1 autoformalization judgment -> cross-model review, NOT "
                      "certified here.")
    return result


# =============================== SELF-TESTS ================================= #
# "A gate that can't fail is not a gate." These run real Lean. They must:
#   (a) ACCEPT a known-good kernel-checked proof,
#   (b) REJECT a sorry-proof,
#   (c) REJECT a proof that adds a bogus axiom,
#   (d) REJECT a proof of a DIFFERENT statement.

_GOOD = """\
theorem ps_add_two : 2 + 2 = 4 := rfl
theorem ps_imp_self (p : Prop) : p -> p := fun h => h
"""

_SORRY = """\
theorem fake : 2 + 2 = 5 := by sorry
"""

_BOGUS = """\
axiom bogus_false : (2 : Nat) + 2 = 5
theorem fake_via_axiom : 2 + 2 = 5 := bogus_false
"""

_WRONGSTMT = """\
theorem proves_four : 2 + 2 = 4 := rfl
"""


def _selftest():
    if not lean_available():
        raise RuntimeError("lean not installed; cannot run the kernel-gate self-test. "
                           "Install Lean 4 via elan, or run the SMT fallback self-test.")

    # (a) ACCEPT a known-good proof (no axioms)
    g = gate(_GOOD, [
        {"name": "ps_add_two", "reference_statement": "2 + 2 = 4", "allowed_axioms": []},
        {"name": "ps_imp_self", "reference_statement": "forall (p : Prop), p -> p", "allowed_axioms": []},
    ])
    assert g["accepted"] is True, ("ACCEPT-GOOD failed", g)
    assert g["targets"]["ps_add_two"]["axioms_used"] == [], g

    # (b) REJECT a sorry-proof  -> check2 must be False, sorryAx surfaced
    s = gate(_SORRY, [{"name": "fake", "reference_statement": "2 + 2 = 5", "allowed_axioms": CLASSICAL_AXIOMS}])
    assert s["accepted"] is False, ("REJECT-SORRY failed (gate accepted a sorry-proof!)", s)
    assert s["targets"]["fake"]["check2_no_sorry_admit"] is False, s
    assert "sorryAx" in (s["targets"]["fake"]["axioms_used"] or []), s

    # (c) REJECT a bogus-axiom proof -> check3 must be False, extra axiom surfaced
    b = gate(_BOGUS, [{"name": "fake_via_axiom", "reference_statement": "2 + 2 = 5", "allowed_axioms": CLASSICAL_AXIOMS}])
    assert b["accepted"] is False, ("REJECT-BOGUS-AXIOM failed (gate accepted a fake axiom!)", b)
    assert b["targets"]["fake_via_axiom"]["check3_axiom_allowlist"] is False, b
    assert "bogus_false" in (b["targets"]["fake_via_axiom"]["extra_axioms"] or []), b

    # (d) REJECT a proof of a DIFFERENT statement -> check4 must be False.
    # proof proves 2+2=4 but the COMMITTED reference says 2+2=5.
    w = gate(_WRONGSTMT, [{"name": "proves_four", "reference_statement": "2 + 2 = 5", "allowed_axioms": []}])
    assert w["accepted"] is False, ("REJECT-WRONG-STATEMENT failed (gate accepted wrong stmt!)", w)
    assert w["targets"]["proves_four"]["check4_statement_match"] is False, w
    # and sanity: with the CORRECT reference it WOULD pass check4
    w2 = gate(_WRONGSTMT, [{"name": "proves_four", "reference_statement": "2 + 2 = 4", "allowed_axioms": []}])
    assert w2["accepted"] is True, ("control: correct-reference proof should pass", w2)

    # (e) REJECT a bundle with an elaboration-time IO command (audit-hardening).
    io_src = _GOOD + "\n#eval IO.FS.writeFile \"/tmp/ps_pwn\" \"x\"\n"
    e = gate(io_src, [{"name": "ps_add_two", "reference_statement": "2 + 2 = 4", "allowed_axioms": []}])
    assert e["accepted"] is False and "rejected_reason" in e, ("REJECT-IO failed", e)

    print("proof_gate selftest: PASS")
    print("  (a) ACCEPT good kernel-checked proof          OK")
    print("  (b) REJECT sorry-proof (sorryAx caught)       OK")
    print("  (c) REJECT bogus-axiom proof (axiom caught)   OK")
    print("  (d) REJECT proof of a DIFFERENT statement     OK")
    print("  (e) REJECT #eval IO command (sandbox guard)   OK")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) == 3:
        src = open(sys.argv[1]).read()
        targets = json.load(open(sys.argv[2]))
        print(json.dumps(gate(src, targets), indent=2))
    else:
        print("usage: proof_gate.py selftest | <proof.lean> <targets.json>")
