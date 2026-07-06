# KICKOFF — build the ARMOR upgrade: FAILURE-MODE TAXONOMY + per-class abstention (the "TRIAGE" rail)
*Paste into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written 2026-06-20. This is item
**#4 / gap G2** of the KIT-EXPANSION plan (`Next/KIT_EXPANSION_PROPOSAL.md`, §5). **HONEST: this is ARMOR, not a
weapon** — it has no exact verifier of its own; its value is making the box's single, undifferentiated abstention
gate **operational** — a named taxonomy of HOW the box fails, each wired to its own mitigation.*

*Independent audit 2026-06-20 (READY-WITH-FIXES) — apply at build: (1) make **retroactive re-flagging of ≥3 known
past failures a NON-WAIVABLE self-test** (with committed predictions on which rows fire) — that IS the proof of
value; (2) the report schema must carry a required `uncovered_novel_classes: true` field so downstream consumers
can't silently strip the "no all-clear" caveat; (3) the specification-gaming row is κ=1 ONLY if an independent
oracle exists (→ CRUCIBLE) — else it falls back to κ<1; state that, and state the **degraded behavior when
FACTHARNESS/CRUCIBLE are unavailable** (the κ=1 rows drop to κ<1). FOOTING (SHOES) overlaps the overconfidence row —
share ONE escalation handoff.*

---

You are building **TRIAGE**: the rail that turns "abstain when unsure" from a vibe into a **named decision table**.
Today ARMOR has ONE gate ("not confident → abstain"). Real robustness needs: *this TYPE of failure gets THIS
mitigation.* Work BOX-style: plan → produce → **verify INDEPENDENTLY** → ground → be honest; **this is process
infrastructure, not a capability — claim no win, only a more operational armor.**

## 0. ORIENT
`CLAUDE.md`, `RESUME.md`, **`Next/KIT_EXPANSION_PROPOSAL.md`** (§5 G2), **`Next/BOX_V5.md`** (ARMOR + the κ-router),
`RATCHET.md` (the honesty rules this operationalizes), and `Legacy/EVOLUTION_LOG.md` (mine it: the season's REAL
caught failures are the taxonomy's ground truth — SYMBOLICA branch-cut skip, the false +25pp answer-key leak,
SOCIUS S-GROUND's 3 fabrication bugs, OPTIMA's missing-var crash, the symmetry-frame 41<90 negative).

