# COMPOSEAUTH (G3) — SPEC

*The compositional-authorization rail: a running blast-radius budget over GLOVES' allowed
actions, so a sequence of individually-safe, individually-authorized steps cannot silently
compose into a catastrophe. Item #6 / gap G3 of the KIT-EXPANSION plan. Completes GLOVES:
GLOVES gates each ACTION; G3 gates the SEQUENCE. Built BOX-style, gate-first. Written 2026-06-20.*

## 1. WHAT G3 IS / IS NOT

**IS** a **stateful budget accumulator** over a session's actuation stream. Each
GLOVES-allowed action adds its blast-radius to running counters (per resource class).
When a counter crosses a committed threshold, G3 **escalates the tier** of the NEXT
action (→ STEP-UP) or **HALTs + escalates to a human** — even though each step alone was fine.

**The κ=1 core:** the accumulation (Σ per class) + the threshold comparison is exact
arithmetic. *A committed sum crossing a committed threshold is a machine fact* — like the
Registrar's token budget, like OPTIMA's objective recompute.

**IS NOT:**
- ❌ a judge of whether the *composition is malicious* (κ=0 intent → it ESCALATEs/HALTs, it
  does NOT accuse).
- ❌ able to set the "right" threshold (the threshold is a committed **policy** input, not
  derivable — stated, not invented).
