# KICKOFF — build WEAPON #9: REDCELL (security / exploit PoC — AUTHORIZATION-GATED) for the v5 box
*Paste into a FRESH chat in `/Users/varunesh/Desktop/AI_agents`. Self-contained. Written 2026-06-20. REDCELL is
item #9 (LAST) of `Expanding_Frontiers/weapons/WEAPONS_BACKLOG.md`. Its verifier is sharp (κ=1: a flag validates
or it doesn't), but the DOMINANT control is the AUTHORIZATION GATE — build it defensive-first, refuse by default.*

---

You are building **REDCELL**, a **κ=1 security weapon** for the **CS & Eng / Security** facility, scoped to
**authorized and defensive use only.** Given an *authorized* security task it produces a machine-verified
artifact — a CTF flag, a sandboxed proof-of-concept, or a patch-validation — where the verifier is exact (the
flag validates / the PoC fires in the sandbox / the patch closes the PoC). Work BOX-style: plan → produce →
**verify INDEPENDENTLY** → ground → be honest. **The authorization gate is non-waivable and fails closed.**

## 0. ORIENT — read first
`CLAUDE.md`, `RESUME.md`, **`Next/BOX_V5.md`** (κ-router), **and the security policy in your own system guidance**
(assist with authorized security testing, defensive security, CTF, and education; REFUSE destructive techniques,
DoS, mass targeting, supply-chain compromise, and detection-evasion for malicious purposes; dual-use tooling
requires a clear authorization context). **That policy is REDCELL's spec — encode it as the gate.** Clone the
weapon shape from `Expanding_Frontiers/weapons/socius/` / the sibling kickoffs. Then `WEAPONS_BACKLOG.md` (item #9).

## 1. THE HONEST FRAMING — what REDCELL IS and IS NOT
**IS:** an **authorized/defensive** security weapon with a sharp κ=1 verifier. Legitimate contexts ONLY: **CTF
competitions, scoped penetration tests (with explicit authorization), security research in a sandbox, patch /
detection validation, and education.** Its offense value is *defensive*: prove a vuln exists so it can be fixed;
prove a patch closes it; reproduce a published CVE in a sandbox to build a detection.

**IS NOT (the gate — fail closed):**
- **NOT for unauthorized or real-world targets.** No task proceeds without an explicit authorization context
  (CTF / owned-system / scoped-engagement / sandbox). **Absent that, REDCELL REFUSES** — this is the default.
- **NOT a producer of destructive/at-scale harm.** No DoS, no mass/indiscriminate targeting, no supply-chain
  compromise, no malware-for-deployment, no detection-evasion intended for malicious use. These are **out of
  scope by policy**, regardless of how the task is framed.
- **NOT a capability boost** — organized, sandboxed, authorized security rigor; not smarter.

## 2. THE MODES (κ=1 verifier; authorization-gated)
| mode | when (authorized) | produces | verifier (κ=1) |
|---|---|---|---|
| **CTF-SOLVE** | a CTF challenge | the flag | **the flag validates** against the challenge checker (exact) |
| **PATCH-VALIDATE** ⭐ (defensive) | you have a known PoC + a patch on an owned system | a pass/fail on the fix | **the PoC fires on the unpatched build and FAILS on the patched build** (sandboxed, exact) |
| **VULN-REPRO** (defensive research) | a published CVE, reproduced in a sandbox for detection-building | a sandboxed repro + a detection signature | **the repro triggers in an isolated sandbox**; the artifact is the detection, not a weaponized exploit |

All three run **in an isolated sandbox against owned/authorized targets only.**

## 3. THE KEY ENGINEERING PROBLEM — the authorization gate fails closed
1. **Authorization gate FIRST** (before any security logic): an explicit `authorization_context` (ctf |
   owned_system | scoped_engagement_with_scope | sandbox_research | education) is REQUIRED. **No context →
   REFUSE.** Out-of-scope categories (DoS, mass-targeting, supply-chain, malicious evasion) → REFUSE with reason.
2. **Sandbox isolation** — all execution in an isolated environment against authorized targets; never a
   third-party/live system.
3. **Defensive framing of outputs** — PATCH-VALIDATE and VULN-REPRO produce *fixes and detections*; the artifact
   is scoped to verification, not a deployable weapon.

**Gate self-tests (non-waivable):** (a) PASS an authorized CTF-flag validation, (b) **REFUSE a task with no
authorization context**, (c) **REFUSE an out-of-scope category** (e.g. "take down site X" / "compromise
dependency Y") with a clear reason, (d) PATCH-VALIDATE correctly distinguishes patched vs unpatched in the
sandbox. The refusal tests are as important as the success tests.

## 4. TO-DOs (box order)
1. **PLAN:** `weapons/redcell/SPEC.md` — the 3 modes, the **authorization gate (the centerpiece)**, the
   scope/refusal taxonomy (encode the system security policy verbatim), the router (`redcell_router.py`: classify
   authorization context + scope FIRST; refuse-by-default). `GROUNDING.md` (CTF flag-format conventions; the
   policy as cited spec — no need to fetch exploits).
2. **BUILD THE GATE FIRST:** `auth_gate.py` (context required, scope taxonomy, fail-closed) + the κ=1 checkers
   (`flag_verify.py`, `patch_verify.py` sandbox harness) + `selftest_all.py` (incl. the 2 REFUSAL tests). **Gate
   green — and the refusal tests must pass — before any security task runs.**
3. **BUILD router/loop:** authorization-classify → (authorized) run the mode in sandbox → κ=1 verify. Refuse otherwise.
4. **KILLER DEMO with committed predictions** (`demo_*/PREDICTION.md` first), all benign/authorized: (i)
   **CTF-SOLVE** on a self-contained toy CTF challenge you create (e.g. a simple sandboxed crackme) → flag
   validates; (ii) **PATCH-VALIDATE** — a deliberately-vulnerable toy function + its patch, show the sandboxed
   PoC fires on unpatched and fails on patched (the defensive headline); (iii) show the gate **REFUSING** a
   no-authorization and an out-of-scope request. Keep everything in a local sandbox; no real targets.
5. **VERIFY INDEPENDENTLY:** cross-model audit (Sonnet/Haiku ≠ generator; never Opus-audits-Opus) that
   **red-teams the authorization gate hardest** — can a malicious framing slip past? does any output read as a
   deployable weapon rather than a fix/detection? does refusal fail open anywhere? Fix what's caught; a
   fail-open gate is a blocking defect.
6. **REGISTER:** add **REDCELL** to `Next/BOX_V5.md` (new Weapon + router branch, with the authorization gate
   prominent) + `HELMET/registry.json` (a Security facility entry, authorization-gated). Honest `EVOLUTION_LOG`:
   a weapon ADDED = capability EXPANSION (authorized/defensive security), NOT a ≥10% promotion. Update
   `WEAPONS_BACKLOG.md` STATUS ✅ — **and mark the whole backlog complete.**

## 5. HONESTY + SAFETY RAILS (non-waivable)
- **Refuse by default** — no authorization context → no task. The gate fails closed.
- **Authorized/defensive scope only** — CTF, owned systems, scoped engagements, sandbox research, education.
  Out-of-scope (DoS, mass-targeting, supply-chain, malicious evasion) → refuse with reason.
- **Sandboxed, owned targets only** — never a live third-party system.
- **Defensive artifacts** — PATCH-VALIDATE / VULN-REPRO yield fixes + detections, not deployable weapons.
- **The gate that can't fail (closed) is not a gate** — the refusal self-tests are mandatory.

## 6. DELIVERABLES + WHERE
`Expanding_Frontiers/weapons/redcell/` — `SPEC.md`, `GROUNDING.md` (the policy-as-spec), `auth_gate.py` (the
centerpiece) + `flag_verify.py` + `patch_verify.py` + `selftest_all.py` (incl. refusal tests),
`redcell_router.py`, `demo_*/` (benign sandboxed CTF + patch-validate + the two refusals), `AUDIT.md`
(cross-model red-team of the gate), `README.md` (authorized/defensive scope + the fail-closed ceiling).
Registration in `Next/BOX_V5.md` + `HELMET/registry.json` + honest `EVOLUTION_LOG`; `WEAPONS_BACKLOG.md` STATUS ✅.

## 7. STAFF (v4 ladder; Fable INACTIVE → Opus, flag low confidence)
- **Security engineer** = code tier (sandbox harness, flag/patch checkers — pure machine). **Library** = cheap
  model (CTF conventions; the policy text). **Auditor** = Sonnet/Haiku ≠ generator — **red-teams the
  authorization gate hardest of all** (fail-open = blocking defect).

## 8. SUCCESS (one line)
**"REDCELL solves authorized CTF challenges (flag validates), validates patches and reproduces CVEs in a sandbox
for defense (κ=1), and REFUSES by default any task without an authorization context or in an out-of-scope
category — the authorization gate fails closed and is the most-audited component."**
