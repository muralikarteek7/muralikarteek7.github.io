# GROUNDING — BOOTSTRAP load-bearing facts (grounded, not asserted from memory)

*Ground-by-fetch per the BOX: a load-bearing fact gets a fetched source or a machine check,
not memory. Fetched 2026-06-20.*

---

## G1 — THE LOAD-BEARING REASON STEP (1) IS 0%-TRUSTED (internal source)
**Fact:** LLM-proposed constructions / tools are **fabrication-prone**, so a proposal that "I found
a verifier / this tool exists" carries zero authority — only the RUN promotes a domain to κ>0.

**Source (internal, cited per kickoff §4):**
- `Next/WEAPON_REGISTRY.json`, weapon `W4_evolutionary_program_search`, `verifier` block:
  > `"verifier_cmd": "the fitness oracle IS the checker; every LLM-proposed construction 0%-trusted"`
  > `"rule": "LLM constructions are fabrication-prone (Haiku+Sonnet fabricated 100% raw) -> checker mandatory"`
  Confirmed by `grep -n "W4" Next/WEAPON_REGISTRY.json` (line 66) and reading the entry on disk
  (2026-06-20).
- `Legacy/EVOLUTION_LOG.md` (C44, FACTHARNESS) institutionalizes the same fabrication-firewall
  lesson ("the institutionalized fabrication firewall"; "every LLM-proposed construction 0%-trusted").

**How BOOTSTRAP uses it:** the searcher/proposer (step 1) is κ<1 and 0%-trusted; the
`bootstrap_gate.validate_candidate` RUN (step 2) is the only authority. A hallucinated verifier
(a tool that does not import/run) is REJECTED at the run step (`HALLUCINATED_NONRUNNING`), never on
its say-so. This is the entire reason the gate exists.

---

## G2 — SUDOKU SOLUTION VALIDITY RULES (the FOUND-domain reference verifier)
**Fact (fetched):** A completed 9×9 Sudoku grid is valid iff it uses digits 1–9 and **each row,
each column, and each of the nine 3×3 boxes (sub-grids) contains all digits 1–9 exactly once.**

**Source:** WebFetch of `https://en.wikipedia.org/wiki/Sudoku` (2026-06-20). Verbatim core:
> "fill a 9×9 grid with digits so that each column, each row, and each of the nine 3×3 subgrids
> that compose the grid ... contains all of the digits from 1 to 9."
> "a completed Sudoku grid is ... a special type of Latin square with the additional property of
> no repeated values in any of the nine blocks."

**Verification checklist (fetched):** every row contains 1–9 exactly once; every column contains
1–9 exactly once; every 3×3 box contains 1–9 exactly once.

**How BOOTSTRAP uses it:** `bootstrap_gate.sudoku_verifier` implements exactly these three
constraints (κ=1, exact, pure-Python). The **three declared violation types** — `row_duplicate`,
`column_duplicate`, `box_duplicate` — come straight from the three constraints, so the gate's
"≥1 broken per declared violation type" coverage requirement (audit fix #2) maps 1:1 to the rule.
The soundness-incomplete planted candidate (`_sudoku_verifier_no_boxes`) drops the **box**
constraint — exactly the "skips boxes" failure the audit warns about — and is REJECTED because the
box-only-broken known-answer case (a shift-by-1 Latin square: rows-valid, columns-valid,
boxes-broken; verified by machine in the self-test) exposes the gap.

---

## G3 — PROPER GRAPH COLORING CHECK (the alternative FOUND-domain the kickoff names)
**Fact (fetched):** A vertex coloring is **proper** iff **no two adjacent vertices share the same
color**. Verifying a candidate coloring is O(m) (m = number of edges): iterate over every edge and
confirm its two endpoints have different colors. (Distinct from the NP-hard problem of *finding* a
minimum coloring — *checking* a given one is linear-time.)

**Source:** WebFetch of `https://en.wikipedia.org/wiki/Graph_coloring` (2026-06-20). Verbatim:
> "a labeling of the graph's vertices with colors such that no two vertices sharing the same edge
> have the same color."

**How BOOTSTRAP uses it:** named in the kickoff as the alternative κ>0 self-test domain (we used
Sudoku as the primary; graph-coloring is interchangeable — its single violation type is
`adjacent_same_color`, checked in O(m)). Documented here so the candidate-source list is grounded.

---

## G4 — THE κ=0 (ARMOR-ONLY) DOMAIN: essay/persuasion quality has NO exact verifier
**Fact:** "How persuasive / high-quality is this essay" is a JUDGMENT — there is no exact,
non-gameable decision procedure that returns a ground-truth VALID/INVALID. Scoring it is an LLM
judgment task (κ<1), not a machine check.

**Source (internal doctrine, cited):** `CLAUDE.md` κ-gate ("cheap exact non-gameable verifier
exists? → if no → ARMOR ONLY"); `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` κ-rule ("a weapon
needs a cheap EXACT non-gameable verifier; κ=0 → armor"). The NLI/entailment framing in FACTHARNESS
(C44) is the canonical example of a κ=0 judgment layer that must ABSTAIN rather than fake a gate.

**How BOOTSTRAP uses it:** the router returns **ARMOR-ONLY (κ=0)** for essay-persuasiveness, and
the pipeline never invents a gate. This is the negative self-test: BOOTSTRAP must look *less*
capable here rather than fake κ.

---

## Fetch status
- G2 (Sudoku rules): FETCHED OK (Wikipedia, 2026-06-20).
- G3 (graph-coloring check): FETCHED OK (Wikipedia, 2026-06-20).
- G1 (W4 fabrication lesson): internal source, confirmed on disk by grep + read (not a web fetch —
  it is the box's OWN owned lesson, cited to the registry entry + EVOLUTION_LOG as the kickoff §4
  directs).
- G4 (κ=0 essay judgment): internal doctrine, cited to CLAUDE.md + WEAPONS_BACKLOG + FACTHARNESS.
No fetch failed.
