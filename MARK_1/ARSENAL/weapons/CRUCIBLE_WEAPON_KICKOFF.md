# KICKOFF — build the META-WEAPON: CRUCIBLE (adversarial verifier-probing) for the v5 box
*Paste everything below into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written
2026-06-20. CRUCIBLE is item **#1** of the KIT-EXPANSION plan (`Next/KIT_EXPANSION_PROPOSAL.md`, §5 G1) — it is
the highest-leverage build because it protects **all 12 existing weapons** by attacking the BOX's single
load-bearing unverified assumption: that each weapon's κ>0 gate is **actually exact and non-gameable.***

*Hardened 2026-06-20 after an independent Sonnet audit (verdict READY-WITH-FIXES) caught a real circularity — the
fixes are folded in: §1a (oracle-independence is genuine for only ~5 of 12 gates; the rest are metamorphic-only),
§3 (BLIND + SUBTLE planted-bug self-tests, not just a max-signal plant), §4a (a pre-committed per-weapon scope
table), and the κ=1-sub-slice-only / decline-guarded-κ rule.*

---

You are building **CRUCIBLE**, the box's first **META-WEAPON**: a verifier red-team that takes a weapon's FROZEN
gate and **tries to break it** — to exhibit an object the gate ACCEPTS but is independently-and-exactly WRONG (a
false-accept / a gameable verifier), or one the gate REJECTS but is exactly CORRECT (a false-reject), or a
meaning-preserving transform of a known-good object that **flips** the verdict (a metamorphic bug), or a malformed
input that makes the gate **silently pass** instead of abstaining. **Every other weapon trusts its gate; CRUCIBLE
is the only thing that tests whether that trust is earned.** Work BOX-style: plan → produce → **verify
INDEPENDENTLY** → ground → be honest; **no win without proof; "we tried hard and didn't break it" is CONFIDENCE,
never a soundness PROOF.**

## 0. ORIENT — read first (in order)
`CLAUDE.md`, `RESUME.md`, **`Next/KIT_EXPANSION_PROPOSAL.md`** (this is item #1 / gap G1; read §0 the honest goal,
§5 G1, §7 build order), **`Next/BOX_V5.md`** (the κ-router — CRUCIBLE is a meta-weapon with a **κ=1 KILL path** and
a **confidence-only NO-KILL path**; never conflate the two), the registry `Next/WEAPON_REGISTRY.json` (note there
is no W-entry yet — you will add one), then the
two cleanest existing weapons as **templates** (`symbolica/`, `optima/` — `SPEC.md`, the frozen gate +
`selftest_all.py`, the router, `demo_*/` with committed predictions, `AUDIT.md`). **Crucially, read the GATE of
every weapon you will probe** — each has a `*_gate.py` / `*_verify.py` with a public verdict function and a
`_selftest()`. CRUCIBLE consumes those gates as its targets.

## 1. THE HONEST FRAMING — what CRUCIBLE IS and IS NOT (do not skip)
**IS:** an **adversarial / differential / metamorphic tester of the BOX's own verifiers.** This is a real,
established discipline that finds real soundness bugs in production checkers — **GROUND it, don't assert** (see §4):
metamorphic + differential fuzzing found **1,500+ bugs (400+ soundness) in Z3/CVC5**; differential testing
(CSmith) found hundreds of compiler bugs; EMI metamorphic testing found **>1,000 GCC bugs**. Our gates
(hand-rolled Python verifiers, sympy/OR-Tools/Lean *wrappers*, frozen test-suites) are exactly this bug class.

**The sharp, κ=1 half (the genuinely-new value):** when CRUCIBLE exhibits an object `X` where the
**gate-under-test** says ACCEPT but an **independent reference oracle ≠ that gate** says WRONG (or vice-versa),
that disagreement is a **machine-checked PROOF the gate has a bug** — a falsification by exhibit. Non-gameable:
you can re-run both and see the contradiction. This is the cap-set-verifier *of the verifiers.*

