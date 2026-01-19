# SPDX-License-Identifier: MIT
"""Track D — Chapter 20: Integrated forecasting (P&L + balance sheet + cash tie-out).

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch20_pnl_forecast_monthly.csv
* ch20_balance_sheet_forecast_monthly.csv
* ch20_cash_flow_forecast_monthly.csv
* ch20_assumptions.csv
* ch20_design.json
* ch20_memo.md
* ch20_figures_manifest.csv

This chapter connects the three core statements into one **integrated** forecast:

- Profit & loss (accrual): revenue, costs, and net income.
- Balance sheet (stocks): cash, working capital, debt, equity.
- Cash flow (flows): explain how we get from beginning cash to ending cash.

Key idea (accountant-friendly): a forecast is not "done" until it reconciles.
If the model says profit is up but cash is down, it should be explainable through
working capital, capex, or financing.

Data source: NSO v1 simulator outputs under a folder like ``data/synthetic/nso_v1``.

Outputs are deterministic and written under ``outputs/track_d``.

Guardrails
----------
- These are planning baselines, not causal claims.
- Rates and "days" assumptions (DSO/DIO/DPO) are descriptive of recent history.
- Any reconciliation residual is surfaced explicitly."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import numpy as np
import pandas as pd

from scripts._cli import apply_seed, base_parser
from scripts._reporting_style import FigureManifestRow, FigureSpec, plot_time_series, save_figure, style_context

CHAPTER = "Track D — Chapter 20"


@dataclass(frozen=True)
class Outputs:
    pnl_forecast_monthly_csv: Path
    balance_sheet_forecast_monthly_csv: Path
    cash_flow_forecast_monthly_csv: Path
    assumptions_csv: Path
    design_json: Path
    memo_md: Path
    figures_manifest_csv: Path


IS_LINE_MAP: dict[str, str] = {
    "Sales Revenue": "sales_revenue",
    "Cost of Goods Sold": "cogs",
    "Operating Expenses": "operating_expenses",
    "Net Income": "net_income",
}

BS_LINE_MAP: dict[str, str] = {
    "Cash": "cash",
    "Accounts Receivable": "accounts_receivable",
    "Inventory": "inventory",
    "PP&E (Cost)": "ppe_cost",
    "Accumulated Depreciation": "accumulated_depreciation",
    "Net PP&E": "net_ppe",
    "Accounts Payable": "accounts_payable",
    "Notes Payable": "notes_payable",
    "Wages Payable": "wages_payable",
    "Payroll Taxes Payable": "payroll_taxes_payable",
    "Sales Tax Payable": "sales_tax_payable",
    "Owner Capital": "owner_capital",
    "Owner Draw": "owner_draw",
    "Retained Earnings (Cumulative, derived)": "retained_earnings",
}

CF_LINE_MAP: dict[str, str] = {
    "Add back Depreciation": "add_back_depreciation",
    "Capital Expenditures (cash)": "capex_cash",
    "Owner Draw (cash)": "owner_draw_cash",
}


def _read_csv(datadir: Path, name: str) -> pd.DataFrame:
    path = datadir / name
    if not path.exists():
        raise FileNotFoundError(f"Expected {name} at {path}, but it was not found.")
    return pd.read_csv(path)


def _pivot_statement(df_long: pd.DataFrame, line_map: dict[str, str]) -> pd.DataFrame:
    """Pivot a month/line/amount statement into a wide dataframe with canonical column names."""
    if df_long.empty:
        return pd.DataFrame(columns=["month", *sorted(set(line_map.values()))])

    df = df_long.copy()
    df["month"] = df["month"].astype(str)
    df = df[df["line"].astype(str).isin(line_map.keys())].copy()
    df["line"] = df["line"].astype(str).map(line_map)

    wide = df.pivot_table(index="month", columns="line", values="amount", aggfunc="sum", fill_value=0.0)
    wide = wide.reset_index().sort_values("month").reset_index(drop=True)

    # Ensure all expected columns exist.
    for col in sorted(set(line_map.values())):
        if col not in wide.columns:
            wide[col] = 0.0

    return wide


def _next_months(last_month: str, n: int) -> list[str]:
    p0 = pd.Period(last_month, freq="M")
    return [(p0 + i).strftime("%Y-%m") for i in range(1, n + 1)]


def _safe_ratio(num: pd.Series, den: pd.Series) -> pd.Series:
    den2 = den.replace(0.0, np.nan)
    return (num.astype(float) / den2.astype(float)).replace([np.inf, -np.inf], np.nan)


def _median_clip(x: pd.Series, lo: float, hi: float, default: float) -> float:
    v = pd.to_numeric(x, errors="coerce").dropna()
    if len(v) == 0:
        return float(default)
    m = float(np.nanmedian(v.to_numpy(dtype=float)))
    return float(np.clip(m, lo, hi))


def _estimate_days(ar: pd.Series, inv: pd.Series, ap: pd.Series, rev: pd.Series, cogs: pd.Series) -> dict[str, float]:
    # Simple “days” heuristics from recent history.
    dso = _median_clip(_safe_ratio(ar, rev) * 30.0, lo=0.0, hi=120.0, default=25.0)
    dio = _median_clip(_safe_ratio(inv, cogs) * 30.0, lo=0.0, hi=180.0, default=45.0)
    dpo = _median_clip(_safe_ratio(ap, cogs) * 30.0, lo=0.0, hi=180.0, default=30.0)
    return {"dso": dso, "dio": dio, "dpo": dpo}


def _seasonal_naive_forecast(history: pd.Series, history_months: pd.Series, future_months: list[str]) -> pd.Series:
    """Seasonal naive: for each future month-of-year, use the average of that month in history."""
    df = pd.DataFrame({"month": history_months.astype(str), "y": pd.to_numeric(history, errors="coerce")}).dropna()
    if df.empty:
        return pd.Series([0.0 for _ in future_months], index=future_months, dtype=float)

    df["moy"] = pd.to_datetime(df["month"] + "-01").dt.month
    moy_mean = df.groupby("moy")["y"].mean().to_dict()
    overall = float(df["y"].mean())

    out = []
    for m in future_months:
        moy = int(pd.to_datetime(m + "-01").month)
        out.append(float(moy_mean.get(moy, overall)))
    return pd.Series(out, index=future_months, dtype=float)


def analyze_ch20(datadir: Path, outdir: Path, seed: int = 123) -> Outputs:
    apply_seed(seed)
    outdir.mkdir(parents=True, exist_ok=True)
    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    is_long = _read_csv(datadir, "statements_is_monthly.csv")
    bs_long = _read_csv(datadir, "statements_bs_monthly.csv")
    cf_long = _read_csv(datadir, "statements_cf_monthly.csv")
    debt = _read_csv(datadir, "debt_schedule.csv") if (datadir / "debt_schedule.csv").exists() else pd.DataFrame()

    is_w = _pivot_statement(is_long, IS_LINE_MAP)
    bs_w = _pivot_statement(bs_long, BS_LINE_MAP)
    cf_w = _pivot_statement(cf_long, CF_LINE_MAP)

    if is_w.empty or bs_w.empty:
        raise ValueError("NSO statement tables are empty; cannot run Chapter 20.")

    # Align months on the intersection to avoid mismatched simulator slices.
    months = sorted(set(is_w["month"].tolist()) & set(bs_w["month"].tolist()))
    is_w = is_w[is_w["month"].isin(months)].sort_values("month").reset_index(drop=True)
    bs_w = bs_w[bs_w["month"].isin(months)].sort_values("month").reset_index(drop=True)
    cf_w = cf_w[cf_w["month"].isin(months)].sort_values("month").reset_index(drop=True)

    last_month = str(months[-1])
    future_months = _next_months(last_month, n=12)

    # --- Estimate rates from the last 12 months (or all if fewer).
    tail_n = min(12, len(is_w))
    hist_is = is_w.tail(tail_n).copy()
    hist_bs = bs_w.tail(tail_n).copy()
    hist_cf = cf_w.tail(tail_n).copy()

    rev = hist_is["sales_revenue"].astype(float)
    cogs = hist_is["cogs"].astype(float)
    opex = hist_is["operating_expenses"].astype(float)

    cogs_rate = _median_clip(_safe_ratio(cogs, rev), lo=0.0, hi=2.0, default=0.55)
    opex_rate = _median_clip(_safe_ratio(opex, rev), lo=0.0, hi=2.0, default=0.35)

    days = _estimate_days(
        ar=hist_bs["accounts_receivable"],
        inv=hist_bs["inventory"],
        ap=hist_bs["accounts_payable"],
        rev=rev,
        cogs=cogs,
    )

    dep_avg = _median_clip(hist_cf["add_back_depreciation"], lo=0.0, hi=1e9, default=0.0)
    capex_cash_avg = _median_clip(hist_cf["capex_cash"], lo=-1e9, hi=0.0, default=0.0)
    owner_draw_cash_avg = _median_clip(hist_cf["owner_draw_cash"], lo=-1e9, hi=0.0, default=0.0)

    # Principal repayment heuristic from the debt schedule (if present).
    principal_pay = 0.0
    if not debt.empty and "principal" in debt.columns:
        principal_pay = _median_clip(pd.to_numeric(debt["principal"], errors="coerce"), lo=0.0, hi=1e9, default=0.0)

    # Baseline revenue forecast is seasonal naive.
    rev_fc = _seasonal_naive_forecast(is_w["sales_revenue"], is_w["month"], future_months)

    # Taxes/wages payables held constant (small for NSO v1, but keeps the structure).
    last_state = bs_w.loc[bs_w["month"] == last_month].iloc[0]

    state = {
        "cash": float(last_state["cash"]),
        "accounts_receivable": float(last_state["accounts_receivable"]),
        "inventory": float(last_state["inventory"]),
        "ppe_cost": float(last_state["ppe_cost"]),
        "accumulated_depreciation": float(last_state["accumulated_depreciation"]),
        "accounts_payable": float(last_state["accounts_payable"]),
        "notes_payable": float(last_state["notes_payable"]),
        "wages_payable": float(last_state["wages_payable"]),
        "payroll_taxes_payable": float(last_state["payroll_taxes_payable"]),
        "sales_tax_payable": float(last_state["sales_tax_payable"]),
        "owner_capital": float(last_state["owner_capital"]),
        "owner_draw": float(last_state["owner_draw"]),
        "retained_earnings": float(last_state["retained_earnings"]),
    }

    pnl_rows: list[dict[str, float | str]] = []
    bs_rows: list[dict[str, float | str]] = []
    cf_rows: list[dict[str, float | str]] = []

    for m in future_months:
        beginning = state.copy()

        sales_revenue = float(rev_fc.loc[m])
        cogs_m = float(sales_revenue * cogs_rate)
        opex_m = float(sales_revenue * opex_rate)
        net_income_m = float(sales_revenue - cogs_m - opex_m)

        # Working capital targets from “days” assumptions.
        ar_end = float((sales_revenue / 30.0) * days["dso"] if sales_revenue != 0.0 else beginning["accounts_receivable"])
        inv_end = float((cogs_m / 30.0) * days["dio"] if cogs_m != 0.0 else beginning["inventory"])
        ap_end = float((cogs_m / 30.0) * days["dpo"] if cogs_m != 0.0 else beginning["accounts_payable"])

        # PP&E and depreciation.
        capex_cash = float(capex_cash_avg)
        capex_increase = float(-capex_cash)  # capex_cash is negative (cash out)
        ppe_cost_end = float(beginning["ppe_cost"] + max(capex_increase, 0.0))
        accumulated_depreciation_end = float(beginning["accumulated_depreciation"] - dep_avg)
        net_ppe_end = float(ppe_cost_end + accumulated_depreciation_end)

        # Debt and owner draws.
        notes_end = float(max(0.0, beginning["notes_payable"] - principal_pay))
        net_borrowings = float(notes_end - beginning["notes_payable"])
        owner_draw_cash = float(owner_draw_cash_avg)
        owner_draw_end = float(beginning["owner_draw"] + owner_draw_cash)

        # Equity roll-forward.
        retained_end = float(beginning["retained_earnings"] + net_income_m)
        owner_cap_end = float(beginning["owner_capital"])  # no new contributions in baseline

        # Liabilities held constant except AP and debt.
        wages_payable_end = float(beginning["wages_payable"])
        payroll_taxes_payable_end = float(beginning["payroll_taxes_payable"])
        sales_tax_payable_end = float(beginning["sales_tax_payable"])

        total_liabilities = float(
            ap_end
            + notes_end
            + wages_payable_end
            + payroll_taxes_payable_end
            + sales_tax_payable_end
        )
        total_equity = float(owner_cap_end + retained_end + owner_draw_end)
        total_l_e = float(total_liabilities + total_equity)

        # Balance sheet: cash is the plug that makes A = L + E.
        cash_end = float(total_l_e - (ar_end + inv_end + net_ppe_end))
        total_assets = float(cash_end + ar_end + inv_end + net_ppe_end)

        # Cash flow bridge from components.
        delta_ar = float(ar_end - beginning["accounts_receivable"])
        delta_inv = float(inv_end - beginning["inventory"])
        delta_ap = float(ap_end - beginning["accounts_payable"])
        delta_wages = float(wages_payable_end - beginning["wages_payable"])
        delta_ptx = float(payroll_taxes_payable_end - beginning["payroll_taxes_payable"])
        delta_stx = float(sales_tax_payable_end - beginning["sales_tax_payable"])

        cfo = float(net_income_m + dep_avg - delta_ar - delta_inv + delta_ap + delta_wages + delta_ptx + delta_stx)
        cfi = float(capex_cash)
        cff = float(net_borrowings + owner_draw_cash)
        net_change_components = float(cfo + cfi + cff)
        net_change_actual = float(cash_end - beginning["cash"])
        reconciliation_residual = float(net_change_actual - net_change_components)
        net_change_in_cash = float(net_change_components + reconciliation_residual)

        ending_cash_bridge = float(beginning["cash"] + net_change_in_cash)
        tieout_delta = float(ending_cash_bridge - cash_end)

        pnl_rows.append(
            {
                "month": m,
                "sales_revenue": sales_revenue,
                "cogs": cogs_m,
                "operating_expenses": opex_m,
                "net_income": net_income_m,
            }
        )

        bs_rows.append(
            {
                "month": m,
                "cash": cash_end,
                "accounts_receivable": ar_end,
                "inventory": inv_end,
                "ppe_cost": ppe_cost_end,
                "accumulated_depreciation": accumulated_depreciation_end,
                "net_ppe": net_ppe_end,
                "accounts_payable": ap_end,
                "notes_payable": notes_end,
                "wages_payable": wages_payable_end,
                "payroll_taxes_payable": payroll_taxes_payable_end,
                "sales_tax_payable": sales_tax_payable_end,
                "owner_capital": owner_cap_end,
                "retained_earnings": retained_end,
                "owner_draw": owner_draw_end,
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "total_equity": total_equity,
                "total_liabilities_equity": total_l_e,
                "balance_check": float(total_assets - total_l_e),
            }
        )

        cf_rows.append(
            {
                "month": m,
                "beginning_cash": float(beginning["cash"]),
                "net_income": net_income_m,
                "add_back_depreciation": dep_avg,
                "delta_accounts_receivable": delta_ar,
                "delta_inventory": delta_inv,
                "delta_accounts_payable": delta_ap,
                "delta_wages_payable": delta_wages,
                "delta_payroll_taxes_payable": delta_ptx,
                "delta_sales_tax_payable": delta_stx,
                "net_cash_from_operations": cfo,
                "capex_cash": capex_cash,
                "net_cash_from_investing": cfi,
                "net_borrowings": net_borrowings,
                "owner_draw_cash": owner_draw_cash,
                "net_cash_from_financing": cff,
                "reconciliation_residual": reconciliation_residual,
                "net_change_in_cash": net_change_in_cash,
                "ending_cash_balance_sheet": cash_end,
                "ending_cash_from_bridge": ending_cash_bridge,
                "tieout_delta": tieout_delta,
            }
        )

        # Update state for next month.
        state.update(
            {
                "cash": cash_end,
                "accounts_receivable": ar_end,
                "inventory": inv_end,
                "ppe_cost": ppe_cost_end,
                "accumulated_depreciation": accumulated_depreciation_end,
                "accounts_payable": ap_end,
                "notes_payable": notes_end,
                "wages_payable": wages_payable_end,
                "payroll_taxes_payable": payroll_taxes_payable_end,
                "sales_tax_payable": sales_tax_payable_end,
                "owner_capital": owner_cap_end,
                "owner_draw": owner_draw_end,
                "retained_earnings": retained_end,
            }
        )

    pnl_df = pd.DataFrame(pnl_rows)
    bs_df = pd.DataFrame(bs_rows)
    cf_df = pd.DataFrame(cf_rows)

    pnl_csv = outdir / "ch20_pnl_forecast_monthly.csv"
    bs_csv = outdir / "ch20_balance_sheet_forecast_monthly.csv"
    cf_csv = outdir / "ch20_cash_flow_forecast_monthly.csv"
    assumptions_csv = outdir / "ch20_assumptions.csv"
    design_json = outdir / "ch20_design.json"
    memo_md = outdir / "ch20_memo.md"
    figures_manifest_csv = outdir / "ch20_figures_manifest.csv"

    pnl_df.to_csv(pnl_csv, index=False)
    bs_df.to_csv(bs_csv, index=False)
    cf_df.to_csv(cf_csv, index=False)

    assumptions = pd.DataFrame(
        [
            {"key": "last_actual_month", "value": last_month},
            {"key": "forecast_horizon_months", "value": 12},
            {"key": "revenue_method", "value": "seasonal_naive_month_of_year_mean"},
            {"key": "cogs_rate_median", "value": cogs_rate},
            {"key": "operating_expenses_rate_median", "value": opex_rate},
            {"key": "dso_days_median", "value": days["dso"]},
            {"key": "dio_days_median", "value": days["dio"]},
            {"key": "dpo_days_median", "value": days["dpo"]},
            {"key": "depreciation_monthly_median", "value": dep_avg},
            {"key": "capex_cash_monthly_median", "value": capex_cash_avg},
            {"key": "owner_draw_cash_monthly_median", "value": owner_draw_cash_avg},
            {"key": "principal_payment_monthly_median", "value": principal_pay},
        ]
    )
    assumptions.to_csv(assumptions_csv, index=False)

    design = {
        "chapter": CHAPTER,
        "dataset": "NSO v1 (synthetic)",
        "last_actual_month": last_month,
        "horizon_months": 12,
        "forecast_months": future_months,
        "methods": {
            "revenue": "seasonal naive (month-of-year mean)",
            "cogs": "median cogs/revenue rate",
            "operating_expenses": "median opex/revenue rate",
            "working_capital": "AR/AP/Inventory via DSO/DPO/DIO medians",
            "ppe": "capex cash median, depreciation median",
            "debt": "principal payment median (no new borrowing baseline)",
            "equity": "retained earnings roll-forward via net income; owner draw from history",
        },
        "outputs": {
            "pnl": pnl_csv.name,
            "balance_sheet": bs_csv.name,
            "cash_flow": cf_csv.name,
            "assumptions": assumptions_csv.name,
            "memo": memo_md.name,
            "figures_manifest": figures_manifest_csv.name,
        },
        "style_contract": "scripts/_reporting_style.py (Track D style contract)",
    }
    design_json.write_text(json.dumps(design, indent=2), encoding="utf-8")

    # --- Figures + manifest
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
                    "Integrated forecasts must reconcile across statements. "
                    "Treat rates/days as baselines and stress test key assumptions."
                ),
            )
        )

    # Figure 1: Ending cash (balance sheet) forecast
    with style_context():
        fig = plot_time_series(
            cf_df,
            x="month",
            series={"Ending cash": "ending_cash_balance_sheet"},
            title="Integrated forecast: ending cash by month",
            x_label="Month",
            y_label="Cash",
        )
        spec = FigureSpec(
            chart_type="line",
            title="Integrated forecast: ending cash by month",
            x_label="Month",
            y_label="Cash",
            data_source="statements_is_monthly.csv + statements_bs_monthly.csv",
            notes="Cash is the reconciled outcome of profit, working capital, capex, and financing.",
        )
        fig_path = figures_dir / "ch20_fig_ending_cash_forecast.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    # Figure 2: Net income forecast
    with style_context():
        fig = plot_time_series(
            pnl_df,
            x="month",
            series={"Net income": "net_income"},
            title="Integrated forecast: net income by month",
            x_label="Month",
            y_label="Net income",
            show_zero_line=True,
        )
        spec = FigureSpec(
            chart_type="line",
            title="Integrated forecast: net income by month",
            x_label="Month",
            y_label="Net income",
            data_source="statements_is_monthly.csv",
            notes="Net income is accrual; cash can differ due to working capital and capex.",
        )
        fig_path = figures_dir / "ch20_fig_net_income_forecast.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    pd.DataFrame([r.__dict__ for r in manifest_rows]).to_csv(figures_manifest_csv, index=False)

    # Memo: short, decision-focused.
    residual_max = float(np.max(np.abs(cf_df["reconciliation_residual"].astype(float).to_numpy())))
    memo_md.write_text(
        "\n".join(
            [
                f"# {CHAPTER}: Integrated forecast summary",
                "",
                "This run produced an integrated 12-month forecast that ties the three statements:",
                "- Profit (P&L) → retained earnings (equity)",
                "- Working capital (AR/AP/Inventory) → operating cash flow",
                "- Capex + debt + owner draws → investing/financing cash flow",
                "",
                "## What to look for",
                "- If profit is improving but cash is tightening, check AR/Inventory growth and capex.",
                "- If cash improves without profit, check payables policy, debt changes, or draws.",
                "",
                "## Guardrails",
                "- Rates (COGS%, Opex%) and days (DSO/DIO/DPO) are descriptive baselines.",
                "- Reconciliation residual should be near zero; large residuals indicate missing flows or inconsistent assumptions.",
                "",
                f"Reconciliation residual max (absolute): {residual_max:,.2f}",
            ]
        ),
        encoding="utf-8",
    )

    return Outputs(
        pnl_forecast_monthly_csv=pnl_csv,
        balance_sheet_forecast_monthly_csv=bs_csv,
        cash_flow_forecast_monthly_csv=cf_csv,
        assumptions_csv=assumptions_csv,
        design_json=design_json,
        memo_md=memo_md,
        figures_manifest_csv=figures_manifest_csv,
    )


def _build_cli() -> Any:
    p = base_parser(description=CHAPTER)
    p.add_argument("--datadir", type=Path, required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    p = _build_cli()
    args = p.parse_args(argv)

    analyze_ch20(datadir=args.datadir, outdir=args.outdir, seed=args.seed or 123)
    print("Wrote Chapter 20 artifacts ->", args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
