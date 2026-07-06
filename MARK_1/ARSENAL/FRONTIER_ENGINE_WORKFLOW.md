# The Frontier Construction Engine — v4 box, as a runnable workflow (2026-06-10)

*This is the de-novo construction engine (from the "what would it take" analysis) instantiated as a deterministic
multi-agent **Workflow**, routed through the **v4 model ladder** ([`../../MARK_0/01_box_versions/BOX_V4.md`](../../MARK_0/01_box_versions/BOX_V4.md)). It is
the answer to "make the workflow": the frontier method ([`THEORY.md`](THEORY.md) / [`ALGORITHM_AND_WEAPONS.md`](ALGORITHM_AND_WEAPONS.md))
turned into an executable pipeline that proposes, machine-gates, and cross-model-audits new constructions.*

## What it does (one line)
**Fable proposes structural ideas → a code agent builds them and runs the FROZEN verifier (the $0 machine gate) →
a different model audits any survivor that beats the record.** Pointed at the open cap-set n=7 frontier (>236).
No record is claimed unless a strictly-larger cap **certifies and survives independent audit.**

## The three phases, each mapped to a v4-ladder rung
| phase | v4 ladder rung | engine | why |
|---|---|---|---|
| **Propose** | *genuinely un-executable hard / novel construction* | **Fable 5** | the creative leap (representation + canonical pieces + non-affine relation) is the one slice that can't be executed; measured +67pts vs Opus there. 6 distinct creative lenses = island diversity. |
| **Build + Verify** | *machine-checkable → EXECUTE ($0) · code → any tier* | **Sonnet writes code, the FROZEN `capset_verify.py` decides** | the gate, not the model, makes output safe — every proposal is built and run; only verifier-passed sizes count. Self-reports are never trusted. |
| **Audit** | *adversarial audit → a frontier model ≠ the generator (C8)* | **Sonnet ≠ the Fable generator** | any >236 claim is re-verified from scratch with an *independent* brute-force check (not `capset_verify`), plus gaming detection. Honesty gate. |

## The de-novo principles encoded into the proposers (so they generate, not transcribe)
Each Fable proposer is handed the three creative levers the ablation proved load-bearing, and told to move *past* them:
1. **Representation** — propose the coordinate system in which *your* object is short (2-coord slice → 3×3 grid;
   group action; quadratic form), not raw vectors.
2. **Obstruction-inversion** — known dead-ends ("two full 112-caps saturate the sumset") become *design targets*
   ("engineer slices whose sumset *misses* a chosen structured set").
3. **Canonical pieces** — build only from interlocking canonical objects (parity cosets, weight classes, group
   orbits, quadrics, involutions), never random sets — because the ablation showed random substitutions break it.

The six lenses: `involution-vary · residual-grow · two-coord-slice · four-block · quadric · parity-stack`.

## Honesty rails (non-waivable, built into the script)
- The verifier is **frozen and authoritative**; proposers only hypothesise, the machine decides.
- A claim leaves the engine only if it is **certified by the gate AND confirmed by an independent cross-model
  brute-force audit AND >236**. Reproduction (≤236) is labelled as such; **no record, no promotion, no
  open-problem claim** otherwise.
- Expected honest outcome: **no >236** (the frontier has resisted everyone, incl. FunSearch). The deliverable is
  the *operational engine run end-to-end through the v4 ladder* + an honest measured result — not a promised record.

## Reproduce / iterate
Launched via the Workflow tool (run `wf_6a58dc41-b83`). Script persisted under the session's
`workflows/scripts/`. Re-invoke with `{scriptPath, resumeFromRunId}` to iterate; same script + args → cached.

## RESULT (run `wf_6a58dc41-b83`, 2026-06-10 — 12 agents, ~540k tokens, ~77 min)
End-to-end through the v4 ladder. 6 Fable proposals → Sonnet build+frozen-gate → audit. Machine-gated sizes:

| lens (Fable idea) | certified size | valid |
|---|---|---|
| **quadric** (quadric/character twist) | **236** | ✅ — *reached the record by a different lens than C-F* |
| twin-lines (extendable-collection variant) | **234** | ✅ — near-miss |
| z3-orbit-quotient | 216 | ✅ |
| quadratic-offset parity grid | 174 | ✅ |
| orbit-twisted / z4-parity-tower | 0 | ❌ (invalid — gate rejected, as it should) |

