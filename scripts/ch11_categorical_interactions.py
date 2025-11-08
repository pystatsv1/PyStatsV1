# SPDX-License-Identifier: MIT
"""
Chapter 11 — Categorical Predictors & Interactions (R → Python)

Examples:
  python scripts/ch11_categorical_interactions.py --save-plots
  python scripts/ch11_categorical_interactions.py --contrasts cylinders=sum,origin=treatment --interaction weight:cylinders --save-plots
  python scripts/ch11_categorical_interactions.py --interaction model_year:origin --save-plots
"""
import argparse, os, math, itertools
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- Patsy contrasts
from patsy.contrasts import Treatment, Sum, Helmert, Diff

CONTRASTS = {
    "treatment": Treatment,
    "sum": Sum,
    "helmert": Helmert,
    "diff": Diff
}

def load_autompg(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=None, engine="python")
    # map possible headers → canonical
    map_try = {
        "mpg": ["mpg"],
        "cylinders": ["cyl", "cylinders"],
        "displacement": ["disp", "displacement"],
        "horsepower": ["hp", "horsepower"],
        "weight": ["wt", "weight"],
        "acceleration": ["acc", "acceleration"],
        "model_year": ["year", "model_year"],
        "origin": ["origin"],
    }
    canon = {}
    for k, opts in map_try.items():
        for o in opts:
            if o in df.columns:
                canon[k] = o
                break
    needed = ["mpg","cylinders","displacement","horsepower","weight","acceleration","model_year"]
    missing = [k for k in needed if k not in canon]
    if missing:
        raise SystemExit(f"ERROR: expected columns missing: {', '.join(missing)}\nAvailable: {list(df.columns)}")

    keep = {k: canon[k] for k in ["mpg","cylinders","displacement","horsepower","weight","acceleration","model_year"] if k in canon}
    if "origin" in canon:
        keep["origin"] = canon["origin"]

    out = pd.DataFrame({k: pd.to_numeric(df[v], errors="coerce") if k not in ("cylinders","origin")
                        else df[v] for k, v in keep.items()})
    out = out.dropna()
    out["cylinders"] = out["cylinders"].astype("category")
    if "origin" in out.columns:
        out["origin"] = out["origin"].astype("category")
    return out

def parse_contrasts(opt: str):
    # e.g. "cylinders=sum,origin=treatment"
    mapping = {}
    if not opt:
        return mapping
    for pair in opt.split(","):
        if not pair:
            continue
        k, v = [x.strip() for x in pair.split(":", 1)] if ":" in pair else [x.strip() for x in pair.split("=", 1)]
        v = v.lower()
        if v not in CONTRASTS:
            raise SystemExit(f"Unknown contrast '{v}' for {k}. Choose from {list(CONTRASTS)}")
        mapping[k] = v
    return mapping

def build_formula(has_origin: bool, interaction_pairs):
    # Base follows a strong MLR from Ch09, but you can tweak here
    base = "mpg ~ weight + model_year + C(cylinders) + horsepower"
    if has_origin:
        base += " + C(origin)"
    for a, b in interaction_pairs:
        # If a or b are categorical keys, wrap with C()
        a_term = f"C({a})" if a in ("cylinders", "origin") else a
        b_term = f"C({b})" if b in ("cylinders", "origin") else b
        base += f" + {a_term}:{b_term}"
    return base

def apply_contrast_in_formula(term: str, contrasts_map):
    # Turn "C(var)" into "C(var, Sum)" etc. when requested
    if term.startswith("C(") and term.endswith(")"):
        inner = term[2:].strip("() ")
        name = inner.split(",")[0].strip()
        if name in contrasts_map:
            return f"C({name}, {CONTRASTS[contrasts_map[name]].__name__})"
    return term

def rewrite_contrasts_in_formula(formula: str, contrasts_map):
    # A quick rewrite: replace C(name) occurrences when user asked for a contrast
    parts = formula.replace(" ", "")
    # crude tokenization around '+' and '~' and ':'
    tokens = []
    buf = ""
    for ch in parts:
        if ch in "+~:":
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
        else:
            buf += ch
    if buf:
        tokens.append(buf)

    out_tokens = []
    for t in tokens:
        if t.startswith("C("):
            out_tokens.append(apply_contrast_in_formula(t, contrasts_map))
        else:
            out_tokens.append(t)
    # re-join (add minimal spacing for readability)
    out = ""
    for t in out_tokens:
        if t in "+~:":
            out += f" {t} "
        else:
            out += t
    return out

def interaction_pairs_from_arg(arg: str):
    # "weight:cylinders,model_year:origin"
    pairs = []
    if not arg:
        return pairs
    for item in arg.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" not in item:
            raise SystemExit(f"--interaction expects pairs like a:b, got '{item}'")
        a, b = [x.strip() for x in item.split(":", 1)]
        pairs.append((a, b))
    return pairs

