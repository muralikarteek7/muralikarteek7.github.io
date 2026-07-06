# FACTHARNESS demo — committed PREDICTIONS (written BEFORE running the verifier)

Source: real text fetched 2026-06-20 from **Wikipedia, "Strassen algorithm"** (verbatim sentences +
numbers, stored in `run_grounding.py` as `SRC` / `META`). Six claims are routed through `ground()`.

| # | claim | what I did to it | PREDICTED `overall` |
|---|---|---|---|
| 1 | "Volker Strassen first published this algorithm in 1969" + number 1969 | faithful verbatim quote + real number | **GROUNDED** |
| 2 | quote "the algorithm requires only six multiplications instead of eight" | FABRICATED quote (source says 7, not six) | **FABRICATION_FLAG** |
| 3 | number 11 (context "multiplications") | FABRICATED number (source has 7 and 8, never 11) | **FABRICATION_FLAG** |
| 4 | cite "Williams and Page" (1969) vs source author "Volker Strassen" | WRONG-AUTHOR cite | **FABRICATION_FLAG** |
| 5 | number 7 (context "multiplications") + number 1969 | faithful real numbers | **GROUNDED** |
| 6 | paraphrase "Strassen changes the asymptotic behaviour of matrix multiplication", judge = uncertain, no verbatim quote | genuine entailment ambiguity | **ABSTAIN** |

Firewall expectation over the batch: `ship_ok = False` (claims 2/3/4 are BLOCKING fabrication flags);
2 grounded ship freely (1, 5); 1 needs an unverified label (6, ABSTAIN).

Honesty note: each FABRICATION_FLAG reports "does not check against the supplied source" + candidate
causes — NEVER an accusation of fraud (claims 2/3/4 are fabrications *I* deliberately injected to test
the gate, not anyone's misconduct).
