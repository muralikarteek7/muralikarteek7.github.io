# GLOVES — SPEC (the box's actuation-safety gate)

*Kit item #2 (`Next/KIT_EXPANSION_PROPOSAL.md` §2). GLOVES is the EFFECTOR gate: the
hands that touch the external world (files, APIs, computer-use, email, deploys, money)
**safely**. It is not a weapon (produces no verified object) and not armor (armor judges
CLAIMs, not EFFECTS). Built BOX-style: gate FIRST, green before anything else counts.*

## The rule
ARMOR: *"abstain when uncertain about a CLAIM."*
GLOVES: **"require explicit authorization before an irreversible STATE CHANGE."**
A wrong claim can be retracted; a sent wire, a deleted table, a mass email cannot. The
new value is a **katastrophe-resistant effector layer** + an honest abstention on
unclassifiable actions — NOT a model-quality delta.

## The four action tiers (the tier sets the gate)
| tier | reversibility × blast-radius | examples | gate behavior |
|---|---|---|---|
| **AUTO** | R0 reversible, B-local | read, dry-run, scratch write, query | execute + log (κ=1 auto) |
| **CONFIRM** | R1–R2, or B-project/external | overwrite-with-backup, send ONE email, create ONE record | require a **token bound to exact params + expiry**, machine-checked (κ=1) |
| **STEP-UP** | R3 irreversible-broad, financial, admin | mass-send, deploy, delete, wire/transfer, change perms | **elevated** auth; agent **cannot self-approve** (κ=1 block without external grant) |
| **ABSTAIN** | unclassifiable, or unknown tool | anything whose class can't be read from the registry | **refuse + escalate**, never silent-pass |

Tier comes from the **frozen tool-risk registry** (`tool_risk_registry.py`), read from
the tool's declared schema — **never the model at runtime**. The LLM may RAISE a class,
never LOWER it. **Financial actions inherit the system rail: never execute a trade / move
money autonomously — `money.transfer` is STEP-UP and always routes to a human.**

## The κ=1 core (exact, frozen — `gloves_gate.py`)
1. **Token verification (κ=1 end-to-end):** a token `{action_hash, granter, scope,
   issued_ts, expiry, token_id, sig}`. The gate ALLOWs a CONFIRM/STEP-UP action **iff**:
   (i) the HMAC `sig` verifies against the **EXTERNAL** signing key, (ii)
   `hash(exact params) == action_hash` (no param drift), (iii) `now < expiry`, (iv) the
   token's `scope` tier-rank **covers** the action tier (a CONFIRM-scoped token presented
   for a STEP-UP action → REJECT), (v) if the token **attests a dry-run artifact**
   (`token.dry_run_artifact_hash` present), the action's declared `dry_run_artifact_hash`
   **matches** it (else REJECT — the κ=1 dry-run path, §2), (vi) for a non-idempotent action
   the `token_id` is **single-use** and unspent (replay → REJECT). Forgery / param-drift /
   stale / replay / scope-mismatch / artifact-mismatch → BLOCK with certainty. **Replay
   protection is self-contained:** a successful single-use verification marks the token spent
   **inside** `verify_token()` (default `commit_spend=True`), so even a caller that bypasses
   `verdict()` and calls `verify_token()` twice gets a `replay` REJECT on the second call
   (audit DEFECT-4); a pure pre-check passes `commit_spend=False` and is told the result is
   `…-UNCOMMITTED` (not yet replay-safe).
2. **Dry-run→commit binding:** an R1+ (`needs_dry_run`) commit must declare **both** a
   dry-run reference (`dry_run_hash`) **and** the produced-artifact hash
   (`dry_run_artifact_hash`) — **both required**; absent OR mismatched → BLOCK.
   *κ-honest label (audit DEFECT-1):* this is **κ=1 only on the token-attested path** —
   when the **EXTERNAL** authority signs the artifact hash into the token
   (`token.dry_run_artifact_hash`), the agent cannot forge it, so the commit is bound to a
   dry-run the authority saw. **Without** that token attestation, the gate's field-equality
   check is **protocol-level (ARMOR-class) only**: in a pure-software box the caller controls
   both fields, so it closes the "fake reference, artifact omitted" bypass but cannot prove a
   real dry-run ran. (Before the fix the artifact field was *optional* → any non-empty fake
   `dry_run_hash` false-accepted; that hole is closed.) Do **not** label the bare-field path
   κ=1 — true κ=1 needs either the token attestation or an infra-enforced artifact store the
   caller cannot write.
