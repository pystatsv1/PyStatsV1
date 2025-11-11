# SPDX-License-Identifier: MIT
"""
Chapter 9 — Multiple Linear Regression (auto-mpg)
- Loads data/autompg.csv
- Cleans common UCI quirks ('?' in horsepower), coerces types
- OLS via statsmodels using a formula (categoricals handled with C())
- Prints SPSS-style tables; saves residual plot + QQ plot + text summary
- Headless: works from the command line
"""
import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.graphics.gofplots import qqplot

def load_data(path):
    df = pd.read_csv(path)
    # Common quirks for UCI auto-mpg:
    if "horsepower" in df.columns:
        df["horsepower"] = pd.to_numeric(df["horsepower"], errors="coerce")
    for col in ["cylinders","displacement","weight","acceleration","model_year","origin","mpg"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["mpg","cylinders","displacement","horsepower","weight",
                           "acceleration","model_year","origin"])
    return df

def fit_model(df):
    # Treat origin and cylinders as categorical (like SPSS/R factor)
    formula = "mpg ~ displacement + horsepower + weight + acceleration + model_year + C(origin) + C(cylinders)"
    model = smf.ols(formula, data=df).fit()
    return model

def print_spss_style(model):
    print("=== OLS Coefficients ===")
    coefs = model.params
    ses   = model.bse
    tvals = model.tvalues
    pvals = model.pvalues
    for name in coefs.index:
        print(f"{name:15s}  est={coefs[name]:9.4f}  SE={ses[name]:8.4f}  t={tvals[name]:8.3f}  p={pvals[name]:.6g}")
    print()
    print("=== Model Fit ===")
    print(f"R^2       : {model.rsquared:.6f}")
    print(f"Adj R^2   : {model.rsquared_adj:.6f}")
    print(f"Sigma (SE): {np.sqrt(model.scale):.6f}")
    print()
    anova = sm.stats.anova_lm(model, typ=1)
    print("=== ANOVA (Type I) ===")
    print(anova)

def save_outputs(model, df, outdir="outputs"):
    os.makedirs(outdir, exist_ok=True)
    # Residuals vs Fitted
    fitted = model.fittedvalues
    resid  = model.resid
    plt.figure()
    plt.scatter(fitted, resid, s=20)
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.xlabel("Fitted values") 
    plt.ylabel("Residuals")
    plt.title("Residuals vs Fitted")
    plt.savefig(os.path.join(outdir, "ch09_resid_vs_fitted.png"), dpi=130, bbox_inches="tight")

    # QQ plot
    plt.figure()
    qqplot(resid, line="45")
    plt.title("QQ Plot of Residuals")
    plt.savefig(os.path.join(outdir, "ch09_qq.png"), dpi=130, bbox_inches="tight")

    # Summary text
    with open(os.path.join(outdir, "ch09_summary.txt"), "w", encoding="utf-8") as f:
        f.write(model.summary().as_text())

def partial_f_test(full, reduced):
    # Compare nested models: F = ((SSE_R - SSE_F) / (df_R - df_F)) / (SSE_F / df_F)
    sse_f, df_f = np.sum(full.resid**2), full.df_resid
    sse_r, df_r = np.sum(reduced.resid**2), reduced.df_resid
    num = (sse_r - sse_f) / (df_r - df_f)
    den = sse_f / df_f
    F   = num / den
    from scipy.stats import f
    p   = 1 - f.cdf(F, df_r - df_f, df_f)
    return F, p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/autompg.csv")
    ap.add_argument("--save-outputs", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.data):
        print(f"ERROR: {args.data} not found. Place autompg.csv in data/", file=sys.stderr)
        sys.exit(1)

    df = load_data(args.data)
    model_full = fit_model(df)
    print_spss_style(model_full)

    # Example nested test: drop 'acceleration'
    reduced = smf.ols("mpg ~ displacement + horsepower + weight + model_year + C(origin) + C(cylinders)", data=df).fit()
    F, p = partial_f_test(model_full, reduced)
    print()
    print("=== Partial F-test: drop acceleration ===")
    print(f"F = {F:.3f}, p = {p:.6g}")

    if args.save_outputs:
        save_outputs(model_full, df)

if __name__ == "__main__":
    main()

