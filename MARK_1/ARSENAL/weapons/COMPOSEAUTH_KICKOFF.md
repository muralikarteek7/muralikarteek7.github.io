# KICKOFF — build the KIT piece: G3 — COMPOSITIONAL AUTHORIZATION (the "LEDGER-BUDGET" rail)
*Paste into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written 2026-06-20. This is item
**#6 / gap G3** of the KIT-EXPANSION plan (`Next/KIT_EXPANSION_PROPOSAL.md`, §5). It is the **completion of GLOVES**:
GLOVES gates each action; G3 gates the SEQUENCE. **DO NOT build before GLOVES exists** — G3 consumes GLOVES' ledger.*

*Independent audit 2026-06-20 (READY-WITH-FIXES; cleanest exact-arithmetic gate of the kit) — apply at build:
(1) add the **just-under-threshold SALAMI self-test** (N actions each below the per-action GLOVES trigger but whose
SUM crosses the session threshold → G3 must catch it) — the canonical accumulator attack, currently named but
untested; (2) require GLOVES' ledger to expose an `other_effects` **catch-all** field so a novel blast-radius type
is routed to UNCOVERED, never silently dropped; (3) label the blast-radius **weights as POLICY inputs** (same as the
thresholds), not derived truth. Hard ordering: blocked until GLOVES' ledger API is frozen.*

---

You are building **the compositional-authorization rail**: a running budget over the stream of actions so that a
sequence of individually-safe, individually-authorized steps **cannot silently compose into a catastrophic one**
(the "galaxy-brained" failure: 100 small reversible deletes = one irreversible wipe; 50 authorized $20 charges =
$1000 nobody approved). Work BOX-style: plan → produce → **verify INDEPENDENTLY** → ground → be honest; **the gate
must be able to FAIL (halt a runaway sequence) or it is not a gate.**

