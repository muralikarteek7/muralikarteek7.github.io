# CRUCIBLE Run Report — Arsenal Verifier-Gate Hardening

**Run date:** 2026-06-20 · **Harness:** `crucible_harness.py` · **Audit:** independent Sonnet cross-model
auditor (a model ≠ the prober/generator). **Scope:** the 11 κ>0 arsenal gates, per the pre-committed
scope table in `crucible_router.py`.

> **Read the ceiling first.** A KILL is a machine-checked proof a gate has a bug. A SURVIVED is
> **evidence, not proof** (Dijkstra: *testing shows the presence of bugs, never their absence*). This
> report **does not** claim any gate is "sound" or "proven", and it **does not** say "all 12 survived".
> A clean sweep upgrades a gate's κ=1 label from **ASSERTED** to **ADVERSARIALLY-TESTED (to budget)** —
> nothing stronger. See the HONEST CEILING section.

---

## 1. HEADLINE

| Outcome | Count | Targets |
|---|---:|---|
| **REAL KILLs** (re-runnable bug, audit-confirmed) | **4** | factharness_quote, optima_feasibility, symbolica_agreement, socius_evalue |
| **SURVIVED to budget** (no kill within budget; evidence not proof) | **7** | trialguard_grim, redcell_ctf, frontier_capset, proofsmith_wrapper, reproml_contamination, **+ codeforge_sortnet, psymetrix_grim** (swept clean in the committed demo) |
| **ABSTAINED / BLOCKED** (coverage could not be exercised — a GAP, not a pass) | **0** | — |
| **DECLINED** (guarded-κ / κ=0 — not falsifiable as an exact verifier) | **1** | econometrix_walkforward |

- **9 gates were probed in this run.** 2 more (codeforge_sortnet, psymetrix_grim) were already swept
  clean as full-differential in the committed demo and are carried as SURVIVED. 1 (econometrix) is DECLINED.
- **4 KILLs total**: factharness carries **two** distinct kills (a Unicode false-accept and a
  malformed-input false-accept); optima carries **two** distinct kills (a metamorphic false-reject and a
  no-status false-accept). Counted as 4 owning-target kills across 6 exhibits.
