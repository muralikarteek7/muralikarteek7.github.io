# KICKOFF — build the KIT piece: SHOES-d — DOMAIN BOOTSTRAP (the "new-weapon scaffolder")
*Paste into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written 2026-06-20. This is item
**#5 (SHOES sub-component d)** of the KIT-EXPANSION plan (`Next/KIT_EXPANSION_PROPOSAL.md`, §4). It is the piece
that lets the arsenal GROW from 12 toward broad coverage **without faking κ** — by helping STAND UP a new
department's exact verifier semi-automatically.*

*Independent audit 2026-06-20 (READY-WITH-FIXES) — apply at build: (1) **commit the candidate-source list** (which
solvers/libraries/benchmarks are searched) AND the **N-attempts bound** in the SPEC, so a κ=0 ARMOR-ONLY verdict is
REPRODUCIBLE (else two runs can disagree); (2) the known-broken test set must include **≥1 instance of EACH distinct
violation type** the candidate claims to check — a soundness-INCOMPLETE verifier (e.g. a Sudoku checker that skips
boxes) can pass toy cases while being wrong on the class; (3) depends on a stable WEAPON_REGISTRY schema to write into.*

---

You are building **BOOTSTRAP**: given a NEW problem class described in natural language, it tries to find and
**validate** an exact verifier for it — turning "add a weapon" from fully-manual into semi-automated, while
**refusing to fake κ** when no real verifier exists. Work BOX-style: plan → produce → **verify INDEPENDENTLY** →
ground → be honest; **the only thing that promotes a domain to κ>0 is a verifier that PASSES known-answer cases —
never a self-report that "this verifier works."**

## 0. ORIENT
`CLAUDE.md`, `RESUME.md`, **`Next/KIT_EXPANSION_PROPOSAL.md`** (§4 SHOES-d), **`Next/WEAPON_REGISTRY.json`** (the
schema BOOTSTRAP writes into), **`Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md`** (the κ-rule that orders the
arsenal: a weapon needs a cheap EXACT non-gameable verifier; κ=0 → armor), and any TWO existing weapons to see what
"a registered verifier + gate + selftest" looks like (`symbolica/`, `optima/`). BOOTSTRAP automates the *verifier-
identification* step the human now does by hand; it does NOT write the whole weapon.

