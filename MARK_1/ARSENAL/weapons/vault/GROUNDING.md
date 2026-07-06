# VAULT — GROUNDING (load-bearing facts FETCHED, not asserted from memory)
*Box rule B4: a load-bearing fact gets a fetched source, not memory. Fetched 2026-06-20
via WebSearch + WebFetch. Where a fetch was partial or sources disagreed, that is stated
plainly rather than smoothed over.*

## G1 — Staleness in high-relevance memories is an OPEN problem (the VAULT's core limit)
**FETCHED (WebFetch, mem0.ai "State of AI Agent Memory 2026", dated Jun 19 2026):**
- Verbatim, under "Open Problems": *"Decay handles low-relevance memories. Staleness in
  high-relevance memories is a harder, open problem."*
- Verbatim example: *"A highly-retrieved memory about a user's employer is accurate until
  they change jobs, at which point it becomes confidently wrong."*

**Why it is load-bearing here:** this is precisely the failure mode the VAULT mitigates
with TTL + a stale-on-read flag — and explicitly does NOT solve. A FETCHED_FACT that was
true when fetched can become "confidently wrong"; the VAULT flags it for re-verify, it
does not know the new truth.
Source: https://mem0.ai/blog/state-of-ai-agent-memory-2026

## G2 — Memory systems REPLACE facts rather than model temporal change
**FETCHED (same WebFetch, "Open Problems" / "Cross-session structure"):**
- Verbatim: *"A user who moves from New York to San Francisco should have that transition
  understood, not just the new city stored. Most systems treat change as replacement."*
- Supporting (WebSearch summary of the same space): base semantic-similarity retrieval
  *"can surface outdated facts if they are semantically closer to the query than the
  updated fact"*; conflict resolution under iterative revisions *"remains an open research
  problem."*

**Why it is load-bearing here:** confirms the kickoff's framing — current memory systems
*replace* facts rather than modeling that the world changed (when a fact became true vs
when it was superseded). The VAULT does NOT attempt temporal modeling; it flags staleness.
This is named as a known limitation in README + SPEC §4/§8, not papered over.
Source: https://mem0.ai/blog/state-of-ai-agent-memory-2026

## G3 — The case AGAINST weight-level continual learning for production
**FETCHED (WebSearch summaries; the mem0 blog itself did NOT cover this — stated honestly):**
- *"Most production teams find that true online learning (updating weights after every
  interaction) is impractical — scheduled periodic retraining (daily, weekly) is the
  actual deployment pattern."*
- Weight-level updates suffer **catastrophic forgetting**: *"knowledge is distributed
  across billions of weight parameters in a highly entangled way — there is no clean
  'module for French' or 'register for user preferences' that can be updated in isolation."*
- Parametric (fine-tune) approaches *"achieve high task fidelity at the expense of
  considerable compute, data, and the danger of catastrophic forgetting"* — positioning
  **external memory** as the practical alternative for production agents.

**Why it is load-bearing here:** justifies the VAULT being EXTERNAL memory (a structured
store), not weight-level continual learning. Sources:
- Rethinking Memory in LLM-based Agents — https://arxiv.org/pdf/2505.00675
- Memento: Fine-tuning LLM Agents without Fine-tuning LLMs — https://arxiv.org/pdf/2508.16153
- Continual learning / catastrophic forgetting overview — https://zylos.ai/research/2026-04-09-continual-learning-catastrophic-forgetting-ai-agents/

## G4 — Benchmark numbers: a HONEST discrepancy (do NOT cite a single number as settled)
The WebSearch summary and the WebFetch of the primary mem0 page returned DIFFERENT
LongMemEval figures:
- WebFetch (mem0 primary page) reported a Mem0 LongMemEval row of **94.4** (with a
  6,787 tokens/query figure).
- WebSearch summary reported **Mem0 49.0 vs Zep/Graphiti 63.8** on LongMemEval, framing
  the gap as "entirely from temporal fact tracking."
**These are not reconcilable from the fetched text alone** (likely different metrics —
e.g. accuracy on a subset vs an overall score, or different LongMemEval variants). The
VAULT does NOT depend on any specific benchmark number, so this is recorded as an OPEN
discrepancy rather than resolved. We do not assert a single figure as fact.

## G5 — Local infra confirmed (machine-probed, not fetched)
- `python3 --version` -> **Python 3.9.6** (probed 2026-06-20, darwin).
- `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"` -> **sqlite3 3.51.0**.
- The box memory directory exists at
  `/Users/varunesh/.claude/projects/-Users-varunesh-Desktop-AI-agents/memory/` with
  `MEMORY.md` (the write-discipline already in use). The VAULT is a JSON-backed store
  alongside it (no external dependency — stdlib `json` + `datetime` only; SQLite NOT
  required, kept JSON for transparency/auditability).

## Fetch-failure honesty
- No fetch FAILED outright. One PARTIAL: the weight-level continual-learning case (G3)
  was NOT present on the primary mem0 page and is grounded instead in the survey/Memento
  arXiv sources via WebSearch summaries — flagged so the reader knows it is second-hand
  summary, not a verbatim primary-page quote.
- G4 is an explicit unresolved discrepancy between two of our own fetches; left open.
