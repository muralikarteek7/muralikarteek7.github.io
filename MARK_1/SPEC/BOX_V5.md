# BOX v5 — ARMOR + WEAPONS + HELMET (offense integrated, then conducted) — assembled 2026-06-12, helmet added 2026-06-20

> **One line:** v5 = the v4 box (always-on **ARMOR** = defense: safe, honest, verified output) **+ registered
> WEAPONS (offense: produce/stress a *machine-verified* object)** + a **WHEN/WHERE router** (armor only vs draw
> the weapon) **+ the HELMET (the conductor worn OVER both: "University Mode" — triage any problem, convene the
> right departments at the right scale, run the full R&D lifecycle with independent peer review, deliver one
> honest artifact).** *Armor keeps you honest; weapons let you break through; the verifier is the only judge;
> the Helmet makes the whole thing behave like a research university — organized, not smarter.*

**Status (honest, non-waivable).** This is the **PI-directed integration of the OFFENSE track** built this
season. Its nature is a **capability EXPANSION** — it adds a task class the box previously could not do (*construct*
a new verified object; armor only ever *checked* one). It is **NOT** a measured ≥10% A/B promotion on the existing
armor arenas (a weapon that produces objects and armor that checks claims are different task classes — there is no
head-to-head). **By the ratchet rule the ≥10% CAPABILITY ratchet stays OPEN at v3.**

**Why "v5" and not "v4.1" (the affirmative case, stated plainly so the stamp isn't a dodge):** v4 cannot produce a
construction object at all — on a "build object X" task it returns a scored abstention (score 0). v5 produces a
machine-verified object. So the only honest head-to-head ("v5 vs v4 on construction arenas") is *positive-by-any-
margin vs abstain* — a **task-class extension**, not a quality delta on a shared task. That is a real new
capability, but it does **not** clear the ≥10%-non-circular-A/B-on-shared-arenas bar (there is no shared arena),
so it is stamped **v5 as a PI-directed integration milestone — the same *class* of stamp as v4 (integration, not a
measured capability promotion).** Nature stated; ratchet not moved.

What is *proven* (grounded, not asserted): the weapon **built and machine-verified a 236-cap in F₃⁷**
(`cap_n7_size236_CF.json`, triple-checked), and a multi-agent run produced **4 valid certified constructions** and
**gate-rejected ≥1 invalid proposal** (the orbit-twisted/z4 class, size 0 — "2 bluffs" if its two lenses ran
separately; see run `wf_6a58dc41-b83`). What is *not* claimed: a record, an open-problem solve, or a benchmark win
over v4.

---

## 1. The two tracks

### ARMOR — defense, always on, never bypassed (unchanged from v3/v4)
Executable verification (never vote on what you can machine-check → route checkable claims to an executor) ·
honesty/fabrication veto · abstention as a scored deliverable · never-trust-a-self-report · the deterministic
**model ladder** (machine-checkable → execute $0 · routine → Haiku · audit → a model ≠ the generator). Spec:
[`BOX_V3.md`](../../MARK_0/01_box_versions/BOX_V3.md), [`BOX_V4.md`](../../MARK_0/01_box_versions/BOX_V4.md); machinery `router.py`, `weapon_gate.py`, `WEAPON_REGISTRY.json`.
**Armor makes output *safe*. It does not make you *win*.**

**+ v5.1 (point release, 2026-06-20) — SELECTIVE-CONTEXT DECOMPOSITION (an EFFICIENCY/cost option, not a new capability).**
On a long-context task whose sub-questions key off retrievable terms, **decompose into sub-tasks, feed each only
the minimal retrieved slice (B7), and compose with code** instead of handing the whole corpus to one prompt.
Measured (`benchmarks/v5_subq_decomp/`, 2 arenas × 3 seeds × N=40, Haiku, code-truth, Sonnet-audited): **~5–8×
cheaper on task-tokens with quality weak-dominance — the decomposed arm never regressed quality (C ≥ monolith in
every cell, 0 losses/40).** HONEST: the big *quality* lifts are mostly the existing executable-verification armor
(offload checkable arithmetic to code); the *new* ingredient (selective context) reliably buys the **cost** win,
its quality *benefit* stays at the noise floor (1/16 isolated). End-to-end token ratio shrinks to ~1.4× once
fixed per-call overhead is counted. **Weak-dominance ⇒ point release, NOT a ≥10% capability promotion; ratchet
stays OPEN at v3.** Use as a routing option for long-context aggregation/lookup; do NOT use when the corpus is
queried repeatedly (extract-once-and-reuse is cheaper) or when retrieval recall is unreliable (load-bearing).

**+ v5.2 (point release, 2026-06-20) — CHEAP CROSS-CHECK AUDIT (an error-DETECTION/honesty + efficiency option, not a new capability).**
Before emitting ANY load-bearing output, run the cheapest *sufficient* check, then FLAG/ABSTAIN (never auto-fix):
- **EXACT** subparts (math/code/invariant) → the MACHINE ($0, owned v3). **FACTS** → retrieval (owned, C22).
- **SURFACE-checkable** (errors detectable locally, no deep reasoning needed) → a **CHEAP (Haiku) cross-model
  check, ≠ generator** — the validated piece. **NESTED/uncertain** → a frontier model ≠ generator, else **ABSTAIN**
  (never Opus-audits-Opus while Fable is down). Aggregate by liberal veto; report the measured FP rate every run.
- **TRIAGE is the load-bearing safety step** (route SURFACE→cheap, NESTED→machine/frontier/abstain) and must
  default to ESCALATE/ABSTAIN on any uncertainty — the cheap check ALONE is unsafe on NESTED outputs.
Measured (`benchmarks/v5_capability_probe/round7_v52_validation/`, 3 arenas, machine-graded vs re-derived truth,
Sonnet-audited SOUND-WITH-CAVEATS): the cheap Haiku cross-check **matches-or-beats a Sonnet strong-check at a
measured ~3× lower cost**, takes error-escape **100%→0% at 0% FP** (11 natural errors all caught), and triage scored
**16/16** routing NESTED away (0 dangerous mislabels). HONEST: this mostly **cashes owned doctrine (B1/C8 — a
non-generator checks the output) at the *cheap* tier**; cheap tier = cross-INSTANCE not cross-MODEL (Haiku is the
only cheap model); cost win is **vs a strong cross-check** (not vs no-check); triage validated on clearly-
categorizable items (NESTED-disguised-as-SURFACE untested → abstain-on-uncertainty is the mitigation). **SUPPORTED-
not-fully-proven; weak-dominance ⇒ point release, NOT a ≥10% capability promotion; ratchet stays OPEN at v3.** Plug
it in as the pre-emission step on any load-bearing artifact (HELMET/Integrity final step); the triage + abstain
pieces ship behind it. Design history: [`BOX_V5.2_DECOMPOSED_CROSSCHECK.md`](BOX_V5.2_DECOMPOSED_CROSSCHECK.md).

### WEAPON — offense, drawn per problem: the **Frontier Construction Engine**
An executable, **verifier-gated construction-SEARCH** system that *produces* a new machine-verified object (not
just checks one). Home: [`../ARSENAL/`](../ARSENAL/) (method = SURVEY/THEORY/
ALGORITHM_AND_WEAPONS/AUDIT; runnable = `cap_set/frontier_engine.py`, `build_236.py`, `capset_verify.py`).
Two modes:
- **FETCH-KNOWN** (target is a published/proven object): fetch the structure → instantiate the forced parts as
  identities → exact-solve the small residual → re-verify from scratch. *(Reproduced the 236-cap this way.)*
- **SEARCH-OPEN** (genuinely open frontier): read the problem as a state vector → propose structural families
  (representation + canonical building-blocks + **obstruction-inversion**: turn a dead-end into a design target)
  → search them executably → **every candidate gated by the frozen verifier** → cross-model audit any survivor.

**The weapon's honest ceiling (measured this season):** it **verifies / reproduces / extends reliably**, and
**invents the load-bearing brand-new idea rarely** (precise count: **2 direct attacks on the verified 236** —
point-extension + LNS — confirmed it a robust local optimum; **3 earlier strong searches stalled at 224** before
the C–F structure was fetched; none invented a >236 idea. The de-novo leap past a record is the open gap). Draw it expecting a *verified object on known/extendable targets* and an
*honest negative + a structural map* on truly open frontiers — not a guaranteed record.

### WEAPON 2 (added 2026-06-20) — **SOCIUS**, a κ-aware empirical-rigor engine for social science
Home: [`../ARSENAL/weapons/socius/`](../ARSENAL/weapons/socius/) (`SPEC.md`, `README.md`,
six frozen verifiers + `selftest_all.py` gate, `socius_router.py`, `demo_durante2013/`, `demo_grounding/`, `AUDIT.md`).
**The first MIXED-κ weapon: it routes INTERNALLY by checkability.** Social science is a **LOW-κ field** — most
claims have no cheap exact verifier — so SOCIUS is **NOT a construction engine and breaks no records.** Given an
*empirical* social-science task it splits the work: the **κ>0 executable pieces** go to frozen, adversarially
self-tested verifiers — **S-REPRO** (reproduce a published statistic), **S-MULTIVERSE** (specification-curve /
multiverse robustness), **S-MEASURE** (reliability + measurement-invariance CFA), **S-CAUSAL** (E-value
confounding sensitivity, κ≈0.5), **S-SAMPLE** (representativeness/weighting, κ≈0.5), **S-GROUND** (a κ=1 FROZEN
fabrication layer — is the quote/number/citation actually IN the fetched source? — plus a κ=0 entailment judgment
by a model ≠ generator, else abstain) — and the **κ=0 judgment pieces** go to armor. **Honest ceiling, stated every run: it raises
trustworthiness (reproducibility + grounding); it does NOT manufacture truth. Reproduction ≠ discovery; robust ≠
true; findings that DIE under stress are the primary valuable output.** Validated end-to-end on a real published
finding (Durante 2013 Study 1, via Steegen 2016's open OSF data+code): **reproduced exactly — 120 specs / 7
significant (5.8%) — then DIES under the multiverse.** Built box-style (Sonnet grounded the method SOTA + the
demo dataset; the frozen verifiers were EXECUTED and machine-gated; a Sonnet audit ≠ the Opus generator
re-derived the math by hand, web-confirmed every load-bearing citation, and red-teamed the honesty framing —
verdict *"sound tool, honest demo"*). A generator machine-check had already caught + fixed one real bug (a false
non-invariance from a small-df ΔRMSEA artifact) before the audit confirmed the fix sound.

### WEAPON 3 (added 2026-06-20) — **PSYMETRIX**, a κ-aware psychometric & statistical-rigor engine
Home: [`../ARSENAL/weapons/psymetrix/`](../ARSENAL/weapons/psymetrix/) (`SPEC.md`,
`GROUNDING.md`, `README.md`, `forensics_verify.py` ⭐ + `psychometrics_verify.py`, `selftest_all.py` gate,
`psymetrix_router.py`, `demo_forensics/`, `AUDIT.md`). **The sibling of SOCIUS, but quant-psych is
HIGHER-κ** — much of it is genuinely machine-checkable — so PSYMETRIX has a **large executable core AND one
genuinely sharp EXACT offensive piece: statistical forensics.** **P-FORENSICS** (GRIM/GRIMMER/SPRITE/TIVA/
p-curve/Benford) can **mathematically PROVE that reported summary statistics are impossible** for the stated
N/scale — the social sciences' closest analogue to the cap-set verifier (an exact certificate, not a judgment;
e.g. a mean of N integer responses can only be `k/(N·items)`, and a reported SD has a forced integer
sum-of-squares parity). The executable core: P-RELIABILITY (Cronbach α + **disattenuated r>1 = exact
inconsistency cert**), **P-MODEL — FULL CFA/SEM/EFA/IRT** (`model_verify.py`, semopy/factor_analyzer/girth:
CFI/TLI/RMSEA/SRMR fit + model comparison + EFA dimensionality + McDonald ω + IRT-2PL test information + Yen's
Q3; Bartlett-sphericity-guarded; **demo on real Holzinger-Swineford 1939 matches lavaan to 4 sig figs**),
**P-REPRO + P-MULTIVERSE** (`repro_multiverse_verify.py`: **dual-path reproduction certificate** (statsmodels +
numpy IRLS) + **specification-curve** robust/fragile/mixed verdict with effect-size spread + OVB & large-n
caveats; **demo on real Fair's Affairs 1978**: religiousness→affair effect reproduced 4 independent ways
(−0.375646) and **ROBUST across 256 specs** — the counterpoint to SOCIUS's effect that *died*), P-DIF
(Mantel–Haenszel), P-META (pooling + Egger), P-DESIGN (power + **constructive optimal item selection = argmax
test information**). κ=0 interpretation → armor. **Killer demo (machine-verified):**
reproduced all 4 of the method papers' OWN published worked examples (GRIM 5.27/43 impossible; GRIMMER
3.44/2.47/18 impossible via parity; 2 consistent controls) and, on a controlled ground-truth corpus (400 rows
from real integer Likert samples), measured GRIM at **100% specificity (zero false positives) and 71.5%
sensitivity**, detection tracking the `1−n/100` power law — the verifier is **sound** (never a false
accusation) and honestly **incomplete**. **Independently audited** (Sonnet ≠ the Opus generator; Fable
inactive): zero false positives in its own sweeps, every certificate re-derived independently, 4 robustness
bugs found and fixed, honesty rails clean. **⚠ NON-WAIVABLE rail: INCONSISTENCY ≠ FRAUD** — a flagged
inconsistency can be rounding/typo/reporting error; PSYMETRIX reports the exact arithmetic and STOPS, never
accuses. **Ceiling, every run: it certifies CONSISTENCY / FIT / ROBUSTNESS, never TRUTH.**

### WEAPON 4 (added 2026-06-20) — **OPTIMA**, exact optimization / OR (promotes registry **W2** to a full weapon)
Home: [`../ARSENAL/weapons/optima/`](../ARSENAL/weapons/optima/) (`SPEC.md`, `GROUNDING.md`,
`README.md`, `optima_gate.py` ⭐ the 4-part independent certificate + `optima_solve.py` (CP-SAT builders + independent
exact reference solvers), `selftest_all.py` gate, `optima_router.py`, `demo_certified/`, `demo_reproduce/`,
`demo_boundprove/`, `demo_reject/`, `AUDIT.md`). The **OR/Operations facility of CS_ENG** for discrete optimization
(scheduling/routing/packing/assignment/allocation). **κ=1 over a sharp cheap verifier** — an optimization solution is
independently checkable: re-evaluate every constraint (feasibility) + recompute the objective + back "optimal" with a
**matching dual/bound** (primal=dual ⇒ proven optimal). **The solver's "OPTIMAL" status is a self-report the box never
trusts; the independent certificate is the result.** Built GATE-FIRST: `optima_gate.py` re-checks plain solution data
against a plain model in pure Python (NEVER calls the solver to judge the solver) via four certificates — FEASIBILITY,
OBJECTIVE, OPTIMALITY (gap=0 via **exhaustive / LP weak-duality verified by exact integer arithmetic / a different exact
algorithm**; the solver's own `best_bound` is the honest *weakest* tier, labeled), INFEASIBILITY (an **IIS** the gate
independently confirms is unsatisfiable, not a solver shrug). Three modes: **EXACT-SOLVE** (certified-optimal),
**BOUND-PROVE** (timeout ⇒ feasible + a RIGOROUS independent lower bound + the honest gap, **never "optimal"** — the W2
failure-mode rail), **REPRODUCE-RECORD** (a benchmark optimum, labeled reproduction). **Infra grounded BEFORE design:**
OR-Tools CP-SAT 9.15 installed + machine-probed (gap=0 on OPTIMAL; a real IIS on INFEASIBLE). **INTEGER-EXACT** (no
float-MILP tolerance). **Killer demos (machine-verified, committed predictions):** (i) assignment+knapsack+TSP certified
optimal, each proven by a *different* exact algorithm (Hungarian/DP/brute); (ii) **reproduced TSPLIB burma14 = 3323 via
three independent routes** (CP-SAT == Held-Karp == the literature); (iii) a hard TSP (n=26) under a 2 s budget →
FEASIBLE + an independent 35% gap, reported as a bound never optimal; (iv) the gate REJECTING a broken "OPTIMAL-but-
infeasible", a wrong objective, a hidden gap, and a bogus IIS. **Independently audited** (Sonnet ≠ the Opus generator;
Fable inactive): verdict **SOUND_WITH_CAVEATS** — no attack produced a false certification, all shipped optima
independently confirmed; 4 robustness/honesty defects found (a missing-var crash, silent extra-vars, an omitted caveat,
an undocumented symmetric-bound assumption) → **all fixed + re-verified**. **⚠ NON-WAIVABLE rail: "optimal FOR THIS
FORMAL MODEL", never the real-world problem** — the modeling joint (words → vars/constraints/objective) is **judgment
(κ<1)** and is cross-model-reviewed; the certificate covers the formal model only. **Ceiling, every run: certifies
optimality for the model, reports timeouts as bounds-with-gap, reproduces labeled-as-reproduction, never a record
without an audited strictly-better certificate.**