- ❌ a replacement for GLOVES (it needs GLOVES' per-action classification).
- ❌ complete against an attacker who spreads effect across resource classes G3 doesn't count
  — *you can only budget what you enumerate.* Effect outside the enumerated classes is
  reported **UNCOVERED**, never silently "within budget."

## 2. BUDGET DIMENSIONS (each a committed counter + threshold — `composeauth_policy.py`)

| dimension | counter | committed STEP_UP | committed HALT |
|---|---|---|---|
| financial | Σ $ committed this session | > $100 | > $1000 |
| data_mutation | # records created/updated/deleted | > 50 | > 500 |
| broadcast | # external recipients contacted | > 10 | > 100 |
| destruction | # irreversible deletes / overwrites | > 5 | > 25 |
| external_calls | # external API calls (denial-of-wallet guard) | > 100 | > 1000 |
| blast-radius SCORE | Σ (weight × class count) — weights are POLICY | — | > 2000 |

**All thresholds AND all score weights are COMMITTED POLICY INPUTS** (human-owned risk
appetite), not derived truth (audit Finding 3). Every G3 verdict carries `policy_banner`
saying so. The EXAMPLE values above are the kit's defaults; a deployment owns its own.

## 3. ARCHITECTURE (gate-first; the arithmetic, not a model, halts)

```
GLOVES allowed action ──► GLOVES (mock) ledger entry
   {tool_id, params, tier, authorization, dry_run_hash, blast_units, ts,
    other_effects}   ← other_effects = the catch-all (audit Finding 2)
        │
        ▼
  extract_effects()  (POLICY effect-extractor, mock_gloves_ledger.py)
        │  ├─► per-class deltas  {financial, data_mutation, broadcast, destruction, external_calls}
        │  └─► UNCOVERED  {class: amount}  for blast outside the enumerated classes
        ▼
  BudgetStore.add()  (κ=1: ENFORCED-monotonic per-class Σ — negative deltas REJECTED;
                      PERSISTED atomically → crash-resume safe)
        ▼
  _evaluate()  (κ=1: running total  >  committed threshold ?)   +  blast_score
        ▼
  decide() ──► { OK | ESCALATE(next→STEP-UP) | HALT(+human) , tripped, uncovered,
                 counters, blast_score, reason, policy_banner, tracked_classes }
```

- **`mock_gloves_ledger.py`** — the MOCK GLOVES feed (kickoff: build against a mock; do not
  block on GLOVES). Emits ledger entries in GLOVES' exact shape + the `other_effects`
  catch-all. The POLICY effect-extractor maps a known tool → tracked classes; an unknown
  tool / novel blast class → UNCOVERED.
- **`composeauth_policy.py`** — all committed thresholds AND score weights, labeled POLICY.
- **`composeauth_gate.py`** — the FROZEN budget gate: `BudgetStore` (persistent, monotonic,
  crash-resume) + `ComposeAuthGate.decide()`. Fails CLOSED → HALT on any exception.
- **`composeauth_router.py`** — classifies an action: BUDGET (maps to a tracked class) /
  UNCOVERED (blast outside enumerated classes) / ABSTAIN (malformed). Decides routing; the
  frozen gate enforces.
- **`selftest_all.py`** — runs every non-waivable self-test; exits non-zero on any failure.

## 4. THE κ BOUNDARY (honesty)

| concern | κ | handling |
|---|---|---|
| Σ per-class accumulation | κ=1 | exact integer sums, persisted |
| running total > committed threshold | κ=1 | exact comparison; a machine fact |
| effect → resource class (KNOWN tool) | κ=1 *within* the policy table | `EFFECT_EXTRACTOR` |
| effect → resource class (tool population) | κ<1 *across* population | unknown tool → UNCOVERED |
| "is this composition malicious?" | κ=0 (intent) | ESCALATE / HALT — **never accuse** |
| "is this threshold correct?" | n/a (policy) | committed by a human; G3 is silent on it |

## 5. THE FIVE NON-WAIVABLE SELF-TESTS (`composeauth_gate._selftest`, kickoff §3 a–e)

- **(a) SALAMI** — N charges each below the per-action GLOVES trigger ($50) AND below the
  session threshold ($100), whose SUM crosses $100 → the next-action-equivalent is
  **ESCALATE**, not auto-allowed. *The canonical accumulator attack* (audit fix #1).
- **(b) DELETE-BURST** — 26 single-op overwrites (running 26 > committed 25) → **HALT**.
- **(c) BENIGN** — one $5 charge well under all thresholds → **OK** (no false halt).
- **(d) PERSISTENCE** — a simulated session-restart does NOT reset the budget ($80 resumes
  as $80, not $0) → defeats crash-and-resume.
- **(e) UNCOVERED** — effect in a class G3 doesn't track → reported **UNCOVERED**, never
  silent "within budget" (the honesty rail). Both an unknown tool and a known tool carrying
  a novel `other_effects` class are surfaced.
- **(+)** fail-closed on a malformed entry → HALT; every verdict carries the POLICY banner
  and the tracked-classes list.
- **(+) AUDIT REGRESSIONS (independent Sonnet cross-model audit, 2026-06-20)** — permanent
  tests that reproduce each found exploit and assert it is now BLOCKED:
  - **R1 negative-blast false-accept** — a `-$80` charge no longer decrements a `$100`
    budget to `$20`; the negative amount **HALTs** (fail-closed) and the running total is
    unchanged, so a later legit `$20` correctly **ESCALATEs** at the real `$120`. Negative
    amounts are refused at the extractor (`_num`) AND at `BudgetStore.add()` (defence in
    depth) — monotonicity is now **enforced**, not just asserted.
  - **R2 broadcast string-`to` silent undercount** — a string recipient (`'a@x'`, not a
    list) counts as **≥1 recipient**, never silently 0; 15 such emails cross the >10 bar.
  - **R5 NaN/Inf not-fail-closed** — `float('inf')`/`float('nan')` blast amounts **HALT**
    (fail-closed), never silently rounded to a `$0` entry.
  - **R4 corrupt/tampered store init fail-not-closed** — a corrupt store file (or a
    negative/non-numeric persisted counter) no longer raises out of `__init__` (which
    bypassed `decide()`'s fail-closed wrapper). The store is **POISONED** → every
    `decide()` **HALTs** until a human resolves it.

## 6. INFRA LIMITS (stated, not faked)

- **Blocked on GLOVES (real feed)** — G3 needs GLOVES' per-action classification. To stay
  unblocked, this build runs against a **MOCK GLOVES ledger** in GLOVES' exact shape; the
  swap to the real feed is the `gloves_ledger_entry` ↔ real-subscription seam.
- **Tamper-resistance is infra-limited** — same as GLOVES: in a pure-software box the
  persistent store is not guaranteed outside the agent's write scope. True tamper-resistance
  needs fs-perms / a separate process / the harness. The store uses an atomic
  temp-file-rename so a crash leaves the old OR new state, never a torn file — but the
  agent-writability limit stands and is stated. **What G3 *does* defend (audit fix):** a
  corrupt/un-parseable store, or a persisted counter that has been tampered NEGATIVE, does
  NOT silently reset to zero and does NOT crash `__init__` open — it **poisons** the store
  so every `decide()` HALTs. (It cannot *prevent* tampering — that is the infra limit — but
  it refuses to *trust* a store it can detect as corrupt or budget-decreasing.)

## 7. THE ONE-LINE TEST OF SUCCESS

> G3 keeps an EXACT running blast-radius budget over GLOVES' allowed actions, per
> enumerated resource class, and escalates or halts the moment a committed threshold is
> crossed — so a sequence of individually-authorized safe steps cannot silently compose
> into a catastrophe — while reporting which classes it does NOT track, treating the
> thresholds (and weights) as human-owned policy not derived truth, and surviving a
> crash-resume.
