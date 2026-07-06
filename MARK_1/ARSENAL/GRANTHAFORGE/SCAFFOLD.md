# GRANTHAFORGE · SCAFFOLD — the reusable folder + harness

*Copy this structure and these three files at the start of a build. `<proj>` = a short project name
(e.g. `grahalaghava`). Everything is self-contained and Spyder/CLI-runnable; the engine imports nothing
outside its own folder.*

```
<proj>_code_and_example/
├── render_pages.py              # PDF→PNG renderer for OCR (scan sources only)
├── source_material/             # the primary text + ALL parallel editions/commentaries
├── ocr_pages/                   # rendered PNGs (kept for re-checking)
├── plan/
│   ├── 00_MASTER_PLAN.md        # design + stages + the per-verse workflow
│   ├── 01_PROGRESS.md           # living verse board + ERRATA + DIVERGENCE tables
│   ├── PAGE_MAP.md              # scan↔printed page offset + chapter openers
│   ├── OCR_LOG.md               # every page read + what it yielded
│   ├── BUILD_REPORT.md          # (at milestones) the method
│   └── HANDOFF_PROMPT.md        # (at milestones) resume-exactly-here prompt
├── <proj>_complete_example/     # GROUND TRUTH
│   ├── examples.py              # verbatim anchor records (pure data)
│   └── verify_examples.py       # runs engine vs records → PASS/Δ
└── <proj>_complete_code/        # the engine
    ├── constants.py             # shared epoch/constants
    ├── ch01_*.py … chNN_*.py    # one module per chapter; one fn per verse-step
    └── <helpers>.py             # sexagesimal/units, figures, date converters
```

---

## 1. `render_pages.py` (scan → PNG for OCR)
```python
import sys, os, fitz                       # PyMuPDF
HERE = os.path.dirname(os.path.abspath(__file__))
PDF  = os.path.join(HERE, "source_material", "PRIMARY.pdf")
OUT  = os.path.join(HERE, "ocr_pages")
def render(first, last=None, dpi=220, pdf=PDF, prefix="pdf"):
    os.makedirs(OUT, exist_ok=True); last = last or first; doc = fitz.open(pdf)
    for p in range(first, last + 1):
        doc[p-1].get_pixmap(dpi=dpi).save(os.path.join(OUT, f"{prefix}{p:03d}.png"))
        print("rendered", p)
    doc.close()
if __name__ == "__main__":
    a = sys.argv[1:]; dpi, pdf, pre = 220, PDF, "pdf"
    if "--dpi" in a: i=a.index("--dpi"); dpi=int(a[i+1]); del a[i:i+2]
    if "--pdf" in a: i=a.index("--pdf"); pdf=os.path.join(HERE,"source_material",a[i+1]); pre="alt"; del a[i:i+2]
    render(int(a[0]), int(a[1]) if len(a)>1 else None, dpi=dpi, pdf=pdf, prefix=pre)
```
Then OCR the PNGs with the google-vision tool; re-render `--dpi 330` for unclear numbers. **Never** trust the
PDF's own text layer on a scan.

---

## 2. `examples.py` — anchor records (PURE DATA; decimal literals only)
Both verifier kinds live here. An **EXAMPLE-GOLD** record carries the book's printed numbers; an
**EXPLANATION-GROUND** record carries the ladder checks (limiting cases, cross-source value, downstream
consequence) instead.
```python
EXAMPLES = [
  # --- EXAMPLE-GOLD: reproduce the printed worked example ---
  {"id": "ch1_ahargana_ex1", "chapter": 1, "verse": "4-5", "topic": "ahargaṇa",
   "verifier": "example", "tier": "VERIFIED", "source": "Author/commentator", "pages": "PDF 16-17",
   "dispatch": "ahargana", "tol": 0.0,                         # exact; or per-field "tols": {...}
   "given": {"saka_year": 1534, "lunar_months_elapsed": 1, "tithis_elapsed": 14},
   "expected": {"cakra": 8, "ahargana": 1521}, "note": ""},
  # --- EXPLANATION-GROUND: no printed example; anchor by ladder rungs ---
  {"id": "ch2_moon_mandaphala_limits", "chapter": 2, "verse": "3", "topic": "Moon mandaphala (no example)",
   "verifier": "ladder", "tier": "DERIVED", "source": "rule + rung3 limit + rung6 cross-source",
   "dispatch": "moon_mandaphala_max", "tol": 0.01,
   "given": {"bhuja_deg": 90.0},                                # the stated parama (max) case
   "expected": {"value": 5.028},                                # text's stated max ≈ 5°
   "note": "rung3 limiting-case (parama=5°) + rung6 (same denom 56 in Joshi ed.) → DERIVED."},
]
```

