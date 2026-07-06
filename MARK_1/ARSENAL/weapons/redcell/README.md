# REDCELL — authorization-gated security weapon (Weapon #9, CS_ENG/Security)

A **κ=1** security weapon scoped to **authorized and defensive use only**. The verifier is sharp (a flag
validates or it doesn't; a PoC fires or it doesn't), but the **dominant control is the AUTHORIZATION
GATE, which fails closed** — it is the most-audited component.

## Modes (authorized only, sandboxed)
- **CTF-SOLVE** — produce a flag; `flag_verify` checks it against the committed answer (constant-time exact / SHA-256).
- **PATCH-VALIDATE** ⭐ (defensive) — a differential PoC: must **fire on the unpatched build and fail on the patched build** in an isolated sandbox → `PATCH_VALID` / `PATCH_INEFFECTIVE` / `PATCH_CRASHED` / `POC_DOES_NOT_EXERCISE`.
- **VULN-REPRO** (defensive research) — sandboxed CVE repro → a *detection signature*, not a weaponized exploit.

## The authorization gate (centerpiece, fail-closed)
`auth_gate.authorize(task)` runs **before any security logic**. It requires an explicit, recognized
`authorization_context` ∈ {ctf, owned_system, scoped_engagement (+scope), sandbox_research, education},
an explicit `target_is_owned_or_sandbox: True`, and a recognized `mode`; it refuses any out-of-scope
category (DoS, mass-targeting, supply-chain, malware-deployment, malicious-evasion, unauthorized target)
**regardless of the asserted context**. Anything missing/unknown/malformed → **REFUSE**.

## Run
```
python3 selftest_all.py              # gate: 39 assertions incl. all refusal + audit-regression paths
python3 auth_gate.py                 # gate decision examples
python3 flag_verify.py / patch_verify.py   # κ=1 checker smoke
python3 redcell_router.py            # routing: gate-first, refuse-by-default
python3 demo_redcell/run_redcell.py  # benign CTF solve + patch-validate + 2 refusals; all predictions matched
```

## Ceiling (honesty + safety — non-waivable)
- **Refuse by default; the gate fails closed.** Authorized/defensive scope only (CTF, owned systems,
  scoped engagements, sandbox research, education). Out-of-scope → refuse with a reason.
- **The gate enforces the DECLARED policy — it is not a content classifier.** It is only as strong as the
  `requested_category` the caller/orchestrator supplies; it should sit behind the model's own policy
  reading, not replace it (audit caveat D3).
- **Sandboxed, owned targets only.** The sandbox is subprocess + CPU/time limits — it is not OS-level
  isolation; run only trusted-party build code (audit informational I1).
- **κ=1 is on the artifact's outcome**, not a general "secure" claim — absence of one firing PoC ≠ absence
  of vulnerabilities. Outputs are fixes + detections, **never deployable weapons**.
- A weapon ADDED = **capability EXPANSION, NOT a ≥10% promotion**. Ratchet stays OPEN at v3.
