# THE HELMET — "University Mode" (the R&D orchestrator brain)

> The third layer of the v5 box. **ARMOR** keeps output safe; **WEAPONS** let it break through on
> checkable targets; the **HELMET** is the conductor worn *over* both that makes the whole model behave
> like a top research university — given any problem, it triages, convenes the right specialists, runs a
> full R&D lifecycle with independent peer review, and delivers one honest artifact. **It CALLS armor +
> weapons; it does not replace them.**

## The one non-negotiable line (state it in every University-Mode output)
**The Helmet makes the model ORGANIZED, RIGOROUS, COMPREHENSIVE — not smarter.** It cannot exceed the
underlying model's capability ceiling. A university of mediocre minds produces mediocre work; structure is
not extra neurons. "Solves at the highest level" means *researched and resolved to the limit of what is
verifiable/groundable, with that limit stated* — **never** "magically cracks an unsolved problem." On
genuinely open / κ=0 problems it delivers grounded analysis + honest **abstention**, not a fabricated
breakthrough.

Two failure modes it is explicitly engineered against:
1. **Theater / bloat** — convening departments that emit ceremony without verified substance. The
   **Registrar** down-scales to the problem: a one-line question gets **one specialist (DESK)**, not a faculty.
2. **Over-claiming on κ=0** — judgment tasks must end in grounded analysis + honest **abstention**, never
   fabricated certainty. The **Integrity Office** enforces this; the **peer-review model (≠ generator)** checks it.

## The five components
| component | role | file |
|---|---|---|
| **Provost** | triage & routing brain: problem → {domains, κ, task type, known/open, stakes} → departments + scale + lifecycle | [`provost.py`](provost.py) (deterministic, machine-tested) |
| **Department Registry** | problem-type → department → weapon (κ>0) / armor method-cluster (κ=0) / mixed | [`registry.json`](registry.json) |
| **R&D Lifecycle** | `INTAKE → LITERATURE → DESIGN → EXECUTE → PEER REVIEW → REVISE → DELIVER`, depth scaled by the Provost | encoded in `provost.py` + the orchestrator |
| **Integrity Office** | the box honesty rules, institutionalized & non-waivable (no claim without proof; mandatory cross-model peer review; reproduction ≠ discovery; κ=0 → abstain) | `registry.json` → `integrity_office` |
| **Registrar** | budget & scaling; the anti-theater control (cheapest path that clears the bar; permission to stop) | `registry.json` → `registrar` |
| **Dean** | convened only for CROSS-scale (≥2 departments); integrates into one honest artifact | `registry.json` → `dean` |

## Departments (each = a weapon for κ>0, or an armor cluster for κ=0)
`MATH_TCS` → Frontier Construction Engine · `STATS` (core facility) → reproduction/verifier armor ·
`QUANT_PSYCH` → PSYMETRIX · `SOCIAL_SCI` → SOCIUS · `CS_ENG` → execution + test-runner armor ·
`NAT_SCI` → simulation + symbolic/numeric + grounding · `ECON_FIN` → out-of-sample backtest + causal ·
`HUMANITIES_LAW_POLICY` → **armor only** (κ=0: ground + abstain). See [`registry.json`](registry.json).

## Scale tiers (the Registrar's anti-theater dial)
- **DESK** — one-liner/factual → ONE specialist, no committee, no full lifecycle.
- **STANDARD** — one department, abbreviated lifecycle.
- **FULL** — one department, full 7-stage lifecycle.
- **CROSS** — ≥2 departments + the Dean integrates.

## How to run it
- **Routing (deterministic, machine-checked):** `python3 provost.py selftest` — six routing cases
  (κ=1 known construct → Math/weapon/FETCH-KNOWN; medium-κ empirical → mixed; κ=0 judgment → armor + abstain;
  one-liner → DESK anti-theater; proxy-only "construct" → forced κ=0; two domains → CROSS+Dean). Route a real
  task with `python3 provost.py <intake.json>`.
- **Live orchestrator (multi-agent):** the Workflow generalized from
  [`../FRONTIER_ENGINE_WORKFLOW.md`](../FRONTIER_ENGINE_WORKFLOW.md): problem string → **Provost agent**
  (emits the intake, runs `provost.py` for the canonical machine-checked plan) → **department agent**
  (executes; machine-checks κ>0, grounds+abstains κ=0) → **peer-review agent (model ≠ generator)** that
  independently re-verifies → deliver. Test runs + committed predictions live in [`tests/`](tests/).

## Honest status
An **orchestration LAYER** added to the box = a **capability EXPANSION (process, not raw capability)** —
**NOT a ≥10% A/B promotion** (no shared arena; the Helmet improves *how* work is organized, not the model's
ceiling). The capability ratchet stays OPEN at v3. What it demonstrably improves: routing correctness,
literature grounding, independent peer-review catch-rate, cross-disciplinary coverage, and honest abstention
on κ=0. What it cannot do: exceed the model it wears. See [`SPEC.md`](SPEC.md) and [`AUDIT.md`](AUDIT.md).
