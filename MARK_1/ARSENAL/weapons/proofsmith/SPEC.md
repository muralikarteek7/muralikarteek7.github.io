# PROOFSMITH — a kernel-gated formal-proof engine (v5 weapon #4)
*One-page spec. Home: `Expanding_Frontiers/weapons/proofsmith/`. To be registered in `Next/BOX_V5.md`.*

## What it is (and is not)
PROOFSMITH is the v5 weapon for the **formal-proof** problem class — it extends the Mathematics &
TCS department from "construct an object" to "**prove a statement**." It produces **kernel-checked
formal proofs** and ships nothing the kernel hasn't accepted. The verifier is the **sharpest that
exists**: a proof-assistant **kernel (Lean 4 here)** re-checks a fully-elaborated proof term against
a tiny trusted core (the de Bruijn criterion) — κ=1.

**Two value props, kept SEPARATE and labeled:**
- **(a) FORMALIZE-VERIFY (reliable floor, the FETCH-KNOWN analogue):** take a theorem with a known
  proof, formalize it, **kernel-check it** → a labeled **reproduction**. Solid and buildable.
- **(b) The CAPABILITY BET (open):** does **kernel-feedback proof-search beat equal-compute
  best-of-k** on **non-memorized** lemmas? The untested repair lever in its most favorable
  (rich-feedback) domain. **An honest negative is a valid outcome** (and is what we found — see `ab/`).

**IS NOT:** ❌ "the model writes a proof in English" (that is armor/prose, an unverified claim — a
weapon's proof is a kernel-checked term). ❌ a `sorry`/axiom laundromat (the cardinal trap — see the
gate). ❌ a wrong-statement trick (proving a restatement that isn't the theorem). ❌ an open-problem
solver — **never claim to prove an open conjecture**; reproduce known theorems, exhibit the term or
report none. ❌ smarter than the model — it raises *verified-proof throughput*, not the ceiling.

## The three modes (map to the κ-router; the kernel is the exact verifier)
| mode | analogue | produces | frozen exact verifier (κ=1) |
|---|---|---|---|
| **FORMALIZE-VERIFY** | FETCH-KNOWN | a formalized + kernel-checked known theorem | the **4-check gate** (below) |
| **PROOF-SEARCH** | armor++ | a proof of a given formal statement (tactics/automation) | same gate; counts only if it closes the goal with allowed axioms |
| **LEMMA-EXTEND** | SEARCH-OPEN | auxiliary lemmas / gap-filling in a known development | gate per lemma; de-novo proof of an OPEN conjecture is the rare frontier → **honest negative expected** |

κ=0 ("is this argument convincing / the right strategy") → **ARMOR** (ground + abstain); the kernel
does NOT certify judgment. Router: `proofsmith_router.py` (self-tested).

## The 4-check KERNEL GATE (`proof_gate.py`) — the whole game
Build it FIRST, with self-tests that prove it can FAIL. For each committed target the gate enforces:
1. **Kernel accepts** — the proof term type-checks (no `error:`; lean exit 0).
2. **No `sorry`/`admit`** — reject `sorryAx` in `#print axioms` + the "uses sorry" warning + a
   source-token scan. *(A proof depending on `sorry` is a FAILURE, not a result.)*
3. **Axiom allow-list** — `#print axioms <thm>` must list only COMMITTED-allowed axioms
   (`{propext, Classical.choice, Quot.sound}` for classical mathlib). Any extra axiom ⇒ REJECT.
   `sorryAx` is never allowed.
4. **Statement matches reference** — kernel-level via `example : <ref> := <thm>` (type-checks IFF
   `<thm>` proves the committed reference). A proof of the *wrong* statement ⇒ REJECT.

**Why the gate can't trust `lean`'s exit code:** `lean` exits **0** on both a `sorry` proof and a
bogus-axiom proof (they are a warning / a fiat axiom, not errors) — so checks 2–3 parse
`#print axioms`, the only signal that catches them. (Machine-verified; see `GROUNDING.md` §A.)

**Gate self-tests (non-waivable, `selftest_all.py`):** (a) ACCEPT a known-good proof, (b) REJECT a
`sorry`-proof, (c) REJECT a bogus-axiom proof, (d) REJECT a proof of a different statement. **All
four pass on real Lean** — and the SMT slice passes its accept/reject pair — or no output is trusted.

## The κ<1 surface PROOFSMITH does NOT hide: autoformalization
**Kernel-checked ≠ correct English theorem.** Check 4 certifies the proof matches a *committed
FORMAL statement*; whether that formal statement *means* the intended English theorem is an
**autoformalization JUDGMENT (κ<1)** → it is **cross-model reviewed (model ≠ generator), not asserted
by the kernel**. A kernel-perfect proof of a mis-translated statement is worthless. The router flags
this surface on every English-claim task.

## Verifier scope (honest)
- **Lean 4 kernel (primary, κ=1):** all of formalizable mathematics.
- **z3 SMT slice (`smt_gate.py`, secondary, κ=1 on a DECIDABLE fragment ONLY):** propositional + QF/
  linear arithmetic. A decision procedure, **not** a general proof assistant — labeled as such.

## Killer demo (committed prediction → run → compare): `demo_formalize_verify/`
Reproduce **3 known theorems** in pure Lean 4 core, kernel-checked with clean `#print axioms`
(and_comm; even-or-odd; Gauss summation), and show the gate **REJECTING** a `sorry`-version, a
bogus-axiom version, and a wrong-statement version, plus a z3 cross-check of the propositional one.
**Result: 7/7 committed predictions confirmed by the machine judge.** (`PREDICTION.md`, `Proofs.lean`,
`run_demo.py`, `results.json`, `print_axioms.txt`.)

## Capability A/B (the open bet): `ab/`
Pre-registered kernel-feedback proof-search **vs equal-compute best-of-k** on **non-memorized**
lemmas. **Report the honest result** — a negative is valid; do NOT manufacture a pass. (See
`ab/RESULT.md`; consistent with the season's owned repair-lever negatives at toy scale.)

## Honesty rails (non-waivable)
A proof depending on `sorry`/`admit` or an unlisted axiom is a **FAILURE**, not a result — ship
`#print axioms` with every proof. **Kernel-checked ≠ correct theorem** (statement-meaning is κ<1 →
cross-model check). **Reproduction is labeled reproduction** (source + date). **Never claim to prove
an open conjecture** — exhibit the term or report none. The gate without its 4 self-tests does not
ship. If the SMT fallback is used, say it covers a *decidable fragment*, not all mathematics.
**Honest ceiling, every run: PROOFSMITH raises verified-proof throughput; it reproduces/verifies/
extends reliably and invents the load-bearing new proof idea rarely.**
