# BOOTSTRAP — the new-weapon scaffolder (SHOES-d)

BOOTSTRAP grows the arsenal by the same rule that built it: **the machine, not the model, earns κ.**
Given a NEW problem class in natural language, it tries to **find and VALIDATE an exact verifier** —
semi-automating "add a weapon" — while **refusing to fake κ** when no real verifier exists.

## The one-line test of success
> Given a new problem class, BOOTSTRAP FINDS a candidate exact verifier, VALIDATES it by RUNNING it
> on known-answer cases (accept-good / catch-broken-per-violation-type / abstain-malformed) before
> registering a κ>0 department — and returns **κ=0 ARMOR-ONLY**, never a fake gate, when no real
> verifier exists or only LLM judgment is available; a **hallucinated verifier is rejected at the
> run step**, and a **toy-passing verifier is never over-sold as frontier-correct**.

## How to run
```
cd /Users/varunesh/Desktop/AI_agents/MARK_1/ARSENAL/weapons/bootstrap
python3 selftest_all.py          # the frozen gate — MUST exit 0 before anything else counts
python3 demo_sudoku_vs_essay/run_demo.py   # the demo (predictions committed first)
```

## The three outcomes
- **κ>0 VERIFIER FOUND** — a candidate PASSED its known-answer run → registration record produced,
  hand off to a full weapon-build kickoff.
- **κ=0 ARMOR-ONLY** — no exact verifier validated in N tries → route to ARMOR; do not build a weapon.
- **ABSTAIN / NEED-INPUT** — under-specified to even search → ask for a sharper spec.

## Files
- `bootstrap_gate.py` — the **validation gate** (`validate_candidate`, `bootstrap_domain`) + the
  reference verifiers (real sudoku, plus the planted hallucinated / no-boxes / can't-fail attackers)
  + the non-waivable self-tests. **This is the authority: only the RUN promotes a domain to κ>0.**
- `bootstrap_router.py` — the router (`route`) + its self-test. Routes by the κ-gate; **never
  promotes from routing alone** (`kappa_hint` is `None` on a SEARCH verdict).
- `selftest_all.py` — runs both, exits non-zero on any failure.
- `SPEC.md` — the design, the κ split, the COMMITTED candidate-source list + N-attempts bound.
- `GROUNDING.md` — the fetched load-bearing facts (W4 fabrication lesson; Sudoku & graph-coloring
  rules; the κ=0 essay-judgment fact).
- `demo_sudoku_vs_essay/` — `PREDICTION.md` (committed first) → `run_demo.py` → `RESULT.md`.
- `AUDIT.md` — cross-model audit stub (auditor ≠ generator fills it).

## HONEST CEILING (read this)
- **Finds + validates verifiers where they exist; returns κ=0 honestly elsewhere.** It cannot
  cover judgment domains (essay quality, persuasion) — there is no exact decision procedure, so it
  returns ARMOR-ONLY, not a fake gate. Looking *less* capable there is the correct behavior.
- **Step (1) is 0%-trusted.** The searcher/proposer ("I found a verifier") hallucinates
  (registry W4: Haiku+Sonnet fabricated 100% raw). A hallucinated/non-running candidate is REJECTED
  at the run step. The RUN is the only authority.
- **Toy-passing ≠ frontier-correct.** A validated verifier carries only its known-answer coverage.
  A verifier that passes 3–5 toy cases can still be wrong on the real frontier target. BOOTSTRAP
  **opens the door**; it does **not** ship the weapon — the new department it scaffolds must STILL
  pass its own full box build (gate-first + demo + cross-model audit).
- **Coverage is only as good as the declared violation types.** The gate enforces ≥1 broken case
  per *declared* violation type, but cannot know about an *undeclared* one. A verifier whose author
  forgot a whole class of violation can validate while being incomplete on the un-named class. The
  honest mitigation is the full-box build downstream, not BOOTSTRAP. **(Hardened after audit Defect
  B:** an *empty* `declared_violation_types` list — which used to disable the coverage check
  entirely and let a memorizer through — is now REJECTED `NO_DECLARED_VIOLATION_TYPES`, and every
  broken case must name its class `BROKEN_CASE_MISSING_VIOLATION_TYPE`. The *undeclared*-class
  ceiling above remains; an *empty*-declaration bypass no longer does.)
- **The abstain bar is now ENFORCED, not optional (audit Defect A fix).** A harness must supply
  ≥1 MALFORMED case (`NO_MALFORMED_CASE_SUPPLIED` otherwise). Previously the malformed loop silently
  no-op'd on an empty list, so a verifier that would CRASH on garbage in production could earn κ=1
  without ever proving it abstains.
- **This is a mechanism to grow the arsenal honestly — NOT a promotion.** It does not advance the
  capability ratchet; each NEW weapon it scaffolds runs the full box discipline.

## κ labels
- κ=1 (exact, machine-checked): the validation RUN in `validate_candidate`.
- κ<1 (judgment, 0%-trusted): the search/proposal step. Nothing counts until the RUN.
