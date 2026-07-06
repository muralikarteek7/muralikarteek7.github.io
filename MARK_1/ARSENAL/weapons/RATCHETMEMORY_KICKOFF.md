# KICKOFF — build the KIT piece: SHOES-b — RATCHETING VERIFIED-MEMORY (the "VAULT")
*Paste into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written 2026-06-20. This is item
**#5 (SHOES sub-component b)** of the KIT-EXPANSION plan (`Next/KIT_EXPANSION_PROPOSAL.md`, §4). It makes the box's
"underused memory directory" into a SYSTEM: each session's MACHINE-VERIFIED results become reusable assets so the
box stops re-walking ground it already proved.*

*Independent audit 2026-06-20 (READY-WITH-FIXES; joint-best honesty framing) — apply at build: (1) define the
**minimum verification-record SCHEMA** (`method`, `artifact`, `result` required) and REJECT a FACT-tier write whose
record is present-but-empty/contentless — "has a record" must mean a VALID one, else a LEAD gets promoted by
attaching `{verified:true}`; (2) **commit TTL values per tier** (e.g. FETCHED=30d) and make "high-stakes" a
committed ENUM, not a model judgment, with a self-test that a short-TTL fact re-flags on next read; (3) test the
in-place LEAD-promotion attack (the record-validity check is the κ=1 core).*

---

You are building **the VAULT**: a verifier-gated, TTL-aware store of **machine-verified** results, keyed for reuse,
so future sessions query it before re-doing work. Work BOX-style: plan → produce → **verify INDEPENDENTLY** →
ground → be honest; **only VERIFIED results enter as facts; everything else is a labeled LEAD, not truth; and a
recalled fact carries a freshness check — staleness without detection is the failure mode.**

## 0. ORIENT
`CLAUDE.md`, `RESUME.md`, **`Next/KIT_EXPANSION_PROPOSAL.md`** (§4 SHOES-b), the existing memory dir
(`/Users/varunesh/.claude/projects/.../memory/` + `MEMORY.md`) and the box's memory rules in `CLAUDE.md` (the
write-discipline already in use), and `RATCHET.md` (the box already ratchets *versions*; the VAULT ratchets
*verified results*). The honest framing: this is INFRA, not a weapon — but it has a κ=1 entry gate (a result enters
as a FACT only if it shipped with a machine-verification record).

## 1. THE HONEST FRAMING — what the VAULT IS and IS NOT
**IS:** a structured store. Each entry: `{result, domain, verification_method, verification_record, valid_until
(TTL), staleness_flag, provenance}`. Writes are **verifier-gated** — a result enters as a FACT only with a machine
or fetched-source verification record; an unverified "the session concluded X" enters as a **LEAD** (clearly
labeled, never returned as a fact). Reads are **TTL-aware** — a high-stakes entry past its TTL triggers a re-verify
before reuse.
**IS NOT:** ❌ a weapon. ❌ a place for unverified beliefs dressed as facts (the cardinal sin — a recalled lead used
as truth). ❌ a model of TEMPORAL CHANGE — the known open problem (mem0 2026): memory systems *replace* facts
rather than modeling that the world changed, so a fetched-URL result true in March can be stale in June. The VAULT
mitigates with TTL + staleness re-check; it does not solve temporal modeling — say so. ❌ weight-level continual
learning (impractical/expensive — this is external memory, not training).

## 2. THE ENTRY TIERS (the read/write contract)
| tier | enters as | example | reuse rule |
|---|---|---|---|
| **VERIFIED FACT** | machine-proof / fetched-source record attached | "OPTIMA: burma14 optimal = 3323 (3 methods)"; "ζ(2)=π²/6 (SYMBOLICA cert)" | reuse freely; re-verify if past TTL & high-stakes |
| **FETCHED FACT** (decays) | a fetched source + URL + date | "library X version is 1.14 (fetched 2026-06-20)" | shorter TTL; re-fetch on stale read |
| **LEAD** (never a fact) | no verification record | "the session thought approach Y was promising" | surfaced as a hypothesis to test, NEVER as truth |

