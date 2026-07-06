> **Path note (post-Mark-1 reorg):** this file was pulled forward from the old `Next/`. Its internal links point at pre-reorg paths; decode any of them via [`../../../MARK_0/MOVE_LOG.md`](../../../MARK_0/MOVE_LOG.md). Current rules/state live in [`../RULES.md`](../RULES.md) and [`../STATE.md`](../STATE.md).

# Innovation Backlog — the team's live "what's lacking / what's next" radar

**Purpose.** A standing, *current* gap-and-innovation radar — the thing that makes "the research team is also looking at what's lacking and innovating next" continuously true, not just emergent. Reconciles the original v2 design gaps ([`GAPS.md`](GAPS.md) G1–G6, [`ROADMAP.md`](ROADMAP.md) T1–T7) against what was actually *learned* (C12–C20), and lists the open frontier with owners + priority.

**Maintenance rule:** every box version / run updates this file — mark gaps closed, reframe gaps changed, add gaps discovered. Last updated: **2026-06-12** (v5 capability loop — interim verdict; see `benchmarks/V5_INTERIM_VERDICT_2026-06-12.md`).

---

## 0. CURRENT — v5 capability loop outcome (2026-06-12) ⟵ READ FIRST
**The v5 CAPABILITY loop (the `V5_KICKOFF.md` execution-gated-repair thread — distinct from the v5 ARMOR+WEAPONS
*integration* stamp, EVOLUTION_LOG C33) ran STAFF → SURVEY → THEORY/EXPERIMENT. No ≥10% capability gain. The ≥10%
CAPABILITY ratchet stays OPEN at v3** (Present = the v5 ARMOR+WEAPONS box, C33; this loop moved no version, no point
release). Full: `benchmarks/V5_INTERIM_VERDICT_2026-06-12.md`.
- **Lever B (principled aggregation) → KILLED at the design-audit gate** (UNSOUND: only clean arena is one C30 forbids;
  the "new" CK rule is a reparametrization of the owned C20/C27 agreement-gate → ≥10% impossible by construction). $0 spent.
- **Lever E (execution-gated repair) → machine-verified NEGATIVE on construction, 2 model strengths.** repair vs
  matched-budget best-of-3: **Haiku −38pp** (feedback *hurts* — thrashing), **Sonnet +0pp** (tie, partially saturated).
  The feedback is NOT the active ingredient; attempts are. Construction closed as a cheap repair-lever path.
