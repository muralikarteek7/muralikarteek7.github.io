# Part 2 — THEORY: a parameterized theory of frontier work (for many fields & cases)

*Grounded in [`SURVEY.md`](SURVEY.md). The point of a theory (vs. a checklist) is that it must **predict** —
given a new frontier problem in any field, the theory says whether it is attackable, which weapon to draw, and
where it will plateau, **before** you spend the budget. It must also be **falsifiable**: each claim below names
what observation would refute it.*

---

## 1. The one-sentence theory

> **A frontier falls when you can assemble a (Generator, Verifier, Structure) triple in which the Structure
> shrinks the effective search small enough that the Generator–Verifier asymmetry can sweep it within budget.**
> Offense is not a bigger Generator. It is *finding the Structure that makes the search small* — and the Verifier
> is the only thing that ever certifies you arrived.

Everything else is how to read a problem to know *which* structure exists and *which* weapon extracts it.

## 2. The state vector: read any frontier problem as 7 observable coordinates

A problem is not "a math problem" or "a trading problem." It is a point in this space. Different **fields** =
different regions of the *same* space, which is why one theory covers them all.

| symbol | coordinate | how to measure it (cheap) | why it decides the weapon |
|---|---|---|---|
| **κ** | **checkability** — is there a cheap, exact, non-gameable verifier? | try to write the verifier in <1 day; does it use exact arithmetic? | **κ>0 is the precondition for ALL offense.** κ=0 ⇒ armor only, abstain on records. (Survey C: every win has a formal verifier.) |
| **α** | **generator–verifier asymmetry** = cost(generate)/cost(verify) | time one verify vs one generate | high α ⇒ you can afford **massive propose-verify** (FunSearch-scale). This is the *engine*. |
| **σ** | **symmetry** — size of the automorphism / invariance group | identify the group acting on solutions | large σ ⇒ **canonical augmentation / symmetry-breaking** divides the search by ~\|G\| |
| **ρ** | **recursive/product structure** — does dim n+1 build from n? **and is the NAIVE product beatable?** | is the space a product (Fₚⁿ, code length, tensor)? | ρ>0 ⇒ **lifting**; the live question is always *"is the naive product a plateau I can TWIST past?"* (Edel) |
| **λ** | **abstraction handle** — can a candidate be a **program / parameterized family** instead of a raw object? | can one short program emit the whole object? | high λ ⇒ search **program space**, the exponential compression behind FunSearch/AlphaEvolve |
| **δ** | **gap** = best-known-construction / best-known-bound | fetch both from the authoritative record | large δ ⇒ both sides open, room to move; small δ ⇒ near closure, need *exact* methods |
| **β,τ** | **budget & test-time scaling** — can you spend more *search* (not a bigger model) on harder instances? | is the loop restartable / parallelizable? | hard frontiers need τ (more search time), not a larger Generator (Survey A, primitive 6) |

**Falsifier for the state-vector claim:** exhibit a frontier broken by a method whose choice is *not* explained
by which of {σ, ρ, algebraic-scheme, finiteness, λ} was large. (None found in the survey; the cap-set,
matmul, sorting, Ramsey, Golomb, kissing records all route cleanly.)

## 3. The Frontier "inequality" (a QUALITATIVE knob-model, not a computable bound)

> **Honesty note (audit Defect 2):** the relation below is **not a usable inequality.** You cannot measure
> `effective_search_size` until you've *found* the structure — which is the whole problem — and the RHS budget is
> a free parameter, so every problem satisfies it for large enough β. It is a **qualitative model of three knobs**,
> kept only because the knobs are the right ones to think about, *not* because you can plug in numbers and get a
> falsifiable "attackable at β=10k." Treat it as a mnemonic, not math.

A construction frontier is *breakable within budget β* roughly when:

```
        effective_search_size(problem after Structure is applied)
        ───────────────────────────────────────────────────────   ≲  β       [QUALITATIVE]
                     α  ·  (candidates per unit budget)
```

Read it as three knobs you can actually turn:
1. **Shrink the numerator** — apply the largest available Structure (σ symmetry, ρ recursion, λ program-encoding,
   scheme→LP). This is the *real* move. Every record in the survey is a numerator collapse, not a denominator boost.