def validate_interaction_pairs(pairs, df):
    """
    Keep only interactions where both variables exist in df.columns.
    Warn and skip if any are missing to avoid patsy NameError.
    """
    valid = []
    for a, b in pairs:
        missing = [v for v in (a, b) if v not in df.columns]
        if missing:
            print(f"WARNING: skipping interaction {a}:{b} — missing column(s): {', '.join(missing)}. "
                  f"Available: {list(df.columns)}")
        else:
            valid.append((a, b))
    return valid

def interaction_plot(df, model, x, cat, outpath):
    os.makedirs("outputs", exist_ok=True)
    # Predict across x-range at median of other numerics
    x_vals = np.linspace(df[x].quantile(0.05), df[x].quantile(0.95), 50)
    other = {}
    for col in ["weight","model_year","horsepower","displacement","acceleration"]:
        if col in df.columns and col != x:
            other[col] = df[col].median()
    # Build small frames per category level
    levels = df[cat].cat.categories
    plt.figure(figsize=(6,5))
    for lvl in levels:
        frame = pd.DataFrame({x: x_vals, **other})
        frame[cat] = lvl
        if cat == "cylinders" or cat == "origin":
            frame[cat] = frame[cat].astype(df[cat].dtype)
        yhat = model.predict(frame)
        plt.plot(x_vals, yhat, label=f"{cat}={lvl}")
    plt.xlabel(x)
    plt.ylabel("Predicted MPG")
    plt.title(f"Interaction: {x} × {cat}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/autompg.csv")
    ap.add_argument("--contrasts", default="", help="e.g. cylinders=sum,origin=treatment")
    ap.add_argument("--interaction", default="", help="Comma-separated pairs like 'weight:cylinders,model_year:origin'")
    ap.add_argument("--save-plots", action="store_true")
    args = ap.parse_args()

    df = load_autompg(args.data)

    inter_pairs = interaction_pairs_from_arg(args.interaction)
    # NEW: drop any interaction pairs that reference columns not present
    inter_pairs = validate_interaction_pairs(inter_pairs, df)
    formula = build_formula("origin" in df.columns, inter_pairs)

    # Rewrite contrasts in formula if requested
    c_map = parse_contrasts(args.contrasts)
    if c_map:
        # replace C(cylinders) / C(origin) occurrences
        # handle also interactions by rebuilding the formula piecewise
        # easiest: rewrite whole formula tokens
        # Replace both main effects and any interactions
        def sub_all(f):
            # break into terms around '~' and '+'
            left, right = [s.strip() for s in f.split("~",1)]
            terms = [t.strip() for t in right.split("+")]
            new_terms = []
            for t in terms:
                if ":" in t:
                    a,b = [s.strip() for s in t.split(":",1)]
                    new_terms.append(f"{apply_contrast_in_formula(a, c_map)}:{apply_contrast_in_formula(b, c_map)}")
                else:
                    new_terms.append(apply_contrast_in_formula(t, c_map))
            return f"{left} ~ " + " + ".join(new_terms)
        formula = sub_all(formula)

    print("=== Formula ===")
    print(formula)

    model = smf.ols(formula, data=df).fit()
    print("\n=== Coefficients ===")
    for name, est, se, tval, pval in zip(model.params.index, model.params.values, model.bse.values, model.tvalues.values, model.pvalues.values):
        print(f"{name:30s} est={est:9.4f}  SE={se:8.4f}  t={tval:8.3f}  p={pval:.3g}")

    print("\n=== Fit Stats ===")
    print(f"R^2: {model.rsquared:.6f}")
    print(f"Adj R^2: {model.rsquared_adj:.6f}")
    print(f"Sigma (SE): {math.sqrt(model.mse_resid):.6f}")
    print(f"AIC: {model.aic:.3f}  BIC: {model.bic:.3f}")

    # Type-II ANOVA is a reasonable default for models with interactions
    print("\n=== ANOVA (Type II) ===")
    print(anova_lm(model, typ=2))

    if args.save_plots and inter_pairs:
        for a, b in inter_pairs:
            # choose numeric for x and categorical for cat
            if a in df.columns and str(df[a].dtype) != "category" and b in df.columns and str(df[b].dtype) == "category":
                x, cat = a, b
            elif b in df.columns and str(df[b].dtype) != "category" and a in df.columns and str(df[a].dtype) == "category":
                x, cat = b, a
            else:
                continue
            out = f"outputs/ch11_interaction_{x}_x_{cat}.png"
            interaction_plot(df, model, x, cat, out)
            print(f"Saved plot -> {out}")

if __name__ == "__main__":
    main()
