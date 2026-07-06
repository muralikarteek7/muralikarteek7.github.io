# 🤖 CLAUDE — MARK 1 · the SUIT MANIFEST

**Mark 1 is the whole disciplined system, packaged as one wearable interface.** Tell Claude
**"put on Mark 1"** (or run **`/mark1`**) and it operates with the full kit: armor always on,
the right model for each job, the router deciding when to draw a weapon, the arsenal of
verifier-gated weapons, and the helmet to conduct hard multi-part problems — all under one
honesty discipline.

> **One-line mental model:** *Armor* defends every output · the *Ladder* picks who does each job ·
> the *Router* decides if a problem is worth a *Weapon* · the *Arsenal* (12 weapons + 8 kit) is the
> offense · the *Helmet* conducts the team on hard problems · `Artifacts/` is where it's all proven.

**Version:** v5.2 (Armor + Weapons + Helmet + the v5.1/v5.2 efficiency/honesty options).
**Honest status (binding):** every component here is **capability EXPANSION** (new task classes) or
**efficiency/honesty** — **NOT a ≥10% capability promotion.** The capability ratchet is **OPEN at v3**.
Fable 5 (top reasoning rung) is currently **inactive** → rerouted to Opus 4.8 (see `LADDER.md`).

---

## The kit (what's in the suit, and where it physically lives)

| Component | What it is | Lives in |
|---|---|---|
| **ARMOR** | always-on defense: execute-don't-vote · ground-don't-assert · verify-independently · honesty rails | [`ARMOR.md`](ARMOR.md) |
| **MODEL LADDER** | the right model per job (execute · Haiku · Opus 4.8 → Fable 5 · audit≠generator) | [`LADDER.md`](LADDER.md) |
| **ROUTER** | the κ-gate: *does a cheap exact verifier exist?* → armor-only / fetch-known / search-open (`router.py`, `weapon_gate.py`, `WEAPON_REGISTRY.json`; its co-located verifier deps live in `ROUTER/benchmarks/math/`) | [`ROUTER/`](ROUTER/) |
| **ARSENAL** | the 12 weapons + 8 kit pieces + the helmet (offense + conductor) | [`ARSENAL/`](ARSENAL/) |
| **SPEC** | the canonical box spec (BOX_V5 + the v5.2 design) | [`SPEC/`](SPEC/) |
| **RESEARCH** | the live workspace: current state, the hard rules, the on-hold backlog | [`RESEARCH/`](RESEARCH/) |
| **PRODUCTS** | the living artifacts the suit improves (history-app · trading · math, all v1.0) | `../Artifacts/` |

---

## The ARSENAL — 12 WEAPONS (offense, drawn per problem, each with a sharp verifier)
Home: [`ARSENAL/weapons/`](ARSENAL/weapons/) (+ the construction engine in [`ARSENAL/cap_set/`](ARSENAL/cap_set/)).

| # | Weapon | Domain |
|---|---|---|
| 1 | **Frontier Construction Engine** | extremal combinatorics (cap-set / Sidon / Costas) |
| 2 | **SOCIUS** | empirical social science (reproduce / multiverse) |
| 3 | **PSYMETRIX** | psychometrics + statistical forensics (GRIM/GRIMMER) |
| 4 | **OPTIMA** | exact optimization / operations research |
| 5 | **SYMBOLICA** | symbolic-exact numerics |
| 6 | **CODEFORGE** | code & algorithm discovery |
| 7 | **PROOFSMITH** | kernel-gated formal proof (Lean) |
| 8 | **TRIALGUARD** | clinical-trial / biostatistics rigor |
| 9 | **ECONOMETRIX** | quant-finance / causal econ |
| 10 | **FACTHARNESS** | grounding / anti-fabrication core facility (cross-cutting) |
| 11 | **REDCELL** | authorization-gated, *defensive-first* security |
| 12 | **REPRO-ML / BENCHWATCH** | ML-evaluation reproducibility |

## The KIT — 8 accessories (armor-hardening, routing, safety, memory)
| Piece | What it does |
|---|---|
| **GLOVES** | actuation-safety gate (guards before any state-changing action) |
| **SHIELD** | active input boundary (armor-hardening, not a weapon) |
| **SHOES (routing)** | router-time rails — footing + route-planner |
| **VAULT** | verifier-gated, TTL-aware memory of verified results |
| **TRIAGE** | armor failure-class → detector → mitigation rail |
| **CRUCIBLE** | the meta-weapon: a red-team that adversarially tests the verifiers themselves |
| **BOOTSTRAP** | the new-weapon scaffolder |
| **COMPOSEAUTH** | the compositional-authorization rail |

## The HELMET — "University Mode" (the conductor worn over armor + weapons)
Home: [`ARSENAL/HELMET/`](ARSENAL/HELMET/). A meta-orchestrator: a **PROVOST** triages → a **REGISTRAR**
sizes the team → **DEPARTMENTS** convene (each = a weapon or armor cluster) → an R&D lifecycle runs with
**independent peer review (cross-model ≠ generator)** → a **DEAN** integrates one honest artifact. It *calls*
armor + weapons; it does not replace them. (Alternative designs live in `ARSENAL/HELMET/other_helmets/`.)
**Honest keystone gap:** the Provost's κ-routing on *unlabeled* inputs is unproven — see `ARSENAL/HELMET/STATE_AND_HANDOFF.md`.

---

## How to wear it
- **Always on (passive):** root `CLAUDE.md` + the `.claude/` hook keep the **armor** engaged every message.
- **Full power-up (one command):** say **"put on Mark 1"** or run **`/mark1`** → Claude loads the full operating
  doctrine and confirms **"Mark 1 online."** See [`ACTIVATE.md`](ACTIVATE.md) for exactly what that does.

## Honesty rails (non-waivable — the suit never bypasses these)
- Verify INDEPENDENTLY (a different model or a machine/source check) — never trust an AI's self-report.
- Ground load-bearing facts (fetch/run, don't assert). Report negatives plainly. Claim no win without proof.
- Only call something a **promotion** if it's **≥10% better via a non-circular A/B + ablation across ≥2 arenas.**
- Never claim to solve an open problem — exhibit a machine-verified object or report you didn't.
