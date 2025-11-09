# SPDX-License-Identifier: MIT
"""
Chapter 12 — Regression Diagnostics & Influence (R → Python)

Examples:
  python scripts/ch12_diagnostics.py --save-plots
  python scripts/ch12_diagnostics.py --formula "mpg ~ weight + model_year + C(cylinders) + horsepower" --save-plots --top-n 10
"""
import argparse, os, math
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import OLSInfluence, variance_inflation_factor
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load_autompg(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=None, engine="python")
    # canonicalize names
    ren = {}
    for want, opts in {
        "mpg": ["mpg"],
        "cylinders": ["cyl","cylinders"],
        "displacement": ["disp","displacement"],
        "horsepower": ["hp","horsepower"],
        "weight": ["wt","weight"],
        "acceleration": ["acc","acceleration"],
        "model_year": ["year","model_year"],
        "origin": ["origin"],
    }.items():
        for o in opts:
            if o in df.columns:
                ren[o] = want; break
    df = df.rename(columns=ren)
    need = ["mpg","cylinders","displacement","horsepower","weight","acceleration","model_year"]
    if not set(need).issubset(df.columns):
        raise SystemExit(f"ERROR: missing columns; have {list(df.columns)}")
    df = df.dropna()
    df["cylinders"] = df["cylinders"].astype("category")
    if "origin" in df.columns: df["origin"] = df["origin"].astype("category")
    return df

def default_formula(df: pd.DataFrame) -> str:
    base = "mpg ~ weight + model_year + C(cylinders) + horsepower"
    if "origin" in df.columns:
        base += " + C(origin)"
    return base

def plot_resid_vs_fitted(fitted, resid, out):
    plt.figure(figsize=(6,5))
    plt.scatter(fitted, resid, s=12, alpha=0.7)
    plt.axhline(0, color="k", lw=1)
    plt.xlabel("Fitted")
    plt.ylabel("Residuals")
    plt.title("Residuals vs Fitted")
    plt.tight_layout(); plt.savefig(out, dpi=150)

def plot_qq(resid, out):
    plt.figure(figsize=(6,5))
    sm.ProbPlot(resid).qqplot(line="45", alpha=0.7)
    plt.title("Normal Q-Q"); plt.tight_layout(); plt.savefig(out, dpi=150)

def plot_scale_location(fitted, resid, out):
    sr = np.sqrt(np.abs(resid))
    plt.figure(figsize=(6,5))
    plt.scatter(fitted, sr, s=12, alpha=0.7)
    plt.xlabel("Fitted"); plt.ylabel("√|Residuals|")
    plt.title("Scale-Location"); plt.tight_layout(); plt.savefig(out, dpi=150)

def plot_leverage_resid2(hat, studres, cooks, out):
    plt.figure(figsize=(6,5))
    sz = 60 * (cooks / (cooks.max() + 1e-9)) + 10
    plt.scatter(hat, studres, s=sz, alpha=0.6)
    plt.xlabel("Leverage (hat)")
    plt.ylabel("Studentized Residuals")
    plt.title("Residuals vs Leverage (size ~ Cook's D)")
    plt.tight_layout(); plt.savefig(out, dpi=150)

def compute_vif(model) -> pd.DataFrame:
    X = model.model.exog
    cols = model.model.exog_names
    # Intercept inflates VIF; skip it if present
    start = 1 if cols[0] == "Intercept" else 0
    data = []
    for i in range(start, X.shape[1]):
        data.append({"term": cols[i], "VIF": variance_inflation_factor(X, i)})
    return pd.DataFrame(data).sort_values("VIF", ascending=False).reset_index(drop=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/autompg.csv")
    ap.add_argument("--formula", default="")
    ap.add_argument("--save-plots", action="store_true")
    ap.add_argument("--top-n", type=int, default=5, help="Top N influential rows to print")
    args = ap.parse_args()

    os.makedirs("outputs", exist_ok=True)
    df = load_autompg(args.data)
    formula = args.formula or default_formula(df)
    print("=== Formula ==="); print(formula)

    model = smf.ols(formula, data=df).fit()
    print("\n=== Fit Stats ===")
    print(f"R^2={model.rsquared:.4f}  AdjR^2={model.rsquared_adj:.4f}  AIC={model.aic:.3f}  BIC={model.bic:.3f}")

    infl = OLSInfluence(model)
    resid = model.resid
    fitted = model.fittedvalues
    studres = infl.resid_studentized_external
    hat = infl.hat_matrix_diag
    cooks = infl.cooks_distance[0]

    print("\n=== Top Influential (by Cook's D) ===")
    top = np.argsort(cooks)[::-1][:args.top_n]
    for idx in top:
        print(f"row={idx}  CookD={cooks[idx]:.4g}  hat={hat[idx]:.4g}  studres={studres[idx]:.3g}")

    print("\n=== VIF ===")
    print(compute_vif(model).to_string(index=False))

    if args.save_plots:
        plot_resid_vs_fitted(fitted, resid, "outputs/ch12_resid_vs_fitted.png")
        plot_qq(resid, "outputs/ch12_qq.png")
        plot_scale_location(fitted, resid, "outputs/ch12_scale_location.png")
        plot_leverage_resid2(hat, studres, cooks, "outputs/ch12_leverage_resid2.png")
        print("Saved plots -> outputs/ch12_resid_vs_fitted.png, ch12_qq.png, ch12_scale_location.png, ch12_leverage_resid2.png")

if __name__ == "__main__":
    main()