# SPDX-License-Identifier: MIT
import argparse, os, math
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- make Windows console UTF-8 friendly ---
import sys
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def hedges_g(a, b):
    na, nb = len(a), len(b)
    sa, sb = a.var(ddof=1), b.var(ddof=1)
    s_p = np.sqrt(((na-1)*sa + (nb-1)*sb)/(na+nb-2))
    d = (a.mean()-b.mean())/s_p
    J = 1 - 3/(4*(na+nb)-9)
    return d*J

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/synthetic/fitness_long.csv")
    ap.add_argument("--save-plots", action="store_true")
    args = ap.parse_args()

    df = pd.read_csv(args.data)
    df["time"]  = pd.Categorical(df["time"],  categories=["pre","post"], ordered=True)
    df["group"] = pd.Categorical(df["group"])

    # Mixed model with random intercept per subject
    import statsmodels.api as sm
    md = sm.MixedLM.from_formula("strength ~ time*group + age + sex + bmi",
                                 groups="id", re_formula="1", data=df)
    m = md.fit(method="lbfgs")

    print("=== LMM: strength ~ time*group + age + sex + bmi + (1|id) ===")
    print(m.summary())

    # Within-group pre→post paired tests
    from scipy import stats
    print("\n=== Within-group pre→post (paired) ===")
    for g in df["group"].cat.categories:
        wide = (df[df.group==g]
                .pivot_table(index="id", columns="time", values="strength", observed=False))
        pre, post = wide["pre"], wide["post"]
        diff = (post - pre).dropna()
        mean = diff.mean(); sd = diff.std(ddof=1); n = diff.shape[0]
        t = mean / (sd/np.sqrt(n))
        p = 2*stats.t.sf(abs(t), df=n-1)
        d_paired = mean / sd
        print(f"{g:8s} n={n:2d}  Δ={mean:6.2f}  t={t:6.2f}  p={p:.3g}  d_paired={d_paired:.2f}")

    # Between-group at post (Welch t) + Hedges g
    post = df[df.time=="post"]
    cats = post.group.cat.categories
    gA = post[post.group==cats[0]]["strength"]
    gB = post[post.group==cats[1]]["strength"]
    t2, p2 = stats.ttest_ind(gA, gB, equal_var=False)
    g = hedges_g(gA, gB)
    print("\n=== Between groups at post (Welch t) ===")
    print(f"t={t2:.2f}  p={p2:.3g}  Hedges g={g:.2f}")

    if args.save_plots:
        os.makedirs("outputs", exist_ok=True)
        fig, ax = plt.subplots(figsize=(6,4))
        # spaghetti
        for (grp, sid), sub in df.sort_values("time").groupby(["group","id"], observed=False):
            ax.plot([0,1], sub["strength"].values, alpha=0.2)
        # thick means per group
        mean_pre  = df[df.time=="pre" ].groupby("group", observed=False)["strength"].mean()
        mean_post = df[df.time=="post"].groupby("group", observed=False)["strength"].mean()
        for gname in df["group"].cat.categories:
            ax.plot([0,1], [mean_pre[gname], mean_post[gname]], linewidth=3, label=gname)
        ax.set_xticks([0,1]); ax.set_xticklabels(["pre","post"])
        ax.set_ylabel("Strength")
        ax.legend()
        fig.tight_layout()
        fp = "outputs/ch13_fitness_spaghetti.png"; fig.savefig(fp, dpi=150)
        print("Saved plot ->", fp)

if __name__ == "__main__":
    main()