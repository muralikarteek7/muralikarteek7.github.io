# RESEARCH — the Mark 1 workspace (how we research now)

The armor era ran on a four-stage ladder (Previous → Present → Next → Legacy) plus `RATCHET.md` and a long
`RESUME.md`. That apparatus built the box up to v5.2 and is now **frozen in `MARK_0/`** (the complete record).
The program has grown past it: we now have armor **+ 12 weapons + 8 kit + a helmet**, organized as the Mark 1
suit. This folder is the **clean, forward workspace** for the expanded program.

## Phase status
- **Phase 1 — build the suit: COMPLETE.** Armor (always-on) + the 12-weapon arsenal + the 8-piece kit + the
  helmet (University Mode) + the v5.1/v5.2 efficiency/honesty options. The three products are at **v1.0**.
- **Phase 2 — sharpen & expand: ON HOLD** (by operator decision, until the reorg settles). See [`backlog/`](backlog/).

## The three living documents (the current truth — kept short on purpose)
| File | What it holds |
|---|---|
| [`STATE.md`](STATE.md) | where the program actually stands today (version, ratchet position, what's paused) |
| [`RULES.md`](RULES.md) | the non-waivable rules (the ≥10% promotion bar, the research flow, the honesty rails) |
| [`backlog/`](backlog/) | the on-hold next ideas (ENCLOSE weapon, CRUCIBLE hardening, the helmet keystone gap) |

## How we research now (the loop, unchanged in spirit, cleaner in form)
1. **Stand on the suit.** Don't rebuild — pick up the live system and advance one piece.
2. **Build → benchmark → update**, repeated, with **non-circular** measurement (real A/B + ablation, machine or
   cross-model truth, never self-report).
3. **Break only at the ≥10% bar** (`RULES.md`). Below it, it's a point release, not a promotion.
4. **Prove on the products** (`../../Artifacts/`) before any promotion — never regress an artifact's scorer.
5. **Honesty gates everything** — report negatives, claim no win without proof, no open-problem-solve claims.

## What goes where
- A **new weapon / kit piece** → built in `../ARSENAL/`, registered in `../ROUTER/WEAPON_REGISTRY.json`.
- A **box-version change** → spec in `../SPEC/`, state updated in `STATE.md`, rules in `RULES.md`.
- **Measurement runs** → kept as dated evidence; the historical measurement layer is archived in
  `MARK_0/04_benchmarks/`.

> The full lineage (every prior box version, the ratchet history, the evolution log, all old benchmarks) lives
> in `MARK_0/` with a `MOVE_LOG.md` decoder. Read it for *how we got here*; read this folder for *where we are*.
