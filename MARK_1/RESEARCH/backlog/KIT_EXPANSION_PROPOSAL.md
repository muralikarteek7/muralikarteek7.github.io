# KIT EXPANSION — the Dean's integration (SHIELD / SHOES / GLOVES + what's really missing)
*Date 2026-06-20. STATUS: a **κ=0 DESIGN PROPOSAL**, produced in ARMOR mode (grounded + independent cross-model
panel + honest abstention). **NOT a verified result, NOT a promotion** — no A/B, no shared arena. The ≥10%
capability ratchet is untouched (stays OPEN at v3). Everything here is a bet to be built box-style, then proven.*

## How this was made (dogfooding the HELMET)
Convened 4 independent **Sonnet** departments (≠ the Opus integrator; Fable inactive): a Security dept (SHIELD),
a Systems/Efficiency dept (SHOES + GLOVES), and an **Integrity-Office red-team** told to attack the whole thing.
Each grounded its piece in fetched 2025–2026 sources (OWASP LLM Top-10, NIST AI 100-2, CVE-2025-53773, MiniScope,
mem0, OWASP Agent cheat-sheet). The Dean (Opus) integrated. **The red-team reshaped the output — its critique is
honored, not softened.** (Caveat: the integrator did not independently re-fetch every URL the sub-agents cited;
the load-bearing ones — OWASP LLM01, CVE-2025-53773 — are well-known; some arXiv IDs are agent-fetched, unverified.)

---

