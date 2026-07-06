# HANDOFF — resume here to implement (b) ENCLOSE + (c) run CRUCIBLE
*Written 2026-06-20 at the wrap of the weapons-arsenal research session. Self-contained: a fresh chat can read
this + the linked docs and pick up cold. STATUS: research STOPPED by the PI ("maybe we will improve later"). No
ratchet move; Present box = v5.2; the ≥10% CAPABILITY ratchet stays OPEN at v3.*

> **⟵ UPDATE 2026-06-20 (later same day): THIS HANDOFF IS COMPLETE — both (b) and (c) DONE.**
> **(c) CRUCIBLE RUN — DONE.** Ran CRUCIBLE against all 11 κ>0 gates → **4 confirmed defects found, patched, and
> frozen as regression self-tests** (factharness ×2, optima ×2, symbolica, socius + a socius overflow follow-up),
> cross-model audited, orchestrator-re-run **5/5 selftests green**. 7 gates SURVIVED-to-budget; 1 declined.
> Report: [`../../ARSENAL/weapons/crucible/CRUCIBLE_RUN_REPORT.md`](../../ARSENAL/weapons/crucible/CRUCIBLE_RUN_REPORT.md) §7.
> **(b) ENCLOSE — BUILT (WEAPON 13).** The infra "UNRESOLVED INFRA QUESTION" below was resolved by machine **in
> mpmath.iv's favor** (iv arithmetic genuinely outward-rounded; `iv.quad` broken → quadrature built on iv; NO
> new dependency, python-flint NOT needed). Gate-first, `selftest_all.py` 24/24 green, demo 9/9, **cross-model
> Sonnet audit SOUND** (no false-accept / 17 attack categories). Home: [`../../ARSENAL/weapons/enclose/`](../../ARSENAL/weapons/enclose/);
> EVOLUTION_LOG C49; backlog #10 ✅. **Both capability EXPANSION, NOT ≥10% promotions — ratchet stays OPEN at v3.**
> **Only remaining Phase-2 item (separate handoff): the HELMET keystone** (`../../ARSENAL/HELMET/STATE_AND_HANDOFF.md`).
> **Optional CRUCIBLE-v2 follow-up:** the metamorphic-only gates (optima/proofsmith/reproml/symbolica + socius
> multiverse) got NO false-accept hunt; proofsmith's Lean kernel path was never exercised — needs Lean + foreign oracles.*

---

## 0. What this session produced (so the trail is complete)
1. **Built WEAPON #6 — TRIALGUARD** (clinical-trial & biostat rigor): `Expanding_Frontiers/weapons/trialguard/`.
   Gate green; cross-model (Sonnet) audited SOUND; logged `Legacy/EVOLUTION_LOG.md` C43. The strictest honesty
   rail in the arsenal (INCONSISTENCY/ANOMALY ≠ FRAUD). Carlisle baseline screen + hand-rolled Cox/KM + GRIM reuse.
2. **Ran the weapon-gap analysis** answering "do we need more weapons?" → `Next/WEAPON_GAP_ANALYSIS.md` (the
   load-bearing doc for this handoff). Method: a 28-agent Workflow (`wf_ef5d3746-3d4`) — 12 grounded domain
   researchers → Sonnet adversarial kills → 3 Sonnet plan-audits → Opus synthesis → a 2nd independent Sonnet
   conclusion-audit → machine verification of the facts.
3. **Verdict:** the planned arsenal is essentially COMPLETE; only ONE clearly-distinct new weapon survived
   (ENCLOSE); the higher-value move is HARDENING (run CRUCIBLE). Added **ENCLOSE as backlog #10** + an **#11
   on-watch** list to `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md`.

## 1. Current arsenal state (machine-verified at wrap, 2026-06-20)
- **12 weapons BUILT** (`WEAPONS_BACKLOG.md` "BUILT (12)"): Frontier Construction Engine, PROOFSMITH, OPTIMA,
  SYMBOLICA, CODEFORGE, PSYMETRIX, SOCIUS, ECONOMETRIX, TRIALGUARD, FACTHARNESS, REPRO-ML/BENCHWATCH, REDCELL.
- **8 KIT pieces BUILT**: crucible, gloves, shield, triage, bootstrap, vault, composeauth, shoes_routing.
- **ENCLOSE: NOT built** (confirmed absent — the one clear gap).
- ⚠ **Concurrency note:** multiple sessions were editing the backlog/registry the same day. Re-`ls` the weapons
  dir and re-read `WEAPONS_BACKLOG.md` before acting — the count may have moved past 12.

---

## (b) BUILD ENCLOSE — rigorous / validated numerics (the one clear new weapon)

