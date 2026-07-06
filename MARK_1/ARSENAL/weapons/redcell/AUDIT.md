# REDCELL — independent cross-model red-team (2026-06-20)

**Auditor:** Claude Sonnet (cross-model, ≠ the Opus generator — never Opus-audits-Opus).
**Method:** read all source; ran `selftest_all.py` (20) + demo (8/8) green; then wrote + executed
independent adversarial Python (35 attacks resisted, 16 unexpected behaviours machine-confirmed). The
auth gate was red-teamed hardest, as required (a fail-open = blocking defect).

## Verdict: SOUND-WITH-CAVEATS → **3 real defects found (incl. 1 HIGH gate fail-open), all FIXED + locked**

The cardinal honesty properties held (outputs are verdicts not weapons; REFUSE runs no security logic;
flag comparison is constant-time; the suppressor attack and CPU-exhaustion were resisted). But the
red-team broke the auth gate's structural guards in three places:

| # | defect | severity | fix |
|---|---|---|---|
| **D1** | the real-target guard was `owned is False` (an *identity* test) → an **absent** `target_is_owned_or_sandbox` key, `None`, `0`, or the string `"false"` all bypassed it → **ALLOW**. A genuine **fail-open** of the only structural real-target check. | **HIGH** | require an explicit boolean `True` (`owned is not True` → REFUSE); fail closed on everything else |
| **D2** | `requested_category` was exact-string match only → aliases (`ddos`, `denial_of_service`, `supply chain`, `mass targeting`, `ransomware`, …) and non-string types (list/dict) slipped through as *uncategorized* → ALLOW. | Med-High | space/hyphen-fold + an alias→canonical map + a non-string type guard (fail closed) |
| **D4** | a *patched* build that **crashes** on the PoC scored `PATCH_VALID` (the exception was caught in the child and read as "didn't fire"). | Medium | demote a thrown build to `ok=False, crashed=True`; new `PATCH_CRASHED` verdict; `PATCH_VALID` requires a clean non-fire |

All fixes are in `auth_gate.py` / `patch_verify.py`; break-cases locked in `selftest_all.py` (20 → **39
assertions**, all green). Demo re-ran clean. **The D1 fail-open is the headline:** the BOX's
independent-verification rule caught a real fail-open of the gate's cardinal property that the
generator's own 20 self-tests passed — exactly why audit ≠ generator is non-waivable.

## D3 — design caveat (NOT a code bug; load-bearing, documented)
The gate enforces the **declared** `requested_category`; it is a deterministic structured-policy enforcer,
**not an NLP content classifier**. An attacker who omits `requested_category` while embedding harmful
intent in free text passes the structural gate. In intended use the LLM orchestrator reads the task and
populates `requested_category` from its understanding; the gate then enforces it. This ceiling is now
stated explicitly in `README.md` and the SPEC — the gate is only as strong as the declaration feeding it,
and should sit behind (not replace) the model's own policy reading.

## Informational (matches stated design, not defects)
The sandbox is `subprocess + RLIMIT_CPU + timeout` — it bounds CPU and isolates the process, but does NOT
restrict filesystem writes, env reads, or network attempts (no namespaces/seccomp/chroot). `patch_verify.py`'s
ceiling note already disclaims OS-level isolation. For running genuinely untrusted build code, upgrade to a
container / gVisor / seccomp sandbox. Logged, not fixed (build code is assumed trusted-party in scope).
