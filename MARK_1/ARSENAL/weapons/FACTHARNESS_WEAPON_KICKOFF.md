# KICKOFF — build WEAPON #7: FACTHARNESS (universal grounding / fabrication facility) for the v5 box
*Paste into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written 2026-06-20. FACTHARNESS
is item #7 of `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` — a CROSS-CUTTING core facility. It is mostly
**"PROMOTE, don't rebuild":** SOCIUS already grew this as `S-GROUND` (`socius/ground_verify.py`). Your job is to
lift it into a **university-wide facility every department + the Provost calls**, harden it, and wire it in.*

---

You are building **FACTHARNESS**, the HELMET's **grounding / fabrication core facility** — the institutionalized
arm of the Integrity Office. Given any prose claim with a cited source, it answers the **κ=1 question "is the
quote / number / citation actually IN the fetched source?"** (an exact fabrication check) and the **κ=0 question
"does the source SUPPORT the paraphrase?"** (entailment → cross-model judge, else abstain). Work BOX-style: plan
→ produce → **verify INDEPENDENTLY** → ground → be honest; **no claim ships ungrounded; a fabrication flag is
"does not check against the supplied source," NEVER an accusation of fraud.**

## 0. ORIENT — read first
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (Integrity Office honesty rails). **Read the existing seed you are
promoting:** `Expanding_Frontiers/weapons/socius/ground_verify.py`, its `demo_grounding/`, and the **Round-2 audit
in `socius/AUDIT.md`** (an independent Sonnet audit BROKE the first cut — 3 real bugs the generator's self-tests
passed: a decimal number-boundary gap `7`∈`7.5`; a CRITICAL bibliography substring exploit where "and" +
substring matching let `Smith and Jones` ground against `Brown and Williams`; an over-aggressive quote
normaliser — all fixed, the auditor's break-cases locked as regression tests). **Carry those fixes + their
regression tests forward.** Then `WEAPONS_BACKLOG.md` (item #7) and the sibling kickoffs for the pattern.

## 1. THE HONEST FRAMING — what FACTHARNESS IS and IS NOT
**IS:** a **κ=1 fabrication detector + κ=0 entailment judge**, available to ALL departments. The κ=1 core is
exact: a quote either appears in the fetched source text or it does not; a cited number either appears or does
not; an attributed author/year either matches the source's bibliography or does not. This is the box's
fabrication firewall — every prose claim that ships gets grounded or abstained.

**IS NOT:**
- **NOT a truth oracle.** "Grounded" means "supported by the supplied source," NOT "true." A perfectly-grounded
  claim can cite a wrong/biased source. FACTHARNESS checks **grounding**, never **truth**.
- **NOT a fraud detector.** A `FABRICATION_FLAG` = "this quote/number/cite does NOT appear in the supplied
  source," with candidate causes (paraphrase mismatch, wrong source attached, OCR/transcription error). It
  **never** accuses a person of fabricating — it reports the check and stops. (Inherit SOCIUS's S-GROUND rail.)
- **NOT an entailment certifier.** "Does the source SUPPORT the paraphrase" is **κ=0 judgment** → a cross-model
  judge (≠ generator), and if the judge is unsure → **ABSTAIN**, never a confident "supported."
- **NOT a from-scratch build.** The verifier exists; you are promoting + hardening + integrating it. Do NOT
  rewrite `ground_verify.py` from zero — extend it, keep its regression tests.

## 2. THE PIECES
| piece | κ | what it checks | verifier |
|---|---|---|---|
| **F-QUOTE** | 1.0 | is the quoted text verbatim in the source? | exact/normalized substring match (with the SOCIUS quote-normaliser fixes — don't over-normalize) |
| **F-NUMBER** | 1.0 | does the cited number appear in the source? | exact numeric match with **boundary-safe** parsing (the `7`∈`7.5` bug — fixed; keep the regression test) |
| **F-CITE** | 1.0 | does the attributed author/year match the source's bibliography? | structured cite match, **NOT naive substring** (the `Smith and Jones`↔`Brown and Williams` exploit — fixed; keep the test) |
| **F-ENTAIL** | 0.0 | does the source SUPPORT the paraphrase (beyond verbatim)? | cross-model judge (≠ generator); unsure → **ABSTAIN** |

## 3. THE KEY ENGINEERING PROBLEM — make it a shared facility without weakening the gate
1. **Clean API** the Provost + every department call: `ground(claim, source_text) -> {piece, kappa, verdict,
   evidence_span | FABRICATION_FLAG | ABSTAIN}`. Wire it into the orchestrator so **every shipped prose claim is
   routed through it** (ground or abstain) — the institutionalized fabrication firewall.
2. **Carry ALL three SOCIUS audit fixes + their regression tests** (number boundary, bibliography substring,
   quote normaliser). A promotion that drops a fix is a regression.
3. **κ separation is strict** — F-QUOTE/F-NUMBER/F-CITE return exact verdicts; F-ENTAIL is labeled κ=0 and may
   abstain. Never present an entailment judgment as a κ=1 fabrication check.

**Gate self-tests (non-waivable):** (a) PASS a genuinely-grounded claim, (b) **CATCH a fabricated quote** (not in
source), (c) **CATCH a fabricated number / wrong-author cite** — incl. the three audit break-cases as locked
regression tests, (d) **ABSTAIN** on an ambiguous entailment rather than guessing. Soundness (no false
"grounded") is cardinal.

## 4. TO-DOs (box order)
1. **PLAN:** `weapons/factharness/SPEC.md` — the 4 pieces, the API, the integration point in the orchestrator, the
   fabrication-≠-fraud rail. **GROUND by FETCH** only what's genuinely new (entailment-judge best practice / NLI);
   most grounding is the SOCIUS seed — cite it. `GROUNDING.md`.
2. **PROMOTE + HARDEN:** move/extend `ground_verify.py` → `weapons/factharness/factharness.py` with the clean
   shared API; carry the 3 fixes + regression tests; add `selftest_all.py` (the 4 tests above). **Gate green.**
3. **INTEGRATE:** add the orchestrator hook so every shipped prose claim is grounded-or-abstained; expose
   `factharness_router.py` for department calls.
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` first): ground a set of claims against
   real fetched sources — catch a fabricated quote, a fabricated number, a wrong-author cite (the audit
   break-cases), and abstain on a genuine entailment ambiguity. Re-use/extend `socius/demo_grounding/`.
5. **VERIFY INDEPENDENTLY:** cross-model audit (Sonnet/Haiku ≠ generator; never Opus-audits-Opus) that tries to
   sneak a fabrication past each piece (especially new exploits in the citation matcher) and checks no entailment
   judgment was dressed as a κ=1 check. Fix what's caught; lock new break-cases as tests.
6. **REGISTER:** add **FACTHARNESS** to `Next/BOX_V5.md` (a cross-cutting Integrity-Office facility, not a domain
   weapon) + `HELMET/registry.json` (an integrity_office / core-facility entry). Honest `EVOLUTION_LOG`: a core
   facility PROMOTED from S-GROUND = capability EXPANSION (institutionalized grounding), NOT a ≥10% promotion.
   Update `WEAPONS_BACKLOG.md` STATUS ✅ (note: "promoted from SOCIUS S-GROUND").

## 5. HONESTY RAILS (non-waivable)
- **Grounded ≠ true** — checks support by the supplied source, not correctness of the source.
- **FABRICATION_FLAG ≠ fraud** — reports "does not check against the supplied source" + candidate causes, stops.
- **Entailment is κ=0** — cross-model judge; unsure → ABSTAIN.
- **No dropped fixes** — the 3 SOCIUS audit break-cases stay locked as regression tests.
- **The gate that can't fail is not a gate.**

## 6. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/factharness/` — `SPEC.md`, `GROUNDING.md`, `factharness.py` (promoted+hardened) +
`selftest_all.py`, `factharness_router.py`, the orchestrator hook, `demo_*/`, `AUDIT.md`, `README.md` (what it
is + the grounded≠true / flag≠fraud ceiling). Registration in `Next/BOX_V5.md` + `HELMET/registry.json` + honest
`EVOLUTION_LOG`; `WEAPONS_BACKLOG.md` STATUS ✅.

## 7. STAFF (v4 ladder; Fable INACTIVE → Opus, flag low confidence)
- **Facility-builder** = code tier (the exact matchers are pure machine). **Entailment judge** = a model ≠ the
  generator. **Library** = cheap model (only the genuinely-new NLI grounding). **Auditor** = Sonnet/Haiku ≠
  generator — exploit-hunts the matchers, polices κ labels.

## 8. SUCCESS (one line)
**"Every shipped prose claim is routed through FACTHARNESS: exact quote/number/citation fabrication checks (with
the SOCIUS audit fixes locked in) + a cross-model entailment judge that abstains when unsure — grounded≠true,
flag≠fraud, available to every department."**