- **best certified = 236; claims >236 = 0; audited records = 0.** Independently re-verified (the 236 and 234
  re-run through the frozen verifier post-hoc by the orchestrator).
- **Honest verdict: a NEGATIVE on the open >236 frontier — the expected outcome.** Even a Fable-proposed,
  6-lens, verifier-gated engine matched the 1994 record (236, by a *different* construction lens) but did **not**
  cross it. No record, no promotion, no open-problem claim. *(The frontier has resisted everyone incl. FunSearch;
  this is consistent, not a failure of the engine — the engine worked: it proposed, gated out 2 invalid bluffs,
  and certified real caps up to the record.)*
- **What the engine demonstrably DID:** generated 4 *valid, distinct, machine-certified* cap constructions from
  scratch (incl. an independent route to 236), and the **gate caught 2 invalid proposals** — i.e. the v4 armor
  worked exactly as designed (proposers bluff; the machine decides; nothing false survived).
- **What it did NOT do:** the de-novo creative leap past the record — confirming the honest ceiling from the
  "what would it take" analysis: the engine raises the probability of a new idea, it does not guarantee it.

## v1/v2 EXECUTABLE ENGINE (Fable-outage-robust rebuild, 2026-06-10)
With Fable 5 down (rerouted to Opus, unreliable on the un-executable creative slice at 0.33), the box's #1 move
is to **make the creativity executable**. So the engine was rebuilt as a **parameterized construction family the
MACHINE searches** — no model in the loop, outage-proof. Files: `cap_set/frontier_engine.py` (v1), `frontier_engine_v2.py` (v2).
- **The construction:** slice 𝔽₃⁷ by coord-0 into A,B,C ⊆ 𝔽₃⁶; valid iff each a cap and no a+b+c=0 transversal,
  i.e. C must avoid `forbidden = −(A+B)`. **The executable inversion (the move C–F did by hand):** for *every*
  (A,B), take **C = the largest cap fitting the hole 𝔽₃⁶∖forbidden** (greedy + CP-SAT). |hole-cap|>12 ⇒ >236.
- **Validated:** the canonical C–F instance is recovered exactly — hole=12, |C|=12, **total=236, verifier-valid**.
- **Searched:** 24 block-family instances (v1) + **180 alpha↔beta relations** (v2: parity cosets × circulant
  widths × coordinate-permuted involutions), each gate-certified.
- **Finding (machine fact, carefully scoped):** **every relation in this family leaves a hole of exactly 12** →
  none can carry a residual >12 → the family is pinned at **236**. The "12" is rigid here. ⚠️ **Scope: this is
  *this construction family* (block-circulant 112-caps + parity-coset core + swap/permutation relations), NOT a
  theorem about all 𝔽₃⁷ caps.** A genuinely different representation (balanced ~79+79+78 slices; a 2-coordinate
  9-cell slicing) is untested and is the next family to wire into the engine.
- **Honest status:** the weapon is **ready, validated, reusable, and outage-robust** — it would surface any >236
  in its search space instantly. It robustly confirms 236 as *this family's* ceiling. **No record, no >236, no
  open-problem claim.**

## 2-COORDINATE representation — CHECKED, negative (`cap_set/twocoord_engine.py`, 2026-06-10)
The de-novo lever was "switch representation," so the 2-coord (3×3 = 9-cell, 𝔽₃⁵ per cell) family was the
honest next shot. Built correct (each cell a cap; every AG(2,3) line of cells transversal-free), gate-certified.
- **2-coord product baseline = 180** (a cap in AG(2,3) is ≤4 cells × 45-cap; verified valid). Structured
  translate-extension added **zero** further cells → stays **180**.
- **Verdict: this representation STARTS BEHIND the 1-coord C–F (180 < 236) and does not climb in reachable
  search.** *We are NOT near a breakthrough* — recorded against the in-the-moment intuition that we were. Beating
  236 remains genuinely open (unbeaten by anyone incl. FunSearch). A *sophisticated* 2-coord extended-product
  could in principle do better, but that is the open research problem, not a quick search away.
