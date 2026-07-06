#!/usr/bin/env python3
"""REPRO-ML killer demo. Real sklearn `digits` benchmark + controlled contamination
and significance cases. Predictions committed in PREDICTION.md BEFORE this ran.
Headline: R-CONTAM catches injected eval->train leakage as a measured rate.
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contam_verify import contamination_report
from signif_verify import compare
from repro_verify import reproduce, accuracy
from reproml_router import route

from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

results = {}
fails = []
def check(name, got, pred):
    match = got == pred
    if not match:
        fails.append(name)
    print(f"[{name}] predicted={pred} got={got} {'OK' if match else '** MISMATCH **'}")
    results[name] = {"predicted": pred, "got": got}

# --- real open benchmark: sklearn digits, two real classifiers ----------- #
X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0)
lr = LogisticRegression(max_iter=5000).fit(Xtr, ytr)
dt = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr)
lr_pred, dt_pred = lr.predict(Xte), dt.predict(Xte)
lr_acc, dt_acc = accuracy(lr_pred, yte), accuracy(dt_pred, yte)
print(f"\nReal digits test accuracies: LogReg={lr_acc:.4f}  DT(depth3)={dt_acc:.4f}\n")

# 1 R-REPRO: both reported accuracies recompute
check("1_repro_lr", reproduce(lr_acc, lr_pred, yte, "accuracy")["verdict"], "REPRODUCED")
check("1_repro_dt", reproduce(dt_acc, dt_pred, yte, "accuracy")["verdict"], "REPRODUCED")
# 2 R-REPRO negative: inflated number does not reproduce
check("2_repro_inflated", reproduce(lr_acc + 0.10, lr_pred, yte, "accuracy")["verdict"],
      "DOES_NOT_REPRODUCE")

# 3/4 R-CONTAM: clean vs leaked train corpus (the headline)
eval_text = [
    "the mitochondria is the powerhouse of the cell producing atp through respiration always",
    "photosynthesis converts carbon dioxide and water into glucose using sunlight in chloroplasts",
    "newtons second law states that force equals mass times acceleration in classical mechanics",
    "the french revolution began in seventeen eighty nine with the storming of the bastille",
    "supply and demand determine the equilibrium price in a competitive free market economy",
    "dna is composed of four nucleotide bases adenine thymine guanine and cytosine paired up",
]
train_clean = [
    "a recipe for sourdough bread requires flour water salt and a living wild yeast starter",
    "the weather forecast predicts heavy rain and strong winds across the coastal regions tomorrow",
]
train_leaked = train_clean + [eval_text[0], eval_text[2], eval_text[5]]   # inject 3 of 6
clean = contamination_report(train_clean, eval_text, n=13)
leaked = contamination_report(train_leaked, eval_text, n=13)
check("3_contam_clean", clean["verdict"], "NO_OVERLAP_DETECTED")
check("3_contam_clean_rate", clean["contamination_rate"], 0.0)
check("4_contam_leaked", leaked["verdict"], "CONTAMINATION_DETECTED")
check("4_contam_leaked_rate", leaked["contamination_rate"], 0.5)

# 5 R-SIGNIF: real LogReg-vs-DT gap on the same test set
lr_correct = (lr_pred == yte).astype(int)
dt_correct = (dt_pred == yte).astype(int)
sig_real = compare(lr_correct, dt_correct, name_a="LogReg", name_b="DT_depth3")
check("5_signif_real_gap", sig_real["verdict"], "SIGNIFICANT_DIFFERENCE")
print(f"    real gap: obs_diff={sig_real['bootstrap_ci']['obs_diff']} "
      f"CI=[{sig_real['bootstrap_ci']['ci_lower']},{sig_real['bootstrap_ci']['ci_upper']}] "
      f"McNemar p={sig_real['mcnemar']['p_value']:.2e}")

# 6 R-SIGNIF noise floor: controlled ~0.6pp gap on N=500
rng = np.random.default_rng(3)
base = rng.random(500) < 0.83
a = base.copy(); b = base.copy()
f = rng.choice(500, 3, replace=False); b[f] = ~b[f]
check("6_signif_noise", compare(a, b)["verdict"], "NOT_SIGNIFICANT")

# 7 kappa=0 residue: "LogReg is best / production-ready" -> armor, not crowned
r = route({"claims_best_or_sota_or_capable": True})
check("7_sota_to_armor", (r["routes_to_armor"] and r["fires_weapons"] == []), True)

allok = len(fails) == 0
out = {"real_accuracies": {"logreg": round(lr_acc, 4), "dt_depth3": round(dt_acc, 4)},
       "results": results, "all_predictions_matched": allok,
       "contam_headline": {"clean_rate": clean["contamination_rate"],
                           "leaked_rate": leaked["contamination_rate"],
                           "method": leaked["method"]}}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"), "w"),
          indent=2)
print("\n" + ("DEMO PASS: all predictions matched. Headline: contamination rate 0.0 -> 0.5 "
              "when 3/6 eval items leaked into train." if allok
              else f"DEMO MISMATCH: {fails}"))
sys.exit(0 if allok else 1)
