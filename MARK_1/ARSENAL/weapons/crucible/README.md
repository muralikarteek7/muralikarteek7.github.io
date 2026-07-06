# CRUCIBLE — the box's first META-WEAPON (a verifier red-team)

**Every other weapon trusts its gate. CRUCIBLE is the only thing that tests whether that trust
is earned.** It takes a weapon's frozen κ>0 gate (black-box) and tries to BREAK it.

## What it does
Four probe modes against a gate-under-test:
- **FALSE-ACCEPT** (needs an independent oracle): find `X` the gate ACCEPTs but an independent
  oracle proves WRONG — a gameable gate.
- **FALSE-REJECT** (needs an oracle): find `X` the gate REJECTs but is CORRECT — an over-strict gate.
- **METAMORPHIC** (no oracle): a meaning-preserving transform `T` where `gate(T(X)) ≠ gate(X)`.
- **ABSTAIN/CRASH** (no oracle): a malformed input where the gate silently ACCEPTs instead of
  abstaining loudly.

A **KILL** is a κ=1, re-runnable bug exhibit `{object, gate_verdict, oracle_verdict, transform}` —
a machine-checked proof the gate has a bug. It then becomes that weapon's permanent regression test.

## The honest ceiling (read this)
- **CRUCIBLE proves a gate BROKEN; it raises CONFIDENCE a gate is sound; it NEVER proves a gate
  sound.** Finding no counterexample under budget B is EVIDENCE, not PROOF (Dijkstra: *testing shows
  the presence of bugs, never their absence* — see `GROUNDING.md`). A no-kill is reported as
  `SURVIVED to budget` with the budget, the transform classes, the oracle coverage, and an explicit
  residual-risk statement. The words **"sound"/"proven" are machine-banned** from a survived report.
- **The oracle must be INDEPENDENT of the gate.** A false-accept hunt judged by the same engine is
  circular and proves nothing. Where no independent oracle exists, CRUCIBLE runs metamorphic +
  abstain/crash only, labeled PARTIAL — it does NOT claim differential coverage it didn't run.
  **Operator invariant (not machine-enforced):** the harness checks the independence FLAG and
  refuses the literal same-callable case, but it CANNOT prove an oracle is *methodologically*
  foreign — the operator must author it from a genuinely different mechanism.
- **CRUCIBLE's own oracle can be wrong.** A buggy oracle yields a SPURIOUS KILL. Every KILL is
  double-checked: the oracle is confirmed sane on a **control GRID** (≥3 known-good AND ≥3
  known-bad objects spanning the probed regime — a 2-point check is a confirmed cry-wolf hole, so
  too-few controls are REFUSED, not free-passed), and the exhibit is re-run.
- **A metamorphic flip only counts if the transform is meaning-preserving.** A fake transform that
  changes the object manufactures a spurious flip; with an independent oracle CRUCIBLE cross-checks
  that the transform preserved the object's ground-truth before shipping a metamorphic KILL.
- **A SURVIVED names the regime it probed.** The candidate stream spans decimal precision {0,1,2,3}
  × items {1,2,3}; a no-kill report states this regime so it is never read as broader coverage than
  the inputs actually exercised (a bug active only OUTSIDE the regime is named residual risk).
- **CRUCIBLE DECLINES κ=0 armor and guarded-κ verdicts** — you cannot adversarially falsify a
  judgment that never claimed an exact verifier.
- **It is not a capability boost.** Adversarial search + an independent oracle is deterministic
  machine work. The new value is the bug exhibit + the honest confidence/residual-risk label.
- **It is not above its own rules.** It ships with a gate-of-the-gate (`selftest_all.py`) that must
  catch a LOCATION-blind, SUBTLE planted bug, raise no false alarm on a good gate, refuse
  buggy/dependent oracles, and label no-kill as confidence — or it is theater. The selftest also
  carries permanent regressions for the cross-model auditor's confirmed exploits (cry-wolf oracle,
  fake transform, candidate-stream blindspots, trivial circularity).
  **Honesty (AUDIT A8):** the in-repo planted fixtures are *builder-authored* (location-blind, not
  author-blind). A true different-agent plant — the strongest test — is the cross-model auditor's
  responsibility (`AUDIT.md`); the builder does not claim to have met that bar.

## Coverage (named, never a blanket "all 12 survived")
Per the pre-committed scope table (`crucible_router.py`, matching kickoff §4a):
- **6 full-differential** (independent oracle): codeforge sortnet, psymetrix GRIM, trialguard GRIM,
  factharness quote, redcell CTF, frontier capset.
- **5 metamorphic-only** (no independent oracle): optima, proofsmith, reproml, symbolica, socius.
- **1 declined** (guarded-κ): econometrix walk-forward.

## Run it
```
cd MARK_1/ARSENAL/weapons/crucible
python3 selftest_all.py          # the gate-of-the-gate — must exit 0 before anything counts
python3 crucible_router.py summary
python3 demo_planted_bugs/run_demo.py   # the killer demo (predictions committed first)
```

## Demo result (2026-06-20, matches committed PREDICTION.md)
- (i) BLIND-planted false-accept in a COPY of the real codeforge sortnet gate (off-by-one in the
  0/1 sweep exponent) → **KILL exhibited**: network `[(0,3),(2,3),(1,3),(1,2),(1,3),(1,2)]` n=4,
  gate=ACCEPT, oracle=WRONG (genuinely fails on input `[1,0,0,1]`, a top-bit-set input the plant
  skips). Independently double-checked; the REAL codeforge gate correctly REJECTS the same network.
- (ii) planted GRIM metamorphic instability → **KILL exhibited**: `0.10`@n10 ACCEPT flips to REJECT
  under the Neff-invariant items-split.
- (iii)/(iv) the REAL, unmodified codeforge + psymetrix gates, all four modes → **CLEAN sweep**
  (SURVIVED to budget, no false alarm). No KILL was manufactured.

## Files
- `crucible_harness.py` — adapter + oracle + search + 4 modes + gate-of-the-gate `_selftest`.
- `crucible_router.py` — pre-committed scope table + routing + `_selftest`.
- `selftest_all.py` — runs both selftests; exits non-zero on any failure.
- `oracles/` — independent oracles (`sortnet_oracle.py` 0/1-enum, `grim_oracle.py` Fraction).
- `demo_planted_bugs/` — `PREDICTION.md` (committed first), `run_demo.py`, `RESULTS.md`, `results.json`,
  `planted_sortnet_gate.py` (the blind-planted gate copy).
- `SPEC.md`, `GROUNDING.md`, `AUDIT.md`.