### WEAPON 5 (added 2026-06-20) — **SYMBOLICA**, symbolic-exact numerics (promotes registry **W7** to a full weapon)
Home: [`../ARSENAL/weapons/symbolica/`](../ARSENAL/weapons/symbolica/) (`SPEC.md`, `GROUNDING.md`,
`README.md`, `symbolica_gate.py` ⭐ the ≥2-independent-method agreement gate, `selftest_all.py`, `symbolica_router.py`,
`demo_agreement/`, `AUDIT.md`). The **exact-computation facility of NAT_SCI** for closed-form integrals/sums/ODEs,
identities, special values and tight bounds. **κ≈0.9 over cross-method AGREEMENT — NOT a kernel** (PROOFSMITH is the
kernel weapon). **The defining honest framing: a single CAS answer is a CLAIM, not a result** — sympy `integrate`/
`simplify` are heuristic (no completeness guarantee, partial Risch — fetched from the docs), so the certificate is
**independent method FAMILIES agreeing**: SYMBOLIC (sympy) vs NUMERIC-AP (mpmath arbitrary precision, `mp.quad`/`nsum`)
vs NUMERIC-DP/SERIES (scipy QUADPACK / sympy series — a different algorithm family). Two **same-family** methods agreeing
is a **shared-blind-spot RISK** → a methodologically-different 3rd check on load-bearing cases. Built GATE-FIRST:
`symbolica_gate.py` certifies only on ≥2-family agreement to a committed digit floor, checks **CONVERGENCE before any
closed form**, and catches **domain/branch-cut** disagreements by full-domain multi-point sampling (a point where one
side is real-defined and the other complex/undefined is a DISAGREEMENT, **not a skip** — the trap, found and fixed during
build: without it `log(x²)=2log(x)` was wrongly certified). Four modes: **CLOSED-FORM** (integral: sympy.integrate vs
mpmath.quad vs scipy.quad), **IDENTITY-PROVE** (`simplify→0` AND K-point numeric; series→0 as 3rd), **SERIES**
(convergence-gated, mpmath.nsum + sympy.summation), **SPECIAL-VALUE** (reproduce vs a fetched reference, labeled).
**Honest label tiers (never swapped): "symbolically proven (simplify→0; not kernel-grade)" vs "verified to D digits at K
points".** **Infra grounded BEFORE design:** sympy 1.14/mpmath 1.3/scipy 1.13 machine-probed. **Killer demo (10/10
committed predictions):** (i) ∫₀^∞e^(−x²)=√π/2 triple-method agreement; (ii) Basel ζ(2)=π²/6 **reproduced** + numeric;
(iii) sin(3x)=3sin(x)−4sin³(x) symbolic-collapse "proven" + 20-pt numeric; (iv) the gate **REJECTING** √π (off ×2);
(v) the gate **REJECTING** √(x²)=x sold as global, CERTIFYING it only on x>0. **Independently audited** (Sonnet ≠ the Opus
generator; Fable inactive): verdict **SOUND-WITH-CAVEATS** — the auditor re-evaluated every result with its OWN numeric
code (all reproduced ≥50 digits) and every branch-cut/divergent/near-coincidence (exp(π√163)) attack was correctly
handled; **1 defect (SERIES mode issued bare `CERTIFIED` on a single numeric family when sympy gave no closed form,
overstating the ≥2 doctrine) caught → fixed** (explicit `CERTIFIED-SINGLE-FAMILY` tier + a regression self-test) +
re-verified. **⚠ NON-WAIVABLE rails: exact BY AGREEMENT, not kernel-proven; no closed form ⇒ numeric WITH error bars,
never a faked exact; what a result MEANS physically is κ=0 → ARMOR. Ceiling, every run: reproduces/verifies/certifies
reliably; does not invent the closed form that doesn't exist.**