3. **Self-protection invariant (CVE-2025-53773):** any action targeting GLOVES' own
   config / allowlist / risk-registry / approval state, OR carrying an `autoApprove`/
   `disable_gate`/`lower_tier` param, is **hard-blocked + ALARMED regardless of token**.
   The param scan is **recursive** (nested dicts and list elements, any depth) and matches a
   downgrade signal as a **substring of either a KEY or a VALUE** — so
   `{'settings': {'autoApprove': True}}`, `{'data': [{'auto_approve': True}]}`, and a value
   like `'set_autoApprove_flag'` are all caught (audit DEFECT-2/DEFECT-3; previously only a
   top-level key/exact-value scan).
   *κ-honest label:* this is κ=1 **only if** the registry/ledger are infra-enforced
   read-only to the agent; in this pure-software box they are not → the rail is
   **ARMOR-class** (gate-level best-effort), labeled by `infra_check.py`, never silently
   upgraded.
4. **Reversibility/blast-radius lookup:** κ=1 **WITHIN** the frozen registry; κ<1 **ACROSS**
   registry population. An UNKNOWN/unregistered tool_id → **ABSTAIN (default-deny), always**.
5. **Append-only ledger:** every ALLOW writes `{tool, exact params, tier, token-id/policy,
   dry-run hash, running-blast-radius, ts}` BEFORE the call fires. *Infra limit: a
   pure-software box cannot self-guarantee this store is outside the agent's write scope —
   stated, not hidden (see `GROUNDING.md` + `infra_check.py`).*
6. **FAIL CLOSED:** the entire decision path is wrapped — any uncaught exception → BLOCK +
   ALARM, never ALLOW.
7. **Per-run blast-radius accumulator** (`BlastAccumulator`): records the running blast
   total so the silent-composition hole is visible. GLOVES is **per-action**; the
   composition is **G3's** job (it FLAGs over-budget, does not block — G3 not yet shipped).

## The router (`gloves_router.py`)
The κ-gate: *can the action's TIER be determined exactly from the registry?* If yes → the
tier sets the gate (AUTO pass-through / CONFIRM require-token / STEP-UP human-approval). If
not (unknown tool) → ABSTAIN. A read-only / no-side-effect call → no-op PASS-THROUGH. The
router decides routing; the FROZEN gate makes the ALLOW/BLOCK enforcement decision; the
router never lowers a tier (only escalates, e.g. self-protection → STEP-UP/BLOCK).

## The twelve gate-of-the-gate self-tests (non-waivable, `gloves_gate._selftest`)
(a) AUTO-allow R0/local read · (b) BLOCK STEP-UP with no token · (c) REJECT param-mismatched
token (send→A vs send→B) · (d) REJECT expired + replayed single-use token · (e) BLOCK +
ALARM the self-downgrade (autoApprove / registry edit / tier lower) · (f) ABSTAIN on
unclassifiable tier · (g) BLOCK unknown/unregistered tool (default-deny) · (h) BLOCK on any
injected exception (fail-closed) · (i) REJECT a tier-scope mismatch (CONFIRM token for a
STEP-UP action) · (j) BLOCK a commit with NO dry-run reference (absent hash) · (k) the SUITE
labels the self-protection rail κ=1 OR ARMOR-class per the infra write-scope check · (l) a
token forged with ONLY agent-available (in-context/in-repo) resources FAILS the gate.

**Cross-model audit regression tests (non-waivable, added after the Sonnet red-team):**
(m) **DEFECT-1** a `needs_dry_run` commit with a fake `dry_run_hash` and the artifact
**omitted** is now BLOCKED (was a false-accept) · (n) **DEFECT-1** when the external authority
**signs** the artifact hash into the token, a mismatched declared artifact is BLOCKED (the
κ=1 dry-run path), matching ALLOWs · (o) **DEFECT-2/DEFECT-3** a **nested** or
**value-substring** self-downgrade payload (`{'settings':{'autoApprove':True}}`,
`'set_disable_gate_flag'`) is BLOCK+ALARM at the gate · (p) **DEFECT-4** `verify_token()`
called twice directly REJECTs the second as `replay` (self-contained replay protection).
The registry self-test also reproduces the DEFECT-2/3 nested + value-substring cases.
`selftest_all.py` runs all four modules and exits non-zero on any failure.

## What GLOVES IS NOT (honest framing)
- **NOT a guarantee the action is wise** — it gates effects, not correctness of intent.
- **NOT trustworthy on the model's self-report of risk** — the LLM can NEVER declare an
  action LESS risky than its registered class (CVE-2025-53773).
- **NOT a defense against a COMPROMISED tool server** — supply-chain attestation is out of scope.
- **NOT semantic prompt-injection defense** — "is this output trying to trick me?" is SHIELD
  (kit #3). GLOVES assumes a (possibly-injected) decision to act was made and asks: *is this
  effect authorized and reversible-enough?* If SHIELD is absent, an injection that produces a
  **CONFIRM-tier** action could be auto-approved (STEP-UP/human is the backstop only for the
  top tier) — stated, not hidden (Finding 8).
- **NOT complete without G3** — a sequence of individually-small, individually-reversible
  authorized actions can COMPOSE into a large irreversible one. GLOVES gates each action; G3
  (compositional authorization, a running blast-radius budget) gates the composition.
- **NOT a capability boost** — a deterministic safety gate; the new value is the
  authorization certificate + the honest abstention.
