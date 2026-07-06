# FACTHARNESS — independent cross-model audit (2026-06-20)

**Auditor:** Claude Sonnet 4.6 (cross-model, ≠ the Opus generator — never Opus-audits-Opus).
**Method:** adversarial attack battery (~66 tests), every claim machine-confirmed by running code.
**Baseline:** `selftest_all.py` (36 assertions) + demo passed before the attack.

## Verdict: SOUND-WITH-CAVEATS → **3 real defects found, all FIXED + locked as regression tests**

The κ-separation core held: the entailment judge (κ=0) can never launder a failed frozen check (H2),
and a judge-only "entailed" never reaches GROUNDED (H1, → GROUNDED_BY_JUDGMENT). The 3 carried-forward
SOCIUS fixes (A1/A3/B-CRITICAL) all resisted new variants. But the auditor BROKE three things:

| # | defect | κ | severity | fix |
|---|---|---|---|---|
| **D2** | Unicode MINUS U+2212 was stripped to a space in `_norm` → a sign-flipped number (`−7`) grounded against a positive source (`7`). A genuine **κ=1 soundness breach**. | 1 | **High** | added `−` (U+2212) to the dash-normalisation range in `_norm` |
| **D1** | name particles `van`/`der`/`von` (3+ chars, not in `_BIB_STOP`) let a particle-only author match `van der X` → false attribution + a real frozen check = `GROUNDED`. | 0.7 | Medium | added particles to `_BIB_STOP` |
| **D3** | `also_require` context used a raw substring → `treat` matched inside `untreated`, `sign` inside `insignificant`. | 1 | Low | word-boundary regex for the context match |

All three fixes are in `factharness.py`; their break-cases are locked in `selftest_all.py` (now 46
assertions, all green) under the "AUDIT REGRESSIONS" block. The demo re-ran clean after the fixes.

## Attacks the gate correctly RESISTED (selected)
A3 variants (`7`∉`70`/`1700`/`1.7e3`; `7`∈`$7M`/`7%` correctly grounds); A1 variants (`p 0.001`∉
`(p < 0.001)`; bracketed CIs preserved); Cyrillic/ZWSP homoglyph quotes (caught/safe); B-CRITICAL
(`Smith and Jones`∌`Brown and Williams`; 3-char fragments; hyphenated names; all-initials);
H1/H2 κ-policing (judge cannot launder a failed frozen check or upgrade to GROUNDED); empty/whitespace
source → ABSTAIN; 100k-word source (no perf issue).

## Non-defect coverage gaps (do NOT compromise soundness — no fabrication becomes grounded)
- `.05` does not verify against `0.05` (leading-zero-free form) — a *false negative*, safe but reduces coverage.
- ZWSP / soft-hyphen in a CMS/PDF-extracted quote can break a true match — safe false negative.
These are logged, not fixed (they cannot produce a false GROUNDED).

## Carry-back note (honest)
D2 and D3 exist **latently in the SOCIUS seed** `socius/ground_verify.py` (same `_norm` / `also_require`
code). FACTHARNESS is now the canonical facility with the fixes; the seed should be back-patched or
deprecated in favour of importing FACTHARNESS. Flagged for a follow-up (does not block this build).
