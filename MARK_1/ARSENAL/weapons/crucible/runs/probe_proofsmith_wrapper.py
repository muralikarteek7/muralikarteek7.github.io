#!/usr/bin/env python3
"""CRUCIBLE probe — PROOFSMITH *WRAPPER* (the pure-Python axiom/IO/sorry scan around
the Lean kernel), NOT the Lean kernel itself.

SCOPE (non-waivable, stated up front):
  * Lean/lake are NOT on $PATH in this environment, BUT proofsmith's gate has an
    `~/.elan/bin` fallback and Lean 4.31.0 DOES run from there. So the kernel IS
    reachable. This probe DELIBERATELY DOES NOT exercise the kernel: it targets only
    the WRAPPER layer that runs in pure Python BEFORE/AROUND any `_run_lean` call.
  * The cleanest kernel-free wrapper surface is PRE-CHECK 0 in proof_gate.gate():
    the `_IO_COMMANDS` regex scan. When it matches, gate() returns a REJECT verdict
    (rejected_reason set) and RETURNS IMMEDIATELY, never calling `_run_lean`.
  * To PROVE we never touch the kernel, we monkeypatch proof_gate._run_lean to a
    TRIPWIRE that raises if called. Under the GateAdapter that raise maps to ERROR,
    so any candidate that slips past PRE-CHECK 0 into Lean shows up as a crash, not a
    silent kernel run. (We assert zero tripwire hits at the end.)

MODES: metamorphic + abstain-crash ONLY (per task). NO oracle: we cannot independently
decide "would Lean execute this hidden #eval?" without invoking the kernel, which is
out of scope -> transform meaning-preservation is CALLER-ASSERTED (residual risk),
exactly as the harness documents for oracle=None.

The adapter IMPORTS AND CALLS the real gate (proof_gate.gate). It re-implements nothing.
"""
import sys
import os
import json

# --- wire the REAL weapon gate (black-box import from the sibling weapon dir) -------
PROOFSMITH_DIR = "/Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/proofsmith"
CRUCIBLE_DIR = "/Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/crucible"
sys.path.insert(0, PROOFSMITH_DIR)
sys.path.insert(0, CRUCIBLE_DIR)

import proof_gate                      # the REAL PROOFSMITH wrapper+kernel gate
from crucible_harness import (
    GateAdapter, ACCEPT, REJECT, ABSTAIN, ERROR,
    metamorphic_hunt, abstain_crash_hunt,
)

# --- KERNEL TRIPWIRE: prove the kernel is NEVER invoked by this probe ---------------
_TRIPWIRE = {"lean_calls": 0, "last_args": None}


def _kernel_tripwire(*args, **kwargs):
    _TRIPWIRE["lean_calls"] += 1
    _TRIPWIRE["last_args"] = (args, kwargs)
    # Raising here means: if any candidate reaches the kernel, the adapter maps it to
    # ERROR (a visible crash), NOT a silent real kernel run. We are wrapper-only.
    raise AssertionError("KERNEL TRIPWIRE: proof_gate._run_lean was invoked — this "
                         "candidate left the pure-Python wrapper surface (out of scope).")


proof_gate._run_lean = _kernel_tripwire   # monkeypatch the real module's kernel call


# --- the REAL gate's verdict fn, called black-box as fn(**obj) ----------------------
def _proofsmith_wrapper_fn(proof_source, targets):
    """Call the REAL proof_gate.gate. With _run_lean tripwired, only PRE-CHECK 0
    (the pure-Python IO/meta-command scan) can produce a verdict; anything that would
    reach the kernel raises (-> ERROR)."""
    return proof_gate.gate(proof_source, targets)


def _to_verdict(raw):
    """Map the REAL gate's native dict onto CRUCIBLE's vocabulary.
      accepted True                       -> ACCEPT
      PRE-CHECK 0 fired (rejected_reason) -> REJECT   (the wrapper killed the bundle)
      accepted False, no rejected_reason  -> ABSTAIN  (would-be-kernel path; shouldn't occur)
    """
    if raw.get("accepted") is True:
        return ACCEPT
    if "rejected_reason" in raw:
        return REJECT
    return ABSTAIN


