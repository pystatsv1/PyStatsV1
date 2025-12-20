# SPDX-License-Identifier: MIT
"""Track D simulator: North Shore Outfitters (NSO) running case, v1.

Goal (v1): multi-month dataset that can support Chapters 4+ without breaking the
clean structure that made LedgerLab work in Chapters 1–3.

Outputs to: data/synthetic/nso_v1/

Core tables:
- chart_of_accounts.csv
- gl_journal.csv
- trial_balance_monthly.csv
- statements_is_monthly.csv
- statements_bs_monthly.csv
- statements_cf_monthly.csv (simple CFO/CFI/CFF bridge)

Ch04 subledgers:
- inventory_movements.csv
- fixed_assets.csv
- depreciation_schedule.csv

Design constraints:
- deterministic via --seed
- small + readable
- tie-out friendly (subledgers have txn_id links into GL)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from scripts._cli import apply_seed, base_parser


@dataclass(frozen=True)
class NSOV1Outputs:
    chart_of_accounts: pd.DataFrame
    gl_journal: pd.DataFrame
    trial_balance_monthly: pd.DataFrame
    statements_is_monthly: pd.DataFrame
    statements_bs_monthly: pd.DataFrame
    statements_cf_monthly: pd.DataFrame
    inventory_movements: pd.DataFrame
    fixed_assets: pd.DataFrame
    depreciation_schedule: pd.DataFrame
    meta: dict[str, Any]


def _parse_month(month: str) -> tuple[int, int]:
    y_s, m_s = month.split("-")
    return int(y_s), int(m_s)


def _fmt_month(y: int, m: int) -> str:
    return f"{y:04d}-{m:02d}"


def _add_months(month: str, delta: int) -> str:
    y, m = _parse_month(month)
    total = (y * 12 + (m - 1)) + delta
    y2 = total // 12
    m2 = (total % 12) + 1
    return _fmt_month(y2, m2)


def _month_bounds(month: str) -> tuple[date, date]:
    """Teaching simplification: all months are treated as 28 days."""
    y, m = _parse_month(month)
    return date(y, m, 1), date(y, m, 28)


def build_chart_of_accounts() -> pd.DataFrame:
    rows = [
        ("1000", "Cash", "Asset", "Debit"),
        ("1100", "Accounts Receivable", "Asset", "Debit"),
        ("1200", "Inventory", "Asset", "Debit"),
        ("1300", "Property, Plant & Equipment (Cost)", "Asset", "Debit"),
        ("1350", "Accumulated Depreciation", "Contra Asset", "Credit"),
        ("2000", "Accounts Payable", "Liability", "Credit"),
        ("3000", "Owner Capital", "Equity", "Credit"),
        ("3100", "Retained Earnings (Cumulative, derived)", "Equity", "Credit"),
        ("4000", "Sales Revenue", "Revenue", "Credit"),
        ("5000", "Cost of Goods Sold", "Expense", "Debit"),
        ("6100", "Rent Expense", "Expense", "Debit"),
        ("6200", "Utilities Expense", "Expense", "Debit"),
        ("6300", "Payroll Expense", "Expense", "Debit"),
        ("6400", "Depreciation Expense", "Expense", "Debit"),
    ]
    return pd.DataFrame(rows, columns=["account_id", "account_name", "account_type", "normal_side"])


def _add_txn(
    *,
    lines: list[dict[str, Any]],
    txn_id: int,
    txn_date: date,
    doc_id: str,
    description: str,
    entries: list[tuple[str, float, float]],
) -> None:
    for account_id, debit, credit in entries:
        lines.append(
            {
                "txn_id": int(txn_id),
                "date": txn_date.isoformat(),
                "doc_id": str(doc_id),
                "description": str(description),
                "account_id": str(account_id),
                "debit": float(debit),
                "credit": float(credit),
            }
        )


def _ending_balance_from_tb(tb: pd.DataFrame, account_id: str) -> float:
    """Return balance in its normal direction (positive if normal-side)."""
    hit = tb.loc[tb["account_id"].astype(str) == str(account_id)]
    if hit.empty:
        return 0.0
    normal = str(hit.iloc[0]["normal_side"])
    ending_side = str(hit.iloc[0]["ending_side"])
    bal = float(hit.iloc[0]["ending_balance"])
    return bal if ending_side == normal else -bal


def _compute_tb_for_cutoff(gl: pd.DataFrame, coa: pd.DataFrame, month: str) -> pd.DataFrame:
    start, end = _month_bounds(month)
    cutoff = pd.to_datetime(end.isoformat())
    dts = pd.to_datetime(gl["date"])
    df = gl.loc[dts <= cutoff].copy()

    # ensure metadata exists
    for col in ["account_name", "account_type", "normal_side"]:
        if col in df.columns:
            df = df.drop(columns=[col])
    df = df.merge(coa, on="account_id", how="left")

    tb = (
        df.groupby(["account_id", "account_name", "account_type", "normal_side"], observed=True)[["debit", "credit"]]
        .sum()
        .reset_index()
    )
    tb["net"] = tb["debit"] - tb["credit"]
    tb["ending_side"] = np.where(tb["net"] >= 0, "Debit", "Credit")
    tb["ending_balance"] = tb["net"].abs()
    tb = tb.drop(columns=["net"])
    tb.insert(0, "month", month)
    return tb


def _compute_is_for_month(gl: pd.DataFrame, coa: pd.DataFrame, month: str) -> tuple[pd.DataFrame, float]:
    start, end = _month_bounds(month)
    dts = pd.to_datetime(gl["date"])
    df = gl.loc[(dts >= pd.to_datetime(start)) & (dts <= pd.to_datetime(end))].copy()

    for col in ["account_name", "account_type", "normal_side"]:
        if col in df.columns:
            df = df.drop(columns=[col])
    df = df.merge(coa, on="account_id", how="left")

    revenue = float(
        df.loc[df["account_type"] == "Revenue", "credit"].sum()
        - df.loc[df["account_type"] == "Revenue", "debit"].sum()
    )

    cogs = float(
        df.loc[df["account_id"].astype(str) == "5000", "debit"].sum()
        - df.loc[df["account_id"].astype(str) == "5000", "credit"].sum()
    )

    op_exp = float(
        df.loc[(df["account_type"] == "Expense") & (df["account_id"].astype(str) != "5000"), "debit"].sum()
        - df.loc[(df["account_type"] == "Expense") & (df["account_id"].astype(str) != "5000"), "credit"].sum()
    )

    gross_profit = revenue - cogs
    net_income = gross_profit - op_exp

    is_df = pd.DataFrame(
        [
            {"month": month, "line": "Sales Revenue", "amount": revenue},
            {"month": month, "line": "Cost of Goods Sold", "amount": cogs},
            {"month": month, "line": "Gross Profit", "amount": gross_profit},
            {"month": month, "line": "Operating Expenses", "amount": op_exp},
            {"month": month, "line": "Net Income", "amount": net_income},
        ]
    )
    return is_df, float(net_income)


def _compute_bs_for_month(tb: pd.DataFrame, month: str, retained_cum: float) -> pd.DataFrame:
    cash = _ending_balance_from_tb(tb, "1000")
    ar = _ending_balance_from_tb(tb, "1100")
    inv = _ending_balance_from_tb(tb, "1200")
    ppe_cost = _ending_balance_from_tb(tb, "1300")
    accum_dep = _ending_balance_from_tb(tb, "1350")  # positive in normal credit direction
    ap = _ending_balance_from_tb(tb, "2000")
    owner_cap = _ending_balance_from_tb(tb, "3000")

    # Present accum dep as a negative line for reporting clarity
    accum_dep_line = -float(accum_dep)
    net_ppe = float(ppe_cost + accum_dep_line)

    total_assets = float(cash + ar + inv + ppe_cost + accum_dep_line)
    total_liab = float(ap)
    total_equity = float(owner_cap + retained_cum)

    bs_df = pd.DataFrame(
        [
            {"month": month, "line": "Cash", "amount": cash},
            {"month": month, "line": "Accounts Receivable", "amount": ar},
            {"month": month, "line": "Inventory", "amount": inv},
            {"month": month, "line": "PP&E (Cost)", "amount": ppe_cost},
            {"month": month, "line": "Accumulated Depreciation", "amount": accum_dep_line},
            {"month": month, "line": "Net PP&E", "amount": net_ppe},
            {"month": month, "line": "Total Assets", "amount": total_assets},
            {"month": month, "line": "Accounts Payable", "amount": total_liab},
            {"month": month, "line": "Total Liabilities", "amount": total_liab},
            {"month": month, "line": "Owner Capital", "amount": owner_cap},
            {"month": month, "line": "Retained Earnings (Cumulative, derived)", "amount": retained_cum},
            {"month": month, "line": "Total Equity", "amount": total_equity},
            {"month": month, "line": "Total Liabilities + Equity", "amount": float(total_liab + total_equity)},
        ]
    )
    return bs_df


def _compute_cf_for_month(
    month: str,
    cash_begin: float,
    cash_end: float,
    ar_begin: float,
    ar_end: float,
    inv_begin: float,
    inv_end: float,
    ap_begin: float,
    ap_end: float,
    net_income: float,
    dep_expense: float,
    capex_cash: float,
    owner_contrib: float,
) -> pd.DataFrame:
    delta_ar = float(ar_end - ar_begin)
    delta_inv = float(inv_end - inv_begin)
    delta_ap = float(ap_end - ap_begin)

    cfo = float(net_income + dep_expense - delta_ar - delta_inv + delta_ap)
    cfi = float(-capex_cash)
    cff = float(owner_contrib)

    net_change = float(cfo + cfi + cff)
    end_from_bridge = float(cash_begin + net_change)

    rows = [
        (month, "Net Income", net_income),
        (month, "Add back Depreciation", dep_expense),
        (month, "Change in Accounts Receivable", -delta_ar),
        (month, "Change in Inventory", -delta_inv),
        (month, "Change in Accounts Payable", delta_ap),
        (month, "Net Cash from Operations", cfo),
        (month, "Capital Expenditures (cash)", -capex_cash),
        (month, "Net Cash from Investing", cfi),
        (month, "Owner Contribution", owner_contrib),
        (month, "Net Cash from Financing", cff),
        (month, "Net Change in Cash", net_change),
        (month, "Beginning Cash", cash_begin),
        (month, "Ending Cash (from bridge)", end_from_bridge),
        (month, "Ending Cash (balance sheet)", cash_end),
    ]
    return pd.DataFrame(rows, columns=["month", "line", "amount"])


def simulate_nso_v1(
    *,
    start_month: str = "2025-01",
    n_months: int = 24,
    n_sales_per_month: int = 12,
    pct_on_account: float = 0.35,
    sku_list: tuple[str, ...] = ("SKU-TEE", "SKU-HAT"),
    mean_sale_qty: float = 2.0,
    unit_cost_mean: float = 22.0,
    unit_cost_sd: float = 2.0,
    unit_price_mean: float = 40.0,
    unit_price_sd: float = 4.0,
    rent: float = 1800.0,
    payroll_mean: float = 2400.0,
    utilities_mean: float = 260.0,
    random_state: int | None = None,
) -> NSOV1Outputs:
    apply_seed(random_state)
    rng = np.random.default_rng(random_state)

    coa = build_chart_of_accounts()

    gl_lines: list[dict[str, Any]] = []
    inv_moves: list[dict[str, Any]] = []
    txn_id = 0

    months = [_add_months(start_month, i) for i in range(n_months)]

    # fixed assets (small, deterministic register)
    fixed_assets = pd.DataFrame(
        [
            {
                "asset_id": "FA001",
                "asset_name": "Delivery Van",
                "in_service_month": _add_months(start_month, 1),
                "cost": 12000.0,
                "useful_life_months": 60,
                "salvage_value": 2000.0,
                "method": "SL",
            },
            {
                "asset_id": "FA002",
                "asset_name": "Point-of-Sale Terminal",
                "in_service_month": _add_months(start_month, 3),
                "cost": 1800.0,
                "useful_life_months": 36,
                "salvage_value": 0.0,
                "method": "SL",
            },
        ]
    )

    # depreciation schedule (built for the requested horizon)
    dep_rows: list[dict[str, Any]] = []
    for _, a in fixed_assets.iterrows():
        cost = float(a["cost"])
        salvage = float(a["salvage_value"])
        life = int(a["useful_life_months"])
        in_service = str(a["in_service_month"])
        monthly = (cost - salvage) / float(life)

        accum = 0.0
        for m in months:
            if m < in_service:
                dep = 0.0
            else:
                dep = float(monthly)
                # stop at full depreciation
                if accum + dep > (cost - salvage) + 1e-9:
                    dep = max(0.0, (cost - salvage) - accum)

            accum = float(accum + dep)
            nbv = float(cost - accum)
            dep_rows.append(
                {
                    "month": m,
                    "asset_id": str(a["asset_id"]),
                    "dep_expense": dep,
                    "accum_dep": accum,
                    "net_book_value": nbv,
                }
            )
    depreciation_schedule = pd.DataFrame(dep_rows)

    # helper: random day within teaching month
    def rand_day(month: str) -> date:
        y, m = _parse_month(month)
        d = int(rng.integers(1, 29))  # 1..28
        return date(y, m, d)

    # 0) Owner contribution on day 1 of first month
    first_start, _ = _month_bounds(months[0])
    txn_id += 1
    _add_txn(
        lines=gl_lines,
        txn_id=txn_id,
        txn_date=first_start,
        doc_id="CAP0001",
        description="Owner contribution (startup capital)",
        entries=[("1000", 25000.0, 0.0), ("3000", 0.0, 25000.0)],
    )
    owner_contrib_by_month = {m: 0.0 for m in months}
    owner_contrib_by_month[months[0]] = 25000.0

    # run-month simulation
    for mi, month in enumerate(months):
        # 1) Inventory purchases (2 per month)
        total_purchase_amount = 0.0
        total_credit_purchases = 0.0

        for p in range(1, 3):
            sku = str(rng.choice(sku_list))
            unit_cost = float(max(rng.normal(unit_cost_mean, unit_cost_sd), 8.0))
            qty = int(max(1, round(rng.normal(mean_sale_qty * n_sales_per_month / 6.0, 2.0))))
            amount = float(qty * unit_cost)

            txn_id += 1
            on_credit = bool(rng.random() < 0.65)
            if on_credit:
                entries = [("1200", amount, 0.0), ("2000", 0.0, amount)]
                total_credit_purchases += amount
                desc = "Inventory purchase on credit"
            else:
                entries = [("1200", amount, 0.0), ("1000", 0.0, amount)]
                desc = "Inventory purchase (cash)"

            _add_txn(
                lines=gl_lines,
                txn_id=txn_id,
                txn_date=rand_day(month),
                doc_id=f"{month}-PO{p:02d}",
                description=desc,
                entries=entries,
            )

            inv_moves.append(
                {
                    "month": month,
                    "txn_id": int(txn_id),
                    "date": rand_day(month).isoformat(),
                    "sku": sku,
                    "movement_type": "purchase",
                    "qty": float(qty),
                    "unit_cost": unit_cost,
                    "amount": float(amount),  # + increases inventory
                }
            )
            total_purchase_amount += amount

        # 2) Sales + COGS (two txns per sale)
        ar_sales = 0.0
        for s in range(1, n_sales_per_month + 1):
            sku = str(rng.choice(sku_list))
            qty = int(max(1, round(rng.normal(mean_sale_qty, 0.8))))
            unit_cost = float(max(rng.normal(unit_cost_mean, unit_cost_sd), 8.0))
            unit_price = float(max(rng.normal(unit_price_mean, unit_price_sd), unit_cost + 4.0))

            sale_amt = float(qty * unit_price)
            cogs_amt = float(qty * unit_cost)

            d = rand_day(month)
            doc = f"{month}-SALE{s:03d}"

            # revenue side
            txn_id += 1
            on_account = bool(rng.random() < pct_on_account)
            if on_account:
                debit_acct = "1100"
                ar_sales += sale_amt
                desc = "Sale on account"
            else:
                debit_acct = "1000"
                desc = "Cash sale"

            _add_txn(
                lines=gl_lines,
                txn_id=txn_id,
                txn_date=d,
                doc_id=doc,
                description=desc,
                entries=[(debit_acct, sale_amt, 0.0), ("4000", 0.0, sale_amt)],
            )

            # cogs side (link this txn_id into inventory movements)
            txn_id += 1
            _add_txn(
                lines=gl_lines,
                txn_id=txn_id,
                txn_date=d,
                doc_id=doc,
                description="Record cost of goods sold",
                entries=[("5000", cogs_amt, 0.0), ("1200", 0.0, cogs_amt)],
            )

            inv_moves.append(
                {
                    "month": month,
                    "txn_id": int(txn_id),
                    "date": d.isoformat(),
                    "sku": sku,
                    "movement_type": "sale_issue",
                    "qty": float(-qty),  # - reduces inventory
                    "unit_cost": unit_cost,
                    "amount": float(-cogs_amt),  # - reduces inventory
                }
            )

        # 3) Count adjustment every 3 months (inventory shrink/overage)
        if (mi + 1) % 3 == 0:
            sku = str(rng.choice(sku_list))
            unit_cost = float(max(rng.normal(unit_cost_mean, unit_cost_sd), 8.0))
            adj_qty = int(rng.integers(-4, 3))  # small shrink/overage
            if adj_qty != 0:
                adj_amt = float(adj_qty * unit_cost)  # + increases inv, - decreases inv
                txn_id += 1
                d = date(_parse_month(month)[0], _parse_month(month)[1], 28)
                if adj_amt < 0:
                    # shrinkage: debit COGS, credit Inventory
                    entries = [("5000", float(-adj_amt), 0.0), ("1200", 0.0, float(-adj_amt))]
                    desc = "Inventory count adjustment (shrinkage)"
                else:
                    # overage: debit Inventory, credit COGS (reduces expense)
                    entries = [("1200", adj_amt, 0.0), ("5000", 0.0, adj_amt)]
                    desc = "Inventory count adjustment (overage)"
                _add_txn(
                    lines=gl_lines,
                    txn_id=txn_id,
                    txn_date=d,
                    doc_id=f"{month}-COUNT",
                    description=desc,
                    entries=entries,
                )
                inv_moves.append(
                    {
                        "month": month,
                        "txn_id": int(txn_id),
                        "date": d.isoformat(),
                        "sku": sku,
                        "movement_type": "count_adjustment",
                        "qty": float(adj_qty),
                        "unit_cost": unit_cost,
                        "amount": float(adj_amt),
                    }
                )

        # 4) Collect some AR at month end (60% of this month's AR sales)
        if ar_sales > 0:
            collect = float(0.60 * ar_sales)
            txn_id += 1
            _, end = _month_bounds(month)
            _add_txn(
                lines=gl_lines,
                txn_id=txn_id,
                txn_date=end,
                doc_id=f"{month}-ARCOLL",
                description="Collect on accounts receivable (partial)",
                entries=[("1000", collect, 0.0), ("1100", 0.0, collect)],
            )

        # 5) Pay some AP at month end (50% of credit purchases this month)
        if total_credit_purchases > 0:
            pay = float(0.50 * total_credit_purchases)
            txn_id += 1
            _, end = _month_bounds(month)
            _add_txn(
                lines=gl_lines,
                txn_id=txn_id,
                txn_date=end,
                doc_id=f"{month}-APPAY",
                description="Pay accounts payable (partial)",
                entries=[("2000", pay, 0.0), ("1000", 0.0, pay)],
            )

        # 6) Operating expenses
        txn_id += 1
        start, _ = _month_bounds(month)
        _add_txn(
            lines=gl_lines,
            txn_id=txn_id,
            txn_date=start,
            doc_id=f"{month}-RENT",
            description="Pay monthly rent",
            entries=[("6100", float(rent), 0.0), ("1000", 0.0, float(rent))],
        )

        util = float(max(rng.normal(utilities_mean, 60.0), 60.0))
        txn_id += 1
        _add_txn(
            lines=gl_lines,
            txn_id=txn_id,
            txn_date=rand_day(month),
            doc_id=f"{month}-UTIL",
            description="Pay utilities",
            entries=[("6200", util, 0.0), ("1000", 0.0, util)],
        )

        payroll = float(max(rng.normal(payroll_mean, 180.0), 900.0))
        txn_id += 1
        _add_txn(
            lines=gl_lines,
            txn_id=txn_id,
            txn_date=rand_day(month),
            doc_id=f"{month}-PAY",
            description="Run payroll (simplified: cash paid)",
            entries=[("6300", payroll, 0.0), ("1000", 0.0, payroll)],
        )

        # 7) Capex purchases on their in-service months (cash)
        capex_cash = 0.0
        for _, a in fixed_assets.iterrows():
            if str(a["in_service_month"]) != month:
                continue
            cost = float(a["cost"])
            capex_cash += cost

            txn_id += 1
            _add_txn(
                lines=gl_lines,
                txn_id=txn_id,
                txn_date=date(_parse_month(month)[0], _parse_month(month)[1], 2),
                doc_id=f"{month}-{a['asset_id']}",
                description=f"Acquire fixed asset: {a['asset_name']}",
                entries=[("1300", cost, 0.0), ("1000", 0.0, cost)],
            )

        # 8) Depreciation entry for this month (sum across assets)
        dep_this_month = float(
            depreciation_schedule.loc[depreciation_schedule["month"].astype(str) == month, "dep_expense"].sum()
        )
        if dep_this_month > 0:
            txn_id += 1
            _add_txn(
                lines=gl_lines,
                txn_id=txn_id,
                txn_date=date(_parse_month(month)[0], _parse_month(month)[1], 28),
                doc_id=f"{month}-DEP",
                description="Record depreciation expense",
                entries=[("6400", dep_this_month, 0.0), ("1350", 0.0, dep_this_month)],
            )

    # Build GL dataframe, join COA metadata
    gl = pd.DataFrame(gl_lines).sort_values(["date", "txn_id", "account_id"], kind="mergesort").reset_index(drop=True)
    gl = gl.merge(coa, on="account_id", how="left")

    # Build monthly TB + statements
    tb_all: list[pd.DataFrame] = []
    is_all: list[pd.DataFrame] = []
    bs_all: list[pd.DataFrame] = []
    cf_all: list[pd.DataFrame] = []

    retained_cum = 0.0

    # beginning balances
    cash_begin = 0.0
    ar_begin = 0.0
    inv_begin = 0.0
    ap_begin = 0.0

    for month in months:
        tb_m = _compute_tb_for_cutoff(gl, coa, month)
        tb_all.append(tb_m)

        is_m, ni_m = _compute_is_for_month(gl, coa, month)
        is_all.append(is_m)
        retained_cum = float(retained_cum + ni_m)

        bs_m = _compute_bs_for_month(tb_m, month, retained_cum=retained_cum)
        bs_all.append(bs_m)

        cash_end = float(bs_m.loc[bs_m["line"] == "Cash", "amount"].iloc[0])
        ar_end = float(bs_m.loc[bs_m["line"] == "Accounts Receivable", "amount"].iloc[0])
        inv_end = float(bs_m.loc[bs_m["line"] == "Inventory", "amount"].iloc[0])
        ap_end = float(bs_m.loc[bs_m["line"] == "Accounts Payable", "amount"].iloc[0])

        dep_exp = float(is_m.loc[is_m["line"] == "Operating Expenses", "amount"].iloc[0] * 0.0)
        # better: read from schedule for add-back
        dep_exp = float(
            depreciation_schedule.loc[depreciation_schedule["month"].astype(str) == month, "dep_expense"].sum()
        )

        capex_cash = float(
            fixed_assets.loc[fixed_assets["in_service_month"].astype(str) == month, "cost"].sum()
        )
        owner_contrib = float(owner_contrib_by_month.get(month, 0.0))

        cf_m = _compute_cf_for_month(
            month=month,
            cash_begin=cash_begin,
            cash_end=cash_end,
            ar_begin=ar_begin,
            ar_end=ar_end,
            inv_begin=inv_begin,
            inv_end=inv_end,
            ap_begin=ap_begin,
            ap_end=ap_end,
            net_income=float(ni_m),
            dep_expense=dep_exp,
            capex_cash=capex_cash,
            owner_contrib=owner_contrib,
        )
        cf_all.append(cf_m)

        cash_begin = cash_end
        ar_begin = ar_end
        inv_begin = inv_end
        ap_begin = ap_end

    tb_df = pd.concat(tb_all, ignore_index=True)
    is_df = pd.concat(is_all, ignore_index=True)
    bs_df = pd.concat(bs_all, ignore_index=True)
    cf_df = pd.concat(cf_all, ignore_index=True)

    inv_df = pd.DataFrame(inv_moves).sort_values(["date", "txn_id"], kind="mergesort").reset_index(drop=True)

    meta: dict[str, Any] = {
        "dataset": "NSO_v1",
        "start_month": start_month,
        "n_months": int(n_months),
        "seed": random_state,
        "assumptions": {
            "teaching_month_days": 28,
            "pct_on_account": float(pct_on_account),
            "inventory_system": "perpetual",
            "inventory_count_adjustment_every_months": 3,
            "depreciation_method": "straight-line",
        },
        "notes": [
            "Retained earnings is derived (cumulative net income) for teaching clarity; no closing entries are posted.",
            "Cash flow uses NI + depreciation add-back + working capital changes, plus simple investing/financing sections.",
        ],
    }

    return NSOV1Outputs(
        chart_of_accounts=coa,
        gl_journal=gl,
        trial_balance_monthly=tb_df,
        statements_is_monthly=is_df,
        statements_bs_monthly=bs_df,
        statements_cf_monthly=cf_df,
        inventory_movements=inv_df,
        fixed_assets=fixed_assets,
        depreciation_schedule=depreciation_schedule,
        meta=meta,
    )


def write_nso_v1(outputs: NSOV1Outputs, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    outputs.chart_of_accounts.to_csv(outdir / "chart_of_accounts.csv", index=False)
    outputs.gl_journal.to_csv(outdir / "gl_journal.csv", index=False)
    outputs.trial_balance_monthly.to_csv(outdir / "trial_balance_monthly.csv", index=False)
    outputs.statements_is_monthly.to_csv(outdir / "statements_is_monthly.csv", index=False)
    outputs.statements_bs_monthly.to_csv(outdir / "statements_bs_monthly.csv", index=False)
    outputs.statements_cf_monthly.to_csv(outdir / "statements_cf_monthly.csv", index=False)

    outputs.inventory_movements.to_csv(outdir / "inventory_movements.csv", index=False)
    outputs.fixed_assets.to_csv(outdir / "fixed_assets.csv", index=False)
    outputs.depreciation_schedule.to_csv(outdir / "depreciation_schedule.csv", index=False)

    (outdir / "nso_v1_meta.json").write_text(json.dumps(outputs.meta, indent=2), encoding="utf-8")


def main() -> None:
    p = base_parser("Track D Simulator: North Shore Outfitters (NSO) v1 (multi-month running case)")
    p.set_defaults(outdir=Path("data/synthetic/nso_v1"))
    p.add_argument("--start-month", type=str, default="2025-01", help="Start month (YYYY-MM)")
    p.add_argument("--n-months", type=int, default=24, help="Number of months to generate")
    p.add_argument("--n-sales-per-month", type=int, default=12)
    p.add_argument("--pct-on-account", type=float, default=0.35)
    args = p.parse_args()

    outs = simulate_nso_v1(
        start_month=args.start_month,
        n_months=args.n_months,
        n_sales_per_month=args.n_sales_per_month,
        pct_on_account=args.pct_on_account,
        random_state=args.seed,
    )
    write_nso_v1(outs, args.outdir)
    print(f"Wrote NSO v1 dataset -> {args.outdir}")


if __name__ == "__main__":
    main()
