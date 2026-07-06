# SPEC — BOOTSTRAP (SHOES-d, the new-weapon scaffolder)

*KIT-EXPANSION item #5 (SHOES sub-component d). Built 2026-06-20, box-style, gate-first.*

## What it is
Given a NEW problem class described in natural language, BOOTSTRAP tries to **find and VALIDATE
an exact verifier** for it — turning "add a weapon" from fully-manual into semi-automated, while
**refusing to fake κ** when no real verifier exists. It automates the *verifier-identification*
step a human now does by hand; it does **not** write the whole weapon.

**The one rule that governs everything:** the ONLY thing that promotes a domain to κ>0 is a
candidate verifier that, when **RUN** on known-answer cases, passes the gate-of-the-gate bar
(accept-good / catch-broken / abstain-malformed). A self-report that "this verifier works" earns
nothing. Step (1) of the pipeline — the searcher proposing a verifier — is **0%-trusted**.

## The three outcomes (the router's verdict)
| outcome | trigger | what BOOTSTRAP does |
|---|---|---|
| **κ>0 VERIFIER FOUND** (`KAPPA>0_VERIFIER_FOUND`) | a candidate verifier PASSES all known-good cases, CATCHES a known-broken one per declared violation type, and ABSTAINS on malformed | produces a registration record for a new department + verifier; hands off to a full weapon-build kickoff |
| **κ=0 ARMOR-ONLY** (`KAPPA=0_ARMOR_ONLY`) | no exact verifier found/validated within the committed N-attempts bound | records "armor-only" + why; routes the domain to ARMOR; does **not** build a "weapon" |
| **ABSTAIN / NEED-INPUT** (`ABSTAIN_NEED_INPUT`) | the problem class is under-specified to even search | asks for a sharper spec; does not guess |

## The κ split (label honestly)
- **κ=1 (exact, machine-checkable):** step (2) — *running* a candidate verifier on cases with
  KNOWN answers. This is `bootstrap_gate.validate_candidate`. It is the only authority.
- **κ<1 (LLM judgment, 0%-trusted):** step (1) — the searcher/proposer claiming "I found a
  verifier / this tool exists." LLM-proposed tools **hallucinate** (registry W4: Haiku+Sonnet
  fabricated 100% raw → checker mandatory; see `GROUNDING.md`). Nothing here counts until the RUN.

## The validate-don't-trust rule (the gate-of-the-gate)
A candidate verifier is a callable `verifier(instance) -> "VALID" | "INVALID" | "MALFORMED"`.
To earn κ>0 it must, **on the new domain's known-answer cases**:
1. **accept every known-GOOD** input as `VALID` (and never raise on a well-formed input — a raise
   means non-running / hallucinated → REJECTED);
2. **catch every known-BROKEN** input as `INVALID`;
3. **declare ≥1 violation type, and be exercised on ≥1 broken instance of EACH declared violation
   type** (audit fix #2 — a soundness-INCOMPLETE verifier, e.g. a Sudoku checker that skips the
   3×3 boxes, passes toy cases while being wrong on the class → REJECTED). An **empty
   `declared_violation_types` list is REJECTED** (`NO_DECLARED_VIOLATION_TYPES`) — with nothing
   declared, the coverage check `missing = [vt for vt in declared if vt not in exercised]` is
   *vacuously* empty and a verifier that merely MEMORIZES the cases would pass (**audit Defect B
   fix**). Every BROKEN case must carry a **non-None `violation_type`** (an untyped broken case
   proves no class → `BROKEN_CASE_MISSING_VIOLATION_TYPE`);
4. **abstain on MALFORMED** input — return `MALFORMED`, never `VALID`/`INVALID`, never raise. **At
   least one MALFORMED case MUST be supplied and is enforced** (`NO_MALFORMED_CASE_SUPPLIED`): the
   contract is "≥1 good + ≥1 broken per declared type + ≥1 malformed", and a harness that OMITS
   malformed cases leaves the abstain bar UNTESTED — a verifier that would CRASH (or return `VALID`)
   on garbage in production would otherwise earn κ=1 (**audit Defect A fix**);
