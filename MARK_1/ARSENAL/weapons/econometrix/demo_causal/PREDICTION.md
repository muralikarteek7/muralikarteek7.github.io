# COMMITTED PREDICTION — the E-CAUSAL pre-trends / placebo demo
*Written BEFORE running. Frozen. Demonstrates ECONOMETRIX's causal-identification gate: a quasi-
experimental causal claim is reported ONLY with its testable diagnostics + a sensitivity number for the
untestable assumptions — never a bare "X caused Y." The "dies under stress" causal analogue: a confound
that a NAIVE difference-in-differences would read as a significant effect is CAUGHT by the pre-trends
placebo.*

**The setup (synthetic DGP, KNOWN ground truth — honestly labelled, NOT a reproduction of a published
number; that is the separate E-REPRO path).** Two difference-in-differences panels, 40 units × 12
periods, treatment at period 7:
- **Scenario A — CLEAN:** a genuine treatment effect (+3.0), parallel pre-trends by construction.
- **Scenario B — CONFOUNDED:** **NO true treatment effect (0.0)**, but the treated group is on a
  divergent PRE-existing trend. A naive 2×2 DiD will misread the trend as a treatment effect.

Plus an **Oster (2019) δ** sensitivity on an observational confounding scenario (robust vs fragile), and
an **E-value** on the clean recovered effect.

| # | Question | Committed prediction | Why |
|---|---|---|---|
| C1 | **Scenario A** — does the pre-trends placebo PASS? | **YES** — joint lead test p > 0.05; parallel-trends plausible. | Pre-trends are parallel by construction. |
| C2 | **Scenario A** — is the post-period effect recovered near +3.0? | **YES** — estimated post-treatment effect ≈ 3.0 (±0.5). | The DGP's true effect is 3.0. |
| C3 | **Scenario B** — does the pre-trends placebo FAIL (catch the confound)? | **YES — the leads are jointly ≠ 0, p < 0.01 → FLAGGED.** This is the headline: the confounded design DIES under the placebo. | The injected divergent pre-trend shows up in the lead coefficients. |
| C4 | **Scenario B** — would a NAIVE DiD have reported a "significant effect"? | **YES** — the naive post-vs-pre, treated-vs-control contrast is non-zero and would look significant, i.e. the trap a naive analyst falls into. | A pre-trend masquerades as a treatment effect in a 2-period DiD. |
| C5 | **Oster δ** — robust scenario |δ| ≥ 1, fragile scenario |δ| < 1? | **YES** — the stable-coefficient design gives |δ| ≥ 1 (robust); the collapsing-coefficient design gives |δ| < 1 (fragile). | δ measures how strong unobserved selection must be to kill the effect. |
| C6 | **E-value** on the clean effect | A **moderate-to-large** E-value (> 2) for a d≈ large effect; reported as the sensitivity number, NOT as proof of causality. | The clean effect is large relative to noise, so an unobserved confounder would need to be strong. |
| C7 | Honest miss I'm allowing for | The exact post-effect estimate or the precise δ value may differ from my point guess; the DIRECTION (A passes, B fails, robust vs fragile) is what I'm committing to. | Finite-sample noise. |

**Overall predicted ECONOMETRIX verdict:** Scenario A is *consistent with* identification (pre-trends
pass) and carries an E-value sensitivity number; Scenario B is **FLAGGED** — the pre-trends placebo
catches the confound that a naive DiD would have laundered into a "significant treatment effect." The
untestable post-period parallel-trends assumption is never certified; only a sensitivity number is given.

**Honesty note (binding):** Passing the pre-trends test is necessary, NOT sufficient — post-period
parallel trends is fundamentally untestable (Roth 2022). ECONOMETRIX reports the testable diagnostic AND
a sensitivity number, and NEVER emits a bare "the treatment caused the outcome." A flagged design is the
valuable output: it stops a confounded correlation from being sold as a causal effect.
