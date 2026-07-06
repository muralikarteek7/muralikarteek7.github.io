# KICKOFF PROMPT — build the Quantitative-Psychology weapon (PSYMETRIX) for the v5 box
*Paste everything below the line into a FRESH chat opened in `/Users/varunesh/Desktop/AI_agents`. Self-contained.
Written 2026-06-12, mirroring the SOCIUS (sociology) weapon — but quant-psych is HIGHER-κ, so this weapon has a
larger executable core and one genuinely sharp exact sub-weapon (statistical forensics).*

---

You are extending the **v5 "ARMOR + WEAPONS" box** with a **new weapon for quantitative psychology** (psychometrics
+ quantitative methods). Work it BOX-style (plan → produce → verify INDEPENDENTLY with a different model or a
machine check → ground load-bearing facts → be honest; no win without proof). Calibrate cost to stakes.

## 0. ORIENT — read first
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (Armor+Weapons + the when/where router this plugs into),
`Expanding_Frontiers/THEORY.md` (the κ state-vector), `Expanding_Frontiers/weapons/SOCIOLOGY_WEAPON_KICKOFF.md`
(the sibling weapon — same pattern, lower κ), and skim `Expanding_Frontiers/cap_set/capset_verify.py` (the *shape*
of a frozen verifier). You are adding a registered weapon, chosen by the router.

## 1. THE HONEST FRAMING — κ-profile DEFINES the weapon (do not skip)
Quantitative psychology is **MEDIUM-to-HIGH κ** — much of it is genuinely machine-checkable, more than sociology.
So **PSYMETRIX** is a **κ-aware Psychometric & Statistical Rigor Engine** with a **large executable core** and a
**sharp exact offensive piece**:
- **HIGH κ (exact, non-gameable — the sharp end):** *statistical forensics* — GRIM/GRIMMER, SPRITE, TIVA, p-curve,
  Benford — can **mathematically PROVE that reported summary statistics are impossible** for the stated N and
  scale (e.g. a mean of N integer Likert responses is consistent with only certain values). This is the social
  sciences' closest analogue to the cap-set verifier: an exact certificate, not a judgment.
- **MEDIUM κ (executable):** psychometric model fit (IRT 1/2/3PL & GRM, EFA→CFA, SEM), reliability (α/ω/ICC),
  measurement invariance & DIF, reproduction, specification-curve/multiverse, power, meta-analysis + pub-bias.
- **LOW κ (armor only):** what a construct *means*, theory choice, construct-validity *interpretation* → ground or
  abstain; never present as machine-verified.

**The weapon's offense:** it *produces* exact certificates where they exist (impossibility proofs, fitted/compared
measurement models, optimal test designs) and raises trustworthiness everywhere else. **Its ceiling (state it
every time):** it certifies *consistency / fit / robustness*, not *truth* — a model that fits is not "the right
theory," and **a statistical inconsistency is NOT proof of fraud** (see honesty rails).

## 2. AIMS
1. **Forensics:** given a paper's reported stats (means/SDs/Ns, test statistics, last-digit patterns), run
   GRIM/SPRITE/TIVA/p-curve/Benford and **certify which reported numbers are mathematically (im)possible / which
   bodies of results lack evidential value.** Exact where the math is exact.
2. **Psychometric model engine:** fit & compare IRT/CFA/SEM models to item-level data; report fit (CFI/RMSEA/SRMR/
   information criteria), dimensionality, local dependence, and whether a claimed scale structure holds.
3. **Invariance / DIF:** test measurement invariance (configural→metric→scalar) and item-level DIF across groups —
   so a "group difference in the construct" isn't a measurement artifact.
4. **Reliability & attenuation:** α/ω/ICC, reliability of *change/difference* scores, disattenuated correlations.
5. **Reproduce + stress:** reproduce a published quantitative effect from open data; specification-curve/multiverse;
   p-curve for evidential value.
6. **Power & design (constructive):** a-priori/sequential power; **optimal item selection** (maximize the test
   information function — a real constructive optimization with an exact objective); optional-stopping correction.
7. **Meta-analysis:** pooled effect + publication-bias correction (PET-PEESE, selection models, p-curve).
8. **Route by problem:** given a quant-psych task, choose which sub-weapons apply; κ=0 residue → armor.

## 3. WEAPON DESIGN — the sub-weapon registry (build the frozen verifier for each κ>0 piece FIRST)
| sub-weapon | fires when | κ | frozen verifier (build + adversarially self-test) |
|---|---|---|---|
| **P-FORENSICS** ⭐ | reported summary stats on bounded/integer scales | **1 (EXACT)** | GRIM/GRIMMER mean–SD–N consistency · SPRITE raw-data reconstruction · TIVA · p-curve · Benford. **Certifies impossibility, exactly.** |
| **P-MODEL** | latent construct / scale / test, item-level data | 1 | fit & compare IRT (1/2/3PL, GRM) / EFA→CFA / SEM; fit indices, dimensionality, local dependence |
| **P-INVARIANCE/DIF** | scores compared across groups | 1 | invariance (configural/metric/scalar) + DIF (Mantel–Haenszel, IRT-LR, logistic) |
| **P-RELIABILITY** | a scale/difference score is used | 1 | α / ω / ICC / SEM-reliability; reliability of change scores; disattenuation |
| **P-REPRO + P-MULTIVERSE** | a published effect with open data | 1 | reproduce the statistic; specification-curve; p-curve evidential value |
| **P-POWER/DESIGN** | designing/evaluating a study | 1 | a-priori & sequential power; optional-stopping correction; **optimal item selection (max test information)** |
| **P-META** | a body of findings | 1 | meta-analysis + pub-bias correction (PET-PEESE, selection models) |
| **P-GROUND** | interpretive/theoretical claims | armor | fetch real source + entailment, else ABSTAIN |

