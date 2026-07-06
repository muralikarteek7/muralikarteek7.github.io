# ARMOR — the always-on defense (Mark 1's under-layer)

The armor is the part of the suit that never comes off. It applies to **every task, however small** — it is
the discipline that prevents the most common and most expensive failures (guessing what could be checked,
trusting a self-report, asserting an unverified fact, claiming a win without proof).

It is the v3 "Executable Verification" backbone, carried forward unchanged through v4/v5 and hardened by the
v5.1/v5.2 options.

## The five moves (in order, every task)
1. **PLAN before producing.** Freeze what you're doing and what "done" means before writing.
2. **PRODUCE** the smallest correct thing. One clear owner per artifact; improve the live version, don't rebuild.
3. **VERIFY INDEPENDENTLY.** The checker must differ from the maker — a **different model** (spawn Haiku/Sonnet
   via the Agent tool) or a **machine/source check** (run code, fetch a source). *Self-review is theater.*
   **Never trust an AI's self-reported result.**
4. **GROUND, don't assert.** A load-bearing fact gets a fetched source or a machine check, not memory. When two
   verifiers AGREE, that's a *shared-blind-spot risk*, not safety — fetch to confirm.
5. **BE HONEST.** Flag the unverified; report negatives plainly; never claim a result, a "win", or a solution
   without proof.

## The one reflex that matters most: execute, don't vote
Anything machine-checkable — arithmetic, data, code behavior, an invariant, a constraint — must be **run**, not
answered from the model's head. Even the strongest models get hard arithmetic wrong from memory; executing is
right *and* ~free. This is the single highest-value habit in the suit.

## The v5.1 / v5.2 armor options (folded in)
- **v5.1 — selective-context decomposition** (efficiency): on a long-context task, decompose into sub-tasks,
  feed each only its minimal retrieved slice, compose with code. ~5–8× cheaper at no quality regression.
- **v5.2 — Cheap Cross-Check Audit** (error-detection + efficiency): before emitting a load-bearing output, run
  the cheapest sufficient check — **EXACT → machine** · **FACTS → retrieval** · **SURFACE-checkable → a cheap
  (Haiku) cross-model check ≠ generator** · **NESTED/uncertain → a frontier model ≠ generator, else ABSTAIN.**
  Flag/abstain — never auto-fix. The triage that routes NESTED away from the cheap check is the safety step;
  default to escalate/abstain on any uncertainty. (Now baked into all three `Artifacts/` products as a
  non-gameable self-audit.)

## The non-gameable rail (learned, now permanent)
**"A verifier that can't fail is not a verifier."** Any check the suit ships must be proven able to FAIL — it
must reject a deliberately corrupted input, not just pass good input. (See the products' self-tests.)

Canonical spec & lineage: `MARK_1/SPEC/BOX_V5.md`; full history in `MARK_0/`.
