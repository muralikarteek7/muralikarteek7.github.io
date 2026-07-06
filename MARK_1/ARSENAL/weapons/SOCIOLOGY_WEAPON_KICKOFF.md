# KICKOFF PROMPT — build the Sociology weapon (SOCIUS) for the v5 box
*Paste everything below the line into a FRESH chat opened in `/Users/varunesh/Desktop/AI_agents`. It is
self-contained: it tells that session what to read, the honest framing, the aims, the to-dos, the steps, and
how to implement + validate + register the weapon. Written 2026-06-12 by the v5 session that built the
Frontier Construction Engine.*

---

You are extending the **v5 "ARMOR + WEAPONS" box** with a **new weapon for a new problem class: social-science /
sociology research.** Work it BOX-style (plan → produce → verify INDEPENDENTLY with a different model or a machine
check → ground load-bearing facts → be honest; never claim a win without proof). Calibrate cost to stakes.

## 0. ORIENT — read before doing anything
- `CLAUDE.md` (the always-on box), `RESUME.md`, **`Next/BOX_V5.md`** (Armor+Weapons + the WHEN/WHERE router —
  this is the framework your weapon plugs into), `Expanding_Frontiers/THEORY.md` (the κ state-vector + weapon map),
  `Expanding_Frontiers/ALGORITHM_AND_WEAPONS.md` (the attack loop), and skim `Expanding_Frontiers/cap_set/capset_verify.py`
  (the *shape* of a frozen verifier you will imitate). You are adding a registered weapon, chosen by the router.

## 1. THE HONEST FRAMING — this DEFINES the weapon (do not skip)
**Sociology is a LOW-κ field.** Most of its claims (theory, interpretation, meaning, normative analysis) have **no
cheap, exact, non-gameable verifier**. By the v5 κ-gate, those pieces are **κ=0 → ARMOR ONLY** (ground every claim
in a real source; cross-model panel; abstain on overreach). **Therefore this weapon is NOT a construction engine —
there are no machine-checkable "records" to break.** It is a **κ-AWARE EMPIRICAL RIGOR ENGINE (codename SOCIUS):**
it decomposes a research task by checkability, routes the **κ=1 executable pieces** (reproduce a statistic, stress
it, check a measure, check a causal assumption) to **frozen verifiers**, and the **κ=0 judgment pieces** to
**armor**. Its "offense" is **trustworthiness**: making findings reproducible, robust, validly measured, and
honestly grounded — and catching the field's characteristic failure modes. **Its ceiling (state it in every
output): it raises V·G (verification·grounding); it does NOT manufacture truth where no ground truth exists.**
A reproduction is a reproduction; a non-robust finding flagged is not a "discovery."