## 0. ORIENT
`CLAUDE.md`, `RESUME.md`, **`Next/KIT_EXPANSION_PROPOSAL.md`** (§5 G3, §2 GLOVES), **`Next/BOX_V5.md`**, and
**`weapons/gloves/`** (REQUIRED — G3 reads GLOVES' per-action `{tier, blast-radius, running-accumulator}` ledger).
Also `Registrar` in `HELMET/registry.json` (the anti-theater budget officer — G3 is its actuation analog: a budget,
but for real-world blast radius instead of tokens).

## 1. THE HONEST FRAMING — what G3 IS and IS NOT
**IS:** a **stateful budget accumulator** over a session's actuation stream. Each GLOVES-allowed action adds its
blast-radius to running counters (per resource class: $ spent, records mutated, recipients contacted, files
deleted, external calls). When a counter crosses a committed threshold, G3 **escalates the tier** of the NEXT
action (CONFIRM→STEP-UP) or **halts + escalates to a human** — even though each step alone was fine.
**The κ=1 core:** the accumulation + threshold comparison is exact arithmetic (like the Registrar's token budget,
like OPTIMA's objective recompute); a sum crossing a frozen threshold is a machine fact.
**IS NOT:** ❌ a judge of whether the *composition is malicious* (that's κ=0 intent — it abstains/escalates, doesn't
accuse). ❌ able to set the "right" threshold for you (the threshold is a committed policy input, not derivable —
state it). ❌ a replacement for GLOVES (it needs GLOVES' per-action classification). ❌ complete against an attacker
who spreads effect across resource classes G3 doesn't count (you can only budget what you enumerate — say so).

## 2. THE BUDGET DIMENSIONS (each a committed counter + threshold)
| dimension | counter | example threshold (policy, committed) |
|---|---|---|
| financial | Σ $ committed this session | > $100 → STEP-UP; > $1000 → halt |
| data-mutation | # records created/updated/deleted | > 50 → STEP-UP |
| broadcast | # external recipients contacted | > 10 → STEP-UP |
| destruction | # irreversible deletes / overwrites | > 5 → STEP-UP; any B-external delete → STEP-UP |
| external-calls / rate | calls per window | > rate R → throttle/halt (Denial-of-Wallet guard) |
| blast-radius score | Σ (reversibility×blast) weights | > B → halt + human |

## 3. THE KEY ENGINEERING PROBLEM — the accumulator + the gate-of-the-gate
`composeauth_gate.*`: subscribes to GLOVES' ledger; maintains the counters; before each NEW action, returns
`{tier_escalation | HALT | OK}`. Counters are **monotonic within a session** and **persisted** (a restart must not
reset the budget — else the attack is "crash and resume"). **Self-tests (non-waivable):** (a) N individually-AUTO
small charges that SUM past the financial threshold → the (N+1)th is ESCALATED, not auto-allowed; (b) a burst of
deletes past the destruction threshold → HALT; (c) a single legitimate small action well under all thresholds →
OK (no false halt); (d) the counter does NOT reset on a simulated session-restart (persistence); (e) effect spread
across a class G3 doesn't track is **reported as uncovered**, never silently "within budget" (the honesty rail).

## 4. INFRA + GROUND-BY-FETCH
- **Confirm:** GLOVES' ledger exposes per-action blast-radius (G3 is blocked without it). Persistent counter store.
- **FETCH-confirm (cite `GROUNDING.md`):** OWASP **Denial-of-Wallet** / agent rate-limiting + spend-tracking
  guidance; the "compounding micro-authorizations" / scope-creep failure (OWASP Excessive Agency LLM06). Don't
  assert from memory.

## 5. TO-DOs (box order)
1. **PLAN** `weapons/composeauth/SPEC.md` — the budget dimensions, the committed thresholds (policy inputs, flagged
   as choices not derivations), the κ=1 accumulation vs κ=0 intent boundary, the router (subscribe to GLOVES; on
   threshold → escalate/halt). **GROUND** Denial-of-Wallet + scope-creep in `GROUNDING.md`.
2. **BUILD THE GATE FIRST** (§3): `composeauth_gate.*` + `selftest_all.py` (the 5 self-tests). Green first.
3. **WIRE to GLOVES' demo:** replay a sequence of safe actions that compose past a threshold → show the escalation
   fire. Use the same safe surfaces as GLOVES (nothing actually irreversible).
4. **KILLER DEMO, committed predictions** (`PREDICTION.md` first): (i) 6 small AUTO charges → 7th escalated;
   (ii) a delete-burst halted; (iii) a benign single action OK; (iv) restart doesn't reset the budget;
   (v) effect via an untracked class reported as UNCOVERED.
5. **VERIFY INDEPENDENTLY:** cross-model audit (Sonnet/Haiku ≠ Opus generator) — tries to slip past via
   class-splitting, crash-resume, and just-under-threshold salami; checks no false halt on benign streams; checks
   the "uncovered class" honesty. Fix what's caught.
6. **REGISTER:** `Next/BOX_V5.md` (GLOVES + G3 = the complete effector layer), `HELMET/registry.json` (Registrar's
   actuation budget), honest `EVOLUTION_LOG` (**completes GLOVES; capability expansion, NOT a promotion**). Update
   plan §7 + backlog.

## 6. HONESTY RAILS
- **You can only budget what you ENUMERATE** — every run reports which resource classes are tracked and that effect
  outside them is uncovered. No silent "within budget."
- **Thresholds are committed POLICY, not derived truth** — state them; they are choices a human owns.
- **κ honesty:** the accumulation + comparison is κ=1; "is this composition malicious?" is κ=0 → escalate, never accuse.
- **Persistence is load-bearing** — a budget that resets on restart is defeated by crash-resume; test it.
- **Blocked on GLOVES** — G3 without GLOVES' per-action classification is not buildable; say so, don't fake it.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/composeauth/` — `SPEC.md`, `GROUNDING.md`, `composeauth_gate.*` + `selftest_all.py`,
`composeauth_router.py`, `demo_*/` (committed predictions + the escalation/halt log), `AUDIT.md`, `README.md`
(honest ceiling: budgets enumerated classes; thresholds are policy; not an intent judge). Registration in
`Next/BOX_V5.md` + `HELMET/registry.json` + honest `EVOLUTION_LOG`; plan §7 + `WEAPONS_BACKLOG.md`.

## 8. STAFF (v4 ladder; Fable INACTIVE → Opus, flag low confidence)
- **Accumulator** = code tier (exact sums + threshold compares + persistence — the arithmetic, not a model, halts).
- **Library** = cheap model: fetch Denial-of-Wallet + scope-creep guidance.
- **Auditor** = a model ≠ generator (Sonnet/Haiku) — salami / class-split / crash-resume attacks; false-halt checks.

## 9. THE ONE-LINE TEST OF SUCCESS
**"G3 keeps an EXACT running blast-radius budget over GLOVES' allowed actions, per enumerated resource class, and
escalates or halts the moment a committed threshold is crossed — so a sequence of individually-authorized safe
steps cannot silently compose into a catastrophe — while reporting which classes it does NOT track, treating the
thresholds as human-owned policy not derived truth, and surviving a crash-resume."** Closes the composition hole
GLOVES alone leaves open; honest that it budgets only what it counts.
