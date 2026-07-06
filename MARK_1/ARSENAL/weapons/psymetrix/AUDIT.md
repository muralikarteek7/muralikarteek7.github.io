# PSYMETRIX — independent cross-model audit (2026-06-20)

**Auditor:** a DIFFERENT model from the generator (Claude Sonnet, spawned via the Agent tool).
Fable 5 is inactive, so the auditor is Sonnet — **never Opus-audits-Opus** (C8 independence).
**Mandate:** re-run from scratch, independently re-derive every forensic certificate, and try to GAME
the verifiers — especially to find a FALSE POSITIVE (a clean stat wrongly flagged = a false accusation).

## What the auditor did
1. **Re-ran** `selftest_all.py` and `demo_forensics/run_demo.py` — both reproduced identically
   (deterministic LCG). Gate OK; demo all-PASS.
2. **Independently re-derived** the certificates with its OWN arithmetic (not the repo's code):
   - GRIM 5.27/43 → interval [227,226] empty → IMPOSSIBLE; 226/43=5.2558→5.26, 227/43=5.2791→5.28. ✓ agrees.
   - GRIM 5.26/43 → consistent; 5.90/40/3items → consistent (powerless). ✓
   - GRIMMER 3.44/2.47/18 → T=62 (even), only SS=317 reproduces SD 2.47, 317 is odd → **parity mismatch →
     INCONSISTENT via parity** (not via empty SD band). ✓ agrees with our verifier exactly.
   - TIVA z-values agree with scipy to <3.2e-9; one-tailed p→z and lower-tail χ² confirmed.
   - p-curve pp=p/.05, Stouffer, p<.05-only inclusion confirmed against scipy.
   - disattenuation r>1 correctly flagged as exact impossibility.

## Findings
### Soundness — VERIFIED SOUND (the load-bearing result)
**Zero false positives** across the auditor's own sweeps: all valid integer sums for n∈[2,100] on a 1–7
scale (1dp & 2dp); 2,000 random real integer samples through GRIMMER; the 200 clean demo rows. The
`Fraction(str(mean))` exact arithmetic is the correct choice and eliminates float-rounding false positives.
The EXACT forensic core does not flag an achievable statistic as impossible.

### Robustness — 4 bugs found, ALL FIXED
| id | bug | fix |
|---|---|---|
| R1 | `grim(..., n=0)` → ZeroDivisionError | guard: n≤0 or items≤0 → `consistent=None` (abstain) |
| R2 | `grimmer(..., n=1)` → ZeroDivisionError (SD undefined at n=1) | guard: n≤1 → abstain |
| R3 | `tiva([])` / `tiva([p])` → ZeroDivisionError | guard: k<2 → abstain |
| R4 | **float mean silently read as 17 decimals → SPURIOUS inconsistent** (e.g. `grim(0.1+0.2,10)`) | raise `TypeError` — a string is required to preserve reported decimals; silent-wrong is worse than a crash |

Each fix is now locked by an assertion in `forensics_verify._selftest()` (the gate would fail if a guard
regressed). R4 was the most important: it was the one path that could produce a false-positive-shaped wrong
answer, and it came from caller error rather than the math — now it fails loudly instead.

### Honesty — CLEAN
- No κ=0 judgment is presented as machine-verified; the router labels every fired rule with its κ and appends
  the ceiling string ("a statistical inconsistency is a mathematical fact about the reported numbers, NEVER an
  accusation about the people").
- Every flagged forensic output explicitly names "rounding/typo/reporting error are possible explanations" and
  "NOT proof of misconduct." No language crosses the inconsistency≠fraud line.
- No real named person is accused; Demo A uses the method papers' own published worked examples.
- **Prediction integrity:** PREDICTION.md was written ~2 min before RESULT.json; no prediction was silently
  revised. The one honest miss (sensitivity 71.5% vs the soft "~40–70%" band) is flagged, not hidden; the hard
  prediction (strictly between 0–100%, monotone in n, specificity=100%) held.

## Auditor's final verdict (quoted)
> "SOUNDNESS: VERIFIED SOUND. Zero false positives found. … HONESTY: CLEAN. No output crosses the
> inconsistency≠fraud line. … The weapon is soundly built."

## Disposition
All 4 robustness bugs fixed and re-gated (2026-06-20); gate + demo re-run green after the fixes. The exact
forensic core is independently confirmed sound.

---

# PSYMETRIX — independent cross-model audit ROUND 2: full P-MODEL (2026-06-20)

After the P-MODEL piece was upgraded from dimensionality-only to a full CFA/SEM/EFA/IRT engine
(`model_verify.py`, using semopy/factor_analyzer/girth, now installed), a second Sonnet audit (≠ the Opus
generator) re-ran everything, independently re-derived the fit numbers, scrutinized a post-hoc verdict change,
and tried to game it.

## What the auditor confirmed
- **CFA numbers match the canonical lavaan reference to 4 sig figs** (recomputed independently via raw semopy):
  CFI 0.9306 vs .931, TLI 0.8958 vs .896, RMSEA 0.0923 vs .092, **SRMR 0.0652 vs ~.065**, chi2 85.306 / df 24
  EXACT. The hand-rolled SRMR is correct (lower-triangle-incl-diagonal, lavaan convention).
- **The "mixed"-verdict change was LEGITIMATE, not goalpost-moving** (the key honesty question). It is grounded
  in Marsh, Hau & Wen (2004) — which `GROUNDING_MODEL.md` cited *before* the run — and, crucially, it does **not**
  rescue the committed prediction: prediction #1 said "acceptable", the verifier returns "mixed", and the demo
  records that as a **`[MISS]`** with `checks.pred1_3factor_verdict_hit=false`. The miss stands, reported, not
  silently converted to a pass.
- **IRT 2PL recovery clean** (corr(a_true,a_est)=0.996, corr(b)=0.996, discrimination rank perfect);
  **Yen's Q3 clean** (flags a cloned pair, no false positives on independent/strong-factor items);
  **EFA parallel analysis seed-stable** (3 factors across 10 seeds).
- **The gate is real, not theater:** flipping the verdict threshold made the self-test fail with a specific
  assertion; reverted.

## Findings — 1 CRITICAL soundness bug + 2 robustness, ALL FIXED
| id | bug | fix |
|---|---|---|
| **D1** | **CRITICAL gaming vector: on random/over-parameterized data semopy returns CFI outside [0,1] (observed −9.7 … 102.5); a noise model could be rated "good" (CFI=33.5) — 4/40 random seeds leaked a good/acceptable verdict** | (1) clamp+degeneracy guard: CFI outside [0,1] or df≤0 → abstain; (2) **Bartlett's test of sphericity as the factor-analysis precondition** — if the correlation matrix is indistinguishable from identity (p>.05) the data is not factorable → abstain. **Re-swept: 0/40 random seeds now leak.** Real HS data (Bartlett p≈1e-166) is unaffected |
| D2 | constant (zero-variance) column → `LinAlgError` crash | input guard: zero-variance column → abstain |
| D3 | NaN inputs silently passed to semopy (unannounced row-drop/impute) | input guard: any NaN → abstain (handle missingness explicitly first) |
| D4 (cosmetic) | "mixed" covers a wide quality range (CFI .877 and .931 both "mixed") | mitigated: the per-index `index_tiers` table is always returned alongside the label, disambiguating |

Each fix is locked by a `model_verify._selftest()` assertion (random→abstain, constant-col→abstain,
NaN→abstain), so the gate fails if a guard regresses.

## Auditor's verdict (quoted)
> "The CFA fit numbers … match lavaan to 4 significant figures. The gate is real… The prediction-miss on #1 is
> reported honestly… The change to the 'mixed' scheme is legitimately grounded in Marsh 2004 and was not used to
> silently convert a miss into a pass. IRT 2PL parameter recovery is correct… Yen Q3 correctly flags cloned
> items… No output claims a passing model is 'true' or 'validated'." — with D1 (critical), D2, D3 to fix
> (now fixed).

## Honest residue
- P-MODEL fits and compares CFA/SEM/IRT and reports fit vs grounded cutoffs; it does **not** auto-search model
  space or do confirmatory bifactor/ESEM — out of scope, route to a human modeler.
- The "fit ≠ truth" ceiling is enforced in every note: a winning model is "not rejected and beats the
  alternative tested," never "true."

---

# PSYMETRIX — independent cross-model audit ROUND 3: P-REPRO + P-MULTIVERSE (2026-06-20)

After adding `repro_multiverse_verify.py` (P-REPRO = reproduce a coefficient two independent ways;
P-MULTIVERSE = specification-curve robust/fragile/mixed verdict), a third Sonnet audit (≠ generator) re-ran
everything, recomputed the reproduction TWO MORE independent ways, and hammered the multiverse verdict for
gameability.

## What the auditor confirmed
- **P-REPRO is SOUND:** the focal `religious` logit coefficient (Fair's Affairs) was reproduced by the auditor's
  **own third and fourth paths** — sklearn `LogisticRegression(penalty=None)` = **−0.375690** and scipy
  L-BFGS-B on the log-likelihood = **−0.375646** — both matching the tool's statsmodels+numpy −0.375646 to
  <1e-4. **Direction grounded** to Fair (1978): religiousness is a negative predictor of affairs.
- **The gate is real** (monkeypatching `specification_curve` to always return "robust" trips the
  null-must-be-fragile assertion); **prediction integrity** intact (PREDICTION.md pre-registered, no silent
  revision); **"robust ≠ true/causal" present** in docstring, notes, RESULT.json, and the demo print.

## Findings — fixed
| id | finding | class | fix |
|---|---|---|---|
| **C1** | all-False exclusion mask → zero specs → opaque `ValueError` crash (`add_constant`/`ptp` on empty, *outside* the try) | SOUNDNESS | design-matrix build moved inside `try`; degenerate subsets skipped; **zero-spec → ABSTAIN** (verdict None), locked by a self-test |
| **C3** | OVB/cherry-picked covariate pool can make a **true null look ROBUST** (omit a confounder → spurious effect in every spec) — structurally unavoidable but **unacknowledged** | ROBUSTNESS/honesty | added a non-waivable **output caveat**: the verdict is *conditional on a complete covariate pool*; the tool cannot certify no omitted confounder. New self-test: a confounded null (confounder in pool) must **not** be certified "robust" |
| **C4** | p-curve non-independence caveat was only in PREDICTION.md, not in machine output (`pcurve_evidential_value: True` with no warning) | HONESTY | added `pcurve_caveat` field + a caveat in the output: nested specs are non-independent → evidential value is **illustrative only** |
| **C5** | large-n significance (100% of specs sig) conflated with a meaningful effect; effect-size spread not reported | HONESTY | output now returns `coef_min/max/std/cv` and a **large-n caveat** ("judge robustness by SIGN + effect-size spread, not the significance rate"). Demo prints CV=0.073 — the effect is genuinely stable, not just large-n significant |
| **C6** | self-test null case used *unconfounded* data (the easy path); the dangerous null+confounding case was untested | ROBUSTNESS | added the confounded-null self-test (C3 row) |
| C2 (minor) | the two demo DV operationalizations (`>0` vs `≥1`) are a subset relation, labeled vaguely | cosmetic | relabeled in-code: "any affair" vs a "stricter, frequent-affair subset — defensible alternative, not identical" |
| C7 (low) | global `warnings.filterwarnings("ignore")` hides separation/collinearity | cosmetic | left as-is (the multiverse routinely hits non-converging specs by design; they're dropped, not silently trusted) — noted, not fixed |

All high/medium findings fixed and locked by self-tests; gate + demo re-run green after the fixes.

## Auditor's verdict (quoted)
> "The reproduction machinery (P-REPRO) is sound… [third path] −0.375690 … [fourth path] −0.375646 exactly…
> direction grounded in Fair (1978). The multiverse verdict machinery (P-MULTIVERSE) is sound conditional on
> honest covariate pool construction" — with C1/C3/C4/C5/C6 to address (now addressed).

## Honest residue
- P-MULTIVERSE certifies "not an artifact of the analytic choices **tested**" — it **cannot** certify the pool
  of choices was complete/unbiased (omitted-confounder gaming is structurally outside any multiverse tool).
  This is now stated in every output. **Robust ≠ true/causal.**
