# JOB HUNTER — weapon kickoff (applied / composite)
*Registered in the Mark 1 arsenal 2026-06-25. Runnable home: `~/.claude/skills/jobhunter/` (installed skill, invoke `/jobhunter`). Unlike the math/computational weapons in `WEAPONS_DOCTRINE.md`, JOB HUNTER is an **applied pipeline** built on the armor rails — its "object" is a verified, apply-ready job pipeline for one client.*

## Signature — fires when
A client needs work: "hunt/find/search jobs for <client>", build or refresh a job pipeline, run the job search for someone.

## What it produces
One **CLIENT PROFILE** → a verified, tailored, apply-ready pipeline: per-role folders (résumé + cover letter/video + a 6-section dossier), consolidated PDF **Sets**, a one-page **command-sheet**, and `README.md` + `SUPPORT.md` cross-session memory.

## Pipeline (6 stages)
Intake → **Discover** (multi-board fan-out; **live-Chrome unlock** for LinkedIn/Indeed/CharityVillage, which wall server-side `WebFetch`) → **Verify** (adversarial: live? · pay? · mode? · level? · eligibility/identity?) → **Build** (de-AI résumé + cover + dossier via `assets/generators.py`) → **Consolidate** (Sets + command-sheet) → **Maintain** (saved-search alerts, periodic re-sweep, README/SUPPORT).

## Verifier & honesty rail (the point)
Verifier = independent **LIVE-posting confirmation**. Non-waivable rails: never fabricate a posting/org/salary/deadline/contact; **verify LIVE before recommending or building**; report negatives plainly ("0 of N recommendable"); respect the client's positioning/identity rules (e.g. settler-ally — never imply Indigenous identity; skip designated roles); don't build on unverified pay/mode; never submit/apply on the client's behalf without per-action consent.

## Honest ceiling
Finds, verifies, and tailors reliably. **Cannot** manufacture unposted jobs, read unpublished pay, bypass a login wall, or apply for the client — those are the human's moves. The verify stage routinely kills phantom postings, expired deadlines, and self-contradicting salaries.

## Status — ✅ validated end-to-end (client #1: Ria Dhanani)
~9 built packages + Sets + command-sheet; `generators.py` smoke-tested (1-page CV + dossier render clean). Key operational discovery: the **browser-unlock** — the live Chrome reads LinkedIn's 1,000+ results that `WebFetch` is 100% blind to.

## Assets (in the skill)
`SKILL.md` (doctrine) · `assets/CLIENT_PROFILE.template.md` · `assets/WORKFLOWS.md` (discover/verify/package) · `assets/generators.py` (résumé+dossier → PDF, green-sidebar, de-AI) · `assets/OPERATIONS.md` (browser-unlock, verification ceiling, geo-block/VPN, file/naming conventions, de-AI voice spec) · `clients/<name>.md`.

## EQUIP
Style **HUNTER** (added to the Mark 1 EQUIP table). Running a hunt = SCHOLAR (grounded discovery) + AUDITOR (adversarial verify); building/extending the weapon = ARCHITECT + BOOTSTRAP.

## Deeper wiring (optional TODO — do with care, don't regress tests)
Add `HUNTER` to `MARK_1/EQUIP/LOADOUTS.json` + `equip.py` and **re-run `test_equip.py` (keep it green)**; add a JOB-HUNTER row to `MARK_1/ROUTER/WEAPON_REGISTRY.json`. Left undone here to avoid blindly regressing the 18/18 selector tests.
