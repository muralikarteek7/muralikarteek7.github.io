# CRUCIBLE — SPEC (the box's first META-WEAPON: an adversarial verifier-prober)

*Built 2026-06-20 (BOX v5). Item #1 of the KIT-EXPANSION plan (gap G1). CRUCIBLE protects
all 12 existing weapons by attacking the BOX's single load-bearing unverified assumption:
that each weapon's κ>0 gate is actually exact and non-gameable.*

## 0. One-line definition
CRUCIBLE takes any κ>0 weapon-gate (black-box, via a uniform adapter) and either **EXHIBITS
a machine-checked object that breaks it** (false-accept / false-reject / metamorphic flip /
silent-pass — a **κ=1 KILL** that becomes that weapon's permanent regression test), or
reports it **SURVIVED to an explicit budget** with explicit oracle coverage + residual risk —
and **NEVER calls a gate "sound" or "proven" without an exhibit**, **NEVER judges a
false-accept with the same engine it is testing**, and **DECLINES to probe κ=0 armor**.

## 1. What CRUCIBLE IS / IS NOT
**IS:** an adversarial / differential / metamorphic tester of the box's OWN verifiers — a
real, established discipline (see `GROUNDING.md`: differential/metamorphic fuzzing finds real
soundness bugs in Z3/CVC5, GCC, LLVM). Our gates (hand-rolled Python verifiers, sympy/OR-Tools/
Lean wrappers, frozen test-suites) are exactly this bug class.

**IS NOT:**
- **NOT a soundness prover.** Finding no counterexample under budget B is EVIDENCE, not PROOF,
  the gate is sound (Dijkstra: *testing shows the presence of bugs, never their absence*). A KILL
  is a proof a gate is BROKEN; a non-kill only RAISES CONFIDENCE. "Survived N probes" is never
  upgraded to "verified sound."
- **NOT able to judge a gate with no independent oracle.** A false-accept hunt needs a second
  ground truth *different from the gate*. Where none exists → metamorphic + abstain/crash only
  (no oracle needed), labeled PARTIAL.
- **NOT a generator of weapons or results.** It produces bug exhibits + a confidence report.
- **NOT itself above suspicion.** It has a gate-of-the-gate (`selftest_all.py`): catch a planted
  bug AND raise no false alarm AND label no-kill as confidence, or it is theater.
- **NOT a capability boost.** Adversarial search + an independent oracle is deterministic machine
  work; the new value is the bug exhibit + the honest confidence/residual-risk label.

## 2. The four probe modes (KILL is always a κ=1 exhibit; absence-of-kill is confidence only)
| mode | needs independent oracle? | the κ=1 exhibit (a KILL) |
|---|---|---|
| **FALSE-ACCEPT** (the dangerous one) | **YES** (oracle ≠ gate) | `X` with `gate(X)=ACCEPT` ∧ `oracle(X)=WRONG` — proven by re-run |
| **FALSE-REJECT** | YES | `X` with `gate(X)=REJECT` ∧ `oracle(X)=CORRECT` |
| **METAMORPHIC** | NO | meaning-preserving `T(X)` where `gate(T(X)) ≠ gate(X)` |
| **ABSTAIN/CRASH** | NO | malformed input where the gate silently ACCEPTs instead of abstaining loudly |

Implemented in `crucible_harness.py` as `false_accept_hunt`, `false_reject_hunt`,
`metamorphic_hunt`, `abstain_crash_hunt`. Each returns a `Kill` (κ=1 exhibit) or a `Survived`
(confidence report with budget + transform classes + oracle coverage + residual risk).

## 3. The oracle-independence problem (the audit's sharpest catch)
A false-accept hunt is only as honest as its oracle being **genuinely independent of the
gate-under-test**. Non-waivable rules, folded into the harness:
1. **κ=1-SUB-SLICE ONLY.** CRUCIBLE probes only the exact, gate-self-declared κ=1 part of a
   weapon. Mixed-κ weapons → probe the exact slice; DECLINE guarded-κ verdicts (walk-forward
   DSR, causal E-value, model-fit) — a "false-accept" on a probabilistic verdict is undefined.
2. **THE ORACLE CAN BE WRONG TOO.** A buggy oracle yields a SPURIOUS KILL. So every KILL is
   double-checked: the oracle is confirmed SANE on a **control GRID** FIRST (`Oracle.is_sane()`),
   the exhibit is re-run. A KILL ships only when gate-vs-oracle disagree AND the oracle passed
   its grid. (The cross-model rule applied to CRUCIBLE itself.)
   - **CONTROL GRID, not 2 points (AUDIT A2 cry-wolf fix).** A 2-point sanity check (one good,
     one bad) is a confirmed hole: a subtly-wrong oracle that agrees on exactly those 2 points
     but lies elsewhere passes and ships a SPURIOUS kill on a GOOD gate. The oracle MUST register
     **≥3 known-good AND ≥3 known-bad controls SPANNING the probed regime** (e.g. GRIM: decimal
     precision {0,1,2,3} × items {1,2}). `is_sane()` **REFUSES** (does not free-pass) when too
     few controls are registered — "sanity not established" is treated as INSUFFICIENT.
3. **TRANSFORMS MUST BE MEANING-PRESERVING (AUDIT A11 fix).** A metamorphic flip only proves a
   gate bug if the transform genuinely preserves meaning. A fake transform (e.g. "add 1/n to the
   mean", which CHANGES the object) manufactures a SPURIOUS metamorphic kill on a GOOD gate. When
   an independent oracle is available, `metamorphic_hunt` cross-checks every candidate flip:
   the KILL ships only if `oracle.truth(obj) == oracle.truth(T(obj))` (the transform really is
   meaning-preserving on that pair); otherwise the flip is suppressed (it is the transform, not
   the gate, that is broken). Without an oracle, transform meaning-preservation is **caller-
   asserted** and the SURVIVED report says so (residual risk), or pass
   `require_oracle_meaning_check=True` to fail-closed.

The harness ENFORCES these: `false_accept_hunt`/`false_reject_hunt` raise if the oracle is not
`is_independent` (circularity rail), raise if `is_sane()` fails or the grid is too small
(spurious-kill rail), and refuse a literal same-callable oracle (trivial-circularity tripwire).

**OPERATOR INVARIANT (AUDIT A1 — NOT machine-enforceable).** The harness checks the
`is_independent` FLAG and refuses the trivially-circular *same-callable* case, but it **cannot
prove** that a `truth()` function is *methodologically* independent of the gate. A caller can
register `Oracle(is_independent=True)` that secretly re-derives the gate's own logic, pass the
control grid, and run a circular hunt. **This is a trust-the-operator invariant, not an enforced
guard** — the operator MUST author the oracle from a genuinely foreign mechanism (different
algorithm, different library, independent re-derivation). CRUCIBLE is a tool, not a proof system.

## 4. The per-weapon ORACLE registry + router (pre-committed scope, §4a)
`crucible_router.py` holds the PRE-COMMITTED scope table — for each of the 12 weapons, the κ=1
slice, the planned oracle, whether it is independent, and the modes. The router routes:
- weapon WITH an independent oracle → **all four modes** (full differential);
- weapon WITHOUT → **metamorphic + abstain/crash only** (partial coverage; false-accept would be
  circular);
- a κ=0 "gate" that is actually armor / a guarded-κ verdict → **DECLINE** (probe nothing).

Coverage (matches kickoff §4a exactly): **6 full-differential** (codeforge sortnet, psymetrix
GRIM, trialguard GRIM, factharness quote, redcell CTF, frontier capset) · **5 metamorphic-only**
(optima, proofsmith, reproml, symbolica, socius) · **1 declined** (econometrix walk-forward).
**No blanket "all 12 survived" — the buckets are named.**

## 5. The harness (built FIRST, gate-of-the-gate green before any claim counts)
- **Uniform adapter** (`GateAdapter`): wraps each gate's verdict fn behind `.verdict(obj) ->
  {ACCEPT|REJECT|ABSTAIN|ERROR}`. Black-box — CRUCIBLE never reads gate internals (a gate bug
  can't hide CRUCIBLE's eyes). A raised exception becomes ERROR (a crash IS a probe result).
- **Independent oracle** (`Oracle`): `truth(obj) -> CORRECT|WRONG|None`, with `is_independent`,
  `is_sane()` controls.
- **Search**: a deterministic seeded LCG mutator (no `hypothesis` available — the psymetrix/SPRITE
  fallback the kickoff sanctions; reproducible by design). An LLM-proposer would be 0%-trusted —
  every candidate is machine-checked by gate-vs-oracle; the model only *suggests where to look*.
- **Verdict + honest label**: `Kill` (κ=1) or `Survived` (banned-word-policed: `to_dict()` raises
  if "sound"/"proven"/etc. leak into a survived report).

## 6. Gate-of-the-gate self-tests (`selftest_all.py`, non-waivable)
Exits non-zero on ANY failure. The five required cases (kickoff §3):
- (a)/(b) **CATCH a SUBTLE planted false-accept** (off-by-one / a too-wide tolerance band — NOT a
  max-signal constraint deletion), **LOCATION-blind** (the SEARCH is not told where the hole is).
  **Honesty (AUDIT A8):** this fixture is *builder-authored*, so it is location-blind, NOT
  author-blind / different-agent — weaker than kickoff §3a. The stronger different-agent plant is
  the cross-model auditor's job (`AUDIT.md`).
- (c) **CATCH a planted metamorphic instability** (verdict flips under a meaning-preserving
  items-split / relabel).
- (+) **CATCH a planted silent-pass** on a malformed input.
- (d) **raise NO false alarm** on a KNOWN-GOOD frozen gate (false-accept/reject/metamorphic/
  abstain all SURVIVE).
- (e) **LABEL "no counterexample found" as CONFIDENCE, not PROOF** (machine-assert the report
  never contains "sound"/"proven" without an exhibit).
- (+) **spurious-kill rail** (a buggy oracle that fails its control grid is REFUSED) and
  **circularity rail** (a non-independent oracle is refused for a false-accept hunt).

**AUDIT REGRESSIONS (permanent, in `crucible_harness._selftest_audit_regressions`).** Each
reproduces a cross-model auditor exploit and asserts it is now BLOCKED:
- **A2 (cry-wolf):** a subtly-wrong oracle (lies on 3dp) is REFUSED — both the old 2-point form
  (too few controls) AND the full-grid form (fails a 3dp good control). No spurious kill ships.
- **A11 (fake transform):** a non-meaning-preserving transform ("add 1/n") that manufactures a
  flip when UNGUARDED is SUPPRESSED once the oracle arbitrates meaning-preservation.
- **A3 / A9 (candidate-stream blindspot):** a 1dp-only bug and an items≥2-only bug — both of which
  SURVIVED the old 2dp/items=1-only stream — are now CAUGHT. The candidate stream spans decimal
  precision {0,1,2,3} × items {1,2,3}; SURVIVED reports NAME the regime probed
  (`_grim_candidate_coverage()`) so a no-kill is never read as broader than the inputs.
- **A1 (trivial circularity):** a same-callable oracle is refused (deeper independence is an
  operator invariant, §3).
- **A10 (definite→abstain gap):** a DEFINITE→ABSTAIN flip under a meaning-preserving transform is
  SUPPRESSED by default (no false alarm) but CATCHABLE via `flag_definite_to_abstain=True`.

## 7. Honesty rails (non-waivable, §6 of kickoff)
- A KILL is a κ=1 exhibit; a non-KILL is CONFIDENCE, never a soundness proof (Dijkstra). Report
  budget + coverage + residual risk; the words "sound"/"proven" require an exhibit; a gate is
  never called "proven sound."
- The oracle must be INDEPENDENT of the gate; no oracle → metamorphic/abstain only, labeled.
- Found a bug ⇒ FIX the gate AND freeze the exhibit as a regression test in that weapon.
- DECLINE κ=0 armor AND guarded-κ verdicts.
- Every KILL is double-checked (oracle sane on controls first; exhibit re-run).
- Registry/dashboard discipline: a `SURVIVED to budget B` entry MUST carry the residual-risk
  statement verbatim; the word "sound" is banned from that field.
- No theater sweep: name which weapons got full differential vs metamorphic-only vs declined.

## 8. Deliverables map
`crucible_harness.py` (adapter + oracle + search + 4 modes + gate-of-the-gate `_selftest`),
`crucible_router.py` (pre-committed scope + routing + `_selftest`), `selftest_all.py` (runs
both, exits non-zero on any failure), `oracles/` (sortnet 0/1-enum, GRIM Fraction — importable
independent oracles), `demo_planted_bugs/` (committed `PREDICTION.md`, `run_demo.py`, exhibits +
survived reports), `SPEC.md` (this), `GROUNDING.md` (fetched premise + Dijkstra), `README.md`
(honest ceiling), `AUDIT.md` (cross-model red-team, auditor-filled).
