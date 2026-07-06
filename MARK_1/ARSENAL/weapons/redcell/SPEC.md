# REDCELL — SPEC (Weapon #9, CS_ENG/Security — AUTHORIZATION-GATED)

*A κ=1 security weapon scoped to AUTHORIZED and DEFENSIVE use only. The verifier is sharp (a flag
validates or it doesn't), but the DOMINANT control is the AUTHORIZATION GATE — built defensive-first,
refuses by default, fails closed. Written 2026-06-20, box-style. Build LAST; the gate is the most-audited
component.*

## 1. WHAT IT IS (one line)
Given an *authorized* security task, produce a machine-verified artifact — a CTF flag, a sandboxed
proof-of-concept for patch validation, or a sandboxed CVE reproduction for detection-building — where the
verifier is exact (the flag validates / the PoC fires on the unpatched build and fails on the patched
build / the repro triggers in an isolated sandbox).

## 2. WHAT IT IS NOT (the gate — fail closed; non-waivable)
- **NOT for unauthorized or real-world targets.** No task proceeds without an explicit
  `authorization_context` (ctf / owned_system / scoped_engagement_with_scope / sandbox_research /
  education). **Absent that → REFUSE.** This is the default.
- **NOT a producer of destructive / at-scale harm.** No DoS, no mass/indiscriminate targeting, no
  supply-chain compromise, no malware-for-deployment, no detection-evasion intended for malicious use.
  **Out of scope by policy, regardless of framing.**
- **NOT a capability boost** — organized, sandboxed, authorized security rigor; not smarter.

## 3. THE MODES (κ=1 verifier; authorization-gated)
| mode | when (authorized) | produces | verifier (κ=1) |
|---|---|---|---|
| **CTF-SOLVE** | a CTF challenge | the flag | the flag validates against the challenge checker (exact) |
| **PATCH-VALIDATE** ⭐ (defensive) | a known PoC + a patch on an owned system | pass/fail on the fix | the PoC fires on the unpatched build and **FAILS on the patched build** (sandboxed, exact) |
| **VULN-REPRO** (defensive research) | a published CVE, reproduced in a sandbox for detection-building | a sandboxed repro + detection signature | the repro triggers in an isolated sandbox; artifact is the **detection**, not a weaponized exploit |

All three run in an isolated sandbox against owned/authorized targets only.

## 4. KEY ENGINEERING PROBLEM — the authorization gate fails closed
1. **Authorization gate FIRST** (before any security logic): an explicit `authorization_context` is
   REQUIRED. No context → REFUSE. Out-of-scope categories (DoS, mass-targeting, supply-chain, malicious
   evasion) → REFUSE with reason. The gate classifies BEFORE any mode runs.
2. **Sandbox isolation** — all execution in an isolated environment against authorized targets; never a
   live third-party system.
3. **Defensive framing of outputs** — PATCH-VALIDATE / VULN-REPRO produce fixes + detections; the
   artifact is scoped to verification, not a deployable weapon.

## 5. GATE SELF-TESTS (non-waivable — the refusal tests matter as much as the success tests)
(a) PASS an authorized CTF-flag validation; (b) **REFUSE a task with no authorization context**;
(c) **REFUSE an out-of-scope category** (e.g. "take down site X" / "compromise dependency Y") with a
clear reason; (d) PATCH-VALIDATE correctly distinguishes patched vs unpatched in the sandbox. Plus
hardening: a malicious task that *claims* an authorization context but requests an out-of-scope action is
still refused (scope beats the asserted context); a malformed/ambiguous context fails CLOSED (refuse).

## 6. ROUTER (`redcell_router.py`)
classify `authorization_context` + scope FIRST (refuse-by-default) → (authorized & in-scope) run the
mode in sandbox → κ=1 verify. Refuse otherwise, with a reason.

## 7. CEILING
Authorized/defensive scope only. The gate fails closed; a fail-open gate is a blocking defect. Outputs
are fixes + detections, not deployable weapons. κ=1 means the flag/PoC verdict is exact — it is NOT a
claim the target is "secure" in general (absence of one PoC ≠ absence of vulnerabilities). A weapon ADDED
= capability EXPANSION, NOT a ≥10% promotion.
