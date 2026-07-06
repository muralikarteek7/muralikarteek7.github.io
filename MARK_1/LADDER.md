# MODEL LADDER — the right model for each job (Mark 1)

The ladder takes each model's best while keeping cost in check. It is evidence-based: on hard arithmetic and
multi-step reasoning, executing beats guessing for every tier, and the gap between models only matters on the
genuinely un-executable slice.

| The task | What the suit does |
|---|---|
| Anything machine-checkable (math, data, code output, invariants) | **Execute** — write code and run it. No model needed. ~$0, and right. |
| Routine generation (standard code, boilerplate text) | **Haiku** — cheap, sufficient. |
| Code (any complexity) | **Any tier** — code is a ceiling task; the gate is the test suite, not the model. |
| Hard reasoning that *can* be made runnable | **Turn it into a script and run it** (model-agnostic, ~free) — this is where most hard reasoning should go. |
| Hard reasoning that genuinely **cannot** be executed | **Opus 4.8**, escalate to **Fable 5** when straining. |
| Novel construction (a new machine-verified object) | **Frontier model + the verifier gate** — never trust the producer's self-report. |
| Audit / verification of a result | **A model ≠ the generator.** Never let a model audit its own output. |

## Cost discipline
The un-executable hard-reasoning residue is small, so the expensive tier is spent only where it pays.
Most tasks resolve at "execute" or "Haiku." Calibrate to stakes: a trivial task gets a trivial response.

## ⚠️ Temporary fallback — Fable 5 is INACTIVE
Reroute every `claude-fable-5` request → **Opus 4.8** for now (Agent spawns + `/model` recommendations).
This degrades the genuinely-un-executable hard-reasoning slice (Opus is unreliable there), so:
1. **Lean even harder on "make it executable and run it"** (model-agnostic, unaffected by the outage).
2. For truly un-executable hard reasoning, Opus is the only option but is **unreliable** — flag low confidence
   explicitly; do not present it as Fable-grade.
3. Where Fable was the cross-model auditor (audit ≠ generator), use **Sonnet or Haiku** — **never Opus-audits-Opus.**
**Revert this section when Fable 5 is active again.**

> Orchestrator default = **Opus 4.8** (`claude-opus-4-8`). Model IDs: Fable 5 `claude-fable-5`, Opus 4.8
> `claude-opus-4-8`, Sonnet 4.6 `claude-sonnet-4-6`, Haiku 4.5 `claude-haiku-4-5`.