### WEAPON 6 (added 2026-06-20) — **CODEFORGE**, a κ=1 code & algorithm-discovery engine (CS_ENG dept)
Home: [`../ARSENAL/weapons/codeforge/`](../ARSENAL/weapons/codeforge/) (`SPEC.md`,
`GROUNDING.md`, four frozen verifiers + `selftest_all.py` gate, `codeforge_router.py`, three `demo_*/`, the
capability A/B under `ab/`, `AUDIT.md` + `audit_independent/`). **Code has the SHARPEST cheap verifier that
exists** — it runs or it doesn't — so CODEFORGE is a **κ=1 construction weapon** with three modes, each with a
FROZEN exact (or held-out) verifier: **SYNTH-VERIFY** (synthesize to a spec; gate on HIDDEN + PROPERTY +
DIFFERENTIAL tests the generator never sees, with an UNPREDICTABLE fuzz seed; hard-coding → `GAMING_DETECTED`),
**SUPEROPT** (search a faster/smaller variant; κ=1 DIFFERENTIAL correctness gate + a *measured* benchmark —
"faster-but-wrong" is REJECTED), and **ALGO-DISCOVER** (a combinatorial object with an EXACT certificate: a
**sorting network via the 0/1 principle** — sorts all 2ⁿ binary inputs ⇒ sorts everything; a **matrix-mult
scheme via a non-commutative symbolic identity** — recursion-safe, the AlphaTensor-style gate). **Killer demos
(machine-verified, predictions committed first):** reproduced the **optimal n=8 sorting network (19
comparators)** and **Strassen's 7-mult 2×2** (labeled reproductions), discovered valid n6/n7 networks from
scratch, and a naive-O(n²)→O(n) SUPEROPT win — every bluff caught (a claimed "8-comparator n=5 sorter" is
impossible and was rejected; agent self-reports ignored). **The capability bet was TESTED → HONEST NEGATIVE:**
verifier-gated *iterate* vs equal-compute *best-of-k* = **+0pp** (feedback never the active ingredient;
reproduces the owned v5 repair-lever lesson in a fresh RICH-feedback arena; faithful at-scale test stays
infra-gated). Built box-style; **independently audited by Sonnet ≠ the Opus generator** (re-derived n=8 via
all 40,320 permutations and Strassen via 10,000 numeric + symbolic trials — all AGREE; verdict
SOUND-WITH-CAVEATS; it caught **2 real false-accept defects** — a predictable fuzz seed + an under-covered
superopt self-test — both **fixed + re-gated green**). **Honest nature: a WEAPON ADDED = capability EXPANSION
(new task class: *construct* a verified code/algorithm object — armor only ever *checked* one), NOT a ≥10% A/B
promotion (the A/B was +0pp). The ≥10% CAPABILITY ratchet stays OPEN at v3.** Ceiling: ships only
frozen-verifier-passed objects; reproduction ≠ discovery; SYNTH/SUPEROPT are as strong as their held-out
battery; κ=0 "is this code *good*/design" → ARMOR.

