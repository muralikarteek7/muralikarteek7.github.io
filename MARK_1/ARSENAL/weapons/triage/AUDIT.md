# AUDIT — TRIAGE (stub for the independent cross-model auditor)

*To be filled by a model ≠ the Opus generator (Sonnet/Haiku; Fable inactive → never Opus-audits-Opus).
This is a STUB written by the build engineer; do not treat anything below as a completed audit.*

## Charter for the auditor (kickoff §5.4)
TRIAGE is **ARMOR, not a weapon** — there is no capability claim to attack. The audit targets are:
1. **Coverage gap** — name a failure class the box has plausibly exhibited that the 8-row table MISSES.
   (Add it as a row if real.) The kickoff seeds the ground truth: branch-cut, answer-key leak,
   S-GROUND fabrication, OPTIMA crash, the 41<90 symmetry-frame negative — are there others?
2. **False fire** — find a CLEAN output record that wrongly fires a row. (The clean control passes
   today; try adversarial-but-honest records: a legitimately domain-restricted identity correctly
   labeled, a numeric value with honest error bars, a same-family agreement that is actually fine.)
3. **κ honesty** — does any row claim κ=1 where the check is really a judgment? In particular:
   - spec-gaming: does it EVER reach κ=1 without an actual independent oracle? (It should not — keyed
     off `independent_oracle_verdict`, not off CRUCIBLE-on-disk. Try to make it launder.)
   - crash/silent-pass: is "errored loudly?" genuinely κ=1, or is the probe gameable (a detector that
     returns a non-"ok" truthy value to dodge the silent-pass check)?
   - fabrication: confirm it actually delegates to FACTHARNESS and flips on a planted defect.
4. **The cardinal rails** — can you make a report emit "safe"/"all-clear", or strip
   `uncovered_novel_classes`, or silent-pass a malformed record? (Self-tests claim no; verify by attack.)
5. **Retroactive re-flag integrity** — are the 3 reconstructions FAITHFUL to the EVOLUTION_LOG
   failures, or are they rigged to fire? (Re-read C39/C41/C38; check the reconstructions in
   `triage_check.py: real_failure_*`.)

## How to run (independently)
```
cd /Users/varunesh/Desktop/AI_agents/Expanding_Frontiers/weapons/triage
python3 selftest_all.py
python3 demo_retroactive/run_demo.py
```
Then write your OWN attack records and run `triage_check.py` / `triage_router.py` on them with your own
expected verdicts — do not trust the generator's self-reported results.

## Auditor findings
*Filled from the independent cross-model (Sonnet) audit, 2026-06-20. 5 real defects found; ALL FIXED with
permanent regression self-tests in `triage_check._selftest` (each reproduces the exploit and asserts it is
now blocked). Re-run `selftest_all.py` (exits 0) to confirm.*

| # | severity | finding | repro | status |
|---|---|---|---|---|
| 1 | HIGH (false-accept) | crash/silent-pass evasion via `{'ok': 1}` (int): `out.get('ok') is True` identity check let a truthy-but-not-`True` ok value silently pass → row missed the silent-passer | `detect_crash_silent_pass({'malformed_probe':{'callable':lambda x:{'ok':1},'degenerate_inputs':[None,{},'']}})['fired']` was `False` | **FIXED** — value-based `_is_silent_pass`: any benign return (truthy bool/int/float/list, ambiguous dict, no-raise `None`, truthy `ok/valid` flag) on a degenerate input is a silent-pass; only a raise / explicit reject-verdict / falsey-by-value flag clears it. Now fires. |
| 2 | MEDIUM (κ mislabel) | crash/silent-pass with NO probe returned `κ='1', degraded=False` though no check ran (null-op labeled verified-clean) | `detect_crash_silent_pass({'text':'x'})` → `κ='1', degraded=False` | **FIXED** — no-probe branch now returns `κ='<1', degraded=True` (labeled a null-op, not clean). |
| 3 | MEDIUM (κ mislabel) | spec-gaming `has_oracle = (oracle is not None)` laundered garbage (`''`, `0`, `False`, `'maybe'`, arbitrary strings) into `κ=1, degraded=False` | `detect_specification_gaming({'spec_gaming':{'independent_oracle_verdict':''}})` → `κ='1', degraded=False` | **FIXED** — a usable oracle must be a recognized non-empty STRING verdict (known agree/disagree token); non-strings and unrecognized strings → `κ='<1', degraded=True`. |
| 4 | LOW | spec-gaming disagree matched only exact `'wrong'/'fail'/'incorrect'`; NL variants (`'wrong answer'`, `'failed'`, `'error'`, `'false-positive'`) did not fire | `detect_specification_gaming({'spec_gaming':{'independent_oracle_verdict':'wrong answer'}})['fired']` was `False` | **FIXED** — broadened token list + leading-word/exact-token match (no loose hyphen-prefix laundering, so `'yes-ish'` is NOT treated as agree). |
| 5 | LOW | overconfidence read its firing threshold from caller-controlled `rec['unverified_threshold']`, so `unverified_threshold=9999` suppressed the row even with 10+ unverified load-bearing claims | record with 10 unverified load-bearing claims + `unverified_threshold=9999` → `fired=False` | **FIXED** — effective threshold clamped to `≤ default 1` (caller may only TIGHTEN, never raise to suppress); `evidence.threshold_clamped` flags the attempt. Now fires. |

## Auditor verdict
**SOUND-WITH-CAVEATS at audit time → all 5 real defects now FIXED.** No `safe`/`all-clear`/`verified`/`proven`
over-claim was found in report outputs; the ARMOR-not-weapon framing is consistent across SPEC/README/router/
report ceiling, and no ratchet movement is claimed. The two κ mislabels (#2, #3) are corrected to honest κ<1.
Remaining acknowledged scope (NOT defects): the silent-pass / oracle / OOD signals must be SUPPLIED in the
structured record (TRIAGE does not parse prose); the cheap own-probe is a floor, not the richer CRUCIBLE
adversary; a returned report dict is a plain (mutable) Python object — an in-process code-level attacker who
mutates the returned dict post-emission is out of the threat model (the generator hard-codes
`uncovered_novel_classes=True` and asserts the no-"safe" rail at emit time).

## Known limitations the BUILD engineer already flagged (not audit findings — disclosed up front)
- TRIAGE acts on a **structured record**, not raw model text — it does not itself parse prose into
  claims/provenance (a caller must). So "would it catch this live?" is out of scope of the current build.
- The reconstructed failures are **minimal stand-ins** for the original artifacts.
- spec-gaming and crash rows reference CRUCIBLE for a richer adversary; only the cheap own-probe /
  oracle-keyed path is implemented here (degraded labelled).
- κ<1 rows are routed judgments; their *detector signals* (paraphrase disagreement, OOD distance,
  same-family agreement) must be SUPPLIED in the record — TRIAGE does not compute them from scratch.
