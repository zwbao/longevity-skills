"""Reference model of how routine labs change with age, fitted on public NHANES 2011-2018 (adults, not pregnant).

For each sex and each analyte: the mean and the SD of the (transformed) value at every age 18..80, and the
correlation of the residuals between analytes. With it, the age that best explains a person's values is found by a
Gaussian likelihood over the analytes the person has (any subset), giving a point estimate and an interval.

Train: 2011-2012 (G), 2013-2014 (H), 2015-2016 (I). Held out: 2017-2018 (J).
usage: python3 fit_age_model.py            -> writes model.json and validation.json next to this file
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent  # put the NHANES .XPT files in HERE/raw (see data/reference/README.md)
RAW = HERE / "raw"
AGES = np.arange(18, 81)  # NHANES codes 80 and over as 80

# analyte -> (file, column, canonical unit, transform)
FEATURES = {
    "albumin": ("BIOPRO", "LBDSALSI", "g/L", "none"),
    "alkaline_phosphatase": ("BIOPRO", "LBXSAPSI", "U/L", "log"),
    "urea": ("BIOPRO", "LBXSBU", "mg/dL (BUN)", "log"),
    "creatinine": ("BIOPRO", "LBDSCRSI", "umol/L", "log"),
    "glucose": ("BIOPRO", "LBDSGLSI", "mmol/L", "log"),
    "total_bilirubin": ("BIOPRO", "LBDSTBSI", "umol/L", "log"),
    "uric_acid": ("BIOPRO", "LBDSUASI", "umol/L", "none"),
    "total_cholesterol": ("BIOPRO", "LBDSCHSI", "mmol/L", "log"),
    "triglycerides": ("BIOPRO", "LBDSTRSI", "mmol/L", "log"),
    "ast": ("BIOPRO", "LBXSASSI", "U/L", "log"),
    "alt": ("BIOPRO", "LBXSATSI", "U/L", "log"),
    "ggt": ("BIOPRO", "LBXSGTSI", "U/L", "log"),
    "ldh": ("BIOPRO", "LBXSLDSI", "U/L", "log"),
    "total_protein": ("BIOPRO", "LBDSTPSI", "g/L", "none"),
    "globulin": ("BIOPRO", "LBDSGBSI", "g/L", "none"),
    "sodium": ("BIOPRO", "LBXSNASI", "mmol/L", "none"),
    "potassium": ("BIOPRO", "LBXSKSI", "mmol/L", "none"),
    "chloride": ("BIOPRO", "LBXSCLSI", "mmol/L", "none"),
    "calcium": ("BIOPRO", "LBDSCASI", "mmol/L", "none"),
    "phosphorus": ("BIOPRO", "LBDSPHSI", "mmol/L", "none"),
    "bicarbonate": ("BIOPRO", "LBXSC3SI", "mmol/L", "none"),
    "wbc": ("CBC", "LBXWBCSI", "10^9/L", "log"),
    "lymphocyte_pct": ("CBC", "LBXLYPCT", "%", "none"),
    "monocyte_pct": ("CBC", "LBXMOPCT", "%", "none"),
    "neutrophil_pct": ("CBC", "LBXNEPCT", "%", "none"),
    "eosinophil_pct": ("CBC", "LBXEOPCT", "%", "log1p"),
    "basophil_pct": ("CBC", "LBXBAPCT", "%", "log1p"),
    "rbc": ("CBC", "LBXRBCSI", "10^12/L", "none"),
    "hemoglobin": ("CBC", "LBXHGB", "g/dL", "none"),
    "hematocrit": ("CBC", "LBXHCT", "%", "none"),
    "mcv": ("CBC", "LBXMCVSI", "fL", "none"),
    "mch": ("CBC", "LBXMCHSI", "pg", "none"),
    "mchc": ("CBC", "LBXMC", "g/dL", "none"),
    "rdw": ("CBC", "LBXRDW", "%", "log"),
    "platelets": ("CBC", "LBXPLTSI", "10^9/L", "log"),
    "hba1c": ("GHB", "LBXGH", "%", "log"),
    "hdl": ("HDL", "LBDHDDSI", "mmol/L", "log"),
    "crp": ("HSCRP", "LBXHSCRP", "mg/L", "logcrp"),
    "bmi": ("BMX", "BMXBMI", "kg/m^2", "log"),
    "waist": ("BMX", "BMXWAIST", "cm", "none"),
    "height": ("BMX", "BMXHT", "cm", "none"),
    "weight": ("BMX", "BMXWT", "kg", "log"),
}
CYCLES_TRAIN = ["G", "H", "I"]
CYCLES_TEST = ["J"]


def transform(kind, x):
    x = np.asarray(x, dtype=float)
    if kind == "none":
        return x
    if kind == "log":
        return np.log(np.where(x > 0, x, np.nan))
    if kind == "log1p":
        return np.log1p(np.where(x >= 0, x, np.nan))
    if kind == "logcrp":
        return np.log(np.maximum(x, 0.1))
    raise ValueError(kind)


def load(cycles):
    frames = []
    for c in cycles:
        demo = pd.read_sas(RAW / f"DEMO_{c}.XPT")[["SEQN", "RIAGENDR", "RIDAGEYR", "RIDEXPRG"]]
        df = demo
        for f in sorted({v[0] for v in FEATURES.values()}):
            path = RAW / f"{f}_{c}.XPT"
            if not path.exists():
                continue
            cols = ["SEQN"] + [v[1] for v in FEATURES.values() if v[0] == f]
            part = pd.read_sas(path)
            part = part[[x for x in cols if x in part.columns]]
            df = df.merge(part, on="SEQN", how="left")
        df["cycle"] = c
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df = df[(df.RIDAGEYR >= 18) & (df.RIDEXPRG.fillna(2) != 1)]
    out = pd.DataFrame({"seqn": df.SEQN.values, "cycle": df.cycle.values,
                        "sex": np.where(df.RIAGENDR == 1, "male", "female"), "age": df.RIDAGEYR.values.astype(float)})
    for name, (_f, col, _u, kind) in FEATURES.items():
        out[name] = transform(kind, df[col].values) if col in df.columns else np.nan
    # at least five lab values, so the person had a blood draw
    labs = [k for k in FEATURES if k not in ("bmi", "waist", "height", "weight")]
    return out[out[labs].notna().sum(axis=1) >= 5].reset_index(drop=True)


def smooth_by_age(age, y, bandwidth=4.0):
    """Gaussian-kernel local-linear mean of y at every integer age in AGES."""
    ok = np.isfinite(y)
    age, y = age[ok], y[ok]
    out = np.empty(len(AGES))
    for i, a in enumerate(AGES):
        w = np.exp(-0.5 * ((age - a) / bandwidth) ** 2)
        X = np.column_stack([np.ones_like(age), age - a])
        WX = X * w[:, None]
        beta = np.linalg.lstsq(WX.T @ X + 1e-9 * np.eye(2), WX.T @ y, rcond=None)[0]
        out[i] = beta[0]
    return out


def fit(train):
    model = {}
    for sex in ("male", "female"):
        d = train[train.sex == sex]
        age = np.minimum(d.age.values, 80)
        mu, sd, n = {}, {}, {}
        resid = pd.DataFrame(index=d.index)
        for f in FEATURES:
            y = d[f].values
            if np.isfinite(y).sum() < 500:
                continue
            m = smooth_by_age(age, y)
            r = y - m[(age - 18).astype(int)]
            # robust scale per age: smoothed mean squared residual after trimming the top 1%
            cut = np.nanquantile(np.abs(r), 0.99)
            r2 = np.where(np.abs(r) <= cut, r ** 2, np.nan)
            s = np.sqrt(np.maximum(smooth_by_age(age, r2, bandwidth=6.0), 1e-12))
            mu[f], sd[f], n[f] = m, s, int(np.isfinite(y).sum())
            resid[f] = r / s[(age - 18).astype(int)]
        keys = list(mu)
        z = resid[keys].clip(-4, 4)
        corr = z.corr(min_periods=300).values
        corr = np.where(np.isfinite(corr), corr, 0.0)
        np.fill_diagonal(corr, 1.0)
        w, v = np.linalg.eigh(corr)  # nearest positive-definite correlation
        w = np.maximum(w, 0.02)
        corr = (v * w) @ v.T
        dd = np.sqrt(np.diag(corr))
        corr = corr / np.outer(dd, dd)
        model[sex] = {"features": keys, "n": n,
                      "mean": {f: [round(float(x), 6) for x in mu[f]] for f in keys},
                      "sd": {f: [round(float(x), 6) for x in sd[f]] for f in keys},
                      "corr": [[round(float(x), 5) for x in row] for row in corr]}
    return model


def predict(model, sex, values, shrink=1.0):
    """values: {feature: transformed value}. Returns posterior mean, 5th and 95th percentile, and the grid posterior."""
    m = model[sex]
    keys = [f for f in m["features"] if f in values and np.isfinite(values[f])]
    if not keys:
        return None
    idx = [m["features"].index(f) for f in keys]
    R = np.array(m["corr"])[np.ix_(idx, idx)]
    Rinv = np.linalg.inv(R)
    x = np.array([values[f] for f in keys])
    logp = np.empty(len(AGES))
    for i in range(len(AGES)):
        mu = np.array([m["mean"][f][i] for f in keys])
        sd = np.array([m["sd"][f][i] for f in keys])
        zz = np.clip((x - mu) / sd, -4, 4)
        logp[i] = shrink * (-0.5 * zz @ Rinv @ zz - np.log(sd).sum())
    p = np.exp(logp - logp.max())
    p /= p.sum()
    cdf = np.cumsum(p)
    return {"mean": float((AGES * p).sum()), "p05": float(AGES[np.searchsorted(cdf, 0.05)]),
            "p95": float(AGES[np.searchsorted(cdf, 0.95)]), "n_features": len(keys), "posterior": p}


def evaluate(model, test, feature_sets):
    out = {}
    for name, feats in feature_sets.items():
        errs, cover, preds, truth = [], [], [], []
        for _, row in test.iterrows():
            vals = {f: row[f] for f in feats if f in row and np.isfinite(row[f])}
            if len(vals) < max(3, len(feats) // 2):
                continue
            r = predict(model, row.sex, vals)
            if r is None:
                continue
            a = min(row.age, 80)
            errs.append(abs(r["mean"] - a))
            cover.append(r["p05"] <= a <= r["p95"])
            preds.append(r["mean"]); truth.append(a)
        if errs:
            out[name] = {"n": len(errs), "mae": round(float(np.mean(errs)), 2),
                         "median_ae": round(float(np.median(errs)), 2),
                         "r": round(float(np.corrcoef(preds, truth)[0, 1]), 3),
                         "coverage_90": round(float(np.mean(cover)), 3),
                         "mae_guess_mean": round(float(np.mean(np.abs(np.array(truth) - np.mean(truth)))), 2)}
    return out


def main():
    train, test = load(CYCLES_TRAIN), load(CYCLES_TEST)
    print("train", len(train), "test", len(test), flush=True)
    model = fit(train)
    lb_like = ["albumin", "alkaline_phosphatase", "urea", "creatinine", "glucose", "total_bilirubin", "uric_acid",
               "total_cholesterol", "hdl", "crp", "wbc", "rbc", "mcv", "rdw", "neutrophil_pct", "lymphocyte_pct",
               "monocyte_pct", "eosinophil_pct", "basophil_pct", "hba1c", "bmi"]
    phenoage9 = ["albumin", "alkaline_phosphatase", "creatinine", "glucose", "crp", "lymphocyte_pct", "mcv", "rdw", "wbc"]
    routine_cn = ["albumin", "alt", "ast", "ggt", "total_bilirubin", "creatinine", "urea", "uric_acid", "glucose",
                  "total_cholesterol", "triglycerides", "hdl", "wbc", "rbc", "hemoglobin", "platelets", "mcv", "rdw",
                  "lymphocyte_pct", "neutrophil_pct", "bmi"]
    sets = {"all": list(FEATURES), "longevitybench_like": lb_like, "phenoage_9": phenoage9, "routine_checkup_cn": routine_cn}
    val = evaluate(model, test, sets)
    print(json.dumps(val, indent=1))
    meta = {"name": "nhanes-age-reference", "fitted_on": "NHANES 2011-2012, 2013-2014, 2015-2016 (adults 18+, not pregnant)",
            "held_out": "NHANES 2017-2018", "ages": [int(AGES[0]), int(AGES[-1])], "age_top_code": "80 means 80 and over",
            "features": {k: {"unit": v[2], "transform": v[3], "nhanes": v[1]} for k, v in FEATURES.items()},
            "n_train": int(len(train)), "n_test": int(len(test)), "validation": val, "model": model}
    (HERE / "model.json").write_text(json.dumps(meta))
    (HERE / "validation.json").write_text(json.dumps(val, indent=1))
    print("wrote", HERE / "model.json", round((HERE / "model.json").stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