**Routing:** classify the task's claims (forensic / measurement / invariance / reliability / effect / design /
meta / interpretive) → draw the matching sub-weapons → κ=0 residue → armor.

## 4. TO-DOs / STEPS (box order)
1. **PLAN + GROUND (don't assert):** fetch & confirm the *current* method specs — GRIM/GRIMMER (Brown & Heathers),
   SPRITE (Heathers et al.), p-curve (Simonsohn et al.), TIVA, measurement invariance / DIF, IRT/SEM packages
   (`girth`/`py-irt`, `factor_analyzer`, `semopy`, `pingouin`, `statsmodels`, `metafor`-equivalents), and the
   psychology replication evidence (Open Science Collaboration 2015; Many Labs). Pick the **killer demo** (below).
   Write a 1-page PSYMETRIX spec.
2. **BUILD THE FROZEN VERIFIERS FIRST** (before any analysis). Start with **P-FORENSICS** — it's exact, cheap, and
   the sharpest. **Adversarially self-test every verifier:** feed a known-consistent stat (must pass) AND a
   known-impossible one (a mean GRIM-inconsistent with its N — must FAIL); a non-invariant scale (DIF must fire);
   a p-hacked set (p-curve must flag). A verifier that can't fail is not a verifier.
3. **COMMIT PREDICTIONS, then RUN PSYMETRIX on the demo end-to-end** — every certificate gate-verified; every prose
   claim grounded or abstained.
4. **VERIFY INDEPENDENTLY (cross-model ≠ generator; Fable inactive → Sonnet/Haiku, never Opus-audits-Opus):** a
   different model re-runs the verifiers from scratch and re-derives the forensic certificates independently. Fix
   what it catches before writing anything down.
5. **REGISTER + ROUTE:** add PSYMETRIX to `Next/BOX_V5.md`'s registry + router (positive trigger: "quant-psych /
   psychometric task with data or reported stats" → PSYMETRIX; κ=0 pure theory → armor). Honest EVOLUTION_LOG entry.
6. **HONEST WRITEUP:** what was certified exactly, what was only grounded/abstained, the ceiling, and (for any
   forensic finding) the inconsistency-not-fraud caveat.

## 5. THE "KILLER DEMO" (commit a prediction before running)
Best demo = the sharp one: **run P-FORENSICS on a real set of published reported statistics** (e.g. a corpus of
open psychology papers' tables, or a single paper with full descriptive tables) and **certify which reported
numbers are GRIM/SPRITE-impossible** — an exact, non-bluffable result, the quant-psych analogue of a verified
cap. Pair it with one **reproduce + multiverse** on an open dataset (e.g. a Many-Labs or OSF replication package).
Predict in writing: how many GRIM-inconsistencies? does the chosen effect reproduce? survive the multiverse? Then
run and compare; report falsifications plainly.

## 6. HONESTY RAILS (non-waivable, specific to this weapon)
- **INCONSISTENCY ≠ FRAUD (the load-bearing one).** GRIM/SPRITE flag *mathematical inconsistency*, which can be
  rounding, typos, or reporting error. **Never accuse; report "reported statistics are inconsistent with the stated
  N/scale" with the exact arithmetic, and stop there.** Real reputations are at stake.
- **Fit ≠ truth; consistent ≠ correct; robust ≠ true.** A model that fits / a stat that's GRIM-consistent / an
  effect that survives the multiverse is *not* validated as true — say what was and wasn't certified.
- **κ-honesty:** label each output piece by κ; never present a κ=0 judgment as machine-verified.
- **No fabricated stats/citations** — every datum and source real, fetched, entailment-checked.
- **Abstain** where neither a check nor grounding exists; abstention is a scored deliverable.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/psymetrix/` — `SPEC.md`, the frozen verifiers (`*_verify.py`; lead with
`forensics_verify.py`), the demo run (`demo_<...>/` with data ref, committed prediction, certified results),
`AUDIT.md` (cross-model red-team), `README.md` (what PSYMETRIX is + its honest ceiling + the inconsistency≠fraud
rule). Registry/router update in `Next/BOX_V5.md`; honest `EVOLUTION_LOG` entry (a weapon ADDED = capability
expansion, NOT a ≥10% promotion).

## 8. STAFF THE TEAM (v4 ladder; Fable 5 INACTIVE → its slots on Opus, flag low confidence)
- **Survey/ground** (cheap): confirm method specs + the demo dataset/corpus. Don't assert.
- **Build** (code tier): the frozen verifiers + demo pipeline — EXECUTE; the machine decides.
- **Audit** (model ≠ generator — Sonnet/Haiku): try to GAME each verifier (esp. forensics — can a consistent stat
  be wrongly flagged, or an impossible one slip through?) and red-team the conclusions.
- Orchestrator (Opus) plans, routes, synthesizes, holds the honesty veto.

## 9. THE ONE-LINE TEST OF SUCCESS
**"Given a quant-psych task, PSYMETRIX chooses the right checks, produces EXACT certificates where the math is
exact (forensics, fit, optimal design), grounds-or-abstains elsewhere, a different model independently confirms
every certificate, and any inconsistency is reported as inconsistency — never as an accusation."** That is a real,
sharp, honest weapon for the field with the largest checkable core in the social sciences.
