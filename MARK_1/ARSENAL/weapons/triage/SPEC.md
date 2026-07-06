# SPEC — TRIAGE: failure-class → detector → mitigation (the ARMOR abstention table)

*Kit piece #4 / gap G2 (`Next/KIT_EXPANSION_PROPOSAL.md` §5). Written 2026-06-20. Built BOX-style,
gate-FIRST. This is **ARMOR, not a weapon** — it has no exact verifier of its own; its value is making
the box's single, undifferentiated abstention gate **operational**: a named taxonomy of HOW the box
fails, each row wired to its own detector + mitigation.*

## 0. WHAT IT IS / IS NOT (non-waivable framing)
- **IS:** a frozen `failure-class → detector → mitigation` decision table, applied as a checklist before
  any load-bearing output ships. Each row traces to a REAL box-caught failure (`EVOLUTION_LOG.md`) or a
  fetched external taxonomy (`GROUNDING.md`).
- **IS NOT:** ❌ a weapon (no exact verifier of "is this output failing?"); ❌ a guarantee of catching
  every failure (covers KNOWN classes; novel ones escape — every report says so); ❌ smarter output;
  ❌ a substitute for the cross-model audit (it ROUTES to it for the κ<1 classes).

## 1. THE DECISION TABLE (8 rows; each row traced)
Columns: `class · cheapest detector · κ of detector · mandated mitigation · trace`. Detector κ is the
honesty contract: κ=1 = a machine check that flips on a planted defect; κ<1 = a routed judgment.

| # | failure class | cheapest detector | κ | mandated mitigation | trace |
|---|---|---|---|---|---|
| 1 | **overconfidence** (consistent but wrong) | cross-paraphrase disagreement; count of unverified load-bearing claims ≥ threshold (threshold is **clamped ≤ default 1** — a caller cannot raise `unverified_threshold` to suppress the row; audit fix) | κ<1 | route up the ladder OR fetch/execute to ground; else abstain (shares ONE escalation handoff with SHOES/FOOTING — audit banner) | NIST valid&reliable; OWASP LLM09; C42 |
| 2 | **fabrication** (quote/number/cite not in source) | FACTHARNESS `ground()` substring+number check | **κ=1** *(κ<1 if no source supplied)* | hard FLAG; do NOT ship the ungrounded claim | C34 S-GROUND; Huang factuality |
| 3 | **specification-gaming** (passes a proxy, not the goal) | proxy ≠ independent oracle; in-sample vs OOS flip | **κ=1 IF an independent oracle exists (→ CRUCIBLE); else κ<1** | reject the proxy as verifier; demand a real check | C40 fuzz-seed; C42 in-sample Sharpe |
| 4 | **circular measurement** (scored on self-authored data) | provenance of eval data == the generator | **κ=1 structural** | invalidate the result; re-test on independent data | C41 answer-key leak |
| 5 | **numeric/branch-cut/convergence** (valid on a sub-domain) | multi-point / full-domain sampling | **κ=1** | label with the domain or REJECT; never global from local | C39 branch-cut |
| 6 | **distribution-shift** (novel input, uncalibrated) | input far from any known-good case | κ<1 | lower confidence explicitly; abstain on load-bearing | NIST "given conditions" |
| 7 | **shared-blind-spot** (verifiers AGREE) | agreement of same-family methods | κ<1 | treat agreement as RISK; add a methodologically-different check | B2/B8; C39 |
| 8 | **crash/silent-pass on malformed input** | adversarial/degenerate inputs (→ CRUCIBLE) | **κ=1 WHEN a probe callable is supplied; else κ<1 (null-op, `degraded`)** | the gate must ABSTAIN/error LOUDLY, never silent-pass | C38 missing-var crash |