## 0. The honest reframe (the red-team's first hit — accepted in full)
**"Best for any world-case scenario" is struck.** It directly contradicts the BOX's own edge — *knowing its
limits and abstaining.* A system that claims to be best in every scenario cannot abstain, would need a verifier
for every domain (the κ-rule already concedes that's impossible), and would have to defend κ=0 ground it has
sworn to only ground-and-abstain on. Worse: **adding κ=0 "kit" to chase universal coverage INCREASES the
surface for confident-wrong output** — the opposite of robustness.

**The honest goal that replaces it:**
> Be **best-in-class where a cheap exact verifier exists (κ>0)**, and **more trustworthy than the alternatives
> where it does not (κ=0) by abstaining instead of confabulating** — and make *both* halves robust to a live
> adversary and safe when the system reaches into the real world.

That is falsifiable and defensible. "Robust across scenarios" = **coverage × resilience × an honest κ=0 floor**,
NOT omnicompetence.

## 1. The analogy is MOTIVATION, not architecture (the second hit — accepted)
The knight's-kit metaphor is decoration. It earns nothing. **Every proposed piece must pass the BOX's own κ-gate
on its own terms before it gets a name** — or it's the theater the project exists to refuse. Verdict table:

| proposed piece | genuinely new? | κ of its core | verdict |
|---|---|---|---|
| **GLOVES** (actuation safety) | **YES — the one real capability gap** | **κ=1** reversibility/confirmation-token core (+ κ=0 edges) | **BUILD FIRST** |
| **SHIELD** (adversarial defense) | Partly — mostly ARMOR-hardening | **κ=1** structural rails (provenance/allowlist/hash/cert); **κ≈0** injection-*intent* detection | **BUILD the κ=1 rails as ARMOR-hardening; the rest = abstain-and-escalate.** NOT a "weapon." |
| **SHOES** (mobility bundle) | No — 5 unrelated things in a costume | mixed per-part | **DISSOLVE** into independent components (below) |
| **WHETSTONE** (self-re-audit) | No — **circular** (violates audit≠generator) | n/a | **KILL** as self-audit; it's already covered by the external cross-model audit rule |
| HORSE/BANNER/VISOR/SCABBARD/SADDLEBAGS | No — engineering or policy, not capabilities | — | fold into existing layers; don't reify |

---

## 2. GLOVES — safe actuation (BUILD FIRST; the only genuinely-new capability)
**Why it's real (red-team agreed):** the BOX today *reasons and produces artifacts*; it does not *act*. ARMOR's
rule is "abstain when uncertain about a **claim**." Actuation needs a different rule: **"require explicit
authorization before an irreversible state change,"** because irreversible outward actions have an asymmetric
cost ARMOR was never built for. This is the highest-stakes gap the moment the BOX touches computer-use / APIs /
files / money.

**The κ=1 core (this is verifiable — build it as a frozen gate):**
- **Reversibility + blast-radius classifier.** Every tool call tagged R0(reversible)→R3(irreversible-broad) ×
  B-local/project/external **from the tool's *declared* schema, never the model's self-report** (CVE-2025-53773:
  an agent edited its own approval settings — *the agent must not be able to downgrade its own action's risk*).
- **Confirmation-token gate (κ=1).** R2+/B-external ⇒ a signed confirmation **bound to the exact parameters +
  an expiry**; the gate machine-checks the token before the call fires. Exact, non-gameable.
- **Dry-run → commit (κ=1 structure).** R1+ actions preview their effect (real `dry_run` or a schema simulation
  with a declared accuracy), commit references the previewed artifact's hash.
- **Append-only actuation ledger**, enforced *outside the agent's write scope* (the agent cannot rewrite its own
  audit log — the sharpest CVE-2025-53773 lesson).

**κ=0 edges (abstain, don't fake):** "is this email blast R2 or R3?" boundary calls; whether a *permitted* tool's
server is compromised. → flag + human step-up, never silent.
**Honest ceiling:** reduces catastrophic irreversible error; does not eliminate misdeclared tool metadata or
infra-level log tampering. Source: OWASP AI-Agent Security Cheat-Sheet; CVE-2025-53773; arXiv 2601.08012.

## 3. SHIELD — reframed as ARMOR-HARDENING + a thin κ=1 rail (NOT a weapon)
The red-team is right that "active vs passive defense" is rhetoric, and that **injection/jailbreak detection is
κ≈0** (an adversarial input is *defined* by evading detection — no cheap exact verifier exists; NIST AI 100-2:
80% attacker success at 25 tries). So SHIELD does **not** ship as a weapon. But the Security dept found a genuine
sliver that **is κ=1 and the BOX lacks today** — structural rails, not intent-guessing:
- **Provenance labeling (κ=1 label).** Tag every context span SYSTEM / USER / ENV(external) at ingestion; the
  wrapper controls the label so attacker text can't relabel itself. (Model *compliance* with the label is κ<1 —
  stated honestly.)
- **Verifier taint-rail (κ=1).** **A weapon's verifier is NEVER fed ENV/attacker-controlled natural language.**
  Its inputs = the candidate object + the frozen verifier code + the system spec. This protects all 12 weapons
  from being *talked into* a false certificate — the analog of "auditor ≠ generator," applied to inputs.
- **Tool-cape / least-privilege (κ=1 allowlist match).** A task-scoped, signed tool allowlist the model cannot
  self-elevate (counters tool-description poisoning + excessive agency; MiniScope arXiv 2512.11147).
- **Certificate anti-replay (κ=1 hash+sig).** Every weapon cert is `{object_hash, verifier_id+version, ts, result}`;
  re-checked before downstream use so a stale/forged "PASS" can't be replayed onto a new object.
- **Everything else (injection intent) = κ=0 → abstain-or-escalate**, never an LLM "injection detector" trusted as
  truth (that's circular — an LLM judging attacks on an LLM).

**Net:** SHIELD = 4 small κ=1 rails folded into ARMOR + the Registrar, plus an honest κ=0 abstention rail. Real,
buildable, and **honestly labeled as hardening, not a new offense capability.** Sources: OWASP LLM01:2025; NIST
AI 100-2 E2025; arXiv 2602.22724 (AgentSentry), 2603.18063 (MCP-38).

## 4. SHOES — DISSOLVED into 4 independent components (the bundle was dishonest)
"Mobility" jammed 5 unrelated capabilities into one costume. Split, each with its own κ:
- **(a) Calibration / "footing" check — κ≈0 → ARMOR.** Cross-paraphrase disagreement + unverified-claim count is
  machine-checkable; the *uncertainty verdict* is judgment. Use it to route up the ladder or abstain. Honest: it
  *reduces* confident-wrongness, can't eliminate it. (arXiv 2502.11021.)
- **(b) Ratcheting verified-memory — INFRA, κ=high only for already-verified entries.** Persist *machine-verified*
  results (with method + a TTL + a staleness re-check) so sessions stop re-walking ground. Unverified "I recall…"
  entries are leads, not facts. The known failure (mem0 2026): systems *replace* facts instead of modeling change
  → staleness. Mandatory TTL + re-verify-on-read for high-stakes.
- **(c) Route-planner + stuck-detector — κ=1 routing, κ<1 strategy.** Pick the cheapest ladder rung that clears the
  bar (industry: ~67% cost cut routing ~14% to frontier); extend the existing saturation tripwire to force a
  strategy switch when *verified-fact delta = 0*. Guard the documented failure: **silent quality regression** on a
  misroute → the (a) footing-check is the backstop + a pre-merge eval gate over 50–500 cases.
- **(d) Domain-bootstrap (new-weapon scaffolder) — the one with real new leverage; κ=1 validation slice.** Given a
  new problem class, search for an existing exact verifier (SAT/SMT/type-checker/benchmark), **instantiate it and
  RUN it on known-answer cases** — passes ⇒ register a κ>0 department; no verifier found in N tries ⇒ record
  "κ=0, ARMOR-only" in memory so it isn't re-attempted. *Never* accept a self-reported "this verifier works."
  This is how the arsenal grows from 12 toward broad coverage **without faking κ.**

---

## 5. WHAT'S ACTUALLY MISSING — the red-team's best contribution (highest value of all)
None of SHIELD/SHOES/GLOVES covers these, and they matter most for "robust across scenarios":

- **G1 — Verifier adversarial-probing (the BOX's single point of failure). HIGHEST VALUE.** The whole project
  rests on the claim that each weapon's κ>0 gate is *actually exact and non-gameable.* That claim is itself
  **unverified.** Build an independent red-team process (different model + different authors) that tries to
  construct objects which **pass a verifier but are wrong.** This is the BOX auditing its own immune system.
  (Note: SYMBOLICA's branch-cut skip-bug and the 0-pp false +25pp that PROOFSMITH/CODEFORGE caught are exactly
  this failure class found *by luck*; G1 makes it systematic.) This is a real meta-weapon with a κ=1 outcome (a
  counterexample that passes the gate either exists or doesn't).
- **G2 — Failure-mode taxonomy + per-class abstention protocol.** ARMOR is one undifferentiated gate. Robustness
  needs a named taxonomy (overconfidence / hallucination / specification-gaming / distribution-shift / branch-cut
  / convergence) each wired to its own mitigation. Makes abstention *operational* instead of vague. Unglamorous,
  cheap, high-leverage; fits ARMOR.
- **G3 — Compositional / scope-creep authorization (pairs with GLOVES).** A sequence of individually-small,
  individually-reversible authorized actions can compose into a large irreversible unauthorized effect (the
  "galaxy-brained" failure). GLOVES gates *each* action; G3 gates the *composition* (a running blast-radius budget).

## 6. KILL LIST (stated plainly, per honesty rules)
- ❌ **"Best for any world-case scenario"** — dishonest; replaced by §0.
- ❌ **SHIELD as a weapon / a κ>0 offense capability** — injection detection is κ=0; ship only the κ=1 rails as armor.
- ❌ **SHOES as a single deliverable** — can never be "done" or benchmarked as a unit; dissolved into §4.
- ❌ **WHETSTONE as self-re-audit** — circular, violates audit≠generator; the external cross-model audit already
  covers the honest version. (If wanted, it *is* G1 — but G1 is external, not self.)
- ❌ Reifying HORSE/BANNER/VISOR/SCABBARD/SADDLEBAGS as kit — they're existing engineering/policy, not capabilities.

## 7. Prioritized build order (each item runs the SAME box discipline: gate-FIRST → demo w/ committed predictions → cross-model audit ≠ generator → register; a weapon ADDED = capability EXPANSION, never a ≥10% promotion)

> **✅ STATUS 2026-06-20 — ALL 8 BUILT + VERIFIED (EVOLUTION_LOG C48).** Built gate-first via a multi-agent
> Workflow (Opus builders → Sonnet auditors ≠ generator), fixed, and independently re-verified by the orchestrator
> (every selftest + demo re-run by hand; never trusting an agent self-report). Each ships a frozen gate +
> adversarial selftest + committed-prediction demo + fetched GROUNDING + cross-model AUDIT.md in
> `Expanding_Frontiers/weapons/<dir>/` (`crucible · gloves · shield · triage · bootstrap · vault · composeauth ·
> shoes_routing`). **The cross-model audit found REAL false-accepts the builders' own selftests missed** (COMPOSEAUTH
> negative-blast, GLOVES fake-dry-run, VAULT in-memory lead→fact, TRIAGE `{'ok':1}`, BOOTSTRAP malformed-bar,
> CRUCIBLE spurious-kill) → **all fixed with permanent regression tests; an independent re-audit confirmed 6/6
> exploits genuinely dead (ALL-CLOSED), 8/8 selftests green.** HONEST: first builds, un-A/B-tested; capability
> EXPANSION (GLOVES acts on the world; CRUCIBLE probes our own gates), NOT a ≥10% promotion; the ratchet stays OPEN
> at v3. Demos: GLOVES 17/17 · VAULT 19/19 · COMPOSEAUTH 13/13 · TRIAGE 8/8 · SHOES 6/6 · CRUCIBLE planted-bugs
> caught + clean real-gate sweep · BOOTSTRAP found/abstained correctly.
1. **G1 — Verifier adversarial-probing → "CRUCIBLE"** (protects all 12 existing weapons; highest risk-reduction;
   κ=1 KILL outcome). **KICKOFF DRAFTED + cross-model-audited (READY-WITH-FIXES, fixes folded in):**
   `Expanding_Frontiers/weapons/CRUCIBLE_WEAPON_KICKOFF.md`. Honest scope from the audit: genuine independent-oracle
   false-accept hunting is realistic for only ~5–6 of 12 gates (CODEFORGE/PSYMETRIX/TRIALGUARD/FACTHARNESS/REDCELL/
   capset); SYMBOLICA & OPTIMA are metamorphic-primary (their gates ARE already multi-method, so a 3rd re-run isn't
   independent); guarded-κ weapons (ECONOMETRIX) are declined.
2. **GLOVES κ=1 core** (actuation gate). **KICKOFF DRAFTED + audited (READY-WITH-FIXES, fixes folded):**
   `GLOVES_KICKOFF.md`. Audit fixed 1 BROKEN (unknown tool → default-deny) + 7 WEAK (fail-closed, κ=1 bounded to
   "within the registry", signing-key as the boundary, 12 self-tests, injection-initiated-CONFIRM gap).
3. **SHIELD κ=1 rails** as ARMOR-hardening. **KICKOFF DRAFTED + audited (READY-WITH-FIXES):** `SHIELD_KICKOFF.md`.
   Audit: best honesty framing of the kit; the VERIFIER TAINT-RAIL is the single highest-value piece (hardens all 12).
4. **G2 — Failure-taxonomy → "TRIAGE"** (makes ARMOR operational). **KICKOFF DRAFTED + audited:** `FAILTAXONOMY_KICKOFF.md`.
5. **SHOES-(d) domain-bootstrap → "BOOTSTRAP"** + **SHOES-(b) ratcheting memory → "VAULT"**. **KICKOFFS DRAFTED +
   audited:** `DOMAINBOOTSTRAP_KICKOFF.md`, `RATCHETMEMORY_KICKOFF.md` (VAULT = joint-best honesty framing).
6. **G3 — compositional authorization → "LEDGER-BUDGET"** (blocked until GLOVES' ledger API is frozen). **KICKOFF
   DRAFTED + audited (cleanest exact-arithmetic gate):** `COMPOSEAUTH_KICKOFF.md`.
7. **SHOES-(a) calibration + (c) route-planner.** **KICKOFF DRAFTED + audited (was NEEDS-REWORK → fixed: κ honesty,
   misroute self-test, per-track stuck-definition):** `SHOES_ROUTING_KICKOFF.md`.

**STATUS 2026-06-20: all 8 kit pieces KICKED OFF (specs drafted + independently cross-model audited + fixes folded);
NONE BUILT yet.** Each kickoff is a fresh-chat build task that runs the full box discipline (gate-first → committed-
prediction demo → cross-model audit → register). Recommended build order = this list; hard dependency: G3 after GLOVES.

## 8. Honest ceiling of the whole plan
This is a roadmap, not a result. Every piece above is **un-A/B-tested**; the κ labels are design intent, not yet
machine-proven. The genuinely-new *capability* is GLOVES (acting in the world) and the genuinely-new *safety* is
G1 (probing our own verifiers) — the rest is hardening, efficiency, and honest book-keeping. None of it makes the
model smarter; it makes the BOX **harder to fool, safer when it acts, and more honest about what it can't do** —
which is the only defensible meaning of "best across scenarios."
