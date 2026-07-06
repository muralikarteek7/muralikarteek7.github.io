# KICKOFF — build THE HELMET: "University Mode" (the R&D orchestrator brain) for the v5 box
*Paste everything below the line into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained.
Written 2026-06-12. This is NOT a weapon — it is the **HELMET**: the conductor worn OVER armor + weapons that
makes the whole model behave like a top research university (MIT/Stanford/Harvard-grade R&D process).*

---

You are adding a third layer to the v5 box. The box has **ARMOR** (always-on defense: honesty, executable
verification, abstention) and **WEAPONS** (problem-specific offense: the Frontier Construction Engine; SOCIUS for
sociology; PSYMETRIX for quant-psych; …). You will build **THE HELMET — "University Mode"**: a meta-orchestrator
that, given ANY problem, triages it, **activates the right research departments**, runs a full R&D lifecycle with
peer review, and delivers a verified result. It **coexists with and CALLS** armor + weapons; it does not replace
them. Work BOX-style (plan → produce → verify INDEPENDENTLY → ground → be honest; no win without proof).

## 0. ORIENT — read first
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (Armor+Weapons + the κ-router — the Helmet generalizes this),
`Expanding_Frontiers/ALGORITHM_AND_WEAPONS.md` (the attack loop), `Expanding_Frontiers/FRONTIER_ENGINE_WORKFLOW.md`
(the multi-agent Workflow you will GENERALIZE from "construct an object" to "run any R&D project"), and the weapon
kickoffs in `Expanding_Frontiers/weapons/` (each = one future "department").

## 1. THE HONEST FRAMING — what the Helmet IS and IS NOT (do not skip)
**IS:** an orchestration layer that turns "answer the question" into "run a rigorous, institution-grade R&D
project with the right specialists, grounded, peer-reviewed, and verified." It raises **process quality**:
specialization · literature grounding · method/weapon selection · independent peer review · institutional
standards · cross-disciplinary coverage. *That is genuinely how top universities outperform a lone responder.*

**IS NOT (the non-negotiable honesty):**
- **NOT a capability boost.** The Helmet does not make the underlying model smarter. A university of mediocre minds
  produces mediocre work; the Helmet ≠ superhuman neurons. It makes the model **organized, rigorous, comprehensive
  — not more capable than its model ceiling.** "Solves at the highest level" = *researched and resolved to the
  limit of what is verifiable/groundable*, NEVER "magically cracks an unsolved problem." On genuinely open/κ=0
  problems it delivers the best grounded analysis + honest bounds + abstention, not a fabricated breakthrough.
