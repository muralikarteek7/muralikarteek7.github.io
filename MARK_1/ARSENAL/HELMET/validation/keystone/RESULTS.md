# HELMET KEYSTONE — Provost routing-accuracy benchmark (RESULTS, 2026-06-21)

**The question (the #1 TIER-1 gap from `../GAPS.md`):** the Provost's κ-classification on **unlabeled** inputs
was UNTESTED — the original A/B/C validation pre-labeled κ. *Until this runs, the helmet's value over plain armor
is unproven.* This benchmark answers it with machine-verified data.

## Method (non-circular, committed-first)
- **24 unlabeled cross-disciplinary problems** (`COMMITTED_KEY.json`) spanning every hard routing case: κ=1 weapon
  tasks, κ=0 normative/open/forecast → abstain, κ=0 settled facts → ground-and-answer, the **C14 proxy traps**
  (in-sample Sharpe, "best essay", MMLU-as-capability, in-sample R²), **anti-theater** grandiose-dressed
  one-liners, and the open-problem rails (P=NP, RH).
- **Committed key authored BEFORE any model ran**, with per-item justification. **Cross-model audited** (Sonnet ≠
  the Opus author): **22/24 gold answers DEFENSIBLE, 0 WRONG, 2 genuinely AMBIGUOUS** (Q14 SI-defined constant;
  Q21 mixed replication+policy) → those 2 scored separately. The key is a fair gold standard.
- **System under test:** a fresh-context agent reads ONE raw problem + the κ-gate doctrine + the dept keys, emits
  the routing descriptor; `provost.route()` (selftest-proven) turns it into a verdict; `score.py` grades it vs gold.
- **Two tiers — Sonnet + Haiku** — both INDEPENDENT of the Opus key author (non-circular) and bracketing the
  capability range, so we learn whether routing is model-robust.

## Baseline result (doctrine as it was)
| tier | routing verdict (24) | clean (22, ambiguous excluded) | κ-class | proxy-trap | anti-theater |
|---|---|---|---|---|---|
| **Sonnet** | 21/24 = **88%** | 21/22 = **95%** | 88% | **4/4** | **2/2** |
| **Haiku**  | 19/24 = **79%** | 19/22 = **86%** | 71% | **4/4** | **2/2** |

**The load-bearing decisions are robust at BOTH tiers:** weapon-vs-abstain, the C14 proxy trap (4/4), anti-theater
DESK scaling (2/2), and the open-problem rails (P=NP, RH → abstain) were all correct. **The failure concentrated in
ONE mode:** over-tagging a **factual lookup** as WEAPON (κ=1) instead of GROUND_AND_ANSWER (κ=0 groundable) — Haiku
missed Q11/Q12/Q14/Q19, Sonnet missed Q19. This is precisely the weak link the red-team predicted ("capital of
Australia"). It is **benign in consequence** (both routes deliver the correct factual answer; nothing is fabricated
and no abstention is missed) but it is a real classification error, worse at the weaker tier.

## The fix (diagnosed → codified → re-measured)
Root cause: the model conflated **"has a definite answer"** with **"a cheap exact verifier exists."** Two
principled fixes, both surfaced by the benchmark:
1. **Stage-1 doctrine** (`provost.py` schema doc + the agent instruction): *a fact you can only LOOK UP / fetch
   from an authority (capital, date, name, a stipulated constant like the SI speed of light, a standard
   definition) has a definite answer but NO computable verifier → κ=0 + groundable, NOT κ=1. κ=1 requires a
   verifier you RUN/COMPUTE/PROVE.*
2. **Stage-2 route() hardening:** a `proxy_only_scorer` verdict mandates abstention **regardless of `groundable`**
   (a gameable "most capable by MMLU" verdict must not be presented as a grounded answer just because the scores
   are lookup-able). `provost.py` selftest stays green.

**Re-test (Haiku, the worst tier, sharpened doctrine + hardened route):**
| run | routing (24) | κ-class | Δ vs baseline |
|---|---|---|---|
| Haiku baseline | 79% | 71% | — |
| **Haiku + fixes** | **100% (24/24)** | **100%** | **+21pp** |

The entire factual-lookup failure mode closed; the last residual (Q17, a proxy item the model also marked
groundable) is caught by the route() hardening.

## Honest verdict
- **The keystone gap is NARROWED, not fully closed.** The Provost's routing on unlabeled inputs is **empirically
  supported**: out of the box it routes the load-bearing decisions correctly (79–88%, 86–95% on unambiguous
  items), and a principled fix lifts the weak tier to 100%. The helmet's core mechanism is no longer *unproven* —
  it is *measured*.
- **⚠ The 100% is IN-SAMPLE to the fix** — the sharpened doctrine was designed against these 24 items. **Held-out
  generalization (a fresh, never-seen problem set) is the remaining gap** and the clear next step. Do NOT read
  "100%" as proven general routing accuracy.
- **Routing is tier-dependent:** weaker models need the sharper doctrine more (Haiku 79% vs Sonnet 88% on the same
  baseline). A weak Provost degrades; pin the sharpened doctrine.
- **This is a DIAGNOSTIC + a fix of an existing PROCESS layer, NOT a ≥10% capability promotion.** The helmet
  remains "organized, not smarter." The capability ratchet stays **OPEN at v3.**
- **Reconciles with the parallel MARK_2 run.** A separate MARK_2 session (`MARK_2/tests/`) ran its own 24-problem
  provost benchmark and reported "100% on the effective-κ field + 14/14 groundable." That is a **coarser metric**
  (the binary κ>0-vs-κ=0 field + the groundable flag, scored separately) on a **different problem set**. This run
  scores the **stricter 3-way routing VERDICT** (WEAPON / GROUND_AND_ANSWER / ARMOR_ABSTAIN) on problems chosen to
  probe the **lookup-vs-compute boundary** specifically — which is why it surfaces a real failure (79–88% baseline)
  that a coarser/different set can miss. The two runs **agree on the bottom line** ("narrowed, not closed, NOT a
  promotion"); this one adds the named failure mode + a verified fix. Net honest read: routing is **not 100% out
  of the box on the strict verdict** (79–88%), reaching 100% on Haiku only **after** the fix and **in-sample**.

## Held-out generalization (the in-sample caveat, RESOLVED — 2026-06-21)
The 100% above was IN-SAMPLE (the sharpened doctrine was designed against the original 24). So a **fresh 24-problem
held-out set** (`heldout/COMMITTED_KEY_HELDOUT.json` — different facts/domains/phrasings: Carmichael numbers, atomic
number of gold, Collatz, mutual-fund/culture-fit/single-benchmark proxy traps, chromosome-count bait, etc.) was
authored + committed, **cross-model audited** (22/24 defensible, 0 wrong, 2 ambiguous: H21 mixed, H23 threshold-
implicit), and classified with the **FROZEN** sharpened doctrine (verbatim, not re-tuned) at both tiers:

| run | routing verdict (22 clean) | κ-class | proxy-trap | anti-theater |
|---|---|---|---|---|
| **Held-out Sonnet** | **22/22 = 100%** | 100% | 4/4 | 2/2 |
| **Held-out Haiku**  | **22/22 = 100%** | 95% | 4/4 | 2/2 |

**The fix GENERALIZES.** On problems the doctrine never saw, both tiers routed every unambiguous item correctly —
the factual-lookup failure mode (the baseline's 79–88% weak spot) is gone, at both tiers. The 2 ambiguous items
split defensibly (Sonnet ABSTAIN-leaning, Haiku WEAPON-leaning — both legitimate per the auditor). Lowest metric is
domain (91–95%): a few department-label mismatches (lower stakes — the weapon/verdict is right, the dept tag slightly off).

**Honest caveats (do NOT overclaim):** (1) n=24 held-out — "100%" = *no errors observed in 22 items*, not a proof
of general accuracy (the CI lower bound at 22/22 is ~85%). (2) The held-out problems, though fresh, were authored by
the **same Opus author** as the doctrine and cover the same hard-case TYPES — cross-model-audited (fair) but
author-correlated; a fully independent/adversarial set could still find failures. (3) This is **routing
CLASSIFICATION accuracy, NOT end-to-end output quality** — accurate routing ≠ a capability gain. The helmet remains
"organized, not smarter."

**Net keystone verdict:** the gap moves from *narrowed* to **substantially closed on classification** — the Provost
routes unlabeled inputs accurately (100% held-out, both tiers, post-fix), the failure mode is fixed and the fix
generalizes. **Still NOT a ≥10% promotion; ratchet stays OPEN at v3.** The remaining frontier is the **end-to-end
A/B** (helmet-routed vs flat output across ≥2 arenas) + a larger fully-independent adversarial routing set.

## Files
`COMMITTED_KEY.json` (problems + gold + justifications, committed first), `score.py` (machine scorer via
`route()`), `raw/` + `{sonnet,haiku}_outputs.json` (baseline descriptors), `raw_v2/` + `haiku_v2_outputs.json`
(sharpened-doctrine descriptors). Provost fixes: `../../provost.py` (κ schema doc + the `must_abstain` line).