## 3. THE KEY ENGINEERING PROBLEM — the verifier-gated write + the gate-of-the-gate
`vault.*`: `write(entry)` REJECTS a FACT-tier write lacking a verification record (demotes it to LEAD); `read(query)`
returns facts with their freshness, and **flags/ re-verifies** stale high-stakes entries. **Self-tests
(non-waivable):** (a) a result WITH a machine-verification record writes as VERIFIED FACT and reads back with its
method; (b) a result WITHOUT a record is REJECTED as a fact and stored as a LEAD (never returned as truth); (c) a
FETCHED entry past its TTL is FLAGGED stale on read (not silently served); (d) a LEAD is never returned in a
"facts" query (only in a "leads/hypotheses" query); (e) provenance survives round-trip (you can always trace a
fact to its verification).

## 4. INFRA + GROUND-BY-FETCH
- **Confirm:** the memory directory + write tooling (already in use); a structured store (JSON/SQLite) for the
  tiers/TTL. State what's present.
- **FETCH-confirm (cite `GROUNDING.md`):** the agent-memory state-of-the-art + its OPEN problem — systems *replace*
  facts rather than model temporal change → staleness without detection; multi-scope keying; the case AGAINST
  weight-level continual learning for production (mem0 2026 / continual-learning surveys). Don't assert from memory.

## 5. TO-DOs (box order)
1. **PLAN** `weapons/vault/SPEC.md` — the 3 tiers, the verifier-gated write, TTL/staleness, the read contract
   (facts vs leads), the κ=1 entry gate vs the κ=0 staleness-judgment. **GROUND** the staleness open-problem in
   `GROUNDING.md`.
2. **BUILD** `vault.*` + `selftest_all.py` (the 5 self-tests). Green first.
3. **BACKFILL from this season, committed predictions** (`PREDICTION.md` first): ingest a handful of REAL verified
   results (burma14=3323, ζ(2)=π²/6, infra versions with dates) and a couple of LEADS; predict that a "facts" query
   returns only the verified ones with methods, the stale infra entry flags, and the leads never appear as facts.
4. **VERIFY INDEPENDENTLY:** cross-model audit (Sonnet/Haiku ≠ Opus generator) — tries to get a LEAD returned as a
   fact, a stale entry served without a flag, a FACT written without a record; checks provenance integrity. Fix
   what's caught.
5. **REGISTER:** `Next/BOX_V5.md` (SHOES-b: verified-result ratchet), `HELMET/registry.json` (a cross-cutting
   memory facility), honest `EVOLUTION_LOG` (**infra that stops rework; NOT a promotion**). Update plan §7 + backlog.

## 6. HONESTY RAILS
- **Only VERIFIED results are facts** — no record ⇒ a LEAD, never returned as truth.
- **Staleness is the failure mode** — every fact carries a TTL; high-stakes stale reads re-verify; never silently
  serve an expired fact. The box does NOT model temporal change — it flags, it doesn't reconcile.
- **Provenance is mandatory** — a fact you can't trace to its verification is not a fact.
- **It's infra, not a capability** — no ratchet movement; the value is not-redoing-verified-work.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/vault/` — `SPEC.md`, `GROUNDING.md`, `vault.*` + `selftest_all.py`, `demo_backfill/`
(committed predictions + the facts/leads/stale behavior), `AUDIT.md`, `README.md` (honest ceiling: verified-only
facts, TTL-flagged staleness, no temporal-change modeling). Registration in `Next/BOX_V5.md` +
`HELMET/registry.json` + honest `EVOLUTION_LOG`; plan §7 + `WEAPONS_BACKLOG.md`.

## 8. STAFF (v4 ladder; Fable INACTIVE → Opus, flag low confidence)
- **Store + gate** = code tier (the verification-record check, not a model, decides FACT vs LEAD).
- **Library** = cheap model: fetch the agent-memory staleness open-problem.
- **Auditor** = a model ≠ generator (Sonnet/Haiku) — lead-as-fact, stale-served, record-less-fact attacks.

## 9. THE ONE-LINE TEST OF SUCCESS
**"The VAULT stores only MACHINE-VERIFIED (or fetched-source) results as facts — each with its verification method,
provenance, and a TTL — demotes everything unverified to a clearly-labeled LEAD that is NEVER returned as truth, and
FLAGS or re-verifies stale high-stakes entries on read rather than silently serving them; it stops the box
re-walking proven ground without ever letting an unverified belief masquerade as a fact."** A ratchet for verified
results; honest that it flags staleness rather than solving it.
