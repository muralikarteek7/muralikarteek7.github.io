# GROUNDING.md — SHOES_ROUTING (FOOTING + ROUTE-PLANNER)

*Load-bearing facts are FETCHED, not asserted from memory (box rule: ground, don't assert).
Fetched 2026-06-20 via WebSearch/WebFetch. Where the kickoff's paraphrase differed from the
fetched primary source, the FETCHED number is recorded and the discrepancy is flagged.*

---

## FACT 1 — LLM model-routing cuts cost at little/no quality loss (the efficiency premise)

**Fetched primary source: RouteLLM (LMSYS, ICLR 2025), https://www.lmsys.org/blog/2024-07-01-routellm/**

Exact figures from the fetched page (MT Bench, with LLM-judge data augmentation):
- **14% of queries routed to the strong model (GPT-4)** while maintaining **95% of GPT-4 performance**.
- That operating point is **"75% cheaper than the random baseline"** on MT Bench.
- Abstract-level summary (same source): **cost reductions of >85% on MT Bench, ~45% on MMLU, ~35% on GSM8K**
  vs GPT-4-only, while keeping ~95% of GPT-4 quality.
- MMLU detail: 54% of queries to the strong model for 95% quality (14% cheaper than random) — i.e. the
  *fraction routed to frontier and the cost win are benchmark-dependent*, not a single universal number.

**HONESTY / DISCREPANCY FLAG (audit-relevant):** the kickoff §4 paraphrased this as
"~67% cost cut routing ~14% to frontier at no quality loss." The fetched source supports the
**~14%-to-frontier** figure and a **large cost cut at ~95% (not 100%) quality** — but the specific
"67%" number is **NOT** the figure on the RouteLLM page (which reports "75% cheaper than random" for that
operating point, and >85% vs GPT-4-only at the abstract level). So: the *direction and order of magnitude*
of the kickoff claim is grounded; the exact "67%" is **not** reproduced from this source and is treated as
an approximate paraphrase, not a load-bearing exact figure. Quality is **~95%, NOT "no quality loss"** — the
honest framing is "little quality loss at this operating point," consistent with our weak-dominance claim.

Corroborating secondary sources (search hits, not individually fetched): anyscale/llm-router tutorial;
"Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey" (arXiv 2603.04445).

**What this grounds in our design:** ROUTE-PLANNER's premise — route the cheap-clearing majority to the
cheap rung, escalate only the slice that needs it — is an established, measured effect. The *size* of the
win is data-dependent; we therefore claim only weak-dominance / a measured cost win on OUR demo set, never
a borrowed headline number.

---

## FACT 2 — the SILENT-QUALITY-REGRESSION hazard + the pre-merge eval-gate mitigation (the adversary)

**Fetched sources:**
- "When Routing Collapses: On the Degenerate Convergence of LLM Routers," arXiv 2602.03478 —
  **routing collapse**: routers can systematically default one way (e.g. to the expensive model, or, in
  the cost-cutting direction, under-escalate), under-utilizing the right tier; and *"for the vast majority
  of queries multiple models are closely matched, making the choice inherently fragile — small
  perturbations change which model appears best, and routing quality degrades rapidly as noise increases."*
- Traceloop, "Catching Silent LLM Degradation," https://www.traceloop.com/blog/catching-silent-llm-degradation-how-an-llm-reliability-platform-addresses-model-and-data-drift —
  **silent degradation:** *"routing to cheaper models can degrade answers in ways that surface as customer
  tickets days later, not on dashboards … users feel it before you do."*
- digitalapplied, "LLM Model Routing in 2026," https://www.digitalapplied.com/blog/llm-model-routing-2026-cost-quality-optimization-engineering-guide —
  states the mitigation in the kickoff's own terms: *a **pre-merge eval gate of 50–500 cases** is the
  offline evaluation that catches quality issues before deployment* (this is exactly the 50–500-case gate
  the kickoff mandates).

**What this grounds in our design:** the **misroute / silent-quality-regression** threat is real and
documented, NOT a hypothetical we invented. FOOTING (ship-time uncertainty backstop) + ROUTE-PLANNER's
`misrouted_below_required_tier` flag + the mandated **pre-merge eval gate (50–500 cases)** are the
non-optional backstops named in the literature, not decoration. Self-test (g) makes this backstop executable.

---

## FACT 3 — uncertainty-estimation-for-routing methods (FOOTING's family)

**Fetched sources (search):**
- "Confident or Seek Stronger: Exploring Uncertainty-Based On-device LLM Routing," arXiv 2502.04428 —
  uncertainty estimates drive a route-up / stay decision.
- "UCCI: Calibrated Uncertainty for Cost-Optimal LLM Cascade Routing," arXiv 2605.18796 — calibrated
  uncertainty for cascade routing.
- "ReDAct: Uncertainty-Aware Deferral for LLM Agents," arXiv 2604.07036 — uncertainty-aware DEFERRAL
  (abstain/escalate) for agents.
- General finding (multiple hits): uncertainty estimation = likelihood-based, sampling/consistency-based
  (multiple samples → measure agreement), and probing-based methods. **Crucially: "for LLMs, token
  probabilities are often miscalibrated and uncertainty estimation for free-form generation remains
  active [research]."**

**What this grounds — AND the kappa honesty fix:** the sampling/consistency family (generate multiple
answers, measure agreement) is exactly FOOTING's **cross-paraphrase disagreement** signal. The fetched
literature confirms the load-bearing honesty point: **deciding whether two free-form answers "agree" is a
semantic comparison that is miscalibrated/model-dependent — it is kappa<1 (a judgment), NOT kappa=1.** That
is why FOOTING computes the disagreement rate through a *comparison oracle* (a model in production) and
treats the resulting verdict as a ROUTING decision, never a certification. Calibration needs held-out
ground truth that is not available at inference → there is **no exact verifier of "is this well-calibrated?"**
→ FOOTING is kappa=0 armor, confirmed by the "remains active / miscalibrated" state of the field.

---

## FETCH FAILURES / LIMITS (honest)
- No fetch failed outright. The RouteLLM page was fetched directly; FACT 2 and FACT 3 rely on search-result
  summaries plus one directly-fetched corroborating page each — the individual arXiv PDFs were NOT each
  opened in full, so their headline claims are recorded as **search-grounded, not line-verified**.
- The kickoff's exact "~67% cost cut" number is **NOT reproduced** from the primary source (see FACT 1 flag);
  treated as an approximate paraphrase. We do not ship "67%" as a load-bearing figure.

## Infra confirmed present (to extend, per kickoff §4)
- **Model ladder** exists (`Next/BOX_V4.md`): machine-checkable→EXECUTE($0) · routine→Haiku · hard-but-
  executable→write-a-solver+EXECUTE · genuinely-un-executable-hard→Opus (Fable when active). ROUTE-PLANNER
  routes onto exactly these rungs.
- **Saturation tripwire** exists (`Next/router.py`, `saturation_tripwire()` → STRUCTURAL_GAP). ROUTE-PLANNER's
  per-track `verified-fact-delta=0` stuck-detector EXTENDS it (machine-confirmed those functions exist).
- **Cheap tier (Haiku)** present for FOOTING's verdict (BOX_V4 ladder).
- **TEMP FALLBACK noted:** Fable 5 is inactive → "escalate" resolves to Opus (flag low confidence on truly
  un-executable hard reasoning); cross-model audits run on Sonnet/Haiku, never Opus-audits-Opus.

## Sources
- https://www.lmsys.org/blog/2024-07-01-routellm/
- https://arxiv.org/html/2602.03478v1 (When Routing Collapses)
- https://www.traceloop.com/blog/catching-silent-llm-degradation-how-an-llm-reliability-platform-addresses-model-and-data-drift
- https://www.digitalapplied.com/blog/llm-model-routing-2026-cost-quality-optimization-engineering-guide
- https://arxiv.org/pdf/2502.04428 (Confident or Seek Stronger)
- https://arxiv.org/html/2605.18796 (UCCI)
- https://arxiv.org/html/2604.07036v1 (ReDAct)
- https://arxiv.org/pdf/2603.04445 (Dynamic Model Routing & Cascading survey)