- Every REAL_KILL below was **independently reproduced against the live gate** while writing this report
  (not taken on the prober's word). Commands and outputs are recorded in §3.

---

## 2. PER-BUCKET TABLE

### 2a. Full-differential (independent oracle present → false-accept/false-reject probed)

| Target | Owning weapon | Status | Coverage actually achieved | Audit verdict |
|---|---|---|---|---|
| codeforge_sortnet | codeforge | SURVIVED (demo) | full-differential (committed demo) | clean sweep (prior) |
| psymetrix_grim | psymetrix | SURVIVED (demo) | full-differential (committed demo) | clean sweep (prior) |
| trialguard_grim | trialguard | **SURVIVED** | full-differential: FA/FR/metamorphic/abstain; 53,322 objects; metamorphic over 25,953 even-n seeds | `SURVIVED_CONFIRMED` |
| factharness_quote | factharness | **KILL ×2** | full-differential: FA 65 / FR 65 / meta 12 / abstain 6 | `REAL_KILL` |
| redcell_ctf | redcell | **SURVIVED** | full-differential: 451 candidates (43 ACCEPT/408 REJECT), 3 metamorphic transforms, 5 abstain | `SURVIVED_CONFIRMED` |
| frontier_capset | frontier (symbolica) | **SURVIVED** | full-differential: FA 325 / FR 125 / meta 96 / abstain 9 + 2000-case cross-fuzz | `SURVIVED_CONFIRMED` |

### 2b. Metamorphic-only (no independent oracle → no false-accept hunt; PARTIAL coverage)

| Target | Owning weapon | Status | Coverage actually achieved | Audit verdict |
|---|---|---|---|---|
| optima_feasibility | optima | **KILL ×2** | metamorphic (4 transform classes) + abstain/crash. **No FA hunt** (oracle is gate's own mechanism class) | `REAL_KILL` |
| proofsmith_wrapper | proofsmith | **SURVIVED** | metamorphic (5 transforms ×6 seeds) + abstain/crash — **PRE-CHECK 0 IO-scan only; Lean kernel never exercised** | `SURVIVED_CONFIRMED` |
| reproml_contamination | reproml | **SURVIVED** | metamorphic (3 caller-asserted transforms ×6 seeds) + abstain/crash — **no FA/FR (free threshold ⇒ circular oracle)** | `SURVIVED_CONFIRMED` |
| symbolica_agreement | symbolica | **KILL** | metamorphic (8 transforms) + abstain/crash. **No FA hunt** | `REAL_KILL` |
| socius_evalue | socius | **KILL** | E-value leg ran a **genuine differential oracle** (FA/FR/metamorphic, ~4,374 probes); multiverse leg metamorphic-only | `REAL_KILL` |

### 2c. Declined / blocked

| Target | Owning weapon | Status | Honest reason |
|---|---|---|---|
| econometrix_walkforward | econometrix | **DECLINED** | Guarded-κ verdict. CRUCIBLE cannot adversarially falsify a judgment that never claimed an exact (κ=1) verifier. This is a deliberate scope exclusion, not a pass. |

### Auditor-flagged problems → ACTION ITEMS

The auditor found **no THEATER_STUB, no SPURIOUS_KILL, and no circular-oracle that invalidated a verdict**.
The non-blocking issues found are tracked as action items:

- **[CODE QUALITY] `oracles/grim_oracle.py` dead code.** Line computes `k_min = … if lo>0 else …` then
  the next line unconditionally overwrites it with `k_min = math.ceil(lo * Neff)`. Confirmed present.
  The auditor verified this does **not** make the oracle circular: the oracle is a distinct Python object
  in a distinct file (`crucible/oracles/grim_oracle.py`) from the gate
  (`psymetrix/forensics_verify.py`), and the final arithmetic is equivalent-by-convergence, not copied.
  **Action:** delete the dead line.
- **[PROBER OUTPUT TRUNCATION] factharness prober output was cut off mid-JSON after Mode 3.** The
  prober's raw capture missed the Mode 4 (list-source) kill and the KILL-double-check section. The
  auditor's full re-run recovered **both** kills. **Action:** capture full prober stdout (the truncation
  hid a real second bug); already reflected in the kill count here.
- **[PROBER OUTPUT TRUNCATION] socius prober output truncated mid-JSON** during the E-value false-reject
  leg, obscuring the abstain-crash KILL until the auditor re-ran. **Action:** same fix.
- **[TASK-PARAM UNDERSTATEMENT] socius coverage label `metamorphic-only` is inaccurate** — the E-value
  leg ran a real bisection oracle on `BF(E)=E²/(2E−1)` (full differential); only the multiverse leg is
  metamorphic-only. This is an *understatement* of coverage (not an overclaim) and does not affect any
  verdict. **Action:** correct the per-target coverage tag to "mixed (E-value full-differential +
  multiverse metamorphic-only)".
- **[CAPTURE ARTIFACT] reproml `disclaimer_present=` blank in prober output** for the all-empty-eval
  case was a terminal-truncation artifact; the auditor's direct gate call confirms `disclaimer_present=True`
  always. No defect. **Action:** none beyond capture fix.

---

## 3. REAL KILLs — exhibit, owning weapon, required fix

Each kill below was **re-run against the live gate while writing this report**; verdicts shown are the
actual observed outputs. **Required fix for every kill: (a) patch the gate; (b) freeze the exhibit as a
permanent regression self-test in the owning weapon's `selftest_all.py`.**

### KILL 1 — factharness_quote · Unicode NFKD false-accept (Mode 1)

- **Owning weapon:** factharness (`factharness.py::verify_quote`, `_norm_quote`)
- **Exhibit:**
  - quote = `"… we observed that m2 across conditions"` (ASCII `m2`, U+0032)
  - source = `"… we observed that m² across conditions"` (U+00B2 SUPERSCRIPT TWO = "m squared")
- **Gate verdict (reproduced):** `{'verdict': 'quote_found', 'grounded': True, 'kappa': 1}` — **ACCEPT**
- **Independent oracle verdict:** WRONG — distinct codepoints, distinct meaning; not a verbatim quote.
- **Root cause:** `_norm_quote` applies **NFKD** normalization. NFKD compatibility-decomposes `²`→`2`
  (and `combining('²')==0`, so it survives the combining-mark filter), silently folding a
  meaning-changing superscript to ASCII. This **exceeds the gate's own stated normalization contract**
  ("modulo case, accents, smart quotes, and whitespace"). The independent NFC-only oracle returns WRONG.
