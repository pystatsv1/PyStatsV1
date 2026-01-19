# SPDX-License-Identifier: MIT
"""Track D — Chapter 18: Expense forecasting (NSO running case).

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch18_expense_monthly_by_account.csv
* ch18_expense_behavior_map.csv
* ch18_payroll_monthly.csv
* ch18_payroll_scenarios_forecast.csv
* ch18_expense_forecast_next12_detail.csv
* ch18_expense_forecast_next12_summary.csv
* ch18_control_plan_template.csv
* ch18_design.json
* ch18_memo.md
* ch18_figures_manifest.csv

Focus:
- classify expenses by cost behavior (fixed / variable / step)
- forecast payroll using a simple scenario model
- produce an accountant-friendly expense control plan template

Reads (from NSO v1 simulator output folder):
- chart_of_accounts.csv
- gl_journal.csv
- payroll_events.csv

Writes (into outdir):
- ch18_expense_monthly_by_account.csv
- ch18_expense_behavior_map.csv
- ch18_payroll_monthly.csv
- ch18_payroll_scenarios_forecast.csv
- ch18_expense_forecast_next12_detail.csv
- ch18_expense_forecast_next12_summary.csv
- ch18_control_plan_template.csv
- ch18_design.json
- ch18_memo.md
- ch18_figures_manifest.csv
- figures/*.png referenced by the manifest

Guardrails:
- This chapter builds planning baselines, not causal claims.
- Coefficients / rates are interpreted as "rules of thumb"."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from scripts._cli import base_parser
from scripts._reporting_style import (
    FigureManifestRow,
    FigureSpec,
    plot_time_series,
    save_figure,
    style_context,
)

CHAPTER = "Track D — Chapter 18"


@dataclass(frozen=True)
class Outputs:
    expense_monthly_by_account_csv: Path
    expense_behavior_map_csv: Path
    payroll_monthly_csv: Path
    payroll_scenarios_forecast_csv: Path
    expense_forecast_detail_csv: Path
    expense_forecast_summary_csv: Path
    control_plan_template_csv: Path
    design_json: Path
    memo_md: Path
    figures_manifest_csv: Path


def _read_csv(datadir: Path, name: str) -> pd.DataFrame:
    path = datadir / name
    if not path.exists():
        raise FileNotFoundError(f"Expected {name} at {path}, but it was not found.")
    return pd.read_csv(path)


def _month_from_date(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series.astype(str), errors="coerce")
    if dt.isna().any():
        raise ValueError("Found invalid dates when building month keys.")
    return dt.dt.to_period("M").astype(str)


def _next_months(last_month: str, n: int) -> list[str]:
    start = pd.Period(str(last_month), freq="M")
    return [str(start + i) for i in range(1, n + 1)]


def _month_of_year(month_str: str) -> int:
    p = pd.Period(month_str, freq="M")
    return int(p.month)


def _behavior_map() -> pd.DataFrame:
    rows = [
        {
            "account_id": "6100",
            "account_name": "Rent Expense",
            "behavior": "fixed",
            "controllable": "mostly",
            "primary_driver": "lease/contract",
            "suggested_method": "flat (recent average)",
            "monitoring_kpi": "rent as % of revenue",
        },
        {
            "account_id": "6200",
            "account_name": "Utilities Expense",
            "behavior": "variable",
            "controllable": "some",
            "primary_driver": "activity + season + rates",
            "suggested_method": "seasonal mean by month-of-year",
            "monitoring_kpi": "utilities per store-day",
        },
        {
            "account_id": "6300",
            "account_name": "Payroll Expense",
            "behavior": "step",
            "controllable": "yes",
            "primary_driver": "headcount × wage × schedule",
            "suggested_method": "scenario baseline (multipliers)",
            "monitoring_kpi": "payroll per revenue or payroll per transaction",
        },
        {
            "account_id": "6500",
            "account_name": "Payroll Tax Expense",
            "behavior": "variable",
            "controllable": "limited",
            "primary_driver": "payroll × employer tax rate",
            "suggested_method": "rate × forecast payroll",
            "monitoring_kpi": "employer tax rate (should be stable)",
        },
        {
            "account_id": "6400",
            "account_name": "Depreciation Expense",
            "behavior": "fixed",
            "controllable": "no (short-run)",
            "primary_driver": "asset base + depreciation policy",
            "suggested_method": "flat (schedule-driven)",
            "monitoring_kpi": "depreciation coverage in budget",
        },
        {
            "account_id": "6600",
            "account_name": "Interest Expense",
            "behavior": "fixed",
            "controllable": "no (short-run)",
            "primary_driver": "debt balance × rate",
            "suggested_method": "flat (recent average)",
            "monitoring_kpi": "interest coverage ratio",
        },
    ]
    return pd.DataFrame(rows)


def _monthly_expenses_from_gl(datadir: Path) -> pd.DataFrame:
    """Build a tidy monthly expense table from the GL.

    Note: NSO v1 gl_journal.csv is already enriched with chart-of-accounts metadata.
    """

    gl = _read_csv(datadir, "gl_journal.csv").copy()

    # month key (YYYY-MM)
    if "month" not in gl.columns:
        gl["month"] = _month_from_date(gl["date"])
    else:
        gl["month"] = gl["month"].astype(str)

    # harmonize metadata column names if they exist with suffixes
    if "account_type" not in gl.columns:
        for c in ("account_type_x", "account_type_y"):
            if c in gl.columns:
                gl["account_type"] = gl[c]
                break
    if "account_name" not in gl.columns:
        for c in ("account_name_x", "account_name_y"):
            if c in gl.columns:
                gl["account_name"] = gl[c]
                break

    if "account_type" not in gl.columns or "account_name" not in gl.columns:
        raise ValueError(
            "Expected gl_journal.csv to contain account_name/account_type columns (NSO v1 contract)."
        )

    # Expenses are debits (positive) for normal usage.
    gl["amount"] = gl["debit"].astype(float) - gl["credit"].astype(float)

    exp = gl.loc[gl["account_type"].astype(str) == "Expense"].copy()
    exp = exp.loc[exp["account_id"].astype(str) != "5000"].copy()  # exclude COGS

    m = (
        exp.groupby(["month", "account_id", "account_name"], as_index=False)["amount"]
        .sum()
        .sort_values(["month", "account_id"])
        .reset_index(drop=True)
    )

    # Wide for plotting + easier scanning
    wide = (
        m.pivot_table(index="month", columns="account_id", values="amount", aggfunc="sum", fill_value=0.0)
        .reset_index()
        .sort_values("month")
        .reset_index(drop=True)
    )

    # Add month keys
    wide["month_of_year"] = wide["month"].map(_month_of_year)

    # Stable expense columns for the major NSO accounts (keep stable even if zeros)
    mapping = {
        "6100": "rent_expense",
        "6200": "utilities_expense",
        "6300": "payroll_expense",
        "6400": "depreciation_expense",
        "6500": "payroll_tax_expense",
        "6600": "interest_expense",
    }
    for acc, col in mapping.items():
        if acc not in wide.columns:
            wide[acc] = 0.0
        wide = wide.rename(columns={acc: col})

    wide["operating_expenses_total"] = (
        wide[list(mapping.values())].astype(float).sum(axis=1)
    )

    cols = ["month", "month_of_year", *mapping.values(), "operating_expenses_total"]
    return wide[cols].copy()



def _payroll_monthly(datadir: Path) -> pd.DataFrame:
    pe = _read_csv(datadir, "payroll_events.csv")
    pe = pe.copy()

    if "month" not in pe.columns:
        pe["month"] = _month_from_date(pe["date"])

    accr = pe.loc[pe["event_type"].astype(str) == "payroll_accrual"].copy()
    tax = pe.loc[pe["event_type"].astype(str) == "payroll_tax_accrual"].copy()

    gross = accr.groupby("month", as_index=False)["gross_wages"].sum().rename(columns={"gross_wages": "gross_wages"})
    emp_tax = tax.groupby("month", as_index=False)["employer_tax"].sum().rename(columns={"employer_tax": "employer_tax"})

    df = gross.merge(emp_tax, on="month", how="outer").fillna(0.0)
    df = df.sort_values("month").reset_index(drop=True)
    df["total_payroll_cost"] = df["gross_wages"].astype(float) + df["employer_tax"].astype(float)

    # rate is only meaningful when gross is non-zero
    df["employer_tax_rate"] = np.where(
        df["gross_wages"].astype(float) > 0,
        df["employer_tax"].astype(float) / df["gross_wages"].astype(float),
        np.nan,
    )

    return df


def _forecast_fixed(history: pd.Series, fallback: float = 0.0) -> float:
    h = history.astype(float)
    h = h.replace([np.inf, -np.inf], np.nan).dropna()
    if len(h) == 0:
        return float(fallback)
    # recent average is more stable than a single last value
    tail = h.tail(min(12, len(h)))
    return float(tail.mean())


def _forecast_seasonal_mean(history_df: pd.DataFrame, value_col: str, months_forecast: list[str]) -> pd.Series:
    tmp = history_df[["month", "month_of_year", value_col]].copy()
    means = tmp.groupby("month_of_year", as_index=False)[value_col].mean()

    out_rows: list[dict[str, object]] = []
    for m in months_forecast:
        moy = _month_of_year(m)
        hit = means.loc[means["month_of_year"] == moy]
        val = float(hit[value_col].iloc[0]) if not hit.empty else float(tmp[value_col].mean())
        out_rows.append({"month": m, value_col: val})

    return pd.DataFrame(out_rows).set_index("month")[value_col]


def analyze_ch18(
    datadir: Path,
    outdir: Path,
    seed: int = 123,
    wage_inflation_monthly: float = 0.002,
) -> Outputs:
    """Run Chapter 18 analysis and write outputs into outdir."""

    outdir.mkdir(parents=True, exist_ok=True)
    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    expense_history = _monthly_expenses_from_gl(datadir)
    payroll_history = _payroll_monthly(datadir)

    months = expense_history["month"].tolist()
    if len(months) < 12:
        raise ValueError(f"Chapter 18 requires at least 12 months of data; got {len(months)}.")

    last_month = str(months[-1])
    horizon = 12
    months_fc = _next_months(last_month, horizon)

    # --- Payroll scenario model (headcount/wage changes modeled as multipliers) ---
    scenarios: dict[str, float] = {
        "Lean": 0.90,
        "Base": 1.00,
        "Growth": 1.15,
    }

    baseline_gross = float(payroll_history["gross_wages"].tail(12).mean())

    rate_series = payroll_history["employer_tax_rate"].replace([np.inf, -np.inf], np.nan).dropna()
    employer_tax_rate = float(rate_series.mean()) if len(rate_series) > 0 else 0.08

    payroll_fc_rows: list[dict[str, object]] = []
    for scenario, mult in scenarios.items():
        for i, m in enumerate(months_fc):
            infl = float((1.0 + wage_inflation_monthly) ** i)
            gross = float(baseline_gross * mult * infl)
            emp_tax = float(gross * employer_tax_rate)
            payroll_fc_rows.append(
                {
                    "month": m,
                    "scenario": scenario,
                    "payroll_multiplier": float(mult),
                    "wage_inflation_monthly": float(wage_inflation_monthly),
                    "forecast_gross_wages": gross,
                    "forecast_employer_tax": emp_tax,
                    "forecast_total_payroll_cost": float(gross + emp_tax),
                }
            )

    payroll_fc = pd.DataFrame(payroll_fc_rows)

    # --- Other expense forecasts (simple explainable baselines) ---
    rent_fixed = _forecast_fixed(expense_history["rent_expense"])
    dep_fixed = _forecast_fixed(expense_history["depreciation_expense"])
    int_fixed = _forecast_fixed(expense_history["interest_expense"])

    util_fc = _forecast_seasonal_mean(expense_history, "utilities_expense", months_fc)

    # Build forecast detail + summary
    behavior = _behavior_map()

    detail_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for scenario in scenarios.keys():
        psub = payroll_fc.loc[payroll_fc["scenario"] == scenario].copy()
        psub = psub.sort_values("month")
        psub = psub.set_index("month")

        for m in months_fc:
            payroll_amt = float(psub.loc[m, "forecast_gross_wages"])
            payroll_tax_amt = float(psub.loc[m, "forecast_employer_tax"])

            row_fixed = {
                "rent_expense": rent_fixed,
                "utilities_expense": float(util_fc.loc[m]),
                "payroll_expense": payroll_amt,
                "payroll_tax_expense": payroll_tax_amt,
                "depreciation_expense": dep_fixed,
                "interest_expense": int_fixed,
            }

            total = float(sum(row_fixed.values()))
            controllable = float(row_fixed["rent_expense"] + row_fixed["utilities_expense"] + row_fixed["payroll_expense"] + row_fixed["payroll_tax_expense"])

            summary_rows.append(
                {
                    "month": m,
                    "scenario": scenario,
                    **row_fixed,
                    "operating_expenses_total": total,
                    "controllable_expenses_total": controllable,
                }
            )

        # detail rows per account
        for m in months_fc:
            detail_rows.extend(
                [
                    {
                        "month": m,
                        "scenario": scenario,
                        "account_id": "6100",
                        "account_name": "Rent Expense",
                        "behavior": "fixed",
                        "forecast_method": "flat_recent_avg",
                        "forecast_amount": float(rent_fixed),
                    },
                    {
                        "month": m,
                        "scenario": scenario,
                        "account_id": "6200",
                        "account_name": "Utilities Expense",
                        "behavior": "variable",
                        "forecast_method": "seasonal_mean_moy",
                        "forecast_amount": float(util_fc.loc[m]),
                    },
                    {
                        "month": m,
                        "scenario": scenario,
                        "account_id": "6300",
                        "account_name": "Payroll Expense",
                        "behavior": "step",
                        "forecast_method": "scenario_multiplier_inflation",
                        "forecast_amount": float(psub.loc[m, "forecast_gross_wages"]),
                    },
                    {
                        "month": m,
                        "scenario": scenario,
                        "account_id": "6500",
                        "account_name": "Payroll Tax Expense",
                        "behavior": "variable",
                        "forecast_method": "rate_x_payroll",
                        "forecast_amount": float(psub.loc[m, "forecast_employer_tax"]),
                    },
                    {
                        "month": m,
                        "scenario": scenario,
                        "account_id": "6400",
                        "account_name": "Depreciation Expense",
                        "behavior": "fixed",
                        "forecast_method": "flat_recent_avg",
                        "forecast_amount": float(dep_fixed),
                    },
                    {
                        "month": m,
                        "scenario": scenario,
                        "account_id": "6600",
                        "account_name": "Interest Expense",
                        "behavior": "fixed",
                        "forecast_method": "flat_recent_avg",
                        "forecast_amount": float(int_fixed),
                    },
                ]
            )

    forecast_detail = pd.DataFrame(detail_rows)
    forecast_summary = pd.DataFrame(summary_rows)

    # Control plan template (filled-in placeholders students can edit)
    control_rows = [
        {
            "expense_group": "Payroll (gross + employer tax)",
            "primary_driver": "headcount × wage × schedule",
            "controllable": "yes",
            "monitoring_kpi": "payroll per revenue; payroll per transaction",
            "owner": "",
            "review_cadence": "weekly",
            "notes": "What staffing decisions change this line?",
        },
        {
            "expense_group": "Rent",
            "primary_driver": "lease contract",
            "controllable": "mostly",
            "monitoring_kpi": "rent as % of revenue",
            "owner": "",
            "review_cadence": "monthly",
            "notes": "Renewals, sublease options, or space optimization.",
        },
        {
            "expense_group": "Utilities",
            "primary_driver": "activity + season + rates",
            "controllable": "some",
            "monitoring_kpi": "utilities per store-day",
            "owner": "",
            "review_cadence": "monthly",
            "notes": "Watch rate changes and seasonal spikes.",
        },
        {
            "expense_group": "Depreciation",
            "primary_driver": "asset base + policy",
            "controllable": "no (short-run)",
            "monitoring_kpi": "capex plan vs budget",
            "owner": "",
            "review_cadence": "quarterly",
            "notes": "Forecast tied to depreciation schedule.",
        },
        {
            "expense_group": "Interest",
            "primary_driver": "debt × rate",
            "controllable": "no (short-run)",
            "monitoring_kpi": "interest coverage ratio",
            "owner": "",
            "review_cadence": "monthly",
            "notes": "Refinancing is a structural change; document assumptions.",
        },
    ]
    control_plan = pd.DataFrame(control_rows)

    # --- Write outputs ---
    expense_monthly_by_account_csv = outdir / "ch18_expense_monthly_by_account.csv"
    expense_behavior_map_csv = outdir / "ch18_expense_behavior_map.csv"
    payroll_monthly_csv = outdir / "ch18_payroll_monthly.csv"
    payroll_scenarios_forecast_csv = outdir / "ch18_payroll_scenarios_forecast.csv"
    expense_forecast_detail_csv = outdir / "ch18_expense_forecast_next12_detail.csv"
    expense_forecast_summary_csv = outdir / "ch18_expense_forecast_next12_summary.csv"
    control_plan_template_csv = outdir / "ch18_control_plan_template.csv"
    design_json = outdir / "ch18_design.json"
    memo_md = outdir / "ch18_memo.md"
    figures_manifest_csv = outdir / "ch18_figures_manifest.csv"

    expense_history.to_csv(expense_monthly_by_account_csv, index=False)
    behavior.to_csv(expense_behavior_map_csv, index=False)
    payroll_history.to_csv(payroll_monthly_csv, index=False)
    payroll_fc.to_csv(payroll_scenarios_forecast_csv, index=False)
    forecast_detail.to_csv(expense_forecast_detail_csv, index=False)
    forecast_summary.to_csv(expense_forecast_summary_csv, index=False)
    control_plan.to_csv(control_plan_template_csv, index=False)

    design = {
        "chapter": CHAPTER,
        "seed": seed,
        "history_months": months,
        "forecast_months": months_fc,
        "horizon_months": horizon,
        "forecast_horizon_months": horizon,
        "scenario_multipliers": scenarios,
        "payroll_scenarios": scenarios,
        "baseline_payroll_gross_recent_avg_12m": baseline_gross,
        "employer_tax_rate_estimate": employer_tax_rate,
        "wage_inflation_monthly": wage_inflation_monthly,
        "notes": [
            "Fixed costs forecasted as a recent average (simple baseline).",
            "Utilities forecasted by month-of-year seasonal mean.",
            "Payroll forecasted via scenario multipliers + wage inflation.",
        ],
    }
    design_json.write_text(json.dumps(design, indent=2), encoding="utf-8")

    memo_lines = [
        "# Chapter 18 Expense Forecast Memo (fixed / variable / step)\n\n",
        "This memo provides a **planning baseline** for key operating expenses.\n",
        "It is not a causal model. Treat rates and multipliers as **rules of thumb**.\n\n",
        "## Expense behavior map\n\n",
        behavior.to_markdown(index=False),
        "\n\n",
        "## Payroll model (scenario-based)\n\n",
        f"- Baseline gross wages: {baseline_gross:,.0f} per month (recent 12-month average)\n",
        f"- Estimated employer tax rate: {employer_tax_rate:.3f}\n",
        f"- Wage inflation assumption: {wage_inflation_monthly:.3%} per month\n\n",
        "Scenarios are implemented as multipliers applied to baseline payroll.\n\n",
        "## Next 12 months: expense forecast summary (by scenario)\n\n",
        forecast_summary.to_markdown(index=False),
        "\n\n",
        "## Control plan template\n\n",
        "Use this template during month-end close to connect expense monitoring to owners and cadence.\n\n",
        control_plan.to_markdown(index=False),
        "\n\n",
        "## Guardrails\n\n",
        "- If payroll changes (hiring/layoffs), update scenario multipliers and document the decision.\n",
        "- If utilities are rate-driven (not activity-driven), treat it as a known event rather than noise.\n",
        "- Keep a versioned assumptions log when sharing forecasts externally.\n",
    ]
    memo_md.write_text("".join(memo_lines), encoding="utf-8")

    # --- Figures + manifest ---
    manifest_rows: list[FigureManifestRow] = []

    def _add_row(fig_path: Path, spec: FigureSpec) -> None:
        manifest_rows.append(
            FigureManifestRow(
                filename=fig_path.name,
                chart_type=spec.chart_type,
                title=spec.title,
                x_label=spec.x_label,
                y_label=spec.y_label,
                data_source="NSO v1 synthetic outputs",
                guardrail_note=(
                    "Forecasts are planning baselines. Confirm assumptions, "
                    "contracts, and staffing decisions before acting."
                ),
            )
        )

    with style_context():
        fig = plot_time_series(
            expense_history,
            x="month",
            series={
                "Rent": "rent_expense",
                "Utilities": "utilities_expense",
                "Payroll": "payroll_expense",
                "Payroll tax": "payroll_tax_expense",
                "Depreciation": "depreciation_expense",
                "Interest": "interest_expense",
            },
            title="Operating expense history by category",
            x_label="Month",
            y_label="Expense (debit amounts)",
        )
        spec = FigureSpec(
            chart_type="line",
            title="Operating expense history by category",
            x_label="Month",
            y_label="Expense (debit amounts)",
            data_source="gl_journal.csv + chart_of_accounts.csv",
            notes="COGS excluded; shows major operating expense categories.",
        )
        fig_path = figures_dir / "ch18_fig_expense_history_by_category.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    # Payroll scenarios (total payroll cost)
    scen_wide = (
        payroll_fc.pivot_table(
            index="month",
            columns="scenario",
            values="forecast_total_payroll_cost",
            aggfunc="mean",
            fill_value=0.0,
        )
        .reset_index()
        .sort_values("month")
        .reset_index(drop=True)
    )

    series_map = {f"Payroll cost ({c})": c for c in ["Lean", "Base", "Growth"] if c in scen_wide.columns}

    with style_context():
        fig = plot_time_series(
            scen_wide,
            x="month",
            series=series_map,
            title="Payroll forecast scenarios (next 12 months)",
            x_label="Month",
            y_label="Total payroll cost",
        )
        spec = FigureSpec(
            chart_type="line",
            title="Payroll forecast scenarios (next 12 months)",
            x_label="Month",
            y_label="Total payroll cost",
            data_source="payroll_events.csv (historical) + scenario model",
            notes="Scenario multipliers model step-cost behavior in staffing.",
        )
        fig_path = figures_dir / "ch18_fig_payroll_scenarios_next12.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    pd.DataFrame([r.__dict__ for r in manifest_rows]).to_csv(figures_manifest_csv, index=False)

    return Outputs(
        expense_monthly_by_account_csv=expense_monthly_by_account_csv,
        expense_behavior_map_csv=expense_behavior_map_csv,
        payroll_monthly_csv=payroll_monthly_csv,
        payroll_scenarios_forecast_csv=payroll_scenarios_forecast_csv,
        expense_forecast_detail_csv=expense_forecast_detail_csv,
        expense_forecast_summary_csv=expense_forecast_summary_csv,
        control_plan_template_csv=control_plan_template_csv,
        design_json=design_json,
        memo_md=memo_md,
        figures_manifest_csv=figures_manifest_csv,
    )


def _build_cli() -> Any:
    p = base_parser(description=CHAPTER)
    p.add_argument("--datadir", type=Path, required=True)
    p.add_argument(
        "--wage-inflation-monthly",
        type=float,
        default=0.002,
        help="Monthly wage inflation assumption for payroll scenarios (default: 0.002 = 0.2%).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    p = _build_cli()
    args = p.parse_args(argv)
    analyze_ch18(
        datadir=args.datadir,
        outdir=args.outdir,
        seed=args.seed or 123,
        wage_inflation_monthly=float(args.wage_inflation_monthly),
    )
    print("Wrote Chapter 18 artifacts ->", args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
