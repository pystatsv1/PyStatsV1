# SPDX-License-Identifier: MIT
"""
Chapter 7 — Simple Linear Regression (R mirror)
- Embedded 'cars' dataset (speed, dist)
- Prints coef, sigma, R^2, predictions
- --save-plot writes outputs/ch07_slr.png
"""
import argparse
import math
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CARS = np.array([
    (4,2),(4,10),(7,4),(7,22),(8,16),(9,10),(10,18),(10,26),(10,34),(11,17),
    (11,28),(12,14),(12,20),(12,24),(12,28),(13,26),(13,34),(13,34),(13,46),(14,26),
    (14,36),(14,60),(14,80),(15,20),(15,26),(15,54),(16,32),(16,40),(17,32),(17,40),
    (17,50),(18,42),(18,56),(18,76),(18,84),(19,36),(19,46),(19,68),(20,32),(20,48),
    (20,52),(20,56),(20,64),(22,66),(23,54),(24,70),(24,92),(24,93),(24,120),(25,85),
], dtype=float)

def fit_slr(x, y):
    Sxy = np.sum((x - x.mean())*(y - y.mean()))
    Sxx = np.sum((x - x.mean())**2)
    b1 = Sxy / Sxx
    b0 = y.mean() - b1 * x.mean()
    yhat = b0 + b1*x
    resid = y - yhat
    n = len(x)
    s2 = np.sum(resid**2) / (n - 2)
    sigma = math.sqrt(s2)
    R2 = 1 - np.sum(resid**2)/np.sum((y - y.mean())**2)
    return b0, b1, yhat, resid, sigma, R2

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save-plot", action="store_true")
    args = ap.parse_args()

    x, y = CARS[:,0], CARS[:,1]
    b0, b1, yhat, resid, sigma, R2 = fit_slr(x, y)

    print("Coefficients:")
    print("(Intercept) =", round(b0,6))
    print("speed       =", round(b1,6))
    print("Residual standard error (sigma):", round(sigma,5))
    print("R^2:", round(R2,6))
    for s in [8, 21, 50]:
        print(f"Prediction dist | speed={s}: {round(b0 + b1*s, 5)}")

    if args.save_plot:
        os.makedirs("outputs", exist_ok=True)
        xs = np.linspace(x.min(), x.max(), 200)
        plt.figure()
        plt.scatter(x, y, s=40)
        plt.plot(xs, b0 + b1*xs, linewidth=3)
        plt.xlabel("Speed (mph)") 
        plt.ylabel("Stopping Distance (ft)")
        plt.title("Stopping Distance vs Speed — Fitted SLR")
        out = "outputs/ch07_slr.png"
        plt.savefig(out, dpi=130, bbox_inches="tight")
        print("Saved plot ->", out)

if __name__ == "__main__":
    main()
