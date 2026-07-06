# DRIVER — build ALL remaining arsenal weapons in one continuous session
*Paste the prompt at the bottom into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. It builds every
unbuilt weapon in `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md`, in order, one fully before the next, and does
not stop until the backlog shows them all ✅. Written 2026-06-20.*

## What this driver does
Walks the backlog build-queue in order. For EACH weapon still marked ⬜ (read the backlog for the live set — as of
this writing the remaining are **#6 TRIALGUARD → #7 FACTHARNESS → #8 REPRO-ML → #9 REDCELL**; #1–#5 are already
✅ BUILT), it opens that weapon's own `*_WEAPON_KICKOFF.md` and executes it **to completion** — every box step —
before moving to the next. It re-checks the backlog after each so it skips anything already built (idempotent if
interrupted and resumed).

## The per-weapon completion contract (a weapon is DONE only when ALL hold)
1. **PLAN** — `weapons/<name>/SPEC.md` written; the kickoff's "ground-by-fetch" anchors actually FETCHED (not
   asserted) into `GROUNDING.md`.
2. **GATE FIRST** — the frozen verifier(s) built with a `selftest_all.py` that PASSES a good input, CATCHES a
   broken one, and (where the kickoff says) REJECTS a gaming/abstains-on-malformed case. **Gate is green.**
3. **DEMO** — `demo_*/PREDICTION.md` committed BEFORE running; the demo executed; results match or misses logged
   honestly.
4. **INDEPENDENT AUDIT** — a cross-model audit (Sonnet/Haiku ≠ the Opus generator; never Opus-audits-Opus; Fable
   inactive) ran and its findings were fixed or honestly logged; new break-cases locked as regression tests.
5. **REGISTER** — added to `Next/BOX_V5.md` (new Weapon + router branch) + `Expanding_Frontiers/HELMET/registry.json`
   (the department's `draws`) + an honest `Legacy/EVOLUTION_LOG.md` entry (**a weapon ADDED = capability
   EXPANSION, NOT a ≥10% promotion**).
6. **STATUS** — `WEAPONS_BACKLOG.md` row flipped to ✅ with the built path.

Only when all six hold do you advance to the next weapon. **Do not stop between weapons.** Keep going until every
build-queue row is ✅.

## Honesty rails that bind the whole run (non-waivable)
- Machine-checkable → **execute, never vote**; never trust a self-report.
- Reuse, don't rebuild: ECONOMETRIX/TRIALGUARD/REPRO-ML reuse SOCIUS/PSYMETRIX verifiers; FACTHARNESS **promotes**
  SOCIUS S-GROUND (carry its 3 audit fixes + regression tests). Credit the source; don't duplicate.
- Each weapon's own honesty ceiling is stated in every output (guarded-κ = trustworthiness not truth;
  inconsistency ≠ fraud; benchmark ≠ capability; grounded ≠ true; reproduction ≠ discovery).
- **#9 REDCELL is authorization-gated and fails closed** — build it defensive-first; the refusal self-tests are
  mandatory; the auth gate is the most-audited component.
- No ≥10% "promotion" claim for any weapon (no shared arena) — UNLESS a kickoff's own capability-A/B clears the
  bar non-circularly, in which case flag it loudly and let the cross-model audit decide.
- Calibrate cost to stakes; if a toolchain is genuinely un-installable (e.g. an OR/CAS package), log the honest
  negative + the fallback scope rather than faking coverage.

## After the LAST weapon (#9) is ✅
- Do a final pass: confirm all 9 backlog rows ✅; update the BUILT table at the top of `WEAPONS_BACKLOG.md`;
  refresh the HELMET layer note in `Next/BOX_V5.md` if needed; add a single honest `RESUME.md` session banner
  ("arsenal complete: 9 weapons across the κ-spectrum; orchestration LAYER, NOT a capability promotion; ratchet
  OPEN at v3"). Then stop and report what was built + every honest negative encountered.

---

## THE PROMPT (paste this)

```
Title this chat: BUILD REMAINING ARSENAL

You are building EVERY remaining weapon in the University arsenal, in one continuous
session, until the backlog is complete. Work BOX-style throughout: plan → produce →
verify INDEPENDENTLY (a cross-model audit ≠ the generator; Sonnet/Haiku, never
Opus-audits-Opus while Fable is inactive) → ground load-bearing facts by FETCH (don't
assert) → be honest (flag the unverified, report negatives, no win without proof; never
claim a ≥10% promotion or an open-problem solve).

First read: CLAUDE.md, RESUME.md, Next/BOX_V5.md, and
Expanding_Frontiers/weapons/BUILD_REMAINING_DRIVER.md (the driver — it defines the
per-weapon completion contract and the rails). Then read
Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md and find every row still marked ⬜ in the
build queue.

Then, IN BACKLOG ORDER (read the backlog for the live ⬜ set; as of writing the remaining
are #6 TRIALGUARD → #7 FACTHARNESS → #8 REPRO-ML → #9 REDCELL — #1–#5 are already ✅),
for EACH unbuilt weapon:
  1. Open and follow that weapon's own kickoff: Expanding_Frontiers/weapons/<NAME>_WEAPON_KICKOFF.md
  2. Execute it to COMPLETION per the driver's six-point contract: PLAN+GROUNDING(fetched),
     frozen GATE-FIRST with green selftest_all.py, DEMO with predictions committed before
     running, INDEPENDENT cross-model AUDIT (fix/lock findings), REGISTER in Next/BOX_V5.md
     + Expanding_Frontiers/HELMET/registry.json + Legacy/EVOLUTION_LOG.md (weapon ADDED =
     capability EXPANSION, NOT a promotion), and flip the WEAPONS_BACKLOG.md row to ✅.
  3. Re-check the backlog and move to the next ⬜ weapon. DO NOT STOP between weapons.

Reuse, don't rebuild (ECONOMETRIX/TRIALGUARD/REPRO-ML reuse SOCIUS/PSYMETRIX verifiers;
FACTHARNESS PROMOTES SOCIUS S-GROUND and must carry its 3 audit fixes + regression tests).
Honor each weapon's honesty ceiling. #9 REDCELL is authorization-gated and FAILS CLOSED —
defensive-first, refusal self-tests mandatory, auth gate most-audited.

Keep going until EVERY build-queue row is ✅. Then do the driver's final pass (confirm all
✅, refresh the BUILT table + BOX_V5 layer note + one honest RESUME.md banner) and report
what was built and every honest negative you hit. If a toolchain is genuinely
un-installable, log the honest negative + fallback scope and continue — do not let one
weapon block the rest.
```