- **Residual note (honest):** this rests on a normalization-*policy* reading — a maintainer who *wanted*
  compatibility folding could call it intended, but the docstring does not document it. Defensible kill;
  the patch should make the policy explicit either way.
- **Required fix:** change `_norm_quote` from NFKD to **NFC** (or NFD + combining strip) so compatibility
  glyphs (superscripts, fullwidth digits, Roman-numeral glyphs, vulgar fractions, enclosed/letter-like
  symbols) are **not** folded to ASCII; document the exact normalization contract. **Freeze `m2`/`m²` as
  a regression self-test (must REJECT).**

### KILL 2 — factharness_quote · malformed-input false-accept (Mode 4)

- **Owning weapon:** factharness (`_norm_quote`)
- **Exhibit:** quote = `"a real quote of words"`, source_text = `['a real quote of words']` (a **list**)
- **Gate verdict (reproduced):** `{'verdict': 'quote_found', 'grounded': True}` — **ACCEPT**
- **Why:** on non-string input, `_norm_quote` calls `str(source_text)` → `"['a real quote of words']"`;
  the quote text is a substring of that repr, so the gate ACCEPTs malformed input instead of abstaining.
- **Required fix:** type-guard `source_text` at the top of `verify_quote` — if it is not a `str`, return
  **ABSTAIN/ERROR**, never `quote_found`. **Freeze the list-source case as a regression self-test (must
  ABSTAIN/ERROR, never ACCEPT).**

### KILL 3 — optima_feasibility · lp_dual ignores `objective.constant` (metamorphic false-reject)

- **Owning weapon:** optima (`optima_gate.py::_verify_lp_dual`)
- **Transform:** objective constant-shift (+1000) — add K to `objective.constant` AND to the claimed
  objective number. Meaning-preserving (shifts every feasible objective value by the same K; the argmax
  is unchanged). Validated by from-scratch brute-force enumeration.
- **Exhibit (reproduced):** base model max `3x+2y` s.t. `x+y≤7`, claim `OPTIMAL x=7,y=0, obj=21`,
  lp_dual cert → **ACCEPT (`OPTIMAL_CERTIFIED`)**. Shift `constant=1000`, claim `obj=1021` → **REJECT
  (`FEASIBLE_WITH_GAP`)** with `dual_bound(as_max)=21`, `primal(as_max)=1021`, `gap=-1000`.
- **Root cause:** `_verify_lp_dual` builds the dual bound from constraint rows + box bounds and **never
  folds in `objective['constant']`**, then compares it against `primal_as_max = claimed_objective` which
  *includes* the constant. At `constant=0` they match; at `constant≠0` the gap is exactly the constant,
  so a correctly-certified shifted optimum is always rejected on the lp_dual path. (The exhaustive and
  independent cert tiers handle the constant correctly; the bug is lp_dual-specific.)
- **Required fix:** in `_verify_lp_dual`, compare `bound + obj.get('constant', 0) == primal_as_max`
  (accounting for the MIN sense flip as already done). **Freeze the +1000-shift pair as a regression
  self-test (both must CERTIFY).**

### KILL 4 — optima_feasibility · missing-`status` false-accept (abstain/crash)

- **Owning weapon:** optima (`optima_gate.py::certify`)
- **Exhibit (reproduced):** a claim dict with **no `status` key** but a feasible solution and an
  optimality certificate → **`OPTIMAL_CERTIFIED`**.
- **Root cause:** `certify` reads `status = claim.get('status')`, special-cases only
  `status == 'INFEASIBLE'`, then falls through to feasibility/objective/optimality checks for *any* other
  value including `None`. Malformed input is silently certified.
- **Required fix:** guard at the top — if `status not in ('OPTIMAL','FEASIBLE','INFEASIBLE')` → **REJECT
  or ABSTAIN**. **Freeze the no-status claim as a regression self-test (must REJECT/ABSTAIN).**

