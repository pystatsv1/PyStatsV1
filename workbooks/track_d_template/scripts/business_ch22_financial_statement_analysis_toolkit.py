# SPDX-License-Identifier: MIT
"""Track D — Chapter 22: Financial statement analysis toolkit.

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch22_ratios_monthly.csv
* ch22_common_size_is.csv
* ch22_common_size_bs.csv
* ch22_variance_bridge_latest.csv
* ch22_assumptions.csv
* ch22_figures_manifest.csv
* ch22_memo.md
* ch22_design.json

This chapter provides an accountant-friendly toolkit to move from *close* to *explain*:

* **Ratios** (liquidity, leverage, profitability, efficiency)
* **Trends** (levels, percent changes, rolling summaries)
* **Common-size** statements (normalize to revenue / total assets)
* **Variance** bridges (what drove the change month-over-month)

The NSO v1 simulator provides monthly income statement, balance sheet, and cash flow tables.
We treat these as the inputs, and produce deterministic, analysis-ready outputs under
``outputs/track_d``.

Guardrails:

* Ratios are **descriptive**, not causal.
* Always sanity-check denominators (small revenue months can create wild percentages).
* Use working-capital context (AR / Inventory / AP) before declaring a "real" improvement.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import numpy as np
import pandas as pd

from scripts._cli import apply_seed, base_parser
from scripts._reporting_style import (
    FigureManifestRow,
    FigureSpec,
    plot_time_series,
    plot_waterfall_bridge,
    save_figure,
    style_context,
)

CHAPTER = "Track D — Chapter 22"
DAYS_PER_MONTH = 28.0  # teaching-friendly constant (matches earlier Track D chapters)


@dataclass(frozen=True)
class Outputs:
    ratios_monthly_csv: Path
    common_size_is_csv: Path
    common_size_bs_csv: Path
    variance_bridge_latest_csv: Path
    assumptions_csv: Path
    design_json: Path
    memo_md: Path
    figures_manifest_csv: Path


def _read_statement(datadir: Path, filename: str) -> pd.DataFrame:
    p = datadir / filename
    if not p.exists():
        raise FileNotFoundError(f"Missing required NSO table: {p}")
    df = pd.read_csv(p)
    if not {"month", "line", "amount"}.issubset(df.columns):
        raise ValueError(f"{filename} must have columns: month, line, amount")
    df = df.copy()
    df["month"] = df["month"].astype(str)
    df["line"] = df["line"].astype(str)
    df["amount"] = df["amount"].astype(float)
    return df


def _wide_by_line(df: pd.DataFrame, *, lines: list[str]) -> pd.DataFrame:
    """Return a month-indexed wide table for the requested statement lines."""
    sub = df.loc[df["line"].isin(lines)].copy()
    wide = sub.pivot_table(index="month", columns="line", values="amount", aggfunc="sum")
    # Ensure missing lines become explicit NaN columns (deterministic schema)
    for ln in lines:
        if ln not in wide.columns:
            wide[ln] = np.nan
    wide = wide[lines].reset_index()
    wide = wide.sort_values("month").reset_index(drop=True)
    return wide


def _safe_div(n: pd.Series, d: pd.Series) -> pd.Series:
    d = d.replace(0.0, np.nan)
    return n / d


def _build_ratios(is_wide: pd.DataFrame, bs_wide: pd.DataFrame) -> pd.DataFrame:
    # Income statement
    revenue = is_wide["Sales Revenue"].astype(float)
    cogs = is_wide["Cost of Goods Sold"].astype(float)
    opex = is_wide["Operating Expenses"].astype(float)
    net_income = is_wide["Net Income"].astype(float)

    # Balance sheet
    cash = bs_wide["Cash"].astype(float)
    ar = bs_wide["Accounts Receivable"].astype(float)
    inv = bs_wide["Inventory"].astype(float)
    ap = bs_wide["Accounts Payable"].astype(float)
    sales_tax = bs_wide["Sales Tax Payable"].astype(float)
    wages_payable = bs_wide["Wages Payable"].astype(float)
    payroll_taxes = bs_wide["Payroll Taxes Payable"].astype(float)
    notes_payable = bs_wide["Notes Payable"].astype(float)
    total_assets = bs_wide["Total Assets"].astype(float)
    total_equity = bs_wide["Total Equity"].astype(float)

    current_assets = cash + ar + inv
    current_liabilities = ap + sales_tax + wages_payable + payroll_taxes

    gross_profit = revenue - cogs

    # Core ratios
    ratios = pd.DataFrame(
        {
            "month": is_wide["month"].astype(str),
            "sales_revenue": revenue,
            "cogs": cogs,
            "operating_expenses": opex,
            "net_income": net_income,
            "gross_margin": _safe_div(gross_profit, revenue),
            "operating_margin": _safe_div(net_income, revenue),
            "opex_ratio": _safe_div(opex, revenue),
            "current_ratio": _safe_div(current_assets, current_liabilities),
            "quick_ratio": _safe_div(cash + ar, current_liabilities),
            "debt_to_equity": _safe_div(notes_payable, total_equity),
            "dso_days": _safe_div(ar, _safe_div(revenue, pd.Series(DAYS_PER_MONTH, index=revenue.index))),
            "dio_days": _safe_div(inv, _safe_div(cogs, pd.Series(DAYS_PER_MONTH, index=cogs.index))),
            "dpo_days": _safe_div(ap, _safe_div(cogs, pd.Series(DAYS_PER_MONTH, index=cogs.index))),
            "cash_conversion_cycle_days": np.nan,
            "total_assets": total_assets,
            "total_equity": total_equity,
            "notes_payable": notes_payable,
            "current_assets": current_assets,
            "current_liabilities": current_liabilities,
        }
    )

    # Alias for tests/docs: use a generic "revenue" column name
    if "revenue" not in ratios.columns:
        ratios["revenue"] = ratios["sales_revenue"]

    ratios["cash_conversion_cycle_days"] = ratios["dso_days"] + ratios["dio_days"] - ratios["dpo_days"]

    # Add simple MoM deltas for a few KPIs
    for col in ["sales_revenue", "net_income", "current_ratio", "debt_to_equity", "cash_conversion_cycle_days"]:
        ratios[f"delta_{col}"] = ratios[col].diff()

    # Trailing 12-month rollups (annualized / averages) for a few stable measures
    # These are useful for statements analysis where single months can be noisy.
    ratios["ttm_revenue"] = ratios["sales_revenue"].rolling(12, min_periods=6).sum()
    ratios["avg_total_assets_12m"] = ratios["total_assets"].rolling(12, min_periods=6).mean()
    ratios["asset_turnover_annual"] = _safe_div(ratios["ttm_revenue"], ratios["avg_total_assets_12m"])
    ratios["roa_annual"] = _safe_div(ratios["net_income"].rolling(12, min_periods=6).sum(), ratios["avg_total_assets_12m"])

    return ratios


def _common_size_is(is_df: pd.DataFrame) -> pd.DataFrame:
    wide = is_df.pivot_table(index="month", columns="line", values="amount", aggfunc="sum")
    revenue = wide.get("Sales Revenue")
    if revenue is None:
        raise ValueError("Income statement missing 'Sales Revenue'")

    out_rows: list[dict[str, Any]] = []
    for month, row in wide.sort_index().iterrows():
        rev = float(row.get("Sales Revenue", np.nan))
        for line, amt in row.items():
            amt_f = float(amt) if pd.notna(amt) else np.nan
            pct = (amt_f / rev) if (pd.notna(amt_f) and rev not in (0.0, np.nan)) else np.nan
            out_rows.append(
                {
                    "month": str(month),
                    "line": str(line),
                    "amount": amt_f,
                    "pct_of_revenue": pct,
                }
            )

    out = pd.DataFrame(out_rows)
    out = out.sort_values(["month", "line"]).reset_index(drop=True)
    return out


def _common_size_bs(bs_df: pd.DataFrame) -> pd.DataFrame:
    wide = bs_df.pivot_table(index="month", columns="line", values="amount", aggfunc="sum")
    total_assets = wide.get("Total Assets")
    if total_assets is None:
        raise ValueError("Balance sheet missing 'Total Assets'")

    out_rows: list[dict[str, Any]] = []
    for month, row in wide.sort_index().iterrows():
        ta = float(row.get("Total Assets", np.nan))
        for line, amt in row.items():
            amt_f = float(amt) if pd.notna(amt) else np.nan
            pct = (amt_f / ta) if (pd.notna(amt_f) and ta not in (0.0, np.nan)) else np.nan
            out_rows.append(
                {
                    "month": str(month),
                    "line": str(line),
                    "amount": amt_f,
                    "pct_of_total_assets": pct,
                }
            )

    out = pd.DataFrame(out_rows)
    out = out.sort_values(["month", "line"]).reset_index(drop=True)
    return out


def _variance_bridge_latest(is_wide: pd.DataFrame) -> pd.DataFrame:
    if len(is_wide) < 2:
        return pd.DataFrame(columns=["component", "amount"])

    cur = is_wide.iloc[-1]
    prev = is_wide.iloc[-2]

    # Components explained in a way that matches the income statement identity.
    # Start at prior net income, then add changes in:
    #   + Revenue
    #   - COGS
    #   - Opex
    start = float(prev["Net Income"])
    end = float(cur["Net Income"])

    delta_rev = float(cur["Sales Revenue"] - prev["Sales Revenue"])
    delta_cogs = float(cur["Cost of Goods Sold"] - prev["Cost of Goods Sold"])
    delta_opex = float(cur["Operating Expenses"] - prev["Operating Expenses"])

    comp_rows = [
        {"component": "Start (prior net income)", "amount": start},
        {"component": "Revenue change", "amount": delta_rev},
        {"component": "COGS change (higher costs reduce NI)", "amount": -delta_cogs},
        {"component": "Opex change (higher opex reduces NI)", "amount": -delta_opex},
    ]

    implied_end = start + delta_rev - delta_cogs - delta_opex
    residual = float(end - implied_end)
    if abs(residual) > 1e-6:
        comp_rows.append({"component": "Other / rounding", "amount": residual})

    comp_rows.append({"component": "End (current net income)", "amount": end})

    return pd.DataFrame(comp_rows)


def _assumptions_table() -> pd.DataFrame:
    rows = [
        ("gross_margin", "(Revenue - COGS) / Revenue", "Profitability"),
        ("operating_margin", "Net Income / Revenue", "Profitability"),
        ("opex_ratio", "Operating Expenses / Revenue", "Profitability"),
        ("current_ratio", "(Cash + AR + Inventory) / Current Liabilities", "Liquidity"),
        ("quick_ratio", "(Cash + AR) / Current Liabilities", "Liquidity"),
        ("debt_to_equity", "Notes Payable / Total Equity", "Leverage"),
        ("dso_days", "AR / (Revenue / 28)", "Efficiency"),
        ("dio_days", "Inventory / (COGS / 28)", "Efficiency"),
        ("dpo_days", "AP / (COGS / 28)", "Efficiency"),
        ("cash_conversion_cycle_days", "DSO + DIO - DPO", "Efficiency"),
        ("asset_turnover_annual", "TTM Revenue / avg Total Assets (12m)", "Efficiency"),
        ("roa_annual", "TTM Net Income / avg Total Assets (12m)", "Profitability"),
    ]

    return pd.DataFrame(rows, columns=["metric", "definition", "category"])


def analyze_ch22(*, datadir: Path, outdir: Path, seed: int | None = None) -> Outputs:
    apply_seed(seed)

    outdir.mkdir(parents=True, exist_ok=True)
    figdir = outdir / "figures"
    figdir.mkdir(parents=True, exist_ok=True)

    is_df = _read_statement(datadir, "statements_is_monthly.csv")
    bs_df = _read_statement(datadir, "statements_bs_monthly.csv")
    cf_df = _read_statement(datadir, "statements_cf_monthly.csv")

    is_lines = ["Sales Revenue", "Cost of Goods Sold", "Operating Expenses", "Net Income"]
    bs_lines = [
        "Cash",
        "Accounts Receivable",
        "Inventory",
        "Accounts Payable",
        "Sales Tax Payable",
        "Wages Payable",
        "Payroll Taxes Payable",
        "Notes Payable",
        "Total Assets",
        "Total Equity",
    ]

    is_wide = _wide_by_line(is_df, lines=is_lines)
    bs_wide = _wide_by_line(bs_df, lines=bs_lines)

    # Ensure month alignment (outer join, deterministic ordering)
    wide = is_wide.merge(bs_wide, on="month", how="outer", suffixes=("_is", "_bs"))
    wide = wide.sort_values("month").reset_index(drop=True)

    # Re-split wide for ratio builder (expects original columns)
    is_wide_aligned = wide[["month"] + is_lines].copy()
    bs_wide_aligned = wide[["month"] + bs_lines].copy()

    ratios = _build_ratios(is_wide_aligned, bs_wide_aligned)
    ratios_monthly_csv = outdir / "ch22_ratios_monthly.csv"
    ratios.to_csv(ratios_monthly_csv, index=False)

    cs_is = _common_size_is(is_df)
    common_size_is_csv = outdir / "ch22_common_size_is.csv"
    cs_is.to_csv(common_size_is_csv, index=False)

    cs_bs = _common_size_bs(bs_df)
    common_size_bs_csv = outdir / "ch22_common_size_bs.csv"
    cs_bs.to_csv(common_size_bs_csv, index=False)

    bridge = _variance_bridge_latest(is_wide_aligned)
    variance_bridge_latest_csv = outdir / "ch22_variance_bridge_latest.csv"
    bridge.to_csv(variance_bridge_latest_csv, index=False)

    assumptions = _assumptions_table()
    assumptions_csv = outdir / "ch22_assumptions.csv"
    assumptions.to_csv(assumptions_csv, index=False)

    # Small "cosmetic improvement" flag for the last month
    cf_wide = _wide_by_line(cf_df, lines=["Net Change in Cash"])
    cf_wide = cf_wide.sort_values("month").reset_index(drop=True)
    net_change_cash_last = float(cf_wide.iloc[-1]["Net Change in Cash"]) if len(cf_wide) else np.nan

    # -------------------------------
    # Figures + manifest
    # -------------------------------
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
                guardrail_note=(
                    "Ratios are signals, not proofs. Avoid causal overclaiming; "
                    "validate with reconciliations and operational detail."
                ),
            )
        )

    with style_context():
        # Profitability (margins)
        fig1 = plot_time_series(
            ratios,
            x="month",
            series={
                "Gross margin": "gross_margin",
                "Operating margin": "operating_margin",
            },
            title="Chapter 22 — Profitability (gross vs operating margin)",
            x_label="Month",
            y_label="Ratio",
            show_zero_line=True,
        )
        spec1 = FigureSpec(
            chart_type="line",
            title="Chapter 22 — Profitability (gross vs operating margin)",
            x_label="Month",
            y_label="Ratio",
            data_source="statements_is_monthly.csv",
            notes="Margins summarize price/cost vs overhead; treat as signals.",
        )
        fig1_path = figdir / "ch22_fig_profitability_margins.png"
        save_figure(fig1, fig1_path, spec=spec1)
        _add_row(fig1_path, spec1)

        # Liquidity
        fig2 = plot_time_series(
            ratios,
            x="month",
            series={
                "Current ratio": "current_ratio",
                "Quick ratio": "quick_ratio",
            },
            title="Chapter 22 — Liquidity (current vs quick ratio)",
            x_label="Month",
            y_label="Ratio",
            show_zero_line=True,
        )
        spec2 = FigureSpec(
            chart_type="line",
            title="Chapter 22 — Liquidity (current vs quick ratio)",
            x_label="Month",
            y_label="Ratio",
            data_source="statements_bs_monthly.csv",
            notes="Liquidity ratios depend on current assets and current liabilities.",
        )
        fig2_path = figdir / "ch22_fig_liquidity_ratios.png"
        save_figure(fig2, fig2_path, spec=spec2)
        _add_row(fig2_path, spec2)

        # Leverage
        fig3 = plot_time_series(
            ratios,
            x="month",
            series={"Debt to equity": "debt_to_equity"},
            title="Chapter 22 — Leverage (debt-to-equity)",
            x_label="Month",
            y_label="Ratio",
            show_zero_line=True,
        )
        spec3 = FigureSpec(
            chart_type="line",
            title="Chapter 22 — Leverage (debt-to-equity)",
            x_label="Month",
            y_label="Ratio",
            data_source="statements_bs_monthly.csv",
            notes="Debt-to-equity uses Notes Payable and Total Equity.",
        )
        fig3_path = figdir / "ch22_fig_debt_to_equity.png"
        save_figure(fig3, fig3_path, spec=spec3)
        _add_row(fig3_path, spec3)

        # Efficiency (cash conversion cycle)
        fig4 = plot_time_series(
            ratios,
            x="month",
            series={
                "DSO": "dso_days",
                "DIO": "dio_days",
                "DPO": "dpo_days",
                "CCC": "cash_conversion_cycle_days",
            },
            title="Chapter 22 — Working capital efficiency (days)",
            x_label="Month",
            y_label="Days",
            show_zero_line=True,
        )
        spec4 = FigureSpec(
            chart_type="line",
            title="Chapter 22 — Working capital efficiency (days)",
            x_label="Month",
            y_label="Days",
            data_source="statements_is_monthly.csv + statements_bs_monthly.csv",
            notes="Days metrics use a 28-day month teaching constant (Track D convention).",
        )
        fig4_path = figdir / "ch22_fig_working_capital_days.png"
        save_figure(fig4, fig4_path, spec=spec4)
        _add_row(fig4_path, spec4)

        # Net income variance bridge (latest month vs prior)
        if not bridge.empty:
            start_value = float(bridge.iloc[0]["amount"])
            end_value = float(bridge.iloc[-1]["amount"])
            components = [
                (str(r["component"]), float(r["amount"]))
                for _, r in bridge.iloc[1:-1].iterrows()
            ]
            fig5 = plot_waterfall_bridge(
                start_label="Prior net income",
                end_label="Current net income",
                start_value=start_value,
                end_value=end_value,
                components=components,
                title="Chapter 22 — Net income variance bridge (latest vs prior month)",
                y_label="Net income",
                x_label="Component",
            )
            spec5 = FigureSpec(
                chart_type="waterfall_bridge",
                title="Chapter 22 — Net income variance bridge (latest vs prior month)",
                x_label="Component",
                y_label="Net income",
                data_source="statements_is_monthly.csv",
                notes="Bridge decomposes month-over-month net income change into key drivers.",
            )
            fig5_path = figdir / "ch22_fig_net_income_bridge_latest.png"
            save_figure(fig5, fig5_path, spec=spec5)
            _add_row(fig5_path, spec5)

    figures_manifest_csv = outdir / "ch22_figures_manifest.csv"
    pd.DataFrame([r.__dict__ for r in manifest_rows]).to_csv(
        figures_manifest_csv, index=False
    )

    # -------------------------------
    # Design + memo
    # -------------------------------
    latest_month = str(ratios["month"].iloc[-1]) if len(ratios) else ""
    memo_lines = [
        f"# {CHAPTER} — Financial statement analysis toolkit\n",
        f"Most recent month in dataset: **{latest_month}**\n",
        "\n",
        "## What to look at first\n",
        "1. **Margins**: gross vs operating margin (price/cost vs overhead).\n",
        "2. **Liquidity**: current and quick ratios (can we pay near-term bills?).\n",
        "3. **Working capital days**: DSO/DIO/DPO (cash timing drivers).\n",
        "4. **Variance bridge**: what changed month-over-month (revenue vs costs).\n",
        "\n",
        "## Guardrails\n",
        "* Ratios do not *prove* causes. Treat them as signals to investigate.\n",
        "* If revenue is small in a month, percent metrics can swing wildly.\n",
        "* A profit improvement can be **cosmetic** if AR/inventory grow faster than sales.\n",
        "\n",
        "## Quick flags (latest month)\n",
    ]

    if len(ratios) >= 2:
        ni_delta = float(ratios["net_income"].iloc[-1] - ratios["net_income"].iloc[-2])
        ccc = float(ratios["cash_conversion_cycle_days"].iloc[-1])
        memo_lines.append(f"* Net income change vs prior month: {ni_delta:,.0f}\n")
        memo_lines.append(f"* Cash conversion cycle (days): {ccc:,.1f}\n")

    if pd.notna(net_change_cash_last):
        memo_lines.append(f"* Net change in cash (cash flow statement): {net_change_cash_last:,.0f}\n")

    memo_lines.append("\n")

    memo_md = outdir / "ch22_memo.md"
    memo_md.write_text("".join(memo_lines), encoding="utf-8")

    design = {
        "chapter": "22",
        "chapter_name": "Financial statement analysis toolkit",
        "inputs": {
            "statements_is_monthly": "statements_is_monthly.csv",
            "statements_bs_monthly": "statements_bs_monthly.csv",
            "statements_cf_monthly": "statements_cf_monthly.csv",
        },
        "outputs": {
            "ratios_monthly_csv": str(ratios_monthly_csv),
            "common_size_is_csv": str(common_size_is_csv),
            "common_size_bs_csv": str(common_size_bs_csv),
            "variance_bridge_latest_csv": str(variance_bridge_latest_csv),
            "assumptions_csv": str(assumptions_csv),
            "figures_manifest_csv": str(figures_manifest_csv),
            "memo_md": str(memo_md),
        },
        "definitions": {
            "days_per_month": DAYS_PER_MONTH,
            "current_liabilities": "AP + Sales Tax Payable + Wages Payable + Payroll Taxes Payable",
            "current_assets": "Cash + Accounts Receivable + Inventory",
        },
        "seed": seed,
        "deterministic": True,
    }

    design_json = outdir / "ch22_design.json"
    design_json.write_text(json.dumps(design, indent=2), encoding="utf-8")

    return Outputs(
        ratios_monthly_csv=ratios_monthly_csv,
        common_size_is_csv=common_size_is_csv,
        common_size_bs_csv=common_size_bs_csv,
        variance_bridge_latest_csv=variance_bridge_latest_csv,
        assumptions_csv=assumptions_csv,
        design_json=design_json,
        memo_md=memo_md,
        figures_manifest_csv=figures_manifest_csv,
    )


def main(argv: list[str] | None = None) -> None:
    p = base_parser(description=f"{CHAPTER}: statement analysis toolkit")
    p.add_argument(
        "--datadir",
        type=Path,
        default=Path("data/synthetic/nso_v1"),
        help="Directory containing NSO v1 synthetic tables (default: data/synthetic/nso_v1)",
    )
    args = p.parse_args(argv)

    out = analyze_ch22(datadir=args.datadir, outdir=args.outdir, seed=args.seed)
    print(f"Wrote Chapter 22 artifacts -> {out.design_json.parent}")


if __name__ == "__main__":
    main()
