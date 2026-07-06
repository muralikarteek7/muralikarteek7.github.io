#!/usr/bin/env python3
"""Faithful Python reproduction of Steegen et al. (2016) multiverse, Study 1
(religiosity) of Durante et al. (2013). Reimplements the data-processing grid
from the authors' own R script (steegen2016_multiverse.R, OSF zj68b) and the
focal statistic: p-value of the Fertility x RelationshipStatus interaction in
OLS(RelComp ~ Fertility * RelationshipStatus).

Grid (Study 1): NMO(2) x Fertility(5) x Relationship(3) x ExclCycleLen(3) x
ExclCertainty(2) = 180 cells; two NMO x exclusion combos are incompatible and
set NA (60 cells) -> 120 valid specifications. Published verdict: 7/120 sig.
"""
import numpy as np
import pandas as pd
from datetime import datetime
import statsmodels.formula.api as smf
import itertools
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _date(s):
    s = str(s).strip()
    if s in ("NA", "", "nan"):
        return None
    return datetime.strptime(s, "%m/%d/%y")


def load_study1():
    df = pd.read_csv(os.path.join(HERE, "data", "durante_study1.txt"), sep="\t",
                     na_values=["NA"])
    df["RelComp"] = df[["Rel1", "Rel2", "Rel3"]].mean(axis=1).round(2)
    for c in ("DateTesting", "StartDateofLastPeriod", "StartDateofPeriodBeforeLast"):
        df[c] = df[c].map(_date)
    return df


# fertility boundary options (from the R script, lines 135-140)
HIGH_LO = [7, 6, 9, 8, 9];   HIGH_HI = [14, 14, 17, 14, 17]
LOW1_LO = [17, 17, 18, 1, 1]; LOW1_HI = [25, 27, 25, 7, 8]
LOW2_LO = [17, 17, 18, 15, 18]; LOW2_HI = [25, 27, 25, 28, 28]


def process(df, i, j, k, l, m):
    """Apply one specification (1-indexed choices, matching the R loops)."""
    d = df.copy()
    # ComputedCycleLength in days
    ccl = (d["StartDateofLastPeriod"] - d["StartDateofPeriodBeforeLast"]).map(
        lambda x: x.days if x is not None and pd.notna(x) else np.nan)
    d["ComputedCycleLength"] = ccl
    # next menstrual onset
    if i == 1:
        nmo = [slp + pd.Timedelta(days=c) if (slp is not None and pd.notna(c)) else None
               for slp, c in zip(d["StartDateofLastPeriod"], ccl)]
    else:  # i == 2: reported cycle length
        nmo = [slp + pd.Timedelta(days=rc) if (slp is not None and pd.notna(rc)) else None
               for slp, rc in zip(d["StartDateofLastPeriod"], d["ReportedCycleLength"])]
    days_before = [(n - dt).days if (n is not None and dt is not None) else np.nan
                   for n, dt in zip(nmo, d["DateTesting"])]
    cycle_day = np.array([28 - x if not np.isnan(x) else np.nan for x in days_before])
    cycle_day = np.where(cycle_day < 1, 1, cycle_day)
    cycle_day = np.where(cycle_day > 28, 28, cycle_day)
    d["CycleDay"] = cycle_day
    # fertility (j is 1-indexed)
    jj = j - 1
    fert = np.array([None] * len(d), dtype=object)
    cd = d["CycleDay"].values
    with np.errstate(invalid="ignore"):
        fert[(cd >= HIGH_LO[jj]) & (cd <= HIGH_HI[jj])] = "High"
        fert[(cd >= LOW1_LO[jj]) & (cd <= LOW1_HI[jj])] = "Low"
        fert[(cd >= LOW2_LO[jj]) & (cd <= LOW2_HI[jj])] = "Low"
    d["Fertility"] = fert
    # relationship status (k)
    rel = d["Relationship"].values
    rs = np.array([None] * len(d), dtype=object)
    if k == 1:
        rs = np.where(rel <= 2, "Single", "Relationship")
    elif k == 2:
        rs = np.where(rel == 1, "Single", "Relationship")
    elif k == 3:
        rs = np.array([None] * len(d), dtype=object)
        rs[rel == 1] = "Single"
        rs[(rel > 2) & (rel < 5)] = "Relationship"   # rel==2 stays None
    d["RelationshipStatus"] = rs
    # exclusion by cycle length (l)
    if l == 2:
        d = d[~((d["ComputedCycleLength"] < 25) | (d["ComputedCycleLength"] > 35))]
    elif l == 3:
        d = d[~((d["ReportedCycleLength"] < 25) | (d["ReportedCycleLength"] > 35))]
    # exclusion by certainty (m)
    if m == 2:
        d = d[~((d["Sure1"] < 6) | (d["Sure2"] < 6))]
    return d


def fit_interaction_p(d):
    """OLS(RelComp ~ Fertility*RelationshipStatus); return p of the interaction."""
    dd = d.dropna(subset=["RelComp", "Fertility", "RelationshipStatus"]).copy()
    # need both levels present in both factors
    if dd["Fertility"].nunique() < 2 or dd["RelationshipStatus"].nunique() < 2:
        return np.nan, np.nan
    try:
        res = smf.ols("RelComp ~ C(Fertility)*C(RelationshipStatus)", data=dd).fit()
    except Exception:
        return np.nan, np.nan
    # the interaction term is the 4th coefficient (matches R's coefficients[4,4])
    inter = [name for name in res.params.index if ":" in name]
    if not inter:
        return np.nan, np.nan
    name = inter[0]
    return float(res.pvalues[name]), float(res.params[name])


def run_multiverse_study1():
    df = load_study1()
    pvals, coefs, specs = [], [], []
    for i, j, k, l, m in itertools.product(range(1, 3), range(1, 6), range(1, 4),
                                           range(1, 4), range(1, 3)):
        # incompatibility rules (R lines 215-216):
        #  nmo1(computed) with ecl3(reported)  -> NA
        #  nmo2(reported) with ecl2(computed)  -> NA
        if (i == 1 and l == 3) or (i == 2 and l == 2):
            continue
        d = process(df, i, j, k, l, m)
        p, b = fit_interaction_p(d)
        if not np.isnan(p):
            pvals.append(p); coefs.append(b)
            specs.append({"nmo": i, "f": j, "r": k, "ecl": l, "ec": m})
    pvals = np.array(pvals); coefs = np.array(coefs)
    n = len(pvals)
    n_sig = int(np.sum(pvals < 0.05))
    return {
        "n_specifications": n,
        "n_significant": n_sig,
        "share_significant": n_sig / n if n else 0.0,
        "median_p": float(np.median(pvals)) if n else None,
        "p_values": pvals.tolist(),
        "coefs": coefs.tolist(),
        "specs": specs,
    }


if __name__ == "__main__":
    import json
    out = run_multiverse_study1()
    print(f"specifications: {out['n_specifications']}")
    print(f"significant (p<.05): {out['n_significant']}  "
          f"({out['share_significant']:.1%})")
    print(f"median p across the multiverse: {out['median_p']:.3f}")
