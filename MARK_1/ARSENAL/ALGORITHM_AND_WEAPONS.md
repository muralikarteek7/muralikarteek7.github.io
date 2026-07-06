# Part 3 — ALGORITHM & WEAPONS: the runnable frontier-attack procedure

*Operationalizes [`THEORY.md`](THEORY.md). This is the part the old [`WEAPONS_DOCTRINE.md`](WEAPONS_DOCTRINE.md)
was missing: it had armor + a decision *philosophy* but **no offensive loop and no propose-verify weapon**. That
is precisely why our n=7 session ran one solver and quit. This document is the loop.*

---

## A0. THE COMBINATION PRINCIPLE (the frame the rest sits in — added 2026-06-10)

> **Research is not computation. It is theory × computation × simulation × experiment, combined efficiently —
> and the way past a wall is hidden in the combination, not in any single instrument run harder.** A plateau from
> one modality (e.g. search saturating at 224) is a *signal to switch modality*, never a verdict on the problem.
> Operate all four as one loop, each feeding the others:
> - **THEORY** says *where* to look and *what's impossible* (e.g. "a 112-cap is sumset-saturating ⇒ 236 ≠ 112+112+residual" — proven, killed a whole branch).
> - **COMPUTATION** fills the residual the theory leaves small (exact-solve the 22-pt slice; the cyclic CP-SAT).
> - **SIMULATION/SEARCH** maps the landscape and finds where structure is forced (where ≥2 strong methods plateau).
> - **EXPERIMENT/GROUNDING** fetches the real record + construction recipe, and the **verifier certifies** every claim.
>
> The instruments *interrogate each other*: a search plateau → ask theory why → theory kills/opens a branch →
> computation tests the opened branch → grounding checks it against the literature. **Never report a single-modality
> negative as a result** — it is at most one reading on one dial. (This is the lesson of the n=7 session: six
> combined angles produced a structural *map* + the named construction that breaks the plateau, where any one
> angle alone produced only "224, shrug.")

## A. THE FRONTIER-ATTACK ALGORITHM (the router + loop)

```
INTAKE
  0. STATE-VECTOR READ — measure (κ, α, σ, ρ, λ, δ, β/τ) cheaply (THEORY §2). Write them down.
  1. κ-GATE. If κ=0 (no exact verifier buildable) → ARMOR-ONLY: panel/abstain, NO record claim. STOP.
  2. BUILD THE VERIFIER FIRST, before any generation. (This is the HARDEST step, not a checkbox — audit Defect 5.)
        - exact arithmetic only (no floating point — Tao: evaluators get gamed via FP near-misses);
        - test BOTH failure directions: feed a known-wrong object + a deliberately-impossible spec (must REJECT —
          false-positive / gaming test, ImpossibleBench discipline) AND feed the known prior-best record (must
          ACCEPT — false-negative test). A verifier that can be gamed, or that rejects known-good, is not a verifier.
        - re-implement it independently from the generator's code. Log it; freeze it.
        - ⛔ VERIFIER-FEASIBILITY KILL-SWITCH: if an exact verifier cannot be built within a bounded slice of β
          (domain needs deep expertise, or "correct" is irreducibly approximate), **exit to κ=0/armor-only** —
          do not proceed with a weak verifier. A weak verifier guarantees self-deception, not progress.
  3. KNOWN-vs-OPEN. Fetch the authoritative record (OEIS / Cohn's table / Bloom's Erdős list / arXiv).
        Record the prior-best number + who/when. Run the prior best THROUGH your verifier — it must score as
        claimed (if your verifier can't reproduce the known record, your verifier is wrong).
        - KNOWN target  → reproduction lane (W1-fetch the structure, instantiate, verify). Honest, not a record.
        - OPEN target   → discovery lane (below).

DISCOVERY LOOP  ⟳ (escalate STRUCTURE before COMPUTE — L2)
  4. CEILING. Bound it: if a scheme/finite-field law exists → W-LP / W-POLY for the upper bound (know the room).
  5. FLOOR — draw the weapon the map names for the dominant coordinate (THEORY §4):
        σ-big → W-SYMM ;  ρ>0 → W-LIFT (twist the naive product) ;  finite/small-δ → W-SAT ;
        existence → W-PROB ;  otherwise / open ground → W-EVOLVE.
  6. PROPOSE–VERIFY at scale (the engine — exploit α):
        - generate MANY candidates (programs ≫ raw objects — search at the λ level);
        - keep an ISLAND population of the best (diversity is the fuel-line, L3) — never collapse to one lineage;
        - test-time scaling: spend τ (more rounds / islands) on the hard residual, not a bigger model.
  7. PLATEAU CHECK — but only AFTER the STRONG instance of the weapon has been run.
        ⚠️ THE WEAK-WEAPON-CAP ERROR (the costliest mistake in this program — proven on no-3-in-line, where a weak
        ILS "plateaued" at 2k−1 but an exact CP-SAT hit the PROVEN optimum 2k): a plateau from a deliberately
        cheap weapon is NOT a finding — it is a self-imposed cap mislabeled as a negative. Before declaring any
        plateau "structural," you MUST have run the weapon at full strength (exact solver / long budget / strong
        search), not a v0. A negative produced by a weak weapon is dishonest by omission.
        Only if ≥2 *strong* heterogeneous methods stall at the same value < ceiling →
        you are MISSING STRUCTURE (L2′). Then do NOT add more of the same compute; go back to 5 and draw a
        different weapon-class (or mine your small-exact solutions for latent structure — §C).
  7b. BUDGET LADDER + STOP RULE (audit Defect 7 — the loop must be able to EXIT without success).
        Allocate β up front, cheapest structure first, and CAP each rung:
           β_ceiling (W-LP/POLY, T2)  →  β_lift (W-LIFT, T2)  →  β_evolve (W-EVOLVE, T3).
        Each weapon-class gets ONE budgeted attempt + ONE structural re-draw after a plateau (max 2 passes/class).
        If all allocated rungs exhaust with no certified object above prior-best →
        **declare the problem PAST THE CURRENT BUDGET FRONTIER, report the honest negative, STOP.**
        (Permission to stop is part of the method — an endless "go back to 5" is its own failure mode.)
  8. CERTIFY. Any candidate beating prior-best is a CLAIM until the frozen verifier passes it, re-run from
        scratch, independently (cross-model where judgment is involved). Never trust a weapon's self-report.

EXIT
  9. HONESTY GATE (Part-3 §D checklist) before ANY claim leaves the room. Reproduction ≠ discovery.
        No record without the certified object strictly beating the fetched prior-best.
```