**κ honesty (audit banner #3):** rows 3 and 8 say "→ CRUCIBLE". CRUCIBLE is **present** on 2026-06-20
(`GROUNDING.md` G5) as a gate-testing meta-weapon — but presence-on-disk does NOT auto-supply an
*independent oracle of the answer* for an arbitrary task, so TRIAGE's κ does NOT key off the dir:
- Row 3 (spec-gaming): **κ=1 ONLY when the record supplies a RECOGNIZED independent oracle verdict / OOS
  signal** (a flat oracle disagreement is exact). A "usable oracle" must be a **non-empty STRING token that
  matches a known agree/disagree verdict** (`correct`/`right`/`pass`/… or `wrong`/`fail`/`incorrect`/
  `error`/`false-positive`/…, including as the leading word of a phrase like `"wrong answer"`). **Garbage
  non-verdicts (`''`, `0`, `False`, `True`, `1`, `"maybe"`, `"yes-ish"`, arbitrary strings) are NOT a usable
  oracle → κ<1, `degraded: True`** (audit fix — `oracle is not None` previously laundered these to κ=1).
  With no usable oracle, TRIAGE runs the **structural in-sample/OOS check itself at κ<1** and SAYS so
  (`degraded: True`). CRUCIBLE-present must not launder a κ<1 judgment into a κ=1 certification — keying κ
  off the *recognized* supplied oracle is the non-circular rail.
- Row 8 (crash/silent-pass): TRIAGE runs its **own** adversarial-input probe (feed degenerate inputs to
  the supplied detector callable) at κ=1 on the *did-it-error-loudly* question (that IS exactly checkable
  by TRIAGE itself) — the κ=1 is on "the gate abstained/errored loudly vs silently passed", not on a
  richer CRUCIBLE adversary (which would extend, not replace, this floor). **A degenerate-input return is a
  silent-pass UNLESS the callable raised, abstained, or returned an EXPLICIT reject/falsey verdict** — the
  silent-pass test is **value-based, not identity-based** (`{'ok': 1}`, truthy ints/lists, bare truthy or
  ambiguous returns, and a no-raise `None` all count as silent-pass; audit fix — the old `out.get('ok') is
  True` identity check let `{'ok': 1}` slip through). **When NO probe callable is supplied, NO check runs →
  the row is κ<1, `degraded: True` (a null-op, NOT a verified-clean κ=1)** (audit fix — it previously
  mislabeled the un-run row κ=1/`degraded: False`).
- Row 2 (fabrication) drops to κ<1 (`degraded`) if FACTHARNESS is unavailable OR no source text is supplied.

## 2. THE REPORT SCHEMA (audit banner #2 — `uncovered_novel_classes` is REQUIRED)
`triage_check(output_record)` returns a TRIAGE REPORT dict. **Required fields:**
```
{
  "tool": "TRIAGE",
  "rows": [ {class, fired: bool, kappa, degraded: bool, evidence, mandated_action}, ... ],  # one per applicable row
  "fired_classes":   [class, ...],         # rows that fired
  "coverage_classes":[class, ...],         # the N classes this table covers
  "n_coverage": N,
  "uncovered_novel_classes": true,         # ALWAYS true — REQUIRED, never strippable
  "overall": "NO_LISTED_CLASS_FIRED" | "CLASS(ES)_FIRED" | "ABSTAIN",
  "verdict_text": "...no 'safe'...",       # see §3
  "ceiling_note": "...",
}
```
`uncovered_novel_classes` is hard-coded `True` and a self-test asserts it can never be `False` — so a
downstream consumer cannot silently strip the "no all-clear" caveat.

## 3. THE "NO ALL-CLEAR" RULE (audit banner / honesty rail)
The report **NEVER** emits "safe" / "all-clear" / "verified safe". When no row fires it emits exactly:
> `"no listed class fired (coverage = these N classes; novel/unknown classes are NOT covered and may escape)"`
A self-test asserts the literal strings "safe" and "all-clear" never appear in any verdict, and that the
absence-of-flag verdict always carries the coverage count + the novel-escape caveat.

## 4. THE NON-WAIVABLE SELF-TESTS (kickoff §3 + audit banner #1)
`selftest_all.py` runs and exits non-zero on ANY failure:
- **(a) accept-good** — a clean, grounded output: NO row falsely fires.
- **(b) catch-broken** — KNOWN-fabricated output → the fabrication row FIRES (via FACTHARNESS).
- **(c) catch-broken** — KNOWN branch-cut "identity" → the numeric row FIRES.
- **(d) abstain-malformed** — a malformed/degenerate output record → TRIAGE ABSTAINS/errors loudly,
  never silent-passes (row 8).
- **(e) no-all-clear** — the report NEVER emits "safe"; the no-flag verdict carries coverage + novel caveat.
- **(f) schema** — `uncovered_novel_classes` is present and `True`, and cannot be set False.
- **(g) RETROACTIVE RE-FLAG (NON-WAIVABLE, audit banner #1)** — feed ≥3 reconstructed REAL past failures
  (SYMBOLICA branch-cut C39, PROOFSMITH answer-key leak C41, OPTIMA malformed-input crash C38) and assert
  **each one re-fires the row the human audit caught by hand**. Committed predictions in
  `demo_retroactive/PREDICTION.md` (written BEFORE the run). This IS the proof of value.
- **(h) router** — `triage_router._selftest`: routes a κ=1-checkable class to a machine check, a κ<1 class
  to the cross-model panel/abstention, an empty record to abstain.
- **(i) every named reject case** — each κ=1 detector must (i) PASS a known-good, (ii) CATCH a known-broken.

A gate that can't fail is not a gate: each detector self-test proves it FLIPS on a planted defect.

## 5. COMPOSITION (kickoff §4)
- **Composes existing κ=1 checkers:** the fabrication row delegates to FACTHARNESS `ground()` (no new
  fabrication solver). Where a κ=1 checker is ABSENT (CRUCIBLE), the row **degrades to κ<1 honestly**
  (`degraded: True` in that row) per §1.
- No new solver is introduced. TRIAGE is a router/checklist over existing checks + cheap structural probes.

## 6. CEILING (every report carries it)
- A taxonomy covers KNOWN classes only — novel failures escape (`uncovered_novel_classes` always true).
- No "safe" — only "no listed class fired."
- κ=1 rows are real machine checks; κ<1 rows are routed judgments, not certifications.
- It is ARMOR, not a weapon — no capability claim, no ratchet movement.
