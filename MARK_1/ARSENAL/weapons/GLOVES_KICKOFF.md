# KICKOFF — build the KIT piece: GLOVES (safe actuation) for the v5 box
*Paste everything below into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written
2026-06-20. GLOVES is item **#2** of the KIT-EXPANSION plan (`Next/KIT_EXPANSION_PROPOSAL.md`, §2) — and the
red-team's verdict was that it is **the ONLY genuinely-new capability** in the kit: the BOX today *reasons and
produces artifacts*; it does not *act on the world*. GLOVES is the safety layer for the moment it reaches out.*

*Hardened 2026-06-20 after an independent Sonnet audit (verdict READY-WITH-FIXES; one BROKEN finding fixed): the
fixes are folded in — unknown tool_id → default-DENY (§1, §2, self-test g); fail-closed on any exception
(self-test h); κ=1 honestly bounded to "within the registry" (§1, §6); the signing key is the security boundary
(self-test l); self-protection is κ=1 only if write-scope is infra-enforced (self-test k); single-use + tier-scope
tokens; per-run blast-radius accumulator until G3; and the injection-initiated-CONFIRM gap stated (§1).*

---

You are building **GLOVES**, the box's **actuation-safety gate**: the hands that touch the external world (APIs,
computer-use, files, email, deploys, money) **safely**. ARMOR's rule is *"abstain when uncertain about a CLAIM."*
Actuation needs a **different** rule — *"require explicit authorization before an irreversible STATE CHANGE"* —
because outward, irreversible actions have an asymmetric cost ARMOR was never built for (a wrong claim can be
retracted; a sent wire, a deleted table, a mass email cannot). Work BOX-style: plan → produce → **verify
INDEPENDENTLY** → ground → be honest; **no win without proof; the gate must be able to FAIL (block a bad action)
or it is not a gate.**

## 0. ORIENT — read first (in order)
`CLAUDE.md`, `RESUME.md`, **`Next/KIT_EXPANSION_PROPOSAL.md`** (§0 the honest goal, §2 GLOVES, §5 G3 the
compositional-authorization gap GLOVES pairs with, §7 build order), **`Next/BOX_V5.md`** (the κ-router — GLOVES'
token/param/expiry/reversibility checks are **κ=1**; the risk-*classification boundary* is κ<1 → abstain), the
registry `Next/WEAPON_REGISTRY.json` (add an entry). Then the two cleanest weapons as **format templates**
(`symbolica/`, `optima/` — `SPEC.md`, the frozen gate + `selftest_all.py`, the router, `demo_*/`, `AUDIT.md`).
GLOVES is **not** a weapon (it produces no verified object) and **not** armor (armor judges claims, not effects) —
it is a new **EFFECTOR gate** that sits in front of every outward tool call.

## 1. THE HONEST FRAMING — what GLOVES IS and IS NOT (do not skip)
**IS:** a **pre-call interceptor** on every tool/MCP/computer-use call that has a real-world side effect. It
classifies the action by **reversibility × blast-radius**, and — based on that class — either auto-executes,
demands a **machine-checked confirmation token bound to the exact parameters + an expiry**, demands **step-up
authorization**, or **abstains/escalates**. The genuinely-new value is **a katastrophe-resistant effector layer**,
not a model-quality delta.

**The κ=1 core (exact and buildable as a frozen gate — with one honest boundary, per audit Finding 2):**
- **token verification (κ=1 end-to-end):** a signed token whose payload must hash-match the exact call parameters,
  be unexpired, be **single-use** for non-idempotent actions, and carry a **tier-scope that covers the action's
  classified tier** (a CONFIRM-scoped token presented for a STEP-UP action → REJECT). Forgery / param-drift / stale
  / replay / scope-mismatch → rejected with certainty. **The signing authority is EXTERNAL** — the key is not
  in-process, not in the repo, not readable from the agent's context (if the agent can read the key, this collapses
  to κ=0 — see self-test).
- **dry-run→commit binding (κ=1):** an R1+ commit must reference the dry-run artifact's hash; a commit with an
  absent OR mismatched dry-run hash → BLOCK.
