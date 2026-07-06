# HELMET / University-Mode — SPEC

*The institution design: the Provost intake schema, the department registry, the R&D lifecycle, and the
Integrity Office + Registrar rules. Grounded in the science-of-science / team-science literature (every
load-bearing claim carries a source + a confidence label; counter-evidence is kept, not hidden).*

> **The non-negotiable framing (repeat in every University-Mode output):** the Helmet makes the model
> **ORGANIZED, RIGOROUS, COMPREHENSIVE — not smarter.** It cannot exceed the underlying model's capability
> ceiling. It improves *process* (specialization · grounding · method/weapon selection · independent peer
> review · honest abstention), which is genuinely how top research orgs outperform a lone responder — **and
> the same literature shows structure has limits and can backfire**, which is why the Registrar and Integrity
> Office are first-class components, not afterthoughts.

---

## 0. Why a "university" process raises *output quality* — grounded, with the counter-evidence

This is the load-bearing justification. It is stated with sources and confidence labels so the design is not
asserted. Confidence: **verified-primary** = paper/abstract fetched from an authoritative source this run;
**secondhand** = consistent across secondary sources, primary paywalled; **unverified** = search-snippet only.

| # | mechanism the Helmet institutionalizes | grounded finding | conf. | source |
|---|---|---|---|---|
| 1 | **Specialization** (route to the right department) | Teams pooling non-overlapping expertise dominate knowledge production across all fields studied (19.9M papers, advantage rising over 50 yrs) | verified-primary | Wuchty, Jones & Uzzi 2007, *Science* 316:1036 ([doi](https://www.science.org/doi/10.1126/science.1136099)) |
| 2 | **Independent peer review** (cross-model audit) | Post-review, 33/34 manuscript-quality dimensions improved (Goodman 1994). **BUT inter-rater κ ≈ .17** — barely above chance | secondhand / **verified-primary** | Bornmann, Mutz & Daniel 2010, *PLOS ONE* 5:e14331 ([url](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0014331)) |
| 3 | **Replication / reproduce-before-trust** (the Stats facility) | Only **36%** of 100 top-psych studies replicated (97% were orig. significant); replication effects ≈ half size | verified-primary | Open Science Collaboration 2015, *Science* 349:aac4716 ([doi](https://www.science.org/doi/10.1126/science.aac4716)) |
| 4 | **Cognitive diversity** (multi-model / multi-lens) | Ethnically diverse teams: **+10.6% citations** (matched-paper causal est., 95% CI 8.1–12.4) | verified-primary | AlShebli, Rahwan & Woon 2018, *Nat. Comms* 9:5163 ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6279741/)) |
| 5 | **Independent verification catches errors** (the machine gate + peer review) | Formal independent inspection caught **82% of defects**, 38 vs 8 defects/KLOC vs author testing alone (~4.75×) | secondhand (consistent ×multiple) | Fagan 1976, *IBM Sys. J.* 15:182 ([doi](https://dl.acm.org/doi/10.1147/sj.153.0182)) |
| 6 | **Structured stage-gate process** (the lifecycle) | Structured-process firms ≈ 59% NPD success; best-practice firms 45% vs 25% of sales from new products | secondhand | PDMA 2021 survey, Knudsen et al. 2023, *JPIM* ([url](https://onlinelibrary.wiley.com/doi/10.1111/jpim.12663)) |

**The counter-evidence is load-bearing too — it is *why* the Registrar and Integrity Office exist:**
- **Bigger ≠ better. Large teams are measurably *less* disruptive:** scaling a team from 1→50 members drops
  its work by ~**70 percentiles** on the disruption index (65M papers/patents/products). Small teams disrupt;
  large teams develop. → **This grounds the Registrar's anti-theater rule: scale the institute to the problem;
  a one-liner gets ONE specialist, not a faculty.** *(Wu, Wang & Evans 2019, Nature 566:378, verified-primary.)*
- **Peer review is an imperfect filter, not a truth oracle (κ ≈ .17), and reviewers from the same epistemic
  community share blind spots** → grounds the Integrity Office rule that peer review must be **cross-MODEL
  (different base), not same-community**, and that agreement is a shared-blind-spot *risk*, not proof (C8).
- **Structured stage-gates over-filter radical ideas** (Christensen disruption critique) and the headline
  "6.5× success" figure is **unverified** (practitioner-sourced) → grounds keeping the lifecycle *depth-scaled*
  and the honesty rail "process is judged by verified output, never by departments convened."
- **Diversity-trumps-ability is landscape-sensitive** (Hong–Page holds on rough landscapes, fails on smooth
  ones; Reijula–Kuorikoski 2021) and AlShebli's scientist-level 47.7% is selection-inflated → we claim only the
  conservative matched estimate and treat multi-model diversity as a *help, not a guarantee*.
- **Replication-rate disputes exist** (Gilbert et al. 2016 argue OSC's 36% under-states true reproducibility)
  → the 36% is cited as an order-of-magnitude motivation, not a settled constant.

**Net, honestly:** the literature supports *specialization + independent verification + reproduce-before-trust
+ depth-scaled structure* as real quality levers, and simultaneously warns that *scale and process have
diminishing/negative returns past the problem's needs*. The Helmet is built to capture the first and resist the
second. None of this makes the model smarter; it makes the *process* rigorous. **Unverified items (Stage-Gate
6.5×; red-team breach-cost; internal Wuchty ratios) are flagged and NOT used as load-bearing.**

---

## 1. THE PROVOST — intake schema (triage & routing brain)
The Provost reads any problem and emits a structured intake. The deterministic core is
[`provost.py`](provost.py) (machine-tested, 6/6 routing cases); in live use an Opus Provost agent fills the
descriptor from natural language and then *runs* `provost.py` to get the canonical machine-checked plan.

```jsonc
{
  "problem": "<raw statement>",
  "domains": ["<department keys: MATH_TCS|STATS|QUANT_PSYCH|SOCIAL_SCI|CS_ENG|NAT_SCI|ECON_FIN|HUMANITIES_LAW_POLICY>"],
  "task_type": "construct|prove|analyze|measure|design|decide|explain|forecast",
  "kappa": 0.0,            // does a cheap EXACT non-gameable verifier exist for the load-bearing claim?
  "known_vs_open": "known|open|n/a",
  "has_data": false,        // empirical task with data / open data+code?
  "stakes": "low|medium|high",
  "triviality": "oneliner|bounded|substantial",
  "proxy_only_scorer": false, // is the only "verifier" a gameable proxy (LLM-judge/in-sample)? -> forces kappa=0
  "groundable": false         // kappa=0 ONLY: settleable by a FETCHED authoritative source (a fact)? -> ground
                              // & ANSWER, do NOT abstain. (Red-team fix: a factual lookup is not a normative
                              // open question; abstention is mandated only for kappa=0 AND not-groundable.)
}
```
Output = the routing plan: convened departments (+ effective track), **scale** (DESK/STANDARD/FULL/CROSS),
**lifecycle stages**, `peer_review_required`, `must_end_in_abstention_if_unverifiable`, and the integrity flags.

**The κ-gate is inherited verbatim from the v5 router** (`Next/BOX_V5.md` §2): a verifier qualifies iff it
re-checks the actual returned object from scratch, is independent of the producer, makes false-positives
detectable, and is **not gameable by overfit**. A proxy (LLM-judge / in-sample score / human rating) does NOT
raise κ — `provost.py` forces such a task to κ=0 (armor only). This is the C14 Sharpe-overfit trap, encoded.

## 2. THE DEPARTMENT REGISTRY — problem-type → department → weapon/method
Full data in [`registry.json`](registry.json). Each department draws a **weapon** (κ>0 build/verify), an
**armor** method-cluster (κ=0 judgment), or is **mixed** (routes internally by checkability, like SOCIUS/
PSYMETRIX). A new weapon = a new department (extensible). Effective track is κ-gated: a weapon/mixed
department whose *task* κ=0 is forced down to the armor track for that task.

| department | covers | draws | ceiling |
|---|---|---|---|
| **MATH_TCS** | construct/prove a checkable object | Frontier Construction Engine | reproduces/extends; invents new ideas rarely; never "solves open problem" |
| **STATS** (core facility) | reproduce · multiverse · power · meta · causal | reproduction/verifier armor + SOCIUS/PSYMETRIX methods | raises trustworthiness, not truth |
| **QUANT_PSYCH** | psychometrics, measurement, forensics | **PSYMETRIX** | certifies consistency/fit, never truth; inconsistency ≠ fraud |
| **SOCIAL_SCI** | empirical social research w/ data | **SOCIUS** | findings that DIE under stress are the product |
| **CS_ENG** | algorithms, systems, code | execution + test-runner armor + algorithm discovery | gates what it can execute; design claims → armor |
| **NAT_SCI** | physics/chem/bio quantitative | simulation + symbolic/numeric + grounding | wet-lab truth not machine-checkable → abstain |
| **ECON_FIN** | markets, pricing, policy eval | out-of-sample backtest + causal | in-sample score gameable → not κ=1; flips OOS → abstain |
| **HUMANITIES_LAW_POLICY** | interpretive/normative (κ=0) | **armor only** | ground + abstain; never fabricated certainty |
| **DEAN** | spans ≥2 departments | convenes + integrates | one honest artifact; abstentions carried forward unflattened |

## 3. THE R&D LIFECYCLE (depth scaled by the Provost)
`INTAKE/FREEZE → LITERATURE (fetch real SOTA, don't assert) → DESIGN (hypotheses + method/weapon selection +
the verification plan: what counts as proof) → EXECUTE (run weapons/armor; machine-checkable → execute & gate)
→ PEER REVIEW (adversarial, cross-model ≠ generator; reproduce; catch overclaims) → REVISE (to standard or
honest-stop) → DELIVER (honest writeup + calibrated claim + the explicit limit).`

Scale → depth (the Registrar dial, grounded in Wu 2019 "scale ≠ value"):
- **DESK** (oneliner, low stakes): `INTAKE → EXECUTE → DELIVER`, one specialist. No committee, no Dean.
- **STANDARD** (single dept, bounded): `INTAKE → LITERATURE → EXECUTE → PEER_REVIEW → DELIVER`.
- **FULL** (single dept, substantial/high-stakes): all 7 stages.
- **CROSS** (≥2 depts): all 7 stages + the **Dean** integrates.

## 4. THE INTEGRITY OFFICE (non-waivable; institutionalizes the box honesty rules)
1. **No claim ships without proof** — a machine check (executed, not voted) or a fetched source.
2. **Independent cross-model peer review is mandatory** before any result ships — auditor model ≠ generator
   model (Fable inactive → Sonnet/Haiku, **never Opus-audits-Opus**). *(Grounded: same-community review shares
   blind spots, κ≈.17; cross-base review is the C8 fix.)*
3. **Reproduction is labeled reproduction** (source + date); **never claim to solve an open problem** — exhibit
   the verified object or report you did not find one.
4. **κ=0 work ends in grounded analysis + honest ABSTENTION**, never fabricated breakthrough — **with one
   distinction the red-team forced (2026-06-20):** a κ=0 task that is **groundable** (a fact settleable by a
   fetched authoritative source — capital cities, dates, settled records) is **ground-&-answered, NOT abstained
   on**; abstention is mandated only for κ=0 *and not groundable* (normative / metaphysical / open judgment).
   "Solved at the highest level" = resolved to the limit of the verifiable, with that limit stated.
5. **A weak/gameable proxy does not raise κ** — declined as a verifier (reward-hacking surface).
6. **INCONSISTENCY ≠ FRAUD** (forensics reports the exact arithmetic and STOPS; never accuses).
7. **Agreement is a risk, not a result** — proposer + auditor agreeing on a "win" is a shared-blind-spot risk →
   a third independent machine check is required for any record-class claim.

## 5. THE REGISTRAR (budget & scaling; the anti-theater control)
- Match institute size to the problem: the **cheapest path that clears the bar**.
- A one-line / factual question gets **ONE specialist (DESK)**, never a faculty. *(Grounded: Wu 2019 — added
  members past need REDUCE disruptive value; bureaucracy over-filters. Convening unused departments is
  negative-value theater.)*
- **Convening a department that adds no verified value over one specialist is a DEFECT** the Registrar fails.
- Log `value × open-defects ÷ cost`; **permission to stop** when the done-criterion is met.

## 6. STAFFING (v4 model ladder; ⚠ Fable inactive → its slots on Opus, flag low confidence)
- **Provost** = Opus (triage/routing/intake classifier).
- **Department PIs** = routed per registry; code/execute tier does machine-checkable work; frontier+gate for
  novel construction. Machine-checkable → **execute ($0), never vote**.
- **Library** = cheap model (Haiku/Sonnet): fetch real SOTA; don't assert.
- **Peer-review committee** = a model **≠ the generator** (Sonnet/Haiku; never Opus-audits-Opus while Fable is down).
- **Dean** = Opus (integrate cross-disciplinary outputs into one honest artifact).
- **Registrar / Integrity Office** = the orchestrator itself (enforces budget + the honesty veto).

## 7. SUCCESS CRITERION (the one-line test)
*Given ANY problem, University Mode convenes exactly the right departments at the right scale, runs the full
lifecycle, an independent model confirms every shipped claim, the κ=1 work yields verified objects, the κ=0 work
yields grounded analysis + honest abstention — and a one-line question is answered by one specialist, not a
faculty.* Rigorous, comprehensive, honest — and not one neuron smarter than the model wearing it, which is
exactly why it is safe to wear over the weapons.

---
*Grounding gathered via live WebSearch/WebFetch (cross-model Library agent, 2026-06-20); confidence labels and
counter-evidence preserved from that fetch. Unverified items are flagged in §0 and excluded from load-bearing use.*