### WEAPON 7 (added 2026-06-20) — **PROOFSMITH**, a κ=1 kernel-gated formal-proof engine (MATH_TCS prove-side)
Home: [`../ARSENAL/weapons/proofsmith/`](../ARSENAL/weapons/proofsmith/) (`SPEC.md`,
`GROUNDING.md`, `proof_gate.py` + `smt_gate.py` + `selftest_all.py` gate, `proofsmith_router.py`,
`demo_formalize_verify/`, `demo_mathlib_classics/`, the capability A/B under `ab/`, `AUDIT.md`). **Extends
MATH_TCS from "construct an object" to "PROVE a statement."** A **proof-assistant kernel is the SHARPEST cheap
verifier that exists** — the **Lean 4.31.0 kernel** re-checks a fully-elaborated proof term against a tiny
trusted core (de Bruijn criterion) — so PROOFSMITH is a **κ=1 weapon** that ships **nothing the kernel hasn't
accepted with a clean `#print axioms`.** Three modes: **FORMALIZE-VERIFY** (known theorem → reproduce +
kernel-check), **PROOF-SEARCH** (given a formal goal), **LEMMA-EXTEND** (de-novo OPEN conjecture = the rare
frontier → honest-negative expected). **The whole game is the 4-CHECK GATE** (`proof_gate.py`): (1) kernel
accepts · (2) **no `sorry`/`admit`** (sorryAx via `#print axioms` + token scan) · (3) **axiom allow-list**
(`#print axioms` shows only committed-allowed axioms — `{propext, Classical.choice, Quot.sound}` for classical
mathlib; any extra ⇒ REJECT) · (4) **statement-match** (kernel-level `example : <ref> := <thm>`). **Cardinal
infra fact (machine-verified):** `lean` exits 0 on BOTH a `sorry` AND a bogus-axiom proof → the gate parses
`#print axioms`, never the exit code. + a **z3 SMT decidable-slice fallback** (propositional / QF arithmetic,
labeled as a decision procedure, NOT a general proof assistant). **Killer demos (predictions committed first):**
FORMALIZE-VERIFY **7/7** (3 core-Lean reproductions — and_comm / every-nat-even-or-odd / Gauss summation — +
the gate REJECTING sorry/bogus-axiom/wrong-statement versions + a z3 cross-check); mathlib **3/3**
(**Euclid's infinitude of primes reproduced** via `Nat.exists_infinite_primes`, clean axioms, sorry rejected).
**The capability bet was TESTED → CLEAN HONEST NEGATIVE:** kernel-feedback proof-search vs equal-compute
best-of-k on non-memorized lemmas (Haiku prover) = **one-shot 1/4 = best-of-3 1/4 = repair 1/4, 0pp** — and a
**contaminated +25pp first run (answer-key leakage to tool-enabled provers + orchestrator fix-hints) was CAUGHT
and killed** by the box's contamination discipline + kernel measurement (the most valuable output of the A/B).
Built box-style; **independently audited by Sonnet ≠ the Opus generator** (65 tool calls, re-ran every
`#print axioms`, tried `@sorryAx`/`opaque`/macro/`native_decide`/transitive-axiom cheats — **all caught by the
gate**; verdict **SOUND on proof correctness**; **1 minor `#eval` IO side-channel → fixed + regression
self-test**). **Honest nature: a WEAPON ADDED = capability EXPANSION (new task class: *prove* a statement — armor
only ever *checked* a claim), NOT a ≥10% A/B promotion (the A/B was 0pp). The ≥10% CAPABILITY ratchet stays OPEN
at v3.** Ceiling: reproduces/verifies/extends reliably, invents the load-bearing new proof idea rarely; **never
claims to prove an open conjecture**; **kernel-checked ≠ correct English theorem** (autoformalization is κ<1 →
cross-model review).

### WEAPON 8 (added 2026-06-20) — **TRIALGUARD**, a κ-aware clinical-trial & biostatistics rigor engine (STATS/Bio dept)
Home: [`../ARSENAL/weapons/trialguard/`](../ARSENAL/weapons/trialguard/) (`SPEC.md`,
`GROUNDING.md`, `README.md`, `forensics_trial_verify.py` ⭐ + `survival_verify.py` + `meta_trial_verify.py`,
`selftest_all.py` gate, `trialguard_router.py`, `demo_forensics/`, `AUDIT.md`). **The PSYMETRIX/SOCIUS sibling
for biomedicine** — clinical biostatistics is **mixed-κ with one genuinely sharp slice.** **T-FORENSICS** has a
true **κ=1 EXACT** end (GRIM/GRIMMER on reported trial means — **reused** from PSYMETRIX; allocation-ratio &
percentage→count consistency — exact arithmetic) PLUS the **genuinely-new Carlisle baseline-anomaly screen**: under
simple randomization the two-sided baseline p-values of *continuous* variables are i.i.d. **U(0,1)**, so a
systematic departure (a Carlisle–Stouffer Z + KS test) is a distributional anomaly — the RCT analogue of GRIM, but
**κ≈0.9 (a calibrated SCREEN, NOT an exact certificate).** Plus **T-SURVIVAL** (hand-rolled Kaplan–Meier +
**Cox PH partial-likelihood HR**, Breslow ties, **cross-checked vs statsmodels PHReg to 5 decimals**), **T-META**
(**reuses** PSYMETRIX pooling/I²/Egger + adds **trim-and-fill**), **T-REPRO/T-MULTIVERSE** (**reused** from SOCIUS),
**T-EVALUE** (observational causal → E-value sensitivity, never a bare causal claim). κ=0 efficacy/approval/clinical
judgment → armor. **The genuinely NEW pieces are Carlisle + survival; everything else is REUSED and credited.**
**Killer demo (machine-verified, predictions committed first):** GRIM 5.27/43 caught; exact allocation (30/90 ≠
1:1) and percentage (33.3% of n=7) caught; on a **controlled ground-truth corpus** (300 properly-randomized + 300
fabricated-too-similar trials) the Carlisle screen showed **specificity ~99.7% (1/300 clean false flag at α=.001,
well-calibrated)** and **86.7% sensitivity** to over-balancing fabrication, with **ZERO of ~600 outputs affirming
misconduct**; T-META flagged funnel asymmetry (Egger p=.012) + trim-and-fill pulled the pooled effect toward null;
the stratified-trial guard held. **Independently audited** (Sonnet ≠ the Opus generator): EXACT core **sound** (zero
false certificates across exhaustive sweeps), Carlisle screen **well-calibrated** (4/2000 at α=.001, within Poisson
noise), Cox matches statsmodels to 5 decimals, honesty framing **clean** — **3 meta-layer defects found and fixed**
(the `affirms_misconduct()` honesty checker hardened against word-boundary / clause-negation / grounded-citation
edge cases; the Carlisle κ label disambiguated 1.0→0.9). **⚠ THE CARDINAL, NON-WAIVABLE rail (strictest in the
arsenal — clinical domain, patients & reputations): INCONSISTENCY / ANOMALY ≠ FRAUD.** Every forensic output
reports the exact statistic + candidate **benign explanations** (Carlisle's own list: stratified allocation,
correlated covariates, rounding, dropout, unusual-but-real sample) + the method's **false-positive modes**, and
**STOPS** — it never names a person or trial as fraudulent. **Honest nature: a WEAPON ADDED = capability EXPANSION
(certifies consistency/fit/robustness of trial statistics — a new task class), NOT a ≥10% A/B promotion. The
CAPABILITY ratchet stays OPEN at v3.** Ceiling: reproduces/screens/checks reliably; reproduction ≠ clinical truth;
a Carlisle flag is a screen, never a verdict; efficacy/approval/causation are κ=0 → armor.

### WEAPON 9 (added 2026-06-20) — **ECONOMETRIX**, a κ-aware quant-finance & causal-econ rigor engine (ECON_FIN dept) — the FIRST guarded-κ weapon
Home: [`../ARSENAL/weapons/econometrix/`](../ARSENAL/weapons/econometrix/) (`SPEC.md`,
`GROUNDING.md`, `README.md`, `backtest_verify.py` ⭐ + `causal_verify.py` + `selftest_all.py` gate,
`econometrix_router.py`, `demo_overfit_dies/`, `demo_causal/`, `AUDIT.md`). **The SOCIUS/PSYMETRIX sibling for
economics & finance, but the FIRST GUARDED-κ weapon: its core number — a backtest Sharpe — is GAMEABLE, so the
weapon's job is to make an edge/causal claim SURVIVE out-of-sample + robustness + sensitivity, NOT to manufacture a
certificate.** Finance/econ is LOW-κ (≈0.4–0.6); the future is unseen and identification rests on assumptions, so
ECONOMETRIX is **NOT a construction engine and NOT a forecaster** — it stress-tests. **E-BACKTEST** ⭐ (the C14-trap
weapon): **walk-forward OOS** (leakage-safe; purge/embargo aware) + the **Deflated Sharpe Ratio** (Bailey & López de
Prado 2014 — corrects multiple-testing + skew/kurtosis) + **net of transaction costs** + a frozen **look-ahead
detector** — **in-sample Sharpe is NEVER the verdict; DSR>0.95 AND OOS>0 net ⇒ edge, else ABSTAIN.** **E-CAUSAL**:
testable identification diagnostics (DiD **pre-trends/placebo**, RDD **McCrary** density, IV **first-stage F /
Stock-Yogo**) + a **sensitivity number** for the untestable assumptions (**E-value**, **Oster δ**) — never a bare "X
caused Y." **E-ROBUST + E-REPRO** reuse SOCIUS's frozen multiverse/repro verifiers. **Honest ceiling, stated every
run: raises trustworthiness (OOS survival + identification diagnostics); does NOT predict the future or manufacture
truth. A backtest is not a forecast; survival ≠ future profit; κ=0 forecast/"should"/market-direction → armor.**
**Killer demos (predictions committed first):** the **C14 headline on REAL data** — 42 SMA rules searched on
SPY/AAPL/BTC/RELIANCE, best in-sample Sharpe (SPY 1.13) **DIES under walk-forward + Deflated Sharpe net of costs →
ABSTAIN 4/4**, and a look-ahead variant's fake **10.1 Sharpe** is caught (6/6 directional predictions correct); the
**E-CAUSAL demo** — a confounded DiD with **no true effect** but a naive estimate of **+3.76 (p≈1e-31)** is **FLAGGED
by the pre-trends placebo** (p≈1e-53), a clean design passes with an E-value of 7.49, Oster δ separates robust (12.5)
from fragile (0.43), and the real **Card-Krueger DiD +2.76 reproduces** (7/7 predictions correct). Gate built FIRST,
green (genuine-edge PASSES / overfit KILLED DSR≈0 / look-ahead CAUGHT / failed-pre-trends + weak-IV FLAGGED). Built
box-style (load-bearing DSR/PSR, purged-CV, McCrary, Stock-Yogo, Oster δ formulas FETCHED — one Wikipedia DSR-denominator
discrepancy caught + documented; verifiers EXECUTED + machine-gated). **Independently audited by Sonnet ≠ the Opus
generator** (re-derived the math, re-ran the walk-forward with its OWN split code → ABSTAIN 4/4 reproduced, attacked
E-BACKTEST with subtle leaks, checked the DSR trial-count + for smuggled κ=0 forecasts) → **SOUND-WITH-CAVEATS**: no
verdict-changing bug, no dishonesty, but **6 real-bounded defects the generator's self-tests missed** (a leakage
blind-spot for diluted/robust-stat leaks, a correlated-trials deflation hole, missing Oster/min-T/R_max guards, a
McCrary heteroscedasticity caveat) → **all fixed + locked by regression self-tests**; gate + demos re-run green.
**Honest nature: a WEAPON ADDED = capability EXPANSION (a new task class — quant-finance & causal-econ rigor), NOT a
≥10% A/B promotion. The CAPABILITY ratchet stays OPEN at v3.**

