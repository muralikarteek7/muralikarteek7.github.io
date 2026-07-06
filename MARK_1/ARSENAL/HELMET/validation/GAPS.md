# WHAT'S MISSING — honest gap assessment of HELMET + weapons (2026-06-20)

*Grounded in the A/B/C validation (`RESULTS.md`) + its independent audit (`AUDIT.md`) + what was observed
building and machine-checking the arsenal. Ordered by how load-bearing the gap is. This is honest analysis, not
a to-do the system can't do — several of these are genuine open questions about whether the design works.*

## TIER 1 — load-bearing gaps (these decide whether the HELMET is real)

1. **The Provost's κ-classification on UNLABELED inputs is UNTESTED — and it's the load-bearing step.**
   The entire helmet value proposition is "route correctly: κ=0 → abstain, κ=1 → the right weapon." The
   validation **pre-labeled κ** and handed it to the helmet arm, so the arm applied a *given* rule — it never
   *classified* a raw problem. The one topic the helmet beat armor on (T5) is therefore a **rule-compliance**
   result, not a routing-intelligence one. **And we already know the provost CAN mis-classify** (the red-team
   caught it tagging "capital of Australia" as κ=0). **The single most valuable next test:** a routing-accuracy
   benchmark — feed N unlabeled cross-disciplinary problems, measure whether the provost assigns the correct
   κ / department / weapon, scored against a committed key. Until that runs, the helmet's distinctive value over
   plain armor is **unproven.**

2. **The runnable orchestrator does NOT auto-dispatch to weapons end-to-end.** `provost.py` classifies and the
   registry maps department→weapon, but there is **no single pipeline** `problem → provost → auto-select & RUN
   the right weapon's verifier → deliver`. In the validation, Arm A *simulated* the helmet by being told which
   weapon to run. The actual wiring (provost output → dispatch to `<weapon>_router.py` / its frozen verifier) is
   missing. Right now the helmet is a **routing brain + 12 separate weapons**, not one closed loop.

3. **The helmet's value over plain ARMOR is ≤10%, single-topic, and artifact-contaminated.** On n=5, armor-only
   (B) scored 4.0–4.5 vs helmet (A) 5.0 — and the gap is one pre-labeled abstention topic. **No promotion; the
   capability ratchet stays OPEN at v3.** A real A-vs-B answer needs the routing test (gap #1) + more topics.

## TIER 2 — coverage / validation gaps

4. **Validation breadth is thin.** n=5, **single run, no replication, no multiple seeds, soft judgment scoring**,
   and the topics were author-chosen (selection risk). Plain Opus 4.8 was already correct on 4/5 — so the test
   barely exercised the scaffolding. A credible validation needs **N≥20 topics, held-out selection, ≥3 seeds**,
   and more topics where plain Opus actually *fails* (so the scaffolding has room to show value).

5. **Each weapon rests on ~1 demo + 1 audit.** Several weapons have a single `demo_*/` (controlled/toy ground
   truth). Real-world robustness is largely untested: does PSYMETRIX/TRIALGUARD GRIM hold on messy real papers?
   does ECONOMETRIX's OOS guard behave on a real strategy with real costs? does CODEFORGE's contamination
   defense survive a genuinely novel spec? The gates are *sound on their self-tests*; their *coverage* on
   in-the-wild inputs is not characterized.

6. **The Dean / CROSS-disciplinary integration is unexercised end-to-end.** The registry has a Dean + CROSS
   scale, but no run has actually fired ≥2 weapons and had the Dean integrate them into one artifact. (The
   earlier helmet test went CROSS on the 4-day-week question but ran no weapons.)

## TIER 3 — known structural / external limits (honest, mostly out of our control)

7. **The capability lever is a confirmed honest NEGATIVE (infra-gated).** CODEFORGE and PROOFSMITH both ran the
   "verifier-gated iterate vs equal-compute best-of-k" A/B → **+0pp**. The arsenal raises **trustworthiness +
   catches errors**; it does **not** make the model solve problems it otherwise couldn't. The "iterate beats
   best-of-k" bet stays unproven and needs SWE-bench-scale contamination-free infra (the standing v5 infra gate).

8. **No live cost / Registrar accounting.** "Value × open-defects ÷ cost" + anti-theater scaling is a *principle*
   enforced only by provost.py's scale tiers, not *measured* per run. The validation is a concrete reminder: the
   helmet spent ~426k tokens / 20 agents to beat a single plain-Opus call by ≤1.5/5 points — the **cost/benefit
   boundary (when wearing the helmet is worth it) is not characterized.** It's worth it when the problem genuinely
   needs execution or abstention; on the 3/5 topics plain Opus already nailed, the overhead bought nothing.

9. **Toolchain fragility.** Observed live: OPTIMA's CBC cross-check was **x86-blocked on this ARM Mac**;
   PROOFSMITH needs Lean; SYMBOLICA needs sympy/scipy; REPRO-ML/ECONOMETRIX need their stacks. Each weapon's
   κ=1 guarantee is only as available as its toolchain. Honest fallbacks exist (z3 for proof, etc.) but
   availability is a real operational gap.

10. **Fable 5 inactive** → the un-executable creative-construction slice (the weapon "propose" stage) runs on
    Opus (0.33 vs Fable 1.00 on that slice). Mitigated by "make it executable so the machine carries it," but the
    de-novo creative leap (inventing the load-bearing new idea) is weaker — an external dependency, not a design flaw.

## The one test that would settle the most (recommended next)
**A routing-accuracy benchmark for the Provost** (gap #1): 20–30 unlabeled cross-disciplinary problems →
provost classifies (κ, department, weapon, scale) → scored against a committed key, cross-model-audited. THEN
re-run the A/B/C with κ NOT pre-labeled, so the helmet has to classify on its own. That directly tests the
helmet's distinctive mechanism — and would either validate the routing or expose it as the weak link the
red-team already hinted at. Everything else (more topics, Dean integration, end-to-end dispatch) is secondary to
proving the routing brain actually works on raw inputs.

## Honest one-paragraph summary
The 12 weapons are individually sound (all gates machine-green) and the armor/abstention discipline is real and
measurable (helmet was the only arm that never over-committed). But the HELMET as an *orchestrator* is, today, a
**routing brain plus a rack of separate weapons** — its load-bearing claim (that it correctly *routes* raw
problems to the right weapon and abstains on κ=0) is **not yet validated on unlabeled inputs**, the end-to-end
auto-dispatch is **not wired**, and its measured advantage over plain armor is **≤10% on one artifact-laden
topic**. It is honestly "organized, not smarter" — and right now, more *organized in principle* than *proven to
organize itself.* The routing benchmark is the missing keystone.
