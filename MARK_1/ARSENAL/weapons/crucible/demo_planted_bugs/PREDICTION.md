# DEMO PREDICTIONS — committed BEFORE running run_demo.py

Date: 2026-06-20. Written by the CRUCIBLE builder (Opus 4.8) BEFORE `run_demo.py` was
executed. This is the demo-with-predictions discipline applied to CRUCIBLE: I commit
what I expect, THEN run, THEN compare. A wrong prediction is reported honestly, not
edited away.

The demo has FOUR parts, each mapping to a kickoff §5.4 demo requirement.

## Part (i) — BLIND-planted false-accept in a COPY of a REAL gate (kickoff 4.i)
A separately-authored copy of the REAL codeforge `verify_sorting_network` gate, with a
SUBTLE hole planted by a *different authoring pass* than the harness (the plant location
is NOT passed to the search). The hole: the exhaustive 0/1 sweep stops one mask short
(`range(1 << n - 1)` style off-by-one), so it MISSES the all-ones-ish failing input on
some networks -> it can ACCEPT a NON-sorting network.

The independent oracle = a from-scratch exhaustive 0/1 enumeration (foreign re-impl).

**PREDICTION (i):** CRUCIBLE's FALSE-ACCEPT hunt EXHIBITS a comparator-network `X` where
the planted buggy gate says ACCEPT (valid sorting network) but the independent oracle
says WRONG (it does NOT sort all inputs). A κ=1 KILL with `{object, gate_verdict=ACCEPT,
oracle_verdict=WRONG}`, re-runnable, oracle sane on controls first.

## Part (ii) — planted METAMORPHIC instability (kickoff 4.ii / §3c)
A copy of the GRIM gate whose verdict FLIPS under a meaning-preserving `items`-split
(Neff-invariant). A sound GRIM gate is invariant; the buggy one ignores `items`.

**PREDICTION (ii):** CRUCIBLE's METAMORPHIC hunt EXHIBITS a base object `X` and a
transform `T` (items-split) where `gate(X) != gate(T(X))` — a verdict-flip κ=1 KILL.

## Part (iii) — KNOWN-GOOD frozen gate -> NO false alarm (kickoff 4.iii)
Run all available modes against the ACTUAL, unmodified codeforge `verify_sorting_network`
gate (the real frozen artifact) and the ACTUAL psymetrix `grim` gate.

**PREDICTION (iii):** NO false alarm. Every hunt returns SURVIVED-to-budget with an
explicit residual-risk statement and the label "SURVIVED to budget" — and the report
contains NO "sound"/"proven" word. (If a real defect IS found here, that is a genuine
KILL on a shipped gate and I will report it as such, not suppress it — but my prediction
is the real frozen gates SURVIVE, because their obvious bug classes are already locked in
their own regression self-tests.)

## Part (iv) — the REAL-ARSENAL sweep (kickoff §5.3 / 4.iv)
Point CRUCIBLE at the κ=1 slices it has importable oracles for in this demo: the REAL
codeforge `verify_sorting_network` (full differential vs exhaustive 0/1) and the REAL
psymetrix `grim` (full differential vs from-scratch Fraction arithmetic). Run all four
modes on each. (FACTHARNESS/REDCELL/Frontier are full-differential in the scope table but
need a network fetch / committed-answer fixture / capset module respectively — out of
this demo's hermetic scope; the router records them as full-coverage targets.)

**PREDICTION (iv):** A CLEAN SWEEP on these two real gates is the most likely outcome
(the obvious historical bug classes — sorting-net off-by-one, GRIM float/precision — are
already locked in each weapon's regression self-tests). I predict 0 KILLs on the two real
gates, reported as SURVIVED-to-budget with full oracle coverage + residual risk. I will
NOT manufacture a KILL. If a real defect surfaces, I report it as a κ=1 exhibit and flag
it for that weapon's owner. Honest expected net: **2 planted KILLs caught (i, ii), 0 false
alarms (iii), 0 real-gate KILLs (iv) — a clean sweep on the live arsenal slices probed.**

## What would FALSIFY the demo (honesty rail)
- If the BLIND plant is NOT caught -> CRUCIBLE is theater (the meta-gate already guards
  this, but the demo must show it on a REAL-gate copy, not just the inline GRIM fixture).
- If the known-good real gate is flagged -> CRUCIBLE cries wolf (the worse failure).
- If any SURVIVED report contains "sound"/"proven" -> the labeling rail is broken.
