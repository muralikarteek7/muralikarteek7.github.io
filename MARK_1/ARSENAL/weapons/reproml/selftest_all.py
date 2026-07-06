#!/usr/bin/env python3
"""REPRO-ML gate self-tests. A gate that can't fail is not a gate.

The 4 mandatory tests (per kickoff):
  (a) PASS a faithfully-reproduced clean eval
  (b) CATCH a contaminated eval (inject test items into 'train')
  (c) CALL a noise-level gap insignificant (tiny gap, small N)
  (d) FLAG an unreproducible metric (predictions don't recompute)
Plus hardening tests on each verifier's soundness in both directions.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contam_verify import contamination_report
from signif_verify import compare, mcnemar
from repro_verify import reproduce, accuracy

n = 0
def ok(cond, msg):
    global n
    assert cond, "FAIL: " + msg
    n += 1

rng = np.random.default_rng(7)

# ---- (a) PASS a faithfully-reproduced CLEAN eval -------------------------- #
labels = rng.integers(0, 4, 300)
preds = labels.copy()
flip = rng.choice(300, 60, replace=False)        # 20% wrong -> acc 0.80
preds[flip] = (preds[flip] + 1) % 4
acc = accuracy(preds, labels)
rep = reproduce(acc, preds, labels, "accuracy")
ok(rep["reproduced"] is True and rep["verdict"] == "REPRODUCED", "(a) faithful metric reproduces")

eval_clean = ["alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi",
              "one two three four five six seven eight nine ten eleven twelve thirteen four"]
train_clean = ["entirely different vocabulary covering oceans mountains rivers and forests wide"]
cc = contamination_report(train_clean, eval_clean, n=13)
ok(cc["contaminated_items"] == 0 and cc["verdict"] == "NO_OVERLAP_DETECTED",
   "(a) clean eval shows no overlap")

# ---- (b) CATCH a contaminated eval --------------------------------------- #
train_dirty = train_clean + [eval_clean[0]]      # leaked eval item 0 into train
cd = contamination_report(train_dirty, eval_clean, n=13)
ok(cd["contaminated_items"] == 1 and cd["contamination_rate"] == 0.5
   and cd["verdict"] == "CONTAMINATION_DETECTED", "(b) contaminated eval is flagged with a rate")
# near-dup: a lightly-edited copy is still caught even without a 13-gram collision
train_neardup = train_clean + [eval_clean[1].replace("thirteen", "thirteenX")]
cn = contamination_report(train_neardup, [eval_clean[1]], n=13, jaccard_threshold=0.8)
ok(cn["contaminated_items"] == 1 and cn["by_near_dup"] == 1, "(b) near-dup leakage caught by Jaccard")

# ---- (c) CALL a noise-level gap INSIGNIFICANT ---------------------------- #
base = rng.random(400) < 0.82
a = base.copy(); b = base.copy()
f = rng.choice(400, 4, replace=False)            # ~1pp difference on N=400
b[f] = ~b[f]
csig = compare(a, b)
ok(csig["verdict"] == "NOT_SIGNIFICANT", "(c) tiny gap on small N -> NOT_SIGNIFICANT")

# ---- (d) FLAG an unreproducible metric ----------------------------------- #
bad = reproduce(0.97, preds, labels, "accuracy")   # over-claimed vs true 0.80
ok(bad["reproduced"] is False and bad["verdict"] == "DOES_NOT_REPRODUCE",
   "(d) inflated metric flagged as DOES_NOT_REPRODUCE")

# ---- HARDENING: significance soundness the OTHER way --------------------- #
# a genuinely large, consistent gap MUST be called significant (no false-negative)
ag = rng.random(400) < 0.92; bg = rng.random(400) < 0.62
ok(compare(ag, bg)["verdict"] == "SIGNIFICANT_DIFFERENCE", "H: real large gap IS significant")
# Bonferroni: comparing many models raises the bar -> a borderline gap can flip to NS
am = rng.random(300) < 0.80
bm = am.copy(); fm = rng.choice(300, 18, replace=False); bm[fm] = ~bm[fm]
single = compare(am, bm, n_comparisons=1)
multi = compare(am, bm, n_comparisons=20)
ok(multi["bonferroni_alpha"] < single["bonferroni_alpha"], "H: Bonferroni tightens alpha with k")

# McNemar uses only discordant pairs: identical predictions -> p=1.0 (no false signif)
ident = rng.random(200) < 0.75
ok(mcnemar(ident, ident.copy())["p_value"] == 1.0, "H: identical models -> p=1.0 (no false signif)")

# repro: macro_f1 path also recomputes
lf = np.array([0,0,1,1,2,2,0,1,2,0]); pf = lf.copy()
from repro_verify import macro_f1
ok(reproduce(macro_f1(pf, lf), pf, lf, "macro_f1")["reproduced"] is True, "H: macro_f1 reproduces")

# contam ceiling note is always present (NO_OVERLAP != clean)
ok("!= clean" in cc["ceiling_note"], "H: contam report states no-overlap != clean")

# ---- AUDIT REGRESSIONS (cross-model Sonnet audit, 2026-06-20) -------------- #
from signif_verify import paired_bootstrap_ci
from scipy import stats as _st
# A1b: p_value must be re-derivable from the reported chi2 within tight tol.
mc = mcnemar(np.array([1]*20 + [0]*1 + [1]*79), np.array([0]*20 + [1]*1 + [1]*79))
ok(abs(_st.chi2.sf(mc["chi2"], 1) - mc["p_value"]) < 1e-6,
   "A1b: p_value re-derives from reported chi2")
# A3: when the two tests disagree, the result must DISCLOSE it (tests_agree + note),
# and the verdict stays the conservative NOT_SIGNIFICANT.
disagree = None
for seed in range(200):
    rg = np.random.default_rng(seed)
    nn = int(rg.integers(120, 200))
    aa = rg.random(nn) < 0.5; bb = aa.copy()
    # craft a boundary one-sided edge
    flip = rg.choice(nn, int(nn * 0.08), replace=False); bb[flip] = ~bb[flip]
    res = compare(aa, bb)
    if not res["tests_agree"]:
        disagree = res; break
ok("tests_agree" in compare(a, b), "A3: result exposes tests_agree")
ok(compare(a, b)["ceiling_note"].count("CONSERVATIVE") >= 1, "A3: AND-logic conservatism documented")
if disagree is not None:
    ok(disagree["verdict"] == "NOT_SIGNIFICANT" and disagree["disagreement_note"] is not None,
       "A3: a disagreement is disclosed + resolved conservatively")
# A5: word-REORDERED leakage (same words, shuffled) is now caught by the token-set pass.
reorder = contamination_report(["kappa iota theta eta zeta epsilon delta gamma beta alpha now"],
                               ["alpha beta gamma delta epsilon zeta eta theta iota kappa now"], n=13)
ok(reorder["contaminated_items"] == 1 and reorder["by_word_reorder"] == 1,
   "A5: word-reordered leakage caught (order-insensitive token-set)")
ok("word-REORDERED" in reorder["ceiling_note"] and "rephrased" in reorder["ceiling_note"],
   "A5: ceiling note states what is caught vs still missed")
# A6: n<10 emits a false-positive-risk warning.
import warnings as _w
with _w.catch_warnings(record=True) as rec:
    _w.simplefilter("always")
    contamination_report(["the cat sat on the mat"], ["the cat sat on the fence"], n=5)
    ok(any("false positive" in str(x.message).lower() for x in rec), "A6: low-n warns of FP risk")
# A9b: a value exactly at true+tol must not be failed by float rounding.
lab = np.array([0,1,2]*50); pr = lab.copy()
true = accuracy(pr, lab)
ok(reproduce(true + 1e-3, pr, lab, "accuracy")["reproduced"] is True,
   "A9b: value exactly at true+tol still REPRODUCED (no FP boundary fail)")
ok(reproduce(true + 1e-2, pr, lab, "accuracy")["reproduced"] is False,
   "A9b: a clearly-inflated value still fails")

print(f"REPRO-ML selftest_all: PASS ({n} assertions) -- reproduces a clean metric; CATCHES "
      "contamination (n-gram + near-dup) as a labeled rate; calls a noise gap NOT_SIGNIFICANT and a "
      "real gap SIGNIFICANT; flags an unreproducible metric; Bonferroni tightens with k; no false "
      "significance on identical models.")
