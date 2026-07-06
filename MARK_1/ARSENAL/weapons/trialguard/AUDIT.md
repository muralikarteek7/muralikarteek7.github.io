# TRIALGUARD — independent cross-model audit (2026-06-20)

**Auditor:** a DIFFERENT model from the generator (Claude **Sonnet**, spawned via the Agent tool). Fable 5 is
inactive, so the auditor is Sonnet — **never Opus-audits-Opus** (C8 independence).
**Mandate (heightened, because the domain is clinical):** re-run from scratch, independently re-derive every
forensic certificate, **hunt for a FALSE POSITIVE** (a clean stat / clean trial wrongly flagged = a false
accusation), and **red-team the inconsistency≠fraud honesty framing HARDEST OF ALL** — does any output read as
an accusation? A single accusatory phrasing is a **blocking defect**.

## What the auditor did
1. **Re-ran** `selftest_all.py` (the gate) and `demo_forensics/run_demo.py` — both pass, **bit-for-bit
   deterministic** across two runs.
2. **Independently re-derived certificates with its OWN arithmetic** (not the repo's code):
   - **GRIM 5.27/n=43** → 226/43=5.2558→5.26, 227/43=5.2791→5.28; neither rounds to 5.27 → **impossible**. ✓
   - **Carlisle–Stouffer** on p=[.90,.85,.92,.88] → its own scipy Z=2.4490, p=0.01432 = TRIALGUARD's
     Z=2.449 / p=0.0143245. ✓ direction logic confirmed (high p → +z_i → Z>0 = too-similar).
   - **Cox PH HR** on its own dataset (n=100, β=1.2) → statsmodels PHReg β=1.41458, SE=0.21346 =
     TRIALGUARD `cox_ph` β=1.41458, SE=0.21346 (**5-decimal agreement**). ✓
   - **E-value** RR=2 → 2+√2 = 3.414214 = 3.4142. ✓
   - **Trim-and-fill** pulls the asymmetric body toward the null (0.13058→0.125, k0=1, suppressed_side=left). ✓
3. **Hunted false positives (the cardinal soundness check):**
   - **Carlisle calibration sweep** — 2000+ genuinely simply-randomized trials, varied k=4–20, n=20–200:
     **0.001→4/2000 (P(X≥4|λ=2)=0.14, NOT significant), 0.01→26/2000, 0.05→90/2000 — WELL-CALIBRATED**; a
     k=8/n=60 confirmatory sweep 2/3000=0.0007. No systematic over-flagging.
   - **Exact checks** — GRIM (all integers for n=43), percentage→count (5000 achievable values), allocation
     ratio (5000 achievable splits): **ZERO false certificates of impossibility.**
4. **Red-teamed the honesty framing** (every verdict/note/ceiling/design_caveat field), tried to break the
   `affirms_misconduct()` checker, checked for κ=0 clinical smuggling, and fed 13 malformed inputs.

## Findings — SOUND core; 3 meta-layer defects, ALL FIXED
The auditor's headline conclusions: **(1) the EXACT forensic core is SOUND** (zero false certificates across
exhaustive sweeps); **(2) the Carlisle screen is WELL-CALIBRATED** at α; **(3) no emitted verdict/note affirms
misconduct and no κ=0 clinical claim is smuggled in**; **(4) all malformed inputs abstain (no crashes).** Three
defects were found, **none in the output path** — all in the meta-layer tooling:

