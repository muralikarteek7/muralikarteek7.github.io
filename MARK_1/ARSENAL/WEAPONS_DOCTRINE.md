# Weapons Doctrine — how the box attacks hard computational / math problems
*A structural re-understanding (2026-06-10), not a write-up of one problem. The cap-set 112 episode is the worked example; the doctrine is general (math, trading, OR, numerics — any "produce a hard verified object" task).*

---

## 0. The one-paragraph re-understanding
The program has, until now, built **ARMOR**: machinery that makes AI output *safe* — checker-first verification, grounding, abstention, honesty veto, never-trust-self-report. Armor is **defense**: it stops you being wrong. It does **not** make you *win*. Breaking a frontier needs **OFFENSE** — **WEAPONS**: special-purpose, differently-priced math/computational capabilities that *produce* a new verified object. **Box = Armor (always-on) + an efficient MIXTURE of Weapons (drawn per problem).** The product is the *mixture/router*, not any single weapon and not any single artifact (e.g. the number 112).

> **The verifier is the only thing that is always true. A weapon proposes; the armor disposes. "Verified" ≠ "new" — armor gives the first, weapons give the second.**

---

## 1. What we went through (the honest case study — extract the lesson, not the number)
Target: a maximum cap set of size **112** in AG(6,3) = F₃⁶ (729 points; pick the most with no 3 summing to 0 mod 3).

**Phase A — pure search (all owned ARMOR), all stalled ≤90:**
trivial greedy 64 · balance-priority greedy 80 · least-constraining greedy 77 · random-restart 78 · iterated local search (ILS) 88 · exact CP-SAT cold 89 · warm-started CP-SAT · LNS combo (trapped, *worse* than its parts) · symmetry-frame CP-SAT 41 (worse). Best verified before grounding: **90** (a 45×{0,1} product cap, *provably maximal* at 90). We burned multiple 700–1500s solver runs + a 47-min agent (which honestly reached 90, ~15% confidence, **refused to fabricate**).

**Phase B — structure (a WEAPON), cracked it instantly:**
the PI supplied Potechin (2008). It gives the **45-45-22 slice structure**: slice F₃⁶ by one coordinate into three F₃⁵ caps of sizes 45, 45, 22. Using our *already-verified* 45-cap as slice0, slice1 = −c−slice0 (an algebraic identity, c=0 worked first try), and **CP-SAT on the tiny 22-point residual → 112 in <30s**, independently re-verified from scratch (zero forbidden triples).

**The fact:** the bottleneck was never compute or solver strength. It was a missing **structural decomposition**. Search over the flat 729-point space saturated at ~80% of target; the right *coordinate* (slices) forced most of the object and left a trivial residue.

---

## 2. The three failure modes we actually exhibited (the structural lessons)
1. **Mistook the example for the objective.** We were told "even finding 112 isn't the point — build the mixture"; we then spent hours grinding 112. *When a concrete salient metric is on the table, do not let it become the goal if the goal is a capability.*
2. **Could only win with an answer key.** Every "win" was measured against something *already known* — reproduce 112, check vs the optimum, re-derive a *published* structure. That is **retrieval, not discovery**. On a truly open frontier there is no key — only the verifier. The reflex to need a key is the deepest limit.
3. **Read a plateau as "search harder," not "wrong weapon."** Nine method-families capped ≤90 against a known 112. *Heterogeneous methods agreeing on a ceiling below a known/target bound is the signature of a STRUCTURAL gap, not a tuning gap.* We kept buying compute instead of switching weapon-class — even after a method returned a result *with a proof of its own maximality* (exhausted by definition).

---

## 3. The exact weapons (the arsenal) — with cost, mode, and HONEST status
**Armor (always-on, free, never removed):** checker-first verification · honesty veto (known-vs-open) · routing · **never trust a weapon's self-report** (we re-verified 112 from scratch). Spine = v3 (`BOX_V3.md`).