**What it is.** A weapon that returns a **guaranteed enclosure `[a,b]` provably containing the true value** of a
numeric quantity — verified definite integrals, root existence/uniqueness in a box, validated ODE/IVP flows,
rigorous global optimization over the reals, floating-point round-off bounds. The verifier is a **containment
PROOF** (interval/ball arithmetic with outward/directed rounding + an interval-Newton / Krawczyk
existence-uniqueness gate), which is **categorically sharper than SYMBOLICA's multi-method AGREEMENT** (agreement =
corroboration; a shared blind spot fools all engines — the branch-cut bug SYMBOLICA's own audit caught). It is the
sibling of SYMBOLICA and **complementary, not a replacement** (SYMBOLICA keeps symbolic/algebraic; ENCLOSE adds
certified numeric bounds).

**⚠ UNRESOLVED INFRA QUESTION — settle this FIRST (machine, don't assert).** The gap-analysis said "needs
`python-flint`/Arb because `mpmath.iv` lacks `iv.quad`." A wrap-time machine check **contradicted that**:
`python-flint` is NOT installed, but `mpmath.iv` IS present and `hasattr(mpmath.iv, 'quad') == True`. So:
1. First, **empirically probe what `mpmath.iv` actually delivers** — does `mpmath.iv` give outward-rounded
   interval results for `+ - * /`, `sqrt/exp/log`, and `quad` (verified quadrature)? Write 5 lines, run them,
   check that the returned intervals truly bracket known constants (π, √2, ∫₀^∞ e^{-x²}=√π/2) and that a
   too-narrow interval is detectable.
2. If `mpmath.iv` suffices for a v0, build on it (no new dependency). If it doesn't (e.g. no rigorous special
   functions / ODE enclosures), install `python-flint` (Arb-backed ball arithmetic) and use that. **Do not assume
   either way — the machine decides.**

**Build it box-style (clone SYMBOLICA's shape — `Expanding_Frontiers/weapons/symbolica/`):**
1. **PLAN** — `weapons/enclose/SPEC.md` + κ-profile + the honest "containment-proof vs agreement" framing +
   the κ=0 boundary (it certifies the COMPUTED enclosure, NOT the modeling step). Commit demo predictions FIRST.
2. **GROUND** — fetch + cite the method anchors (fundamental theorem of interval arithmetic / inclusion property;
   interval-Newton & Krawczyk existence-uniqueness; Tucker's Lorenz proof; Hales/Flyspeck; INTLAB/Arb docs).
   Record in `enclose/GROUNDING.md`. Re-confirm the infra probe result here.
3. **BUILD THE GATE FIRST** — `enclose_gate.py`: ACCEPTS a true enclosure, **REJECTS a too-narrow/false box**
   (the verifier must be able to FAIL), and ABSTAINS on malformed input / when rounding-mode safety can't be
   guaranteed. Self-tests green before any result counts.
4. **KILLER DEMO** (`demo_*/`, predictions committed first) — e.g. a verified ∫, a Krawczyk root
   existence-uniqueness certificate, a validated ODE step; plus the gate REJECTING a fabricated narrow interval.
5. **VERIFY INDEPENDENTLY** — cross-model audit (Sonnet/Haiku ≠ the Opus generator; never Opus-audits-Opus):
   re-derive enclosures with its own code, hunt for a false-accept (a "verified" box that does NOT contain the
   truth — the cardinal soundness failure), red-team the "complementary-not-replacement" honesty framing.
6. **REGISTER** — `Next/BOX_V5.md` (new Weapon + router branch), `HELMET/registry.json` (NAT_SCI, sibling of
   SYMBOLICA), honest `EVOLUTION_LOG` entry (**a weapon ADDED = capability EXPANSION, NOT a ≥10% promotion**),
   flip `WEAPONS_BACKLOG.md` #10 STATUS → ✅.

**Honest ceiling to state every run:** κ=1 holds **under directed rounding ONLY** — degrades to ≈0.95 under
`-ffast-math` (pin a rounding-safe toolchain, reject fast-math builds). Surface = **moderate, not broad**.
Certifies the computed enclosure, not the model. Containment-proof, not "the answer is interesting."

---

## (c) RUN CRUCIBLE against the existing gates (the highest risk-reduction move — HARDENING)

**What it is + why it's #1.** CRUCIBLE (`Expanding_Frontiers/weapons/crucible/`, already built) is the
meta-weapon that tests the **single unverified load-bearing assumption under the entire arsenal**: that each
weapon's κ>0 gate is *actually* exact and non-gameable. It tries to construct objects that **PASS a gate but are
WRONG (a false-accept)**. Today every "κ=1" label across the 12 weapons is **asserted, not adversarially proven** —
and build-time audits already caught HIGH-severity gate defects in ~6 of 12 weapons (REDCELL fail-open, SYMBOLICA
branch-cut skip, CODEFORGE 2× false-accept, FACTHARNESS Unicode-minus, TRIALGUARD honesty-checker), each found
*by luck*. CRUCIBLE makes that hunt systematic.

**How to run it (entry points, verified to exist):**
- `python3 crucible/selftest_all.py` — confirm the harness gate is green first.
- `crucible/crucible_harness.py` — the runnable probing harness; `crucible/crucible_router.py` selects targets;
  `crucible/oracles/` holds the independent oracles; `crucible/demo_planted_bugs/` is the worked demo.
- Read `crucible/README.md` + `crucible/SPEC.md` for the exact invocation and the per-gate probe protocol.

**Honest scope (do NOT overclaim — from the plan-audit):** genuine **independent-oracle** false-accept hunting is
realistic for only **~5–6 of the 12 gates** (CODEFORGE, PSYMETRIX, TRIALGUARD, FACTHARNESS, REDCELL, capset).
SYMBOLICA & OPTIMA are **metamorphic-primary** (their gates are already multi-method, so a 3rd re-run isn't truly
independent); guarded-κ weapons (ECONOMETRIX) are declined. Report metamorphic coverage ≠ full-differential
false-accept coverage — a run that only did metamorphic probing must NOT claim "all 12 survived full differential."

**Resolve these BEFORE/at run time:**
1. **CRUCIBLE↔SHIELD taint-rail coordination.** SHIELD's verifier-taint-rail (`shield/shield_gate.py`,
   `shield/shield_router.py`) blocks ENV/attacker-controlled input from weapon gates. CRUCIBLE feeds gates from
   outside — so **CRUCIBLE must be registered as a trusted (SYSTEM/USER) caller** or the taint-rail blocks its own
   probes. Settle this in CRUCIBLE's or SHIELD's SPEC first.
2. **KILL → gate-patch protocol.** When CRUCIBLE finds a false-accept, the fix has a clear owner: **patch the
   owning weapon's gate AND freeze the exhibit as a regression self-test** (the same pattern every weapon used for
   its audit fixes). Don't let a KILL sit without a patch owner.

