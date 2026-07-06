# KICKOFF — build WEAPON #4: SYMBOLICA (symbolic-exact numerics) for the v5 box
*Paste everything below into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written
2026-06-20. SYMBOLICA is item #4 of `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` — it returns an **exact**
closed form whose correctness rests on **independent engines agreeing**, not on one CAS's self-report.*

---

You are building **SYMBOLICA**, the box's next **WEAPON** (offense): an agreement-gated engine that **produces
exact closed-form results** — definite/indefinite integrals, infinite sums, limits, ODE solutions, special
values, tight analytic bounds — where the judge is **two-or-more independent computations agreeing**, never a
single symbolic engine's output. It becomes the **Natural Sciences** department's exact-computation facility.
Work BOX-style: plan → produce → **verify INDEPENDENTLY** (a second/third independent method must agree; or a
cross-model audit of the setup) → ground → be honest; **no win without proof; a single-engine answer is a claim,
not a result.**

## 0. ORIENT — read first (in order)
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (the κ-router — SYMBOLICA is a high-κ weapon; KNOWN closed form →
FETCH/reproduce, derive-a-new one → search), the registry entry **W7_exact_symbolic_numerics** in
`Next/WEAPON_REGISTRY.json` (read it: rule = *"cross-check symbolic answer vs high-precision numerical eval —
two independent engines must agree; single-engine answers are claims, not results"*; status SEEDED — you are
building it). Then `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md` (item #4 = this), the two existing weapons as
**templates** (`socius/`, `psymetrix/` — `SPEC.md`, frozen gate, `selftest_all.py`, router, `demo_*/`, `AUDIT.md`),
and the sibling kickoffs `OPTIMA_WEAPON_KICKOFF.md` + `PROOFSMITH_WEAPON_KICKOFF.md` (same pattern).

## 1. THE HONEST FRAMING — what SYMBOLICA IS and IS NOT (do not skip)
**IS:** a **high-κ (≈0.9) weapon** — exactness at near-zero cost where sampling would only give error bars. Its
verifier is **cross-method agreement**: a symbolic answer (sympy) cross-checked against **independent
high-precision numeric evaluation** (mpmath) at many points, and/or a symbolic **simplify-to-zero** of
(claim − reference). When ≥2 independent methods agree to many digits across the domain, the result is certified.

**IS NOT:**
- **NOT "sympy said so."** A single CAS is **heuristic and can be wrong** (bad branch, unsimplified/incorrect
  `integrate`, a wrong assumption). One engine = a claim. **The result is the AGREEMENT, not the engine output.**
- **NOT kernel-grade like PROOFSMITH (state this clearly).** `sympy.simplify(lhs-rhs)==0` is strong but **not a
  trusted proof kernel** — it can fail to simplify a true zero, or (rarely) mis-handle branch cuts. So
  SYMBOLICA's certificate is **"verified by independent agreement,"** which is *empirically very strong* but
  weaker than a Lean proof. Label it honestly: "verified to D digits at K points + symbolic simplify-to-0,"
  not "proven" unless a genuine symbolic identity collapses to 0 unconditionally.
- **NOT safe just because two engines agree (THE shared-blind-spot trap).** Per the box: *when verifiers AGREE,
  that's a RISK (shared library bug / same wrong branch cut), not safety.* For any load-bearing result use a
  **THIRD, methodologically different** check — e.g. numeric **quadrature (scipy.integrate)** vs **series
  expansion** vs **symbolic** — diversify the *method*, not just re-run sympy at higher precision.
- **NOT exact when it isn't.** Non-convergent sums, domain-restricted closed forms, branch-cut ambiguities,
  removable singularities — must be detected and flagged, not papered over. Numeric agreement to 15 digits is
  evidence, not a convergence proof.
- **NOT a capability boost.** Symbolic computation is deterministic machine work (the "execute, don't guess"
  rung). SYMBOLICA's new value is the **exact answer + the multi-method certificate**, not a model-quality delta.

## 2. THE THREE MODES (map to the κ-router; multi-method agreement is the verifier)
| mode | analogue | what it produces | the FROZEN verifier (κ≈0.9) |
|---|---|---|---|
| **CLOSED-FORM** | FETCH/armor++ | an integral/sum/limit/ODE in closed form | **symbolic result + independent high-precision numeric (mpmath) agreement to D digits at K sampled points across the domain + a 3rd diversified method on load-bearing cases** |
| **IDENTITY-PROVE** | PROOFSMITH-lite | an equality/identity certified | **symbolic `simplify(lhs-rhs) → 0` AND numeric agreement at K random points** (both required; report which fired) |
| **SPECIAL-VALUE / BOUND** | construction-lite | an exact special value (e.g. ζ(2)=π²/6) or a tight analytic bound | reproduce vs a **fetched known value** (labeled reproduction) + cross-method numeric; a bound is checked tight by exhibiting near-equality cases |

## 3. THE KEY ENGINEERING PROBLEM — agreement across DIVERSE methods, with domain checks
Build the **agreement gate FIRST**:
1. **Two-method floor** — every result must pass **symbolic vs independent high-precision numeric** agreement to
   a committed digit count D at K sampled points (random points in the domain for identities; the value itself
   for definite results, evaluated by independent quadrature for integrals).
2. **Third-method diversification for load-bearing claims** — a methodologically *different* check (quadrature
   vs series vs symbolic; or a different CAS path). Agreement of two same-family methods is a shared-blind-spot
   risk; record it as such.
3. **Domain & convergence checks** — test the claimed identity at points spanning the domain incl. near
   singularities/branch cuts; verify convergence for sums/integrals before reporting a closed form; flag any
   point of disagreement (a closed form valid only on a sub-domain must be labeled with its domain).
4. **Exactness labeling** — distinguish **"symbolically proven (simplify→0 unconditionally)"** from **"verified
   to D digits at K points"** (empirical-strong). Never upgrade the latter's wording to "proven."

**Gate self-tests (non-waivable, see `socius/selftest_all.py`):** the gate must (a) ACCEPT a known correct
closed form (numeric + symbolic agree), (b) **REJECT a subtly-WRONG closed form** (e.g. off by a constant or a
factor — numeric disagreement must catch it), (c) **REJECT a domain-restricted form presented as global** (flag
the disagreement off-domain), (d) **REJECT a non-convergent "sum" with a fake closed form**. A gate that catches
all four is trustworthy.

## 4. INFRA REALITY CHECK — ground the toolchain BEFORE designing around it
- **Confirm available:** `sympy` (symbolic), `mpmath` (arbitrary precision — ships with sympy), `scipy`
  (independent numeric quadrature) and/or `numpy`. `pip install` if absent; state what's present.
- If only `sympy`+`mpmath` are available, the third diversified method = **series expansion / different symbolic
  route / mpmath's own quadrature (`mp.quad`)** — still independent of sympy's `integrate`. Don't claim a 3rd
  method you didn't run.

## 5. TO-DOs / STEPS (box order)
1. **PLAN:** `weapons/symbolica/SPEC.md` — the three modes, the multi-method agreement gate, the
   proven-vs-verified labeling rule, the shared-blind-spot 3rd-method rule, the router (`symbolica_router.py`:
   integral/sum/limit/ODE with a plausible closed form → CLOSED-FORM; an equality to check → IDENTITY-PROVE;
   special value → reproduce; a problem with **no** closed form / only numeric-with-error-bars → report numeric +
   error bars, do NOT fake exactness; a modeling/interpretation question → κ=0 → armor). **GROUND by FETCH
   (don't assert):** that sympy `integrate`/`simplify` are heuristic (can fail/err); that multi-point
   high-precision numeric agreement is strong evidence of a symbolic identity (polynomial: Schwartz–Zippel
   intuition; transcendental: multi-point high-precision); known closed forms for the demo (Gaussian integral
   √π, Basel ζ(2)=π²/6, a definite integral with a tabulated value). Cite each in `GROUNDING.md`.
2. **BUILD THE GATE FIRST** (§3): `symbolica_gate.*` (two-method agreement + 3rd-method hook + domain/convergence
   checks + exactness labeling) + `selftest_all.py` (accept-correct / reject-wrong-constant / reject-domain-
   restricted / reject-nonconvergent). **Gate green before any result counts.**
3. **BUILD the weapon loop:** propose closed form → **agreement gate** → (load-bearing survivor) 3rd-method +
   cross-model audit of the setup. Machine-checkable → **execute, never vote.**
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` BEFORE running): (i) ∫₀^∞ e^{−x²}dx = √π/2,
   symbolic vs mpmath-50-digit vs scipy-quad — triple agreement; (ii) **reproduce Basel** ζ(2)=π²/6 (labeled
   reproduction) cross-checked; (iii) an **IDENTITY-PROVE** (a non-trivial trig/hypergeometric identity) via
   simplify→0 + 20 random points; (iv) show the gate **REJECTING** a deliberately wrong closed form (off by a
   constant) via numeric disagreement; (v) show the **shared-blind-spot guard**: a branch-cut-sensitive case
   where the diversified method matters.
5. **VERIFY INDEPENDENTLY:** a cross-model audit (Sonnet/Haiku ≠ the Opus generator; **never Opus-audits-Opus**;
   Fable inactive) that (a) re-evaluates each shipped result with its OWN independent numeric code, (b) attacks
   the gate with a wrong-but-close form and a domain-restricted form, (c) checks the exactness labels aren't
   over-stated ("proven" vs "verified to D digits"). Fix what's caught.
6. **REGISTER:** add **SYMBOLICA** to `Next/BOX_V5.md` (promote registry **W7** to a full Weapon + router branch)
   and `Expanding_Frontiers/HELMET/registry.json` (NAT_SCI's exact-computation `draws`). Honest `EVOLUTION_LOG`
   entry: **a weapon ADDED = capability EXPANSION, NOT a ≥10% promotion** (deterministic compute; the new value
   is the multi-method exactness certificate). Update `WEAPONS_BACKLOG.md` STATUS ✅.

## 6. HONESTY RAILS (non-waivable, specific to SYMBOLICA)
- **A single-engine answer is a claim, not a result** — every shipped value carries its cross-method agreement
  (which methods, how many digits, how many points).
- **Agreement is a risk, not proof** — for load-bearing results, a 3rd *methodologically different* check; record
  same-family agreement as a shared-blind-spot risk.
- **"Proven" vs "verified to D digits" are different words** — use the strong one only for an unconditional
  symbolic collapse to 0; otherwise label it empirical-strong.
- **Flag domain/convergence/branch-cut** — a closed form valid on a sub-domain is labeled with its domain; a
  non-convergent object is not given a closed form.
- **No closed form ⇒ numeric WITH error bars** (the W7 fallback), never a faked exact.
- **The gate that can't fail is not a gate** — ship no gate without its 4 reject self-tests.
- **κ=0 stays armor:** modeling/interpretation ("what does this integral *mean* physically") → ground + abstain.

## 7. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/symbolica/` — `SPEC.md`, `GROUNDING.md` (fetched sources + infra-check), the frozen
`symbolica_gate.*` + `selftest_all.py`, `symbolica_router.py`, `demo_*/` (committed predictions + verified
results + the agreement logs), `AUDIT.md` (cross-model red-team incl. wrong-constant / domain / over-labeling
attacks), `README.md` (what it is + honest ceiling: exact-by-agreement, not kernel-proven). Registration in
`Next/BOX_V5.md` (W7 → Weapon) + `HELMET/registry.json` + honest `EVOLUTION_LOG` entry; `WEAPONS_BACKLOG.md`
STATUS updated.

## 8. STAFF THE TEAM (v4 ladder; Fable INACTIVE → its slots on Opus, flag low confidence)
- **Symbolic setup** = code tier writes the sympy/mpmath/scipy calls (deterministic compute — the *agreement*,
  not the model, is the gate).
- **Library** = cheap model: fetch the heuristic-CAS caveats + the known closed forms for the demo.
- **Auditor** = a model ≠ the generator (Sonnet/Haiku; never Opus-audits-Opus) — re-evaluates each result with
  independent numeric code, attacks the gate, polices the exactness labels.

## 9. THE ONE-LINE TEST OF SUCCESS
**"SYMBOLICA ships only results that ≥2 INDEPENDENT methods agree on (symbolic + high-precision numeric, a 3rd
diversified method on load-bearing cases), labels 'proven' vs 'verified to D digits' honestly, flags domain /
convergence / branch-cut, reproduces known closed forms labeled as reproductions, and falls back to numeric +
error bars when no closed form exists — never a single-engine claim dressed as exact."** Exact by agreement,
honest about the gap from kernel-proof.