### KILL 5 — symbolica_agreement · 0-vs-residue over-strict false-reject (metamorphic)

- **Owning weapon:** symbolica (`symbolica_gate.py::_agree`, `verify_identity`)
- **Transform:** rearrange `A==B` → `(A−B)==0`. Meaning-preserving by the field axiom `a=b ⟺ a−b=0`
  (confirmed by `sympy.simplify` on both forms).
- **Exhibit (reproduced):** `verify_identity('sin(x)**2 + cos(x)**2', '1', ['x'], [-3,3])` → **CERTIFIED**
  (worst_agreed_digits ≈ 50.6). Rearranged `verify_identity('sin(x)**2 + cos(x)**2 - 1', '0', …)` →
  **REJECTED** ("numeric disagreement"), `worst_agreed_digits = 0.0`, residue ≈ `−1.34e-51`.
- **Root cause:** `_agree` has an absolute-tolerance floor **only when `scale == 0` exactly**. On the
  rearranged form, catastrophic cancellation makes the lhs a tiny float residue (~1e-51) instead of exact
  `0.0`; `scale` becomes that residue, `rel = diff/scale = 1.0`, `achieved = −log10(1.0) = 0` digits →
  the numeric leg reports DISAGREEMENT and short-circuits to REJECTED, even though `symbolic_simplify_zero`
  and `series_zero` both fire. Confirmed at the primitive: `_agree(-1.33e-51, 0, 30)` → `(False, 0.0)`.
- **Narrowness (honest):** the bug does **not** mask genuinely-wrong identities — a truly-false rearranged
  identity like `(-x)==0` on `(1,4)` still correctly REJECTS. **No false-accept hunt was run** (no
  independent oracle), so a gate that wrongly CERTIFIES a wrong closed form would not be caught by this
  campaign. This kill is a false-*reject*, not a soundness hole.
- **Required fix:** apply the absolute-tolerance floor whenever `|scale|` is near machine-epsilon-times-
  magnitude (not only `scale==0`), OR let an unconditional `symbolic_simplify_zero` short-circuit to
  CERTIFIED before the numeric leg can veto. **Freeze the rearranged Pythagorean-identity pair as a
  regression self-test (both must CERTIFY).**

### KILL 6 — socius_evalue · non-finite input false-accept (abstain/crash)

- **Owning weapon:** socius (`eval_verify.py::assess_sensitivity`, `e_value`)
- **Exhibit (reproduced):** `assess_sensitivity(float('inf'), 'RR')` → `robust_to_confounding=True`,
  `e_value_point=inf` — a **confident ACCEPT on a non-finite input** with no loud abstain.
- **Root cause:** `e_value(inf)=inf`, and `inf >= 2.0` (benchmark) is `True`, so a nonsense input is
  certified "robustly confounding-proof". The gate **does** guard `estimate<=0` (`-1.0` → `ValueError`,
  confirmed), so its input validation is **inconsistent** — the `>0` guard lets non-finite values
  through. (`nan` → `robust=False` (REJECT), which lands in the safe set, so it is not a kill, but the
  gate still does not raise on nonsense `nan`.)
- **Severity (honest):** moderate — a real reported effect estimate is never literally `+inf`/`nan`, but
  the gate's own `≤0` guard shows it *intends* validation, and it inconsistently admits non-finite values
  with a confident verdict. Note `assess_sensitivity` self-reports **κ=0.5** (guarded): the arithmetic
  E-value is κ=1 but the "robust" verdict depends on the κ=0 benchmark.
- **Required fix:** at the top of `assess_sensitivity`, reject non-finite estimates —
  `if not math.isfinite(estimate): raise ValueError`/return ABSTAIN — so the `>0` guard and the finite
  guard are consistent. **Freeze `+inf` (and `nan`) as a regression self-test (must ABSTAIN/ERROR, never
  a confident robust verdict).**

---

## 4. SURVIVED to budget — regime probed + residual risk (evidence, not proof)

> Each entry below is **`SURVIVED to budget`**, not "sound". The words "sound"/"proven" are deliberately
> avoided. A bug active *outside* the named regime is named residual risk, not a contradiction.

