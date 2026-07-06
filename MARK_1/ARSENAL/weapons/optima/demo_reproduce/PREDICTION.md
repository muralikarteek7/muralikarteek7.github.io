# PREDICTION — REPRODUCE-RECORD demo (committed BEFORE running)
*Written 2026-06-20, before `run_demo.py` executed. Frozen forecast; compare to RESULT.json.*

Reproduce the **published optimum of TSPLIB `burma14`** (14 Burmese cities, GEO distances). This
is a **labeled REPRODUCTION of a known optimum**, never a record. Two independent checks of the
solver's answer: (a) the **published optimal length 3323** (TSPLIB / Heidelberg STSP table,
fetched — see GROUNDING.md), and (b) an **independent Held-Karp DP** exact optimum (a different
algorithm than CP-SAT's MTZ).

| # | claim | committed prediction | why |
|---|---|---|---|
| P1 | CP-SAT solves burma14 to OPTIMAL | **OPTIMAL** | n=14 MTZ closes instantly; probe already confirmed |
| P2 | certified optimal tour length | **3323** | the published TSPLIB optimum; probe hit it exactly with the documented GEO formula |
| P3 | independent **Held-Karp** optimum | **3323** (== CP-SAT, == published) | a different exact method must agree or the reproduction is void |
| P4 | gate verdict on the returned tour | **OPTIMAL_CERTIFIED** | feasibility (degree-2 + MTZ) re-checked + objective recomputed + independent optimum matches |
| P5 | label assigned | **REPRODUCTION (matches published optimum), NOT a discovery/record** | honesty rail: a known optimum is never claimed as new |
| P6 | distance formula used | **TSPLIB GEO** (lat/long → radians via the documented deg+min formula, RRR=6378.388) | reproducing the published number requires the exact TSPLIB metric |

**Falsifiers:** CP-SAT length ≠ 3323; Held-Karp ≠ 3323 (would mean the GEO metric or model is
wrong — a transparent negative we would report, NOT paper over); gate verdict ≠ OPTIMAL_CERTIFIED.

**Honesty commitment:** burma14's optimum is a **known published result**. Reproducing it
demonstrates the REPRODUCE-RECORD mode and the certificate; it is **NOT** an open-problem solve and
**NOT** a record. Hitting 3323 via three independent routes (CP-SAT, Held-Karp, the literature) is
the strongest form of "the certificate, not the solver, is the result."