---

## 3. `verify_examples.py` — the heartbeat
```python
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(os.path.dirname(HERE), "<proj>_complete_code")
for p in (HERE, ENGINE):
    if p not in sys.path: sys.path.insert(0, p)
from examples import EXAMPLES
import ch01_madhyama as m1  # … import each engine module
DISPATCH = { "ahargana": lambda g: m1.ahargana(**g), }  # dispatch -> callable(given)->result dict
def _close(a, b, tol): return abs(a-b) <= tol if isinstance(a,(int,float)) and isinstance(b,(int,float)) else a==b
def main(argv):
    only = int(argv[argv.index("--chapter")+1]) if "--chapter" in argv else None
    npass = nfail = 0
    for ex in EXAMPLES:
        if only and ex["chapter"] != only: continue
        fn = DISPATCH.get(ex["dispatch"]);  res = fn(ex["given"]) if fn else None
        tol = ex.get("tol", 0.0); per = ex.get("tols", {})
        diffs = [f"{k}: {res.get(k)!r} != {v!r}" for k,v in ex["expected"].items()
                 if not _close(res.get(k), v, per.get(k, tol))] if res else ["no dispatch"]
        if not diffs: npass += 1; print("PASS ", ex["id"], f"[{ex.get('tier','?')}]")
        else: nfail += 1; print("FAIL ", ex["id"]); [print("    Δ", d) for d in diffs]
    print(f"\n{npass} passed, {nfail} failed.")
    return 1 if nfail else 0
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
```
Run: `python3 <proj>_complete_example/verify_examples.py [--chapter N]`.

---

## 4. `plan/01_PROGRESS.md` — the living board (the path-keeper)
Three tables. Update after every verse.

**Stage status** (one row per chapter: TODO / in-progress / COMPLETE + date).

**Verse log** — one row per verse:
`| Ch | Verse | Topic | OCR pp | Anchor (example/ladder) | Engine fn | Tier | Notes |`
where **Tier** ∈ VERIFIED / DERIVED / CODED / TODO (see VERIFICATION_LADDER.md).

**Divergences** (commentator vs base text) and **ERRATA** (book's own slips):
`| Ch | Verse | What differs | base value/formula | commentator/erratum value | Source pp |`

Plus an **open-questions** section and (at milestones) a **NASA/oracle-validation** block.

---

## 5. Plan templates (headers)
- `00_MASTER_PLAN.md`: goal · folder layout · the per-verse workflow · the stage table · known facts ·
  honesty rails.
- `PAGE_MAP.md`: the offset rule + anchors that fix it + chapter-opener table (confirm each by reading).
- `OCR_LOG.md`: a table `| page | printed-page | content | yield |` + a "verified constants" block per chapter.
- `BUILD_REPORT.md` / `HANDOFF_PROMPT.md`: write at milestones (see the GL build's copies for the template).

---

## 6. Conventions that travel
- One function per verse-step; constants inline; docstring quotes the rule.
- Tolerances = the text's own rounding (exact fields → 0).
- Tier honestly; a running-but-unchecked formula is **CODED**, never VERIFIED.
- Flag every divergence + erratum; the engine follows the stated rule, the slip is logged.
- Keep the source's parallel editions in `source_material/` and OCR them on demand (`render_pages.py --pdf …`)
  for cross-source corroboration (ladder rung 6).
```
