# SPDX-License-Identifier: MIT
"""Track D – Chapter 1: Accounting as a measurement system.

This script reads the LedgerLab Ch01 tables, performs basic integrity checks
(controls-aware analytics), and produces accountant-friendly descriptive
summaries.

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* business_ch01_cash_balance.png
* business_ch01_balance_sheet_bar.png
* business_ch01_summary.json

The goal is to model a reproducible "mini-close" workflow:

1) simulate bookkeeping data
2) derive statements
3) validate core accounting identities
4) produce a short, decision-oriented summary"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd

from scripts._cli import apply_seed, base_parser


@dataclass(frozen=True)
class Ch01Summary:
    checks: dict[str, Any]
    metrics: dict[str, Any]


def load_ledgerlab(datadir: pathlib.Path) -> dict[str, pd.DataFrame]:
    """Load required LedgerLab tables for Chapter 1."""
    tables = {
        "chart_of_accounts": datadir / "chart_of_accounts.csv",
        "gl_journal": datadir / "gl_journal.csv",
        "trial_balance_monthly": datadir / "trial_balance_monthly.csv",
        "statements_is_monthly": datadir / "statements_is_monthly.csv",
        "statements_bs_monthly": datadir / "statements_bs_monthly.csv",
    }
    missing = [name for name, path in tables.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing required LedgerLab tables in {datadir}: {', '.join(missing)}"
        )

    # Ensure key identifiers stay as strings (CSV auto-inference would turn
    # account_id 1000 into int, which breaks joins and filters).
    read_specs: dict[str, dict[str, Any]] = {
        "chart_of_accounts": {"dtype": {"account_id": str}},
        "gl_journal": {"dtype": {"txn_id": str, "doc_id": str, "account_id": str}},
        "trial_balance_monthly": {"dtype": {"account_id": str}},
        "statements_is_monthly": {},
        "statements_bs_monthly": {},
    }

    out: dict[str, pd.DataFrame] = {
        name: pd.read_csv(path, **read_specs.get(name, {})) for name, path in tables.items()
    }
    return out


def check_transactions_balance(gl: pd.DataFrame, tol: float = 1e-6) -> dict[str, Any]:
    """Validate debits == credits for each transaction."""
    by_txn = gl.groupby("txn_id", as_index=False)[["debit", "credit"]].sum()
    by_txn["diff"] = (by_txn["debit"] - by_txn["credit"]).abs()
    bad = by_txn.loc[by_txn["diff"] > tol]
    return {
        "transactions_balanced": bool(bad.empty),
        "n_transactions": int(by_txn.shape[0]),
        "n_unbalanced": int(bad.shape[0]),
        "max_abs_diff": float(by_txn["diff"].max()) if not by_txn.empty else 0.0,
    }


def check_accounting_equation(bs: pd.DataFrame, tol: float = 1e-6) -> dict[str, Any]:
    """Validate Assets == Liabilities + Equity using the statement totals."""
    def _line_amount(line: str) -> float:
        row = bs.loc[bs["line"] == line]
        if row.empty:
            return 0.0
        return float(row.iloc[0]["amount"])

    assets = _line_amount("Total Assets")
    le = _line_amount("Total Liabilities + Equity")
    diff = float(abs(assets - le))
    return {
        "accounting_equation_balances": diff <= tol,
        "total_assets": assets,
        "total_liabilities_plus_equity": le,
        "abs_diff": diff,
    }


def compute_metrics(gl: pd.DataFrame, is_stmt: pd.DataFrame, bs: pd.DataFrame) -> dict[str, Any]:
    """Compute a small set of accountant-friendly descriptive statistics."""
    # Sales revenue: credit to account_id=4000
    sales_lines = gl.loc[gl["account_id"] == "4000", "credit"].to_numpy(dtype=float)
    sales_total = float(np.sum(sales_lines))
    n_sales = int(gl.loc[gl["doc_id"].str.startswith("SALE"), "doc_id"].nunique())
    avg_sale = float(sales_total / n_sales) if n_sales else 0.0

    # Cash vs AR sales (from the revenue-side entry)
    rev_side = gl.loc[(gl["doc_id"].str.startswith("SALE")) & (gl["account_id"] == "4000")]
    # match revenue-side by txn_id: the debit line account_id will be Cash or AR
    rev_txn_ids = rev_side["txn_id"].unique()
    rev_txn_lines = gl.loc[gl["txn_id"].isin(rev_txn_ids)].copy()
    debit_by_txn = (
        rev_txn_lines.loc[rev_txn_lines["debit"] > 0]
        .groupby("txn_id", as_index=False)["account_id"]
        .first()
    )
    pct_on_account = 0.0
    if not debit_by_txn.empty:
        pct_on_account = float((debit_by_txn["account_id"] == "1100").mean())

    # Gross margin proxy (Sales - COGS)
    cogs_total = float(gl.loc[gl["account_id"] == "5000", "debit"].sum())
    gross_profit = sales_total - cogs_total
    gross_margin_pct = float(gross_profit / sales_total) if sales_total else 0.0

    # Net income from statement
    ni_row = is_stmt.loc[is_stmt["line"] == "Net Income"]
    net_income = float(ni_row.iloc[0]["amount"]) if not ni_row.empty else float("nan")

    # Ending cash from balance sheet
    cash_row = bs.loc[bs["line"] == "Cash"]
    ending_cash = float(cash_row.iloc[0]["amount"]) if not cash_row.empty else float("nan")

    return {
        "sales_total": sales_total,
        "n_sales": n_sales,
        "avg_sale": avg_sale,
        "pct_sales_on_account": pct_on_account,
        "cogs_total": cogs_total,
        "gross_profit": gross_profit,
        "gross_margin_pct": gross_margin_pct,
        "net_income": net_income,
        "ending_cash": ending_cash,
    }


def plot_cash_balance(gl: pd.DataFrame, outpath: pathlib.Path) -> None:
    """Plot daily cash balance (simple teaching calendar: 28 days)."""
    cash_lines = gl.loc[gl["account_id"] == "1000", ["date", "debit", "credit"]].copy()
    if cash_lines.empty:
        return
    cash_lines["date"] = pd.to_datetime(cash_lines["date"]).dt.date
    cash_lines["delta"] = cash_lines["debit"].astype(float) - cash_lines["credit"].astype(float)
    daily = cash_lines.groupby("date", as_index=False)["delta"].sum().sort_values("date")
    daily["balance"] = daily["delta"].cumsum()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(daily["date"], daily["balance"], marker="o")
    ax.set_title("Daily Cash Balance (LedgerLab)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cash balance")
    ax.grid(True, linestyle=":", alpha=0.7)
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_balance_sheet(bs: pd.DataFrame, outpath: pathlib.Path) -> None:
    """Simple bar chart: Assets vs Liabilities vs Equity."""
    def _line(line: str) -> float:
        row = bs.loc[bs["line"] == line]
        return float(row.iloc[0]["amount"]) if not row.empty else 0.0

    assets = _line("Total Assets")
    liab = _line("Total Liabilities")
    equity = _line("Total Equity")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Assets", "Liabilities", "Equity"], [assets, liab, equity])
    ax.set_title("Balance Sheet Snapshot (Month End)")
    ax.set_ylabel("Amount")
    ax.grid(axis="y", linestyle=":", alpha=0.7)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def analyze_ch01(datadir: pathlib.Path, outdir: pathlib.Path, seed: int | None = None) -> Ch01Summary:
    """Run Chapter 1 analysis and write artifacts."""
    apply_seed(seed)
    outdir.mkdir(parents=True, exist_ok=True)

    tables = load_ledgerlab(datadir)
    gl = tables["gl_journal"]
    is_stmt = tables["statements_is_monthly"]
    bs = tables["statements_bs_monthly"]

    checks: dict[str, Any] = {}
    checks.update(check_transactions_balance(gl))
    checks.update(check_accounting_equation(bs))

    metrics = compute_metrics(gl, is_stmt, bs)

    plot_cash_balance(gl, outdir / "business_ch01_cash_balance.png")
    plot_balance_sheet(bs, outdir / "business_ch01_balance_sheet_bar.png")

    payload = {
        "chapter": "business_ch01_accounting_measurement",
        "datadir": str(datadir),
        "seed": seed,
        "checks": checks,
        "metrics": metrics,
    }
    (outdir / "business_ch01_summary.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    return Ch01Summary(checks=checks, metrics=metrics)


def main() -> None:
    parser = base_parser("Track D Chapter 1: Accounting as measurement")
    parser.add_argument(
        "--datadir",
        type=pathlib.Path,
        default=pathlib.Path("data/synthetic/ledgerlab_ch01"),
        help="Directory containing LedgerLab core tables",
    )
    parser.set_defaults(outdir=pathlib.Path("outputs/track_d"))
    args = parser.parse_args()

    try:
        summary = analyze_ch01(args.datadir, args.outdir, seed=args.seed)
    except FileNotFoundError as e:
        print(str(e))
        print("Hint: run `python -m scripts.sim_business_ledgerlab --outdir data/synthetic/ledgerlab_ch01 --seed 123`. ")
        return

    print("\nChecks:")
    for k, v in summary.checks.items():
        print(f"- {k}: {v}")

    print("\nKey metrics:")
    for k, v in summary.metrics.items():
        if isinstance(v, float):
            print(f"- {k}: {v:.4f}")
        else:
            print(f"- {k}: {v}")

    print(f"\nWrote outputs -> {args.outdir}")


if __name__ == "__main__":
    main()
