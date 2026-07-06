# BOX v5.2 (CANDIDATE) — Cheap Cross-Check Audit: an error-DETECTION layer with abstention

**Status: DESIGN PROPOSAL, point-release-CANDIDATE, NOT a stamped promotion. v2 — substantially REWRITTEN after an
independent Sonnet red-team ruled v1 UNSOUND.** The red-team's decisive catch: v1's core mechanism (per-facet
*decomposition*) was contradicted by the very experiment it cited — round 5 found decomposition was NOT needed and
slightly HURT (holistic Haiku was also 8/8; the decomposed arm added a false positive). v2 keeps only what the
evidence supports. It is an **error-DETECTION (honesty) lever — flag → abstain/escalate, NOT immunity, NOT auto-fix,
NOT raw capability.** Ceiling = weak-dominance / point-release, and even that is OWED an A/B.

## The ONE thing round 5 actually licenses (and the one it refutes)
- **LICENSES:** on **surface-checkable** outputs, a **cheap weak model audits as reliably as a strong one** —
  Haiku *holistic* 8/8 detection, 0 false alarms = Sonnet 8/8 (`round5_oversight/RESULT.md`). The verify ≪ generate
  asymmetry. This is a confirmation of owned doctrine (B1/C8: a non-generator model checks the output), now with a
  cost angle: **the checker can be the CHEAP tier.**
- **REFUTES:** that *decomposition* is the active ingredient. Holistic weak checking already maxed out; per-facet
  decomposition added a false positive (a Haiku slip on one of ~30 facets). **So decomposition is NOT the default.**

## The HARD LIMITS (non-waivable)
1. **C20/C21/C22 NESTING WALL.** A weak checker only works on **locally-checkable** errors; if catching the error
   needs the generating capability, the weak checker's errors nest inside the generator's (participation ratio 1.0)
   and it confidently passes the error. → weak audit is for SURFACE-checkable outputs ONLY.
2. **AGREEMENT = RISK, not safety (C2/C8/C20).** Correlated agreement is worthless; gate on participation ratio.
3. **FLAG, DON'T FIX.** Feedback-repair is weak-model-only (round 4). The layer flags/abstains/escalates; no auto-fix.

---

## THE CORE (simplified per the audit — the evidence-backed minimum)
**For any LOAD-BEARING output, before it leaves the box, run a CHEAP cross-model HOLISTIC audit by a non-generator,
plus the two already-owned exact routes. Decomposition is reserved for *localizing* a flag, not as the default checker.**

```
1. PRODUCE         generator emits output (per v4 ladder).
2. TRIAGE the output (cheap, conservative — see "Triage honesty" below):
     has EXACT checks?   (math/code/invariant)        → MACHINE EXECUTOR ($0)            [v3 armor, owned]
     rests on FACTS?     (external, groundable)        → GROUNDING FETCHER (fetch, don't vote) [C22, owned]
     SURFACE-checkable?  (errors detectable locally)   → CHEAP HOLISTIC AUDIT: 1–3 Haiku, ≠ generator  [the round-5 win]
     NESTED / uncertain? (needs deep reasoning to spot)→ FRONTIER checker ≠ generator; if none available → ABSTAIN/flag
3. GUARD AGREEMENT  if you lean on "the panel agreed", first compute participation ratio on a fresh seeded error-bank;
                    ≈1.0 (nested) → discard the agreement, escalate or abstain.
4. AGGREGATE        LIBERAL VETO with a PRECISION FLOOR (see FP control): a grounded flag holds; a bare "fine" never
                    overrides. 
5. DECIDE           clean → EMIT with verdicts attached; any flag → FLAG that part + ABSTAIN/ESCALATE. Never auto-fix.
6. SELF-AUDIT       a model ≠ the orchestrator red-teams the TRIAGE on the high-stakes outputs (not a token sample).
```

### What changed from v1 (audit corrections, all folded in)
- **DROPPED "decompose every output into n facets + 3 Haiku each" as the default** — round 5 refutes it and the
  per-facet false-positives compound. Default SURFACE check is now a **holistic** cheap audit (1–3 Haiku), which
  round 5 showed is already 100% on surface errors. Decomposition is used only *after* a holistic flag fires, to
  localize WHICH part is wrong (or for FACT extraction) — never as the blanket checker.
- **RENAMED** from "error-immunity" to "error-DETECTION with abstention." There is no guarantee; it's a probabilistic
  flag conditional on correct triage, for naturally-surface-checkable errors.
