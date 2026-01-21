"""My Own Data — scaffold script (beginner friendly).

This script is designed to be copied and customized.

Default behavior:
  - reads data/my_data.csv
  - prints a small diagnostic report
  - writes a few simple outputs under outputs/my_data/

Student edits:
  - change ID_COL / GROUP_COL if your dataset uses different names
  - optionally set OUTCOME_COL to focus on one numeric column
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # safe for headless CI

import matplotlib.pyplot as plt
import pandas as pd


# === Student edits start here ================================================

ID_COL = "id"  # optional
GROUP_COL = "group"  # optional
OUTCOME_COL = "outcome"  # optional

# === Student edits end here ==================================================


@dataclass(frozen=True)
class ReportPaths:
    outdir: Path
    tables_dir: Path
    plots_dir: Path
    missingness_csv: Path
    numeric_summary_csv: Path
    group_means_csv: Path
    numeric_hist_png: Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate + explore a CSV (beginner-friendly scaffold).",
    )
    p.add_argument(
        "--csv",
        default="data/my_data.csv",
        help="Path to your CSV file (default: data/my_data.csv).",
    )
    p.add_argument(
        "--outdir",
        default="outputs/my_data",
        help="Where to write outputs (default: outputs/my_data).",
    )
    return p.parse_args()


def ensure_outdirs(outdir: Path) -> ReportPaths:
    outdir = outdir.expanduser().resolve()
    tables_dir = outdir / "tables"
    plots_dir = outdir / "plots"
    tables_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    return ReportPaths(
        outdir=outdir,
        tables_dir=tables_dir,
        plots_dir=plots_dir,
        missingness_csv=tables_dir / "missingness.csv",
        numeric_summary_csv=tables_dir / "numeric_summary.csv",
        group_means_csv=tables_dir / "group_means.csv",
        numeric_hist_png=plots_dir / "numeric_histograms.png",
    )


def read_csv(path: Path) -> pd.DataFrame:
    path = path.expanduser().resolve()
    if not path.exists():
        raise SystemExit(
            f"CSV not found: {path}\n"
            "Tip: put your file at data/my_data.csv or pass --csv <path>."
        )
    df = pd.read_csv(path)
    if df.shape[0] < 3:
        raise SystemExit(
            f"CSV has too few rows for analysis: rows={df.shape[0]}\n"
            "Tip: include at least a few observations."
        )
    if df.shape[1] < 2:
        raise SystemExit(
            f"CSV has too few columns for analysis: cols={df.shape[1]}\n"
            "Tip: one column is rarely enough."
        )
    return df


def missingness_table(df: pd.DataFrame) -> pd.DataFrame:
    miss = df.isna().sum().rename("missing")
    pct = (miss / len(df)).rename("missing_pct")
    out = pd.concat([miss, pct], axis=1).reset_index().rename(columns={"index": "column"})
    return out.sort_values(["missing", "column"], ascending=[False, True])


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    # Create a copy where columns that *look* numeric become numeric.
    out = df.copy()
    for c in out.columns:
        if out[c].dtype == object:
            out[c] = pd.to_numeric(out[c], errors="ignore")
    return out


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include=["number"])
    if numeric.empty:
        return pd.DataFrame(columns=["column", "count", "mean", "std", "min", "max"]).copy()
    desc = numeric.describe().T
    keep = desc[["count", "mean", "std", "min", "max"]].reset_index().rename(columns={"index": "column"})
    return keep


def group_means(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if group_col not in df.columns:
        return pd.DataFrame(columns=[group_col]).copy()
    numeric = df.select_dtypes(include=["number"])
    if numeric.empty:
        return pd.DataFrame(columns=[group_col]).copy()
    g = df.groupby(group_col, dropna=False)
    means = g[numeric.columns].mean(numeric_only=True).reset_index()
    return means


def plot_numeric_histograms(df: pd.DataFrame, outpath: Path) -> None:
    numeric = df.select_dtypes(include=["number"])
    if numeric.empty:
        return
    cols = list(numeric.columns)

    # One figure with multiple rows (simple and readable)
    n = len(cols)
    fig_h = max(3.0, 2.0 * n)
    fig, axes = plt.subplots(nrows=n, ncols=1, figsize=(7.5, fig_h))
    if n == 1:
        axes = [axes]
    for ax, c in zip(axes, cols, strict=False):
        ax.hist(numeric[c].dropna().to_numpy(), bins=12)
        ax.set_title(f"Histogram: {c}")
        ax.set_xlabel(c)
        ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def print_quick_report(df: pd.DataFrame) -> None:
    print("\nMy Own Data — quick report")
    print("========================")
    print(f"rows: {df.shape[0]}  cols: {df.shape[1]}")
    print("\ncolumns:")
    for c in df.columns:
        print(f"  - {c}")

    if ID_COL in df.columns:
        dup = df[ID_COL].duplicated().sum()
        if dup:
            print(f"\n[WARN] Duplicate {ID_COL} values: {dup}")

    if GROUP_COL in df.columns:
        k = df[GROUP_COL].nunique(dropna=False)
        print(f"\n{GROUP_COL}: {k} group(s)")
        vc = df[GROUP_COL].value_counts(dropna=False)
        for lvl, n in vc.items():
            print(f"  - {lvl!r}: {int(n)}")

    numeric = df.select_dtypes(include=["number"]).columns
    if len(numeric) == 0:
        print(
            "\n[WARN] No numeric columns detected. If numbers are stored as text, fix your CSV or edit the script."
        )
    else:
        print("\nnumeric columns:")
        for c in numeric:
            print(f"  - {c}")


def main() -> int:
    args = parse_args()

    df_raw = read_csv(Path(args.csv))
    df = coerce_numeric(df_raw)

    paths = ensure_outdirs(Path(args.outdir))

    print_quick_report(df)

    miss = missingness_table(df)
    miss.to_csv(paths.missingness_csv, index=False)

    num = numeric_summary(df)
    num.to_csv(paths.numeric_summary_csv, index=False)

    gm = group_means(df, group_col=GROUP_COL)
    if not gm.empty:
        gm.to_csv(paths.group_means_csv, index=False)

    plot_numeric_histograms(df, paths.numeric_hist_png)

    print("\nWrote outputs to:")
    print(f"  {paths.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