- **self-protection invariant (κ=1 *gate-level* check; infra-dependent for true enforcement — Finding 3):** the
  action set "modify GLOVES' own config / allowlist / risk-registry / approval settings" is **hard-blocked**
  regardless of token (the CVE-2025-53773 countermeasure, §4). *Honest limit: a gate-level block is breakable if
  the agent can write the registry/gate code itself — true enforcement needs the registry/ledger to be read-only
  to the agent process, which a pure-software box cannot self-guarantee. The gate MUST self-test that write-scope
  before declaring healthy, else this rail is labeled ARMOR-class, not κ=1 (§3, §6).*
- **reversibility/blast-radius lookup (κ=1 WITHIN the registry; κ<1 ACROSS registry population — Finding 2):** the
  class is read from a frozen tool-risk registry, NOT the model. The *lookup* is exact; but it is only as honest as
  the registry entry — a tool that under-declares its own risk (or is absent) is the real attack surface. So:
  **an UNKNOWN/unregistered tool_id → ABSTAIN (default-deny), always** (audit Finding 1, BROKEN-if-omitted); and the
  κ=1 label applies to the mechanical lookup, not to the trustworthiness of the registry entry.

**IS NOT:**
- **NOT a guarantee the action is *wise*.** GLOVES gates *effects*, not correctness of intent. A correctly-authorized
  action can still be a mistake. It bounds catastrophe; it does not confer judgment.
- **NOT trustworthy on the model's self-report of risk.** **The LLM can NEVER declare an action LESS risky than its
  registered class.** Risk class comes from the tool's *declared schema*, not the model at runtime (CVE-2025-53773:
  an agent set `autoApprove:true` in its own settings to disable its gate — the agent must not be able to downgrade
  its own controls).
- **NOT a defense against a COMPROMISED tool server.** A permitted tool whose backend is malicious is out of scope —
  GLOVES limits *which* tools and *what blast radius*, not server integrity (that's a supply-chain attestation
  problem). Stated, not hidden.
- **NOT semantic prompt-injection defense.** "Is this tool *output* trying to trick me into acting?" is the SHIELD
  untrusted-output rail (kit item #3), not GLOVES. GLOVES assumes a (possibly-injected) decision to act has been
  made and asks: *is this effect authorized and reversible-enough to allow?*
- **NOT complete without G3.** A sequence of individually-small, individually-reversible authorized actions can
  COMPOSE into a large irreversible one (the "galaxy-brained" failure). GLOVES gates each action; **G3
  (compositional authorization, a running blast-radius budget) gates the composition.** Until G3 ships, GLOVES MUST
  still emit a **per-run running blast-radius accumulator** in the ledger (Finding 1c) so the silent-composition
  hole is visible and G3 has data when it lands.
- **NOT an injection detector.** If the *decision* to act was injection-driven, the action's params (and any token
  bound to them) are injection-driven too — a token bound to attacker-crafted params is still a valid token. GLOVES
  does NOT detect injection-origin (that is SHIELD). **If SHIELD is absent, an injection that produces a CONFIRM-tier
  action could be auto-approved** — STEP-UP (human) is the backstop for the highest tier, but CONFIRM is not (Finding 8).
- **NOT a capability boost.** It's a deterministic safety gate; the new value is the authorization certificate +
  the honest abstention on unclassifiable actions.

## 2. THE FOUR ACTION TIERS (map to the κ-router; the tier sets the gate)
| tier | reversibility × blast-radius | examples | gate behavior |
|---|---|---|---|
| **AUTO** | R0 reversible, B-local | read, dry-run, local scratch write, query | execute + log (κ=1 auto) |
| **CONFIRM** | R1–R2, or B-project/B-external | overwrite-with-backup, send ONE email, create ONE record | require a **token bound to exact params + expiry**, machine-checked (κ=1) |
| **STEP-UP** | R3 irreversible-broad, financial, admin | mass-send, deploy, delete, wire/transfer, change perms | **elevated** auth; the agent **cannot self-approve** (κ=1 block without external grant) |
| **ABSTAIN/DECLINE** | unclassifiable, or irreversible+broad without authorization | anything whose class can't be determined from schema | **refuse + escalate**, never silent-pass (the κ=0 boundary → abstain) |

