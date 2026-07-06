# WEAPONS BACKLOG — the University's arsenal to-do list

*An ordered build queue for the HELMET's departments. Work top-to-bottom; one weapon at a time.
This file is the single source of truth for weapon state — update the STATUS column as each ships.*

> **The one rule that orders this list (owned/verified by the project):** a **weapon** requires **κ>0** —
> a cheap, EXACT, non-gameable verifier. Domain does not decide it; the *verifier* does. Sharper verifier =
> higher-value weapon (the machine, not the model, carries the result). κ=0 domains get **armor (ground +
> abstain)** — building a "weapon" there is theater. **This backlog is a design roadmap (κ=0 prioritization),
> NOT a verified result.** Each item lists the factual anchor to FETCH-confirm before building it.

## Legend
- **κ tier:** **S** = sharp exact certificate (cap-set / GRIM class) · **A** = mixed-κ, reproduce-and-stress
  (SOCIUS class) · **0** = no verifier → armor only, NOT a weapon.
- **STATUS:** ✅ built · 🔜 next · ⬜ queued · 🚫 not-a-weapon (armor).

---

## BUILT (12)
| # | weapon | dept | κ | verifier | status |
|---|---|---|---|---|---|
| — | **Frontier Construction Engine** | MATH_TCS (construct) | S | `capset_verify.py` (re-check the object from scratch) | ✅ |
| — | **SOCIUS** | SOCIAL_SCI | A | 6 frozen verifiers (S-REPRO/MULTIVERSE/MEASURE/CAUSAL/SAMPLE/GROUND) | ✅ |
| — | **PSYMETRIX** | QUANT_PSYCH | A (+S forensics) | GRIM/GRIMMER/SPRITE exact certificates | ✅ |
| 5 | **ECONOMETRIX** | ECON_FIN | A (guarded ≈0.4–0.6) | E-BACKTEST (walk-forward + **Deflated Sharpe** + costs + look-ahead detector) · E-CAUSAL (DiD pre-trends/McCrary/weak-IV F/Oster δ/E-value) · E-ROBUST + E-REPRO (reused from SOCIUS). **The FIRST guarded-κ weapon: in-sample/backtest score is NEVER the verdict (C14)** | ✅ |
| 6 | **TRIALGUARD** | STATS/Bio | A (+S forensics slice) | EXACT GRIM/GRIMMER (reused) + allocation-ratio/percentage→count · **Carlisle baseline-anomaly SCREEN** (κ≈0.9 Stouffer-Z + KS vs U(0,1), continuous-only, stratified-excluded) · T-SURVIVAL (KM + Cox PH vs statsmodels PHReg, 5-dec) · T-META (+trim-and-fill) · T-REPRO/T-MULTIVERSE (reused SOCIUS). **STRICTEST rail: INCONSISTENCY ≠ FRAUD — every flag carries benign explanations + FP modes, never accuses** | ✅ |
| 1 | **CODEFORGE** | CS_ENG | S | 4 frozen verifiers — SORTNET (0/1 principle, exact) · MATMUL (non-commutative symbolic identity) · SYNTH-VERIFY (hidden+property+differential, unpredictable seed) · SUPEROPT (differential correctness + benchmark); passes-good/catches-broken/rejects-gaming. **Capability A/B = +0pp honest negative** | ✅ |
| 3 | **OPTIMA** | CS_ENG/OR | S | `optima_gate.py` — independent 4-part certificate (feasibility / objective / gap=0-dual / IIS); the solver's OPTIMAL status is NEVER trusted | ✅ |
| 4 | **SYMBOLICA** | NAT_SCI | A (κ≈0.9, agreement-not-kernel) | `symbolica_gate.py` — ≥2 INDEPENDENT methods agree (sympy vs mpmath vs scipy/series) + convergence/branch-cut/domain checks; a single-engine answer is a CLAIM, not a result | ✅ |
| 2 | **PROOFSMITH** | MATH_TCS (prove) | S | Lean 4 kernel + `#print axioms` 4-check gate (`proofsmith/proof_gate.py`): kernel-accepts / no-sorry(sorryAx) / axiom-allow-list / statement-match(`example : ref := thm`); z3 SMT decidable-slice fallback. **Capability A/B = 0pp honest negative (false +25pp caught + killed)** | ✅ |
| 7 | **FACTHARNESS** | Integrity Office (cross-cutting) | S slice (κ=1 + κ=0.7 + κ=0) | PROMOTED from SOCIUS S-GROUND — F-QUOTE (verbatim) · F-NUMBER (boundary-safe) · F-CITE (κ=0.7 exact-word author) · F-ENTAIL (κ=0 cross-model judge → ABSTAIN); `firewall()` blocks shipping any FABRICATION_FLAG. **Audit caught a HIGH κ=1 Unicode-minus soundness breach → fixed. grounded ≠ true; flag ≠ fraud** | ✅ |
| 8 | **REPRO-ML / BENCHWATCH** | CS_ENG | A | R-REPRO (recompute metric from artifacts) · **R-CONTAM** (13-gram + char-Jaccard + token-set overlap → a contamination RATE + method label) · R-SIGNIF (paired McNemar + bootstrap CI + Bonferroni); "X is best/SOTA" → κ=0 armor. **A benchmark number is NEVER a capability** | ✅ |
| 9 | **REDCELL** | CS_ENG/Security | S (authorization-gated) | `auth_gate.py` (fail-closed, most-audited) → CTF-SOLVE (flag validates) · PATCH-VALIDATE (differential PoC fires-unpatched/fails-patched, sandboxed) · VULN-REPRO (detection signature). **Audit caught a HIGH gate FAIL-OPEN → fixed. Authorized/defensive only; refuse-by-default** | ✅ |

