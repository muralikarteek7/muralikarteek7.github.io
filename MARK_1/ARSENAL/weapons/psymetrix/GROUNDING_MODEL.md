# P-MODEL — grounded fit conventions (fetched, not asserted)

*Grounding pass 2026-06-20 for the full IRT/CFA/SEM engine (`model_verify.py`). Thresholds are load-bearing;
each is from a primary/authoritative source (Sources at end).*

## CFA/SEM global fit cutoffs
- **Hu & Bentler (1999)** GOOD fit (JOINT, not per-index golden numbers): **CFI ≥ .95 AND RMSEA ≤ .06 AND
  SRMR ≤ .08** (their two-index strategy = SRMR≤.08 paired with CFI≥.95 or RMSEA≤.06).
- Common two-tier **ACCEPTABLE**: CFI ≥ .90, RMSEA ≤ .08, SRMR ≤ .10 (looser textbook synthesis;
  Browne & Cudeck 1993 for RMSEA tiers).
- **χ²/df** has no agreed cutoff (<2 strict, <3 lenient); the χ² test over-rejects at large N — reported as a
  soft heuristic only.
- **CAVEAT — not golden rules:** Marsh, Hau & Wen (2004) — cutoffs were derived from a specific simple-structure
  CFA simulation and do not generalize; do not auto-fail on a single index. `model_verify` reports the numbers +
  a verdict relative to the benchmarks and says explicitly "fit ≠ truth."

## Measurement invariance deltas
- **Cheung & Rensvold (2002): ΔCFI ≤ .01** ⇒ invariance holds. **Chen (2007):** pair ΔCFI ≤ .010 with
  **ΔRMSEA ≤ .015** (best for N>300).
- **CAVEAT — small df:** Kenny, Kaniskan & McCoach (2015) — RMSEA/ΔRMSEA misbehave at low df → down-weight
  ΔRMSEA, lean on ΔCFI. (This is the same blind-spot SOCIUS's S-MEASURE already encodes.)

## IRT
- **2PL IRF:** `P(θ)=1/(1+e^{−a(θ−b)})`; `a`=discrimination, `b`=difficulty. **Item information**
  `I_i(θ)=a²·P·(1−P)`, peaks at θ=b. **Test information** `I(θ)=Σ I_i(θ)`; **SE(θ)=1/√I(θ)**.
- **GRM** (Samejima 1969): one `a` per item, K−1 ordered thresholds; category prob = difference of adjacent
  boundary curves.
- **Item/model fit:** S-X² (Orlando & Thissen 2000; magnitude via per-item RMSEA≤.06); M2 (Maydeu-Olivares & Joe
  2005); infit/outfit 0.5–1.5 (Rasch).
- **Local dependence — Yen's Q3:** residual correlation after conditioning on θ; flag **|Q3| > 0.2**
  (Chen & Thissen 1997). Q3 has a small negative bias (E≈−1/(n−1)); prefer **mean-corrected** `Q3 − mean(Q3)`
  (Christensen et al. 2017). `model_verify` uses the mean-corrected rule.

## Dimensionality
- **Parallel analysis** (Horn 1965; **Glorfeld 1995 95th-percentile** reference — the modern default, more
  conservative than Horn's mean). **Kaiser eigenvalue>1 over-extracts** — reported but secondary.

## Reliability
- **McDonald's ω** preferred over **Cronbach α** when loadings are unequal (α assumes tau-equivalence and is a
  lower bound). **ω_total = (Σλ)² / ((Σλ)² + Σ(1−λ²))** from standardized 1-factor loadings. Report both; the
  α–ω gap diagnoses tau-equivalence violation.

## Demo dataset (real, bundled — no fabrication)
- **Holzinger-Swineford 1939** ships inside semopy (`from semopy.examples import holzinger39`): 301 students, 9
  cognitive tests x1–x9, **known 3-factor structure**: `visual =~ x1+x2+x3`, `textual =~ x4+x5+x6`,
  `speed =~ x7+x8+x9`. The canonical CFA teaching dataset.
- **Grounded reference fit** (lavaan, widely published): the *correct* 3-factor model reaches only
  **CFI≈.931, TLI≈.896, RMSEA≈.092, SRMR≈.065** — i.e. ACCEPTABLE by the two-tier convention but **NOT** strict
  Hu & Bentler good-fit. `model_verify`'s SRMR matches lavaan to 4 dp (0.0652). This is itself the honest lesson:
  even the textbook-correct model does not clear the strict cutoffs.

## Sources (fetched)
- Hu & Bentler 1999 — semanticscholar d2cd75e6…; Marsh/Hau/Wen 2004 — scirp ref 1393961, ora.ox.ac.uk uuid
  b059d29a; Cheung & Rensvold 2002 / Chen 2007 — researchgate 233253342 / 232911947; Kenny et al. 2015 —
  journals.sagepub.com/doi/10.1177/0049124114543236; Yen Q3 / Christensen — ncbi PMC5978551, ub.edu/gdne
  local_dependence_epm12.pdf; GRM — assess.com/graded-response-model, stata irtgrm; S-X²/M2 —
  philchalmers.github.io/mirt itemfit; parallel analysis — sagepub 10.1177/0013164495055003002,
  en.wikipedia.org/wiki/Parallel_analysis; omega — tandfonline 10.1080/19312458.2020.1718629; HS1939 —
  rdrr.io/cran/lavaan/man/HolzingerSwineford1939.html; semopy examples — semopy.com/docs/examples.

## Honesty caveat (from the grounding agent)
The Hu & Bentler primary PDF refused connection at fetch time; its exact cutoffs (.95/.06/.08) are grounded in
the Semantic Scholar abstract + multiple secondary sources that agree — agreement among secondaries is a
shared-source risk, not independent confirmation. The numbers are also the universally-cited values and match
the lavaan/semopy tooling behaviour, so confidence is high, but the literal page-level table was not fetched.
