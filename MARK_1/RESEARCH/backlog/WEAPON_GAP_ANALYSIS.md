# WEAPON GAP ANALYSIS — do we need more weapons? (2026-06-20)

> **STATUS: a κ=0 STRATEGIC JUDGMENT, not a verified result.** No A/B, no shared arena; the ≥10% capability
> ratchet is untouched (stays OPEN at v3). What IS grounded: the per-domain *verifier-existence* facts (web-fetched)
> and the built-state (machine-verified by `ls` + reading `WEAPONS_BACKLOG.md`). The *prioritization* is judgment.

## How this was produced (dogfooding the box)
A background **Workflow** (`wf_ef5d3746-3d4`, 28 agents): **(1) Research** — 12 candidate weapon domains NOT in the
plan, each grounded by web-fetch against the κ-test (does a cheap EXACT non-gameable verifier exist that re-checks
the returned object?). **(2) Kill** — a separate **Sonnet** skeptic (≠ the Opus researcher) tried to refute each as
a genuine new weapon. **(3) AuditPlan** — 3 independent Sonnet audits of the existing weapons + kit + a
verifier-mechanism coverage map. **(4) Synthesize** — an Opus Dean integrated. Then a **second independent Sonnet
audit** stress-tested the conclusion, and the orchestrator **machine-verified** the load-bearing facts (built-state,
`mpmath.iv` limits, `redcell/auth_gate.py`). Three independent passes + machine checks; the final audit *disagreed*
on one point (below) — a healthy non-rubber-stamp signal.

## 1. ONE-LINE ANSWER
**Barely. The planned arsenal is essentially complete (12 weapons + 8 kit pieces, machine-verified). Of 12
candidate new domains, 10 fold or decline; exactly ONE genuinely-distinct new κ=1 mechanism survived every pass
(ENCLOSE, rigorous interval/enclosure numerics). The higher-value work is HARDENING what exists — running CRUCIBLE
against the gates — not chasing new domains. The arsenal is near verifier-MECHANISM saturation.**

## 2. WHERE THINGS STAND (machine-verified)
- **12 weapons BUILT** (`WEAPONS_BACKLOG.md` = "BUILT (12)"): Frontier Construction Engine, PROOFSMITH, OPTIMA,
  SYMBOLICA, CODEFORGE, PSYMETRIX, SOCIUS, ECONOMETRIX, TRIALGUARD, FACTHARNESS, REPRO-ML/BENCHWATCH, REDCELL.
- **8 KIT/equipment pieces BUILT** (dirs with 777–1121 LOC + gates/selftests): crucible, gloves, shield, triage,
  bootstrap, vault, composeauth, shoes_routing. *(The "none built yet" line in `KIT_EXPANSION_PROPOSAL.md` §7 is
  now STALE — concurrent sessions built them.)*
- **Verifier-mechanism coverage:** the 12 weapons realize **7 deep mechanism families** — formal-kernel proof
  (PROOFSMITH) · solver-duality certificate (OPTIMA) · execution+differential tests (CODEFORGE/REPRO-ML) ·
  multi-method agreement (SYMBOLICA) · exact-arithmetic forensics (PSYMETRIX/TRIALGUARD GRIM) ·
  reproduce-and-robustness (SOCIUS/ECONOMETRIX) · construction-search+object-recheck (Frontier) — plus narrower ones
  (source-grounding FACTHARNESS, binary-oracle REDCELL).

## 3. THE 12-DOMAIN HUNT — results (grounded → Sonnet-killed)
| domain | verdict | one-line reason |
|---|---|---|
| **validated_numerics → ENCLOSE** | **BUILD_NEW** ✅ | rigorous interval/enclosure = a *containment proof*, a κ=1 mechanism the arsenal lacks (distinct from SYMBOLICA agreement) |
| bioinformatics → BIOVERIFY | BUILD (scoped) | only alignment-DP + HMM-DP recompute are κ=1; phylo-likelihood/MolProbity/variant-concordance are NOT bit-reproducible → guarded |
| game_theory → GAMETHEORY | ON WATCH | equilibrium/stable-matching/fairness checks are κ=1, but correlated-eq = OPTIMA's LP machinery → needs hard API fencing + exact rationals |
| numerical_pde | ON WATCH | MMS convergence-order is κ-GUARDED (ECONOMETRIX-class), not sharp; asymptotic-regime + logic-error caveats |
| cryptography | FOLD | every slice partitions across Frontier / PROOFSMITH / CODEFORGE / REDCELL; orphan = a stdlib wrapper |
| chemistry | FOLD → SYMBOLICA | element-matrix nullspace over ℚ is a standard SymPy op; high-value chem (retrosynthesis/oxidation-state) is κ=0 |
| quantum | FOLD | Clifford-tableau = Frontier re-check / CODEFORGE+Stim; min-distance NP-hard; general equiv QMA-complete |
| geometry | FOLD | Wu/Gröbner = SYMBOLICA; synthetic proofs = PROOFSMITH; constructibility = SYMBOLICA; adapter is a thin front-end |
| coding_information_theory | FOLD → Frontier | coding/packing records ARE Frontier's scope; covering-radius Π₂ᵖ-complete; large min-weight NP-hard |
| formal_systems / temporal-logic | FOLD / DECLINE | AIGER-safety = PROOFSMITH SAT/SMT; the distinctive TLA+/SPIN liveness slice has NO standardized independent certificate → building it = tool-construction theater |
| financial_model_units_audit | FOLD | recompute-and-tie = GRIM-class (PSYMETRIX); "is the model right" = κ=0 |
| protocols_smartcontracts | FOLD / DECLINE | Certora half re-validates spurious counterexamples (κ≈0); TLA+ trace-replay is narrow, folds toward PROOFSMITH |