---

## BUILD QUEUE (ordered by value = verifier-sharpness × surface-area)

### 1. ✅ CODEFORGE — code & algorithm discovery  `[dept: CS_ENG · κ: S]`  → **BUILT** 2026-06-20: `weapons/codeforge/`
- **Produces:** synthesized code (SYNTH-VERIFY), superoptimized routines (SUPEROPT), discovered algorithm
  objects (ALGO-DISCOVER: sorting networks, matrix-mult schemes) — all gated by a FROZEN exact verifier.
- **Verifier (κ=1):** four frozen verifiers — SORTNET (**0/1 principle**, exact over all 2ⁿ binary inputs) ·
  MATMUL (**non-commutative symbolic identity**, recursion-safe) · SYNTH-VERIFY (hidden+property+differential,
  UNPREDICTABLE fuzz seed) · SUPEROPT (differential correctness κ=1 + a *measured* benchmark). Self-reports ignored.
- **Built (box-style):** grounded (0/1 principle, Strassen 1969, AlphaTensor — fetched); gate built FIRST with
  passes-good/catches-broken/**rejects-gaming** self-tests green; 3 committed-prediction demos — reproduced the
  **optimal n=8 net (19 comparators)** + **Strassen 7-mult**, discovered valid n6/n7 nets from scratch, an
  O(n²)→O(n) superopt win; **every bluff caught** (an "8-comparator n=5 sorter" is impossible → rejected).
- **The capability A/B RAN → HONEST NEGATIVE:** verifier-gated iterate vs equal-compute best-of-k = **+0pp**
  (feedback not the active ingredient; reproduces the owned v5 lesson in a fresh rich-feedback arena; the
  faithful at-scale test stays infra-gated). **No promotion; the ≥10% capability ratchet stays OPEN at v3.**
- **Independently audited** (Sonnet ≠ Opus generator): **SOUND-WITH-CAVEATS** — math re-derived independently
  (all 40,320 perms; 10,000 numeric + symbolic), **2 false-accept defects caught → fixed + re-gated green**.
  Registered: `Next/BOX_V5.md` (Weapon 6 + router Branch H), `HELMET/registry.json` (CS_ENG), `EVOLUTION_LOG` C40.
- **Honest ceiling:** discovers/optimizes/reproduces within the verifier's reach; reproduction ≠ discovery;
  κ=0 "is this code good/design" → armor; cannot certify properties the tests don't cover.

### 2. ✅ PROOFSMITH — formal proof  `[dept: MATH_TCS (prove-side) · κ: S]`  → **BUILT** 2026-06-20: `weapons/proofsmith/`
- **Produces:** machine-checked formal proofs of theorems/lemmas (formalize-verify / proof-search / lemma-extend).
- **Verifier (κ=1):** the **Lean 4.31.0 kernel + `#print axioms`** wrapped in the **4-check gate** (`proof_gate.py`):
  (1) kernel-accepts the term · (2) no `sorry`/`admit` (sorryAx via `#print axioms` + token scan) · (3) axiom
  allow-list · (4) statement-match (kernel-level `example : <ref> := <thm>`). + a z3 SMT decidable-slice fallback.
  **The cardinal infra fact:** `lean` exits 0 on a `sorry` AND a bogus-axiom proof → the gate parses `#print
  axioms`, never the exit code.
- **Built (box-style):** INFRA grounded + machine-verified (Lean installed, kernel re-checks, sorryAx/axioms
  surface); gate built FIRST + 5 reject self-tests green (accept-good / reject-sorry / reject-bogus-axiom /
  reject-wrong-statement / reject-#eval); FORMALIZE-VERIFY demo **7/7** (3 core-Lean reproductions + 3 attacks
  rejected + z3 cross-check); mathlib demo **3/3** (**infinitude of primes reproduced**, clean axioms, sorry
  rejected). **Capability A/B RAN → CLEAN 0pp NEGATIVE** (kernel-feedback repair == best-of-k; a contaminated
  +25pp from answer-key leakage + orchestrator hints was CAUGHT and killed).
- **Independently audited** (Sonnet ≠ Opus generator, 65 tool calls): **SOUND on proof correctness** — every
  cheat (`@sorryAx`/`opaque`/macro/`native_decide`/transitive-axiom) caught by `#print axioms`; **1 minor
  finding (`#eval` IO side-channel) → fixed + regression self-test**. Registered: `Next/BOX_V5.md` (Weapon +
  router branch), `HELMET/registry.json` (MATH_TCS gains a prove draw), `EVOLUTION_LOG`.
- **Honest ceiling:** **never claim to prove an open problem** — exhibit the kernel-checked term or report none;
  reproduction ≠ discovery; kernel-checked ≠ correct English theorem (autoformalization is κ<1 → cross-model
  review); the de-novo hard-proof leap is rare (same ceiling as the construction engine).

### 3. ✅ OPTIMA — exact optimization / OR  `[dept: CS_ENG/OR · κ: S]`  → **BUILT** 2026-06-20: `weapons/optima/`
- **Produces:** certified-optimal (or proven-bound) solutions to scheduling, routing, packing, allocation.
- **Verifier (κ=1):** **NOT the solver's OPTIMAL status (a self-report) — the independent 4-part certificate**
  (`optima_gate.py`): feasibility re-check (all constraints, no solver) + objective recompute + optimality
  (gap=0 via exhaustive / LP weak-duality / a different exact method) + infeasibility (an IIS the gate confirms).
- **Built (box-style):** infra grounded (OR-Tools CP-SAT 9.15 machine-probed); gate built FIRST + 4 reject
  self-tests green; 4 committed-prediction demos (certified assignment/knapsack/TSP via 3 independent methods;
  **burma14 reproduced = 3323 three ways**; BOUND-PROVE timeout→bound-with-gap; gate-rejects-broken-OPTIMAL).
- **Independently audited** (Sonnet ≠ Opus generator): **SOUND_WITH_CAVEATS** — no false certification; 4
  robustness/honesty defects caught → fixed + re-verified. Registered: `Next/BOX_V5.md` (Weapon 4 + router
  Branch F), `HELMET/registry.json` (CS_ENG_OR), `EVOLUTION_LOG`.
- **Honest ceiling:** certifies optimality FOR THE FORMAL MODEL (modeling is κ<1, cross-model-reviewed);
  flat-space timeout → best-found is a **bound, never "optimal"** (the W2 failure mode); INTEGER-EXACT (float-MILP
  tolerance disclosed, not used here).

### 4. ✅ SYMBOLICA — symbolic-exact numerics  `[dept: NAT_SCI · κ≈0.9]`  → **BUILT** 2026-06-20: `weapons/symbolica/` (promotes registry W7)
- **Produces:** closed-form definite integrals/sums/ODEs, identities, special values, tight bounds.
- **Verifier (NOT one CAS — the AGREEMENT):** `symbolica_gate.py` — ≥2 INDEPENDENT method families agree:
  SYMBOLIC (sympy) vs NUMERIC-AP (mpmath arbitrary precision) vs NUMERIC-DP/SERIES (scipy QUADPACK / series).
  A single-engine answer is a CLAIM; two same-family methods agreeing is a shared-blind-spot RISK → a
  methodologically-different 3rd check on load-bearing cases. Convergence checked BEFORE any closed form;
  branch-cut/domain disagreements caught by full-domain multi-point sampling (NOT skipped — the trap, fixed).
- **Built (box-style):** infra grounded (sympy 1.14/mpmath 1.3/scipy 1.13 machine-probed; sympy heuristic-ness
  FETCHED from docs); gate built FIRST + reject self-tests green (accept-correct / off-by-constant / domain-
  restricted / branch-cut / non-convergent / single-family downgrade); demo 10/10 committed predictions
  (Gaussian √π/2 triple-agreement; Basel ζ(2)=π²/6 reproduced; sin 3x symbolic-collapse; REJECT √π off×2;
  REJECT √(x²)=x global, CERTIFY on x>0).
- **Independently audited** (Sonnet ≠ Opus generator): **SOUND-WITH-CAVEATS** — re-evaluated every result with
  own numeric code; all branch-cut/divergent/near-coincidence attacks correctly handled; 1 defect (SERIES
  single-family verdict overstated ≥2 doctrine) caught → fixed (`CERTIFIED-SINGLE-FAMILY` tier) + re-verified.
  Registered: `WEAPON_REGISTRY.json` W7→VALIDATED, `Next/BOX_V5.md`, `HELMET/registry.json`, `EVOLUTION_LOG`.
- **Honest ceiling:** exact **by agreement**, NOT kernel-proven (PROOFSMITH is); "proven" (symbolic collapse)
  ≠ "verified to D digits"; no closed form → numeric **with explicit error bars**, never a false exact.

### 5. ✅ ECONOMETRIX — quant-finance & causal-econ  `[dept: ECON_FIN · κ: A guarded]`  → **BUILT** 2026-06-20: `weapons/econometrix/`
- **Produces:** stress-tested edge/causal claims (reproduce + break) — **the FIRST guarded-κ weapon.**
- **Verifier (κ≈0.4–0.6, guarded):** **E-BACKTEST** (walk-forward OOS + **Deflated Sharpe Ratio** —
  Bailey & López de Prado 2014 — + net costs + a frozen **look-ahead detector**); **E-CAUSAL** (DiD
  pre-trends / McCrary density / weak-IV first-stage F / Oster δ / E-value); **E-ROBUST + E-REPRO**
  reused from SOCIUS. **In-sample/backtest score is NEVER the verdict (the C14 trap).**
- **Built (box-style):** grounded (DSR/PSR, purged-CV, McCrary, Stock-Yogo, Oster δ, E-value — fetched);
  gate built FIRST with 4 reject self-tests green (genuine-edge PASSES / overfit KILLED DSR≈0 /
  look-ahead CAUGHT / failed-pre-trends + weak-IV FLAGGED); **killer demo on REAL data**: best in-sample
  Sharpe (SPY 1.13) **DIES under walk-forward + DSR net of costs → ABSTAIN 4/4**; a leaky rule's fake
  10.1 Sharpe caught; a confounded DiD (naive +3.76, p≈1e-31) **FLAGGED by the pre-trends placebo**;
  Card-Krueger **+2.76 reproduced**.
- **Independently audited** (Sonnet ≠ Opus generator): **SOUND-WITH-CAVEATS** — math re-derived, walk-forward
  re-run with own split code (ABSTAIN 4/4 confirmed), no κ=0 forecast smuggled in; **6 real-bounded defects
  caught → fixed + locked by regression self-tests** (a leakage blind-spot, a correlated-trials deflation
  hole, Oster/T/R_max guards, a McCrary heteroscedasticity caveat). Registered: `Next/BOX_V5.md` (Weapon 8
  + router Branch J), `HELMET/registry.json` (ECON_FIN), `EVOLUTION_LOG` C42.
- **Honest ceiling:** raises trustworthiness; an in-sample score is not truth; **a backtest is not a
  forecast**; edge that flips OOS → **ABSTAIN**; κ=0 forecast/"should"/market-direction → armor.

### 6. ✅ TRIALGUARD — clinical-trial / biostat rigor  `[dept: STATS/Bio · κ: A with an S slice]`  → **BUILT** 2026-06-20: `weapons/trialguard/`
- **Produces:** reproduce + stress published clinical/epi findings; baseline-anomaly screen; survival
  reproduction (KM + Cox); meta-analysis with publication-bias (I²/Egger/trim-and-fill); E-value sensitivity.
- **Verifier:** mixed — **κ=1 EXACT slice** (GRIM/GRIMMER on trial means **reused** from PSYMETRIX; allocation-
  ratio & percentage→count consistency) **+ the genuinely-new Carlisle baseline-anomaly SCREEN** (κ≈0.9, NOT
  exact: under simple randomization continuous baseline p-values are i.i.d. U(0,1); a Carlisle–Stouffer-Z + KS
  departure is a calibrated anomaly, the RCT analogue of GRIM) + T-SURVIVAL (hand-rolled KM + Cox PH, **cross-
  checked vs statsmodels PHReg to 5 decimals**) + T-META (+trim-and-fill) + T-REPRO/T-MULTIVERSE (**reused** SOCIUS).
- **Built (box-style):** grounded (Carlisle 2017 **+ its critiques** — correlated covariates, stratification,
  categorical-variable unsoundness — all FETCHED; Cox/KM/E-value/trim-and-fill sourced); gate built FIRST with the
  **4 cardinal tests** (clean trial PASSES zero false flags · GRIM-impossible mean CAUGHT · too-similar baseline
  FLAGGED+explained · stratified trial NOT accused) + a no-output-affirms-misconduct scan, all green; killer demo
  on a **controlled ground-truth corpus** (300 randomized + 300 fabricated): Carlisle **~99.7% specificity (1/300
  at α=.001, well-calibrated), 86.7% sensitivity, ZERO of ~600 outputs affirm misconduct**.
- **Independently audited** (Sonnet ≠ Opus generator): EXACT core **sound** (zero false certificates across
  exhaustive sweeps), Carlisle screen **well-calibrated** (4/2000 at α=.001), Cox matches statsmodels to 5
  decimals; **3 meta-layer defects caught → fixed + re-gated** (honesty checker hardened vs word-boundary/clause-
  negation/citation edge cases; Carlisle κ label 1.0→0.9). Registered: `Next/BOX_V5.md` (Weapon 8 + router Branch
  J), `HELMET/registry.json` (STATS), `EVOLUTION_LOG`.
- **Honest ceiling:** **INCONSISTENCY/ANOMALY ≠ FRAUD** (the strictest rail in the arsenal — clinical domain;
  every flag carries benign explanations + false-positive modes, never accuses); Carlisle is a SCREEN not a
  certificate; reproduction ≠ clinical truth; efficacy/approval/causation κ=0 → armor. **A weapon ADDED =
  capability EXPANSION, NOT a ≥10% promotion. The CAPABILITY ratchet stays OPEN at v3.**

### 7. ✅ FACTHARNESS — universal grounding/fabrication facility  `[cross-cutting core facility · κ: S slice]`  → **BUILT** 2026-06-20: `weapons/factharness/` (promoted from SOCIUS S-GROUND)
- **Produces:** a university-wide check every department calls — **is the quote/number/citation actually IN
  the fetched source?** (κ=1 fabrication detector) + a κ=0 entailment judgment (model ≠ generator, else abstain).
- **Built (box-style):** PROMOTED + HARDENED from SOCIUS `S-GROUND` → `factharness.py` (clean `ground()` API)
  + `factharness_router.py` (the shipping **firewall**: FABRICATION_FLAG/CONTRADICTED block; ABSTAIN/
  GROUNDED_BY_JUDGMENT ship only behind an unverified label). Carried the 3 SOCIUS audit fixes + regression
  tests forward. Gate built FIRST + green (**46 assertions**). Killer demo (predictions committed first): 6
  claims vs a REAL fetched Wikipedia source — catches a fabricated quote/number/wrong-author cite, abstains on
  an entailment ambiguity; all predictions matched.
- **Independently audited** (Sonnet ≠ Opus generator, ≈66 tests): **SOUND-WITH-CAVEATS** — κ-separation held
  (κ=0 judge can't launder a failed frozen check); **3 defects caught (D2 HIGH κ=1 Unicode-minus soundness
  breach, D1 bib particle, D3 substring context) → all fixed + locked**. Registered: `Next/BOX_V5.md`
  (Weapon 10), `HELMET/registry.json` (integrity_office core_facility), `EVOLUTION_LOG` C44.
- **Honest ceiling:** a FABRICATION flag = "does not check against the supplied source," **never fraud**;
  grounded ≠ true; entailment is κ=0. Carry-back: D2/D3 exist latently in the SOCIUS seed → flagged for back-patch.

### 8. ✅ REPRO-ML / BENCHWATCH — ML-eval reproducibility  `[dept: CS_ENG · κ: A]`  → **BUILT** 2026-06-20: `weapons/reproml/`
- **Produces:** reproduce a benchmark number; detect train/test **contamination & leakage** (the headline);
  significance of model comparisons.
- **Verifier:** mixed — **R-REPRO** (recompute metric from open artifacts within tol) · **R-CONTAM** ⭐
  (13-gram + char-Jaccard + token-set overlap → a contamination RATE + method label) · **R-SIGNIF** (paired
  McNemar + bootstrap CI + Bonferroni); "X is best/SOTA/capable" → κ=0 armor.
- **Built (box-style):** grounded (GPT-3 13-gram decontam Brown 2020; McNemar/Dietterich 1998; underpowered-NLP
  Card 2020 — fetched); gate built FIRST + green (**20 assertions**); killer demo (predictions first, 11/11) on
  REAL sklearn `digits` — both models REPRODUCE, **contamination rate 0.0→0.5** when 3/6 eval items leaked, real
  gap SIGNIFICANT (p≈4e-60) vs a noise gap NOT, "best" → armor.
- **Independently audited** (Sonnet ≠ Opus generator): **SOUND-WITH-CAVEATS** — math verified correct (McNemar
  bit-for-bit, macro_f1 == sklearn over 200 trials, Type-I 0.016); **5 disclosure/coverage defects (no
  false-verdict risk) → fixed + locked** (undocumented AND-logic, word-reorder evasion, low-n FP, chi2/p +
  tolerance disclosure). Registered: `Next/BOX_V5.md` (Weapon 12 + Branch L), `HELMET/registry.json` (CS_ENG), `EVOLUTION_LOG` C45.
- **Honest ceiling:** reproduction ≠ a SOTA claim; contamination is a measured rate, not "clean" (NO_OVERLAP
  ≠ clean — misses rephrased leakage); flag contamination, don't crown winners.

### 9. ✅ REDCELL — security / exploit PoC  `[dept: CS_ENG/Security · κ: S]`  *(authorization-gated)*  → **BUILT** 2026-06-20: `weapons/redcell/`
- **Produces:** CTF flags / sandboxed proof-of-concept (patch-validation, CVE-repro) — **defensive, authorized only.**
- **Verifier (κ=1):** the **flag validates or it doesn't**; the PoC **fires on the unpatched build and fails on
  the patched build** in a sandbox. But the DOMINANT control is the **authorization gate (`auth_gate.py`), which
  FAILS CLOSED**.
- **Built (box-style):** the security policy in the system guidance IS the spec; gate built FIRST with the
  **refusal self-tests as cardinal as the success tests** + green (**39 assertions**); killer demo (predictions
  first, 8/8, all benign/sandboxed) — toy CTF solve, patch-validate differential, and the gate REFUSING no-auth +
  out-of-scope.
- **Independently red-teamed** (Sonnet ≠ Opus generator, auth gate hardest): **SOUND-WITH-CAVEATS** — **3 defects
  incl. a HIGH gate FAIL-OPEN (D1: `is False` identity check let an absent target key bypass), a category
  alias/type bypass (D2), crash-as-PATCH_VALID (D4) → all fixed + locked; the fail-open closed**. Registered:
  `Next/BOX_V5.md` (Weapon 11 + Branch M), `HELMET/registry.json` (new CS_ENG_SECURITY dept), `EVOLUTION_LOG` C46.
- **⚠ Gate:** authorized/defensive contexts only (CTF, pentest-with-scope, patch validation); refuse-by-default;
  enforces the DECLARED policy (not free-text intent); outputs are fixes + detections, never deployable weapons.

---

## NEW (from the 2026-06-20 gap analysis — `Next/WEAPON_GAP_ANALYSIS.md`)
*The planned arsenal (12 weapons + 8 kit pieces) is BUILT. A grounded 12-domain hunt (web-fetched κ-test → Sonnet
adversarial kill → Sonnet conclusion-audit) found the arsenal near verifier-MECHANISM saturation: 10 of 12
candidate domains FOLD into existing weapons or DECLINE (κ=0). Only ONE genuinely-distinct new κ=1 mechanism
survived all passes.*

### 10. ✅ ENCLOSE — rigorous / validated numerics  `[dept: NAT_SCI (sibling of SYMBOLICA) · κ: S — a containment PROOF]`  → **BUILT 2026-06-20** (`weapons/enclose/`)
- **Produces:** a **guaranteed enclosure `[a,b]`** that *provably contains* the true value of a numeric
  quantity. **v0 surface (built):** verified definite integrals (iv-evaluable integrands), root
  existence/uniqueness in a box (Krawczyk), and containment of a recomputable constant/expression. *(Stiff-ODE
  enclosures, multivariate Krawczyk, singular integrands = future work — conservatively ABSTAINed in v0.)*
- **Verifier (κ=1, a DISTINCT mechanism the arsenal lacks):** **interval arithmetic with outward
  (directed) rounding** — the inclusion property `[f]([x]) ⊇ {f(y):y∈[x]}` — + an **interval-Newton / Krawczyk
  existence-uniqueness gate**. A bogus/too-narrow box fails the containment test or the contraction step →
  REJECT. **This is a containment PROOF, categorically sharper than SYMBOLICA's multi-method AGREEMENT**
  (agreement = corroboration; a shared blind spot fools all engines — exactly the branch-cut bug SYMBOLICA's own
  audit caught). Literature anchors (fetched, `enclose/GROUNDING.md`): Moore/Hickey inclusion theorem,
  Zgliczyński Krawczyk Thm 2 verbatim, Tucker's Lorenz proof, INTLAB.
- **✅ INFRA RESOLVED BY MACHINE (corrects the old guess):** built on **`mpmath.iv` with NO new dependency**.
  Basic iv arithmetic (`+−×÷`, `sqrt/exp/log`, `pi`) IS genuinely outward-rounded (probed). `iv.quad` exists
  but is **broken** (raises) → verified quadrature is built **ON iv arithmetic** (interval rectangle rule). The
  old "`python-flint`/Arb must be installed first" claim was **wrong** — python-flint absent, mpmath.iv suffices.
- **✅ Verify-before-build (the κ=1 anchor) DONE:** `selftest_all.py` green — the gate ACCEPTs true/provable
  enclosures + Krawczyk-unique roots, **REJECTs false (disjoint) boxes + false certs**, ABSTAINs on too-tight +
  malformed; soundness invariant (every ACCEPT brackets an independent 200-dps reference) holds. `demos/`
  prediction-committed (9/9, incl. an honest miss). **Cross-model Sonnet audit: SOUND** (no false-accept across
  17 attack categories; 4 hardening findings fixed + frozen). `AUDIT.md`.
- **Honest ceiling:** κ=1 holds **under directed rounding** — and because mpmath.iv rounds in **SOFTWARE**, the
  `-ffast-math` hardware-float caveat does NOT apply (deterministic rounding; the residual is mpmath.iv's own
  rounding correctness, not formally verified). The rectangle rule is rigorous but **LOOSE** (ABSTAINs on a true
  claim tighter than its enclosure). **COMPLEMENTARY to SYMBOLICA, NOT a replacement** (SYMBOLICA
  keeps symbolic/algebraic work; ENCLOSE adds certified numeric BOUNDS). Surface = **moderate, not broad**.
  Certifies the COMPUTED enclosure, not the modeling step. A weapon ADDED = capability EXPANSION, NOT a ≥10%
  promotion; ratchet stays OPEN at v3.

### 11. 🔭 ON WATCH — survived with hard fences (do NOT build before the fence/precondition spec)
- **BIOVERIFY** (bioinformatics) — build ONLY scoped to **alignment-DP + HMM-DP recompute**; the other 3
  sub-domains (phylo-likelihood, MolProbity clashscore, variant concordance) are NOT bit-reproducible → κ-guarded.
  New *surface* on the owned CODEFORGE M3 mechanism, not a new mechanism.
- **GAMETHEORY** (equilibrium / stable-matching / fairness object-property checks) — survives only with **hard
  API fencing vs OPTIMA** (correlated-eq is an LP feasibility check = OPTIMA machinery) + **enforced
  exact-rational profiles** (float Nash degrades it to approximate). Write the fence spec first.
- **NUMERICAL_PDE** (MMS convergence-order gate) — corrected to **κ-GUARDED, ECONOMETRIX-class, NOT sharp**;
  build only with a min-grid-count + asymptotic-range precondition, logic-errors scoped out as κ=0 armor, and
  *calling* SYMBOLICA for source-term derivation. Lower priority than ENCLOSE.
- **The bigger move is HARDENING, not expansion:** *run* CRUCIBLE against the existing gates (every "κ=1" label
  is asserted, not yet adversarially proven — build-time audits already found HIGH-severity gate defects in ~6
  of the 12 weapons). See `Next/WEAPON_GAP_ANALYSIS.md` §priority.

---

## NOT WEAPONS — armor only (κ=0; here so we don't accidentally build theater)
🚫 Law · ethics · policy · history/literary interpretation · strategy · design taste · unresolved forecasting.
**No exact verifier exists → ground + honest ABSTENTION, never a weapon.** The HELMET's job here is to *resist*
manufacturing certainty (already red-team-confirmed: the free-will bait abstained correctly).

---

## How we work this list (box discipline, per weapon)
1. **PLAN** — write a `<weapon>/SPEC.md` + commit predictions BEFORE building (like the existing kickoffs).
2. **GROUND** — fetch-confirm the "verify-before-build" anchor; don't assert it.
3. **BUILD** — the frozen verifier first (gate: "a verifier that can't fail is not a verifier" — must pass a
   good input AND catch a broken one AND abstain on malformed); then the weapon that feeds it.
4. **VERIFY INDEPENDENTLY** — a cross-model audit (Sonnet/Haiku ≠ the Opus generator; never Opus-audits-Opus).
5. **REGISTER** — add to `Next/BOX_V5.md` (new Weapon + router branch) + `HELMET/registry.json` (its department)
   + an honest `EVOLUTION_LOG` entry: **a weapon ADDED = capability EXPANSION, NOT a ≥10% promotion.**

**Recommended order:** 1 → 2 → 3 (the three Tier-S prizes) first, then the Tier-A reproduce-and-stress weapons.