### trialguard_grim — full-differential — `SURVIVED_CONFIRMED`
- **Regime:** κ=1 GRIM exact-arithmetic slice **only** (not the Carlisle fraud heuristic). 53,322 unique
  objects: decimal precision D∈{0,1,2,3} × items∈{1,2,3} × n∈[3,40); achievable + deliberately-off means.
  Metamorphic: items-split (N_eff-invariant) over 25,953 even-n seeds, oracle-validated. Abstain/crash:
  n=0, n<0, n='garbage', items≤0, mean-as-float.
- **Residual risk:** no counterexample ≠ soundness proof (Dijkstra). **Not probed:** D≥4, items≥4, n≥40,
  non-decimal means — a FA/FR bug active only there would be missed. Metamorphic tested **one** transform
  class (items-split). The oracle shares the gate's mathematical *spec* (k/N_eff within half-ULP); a
  shared spec-level misunderstanding (e.g. both wrong about the rounding convention) would survive
  differential testing — only an *implementation* divergence is detectable. The powerless regime
  (N_eff≥10^D) is verified for agreement but not independently challenged.

### redcell_ctf — full-differential — `SURVIVED_CONFIRMED`
- **Regime:** the CTF-SOLVE κ=1 flag-equality slice of `verify_flag` (submitted/expected/
  expected_sha256/fmt) over benign synthetic `FLAG{…}` strings. 451 candidates (43 ACCEPT/408 REJECT):
  exact, single-char flips, length deltas, case folding, whitespace, prefix/suffix, hash path (incl.
  UPPER-case digest), format-wrapper path, empty/None, unicode. Metamorphic: 3 oracle-validated transforms.
  Abstain/crash: 5 malformed inputs. **Explicitly NOT** `auth_gate.authorize` — only flag equality.
- **Residual risk:** SURVIVED to budget, not a soundness proof. **Not probed:** adversarial unicode
  normalization (NFC/NFD/homoglyph collisions), non-string expected types, very large inputs, malformed
  fmt tuples, and the constant-time-vs-non-constant-time compare under timing side-channels (out of scope
  for an equality-correctness hunt). The authorization policy gate was deliberately not probed.

### frontier_capset — full-differential — `SURVIVED_CONFIRMED`
- **Regime:** FA stream 325 candidates (direct lines n=1..4, greedily-built injected-line near-caps
  corrupted with one line-completing point n=3..7 incl. the n=7 frontier cell, duplicate-point lines,
  ~300 random subsets n=2..4, size-mismatch claims). Oracle judged 210 WRONG → gate REJECTED all 210;
  115 CORRECT → all ACCEPTED. FR stream 125 (45-cap, 90-cap, persisted 236-cap n=7 frontier object, 120
  random maximal caps, empty, singleton). Metamorphic 96 (coord-permutation, translation, invertible
  affine relabel, lift to F₃^{n+1} — all cap-and-size-preserving F₃ symmetries, oracle-validated). Plus a
  2000-case cross-fuzz over random n=2..4 sets with **zero** gate-vs-oracle disagreements. Abstain/crash 9.
- **Residual risk:** confidence, not soundness proof. **Not probed:** n≥8, caps at/above the open n=7
  frontier beyond 236, exhaustive coverage of the astronomically larger C(3^n,k) space (this is sampling),
  transforms outside the affine group of F₃^n. The "cap of stated size" claim's size-half is checked by a
  thin distinct-count wrapper in the probe, not by `is_capset` (pure cap-ness); `capset_verify.score()`
  size logic was not differentially probed beyond size-mismatch controls.

