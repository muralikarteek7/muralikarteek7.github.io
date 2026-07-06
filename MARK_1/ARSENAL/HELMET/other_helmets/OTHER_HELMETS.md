# OTHER HELMETS — can the orchestration pattern generalize? (2026-06-20)

*Method: 8 candidate helmet-domains analyzed independently (Sonnet, web-grounded) → adversarial deflationary
ranking (Sonnet ≠ generator) → Dean synthesis (Opus). Run `wf_837513ad-583`; raw `run_raw.json`. **This is a
κ=0 DESIGN argument, NOT a validated result** — no cross-domain A/B was run; the classifications are the
trustworthy output, the numeric scores are ordinal/illustrative only.*

## The answer in one line
**Yes — the helmet is an abstract PATTERN (triage → route → independently verify → integrate + abstain), so
there is one per task family. But its value is governed by a law, and by that law most helmets are ARMOR, a few
are WEAPONS, and several are THEATER.**

## The governing law (generalizes the measured "organized, not smarter" finding)
> **Helmet value ≈ κ-density × economic-work-density × base-model-failure-rate** — all three factors must be
> non-trivial. Value lives ONLY in the κ=1 execution slice (forcing the frozen check the model would otherwise
> skip/fake) and the κ=0 abstention slice (preventing false confidence). **Everything in between — routing to
> named "specialists," multi-agent deliberation, cross-instance review inside the same model family — is
> structured theater** (appearance of rigor without an oracle; consensus among same-family agents is a
> shared-blind-spot *risk*, not safety). Value tracks verifier-density, **not domain glamour.**

## The tiering (classification is load-bearing; scores are ordinal only)
| domain | score | class | the real weapon (κ=1 slice) | the honest deflation |
|---|---|---|---|---|
| **Software engineering** | ~8.5 | **REAL weapon-helmet** | compiler · type-checker · test suite · linter · SAST · CVE scanner — frozen, independent | LLM writing both code + tests → self-grading, κ→0; architecture/naming/taste (~40%) is κ=0 → abstain |
| **Data analytics / BI** | ~6 | **REAL weapon-helmet** | the DB engine (SQL runs or errors) · metric re-derivation by 2 independent queries · dbt/GE assertions | the semantic "does this JOIN mean what was intended" layer (~κ0.5) is the costliest failure & resists checking; KPI/narrative κ=0 |
| **Legal / compliance** | ~4.5 | mostly-armor | **citation existence via live legal-DB lookup** (catches a cited 30–88% hallucination rate ⚠) | 70–80% (materiality, "market standard", posture) κ=0; abstention rail under client pressure |
| **Operations / SRE** | ~4 | mostly-armor | metric queries · config diffs · health checks · change-correlation · a reversibility gate | most live root-cause cognition κ=0; existing tooling already runs the κ=1 steps → crowded |
| **Clinical decision support** | ~3.5 | mostly-armor | dosing arithmetic · lab-range flagging | DDI "verifier" is soft — databases disagree (cited κ≈0.01 ⚠); diagnosis/treatment κ=0; abstention is the value (high-stakes) |
| **Education / tutoring** | ~2.5 | mostly-armor | CAS/test-runner for math/code · readability · prereq-graph cycles | rubric ICC is a PROXY scorer not exact; explanation/scaffolding κ=0; base model already adequate |
| **Design / UX** | ~2 | **theater-risk** | WCAG contrast · touch-target px · focus order · Lighthouse | tools catch only ~30% even in-slice; 70–80% (hierarchy, feel, mental-model) κ=0 → "run Lighthouse then abstain" = a shell script |
| **Long-form writing** | ~2 | **theater-risk** | citations · word counts · heading depth · broken URLs (~10–15%) | a "style specialist" is the same model with the same blind spots; parametric "fact-check" = circular measurement |

## The single best NEXT helmet (untested hypothesis): SYSTEMATIC-REVIEW helmet
The one candidate (not in the original 8) that scores high on **all three** law factors and has a genuine κ=1
weapon the low-scorers lack: **a second independent automated extraction pipeline over full-text PDFs that
re-derives every numerical claim and flags discrepancies** (DOI resolution, citation existence, effect-size/CI/
p-value arithmetic, criterion-matching — all κ=1). The base model fails badly here (hallucinated cites,
confabulated stats, cross-paper conflation), the stakes are high (guidelines, policy, investment theses), and it
mechanizes what Cochrane review teams do by hand over weeks. **It is adjacent to the existing research helmet +
FACTHARNESS + SOCIUS/PSYMETRIX — a natural extension, not a new universe.** ⚠ Structural argument, unbenchmarked.

## Honesty rails on THIS analysis (it wears its own abstention)
- **No A/B across the 8 domains** — scores ordinal/illustrative, classifications are the trustworthy part. Nothing here clears the 10% bar; it's a roadmap hypothesis, not a promotion.
- **Self-referential risk:** the ranking model shares a training distribution with the model being evaluated → systematic over/under-confidence in any domain can't be ruled out (a shared blind spot, by our own law).
- **Two load-bearing facts are UNVERIFIED here** (cited from the analysis, not independently fetched): the DDI cross-DB κ≈0.01 and the 30–88% legal-citation hallucination range. They carry the clinical & legal classifications — **confirm against primary sources before designing either helmet.**
- κ-density figures are rough domain characterizations; realized κ swings hard with task mix.

## Bottom line
The helmet generalizes as a pattern, one per task family. **Software engineering and data/BI are the only two
that clearly earn "weapon" on current evidence; systematic-review is the best untested candidate; the rest are
worth building only for their honesty — and honesty doesn't need three agents.** The most important consequence:
before building any new helmet, estimate its κ-density first — if it's κ=0-dominated, you don't need a helmet,
you need a good system prompt that grounds and abstains.
