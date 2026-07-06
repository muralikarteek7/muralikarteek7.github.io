# PROOFSMITH capability A/B — RESULT (honest negative; a false positive caught + killed)

*Pre-registration: `PREREG.md`. Truth = the Lean kernel (`proof_gate.py`) on every returned proof;
zero trust in agent self-reports. Prover = Haiku. 4 non-memorized lemmas over fresh recursive
functions (`preamble.lean`).*

## Headline
**CLEAN result: kernel-feedback repair shows NO advantage over equal-compute best-of-k.**
one-shot **1/4** · best-of-3 **1/4** · repair (3 calls, pure verbatim feedback) **1/4** →
**repair − best-of-3 = 0pp.** All three arms solve only **L2** (the one linear lemma); on
L1/L3/L4 the prover **thrashes** — repeating the same `omega`-on-nonlinear-goal and
`simp only [ps_d]` over-unfold mistakes across all 3 rounds, unable to convert the raw kernel
error into the fix. **HONEST NEGATIVE.** No promotion. Consistent with the season's owned
repair-lever negatives (construction: Haiku −38pp, Sonnet +0pp; code: saturation), now extended
into the **formal-proof / rich-feedback** domain the season flagged as the one worth testing.

## ⚠ The honest part: a CONTAMINATED first run produced a FALSE +25pp, and the box caught it
The first pass *looked* like a win — repair 4/4 vs best-of-3 3/4 (+25pp, separated by L3). Reading
the agent transcripts before trusting it surfaced **two contamination vectors**, both of which I
introduced:
1. **Orchestrator-authored fix-hints.** My repair prompts appended interpretation of the kernel
   error ("add `at *`", "use `Nat.mul_add`…") — that is me solving it for the model, which the
   probe's own rule forbids ("feedback = the checker's output verbatim; do not solve it for the
   model"). The "informative feedback" variable was no longer isolated.
2. **Answer-key leakage to tool-enabled provers (worse).** The Haiku agents have Bash/Read access,
   and several **read `reference_proofs.lean` off disk** — one L3 agent literally announced "I can
   see the reference proof on line 37-40"; round-1 L1/L4 agents logged 2–3 tool calls. They copied
   the answer. The pass rate was inflated by leakage, not by the lever.

**Fix + clean re-run:** quarantined every answer-bearing file off-disk (`/tmp/ps_quarantine/`,
verified no worked proof remained in the repo), re-ran with provers **barred from tools**
(`tool_uses=0` verified on all 24 spawns) and **pure verbatim kernel feedback only**. The clean
result (1/4 = 1/4 = 1/4, 0pp) **contradicts** the contaminated +25pp — confirming the apparent win
was entirely contamination. *This is the box working: contamination awareness + non-circular
machine measurement killed a false positive that self-review would have shipped.*

## Clean per-lemma tally (key quarantined, no tools, pure feedback)
| lemma | one-shot | best-of-3 | repair (3 calls) | note |
|---|---|---|---|---|
| L1 `ps_f1 n = n*n`        | fail | fail | **fail** | omega can't do nonlinear; prover never adds distributivity lemmas |
| L2 `ps_g n = 3*n`         | **PASS** | **PASS** | **PASS** | the one linear lemma — one-shot solves it |
| L3 `2*ps_t n = n*(n+1)`   | fail | fail | **fail** | same nonlinear trap; r3 even reached for `ring` (mathlib, rejected) |
| L4 `ps_d (n+1) = ps_t n`  | fail | fail | **fail** | repeats the `simp only [ps_d]` over-unfold that breaks `rw [ih]` |
| **rate** | **1/4** | **1/4** | **1/4** | **repair − best-of-3 = 0pp** |

## Why repair failed (interpretation; the numbers are machine-solid)
The kernel's error is rich *for a human* (it prints the exact unsolved goal + an omega
counterexample), but **Haiku cannot act on it**: told "omega failed on `n*n` vs `(n+1)*(n+1)`",
it re-submits `omega` (L1 r2 = L1 r1), or switches to `ring` (not in core), or repeats the
over-unfold (L4). Rich feedback ≠ actionable feedback **for a weak prover**. Independent resampling
did no better — there is simply no signal here.

## Honest scope / caveats (non-waivable)
- **N=4, Haiku-only.** This tests "does pure kernel-feedback rescue a WEAK prover on fresh lemmas?"
  → **no.** It does **NOT** test the strong-prover regime (Fable inactive; faithful powered scale
  needs API + budget control we lack) — that remains the **infra-gated open question**, unrefuted.
- A powered, cross-model-audited ≥10% beat over best-of-k on non-memorized lemmas would be needed to
  move the ratchet; this small probe is not powered for that and **claims no promotion**.
- The contaminated run's files are quarantined in `/tmp/ps_quarantine/` (not deleted, for audit).
- **Deliverable banked:** a reusable, contamination-hardened kernel-feedback A/B harness
  (`clean_ab.py` + the gate), and a clean negative written down. Cost: ~30 Haiku spawns.

## Verdict
**No capability signal for kernel-feedback repair over best-of-k (clean, 0pp). No promotion; the
≥10% CAPABILITY ratchet stays OPEN at v3.** The lever's only surviving hope (strong prover × harder
lemmas × rich feedback) is unchanged and infra-gated. The most valuable output of this A/B is the
**caught false positive** — a textbook case for why measurement must be contamination-free and
independent of the generator.
