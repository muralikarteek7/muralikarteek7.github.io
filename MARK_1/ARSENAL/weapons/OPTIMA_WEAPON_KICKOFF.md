# KICKOFF — build WEAPON #3: OPTIMA (exact optimization / OR) for the v5 box
*Paste everything below into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written
2026-06-20. OPTIMA is item #3 of `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` — an exact solver that returns
a **certified-optimal** answer with an **independent certificate**, not a solver's self-report.*

---

You are building **OPTIMA**, the box's next **WEAPON** (offense): a solver-gated engine that **produces
certified-optimal (or proven-bound) solutions** to discrete/combinatorial optimization — scheduling, routing,
packing, assignment, allocation — where an **independent feasibility-and-bound certificate is the only judge.**
It becomes the **OR / Operations** facility of the **CS & Engineering** department of the HELMET. Work BOX-style:
plan → produce → **verify INDEPENDENTLY** (re-check the solution & the bound without the solver; cross-model
audit the model) → ground → be honest; **no win without proof; "optimal" is never a solver's word to take.**

## 0. ORIENT — read first (in order)
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (the κ-router — OPTIMA is a κ=1 weapon; the registry already
seeds it as **W2 exact combinatorial solver** in `Next/WEAPON_REGISTRY.json` — read that entry, incl. its
**failure mode**), `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` (item #3 = this), the two existing weapons as
**templates** (`Expanding_Frontiers/weapons/socius/`, `…/psymetrix/` — copy their shape: `SPEC.md`, a frozen
gate, `selftest_all.py`, a router, `demo_*/` with committed predictions, `AUDIT.md`), and the sibling kickoffs
`CODEFORGE_WEAPON_KICKOFF.md` + `PROOFSMITH_WEAPON_KICKOFF.md` (same weapon-design pattern — OPTIMA shares
PROOFSMITH's "model-vs-reality is the κ<1 slice" structure).

**⚠ The registry already names OPTIMA's signature failure mode (do not repeat it):** `W2_exact_combinatorial_solver`
→ *"flat-space timeout (n=6 cold: 89/112 in 700s) → report best-found as a lower bound, never 'optimal'."* And
the **weak-weapon-cap error** (`Next/BOX_V5.md` §3): never declare a bound "the answer" until the STRONG solver
has run. Timeout ≠ optimal. Carry the gap, always.

## 1. THE HONEST FRAMING — what OPTIMA IS and IS NOT (do not skip)
**IS:** a κ=1 weapon over a sharp, cheap verifier — **an optimization solution is independently checkable**:
re-evaluate every constraint on the returned assignment (feasibility) and recompute the objective; optimality is
certified by a **matching dual/bound** (primal = dual ⇒ proven optimal). OPTIMA *produces* a certified solution
and ships nothing the independent checker hasn't re-verified. **Its value is the CERTIFICATE + the modeling, not
"the model did mental math."** It is mostly a **reliable-floor weapon** (the FETCH-KNOWN/armor++ kind), with one
genuine κ<1 slice (modeling, below).

**IS NOT:**
- **NOT "trust the solver's OPTIMAL status" — that is a self-report, and the box never trusts a self-report.**
  The gate **independently re-checks**: (a) the solution is FEASIBLE (re-evaluate all constraints from scratch,
  not via the solver), (b) the objective equals the claimed value, (c) optimality is backed by a **dual bound /
  proof of gap=0**, not just a status string.
- **NOT "optimal for the real problem" — only "optimal FOR THIS MODEL."** Translating a word-problem into
  variables/constraints/objective is **JUDGMENT (κ<1)** — the model can be wrong even when the solve is exact.
  The modeling step needs an **independent cross-model review**; the certificate covers the formal model only.
  (Same structure as PROOFSMITH's autoformalization caveat.)
- **NOT "best-found = optimal."** A timeout or an open gap ⇒ report the **feasible solution as a bound + the
  honest gap**, never "optimal." An **infeasibility** claim ("no solution exists") also needs a certificate (an
  infeasibility proof / IIS), not a solver shrug.
- **NOT a capability boost.** OPTIMA's edge over a one-shot LLM answer is the **already-owned "execute, don't
  guess" armor** (an exact solver crushes mental arithmetic — that's v3, not a new capability). If you run an
  LLM-one-shot-vs-OPTIMA comparison, it will win big, but **label it as re-demonstrating execute-don't-guess, NOT
  a ≥10% capability promotion.** The genuinely new thing OPTIMA adds is the **independent optimality certificate**.

## 2. THE THREE MODES (map to the κ-router; the independent re-checker is the exact verifier)
| mode | analogue | what it produces | the FROZEN exact verifier (κ=1) |
|---|---|---|---|
| **EXACT-SOLVE** | FETCH-KNOWN / armor++ | a certified-optimal solution | **independent feasibility re-check (all constraints, no solver) + objective recompute + proof of gap=0 (primal=dual / verified status)** |
| **BOUND-PROVE** | SEARCH-OPEN | best feasible solution + a proven dual bound on hard instances | feasibility re-check of the primal + an independently-valid **dual/relaxation bound**; report the **gap**, never "optimal" |
| **REPRODUCE-RECORD** | construction engine | a known-best on a benchmark instance (TSPLIB/MIPLIB) | re-check against the published optimum; labeled **reproduction**. Beating a record needs an audited certificate — **honest negative expected** |

## 3. THE KEY ENGINEERING PROBLEM — the certificate, not the solver, is the result
Build the **independent verifier FIRST** (it must not call the solver to judge the solver):
1. **Feasibility certificate** — a standalone function re-evaluates **every** constraint on the returned solution
   and confirms each holds (integer/domain bounds, all relations). Independent of the solver's internal state.
2. **Objective check** — recompute the objective from the solution; it must equal the reported value.
3. **Optimality certificate** — the hard part. Accept "optimal" ONLY with one of: (a) the solver's
   **best_bound == objective** (verified gap = 0, e.g. CP-SAT `OPTIMAL` with bound captured), or (b) an
   independent **dual-feasible bound** that meets the primal (LP/relaxation weak-duality: any dual-feasible value
   bounds the optimum). No matching bound ⇒ it is a **feasible solution + a gap**, labeled as such.
4. **Infeasibility certificate** — if claiming "no solution," produce an **IIS / infeasibility proof**, not a bare
   status. (And sanity-check by trying to find ANY feasible point.)

**Gate self-tests (non-waivable, see `socius/selftest_all.py`):** the gate must (a) ACCEPT a known optimal with a
valid gap=0 certificate, (b) **REJECT an "OPTIMAL" answer that is actually INFEASIBLE** (inject a constraint
violation), (c) **REJECT an "optimal" claim with a non-zero gap** (relabel as a bound), (d) **REJECT a wrong
objective value**. A gate that passes all four is trustworthy.

## 4. INFRA + EXACTNESS REALITY CHECK — ground the toolchain BEFORE designing around it
- **Try to install OR-Tools** (`pip install ortools` → CP-SAT, the strongest free exact engine; emits OPTIMAL/
  FEASIBLE/INFEASIBLE + objective bounds). Confirm it solves a tiny model and exposes the **best bound**.
- **Fallbacks if absent:** PuLP / `python-mip` / Pyomo + CBC (MILP); or pure-Python exact for tiny instances
  (branch-and-bound / DP for knapsack/assignment). State what's available; don't assume.
- **⚠ Exactness caveat (ground this):** **integer/CP** solving is exact; **floating-point MILP** has tolerance
  (a reported optimum can be off by the solver's feasibility/integrality tolerance). Prefer **integer/CP models**
  where possible; when using float MILP, **flag the tolerance** and re-check feasibility with an explicit epsilon.
  Don't dress a tolerance-bound float result as bit-exact.

## 5. TO-DOs / STEPS (box order)
1. **PLAN:** `weapons/optima/SPEC.md` — the three modes, the 4-part certificate gate, the **model-vs-reality κ<1
   caveat**, the router (`optima_router.py`: a problem with a clean discrete model → EXACT-SOLVE; hard/large →
   BOUND-PROVE with gap; benchmark instance → REPRODUCE-RECORD; a fuzzy "optimize our strategy" with no
   formalizable objective → **κ=0 → armor**, do not pretend to certify). **GROUND by FETCH (don't assert):** that
   CP-SAT emits a proven OPTIMAL status with a dual/best bound and INFEASIBLE proofs; LP weak-duality (dual
   feasible ⇒ bound on primal) as the optimality-certificate basis; IIS for infeasibility; a benchmark with known
   optima (small TSPLIB/MIPLIB) for the reproduction demo. Cite each in `GROUNDING.md`.
2. **INFRA CHECK + BUILD THE GATE FIRST** (§4 + §3): install OR-Tools (or fallback), then `optima_gate.*` with the
   4 certificates + `selftest_all.py` (accept-optimal-with-cert / reject-infeasible / reject-nonzero-gap /
   reject-wrong-objective). **Gate green before any solving counts.**
3. **BUILD the weapon loop:** model → solve → **independent certificate gate** → (survivor) cross-model audit of
   the **model** (does it capture the stated problem?). Machine-checkable → **execute ($0, no model needed for the
   solve), never vote.**
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` BEFORE running): (i) solve a small
   **assignment/knapsack/TSP** to certified optimality + independently re-verify feasibility + objective + gap=0;
   (ii) **reproduce a known optimum** on a small TSPLIB/MIPLIB instance (labeled reproduction); (iii) a
   **BOUND-PROVE** case — a harder instance that doesn't close → feasible solution + dual bound + the honest gap;
   (iv) show the gate **REJECTING** a deliberately-broken "OPTIMAL but infeasible" answer.
5. **(Optional, honestly-labeled) execute-don't-guess demo:** OPTIMA vs a one-shot LLM answer on word-problems —
   expect OPTIMA to win big, but **label it re-demonstrating v3 armor (execute-don't-guess), NOT a capability
   promotion.** The real new value is the certificate. Do NOT run a misleading "capability A/B" here.
6. **VERIFY INDEPENDENTLY:** a cross-model audit (Sonnet/Haiku ≠ the Opus generator; **never Opus-audits-Opus**;
   Fable inactive) that (a) re-checks each shipped solution's feasibility & objective with its OWN code, (b)
   attacks the gate with an infeasible "optimal" and a gap-hidden "optimal," (c) reviews whether each MODEL
   actually captures its stated problem (the modeling attack — the highest-value find). Fix what's caught.
7. **REGISTER:** add **OPTIMA** to `Next/BOX_V5.md` (promote registry **W2** to a full Weapon + router branch) and
   `Expanding_Frontiers/HELMET/registry.json` (the CS_ENG / OR facility's `draws`). Honest `EVOLUTION_LOG` entry:
   **a weapon ADDED = capability EXPANSION, NOT a ≥10% promotion** (the solve is deterministic machine work; the
   new capability is the independent certificate, not a model-quality delta). Update `WEAPONS_BACKLOG.md` STATUS ✅.

## 6. HONESTY RAILS (non-waivable, specific to OPTIMA)
- **"Optimal" is earned by a certificate (gap=0 / matching dual bound), never by a solver status string alone.**
  No certificate ⇒ "feasible solution + gap," labeled.
- **Certified-optimal ≠ right answer to the real problem** — the model is judgment (κ<1); cross-model-review the
  formulation. The certificate covers the formal model only; say so.
- **Timeout / open gap ⇒ a bound, never optimal** (the W2 + weak-weapon-cap rules). Run the STRONG solver before
  calling any plateau structural.
- **Infeasibility is a claim that needs a proof** (IIS), not a solver shrug.
- **Float tolerance is disclosed** — prefer integer/CP exactness; flag any tolerance-bound MILP result.
- **The gate that can't fail is not a gate** — ship no gate without its 4 reject self-tests.
- **κ=0 stays armor:** a fuzzy "optimize our business strategy" with no formalizable exact objective → ground +
  abstain, do NOT manufacture a certificate.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/optima/` — `SPEC.md`, `GROUNDING.md` (fetched sources + infra-check result),
`optima_gate.*` (the 4 certificates) + `selftest_all.py`, `optima_router.py`, `demo_*/` (committed predictions +
certified solutions + certificates), `AUDIT.md` (cross-model red-team incl. the infeasible/gap/modeling attacks),
`README.md` (what it is + honest ceiling: certifies optimality FOR THE MODEL, not real-world truth). Registration
in `Next/BOX_V5.md` (W2 → Weapon) + `HELMET/registry.json` + honest `EVOLUTION_LOG` entry; `WEAPONS_BACKLOG.md`
STATUS updated.

## 8. STAFF THE TEAM (v4 ladder; Fable INACTIVE → its slots on Opus, flag low confidence)
- **Modeler** = code tier writes the OR model (the model is judgment — cross-model-review it). **The solver +
  independent certificate, not the model, is the gate.**
- **Solver** = the exact engine (CP-SAT/MILP) — pure machine, $0, no LLM in the solve loop.
- **Library** = cheap model: fetch the CP-SAT bound/IIS facts, LP-duality basis, the benchmark optima.
- **Auditor** = a model ≠ the generator (Sonnet/Haiku; never Opus-audits-Opus) — re-checks feasibility/objective
  independently, attacks the gate, reviews the modeling fidelity.

## 9. THE ONE-LINE TEST OF SUCCESS
**"OPTIMA ships only solutions an INDEPENDENT checker re-verified (feasible + objective + a gap=0/dual
certificate); it labels 'optimal FOR THIS MODEL' and cross-model-reviews the modeling; it reports timeouts as
bounds-with-gap, never optimal; it reproduces known optima labeled as reproductions; it never claims a record
without an audited certificate — and it routes fuzzy κ=0 'optimize our strategy' asks to armor."** Exact where
the math is exact, honest about the modeling joint, certificate over solver-status always.
