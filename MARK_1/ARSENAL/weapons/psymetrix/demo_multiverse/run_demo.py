#!/usr/bin/env python3
"""P-REPRO + P-MULTIVERSE demo on REAL open data (Fair's Affairs, 1978).
Predictions committed in PREDICTION.md BEFORE this run. Run after selftest_all.py.

Certifies: (1) the focal religiousness->affair logit coefficient is REPRODUCED two
independent ways; (2) across the analytic multiverse the effect is ROBUST (sign-
stable + mostly significant) — the honest counterpoint to an effect that DIES.
Ceiling: robust != true/causal (observational data).
"""
import sys, os, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import statsmodels.api as sm
import repro_multiverse_verify as RM

d = sm.datasets.fair.load_pandas().data.copy()
d["any_affair"] = (d["affairs"] > 0).astype(int)            # any affair (rate > 0)
d["frequent_affair"] = (d["affairs"] >= 1.0).astype(int)   # frequent (rate >= 1/yr); a STRICTER
# DV, a subset of any_affair — a defensible alternative operationalization, not an identical one.

# ---- P-REPRO: reproduce the focal religiousness coefficient two independent ways ----
covs = ["rate_marriage", "age", "yrs_married", "children", "educ", "occupation"]
rep = RM.reproduce_coefficient(d, "any_affair", ["religious"] + covs, "religious",
                               family="logit")
rep_rate = RM.reproduce_coefficient(d, "any_affair", ["rate_marriage"] + ["religious", "age",
                                    "yrs_married", "children", "educ", "occupation"],
                                    "rate_marriage", family="logit")

# ---- P-MULTIVERSE: specification curve over defensible analytic forks ----
outcomes = {"any_affair": "any_affair", "frequent_affair": "frequent_affair"}
exclusions = {"full sample": (lambda x: np.ones(len(x), bool)),
              "married >1yr": (lambda x: x["yrs_married"].to_numpy() > 1.0)}
cov_pool = ["rate_marriage", "age", "yrs_married", "children", "educ", "occupation"]
mv = RM.specification_curve(d, "religious", outcomes, cov_pool, exclusions, family="logit")

print("=" * 74)
print("P-REPRO + P-MULTIVERSE demo — Fair's Affairs 1978 (real open data, n=6366)")
print("=" * 74)
print(f"  P-REPRO religious: statsmodels={rep['coef_statsmodels']}  "
      f"numpy-independent={rep['coef_numpy_independent']}  p={rep['p_value']:.2e}")
print(f"                     dual-path agree: {rep['dual_path_agree']}  -> {rep['reproduced']}")
print(f"  P-REPRO rate_marriage: coef={rep_rate['coef_statsmodels']} (control sanity check)")
print(f"  P-MULTIVERSE: {mv['n_specifications']} specs | median coef={mv['median_coef']} | "
      f"%sig={mv['pct_significant']} | %same-sign={mv['pct_same_sign_as_median']}")
print(f"                %sig-in-dominant-sign={mv['pct_significant_in_dominant_sign']} "
      f"-> VERDICT: {mv['robustness_verdict'].upper()}")
print(f"                effect-size spread: coef in [{mv['coef_min']}, {mv['coef_max']}], "
      f"std={mv['coef_std']}, CV={mv['coef_cv']}  (judge robustness by SIGN+SPREAD, not %sig at large n)")
print(f"                p-curve of significant specs: {mv['pcurve_evidential_value']} "
      f"({mv['pcurve_caveat']})")

checks = {
    "repro_dual_path_agrees": rep["dual_path_agree"] and rep["reproduced"],
    "repro_coef_in_band": -0.40 <= rep["coef_statsmodels"] <= -0.33,
    "multiverse_robust": mv["robustness_verdict"] == "robust",
    "sign_stable_95": mv["pct_same_sign_as_median"] >= 0.95,
    "median_in_band": -0.45 <= mv["median_coef"] <= -0.25,
    "rate_marriage_stronger": rep_rate["coef_statsmodels"] < rep["coef_statsmodels"],
}
print("=" * 74)
print("PREDICTION CHECK:")
labels = {
    "repro_dual_path_agrees": "P-REPRO: two independent paths agree (reproduced)",
    "repro_coef_in_band": "religious coef in predicted -0.37+-0.04 band",
    "multiverse_robust": "multiverse verdict = robust",
    "sign_stable_95": "effect negative in >=95% of specs",
    "median_in_band": "median coef in -0.25..-0.45 band",
    "rate_marriage_stronger": "rate_marriage a stronger predictor than religiousness (control)",
}
for k, v in checks.items():
    print(f"  [{'PASS' if v else 'MISS'}] {labels[k]}")

out = {"p_repro_religious": rep, "p_repro_rate_marriage": rep_rate,
       "p_multiverse": {k: v for k, v in mv.items() if k != "specs"},
       "n_specs": mv["n_specifications"], "checks": checks}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "RESULT.json"), "w"), indent=2)
print("\nHONEST CEILING: a 'robust' multiverse verdict means the effect is NOT an artifact")
print("of the analytic choices tested — it does NOT prove the effect is causal or true.")
print("This is observational survey data; religiousness is confounded with many factors.")
print("Robust != true. PSYMETRIX certifies robustness, not truth.")
print("wrote RESULT.json")
core = all(checks.values())
sys.exit(0 if core else 1)
