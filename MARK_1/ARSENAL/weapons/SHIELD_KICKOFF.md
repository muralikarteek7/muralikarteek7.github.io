# KICKOFF — build the KIT piece: SHIELD (adversarial-input hardening) for the v5 box
*Paste into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written 2026-06-20. SHIELD is item
**#3** of the KIT-EXPANSION plan (`Next/KIT_EXPANSION_PROPOSAL.md`, §3). **HONEST UP FRONT (the red-team's ruling):
SHIELD is NOT a weapon and mostly NOT new — it is ARMOR-HARDENING.** Injection/jailbreak *intent* detection is
κ≈0 (an attack is defined by evading detection — no cheap exact verifier exists). What IS new and buildable is a
thin set of **κ=1 STRUCTURAL rails** the box lacks today. Build those; route the rest to abstain-and-escalate.*

*Independent audit 2026-06-20 (READY-WITH-FIXES; best honesty framing of the kit) — apply at build: (1) add a
non-waivable self-test with a **non-syntactic, semantically-embedded injection** (no base64/keyword) whose correct
verdict is ABSTAIN — toy attacks aren't enough; (2) PROVENANCE-LABEL is exact but **model OBEDIENCE to the label is
κ<1 and untested** — add a defense-in-depth test that a labeled injection still hits ARMOR's fabrication veto, and
state the residual risk; (3) wire SHIELD's ABSTAIN rail + TRIAGE's distribution-shift row to the SAME downstream
handler. The VERIFIER TAINT-RAIL is the single highest-value rail in the whole kit — hardens all 12 weapons.*

---

You are building **SHIELD**: the box's **active boundary** between attacker-controlled input and its internals.
ARMOR is passive always-on honesty; SHIELD is the gate that decides *what reaches ARMOR/WEAPONS/HELMET at all*
when the input did not originate from the box's own code (user text, tool output, retrieved docs, web, MCP
metadata, memory reads, other-agent messages). Work BOX-style: plan → produce → **verify INDEPENDENTLY** → ground →
be honest; **the κ=1 rails ship as armor-hardening; the κ=0 part ABSTAINS — never an LLM "injection detector"
trusted as truth (that's circular: an LLM judging attacks on an LLM).**

## 0. ORIENT — read first (in order)
`CLAUDE.md`, `RESUME.md`, **`Next/KIT_EXPANSION_PROPOSAL.md`** (§3 SHIELD, §0 honest goal), **`Next/BOX_V5.md`**
(ARMOR section — SHIELD extends it), the registry `Next/WEAPON_REGISTRY.json`. Then `socius/` (the existing
`S-GROUND` fabrication layer — SHIELD is adjacent: S-GROUND checks "is the quote really in the source"; SHIELD
checks "is this input trying to subvert me") and `factharness/` (the promoted grounding facility). SHIELD is
**armor-hardening + 4 κ=1 rails**, NOT an offense weapon — frame it that way everywhere.

## 1. THE HONEST FRAMING — what SHIELD IS and IS NOT
**IS:** four **κ=1 structural rails** (exact, machine-checkable, the box lacks them) + a κ=0 abstain rail:
- **PROVENANCE-LABEL (κ=1 label):** tag every context span `SYSTEM` / `USER` / `ENV`(external) at ingestion. The
  wrapper controls the label, so attacker text **cannot relabel itself**. (Model *compliance* with the label is
  κ<1 — state that honestly; the label is exact, the obedience is not.)
- **VERIFIER TAINT-RAIL (κ=1):** **no weapon's verifier is ever fed `ENV`/attacker-controlled natural language.**
  A gate's inputs = the candidate object + the frozen verifier code + the system spec — never retrieved prose.
  This protects all weapons from being *talked into* a false certificate (the analog of "auditor ≠ generator",
  applied to inputs). This is the single highest-value rail — it hardens the entire arsenal.
- **TOOL-CAPE (κ=1 allowlist match):** a task-scoped, signed tool allowlist the model **cannot self-elevate**
  (counters tool-description poisoning + excessive agency). Pairs with GLOVES (which gates the *effect*; TOOL-CAPE
  gates *which tools exist* for this task).
- **CERT ANTI-REPLAY (κ=1 hash+sig):** every weapon certificate is `{object_hash, verifier_id+version, ts, result}`,
  re-checked before downstream use so a stale/forged "PASS" can't be replayed onto a new object.
- **ABSTAIN-OR-ESCALATE (κ=0):** for injection *intent* / jailbreak / social-engineering — SHIELD raises a κ<1
  suspicion flag (cheap structural signals: a relabel attempt, base64, mid-document language switch, an imperative
  override pattern) and routes to (a) human review for high-privilege ops, (b) capability downgrade to read-only,
  or (c) hard abstain + log. It **never self-certifies "injection-free."**

**IS NOT:** ❌ a "weapon" (it builds nothing). ❌ a complete injection defense (NIST AI 100-2: ~80% attacker success
at 25 tries — no machine-checkable defense exists for semantic injection woven through a long document). ❌ an LLM
injection-classifier trusted as ground truth (circular). ❌ a replacement for ARMOR's fabrication veto or the
cross-model audit — it's a layer *in front*, assuming the others may still fail (defense-in-depth, not a wall).

## 2. THE RAILS, BY κ (the gate is structural where it can be, abstains where it can't)
| rail | κ | what it blocks | honest failure mode |
|---|---|---|---|
| PROVENANCE-LABEL | κ=1 label / κ<1 obedience | authority-confusion (ENV text read as instruction) | a crafted payload can still semantically prime the model despite the label |
| VERIFIER TAINT-RAIL | κ=1 | gaming a weapon's gate via poisoned context | a genuine *code* bug in the verifier (not an input attack) — out of scope (that's CRUCIBLE) |
| TOOL-CAPE | κ=1 allowlist | excessive agency, tool-description poisoning | a *permitted* tool whose server is compromised — supply chain, out of scope |
| CERT ANTI-REPLAY | κ=1 hash+sig | replaying a stale/forged PASS onto a new object | the verifier binary replaced wholesale — needs build attestation, out of scope |
| ABSTAIN-OR-ESCALATE | κ=0 | novel injection / jailbreak / social-eng | false negatives pass to ARMOR (the depth layer); false positives add friction |

