# SOCIUS — independent cross-model audit (auditor ≠ generator)

**Generator:** Opus 4.8 (orchestrator). **Auditor:** Sonnet 4.6 (a different model — Fable 5
inactive, so never Opus-audits-Opus). **Date:** 2026-06-20. The auditor re-ran the gate from
scratch, **re-derived the math by hand**, web-confirmed the load-bearing citations, and
red-teamed the honesty framing. Full charge + transcript in session history.

## Top-line verdict (auditor, verbatim sense)
> **"SOCIUS is sound as a tool. The demo is honest. No fraud, no circular measurement, no
> laundering of a failed finding into a positive one."**

## Independently re-derived (auditor's own arithmetic — all matched)
| quantity | auditor re-derivation | SOCIUS output | match |
|---|---|---|---|
| E-value(3.9) | 3.9+√(3.9·2.9)=7.263 (anchor: VanderWeele & Ding report 7.26) | 7.263 | ✅ |
| E-value(2.0) | 2+√2=3.4142 | 3.4142 | ✅ |
| d=−0.452 → RR → E | exp(0.91·−0.452)=0.663 → invert 1.509 → E=2.386 | 2.386 | ✅ |
| 120-spec count | 2·5·3·3·2=180 − 2 incompatible combos (30 each)=120 (direct enumeration) | 120 | ✅ |
| Cronbach α (raw data, own pandas) | (3/2)(1−31.370/81.797)=0.9247 | 0.9247 | ✅ |
| multiverse significant | 7/120 (5.8%), matches Steegen et al. 2016 | 7/120 | ✅ |

## Citations the auditor web-confirmed (the load-bearing ones)
- **Kenny, Kaniskan & McCoach (2015)**, *Sociological Methods & Research* 44(3):486–507 — RMSEA
  "too often falsely indicates a poor fitting model" at small df. **Confirmed real** (the basis for
  the invariance fix). The auditor independently ran a 20-seed simulation: strict ΔRMSEA falsely
  rejected **10/20 truly-invariant 3-item models**; ΔCFI held in all 10 → **"Kenny vindicated"**.
  The fix is a legitimate methodological choice, **not results-hacking**.
- **Cheung & Rensvold (2002)**, *SEM* 9:233–255 — ΔCFI ≤ 0.01 as primary criterion. **Confirmed.**

## Findings (4) and what I did about each
| # | auditor finding | severity | resolution |
|---|---|---|---|
| 1 | **Small-df guard mutes subtle metric DIF on 3-item scales** (detection: 0.10 gap→3%, 0.15→30%, 0.20→70%, 0.30→100%). Real blind spot, but the Durante scale is genuinely invariant (ΔCFI≈0) so no signal is masked here. | real, bounded | **DOCUMENTED** prominently in `measure_verify.py` docstring with the measured rates + a mitigation (prefer ≥4–5 items; treat a short-scale 'pass' as 'no GROSS non-invariance'). The guard is correct (Kenny); removing it would re-introduce false rejections. |
| 2 | **Demo reimplemented the multiverse verdict** instead of calling the frozen verifier → reduced independence (both gave robust=False, so no verdict change). | minor | **FIXED.** Extracted `summarize_speccurve()` as the single frozen rule; both `run_multiverse()` and the demo's `s_multiverse()` now call it. Demo no longer reimplements the gate. |
| 3 | **`robust_to_confounding=True`** on S-CAUSAL could be misread as "finding is fine" — the E-value is for ONE cherry-picked path (1 of 120). | minor | **FIXED.** Renamed to `robust_to_confounding_on_this_single_path`, added a `scope` field and a `WARNING` that the path is cherry-picked and the finding still DIES; console line updated. |
| 4 | **`repro_verify` abs_tol=1e-6 floor** lets a 2× discrepancy pass on values <1e-5 (irrelevant to the demo's integer checks). | trivial | Acknowledged; does not affect any demo output (counts are large integers). Left as a known property of mixed tol; callers pass explicit tol for tiny-value comparisons. |

## Net
The auditor found **no verdict-changing bug** and **no dishonesty**. The one genuine limitation
(short-scale invariance sensitivity) is now disclosed in-code. The two clarity/independence issues
are fixed and the suite re-runs green. **An earlier, separate machine-check by the generator had
already caught and fixed the one real bug** (the false non-invariance from a small-df ΔRMSEA
artifact) before this audit — the audit then *confirmed* that fix is methodologically sound rather
than convenient. This is the verify-independently loop working as intended on both the tool and the
generator.

---

# ROUND 2 — S-GROUND audit (the grounding / fabrication-detector sub-weapon, added 2026-06-20)

**Auditor:** Sonnet 4.6 (≠ the Opus generator). Charged to BREAK the frozen layer. **It did — and
this is the loop working.** Verdict: *"the frozen layer is NOT fully sound; the demo is honest."*
It found **3 genuine bugs** the self-tests missed (plus confirmed all 3 source abstracts are real:
Steegen 2016, Scott & Pound 2015 verbatim-matched to the published PDFs/PMC; Durante 2013 key
quote + authors confirmed).

| # | audit break | was it real? | fix (machine-verified) |
|---|---|---|---|
| **A3** | `verify_number("7", "7.5")` → grounded (a "7" matched inside the decimal 7.5) — the lookahead blocked a following digit but not a following decimal point | **REAL bug** | boundary regex now `(?<!\d)(?<!\d\.)NUM(?!\d)(?!\.\d)` — blocks decimal context both sides; sentence-final `7.` still grounds. Regression self-tests added. |
| **B-CRITICAL / B1 / B2** | `verify_bibliography("Smith and Jones", …, "Brown and Williams")` → grounded; `"Fra Gel Van"` matched `Francis…Gelman…Vanpaemel` — connector "and" was a valid 3-char token and matching was SUBSTRING not word-boundary | **REAL bug (the worst)** | now EXACT alphabetic-word matching against the source author word-set, a stopword filter (`and/et/al/…`), and **every** claimed name-token must match. Wrong-author cites now fail; real cites still pass. Regression self-tests added. |
| **A1** | `verify_quote("significant effect p 0.001", "significant effect (p < 0.001)")` → grounded — aggressive normalisation stripped `(`,`<`,`)` so a punctuation-stripped fabrication matched | **REAL (moderate)** | quotes now use a PUNCTUATION-PRESERVING normaliser (case/accents/smart-quotes/whitespace only); a stripped fabrication no longer matches, real verbatim quotes still do. Regression self-test added. |
| A4 | `verify_number("2213", "2,213")` missed (comma format) — a false ACCUSATION risk | already fixed by the generator (thousands-comma strip) before the audit; auditor confirmed the fix path | locked by self-test |
| struct. | `layer1_frozen_checks` field mixed in the κ=0.7 bib check | clarity | split into `layer1_frozen_checks_kappa1` (quote/number) + `bibliographic_check_kappa0p7` |

**All 3 bugs fixed; the auditor's exact break inputs were independently re-run and now return the
correct verdict; real cases still ground; the full gate + both demos re-run green (demo 8/8).** The
self-test gate now carries the auditor's break cases as regression locks — the bugs cannot silently
return. κ-labelling, the non-accusation rail, and ABSTAIN-on-unfetchable were all judged **PASS**.
**Honest takeaway: the first cut of S-GROUND shipped unsound in three ways; the independent audit
caught them and the gate now locks the fixes. This is exactly why a different model must check —
the generator's own self-tests passed all three buggy versions.**
