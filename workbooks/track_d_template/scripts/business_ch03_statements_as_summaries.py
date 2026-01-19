# SPDX-License-Identifier: MIT
"""
Track D - Chapter 3
Financial statements as summary statistics.

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* business_ch03_summary.json
* business_ch03_statement_bridge.csv
* business_ch03_trial_balance.csv
* business_ch03_net_income_vs_cash_change.png

Reads LedgerLab tables, recomputes a TB from the GL, reconciles statements,
and builds a simple net-income -> cash-change bridge (cash flow style)."""

from __future__ import annotations

import argparse
import json
import pathlib
from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts._cli import apply_seed


@dataclass(frozen=True)
class Ch03Summary:
    checks: dict[str, Any]
    metrics: dict[str, Any]


# -----------------------------
# I/O helpers
# -----------------------------
def _read_csv(path: pathlib.Path, **kwargs: Any) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required table: {path}")
    return pd.read_csv(path, **kwargs)


def load_ledgerlab_tables(datadir: pathlib.Path) -> dict[str, pd.DataFrame]:
    tables = {
        "chart_of_accounts": _read_csv(
            datadir / "chart_of_accounts.csv",
            dtype={"account_id": str},
        ),
        "gl_journal": _read_csv(
            datadir / "gl_journal.csv",
            dtype={"txn_id": str, "doc_id": str, "account_id": str},
        ),
        "trial_balance_monthly": _read_csv(
            datadir / "trial_balance_monthly.csv",
            dtype={"account_id": str},
        ),
        "statements_is_monthly": _read_csv(datadir / "statements_is_monthly.csv"),
        "statements_bs_monthly": _read_csv(datadir / "statements_bs_monthly.csv"),
    }

    # CF table is expected for Ch03, but we allow “compute if missing”
    cf_path = datadir / "statements_cf_monthly.csv"
    if cf_path.exists():
        tables["statements_cf_monthly"] = _read_csv(cf_path)

    return tables


# -----------------------------
# Core checks and transforms
# -----------------------------
def check_transactions_balance(gl: pd.DataFrame) -> dict[str, Any]:
    required = {"txn_id", "debit", "credit"}
    if not required.issubset(gl.columns):
        return {
            "transactions_balanced": False,
            "n_transactions": None,
            "n_unbalanced": None,
            "max_abs_diff": None,
        }

    g = gl.groupby("txn_id", observed=True)[["debit", "credit"]].sum()
    diff = (g["debit"].astype(float) - g["credit"].astype(float)).abs()
    n_txn = int(g.shape[0])
    n_unbalanced = int((diff > 1e-9).sum())
    max_abs_diff = float(diff.max()) if n_txn else 0.0

    return {
        "transactions_balanced": bool(n_unbalanced == 0),
        "n_transactions": n_txn,
        "n_unbalanced": n_unbalanced,
        "max_abs_diff": max_abs_diff,
    }