### proofsmith_wrapper — metamorphic-only — `SURVIVED_CONFIRMED`
- **Regime:** PROOFSMITH wrapper **PRE-CHECK 0 only** — the pure-Python `_IO_COMMANDS` regex scan in
  `proof_gate.gate()` that REJECTs any bundle with a forbidden elaboration-time IO/meta command (#eval,
  #exit, run_cmd, initialize, unsafe, implemented_by, extern) **before any kernel call**. 6 IO-bearing
  seeds (all REJECT). Metamorphic: 5 reformatting transforms ×6 seeds = 30, all verdict-invariant.
  Abstain/crash: 6 malformed inputs, all → a safe verdict in {REJECT, ABSTAIN, ERROR}.
- **Residual risk:** SURVIVED on the wrapper IO-scan slice **only** — the **Lean kernel was deliberately
  never exercised** (tripwired to raise; 0 kernel calls occurred). (1) **No oracle:** the 5 metamorphic
  transforms are caller-asserted meaning-preserving. (2) The security-relevant question — can a forbidden
  command or a `sorry` be lexically **hidden** so the regex misses it while Lean still executes/admits it
  — is **not decidable without the kernel as oracle** and is untested. (3) `_SORRY_TOKENS`,
  `_parse_axioms` of real `#print axioms` output, comment-stripping, and CHECK 1/3/4 were not probed.
  (4) The regex bypass surface (Unicode/zero-width tricks, lookbehind mishandling) was not enumerated.
  **This is a coverage-bounded result, not a verdict on the verifier as a whole.**

### reproml_contamination — metamorphic-only — `SURVIVED_CONFIRMED`
- **Regime:** metamorphic invariance of the R-CONTAM binary verdict (NO_OVERLAP_DETECTED vs
  CONTAMINATION_DETECTED) under 3 caller-asserted transforms (whitespace+case norm, document reorder,
  train-side exact duplication), 6 seeds (2 clean + 4 dirty: verbatim n-gram, char-jaccard near-dup,
  word-reorder/bow), at n∈{5,13}, default jaccard=0.8, bow=0.9. Abstain/crash: 6 degenerate corpora.
- **Residual risk:** **THRESHOLD-DEPENDENCE (primary):** the verdict is a function of three **tunable free
  parameters** (n-gram order, char-5gram jaccard threshold, bow threshold). There is **no single exact
  ground truth** for "is this corpus contaminated", so no independent oracle exists without re-deriving
  the gate's own thresholded engine (circular). Therefore **no FA/FR hunt was run**, and metamorphic
  invariance is asserted **per gate configuration** — a different operator threshold is a different gate
  not exercised here. Caller-asserted transforms (A11 guard could not machine-validate). Two investigated
  **non-bugs honestly NOT shipped as kills:** (1) empty/degenerate eval → NO_OVERLAP_DETECTED carries the
  documented "≠ clean" ceiling note on every return (machine-confirmed `disclaimer_present=True`); (2)
  n=0 → universal collision over-flags (the conservative/fail-loud direction, not a silent unsafe ACCEPT).
  **Disclosed ceiling (not a bug):** rephrased/translated/paraphrased leakage evades n-gram + char-jaccard
  + token-set overlap; absence of detected overlap is never proof of cleanliness.

---

## 5. ABSTAINED / BLOCKED (coverage gaps) and DECLINED

- **ABSTAINED / BLOCKED: none.** No target was blocked by a missing dependency (e.g. Lean not installed,
  network required) in this run. **Note:** proofsmith's Lean-kernel path was *deliberately* not exercised
  (kernel tripwired) — that is a **scoped GAP**, not a pass, and is named in §4 as residual risk, not as
  an ABSTAINED_BLOCKED row.
- **DECLINED (1): econometrix_walkforward.** A guarded-κ verdict. CRUCIBLE declines κ=0 armor and
  guarded-κ verdicts on principle: you cannot adversarially falsify a judgment that never claimed to be an
  exact (κ=1) verifier. **This is a coverage exclusion by design, not evidence the gate is good.**

---

## 6. HONEST CEILING

- **A clean sweep upgrades a gate's κ=1 label from ASSERTED → ADVERSARIALLY-TESTED (to budget).** It does
  **not** prove soundness. Finding no counterexample under budget B is **evidence, not proof** (Dijkstra:
  *testing shows the presence of bugs, never their absence*). The words "sound"/"proven" are
  machine-banned from a survived report and are absent here. We never say "all 12 survived" — 4 were
  killed, 7 survived to budget, 1 declined.
- **Metamorphic-only targets carry a strictly weaker label.** With no independent oracle, **no false-accept
  hunt ran** for optima, proofsmith, reproml, symbolica (and the multiverse leg of socius). A gate that
  *wrongly certifies a wrong object* would not be caught by a metamorphic+abstain campaign — those probe
  verdict-instability and malformed-input robustness, not soundness. This is named, not hidden.
- **This run is HARDENING / EXPANSION, NOT a capability PROMOTION.** Adversarial search + an independent
  oracle is deterministic machine work; the value produced is **6 bug exhibits + honest confidence/
  residual-risk labels**, not a smarter generator. Per the promotion bar (≥10% better via a non-circular
  A/B + ablation across ≥2 arenas), nothing here clears that bar. **The capability ratchet stays OPEN at
  v3.**
- **Net effect of this run:** 4 owning weapons (factharness, optima, symbolica, socius) have **confirmed,
  reproduced gate bugs** that must be patched and frozen as regression self-tests (§3); 7 gates earned an
  ADVERSARIALLY-TESTED-to-budget label within their named regimes (§4); 1 is out of scope by design (§5).
  Until the §3 patches land + their exhibits are frozen, those four weapons' gates carry **known
  defects**, not merely untested ones.

---

## 7. PATCHES LANDED (2026-06-20, same session — all machine-verified + cross-model audited)

All four §3 KILLs were **patched and frozen as permanent regression self-tests**, each cross-model audited
(Sonnet ≠ the Opus patcher) and **independently re-run by the orchestrator** (agent self-reports not trusted).

| Weapon | Fix | Exhibit frozen as regression | Audit |
|---|---|---|---|
| **factharness** | `_norm_quote` NFKD→NFC (no compatibility-folding of `²`→`2`); type-guard non-str `source_text`→abstain | `m2`≠`m²` REJECT; list-source ABSTAIN; +`naïve` accent-fold preserved (52 assertions) | `PATCH_GOOD`, no new hole |
| **optima** | `_verify_lp_dual` folds `objective.constant` into the bound; `certify` guards `status ∉ {OPTIMAL,FEASIBLE,INFEASIBLE}` | +1000 constant-shift pair both CERTIFY (+ sub-optimal still rejected); no-status/None/bogus REJECT | `PATCH_GOOD`, no new hole |
| **symbolica** | `_agree` abs-tol floor near machine-eps (not only `scale==0`) | rearranged `sin²+cos²−1==0` CERTIFIES **and** 4 false identities + small-scale disagreement STILL REJECT (soundness rail frozen) | `PATCH_GOOD`, no new hole |
| **socius** | guard non-finite **input** estimate/ci; **plus** guard non-finite **computed** rr / governing E-value (closes the auditor's pre-existing overflow false-accept: `smd 500`→`e_value=inf`→`robust=True`) | `inf`/`nan` raise; `smd 500` & `rr 1e200` finite-overflow raise; valid finite estimates unchanged | `PATCH_GOOD`; overflow follow-up closed inline |

Plus: removed dead double-assigned `k_min` line in `oracles/grim_oracle.py` (auditor-confirmed non-circular).

---

## 8. CRUCIBLE-v2 — DIFFERENTIAL false-accept hunt on the metamorphic-only gates (2026-06-21)

The original run ran **metamorphic-only** on optima/proofsmith/reproml/symbolica (no independent oracle → no
false-accept hunt). CRUCIBLE-v2 builds genuinely-foreign oracles to add **differential** coverage.

**optima — KILL found + patched.** Independent oracle = `scipy.linprog` (SIMPLEX on the LP relaxation, a rigorous
bound on the integer optimum — a different algorithm than optima's enumeration; `scipy.milp`/HiGHS was tried but
SIGBUS-crashes on some `==`-constraint models, so linprog is used). Hunt: `crucible/runs/probe_v2_optima.py`,
4000 seeded random integer programs, 6696 gate probes.
- **THE KILL (κ=1 false-accept):** the `independent` optimality-certificate type certified **a SUBOPTIMAL feasible
  point as OPTIMAL**. It verified only that the witness *achieves* the claimed value (a lower bound) and then
  **trusted the caller's claim** that the value was the optimum. Minimal exhibit: `max x` s.t. `0≤x≤5` (true
  optimum 5) — claiming `x=3` optimal via `{"type":"independent","value":3,"witness":{"x":3}}` returned
  `OPTIMAL_CERTIFIED`, even labeled `independence: FULL`. (The original CRUCIBLE run had *declined* optima's
  false-accept hunt for lack of an independent oracle — so this hole was invisible to the metamorphic-only pass.)
- **THE FIX:** the `independent` branch now **enumerates the feasible space to CONFIRM** the claimed value is truly
  optimal (achievability alone is only a bound); if the space is too large to enumerate, it **declines to certify
  optimal** (reports a bound; supply lp_dual/exhaustive instead). Frozen as selftest regression **(g')**.
- **Re-verified:** exhibit now `FEASIBLE_WITH_GAP`; true optimum still `OPTIMAL_CERTIFIED`; selftest green; the
  4000-model hunt now **SURVIVED (0 kills)** — optima's optimality gate is upgraded from *metamorphic-only* to
  **adversarially differential-tested** on the `exhaustive`/`independent` paths.
- **CROSS-MODEL AUDIT: FIX_GOOD** (Sonnet ≠ Opus) — re-ran the repro/selftest/hunt + 29 of its own adversarial
  probes: bug confirmed real (the achievability check was circular — a suboptimal point self-witnesses its own
  value), fix correct + minimal (only the `independent` branch touched; lp_dual/exhaustive byte-identical), no
  new hole (false-reject-clean, large-space declines gracefully, no crash).
- **SECOND fix (the audit's own finding): `solver_bound_gap0` label-soundness.** The auditor noted that tier
  emits `OPTIMAL_CERTIFIED` on the solver's UNVERIFIED `best_bound` (a lying `best_bound==objective` certifies a
  suboptimum as proven — same false-accept class). **Demoted** to a distinct verdict `OPTIMAL_SOLVER_ASSERTED` so
  `OPTIMAL_CERTIFIED` now strictly means PROVEN (exhaustive / lp_dual / enumeration-confirmed independent). Frozen
  as regression `(g'')`; selftest green; hunt still SURVIVES. Still hardening, NOT a promotion; ratchet OPEN at v3.

**reproml — SURVIVED (no bug; differential coverage added).** Independent oracle = **substring-search collision**
on the joined token stream (a different mechanism than reproml's n-gram set-intersection; shares only the
tokenizer). Hunt: `crucible/runs/probe_v2_reproml.py`, 4000 rounds / **14,064 eval docs (3,834 truly dirty)**,
fuzzy thresholds disabled to isolate the exact leg. reproml's n-gram detector **agreed with the oracle on every
doc** → the exact verbatim-collision leg is now **differential-tested** (was metamorphic-only). Honest scope: ONLY
the exact n-gram leg; the threshold-dependent char-Jaccard/BOW legs + the paraphrase-evasion ceiling are NOT
covered (no exact oracle, by design).

**symbolica — SURVIVED (no false-accept).** Independent oracle = random-point high-precision identity refutation
(Schwartz–Zippel style, a different mechanism than symbolica's multi-method agreement). Curated adversarial set
targeting its prior-bug class (branch cuts / domain-restriction / near-equal): **0 false-accepts** — it correctly
CERTIFIED 6 true identities and REJECTED all 4 tricky false ones (`sqrt(x²)==x`, `Abs(x)==x`, the domain-restricted
`log(x²)==2log(x)`, `sin(x)==x`, a `1e-9` offset). The one oracle-mismatch was the *oracle* being too lenient
(skipping complex points); symbolica's reject was the more-correct verdict.

**CRUCIBLE-v2 net:** **optima → 1 real false-accept KILL + a 2nd label-soundness fix (both patched, frozen,
audit FIX_GOOD)**; **reproml → survived** (n-gram leg, 14k docs); **symbolica → survived** (branch-cut class).
proofsmith remains the one untestable here (needs the Lean kernel as the oracle; lean not on PATH).

**Final machine gate (orchestrator re-run):** `factharness · optima · symbolica · socius · crucible` selftests
= **5 green / 0 red**. The 7 SURVIVED-to-budget labels and the §6 honest ceiling are unchanged. **This whole
arc is HARDENING/EXPANSION, not a ≥10% promotion — the capability ratchet stays OPEN at v3.** Residual risk
unchanged: metamorphic-only weapons (optima, proofsmith, reproml, symbolica + socius multiverse leg) ran **no
false-accept hunt**, and proofsmith's **Lean kernel path was never exercised** — named gaps, not passes.