**IS NOT:**
- **NOT a soundness prover.** **Finding no counterexample under budget B is EVIDENCE, not PROOF, that the gate is
  sound** (testing ≠ verification; exactly SPRITE's "not found ≠ impossible" rail). CRUCIBLE can PROVE a gate
  BROKEN (exhibit) but can only ever RAISE CONFIDENCE that a gate is sound. **Never upgrade "survived N probes"
  to "verified sound."** Report the budget, the transform classes tried, and the residual risk.
- **NOT able to judge a gate with no independent oracle.** A false-accept hunt needs a **second ground truth
  different from the gate** (brute-force on small instances; a different exact method; exhaustive enumeration; a
  different solver). Where no independent oracle exists, CRUCIBLE can still do **metamorphic** and **abstain/crash**
  probing (which need no oracle) but **must NOT claim differential coverage it didn't run.**
- **NOT a generator of weapons or results.** It produces **bug exhibits + a confidence report**, nothing the
  probed weapon would call a result. It is offense pointed *inward* — at our own immune system.
- **NOT itself above suspicion.** CRUCIBLE has its own gate-of-the-gate: it must CATCH a deliberately-planted
  verifier bug AND raise NO false alarm on a known-good verifier (§3). A meta-verifier that can't catch a planted
  hole is theater.
- **NOT a capability boost.** Adversarial search + an independent oracle is deterministic machine work (the
  "execute, don't guess" rung). The new value is the **bug exhibit + the honest confidence/residual-risk label.**

## 1a. THE ORACLE-INDEPENDENCE PROBLEM (the audit's sharpest catch — read before §2)
The FALSE-ACCEPT hunt is only as honest as its oracle being **genuinely independent of the gate-under-test.** The
naïve plan fails for ~half the arsenal, because several gates are *already* multi-method cross-checks:
- **SYMBOLICA's gate IS multi-method agreement** (symbolic + mpmath + scipy/series). A "3rd method (series vs
  quadrature)" is **already one of its certificate legs** — re-running it is circular and shares any common
  special-function/library blind spot. → SYMBOLICA gets **metamorphic + abstain/crash only**, UNLESS a truly
  foreign engine is available (e.g. a different CAS / arbitrary-precision lib not used by the gate). Say which.
- **OPTIMA's gate already runs exhaustive enumeration + Held-Karp/Hungarian** as its own certificate. CRUCIBLE's
  "brute-force oracle" IS that mechanism → not independent. A genuine oracle = a **separately-authored solver**
  (e.g. PuLP→GLPK, not OR-Tools) + an independently-coded dual-feasibility check. If unavailable → metamorphic-only.
- **Genuinely independent oracles DO exist** for: CODEFORGE sorting-nets (exhaustive 0/1 enumeration is foreign to
  the synthesis engine); PSYMETRIX/TRIALGUARD GRIM (re-implement the exact Fraction arithmetic from scratch);
  FACTHARNESS quote/number (a second fetch + a different text extractor); REDCELL CTF (`flag==expected` is exactly
  independently checkable). These get **full differential** false-accept hunting.

**Two non-waivable rules this forces (fold into the SPEC):**
1. **κ=1-SUB-SLICE ONLY.** CRUCIBLE probes only the **exact, gate-self-declared κ=1** part of a weapon. For
   mixed-κ weapons it probes the exact slice (GRIM arithmetic, feasibility re-check, quote-substring) and
   **DECLINES the guarded-κ verdicts** (ECONOMETRIX walk-forward DSR, SOCIUS causal, P-MODEL fit) — a "false-accept"
   on a probabilistic verdict is undefined and can't be a κ=1 KILL. Declining κ=0 armor AND guarded-κ is honest scope.
2. **THE ORACLE CAN BE WRONG TOO.** A bug in CRUCIBLE's own oracle yields a **spurious KILL** (declaring a sound
   gate broken). So every KILL is **double-checked**: the exhibit is re-run, and the oracle's verdict on a *known-good*
   object is confirmed correct first. A KILL ships only when gate-vs-oracle disagree AND the oracle is independently
   sane on controls. (This is the cross-model rule applied to CRUCIBLE itself.)

