# SPDX-License-Identifier: MIT
"""Track D — Chapter 14: Regression Driver Analysis (NSO).

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch14_driver_table.csv
* ch14_model_design.json
* ch14_summary.json
* ch14_memo.md
* ch14_figures_manifest.csv

"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from scripts._cli import base_parser
from scripts._reporting_style import FigureManifestRow, FigureSpec, save_figure, style_context

CHAPTER = "Track D Chapter 14 — Regression Driver Analysis (NSO)"


@dataclass(frozen=True)
class Outputs:
    driver_table_csv: Path
    design_json: Path
    summary_json: Path
    memo_md: Path
    figures_manifest_csv: Path


def _read_csv(datadir: Path, name: str) -> pd.DataFrame:
    p = datadir / name
    if not p.exists():
        raise FileNotFoundError(f"Expected {name} in {datadir} but not found.")
    return pd.read_csv(p)


def _month_key_from_date(series: pd.Series) -> pd.Series:
    # stable month key used across NSO files
    return pd.to_datetime(series).dt.to_period("M").astype(str)


def _build_driver_table(datadir: Path) -> pd.DataFrame:
    inv = _read_csv(datadir, "inventory_movements.csv")
    ar = _read_csv(datadir, "ar_events.csv")
    is_df = _read_csv(datadir, "statements_is_monthly.csv")

    # ---- Units sold (monthly): inventory movement_type == sale_issue (qty is negative in sim)
    inv_sale = inv[inv["movement_type"] == "sale_issue"].copy()
    inv_sale["month"] = _month_key_from_date(inv_sale["date"])
    units = (
        inv_sale.groupby("month", as_index=False)["qty"]
        .sum()
        .rename(columns={"qty": "units_sold"})
    )
    units["units_sold"] = -units["units_sold"]  # convert negative issues to positive units sold

    # ---- Invoice count (monthly): AR event_type == invoice
    ar_inv = ar[ar["event_type"] == "invoice"].copy()
    ar_inv["month"] = _month_key_from_date(ar_inv["date"])
    invoices = (
        ar_inv.groupby("month", as_index=False)["event_type"]
        .count()
        .rename(columns={"event_type": "invoice_count"})
    )

    # ---- Income statement (monthly): extract Sales Revenue + COGS
    # statements_is_monthly has columns: month, line, amount
    is_keep = is_df[is_df["line"].isin(["Sales Revenue", "Cost of Goods Sold"])].copy()
    is_pivot = (
        is_keep.pivot_table(index="month", columns="line", values="amount", aggfunc="sum")
        .reset_index()
        .rename(
            columns={
                "Sales Revenue": "sales_revenue",
                "Cost of Goods Sold": "cogs",
            }
        )
    )

    # ---- Join drivers + P&L lines
    df = is_pivot.merge(units, on="month", how="left").merge(invoices, on="month", how="left")
    df["units_sold"] = df["units_sold"].fillna(0.0)
    df["invoice_count"] = df["invoice_count"].fillna(0.0)

    # keep a real datetime month column for nicer tables/figures
    df["month_dt"] = pd.to_datetime(df["month"] + "-01")
    df = df.sort_values("month_dt").reset_index(drop=True)

    # reorder
    cols = ["month", "month_dt", "units_sold", "invoice_count", "sales_revenue", "cogs"]
    return df[cols]


def _fit_ols(y: pd.Series, X: pd.DataFrame) -> sm.regression.linear_model.RegressionResultsWrapper:
    Xc = sm.add_constant(X, has_constant="add")
    return sm.OLS(y, Xc).fit()


def analyze_ch14(datadir: Path, outdir: Path, seed: int = 123) -> Outputs:
    outdir.mkdir(parents=True, exist_ok=True)
    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    df = _build_driver_table(datadir)

    # ---- Models (keep explainable)
    # COGS ~ units_sold  (fixed + variable)
    m1 = _fit_ols(df["cogs"], df[["units_sold"]])

    # Revenue ~ units_sold (avg selling price lens)
    m2 = _fit_ols(df["sales_revenue"], df[["units_sold"]])

    # Revenue ~ units_sold + invoice_count (mix / activity check)
    m3 = _fit_ols(df["sales_revenue"], df[["units_sold", "invoice_count"]])

    # simple forecast example: next month drivers = avg last 3 months
    last3 = df.tail(3)
    next_units = float(last3["units_sold"].mean())
    next_invoices = float(last3["invoice_count"].mean())

    pred_cogs = float(
        m1.predict(
            sm.add_constant(pd.DataFrame({"units_sold": [next_units]}), has_constant="add")
        ).iloc[0]
    )
    pred_rev_m2 = float(
        m2.predict(
            sm.add_constant(pd.DataFrame({"units_sold": [next_units]}), has_constant="add")
        ).iloc[0]
    )
    pred_rev_m3 = float(
        m3.predict(
            sm.add_constant(
                pd.DataFrame({"units_sold": [next_units], "invoice_count": [next_invoices]}),
                has_constant="add",
            )
        ).iloc[0]
    )

    # ---- Write core artifacts
    driver_csv = outdir / "ch14_driver_table.csv"
    design_json = outdir / "ch14_regression_design.json"
    summary_json = outdir / "ch14_regression_summary.json"
    memo_md = outdir / "ch14_regression_memo.md"
    manifest_csv = outdir / "ch14_figures_manifest.csv"

    df.to_csv(driver_csv, index=False)

    design = {
        "chapter": CHAPTER,
        "seed": seed,
        "expected_inputs": ["inventory_movements.csv", "ar_events.csv", "statements_is_monthly.csv"],
        "drivers": {
            "units_sold": "Monthly sum of -qty for inventory_movements where movement_type == 'sale_issue'",
            "invoice_count": "Monthly count of ar_events where event_type == 'invoice'",
        },
        "models": [
            {"name": "m1_cogs_units", "formula": "cogs ~ 1 + units_sold", "interpretation": "fixed + variable_cost_per_unit"},
            {"name": "m2_rev_units", "formula": "sales_revenue ~ 1 + units_sold", "interpretation": "base + avg_price_per_unit"},
            {"name": "m3_rev_units_invoices", "formula": "sales_revenue ~ 1 + units_sold + invoice_count", "interpretation": "simple multi-driver check"},
        ],
        "note": "Regression is a driver lens; it does not prove causation.",
    }

    summary = {
        "rows": int(df.shape[0]),
        "date_range": {"min_month": str(df["month_dt"].min().date()), "max_month": str(df["month_dt"].max().date())},
        "m1_cogs_units": {"params": {"const": float(m1.params["const"]), "units_sold": float(m1.params["units_sold"])}, "r2": float(m1.rsquared)},
        "m2_rev_units": {"params": {"const": float(m2.params["const"]), "units_sold": float(m2.params["units_sold"])}, "r2": float(m2.rsquared)},
        "m3_rev_units_invoices": {
            "params": {
                "const": float(m3.params["const"]),
                "units_sold": float(m3.params["units_sold"]),
                "invoice_count": float(m3.params["invoice_count"]),
            },
            "r2": float(m3.rsquared),
        },
        "forecast_example": {
            "assumption": "Next month drivers = average of last 3 months",
            "next_units_sold": next_units,
            "next_invoice_count": next_invoices,
            "predicted_cogs_m1": pred_cogs,
            "predicted_sales_rev_m2": pred_rev_m2,
            "predicted_sales_rev_m3": pred_rev_m3,
        },
    }

    design_json.write_text(json.dumps(design, indent=2), encoding="utf-8")
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    memo_lines = [
        "# Chapter 14 — Regression Driver Analysis (NSO)\n",
        "## What we did\n",
        "- Built a monthly driver table:\n",
        "  - **Units sold** from inventory movements (sale_issue rows)\n",
        "  - **Invoice count** from AR events (invoice rows)\n",
        "  - **Revenue & COGS** from the monthly income statement\n",
        "- Fit simple, explainable regressions to estimate **rates** and **baseline** components.\n",
        "\n",
        "## Key results\n",
        f"- **COGS ~ units_sold**: intercept ≈ **{m1.params['const']:.2f}**, slope ≈ **{m1.params['units_sold']:.2f}**, R² ≈ **{m1.rsquared:.3f}**\n",
        f"- **Revenue ~ units_sold**: intercept ≈ **{m2.params['const']:.2f}**, slope ≈ **{m2.params['units_sold']:.2f}**, R² ≈ **{m2.rsquared:.3f}**\n",
        "\n",
        "## Forecast example (avg last 3 months)\n",
        f"- Next units_sold: **{next_units:.1f}**\n",
        f"- Predicted COGS (m1): **{pred_cogs:.2f}**\n",
        f"- Predicted Revenue (m2): **{pred_rev_m2:.2f}**\n",
        f"- Predicted Revenue (m3): **{pred_rev_m3:.2f}**\n",
        "\n",
        "## Notes / limitations\n",
        "- Regression is a quantitative driver lens — **not proof of causation**.\n",
        "- If pricing or product mix changes, re-fit and re-check residuals.\n",
    ]
    memo_md.write_text("".join(memo_lines), encoding="utf-8")

    # ---- Figures + manifest (match repo reporting style contract)
    manifest_rows: list[FigureManifestRow] = []

    def _add_row(fig_path: Path, spec: FigureSpec) -> None:
        manifest_rows.append(
            FigureManifestRow(
                filename=fig_path.name,
                chart_type=spec.chart_type,
                title=spec.title,
                x_label=spec.x_label,
                y_label=spec.y_label,
                data_source=spec.data_source,
                guardrail_note="Driver lens only; correlation ≠ causation. Interpret slope as rate and intercept as baseline.",
            )
        )

    def _save_scatter_with_fit(
        fig_id: str,
        x: pd.Series,
        y: pd.Series,
        model: Any,
        xlabel: str,
        ylabel: str,
        title: str,
    ) -> None:
        fig_path = figures_dir / f"{fig_id}.png"
        xs = np.linspace(float(x.min()), float(x.max()), 120)

        # predict with model
        if "invoice_count" in model.model.exog_names:
            # only used for the m3 figure; caller should pass scalar invoice_count series
            raise RuntimeError("Use the m3-specific helper for multi-driver predictions.")
        xdf = pd.DataFrame({"units_sold": xs})
        yhat = model.predict(sm.add_constant(xdf, has_constant="add"))

        spec = FigureSpec(
            chart_type="scatter",
            title=title,
            x_label=xlabel,
            y_label=ylabel,
            data_source="NSO v1 synthetic outputs",
            notes="Scatter with OLS fit line.",
        )

        with style_context():
            fig, ax = plt.subplots()
            ax.scatter(x.to_numpy(dtype=float), y.to_numpy(dtype=float))
            ax.plot(xs, yhat.to_numpy(dtype=float))
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            save_figure(fig, fig_path, spec=spec)

        _add_row(fig_path, spec)

    # Fig 1: COGS vs units
    _save_scatter_with_fit(
        fig_id="ch14_fig01_cogs_vs_units",
        x=df["units_sold"],
        y=df["cogs"],
        model=m1,
        xlabel="Units sold (monthly)",
        ylabel="COGS",
        title="COGS vs Units Sold (monthly)",
    )

    # Fig 2: Revenue vs units
    _save_scatter_with_fit(
        fig_id="ch14_fig02_revenue_vs_units",
        x=df["units_sold"],
        y=df["sales_revenue"],
        model=m2,
        xlabel="Units sold (monthly)",
        ylabel="Sales Revenue",
        title="Sales Revenue vs Units Sold (monthly)",
    )

    # Fig 3: Actual vs predicted revenue (m3)
    fig3_id = "ch14_fig03_actual_vs_predicted_revenue_m3"
    fig3_path = figures_dir / f"{fig3_id}.png"
    exog3 = sm.add_constant(df[["units_sold", "invoice_count"]], has_constant="add")
    yhat3 = m3.predict(exog3)

    spec3 = FigureSpec(
        chart_type="scatter",
        title="Actual vs Predicted Sales Revenue (m3)",
        x_label="Predicted Sales Revenue",
        y_label="Actual Sales Revenue",
        data_source="NSO v1 synthetic outputs",
        notes="Scatter; closer to the 45° line indicates better fit.",
    )
    with style_context():
        fig, ax = plt.subplots()
        ax.scatter(yhat3.to_numpy(dtype=float), df["sales_revenue"].to_numpy(dtype=float))
        ax.set_title(spec3.title)
        ax.set_xlabel(spec3.x_label)
        ax.set_ylabel(spec3.y_label)
        save_figure(fig, fig3_path, spec=spec3)
    _add_row(fig3_path, spec3)

    pd.DataFrame([r.__dict__ for r in manifest_rows]).to_csv(manifest_csv, index=False)

    return Outputs(
        driver_table_csv=driver_csv,
        design_json=design_json,
        summary_json=summary_json,
        memo_md=memo_md,
        figures_manifest_csv=manifest_csv,
    )


def write_outputs(_: Outputs) -> None:
    # For API symmetry with some chapters; this chapter writes inside analyze_ch14.
    return


def _build_cli() -> Any:
    p = base_parser(description=CHAPTER)
    p.add_argument("--datadir", type=Path, required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    p = _build_cli()
    args = p.parse_args(argv)

    outdir = args.outdir
    analyze_ch14(datadir=args.datadir, outdir=outdir, seed=args.seed if args.seed is not None else 123)

    print(f"Wrote Chapter 14 artifacts -> {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
