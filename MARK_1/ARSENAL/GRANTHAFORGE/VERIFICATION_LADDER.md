# GRANTHAFORGE · VERIFICATION LADDER — the heart of the weapon

*When you code a verse of a computational treatise, the code is a claim: "this function is the rule the text
states." A claim needs a verifier. The whole craft is choosing the right verifier for what the text gives you —
and the text gives you one of two things: a **worked example**, or only an **explanation**. Both are on the same
path; they license different verifiers. This file is the discipline for both, with the honest tiering that keeps
the build truthful.*

> The operator's law (paraphrased at the origin of this weapon): *"Not all the time will we have examples — but
> we will have explanations, and they play the most crucial role. Both are on the same path."*

---

## 0. The frame

A verse maps inputs → outputs. "Done" ≠ "I transcribed a plausible formula." Done = **the output is anchored**
by something independent of the act of coding it. Self-review is theater. So every verse carries a **tier** that
says how strongly it is anchored — and the tier is written next to it in `plan/01_PROGRESS.md`.

```
VERIFIED  >  DERIVED  >  CODED  >  TODO
```

- **VERIFIED** — reproduces a worked example (or an exact independent equivalent) to the text's precision.
- **DERIVED** — no example, but the rule is faithfully coded AND ≥2 independent ladder rungs (below) hold.
- **CODED** — faithfully transcribed; ≤1 check; explicitly flagged "needs a verifier."
- **TODO** — not yet read/coded.

**Never** stamp VERIFIED on an explanation-only verse without an independent equivalent. A formula that "looks
right" and runs without error is **CODED**, not verified — say so.

---

## A. EXAMPLE-GOLD (a worked example exists)

The example is a frozen, non-gameable verifier. Reproduce its printed numbers.

1. **Feed the example's `given`, compare every printed intermediate**, not just the final answer — the
   intermediates localize a fault to one step.
2. **Tolerance = the text's own rounding**, not your patience. Integer/exact fields → tol 0. Sexagesimal that the
   book hand-rounds → a few arc-seconds / one minor unit. Per-field tolerances where a result mixes exact and
   rounded parts.
3. **Two examples beat one.** Where the same rule has a small-multiplier and a large-multiplier example (e.g. a
   per-cycle constant × a small vs large cycle count), verify against BOTH. A wrong high digit can vanish under
   one and be exposed by the other. (Canonical: two GL dhruvakas hidden mod 360 by a small cakra count, exposed
   by the modern large-count example, then confirmed by the source table.)
4. **When the example won't match:** do NOT loosen tolerance to force green. Re-OCR the inputs (a misread digit),
   re-read the rule, check for a units convention. If the rule is unambiguous and only the example is off, it is
   a **book erratum** — log it, keep the engine on the stated rule, and look for a second example that
   corroborates the engine (the book often contradicts its own slip elsewhere). Operator-confirmable policy.

---

## B. EXPLANATION-GROUND (only prose / a rule / a derivation — no example)

This is the harder, more common case in advanced material. The explanation is the authority. Build to it
**faithfully** (no silent reinterpretation; the docstring quotes the verse), then **climb as many rungs as the
material allows.** Each rung is an *independent* check — it does not re-use the act of transcription.

| Rung | Check | What it rules out |
|---|---|---|
| 1 | **Faithful transcription** — code == stated rule, verbatim; docstring quotes it | reinterpretation / wishful formula (necessary, never sufficient) |
| 2 | **Units / dimensions** resolve to the claimed output unit; conversions explicit | unit-mismatch bugs, stray ×60/÷60 |
| 3 | **Boundary & limiting cases** hit the text's stated zeros / maxima (*parama*) / symmetry points | wrong constants, sign errors, off-by-scale |
| 4 | **Monotonicity / shape** the text asserts (rises, saturates, is symmetric) holds in the code | structural errors the endpoints miss |
| 5 | **Derivation closure** — if a rationale is given, re-derive (symbolically if possible); the code must land on the derivation's endpoint | a formula that matches a point but not the curve |
| 6 | **Cross-source corroboration** — the SAME rule in another edition / commentary / translation / parallel text states the same structure & constants | a single-source typo or your mis-transcription |
| 7 | **Inter-section closure** — the quantity feeds a later verse that DOES have an example / a measurable consequence; run the chain, check the downstream number | an unverifiable middle step (verified *through* its use) |
| 8 | **Synthetic equivalent** — construct a legitimate input; compute two ways (the text's rule vs an independent closed form / reference implementation / different algorithm); the residual = the *expected approximation*, not a bug | the rule being subtly wrong vs merely approximate |
| 9 | **External-reality oracle** — where a modern ephemeris / dataset / solver / ground truth exists, compare and report the residual honestly | the text (and you) both being wrong about the world |

**Tiering from the ladder:** rungs 1 + (any ≥2 of 3–9 that genuinely hold) → **DERIVED**. Rung 8 or 9 returning an
exact match (not just "close") → **VERIFIED** (you found an independent equivalent). Only rung 1 (or 1+2) →
**CODED**, flagged.

**The two failure modes to name out loud:**
- *False green* — a rung "passes" because it's too weak (e.g. units check on a formula whose constants are wrong).
  Prefer rungs 3/5/7/8 (they bind the actual numbers) over 1/2 (they only bind the form).
- *Approximation mistaken for error* — rung 8/9 shows a gap; before calling it a bug, ask whether the text is a
  deliberate rational/koṣṭha approximation (most karaṇas are). Quantify the expected gap and compare. A gap that
  matches the approximation order is a PASS with a noted residual, not a failure.

---

## C. Worked instances (from the GL build — proof the ladder bites)

- **Rung 3 (limiting case) caught a constant:** the Moon mandaphala denominator — the rule's *parama* (max at
  kendra 90°) had to equal the text's stated 5°; the example then localized a book slip vs the formula.
- **Rung 6 (cross-source) settled an OCR ambiguity:** the printed parilekha **Figure 2** (from a Hindi-commentary
  companion) fixed which side the totality contacts sit on — a positional error the prose alone left ambiguous.
- **Rung 7 (inter-section closure) verified no-example diameters:** Chapter-8 disk diameters had no direct
  example, but they feed a grāsa that does — the chain closed them.
- **Rung 8/9 (oracle) caught a live bug:** comparing two walkthrough eclipses to DE422 (NASA-grade) exposed a
  solar-magnitude error (dividing grāsa by the Moon instead of the Sun) the engine's own number had hidden.
- **Approximation ≠ error:** GL's no-jyā mandaphala sits ~2′ from the true sine — rung 8 flagged the gap, but it
  is the *expected* rational-approximation residual, so the verse is correct (with the residual noted), not buggy.

---

## D. One-line discipline

> Pick the strongest verifier the text affords. With an example, reproduce it (and prefer two). Without one, build
> to the explanation and climb the ladder until ≥2 independent rungs bind the *numbers*, not just the form — then
> tier honestly, and flag every gap, divergence, and erratum instead of fudging to green.