## 4. THE ONE CLEAR NEW WEAPON — ENCLOSE (backlog #10)
- **Mechanism:** interval / ball arithmetic with **outward (directed) rounding** (inclusion property) + an
  interval-Newton / Krawczyk existence-uniqueness gate. The output `[a,b]` **provably contains** the true value —
  a **containment PROOF**, not corroboration.
- **Why it is NOT SYMBOLICA (the load-bearing claim — survived the hardest attack):** SYMBOLICA verifies by
  *agreement* of independent CAS families, which the interval-arithmetic literature explicitly calls *corroboration,
  not proof* — a shared blind spot (e.g. a branch-cut error) fools all engines at once (this failure class is real:
  SYMBOLICA's own audit caught a branch-cut bug). An enclosure is κ=1 by the IEEE rounding-mode invariant, a
  *different mechanism entirely*. **Machine-confirmed distinct:** `mpmath.iv` gives outward rounding for basics but
  **lacks `iv.quad`/`iv.zeta`** → not a drop-in; ENCLOSE needs `python-flint`/Arb (not yet installed).
- **Honest scope (from the audit):** it is **COMPLEMENTARY to SYMBOLICA, not a replacement** — SYMBOLICA keeps
  symbolic/algebraic work; ENCLOSE adds certified numeric *bounds*. Surface = **moderate** (rigorous ODE/PDE bounds,
  certified-float programs, validated quadrature), not "broad." κ=1 degrades to ≈0.95 under `-ffast-math` → pin a
  rounding-safe toolchain.

## 5. THE PRIORITY — harden before expand
The plan-audit found the existing priority sound; **5 of the top-6 slots are finish-and-harden, not new domains:**
1. **Run CRUCIBLE against the existing gates (HIGHEST).** It tests the single unverified load-bearing assumption
   under the *entire* arsenal — that each weapon's gate is *actually* exact and non-gameable. Justified: build-time
   audits already caught HIGH-severity gate defects in ~6 of 12 weapons (REDCELL fail-open, SYMBOLICA branch-cut,
   CODEFORGE 2× false-accept, FACTHARNESS Unicode-minus, TRIALGUARD honesty-checker). **Honest limit:** CRUCIBLE
   gets genuine *independent-oracle* probing on only ~5–6 of the 12 gates; the rest get weaker metamorphic probing.
2. **Resolve the CRUCIBLE↔SHIELD taint-rail interface** (CRUCIBLE's probes feed gates from outside; SHIELD's
   taint-rail would block them unless CRUCIBLE is a trusted caller) and **sequence SHIELD's VERIFIER-TAINT-RAIL first.**
3. **Tighten the newest weapons' disclosure** (no soundness bugs): REDCELL "fails-closed" is conditional on the
   orchestrator populating `requested_category` (confirmed in `weapons/redcell/auth_gate.py`); FACTHARNESS κ=0.7
   F-CITE-only failure blocks shipping (disclose); REPRO-ML κ≈0.8 = proxy-gap not indeterminism (disclose).
4. **Build ENCLOSE** — the one clear new κ=1 mechanism.
5. **Scoped BIOVERIFY**, then the fenced on-watch candidates.

## 6. THE κ=0 BOUNDARY — do NOT build as a weapon (anti-theater)
Crypto *offense* outside an authorization-gated frozen challenge; TLA+/SPIN concurrent *liveness* (no standardized
independent certificate exists); Certora/EVM "proven safe" (spurious counterexamples → κ≈0); high-value chemistry
(retrosynthesis, oxidation-state), exact code min-distance (NP-hard), covering-radius (Π₂ᵖ-complete), "is the
financial model *right*"; and the standing list — **law, ethics, policy, forecasting, design taste, clinical
*efficacy*, "is this writing good."** Armor + abstain there, never a weapon.

## 7. HONEST CEILING
- **This is a κ=0 strategic judgment, not a machine-verified result.** Grounded: built-state, ENCLOSE's absence +
  distinctness (machine-checked), and the per-domain verifier-existence facts (web-fetched). The ranking is judgment.
- **The final audit DISAGREED on one point (kept, not softened):** the synthesis claimed "4 structurally-absent
  mechanisms"; the auditor showed only **~2 are genuine** (interval-enclosure G1, temporal-logic model-checking G2)
  — **crypto-witness folds into CODEFORGE** (run the verifier differentially) and **conservation/dimensional is a
  SYMBOLICA sub-mode**, not a missing mechanism. This makes "near saturation" *more* true. Of the 2, only G1
  (ENCLOSE) is build-worthy now; G2 is low-surface for this arsenal AND lacks κ=1 certificate infra (theater risk).
- **One niche κ=1 mechanism the 12-domain study omitted:** Alloy/relational bounded model-finding (counterexample
  within a scope). Genuine but low-priority; logged for completeness, not recommended now.
- **Two/three independent passes agreeing is a shared-blind-spot RISK, not a guarantee.** The new-weapon count
  could be off if the passes share an unexamined notion of "distinct mechanism."
- **A weapon ADDED = capability EXPANSION, never a ≥10% promotion** (no shared non-circular A/B arena). **The
  capability ratchet stays OPEN at v3.** ENCLOSE/BIOVERIFY, if built, are integration stamps like the existing 12.

**Pointers:** backlog `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` (#10 ENCLOSE, #11 on-watch); kit plan
`Next/KIT_EXPANSION_PROPOSAL.md`; registry `Expanding_Frontiers/HELMET/registry.json`. Verified facts spot-checked
against `weapons/redcell/auth_gate.py` and live `mpmath.iv`.
