# VAULT — independent AUDIT (stub for the auditor to fill)
*The auditor MUST be a model ≠ the generator (Sonnet/Haiku ≠ the Opus build).
Self-review is theater (box rule C8). This stub frames the attacks; the auditor fills
the verdicts below.*

## Build state at hand-off (filled by the builder)
- `selftest_all.py` exits **0** (all three suites green): gate, store-contract, router.
- `demo_backfill/run_demo.py` exits **0**: **19/19** committed predictions confirmed.
- Deps: Python 3.9.6 stdlib only (`json`, `datetime`, `tempfile`, `os`, `sys`). No pip
  installs needed.

## The attacks the auditor MUST attempt (each: state the input, the observed output, PASS/FAIL)
1. **LEAD-as-fact (the cardinal sin).** Try every way to get an unverified result returned
   by `query_facts`: requested_tier=VERIFIED_FACT with no record; an empty record; a
   `{verified:true}` record; a record with whitespace-only fields; a domain string that
   matches a real fact's domain. Expected: ALL land as LEAD, none appear in `query_facts`.
   - Auditor verdict: __________
2. **In-place LEAD-promotion attack (the κ=1 core).** Specifically attack
   `validate_verification_record` — find ANY present-but-contentless record shape that
   passes. Try: nested-empty `{"method":{},"artifact":"","result":[]}`; numeric-zero
   fields; boolean fields; extra keys masking missing required ones.
   - Auditor verdict: __________
3. **Stale-served-silently.** Take a FETCHED_FACT past its TTL on a high-stakes read; try
   to get it back WITHOUT a REVERIFY flag. Check a low-stakes stale read is FLAG_STALE (not
   silently FRESH). Check a VERIFIED_FACT is correctly non-decaying (no false staleness).
   - Auditor verdict: __________
4. **Provenance integrity.** Confirm every fact in `query_facts` traces to a real
   method/artifact; confirm a LEAD yields NO provenance trail; confirm provenance survives
   the disk round-trip and a tampered JSON (hand-edit a stored LEAD's tier to VERIFIED_FACT
   on disk — does it then leak into facts? If so, that is a finding: the store trusts disk).
   - Auditor verdict: __________
5. **TTL / stakes ENUM committed-not-judged.** Confirm TTL_DAYS and STAKES are constants,
   not model calls; confirm an out-of-enum stakes value raises; confirm a short-TTL fact
   re-flags on the next read past its TTL.
   - Auditor verdict: __________
6. **Honesty rails.** Confirm README + SPEC state the temporal-change limitation, the
   literal-key retrieval limit, the "record structurally valid but not re-run" limit, and
   the infra-not-weapon framing. Confirm GROUNDING cites FETCHED sources (not memory) and
   flags the G4 benchmark discrepancy + the G3 partial-fetch.
   - Auditor verdict: __________

## Known builder-disclosed limitations (do not re-discover as if hidden)
- The store TRUSTS its JSON file on reload (no integrity signature). A hand-edit of the
  persisted JSON to flip a tier WOULD leak — out of scope for v0 (the threat model is
  honest write-discipline, not a malicious on-disk attacker). Flagged for the auditor to
  confirm/escalate.
- Retrieval is literal substring, not semantic — recall can miss a non-literal query key.
- The gate validates record STRUCTURE, not record TRUTH (it does not re-run verification).

## Auditor sign-off
- Auditor model: __________   Date: __________
- Overall: __________ (SOUND / SOUND-WITH-CAVEATS / UNSOUND)
- Findings filed: __________
