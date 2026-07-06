# TRIAGE — the ARMOR failure-class → detector → mitigation rail

*Kit piece #4 / gap G2. Built 2026-06-20, BOX-style, gate-FIRST. **ARMOR, not a weapon.***

## What it is (one line)
TRIAGE turns ARMOR's single, undifferentiated abstention gate ("not confident → abstain") into a
**named decision table**: *this TYPE of failure gets THIS detector and THIS mitigation* — seeded from
the box's REAL caught failures, running the κ=1 rows as machine checks and routing the κ<1 rows to the
cross-model panel or abstention, and it **NEVER emits "safe"** — only "no listed class fired, coverage =
these N classes."

## What it is NOT (non-waivable)
- ❌ a weapon — it has **no exact verifier** of "is this output failing?" (κ=0 in general).
- ❌ a guarantee — a taxonomy covers KNOWN classes; **novel ones escape** (`uncovered_novel_classes` is
  always `True`, hard-coded and self-test-locked).
- ❌ smarter output — it makes abstention *specific and auditable*, not the model better.
- ❌ a substitute for the cross-model audit — it ROUTES to it for the judgment (κ<1) classes.

## Files
- `triage_check.py` — the 8-row checklist + the entry point `triage_check(record)` → TRIAGE REPORT; the
  malformed-record guard (`TriageAbstain`); the reconstructed-real-failure builders; `_selftest`.
- `triage_router.py` — routes each fired class: κ=1 → **machine** track, κ<1 → **panel** track; a
  degraded "machine" row (frozen checker absent) is downgraded to panel; `_selftest`.
- `triage_retroactive.py` — the NON-WAIVABLE retroactive re-flag of ≥3 REAL past failures; `_selftest`.
- `selftest_all.py` — runs all three `_selftest`s; **exits non-zero on any failure**.
- `SPEC.md` — the decision table, each row traced; the report schema; the "no all-clear" rule.
- `GROUNDING.md` — the FETCHED external taxonomies (NIST AI RMF 1.0, OWASP LLM Top-10 v1.1, Huang 2023
  hallucination survey) reconciled against the home-grown table + what the box's history adds.
- `demo_retroactive/` — `PREDICTION.md` (committed BEFORE the run), `run_demo.py`, `results.json`,
  `RESULTS.md`.
- `AUDIT.md` — a stub for the independent cross-model auditor (≠ the generator) to fill.

## Run it
```
cd /Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/triage
python3 selftest_all.py            # the gate — must exit 0 before anything else counts
python3 demo_retroactive/run_demo.py   # the demo — scores against committed predictions
python3 triage_check.py <record.json>  # triage one output record
python3 triage_router.py <record.json> # route one output record
```

## The 8 rows (see SPEC.md for the full traced table)
overconfidence (κ<1) · **fabrication (κ=1 via FACTHARNESS)** · specification-gaming (κ=1 with a
*recognized* independent-oracle verdict, else κ<1 degraded) · **circular-measurement (κ=1 structural)** ·
**numeric/branch-cut/convergence (κ=1)** · distribution-shift (κ<1) · shared-blind-spot (κ<1) ·
**crash/silent-pass on malformed input (κ=1 on "errored loudly?" WHEN a probe callable is supplied; κ<1
null-op when none is)**.

## Composition + honest degradation
- **Composes** the existing κ=1 fabrication checker **FACTHARNESS** (`../factharness/`) — no new
  fabrication solver. Verified importable by the gate (`composes FACTHARNESS: True`).
- **CRUCIBLE** (`../crucible/`, the gate-testing meta-weapon) is present, but presence-on-disk does NOT
  auto-supply an *answer-oracle* for an arbitrary task, so spec-gaming reaches **κ=1 only when the record
  supplies a RECOGNIZED independent-oracle verdict** (a non-empty string matching a known agree/disagree
  token — garbage like `''`/`0`/`False`/`"maybe"` is NOT a usable oracle and stays κ<1); otherwise it runs
  TRIAGE's own **κ<1** structural check and labels it `degraded` (it must not launder a judgment into a
  certification).
- If FACTHARNESS were unavailable, the fabrication row degrades to κ<1 (`degraded: True`) honestly.

## The honest ceiling (carried in every report)
- A taxonomy covers **KNOWN classes only** — novel/unknown failures escape.
- **No "safe"** — absence of a flag is "no listed class fired", never a safety proof.
- κ=1 rows are real machine checks; κ<1 rows are routed judgments, not certifications.
- It is **ARMOR**, not a weapon — **no capability claim, no ratchet movement.** This operationalizes the
  abstention gate; it does not raise the model's ceiling.

## Status
- Gate: **green** (`selftest_all.py` exits 0) — see the structured run output.
- Demo: **8/8** against committed predictions (3/3 retroactive re-flags of C39/C41/C38 + 4 fresh
  positives + 1 clean control). See `demo_retroactive/RESULTS.md` for the honest reconciliation (case 4
  fired one more row than the minimal prediction named — recorded, not buried).
- Independent cross-model audit (≠ the generator): **DONE** — a Sonnet auditor ran adversarial attacks and
  found 5 real defects; **all 5 fixed** with permanent regression self-tests (in `triage_check._selftest`):
  - **(HIGH, false-accept) FIXED** — crash/silent-pass evasion via `{'ok': 1}` (and truthy ints/lists, bare
    truthy/ambiguous/None returns): the silent-pass test is now **value-based** (`_is_silent_pass`), not the
    old `out.get('ok') is True` identity check, so a degenerate-input return is a silent-pass unless the
    callable raised or returned an EXPLICIT reject/falsey verdict.
  - **(MEDIUM, κ mislabel) FIXED** — crash/silent-pass with NO probe supplied now returns **κ<1,
    `degraded: True`** (a null-op, not a verified-clean κ=1).
  - **(MEDIUM, κ mislabel) FIXED** — spec-gaming oracle laundering: a usable oracle must be a **recognized
    non-empty string verdict**; garbage (`''`/`0`/`False`/`"maybe"`/`"yes-ish"`/…) stays **κ<1 `degraded`**.
  - **(LOW) FIXED** — spec-gaming disagree matching broadened to NL variants (`"wrong answer"`, `"failed"`,
    `"error"`, `"false-positive"`, …) via leading-word + exact-token match (no loose hyphen-prefix laundering).
  - **(LOW) FIXED** — overconfidence `unverified_threshold` is **clamped ≤ default 1** so a caller-set
    `unverified_threshold=9999` can no longer suppress the row.
- Registration (`Next/BOX_V5.md`, `HELMET/registry.json`, `EVOLUTION_LOG.md`): handled separately — NOT
  done by this build (per the build charter, no shared files edited).