**Financial actions inherit the system rail:** never execute a trade / move money / place an order on the user's
behalf — STEP-UP routes to the human, always (see the computer-use guidance already in the box).

## 3. THE KEY ENGINEERING PROBLEM — the gate + the gate-of-the-gate, built FIRST
Build the **frozen actuation gate FIRST**, self-tests green before any action is ever allowed:
1. **`gloves_gate.verdict(action) -> {AUTO|CONFIRM|STEP-UP|ABSTAIN}` + an enforcement decision** `{ALLOW|BLOCK}`.
   Inputs: the action's declared tool-id + parameters + an optional confirmation token. The gate reads the
   reversibility/blast-radius from a **frozen tool-risk registry** (not the model).
2. **Token format + verification (κ=1):** a token is `{action_hash, granter, scope, issued_ts, expiry}` signed by
   an authority OUTSIDE the agent. The gate ALLOWs a CONFIRM/STEP-UP action **iff** `hash(exact params) ==
   action_hash` AND `now < expiry` AND scope covers the tier. Param drift, forgery, replay, expiry → BLOCK.
3. **Dry-run→commit (κ=1 structure):** R1+ actions must present a dry-run artifact; the commit references its hash;
   a commit whose preview-hash is absent or mismatched → BLOCK.
4. **Self-protection invariant (κ=1):** any action targeting GLOVES' own config / allowlist / risk-registry /
   approval state → **BLOCK unconditionally + ALARM** (no token overrides it). This is the CVE-2025-53773 rail.
5. **Append-only actuation ledger:** every ALLOW writes `{tool, exact params, tier, token-id or policy-rule,
   dry-run hash, running-blast-radius, result, ts}` BEFORE the call fires, **targeted at** a store the agent cannot
   rewrite — *conditional on §4's infra limit: a pure-software box cannot self-guarantee this; an audit log the
   agent can rewrite is not an audit log. State which holds in the actual deployment.*
6. **FAIL CLOSED (Finding 4):** the entire decision path is wrapped so that **any uncaught exception → BLOCK +
   ALARM, never ALLOW** (a registry-read failure, a hash/lib crash, a malformed param must deny, not pass).

**Gate-of-the-gate self-tests (non-waivable, see `symbolica/selftest_all.py` for the pattern). The gate must:**
(a) **AUTO-allow** an R0/B-local read with no friction;
(b) **BLOCK** an R3/irreversible action carrying no token;
(c) **REJECT a parameter-mismatched token** (issued for `send to A`, call is `send to B`) — stops bait-and-switch;
(d) **REJECT an expired/replayed token** (and a single-use token presented twice for a non-idempotent action);
(e) **BLOCK + ALARM the self-downgrade** (sets `autoApprove=true` / edits the risk registry / lowers its own tier —
    the CVE-2025-53773 attack);