5. have had **at least one GOOD and one BROKEN** case supplied (a verifier never tested on a
   broken input is **REJECTED** — "a verifier that can't fail is not a verifier").

Reject reasons are frozen, machine-readable: `HALLUCINATED_NONRUNNING`, `REJECTS_KNOWN_GOOD`,
`ACCEPTS_KNOWN_BROKEN_OR_NO_BROKEN_TESTED`, `SOUNDNESS_INCOMPLETE_MISSED_VIOLATION_TYPE`,
`DID_NOT_ABSTAIN_ON_MALFORMED`, `NO_KNOWN_ANSWER_CASES_SUPPLIED`, `NO_MALFORMED_CASE_SUPPLIED`
(Defect A), `NO_DECLARED_VIOLATION_TYPES` (Defect B), `BROKEN_CASE_MISSING_VIOLATION_TYPE` (Defect B).

## COMMITTED reproducibility parameters (audit fix #1 — so two runs can't disagree)
A κ=0 ARMOR-ONLY verdict is only reproducible if the *search budget* and *candidate sources* are
pinned. These are frozen here:

- **Candidate-source list (what the searcher is allowed to draw from), in priority order:**
  1. an existing **constraint checker / validator library** (e.g. a pure-Python rule checker,
     `networkx` proper-coloring check, sudoku validators);
  2. a **SAT/SMT solver** (`z3` — present in this infra) for decision properties expressible in
     propositional/first-order logic;
  3. a **constraint solver** (Google **OR-Tools** `ortools` — present) for CP/feasibility checks;
  4. a **symbolic engine** (`sympy` — present) for algebraic identity/decision properties;
  5. a **published benchmark with ground-truth labels** (a fetched dataset that decides the
     property), used as the known-answer cases the candidate is RUN against.
  Confirmed present in this infra: `sympy 1.14.0`, `z3`, `ortools`. Absent: `networkx`, `pysat`
  (so the demos use pure-Python reference verifiers, no external dependency).
- **N-attempts bound:** `n_attempts_bound` (default **3**). BOOTSTRAP runs at most N proposed
  candidate harnesses; if none validate, the verdict is κ=0 ARMOR-ONLY. Pin N in the call so a
  re-run draws the same conclusion. (The number of *known-answer cases* per candidate is 3–5,
  ≥1 good + ≥1 broken per declared violation type + ≥1 malformed.)

## The router
`bootstrap_router.route(spec)` classifies a domain by the κ-gate *before* searching:
- exact, non-gameable property plausibly exists → **SEARCH-AND-VALIDATE** (run candidates; the RUN,
  not the routing, earns κ — `kappa_hint` is `None`, never promoted by routing);
- judgment-only / no exact property (incl. a judgment domain *dressed* as exact) → **ARMOR-ONLY**
  (κ=0; never invent a gate);
- under-specified → **ABSTAIN-NEED-INPUT**.

## What BOOTSTRAP is NOT
- ❌ a verifier itself (it finds/validates one).
- ❌ trustworthy on "I found a verifier" — that is LLM judgment and hallucinates; only the RUN counts.
- ❌ able to cover κ=0 domains (no formal tool for "persuasive-writing quality" → it must return
  κ=0, not invent a fake gate).
- ❌ a guarantee the validated verifier is correct on the FRONTIER — toy-passing ≠ frontier-correct
  (honest ceiling).

## Deliverables
`bootstrap_gate.py` (the validation gate + reference verifiers + non-waivable self-tests),
`bootstrap_router.py` (router + self-test), `selftest_all.py` (runs both, exits non-zero on any
failure), `GROUNDING.md` (fetched load-bearing facts), `README.md` (honest ceiling), `AUDIT.md`
(auditor stub), `demo_sudoku_vs_essay/` (committed `PREDICTION.md` → `run_demo.py` → results).