2. **Raise α** — make the verifier cheaper / the generator more on-target (diffs not rewrites; islands for diversity).
3. **Spend β/τ** — more search time on the hard residual (test-time search), *not* a bigger model.

**Corollary (the anti-pattern, named):** if ≥2 heterogeneous methods plateau at the same value below the known
bound, the numerator is still too big — you are missing Structure, and **adding more Generator/compute is
provably the wrong knob.** (This is exactly the cap-set ≤90-then-112 story, and my own 224 plateau — §6.)

## 4. The weapon-selection map (the theory's main predictive output)

Given the state vector, draw the weapon whose precondition is satisfied. **Most hard problems trigger several
rows at once** (audit Defect 3: cap-set n=7 fires ρ, λ, scheme, AND finite simultaneously — that multi-fire *is*
why it's hard). So the map needs an explicit **dominance order**, not just "pick the satisfied row":

> **DOMINANCE / TIE-BREAK ORDER (apply top-down; do the cheap ceiling first, then the strongest applicable floor):**
> 1. **κ=0 → armor only.** (overrides everything)
> 2. **Always first, if cheap:** a scheme/finite-field law → **W-LP/W-POLY** for the *ceiling* (you want to know
>    the room before searching). This co-fires with floor weapons — it is not an alternative to them.
> 3. **Floor weapon, strongest structure wins:** large σ → **W-SYMM** ▷ then ρ>0 with a beatable naive product →
>    **W-LIFT** ▷ then small-δ finite residual → **W-SAT** ▷ else open ground/high λ → **W-EVOLVE**.
> 4. **W-EVOLVE is the residual/default** — use it when no closed-form structure (σ, ρ, scheme) dominates, or to
>    search *on top of* a structural weapon (e.g. evolve the twist inside W-LIFT, as `w_evolve.py` does).
>
> For cap-set n=7 this resolves the four-way tie to: **W-LP/POLY (ceiling) + W-LIFT (ρ has a beatable product) +
> W-EVOLVE on the residual** — which is exactly what §6 says, now *derived from the order, not asserted in prose.*

Order of operations: **bound the ceiling, then build the floor, escalating Structure before compute.**

| if the dominant coordinate is… | the structure to extract | weapon (see Part 3) |
|---|---|---|
| κ = 0 | none — it's a judgment task | **armor only**: panel/abstain, no record claim |
| finite & bounded, small δ | a certified yes/no | **W-SAT** (cube-and-conquer, symmetry-broken) |
| large σ | one rep per isomorphism class | **W-SYMM** (canonical augmentation; or symmetry-breaking inside W-SAT) |
| association scheme / finite-field linear law | a dual certificate (the ceiling) | **W-LP / W-POLY** (Delsarte / slice-rank) |
| ρ > 0 (product space) | base cases + a **twisted** recursion | **W-LIFT** (Edel extendable collections) — *naive product is the trap* |
| high λ, open ground, no clean structure yet | a *program* that emits ever-better objects | **W-EVOLVE** (FunSearch/AlphaEvolve propose-verify, islands) |
| existence only, sparse bad events | a probabilistic guarantee | **W-PROB** (LLL + Moser–Tardos to make it explicit) |

**Falsifier for the map:** a problem where the precondition-matched weapon is *dominated* at matched budget by a
precondition-mismatched one. (Would force a row revision — that's the theory earning its keep.)

## 5. Three structural laws (field-independent, each falsifiable)

- **L1 — Verifier primacy.** Certified output quality is capped by verifier integrity, not generator strength.
  *Falsifier:* a sustained record set by an un-verifier-able method. *Status:* survives — every survey win has a
  formal/executable verifier; every overclaim (OpenAI-Oct) lacked an independent one.
- **L2 — Structure beats compute at the margin.** Past the first plateau, marginal records come from new
  Structure, not more search of the old kind. *Falsifier (sharpened, audit Defect 4 — the loose version let any
  new program count as "structure"):* a record set by **increasing compute budget alone, holding the search
  formulation fixed** — same program space, same generator architecture, same verifier — in a domain where ≥2
  heterogeneous methods already plateaued. *Status:* **REFUTED as a universal law; real behaviour is
  regime-dependent.** On **no-3-in-line** ([`no3line/COLD_TEST_2026-06-10.md`](no3line/COLD_TEST_2026-06-10.md))
  an exact CP-SAT reaches the **proven optimum 2k at k=10,12** with *no new structure* — compute closes the
  small-k margin, so L2 is false there. (At larger k, generic search stalls and the *algebraic* construction
  becomes the efficient route — structure wins the scale, not the margin.) Cap-set 90→112 and FunSearch remain
  consistent with L2. **Corrected law (L2′): the structure-vs-compute winner is REGIME-dependent — compute often
  wins the small-instance margin; structure wins at scale / when ≥2 *strong* (not weak) methods plateau.** The
  original overclaim ("plateau confirms L2") was a weak-weapon artifact, caught by cross-model verification and
  retracted. **Operational consequence: never call a plateau "structural" until the STRONG instance of the weapon
  has been run** (the weak-weapon-cap error — see ALGORITHM §A step 7).
- **L3 — Asymmetry is the engine, diversity is the fuel-line.** Offense throughput ∝ α, but collapses without
  diversity maintenance. *Falsifier:* a high-α propose-verify loop that beats a record *without* any
  diversity/island mechanism and *without* injected structure. *Status:* survives (FunSearch 512 in 4/140 runs —
  diversity is why running more islands eventually hits it).

## 6. The theory applied to our own failure (a DIAGNOSIS — not yet a validation)

> **Honesty note (audit Defect 10):** what follows is **post-hoc** — the theory is applied to the one case it was
> built from, whose answer was already known. That makes this a *diagnosis*, **not** evidence the theory predicts.
> A real validation requires running the algorithm **COLD on a problem whose answer we don't know** (e.g. a
> kissing-number or Sidon-set dimension) and reporting whether the routing was right. Until that cold test exists,
> "the theory has teeth" is a claim, not a result. *(This is exactly the post-hoc trap the predecessor doctrine
> fell into; flagging it rather than repeating it silently.)*

Apply the state vector to **our n=7 cap-set session** (the 224 plateau, [`cap_set/N7_PLATEAU_2026-06-10.md`](cap_set/N7_PLATEAU_2026-06-10.md)):

- κ = 1 (exact verifier exists ✓), α high ✓, **ρ > 0** (Fₚⁿ product space — the dominant coordinate), λ high
  (caps are emittable by short programs), δ = 224/236 ≈ 0.95 (gap open).
- **The map says: ρ-dominant ⇒ draw W-LIFT (Edel extendable collections), and W-EVOLVE on the residual.**
- **What we actually did:** ran **one** CP-SAT (a W-SAT/object-space move), hit 224 = the **naive product**
  2·112, confirmed it maximal, and *stopped*. We never drew the weapon the theory names for ρ-dominant problems.
  L2 predicts exactly this: object-space search plateaus; the record needs the *twisted* recursion.
- **Verdict:** 224 was not "cheap derivation honestly hitting its ceiling." It was **drawing the wrong weapon and
  quitting** — armor (honest negative) substituting for offense (W-LIFT + W-EVOLVE never run). *(Update: W-EVOLVE
  has since been built and run — `cap_set/w_evolve.py`, 4000 twisted candidates, still 224, an honest negative.
  So the routing was right that object-space CP-SAT was the wrong weapon, but the named offense **also** doesn't
  reach 236 in its v0 form — 236 needs W-LIFT's specific Edel structure, still unbuilt. The diagnosis holds; the
  cure is only partially built.)*

## 7. What the theory does NOT claim (honesty boundary)
- It does **not** promise a record. It predicts *which weapon* and *where the plateau is*; the object still has to
  be built and **machine-certified**. Many problems are genuinely past the budget frontier.
- κ·σ·ρ·λ are **decomposition coordinates, not a fitted predictor.** The prior program already showed (C-term,
  H5) that small-N "predict the gain from the coordinates" fails. The theory **routes**; it does not forecast the
  number.
- The honesty layer (Part 3 §armor) is **not optional scaffolding** — it is what makes the difference between the
  two OpenAI-Erdős episodes. A record without it is theater (L1).
