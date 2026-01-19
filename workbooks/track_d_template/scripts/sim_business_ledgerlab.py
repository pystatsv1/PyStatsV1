# SPDX-License-Identifier: MIT
"""Track D simulator: LedgerLab (accounting-shaped synthetic dataset).

This simulator generates a tiny month of bookkeeping activity with:

- Chart of accounts (COA)
- Journal / general ledger detail (debit/credit lines)
- Derived month-level statements (IS/BS/CF)

Design goals (aligned with PyStatsV1):
- Deterministic output via ``--seed``
- Human-readable CSV artifacts
- Simple but realistic accounting story (sales, COGS, inventory, expenses)

Chapter usage:
- Track D Ch01 uses the core tables produced here
- Track D Ch02/Ch03 use GL/TB/Statements for analysis and validation
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
class LedgerLabOutputs:
    chart_of_accounts: pd.DataFrame
    gl_journal: pd.DataFrame
    trial_balance_monthly: pd.DataFrame
    statements_is_monthly: pd.DataFrame
    statements_bs_monthly: pd.DataFrame
    statements_cf_monthly: pd.DataFrame
    meta: dict[str, Any]


def _month_bounds(month: str) -> tuple[date, date]:
    """Return (start_date, end_date) for a YYYY-MM month.

    Teaching simplification: all months are treated as 28 days.
    """
    year_s, mon_s = month.split("-")
    y = int(year_s)
    m = int(mon_s)
    start = date(y, m, 1)
    end = date(y, m, 28)
    return start, end


def build_chart_of_accounts() -> pd.DataFrame:
    """Minimal chart of accounts suitable for early Track D chapters."""
    rows = [
        ("1000", "Cash", "Asset", "Debit"),
        ("1100", "Accounts Receivable", "Asset", "Debit"),
        ("1200", "Inventory", "Asset", "Debit"),
        ("2000", "Accounts Payable", "Liability", "Credit"),
        ("3000", "Owner Capital", "Equity", "Credit"),
        ("3100", "Retained Earnings (Current Period)", "Equity", "Credit"),
        ("4000", "Sales Revenue", "Revenue", "Credit"),
        ("5000", "Cost of Goods Sold", "Expense", "Debit"),
        ("6100", "Rent Expense", "Expense", "Debit"),
        ("6200", "Utilities Expense", "Expense", "Debit"),
        ("6300", "Payroll Expense", "Expense", "Debit"),
    ]
    return pd.DataFrame(
        rows, columns=["account_id", "account_name", "account_type", "normal_side"]
    )


def _add_txn(
    *,
    lines: list[dict[str, Any]],
    txn_id: int,
    txn_date: date,
    description: str,
    doc_id: str,
    entries: list[tuple[str, float, float]],
) -> None:
    """Append journal lines for one transaction."""
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


def simulate_ledgerlab_month(
    *,
    month: str,
    n_sales: int = 18,
    mean_sale: float = 220.0,
    sale_sd: float = 60.0,
    pct_on_account: float = 0.45,
    cogs_rate: float = 0.55,
    initial_cash: float = 5000.0,
    pay_rent: float = 1400.0,
    payroll_runs: int = 2,
    mean_utilities: float = 180.0,
    random_state: int | None = None,
) -> LedgerLabOutputs:
    """Simulate a small month of ledger activity and derive IS/BS/CF statements."""
    apply_seed(random_state)
    rng = np.random.default_rng(random_state)
    start, end = _month_bounds(month)

    coa = build_chart_of_accounts()

    lines: list[dict[str, Any]] = []
    txn_id = 0

    def rand_day() -> date:
        d = int(rng.integers(1, 29))  # 1..28 inclusive
        return date(start.year, start.month, d)

    # 1) Owner invests cash (startup month)
    txn_id += 1
    _add_txn(
        lines=lines,
        txn_id=txn_id,
        txn_date=start,
        description="Owner contribution (startup capital)",
        doc_id="CAP0001",
        entries=[("1000", initial_cash, 0.0), ("3000", 0.0, initial_cash)],
    )

    # 2) Sales amounts and whether on account (AR) vs cash
    sale_amounts = np.maximum(rng.normal(mean_sale, sale_sd, size=n_sales), 20.0)
    is_on_account = rng.random(size=n_sales) < pct_on_account

    total_sales = float(np.sum(sale_amounts))
    total_cogs = float(total_sales * cogs_rate)

    # 3) Inventory purchases (ensure inventory covers COGS)
    purchase_total = total_cogs * 1.25
    n_purchases = 3
    purchase_splits = rng.dirichlet(np.ones(n_purchases)) * purchase_total
    purchase_on_credit = [True, True, False]  # deterministic pattern

    for i, amt in enumerate(purchase_splits, start=1):
        txn_id += 1
        amt_f = float(amt)
        if purchase_on_credit[i - 1]:
            desc = "Inventory purchase on credit"
            entries = [("1200", amt_f, 0.0), ("2000", 0.0, amt_f)]
        else:
            desc = "Inventory purchase (cash)"
            entries = [("1200", amt_f, 0.0), ("1000", 0.0, amt_f)]
        _add_txn(
            lines=lines,
            txn_id=txn_id,
            txn_date=rand_day(),
            description=desc,
            doc_id=f"PO{i:04d}",
            entries=entries,
        )

    # 4) Record sales + COGS (two txns per sale for clarity)
    for i, amt in enumerate(sale_amounts, start=1):
        sale_amt = float(amt)
        cogs_amt = float(sale_amt * cogs_rate)
        txn_date = rand_day()
        doc_id = f"SALE{i:04d}"

        # a) Revenue side
        txn_id += 1
        if bool(is_on_account[i - 1]):
            debit_acct = "1100"  # AR
            desc = "Sale on account"
        else:
            debit_acct = "1000"  # Cash
            desc = "Cash sale"
        _add_txn(
            lines=lines,
            txn_id=txn_id,
            txn_date=txn_date,
            description=desc,
            doc_id=doc_id,
            entries=[(debit_acct, sale_amt, 0.0), ("4000", 0.0, sale_amt)],
        )

        # b) COGS side
        txn_id += 1
        _add_txn(
            lines=lines,
            txn_id=txn_id,
            txn_date=txn_date,
            description="Record cost of goods sold",
            doc_id=doc_id,
            entries=[("5000", cogs_amt, 0.0), ("1200", 0.0, cogs_amt)],
        )

    # 5) Collect some AR (assume 60% collected in-month)
    ar_sales_total = float(np.sum(sale_amounts[is_on_account]))
    collect_amt = 0.60 * ar_sales_total
    if collect_amt > 0.0:
        txn_id += 1
        _add_txn(
            lines=lines,
            txn_id=txn_id,
            txn_date=end,
            description="Collect on accounts receivable",
            doc_id="ARCOLL01",
            entries=[("1000", float(collect_amt), 0.0), ("1100", 0.0, float(collect_amt))],
        )

    # 6) Pay some AP (assume 50% of AP purchases paid in-month)
    ap_purchases_total = float(np.sum(purchase_splits[:2]))
    pay_ap_amt = 0.50 * ap_purchases_total
    if pay_ap_amt > 0.0:
        txn_id += 1
        _add_txn(
            lines=lines,
            txn_id=txn_id,
            txn_date=end,
            description="Pay accounts payable",
            doc_id="APPAY01",
            entries=[("2000", float(pay_ap_amt), 0.0), ("1000", 0.0, float(pay_ap_amt))],
        )

    # 7) Operating expenses (rent once; utilities once; payroll N times)
    txn_id += 1
    _add_txn(
        lines=lines,
        txn_id=txn_id,
        txn_date=start,
        description="Pay monthly rent",
        doc_id="RENT0001",
        entries=[("6100", float(pay_rent), 0.0), ("1000", 0.0, float(pay_rent))],
    )

    util_amt = float(max(rng.normal(mean_utilities, 40.0), 40.0))
    txn_id += 1
    _add_txn(
        lines=lines,
        txn_id=txn_id,
        txn_date=rand_day(),
        description="Pay utilities",
        doc_id="UTIL0001",
        entries=[("6200", util_amt, 0.0), ("1000", 0.0, util_amt)],
    )

    for p in range(1, payroll_runs + 1):
        pay_amt = float(max(rng.normal(1200.0, 120.0), 600.0))
        txn_id += 1
        _add_txn(
            lines=lines,
            txn_id=txn_id,
            txn_date=rand_day(),
            description="Run payroll (simplified: expense paid in cash)",
            doc_id=f"PAY{p:04d}",
            entries=[("6300", pay_amt, 0.0), ("1000", 0.0, pay_amt)],
        )

    gl = pd.DataFrame(lines)
    gl = (
        gl.sort_values(["date", "txn_id", "account_id"], kind="mergesort")
        .reset_index(drop=True)
    )

    # Join account metadata for convenience
    gl = gl.merge(coa, on="account_id", how="left")

    # Trial balance (sum debits/credits per account)
    tb = (
        gl.groupby(["account_id", "account_name", "account_type", "normal_side"], observed=True)[
            ["debit", "credit"]
        ]
        .sum()
        .reset_index()
    )
    tb["net"] = tb["debit"] - tb["credit"]
    tb["ending_side"] = np.where(tb["net"] >= 0, "Debit", "Credit")
    tb["ending_balance"] = tb["net"].abs()
    tb = tb.drop(columns=["net"])
    tb.insert(0, "month", month)

    # Income statement (standard breakdown: Revenue, COGS, Operating Expenses, Net Income)
    revenue = float(
        tb.loc[tb["account_type"] == "Revenue", "credit"].sum()
        - tb.loc[tb["account_type"] == "Revenue", "debit"].sum()
    )

    cogs = float(
        tb.loc[tb["account_id"] == "5000", "debit"].sum()
        - tb.loc[tb["account_id"] == "5000", "credit"].sum()
    )

    op_expenses = float(
        tb.loc[
            (tb["account_type"] == "Expense") & (tb["account_id"] != "5000"),
            "debit",
        ].sum()
        - tb.loc[
            (tb["account_type"] == "Expense") & (tb["account_id"] != "5000"),
            "credit",
        ].sum()
    )

    gross_profit = revenue - cogs
    net_income = gross_profit - op_expenses

    is_df = pd.DataFrame(
        [
            {"month": month, "line": "Sales Revenue", "amount": revenue},
            {"month": month, "line": "Cost of Goods Sold", "amount": cogs},
            {"month": month, "line": "Gross Profit", "amount": gross_profit},
            {"month": month, "line": "Operating Expenses", "amount": op_expenses},
            {"month": month, "line": "Net Income", "amount": net_income},
        ]
    )


    # Balance sheet (assets/liabilities from TB; equity = owner capital + current-period earnings)
    def _ending_balance(acct_id: str) -> float:
        """Return balance in its normal direction (positive if normal-side)."""
        row = tb.loc[tb["account_id"] == acct_id]
        if row.empty:
            return 0.0
        normal = str(row.iloc[0]["normal_side"])
        ending_side = str(row.iloc[0]["ending_side"])
        bal = float(row.iloc[0]["ending_balance"])
        return bal if ending_side == normal else -bal

    cash = _ending_balance("1000")
    ar = _ending_balance("1100")
    inv = _ending_balance("1200")
    ap = _ending_balance("2000")
    owner_cap = _ending_balance("3000")
    retained = net_income  # simplified: current-period NI sits in equity

    total_assets = float(cash + ar + inv)
    total_liab = float(ap)
    total_equity = float(owner_cap + retained)

    bs_df = pd.DataFrame(
        [
            {"month": month, "line": "Cash", "amount": cash},
            {"month": month, "line": "Accounts Receivable", "amount": ar},
            {"month": month, "line": "Inventory", "amount": inv},
            {"month": month, "line": "Total Assets", "amount": total_assets},
            {"month": month, "line": "Accounts Payable", "amount": total_liab},
            {"month": month, "line": "Total Liabilities", "amount": total_liab},
            {"month": month, "line": "Owner Capital", "amount": owner_cap},
            {"month": month, "line": "Retained Earnings (Current Period)", "amount": retained},
            {"month": month, "line": "Total Equity", "amount": total_equity},
            {"month": month, "line": "Total Liabilities + Equity", "amount": total_liab + total_equity},
        ]
    )

    # Cash flow statement (simple bridge; startup-month friendly)
    net_income_stmt = float(is_df.loc[is_df["line"] == "Net Income", "amount"].iloc[0])
    cash_end = float(bs_df.loc[bs_df["line"] == "Cash", "amount"].iloc[0])
    ar_end = float(bs_df.loc[bs_df["line"] == "Accounts Receivable", "amount"].iloc[0])
    inv_end = float(bs_df.loc[bs_df["line"] == "Inventory", "amount"].iloc[0])
    ap_end = float(bs_df.loc[bs_df["line"] == "Accounts Payable", "amount"].iloc[0])

    # Beginning balances assumed 0 for teaching “month 1”
    cash_begin = 0.0

    # CFO using ΔWC with beginning = 0
    cfo = float(net_income_stmt - ar_end - inv_end + ap_end)

    # CFF = owner contribution (startup month)
    cff = float(owner_cap)

    net_change_cash = float(cfo + cff)
    cash_end_from_bridge = float(cash_begin + net_change_cash)

    cf_rows = [
        (month, "Net Income", net_income_stmt),
        (month, "Change in Accounts Receivable", -ar_end),
        (month, "Change in Inventory", -inv_end),
        (month, "Change in Accounts Payable", ap_end),
        (month, "Net Cash from Operations", cfo),
        (month, "Owner Contribution", owner_cap),
        (month, "Net Cash from Financing", cff),
        (month, "Net Change in Cash", net_change_cash),
        (month, "Beginning Cash (assumed)", cash_begin),
        (month, "Ending Cash (from bridge)", cash_end_from_bridge),
        (month, "Ending Cash (balance sheet)", cash_end),
    ]
    cf_df = pd.DataFrame(cf_rows, columns=["month", "line", "amount"])

    meta: dict[str, Any] = {
        "dataset": "LedgerLab",
        "month": month,
        "seed": random_state,
        "n_sales": int(n_sales),
        "assumptions": {
            "pct_on_account": float(pct_on_account),
            "cogs_rate": float(cogs_rate),
            "ar_collected_in_month": 0.60,
            "ap_paid_in_month": 0.50,
            "month_length_days": 28,
            "cash_begin_assumed": 0.0,
        },
        "notes": [
            "Equity simplified: Owner Capital + current-period net income (no closing entries).",
            "Cash flow uses a simple NI + working-capital bridge with beginning balances assumed 0.",
        ],
    }

    return LedgerLabOutputs(
        chart_of_accounts=coa,
        gl_journal=gl,
        trial_balance_monthly=tb,
        statements_is_monthly=is_df,
        statements_bs_monthly=bs_df,
        statements_cf_monthly=cf_df,
        meta=meta,
    )


def write_ledgerlab(outputs: LedgerLabOutputs, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    outputs.chart_of_accounts.to_csv(outdir / "chart_of_accounts.csv", index=False)
    outputs.gl_journal.to_csv(outdir / "gl_journal.csv", index=False)
    outputs.trial_balance_monthly.to_csv(outdir / "trial_balance_monthly.csv", index=False)
    outputs.statements_is_monthly.to_csv(outdir / "statements_is_monthly.csv", index=False)
    outputs.statements_bs_monthly.to_csv(outdir / "statements_bs_monthly.csv", index=False)
    outputs.statements_cf_monthly.to_csv(outdir / "statements_cf_monthly.csv", index=False)

    (outdir / "ledgerlab_meta.json").write_text(
        json.dumps(outputs.meta, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = base_parser("Track D Simulator: LedgerLab (Chapter 1+ core tables)")
    parser.set_defaults(outdir=Path("data/synthetic/ledgerlab_ch01"))

    parser.add_argument(
        "--month",
        type=str,
        default="2025-01",
        help="Month to simulate (YYYY-MM). Uses a 28-day teaching calendar.",
    )
    parser.add_argument("--n-sales", type=int, default=18, help="Number of sales in the month")
    parser.add_argument(
        "--pct-on-account",
        type=float,
        default=0.45,
        help="Share of sales on account (AR) rather than cash",
    )
    parser.add_argument("--mean-sale", type=float, default=220.0, help="Average sale amount")
    parser.add_argument(
        "--sale-sd",
        type=float,
        default=60.0,
        help="Sale amount standard deviation",
    )
    parser.add_argument(
        "--cogs-rate",
        type=float,
        default=0.55,
        help="COGS as a fraction of sales (e.g., 0.55)",
    )
    parser.add_argument(
        "--initial-cash",
        type=float,
        default=5000.0,
        help="Owner contribution at start of month (startup cash).",
    )
    parser.add_argument("--pay-rent", type=float, default=1400.0, help="Monthly rent paid (cash).")
    parser.add_argument(
        "--payroll-runs",
        type=int,
        default=2,
        help="Number of payroll runs (each is a cash-paid expense).",
    )
    parser.add_argument(
        "--mean-utilities",
        type=float,
        default=180.0,
        help="Mean utilities expense (cash).",
    )

    args = parser.parse_args()

    outs = simulate_ledgerlab_month(
        month=args.month,
        n_sales=args.n_sales,
        mean_sale=args.mean_sale,
        sale_sd=args.sale_sd,
        pct_on_account=args.pct_on_account,
        cogs_rate=args.cogs_rate,
        initial_cash=args.initial_cash,
        pay_rent=args.pay_rent,
        payroll_runs=args.payroll_runs,
        mean_utilities=args.mean_utilities,
        random_state=args.seed,
    )
    write_ledgerlab(outs, args.outdir)

    print(f"Wrote LedgerLab core tables -> {args.outdir}")


if __name__ == "__main__":
    main()