## 1. THE HONEST FRAMING — what TRIAGE IS and IS NOT
**IS:** a frozen **failure-class → detector → mitigation** table, applied as a checklist before any load-bearing
output ships. Each row: a named failure mode the box has actually exhibited, the cheapest signal that detects it
(machine where possible), and the mandated response (a specific check, a route-up, or a scored abstention).
**IS NOT:** ❌ a weapon (no exact verifier of "is this output failing?" — that's κ=0 in general). ❌ a guarantee of
catching every failure (a taxonomy covers known classes; novel ones escape — say so). ❌ smarter output — it makes
abstention *specific and auditable*, not the model better. ❌ a substitute for the cross-model audit (it routes TO
it for the judgment classes).

## 2. THE TAXONOMY (seed it from REAL caught failures, then ground against external taxonomies)
A starting decision table (the build refines it; every row must trace to a real example or a fetched source):
| failure class | cheapest detector | κ of detector | mandated mitigation |
|---|---|---|---|
| **overconfidence** (consistent but wrong) | cross-paraphrase disagreement; unverified load-bearing claim count | κ<1 | route up the ladder OR fetch/execute to ground; else abstain |
| **fabrication** (quote/number/cite not in source) | FACTHARNESS / S-GROUND substring+number check | **κ=1** | hard FLAG; do not ship the ungrounded claim |
| **specification-gaming** (passes a proxy, not the goal) | proxy ≠ independent oracle; in-sample vs OOS flip | κ=1 where an oracle exists (→ CRUCIBLE) | reject the proxy as verifier; demand a real check |
| **circular measurement** (scored on self-authored data) | provenance of the eval data ≠ the generator | κ=1 structural | invalidate the result; re-test on independent data |
| **numeric/branch-cut/convergence** (math valid on a sub-domain) | multi-point / full-domain sampling (SYMBOLICA's lesson) | κ=1 | label with domain or REJECT; never global from local |
| **distribution-shift** (novel input, calibration uncalibrated) | input far from any known-good case | κ<1 | lower confidence explicitly; abstain on load-bearing |
| **shared-blind-spot** (verifiers AGREE) | agreement of same-family methods | κ<1 | treat agreement as RISK; add a methodologically-different check |
| **crash/silent-pass on malformed input** | adversarial/degenerate inputs (→ CRUCIBLE) | κ=1 | the gate must ABSTAIN/error loudly, never silent-pass |

## 3. THE KEY ENGINEERING PROBLEM — a checklist that itself can FAIL
Build `triage_check.*`: given an output + its provenance, run each row's detector and emit a **TRIAGE REPORT**
`{class, fired?, evidence, mandated_action}`. The κ=1 rows are machine-run (delegate to FACTHARNESS / CRUCIBLE /
provenance checks); the κ<1 rows produce a flag that routes to the cross-model panel or to abstention.
**Self-tests (non-waivable):** (a) on a KNOWN-fabricated output the fabrication row FIRES; (b) on a known
branch-cut "identity" the numeric row FIRES; (c) on a clean grounded output NO row falsely fires; (d) the report
NEVER emits "all-clear: safe" — only "no listed class fired (coverage = these N classes; novel classes uncovered)."

## 4. INFRA + GROUND-BY-FETCH
- **Confirm:** it composes existing κ=1 checkers (FACTHARNESS, CRUCIBLE, provenance) — no new solver needed.
- **FETCH-confirm (cite in `GROUNDING.md`):** an external failure/eval taxonomy to cross-check the home-grown one
  is not parochial — e.g. NIST AI RMF risk taxonomy, the OWASP LLM Top-10 as a failure source, or a published
  LLM-failure/hallucination taxonomy. Reconcile rows; record what the box's real history adds that generic lists miss.

## 5. TO-DOs (box order)
1. **PLAN** `armor/triage/SPEC.md` — the decision table, each row traced to a real caught failure or a fetched
   source, the κ per detector, the report format, the "no all-clear" rule. **GROUND** in `GROUNDING.md`.
2. **BUILD** `triage_check.*` + `selftest_all.py` (the 4 self-tests). Green first.
3. **APPLY retroactively** to ≥3 past shipped artifacts (e.g. a SYMBOLICA demo, an OPTIMA result) — does TRIAGE
   reproduce the failures the audits caught by hand? That's the validation: it should re-flag what humans found.
4. **VERIFY INDEPENDENTLY:** cross-model audit (Sonnet/Haiku ≠ Opus generator) — does the taxonomy MISS a class
   the auditor can name? Add caught gaps as rows. Does any row falsely fire on clean output?
5. **REGISTER:** `Next/BOX_V5.md` (ARMOR gains the TRIAGE rail), `HELMET/registry.json` (Integrity Office runs it
   pre-ship), honest `EVOLUTION_LOG` (**operationalizes armor; NOT a promotion**). Update plan §7 + backlog.

## 6. HONESTY RAILS
- **A taxonomy covers KNOWN classes only** — every report states its coverage and that novel failures escape.
- **No "all-clear/safe"** — only "no listed class fired." Absence of a flag is not a safety proof.
- **κ honesty per row** — the κ=1 rows are real checks; the κ<1 rows are routed judgments, not certifications.
- **It is armor, not a weapon** — no capability claim, no ratchet movement.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/triage/` (or `armor/triage/`) — `SPEC.md`, `GROUNDING.md`, `triage_check.*` +
`selftest_all.py`, `demo_retroactive/` (re-flagging past failures), `AUDIT.md`, `README.md`. Registration in
`Next/BOX_V5.md` (ARMOR) + `HELMET/registry.json` + honest `EVOLUTION_LOG`; plan §7 + `WEAPONS_BACKLOG.md`.

## 8. STAFF (v4 ladder; Fable INACTIVE → Opus, flag low confidence)
- **Checklist engine** = code tier (composes existing κ=1 checkers).
- **Library** = cheap model: fetch the external taxonomy; mine the EVOLUTION_LOG for real failures.
- **Auditor** = a model ≠ generator (Sonnet/Haiku) — names missing classes, tests false-fires.

## 9. THE ONE-LINE TEST OF SUCCESS
**"TRIAGE turns ARMOR's one abstention gate into a named failure-class → detector → mitigation table seeded from
the box's REAL caught failures, runs the κ=1 rows as machine checks and routes the κ<1 rows to the cross-model
panel or abstention, re-flags past failures the human audits caught, and NEVER emits 'safe' — only 'no listed
class fired, coverage = these N classes.'"** Operational honesty, not a new capability.