def make_tidy_gl(gl: pd.DataFrame, coa: pd.DataFrame) -> pd.DataFrame:
    df = gl.copy()

    # Safe: allow account_name/type/normal_side to already exist
    for col in ["account_name", "account_type", "normal_side"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    coa_cols = ["account_id", "account_name", "account_type", "normal_side"]
    df = df.merge(coa[coa_cols], on="account_id", how="left")

    df["debit"] = df["debit"].astype(float)
    df["credit"] = df["credit"].astype(float)
    df["dc_amount"] = df["debit"] - df["credit"]

    # Normal-side amount: positive means “in the normal direction”
    df["normal_amount"] = np.where(
        df["normal_side"] == "Debit",
        df["dc_amount"],
        -df["dc_amount"],
    )

    cols = [
        "txn_id",
        "date",
        "doc_id",
        "description",
        "account_id",
        "account_name",
        "account_type",
        "normal_side",
        "debit",
        "credit",
        "dc_amount",
        "normal_amount",
    ]
    return (
        df[cols]
        .sort_values(["date", "txn_id", "account_id"], kind="mergesort")
        .reset_index(drop=True)
    )


def compute_trial_balance(tidy: pd.DataFrame, month: str) -> pd.DataFrame:
    tb = (
        tidy.groupby(
            ["account_id", "account_name", "account_type", "normal_side"], observed=True
        )[["debit", "credit"]]
        .sum()
        .reset_index()
    )
    tb["net"] = tb["debit"] - tb["credit"]
    tb["ending_side"] = np.where(tb["net"] >= 0, "Debit", "Credit")
    tb["ending_balance"] = tb["net"].abs()
    tb = tb.drop(columns=["net"])
    tb.insert(0, "month", month)
    return tb


def _get_stmt_amount(stmt: pd.DataFrame, line: str) -> float:
    if stmt.empty:
        return 0.0
    hit = stmt.loc[stmt["line"].astype(str) == line, "amount"]
    if hit.empty:
        return 0.0
    return float(hit.iloc[0])


def _get_stmt_amount_any(stmt: pd.DataFrame, lines: list[str]) -> float:
    """Return first matching statement line amount, else 0.0."""
    for line in lines:
        v = _get_stmt_amount(stmt, line)
        if v != 0.0 or (stmt["line"].astype(str) == line).any():
            return v
    return 0.0


def _net_income_from_is_stmt(is_stmt: pd.DataFrame) -> float:
    """
    Support both LedgerLab IS schemas:
    A) Old: Sales Revenue, Total Expenses (incl. COGS), Net Income
    B) New: Sales Revenue, Cost of Goods Sold, Operating Expenses, Net Income (and optional Gross Profit)
    """
    # Prefer explicit net income if present
    if (is_stmt["line"].astype(str) == "Net Income").any():
        return float(is_stmt.loc[is_stmt["line"].astype(str) == "Net Income", "amount"].iloc[0])

    revenue = _get_stmt_amount(is_stmt, "Sales Revenue")

    if (is_stmt["line"].astype(str) == "Total Expenses (incl. COGS)").any():
        expenses = _get_stmt_amount(is_stmt, "Total Expenses (incl. COGS)")
        return revenue - expenses

    cogs = _get_stmt_amount_any(is_stmt, ["Cost of Goods Sold", "COGS"])
    opx = _get_stmt_amount_any(is_stmt, ["Operating Expenses", "OpEx", "OPEX"])
    return revenue - (cogs + opx)


def _net_income_from_tb(tb: pd.DataFrame) -> float:
    """Compute net income from TB as Revenue - Expenses (including COGS)."""
    revenue_tb = float(
        tb.loc[tb["account_type"] == "Revenue", "credit"].sum()
        - tb.loc[tb["account_type"] == "Revenue", "debit"].sum()
    )
    expenses_tb = float(
        tb.loc[tb["account_type"] == "Expense", "debit"].sum()
        - tb.loc[tb["account_type"] == "Expense", "credit"].sum()
    )
    return revenue_tb - expenses_tb


def build_statement_bridge(is_stmt: pd.DataFrame, bs_stmt: pd.DataFrame) -> pd.DataFrame:
    """
    Simple operating cash bridge (startup-month friendly):
    CFO ≈ Net Income - ΔAR - ΔInv + ΔAP
    Financing includes owner contribution.
    Beginning cash assumed 0 for this synthetic startup month.
    """
    net_income = _net_income_from_is_stmt(is_stmt)
    cash_end = _get_stmt_amount(bs_stmt, "Cash")
    ar_end = _get_stmt_amount(bs_stmt, "Accounts Receivable")
    inv_end = _get_stmt_amount(bs_stmt, "Inventory")
    ap_end = _get_stmt_amount(bs_stmt, "Accounts Payable")
    owner_cap = _get_stmt_amount(bs_stmt, "Owner Capital")

    cfo = net_income - ar_end - inv_end + ap_end
    cff = owner_cap
    net_change_cash = cfo + cff
    cash_begin = 0.0
    cash_end_from_bridge = cash_begin + net_change_cash

    rows = [
        ("Net Income", net_income),
        ("Change in Accounts Receivable", -ar_end),
        ("Change in Inventory", -inv_end),
        ("Change in Accounts Payable", ap_end),
        ("Net Cash from Operations", cfo),
        ("Owner Contribution", owner_cap),
        ("Net Cash from Financing", cff),
        ("Net Change in Cash", net_change_cash),
        ("Beginning Cash (assumed)", cash_begin),
        ("Ending Cash (from bridge)", cash_end_from_bridge),
        ("Ending Cash (balance sheet)", cash_end),
        ("Bridge Diff (abs)", abs(cash_end_from_bridge - cash_end)),
    ]
    return pd.DataFrame(rows, columns=["line", "amount"])


# -----------------------------
# Plotting
# -----------------------------
def plot_net_income_vs_cash_change(
    net_income: float, cash_change: float, outpath: pathlib.Path
) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    ax.bar(["Net Income", "Cash Change"], [net_income, cash_change])
    ax.set_title("Net Income vs Change in Cash")
    ax.set_ylabel("Amount")
    ax.grid(axis="y", linestyle=":", alpha=0.7)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


# -----------------------------
# Main analysis
# -----------------------------
def analyze_ch03(datadir: pathlib.Path, outdir: pathlib.Path, seed: int | None = None) -> Ch03Summary:
    apply_seed(seed)
    outdir.mkdir(parents=True, exist_ok=True)

    tables = load_ledgerlab_tables(datadir)
    coa = tables["chart_of_accounts"]
    gl = tables["gl_journal"]
    tb_src = tables["trial_balance_monthly"]
    is_stmt = tables["statements_is_monthly"]
    bs_stmt = tables["statements_bs_monthly"]

    # Month: prefer TB month, else infer from GL date
    if "month" in tb_src.columns and not tb_src.empty:
        month = str(tb_src.iloc[0]["month"])
    else:
        first_date = pd.to_datetime(gl["date"].iloc[0]).to_period("M")
        month = f"{first_date.year:04d}-{first_date.month:02d}"

    checks: dict[str, Any] = {}
    checks.update(check_transactions_balance(gl))

    tidy = make_tidy_gl(gl, coa)
    tb = compute_trial_balance(tidy, month=month)

    # TB reconciliation (like Ch02)
    if {"account_id", "ending_balance", "ending_side"}.issubset(tb_src.columns):
        tb_merge = tb.merge(
            tb_src[["account_id", "ending_balance", "ending_side"]].rename(
                columns={
                    "ending_balance": "ending_balance_src",
                    "ending_side": "ending_side_src",
                }
            ),
            on="account_id",
            how="left",
        )
        tb_merge["diff"] = (
            tb_merge["ending_balance"].astype(float)
            - tb_merge["ending_balance_src"].astype(float)
        ).abs()
        max_diff = float(tb_merge["diff"].max()) if not tb_merge.empty else 0.0
        checks["trial_balance_matches_source"] = bool(max_diff <= 1e-6)
        checks["trial_balance_max_abs_diff"] = max_diff
    else:
        checks["trial_balance_matches_source"] = False
        checks["trial_balance_max_abs_diff"] = None

    # Income statement tie-out (robust to LedgerLab IS schema changes)
    ni_tb = _net_income_from_tb(tb)
    ni_is = _net_income_from_is_stmt(is_stmt)
    ni_abs_diff = float(abs(ni_tb - ni_is))
    checks["income_statement_ties_to_trial_balance"] = bool(ni_abs_diff <= 1e-6)
    checks["income_statement_max_abs_diff"] = ni_abs_diff

    # Balance sheet equation check (from statement lines)
    total_assets = _get_stmt_amount(bs_stmt, "Total Assets")
    total_l_plus_e = _get_stmt_amount(bs_stmt, "Total Liabilities + Equity")
    bs_abs_diff = abs(total_assets - total_l_plus_e)
    checks["balance_sheet_equation_balances"] = bool(bs_abs_diff <= 1e-6)
    checks["balance_sheet_abs_diff"] = float(bs_abs_diff)

    # Cash flow bridge & tie-out
    bridge = build_statement_bridge(is_stmt, bs_stmt)
    cash_end_from_bridge = float(
        bridge.loc[bridge["line"] == "Ending Cash (from bridge)", "amount"].iloc[0]
    )
    cash_end_bs = float(
        bridge.loc[bridge["line"] == "Ending Cash (balance sheet)", "amount"].iloc[0]
    )
    cash_diff = abs(cash_end_from_bridge - cash_end_bs)
    checks["cash_flow_ties_to_balance_sheet_cash"] = bool(cash_diff <= 1e-6)
    checks["cash_flow_cash_abs_diff"] = float(cash_diff)

    # Metrics
    cash_change = cash_end_bs  # beginning cash assumed 0 for this synthetic startup month
    metrics = {
        "month": month,
        "n_gl_rows": int(gl.shape[0]),
        "n_transactions": int(gl["txn_id"].nunique()),
        "net_income": float(ni_is),
        "cash_change": float(cash_change),
        "net_income_minus_cash_change": float(ni_is - cash_change),
    }

    # Write outputs
    (outdir / "business_ch03_summary.json").write_text(
        json.dumps({"checks": checks, "metrics": metrics}, indent=2),
        encoding="utf-8",
    )

    bridge_out = bridge.copy()
    bridge_out.insert(0, "month", month)
    bridge_out.to_csv(outdir / "business_ch03_statement_bridge.csv", index=False)

    tb.to_csv(outdir / "business_ch03_trial_balance.csv", index=False)

    plot_net_income_vs_cash_change(
        net_income=float(ni_is),
        cash_change=float(cash_change),
        outpath=outdir / "business_ch03_net_income_vs_cash_change.png",
    )

    # Console output (matches Ch01/Ch02 style)
    print("\nChecks:")
    for k, v in checks.items():
        print(f"- {k}: {v}")

    print("\nMetrics:")
    for k, v in metrics.items():
        print(f"- {k}: {v}")

    print(f"\nWrote outputs -> {outdir}")

    return Ch03Summary(checks=checks, metrics=metrics)


# -----------------------------
# CLI
# -----------------------------
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Track D Chapter 3: statements as summary statistics (reconcile + bridge)."
    )
    p.add_argument("--datadir", type=pathlib.Path, required=True)
    p.add_argument("--outdir", type=pathlib.Path, required=True)
    p.add_argument("--seed", type=int, default=None)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    analyze_ch03(args.datadir, args.outdir, seed=args.seed)


if __name__ == "__main__":
    main()
