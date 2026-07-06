# REDCELL — GROUNDING (the policy-as-spec; no exploits fetched)

REDCELL's spec is the **security policy in the system guidance** — that IS the gate. No exploit
techniques are fetched or needed; the load-bearing artifacts are the authorization taxonomy and the
κ=1 flag/patch checkers, both pure machine code.

## G1 — the authorization / scope policy (verbatim intent, encoded as the gate)
From the operating security policy (system guidance), REDCELL **assists with**:
- authorized security testing, defensive security, CTF challenges, and educational contexts.

REDCELL **refuses**:
- destructive techniques, denial-of-service (DoS) attacks, mass targeting, supply-chain compromise, and
  detection-evasion for malicious purposes.

Dual-use security work (e.g. exploit development, credential testing, C2-style tooling) requires a
**clear authorization context**: a pentesting engagement with scope, a CTF competition, security
research in a sandbox, or a defensive use case. **Absent that context, REDCELL refuses by default.**

This policy is encoded directly in `auth_gate.py`:
- allowed `authorization_context` ∈ {`ctf`, `owned_system`, `scoped_engagement`, `sandbox_research`,
  `education`} (scoped_engagement additionally REQUIRES an explicit non-empty `scope`).
- refused scope categories ∈ {`dos`, `mass_targeting`, `supply_chain`, `malware_deployment`,
  `malicious_evasion`, `unauthorized_real_target`} — refused regardless of the asserted context.
- missing / unknown / malformed context → **REFUSE (fail closed)**.

## G2 — CTF flag-format convention (the κ=1 checker target)
CTF challenges award a **flag**, conventionally a fixed string the challenge author commits to, often
wrapped in a recognizable format such as `FLAG{...}` / `CTF{...}` / `picoCTF{...}`. Verification is
exact: the submitted flag string equals the committed flag (or its known hash). This is the κ=1 verifier
for CTF-SOLVE — no judgment, a byte-exact comparison (constant-time to avoid leaking via timing).

## G3 — patch-validation logic (the defensive κ=1 verifier)
A patch is validated by the **differential**: the same proof-of-concept input must (a) **trigger** the
vulnerable behaviour on the UNPATCHED build and (b) **fail to trigger** on the PATCHED build, both run in
an isolated sandbox. A patch that does not change the PoC outcome did not fix the issue (or the PoC does
not exercise it). This is the standard regression-style validation; the artifact is a pass/fail on the
fix, not a deployable exploit.

## Ceiling note
κ=1 here means the flag/PoC *outcome* is exact. It is NOT a claim the target is "secure" — absence of a
single firing PoC is not absence of vulnerabilities. Outputs are fixes + detections, never deployable weapons.
