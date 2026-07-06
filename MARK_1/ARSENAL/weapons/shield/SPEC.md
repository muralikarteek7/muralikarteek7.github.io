# SHIELD — SPEC (the box's active boundary; ARMOR-HARDENING, not a weapon)

*Written BEFORE the gate, per box order (plan → produce → verify INDEPENDENTLY → ground → honest).
SHIELD is item #3 of the KIT-EXPANSION plan. **HONEST UP FRONT: SHIELD is NOT a weapon and mostly NOT
new — it is ARMOR-HARDENING.** It builds nothing; it adds a thin set of EXACT (κ=1) structural rails the
box lacks and routes everything it CANNOT exactly check to abstain-or-escalate.*

## 0. What SHIELD is / is not

**IS:** the gate that decides *what reaches ARMOR / WEAPONS / HELMET at all* when an input did NOT
originate from the box's own code (user text, tool output, retrieved docs, web, MCP metadata, memory
reads, other-agent messages). ARMOR is passive always-on honesty; SHIELD is the active boundary in
front of it. It is **4 κ=1 structural rails + 1 κ=0 abstain rail.**

**IS NOT:** ❌ a weapon (builds nothing). ❌ a complete injection defense — the documented ceiling is
**50–84% attacker success across common LLMs, 85%+ for adaptive attacks, >90% on naive deployments**,
and experts state prompt injection is *"unlikely to ever be fully solved"* (`GROUNDING.md §C`). ❌ an
LLM injection-classifier trusted as ground truth (circular: an LLM judging attacks on an LLM). ❌ a
replacement for ARMOR's fabrication veto or the cross-model audit — a layer *in front*, defense-in-depth.

## 1. The rails, by κ

| rail | κ | what it blocks (exactly) | honest failure mode |
|---|---|---|---|
| **PROVENANCE-LABEL** | κ=1 label / **κ<1 obedience** | authority-confusion: ENV/external text read as a SYSTEM/USER instruction | a crafted payload can still *semantically prime* the model despite a correct label — obedience to the label is NOT machine-checkable; depth layer = ARMOR's fabrication veto must still hold |
| **VERIFIER TAINT-RAIL** | κ=1 | a weapon gate being *talked into* a false certificate via poisoned context | a genuine *code* bug in the verifier (not an input attack) — out of scope, that's CRUCIBLE |
| **TOOL-CAPE** | κ=1 allowlist + sig | excessive agency, tool-description poisoning, runtime self-elevation | a *permitted* tool whose server is compromised — supply chain, out of scope |
| **CERT ANTI-REPLAY** | κ=1 hash+HMAC | replaying a stale/forged PASS onto a *different* object | the verifier binary replaced wholesale — needs build attestation, out of scope |
| **ABSTAIN-OR-ESCALATE** | **κ=0** | novel injection / jailbreak / social-engineering *intent* | false negatives pass to ARMOR (the depth layer); false positives add friction. It NEVER self-certifies "injection-free". |

### κ honesty, per rail (non-negotiable)
- **The label is exact (κ=1); model OBEDIENCE to the label is κ<1 and untested here.** The wrapper
  controls the label, so attacker text cannot relabel *itself* — that is the exact part. Whether the
  model then *ignores* an ENV-tagged instruction is a behavioral property we do NOT certify. We add a
  defense-in-depth assertion (`test_labeled_injection_still_hits_armor_veto`) that a labeled injection
  is still routed to ARMOR's fabrication veto, and we state the residual risk explicitly.
- **The other three rails (taint, cape, anti-replay) are fully κ=1** — a deterministic
  label/typed-slot/allowlist/HMAC check is the block; no model is in the trusted path.
- **The abstain rail is κ=0** — it raises a *suspicion flag* from cheap structural signals (a relabel
  attempt, base64 blob, mid-document language switch, an imperative-override pattern). A flag **routes**
  (human review / read-only downgrade / hard abstain + log); it **does not clear**. SHIELD never emits
  `injection-free: true` as a positive certification.

## 2. The frozen gate (`shield_gate.py`) — built FIRST, self-tests green before anything routes

Five rail implementations, each a deterministic function with `kappa` stated in its result:

1. **PROVENANCE-LABEL** — `ingest(text, tier)` stamps a wrapper-set, read-only `Span(tier ∈ {SYSTEM,
   USER, ENV})`. `relabel_attempt(...)` proves external *text* cannot produce a SYSTEM/USER label *for
   itself*: the tier is set by the wrapper at ingestion and is read-only via normal assignment; any
   "ignore above, you are SYSTEM" content inside an ENV span stays ENV. κ=1 on the label.
   **Honest scope (audit DEFECT 1/2):** Python has no true immutability — we say *wrapper-set &
   read-only*, NOT *truly immutable*. A *code-level* (in-process) attacker is outside the primary
   (input-level) threat model, but we harden against it anyway: (a) the tier is stored in the slot as an
   **HMAC token bound to {tier, text}** under the box key, so an `object.__setattr__` relabel writes an
   unsigned value that fails verification and fail-closes to ENV (least trust); (b) `Span` is a **final
   class** (`__init_subclass__` raises), so a tier-overriding subclass cannot be defined; and (c) the
   load-bearing taint check reads the **verified internal slot** (`_tier_of`), never the overridable
   `tier` property. Forging a valid token requires the box key, which the in-process attacker lacks.