## 2. THE FOUR PROBE MODES (the KILL is always a κ=1 exhibit; absence-of-kill is confidence only)
| mode | needs an independent oracle? | what it produces | the κ=1 exhibit (a KILL) |
|---|---|---|---|
| **FALSE-ACCEPT HUNT** (the dangerous one) | **YES** (oracle ≠ gate) | a gameable-gate exhibit | `X` with `gate(X)=ACCEPT` ∧ `oracle(X)=WRONG` — proven by re-run |
| **FALSE-REJECT HUNT** | YES | an over-strict-gate exhibit | `X` with `gate(X)=REJECT` ∧ `oracle(X)=CORRECT` |
| **METAMORPHIC** (no oracle needed) | NO | a verdict-instability exhibit | a meaning-preserving transform `T` of a known-good `X` where `gate(T(X)) ≠ gate(X)` (relabel/reorder/rescale/reparametrize/refactor) |
| **ABSTAIN/CRASH** (robustness) | NO | a silent-failure exhibit | a malformed/degenerate/adversarial input where the gate **silently passes or crashes** instead of abstaining loudly |

The **metamorphic** mode is the workhorse where no second oracle exists — it is exactly how SYMBOLICA's own
branch-cut skip-bug *would* have been caught (a sign-flip transform `x→−x` flips a verdict that should be
invariant), and how the false +25pp in PROOFSMITH/CODEFORGE leaked. CRUCIBLE makes finding that class **systematic
instead of lucky.**

## 3. THE KEY ENGINEERING PROBLEM — the harness + the gate-of-the-gate, built FIRST
Build the **probe harness FIRST**, gate-of-the-gate green before any "weapon X is sound-to-budget-B" claim counts:
1. **A uniform gate adapter.** Wrap each target weapon's verdict function behind one interface
   `probe_target.verdict(obj) -> {ACCEPT|REJECT|ABSTAIN|ERROR}`. CRUCIBLE never reads the gate's internals — it
   probes it black-box (so a gate bug can't hide CRUCIBLE's eyes).
2. **A per-weapon INDEPENDENT ORACLE registry.** For each probed weapon, register a ground truth **methodologically
   different from the gate**: OPTIMA → brute-force/Held-Karp on small instances; SYMBOLICA → a 3rd method
   (series vs quadrature) at higher precision; CODEFORGE sorting-nets → exhaustive 0/1; PROOFSMITH → the Lean
   kernel itself is near-oracle, so probe the **wrapper/axiom-scan**, not the kernel. **If no independent oracle:
   metamorphic + abstain/crash modes only, and SAY SO.**
3. **The search.** Adversarial generation toward a disagreement: structured mutation (type-aware, near a known
   boundary), metamorphic transforms, malformed/degenerate inputs, and an LLM-proposer **0%-trusted** (every
   proposed counterexample is machine-checked by gate-vs-oracle; the model only *suggests* where to look).
4. **The verdict + honest label.** A KILL = a reproducible `{object, gate_verdict, oracle_verdict, transform}`
   exhibit (κ=1). No-kill ⇒ **`SURVIVED to budget B`** with: probes run, transform classes covered, oracle
   coverage (full / partial / none), and the **residual-risk statement** — never "sound."

**Gate-of-the-gate self-tests (non-waivable, see `symbolica/selftest_all.py` for the pattern).** Catching a bug
**you planted at full signal** (skip one constraint) is near-theater — real gate bugs are subtle and low-signal
(the FACTHARNESS `7`∉`7.5` boundary, a precision threshold that passes 11 digits but fails the 12th, a dict-key
ordering dependency). So the self-test must include the HARD cases:
(a) **CATCH a BLIND plant** — a *different agent* (≠ the CRUCIBLE builder) plants a false-accept hole in a COPY of
a real gate and does NOT reveal where; CRUCIBLE must EXHIBIT the counterexample without knowing the location. This
is the minimum meaningful test (catching your own known plant proves little).
(b) **CATCH a SUBTLE-category plant** — the hole must be of a class that actually appears in the arsenal's history:
an off-by-one in a range/boundary check, a precision threshold one digit too loose, a silent-pass on a malformed
input type — NOT a max-signal constraint deletion.
(c) **CATCH a planted metamorphic instability** (a gate whose verdict flips under a meaning-preserving relabel).
(d) **raise NO false alarm** on a known-good frozen gate (no spurious "bug" — a meta-verifier that cries wolf, or
whose own oracle is buggy, is worse than useless; controls confirm the oracle is sane first).
(e) **correctly LABEL "no counterexample found" as CONFIDENCE, not PROOF** (machine-assert the report never
contains "sound"/"proven" without an exhibit). A harness that passes all five — especially the BLIND plant — is
trustworthy.

