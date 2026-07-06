# STATE — where the program stands today

*Carried forward from the (now-archived) `RESUME.md`. This is the single current-truth file; the full
historical state record is in `MARK_0/02_ladder_history/RESUME.md`.*

## The headline
- **Suit version:** **v5.2** — Armor + Weapons + Helmet + the v5.1 (selective-context decomposition) and v5.2
  (cheap cross-check audit) efficiency/honesty options.
- **Capability ratchet:** **OPEN at v3.** Everything added since (v4 ladder, v5 weapons, the helmet, v5.1/v5.2)
  is **capability EXPANSION** (new task classes) or **efficiency/honesty** — **none is a ≥10% capability
  promotion.** Stated plainly and non-negotiably.
- **Products:** `Artifacts/{history-app, trading, math}` all at **v1.0**, each with a non-gameable self-audit
  baked in (the v5.2 rail), scorers non-regressed, cross-model audited.
- **Phase 1 (build the suit): COMPLETE.** Phase 2 (sharpen & expand): **ON HOLD** (operator decision).

## The honest open bet (the only thing that would move the ratchet)
A genuine **≥10% capability gain over the best single model** is **infra-gated**. Every cheap path tried hit the
same wall: strong models rarely confidently err on cleanly-checkable tasks, so no cheap lever beats them. A real
gain needs a **SWE-bench-scale, contamination-free arena** (non-memorized hard tasks + rich execution feedback)
**and Fable 5 active**. Until that infra exists, the ratchet stays at v3 — honestly.

## What's paused (Phase 2 — see `backlog/`)
- *(All three original Phase-2 threads are now DONE — see below. Remaining work is follow-ups, not paused threads:
  a HELD-OUT routing set for the helmet keystone, the κ-not-prelabeled A/B/C re-run, and the optional CRUCIBLE-v2
  / ENCLOSE-tightening items.)*

## What's DONE (Phase 2)
- ✅ **CRUCIBLE hardening run (2026-06-20).** Adversarially probed all 11 κ>0 gates. **Found + patched 4
  confirmed gate defects** (factharness ×2, optima ×2, symbolica, socius — incl. 2+ false-ACCEPTs = real
  soundness holes), each frozen as a permanent regression self-test, cross-model audited, orchestrator-re-run
  green (5/5 selftests). **7 gates SURVIVED-to-budget** (adversarially-tested, NOT "sound"); 1 declined
  (econometrix, guarded-κ). Report: `../ARSENAL/weapons/crucible/CRUCIBLE_RUN_REPORT.md`. **Hardening/expansion,
  NOT a ≥10% promotion — ratchet stays OPEN at v3.** Named residual gaps: metamorphic-only weapons (optima,
  proofsmith, reproml, symbolica + socius multiverse) had **no false-accept hunt**; proofsmith's **Lean kernel
  path was never exercised**. Closing those is the natural CRUCIBLE-v2 follow-up (needs Lean + foreign oracles).
- ✅ **ENCLOSE built (WEAPON 13, backlog #10, 2026-06-20).** The certified-numerics weapon — a **containment
  PROOF** (interval arithmetic with outward rounding + Krawczyk existence-uniqueness), categorically sharper
  than SYMBOLICA's multi-method agreement. Built **gate-first on `mpmath.iv` with NO new dependency** (infra
  settled by machine: iv arithmetic is genuinely outward-rounded; `iv.quad` broken → quadrature built on iv).
  Verifies definite integrals (incl. non-elementary erf), Krawczyk roots, recomputable constants; ACCEPTs true
  enclosures, **REJECTs fabricated ones**, ABSTAINs honestly. `selftest_all.py` 24/24 green (incl. a soundness
  invariant); `demos/` 9/9 predictions (with an honest miss recorded). **Cross-model Sonnet audit: SOUND** (no
  false-accept across 17 attack categories; 4 hardening findings fixed). Home: `../ARSENAL/weapons/enclose/`.
  EVOLUTION_LOG C49. **Capability EXPANSION, NOT a ≥10% promotion — ratchet stays OPEN at v3.** This completes
  the `(b)/(c)` handoff; only the HELMET keystone remains in Phase 2.
