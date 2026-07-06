# GRANTHAFORGE — weapon kickoff

**What:** turn a math/computation **treatise** (karaṇa, siddhānta, algorithm book, numerical-methods text,
technical spec — any verse/section-structured computational source) into a self-contained, **verse-by-verse,
verified code engine**, stage by stage, phase by phase, without losing the path.

**Engage:** `/granthaforge`, or auto-engages on "code this book/treatise verse by verse", "build a verified
engine from this text", "reproduce its worked examples in code", "port this karaṇa/siddhānta/spec".

**Verifier (the heart):** each verse is anchored by its **example** (reproduce the printed numbers; prefer two)
OR, when there is none, its **explanation** via the verification ladder (units → limiting cases →
derivation-closure → cross-source → inter-section closure → synthetic equivalent → external oracle). Honest tiers:
VERIFIED / DERIVED / CODED / TODO. Both anchors are on the same path.

**Loop:** scaffold (engine / ground-truth / plan / source_material + render→OCR→verify harness) → page map →
PILOT a few verses → take off chapter by chapter. OCR is load-bearing (never a number from memory). Flag book
errata + commentator-vs-base divergences, never fudge. Keep a living progress board so the build survives context
resets; write BUILD_REPORT + HANDOFF_PROMPT at milestones.

**Honesty rail (weapon ceiling):** a verse running without error is **CODED**, not verified. Never stamp VERIFIED
without an example or an exact independent equivalent. The verifier is the only authority.

**Doctrine:** `MARK_1/ARSENAL/GRANTHAFORGE/CHARTER.md` · `VERIFICATION_LADDER.md` (the heart) · `SCAFFOLD.md`
(reusable folder + harness).

**Canonical case study:** `Parvad_code_v2/grahalaghava_code_and_example/` — Grahalāghava engine, Ch.1–8, 60/60
worked examples, NASA-validated, errata + Viśvanātha divergences logged (`plan/BUILD_REPORT.md`).
