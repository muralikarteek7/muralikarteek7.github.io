# GLOVES — the box's actuation-safety gate

**The hands that touch the external world, SAFELY.** GLOVES is a deterministic **pre-call
interceptor** on every tool / MCP / computer-use call with a real-world side effect. It
classifies the action by **reversibility × blast-radius** (from a frozen tool-risk registry,
not the model) and either auto-executes, demands a machine-checked authorization token bound
to the exact parameters + an expiry, routes to a human, or **abstains**. It lets the box
**ACT** only when the action is reversible-enough or carries a valid token — and it
hard-blocks any attempt by the agent to lower its own risk class or edit its own controls.

This is **kit item #2** and (per the red-team) the only genuinely-*new* capability in the
kit: the box today reasons and produces artifacts; GLOVES is the safety layer for the moment
it reaches out to act.

## Files
- `tool_risk_registry.py` — the **frozen** tool-risk registry (tiers, reversibility,
  blast-radius, self-protection surface). The tier is read from here, never the model.
- `gloves_gate.py` — the **frozen actuation gate**: `verdict(action) → {tier, decision,
  alarm, reason, blast_units, ledger}`. Token/param/expiry/single-use/scope verification,
  dry-run→commit binding, self-protection rail, fail-closed, blast accumulator. Houses the
  **12 non-waivable gate-of-the-gate self-tests** (a..l).
- `gloves_router.py` — routes an action to its gate behavior (`_selftest` included).
- `infra_check.py` — honestly labels the self-protection rail κ=1 vs ARMOR-class by testing
  the registry/ledger write-scope.
- `selftest_all.py` — runs every self-test; **exits non-zero on any failure**.
- `demo_actuation/` — committed `PREDICTION.md`, `run_demo.py` (proven on a real temp file),
  `results.json`.
- `SPEC.md`, `GROUNDING.md` (CVE-2025-53773 + OWASP, fetched), `AUDIT.md`.

## Run it
```
cd MARK_1/ARSENAL/weapons/gloves
python3 selftest_all.py            # the gate-of-the-gate; must exit 0 before trusting GLOVES
python3 demo_actuation/run_demo.py # 9 cases + side-effect ground truth on a real temp file
```
Both exit 0. Self-test status (verified 2026-06-20): **17/17 demo predictions confirmed by
the machine judge; all 12 gate self-tests (a..l) green.** No third-party packages required
(stdlib only: `hashlib`, `hmac`, `json`, `tempfile`).

## The one-line test of success
*GLOVES lets the box ACT on the world only when the action is reversible-enough or carries a
machine-checked authorization token bound to its exact parameters and unexpired; it
hard-blocks any attempt by the agent to lower its own risk class or edit its own controls
(CVE-2025-53773); it routes irreversible/broad/financial actions to a human who must approve,
and ABSTAINS — never silently acts — on anything it cannot classify; and it states plainly
where its tamper-resistance depends on infra it doesn't control.*

## The honest ceiling (do not over-claim)
- **GLOVES gates EFFECTS, not wisdom.** It bounds catastrophe by construction; it does NOT
  confer judgment. A correctly-authorized action can still be a mistake.
- **The signing key IS the security boundary** — it must be EXTERNAL (a secret store, the
  harness), not in-process, not in the repo, not in the agent's context. A token the agent
  can mint is no token (self-test l).
- **Tamper-resistance is infra-limited.** In this pure-software single-uid box the agent can
  write its own registry/ledger, so the self-protection rail is **ARMOR-class** (gate-level
  best-effort), honestly labeled by `infra_check.py` — NOT κ=1. True enforcement needs
  fs-perms / a separate process / the harness. An audit log the agent can rewrite is not an
  audit log.
- **Not complete without G3.** GLOVES is **per-action**; a sequence of individually-safe
  actions can COMPOSE into an unsafe one. G3 (compositional authorization, a running
  blast-radius budget) gates the composition — not yet shipped. GLOVES emits the per-run
  blast accumulator so the hole is visible and G3 has data when it lands.
- **Not an injection detector** (that is SHIELD, kit #3). A token bound to attacker-crafted
  params is still a valid token; if SHIELD is absent, an injection that produces a
  **CONFIRM**-tier action could be auto-approved (STEP-UP/human is the backstop only for the
  top tier).
- **Not a defense against a compromised tool server** (supply-chain attestation, out of scope).
- **κ honesty:** token/param/expiry/single-use/scope are **κ=1**. **Dry-run→commit is κ=1
  ONLY on the token-attested path** (the external authority signs the artifact hash into the
  token — the agent cannot forge it); the bare two-field equality check is **protocol-level
  (ARMOR-class)** in a pure-software box where the caller controls both fields — it closes the
  "fake reference, artifact omitted" false-accept the cross-model audit found (DEFECT-1) but
  does not by itself prove a real dry-run ran. The class lookup is **κ=1 within the registry,
  κ<1 across population** (unknown tool → ABSTAIN); the classification boundary is **κ<1 →
  ABSTAIN**. The self-protection param scan is **recursive + key/value-substring** (DEFECT-2/3);
  `verify_token()` replay protection is **self-contained** (DEFECT-4).

## Status
GLOVES ADDED = a **capability EXPANSION** (the box can now ACT on the world, safely-gated),
**NOT a ≥10% promotion** (no shared arena; it is a deterministic safety gate, not a
model-quality delta). Pairs with G3.
