# SPDX-License-Identifier: MIT
"""
Chapter 8 — Inference for Simple Linear Regression (R mirror, manual formulas)
- Uses the same embedded 'cars' dataset (speed, dist)
- Prints t-tests for slope/intercept, 95% CIs, ANOVA table
- Gives mean response CI and prediction interval at user x0 (default 20)
- Optional: saves CI/PI bands plot at outputs/ch08_slr_bands.png with --save-plot
"""
import argparse
import math
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

CARS = np.array([
    (4,2),(4,10),(7,4),(7,22),(8,16),(9,10),(10,18),(10,26),(10,34),(11,17),
    (11,28),(12,14),(12,20),(12,24),(12,28),(13,26),(13,34),(13,34),(13,46),(14,26),
    (14,36),(14,60),(14,80),(15,20),(15,26),(15,54),(16,32),(16,40),(17,32),(17,40),
    (17,50),(18,42),(18,56),(18,76),(18,84),(19,36),(19,46),(19,68),(20,32),(20,48),
    (20,52),(20,56),(20,64),(22,66),(23,54),(24,70),(24,92),(24,93),(24,120),(25,85),
], dtype=float)

def fit_slr(x, y):
    n     = len(x)
    xbar  = x.mean()
    ybar  = y.mean()
    Sxx   = np.sum((x - xbar)**2)
    Sxy   = np.sum((x - xbar)*(y - ybar))
    b1    = Sxy / Sxx
    b0    = ybar - b1*xbar
    yhat  = b0 + b1*x
    resid = y - yhat
    s2    = np.sum(resid**2) / (n - 2)
    sigma = math.sqrt(s2)
    SST   = np.sum((y - ybar)**2)
    SSR   = np.sum((yhat - ybar)**2)
    SSE   = np.sum(resid**2)
    R2    = SSR / SST
    return dict(n=n, xbar=xbar, ybar=ybar, Sxx=Sxx, b0=b0, b1=b1, yhat=yhat, resid=resid,
                s2=s2, sigma=sigma, SST=SST, SSR=SSR, SSE=SSE, R2=R2)

def inference(outputs, alpha=0.05, x0=20.0, save_plot=False):
    x, y = outputs["x"], outputs["y"]
    res  = outputs["fit"]
    n, Sxx, xbar = res["n"], res["Sxx"], res["xbar"]
    b0, b1, _, sigma = res["b0"], res["b1"], res["s2"], res["sigma"]
    df = n - 2
    tcrit = stats.t.ppf(1 - alpha/2, df)

    # Std errors
    se_b1 = sigma / math.sqrt(Sxx)
    se_b0 = sigma * math.sqrt(1/n + (xbar**2)/Sxx)

    # t-tests for coefficients (H0: beta=0)
    t_b1 = b1 / se_b1
    p_b1 = 2 * (1 - stats.t.cdf(abs(t_b1), df))
    t_b0 = b0 / se_b0
    p_b0 = 2 * (1 - stats.t.cdf(abs(t_b0), df))

    # 95% CIs
    ci_b1 = (b1 - tcrit*se_b1, b1 + tcrit*se_b1)
    ci_b0 = (b0 - tcrit*se_b0, b0 + tcrit*se_b0)

    # ANOVA table
    MSR = res["SSR"] / 1
    MSE = res["SSE"] / df
    F   = MSR / MSE
    p_F = 1 - stats.f.cdf(F, 1, df)

    # CI for mean at x0; PI for a new y at x0
    yhat0 = b0 + b1*x0
    se_mean = sigma * math.sqrt(1/n + (x0 - xbar)**2 / Sxx)
    se_pred = sigma * math.sqrt(1 + 1/n + (x0 - xbar)**2 / Sxx)
    ci_mean = (yhat0 - tcrit*se_mean, yhat0 + tcrit*se_mean)
    pi_new  = (yhat0 - tcrit*se_pred, yhat0 + tcrit*se_pred)

    # Print block (SPSS-style)
    print("=== Coefficient Inference (alpha={:.2f}) ===".format(alpha))
    print("Intercept:  est={:.6f}  SE={:.6f}  t({})={:.3f}  p={:.6g}  95% CI=({:.6f},{:.6f})"
          .format(b0, se_b0, df, t_b0, p_b0, ci_b0[0], ci_b0[1]))
    print("Slope:      est={:.6f}  SE={:.6f}  t({})={:.3f}  p={:.6g}  95% CI=({:.6f},{:.6f})"
          .format(b1, se_b1, df, t_b1, p_b1, ci_b1[0], ci_b1[1]))
    print()
    print("=== Model Fit ===")
    print("Residual SE (sigma): {:.5f}".format(sigma))
    print("R^2: {:.6f}".format(res["R2"]))
    print()
    print("=== ANOVA (Regression) ===")
    print("Source        DF       SS         MS         F        p")
    print("Regression     1  {:10.4f}  {:10.4f}  {:8.3f}  {:.6g}".format(res["SSR"], MSR, F, p_F))
    print("Error        {:>3}  {:10.4f}  {:10.4f}".format(df, res["SSE"], MSE))
    print("Total        {:>3}  {:10.4f}".format(res["n"]-1, res["SST"]))
    print()
    print("=== Inference at x0 = {:.3f} ===".format(x0))
    print("Mean response CI (95%): ({:.5f}, {:.5f})".format(ci_mean[0], ci_mean[1]))
    print("Prediction interval (95%): ({:.5f}, {:.5f})".format(pi_new[0], pi_new[1]))

    if save_plot:
        os.makedirs("outputs", exist_ok=True)
        xs = np.linspace(x.min(), x.max(), 300)
        yhat = b0 + b1*xs
        # CI & PI bands
        se_mean_x = sigma * np.sqrt(1/n + (xs - xbar)**2 / Sxx)
        se_pred_x = sigma * np.sqrt(1 + 1/n + (xs - xbar)**2 / Sxx)
        ci_u, ci_l = yhat + tcrit*se_mean_x, yhat - tcrit*se_mean_x
        pi_u, pi_l = yhat + tcrit*se_pred_x, yhat - tcrit*se_pred_x

        plt.figure()
        plt.scatter(x, y, s=30)
        plt.plot(xs, yhat, linewidth=2)
        plt.plot(xs, ci_u, linestyle="--")
        plt.plot(xs, ci_l, linestyle="--")
        plt.plot(xs, pi_u, linestyle=":")
        plt.plot(xs, pi_l, linestyle=":")
        plt.xlabel("Speed (mph)") 
        plt.ylabel("Stopping Distance (ft)")
        plt.title("SLR with 95% CI (--) and 95% PI (:)")
        out = "outputs/ch08_slr_bands.png"
        plt.savefig(out, dpi=130, bbox_inches="tight")
        print("Saved plot ->", out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x0", type=float, default=20.0, help="x value for CI/PI calculations")
    ap.add_argument("--alpha", type=float, default=0.05, help="significance level")
    ap.add_argument("--save-plot", action="store_true")
    args = ap.parse_args()

    x, y = CARS[:,0], CARS[:,1]
    fit = fit_slr(x, y)
    inference({"x": x, "y": y, "fit": fit}, alpha=args.alpha, x0=args.x0, save_plot=args.save_plot)

if __name__ == "__main__":
    main()