## 4. INFRA REALITY CHECK + GROUND-BY-FETCH (don't assert)
- **Confirm available:** the probed weapons' gates are importable and expose a verdict function + `_selftest`
  (they do — `symbolica_gate.py`, `optima_gate.py`, etc.). Python `hypothesis` (property-based testing) is a
  natural mutation engine — `pip install` if absent; if absent, a deterministic LCG mutator (see
  `psymetrix` SPRITE) suffices. State what's present.
- **FETCH-confirm the load-bearing premise (cite in `GROUNDING.md`):** that **differential/metamorphic/fuzz
  testing finds real SOUNDNESS bugs in production verifiers** — Z3/CVC5 1,500+ bugs / 400+ soundness (Winterer
  et al., type-aware mutation / semantic fusion / STORM); CSmith differential compiler testing; EMI metamorphic
  testing (>1,000 GCC bugs). And the epistemic limit: **testing shows the presence of bugs, never their absence**
  (Dijkstra) — the load-bearing honesty rail of this whole weapon.

## 4a. THE PRE-COMMITTED SCOPE TABLE (commit BEFORE running — the demo-with-predictions rule applied to CRUCIBLE)
State, for each of the 12, the planned oracle + mode + reason BEFORE code runs; log any build-time deviation as an
honest scope change. Audit-estimated buckets (refine, don't silently expand):

| weapon (κ=1 slice) | independent oracle? | planned mode |
|---|---|---|
| CODEFORGE sorting-nets | YES — exhaustive 0/1 enumeration (foreign to synthesis) | **full differential** |
| PSYMETRIX GRIM/GRIMMER | YES — re-implement exact Fraction arithmetic from scratch | **full differential** (κ=1 slice) |
| TRIALGUARD Carlisle/GRIM | YES — same | **full differential** (κ=1 slice) |
| FACTHARNESS quote/number | YES — 2nd fetch + different text extractor | **full differential** |
| REDCELL CTF flag | YES — `flag==expected` independently checkable | **full differential** (CTF mode) |
| OPTIMA feasibility/optimality | PARTIAL — needs a separately-authored solver (PuLP→GLPK) + independent dual check | metamorphic + limited differential |
| PROOFSMITH wrapper | PARTIAL — Lean kernel is near-oracle; probe the wrapper/axiom-scan, not the kernel | metamorphic + wrapper-crash |
| REPROML contamination | PARTIAL — n-gram re-impl feasible; threshold is a free param | metamorphic + limited differential |
| SYMBOLICA agreement | WEAK — all 3 families already used by the gate (see §1a) | **metamorphic + abstain only** unless a foreign CAS is found |
| SOCIUS E-value slice | PARTIAL — E-value arithmetic re-implementable; multiverse is metamorphic | differential on E-value; metamorphic on multiverse |
| ECONOMETRIX walk-forward | NO — guarded-κ (~0.4), no exact oracle | **DECLINE** (probe nothing; not a κ=1 claim) |
| Frontier Construction (capset) | YES — `capset_verify` re-check is already κ=1; probe for a passing-but-invalid cap | **full differential** |

Net (audit estimate): ~5–6 get full differential false-accept hunting; ~4–5 metamorphic-primary; 1–2 declined.
**Do NOT report a blanket "all 12 survived" — name which got full differential vs metamorphic-only vs declined.**

## 5. TO-DOs / STEPS (box order)
1. **PLAN:** `weapons/crucible/SPEC.md` — the four modes, the independent-oracle requirement, the KILL=κ1-exhibit
   vs SURVIVED=confidence-only labeling rule, the per-weapon oracle registry, the router
   (`crucible_router.py`: a weapon WITH an independent oracle → all four modes; a weapon WITHOUT → metamorphic +
   abstain/crash only, labeled partial; a κ=0 "gate" that is actually armor → **CRUCIBLE declines** — you cannot
   adversarially falsify a judgment that never claimed κ>0). **GROUND** the premise + the Dijkstra limit in
   `GROUNDING.md`.
2. **BUILD THE HARNESS + GATE-OF-THE-GATE FIRST** (§3): `crucible_harness.*` (adapter + oracle registry + search +
   the four modes) + `selftest_all.py` (catch-planted-false-accept / catch-planted-metamorphic / no-false-alarm /
   confidence-not-proof labeling). **Green before any soundness-confidence claim counts.**
3. **RUN IT ON THE REAL ARSENAL:** point CRUCIBLE at the κ=1 slices per the §4a table. **Calibrated expectation:
   ≥1 genuine defect across 12 gates is PLAUSIBLE given the season's base rate (SYMBOLICA branch-cut, the false
   +25pp were this class — but those were found PRE-freeze/PRE-audit; the obvious ones are now locked in regression
   tests, so a CLEAN SWEEP is also a valid, honest outcome — do NOT manufacture a KILL).** **Report every KILL as
   a κ=1 exhibit and FIX the gate** (then freeze the exhibit as a permanent regression self-test in that weapon).
   Where it finds nothing, report `SURVIVED to budget B` with oracle-coverage + residual risk — **claim no weapon
   "sound."**
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` BEFORE running): (i) plant a known
   false-accept hole in a COPY of a real gate → predict CRUCIBLE exhibits the counterexample; (ii) plant a
   metamorphic instability → predict the verdict-flip is caught; (iii) run against a KNOWN-GOOD frozen gate →
   predict **no false alarm** + a `SURVIVED` label with the residual-risk statement (NOT "sound"); (iv) the
   real-arsenal sweep → predict ≥1 genuine defect across 12 gates (and report honestly if zero — a clean sweep is
   a valid, if surprising, outcome).
5. **VERIFY INDEPENDENTLY:** a cross-model audit (Sonnet/Haiku ≠ the Opus generator; **never Opus-audits-Opus**;
   Fable inactive) that (a) re-checks each shipped KILL exhibit with its OWN code (does the gate really accept the
   wrong object?), (b) attacks CRUCIBLE itself — can it be made to MISS a planted bug, or to cry wolf? (c) polices
   the labels: is any `SURVIVED` secretly worded as "sound/proven"? Fix what's caught.
6. **REGISTER:** add **CRUCIBLE** to `Next/WEAPON_REGISTRY.json` (a new meta-weapon entry), `Next/BOX_V5.md` (a new
   meta-weapon + a router note: it runs as a standing **Integrity-Office** process, re-probing every gate on
   change — the honest, EXTERNAL version of the killed "WHETSTONE"), `HELMET/registry.json` (the Integrity Office
   gains a `draws: CRUCIBLE` verifier-probing facility). Honest `EVOLUTION_LOG` entry: **a meta-weapon ADDED =
   capability EXPANSION (we can now falsify our own gates), NOT a ≥10% promotion.** Update
   `KIT_EXPANSION_PROPOSAL.md` §7 STATUS and `WEAPONS_BACKLOG.md`.

## 6. HONESTY RAILS (non-waivable, specific to CRUCIBLE)
- **A KILL is a κ=1 exhibit; a non-KILL is CONFIDENCE, never a soundness proof** (Dijkstra). Report budget +
  coverage + residual risk; the words "sound"/"proven" require an exhibit, and a gate is never called "proven sound."
- **The oracle must be INDEPENDENT of the gate** — a false-accept hunt judged by the same engine is circular and
  proves nothing (the box's cross-model rule applied to verifiers). No oracle ⇒ metamorphic/abstain only, labeled.
- **CRUCIBLE is not above its own rules** — ship no harness without its gate-of-the-gate (catch a planted bug,
  no false alarm, confidence-not-proof labeling).
- **Found a bug ⇒ FIX the gate AND freeze the exhibit as a regression test** in that weapon — a caught bug that
  isn't locked down will return.
- **Decline κ=0 armor AND guarded-κ verdicts:** you cannot adversarially falsify a judgment that never claimed an
  exact verifier (armor), and a "false-accept" on a probabilistic/guarded-κ verdict (walk-forward DSR, causal
  E-value verdict, model-fit) is undefined — not a κ=1 KILL. CRUCIBLE probes ONLY the gate-self-declared κ=1 slice.
- **CRUCIBLE's own oracle can be wrong → every KILL is double-checked.** A buggy oracle yields a SPURIOUS KILL
  (a sound gate wrongly declared broken), wasting the team on a non-bug. Confirm the oracle is correct on known-good
  controls FIRST; a KILL ships only when gate-vs-oracle disagree AND the oracle is independently sane.
- **Registry/dashboard discipline:** a `SURVIVED to budget B` entry in `WEAPON_REGISTRY.json` / any Provost
  dashboard MUST carry the residual-risk statement verbatim; the word **"sound" is banned** from that field (a bare
  "survived 10k probes" reads as "sound" to a skimmer — exactly the slip this weapon exists to prevent).
- **No theater sweep:** if oracle coverage is partial across the 12, **say which weapons got full differential
  coverage and which got metamorphic-only** — a silent "all 12 survived" reads as proof when it isn't.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/crucible/` — `SPEC.md`, `GROUNDING.md` (fetched premise + Dijkstra limit + infra),