gate = GateAdapter("PROOFSMITH-wrapper(IO-scan)", _proofsmith_wrapper_fn, _to_verdict)


# --- SEEDS: bundles whose verdict is decided ENTIRELY by the wrapper PRE-CHECK 0 -----
# Each contains a forbidden elaboration-time IO/meta command, so PRE-CHECK 0 REJECTs it
# without ever calling Lean. These are the gate-self-declared kappa=1 wrapper outcomes
# (an IO-bearing bundle is REJECTED unconditionally — stated in the gate docstring).
def _seed(src, names):
    return {"proof_source": src,
            "targets": [{"name": nm, "reference_statement": "2 + 2 = 4",
                         "allowed_axioms": []} for nm in names]}


SEEDS = [
    _seed("theorem a : 2 + 2 = 4 := rfl\n#eval IO.println \"x\"\n", ["a"]),
    _seed("theorem a : 2 + 2 = 4 := rfl\nrun_cmd pure ()\n", ["a"]),
    _seed("theorem a : 2 + 2 = 4 := rfl\ntheorem b : 1 + 1 = 2 := rfl\n#exit\n", ["a", "b"]),
    _seed("unsafe def danger : Nat := 0\ntheorem a : 2 + 2 = 4 := rfl\n", ["a"]),
    _seed("initialize x : Nat <- pure 0\ntheorem a : 2 + 2 = 4 := rfl\n", ["a"]),
    _seed("@[implemented_by foo] theorem a : 2 + 2 = 4 := rfl\n", ["a"]),
]


# --- METAMORPHIC transforms: CLAIMED meaning-preserving reformattings ----------------
# A bundle REJECTED for containing a forbidden IO/meta command must STAY rejected under
# reformatting that does not remove the command. Meaning-preservation is CALLER-ASSERTED
# (no oracle): we never invoke Lean to confirm, so this is residual risk.
def _t_trailing_ws(obj):
    # append trailing spaces/newlines — pure whitespace, command still present
    return {"proof_source": obj["proof_source"].rstrip() + "   \n\n",
            "targets": obj["targets"]}


def _t_leading_blankline(obj):
    # prepend blank lines — does not remove the forbidden command
    return {"proof_source": "\n\n" + obj["proof_source"],
            "targets": obj["targets"]}


def _t_reorder_targets(obj):
    # reverse the targets list — same theorems, same source; verdict must not change
    return {"proof_source": obj["proof_source"],
            "targets": list(reversed(obj["targets"]))}


def _t_indent_command(obj):
    # indent every line by two spaces — Lean is whitespace-insensitive at decl level
    # and the IO command is still lexically present (the regex has no anchoring)
    src = "\n".join("  " + ln if ln.strip() else ln
                    for ln in obj["proof_source"].splitlines())
    return {"proof_source": src + "\n", "targets": obj["targets"]}


def _t_crlf(obj):
    # normalize newlines to CRLF — line content (incl. the command) unchanged
    return {"proof_source": obj["proof_source"].replace("\n", "\r\n"),
            "targets": obj["targets"]}


TRANSFORMS = [
    ("append-trailing-whitespace", _t_trailing_ws),
    ("prepend-blank-lines", _t_leading_blankline),
    ("reorder-targets-list", _t_reorder_targets),
    ("indent-all-lines-2sp", _t_indent_command),
    ("newline->CRLF", _t_crlf),
]