## 2. AIMS (what the weapon must do)
1. **Reproduce** a published quantitative social-science finding from its open data + code, exactly (within tol).
2. **Stress it** — run a specification-curve / multiverse analysis; report whether the finding survives reasonable
   analytic choices, or is an artifact of one path (the field's biggest real failure mode).
3. **Audit measurement** — reliability (Cronbach's α / McDonald's ω / ICC; inter-coder κ for qualitative coding),
   validity, and **measurement invariance** across the groups being compared (so a "group difference" isn't a
   measurement artifact).
4. **Audit causal claims** — build the DAG / identification argument; check overlap & balance; run sensitivity
   analysis (E-values, Rosenbaum bounds), placebo / negative-control tests; flag claims that don't survive.
5. **Audit sampling / generalizability** — representativeness, weighting, target-vs-inference population gap;
   flag over-generalization beyond the sampled population.
6. **Ground the qualitative / interpretive layer** — every empirical assertion → a fetched real source (entailment
   checked) or a re-run; **abstain** on claims neither grounded nor checkable; surface reflexivity/positionality.
7. **Be a chooser** — produce a **router** so that, given a sociology task, the box decides which sub-weapon(s)
   apply (e.g. "this is a causal claim from observational survey data" → measurement + causal + sampling audits).

## 3. THE WEAPON DESIGN — a κ-router for social-science tasks
Build SOCIUS as a small registry of **sub-weapons**, each with a **frozen, executable verifier** where κ>0, and an
**armor fallback** where κ=0. Suggested sub-weapons (the new chat refines after grounding):

| sub-weapon | fires when | κ | verifier (build it FIRST, frozen) |
|---|---|---|---|
| **S-REPRO** | a published quantitative finding has open data+code | 1 | re-run pipeline → reproduces the reported statistic within tolerance (exact-ish machine check) |
| **S-MULTIVERSE** | a finding rests on defensible-but-arbitrary analytic choices | 1 | specification-curve over the choice grid → report effect distribution + share significant/sign-stable |
| **S-MEASURE** | constructs are latent (scales, indices, coded categories) | 1 | reliability + CFA fit + **measurement-invariance** tests across compared groups; inter-coder κ |
| **S-CAUSAL** | the claim is causal from observational data | 0.5 | DAG + identification check; overlap/balance; **E-value / Rosenbaum** sensitivity; placebo & negative-control |
| **S-SAMPLE** | inference generalizes beyond the sample | 0.5 | weighting/representativeness check; target-vs-inference population diff; flag extrapolation |
| **S-GROUND** | any empirical assertion in prose | armor | fetch real source + NLI entailment of the claim against it; else ABSTAIN |
| **S-ABM** (optional) | the theory predicts emergent macro patterns | 1 | agent-based / network simulation whose output is checked against the theory's stated prediction |

**Routing:** read the task → classify its claims (descriptive / measurement / causal / interpretive / predictive)
→ draw the sub-weapons whose preconditions hold → κ=0 residue goes to armor (panel + abstention). This *is* the
"choose the weapon by the problem" capability the PI asked for.

## 4. TO-DOs / STEPS (box order — do them in this sequence)
1. **PLAN + GROUND (don't assert):** fetch the *current* SOTA for each method above (specification curve =
   Simonsohn/Simmons/Nelson; multiverse = Steegen et al.; E-values = VanderWeele/Ding; measurement invariance =
   the alignment / `semTools`/`lavaan` literature; replication-crisis evidence = the social-science replication
   projects). Confirm names/APIs are real and current — do NOT trust memory. Write a one-page SOCIUS spec.
2. **BUILD THE FROZEN VERIFIERS FIRST** (before any "analysis"): one runnable, independent checker per κ>0
   sub-weapon (Python: `statsmodels`/`scipy`/`pandas`/`linearmodels`/`lavaan`-via-`semopy`/`networkx`/`mesa`).
   **Adversarially self-test each:** feed a known-good result (must pass) AND a known-broken one — a p-hacked
   spec, a non-invariant scale, a finding that dies under the multiverse (must FAIL). A verifier that can't fail is
   not a verifier (the "weak-weapon-cap" lesson).
3. **PICK A KILLER DEMO (real, open, contamination-aware):** choose ONE published finding with **openly available
   data + code** (e.g. from the GSS, a replication-archive dataset, or a journal's reproducibility package).
   Prefer a finding old enough to have a known robustness verdict so you can validate SOCIUS against ground truth.
4. **RUN SOCIUS on the demo end-to-end:** reproduce → multiverse → measurement → causal → sampling → ground the
   write-up. Every number gate-certified by its frozen verifier; every prose claim grounded or abstained.
5. **VERIFY INDEPENDENTLY (cross-model, ≠ the generator):** a different model re-runs the verifiers from scratch
   and red-teams the conclusions (with Fable 5 inactive, use Sonnet/Haiku — never Opus-audits-Opus). Fix what it
   catches before writing anything down.
6. **REGISTER + ROUTE:** add SOCIUS to the weapon registry and to BOX_V5's router (a new positive-trigger row:
   "empirical social-science task with data" → SOCIUS; and an explicit κ=0 note: pure theory/interpretation →
   armor only). Update RATCHET/RESUME/EVOLUTION_LOG pointers honestly.
7. **HONEST WRITEUP:** what SOCIUS verified, what it could only ground/abstain on, and its ceiling.

## 5. THE "KILLER DEMO" CONTRACT (commit before running)
Pick the finding and **predict, in writing, before you run:** will it reproduce? will it survive the multiverse?
is the key measure invariant? does the causal claim survive sensitivity analysis? Then run and compare. Report the
falsifications plainly (you WILL get some predictions wrong — that's the method working).

## 6. HONESTY RAILS (non-waivable, specific to this weapon)
- **κ-honesty:** label every output's pieces by κ. Never present a κ=0 judgment as if machine-verified.
- **Reproduction ≠ discovery; robust ≠ true.** A finding that survives the multiverse is *robust to analytic
  choice*, not *true* — it can still be confounded, non-generalizable, or measuring the wrong thing. Say so.
- **Never launder a non-robust finding as robust** to please anyone. Report negatives (findings that die under
  stress) as the primary, valuable output.
- **No fabricated citations/data** — every source fetched and entailment-checked; every dataset real and cited.
  (AI-fabricated citations are a documented failure mode — verify all three: paper exists, authors match, claim
  matches.)
- **Abstain** on anything neither grounded nor checkable. Abstention is a scored deliverable, not a failure.
- **This weapon does not "do sociology" for anyone** — it is an instrument that makes a human's social-science
  work more reproducible and honest. State that.

## 7. DELIVERABLES + WHERE
- `Expanding_Frontiers/weapons/socius/` — `SPEC.md`, the frozen verifiers (`*_verify.py`), the demo run
  (`demo_<finding>/` with data ref, code, the committed prediction, the certified results), `AUDIT.md`
  (the cross-model red-team), `README.md` (what SOCIUS is + its honest ceiling).
- Registry + router updates in `Next/BOX_V5.md` (a new weapon row + when/where), and an `EVOLUTION_LOG` entry
  honestly framed (a new weapon ADDED — capability expansion, NOT a ≥10% promotion).

## 8. STAFF THE TEAM (v4 model ladder; Fable 5 currently INACTIVE → its slots run on Opus, flag low confidence)
- **Survey/ground** (cheap model): fetch+confirm the method SOTA and the demo dataset. Don't assert.
- **Build** (code tier, Sonnet/Haiku): the frozen verifiers + the demo pipeline — EXECUTE, the machine decides.
- **Audit** (a model ≠ the generator — Sonnet/Haiku, never Opus-audits-Opus while Fable is down): red-team the
  verifiers (can they be gamed?) and the demo conclusions.
- Orchestrator (Opus) plans, routes, synthesizes, and holds the honesty veto.

## 9. THE ONE-LINE TEST OF SUCCESS
Not "SOCIUS produced a sociological breakthrough" (it can't — low-κ). Success = **"given a social-science task,
SOCIUS correctly chooses which checks apply, runs the κ>0 ones to a frozen verifier, grounds or abstains on the
κ=0 ones, and a different model confirms the verdict — including the findings that DIED under stress."** That is a
real, honest weapon for a field where the enemy is not an unbroken record but un-reproducible, over-claimed work.