- ✅ **HELMET keystone tested (2026-06-21).** The Provost's κ-routing on **unlabeled** inputs — the one test that
  decides if the helmet beats plain armor — was the #1 untested gap. Ran a **24-problem committed-key benchmark**
  (cross-model-audited: 22/24 gold defensible, 0 wrong) at 2 tiers. **Baseline routing accuracy: Sonnet 88% /
  Haiku 79%** (95% / 86% on unambiguous items); the load-bearing decisions (weapon-vs-abstain, C14 proxy-trap 4/4,
  anti-theater 2/2, open-problem rails) robust at both tiers. Dominant failure = the red-team's predicted weak
  spot (over-tagging a **factual lookup** as κ=1 instead of κ=0-groundable). **A principled fix** (doctrine
  "lookup ≠ κ=1" + route() proxy-abstain hardening, both in `provost.py`, selftest green) lifted Haiku to 100%
  in-sample **— and GENERALIZES: on a FRESH held-out 24-problem set (cross-model-audited), with the FROZEN
  doctrine, BOTH Sonnet and Haiku scored 100% (22/22 unambiguous).** Verdict: the keystone gap is **substantially
  CLOSED on classification** — routing on unlabeled inputs is accurate and the fix is not overfit (caveats:
  n=24/author-correlated; routing accuracy ≠ end-to-end output quality). `../ARSENAL/HELMET/validation/keystone/RESULTS.md`.
  **Diagnostic + process fix, NOT a ≥10% promotion — ratchet stays OPEN at v3; the helmet is "organized, not smarter."**
- ✅ **HELMET end-to-end A/B (2026-06-21)** — the real "does the helmet beat plain armor on OUTPUT" test. HELMET
  (route→execute/abstain) vs FLAT (answer directly), same model+tools, 2 arenas × 2 tiers, machine + cross-model-judge
  scored (`../ARSENAL/HELMET/validation/ab/AB_RESULTS.md`). **CAPABILITY/correctness Δ=0 both tiers** (checkable
  arena saturated — the tool-enabled FLAT arm executed itself, 10/10). **HONESTY/abstention: HELMET 0/10 over-commit
  vs FLAT 2/10 (Haiku) / 3/10 (Sonnet)** — prevents fabricated certainty on 20–30% of unverifiable questions,
  persisting at the strong tier. **First end-to-end confirmation of "honesty, not capability"; NOT a ≥10% promotion
  (correctness unchanged); ratchet OPEN at v3.** Caveats: n=10/arena (low power); 0-over-commit partly by-construction.

## Environment caveats (current)
- **Fable 5 is INACTIVE** → rerouted to Opus 4.8. This degrades the genuinely-un-executable hard-reasoning
  slice; lean harder on execute-and-run, and never use Opus to audit Opus (use Sonnet/Haiku). See `../LADDER.md`.

## Latest milestones
- **HELMET keystone tested (2026-06-21)** — Provost κ-routing on unlabeled inputs measured (Sonnet 88% / Haiku
  79% baseline; principled fix → Haiku 100% in-sample). The helmet's core mechanism is no longer unproven. See
  `## What's DONE` above.
- **ENCLOSE built (2026-06-20)** — WEAPON 13, the certified-numerics weapon (containment proof). Arsenal now
  **13 weapons + 8 kit**. See `## What's DONE` above.
- **CRUCIBLE hardening run (2026-06-20)** — the arsenal's verifier gates adversarially red-teamed; 4 confirmed
  defects found + patched + frozen as regressions; gates' κ=1 labels upgraded ASSERTED → ADVERSARIALLY-TESTED
  (to budget) where they survived. See `## What's DONE` above.
- v5.2 "Cheap Cross-Check Audit" stamped as a point release (efficiency/honesty, supported-not-fully-proven).
- All three products bumped v0.x → **v1.0**.
- The whole program reorganized into **MARK_0** (the primitive-era archive) and **MARK_1** (this active suit),
  with a one-command `/mark1` activation. Move map: `MARK_0/MOVE_LOG.md`.