- **NOT theater.** The #1 failure mode to engineer against is **process bloat** — convening elaborate "departments"
  that emit verbose ceremony with no verified substance. A real R&D project ends in a **checkable deliverable**,
  not a brochure. The institution is judged by *verified output per unit cost*, never by how many departments it
  convened. Scale the institute to the problem (don't convene the faculty for a one-liner).

## 2. AIMS (what the Helmet must do)
1. **Triage any problem** → classify it (domains · κ-profile · type · known-vs-open · stakes/budget) → decide which
   departments to activate and at what scale.
2. **Activate departments** = route to the matching weapon(s) (κ>0 build/verify) and/or armor method-clusters (κ=0
   judgment), staffing each with the right specialist seats on the v4 model ladder.
3. **Run the R&D lifecycle** (intake → literature → design → execute → review → revise → deliver) with **mandatory
   independent peer review** (cross-model ≠ generator).
4. **Coordinate cross-disciplinary** problems (multiple departments, a "Dean" that integrates).
5. **Enforce institutional standards** (the box's honesty rules = the integrity office) and **budget discipline**
   (the registrar: value × openness ÷ cost; permission to stop).
6. **Deliver** a single honest artifact: verified claims, grounded claims, abstentions, calibrated confidence, and
   the explicit limit of what was established.

## 3. THE ARCHITECTURE (build these five components)
1. **THE PROVOST — triage & routing brain.** Input: any problem. Output (a structured intake object): domains;
   per-claim κ (checkable?); task type (construct / prove / analyze / measure / design / decide / explain /
   forecast); known-vs-open; stakes & budget tier; → the set of departments to convene + the lifecycle depth.
2. **THE DEPARTMENT REGISTRY — problem-type → department → weapon/method** (extensible; a new weapon = a new dept):
   | department | covers | draws |
   |---|---|---|
   | Mathematics & TCS | construct/prove a checkable object | **Frontier Construction Engine** (cap-set engine, SAT/CP, exact solvers) |
   | Statistics & Methodology (core facility, cross-cuts all) | reproduce · multiverse · power · meta · causal | the verifier/reproduction armor + SOCIUS/PSYMETRIX shared methods |
   | Quantitative Psychology | psychometrics, measurement, forensics | **PSYMETRIX** |
   | Social Sciences | empirical social research | **SOCIUS** |
   | Computer Science & Engineering | algorithms, systems, code | execution + test-runner armor + algorithm discovery |
   | Natural Sciences | physics/chem/bio | simulation + literature grounding (wet-lab = κ=0 → design + abstain) |
   | Economics & Finance | markets, policy eval | held-out backtest (the trading arena) + causal methods |
   | Humanities · Law · Policy | interpretive/normative (κ=0) | **armor only**: grounding · argument-mapping · abstention |
   | Dean of Cross-Disciplinary | spans ≥2 departments | convenes + integrates the above |
3. **THE R&D LIFECYCLE — every project runs these stages (depth scaled by the Provost):**
   `INTAKE/FREEZE → LITERATURE (fetch real SOTA, don't assert) → DESIGN (hypotheses + method/weapon selection +
   the verification plan: what will count as proof) → EXECUTE (run weapons/armor; machine-checkable → execute &
   gate) → PEER REVIEW (adversarial audit, cross-model ≠ generator; reproduce; catch overclaims) → REVISE (iterate
   to standard or honest-stop) → DELIVER (honest writeup + calibrated claim + limits).`
4. **THE INTEGRITY OFFICE — the box's honesty rules, institutionalized & non-waivable:** no claim without proof;
   reproduction ≠ discovery; never claim to solve an open problem; abstain honestly; **independent (cross-model)
   verification is mandatory before any result ships**; flag every unverified/κ=0 piece as such.
5. **THE REGISTRAR — budget & scaling:** match institute size to the problem; cheapest path that clears the bar;
   permission to stop; log value × open-defects ÷ cost. A trivial question gets a single specialist, not a faculty.

## 4. TO-DOs / STEPS (box order)
1. **PLAN:** write `HELMET/SPEC.md` — the Provost intake schema, the department registry, the lifecycle stages,
   the integrity + registrar rules. Ground the "how top R&D orgs actually outperform" claims in real sources
   (science-of-science / team-science literature) — don't assert.
2. **BUILD THE RUNNABLE ORCHESTRATOR** (generalize `FRONTIER_ENGINE_WORKFLOW`): a Workflow that takes a problem
   string → **PROVOST agent** emits the structured intake (schema-validated) → fans out to **department agents**
   (each routed to its weapon/armor per the registry) → runs the lifecycle as a pipeline → a **PEER-REVIEW agent
   (model ≠ generator)** audits each deliverable → a **DEAN agent** synthesizes one honest artifact. Every
   machine-checkable claim is executed/gated; every prose claim grounded or abstained.
3. **PICK 3 TEST PROBLEMS spanning the κ-spectrum** (commit predictions before running):
   (a) a κ=1 construct task (routes to Math dept → construction engine — should produce a verified object or honest
   negative); (b) a medium-κ empirical task (routes to Stats/PSYMETRIX/SOCIUS — should reproduce + stress); (c) a
   κ=0 judgment task (routes to armor-only dept — should ground + abstain, NOT fabricate). The Helmet passes iff it
   **routes each correctly, runs the right lifecycle depth, and the peer-review model confirms** — including that
   the κ=0 task ends in honest abstention, not invented certainty.
4. **VERIFY INDEPENDENTLY:** a different model red-teams the orchestrator on an adversarial problem designed to make
   it (i) over-convene (theater) and (ii) over-claim on a κ=0 task. The Helmet must resist both (registrar caps
   scale; integrity office forces abstention). Fix what's caught.
5. **REGISTER:** add the Helmet as the top layer in `Next/BOX_V5.md` (box = ARMOR + WEAPONS + **HELMET**), with a
   note that it CALLS weapons/armor and is invoked for genuine R&D-grade problems (not trivial queries — the
   registrar gate). Honest `EVOLUTION_LOG` entry: an orchestration LAYER added (capability EXPANSION — process,
   not raw capability; NOT a ≥10% promotion).
6. **HONEST WRITEUP:** what University Mode demonstrably improves (routing, grounding, peer-review catch-rate,
   coverage), and its ceiling (it cannot exceed the model's capability; it makes the model *organized*, and on
   open/κ=0 problems it abstains honestly rather than fabricating).

## 5. HONESTY RAILS (non-waivable, specific to the Helmet)
- **Organized, not smarter.** Never let "University Mode" imply a capability beyond the underlying model. State the
  ceiling in every University-Mode deliverable.
- **Anti-theater clause.** If a project's verified substance could have been produced by one specialist, the
  institute MUST down-scale — convening departments without added verified value is a defect the registrar fails.
- **κ=0 ends in honest analysis + abstention, never fabricated breakthrough.** "Solved at the highest level" =
  resolved to the limit of the verifiable, with the limit stated.
- **Mandatory independent peer review** (cross-model ≠ generator; Fable inactive → Sonnet/Haiku, never
  Opus-audits-Opus) before any result ships. Self-review by the producing department does not count.
- **Reproduction ≠ discovery; never claim to solve an open problem.** Inherit all weapon/armor honesty rails.

## 6. DELIVERABLES + WHERE
`Expanding_Frontiers/HELMET/` — `SPEC.md` (the institution), `orchestrator.*` (the runnable Workflow/harness),
`registry.json` (department → weapon/method map), the 3 test-problem runs (`tests/` with committed predictions +
peer-reviewed results), `AUDIT.md` (the cross-model red-team incl. the theater + over-claim adversarial tests),
`README.md` (what University Mode is + its honest ceiling). Layer note + router hook in `Next/BOX_V5.md`; honest
`EVOLUTION_LOG` entry.

## 7. STAFF THE TEAM (v4 ladder; Fable 5 INACTIVE → its slots on Opus, flag low confidence)
- **Provost** (Opus): triage/routing brain — the intake classifier.
- **Department PIs** (routed per registry; code tier executes, frontier+gate for novel construction).
- **Library** (cheap model): fetch real SOTA; don't assert.
- **Peer-review committee** (model ≠ generator — Sonnet/Haiku): adversarial audit + reproduction.
- **Dean** (Opus): integrate cross-disciplinary outputs into one honest artifact.
- **Registrar / Integrity office** (the orchestrator itself): enforce budget + honesty veto.

## 8. THE ONE-LINE TEST OF SUCCESS
**"Given ANY problem, University Mode convenes exactly the right departments at the right scale, runs the full
lifecycle, an independent model confirms every shipped claim, the κ=1 work yields verified objects, the κ=0 work
yields grounded analysis + honest abstention — and a one-line question is answered by one specialist, not a
faculty."** That is a top university: rigorous, comprehensive, honest, and not a single neuron smarter than the
model wearing it — which is exactly why it's safe to wear alongside the weapons.
