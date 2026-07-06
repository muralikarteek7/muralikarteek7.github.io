# PROOFSMITH — independent cross-model audit (auditor ≠ generator)

**Generator:** Opus 4.8 (orchestrator). **Auditor:** Sonnet 4.6 (a different model — Fable 5
inactive, so never Opus-audits-Opus). **Date:** 2026-06-20. The auditor was charged to BREAK the
gate and verify every claim by **running things itself** (65 tool calls) — it re-ran the self-tests
and demos, independently re-ran `#print axioms` on every shipped proof, constructed cheat proofs to
sneak past the gate, attacked the autoformalization surface, and re-tallied the A/B. Full transcript
in session history.

## Top-line verdict (auditor, verbatim sense)
> **"PROOFSMITH is SOUND on proof correctness. The 4-check kernel gate cannot be bypassed by any of
> the attacks I attempted. The A/B result is honest. One real but minor finding (a `#eval`
> sandboxing gap, not a proof bypass)."**

## Independently re-verified (auditor ran these itself, not via our gate)
| claim | auditor's independent check | match |
|---|---|---|
| `selftest_all.py` green | re-ran → EXIT 0, all 4 kernel + 4 SMT sub-tests pass | ✅ |
| FORMALIZE-VERIFY demo 7/7 | re-ran → EXIT 0, 7/7 | ✅ |
| mathlib demo 3/3 | re-ran `lake env lean` itself → `infinitude_of_primes` axioms `[propext, Classical.choice, Quot.sound]`, no sorryAx | ✅ |
| `and_comm_demo` no axioms | own `.lean` + `lean` → `does not depend on any axioms` | ✅ |
| `even_or_odd_demo`/`gauss_demo` axioms | own run → `[propext, Quot.sound]` ⊆ allow-list, no sorryAx | ✅ |
| A/B clean tally = 0pp | re-tallied `clean_final.json` + re-gated 2 stored attempts → one-shot 1/4 = best-of-3 1/4 = repair 1/4 | ✅ |

## Cheat-injection attacks (all correctly REJECTED by the gate)
`sorry` inside a `have`; a custom `axiom` used transitively through a helper `def`; `native_decide`
(its auto-generated `ofReduceBool`-class axiom is not on the allow-list → rejected); `@sorryAx`
written to dodge the token scan (**token scan misses it, but `#print axioms` catches `sorryAx` —
defense-in-depth holds**); `opaque` hiding sorry (`#print axioms` traces through); a macro expanding
to `sorry`; an `unsafe def` proving False (kernel rejects at elaboration); wrong-statement proofs
(check 4 type-mismatch). **No cheat achieved `accepted: true`.**

## Autoformalization (κ<1) scrutiny — the demo reference statements are FAITHFUL
The auditor confirmed each committed formal statement means its English theorem:
`∀ n, ∃ p, n ≤ p ∧ Nat.Prime p` ⇔ infinitely many primes (the standard mathlib form);
`∀ n, ∃ k, n = 2k ∨ n = 2k+1` ⇔ every nat even-or-odd; `2 * sumTo n = n*(n+1)` is faithful Gauss
given `sumTo`'s definition (auditor `#eval`'d `sumTo` = 0,1,3,6,10). It also confirmed the gate
**correctly disclaims** semantic faithfulness as a κ<1 surface (a caller *could* commit a vacuous
reference like `True` and get a trivial proof accepted — that is the documented autoformalization
limitation, handled by cross-model review, not a gate bug).

## The one real finding and its fix
| # | finding | severity | resolution |
|---|---|---|---|
| 1 | **`#eval` side-channel.** `#eval IO.FS.writeFile ...` in submitted Lean source executes arbitrary IO inside the gate's Lean subprocess during gating. NOT a proof-soundness bypass (sorry/axiom checks still fire and reject), but an unacknowledged sandboxing gap. Low practical impact here (the reference statement is caller-provided, not secret). | **minor (real)** | **FIXED.** Added PRE-CHECK 0 to `proof_gate.gate`: the source is scanned for elaboration-time IO/meta commands (`#eval`, `#exit`, `run_cmd`, `initialize`, `unsafe`, `implemented_by`, `extern`) and the bundle is **rejected unconditionally** — a proof never needs them. Added a non-waivable self-test `(e) REJECT #eval` to `proof_gate._selftest`; the suite re-runs green (now 5 kernel checks) and the demo stays 7/7. |
| 2 | `Classical.choice` is on the allow-list but unused by `even_or_odd_demo`/`gauss_demo` (subset check, so technically correct but slightly over-permissive). | trivial | Acknowledged. The subset test is the right one; tightening per-proof allow-lists is optional and does not affect soundness. |

## Net
The auditor found **no proof-soundness bypass** and **no dishonesty**. The 4-check gate held against
every cheat it constructed (the gate's own self-tests pass all four buggy-input cases, and the
auditor's novel evasions — `@sorryAx`, `opaque`, macro, `native_decide`, transitive axiom — were all
caught by `#print axioms`). The one genuine finding (a `#eval` IO side-channel, not a proof bypass)
is now closed with a guard + a regression self-test. The A/B's clean 0pp negative and its disclosed
contaminated-run are judged honest. **This is the verify-independently loop working as intended: a
different model re-ran every machine check, tried hard to cheat the gate, and hardened it.**