## 3. THE KEY ENGINEERING PROBLEM — build the κ=1 rails as a frozen gate FIRST
`shield_gate.*` with self-tests green before anything routes through it:
1. **PROVENANCE-LABEL:** an ingestion wrapper that stamps every span with its origin tier; assert external text
   cannot produce a `SYSTEM`/`USER` label for itself.
2. **VERIFIER TAINT-RAIL:** a checked interface for weapon gates — inputs are typed `{candidate_object, frozen_code,
   system_spec}`; any `ENV`-tagged string in those slots → REJECT before the gate runs.
3. **TOOL-CAPE:** a signed per-task allowlist; the call-shim BLOCKs any tool not in the cape; the model cannot add
   to the cape at runtime (CVE-2025-53773-style self-elevation → BLOCK + ALARM).
4. **CERT ANTI-REPLAY:** issue + verify signed certificate tuples; a hash-mismatch or stale/forged cert → REJECT.

**Gate-of-the-gate self-tests (non-waivable):** (a) external text CANNOT relabel itself to SYSTEM/USER; (b) a
verifier fed an ENV string in a code/spec slot REJECTS before running; (c) a tool outside the cape is BLOCKED and a
self-elevation attempt ALARMS; (d) a certificate replayed onto a *different* object (hash-mismatch) is REJECTED;
(e) the ABSTAIN rail FLAGS a planted obvious-injection sample and routes it to escalation **without** ever
emitting "injection-free: true" (assert the word never appears as a positive certification). Six green → trustworthy.

## 4. INFRA + GROUND-BY-FETCH (don't assert)
- **Confirm:** where ingestion/labeling and the call-shim can live in the harness; standard crypto (hash+sig) for
  certs/capes/tokens. State what's present.
