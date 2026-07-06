# GROUNDING — CRUCIBLE's load-bearing facts (FETCHED, not asserted)

*All facts below were fetched via WebSearch/WebFetch on 2026-06-20, not recalled from
memory (the box's "ground, don't assert" rule). Where a fetch was partial, that is stated.*

## Premise A — differential/metamorphic/fuzz testing finds REAL SOUNDNESS bugs in production verifiers
This is the load-bearing premise: CRUCIBLE's discipline is established and demonstrably finds
real soundness bugs in the exact class of artifact our gates are (hand-rolled verifiers + solver
wrappers + frozen test-suites).

### A1 — SMT solvers Z3 and CVC4/CVC5 (Winterer et al., metamorphic + type-aware mutation)
- A large-scale campaign found **1,500+ unique bugs in Z3 and CVC4/CVC5**, of which **1,100+ were
  already fixed by the developers** and **400+ are critical SOUNDNESS bugs.**
- Breakdown (from the SpeakerDeck "Finding 1,500 bugs in the SMT Solvers Z3 and CVC5"):
  total ~1,560 (Z3 1,147 / 779 fixed; CVC4 413 / 282 fixed); **soundness ~446 (Z3 375 / 228 fixed;
  CVC4 71 / 60 fixed).**
- Techniques: **Semantic Fusion** (a METAMORPHIC method — fuse two satisfiable formulas via fusion
  functions preserving satisfiability; tool **YinYang**); **Type-Aware Operator Mutation** (mutate
  operators respecting type constraints; tool **OpFuzz**); **Generative Type-Aware Mutation** (tool
  **TypeFuzz**).
- Per-tool soundness counts: STORM 17 (Z3) / 0 (CVC4-default); YinYang 24 (Z3) / 5 (CVC4);
  **OpFuzz 114 (Z3) / 11 (CVC4-default).**
- Sources:
  - https://speakerdeck.com/wintered/finding-1-500-bugs-in-the-smt-solvers-z3-and-cvc5
  - https://chengyuzhang.com/papers/park-etal-oopsla21.pdf (Generative Type-Aware Mutation, OOPSLA'21)

### A2 — C compilers GCC and LLVM (Csmith, differential testing — PLDI 2011)
- Csmith generates random C programs and uses **differential testing** (compile with multiple
  compilers; if behavior differs, at least one has a bug). Over a three-year period the authors
  reported **more than 325 previously unknown bugs** to compiler developers. *Every* compiler tested
  was found to both crash and silently miscompile valid input.
- Sources:
  - https://www.flux.utah.edu/paper/yang-pldi11 ("Finding and Understanding Bugs in C Compilers", PLDI 2011)
  - https://blog.regehr.org/archives/492
  - https://en.wikipedia.org/wiki/Csmith (confirms Csmith stress-tests compilers/static analyzers)

### A3 — EMI metamorphic compiler testing (Le, Afshari, Su — PLDI 2014)
- **Equivalence Modulo Inputs (EMI)** is a metamorphic methodology: from a program + test inputs,
  generate EMI variants (same behavior on those inputs) and differentially test compilers against them.
- The PLDI'14 paper reported **147 confirmed unique bug reports for GCC and LLVM in eleven months**,
  the majority miscompilations, with 100+ already fixed. The ongoing EMI Compiler Validation Project
  tracks a higher cumulative total over the years (GCC/LLVM **1,634** with **1,076 fixed** per recent
  tracking). The kickoff's ">1,000 GCC bugs" refers to this cumulative project tracking, not the
  single-paper figure — reported here honestly so the number is not over-claimed.
- Sources:
  - https://web.cs.ucdavis.edu/~su/emi-project/ (EMI Compiler Validation Project)
  - https://dl.acm.org/doi/10.1145/2594291.2594334 ("Compiler validation via equivalence modulo inputs", PLDI'14)

**Conclusion (grounded):** metamorphic + differential testing repeatedly finds SOUNDNESS bugs (not
just crashes) in mature, heavily-used verifiers and compilers. Our gates are the same artifact class.
CRUCIBLE applies this discipline inward, at the box's own immune system.

## Premise B — the epistemic LIMIT (the load-bearing honesty rail)
**Dijkstra:** *"Program testing can be used to show the presence of bugs, but never to show their
absence."*
- Earliest documented form: NATO Software Engineering Techniques conference proceedings, **1969**
  (published April 1970). The well-known phrasing appears in Dijkstra's **"Notes On Structured
  Programming" (EWD249), 1970**, §3 "On The Reliability of Mechanisms."
- Sources:
  - https://en.wikiquote.org/wiki/Edsger_W._Dijkstra
  - https://quotepark.com/quotes/1723679-edsger-w-dijkstra-program-testing-can-be-used-to-show-the-presence-o/

**Why this is load-bearing for CRUCIBLE:** it is exactly why a no-kill is CONFIDENCE, never a
soundness proof. CRUCIBLE can PROVE a gate BROKEN (an exhibit), but can only ever RAISE CONFIDENCE
that a gate is sound. The word "sound"/"proven" is machine-banned from any SURVIVED report
(`crucible_harness.Survived.to_dict()` raises; `selftest_all.py` case (e) asserts it).

## Infra reality check (stated, not assumed)
- **Python 3.9.6.** `sympy 1.14.0` present. **`hypothesis` is ABSENT** — CRUCIBLE therefore uses a
  deterministic seeded LCG mutator (the psymetrix/SPRITE fallback the kickoff sanctions; reproducible
  by design, which is preferable for a regression-test exhibit). No pip install was performed.
- The probed weapons' gates are importable and expose a verdict function + `_selftest`: confirmed for
  `codeforge/sortnet_verify.py` (`verify_sorting_network`) and `psymetrix/forensics_verify.py` (`grim`),
  which are the two real κ=1 gates the demo probes with importable hermetic oracles. Other full-
  differential targets (factharness quote, redcell CTF, frontier capset) need a network fetch / a
  committed-answer fixture / the capset module respectively, out of the hermetic demo's scope — they
  are recorded as full-coverage targets in the router scope table, not claimed as swept.
