# SHIELD — GROUNDING (fetched sources + infra check)
*Load-bearing facts are FETCHED here (WebFetch/WebSearch, 2026-06-20), not asserted from memory. Box
rule: ground, don't assert. Where a fetch did not yield the exact figure the kickoff named, that is
stated as a provenance gap — not papered over.*

## Infra reality check (run 2026-06-20, this machine)
```
python3 3.9.6
hashlib, hmac, secrets, base64, json   — Python stdlib, all present (no pip install)
cryptography 48.0.0                     — present, but NOT used: HMAC-SHA256 from stdlib hmac suffices
```
SHIELD's κ=1 rails need only: a deterministic origin label, typed input slots, an allowlist match, and
a keyed hash (HMAC-SHA256). All are stdlib. **No `pip install` was performed.** Signing uses a
symmetric HMAC key — honest scope: this authenticates capes/certs against an attacker WITHOUT the key
(the box's own runtime holds it); it is NOT public-key non-repudiation. For the threat model here
(attacker-controlled *input* cannot forge a cape/cert it never had the key for) HMAC is sufficient and
is the standard primitive.

## §A — OWASP LLM01:2025 Prompt Injection (the PROVENANCE-LABEL + ABSTAIN rails)
**Fetched:** genai.owasp.org/llmrisk/llm01-prompt-injection/ , 2026-06-20.
- Definition (verbatim): *"A Prompt Injection Vulnerability occurs when user prompts alter the LLM's
  behavior or output in unintended ways."*
- **Two types** (verbatim): **Direct** — *"a user's prompt directly modifies model behavior."*
  **Indirect** — *"an LLM processes input from external sources like websites or files, where hidden
  content alters behavior unexpectedly."* (This is the ENV tier SHIELD labels and scans.)
- Mitigation that SHIELD's PROVENANCE-LABEL rail implements (verbatim): *"Separate and clearly denote
  untrusted content to limit its influence on user prompts."* and *"Provide specific instructions about
  the model's role, capabilities, and limitations within the system prompt."*
- **Honest read:** OWASP lists these as *mitigations*, not solutions — segregation reduces influence, it
  does not prove obedience. This is exactly why the label is κ=1 but obedience is κ<1 in SHIELD.

## §B — OWASP LLM06:2025 Excessive Agency (the TOOL-CAPE rail)
**Fetched:** genai.owasp.org/llmrisk/llm062025-excessive-agency/ , 2026-06-20.
- Root causes (verbatim): **1. Excessive functionality** — *"Extensions contain capabilities beyond
  operational needs"*; **2. Excessive permissions** — *"Systems access broader authority than required"*;
  **3. Excessive autonomy** — *"Lack of human oversight on high-impact actions."*
- Prevention SHIELD's TOOL-CAPE implements (verbatim): *"Limit the extensions that LLM agents are
  allowed to call to only the minimum necessary"*, *"Limit the permissions ... to the minimum"*, and
  crucially *"authorization in downstream systems rather than relying on an LLM to decide if an action
  is allowed."* — TOOL-CAPE is exactly this: a signed allowlist the **model cannot self-elevate**;
  the structure, not the model, is the authorization.
- OWASP also notes monitoring/logging *"cannot prevent the vulnerability but can mitigate damage"* —
  matches SHIELD's honest framing (the cape blocks the unpermitted tool; it cannot fix a compromised
  permitted server).

## §C — NIST AI 100-2 E2025 + the empirical injection ceiling (the honest "not a wall")
**Fetched/searched:** NIST AI 100-2 E2025 (csrc.nist.gov/pubs/ai/100/2/e2025/final; OECD.AI &
Adversa.ai summaries) + a meta-analysis aggregation (sqmagazine.co.uk/prompt-injection-statistics/,
which cites the study range), 2026-06-20.
- **NIST AI 100-2 E2025** (published 2025-03-24) newly defines **Indirect Prompt Injection** as
  *"sophisticated attacks that exploit external or indirect channels to manipulate GenAI behaviors"*
  and adds a dedicated treatment of **autonomous AI agent** vulnerabilities (absent from the 2023
  edition): indirect injection, memory poisoning, and tool/supply-chain attacks on agents.