## 1. THE HONEST FRAMING — what BOOTSTRAP IS and IS NOT
**IS:** a pipeline — given a new problem class, it (1) SEARCHES for a known exact verifier (a theorem prover, SAT/SMT
solver, constraint checker, a published benchmark with ground truth, an existing library that decides the property),
(2) **instantiates a candidate verifier and RUNS it on 3–5 known-answer cases**, (3) if all pass → registers it as
κ>0 and opens a new department slot; if no verifier found/validated in N tries → classifies the domain **κ=0 /
ARMOR-only** and records that conclusion (so it isn't wastefully re-attempted).
**The κ=1 slice:** step (2) — running a candidate verifier on cases with KNOWN answers is fully machine-checkable.
**IS NOT:** ❌ a verifier itself (it finds/validates one). ❌ trustworthy on step (1)'s "I found a verifier" — that
is LLM judgment and **hallucinates non-existent tools**; the ONLY thing that counts is the verifier actually running
and passing known cases. ❌ able to cover κ=0 domains (no formal tool exists for "persuasive-writing quality" — it
must correctly return κ=0, not invent a fake gate). ❌ a guarantee the new verifier is correct on the FRONTIER — a
verifier that passes toy cases can still be wrong on the real target (honest ceiling).

## 2. THE THREE OUTCOMES (the router's verdict)
| outcome | trigger | what BOOTSTRAP does |
|---|---|---|
| **κ>0 VERIFIER FOUND** | a candidate verifier PASSES all known-answer cases AND catches a known-broken one | register the department + verifier; hand off to a full weapon-build kickoff |
| **κ=0 ARMOR-ONLY** | no exact verifier found/validated in N tries | record "armor-only" + why; route the domain to ARMOR; do NOT build a "weapon" |
| **ABSTAIN / NEED-INPUT** | the problem class is under-specified to even search | ask for a sharper spec; do not guess |

## 3. THE KEY ENGINEERING PROBLEM — validate, never trust; and the gate-of-the-gate
`bootstrap.*`: a candidate-verifier must pass the SAME bar every weapon gate passes — **accept a known-good input,
catch a known-broken one, abstain on malformed** — on the new domain's known-answer cases, BEFORE registration.
A candidate that only accepts-good (never tested on broken) is REJECTED (a verifier that can't fail is not a
verifier). **Self-tests (non-waivable):** (a) on a domain WITH a real verifier (e.g. "is this Sudoku solution
valid" → a checker), BOOTSTRAP finds + validates + registers it; (b) on a κ=0 domain ("rate this essay's
persuasiveness"), BOOTSTRAP returns **κ=0 ARMOR-ONLY**, never a fake gate; (c) a HALLUCINATED verifier (a tool that
doesn't exist / doesn't run) is REJECTED at the run step, never registered on its say-so; (d) a candidate that
passes good cases but FAILS to catch a planted broken one is REJECTED.

## 4. INFRA + GROUND-BY-FETCH
- **Confirm:** the existing verifier libraries reachable (SAT/SMT, sympy, OR-Tools, test-runners) as candidate
  sources; the registry schema to write. State what's present.
- **FETCH-confirm (cite `GROUNDING.md`):** the box's OWN owned lesson that **LLM-proposed constructions/tools are
  fabrication-prone** (the registry's W4 note: Haiku+Sonnet fabricated 100% raw → checker mandatory) — this is the
  load-bearing reason step (1) is 0%-trusted and step (2) is the only authority. (Internal source; cite the
  registry entry + EVOLUTION_LOG.)

## 5. TO-DOs (box order)
1. **PLAN** `weapons/bootstrap/SPEC.md` — the 3 outcomes, the validate-don't-trust rule, the κ=1 validation slice
   vs the κ<1 search step, the router. **GROUND** the fabrication-prone-proposals lesson in `GROUNDING.md`.
2. **BUILD** `bootstrap.*` + `selftest_all.py` (the 4 self-tests, incl. the hallucinated-verifier rejection). Green first.
3. **RUN on 2 fresh domains, committed predictions** (`PREDICTION.md` first): one that SHOULD yield a κ>0 verifier
   (e.g. Sudoku-validity, or graph-coloring-check) → predict FOUND+registered; one that should NOT (an essay-quality
   judgment) → predict κ=0 ARMOR-ONLY. The run is the judge.
4. **VERIFY INDEPENDENTLY:** cross-model audit (Sonnet/Haiku ≠ Opus generator) — feeds it a plausible-but-fake
   verifier (must be rejected at run), a κ=0 domain dressed as κ>0 (must return κ=0), and checks no toy-passing
   verifier is over-sold as frontier-correct. Fix what's caught.
5. **REGISTER:** `Next/BOX_V5.md` (SHOES-d: the arsenal-growth mechanism), `HELMET/registry.json` (a Registrar/Dean
   facility for standing up new departments), honest `EVOLUTION_LOG` (**a mechanism to grow the arsenal honestly;
   NOT a promotion; each NEW weapon it scaffolds still runs the full box discipline**). Update plan §7 + backlog.

## 6. HONESTY RAILS
- **Only a RUN promotes a domain to κ>0** — never a self-report that a verifier exists. Step (1) is 0%-trusted.
- **κ=0 stays κ=0** — BOOTSTRAP must return ARMOR-ONLY for judgment domains, never invent a gate to look capable.
- **Toy-passing ≠ frontier-correct** — a validated verifier carries its known-answer coverage; the new weapon it
  scaffolds must STILL pass its own full box build (gate-first + demo + cross-model audit). BOOTSTRAP opens the
  door; it does not ship the weapon.
- **A verifier that can't fail is not a verifier** — reject candidates not tested on a broken input.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/bootstrap/` — `SPEC.md`, `GROUNDING.md`, `bootstrap.*` + `selftest_all.py`,
`bootstrap_router.py`, `demo_*/` (committed predictions: one FOUND, one ARMOR-ONLY), `AUDIT.md`, `README.md`
(honest ceiling: finds+validates verifiers where they exist; returns κ=0 honestly elsewhere; toy ≠ frontier).
Registration in `Next/BOX_V5.md` + `HELMET/registry.json` + honest `EVOLUTION_LOG`; plan §7 + `WEAPONS_BACKLOG.md`.

## 8. STAFF (v4 ladder; Fable INACTIVE → Opus, flag low confidence)
- **Validator + registrar-writer** = code tier (runs candidates on known-answer cases — the RUN, not a model, promotes).
- **Searcher (proposer)** = any tier suggests candidate verifiers — **0%-trusted**, every candidate RUN-validated.
- **Auditor** = a model ≠ generator (Sonnet/Haiku) — fake-verifier + κ=0-dressed-as-κ>0 attacks; over-sell checks.

## 9. THE ONE-LINE TEST OF SUCCESS
**"BOOTSTRAP, given a new problem class, FINDS a candidate exact verifier, VALIDATES it by running it on known-answer
cases (accept-good / catch-broken / abstain-malformed) before registering a κ>0 department — and returns κ=0
ARMOR-ONLY, never a fake gate, when no real verifier exists or only LLM judgment is available; a hallucinated
verifier is rejected at the run step, and a toy-passing verifier is never over-sold as frontier-correct."** Grows
the arsenal by the same rule that built it: the machine, not the model, earns κ.
