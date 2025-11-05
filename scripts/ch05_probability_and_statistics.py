"""
Chapter 5 — Probability & Statistics (R mirror)
- Normal pdf/cdf/quantiles
- Binomial pmf
- One-sample and two-sample t-tests (manual + SciPy)
- Small simulation comparing analytic approx
"""
import argparse
import numpy as np
from scipy import stats

def one_sample_demo():
    # Captain Crisp example (weights in oz; R example)
    w = np.array([15.5,16.2,16.1,15.8,15.6,16.0,15.8,15.9,16.2])
    n = len(w)
    xbar = w.mean()
    s = w.std(ddof=1)
    mu0 = 16
    t = (xbar - mu0) / (s/np.sqrt(n))
    pval = stats.t.cdf(t, df=n-1)  # one-sided, less-than
    print("One-sample t-test (manual): t =", round(t,4), "p-value =", round(pval,6))
    tt = stats.ttest_1samp(w, popmean=16, alternative="less")
    print("One-sample t-test (scipy):  t =", round(tt.statistic,4), "p-value =", round(tt.pvalue,6))

def two_sample_demo():
    # R example vectors
    x = np.array([70,82,78,74,94,82])
    y = np.array([64,72,60,76,72,80,84,68])
    nx, ny = len(x), len(y)
    sx, sy = x.std(ddof=1), y.std(ddof=1)
    xbar, ybar = x.mean(), y.mean()
    sp = np.sqrt(((nx-1)*sx**2 + (ny-1)*sy**2) / (nx+ny-2))
    t = ((xbar - ybar) - 0) / (sp*np.sqrt(1/nx + 1/ny))
    pval = 1 - stats.t.cdf(t, df=nx+ny-2)  # greater-than
    print("Two-sample pooled t (manual): t =", round(t,4), "p-value =", round(pval,6))
    tt = stats.ttest_ind(x, y, equal_var=True, alternative="greater")
    print("Two-sample pooled t (scipy):  t =", round(tt.statistic,4), "p-value =", round(tt.pvalue,6))

def simulation_demo(seed=42, num_samples=10_000):
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(num_samples):
        x1 = rng.normal(6, 2, size=25)
        x2 = rng.normal(5, 2, size=25)
        diffs.append(x1.mean() - x2.mean())
    diffs = np.array(diffs)
    prob = np.mean((0 < diffs) & (diffs < 2))
    print("Simulated P(0 < D < 2) ≈", round(prob,6))
    # Normal approx: mean=1, var=(2^2/25 + 2^2/25) = 0.32
    approx = stats.norm(1, np.sqrt(0.32)).cdf(2) - stats.norm(1, np.sqrt(0.32)).cdf(0)
    print("Normal approx             ", round(approx,6))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    # Distribution helpers (mirror of R's dnorm/pnorm/qnorm, dbinom)
    print("dnorm(x=3, mean=2, sd=5) =", round(stats.norm(2,5).pdf(3), 8))
    print("pnorm(q=3, mean=2, sd=5) =", round(stats.norm(2,5).cdf(3), 7))
    print("qnorm(p=.975, mean=2, sd=5) =", round(stats.norm(2,5).ppf(.975), 5))
    print("dbinom(x=6, size=10, prob=.75) =", round(stats.binom.pmf(6, 10, 0.75), 6))

    one_sample_demo()
    two_sample_demo()
    simulation_demo(args.seed)

if __name__ == "__main__":
    main()
