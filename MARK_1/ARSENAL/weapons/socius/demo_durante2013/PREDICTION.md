# COMMITTED PREDICTION — Durante et al. (2013) Study 1, religiosity
*Written BEFORE running SOCIUS. Frozen. The point of the box is that some of these
predictions will be WRONG — that is the method working, not failing.*

**Finding under test (Durante, Rae & Griskevicius 2013, *Psychological Science* 24:1007–1016, Study 1):**
A Fertility × Relationship-status interaction predicts women's religiosity (single women
near peak fertility report lower religiosity; partnered women higher) — the single-path
analysis was statistically significant (p < .05).

**Known ground-truth verdict (Steegen, Tuerlinckx, Gelman & Vanpaemel 2016, *Perspectives
on Psychological Science* 11:702–712):** the religiosity effect in Study 1 is FRAGILE —
only **7 of 120** specifications (≈6%) are significant. This is the canonical
"dies in the multiverse" case. I have the raw data + their R code; I am reimplementing in
Python and predicting against this published verdict.

| # | Question | My committed prediction | Why |
|---|---|---|---|
| P1 | **S-REPRO** — does my Python pipeline reproduce the published multiverse structure? | **YES** — exactly **120** valid specifications (180 cells − 60 incompatible NMO×exclusion cells). | Direct from the R code's grid (2·5·3·3·2) and its two NA rules. |
| P2 | **S-REPRO** — does it reproduce Steegen's "≈7/120 significant"? | **YES, within ±2** — I expect **5–9** significant of 120. | Faithful reimplementation of the same processing + `lm` interaction p-value. |
| P3 | **S-MULTIVERSE** — does the finding survive? | **NO — it DIES.** Share significant in the hypothesised direction ≪ 50%; verdict `robust=False`. | The published verdict; ≈6% is far below any defensible robustness bar. |
| P4 | **S-MEASURE** — is the 3-item religiosity scale (Rel1–Rel3) reliable? | **YES** — Cronbach's α > 0.80. | Three tightly-related religiosity items typically cohere. |
| P5 | **S-MEASURE** — is the scale measurement-invariant across Single vs Relationship? | **PROBABLY YES (low confidence)** — I expect metric/scalar invariance to roughly hold. | No strong theoretical reason for differential item functioning by relationship status; but 3 items is a thin CFA — I may be unable to establish it cleanly. |
| P6 | **S-CAUSAL** — does the single-path effect survive a confounding-sensitivity (E-value) check? | **NO — fragile.** The standardised interaction effect is small → E-value near 1 → below a benchmark of 2. | If it dies under analytic choice, the one significant path is a weak effect with a tiny E-value. |
| P7 | **S-SAMPLE** — can I run a quantitative generalisability check? | **NO — ABSTAIN.** Durante used an MTurk convenience sample; I have no population target marginals in the data, so a quantitative representativeness check is not possible. I will route this to armor as a flagged, *abstained* generalisability concern, not fabricate population data. | Abstention is a scored deliverable; fabricating population data would violate the honesty rail. |

**Overall predicted SOCIUS verdict:** the Durante Study-1 religiosity finding REPRODUCES
as a published artifact but does NOT survive stress — it is an artifact of one analytic
path. SOCIUS should report it as **fragile / dies under the multiverse**, with measurement
reliability OK, causal sensitivity fragile, and sampling generalisability abstained.

**Honesty note (binding):** Reproducing 7/120 is a *reproduction*, not a discovery.
"Dies in the multiverse" is the valuable output. None of this proves the underlying
ovulation–religiosity hypothesis is true or false in nature — only that *this dataset does
not robustly support it*. SOCIUS raises trustworthiness; it does not manufacture truth.
