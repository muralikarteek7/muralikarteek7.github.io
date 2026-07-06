# Expanding Frontiers
*Where the box stops defending and starts breaking through.*

This folder holds the program's **offensive capability** — the **weapons** (special-purpose, priced
math/computational methods that *produce* a new machine-verified object) as opposed to the **armor** (the
always-on backbone that keeps output honest/verified). The thesis the PI set:

> **Box = ARMOR (defense: safe output) + WEAPONS (offense: produce a *new* verified object).**
> "Verified" ≠ "new". The verifier is the only thing always true. Find (fetch **or derive**) the structure
> that makes a hard search small — that is the move, not a bigger hammer.

The full doctrine (what to do / not do, the arsenal, honesty rules) lives in [`WEAPONS_DOCTRINE.md`](WEAPONS_DOCTRINE.md).

---

## ⭐ HOW TO DO FRONTIER WORK — the method (rebuilt & audited 2026-06-10)

*The old doctrine was armor-heavy: it taught the box to stay honest, not to break through. After a session where
that produced a defensive "honest negative" instead of an attack, the method was rebuilt as three grounded,
cross-model-audited parts. **Read these before attacking any frontier:***

1. **[`SURVEY.md`](SURVEY.md)** — *the ways frontiers actually fall*, grounded in real records (FunSearch,
   AlphaEvolve, AlphaTensor/Dev, AlphaProof; probabilistic method, symmetry, Edel lifting, LP/polynomial bounds,
   SAT, metaheuristics) + the honesty failures (the OpenAI-Erdős retrieval-vs-discovery contrast).
2. **[`THEORY.md`](THEORY.md)** — *a parameterized theory for many fields*: read any problem as a 7-coordinate
   state vector (κ checkability, α asymmetry, σ symmetry, ρ recursion, λ abstraction, δ gap, β/τ budget); a
   weapon-selection map with an explicit dominance order; three falsifiable laws.
3. **[`ALGORITHM_AND_WEAPONS.md`](ALGORITHM_AND_WEAPONS.md)** — *the runnable attack loop* + the weapon registry
   (W-EVOLVE, W-LIFT, W-SYMM, W-LP/POLY, W-SAT, W-PROB, W1-fetch) + the anti-self-deception gate.

**[`AUDIT.md`](AUDIT.md)** — the cross-model red-team of the above and its honest verdict: *"better armor + a
real first offensive weapon (W-EVOLVE v0, built & run → honest negative on n=7) — NOT yet a validated
frontier-breaking method."* Open defects (unbuilt W-LIFT, the unverified 236 anchor, no cold-test validation) are
listed there, not hidden. **The honest status: an audited design, partially implemented — 2.5 of 7 weapons built.**

---

## Case study 1 — the cap-set problem ([`cap_set/`](cap_set/))
**Problem.** A *cap set* in F₃ⁿ is a set of n-tuples over {0,1,2} with **no three distinct points summing to
0 (mod 3)** — the math version of the card game *Set*. Goal: find the largest one. Easy to *state*, easy to
*check*, brutally hard to *find* (for n=6 the search space of subsets is ~10²¹⁹). It is a perfect, un-bluffable
arena: a tiny verifier certifies any claim, so an AI cannot fake a result.

**What happened (the lesson this whole folder exists for).**
- **Pure search saturated at ≤90 / 112** (greedy 80, ILS 88, exact CP-SAT 89, LNS, symmetry-frame 41). Heavy
  compute, no breakthrough — the "bigger hammer" trap.
- **Structure cracked it.** A 112-cap has a **45-45-22 slice decomposition** (Potechin 2008). Using a verified
  45-cap as a slice + an exact solver on the tiny 22-point residual → **112 in <30s**, the *proven maximum*.
- The structure was even **latent in our own data** — we lacked the *weapon to extract it*, not the data.

**The weapon born here — "Structured Construction" (two modes):**
| mode | how | when | status |
|---|---|---|---|
| **fetch** | retrieve a published decomposition, instantiate, verify | the object is *known* | ✅ validated (n=6 → 112) |
| **derive** | discover the decomposition yourself (first-principles / small-case mining / symmetry) | the object is *open* | 🟡 real but ceiling below frontier |

