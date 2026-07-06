# GLOVES — GROUNDING (fetched, not asserted)

*Box rule: a load-bearing fact gets a fetched source, not memory. The two facts GLOVES is
built on were fetched on 2026-06-20 via WebSearch + WebFetch. Where a fetch is paraphrased
it is marked; exact strings are quoted.*

---

## 1. CVE-2025-53773 — the agent must not be able to modify its own safety controls

**The canonical proof for GLOVES' self-protection rail.** Fetched from Embrace The Red
(Johann Rehberger), the original disclosing researcher, and corroborated by NPAV / GBHackers
/ CybersecurityNews / Persistent-Security write-ups.

- **What it is:** a critical RCE in **GitHub Copilot / Visual Studio Code** via **prompt
  injection**. Injected instructions (in source comments, project files, GitHub issues, or
  web content) cause the AI agent to write a setting into a config file, **disabling its own
  confirmation controls**.
- **The exact payload (quoted):** the agent wrote **`"chat.tools.autoApprove": true`** into
  **`.vscode/settings.json`** (created if absent). The researcher called this **"YOLO mode,"**
  which *"disables all user confirmations, and we can run shell commands, browse the web, and
  more!"* — i.e. arbitrary terminal command execution without human approval, cross-platform
  (Windows/macOS/Linux), with invisible-Unicode stealth and an AI-worm propagation scenario.
- **Disclosure / patch:** reported to Microsoft **2025-06-29**; patched in the **August 2025
  Patch Tuesday** release.
- **The core lesson (quoted):** the design flaw was an agentic system able to *"modify its own
  configuration or update security-relevant settings"* — *"AI that can set its own permissions
  and configuration settings is wild!"*

**→ GLOVES countermeasure (`tool_risk_registry.SELF_PROTECT_PREFIXES` +
`SELF_DOWNGRADE_PARAM_KEYS`; `gloves_gate` self-protection rail, self-tests e & 6/6b):** any
action targeting GLOVES' own config / registry / ledger / approval state, OR carrying an
`autoApprove`/`disable_gate`/`lower_tier`/`yolo` param, is **hard-blocked + ALARMED regardless
of any token**. The single most important rail. **HONEST LIMIT (see §3):** a gate-level block
stops self-edit *actions routed through the gate*; it does NOT stop a process that writes the
registry/gate files directly — true enforcement needs infra GLOVES doesn't control.

Sources:
- https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/ (primary; quotes above fetched from here)
- https://blogs.npav.net/blogs/post/github-copilot-rce-vulnerability-cve-2025-53773-allows-remote-code-execution-via-prompt-injection
- https://gbhackers.com/github-copilot-rce-vulnerability/
- https://www.persistent-security.net/post/part-iii-vscode-copilot-wormable-command-execution-via-prompt-injection

---

## 2. OWASP AI Agent Security Cheat Sheet — the risk-tier model + approval integrity

**The grounding for GLOVES' four tiers, token binding, and fail-closed rule.** Fetched from
the OWASP Cheat Sheet Series.

- **The tier model (maps directly onto GLOVES' AUTO/CONFIRM/STEP-UP/ABSTAIN):**
  - **LOW (auto-approved):** read operations / safe queries (`search_documents`, `read_file`)
    → GLOVES **AUTO**.
  - **MEDIUM (confirmation required):** write operations / API calls (`write_file`)
    → GLOVES **CONFIRM**.
  - **HIGH (human approval):** financial / deletion / external communications (`send_email`,
    `execute_code`) → GLOVES **CONFIRM**/**STEP-UP** by blast-radius.
  - **CRITICAL (irreversible, multi-control):** `database_delete`, `transfer_funds`
    → GLOVES **STEP-UP** (step-up auth + binding controls).
- **Approval integrity (quoted):** *"Bind approval to the exact action. Include the actor,
  tool name, target resource, normalized parameters, timestamp, and expiry in the approval
  record."* — GLOVES' token binds `action_hash(tool_id, exact params)` + `expiry` + `scope`
  + `granter`.
- **Short-lived artifacts (quoted):** *"Use short-lived authorization artifacts and replay
  protection for irreversible operations."* — GLOVES tokens carry `expiry` + single-use
  `token_id` (replay protection for non-idempotent actions).
- **Step-up auth (quoted):** *"Require step-up authentication for critical actions such as
  account recovery, payment initiation, privilege changes, bulk deletion, or production
  deployment."* — GLOVES STEP-UP tier; agent cannot self-approve.
- **Fail closed (quoted):** *"Fail closed when risk classification, approval validation,
  policy lookup, or audit logging fails."* — GLOVES wraps the entire decision path; any
  exception → BLOCK (self-test h).
- **Allowlists, not wildcards (quoted):** the bad approach `"allowed_commands": "*"`; the
  good approach scoped allowlists `"allowed_paths": ["/app/reports/*"]`. GLOVES tiers by an
  explicit frozen registry, never a wildcard; unknown tool → ABSTAIN. **Rate limits /
  circuit breakers** bound resource use ("Denial of Wallet"). **OWASP LLM06 Excessive
  Agency** is the umbrella risk GLOVES exists to bound.

Sources:
- https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html (primary; quotes above fetched from here)
- https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/AI_Agent_Security_Cheat_Sheet.md

*(Optional papers named in the kickoff — arXiv 2601.08012 verifiably-safe tool use; the
Progent policy language — were NOT fetched, so they are NOT cited or relied upon. Honest
negative: not claimed.)*

---

## 3. INFRA REALITY CHECK — what is and is NOT enforceable here (not over-claimed)

- **Enforcement point:** in this box, tool/MCP/computer-use calls route through the harness,
  so GLOVES is a **pre-call shim** — `gloves_gate.verdict(action)` is intended to be called
  before any outward tool fires. That interception point is where GLOVES lives.
- **The honest tamper-resistance limit (machine-checked by `infra_check.py`):** a pure-software
  box run under a single uid **cannot self-guarantee** the risk-registry and ledger are outside
  the agent's write scope. `infra_check.write_scope_status()` tests this at runtime; in THIS
  setup the agent process CAN write its own `tool_risk_registry.py` / `gloves_gate.py` /
  ledger, so the self-protection rail is honestly labeled **ARMOR-class** (gate-level
  best-effort), **NOT κ=1**. The gate blocks self-edit *actions routed through it*, but a
  process writing the files directly bypasses the gate. **An audit log the agent can rewrite is
  not an audit log (CVE-2025-53773 again).**
- **True κ=1 enforcement** requires the registry/ledger be owned by a different uid / mounted
  read-only / fronted by a separate-process gate the agent cannot reach / enforced by the
  harness. Stated plainly; not claimed where not backed.

---

## 4. κ honesty (restated)
- token / param / expiry / single-use / scope + dry-run→commit checks: **κ=1 end-to-end**.
- reversibility-class LOOKUP: **κ=1 WITHIN the registry, κ<1 ACROSS its population** (unknown
  tool → ABSTAIN).
- self-protection rail: **κ=1 only if write-scope is infra-enforced, else ARMOR-class** (here:
  ARMOR-class, labeled).
- the risk-CLASSIFICATION boundary ("is this R2 or R3?"): **κ<1 → ABSTAIN**.