**Outcome.** Each CRUCIBLE KILL is a real κ=1 result (a concrete object that passes a gate but is wrong) → patch +
regression-test. A clean sweep (no false-accept after honest adversarial effort) upgrades that gate's κ label from
*asserted* to *adversarially-tested*. Either way it is the highest-value next step.

---

## 2. Key reference docs (read these to resume)
- **`Next/WEAPON_GAP_ANALYSIS.md`** — the full analysis (12-domain table, ENCLOSE case, κ=0 boundary, priority,
  honest ceiling, the audit disagreement on G3/G4). THE doc for this handoff.
- `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` — #10 ENCLOSE, #11 on-watch (BIOVERIFY scoped / GAMETHEORY
  fenced / NUMERICAL_PDE guarded), the κ=0 NOT-WEAPONS list, and the per-weapon box-discipline recipe.
- `Next/KIT_EXPANSION_PROPOSAL.md` — the 8-kit plan (CRUCIBLE/GLOVES/SHIELD/… ) and their honest κ labels.
- `Expanding_Frontiers/weapons/symbolica/` — the cleanest TEMPLATE to clone for ENCLOSE (sibling NAT_SCI weapon).
- `Expanding_Frontiers/weapons/crucible/` — the meta-weapon to run for (c).
- `CLAUDE.md` / `RATCHET.md` — the box method + the hard rules (10% threshold, research flow, κ>0 doctrine).

## 3. Non-negotiable rails for whoever resumes
- **Box discipline per build:** PLAN → GROUND (fetch, don't assert) → GATE-FIRST (a verifier that can't FAIL is
  not a verifier) → committed-prediction demo → **cross-model audit ≠ the generator** (Sonnet/Haiku; Fable
  inactive → never Opus-audits-Opus) → register. No win without proof.
- **A weapon ADDED = capability EXPANSION, never a ≥10% promotion.** No shared non-circular A/B arena across
  heterogeneous weapons → the CAPABILITY ratchet stays OPEN at v3. Don't mislabel an addition as a ratchet move.
- **The whole gap analysis is κ=0 strategic JUDGMENT, not a verified result.** Grounded: the verifier-existence
  facts + built-state. The "harden over expand" call and the new-weapon count are judgment — and two/three passes
  agreeing is a shared-blind-spot RISK, not a guarantee. Treat "ENCLOSE is the one gap" as the best current
  estimate, re-checkable, not gospel.
- **The infra claim for ENCLOSE is UNVERIFIED** (mpmath.iv vs python-flint) — settle it by machine before building.
