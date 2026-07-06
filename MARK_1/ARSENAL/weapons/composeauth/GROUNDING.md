# COMPOSEAUTH (G3) — GROUNDING

*Load-bearing external facts the kickoff §4 names, FETCHED (not asserted from memory) on
2026-06-20 via WebFetch/WebSearch. Each claim carries its source + an exact quote. Where a
source does NOT support a claim, that is stated plainly (honesty rail). G3's NUMBERS
(thresholds, weights) are POLICY choices and are deliberately NOT grounded in any source —
they are owned by a human, not derived.*

---

## 1. OWASP LLM06:2025 — Excessive Agency (the scope-creep / compounding failure)

**Source:** OWASP GenAI / Top 10 for LLM Apps 2025 — LLM06:2025 Excessive Agency
`https://genai.owasp.org/llmrisk/llm062025-excessive-agency/` (fetched 2026-06-20).

- **Definition (exact quote):** "the vulnerability that enables damaging actions to be
  performed in response to unexpected, ambiguous or manipulated outputs from an LLM,
  regardless of what is causing the LLM to malfunction."
- **Three contributing factors (exact):** *Excessive Functionality* ("capabilities beyond
  what's needed"), *Excessive Permissions* ("more access rights than necessary on downstream
  systems"), and **Excessive Autonomy** — "Systems lack verification and approval mechanisms
  for high-impact actions." → G3 is exactly an *autonomy* control: a verification/approval
  mechanism that fires on the COMPOSITION.
- **Human-in-the-loop (exact quote):** the guidance recommends "human-in-the-loop control to
  require a human to approve high-impact actions before they are taken." → G3's HALT
  escalates to a human; ESCALATE raises the next action to STEP-UP (a human-grant tier).
- **Rate-limiting (exact quote):** rate-limiting can "reduce the number of undesirable
  actions that can take place within a given time period, increasing the opportunity to
  discover undesirable actions through monitoring." → motivates the `external_calls` /
  denial-of-wallet counter.

**HONEST NEGATIVE:** the LLM06 page **does not explicitly address the compounding effect of
repeated low-risk actions** (the salami / accumulator attack G3 is built for). The fetch
returned: "The document does not explicitly address compounding effects of repeated low-risk
actions." So the *named* OWASP risk that G3 maps to most cleanly is **Excessive Autonomy**
(missing approval mechanisms for high-impact actions) — and the compounding framing is G3's
own contribution / the kit's analysis, NOT an OWASP quote. Stated so we do not over-claim a
source we don't have.

---

## 2. OWASP LLM10:2025 — Unbounded Consumption / Denial of Wallet (DoW)

**Source:** OWASP GenAI — LLM10:2025 Unbounded Consumption
`https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/` (fetched 2026-06-20).

- **Definition (exact quote):** Unbounded Consumption occurs "when a Large Language Model
  (LLM) application allows users to conduct excessive and uncontrolled inferences, leading to
  risks such as denial of service (DoS), economic losses, model theft, and service
  degradation."
- **Denial of Wallet (exact quote, named explicitly):** "By initiating a high volume of
  operations, attackers exploit the cost-per-use model of cloud-based AI services, leading to
  unsustainable financial burdens on the provider and risking financial ruin." → motivates
  G3's `external_calls` rate/volume counter and the `financial` counter.
- **Mitigations (exact quotes):** "Apply rate limiting and user quotas to restrict the number
  of requests a single source entity can make in a given time period"; "Implement
  restrictions on the number of queued actions and total actions, while incorporating dynamic
  scaling." → G3 is precisely a **restriction on TOTAL actions / total committed effect** per
  session.

**HONEST NEGATIVE:** the LLM10 page "does not explicitly mention cumulative token budgets,
spend tracking, or spending quotas as distinct mitigation strategies." Its closest support is
"restrictions on the number of queued actions and **total actions**." So G3's *cumulative
per-class spend budget* is supported by the "total actions" restriction language and by the
Agent Security cheat sheet (§3 below), NOT by an LLM10 "spend budget" quote.

---

## 3. OWASP AI Agent Security Cheat Sheet — session spend tracking + separate enforcement

**Source:** OWASP Cheat Sheet Series — AI Agent Security
`https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html`
(fetched 2026-06-20).

- **Denial of Wallet (exact quote):** "Attacks causing excessive API/compute costs through
  unbounded agent loops."
- **Per-session spend tracking (exact quotes):** under monitoring it recommends tracking
  "token usage and costs per session/user" and lists an anomaly threshold example
  `"cost_per_session_usd": 10.0`. → direct support for G3's **per-session financial budget**.
- **Human-in-the-loop (exact quote):** "Require explicit approval for high-impact or
  irreversible actions." → G3's destruction-HALT and financial-HALT escalate to a human.
- **Separate decision from execution (exact quote):** "Separate decision-making from
  execution. The agent can propose an action, but a policy service or execution component
  should independently validate scope, privilege, and approval state before execution." →
  G3 is exactly such an independent policy component sitting between the agent's proposed
  action stream and execution; the FROZEN gate (not the model) decides OK/ESCALATE/HALT.
- **Rate limiting (exact quote):** a rate-limiter example "RateLimiter(max_calls=100,
  window_seconds=60)" and "Enforce token, cost, retry, and tool-chain limits."

**HONEST NEGATIVE:** the cheat sheet "doesn't explicitly address scope creep from repeated
small approvals." Its nearest item is "Decision and Approval Manipulation" — "Attackers
influencing risk scores, model confidence, or approval thresholds to bypass safeguards" —
which is adjacent (G3's self-protection-by-design: thresholds are frozen policy the agent
can't lower) but is NOT the compounding-micro-authorization framing. Stated, not stretched.

---

## 4. SUMMARY — what is grounded vs what is G3's own framing

| claim | grounded? | source |
|---|---|---|
| missing approval mechanisms for high-impact actions is a named OWASP risk | YES | LLM06 (Excessive Autonomy) |
| human-in-the-loop for high-impact / irreversible actions | YES (exact quote) | LLM06 + Agent Cheat Sheet |
| Denial-of-Wallet is a named OWASP attack | YES (exact quote) | LLM10 |
| per-session cost/spend tracking is recommended | YES (exact quote) | Agent Cheat Sheet |
| separate policy component validates before execution | YES (exact quote) | Agent Cheat Sheet |
| restrict TOTAL actions per session | YES (exact quote) | LLM10 |
| the SALAMI / compounding-micro-authorization framing | **NO explicit source** | G3 / kit analysis |
| the specific threshold + weight NUMBERS | **N/A — POLICY, not derived** | human-owned choice |

No fetch failed. All three pages returned content; the honest negatives above are
genuine "the source does not say X" results, not fetch errors.