# --- ABSTAIN/CRASH malformed inputs: wrapper must not silently ACCEPT garbage --------
# SAFE = the wrapper rejects, abstains, or raises a guard (ERROR). A silent ACCEPT on
# garbage would be the bug. All of these still carry a forbidden IO command (so the
# correct outcome is REJECT) OR are structurally degenerate.
_SAFE = {REJECT, ABSTAIN, ERROR}
MALFORMED = [
    # NB: every malformed input here MUST be decided by the wrapper's pure-Python path
    # (PRE-CHECK 0 IO-scan, or a Python error BEFORE _run_lean). A no-IO/empty source
    # would sail past PRE-CHECK 0 into the kernel — that is NOT a wrapper probe, so it
    # is deliberately excluded (see _run_lean tripwire assertion below).
    ("IO command + degenerate empty-string target name",
     {"proof_source": "#eval IO.println \"x\"\n",
      "targets": [{"name": "", "reference_statement": "2+2=4", "allowed_axioms": []}]}, _SAFE),
    ("IO command but EMPTY targets list",
     {"proof_source": "#eval IO.println \"x\"\n", "targets": []}, _SAFE),
    ("targets missing 'name' key (KeyError path) + IO cmd",
     {"proof_source": "#eval foo\n", "targets": [{"reference_statement": "2+2=4"}]}, _SAFE),
    ("source is None (type error path)",
     {"proof_source": None, "targets": [{"name": "a", "reference_statement": "2+2=4",
                                          "allowed_axioms": []}]}, _SAFE),
    ("targets is None",
     {"proof_source": "#eval foo\n", "targets": None}, _SAFE),
    ("only an IO command, no theorem at all",
     {"proof_source": "run_cmd pure ()\n",
      "targets": [{"name": "ghost", "reference_statement": "2+2=4", "allowed_axioms": []}]}, _SAFE),
]


def main():
    print("=" * 78)
    print("CRUCIBLE probe: PROOFSMITH WRAPPER (pure-Python IO/meta-command scan)")
    print("REAL gate: proof_gate.gate  | kernel: TRIPWIRED (must stay 0 calls)")
    print("modes: metamorphic + abstain-crash | oracle: NONE (meaning-preservation"
          " caller-asserted)")
    print("=" * 78)

    # sanity: a clean (no-IO) bundle would HEAD INTO the kernel -> tripwire -> ERROR.
    # This confirms the tripwire actually fires when the kernel is reached, so a 0-count
    # at the end genuinely means "we never left the wrapper", not "tripwire is dead".
    clean = {"proof_source": "theorem a : 2 + 2 = 4 := rfl\n",
             "targets": [{"name": "a", "reference_statement": "2 + 2 = 4",
                          "allowed_axioms": []}]}
    clean_v = gate.verdict(clean)
    print(f"\n[tripwire liveness] clean (no-IO) bundle -> {clean_v} "
          f"(expect ERROR: it would reach the kernel) | lean_calls so far="
          f"{_TRIPWIRE['lean_calls']}")
    assert clean_v == ERROR, "tripwire DEAD: a kernel-bound bundle did not ERROR"
    calls_after_liveness = _TRIPWIRE["lean_calls"]

    # confirm every SEED is a wrapper REJECT (decided by PRE-CHECK 0, no kernel)
    print("\n[seed verdicts] (all must be REJECT, decided by the wrapper scan):")
    for i, s in enumerate(SEEDS):
        v = gate.verdict(s)
        print(f"  seed[{i}] -> {v}")

    # --- MODE 1: METAMORPHIC -------------------------------------------------------
    print("\n--- MODE 1: METAMORPHIC (verdict must be invariant under reformatting) ---")
    mm = metamorphic_hunt(gate, SEEDS, TRANSFORMS, max_probes=10000, oracle=None)
    print(json.dumps(mm.to_dict(), indent=2, default=str))

    # --- MODE 2: ABSTAIN/CRASH -----------------------------------------------------
    print("\n--- MODE 2: ABSTAIN/CRASH (no silent ACCEPT on malformed input) ---")
    ac = abstain_crash_hunt(gate, MALFORMED, max_probes=1000)
    print(json.dumps(ac.to_dict(), indent=2, default=str))

    # --- the kernel must NEVER have been invoked by the actual hunts ----------------
    hunt_kernel_calls = _TRIPWIRE["lean_calls"] - calls_after_liveness
    print("\n" + "=" * 78)
    print(f"KERNEL TRIPWIRE: {hunt_kernel_calls} kernel call(s) during the hunts "
          f"(MUST be 0 for a wrapper-only probe).")
    print(f"(total tripwire hits incl. the deliberate liveness check = "
          f"{_TRIPWIRE['lean_calls']})")
    assert hunt_kernel_calls == 0, ("WRAPPER-ONLY VIOLATED: a hunt candidate reached "
                                    "the kernel.")
    print("WRAPPER-ONLY CONFIRMED: every hunt verdict came from the pure-Python scan.")
    print("=" * 78)


if __name__ == "__main__":
    main()