- **The ONE open capability lever is INFRA-GATED, not refuted:** repair in the **strong-model × code (rich-feedback)**
  regime (survey's Live-SWE-agent 77.4%). Needs an **API key + SDK + a contamination-free code bench** (`benchmarks/
  V5_REPAIR_RUNNABILITY_2026-06-11.md`); audit-cleared design frozen at `benchmarks/V5_REPAIR_PREREG_2026-06-11.md §10`.
- **Banked reusable assets** (`benchmarks/v5_repair_probe/`): `verify_cli.py`, `script_solver.py`, `score_batch.py`,
  the two Workflow scripts, all logs. Plus the survey's **CK + C3 aggregator** idea (grounded, unbuilt, *point-release-
  class* per the audit — a refinement of owned prior art, NOT a ≥10% path).
- **Meta-finding (honest):** at this budget/infra, the cheaply-testable capability levers don't clear the bar —
  aggregation collapses into prior art; on crisp combinatorial constraints a cheap algorithm beats the model and feedback
  doesn't beat resampling. The real capability frontier needs infra we lack.
- **REPAIR-ON-CODE (2026-06-12, ~40% budget run) → SATURATION WALL** (`benchmarks/v5_code_repair/RESULT.md`). Built a full
  contamination-resistant code bench + ran repair vs best-of-k on classic AND hard (regex/atoi/calc/decode/simplify)
  problems, Haiku, 3 seeds. **One-shot = 100% everywhere → no failure band → lever untestable at toy scale.** Structural
  catch-22: *any problem I can author a reference for is a memorized classic → one-shot.* The lever's only home =
  **non-memorized hard real-world tasks with rich feedback (SWE-bench-scale)** = the INFRA-GATED bet. Reusable harness banked.
- **CAPTURED EFFICIENCY LEVER — "SubQ-style decomposition + selective context"** (from the PI's SubQ video, 2026-06-12).
  SubQ-the-architecture (sub-quadratic attention) = not implementable (weights) + hype-flagged (vendor-run; lab 83 vs
  prod 65.9 on MRCR v2). BUT the orchestration analog IS our lane: decompose a long/complex task into sub-questions, feed
  each a *minimal relevant context* (B7) + compose. Moves **C (relevance density) / B (cost)** — **point-release-class**
  (efficiency, not a ≥10% capability gain unless decomposition unlocks tasks the monolith can't). Testable on the code
  bench or a long-context arena: decompose-and-compress vs monolithic prompt, measure Q AND B.
  **✅ RAN 2026-06-20 (`benchmarks/v5_subq_decomp/`) — EFFICIENCY POINT-RELEASE candidate (v5.1), NOT a promotion.**
  Generalized across **2 arenas × 3 seeds × N=40** (Haiku, code-computed + independently re-derived truth,
  Sonnet-audited SOUND-WITH-CAVEATS): decompose+compress (C) is **~5× (arena 1) to ~7.7× (arena 2) cheaper** on
  the task-token proxy and **NEVER regressed quality — C ≥ monolith A in every cell, 0 losses in 40 queries** =
  empirical **weak dominance** (→ point-release class per RATCHET; ratchet does NOT move). **Honest attribution:**
  the big quality lifts (arena 1: A 0.42/0.50 → C 1.00) are **mostly the OWNED v3 armor** (offload checkable
  arithmetic to code). The genuinely NEW ingredient (selective context, B7) reliably buys the **cost win**, but
  its quality *benefit* (isolated in arena 2, no code confound) is **1/16 queries — at the noise floor** (seed 7
  saturated). Cost has 3 views: per-query proxy ~5–8×, but only **~1.4× end-to-end** once fixed harness overhead
  is counted. **HARDENED 2026-06-20 (single-model + synthetic-corpus caveats retired):** a **Sonnet tier
  saturates both arenas (A=C=1.0) → the quality benefit is WEAK-MODEL-ONLY; the cost win is model-independent**;
  a **natural-prose corpus** left monolith unchanged (0.417) and C at 0.917 (one genuine extraction slip from
  messier text) — **C still weak-dominated A and stayed ~5× cheaper in every condition (0 cases of C<A across
  ~64 instances).** Remaining OPEN caveat: retrieval RECALL when the query key isn't literal. Stamped **point
  release v5.1** (RATCHET + EVOLUTION_LOG C35 + BOX_V5 §1). Verdict: `benchmarks/v5_subq_decomp/RESULT.md`.
- **CAPTURED — "better agent-communication language" cluster** (PI video, 2026-06-12; EcoLANG arXiv 2505.06904, Interlat
  latent-comms arXiv 2511.09149, AIM symbol protocol, A2A/MCP). **Splits two ways:** (a) **latent/hidden-state comms
  (Interlat ≈ our cluster-D LatentMAS) = NOT implementable (model internals) + already flagged V-HARMFUL** (collapses
  verifier independence, participation ratio→1) — already in the v5 survey, no action; (b) **structured/compressed TEXT
  protocol = our lane, an efficiency lever (C/B), point-release-class** — sibling of the SubQ-decomposition item. **BINDING
  CAUTION:** a tighter agent language can buy agreement at the cost of independence — any adoption MUST be gated on the
  participation ratio (C2/C8/C20); agreement-by-shared-language is a *risk*, not a win. Does NOT unlock the capability
  ratchet (still infra-gated). Queued, not run.
- **CAPABILITY PROBE — "use small problems instead of SWE-bench" hypothesis TESTED 2026-06-20 → machine-verified
  NEGATIVE** (`benchmarks/v5_capability_probe/VERDICT.md`, Sonnet-audited SOUND-WITH-CAVEATS). 2 rounds, Haiku,
  frozen graders. **Round 1 (Sidon construction):** repair "won" only by writing+running its own search script
  (confound = execute-beats-guess, owned; not feedback). **Round 2 (code-debug, feedback isolated):** single =
  best-of-3 = feedback-repair = **4/5 (+0)**; easy bugs one-shot (saturated), the 1 hard failure (datediff 2000-leap)
  failed in all arms (model limit). **Structural catch-22:** small self-authorable problems can't be simultaneously
  hard-to-one-shot + feedback-generalizing + held-out — that clean middle IS SWE-bench-scale. **Re-confirms the
  infra-gated verdict; the capability ratchet stays OPEN at v3.** (Honest: low power — only 1 genuinely hard problem;
  this shows the cheap path's *difficulty*, not a proof it's impossible.)
- **CAPABILITY PROBE — ROUND 3: the cheap path WORKS (first machine-verified capability gain, 2026-06-20)**
  (`benchmarks/v5_capability_probe/round3_constrained/RESULT.md`, Sonnet-audited SOUND-WITH-CAVEATS). Arena =
  **constrained text generation / lipograms** (write coherent prose avoiding a letter + required words + length;
  exact surface verifier). **Defeats both walls:** coherent prose isn't scriptable (Wall 1), random constraints
  aren't memorized (Wall 2). **Step 1 (N=6/arena, matched budget K=3, Haiku): single 25% → repair 100% (+75pp);
  feedback-repair beats fair INDEPENDENT resampling +33pp** (conservative ~+50pp) on the discriminating arena.
  **Mechanism = systematic correlated blind spots** (model always slips a given letter → resampling plateaus;
  targeted feedback names the offending word → fixes it). **First cheap capability lever that beats resampling.**
- **CAPABILITY PROBE — ROUND 4: v6 promotion attempt → NOT PROMOTED (lever is WEAK-MODEL-ONLY; 2026-06-20)**
  (`benchmarks/v5_capability_probe/round4_promotion/RESULT.md`). Ran the full promotion flow with a hardened
  harness (coherence gate + budget logging + 2 distinct arenas: lipogram + word-length-cap). **Haiku: feedback>
  resampling +50pp (lipogram) / +17pp (lengthcap), budget-logged, audited SOUND.** **Cross-model (Sonnet): the
  independent audit caught a coherence-gate bug** (macOS wordlist missing "feet"/"women"/"cafe" → false-rejected a
  coherent Sonnet output, the sole Sonnet feedback win). **Fixed + re-scored → Sonnet feedback-vs-resampling +0pp**
  (plain resample+verify, OWNED v3, reaches 100% at the strong model). **VERDICT: NOT a promotion — the novel
  lever is WEAK-MODEL-SPECIFIC** (like v5.1's quality benefit); fails the cross-model ≥10%-over-best-single-model
  bar. **Ratchet stays OPEN at v3.** The verify-independently loop caught the orchestrator's own bug before a false
  stamp. SURVIVES: a real, audited, weak-model capability lever; genuine systematic-blind-spot mechanism. **To
  earn v6 still needs: a lever that helps a STRONG model too (beats resample+verify at the frontier).**
- **⭐ CURRENT NEXT TASK (2026-06-20) → VALIDATE & STAMP a stable v5.2 "Cheap Cross-Check Audit."** Rounds 5–6 confirmed
  (machine + Sonnet-audited) that a CHEAP weak model verifies SURFACE-checkable errors as well as a strong one
  (round 5 Haiku=Sonnet 8/8 0FP; round 6 2nd arena 10/10 0FP, 2/2 natural). Designed as an error-DETECTION layer
  (v1 over-engineered design was red-team-KILLED; v2 simplified). **Candidate, OFF by default, OWED a validation A/B.**
  The plan is frozen: [`V5_2_STAMP_PLAN.md`](V5_2_STAMP_PLAN.md) — run cheap-cross-check vs baseline on ≥2 arenas with
  **MEASURED cost + measured FP + ≥10 NATURAL errors + a SURFACE-vs-NESTED triage check** (closing round-6's 3 audit
  holes), then stamp v5.2 as an efficiency/honesty point-release if weak-dominance holds. **Capability-vs-best-model
  is OUT OF SCOPE (PI: leave it; it's infra-gated).** Spec `BOX_V5.2_DECOMPOSED_CROSSCHECK.md`.

## 1. Original gaps/targets — status as of C20 (predicted → learned)

| id | original gap/target | status | what changed it |
|---|---|---|---|
| **G1 / T1** | paste-mode ceiling: can't touch reality → add tool runtime | ✅ **CLOSED** | This whole session ran in **TOOL mode**: real data downloaded, `VERIFY_CMD` executed, citations fetched, `gcvb.py` run. |
| **G2 / T4** | "independent" verifiers are correlated, unmeasured | ✅ **mechanism done** | Participation ratio measured: **1.0 pipelined → 1.45 un-pipelined** (C12); the "≥1 different model" rule is BOX_V2 Δ1. Needs more N. |
| **G3 / T2** | nothing measured; grounding not entailment | 🟡 **half-closed** | `G_faith` upgraded **stub → real NLI** (C15, App 0.92→0.79). **`C` still a stub** — the one remaining un-instrumented term. |
| **G4 / T3** | token efficiency asserted, never optimized | 🟡 **measured, not optimized** | Token telemetry real; the **cheap-verification lever** found (App 27× → Math 3.6× → cheap), but no automatic budget-knee stop yet. |
| **T5** | cross-run verifier calibration | 🟡 **spec wired (v2.2 Δ4)** | Hit-rate weighting specced in BOX_V2.2 Δ4; needs N runs to be non-trivial → carried to v4 goal 4. |
| **G_avail coverage** | the residual shared blind spot (post-cutoff / stale consensus) | 🟡 **point-release (v2.2), NOT closed** | Retrieval-gating *demonstrated* (8/8 post-cutoff facts via real WebSearch; WHS 43→44 drift caught) but the A/B was hand-authored/circular + no ablation + single-model → v3 bar unmet. The *mechanism* is right (only retrieval fixes G=0, P6/C20); the *proof* still owes an ablation + ≥2 arenas + ≥5 trials. |
| **T6** | deep-stack pilots (grounding-aware decoding, sparsity) | ❌ **open / deprioritized** | The runs show value lives at the orchestration layer, not the model layer — deep-stack is lower priority than first thought. |
| **G6 / T7** | one suite, five template weight-profiles; transfer | ❌ **open** | Exponent transfer (P5) untestable until `C` is upgraded. |

## 2. NEW gaps discovered this session (not in the original list)

| id | gap | why it matters | blocks |
|---|---|---|---|
| **N1** | **Error-eliciting item bank** was missing | Without tasks that make strong models err, *every* superiority/independence/P6 measurement saturates (C17). | A/B, P6, math arena |
| | → status | 🟡 **v1 built** (C18: breaks Haiku/Sonnet) + **post-cutoff tier** (C20: breaks all). Needs scaling to ~20+ items/tier. | |
| **N2** | **`C` (compression) has no trustworthy estimator** | ✅ **RESOLVED (C23):** split into C_density (measurable, zlib/token) + C_relevance (oracle-bound, entangled with G/B). **P5 exponent-fit RETIRED**; Q is an organizing frame, not a fitted law. See [C_RESOLUTION](measurement/C_RESOLUTION_2026-06-07.md). | ~~theory~~ closed |
| **N3** | **The box is E-negative unless verification is cheap** | The headline efficiency finding (C12): multi-agent pays only where errors exist AND verification is cheap+independent. | the whole value proposition |
| **N4** | **The value proposition is "honesty, not capability"** | Triangulated C9/C12/C13/C14: the box buys grounding-faithfulness + abstention, not raw correctness. Reframes what to optimize and market. | positioning, box design |
| **N5** | **Promotion needs multi-trial A/B + ablation** | One trial saturated (C17); need many trials on error-bank tasks for significance. | Next→Present promotion |
| **N6** | **Verifier diversity must be NON-NESTED, not a capability ladder** | C21: Opus⊂Sonnet⊂Haiku errors nested on recall → PR 1.0. **C22 (tested):** even model+retrieval is nested (retrieval *dominates*, not orthogonal) → PR 1.0. **Independence > 1 is the exception** — seen once (App judgment, 1.45); on factual work use best-model+retrieval, not a panel. See [VERIFIER_INDEPENDENCE](measurement/VERIFIER_INDEPENDENCE_2026-06-07.md). | the V term, BOX_V2 Δ1 — **largely resolved** |
| **N1** | → status update | 🟢 **bank scaled** (Tier A 10 items, post-cutoff 12). Each tier ~target 20; next: add a cross-architecture/tool verifier so independence (N6) is measurable. | — |

## 3. Confirmed (the theory's wins this session — what NOT to keep re-litigating)
- **P6 strict complementarity: NOT falsified, probed 3 ways** incl. the pristine G=0-for-all test (C20). `Q∝G·V` stands. *Stop re-testing the core; replicate at larger N only.*
- **C9 reconfirmed across 3 arenas + the experiment level:** gross-error gap → 0 at strong models; the box's edge is discipline at the margin.

## 4. Prioritized next innovations (the team's plan, ranked by value × unblock ÷ cost)

1. **Scale the error-eliciting bank to ~20+/tier** (Group 2 Eval). *Unblocks A/B, P6-at-N, math arena in one build.* Cheapest high-leverage move. **← do first.**
2. **Multi-trial Next-vs-Present A/B + ablation on the bank** (Group 5). The promotion gate; now finally measurable.
3. **Upgrade `C`** or, if a true estimator is impossible, **formally retire the exponent-fit goal** and state Q qualitatively (Group 1 + Eval). Resolve the last measurement blocker honestly.
4. **Cross-run calibration (T5)** — weight verifier votes by historical hit-rate (Group 5). Now feasible because runs persist.
5. **Auto budget-knee stop (G4/T3)** — stop a section at marginal-quality-per-token (Group 2/3). Turns the cheap-verification finding into an automatic policy.
6. **No-abstention-prompt hallucination variant of P6** (Group 2) — measure unprompted confident-hallucination at G=0 and whether a panel reduces it (predicted: no).

## 5c. MATH EFFICIENT arena — new finding (2026-06-08, candidate → F8/F11 gate)
**Constructive math is the box's strongest-grounding arena: machine-checked `G_faith`=1.0, no web needed,
honesty gate automatic.** On cap-set construction (the FunSearch problem), real Haiku+Sonnet **fabricated
100% of the time** — emitting valid-looking, optimal-*sized*, mathematically-INVALID sets; only the
independent verifier caught them. The box's value here is the **execute-verify loop**, not generation.
Verified lift: swap-search reached the **optimal n=4 cap (18→20)**, n=5 38→40 (no SOTA breakthrough; n≤6
proven optimal). New candidate breakthrough "**Cx — machine-verified constructive math is where the box's
grounding is unfakeable**" — distinct from C9; parked for the F8 vote + F11 gate. Log:
`benchmarks/math/MATH_EFFICIENT_2026-06-08.md`. Next: SA / FunSearch-style LLM-in-loop to push n=5,6→optimal
and n=7 past 162→236; generalize to Sidon / no-3-in-line as a standing verifiable-math sub-arena.

## 5d. v4 SURVEY finding — v3's core claims are REDISCOVERIES (2026-06-09, cross-model verified)
**The new Survey department's first run grounded v3 externally for the first time (C1–C30 had been
self-contained) and found all three of v3's load-bearing claims are established prior art** — fetched spans +
an adversarial Sonnet check in [`benchmarks/V4_SURVEY_2026-06-09.md`](benchmarks/V4_SURVEY_2026-06-09.md):
- (A) "voting false-approves correlated/shared errors" → Condorcet-under-correlation (Ladha 1992; Berend–Paroush 1998); LLM-specific in arXiv 2602.09341 ("Condorcet … assumption collapses in practice") + arXiv 2506.07962 (350+ models agree-when-wrong). The program's participation-ratio (C12/C21) is a rediscovery of this.
- (B) "execute, don't vote, on checkable claims" → established practice (arXiv 2401.00812: code execution "largely deterministic … remain faithful"); eval tooling already says use execution over LLM-judge where verifiable.
- (C) **H1 (grounding decays with time) → settled** (Lazaridou 2021 "Mind the Gap"; Dhingra 2022). **H1 RETIRED as a novelty candidate** — cite as known; at most measure the decay *rate* per arena.
- **Implication:** v3's research *novelty* was overstated; its real contribution is the per-arena *quantification*, not the mechanism. Survey did its job (killed reinvention). This does not retract the v3 box.

## 5e. H5 — the κ·ρ routing predictor (NEW, 2026-06-09; candidate novel synthesis, NOT confirmed)
- **H5 (V/G):** execute-vs-vote gain ≈ **κ·ρ** (κ = checkable share, ρ = agreed-but-wrong rate on checkable claims). Estimators named in the cycle log. ⟦XM: likely novel as a *routing* formula (no prior art found vs RouteLLM/FrugalGPT/RouterR1), but modest/derivable.⟧
- **Reframes the bar:** in every checkable arena κ≈1 ⇒ gain≈ρ ⇒ "≥10% across ≥2 arenas" reduces to "find ≥2 arenas with shared-error rate ρ≥10%." Explains why v3 keeps failing the cross-arena bar and why constructive-math (ρ≈100%) is special.
- ⚠️ **The 6-arena retrospective fit is CIRCULAR (κ≈1 ⇒ gain≈ρ is definitional)** — flagged by the cross-model verifier, logged as consistency NOT evidence. **Non-circular test (pre-registered, cycle 2):** a κ-varying *mixed-workload* arena (checkable + judgment claims), predict gain=κ·ρ on a calibration slice, confirm on held-out; kill if non-checkable claims also benefit. Doubles as Goal G3 (trading/app are mixed-κ).
- ✅ **CYCLE-2 RESULT (2026-06-09, machine-verified, non-circular): H5-predict NOT robustly confirmed — 1/2 arenas.** 2 arenas (κ=0.80 / 0.60), real 3-model panel (Haiku+Sonnet+Opus), Python/fetch truth. Calibration→held-out: **Arena B MATCH (+20%=+20%); Arena A MISMATCH (pred 0% vs actual +20%)** — the calibration slice held zero errors while the one hard item (3-way model disagreement) sat in the held-out slice. **Root cause: sparse/lumpy checkable errors ⇒ ρ has high across-slice variance, doesn't transfer at small N; split-sensitive.** **Constructive residue:** gain=κ·ρ is a sound *decomposition* of where checker-first pays, NOT a *small-sample predictor* of it. **No promotion; honest negative logged.** Next: larger-N ρ-stability replication, or pivot to another v4 goal. Log: [`benchmarks/V4_H5_EXPERIMENT_2026-06-09.md`](benchmarks/V4_H5_EXPERIMENT_2026-06-09.md).

## 5b. Innovation-branch hypotheses (NR3, parked candidates — 2026-06-08)
Generated by the standing theory-generation branch ([`INNOVATION_BRANCH.md`](INNOVATION_BRANCH.md)); each
names a term + estimator (guardrail enforced). **Not promoted** — awaiting F8+F11 after tests at N.
- **H1 (G):** `G_avail` decays with wall-clock time → coverage must be re-validated on a schedule. *First evidence: WHS 43→44 drift. Not falsified.* → v4 goal 3.
- **H2 (V):** verifier agreement is an *anti*-signal at G=0. *Parked: needs N (statistician).* → v4 goal 5.
- **H3 (B):** retrieval is Pareto-cheaper than verification for coverage. *First number: ~220 tok/covered-claim vs ∞ for a panel at G=0. Not falsified.*
- **H4 (C):** C and V are not independent factors (attacks the functional's separability). *Parked: needs N.* → v4 goal 5.

## 6. NEXT-SESSION ENTRY POINT (resume here)

> **↳ For the full pick-up, open [`/RESUME.md`](../RESUME.md) (repo root) — the authoritative resume doc.**

**Where we are (end of 2026-06-08, C1–C30):** **v3 PROMOTED to Present — Executable Verification (Checker-First), C30.** *Never vote on what you can check:* route machine-checkable claims to an executor (run code / fetch / check invariant); panel is fallback. Cleared the bar on a non-circular cross-arena A/B (construction ~100%→0% invalid-survives, computation +25%, factual +16.7%). Two-attempt history: the FIRST v3 (the retrieval-gate) over-claimed → rolled back to v2.2 point release; the SECOND (executable verification) cleared it. History-app advanced to **v0.3** ("history of everything", 25 grounded entities, VERIFY_CMD green). **Now v4 seeded** = the Survey→Theory→Experiment engine + replication + breadth. **Prior:** v2 promoted (C25); products v0.2; P6 survived 3 probes; error bank built; G_faith real; C split / P5 retired.

**Top to-do (finish v3 properly):** (1) **the missing ablation** — agreement-gate vs v2's disputed-item gate on the same items (the core open task); (2) ≥2 arenas, ≥5 trials, non-circular scoring; (3) cross-model verification (close C8); (4) confirm/kill H1 (grounding decay) for the theory-advance version. Full goals: [`/RATCHET.md`](../RATCHET.md) §v3.

**The thesis (well-supported, self-consistent):** *The box buys honesty + grounding, not capability or verifier headcount. G does the real work; V-independence pays only narrowly (judgment tasks, non-nested verifiers). On factual/recall work, best-model + retrieval wins.*

**Settled — do NOT re-litigate:** P6 / strict complementarity (confirmed 3 ways, C16/C18/C20); C9 saturation (gross-error gap→0 at strong models); verifier-independence is task-shaped and usually nested (C21/C22).

**✅ v2 PROMOTED to Present (C25) — the directive's stopping point reached.** The true v2 is *adaptive verification* (Δ1); it weakly dominates the old fixed-pipeline box by construction.

**✅ also done since:** all 3 products advanced to **v0.2** (C26); ratchet advanced + v3 seeded ([`/RATCHET.md`](../RATCHET.md)).

**Top to do next (v3 + replication):**
1. **Begin v3 — grounding COVERAGE.** Close the *shared blind spot* class (captured-vs-built; post-cutoff facts) that v2 is structurally blind to → retrieval-gated grounding + calibrated abstention + a coverage metric. Test set already exists: `measurement/error_bank_*.json` (shared-error + post-cutoff tiers). Goals: [`/RATCHET.md`](../RATCHET.md) §v3.
2. **Multi-trial A/B replication** — ≥5 paired judgment-task trials for tight significance on the v2-dominance claim.
3. **Products → v0.3** under the contract (3rd state for app / news for trading / 3rd problem for math).
4. **Cross-run calibration (T5)** — weight verifiers by historical hit-rate.

**Key files to reopen:** [`/RESUME.md`](../RESUME.md) (start here) · `Legacy/EVOLUTION_LOG.md` (C1–C26) · `Next/BOX_V2.md` · `/RATCHET.md` · `/Journey_v1_to_v2/` · `Artifacts/README.md`.

---

## 5. Honest meta-note
Through C16, gap-finding was **reactive** (a saturated run forced the next move). This file exists so it becomes **proactive**: the team reads it at the start of each version, picks the top unblock, and updates it at the end. If this file ever goes stale again (no new dated entry across a version), that itself is the signal the team stopped innovating and reverted to box-ticking.