| id | severity | defect | fix |
|---|---|---|---|
| **F1** | MEDIUM | `affirms_misconduct()` returns **True on the CEILING string itself** — the CEILING ends with Carlisle's grounded quote *"Fraud, unintentional error, correlation, stratified allocation and poor methodology…"*; the checker's 24-char negation window missed it. A latent downstream-consumer trap (the gate only scanned `verdict`, so the gate was internally correct, but a consumer scanning the ceiling would get a spurious True). | Hardened the checker: **clause-level** negation scan (back to the last sentence/quote boundary) + a **citation/list-of-causes exemption** (`carlisle`, `might have contributed`, `unintentional error`, …). `affirms_misconduct(CEILING)` is now **False**; locked by a self-test. |
| **F2** | LOW | checker false-positives on legitimate disambiguating phrasings: `"fraud remains unconfirmed"` (postceding negator), `"cannot be concluded to involve fraud"` (negator outside the window), `"antifraud"` (no word boundary). Over-flagging (blocks legit text), not under-catching. | Added **word-boundary** check (skip word-internal matches like *anti-fraud*), **postceding negators** (`unconfirmed`/`unproven`/`alleged`/…), and the clause-level scan. All three now **False**; true affirmations (`fraudulent`/`fabricated`/`rigged`/`manipulated`/`falsified`) still **True**; locked by self-tests. |
| **F3** | LOW | the Carlisle output dict reported `kappa=1`, ambiguous against the truly-exact GRIM/allocation/percentage κ=1 checks (the `regime` field and SPEC qualified it, but a consumer reading only `kappa` could conflate). | Changed the Carlisle output to **`kappa=0.9` + a `kappa_note`**: "the Stouffer arithmetic is exact, but a Carlisle flag is a calibrated STATISTICAL SCREEN, NOT an exact certificate like GRIM." SPEC's κ-profile already says the same. |

All fixes are **locked by assertions** in `forensics_trial_verify._selftest()` (the gate fails if a guard
regresses); gate + demo re-run **green** after the fixes, and the auditor's exact F1/F2 reproductions now return
the correct verdict (verified: CEILING→False, antifraud→False, "fraud remains unconfirmed"→False, while
"this trial is fraudulent"→True).

## Honesty / soundness verdict (the load-bearing results)
- **EXACT core SOUND:** zero false certificates of impossibility found (GRIM / allocation / percentage).
- **Carlisle screen WELL-CALIBRATED:** false-flag rate ≈ α (4/2000 at α=.001, within Poisson noise) — exactly
  the honest property: a *calibrated screen*, not an exact certificate, never a systematic false accuser.
- **Honesty CLEAN:** no emitted `verdict`/`note` affirms misconduct; the cardinal inconsistency≠fraud rail holds
  on every flagged output (each carries the exact statistic + benign explanations + false-positive modes + the
  ceiling). No κ=0 clinical/efficacy/causal verdict smuggled in; efficacy/approval routes to armor.

## Auditor's overall verdict (quoted)
> "TRIALGUARD's operational core is sound: the EXACT checks produce zero false certificates of impossibility; the
> Carlisle screen is well-calibrated at alpha; no output in any tested path affirms misconduct or asserts
> clinical truth… The Cox PH implementation matches statsmodels PHReg to 5 decimal places… Three defects were
> found, none in the primary output path… None of these defects cause a false accusation of any trial or person
> in any actual output. The cardinal rail (inconsistency ≠ fraud) is operationally enforced on all emitted
> verdict strings."

## Disposition
F1/F2/F3 fixed and re-gated (2026-06-20); the cross-model audit's own reproductions re-verified post-fix. The
exact forensic core is independently confirmed **sound**; the Carlisle screen independently confirmed
**well-calibrated**; the honesty framing independently confirmed **clean** (no output crosses the
inconsistency≠fraud line).

## Honest residue
- The Carlisle test is a **statistical screen**, not an exact certificate: its false-positive rate is ≈ α **by
  construction** and is **inflated** by correlated covariates and stratified/cluster designs (surfaced on every
  output as false-positive modes). It catches over-balancing fabrication with finite power (demo sensitivity
  86.7% on a strong fabrication), and **never** distinguishes fabrication from a legitimate stratified design —
  it reports the anomaly and the benign explanations, and STOPS.
- Reproduction (T-REPRO/T-SURVIVAL/T-META) ≠ clinical truth; robustness (T-MULTIVERSE) ≠ true; consistency
  (GRIM) ≠ correct. Efficacy/approval/causation are κ=0 → armor + abstain (E-value for observational causal).
