# EQUIP — the pre-battle loadout phase

**The gap this closes:** `/mark1` loads the whole *catalog* (12 weapons + 8 kit, "ready / on standby"),
but nothing chose a **loadout**. Weapons were drawn reactively, mid-task, by the κ-gate — one at a time,
on contact. There was no deliberate *"read the battle → pick a style → carry only that"* ritual.

**EQUIP adds that ritual.** It runs **once, before** the κ-gate, narrows the rack to a curated loadout,
and declares it out loud. The κ-gate then draws only from the equipped set.

```
"put on Mark 1"        EQUIP  (once, pre-battle)        κ-gate (per task)        fight
─────────────────  →  ───────────────────────────  →  ──────────────────  →  ──────────
load the CATALOG       read battle → pick STYLE        draw a weapon FROM      verify ·
(all 12 + 8 + helmet)  → equip that loadout            the equipped loadout    reproduce ·
                       → declare it                    (or armor-only)         or abstain
```

## The 8 styles (+ WARLORD)
Each style = a curated subset of the real arsenal + a mode + a posture. Full data: `LOADOUTS.json`.

| Style | When | Weapons equipped | Mode |
|---|---|---|---|
| **SAGE** | judgment / advice / synthesis — *no exact verifier* | FACTHARNESS (grounding only) | the κ=0 path |
| **SCHOLAR** | research / literature survey | FACTHARNESS · REPRO-ML | `mark1research` |
| **SCRIBE** | write an article / paper / chapter | FACTHARNESS | `mark1article` |
| **ANALYST** | data exploration / EDA / descriptive | REPRO-ML · FACTHARNESS | explore+run |
| **ARCHITECT** | design / build / code | CODEFORGE · OPTIMA · REPRO-ML | build+run |
| **PROVER** | math / proof / exact / optimize | PROOFSMITH · SYMBOLICA · FRONTIER · OPTIMA · ENCLOSE | search-open / fetch-known |
| **AUDITOR** | reproduce / forensics / stress a claim | SOCIUS · PSYMETRIX · TRIALGUARD · ECONOMETRIX · REPRO-ML · FACTHARNESS | reproduce + multiverse |
| **SENTINEL** | authorized, defensive-first security | REDCELL | defensive-first |
| **WARLORD** | a multi-front battle (≥2 styles tie) | the **union** (capped at top-3) + **BOOTSTRAP** | convene the **Helmet** |

**The under-suit is always equipped, never chosen:** ARMOR · MODEL LADDER · SHOES · VAULT · TRIAGE.
**Coverage (audit-locked):** every weapon (13, incl. ENCLOSE) and kit piece (8, incl. BOOTSTRAP-via-WARLORD)
is reachable by some style — enforced by `test_equip.py::coverage`. BOOTSTRAP is the *router-failure* meta-tool:
when a task has a verifier but no existing weapon fits, WARLORD scaffolds one rather than forcing a wrong weapon.

## How it decides (deterministic, unit-testable — like `router.py`)
1. Score every style by word-boundary trigger matches against the battle text (`equip.py:_score_style`).
2. Top score below `MIN_CONFIDENCE` → **SAGE** (never force a weapon onto a judgment task).
3. ≥2 styles within `AMBIGUITY_BAND` of the top → **WARLORD** (load the union, convene the Helmet).
4. Otherwise → the single dominant style.

It is a **deterministic classifier, not an LLM** — so it is testable and honest about its limits
(keyword-based, no stemming; retune the lexicon in `LOADOUTS.json`, don't fudge the test).

## Honest status
- **What it is:** an orchestration/efficiency layer — a deliberate loadout step + a declared style.
  It narrows the κ-gate's working set and forces an upfront commitment to a posture.
- **What it is NOT:** a capability promotion. No new task class is solved that armor+weapons couldn't.
  Ratchet stays **OPEN at v3**. EQUIP makes the suit *choose* better, not *think* harder.
- **Verified:** `test_equip.py` 18/18 + coverage (machine check). The classifier is keyword-based and will
  mis-style adversarial/sparse phrasings — that's a known limit, mitigated by the SAGE and WARLORD
  fallbacks (ambiguity → escalate, not silently guess).

## Files
- `equip.py` — the selector (`equip(battle_text) -> loadout dict + declaration`). Runnable: `python3 equip.py "your task"`.
- `LOADOUTS.json` — the editable style registry (retune here).
- `test_equip.py` — 18-case machine check + coverage check.