## B. THE WEAPON REGISTRY (offense + armor), with the precondition that fires each

> **⚠️ REGISTRY STATUS (audit Defect 8 — do not read this as "weapons we have").** Most rows are a **ROADMAP**,
> not built code. Only **W-SAT, W1-fetch, W-MINE, and W-EVOLVE (v0)** are actually runnable in this program today.
> The algorithm above is therefore an *operational design partially implemented* — calling it a finished method
> would repeat the exact overclaim this method warns against. Honest label: **2.5 weapons built, the rest specced.**

**Armor (always on — defense, never removed):** exact frozen verifier · known-vs-open veto · independent
re-verification from scratch · evaluator-gaming detection · honesty/announcement discipline. *Armor keeps you
honest; it does not make you win.*

| weapon | fires when (state-vector signature) | what it produces | cost | status in OUR program |
|---|---|---|---|---|
| **W-EVOLVE** ⭐ | open ground, high λ, no clean closed-form structure | a **program** that emits ever-better verified objects; island/evolutionary propose-verify (FunSearch/AlphaEvolve) | T3 | 🟡 **v0 BUILT + RAN** (`cap_set/w_evolve.py`): 4000 twisted-triple candidates, frozen-verifier scored → **still 224 (honest negative).** v0 uses a *greedy* residual; a strong version (exact CP-SAT residual / LLM-in-loop program search) is still owed. |
| **W-LIFT** ⭐ | ρ>0 (product space); naive product is a plateau | dim n+1 object from small base cases via a **twisted** recursion (Edel extendable collections) | T2 | **NOT YET BUILT — the named lever toward 236.** ⚠️ 224→236 would be **reproduction of Edel's published construction (W1-fetch), NOT a discovery and BELOW the 10% bar** (audit Defect 1/6). True offense = a certified cap **>236**, which no AI system has produced. |
| **W-SYMM** | large σ (automorphism group) | one representative per iso-class (canonical augmentation / nauty), or symmetry-breaking predicates | T1–T2 | not built |
| **W-LP / W-POLY** | association scheme / finite-field linear law | a **dual certificate** = upper bound (the ceiling) | T2 | not built (would give us the real n=7 ceiling instead of borrowing ≤288) |
| **W-SAT** | finite, bounded, small δ | a *certified* yes/no + checkable proof; exact on a small residual | T2 | ✅ used (the 22-pt residual → 112; the 224 joint solve) |
| **W-PROB** | existence only; sparse local bad events | existence proof; **Moser–Tardos** to make it explicit | T1 | not built |
| **W1-fetch** | KNOWN target, named structure | retrieve + instantiate a published construction, verify | T0 | ✅ validated (Potechin → 112) |
| **W-MINE** | you have exact small cases | extract latent structure from your OWN solved small-n data (the 45-45-22 was latent in our data) | T1 | partially (post-hoc) |

