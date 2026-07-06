# SHIELD — the box's active input boundary (ARMOR-HARDENING, not a weapon)

**What it is.** SHIELD is the gate that decides *what reaches ARMOR / WEAPONS / HELMET at all* when an
input did **not** originate from the box's own code (user text, tool output, retrieved docs, web, MCP
metadata, memory reads, other-agent messages). ARMOR is passive always-on honesty; SHIELD is the
**active boundary in front of it**. It is **4 EXACT (κ=1) structural rails the box lacked + 1 κ=0
abstain rail** — it **builds nothing**, so it is **ARMOR-HARDENING, not a weapon** (KIT-EXPANSION #3).

**The one rule.** *Exact where it can be, abstaining where it can't, honest about the wall it is not.*
Injection/jailbreak *intent* detection is **κ=0** — an attack is defined by evading detection, so no
cheap exact verifier exists. SHIELD never ships an LLM injection-classifier trusted as ground truth
(that is circular: an LLM judging attacks on an LLM). It makes the structural parts exact and routes
the rest to abstain-or-escalate.

## The five rails (κ honesty per rail)
| rail | κ | blocks (exactly) | honest failure mode |
|---|---|---|---|
| **PROVENANCE-LABEL** | κ=1 label / **κ<1 obedience** | ENV/external text read as a SYSTEM/USER instruction | a crafted payload can still *semantically prime* the model despite a correct label — obedience is NOT machine-checkable; ARMOR's veto remains the depth layer |
| **VERIFIER TAINT-RAIL** | κ=1 | a weapon gate being *talked into* a false cert via poisoned context | a *code* bug in the verifier (not an input attack) — out of scope (CRUCIBLE) |
| **TOOL-CAPE** | κ=1 allowlist+HMAC | excessive agency, tool-description poisoning, runtime self-elevation | a *permitted* tool whose server is compromised — supply chain, out of scope |
| **CERT ANTI-REPLAY** | κ=1 hash+HMAC | replaying a stale/forged PASS onto a *different* object | the verifier binary replaced wholesale — needs build attestation, out of scope |
| **ABSTAIN-OR-ESCALATE** | **κ=0** | novel injection / jailbreak / social-engineering *intent* | false negatives pass to ARMOR (depth layer); false positives add friction. It **never** self-certifies safe. |

The single highest-value rail is the **VERIFIER TAINT-RAIL** — it hardens *every* weapon gate at once
(the analog of "auditor ≠ generator", applied to a gate's *inputs*).

## The honest ceiling (stated on every run; `GROUNDING.md §C`)
SHIELD is **NOT a complete injection defense.** Documented attacker success against LLMs is **50–84%
across common models, 85%+ for adaptive attacks, >90% on naive deployments**; experts state prompt
injection is *"unlikely to ever be fully solved."* (NIST AI 100-2 E2025 newly covers indirect
injection + agent attacks; the exact "~80% at 25 tries" figure the kickoff cited could **not** be
confirmed verbatim from the fetched NIST summary pages — see `GROUNDING.md §C` for the grounded
substitute range and the honest provenance gap.) **Defense-in-depth, not a wall:** SHIELD failure ≠
system failure (ARMOR's fabrication veto + the cross-model audit remain), and SHIELD success ≠ "secure".

## Run it
```
cd MARK_1/ARSENAL/weapons/shield
python3 selftest_all.py                 # the frozen gate's accept-good/catch-broken/abstain-malformed
                                        # self-tests — MUST be green (exit 0) or NOTHING is trustworthy
cd demo_rails && python3 run_demo.py    # 7/7 committed predictions, judged by the gate
```

## Files
- `shield_gate.py` — the frozen gate (built FIRST): `ingest`/`relabel_attempt`/`Span` (provenance),
  `gate_inputs_ok` (taint-rail), `issue_cape`/`call_allowed`/`try_self_elevate` (tool-cape),
  `issue_cert`/`verify_cert` (anti-replay), `suspicion_scan`/`high_privilege_decision` (κ=0 abstain).
  Its `_selftest` is the six non-waivable gate-of-the-gate checks (incl. the non-syntactic semantic
  injection → ABSTAIN test).
- `selftest_all.py` — runs the gate + router self-tests; **exits non-zero on any failure**.
- `shield_router.py` — routes a boundary event to the right rail (or to abstain-or-escalate); own `_selftest`.
- `SPEC.md` — the plan (the 5 rails, κ per rail, the router). `GROUNDING.md` — fetched OWASP/NIST/MCP sources.
- `demo_rails/` — `PREDICTION.md` (committed BEFORE running) + `run_demo.py` + `results.json`.
- `AUDIT.md` — cross-model (Sonnet/Haiku ≠ the Opus generator) red-team (a stub the auditor fills).

## What SHIELD is NOT (stated plainly)
❌ a weapon (builds nothing). ❌ a complete injection defense (see ceiling). ❌ an LLM injection-detector
trusted as truth. ❌ a replacement for ARMOR's fabrication veto or the cross-model audit. It is a layer
*in front*, assuming the others may still fail. Calling it a weapon would overstate buildable safety.
