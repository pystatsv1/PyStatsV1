"""Track D — Chapter 21: scenario planning, sensitivity, and stress testing.

This chapter builds an accountant-friendly scenario pack using the NSO v1
simulator outputs. The goal is not to "predict the future" but to:

- make assumptions explicit,
- tie profit, working capital, and cash together,
- quantify downside risk (cash buffer triggers), and
- identify the handful of levers that matter most.

Outputs are deterministic and written to outputs/track_d/.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts._cli import apply_seed, base_parser
from scripts._reporting_style import plot_bar


CHAPTER = "Track D — Chapter 21"
TEACHING_MONTH_DAYS = 28.0


@dataclass(frozen=True)
class Outputs:
    scenario_pack_monthly_csv: Path
    sensitivity_summary_csv: Path
    assumptions_csv: Path
    governance_template_csv: Path
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
    if df_long.empty:
        return pd.DataFrame(columns=["month", *sorted(set(line_map.values()))])

    df = df_long.copy()
    df["month"] = df["month"].astype(str)
    df = df[df["line"].astype(str).isin(line_map.keys())].copy()
    df["line"] = df["line"].astype(str).map(line_map)

    wide = df.pivot_table(index="month", columns="line", values="amount", aggfunc="sum", fill_value=0.0)
    wide = wide.reset_index().sort_values("month").reset_index(drop=True)

    for col in sorted(set(line_map.values())):
        if col not in wide.columns:
            wide[col] = 0.0
    return wide


def _median_clip(s: pd.Series, lo: float, hi: float, default: float) -> float:
    x = pd.to_numeric(s, errors="coerce").dropna().astype(float)
    if x.empty:
        return float(default)
    v = float(np.median(x))
    return float(min(max(v, lo), hi))


def _seasonal_naive_revenue(hist_is: pd.DataFrame, horizon_months: int) -> pd.Series:
    """Seasonal naive: future month revenue = avg revenue of that calendar month in history."""
    if hist_is.empty:
        return pd.Series(dtype=float)

    df = hist_is[["month", "sales_revenue"]].copy()
    df["month"] = df["month"].astype(str)
    df["cal_m"] = df["month"].str.slice(5, 7)
    by_cal = df.groupby("cal_m", observed=True)["sales_revenue"].mean().to_dict()

    last_month = df["month"].max()
    start = pd.Period(last_month, freq="M") + 1
    future = [str((start + i).strftime("%Y-%m")) for i in range(horizon_months)]

    vals = []
    for m in future:
        cal = m[5:7]
        vals.append(float(by_cal.get(cal, float(df["sales_revenue"].mean()))))

    return pd.Series(vals, index=future, dtype=float)


def _cash_history_weekly_from_bank(bank: pd.DataFrame) -> pd.DataFrame:
    if bank.empty:
        return pd.DataFrame(columns=["week_start", "cash_in_total", "cash_out_total", "net_cash_flow", "ending_cash"])

    df = bank.copy()
    df["posted_date"] = pd.to_datetime(df["posted_date"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).astype(float)

    df["week_start"] = df["posted_date"].dt.to_period("W-SUN").apply(lambda p: p.start_time)
    weekly = df.groupby("week_start", observed=True)["amount"].sum().reset_index()
    weekly = weekly.sort_values("week_start").reset_index(drop=True)

    weekly["cash_in_total"] = weekly["amount"].clip(lower=0.0)
    weekly["cash_out_total"] = (-weekly["amount"].clip(upper=0.0)).astype(float)
    weekly["net_cash_flow"] = weekly["amount"].astype(float)
    weekly["ending_cash"] = weekly["net_cash_flow"].cumsum()
    weekly["week_start"] = weekly["week_start"].dt.strftime("%Y-%m-%d")

    return weekly[["week_start", "cash_in_total", "cash_out_total", "net_cash_flow", "ending_cash"]]


def _buffer_target_weekly(history_weekly: pd.DataFrame) -> float:
    if history_weekly.empty:
        return 0.0
    net = pd.to_numeric(history_weekly["net_cash_flow"], errors="coerce").fillna(0.0).astype(float)
    out = pd.to_numeric(history_weekly["cash_out_total"], errors="coerce").fillna(0.0).astype(float)

    bad = (-net.loc[net < 0]).astype(float)
    if len(bad) >= 3:
        return float(np.quantile(bad, 0.90))
    if len(out) >= 3:
        return float(np.quantile(out, 0.75))
    return float(out.mean())


def _safe_rate(x: float) -> float:
    # Keep rates in a sane range for teaching.
    return float(min(max(x, 0.01), 0.99))


def _safe_days(x: float) -> float:
    return float(min(max(x, 0.0), 120.0))


def _scenario_table() -> pd.DataFrame:
    """Scenario contract used for both outputs + documentation."""
    return pd.DataFrame(
        [
            {
                "scenario": "Base",
                "revenue_multiplier": 1.00,
                "cogs_rate_delta": 0.00,
                "opex_rate_delta": 0.00,
                "dso_days_delta": 0.0,
                "dio_days_delta": 0.0,
                "dpo_days_delta": 0.0,
                "capex_multiplier": 1.00,
                "owner_draw_multiplier": 1.00,
                "stress_revenue_shock_months": "",
                "stress_revenue_shock_multiplier": 1.00,
            },
            {
                "scenario": "Best",
                "revenue_multiplier": 1.05,
                "cogs_rate_delta": -0.01,
                "opex_rate_delta": -0.01,
                "dso_days_delta": -7.0,
                "dio_days_delta": -7.0,
                "dpo_days_delta": 7.0,
                "capex_multiplier": 1.05,
                "owner_draw_multiplier": 0.90,
                "stress_revenue_shock_months": "",
                "stress_revenue_shock_multiplier": 1.00,
            },
            {
                "scenario": "Worst",
                "revenue_multiplier": 0.92,
                "cogs_rate_delta": 0.02,
                "opex_rate_delta": 0.02,
                "dso_days_delta": 14.0,
                "dio_days_delta": 14.0,
                "dpo_days_delta": -7.0,
                "capex_multiplier": 1.10,
                "owner_draw_multiplier": 1.10,
                "stress_revenue_shock_months": "",
                "stress_revenue_shock_multiplier": 1.00,
            },
            {
                "scenario": "Stress_Revenue_Drop",
                "revenue_multiplier": 1.00,
                "cogs_rate_delta": 0.01,
                "opex_rate_delta": 0.01,
                "dso_days_delta": 7.0,
                "dio_days_delta": 0.0,
                "dpo_days_delta": 0.0,
                "capex_multiplier": 1.00,
                "owner_draw_multiplier": 1.00,
                "stress_revenue_shock_months": "1,2",
                "stress_revenue_shock_multiplier": 0.85,
            },
        ]
    )


def _run_one_scenario(
    *,
    scenario_row: dict[str, Any],
    future_months: list[str],
    rev_fc: pd.Series,
    base_rates: dict[str, float],
    base_days: dict[str, float],
    starting_state: dict[str, float],
    dep_monthly: float,
    capex_cash_monthly: float,
    owner_draw_cash_monthly: float,
    principal_payment_monthly: float,
    buffer_target_monthly: float,
) -> pd.DataFrame:
    scen = str(scenario_row["scenario"])

    cogs_rate = _safe_rate(float(base_rates["cogs_rate"]) + float(scenario_row["cogs_rate_delta"]))
    opex_rate = _safe_rate(float(base_rates["opex_rate"]) + float(scenario_row["opex_rate_delta"]))
    rev_mult = float(scenario_row["revenue_multiplier"])

    days = {
        "dso": _safe_days(float(base_days["dso"]) + float(scenario_row["dso_days_delta"])),
        "dio": _safe_days(float(base_days["dio"]) + float(scenario_row["dio_days_delta"])),
        "dpo": _safe_days(float(base_days["dpo"]) + float(scenario_row["dpo_days_delta"])),
    }

    capex = float(capex_cash_monthly) * float(scenario_row["capex_multiplier"])
    owner_draw = float(owner_draw_cash_monthly) * float(scenario_row["owner_draw_multiplier"])

    shock_months: set[int] = set()
    if str(scenario_row.get("stress_revenue_shock_months", "")).strip():
        shock_months = {int(x.strip()) for x in str(scenario_row["stress_revenue_shock_months"]).split(",") if x.strip()}
    shock_mult = float(scenario_row.get("stress_revenue_shock_multiplier", 1.0))

    state = starting_state.copy()
    rows: list[dict[str, Any]] = []

    for idx, m in enumerate(future_months, start=1):
        beginning = state.copy()

        revenue = float(rev_fc.loc[m]) * rev_mult
        if idx in shock_months:
            revenue *= shock_mult

        cogs = float(revenue * cogs_rate)
        opex = float(revenue * opex_rate)
        net_income = float(revenue - cogs - opex)

        # Working capital targets (days). Use teaching month length (28 days).
        ar_end = float((revenue / TEACHING_MONTH_DAYS) * days["dso"] if revenue != 0.0 else beginning["accounts_receivable"])
        inv_end = float((cogs / TEACHING_MONTH_DAYS) * days["dio"] if cogs != 0.0 else beginning["inventory"])
        ap_end = float(((cogs + opex) / TEACHING_MONTH_DAYS) * days["dpo"] if (cogs + opex) != 0.0 else beginning["accounts_payable"])

        # PP&E and depreciation.
        capex_increase = float(-capex)  # capex is negative cash out
        ppe_cost_end = float(beginning["ppe_cost"] + max(capex_increase, 0.0))
        accumulated_depreciation_end = float(beginning["accumulated_depreciation"] - dep_monthly)
        net_ppe_end = float(ppe_cost_end + accumulated_depreciation_end)

        # Debt and owner draws.
        notes_end = float(max(0.0, beginning["notes_payable"] - principal_payment_monthly))
        net_borrowings = float(notes_end - beginning["notes_payable"])
        owner_draw_end = float(beginning["owner_draw"] + owner_draw)

        retained_end = float(beginning["retained_earnings"] + net_income)
        owner_cap_end = float(beginning["owner_capital"])

        # Keep non-working-capital payables constant for Chapter 21 focus.
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

        # Cash is the plug to enforce A = L + E.
        cash_end = float(total_l_e - (ar_end + inv_end + net_ppe_end))

        # Cash bridge components.
        delta_ar = float(ar_end - beginning["accounts_receivable"])
        delta_inv = float(inv_end - beginning["inventory"])
        delta_ap = float(ap_end - beginning["accounts_payable"])
        delta_wages = float(wages_payable_end - beginning["wages_payable"])
        delta_ptx = float(payroll_taxes_payable_end - beginning["payroll_taxes_payable"])
        delta_stx = float(sales_tax_payable_end - beginning["sales_tax_payable"])

        cfo = float(net_income + dep_monthly - delta_ar - delta_inv + delta_ap + delta_wages + delta_ptx + delta_stx)
        cfi = float(capex)
        cff = float(net_borrowings + owner_draw)
        net_change_components = float(cfo + cfi + cff)
        net_change_actual = float(cash_end - beginning["cash"])
        reconciliation_residual = float(net_change_actual - net_change_components)

        buffer_trigger = bool(cash_end < buffer_target_monthly)

        rows.append(
            {
                "month": m,
                "scenario": scen,
                "sales_revenue": revenue,
                "net_income": net_income,
                "ending_cash": cash_end,
                "buffer_target_monthly": float(buffer_target_monthly),
                "buffer_trigger": buffer_trigger,
                "dso_days": float(days["dso"]),
                "dio_days": float(days["dio"]),
                "dpo_days": float(days["dpo"]),
                "reconciliation_residual": reconciliation_residual,
                "capex_cash": float(capex),
                "owner_draw_cash": float(owner_draw),
            }
        )

        # update state for next month
        state.update(
            {
                "cash": cash_end,
                "accounts_receivable": ar_end,
                "inventory": inv_end,
                "ppe_cost": ppe_cost_end,
                "accumulated_depreciation": accumulated_depreciation_end,
                "net_ppe": net_ppe_end,
                "accounts_payable": ap_end,
                "notes_payable": notes_end,
                "owner_draw": owner_draw_end,
                "retained_earnings": retained_end,
                "owner_capital": owner_cap_end,
                "wages_payable": wages_payable_end,
                "payroll_taxes_payable": payroll_taxes_payable_end,
                "sales_tax_payable": sales_tax_payable_end,
            }
        )

    return pd.DataFrame(rows)


def _sensitivity_grid() -> list[dict[str, Any]]:
    """One-at-a-time shocks for sensitivity analysis."""
    return [
        {"lever": "revenue_multiplier", "shock": -0.05},
        {"lever": "revenue_multiplier", "shock": 0.05},
        {"lever": "cogs_rate_delta", "shock": 0.01},
        {"lever": "opex_rate_delta", "shock": 0.01},
        {"lever": "dso_days_delta", "shock": 7.0},
        {"lever": "dpo_days_delta", "shock": -7.0},
        {"lever": "capex_multiplier", "shock": 0.20},
        {"lever": "owner_draw_multiplier", "shock": 0.20},
    ]


def analyze_ch21(*, datadir: Path, outdir: Path, seed: int = 123, horizon_months: int = 12) -> Outputs:
    apply_seed(seed)
    outdir.mkdir(parents=True, exist_ok=True)
    figs_dir = outdir / "figures"
    figs_dir.mkdir(parents=True, exist_ok=True)

    is_long = _read_csv(datadir, "statements_is_monthly.csv")
    bs_long = _read_csv(datadir, "statements_bs_monthly.csv")
    cf_long = _read_csv(datadir, "statements_cf_monthly.csv")
    debt = _read_csv(datadir, "debt_schedule.csv")
    bank = _read_csv(datadir, "bank_statement.csv")

    hist_is = _pivot_statement(is_long, IS_LINE_MAP)
    hist_bs = _pivot_statement(bs_long, BS_LINE_MAP)
    hist_cf = _pivot_statement(cf_long, CF_LINE_MAP)

    if hist_is.empty or hist_bs.empty:
        raise ValueError("NSO v1 statements are empty; cannot run Chapter 21.")

    # Baselines from recent history (last 6 months).
    hist_is_num = hist_is.copy()
    for c in ["sales_revenue", "cogs", "operating_expenses", "net_income"]:
        hist_is_num[c] = pd.to_numeric(hist_is_num[c], errors="coerce").fillna(0.0).astype(float)
    recent_is = hist_is_num.tail(6)
    cogs_rate = _median_clip(recent_is["cogs"] / recent_is["sales_revenue"].replace(0.0, np.nan), 0.01, 0.99, 0.55)
    opex_rate = _median_clip(
        recent_is["operating_expenses"] / recent_is["sales_revenue"].replace(0.0, np.nan), 0.01, 0.99, 0.25
    )

    hist_bs_num = hist_bs.copy()
    for c in BS_LINE_MAP.values():
        if c != "month":
            hist_bs_num[c] = pd.to_numeric(hist_bs_num[c], errors="coerce").fillna(0.0).astype(float)
    recent_bs = hist_bs_num.tail(6)

    # Working capital "days" baselines.
    dso = _median_clip(
        (recent_bs["accounts_receivable"] / recent_is["sales_revenue"].replace(0.0, np.nan)) * TEACHING_MONTH_DAYS,
        0.0,
        120.0,
        28.0,
    )
    dio = _median_clip(
        (recent_bs["inventory"] / recent_is["cogs"].replace(0.0, np.nan)) * TEACHING_MONTH_DAYS,
        0.0,
        120.0,
        28.0,
    )
    dpo = _median_clip(
        (recent_bs["accounts_payable"] / (recent_is["cogs"] + recent_is["operating_expenses"]).replace(0.0, np.nan))
        * TEACHING_MONTH_DAYS,
        0.0,
        120.0,
        21.0,
    )

    dep_monthly = _median_clip(hist_cf["add_back_depreciation"], 0.0, 1e9, 0.0)
    capex_cash_monthly = _median_clip(hist_cf["capex_cash"], -1e9, 0.0, 0.0)
    owner_draw_cash_monthly = _median_clip(hist_cf["owner_draw_cash"], -1e9, 0.0, 0.0)
    principal_payment_monthly = 0.0
    if not debt.empty and "principal" in debt.columns:
        principal_payment_monthly = _median_clip(debt["principal"], 0.0, 1e9, 0.0)

    # Revenue forecast baseline.
    rev_fc = _seasonal_naive_revenue(hist_is, horizon_months=horizon_months)
    future_months = list(rev_fc.index.astype(str))

    # Buffer policy based on weekly bank history.
    hist_weekly = _cash_history_weekly_from_bank(bank)
    buffer_weekly = _buffer_target_weekly(hist_weekly)
    buffer_target_monthly = float(buffer_weekly * 4.0)

    # Starting state from last observed balance sheet.
    last_bs = hist_bs_num.iloc[-1].to_dict()
    starting_state = {
        "cash": float(last_bs.get("cash", 0.0)),
        "accounts_receivable": float(last_bs.get("accounts_receivable", 0.0)),
        "inventory": float(last_bs.get("inventory", 0.0)),
        "ppe_cost": float(last_bs.get("ppe_cost", 0.0)),
        "accumulated_depreciation": float(last_bs.get("accumulated_depreciation", 0.0)),
        "net_ppe": float(last_bs.get("net_ppe", 0.0)),
        "accounts_payable": float(last_bs.get("accounts_payable", 0.0)),
        "notes_payable": float(last_bs.get("notes_payable", 0.0)),
        "wages_payable": float(last_bs.get("wages_payable", 0.0)),
        "payroll_taxes_payable": float(last_bs.get("payroll_taxes_payable", 0.0)),
        "sales_tax_payable": float(last_bs.get("sales_tax_payable", 0.0)),
        "owner_capital": float(last_bs.get("owner_capital", 0.0)),
        "owner_draw": float(last_bs.get("owner_draw", 0.0)),
        "retained_earnings": float(last_bs.get("retained_earnings", 0.0)),
    }

    base_rates = {"cogs_rate": float(cogs_rate), "opex_rate": float(opex_rate)}
    base_days = {"dso": float(dso), "dio": float(dio), "dpo": float(dpo)}

    scenario_def = _scenario_table()
    scenario_rows = scenario_def.to_dict(orient="records")

    scen_frames: list[pd.DataFrame] = []
    for row in scenario_rows:
        scen_frames.append(
            _run_one_scenario(
                scenario_row=row,
                future_months=future_months,
                rev_fc=rev_fc,
                base_rates=base_rates,
                base_days=base_days,
                starting_state=starting_state,
                dep_monthly=dep_monthly,
                capex_cash_monthly=capex_cash_monthly,
                owner_draw_cash_monthly=owner_draw_cash_monthly,
                principal_payment_monthly=principal_payment_monthly,
                buffer_target_monthly=buffer_target_monthly,
            )
        )

    scenario_pack = pd.concat(scen_frames, ignore_index=True)

    scenario_pack_csv = outdir / "ch21_scenario_pack_monthly.csv"
    scenario_pack.to_csv(scenario_pack_csv, index=False)

    # Sensitivity analysis (one-at-a-time shocks around the Base scenario row).
    base_row = scenario_def.loc[scenario_def["scenario"] == "Base"].iloc[0].to_dict()
    base_df = _run_one_scenario(
        scenario_row=base_row,
        future_months=future_months,
        rev_fc=rev_fc,
        base_rates=base_rates,
        base_days=base_days,
        starting_state=starting_state,
        dep_monthly=dep_monthly,
        capex_cash_monthly=capex_cash_monthly,
        owner_draw_cash_monthly=owner_draw_cash_monthly,
        principal_payment_monthly=principal_payment_monthly,
        buffer_target_monthly=buffer_target_monthly,
    )
    base_min_cash = float(pd.to_numeric(base_df["ending_cash"], errors="coerce").min())

    sens_rows: list[dict[str, Any]] = []
    for g in _sensitivity_grid():
        row = base_row.copy()
        lever = str(g["lever"])
        shock = float(g["shock"])
        if lever in {"revenue_multiplier", "capex_multiplier", "owner_draw_multiplier"}:
            row[lever] = float(row[lever]) * (1.0 + shock)
        else:
            row[lever] = float(row[lever]) + shock

        df = _run_one_scenario(
            scenario_row=row,
            future_months=future_months,
            rev_fc=rev_fc,
            base_rates=base_rates,
            base_days=base_days,
            starting_state=starting_state,
            dep_monthly=dep_monthly,
            capex_cash_monthly=capex_cash_monthly,
            owner_draw_cash_monthly=owner_draw_cash_monthly,
            principal_payment_monthly=principal_payment_monthly,
            buffer_target_monthly=buffer_target_monthly,
        )

        end_cash = pd.to_numeric(df["ending_cash"], errors="coerce").astype(float)
        min_cash = float(end_cash.min())
        worst_idx = int(end_cash.idxmin())
        worst_month = str(df.loc[worst_idx, "month"])
        below = int((end_cash < buffer_target_monthly).sum())

        sens_rows.append(
            {
                "lever": lever,
                "shock": shock,
                "min_ending_cash": min_cash,
                "delta_min_cash_vs_base": float(min_cash - base_min_cash),
                "months_below_buffer": below,
                "worst_month": worst_month,
            }
        )

    sens = pd.DataFrame(sens_rows)
    sensitivity_csv = outdir / "ch21_sensitivity_cash_shortfall.csv"
    sens.to_csv(sensitivity_csv, index=False)

    # Assumptions table
    assumptions_rows: list[dict[str, Any]] = []
    assumptions_rows.append({"scenario": "BASELINES", "key": "cogs_rate_median", "value": float(cogs_rate), "note": "Median COGS/revenue (recent months)."})
    assumptions_rows.append({"scenario": "BASELINES", "key": "opex_rate_median", "value": float(opex_rate), "note": "Median opex/revenue (recent months)."})
    assumptions_rows.append({"scenario": "BASELINES", "key": "dso_days_median", "value": float(dso), "note": "AR days baseline (recent months)."})
    assumptions_rows.append({"scenario": "BASELINES", "key": "dio_days_median", "value": float(dio), "note": "Inventory days baseline (recent months)."})
    assumptions_rows.append({"scenario": "BASELINES", "key": "dpo_days_median", "value": float(dpo), "note": "AP days baseline (recent months)."})
    assumptions_rows.append({"scenario": "BASELINES", "key": "buffer_target_monthly", "value": float(buffer_target_monthly), "note": "Cash buffer target = 4× weekly buffer from bank history."})
    assumptions_rows.append({"scenario": "BASELINES", "key": "depreciation_monthly_median", "value": float(dep_monthly), "note": "From CF: Add back Depreciation."})
    assumptions_rows.append({"scenario": "BASELINES", "key": "capex_cash_monthly_median", "value": float(capex_cash_monthly), "note": "From CF: Capital Expenditures (cash)."})
    assumptions_rows.append({"scenario": "BASELINES", "key": "owner_draw_cash_monthly_median", "value": float(owner_draw_cash_monthly), "note": "From CF: Owner Draw (cash)."})
    assumptions_rows.append({"scenario": "BASELINES", "key": "principal_payment_monthly_median", "value": float(principal_payment_monthly), "note": "From debt schedule: principal median."})

    for r in scenario_rows:
        for k in [
            "revenue_multiplier",
            "cogs_rate_delta",
            "opex_rate_delta",
            "dso_days_delta",
            "dio_days_delta",
            "dpo_days_delta",
            "capex_multiplier",
            "owner_draw_multiplier",
            "stress_revenue_shock_months",
            "stress_revenue_shock_multiplier",
        ]:
            assumptions_rows.append(
                {
                    "scenario": str(r["scenario"]),
                    "key": k,
                    "value": r[k],
                    "note": "Scenario lever",
                }
            )

    assumptions_csv = outdir / "ch21_assumptions.csv"
    pd.DataFrame(assumptions_rows).to_csv(assumptions_csv, index=False)

    governance_rows = [
        {
            "cadence": "Weekly",
            "owner": "Controller / Finance",
            "update_inputs": "AR collections, AP payment plan, payroll schedule",
            "decision_trigger": "Ending cash < buffer target (any scenario)",
            "actions": "Freeze discretionary spend, renegotiate terms, accelerate collections",
        },
        {
            "cadence": "Monthly",
            "owner": "FP&A / CFO",
            "update_inputs": "Revenue outlook, margin assumptions, working capital days",
            "decision_trigger": "2+ months below buffer in Worst/Stress",
            "actions": "Reset forecast, update scenario levers, communicate plan to leadership",
        },
    ]
    governance_csv = outdir / "ch21_governance_template.csv"
    pd.DataFrame(governance_rows).to_csv(governance_csv, index=False)

    # Figures
    fig_rows: list[dict[str, str]] = []

    # Cash by scenario
    cash_fig = figs_dir / "ch21_fig_cash_by_scenario.png"
    plt.figure(figsize=(10, 5))
    for scen in scenario_def["scenario"].astype(str).tolist():
        s = scenario_pack.loc[scenario_pack["scenario"].astype(str) == scen].copy()
        plt.plot(s["month"].astype(str), s["ending_cash"].astype(float), label=scen)
    plt.axhline(buffer_target_monthly, linestyle="--")
    plt.title("Ending cash by scenario (12-month horizon)")
    plt.xlabel("Month")
    plt.ylabel("Ending cash")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(cash_fig)
    plt.close()
    fig_rows.append({"filename": cash_fig.name, "title": "Ending cash by scenario", "kind": "time_series"})

    # Sensitivity bar: delta in min cash vs base
    sens_worst = sens.sort_values("delta_min_cash_vs_base").copy()
    sens_fig = figs_dir / "ch21_fig_sensitivity_min_cash_delta.png"
    sens_plot = sens_worst.assign(
        label=[
            f"{a} ({b:+g})"
            for a, b in zip(
                sens_worst["lever"].astype(str),
                sens_worst["shock"].astype(float),
            )
        ]
    )
    fig = plot_bar(
        sens_plot,
        x="label",
        y="delta_min_cash_vs_base",
        title="Sensitivity: impact on minimum ending cash (vs Base)",
        x_label="Lever (shock)",
        y_label="Delta min cash",
    )
    fig.savefig(sens_fig, dpi=144, bbox_inches="tight")
    plt.close(fig)
    fig_rows.append({"filename": sens_fig.name, "title": "Sensitivity (delta min cash)", "kind": "bar"})

    figures_manifest_csv = outdir / "ch21_figures_manifest.csv"
    pd.DataFrame(fig_rows).to_csv(figures_manifest_csv, index=False)

    # Design + memo
    design = {
        "chapter": CHAPTER,
        "dataset": "NSO_v1",
        "horizon_months": int(horizon_months),
        "scenarios": scenario_def["scenario"].astype(str).tolist(),
        "scenario_names": scenario_def["scenario"].astype(str).tolist(),
        "baseline_method": "Seasonal naive revenue; median rates for costs and working-capital days",
        "buffer_policy": {
            "weekly_target": float(buffer_weekly),
            "monthly_target": float(buffer_target_monthly),
            "note": "Monthly target = 4× weekly buffer (90th pct of bad weeks).",
        },
        "levers": {
            "revenue_multiplier": "Revenue level shift",
            "cogs_rate_delta": "COGS rate change (percentage points)",
            "opex_rate_delta": "Opex rate change (percentage points)",
            "dso_days_delta": "AR collection speed",
            "dio_days_delta": "Inventory turns",
            "dpo_days_delta": "Supplier payment timing",
            "capex_multiplier": "Capex intensity",
            "owner_draw_multiplier": "Owner draws (cash)",
        },
    }
    design_json = outdir / "ch21_design.json"
    design_json.write_text(json.dumps(design, indent=2), encoding="utf-8")

    # Memo: highlight triggers + top levers.
    base_cash = scenario_pack.loc[scenario_pack["scenario"] == "Base", "ending_cash"].astype(float)
    worst_cash = scenario_pack.loc[scenario_pack["scenario"] == "Worst", "ending_cash"].astype(float)
    stress_cash = scenario_pack.loc[scenario_pack["scenario"] == "Stress_Revenue_Drop", "ending_cash"].astype(float)

    top_levers = (
        sens.sort_values("delta_min_cash_vs_base").head(3)[["lever", "shock", "delta_min_cash_vs_base"]].copy()
    )
    lines = [
        f"# {CHAPTER}",
        "",
        "## What this pack does",
        "- Produces a best/base/worst + stress scenario forecast that ties profit, working capital, and cash.",
        "- Applies a simple cash buffer policy and flags months below the buffer.",
        "- Runs one-at-a-time sensitivity shocks to identify the biggest cash shortfall drivers.",
        "",
        "## Key results (quick read)",
        f"- Buffer target (monthly): **{buffer_target_monthly:,.0f}**",
        f"- Base scenario min ending cash: **{float(base_cash.min()):,.0f}**",
        f"- Worst scenario min ending cash: **{float(worst_cash.min()):,.0f}**",
        f"- Stress scenario min ending cash: **{float(stress_cash.min()):,.0f}**",
        "",
        "## Top sensitivity levers (largest downside to min cash)",
    ]
    for _, r in top_levers.iterrows():
        lines.append(f"- {r['lever']} shock {r['shock']:+g} → Δmin cash {float(r['delta_min_cash_vs_base']):,.0f}")

    lines += [
        "",
        "## Guardrails",
        "- These are **descriptive baselines** (rates and days), not causal claims.",
        "- If residuals are large, treat it as a modeling red flag: missing flows or inconsistent assumptions.",
        "",
        "## Suggested stress-test narrative",
        "If Stress_Revenue_Drop falls below the buffer, write a plan with:",
        "- Collection actions (DSO)",
        "- Supplier term negotiations (DPO)",
        "- Discretionary spend + capex deferrals",
        "- Governance: who updates, how often, and escalation triggers",
    ]
    memo_md = outdir / "ch21_memo.md"
    memo_md.write_text("\n".join(lines), encoding="utf-8")

    return Outputs(
        scenario_pack_monthly_csv=scenario_pack_csv,
        sensitivity_summary_csv=sensitivity_csv,
        assumptions_csv=assumptions_csv,
        governance_template_csv=governance_csv,
        design_json=design_json,
        memo_md=memo_md,
        figures_manifest_csv=figures_manifest_csv,
    )


def _build_cli() -> Any:
    p = base_parser(description=CHAPTER)
    p.add_argument("--datadir", type=Path, required=True)
    p.add_argument("--horizon-months", type=int, default=12)
    return p


def main(argv: list[str] | None = None) -> int:
    p = _build_cli()
    args = p.parse_args(argv)

    analyze_ch21(datadir=args.datadir, outdir=args.outdir, seed=args.seed or 123, horizon_months=int(args.horizon_months))
    print("Wrote Chapter 21 artifacts ->", args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
