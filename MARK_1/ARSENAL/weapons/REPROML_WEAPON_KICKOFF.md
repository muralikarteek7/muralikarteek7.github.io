# KICKOFF — build WEAPON #8: REPRO-ML / BENCHWATCH (ML-eval reproducibility) for the v5 box
*Paste into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written 2026-06-20. REPRO-ML is
item #8 of `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` — a mixed-κ weapon for ML evaluation rigor. It has a
useful self-referential payoff: it hardens the box's OWN benchmark hygiene (the v5 contamination concern).*

---

You are building **REPRO-ML** (a.k.a. BENCHWATCH), a **κ-aware ML-evaluation rigor weapon** for the **CS & Eng**
department. Given an ML result/claim, it routes the **κ>0 pieces** (re-run the eval; detect train/test
contamination & leakage; test the significance of a model comparison) to frozen verifiers, and the **κ=0 pieces**
("model X is better / SOTA / more capable") to **armor (ground + abstain)**. Work BOX-style: plan → produce →
**verify INDEPENDENTLY** → ground → be honest; **no win without proof; a benchmark number is not a capability.**

## 0. ORIENT — read first
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (κ-router; NEGATIVE-list (4) gameable proxies). Read the box's own
contamination work — **`Next/benchmarks/V5_INFRA_UNLOCK_SPEC.md`** (the contamination-free hidden-test demand)
and `Next/benchmarks/V5_INTERIM_VERDICT_2026-06-12.md` — because REPRO-ML's contamination detector is exactly
what that gate needs. Clone the SOCIUS shape (`socius/repro_verify.py` for reproduction) and the CODEFORGE
contamination thinking (`Expanding_Frontiers/weapons/CODEFORGE_WEAPON_KICKOFF.md`). Then `WEAPONS_BACKLOG.md`
(item #8).

## 1. THE HONEST FRAMING — what REPRO-ML IS and IS NOT
**IS:** a **mixed, guarded-κ trustworthiness weapon.** Some ML-eval claims are checkable: re-running an open eval
harness is exact; train/test **contamination** (n-gram/embedding overlap) is measurable; the **statistical
significance** of model A vs B on a finite test set is computable. REPRO-ML stress-tests an eval claim: does the
number **reproduce**, is it **contaminated**, is the A>B gap **significant**?

**IS NOT:**
- **NOT a SOTA-crowner.** "Model X is the best / most capable" is **κ=0** — a benchmark number ≠ capability
  (Goodhart; contamination; metric cherry-picking). → armor + abstain. REPRO-ML reports reproduction +
  contamination + significance, never "X is best."
- **NOT contamination-blind.** The dominant ML-eval failure is the model having SEEN the test set. A reproduced
  number on a **contaminated** benchmark proves nothing — REPRO-ML must measure overlap and flag it.
- **NOT a significance-free leaderboard.** A 0.3-point gap on a 500-item test set is usually noise → paired
  significance testing required; report CIs, not point ranks.
- **NOT smarter than the model** — organized eval rigor, not capability.

## 2. THE SUB-WEAPONS (mixed-κ)
| sub-weapon | κ | what it checks | verifier |
|---|---|---|---|
| **R-REPRO** | ≈0.7 | does the reported metric reproduce from the open harness/data? | re-run the eval; recompute the metric within tolerance (reuse `socius/repro_verify.py` shape) |
| **R-CONTAM** ⭐ | ≈0.8 | did the eval set leak into training? | **n-gram overlap (e.g. 13-gram, à la GPT-3/Brown 2020 decontam) + embedding near-duplicate detection** between train corpus (or the model's outputs) and the eval set; report contamination rate |
| **R-SIGNIF** | ≈0.9 | is the A>B gap real, not noise? | **paired bootstrap / McNemar / permutation test + CIs**; multiple-comparison correction across many models |
| **κ=0 residue** | 0 | "X is best / SOTA / more capable / production-ready" | **ARMOR** — ground or abstain; benchmark ≠ capability |

**The genuinely NEW pieces are R-CONTAM + R-SIGNIF**; R-REPRO reuses the SOCIUS reproduction shape.

## 3. THE KEY ENGINEERING PROBLEM — measure contamination + significance honestly
1. **Contamination = overlap, reported as a rate with a method label** (n-gram order, dedup threshold). Don't
   claim "clean" — claim "X% n-gram overlap at 13-gram; Y near-duplicates." Absence of detected overlap ≠ proof
   of no contamination (state it).
2. **Significance = paired test + CI**, never a bare point gap; correct for multiple models compared.
3. **Reproduction = re-run, not re-quote** — recompute the metric from predictions; a metric you can't recompute
   from open artifacts is unverified.

**Gate self-tests (non-waivable):** (a) PASS a faithfully-reproduced clean eval, (b) **CATCH a contaminated eval**
(inject test items into the "train" set → R-CONTAM flags it), (c) **CALL a noise-level gap insignificant**
(tiny gap on small N → not significant), (d) **flag an unreproducible metric** (predictions don't recompute).

## 4. TO-DOs (box order)
1. **PLAN:** `weapons/reproml/SPEC.md` — the 4 sub-weapons + κ table, the contamination-method labeling rule, the
   benchmark≠capability rail, the router (`reproml_router.py`: reported metric + artifacts → R-REPRO; train+eval
   sets → R-CONTAM; model comparison → R-SIGNIF; "is X best/capable" → κ=0 armor). **GROUND by FETCH:** n-gram
   decontamination practice (Brown et al. 2020 GPT-3 13-gram; later data-contamination literature); paired
   bootstrap / McNemar significance for classifiers; embedding near-dup detection. `GROUNDING.md`.
2. **BUILD THE VERIFIERS FIRST:** `contam_verify.py` (n-gram + embedding overlap), `signif_verify.py` (paired
   tests + CIs), reuse repro. `selftest_all.py` (the 4 tests). **Gate green.**
3. **BUILD router/loop** (clone SOCIUS): route → κ>0 verifiers → κ=0 armor → label κ. Execute, never vote.
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` first): (i) reproduce a small open
   benchmark number; (ii) **the contamination demo** — inject eval items into a "train" set and show R-CONTAM
   catches the overlap (the headline); (iii) **R-SIGNIF** — show a small leaderboard gap is NOT significant.
5. **VERIFY INDEPENDENTLY:** cross-model audit (Sonnet/Haiku ≠ generator; never Opus-audits-Opus) — re-runs the
   contamination scan with its own n-gram code, checks the significance math, ensures no κ=0 "best" claim leaked.
6. **REGISTER:** add **REPRO-ML** to `Next/BOX_V5.md` (new Weapon + router branch) + `HELMET/registry.json`
   (CS_ENG eval facility `draws`). Honest `EVOLUTION_LOG`: a weapon ADDED = capability EXPANSION, NOT a ≥10%
   promotion. **Bonus:** note it can harden the box's own hidden-test hygiene (V5 infra gate). Update
   `WEAPONS_BACKLOG.md` STATUS ✅.

## 5. HONESTY RAILS (non-waivable)
- **Benchmark ≠ capability** — never crown a SOTA/best/most-capable; that's κ=0 → armor.
- **Contamination reported as a measured rate + method label** — "no overlap detected" ≠ "clean."
- **Significance with CIs + multiple-comparison correction** — no bare point-rank leaderboards.
- **Reproduction = recompute from artifacts**, not re-quote.
- **The gate that can't fail is not a gate.**

## 6. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/reproml/` — `SPEC.md`, `GROUNDING.md`, `contam_verify.py` + `signif_verify.py`
(+ imported repro) + `selftest_all.py`, `reproml_router.py`, `demo_*/`, `AUDIT.md`, `README.md` (ceiling:
reproduction + contamination + significance, never a capability/SOTA claim). Registration in `Next/BOX_V5.md` +
`HELMET/registry.json` + honest `EVOLUTION_LOG`; `WEAPONS_BACKLOG.md` STATUS ✅.

## 7. STAFF (v4 ladder; Fable INACTIVE → Opus, flag low confidence)
- **Eval engineer** = code tier (the scans/tests are pure machine). **Library** = cheap model (n-gram-decontam +
  significance sources). **Auditor** = Sonnet/Haiku ≠ generator — re-runs contamination + significance, polices
  the benchmark≠capability rail.

## 8. SUCCESS (one line)
**"REPRO-ML reproduces an ML metric from open artifacts, measures train/test contamination as a method-labeled
rate, tests model-comparison significance with CIs + multiple-comparison correction, makes the contamination
catch its headline, and routes 'X is best/most-capable' to armor — a benchmark number is never a capability."**