- **FETCH-confirm (cite in `GROUNDING.md`):** OWASP **LLM01:2025 Prompt Injection** (direct + indirect; "segregate
  and denote untrusted content" mitigation = the provenance rail) and **LLM06 Excessive Agency** (= TOOL-CAPE);
  **NIST AI 100-2 E2025** (agent-specific: indirect injection, memory poisoning, tool supply-chain; ~80% success at
  25 tries — the honest ceiling); **MiniScope** least-privilege (TOOL-CAPE); MCP tool-description poisoning
  (MCP-38 / MCPTox). Don't claim a source you didn't fetch.

## 5. TO-DOs (box order)
1. **PLAN:** `weapons/shield/SPEC.md` — the 4 κ=1 rails + the κ=0 abstain rail, the κ honesty per rail, the router
   (`shield_router.py`: external input → label + scan; a weapon call → enforce taint-rail + cert check; a tool call
   → enforce cape; a high-privilege op under suspicion → escalate/abstain). **GROUND** OWASP/NIST in `GROUNDING.md`.
2. **BUILD THE GATE FIRST** (§3): `shield_gate.*` + `selftest_all.py` (the 6 self-tests). Green before routing.
3. **WIRE the highest-value rail first:** the **VERIFIER TAINT-RAIL** across the existing weapon gates (the biggest
   arsenal-wide hardening) — prove a poisoned-context attempt is rejected before a gate runs.
4. **KILLER DEMO, committed predictions** (`PREDICTION.md` first): (i) ENV text fails to relabel itself; (ii) a
   weapon gate rejects an ENV string smuggled into its spec slot; (iii) an out-of-cape tool blocked + self-elevation
   alarmed; (iv) a replayed certificate rejected; (v) a planted injection routed to escalation with NO
   "injection-free" certification. Predict each verdict before running.
5. **VERIFY INDEPENDENTLY:** cross-model audit (Sonnet/Haiku ≠ Opus generator; never Opus-audits-Opus) — attacks each
   rail with its own code (relabel, taint-smuggle, cape-escape, cert-replay), and checks the κ=0 rail never
   over-claims detection. Fix what's caught.
6. **REGISTER:** `Next/BOX_V5.md` (ARMOR section gains the SHIELD rails; note SHIELD is hardening, NOT a weapon),
   `HELMET/registry.json` (Integrity Office + Registrar gain the rails), honest `EVOLUTION_LOG` (**armor-hardening,
   NOT a capability promotion**). Update `KIT_EXPANSION_PROPOSAL.md` §7 + `WEAPONS_BACKLOG.md`.

## 6. HONESTY RAILS (non-waivable)
- **The κ=1 rails are exact; injection *intent* detection is κ=0 → ABSTAIN/escalate, never self-certify safe.**
- **Never an LLM injection-detector trusted as truth** (circular). A suspicion flag routes; it does not clear.
- **Defense-in-depth, not a wall** — SHIELD failure ≠ system failure (ARMOR's fabrication veto + cross-model audit
  remain). Conversely SHIELD success ≠ "secure." State the NIST ceiling on every run.
- **Label SHIELD as hardening, not a new offense capability** — calling it a weapon would overstate buildable safety.
- **Scope honesty:** TAINT-RAIL stops input-attacks on a gate, not *code* bugs in the gate (that's CRUCIBLE);
  TOOL-CAPE stops unpermitted tools, not compromised permitted servers (supply chain).

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/shield/` — `SPEC.md`, `GROUNDING.md`, `shield_gate.*` + `selftest_all.py`,
`shield_router.py`, `demo_*/` (committed predictions + the blocked-attack exhibits), `AUDIT.md`, `README.md` (honest
ceiling: 4 exact rails + an abstain rail; not a complete injection defense). Registration in `Next/BOX_V5.md`
(ARMOR) + `HELMET/registry.json` + honest `EVOLUTION_LOG`; `KIT_EXPANSION_PROPOSAL.md` §7 + `WEAPONS_BACKLOG.md`.

## 8. STAFF (v4 ladder; Fable INACTIVE → Opus, flag low confidence)
- **Rails** = code tier (deterministic label/allowlist/hash checks — the structure, not a model, is the block).
- **Library** = cheap model: fetch OWASP LLM01/LLM06 + NIST AI 100-2 + MiniScope/MCP-poisoning.
- **Auditor** = a model ≠ generator (Sonnet/Haiku; never Opus-audits-Opus) — attacks each rail; polices the κ=0
  abstain rail against any "we detect all injections" over-claim.

## 9. THE ONE-LINE TEST OF SUCCESS
**"SHIELD adds four EXACT structural rails the box lacked — provenance-labeled input, a verifier-input taint-rail
that stops any weapon gate being talked into a false certificate, a non-self-elevatable tool-cape, and certificate
anti-replay — and routes everything it CANNOT exactly check (injection intent, jailbreaks) to abstain-or-escalate,
never to an LLM detector trusted as truth; it is labeled ARMOR-HARDENING, not a weapon, and it states the NIST
ceiling that no injection defense is complete."** Exact where it can be, abstaining where it can't, honest about
the wall it is not.