⭐ = the two weapons whose absence explains the 224 retreat. Building them is the concrete to-do this method sets.

## C. The structural-mining sub-routine (how to FIND structure, not just hope for it)

When the map says "draw W-LIFT/W-EVOLVE" you still need the actual structure. The survey's method for *finding*
it (Polya + the record-setters):
1. **Solve the smallest cases EXACTLY** (W-SAT) and store them.
2. **Mine them:** look for a coordinate along which most of the object is *forced* — slices, cones, orbits,
   invariants, a recurring sub-block. (Our 45-45-22 slice was already latent in the n≤5 exact data.)
3. **Encode the pattern as a program** (λ-lift) and let W-EVOLVE mutate it; the verifier kills wrong guesses.
4. **For ρ:** explicitly test "is the naive product maximal in its class?" — if yes (our 224), that is the
   signal to look for the *twist* (different sub-objects per slice, Edel-style), not to extend the product.

## D. THE ANTI-SELF-DECEPTION GATE (run before any claim — grounded in real failures)

A record claim leaves the room only if **all** pass (each line maps to a documented failure mode, SURVEY §C):

- [ ] **Verifier integrity** — written before outputs, executable (not an LLM judge), exact arithmetic, and it
      *rejects* a deliberately-impossible spec. (Tao FP-exploit; ImpossibleBench 76% cheat rate.)
- [ ] **Known-vs-open** — prior best fetched from the authoritative record; our object scores **strictly above**
      it through the frozen verifier. (OpenAI-Oct fiasco = retrieval mislabeled discovery.)
- [ ] **Independent re-verification** — reproduced from the output alone, from scratch, by a *different* system
      than generated it. (Self-check appears in zero real wins.)
- [ ] **Formalization faithfulness** (if a formal checker is used) — the checked statement is the claimed one.
      (The Lean trap: it proves what you *stated*, maybe not what you *meant*.)
- [ ] **No gaming** — output re-scored by an independent clean verifier; no test-file edits / FP near-misses.
- [ ] **Reproduction vs discovery labeled**; sub-threshold gains called point releases, not "breakthroughs."
- [ ] **Announcement discipline** — independent expert/model verification *before* the claim (Bloom standard),
      not after (Weil anti-standard).

## E. The immediate to-do this method generates (so it isn't just prose)
1. ✅ **W-EVOLVE v0 built + run** (`cap_set/w_evolve.py`) — honest negative (still 224). **Owed:** a *strong*
   W-EVOLVE (exact CP-SAT residual on promising twists, or an LLM-in-the-loop program search à la FunSearch).
2. **Build W-LIFT**: implement Edel-style **extendable collections** (different sub-caps per slice). ⚠️ **Scope
   honestly:** reaching **236 is REPRODUCTION** of Edel's 2004 construction (W1-fetch discipline), it does **NOT**
   count toward the 10% promotion bar, and it is **not** "solving an open problem." The only *offensive* target is
   a certified cap **strictly above 236** — for which **no AI system has a published result** (audit Defect 1/9).
   Expect a plateau; the deliverable is a working twist-recursion + an honest number, not a record.
3. **W1-fetch the 236 anchor FIRST (cheapest, highest-value, T0).** Retrieve Edel's explicit 236-cap (or its
   generator), instantiate, verify with `capset_verify.py`. This **grounds the whole numerical baseline** — the
   verifier's `KNOWN_LB[7]=236` currently rests on a single secondary citation neither author could fetch from a
   primary source (audit Defect 1, Part IV).
4. **Build W-POLY** for the ceiling: slice-rank / LP upper bound for n=7, so we *own* our ceiling instead of citing ≤288.
5. **The real validation (not done): run the full algorithm COLD on a problem we don't know the answer to** (a
   kissing-number / Sidon-set dimension) — the only thing that turns this audited design into a *validated* method
   (THEORY §6, audit Defect 10). No record claimed until the frozen verifier passes a strictly larger certified object.