| # | Weapon | Fires when (signature) | Cost tier | Verifier | Status |
|---|---|---|---|---|---|
| **W1-fetch** | **Structure Acquisition — FETCH** (retrieve a published construction/decomposition) | target is a **known/proven** object (named optimum, named structure) | **T0 (cheapest)** | machine-check the instantiation | ✅ **validated** (112) |
| **W1-derive** | **Structure Acquisition — DERIVE** (discover the decomposition *yourself*: small-exact→pattern, symmetry/invariant, recursion) | structure is **unknown / open** — nothing to fetch | T2–T3 | machine-check | ⚠️ **ASPIRATIONAL — unproven** (the real frontier capability) |
| **W2** | **Exact solver** (CP-SAT/ILP) on a **small/structured** subproblem | a structural prior has isolated a small residual | T2 | the solver's solution, re-checked | ✅ validated (22-pt residual; n≤5 optima 20/45) |
| **W3** | **Metaheuristic search** (greedy / ILS / LNS / SA) | quick baseline; no structure yet | T1 (cheap) | machine-check | ✅ validated — **reaches ~70–80%, then plateaus** |
| **W4** | **FunSearch / propose-verify** (LLM proposes *structural strategies*, machine kills the wrong ones) | **open ground**, want *new* structure | T3 (expensive) | machine-check each candidate | 🟡 partial (pushed n=6 to 96 earlier; the open-ground weapon) |
| **W5** | **Cross-model construction agent** (LLM builds the object from a given structure, machine verifies) | structure known, instantiation is fiddly | T2 | independent re-verify (don't trust self-report) | ✅ validated (built 112; honestly failed at 90 without structure) |
| **W6** | **Retrieval-grounding** (fetch a real-world value/fact) | a fetchable fact is load-bearing | T0 | the fetched source | ✅ validated (v2.2 checker) |

**Cost ladder (the efficiency lesson):** 64 (free) → 80 → 88 → 89 (search) → **112 (structure + small exact solve)**. ~70% is free; the last fraction costs exponentially *if you stay in search* — but is *cheap* once you have structure. **Draw structure EARLY, not as the last resort.**

---

## 4. The decision procedure — DO / DON'T

### Classify at intake (this picks the first weapon)
- **KNOWN-RESULT REPRODUCTION** (named optimum / named object) → **W1-fetch FIRST**, then W2 on the residual. Search is gated *behind* a structure attempt.
- **OPEN-FRONTIER DISCOVERY** (no known answer) → **W1-derive + W4**, verifier-only. There is no answer key; the construction *is* the result.
- **JUDGMENT / non-checkable** → armor only (panel/abstain). No weapon applies.

### DON'T
- ❌ **Don't make the salient number the goal** when the goal is the capability/mixture. (Our #1 sin.)
- ❌ **Don't escalate search/compute** once ≥2 method-families plateau below a known/target bound — that's a *structural* gap. Switch weapon-class.
- ❌ **Don't keep grinding** a method that returned a result *with a maximality proof for its class* — it is exhausted.
- ❌ **Don't recall constructions from LLM memory** — ground in a source *or derive*; never assert from memory (it failed here).
- ❌ **Don't measure only against an answer key** — on open ground there is none; needing one is the trap.
- ❌ **Don't trust a weapon-agent's self-report** — re-verify independently, from scratch.

### DO
- ✅ **Hunt the structure first:** *"is there a coordinate along which most of the object is FORCED, not free?"* (slices, cones, products, symmetry orbits, invariants). Fetch it if known; **derive it** if not.
- ✅ **Solve small cases EXACTLY, then MINE them** for the structure (we had n≤5 exact and the 90 = 45-45-0 slice — the 45-45-22 idea was *latent in our own data*; we lacked the weapon to extract it, not the data).
- ✅ **Make structure-acquisition the cheapest, earliest rung** — before blind search. Instrument *time-to-first-structure-attempt* and penalize "long search before it" in E.
- ✅ **Compose the minimal efficient mixture;** escalate weapon TIER only as the bar demands; use permission-to-stop.
- ✅ **On open ground, let the verifier be the only truth;** every construction is a claim until machine-certified; report where it stalls plainly.

---

## 5. Honesty rules specific to weapons
- **Verifier-gated, always.** A weapon's output is a *claim*; only the machine check makes it real. We re-verified 112 from scratch (not the agent's code, not even our own verifier first).
- **Known-vs-open veto (non-waivable).** Reproducing a *known* optimum (112) is honest reproduction; it is **never** "solving an open problem." On *open* frontiers, never claim a record without the machine-certified object — and never claim to have *closed* an open problem.
- **Agreement is a risk, not safety** (C20/P6). Method-families agreeing on a ceiling = shared blind spot → switch weapon, don't add more of the same.
- **Mark validated vs aspirational.** W1-fetch, W2, W3, W5, W6 are validated this session. **W1-derive (independent discovery) and W4 at the open frontier are UNPROVEN** — the next real test (n=7 > 236, no answer key) measures whether the box can *discover*, not just *retrieve*. Likely outcome stated up front: we may not beat the record; the deliverable is a working discovery-orchestrator + an honest measurement of how far no-answer-key discovery gets.

---

## 6. Pointers (the detailed docs this README sits above)
- `Next/BOX_ARMOR_WEAPONS.md` — the full architecture (armor + weapon registry + router + cost model).
- `Next/WEAPON_NOT_ARMOR_2026-06-09.md` — the PI correction + the cap-set cost ladder.
- `Next/RETROSPECTIVE_INSIDE_THE_BOX_2026-06-10.md` — the audited retrospective (what we lacked, the trip-wires).
- `Next/benchmarks/math/R1_CAPSET_2026-06-09.md` — the full cap-set run log (every method + the 112 build).
- `Next/benchmarks/math/build_112_pathA.py`, `cap_n6_size112.json` — the validated weapon in action.

> **The single sentence to remember:** *When a hard problem won't yield, the move is not a bigger hammer — it's finding (fetching OR deriving) the structure that makes the search small. Armor keeps you honest; weapons let you break through; the verifier is the only judge.*