**Results (all machine-verified; independently re-checked from scratch, not the agent's self-report):**
| n | what we built | size | reference | honest verdict |
|---|---|---|---|---|
| 4 | exact solver | **20** | max=20 | ✅ proven optimum |
| 5 | exact solver | **45** | max=45 | ✅ proven optimum |
| 6 | fetch-mode (Potechin structure) + exact residual | **112** | **max=112** | ✅ **proven maximum reproduced** (not an open-problem solve) |
| 7 | **derive-mode** (product `cap(1)·cap(6)=2·112`, no paper) | **224** | LB=236 | 🟡 +24% over blind search; **provably maximal in the product class** (3 strong weapons stall here) |
| 7 | **fetch-mode** — Calderbank–Fishburn (1994) construction transcribed from the paper (`build_236.py`) | **236** | =LB 236 | ✅ **VERIFIED 236-cap** (triple-checked incl. cross-model). Honest **reproduction** of the known LB, **not a record / not >236** |

**The honest frontier verdict (n=7):** derive/search **provably plateaus at 224** (product cap; three strong,
heterogeneous weapons — 20-min CP-SAT, 6.3M-iter SA, evolution — all stall there). Reaching **236** required the
*structure*, not search: with the **Calderbank–Fishburn 1994 paper** (placed by the PI), the construction was
transcribed and a **236-cap was built and machine-verified** (`build_236.py`, triple-checked incl. cross-model) —
our artifact **224 → 236**. This is honest **fetch-mode reproduction** of the known lower bound, **not a record,
not solving an open problem** (the open frontier is a certified cap **>236**, which no method — incl. FunSearch —
has reached). The clean lesson: *on a known target, fetch the structure; search alone stalls below it.*

**Update 2026-06-10 — the 224 plateau, characterized (machine-verified, honest negative):** a fresh attack
(point-extension, slice-translation, the shrink-trade-off, and a full joint 3-slice CP-SAT) confirmed 224 is a
*sharp* local optimum — four independent methods all return exactly 224, none reaches 225. We now have the
mechanism (two full 112-caps saturate all 729 transversal points; the one-full-slice trade-off is exactly 1:1)
rather than just the number. Still **no record, no open-problem claim** (224 < known LB 236 < UB ≤288, fetched
& cited). Full log + reproduce steps: [`cap_set/N7_PLATEAU_2026-06-10.md`](cap_set/N7_PLATEAU_2026-06-10.md).

---

## Implementation ([`cap_set/`](cap_set/)) — self-contained, reproducible
| file | what |
|---|---|
| `capset_verify.py` | the **independent machine verifier** + known maxima/lower-bounds (the ground truth) |
| `build_112.py` | the n=6 weapon: 45-45-22 construction → **verified 112** (`python3 build_112.py`) |
| `build_n7.py` | the n=7 derive-mode: product + exact slice-residual (`python3 build_n7.py product`) |
| `verified_caps_45_90.py` | verified 45-cap (n=5) and 90-cap (n=6) building blocks |
| `cap_n6_size112.json` / `cap_n7_size224.json` | the verified caps (explicit points) |

Reproduce / re-verify everything:
```
cd cap_set
python3 build_112.py                      # -> 112, valid
python3 build_n7.py product               # -> 224, valid
python3 -c "import json;from capset_verify import score;print(score([tuple(p) for p in json.load(open('cap_n6_size112.json'))['6']],6))"
```

---

## How to add the next frontier problem (the pattern)
1. Drop a **machine verifier** for the new object (like `capset_verify.py`) — no claim is real without it.
2. Classify: **known-result reproduction** (→ fetch structure first) vs **open-frontier discovery** (→ derive / FunSearch, verifier-only).
3. Find the **forcing coordinate / decomposition**; exact-solve the small residual.
4. **Independently re-verify** every result (never trust a weapon-agent's self-report). Mark validated vs aspirational.
5. Log honestly: known-vs-open veto, no record without the certified object.

*Candidates next:* Sidon sets / Golomb rulers (`Next/benchmarks/math/arena2_sidon_verify.py`), no-3-in-line,
and the genuinely-open cap-set frontiers (n=7 > 236, n=8) via FunSearch-style propose-verify.