### WEAPON 10 (added 2026-06-20) — **FACTHARNESS**, the university-wide grounding / fabrication core facility (Integrity-Office facility, cross-cutting — PROMOTED from SOCIUS S-GROUND)
Home: [`../ARSENAL/weapons/factharness/`](../ARSENAL/weapons/factharness/) (`SPEC.md`,
`GROUNDING.md`, `README.md`, `factharness.py` + `selftest_all.py` gate, `factharness_router.py` the firewall,
`demo_grounding/`, `AUDIT.md`). **NOT a domain weapon — a CROSS-CUTTING Integrity-Office facility every department +
the Provost call**, promoted + hardened from SOCIUS `S-GROUND`. Given any prose claim with a cited source it answers
the **κ=1 question "is the quote/number/citation actually IN the fetched source?"** (exact fabrication check:
**F-QUOTE** verbatim, **F-NUMBER** boundary-safe, **F-CITE** κ=0.7 advisory exact-word author match) and the **κ=0
question "does the source SUPPORT the paraphrase?"** (**F-ENTAIL** → cross-model judge ≠ generator, unsure → ABSTAIN).
The **firewall** (`factharness_router.py`) is wired so every shipped prose claim is grounded-or-abstained:
FABRICATION_FLAG / CONTRADICTED **block** shipping; GROUNDED_BY_JUDGMENT / ABSTAIN ship only behind an explicit
unverified label. **Carries the 3 SOCIUS Round-2 audit fixes + their regression tests forward** (A1 quote-normaliser,
A3 number-boundary 7∉7.5, B-CRITICAL bibliography substring). Gate built FIRST, green (36 → **46 assertions** after the
audit). **Killer demo (predictions committed first):** 6 claims vs a REAL fetched Wikipedia source (Strassen
algorithm) — grounds 2 faithful claims, **catches a fabricated quote, a fabricated number, and a wrong-author cite**,
and **abstains** on a genuine entailment ambiguity; the firewall returns ship_ok=False (3 blocked). **Independently
audited by Sonnet ≠ the Opus generator** (≈66-test attack battery) → **SOUND-WITH-CAVEATS**: κ-separation held (a κ=0
judge can never launder a failed frozen check), but **3 real defects caught — incl. a HIGH κ=1 soundness breach
(Unicode MINUS U+2212 stripped → a sign-flipped number grounded), a bib name-particle gap, and a substring context
bypass — all fixed + locked as regression tests**; gate + demo re-run green. **Honest ceiling: grounded ≠ true** (a
perfectly-grounded claim can cite a wrong source); **FABRICATION_FLAG ≠ fraud** (it reports "does not check against the
supplied source" + candidate causes, never accuses); **entailment is κ=0.** **Honest nature: a core facility PROMOTED
from S-GROUND = capability EXPANSION (institutionalized grounding), NOT a ≥10% A/B promotion. Ratchet stays OPEN at v3.**

### WEAPON 11 (added 2026-06-20) — **REDCELL**, an AUTHORIZATION-GATED, defensive-first security weapon (CS_ENG/Security dept)
Home: [`../ARSENAL/weapons/redcell/`](../ARSENAL/weapons/redcell/) (`SPEC.md`, `GROUNDING.md`,
`README.md`, **`auth_gate.py` the centerpiece**, `flag_verify.py` + `patch_verify.py` κ=1 checkers, `selftest_all.py`
gate, `redcell_router.py`, `demo_redcell/`, `AUDIT.md`). **A κ=1 security weapon scoped to AUTHORIZED + DEFENSIVE use
only — the verifier is sharp (a flag validates or it doesn't; a PoC fires or it doesn't), but the DOMINANT control is
the AUTHORIZATION GATE, which FAILS CLOSED and is the most-audited component.** Three sandboxed modes: **CTF-SOLVE**
(flag validates against the committed checker, constant-time exact/SHA-256), **PATCH-VALIDATE** ⭐ (defensive — a
differential PoC must FIRE on the unpatched build and FAIL on the patched build → PATCH_VALID/INEFFECTIVE/CRASHED/
POC_DOES_NOT_EXERCISE), **VULN-REPRO** (sandboxed CVE repro → a *detection signature*, not a weaponized exploit).
**The gate (`auth_gate.py`) runs BEFORE any security logic and refuses by default:** an explicit recognized
`authorization_context` + `target_is_owned_or_sandbox: True` + a recognized `mode` are REQUIRED; any out-of-scope
category (DoS, mass-targeting, supply-chain, malware-deployment, malicious-evasion, unauthorized target) is REFUSED
*regardless of the asserted context*; anything missing/unknown/malformed → REFUSE. **GROUNDED:** the security policy in
the system guidance IS the spec (no exploits fetched). Built **GATE-FIRST**, the **refusal self-tests as cardinal as
the success tests**, green (20 → **39 assertions** after the audit). **Killer demo (all benign/sandboxed, predictions
committed first):** a self-contained toy crackme **CTF-SOLVE** (flag validates, wrong guess rejected), a **PATCH-VALIDATE**
on a toy auth-bypass + its patch (fires unpatched, fails patched), and the gate **REFUSING** a no-authorization and an
out-of-scope request — all 8 predictions matched. **Independently red-teamed by Sonnet ≠ the Opus generator** (the auth
gate hardest; 35 attacks resisted) → **SOUND-WITH-CAVEATS**, but **3 real defects caught — incl. a HIGH gate FAIL-OPEN
(D1: the real-target guard was an `is False` identity test, so an absent key / None / 0 / "false" bypassed it → ALLOW),
a category alias/type bypass (D2), and a crash-as-PATCH_VALID (D4) — all fixed + locked as regression tests**; gate +
demo re-run green, the fail-open closed. **Honest caveat (D3, documented):** the gate enforces the DECLARED policy — it
is a structured-policy enforcer, NOT a content classifier — so it sits behind the model's own policy reading, only as
strong as the `requested_category` fed it; the sandbox is subprocess+rlimit, not OS-level isolation (trusted build code
only). **Honest ceiling:** authorized/defensive scope only; the gate fails closed (a fail-open is a blocking defect);
outputs are fixes + detections, never deployable weapons; κ=1 is on the artifact's outcome, not a general "secure"
claim. **Honest nature: a weapon ADDED = capability EXPANSION (authorized/defensive security), NOT a ≥10% A/B
promotion. Ratchet stays OPEN at v3.**

### WEAPON 12 (added 2026-06-20) — **REPRO-ML / BENCHWATCH**, a κ-aware ML-evaluation reproducibility weapon (CS_ENG dept)
Home: [`../ARSENAL/weapons/reproml/`](../ARSENAL/weapons/reproml/) (`SPEC.md`, `GROUNDING.md`,
`README.md`, `contam_verify.py` ⭐ + `signif_verify.py` + `repro_verify.py` + `selftest_all.py` gate,
`reproml_router.py`, `demo_reproml/`, `AUDIT.md`). **A mixed-κ "reproduce-and-stress" weapon for ML-eval rigor — a
benchmark number is NEVER a capability.** **R-REPRO** (κ≈0.7): recompute a reported metric (accuracy/macro-F1) from
open predictions within tolerance (reproduce = recompute, not re-quote). **R-CONTAM** ⭐ (κ≈0.8, the headline): measure
train/test overlap as a **rate + method label** — **13-gram word collision** (GPT-3/Brown 2020 decontam convention) +
char-5gram Jaccard near-dup + an order-insensitive token-set Jaccard (word-reorder); `NO_OVERLAP_DETECTED` ≠ "clean".
**R-SIGNIF** (κ≈0.9): is an A>B gap real? **McNemar** (paired, Dietterich 1998) + a **paired bootstrap CI** +
**Bonferroni** for k comparisons — CIs, never bare point ranks. **κ=0 residue** ("X is best/SOTA/most-capable") →
**armor** (ground or abstain). **GROUNDED** (fetched): GPT-3 13-gram decontam (Brown 2020; >90% of QuAC/SQuADv2/DROP
flagged → contamination is common), McNemar/Dietterich 1998, Card et al. 2020 underpowered-NLP. Built **GATE-FIRST**,
green (11 → **20 assertions** after the audit). **Killer demo (predictions committed first):** on the REAL sklearn
`digits` benchmark, LogReg 0.954 / shallow-DT 0.441 both **REPRODUCE** (an inflated number flagged); **contamination
rate goes 0.0 → 0.5** when 3/6 eval items are leaked into "train" (the headline); the real LogReg–DT gap is
**SIGNIFICANT** (p≈4e-60, CI [0.47,0.56]) while a ~0.6pp gap on N=500 is **NOT**; "LogReg is best" routes to armor —
all 11 predictions matched. **Independently audited by Sonnet ≠ the Opus generator** (re-derived the math): **SOUND-
WITH-CAVEATS** — McNemar p-values match a from-scratch re-impl bit-for-bit, the bootstrap is genuinely paired,
**macro_f1 matches sklearn exactly over 200 trials**, Type-I rate 0.016, no κ=0 claim leaks; **5 defects (all
disclosure/coverage, NO false-verdict risk) caught → fixed + locked** (undocumented conservative AND-logic → now emits
`tests_agree`+disclosure; word-reorder evasion → order-insensitive token-set pass added; low-n false-positive → warning;
chi2/p display + tolerance-window disclosure). **Honest ceiling: benchmark ≠ capability** (never crown SOTA → armor);
**contamination is a measured rate, not a verdict** (`NO_OVERLAP_DETECTED` ≠ clean — overlap detection misses rephrased
leakage); significance carries CIs + multiple-comparison correction; reproduction = recompute from artifacts. **Bonus:
can harden the box's own hidden-test hygiene** (the v5 contamination gate). **Honest nature: a weapon ADDED = capability
EXPANSION, NOT a ≥10% A/B promotion. Ratchet stays OPEN at v3.**

---

### WEAPON 13 (added 2026-06-20) — **ENCLOSE**, the certified-numerics weapon — a containment PROOF (NAT_SCI, sibling of SYMBOLICA)
Home: [`../ARSENAL/weapons/enclose/`](../ARSENAL/weapons/enclose/) (`SPEC.md`, `README.md`, `GROUNDING.md`,
`AUDIT.md`, `enclose_gate.py` ⭐ the interval-arithmetic + Krawczyk containment gate, `selftest_all.py`, `demos/`).
**The κ=1 verifier is a CONTAINMENT PROOF, categorically sharper than SYMBOLICA's multi-method AGREEMENT.**
ENCLOSE returns a **guaranteed enclosure `[a,b]` provably containing** the true value, via interval arithmetic
with outward (directed) rounding (Moore's inclusion property: the natural interval extension of `f` over a box
is a guaranteed outer bound of its true range) + the **Krawczyk** existence-uniqueness test (`K(X) ⊂ int(X) ⇒
unique root in X`). The gate never trusts the claimed answer — it recomputes its own rigorous `E` and:
`E ⊆ claim` → **ACCEPT**; `claim ∩ E = ∅` → **REJECT**; tighter-than-provable / malformed / singular →
**ABSTAIN**. v0 surface: verified definite integrals (incl. **non-elementary** like `∫₀¹ e^(−x²)`, where
SYMBOLICA's symbolic leg has nothing to agree on), Krawczyk roots, recomputable constants. **Built on
`mpmath.iv` with NO new dependency** (machine-probed: basic iv arithmetic is genuinely outward-rounded;
`iv.quad` is broken → quadrature built ON iv arithmetic). Because mpmath.iv rounds in SOFTWARE, the
`-ffast-math` caveat does not apply; the residual is mpmath.iv's own rounding correctness (not formally
verified) — named, not hidden. **Cross-model Sonnet audit: SOUND** (no false-accept across 17 attack categories;
4 hardening findings fixed + frozen). **Honest nature: a weapon ADDED = capability EXPANSION, NOT a ≥10% A/B
promotion. The rectangle-rule quadrature is rigorous but LOOSE (ABSTAINs rather than over-certify). Ratchet
stays OPEN at v3.**

---

## 1c. THE KIT / EQUIPMENT LAYER (added 2026-06-20) — beyond ARMOR+WEAPONS+HELMET (EVOLUTION_LOG C48)
Home: the 8 dirs under [`../ARSENAL/weapons/`](../ARSENAL/weapons/) (`crucible · gloves · shield ·
triage · bootstrap · vault · composeauth · shoes_routing`); design + honest framing in
[`KIT_EXPANSION_PROPOSAL.md`](../RESEARCH/backlog/KIT_EXPANSION_PROPOSAL.md). Extends the knight's-kit analogy with pieces that each
passed the κ-gate on their own (the metaphor is motivation, not architecture). Built gate-FIRST via a multi-agent
workflow, cross-model audited (Sonnet ≠ the Opus builders — **which found REAL false-accepts the builders' selftests
missed**), fixed with regression tests, and independently re-verified ALL-CLOSED (6/6 exploits dead, 8/8 selftests
green on the orchestrator's own re-run). The pieces, by layer:
- **CRUCIBLE** — a **META-WEAPON**: adversarially probes the box's OWN κ>0 gates (false-accept / false-reject /
  metamorphic / silent-pass) against an INDEPENDENT oracle. **A KILL is a κ=1 exhibit; a no-kill is CONFIDENCE,
  never "sound"** (Dijkstra, machine-enforced). The immune system, finally tested.
- **GLOVES** + **COMPOSEAUTH/G3** — the **EFFECTOR layer** (the genuinely-new capability: the box can now ACT on the
  world, safely-gated). GLOVES = per-action reversibility×blast-radius tiers + param/expiry/single-use/scope tokens +
  dry-run→commit + fail-closed + the CVE-2025-53773 self-downgrade BLOCK; G3 = a running blast-radius budget closing
  the salami/composition hole. **Honest ceiling: tamper-resistance + dry-run attestation are pure-software-LIMITED
  (ARMOR-class without an external signing authority — disclosed in code); irreversible/financial ⇒ a human.**
- **SHIELD** + **TRIAGE** + **VAULT** + **SHOES-routing** — **ARMOR-HARDENING / EFFICIENCY / INFRA**: SHIELD's 4 κ=1
  rails (incl. the verifier TAINT-RAIL that hardens every weapon) + a κ=0 abstain rail (NOT a weapon; injection is
  not fully solvable); TRIAGE's failure-class→mitigation table (makes ARMOR operational); VAULT's verifier-gated
  cross-session memory (only machine-verified results are facts); SHOES' FOOTING calibration + ROUTE-PLANNER.
- **BOOTSTRAP** — the **ARSENAL-GROWTH** mechanism: find + VALIDATE-by-run a new domain's exact verifier (κ>0) or
  return κ=0 ARMOR-only — grows the arsenal without faking κ.

**Honest nature (non-waivable): the kit = CAPABILITY EXPANSION (act-on-the-world + falsify-our-own-gates), NOT a
≥10% A/B promotion — first builds, un-A/B-tested, no shared arena. The ≥10% CAPABILITY ratchet stays OPEN at v3.**
None makes the model smarter; the kit makes the box harder to fool, safer when it acts, more honest about its limits.

---

## 1b. THE HELMET (added 2026-06-20) — "University Mode": the conductor worn OVER armor + weapons
Home: [`../ARSENAL/HELMET/`](../ARSENAL/HELMET/) (`SPEC.md`, `README.md`, `registry.json`,
`provost.py` ⭐ deterministic routing brain — **8/8 selftest**, `tests/` with committed predictions + peer-reviewed
runs, `AUDIT.md` the cross-model red-team). **The HELMET is NOT a weapon — it is the third LAYER**, a meta-orchestrator
that, given ANY problem, makes the model behave like a top research university and **CALLS armor + weapons** (it does
not replace them). Five components: a **PROVOST** triages (domains · κ-profile · task type · known/open · stakes ·
triviality) and routes; a **REGISTRAR** scales the institute to the problem (DESK → STANDARD → FULL → CROSS — the
anti-theater dial: a one-liner gets ONE specialist, not a faculty); a **DEPARTMENT REGISTRY** convenes the right
specialists (8 departments — each a weapon for κ>0 or an armor method-cluster for κ=0); the **R&D LIFECYCLE** runs
(intake → literature → design → execute → **PEER REVIEW, cross-model ≠ generator** → revise → deliver); the
**INTEGRITY OFFICE** enforces the honesty rails (no claim without proof; reproduction ≠ discovery; κ=0 → abstain;
mandatory independent review); a **DEAN** integrates cross-disciplinary work. **The non-waivable honest framing
(stated in every University-Mode output): the Helmet makes the model ORGANIZED, RIGOROUS, COMPREHENSIVE — NOT
smarter; it cannot exceed the underlying model's capability ceiling.** Grounded in fetched science-of-science
sources (Wuchty 2007, OSC 2015, AlShebli 2018, **Wu 2019 "large teams disrupt less" → the Registrar's anti-theater
rule**, Bornmann 2010 peer-review κ≈.17 → the cross-MODEL audit rule, Fagan 1976) **with counter-evidence preserved**.
**Validated:** the runnable orchestrator (a Workflow generalized from `FRONTIER_ENGINE_WORKFLOW`) routed 3
committed-prediction problems across the κ-spectrum correctly (κ=1 construct → verified Sidon set; medium-κ → GRIM
where the executed check overrode an asserted prediction; κ=0 normative → honest abstention), each peer-review-confirmed
by a model ≠ the generator. An **independent Sonnet red-team** (≠ the Opus Provost) on two baits (over-convene +
κ=0 over-claim) returned **ROBUST_WITH_CAVEATS**: over-claim resisted cleanly; a real intake defect (a groundable
fact misclassified κ=0 → spurious abstention flag) was caught and **fixed + re-verified** (added a `groundable`
dimension; abstention mandated only for κ=0 *and not groundable*). **HONEST nature: an orchestration LAYER = a
CAPABILITY EXPANSION (process — routing/grounding/independent review/honest abstention — NOT raw capability), the
same class of stamp as v4/v5 integration, NOT a ≥10% A/B promotion (no shared arena). The ≥10% CAPABILITY ratchet
stays OPEN at v3.** **When invoked:** genuine R&D-grade problems (multi-faceted, stakes, novelty) — gated by the
Registrar, which routes trivial queries to a single specialist (DESK) and *declines* to convene a faculty.

---

## 2. THE WHEN/WHERE ROUTER (the centerpiece — exactly when and where to draw the weapon)

```
STAGE 0 — FREEZE. Lock goal + done-criterion + the SOURCE-OF-TRUTH (which checker judges each load-bearing
          claim) BEFORE routing. Underdefined → abstain; do not route.

STAGE 1 — κ-GATE (the only gate that can route to a weapon).
   Q: does a cheap, EXACT, non-gameable verifier exist, or can one be built within budget?
      qualifies iff ALL of: (1) re-checks the actual returned OBJECT from scratch · (2) independent of the producer ·
      (3) a false-positive is detectable — a result > KNOWN_MAX flags a BUG, not a win · (4) NOT gameable by overfit
      — the score is a STRUCTURAL property of the object, not a return-number on seen data (a held-out/backtest score
      is "exact" yet gameable → does NOT qualify; this is the C14 Sharpe-overfit trap).
   κ = 0  → ARMOR ONLY (Branch A). The weapon NEVER applies. A weak/gameable proxy (LLM-judge / human rating /
            approximate fitness / in-sample score) does NOT raise κ — it is a reward-hacking surface; decline it.
   κ = 1  → weapon-eligible → STAGE 2.

STAGE 2 — KNOWN vs OPEN target.
   KNOWN proven object / named optimum / named construction   → Branch B  (FETCH-KNOWN)
   OPEN  (only a lower bound; no published object at scale)    → Branch C  (SEARCH-OPEN)
   NOTE: KNOWN/OPEN is authoritative ONLY when resolved by a grounded lookup table (capset, Sidon, …) or a FETCHED
   literature status — NOT from task-description words alone. For any unlisted domain: fetch the literature status
   first; WHEN IN DOUBT, treat as OPEN (Branch C) and make structure-fetch the first search step.
```

| branch | when (signature) | what to run | EXPECTED-OUTCOME CONTRACT (commit before running) |
|---|---|---|---|
| **A — ARMOR ONLY** | κ=0: judgment, synthesis, strategy, writing, ethics; "looks like math" but the deliverable is a proof *sketch* with no certified object; any proxy-only scorer | v3/v4 spine: cross-model panel + scored **abstention**; honesty veto | best cross-model consensus or a scored abstention. **No object produced.** Panel agreement = shared-blind-spot *risk*, not a result |
| **B — FETCH-KNOWN** | κ=1 AND target is a named/proven object (`KNOWN_MAX` exists) | fetch structure → instantiate → exact-solve residual → independent re-verify. **Search budget GATED behind a completed structure-fetch** | a machine-verified **reproduction** of the known object, *labeled "reproduction of [source], verified [date]"*. **Never** a record/solve |
| **C — SEARCH-OPEN** | κ=1 AND target is open (`KNOWN_LB` only) | the Frontier Construction Engine: state-vector → W1-derive structure → propose-gate-audit loop, executable, frozen-verifier-gated | a certified witness **strictly > KNOWN_LB** (audited) **or** an honest plateau + structural map. **Never** "frontier closed" |
| **D — SOCIUS (mixed-κ)** | **EMPIRICAL social-science task WITH data** (a quantitative finding/claim + a dataset or open data+code): reproducibility, robustness, measurement, causal-from-observational, or sampling questions | draw **SOCIUS** (`socius_router.py`): it splits the task — κ>0 pieces → frozen verifiers (S-REPRO/S-MULTIVERSE/S-MEASURE/S-CAUSAL/S-SAMPLE); κ=0 pieces → armor (ground/abstain) | per-piece κ-labelled verdicts; the headline names **what survived AND what DIED under stress**; **trustworthiness raised, truth NOT manufactured.** *Pure theory/interpretation with NO data → this is κ=0 → Branch A (ARMOR ONLY), do NOT draw SOCIUS.* |
| **E — PSYMETRIX (mixed-κ, sharp exact end)** | **QUANT-PSYCH / PSYCHOMETRIC task WITH data or reported stats**: reported summary statistics on bounded/integer scales or a body of p-values (forensics); scale reliability/dimensionality; cross-group DIF; effect reproduction; study design/power; meta-analysis | draw **PSYMETRIX** (`psymetrix_router.py`): κ=1 EXACT forensics (GRIM/GRIMMER/SPRITE/TIVA/p-curve/Benford) **PROVE (im)possibility**; executable pieces (reliability/disattenuation/dimensionality/DIF/meta/power/optimal-items); κ=0 interpretation → armor | exact (im)possibility certificates where the math is exact, fit/robustness elsewhere; **certifies CONSISTENCY/FIT/ROBUSTNESS, never TRUTH.** **⚠ INCONSISTENCY ≠ FRAUD: report the arithmetic, never accuse.** *Pure theory/interpretation with NO data/stats → κ=0 → Branch A (ARMOR ONLY).* |
| **F — OPTIMA (κ=1 exact OR)** | **DISCRETE OPTIMIZATION with a clean model**: scheduling / routing / packing / assignment / allocation — "find the best feasible X subject to these constraints", or "is any feasible X possible?" | draw **OPTIMA** (`optima_router.py`): EXACT-SOLVE (clean+tractable → certified optimum), BOUND-PROVE (hard/large → feasible + a rigorous **independent** bound + the honest gap, **never optimal on a timeout**), REPRODUCE-RECORD (benchmark optimum, labeled reproduction). The **independent 4-part certificate** (feasibility/objective/gap=0-dual/IIS) is the verdict, **NOT the solver's status string** | a machine-certified optimum **for the FORMAL MODEL** (gap=0 / matching dual / a different exact method), or a feasible **bound-with-gap** on a timeout, or an **IIS** infeasibility proof. **⚠ "optimal FOR THIS MODEL", not the real problem — modeling is κ<1, cross-model-reviewed.** *Fuzzy "optimize our strategy" with no formalizable exact objective → κ=0 → Branch A (ARMOR ONLY).* |
| **G — SYMBOLICA (κ≈0.9 exact-by-agreement)** | **CLOSED-FORM / EXACT computation**: a definite integral / infinite sum / ODE / limit with a plausible closed form, an identity to check, a known special value, or a tight analytic bound — "evaluate / prove this exactly", "is this identity true?" | draw **SYMBOLICA** (`symbolica_router.py`): CLOSED-FORM (sympy.integrate vs mpmath.quad vs scipy.quad), IDENTITY-PROVE (`simplify→0` AND K-point numeric; series→0 as 3rd), SERIES (convergence-gated; mpmath.nsum + sympy.summation), SPECIAL-VALUE (reproduce vs a fetched reference). The **≥2-independent-method AGREEMENT** is the verdict, **NOT one CAS's output** | an exact value/identity certified by ≥2 independent families (a methodologically-different 3rd on load-bearing cases), labeled **"verified to D digits"** or **"symbolically proven (simplify→0; not kernel-grade)"** — never swapped. **⚠ a single-engine answer is a CLAIM; agreement of same-family methods is a shared-blind-spot RISK; "proven" ≠ "verified to D digits".** *No closed form → NUMERIC-FALLBACK (high-precision value + error bars). What it MEANS physically → κ=0 → Branch A (ARMOR ONLY).* |
| **H — CODEFORGE (κ=1 code/algorithm)** | **CODE / ALGORITHM task with an executable or exact verifier**: synthesize code to a spec; superoptimize a correct function; discover a combinatorial algorithm object (sorting network, matrix-mult scheme) | draw **CODEFORGE** (`codeforge_router.py`): SYNTH-VERIFY (hidden+property+differential, UNPREDICTABLE fuzz seed; hard-coding → GAMING_DETECTED), SUPEROPT (κ=1 differential correctness + a *measured* benchmark), ALGO-DISCOVER (sorting net via 0/1 principle / matmul scheme via non-commutative symbolic identity; KNOWN→reproduce, OPEN→search). **Self-reports ignored; the frozen verifier is the judge** | a frozen-verifier-passed object: synthesized code passing the held-out battery, a correct+faster superopt, or a certified algorithm object (reproduction labeled; OPEN search → audited witness or honest negative). **Capability A/B (iterate vs best-of-k) = +0pp honest negative.** *κ=0 "is this code GOOD / design this architecture", or a gameable proxy-only scorer (LLM-judge) → Branch A (ARMOR ONLY); routine codegen the test-runner already handles → not worth the weapon.* |
| **I — PROOFSMITH (κ=1 formal proof)** | **PROVE a STATEMENT with a kernel as judge**: formalize + machine-check a known theorem; prove a given formal goal; fill auxiliary lemmas — "prove that …", "is this lemma true (formally)?", "formalize and verify this" | draw **PROOFSMITH** (`proofsmith_router.py`): FORMALIZE-VERIFY (known theorem → reproduce + kernel-check), PROOF-SEARCH (given a formal goal), LEMMA-EXTEND (de-novo OPEN conjecture → honest-negative expected). The **4-check kernel gate** (`proof_gate.py`) is the verdict: kernel-accepts + **no `sorry`** (sorryAx via `#print axioms`) + **axiom allow-list** + **statement-match** (`example : ref := thm`); z3 SMT decidable-slice fallback. **`lean`'s exit code is NEVER trusted (it exits 0 on `sorry`/bogus-axiom) — the gate parses `#print axioms`** | a kernel-checked proof term shipped with a clean `#print axioms` (no sorry, no rogue axiom) of the **committed FORMAL statement** — a labeled reproduction for known theorems, or an honest "no proof found". **Capability A/B (kernel-feedback vs best-of-k) = 0pp honest negative.** **⚠ kernel-checked ≠ correct English theorem — autoformalization is κ<1, cross-model-reviewed; NEVER claim to prove an open conjecture.** *κ=0 "is this informal argument convincing / the right proof strategy" → Branch A (ARMOR ONLY).* |
| **J — TRIALGUARD (mixed-κ, sharp exact slice, STRICTEST rail)** | **CLINICAL-TRIAL / BIOSTAT task with reported stats or data**: reported trial means/SDs, a baseline (Table 1) of continuous variables, group sizes/percentages, survival/time-to-event data, a body of studies to meta-analyse, or an observational causal claim | draw **TRIALGUARD** (`trialguard_router.py`): κ=1 EXACT (GRIM/GRIMMER reused; allocation-ratio & percentage→count) + the **Carlisle baseline-anomaly SCREEN** (κ≈0.9, Stouffer-Z + KS vs U(0,1), continuous-only, stratified-vars excluded); T-SURVIVAL (KM + Cox PH vs statsmodels PHReg); T-META (pool/I²/Egger + trim-and-fill); T-REPRO/T-MULTIVERSE (reused SOCIUS); T-EVALUE (observational causal → E-value); κ=0 efficacy/approval/clinical judgment → armor | exact (im)possibility certificates where the arithmetic is exact + a calibrated Carlisle anomaly SCREEN (FP rate ~α, inflated by correlation/stratification) + reproduced survival/meta; **certifies CONSISTENCY/FIT/ROBUSTNESS, never CLINICAL TRUTH or EFFICACY.** **⚠ THE STRICTEST RAIL: INCONSISTENCY/ANOMALY ≠ FRAUD — exact statistic + benign explanations + false-positive modes, then STOP; never accuse (clinical domain).** *κ=0 "does the drug work / approve it / is it clinically true" → Branch A (ARMOR ONLY); categorical-variable Carlisle use is unsound → excluded.* |
| **K — ECONOMETRIX (mixed, GUARDED-κ — in-sample is NEVER the verdict)** | **QUANT-FINANCE / CAUSAL-ECON task with data**: a market-edge / trading-rule claim with price data; a quasi-experimental causal claim (DiD / RDD / IV); a finding resting on analytic choices; a published economic statistic with open data+code | draw **ECONOMETRIX** (`econometrix_router.py`): **E-BACKTEST** (walk-forward OOS + **Deflated Sharpe Ratio** + net costs + a frozen look-ahead detector — the in-sample score is GAMEABLE and is NEVER the verdict, C14); **E-CAUSAL** (DiD pre-trends / McCrary density / weak-IV first-stage F / Oster δ / E-value); **E-ROBUST + E-REPRO** (reused SOCIUS); forecast/normative/market-direction → κ=0 armor | an edge reported ONLY if it SURVIVES walk-forward OOS net of costs AND DSR>0.95 (else **ABSTAIN**); a causal effect reported ONLY with its testable diagnostics + a sensitivity number for the untestable assumptions; **a result that DIES under stress is the headline.** **⚠ NON-WAIVABLE: a backtest is NOT a forecast (survival ≠ future profit); an in-sample/backtest Sharpe is a gameable proxy → does NOT raise κ.** *κ=0 "will it go up / should we / market direction" → Branch A (ARMOR ONLY).* |
| **L — REPRO-ML / BENCHWATCH (mixed-κ ML-eval rigor)** | **ML-EVALUATION claim with artifacts**: a reported benchmark metric + open predictions/data; a train corpus + an eval set (contamination); a model-A-vs-B comparison on the same test set | draw **REPRO-ML** (`reproml_router.py`): **R-REPRO** (recompute the metric from artifacts within tol — reproduce, not re-quote); **R-CONTAM** ⭐ (13-gram + char-Jaccard + token-set overlap → a contamination RATE + method label; `NO_OVERLAP_DETECTED` ≠ clean); **R-SIGNIF** (paired McNemar + bootstrap CI + Bonferroni); "X is best/SOTA/capable" → κ=0 armor | a reproduced metric, a method-labeled contamination rate, a CI-bearing significance verdict — **a benchmark number is NEVER a capability.** **⚠ contamination is a measured rate, not "clean"; significance carries CIs + multiple-comparison correction; reproduction = recompute from artifacts.** *κ=0 "model X is best / most capable / production-ready" → Branch A (ARMOR ONLY).* |
| **M — REDCELL (κ=1 security, AUTHORIZATION-GATED, fail-closed)** | **AUTHORIZED + DEFENSIVE security task**: a CTF challenge; a known PoC + a patch on an OWNED system; a published CVE to reproduce in a sandbox for detection — WITH an explicit authorization context | draw **REDCELL** (`redcell_router.py`) ONLY after `auth_gate.py` ALLOWs: **CTF-SOLVE** (flag validates), **PATCH-VALIDATE** (differential PoC fires-unpatched/fails-patched in sandbox), **VULN-REPRO** (sandboxed repro → a detection signature). The gate runs FIRST and **refuses by default** | a κ=1 verification artifact (flag valid / patch pass-fail / detection) from a sandboxed, owned-target, authorized task — **a fix/detection, NEVER a deployable weapon.** **⚠ FAIL-CLOSED: no authorization context, or any out-of-scope category (DoS / mass-targeting / supply-chain / malware / malicious-evasion / unauthorized target) → REFUSE regardless of framing. The gate enforces the DECLARED policy, not free-text intent.** *Any unauthorized / real-world / destructive / at-scale request → REFUSE (not Branch A — an explicit refusal).* |

**POSITIVE triggers — DRAW the CONSTRUCTION weapon (κ=1, produce-an-object):** extremal-combinatorics
constructions (caps, Sidon/B₂ sets, Golomb rulers, no-3-in-line); matrix-multiplication / algorithm discovery
(à la AlphaTensor/Dev); packing & coding-theory records (kissing numbers, best [n,k,d] codes); SAT/CP
object-finding (Ramsey/Schur witnesses); optimization with an **exact** scorer; "find a hard object that is
cheap to check."

**POSITIVE trigger — DRAW SOCIUS (mixed-κ, raise trustworthiness, do NOT produce a record):** an **empirical
social-science task with data** — reproduce a published quantitative finding; stress it (specification-curve /
multiverse); check a scale's reliability / measurement-invariance across compared groups; sensitivity-analyse a
causal claim from observational data (E-value); check sampling/generalisability. SOCIUS then routes its own
κ>0 pieces to frozen verifiers and its κ=0 pieces to armor. **κ=0 pure theory/interpretation with no data is
NOT a SOCIUS trigger → Branch A (armor only).**

**POSITIVE trigger — DRAW PSYMETRIX (mixed-κ with a SHARP exact end):** a **quant-psych / psychometric task
with data or reported stats** — certify whether reported means/SDs/Ns or a body of p-values are mathematically
(im)possible (EXACT forensics: GRIM/GRIMMER/SPRITE/TIVA/p-curve/Benford); check a scale's
reliability/dimensionality; test cross-group DIF; reproduce an effect; evaluate study power / select optimal
items; meta-analyse with publication-bias correction. PSYMETRIX routes its κ=1 pieces to frozen verifiers
(forensics is EXACT) and κ=0 interpretation to armor. **⚠ NON-WAIVABLE: a forensic inconsistency is reported
as inconsistency WITH the exact arithmetic — NEVER as fraud. κ=0 pure theory with no data → Branch A (armor only).**

**POSITIVE trigger — DRAW OPTIMA (κ=1 exact OR):** a **discrete optimization problem with a clean model** —
schedule/route/pack/assign/allocate to minimize/maximize an objective subject to constraints, or decide
feasibility ("does any valid configuration exist?"). OPTIMA models it (CP-SAT/integer-exact), solves, and the
**independent 4-part certificate is the verdict**: feasibility re-checked from scratch + objective recomputed +
optimality earned by gap=0 (exhaustive / LP weak-duality / a different exact method — the solver's own bound is
the honest weakest tier) + infeasibility proven by an IIS. Timeout ⇒ a **bound with a gap, never optimal**;
benchmark optimum ⇒ a **labeled reproduction**. **⚠ NON-WAIVABLE: "optimal FOR THIS FORMAL MODEL", not the
real-world problem — the modeling (words → vars/constraints/objective) is κ<1 and is cross-model-reviewed. A
fuzzy "optimize our strategy" with no formalizable exact objective → κ=0 → Branch A (armor only).**

**POSITIVE trigger — DRAW TRIALGUARD (mixed-κ with a sharp exact slice; STRICTEST honesty rail):** a **clinical-
trial / biostat task with reported statistics or data** — check whether reported trial means/SDs are
arithmetically possible (EXACT GRIM/GRIMMER, reused) or group sizes/percentages match the stated allocation
(exact); screen a baseline (Table 1) of **continuous** variables for departure from the U(0,1) expected under
randomization (the **Carlisle** anomaly screen, κ≈0.9 — calibrated, NOT exact); reproduce a Kaplan–Meier / Cox HR
(T-SURVIVAL); meta-analyse with publication-bias correction (Egger/trim-and-fill); sensitivity-analyse an
observational causal claim (E-value). TRIALGUARD routes its κ>0 pieces to frozen verifiers and κ=0
efficacy/approval/clinical judgment to armor. **⚠ THE STRICTEST NON-WAIVABLE RAIL: INCONSISTENCY / ANOMALY ≠
FRAUD** — every forensic output reports the exact statistic + candidate benign explanations (stratified allocation,
correlated covariates, rounding, dropout) + the method's false-positive modes, and **STOPS**; it never names a
person or trial as fraudulent (the domain is clinical — patients & reputations). **κ=0 "does the drug work / should
it be approved / is it clinically true" → Branch A (armor only); categorical-variable Carlisle use is unsound →
excluded.**

**NEGATIVE list — do NOT draw the weapon even when tempting:** (1) judgment/synthesis with no exact verifier;
(2) "proof" tasks whose deliverable is an argument, not a certified object; (3) routine codegen (armor's
test-runner already suffices — the weapon adds cost, no Q); (4) proxy-only scorers (gameable → will be gamed);
(5) open problems with no constructive certificate even in principle (running the weapon is theater);
(6) voting/aggregation arenas (→ armor's panel, not the weapon).

**CONFLICT RULE:** if a task matches a POSITIVE trigger AND a NEGATIVE item, **the negative wins (weapon off).**
Note the two kinds of negative: items (1)(2)(4)(5) are **κ=0** (no real verifier — armor only); items (3)(6) are
**κ=1 but not worth it** (a verifier exists, but armor's test-runner / panel already suffices and the weapon only
adds cost) — route to armor, not because it's unverifiable but because the weapon's marginal Q is ~0.

---

## 3. Cost, escalation & the hard-won discipline rules

- **Cheapest weapon first; structure BEFORE compute** — enforced, not preferred (the fetch-gate blocks the
  exact-solver until a structure is in hand). Log `time_to_first_source` and `search_before_source`; penalize the
  "long solver run before reading the paper" mode directly in E=Q/B.
- **⚠ THE WEAK-WEAPON-CAP ERROR (the season's costliest bug):** *never declare a plateau "structural" until the
  STRONG instance of the weapon has run.* A plateau from a weak/cheap weapon is a self-imposed cap mislabeled as
  an honest negative. (Proven both ways: no-3-in-line — weak ILS stalled at 2k−1, exact CP-SAT hit the proven 2k;
  cap-set — strong compute genuinely plateaus at 224, *then* structure reached 236.)
- **Saturation tripwire:** ≥2 heterogeneous *strong* methods plateauing < a known bound ⇒ STRUCTURAL_GAP → switch
  weapon-class, do **not** add more of the same compute.
- **Permission to stop:** stop when (a) FETCH-KNOWN reproduces the object, (b) SEARCH-OPEN beats `KNOWN_LB` and
  survives audit, (c) the tripwire fires with no class-switch available, or (d) the compute hard-stop is hit.
  Honest abstention is the correct output whenever (a)/(b) is unmet.

## 4. The model ladder, applied to the weapon (v4 ladder; ⚠ Fable-inactive fallback active 2026-06-12)
| weapon stage | task class | engine |
|---|---|---|
| **Propose** structural ideas | genuinely un-executable creative construction | **Fable 5** — *but Fable is INACTIVE → reroute to Opus 4.8 and FLAG low confidence; lean harder on making the idea executable so the machine, not the model, carries it* |
| **Build + verify** each candidate | machine-checkable → execute ($0); code → any tier | **Sonnet/Haiku writes code; the FROZEN verifier is the gate** (the gate, not the model, makes it safe) |
| **Audit** any record-claim | adversarial, independence (C8) | **a model ≠ the generator** (Sonnet/Haiku — *never Opus-audits-Opus while Fable is down*) |

## 5. Honesty rails specific to the weapon (non-waivable, F11)
- **No record** without a machine-certified object **strictly beating prior art** AND an **independent
  cross-model audit** (auditor ≠ generator). Agreement of proposer+auditor on a "win" is a shared-blind-spot risk
  → requires a third independent machine check.
- **Reproduction is labeled reproduction** (source + date). Carry the `known_status` field (KNOWN_MAX reached /
  KNOWN_LB matched / below LB). `beats_optimal_IMPOSSIBLE=true` ⇒ a bug, not a discovery.
- **Never claim to close an open problem** — exhibit the verified object or report you did not find one.

## 6. Where v5 stands vs the seeded plan (honest reconciliation)
- v5 was **originally seeded** ([`V5_KICKOFF.md`](../../MARK_0/01_box_versions/V5_KICKOFF.md), 2026-06-11) as a *self-evolving ARMOR* capability
  push, lead lever = **execution-gated generate→repair**. That lever was **probed and returned honest NEGATIVES**
  on construction arenas: at Haiku, repair scored **0% — beaten by matched-budget resampling (−38pp) AND by a
  dumb no-model random-greedy script (−50pp)**; at Sonnet, repair **tied best-of-3 (+0pp)** — feedback was never
  the active ingredient (see `benchmarks/v5_repair_probe/PROBE_LOG.md`). Its faithful ≥10% promotion run is
  **blocked** (Fable inactive + no API/hidden-test infra). The aggregation A/B was **killed pre-build** (unsound).
- **Therefore v5's shipped content is the WEAPON integration (this doc), not the repair lever.** The repair lever
  remains an *open, unproven* armor-capability bet (retry when Fable + a contamination-free hidden-test code arena
  are available). The ≥10% capability ratchet stays **open at v3**.

## 7. Pointers
- Armor: [`BOX_V4.md`](../../MARK_0/01_box_versions/BOX_V4.md) / [`BOX_V3.md`](../../MARK_0/01_box_versions/BOX_V3.md). Weapon: [`../ARSENAL/`](../ARSENAL/)
  (THEORY = state-vector + weapon-map; ALGORITHM_AND_WEAPONS = the loop; FRONTIER_ENGINE_WORKFLOW = the validated run).
- Evidence the weapon is real: `../ARSENAL/cap_set/cap_n7_size236_CF.json` (verified), `N7_PLATEAU_2026-06-10.md`,
  `no3line/COLD_TEST_2026-06-10.md`. Lineage: `../Legacy/EVOLUTION_LOG.md` C32. Repair-lever status: `benchmarks/v5_repair_probe/PROBE_LOG.md`.
