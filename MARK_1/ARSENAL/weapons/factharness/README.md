# FACTHARNESS — the Helmet's grounding / fabrication core facility (Weapon #7)

**PROMOTED + HARDENED from SOCIUS `S-GROUND`** (not built from scratch). The institutionalized arm of
the Integrity Office: every department + the Provost call it; every shipped prose claim is routed
through it (ground or abstain).

## What it does
Given a prose claim + the *fetched* text of its cited source:
- **F-QUOTE (κ=1)** — is the quoted text verbatim in the source? (punctuation-preserving exact match)
- **F-NUMBER (κ=1)** — does the cited number appear in the source? (boundary-safe: `7` ∉ `7.5`)
- **F-CITE (κ=0.7, advisory)** — do the claimed authors/year match the source bibliography? (exact-word, not substring)
- **F-ENTAIL (κ=0)** — does the source *support* the paraphrase? → a cross-model judge (≠ generator); unsure → **ABSTAIN**

## Use it
```python
from factharness import ground
r = ground({"text": "...", "source_text": "<fetched source>", "quote": "...",
            "numbers": [{"value": "7", "context": "significant"}],
            "claimed_authors": "Steegen et al.", "claimed_year": 2016,
            "source_metadata": {"authors": "...", "year": 2016}})
r["overall"]   # GROUNDED | GROUNDED_BY_JUDGMENT | FABRICATION_FLAG | CONTRADICTED_BY_SOURCE | ABSTAIN
```
Firewall over a batch (the shipping gate): `from factharness_router import firewall; firewall(claims)`
→ `{ship_ok, grounded, needs_label, blocked}`. FABRICATION_FLAG / CONTRADICTED **block** shipping;
GROUNDED_BY_JUDGMENT / ABSTAIN ship only behind an explicit unverified label.

## Run the gate + demo
```
python3 selftest_all.py                 # 36 assertions, incl. 3 SOCIUS audit regressions (A1/A3/B-CRITICAL)
python3 factharness_router.py           # firewall smoke test
python3 demo_grounding/run_grounding.py # 6 claims vs a real Wikipedia source; all predictions matched
```

## Carried-forward audit fixes (locked as regression tests)
- **A1** quote over-normalisation: `p 0.001` must NOT match `(p < 0.001)`.
- **A3** number boundary: `7` must NOT match inside `7.5`.
- **B-CRITICAL** bibliography substring exploit: `Smith and Jones` must NOT match `Brown and Williams`.

## Ceiling (honesty — non-waivable)
- **Grounded ≠ true.** Checks support by the *supplied source*, not correctness of the source. A
  perfectly-grounded claim can cite a wrong/biased source.
- **FABRICATION_FLAG ≠ fraud.** A flag = "this quote/number/cite does NOT appear in the supplied source,"
  with candidate causes (paraphrase mismatch, wrong source, OCR error). It never accuses a person.
- **Entailment is κ=0.** F-ENTAIL is a cross-model judgment; unsure → ABSTAIN. Never dressed as a κ=1 check.
- A weapon ADDED (promoted facility) = **capability EXPANSION (institutionalized grounding), NOT a ≥10%
  promotion** — no shared arena. The capability ratchet stays OPEN at v3.