(f) **ABSTAIN (not silent-pass)** on an action whose tier can't be determined from schema;
(g) **BLOCK an UNKNOWN/unregistered tool_id** (default-deny — the audit's BROKEN finding);
(h) **BLOCK on any injected exception** in the gate's own path (fail-closed — Finding 4);
(i) **REJECT a tier-scope mismatch** (a CONFIRM-scoped token presented for a STEP-UP action — Finding 6c);
(j) **BLOCK a commit with NO dry-run reference** (absent hash, not just mismatched — Finding 6e);
(k) **the self-test SUITE itself fails** if the gate cannot confirm the risk-registry/ledger are read-only to the
    agent process (Finding 3) — OR the self-protection rail is downgraded to ARMOR-class, labeled, not κ=1;
(l) **a token forged using ONLY resources available to the agent** (e.g. an in-context/in-repo key) must FAIL to
    pass the gate (Finding 7) — if it passes, the signing architecture is broken.
A gate that passes all twelve — especially (c), (e), (g), (h), (l) — is trustworthy. (The original six were
necessary but NOT sufficient for a security-critical gate; the audit added g–l.)

## 4. INFRA REALITY CHECK + GROUND-BY-FETCH (don't assert)
- **Confirm the enforcement point:** in this box, tool/MCP/computer-use calls route through the harness, so GLOVES
  is a **pre-call shim**. Confirm where that interception can live. **Honest infra limit:** a pure-software box
  cannot, by itself, guarantee the ledger and risk-registry are outside the agent's write scope — that
  tamper-resistance needs an enforcement layer the agent cannot reach (filesystem perms / a separate process /
  the harness). State plainly what is and isn't enforceable in the current setup; do not claim tamper-resistance
  you can't back.
- **FETCH-confirm the load-bearing facts (cite in `GROUNDING.md`):** **CVE-2025-53773** (GitHub Copilot/VS Code RCE
  via prompt injection — the agent wrote `"chat.tools.autoApprove": true` into `.vscode/settings.json` to disable
  its own confirmation, patched Aug 2025) — the canonical proof that *the agent must not be able to modify its own
  safety controls*. The **OWASP AI Agent Security Cheat-Sheet** risk-tier model (auto-approve low / queue medium /
  step-up auth high-critical; approval bound to exact params + expiry; allowlists not wildcards; rate limits /
  circuit breakers). OWASP **LLM06 Excessive Agency**. (Optional: arXiv 2601.08012 verifiably-safe tool use;
  Progent policy language — least-privilege tool invocation. Don't claim a paper you didn't fetch.)

## 5. TO-DOs / STEPS (box order)
1. **PLAN:** `weapons/gloves/SPEC.md` — the four tiers, the κ=1 token/param/expiry/reversibility checks, the
   self-protection invariant, the κ<1 boundary → abstain rule, the router (`gloves_router.py`: schema-classifiable +
   reversible → AUTO; needs-confirmation → CONFIRM; irreversible/broad/financial → STEP-UP; unclassifiable →
   ABSTAIN; a read-only / no-side-effect call → GLOVES is a no-op pass-through). **GROUND** CVE-2025-53773 + the
   OWASP tier model in `GROUNDING.md`.
2. **BUILD THE GATE FIRST** (§3): `gloves_gate.*` + `selftest_all.py` with the six reject/allow self-tests. **Green
   before any action is allowed.** Include a small **frozen tool-risk registry** (a few example tools across all
   four tiers) so the tiering is itself testable.
3. **WIRE IT (carefully):** make GLOVES a pre-call shim for ONE real low-risk tool end-to-end (e.g. a file write):
   AUTO for a scratch read, CONFIRM-with-token for an overwrite, dry-run→commit, ledger entry. **Do not wire it to
   anything irreversible/outward in the demo** — prove the gate on safe surfaces.
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` BEFORE running): (i) an R0 read auto-allowed +
   logged; (ii) an R2 overwrite BLOCKED without a token, ALLOWED with a valid param-bound token, BLOCKED again when
   the params drift; (iii) an expired token rejected; (iv) the **self-downgrade attack BLOCKED + ALARMED** (an
   action that tries to set `autoApprove=true` / edit the risk registry); (v) an unclassifiable action ABSTAINED.
   Predict each verdict before running; the gate is the judge.
5. **VERIFY INDEPENDENTLY:** a cross-model audit (Sonnet/Haiku ≠ the Opus generator; **never Opus-audits-Opus**;
   Fable inactive) that (a) tries to **forge/replay/param-drift a token** past the gate with its own code, (b) tries
   the **self-downgrade / settings-edit** attack from a different angle, (c) checks no κ<1 boundary call is
   silently classified instead of abstaining, (d) audits the honest infra-limit wording (is tamper-resistance
   over-claimed?). Fix what's caught.
6. **REGISTER:** add **GLOVES** to `Next/WEAPON_REGISTRY.json` (an EFFECTOR-gate entry, κ=1 core / κ<1 boundary),
   `Next/BOX_V5.md` (a new kit layer: ARMOR + WEAPONS + HELMET + **GLOVES effector gate** — note it pairs with G3),
   `HELMET/registry.json` (a cross-cutting actuation facility every department calls before acting). Honest
   `EVOLUTION_LOG` entry: **GLOVES ADDED = capability EXPANSION (the box can now ACT on the world, safely-gated),
   NOT a ≥10% promotion.** Update `KIT_EXPANSION_PROPOSAL.md` §7 + `WEAPONS_BACKLOG.md`.

## 6. HONESTY RAILS (non-waivable, specific to GLOVES)
- **The agent cannot lower its own risk class or edit its own controls** — hard-blocked + alarmed, no token
  overrides (CVE-2025-53773). The single most important rail.
- **Risk class comes from the tool's declared schema, never the model's runtime word** — the LLM may raise a class,
  never lower it.
- **Irreversible/broad/financial ⇒ a human, always.** Never execute a trade / transfer / mass-action autonomously.
- **Unclassifiable ⇒ ABSTAIN, never silent-pass** — an action whose tier can't be determined is refused + escalated.
- **κ honesty (restated per audit Finding 2):** token/param/expiry/single-use/scope + dry-run→commit checks are
  **κ=1 end-to-end**; the **reversibility-class lookup is κ=1 ONLY within the registry, κ<1 across registry
  population** (an absent or under-declared tool is the attack surface → unknown tool_id ABSTAINS); the
  **self-protection rail is κ=1 only if registry/ledger write-scope is infra-enforced, else ARMOR-class** (Finding 3);
  the risk-classification *boundary* ("is this R2 or R3?") is κ<1 → abstain.
- **The signing key IS the security boundary** — external, not in-process, not in the repo, not in the agent's
  context. A token the agent can mint itself is no token (Finding 7; self-test (l)).
- **Fail closed:** any exception or unknown tool → BLOCK, never ALLOW (Finding 4, 1).
- **State the infra limit:** if the ledger/registry tamper-resistance is not actually enforceable in the current
  software setup, SAY SO — an audit log the agent can rewrite is not an audit log (CVE-2025-53773 again).
- **GLOVES is per-action; the composition is G3's job** — every run flags that a sequence of safe actions can still
  compose into an unsafe one until G3 ships.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/gloves/` — `SPEC.md`, `GROUNDING.md` (CVE-2025-53773 + OWASP tier model + the honest
infra-limit), the frozen `gloves_gate.*` + `selftest_all.py`, `gloves_router.py`, the frozen tool-risk registry,
`demo_*/` (committed predictions + the allow/block/abstain log + the blocked self-downgrade exhibit), `AUDIT.md`
(cross-model red-team incl. token forgery/replay/param-drift + self-downgrade attacks), `README.md` (what it is +
honest ceiling: bounds catastrophe, does not confer judgment, not complete without G3, infra-limited
tamper-resistance). Registration in `Next/WEAPON_REGISTRY.json` + `Next/BOX_V5.md` + `HELMET/registry.json` +
honest `EVOLUTION_LOG`; `KIT_EXPANSION_PROPOSAL.md` §7 + `WEAPONS_BACKLOG.md` updated.

## 8. STAFF THE TEAM (v4 ladder; Fable INACTIVE → its slots on Opus, flag low confidence)
- **Gate + registry** = code tier writes the tiering / token-verification / dry-run-commit / ledger (deterministic —
  the *token+param+expiry match*, not a model, is the ALLOW).
- **Library** = cheap model: fetch CVE-2025-53773 + the OWASP AI-Agent Security tier model.
- **Auditor** = a model ≠ the generator (Sonnet/Haiku; never Opus-audits-Opus) — forges/replays/param-drifts tokens,
  runs the self-downgrade attack, polices the abstain-on-boundary and the infra-limit honesty.

## 9. THE ONE-LINE TEST OF SUCCESS
**"GLOVES lets the box ACT on the world only when the action is reversible-enough or carries a machine-checked
authorization token bound to its exact parameters and unexpired; it hard-blocks any attempt by the agent to lower
its own risk class or edit its own controls (CVE-2025-53773); it routes irreversible/broad/financial actions to a
human who must approve, and ABSTAINS — never silently acts — on anything it cannot classify; and it states plainly
where its tamper-resistance depends on infra it doesn't control."** Bounds catastrophe by construction; honest that
it gates effects, not wisdom — and not complete until G3 gates the composition.