the frozen `crucible_harness.*` + `selftest_all.py`, `crucible_router.py`, the per-weapon `oracles/`, `demo_*/`
(committed predictions + the bug exhibits + the survived-to-budget reports), `AUDIT.md` (cross-model red-team incl.
make-it-miss-a-planted-bug and make-it-cry-wolf attacks), `README.md` (what it is + honest ceiling: proves a gate
BROKEN, raises CONFIDENCE a gate is sound, never proves soundness). Registration in `Next/WEAPON_REGISTRY.json` +
`Next/BOX_V5.md` + `HELMET/registry.json` (Integrity Office) + honest `EVOLUTION_LOG`; `KIT_EXPANSION_PROPOSAL.md`
§7 + `WEAPONS_BACKLOG.md` updated.

## 8. STAFF THE TEAM (v4 ladder; Fable INACTIVE → its slots on Opus, flag low confidence)
- **Harness + oracles** = code tier writes the adapter / mutators / independent oracles (deterministic — the
  gate-vs-oracle *disagreement*, not a model, is the KILL).
- **Library** = cheap model: fetch the differential/metamorphic-testing premise + the Dijkstra limit.
- **Proposer (optional)** = any tier suggests *where* to look (boundary cases, transforms) — **0%-trusted**, every
  proposal machine-checked by gate-vs-oracle.
- **Auditor** = a model ≠ the generator (Sonnet/Haiku; never Opus-audits-Opus) — re-checks each KILL exhibit
  independently, tries to make CRUCIBLE miss a planted bug or cry wolf, polices the confidence-not-proof labels.

## 9. THE ONE-LINE TEST OF SUCCESS
**"CRUCIBLE takes any κ>0 weapon-gate and either EXHIBITS a machine-checked object that breaks it (false-accept /
false-reject / metamorphic flip / silent-pass — a κ=1 KILL, which then becomes that weapon's permanent regression
test), or reports it SURVIVED to an explicit budget with explicit oracle coverage and residual risk — and NEVER
calls a gate 'sound' or 'proven' without an exhibit, NEVER judges a false-accept with the same engine it's
testing, and DECLINES to probe κ=0 armor."** Proves a gate broken; raises confidence it isn't; honest about the
gap from a soundness proof — the immune system, finally tested.