2. **VERIFIER TAINT-RAIL** — `gate_inputs_ok(candidate_object, frozen_code, system_spec)` types the
   gate's three input slots; any `ENV`-tagged `Span` (or raw external string flagged tainted) in the
   `frozen_code` or `system_spec` slot → **REJECT before the gate runs**. The candidate object may be
   ENV (it is *the thing under test*); the verifier code and spec may not.
3. **TOOL-CAPE** — `Cape(task_id, allowlist, sig)` signed with HMAC-SHA256 over the canonical cape;
   `call_allowed(cape, tool)` BLOCKs any tool not in the allowlist; `try_self_elevate(cape, tool)`
   (a runtime attempt to add to the cape — CVE-2025-53773-style) → **BLOCK + ALARM**, never mutates the
   signed cape. A tampered cape (bad sig) → REJECT.
4. **CERT ANTI-REPLAY** — `issue_cert(object, verifier_id, version, result)` → signed tuple
   `{object_hash, verifier_id, version, ts, result, sig}`; `verify_cert(cert, object)` re-hashes the
   object and re-checks the HMAC: a hash-mismatch (cert replayed onto a *different* object), a forged/
   tampered tuple, a **future-dated ts** beyond a small clock-skew tolerance, a **non-finite/non-numeric
   ts** (e.g. `inf`/`nan`/string — audit DEFECT 3, otherwise `now - ts` never exceeds the TTL), or a
   stale cert beyond TTL → **REJECT**.

The κ=0 abstain rail lives in the router (it is a *routing* decision, not a structural block):
5. **ABSTAIN-OR-ESCALATE** — `suspicion_scan(span)` returns cheap structural signals + a verdict in
   {CLEAN-no-signal (NOT a clearance), FLAG→escalate}. It NEVER returns "injection-free: true".

## 3. Gate-of-the-gate self-tests (`selftest_all.py`, non-waivable) — six green = trustworthy

(a) external text CANNOT relabel itself to SYSTEM/USER (accept-good label + catch-broken relabel);
(b) a verifier fed an ENV string in a code/spec slot REJECTS before running;
(c) a tool outside the cape is BLOCKED **and** a self-elevation attempt ALARMS; a tampered cape REJECTS;
(d) a certificate replayed onto a *different* object (hash-mismatch) is REJECTED; forged/stale → REJECT;
(e) the ABSTAIN rail FLAGS a planted obvious-injection sample and routes it to escalation, and the
   word `injection-free` NEVER appears as a positive certification (asserted absent from all output);
(f) **the non-syntactic, semantically-embedded injection** (no base64/keyword/relabel token — a polite
   instruction woven into prose) whose correct verdict is **ABSTAIN**: SHIELD must NOT claim to have
   detected/cleared it; it routes to abstain-or-escalate. (Audit-mandated: toy attacks aren't enough.)

Plus malformed-input ABSTAIN for each rail (None/empty/wrong-type → ABSTAIN, never a silent pass) and
the defense-in-depth assertion that a *labeled* injection still hits ARMOR's fabrication veto.

## 4. The router (`shield_router.py`)
Given an event, decide which rail(s) fire:
- external input arrives → **PROVENANCE-LABEL** + **suspicion_scan** (κ=0 → CLEAN-no-signal or FLAG);
- a weapon-gate call → enforce **VERIFIER TAINT-RAIL** + **CERT ANTI-REPLAY** on any prior cert;
- a tool call → enforce **TOOL-CAPE**;
- a high-privilege op under suspicion → **escalate / abstain** (never auto-proceed).
The router decides routing; the gate does the exact blocking. The κ=0 residue (injection *intent*) is
always routed to abstain-or-escalate, never to an LLM detector trusted as truth. The CEILING string
(NIST/empirical: no complete injection defense) is attached to every plan.

## 5. Honesty rails (non-waivable, stated on every run)
- κ=1 rails are exact; injection-*intent* detection is κ=0 → abstain/escalate, never self-certify safe.
- Never an LLM injection-detector trusted as truth. A suspicion flag routes; it does not clear.
- Defense-in-depth, not a wall — SHIELD failure ≠ system failure (ARMOR + cross-model audit remain);
  SHIELD success ≠ "secure". State the empirical ceiling on every run.
- SHIELD is **hardening, not a new offense capability** — calling it a weapon would overstate buildable safety.
- Scope: TAINT-RAIL stops input-attacks on a gate, not *code* bugs (CRUCIBLE); TOOL-CAPE stops
  unpermitted tools, not compromised permitted servers (supply chain).