- **TRIAGE demoted from a safety *guarantee* to a conservative *heuristic*** (see below).
- **FP control added** (see below).
- **Fable-inactive degradation flagged** (see below).
- **Decomposer/coverage check added** for the only place decomposition is still used (localization).

## Triage honesty (the layer's own biggest error surface — stated plainly)
The auditor's sharpest point: *classifying "can a weak model check this?" may itself be a nested problem*, and a
NESTED facet mislabeled SURFACE gets confidently passed by the cheap audit. We do NOT claim the triage is reliable.
Mitigations, conservative by construction:
- **Default to ESCALATE/ABSTAIN on any uncertainty.** Triage only routes to the cheap audit when the output is
  *clearly* surface-checkable (exact-checkable subparts, simple factual/constraint claims). Anything ambiguous →
  frontier or abstain. False *escalation* costs money; false *de-escalation* (NESTED→SURFACE) costs a missed error,
  so the asymmetry is deliberately tuned to over-escalate.
- **The triage is audited on ALL high-stakes outputs by a non-generator** (step 6), not sampled — systematic
  mis-triage is the failure mode, and sampling underdetects systematic errors.
- **Honest residual:** for genuinely hard-reasoning domains, telling SURFACE from NESTED needs frontier-tier
  judgment. With **Fable INACTIVE**, that tier degrades to Opus — i.e. Opus would be triaging/auditing Opus's own
  output, which violates "never Opus-audits-Opus." **In the current configuration, NESTED/hard-reasoning outputs
  must ABSTAIN or wait for Fable, not be cheaply audited.** This is a real, current limitation, not hand-waved.

## False-positive control (the compounding-FP problem, quantified)
Per-facet FP rate from round 5's decomposed arm ≈ 12%; under liberal veto over n facets, P(≥1 false flag) ≈
1−(1−0.12)ⁿ → ~72% at n=10. **This is why decomposition is NOT the default.** A *holistic* cheap audit is a single
judgment (round 5: 0/8 FP for Haiku holistic), so it does not compound. Rules: (a) default holistic (n=1); (b) if
decomposition is used to localize, require a per-facet precision floor and cap n, else the layer is net-harmful
(flags correct outputs more than it catches real ones); (c) report the measured FP rate every run.

## Model combinations (what to use where)
- **Generator ≠ every checker.** Always (B1/C8).
- **SURFACE-checkable load-bearing output → a CHEAP holistic audit (1–3 Haiku, ≠ generator).** The round-5 win:
  weak ≈ strong at ~1/10 the cost. *Use the cheap tier here on purpose — a frontier audit is wasted money.*
- **NESTED → ONE frontier model ≠ generator; if unavailable (Fable down → would be Opus-audits-Opus) → ABSTAIN.**
- **FACTS → retrieval, not a panel** (C22). **EXACT → the machine, no model** (v3).
- **The layer itself → audited by a model ≠ the orchestrator.** (This rail caught my round-4 gate bug AND just
  caught this design's over-engineering.)

## Where it plugs into v5.1
Highest value first: (1) **pre-emission cheap holistic audit on any load-bearing artifact** (HELMET/Integrity final
step) — biggest blast radius, evidence-backed, cheap; (2) **executable/fact routing** is already owned (v3 + retrieval)
— keep; (3) the surface/nested triage + participation-guard are the *new, unproven* pieces → ship them OFF by default,
behind the A/B.

## Honest scope + what's OWED before any v5.2 stamp
- **It's a cheap-cross-model-audit point-release at most** — mostly cashing in round 5's confirmation of owned
  doctrine (use the *cheap* non-generator tier on surface-checkable outputs). The genuinely new pieces (surface/nested
  triage; participation-guard-as-standing-gate) are **unvalidated** and the audit rates the triage as the weak link.
- **OWED:** (a) a non-circular A/B — does the cheap-holistic-audit catch ≥ as many *naturally-occurring* confident
  errors as the current frontier audit, at lower cost, on ≥2 arenas? (round 5 used INJECTED errors — the bigger
  question, *do strong models confidently err on surface-checkable real tasks often enough to matter*, is unanswered
  and may be NO); (b) measured FP rate; (c) external prior-art grounding (debate / process-verification /
  weak-to-strong — survey agent was rate-limited; owed); (d) a triage-accuracy benchmark (SURFACE vs NESTED labels)
  before the triage is trusted at all.
- **No ratchet move claimed.** Capability ratchet stays OPEN at v3. This is honesty-axis.
