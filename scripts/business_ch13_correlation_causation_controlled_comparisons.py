"""
Track D — Chapter 13
Correlation, Causation, and Controlled Comparisons (NSO running case)

Goal:
- Show how "two lines move together" can be misleading.
- Demonstrate a controlled comparison via partial correlation:
  corr(X,Y) vs corr(resid(X|Z), resid(Y|Z))

Outputs (written to --outdir):
- ch13_controlled_comparisons_design.json
- ch13_correlation_summary.json
- ch13_correlation_memo.md
- figures/ + ch13_figures_manifest.csv
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from scripts._cli import base_parser
from scripts._reporting_style import FigureManifestRow, FigureSpec, save_figure, style_context


CHAPTER = "ch13"


@dataclass(frozen=True)
class Outputs:
    figures_dir: Path
    design_path: Path
    summary_path: Path
    memo_path: Path
    manifest_path: Path


def _month_key(dt: pd.Series) -> pd.Series:
    return pd.to_datetime(dt).dt.to_period("M").astype(str)


def _signed_amount(df: pd.DataFrame) -> pd.Series:
    """GL signed amount convention: debit - credit (credits become negative)."""
    return df["debit"].astype(float) - df["credit"].astype(float)


def _series_monthly(gl: pd.DataFrame, *, account_name: str) -> pd.Series:
    """Return a monthly signed series for a given GL account_name."""
    df = gl.loc[gl["account_name"] == account_name, ["date", "debit", "credit"]].copy()
    if df.empty:
        raise ValueError(f"account_name not found in gl_journal: {account_name!r}")
    df["month"] = _month_key(df["date"])
    df["amount"] = _signed_amount(df)
    return df.groupby("month", sort=True)["amount"].sum()


def _revenue_monthly(gl: pd.DataFrame) -> pd.Series:
    """Revenue is stored as credits (negative signed amounts); convert to positive sales."""
    df = gl.loc[gl["account_type"] == "Revenue", ["date", "debit", "credit"]].copy()
    df["month"] = _month_key(df["date"])
    df["amount"] = _signed_amount(df)
    return -df.groupby("month", sort=True)["amount"].sum()


def _residualize(x: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Return residuals of x after linear fit on z."""
    if len(x) != len(z):
        raise ValueError("x and z must have same length")
    a, b = np.polyfit(z, x, deg=1)
    return x - (a * z + b)


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _partial_corr(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    return _corr(_residualize(x, z), _residualize(y, z))


def analyze_ch13(*, datadir: Path, outdir: Path, seed: int) -> Outputs:
    rng = np.random.default_rng(seed)

    gl_path = datadir / "gl_journal.csv"
    if not gl_path.exists():
        raise FileNotFoundError(f"Missing required input: {gl_path}")

    gl = pd.read_csv(gl_path)
    gl["date"] = pd.to_datetime(gl["date"])

    # ---- Design (pre-commitment) ----
    x_name = "Revenue"
    y_name = "Payroll Tax Expense"
    z_name = "Payroll Expense"

    design: Dict[str, Any] = {
        "chapter": CHAPTER,
        "question": "Do payroll taxes move with revenue, and does that imply causation?",
        "x": {"name": x_name, "definition": "Monthly sales revenue from GL revenue accounts."},
        "y": {"name": y_name, "definition": "Monthly payroll tax expense from GL."},
        "control_z": {
            "name": z_name,
            "definition": "Monthly payroll expense (proxy for headcount/activity).",
            "why_control": "Payroll taxes are mechanically tied to payroll; revenue may co-move because activity drives both.",
        },
        "claim_rules": [
            "Report correlation and partial correlation only (no causal claim).",
            "Interpret effect sizes in business terms (direction + materiality).",
            "If results are sensitive to one or two months, say so explicitly.",
        ],
        "seed": int(seed),
    }

    # ---- Compute series ----
    revenue = _revenue_monthly(gl)
    payroll_tax = _series_monthly(gl, account_name=y_name)
    payroll = _series_monthly(gl, account_name=z_name)

    df = pd.concat({"revenue": revenue, "payroll_tax": payroll_tax, "payroll": payroll}, axis=1).dropna()

    # Deterministic jitter so points don't overlap perfectly in plots
    df["revenue_j"] = df["revenue"] * (1.0 + rng.normal(loc=0.0, scale=1e-6, size=len(df)))

    x = df["revenue"].to_numpy()
    y = df["payroll_tax"].to_numpy()
    z = df["payroll"].to_numpy()

    naive_r = _corr(x, y)
    partial_r = _partial_corr(x, y, z)

    loo_rs = []
    for i in range(len(df)):
        mask = np.ones(len(df), dtype=bool)
        mask[i] = False
        loo_rs.append(_corr(x[mask], y[mask]))
    loo_min, loo_max = float(np.nanmin(loo_rs)), float(np.nanmax(loo_rs))

    summary: Dict[str, Any] = {
        "chapter": CHAPTER,
        "n_months": int(len(df)),
        "variables": {"x": x_name, "y": y_name, "control_z": z_name},
        "correlations": {
            "naive_pearson_r": naive_r,
            "partial_pearson_r_control_z": partial_r,
            "leave_one_out_naive_r_min": loo_min,
            "leave_one_out_naive_r_max": loo_max,
        },
        "interpretation": {
            "naive": "Correlation is a 'look here' signal; it does not prove causality.",
            "controlled": "Partial correlation estimates the relationship between X and Y after removing Z's linear effect.",
            "note": "If partial correlation shrinks materially, the naive story is likely confounded by payroll.",
        },
    }

    # ---- Write outputs ----
    outdir.mkdir(parents=True, exist_ok=True)
    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    design_path = outdir / "ch13_controlled_comparisons_design.json"
    summary_path = outdir / "ch13_correlation_summary.json"
    memo_path = outdir / "ch13_correlation_memo.md"
    manifest_path = outdir / "ch13_figures_manifest.csv"

    design_path.write_text(json.dumps(design, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    memo = f"""# Chapter 13 — Correlation, Causation, and Controlled Comparisons

## Executive summary
- **Revenue vs Payroll Tax Expense** correlation (naïve): r = {naive_r:.3f}
- After controlling for **Payroll Expense** (proxy for headcount/activity): partial r = {partial_r:.3f}

## What this means
Payroll taxes are mechanically tied to payroll. If revenue and payroll co-move (seasonality/activity),
payroll taxes will also appear to co-move with revenue.

The controlled comparison (partial correlation) helps avoid a misleading story: “Revenue causes payroll taxes.”

## What we can and cannot claim
✅ We can say: Revenue and payroll taxes move together in this dataset, and payroll explains much of that relationship.
❌ We cannot say: Increasing revenue causes payroll taxes to rise (causal claim).

## Sensitivity check
Leave-one-out naive correlation range: {loo_min:.3f} to {loo_max:.3f}

## Next steps (if you need causality)
- Define an intervention (policy) and a comparison group (or time-based control).
- Pre-commit the metric and the evaluation window (avoid p-hacking).
"""
    memo_path.write_text(memo, encoding="utf-8")

    # ---- Figures ----
    import matplotlib.pyplot as plt

    manifest_rows: list[FigureManifestRow] = []

    # Fig 1: naive scatter
    fig1_id = "ch13_fig01_naive_scatter"
    fig1_path = figures_dir / f"{fig1_id}.png"
    with style_context():
        fig, ax = plt.subplots()
        ax.scatter(df["revenue_j"], df["payroll_tax"])
        ax.set_title("Naïve correlation: Revenue vs Payroll Tax Expense")
        ax.set_xlabel("Revenue (monthly, $)")
        ax.set_ylabel("Payroll Tax Expense (monthly, $)")
        a, b = np.polyfit(df["revenue"], df["payroll_tax"], deg=1)
        xs = np.linspace(df["revenue"].min(), df["revenue"].max(), 100)
        ax.plot(xs, a * xs + b)
        spec = FigureSpec(
            chart_type="scatter",
            title="Revenue vs Payroll Tax Expense (naïve)",
            x_label="Revenue (monthly, $)",
            y_label="Payroll Tax Expense (monthly, $)",
            data_source="NSO v1: gl_journal.csv",
            notes="Scatter with OLS line. Correlation ≠ causation.",
        )
        save_figure(fig, fig1_path, spec=spec)
    manifest_rows.append(
        FigureManifestRow(
            filename=fig1_path.name,
            chart_type="scatter",
            title=spec.title,
            x_label=spec.x_label,
            y_label=spec.y_label,
            guardrail_note="Naïve correlation only; do not claim causation.",
            data_source=spec.data_source,
        )
    )

    # Fig 2: residual scatter (controlled)
    fig2_id = "ch13_fig02_residual_scatter"
    fig2_path = figures_dir / f"{fig2_id}.png"
    rx = _residualize(x, z)
    ry = _residualize(y, z)
    with style_context():
        fig, ax = plt.subplots()
        ax.scatter(rx, ry)
        ax.set_title("Controlled comparison: residuals after controlling for Payroll")
        ax.set_xlabel("Revenue residual (after controlling for Payroll)")
        ax.set_ylabel("Payroll Tax residual (after controlling for Payroll)")
        a, b = np.polyfit(rx, ry, deg=1)
        xs = np.linspace(rx.min(), rx.max(), 100)
        ax.plot(xs, a * xs + b)
        spec2 = FigureSpec(
            chart_type="scatter",
            title="Residual correlation after controlling for Payroll",
            x_label="Revenue residual",
            y_label="Payroll Tax residual",
            data_source="NSO v1: gl_journal.csv",
            notes="Partial correlation uses residuals from linear fits on Payroll Expense.",
        )
        save_figure(fig, fig2_path, spec=spec2)
    manifest_rows.append(
        FigureManifestRow(
            filename=fig2_path.name,
            chart_type="scatter",
            title=spec2.title,
            x_label=spec2.x_label,
            y_label=spec2.y_label,
            guardrail_note="Partial correlation: controlled for Payroll Expense.",
            data_source=spec2.data_source,
        )
    )

    # Fig 3: compare r
    fig3_id = "ch13_fig03_r_comparison"
    fig3_path = figures_dir / f"{fig3_id}.png"
    with style_context():
        fig, ax = plt.subplots()
        ax.bar(["Naïve r", "Partial r\n(control Payroll)"], [naive_r, partial_r])
        ax.set_ylim(-1, 1)
        ax.set_title("Correlation shrinks after a controlled comparison")
        ax.set_ylabel("Pearson r")
        spec3 = FigureSpec(
            chart_type="bar",
            title="Naïve vs controlled correlation",
            x_label="Correlation type",
            y_label="Pearson r",
            data_source="Derived from monthly GL aggregates",
            notes="If partial r shrinks materially, the naive story is likely confounded by Payroll.",
        )
        save_figure(fig, fig3_path, spec=spec3)
    manifest_rows.append(
        FigureManifestRow(
            filename=fig3_path.name,
            chart_type="bar",
            title=spec3.title,
            x_label=spec3.x_label,
            y_label=spec3.y_label,
            guardrail_note="Compare r values; shrinking suggests confounding.",
            data_source=spec3.data_source,
        )
    )

    pd.DataFrame([r.__dict__ for r in manifest_rows]).to_csv(manifest_path, index=False)

    return Outputs(
        figures_dir=figures_dir,
        design_path=design_path,
        summary_path=summary_path,
        memo_path=memo_path,
        manifest_path=manifest_path,
    )


def _build_cli():
    p = base_parser(description="Track D Ch13: Correlation, causation, and controlled comparisons (NSO).")
    p.add_argument("--datadir", type=Path, required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    p = _build_cli()
    args = p.parse_args(argv)

    analyze_ch13(datadir=args.datadir, outdir=args.outdir, seed=args.seed)
    print("Wrote Chapter 13 artifacts ->", args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