- **The honest ceiling (the load-bearing number).** The exact phrasing the kickoff cited — *"~80%
  attacker success at 25 tries"* — I could **NOT confirm as a single verbatim NIST line** from the
  fetched summary pages (the full PDF body was not machine-readable through WebFetch; the CSRC/OECD/
  Adversa pages summarize scope, not success-rate tables). **PROVENANCE GAP, stated honestly.** What I
  DID ground from fetched aggregations of peer-reviewed studies:
  - *"Prompt injection attacks achieve success rates between **50% and 84% across common LLMs**."*
  - *"Advanced adaptive attacks exceed **85% success rates in controlled environments**."*
  - *"success rates can climb to **over 90% in naive model deployments**."*
  - Multi-turn / repeated attempts: *"improve effectiveness by **20–30% compared to single prompts**"*
    (consistent with "more tries → higher success" — the spirit of the 25-tries figure).
  - Agent tool-misuse via injection: *"unauthorized actions in **31%** of evaluated agent scenarios"*;
    autonomous API-calling agents *"up to **2.5x** higher risk exposure than standalone models."*
  - **The decisive qualitative claim**, fetched verbatim: experts warn prompt injection may be
    *"unlikely to ever be fully solved."*
- **Conclusion SHIELD states on every run:** no machine-checkable defense exists for semantic injection
  woven through a long document; the documented attacker success is high (50–90%+ depending on
  setting). SHIELD therefore makes the EXACT rails exact and ABSTAINS on the κ=0 part — it never claims
  a complete defense. **The "~80% / 25 tries" exact figure is reported as an unverified citation; the
  50–84%+ range is the grounded substitute.**

## §D — MCP tool-description poisoning + CVE-2025-53773 (TOOL-CAPE + VERIFIER TAINT-RAIL motivation)
**Searched:** MCP tool poisoning / CVE-2025-53773, 2026-06-20.
- **CVE-2025-53773** (CVSS 9.6): a remote-code-execution vuln in GitHub Copilot — *malicious
  instructions in externally fetched content caused the agent to execute attacker-controlled commands.*
  The self-elevation analog SHIELD's TOOL-CAPE blocks (a runtime attempt to expand its own capabilities).
- **Tool poisoning** = a form of indirect injection where *"malicious instructions are embedded in tool
  metadata (descriptions, parameters, prompts) rather than in user inputs"* — a compromised MCP server
  injects instructions into tool descriptions that agents read to decide when to call a tool.
- **The structural root** (verbatim): *"The user's prompt, developer's system message, and tool
  descriptions from third-party MCP servers all collapse into a single context window, with the model
  having no way to distinguish between them."* — this collapse is EXACTLY what PROVENANCE-LABEL +
  VERIFIER TAINT-RAIL counter: MCP tool metadata is ENV-tier, so it cannot reach a verifier's
  code/spec slot, and it is labeled distinct from SYSTEM/USER.
- **April 2026 real-world demo** (fetched): researchers hijacked Claude Code, Gemini CLI, and GitHub
  Copilot by injecting instructions into GitHub PR titles; agents read the PR data and exfiltrated
  Actions secrets. Confirms ENV-tier (PR metadata) → action is the live threat the label/scan address.

## §E — MiniScope / least-privilege (TOOL-CAPE doctrine)
The least-privilege principle (grant only the minimum tools/permissions a task needs) is the doctrine
behind TOOL-CAPE and is the OWASP LLM06 prevention guidance (§B, fetched). I did not separately fetch a
"MiniScope" paper page; the least-privilege grounding rests on the OWASP LLM06 verbatim lines above,
which is the load-bearing, fetched source. **Stated honestly: "MiniScope" is named in the kickoff but
its grounding here is the OWASP LLM06 least-privilege text, not a separate fetch.**

## Independent verification of this hardening
- `selftest_all.py` — the frozen gate's own accept-good / catch-broken / abstain-malformed self-tests,
  including the non-syntactic semantic-injection ABSTAIN test (machine, κ=1 where applicable).
- `demo_rails/` — committed predictions confirmed by the gate (machine).
- `AUDIT.md` — a cross-model (Sonnet/Haiku ≠ the Opus generator) red-team stub that attacks each rail
  with its own code (relabel, taint-smuggle, cape-escape, cert-replay) and polices the κ=0 rail against
  any "we detect all injections" over-claim.
