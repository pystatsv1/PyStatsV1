"""
Track D - Chapter 5
Liabilities, payroll, taxes, and equity: obligations and structure.

Reads NSO v1 tables, recomputes key monthly totals from the GL, and performs
controls-as-validation tie-outs:

- Debt schedule ↔ interest expense + notes payable rollforward
- Payroll events ↔ payroll expense + wages payable + payroll taxes payable rollforward
- Sales tax events ↔ sales tax payable rollforward
- Equity events ↔ contributions/draws + equity rollforward (simple)

Writes summary checks/metrics + rollforward tables + (optional) a plot.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from scripts._cli import apply_seed


@dataclass(frozen=True)
class Ch05Summary:
    checks: dict[str, Any]
    metrics: dict[str, Any]


def _read_csv(path: pathlib.Path, **kwargs: Any) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required table: {path}")
    return pd.read_csv(path, **kwargs)


def load_nso_v1_tables(datadir: pathlib.Path) -> dict[str, pd.DataFrame]:
    # Core
    tables: dict[str, pd.DataFrame] = {
        "chart_of_accounts": _read_csv(datadir / "chart_of_accounts.csv", dtype={"account_id": str}),
        "gl_journal": _read_csv(
            datadir / "gl_journal.csv",
            dtype={"txn_id": str, "doc_id": str, "account_id": str},
        ),
        "trial_balance_monthly": _read_csv(datadir / "trial_balance_monthly.csv", dtype={"account_id": str}),
        "statements_is_monthly": _read_csv(datadir / "statements_is_monthly.csv"),
        "statements_bs_monthly": _read_csv(datadir / "statements_bs_monthly.csv"),
        "statements_cf_monthly": _read_csv(datadir / "statements_cf_monthly.csv"),
        # Subledgers / events (Ch04/Ch05)
        "inventory_movements": _read_csv(datadir / "inventory_movements.csv", dtype={"txn_id": str}),
        "fixed_assets": _read_csv(datadir / "fixed_assets.csv", dtype={"asset_id": str}),
        "depreciation_schedule": _read_csv(datadir / "depreciation_schedule.csv", dtype={"asset_id": str}),
        # Ch05 additions
        "payroll_events": _read_csv(datadir / "payroll_events.csv", dtype={"txn_id": str}),
        "sales_tax_events": _read_csv(datadir / "sales_tax_events.csv", dtype={"txn_id": str}),
        "debt_schedule": _read_csv(datadir / "debt_schedule.csv", dtype={"loan_id": str, "txn_id": str}),
        "equity_events": _read_csv(datadir / "equity_events.csv", dtype={"txn_id": str}),
        "ap_events": _read_csv(datadir / "ap_events.csv", dtype={"txn_id": str, "invoice_id": str}),
    }
    return tables


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


def _month_series_from_date(gl: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(gl["date"]).dt.to_period("M").astype(str)


def gl_monthly_amount(gl: pd.DataFrame, account_id: str) -> pd.Series:
    """
    Monthly signed amount in debit-credit space: debit - credit.
    For expense accounts, this is typically positive.
    """
    df = gl.copy()
    df["month"] = _month_series_from_date(df)
    g = df.loc[df["account_id"].astype(str) == str(account_id)].groupby("month", observed=True)[["debit", "credit"]].sum()
    amt = (g["debit"].astype(float) - g["credit"].astype(float))
    return amt.sort_index()


def tb_signed_normal_balance(tb: pd.DataFrame, account_id: str) -> pd.Series:
    """
    Monthly ending balance signed in the account's normal direction:
    + means "in normal_side", - means opposite.

    tb has: month, account_id, normal_side, ending_side, ending_balance
    """
    df = tb.loc[tb["account_id"].astype(str) == str(account_id)].copy()
    if df.empty:
        return pd.Series(dtype=float)

    df["ending_balance"] = df["ending_balance"].astype(float)
    same = df["ending_side"].astype(str) == df["normal_side"].astype(str)
    df["signed_normal"] = df["ending_balance"].where(same, -df["ending_balance"])
    out = df.set_index(df["month"].astype(str))["signed_normal"].sort_index()
    out.index.name = "month"
    return out


def _rollforward_from_deltas(
    ending_balance: pd.Series,
    delta: pd.Series,
) -> pd.DataFrame:
    """
    Build a rollforward table with:
      begin + delta = end
    using ending balances as source of truth.
    """
    months = sorted(set(ending_balance.index.astype(str)) | set(delta.index.astype(str)))
    end = ending_balance.reindex(months).fillna(0.0).astype(float)
    d = delta.reindex(months).fillna(0.0).astype(float)
    begin = end.shift(1).fillna(0.0)
    rf = pd.DataFrame({"begin": begin, "delta": d, "end": end}, index=pd.Index(months, name="month"))
    rf["calc_end"] = rf["begin"] + rf["delta"]
    rf["diff"] = (rf["calc_end"] - rf["end"]).abs()
    return rf.reset_index()


def plot_liabilities_over_time(
    outpath: pathlib.Path,
    wages_payable_end: pd.Series,
    payroll_tax_payable_end: pd.Series,
    sales_tax_payable_end: pd.Series,
    notes_payable_end: pd.Series,
) -> None:
    df = pd.DataFrame(
        {
            "Wages Payable": wages_payable_end,
            "Payroll Taxes Payable": payroll_tax_payable_end,
            "Sales Tax Payable": sales_tax_payable_end,
            "Notes Payable": notes_payable_end,
        }
    ).fillna(0.0)

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    df.plot(ax=ax)  # default colors
    ax.set_title("Key Liabilities (Ending Balances) Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Ending Balance (normal-direction signed)")
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def analyze_ch05(datadir: pathlib.Path, outdir: pathlib.Path, seed: int | None = None) -> Ch05Summary:
    apply_seed(seed)
    outdir.mkdir(parents=True, exist_ok=True)

    t = load_nso_v1_tables(datadir)
    gl = t["gl_journal"]
    tb = t["trial_balance_monthly"]

    payroll = t["payroll_events"].copy()
    sales_tax = t["sales_tax_events"].copy()
    debt = t["debt_schedule"].copy()
    equity = t["equity_events"].copy()
    ap = t["ap_events"].copy()

    checks: dict[str, Any] = {}
    checks.update(check_transactions_balance(gl))

    # ---- Accounts (match NSO v1 COA) ----
    ACCTS = {
        "wages_expense": "6300",
        "payroll_tax_expense": "6500",
        "interest_expense": "6600",
        "wages_payable": "2110",
        "payroll_taxes_payable": "2120",
        "sales_tax_payable": "2100",
        "notes_payable": "2200",
        "owner_capital": "3000",
        "owner_draw": "3200",
        "accounts_payable": "2000",
    }

    # ---- Monthly GL totals ----
    wages_exp_gl = gl_monthly_amount(gl, ACCTS["wages_expense"])
    pr_tax_exp_gl = gl_monthly_amount(gl, ACCTS["payroll_tax_expense"])
    interest_exp_gl = gl_monthly_amount(gl, ACCTS["interest_expense"])

    # ---- Payroll tie-outs ----
    # payroll_events schema:
    # month, txn_id, date, event_type,
    # gross_wages, employee_withholding, employer_tax,
    # cash_paid, wages_payable_delta, payroll_taxes_payable_delta
    payroll["month"] = payroll["month"].astype(str)
    for c in [
        "gross_wages",
        "employee_withholding",
        "employer_tax",
        "cash_paid",
        "wages_payable_delta",
        "payroll_taxes_payable_delta",
    ]:
        payroll[c] = payroll[c].astype(float)

    wages_exp_sub = payroll.groupby("month", observed=True)["gross_wages"].sum().sort_index()
    pr_tax_exp_sub = payroll.groupby("month", observed=True)["employer_tax"].sum().sort_index()

    wages_exp_diff = (wages_exp_sub.reindex(wages_exp_gl.index).fillna(0.0) - wages_exp_gl.fillna(0.0)).abs()
    pr_tax_exp_diff = (pr_tax_exp_sub.reindex(pr_tax_exp_gl.index).fillna(0.0) - pr_tax_exp_gl.fillna(0.0)).abs()

    checks["payroll_expense_ties_to_gl"] = bool(float(wages_exp_diff.max() if not wages_exp_diff.empty else 0.0) <= 1e-6)
    checks["payroll_expense_max_abs_diff"] = float(wages_exp_diff.max()) if not wages_exp_diff.empty else 0.0

    checks["payroll_tax_expense_ties_to_gl"] = bool(float(pr_tax_exp_diff.max() if not pr_tax_exp_diff.empty else 0.0) <= 1e-6)
    checks["payroll_tax_expense_max_abs_diff"] = float(pr_tax_exp_diff.max()) if not pr_tax_exp_diff.empty else 0.0

    # Wages payable rollforward: ending = begin + delta (deltas from payroll_events)
    wages_payable_end = tb_signed_normal_balance(tb, ACCTS["wages_payable"])
    wages_payable_delta = payroll.groupby("month", observed=True)["wages_payable_delta"].sum().sort_index()
    wages_rf = _rollforward_from_deltas(wages_payable_end, wages_payable_delta)
    checks["wages_payable_rollforward_ties"] = bool(float(wages_rf["diff"].max() if not wages_rf.empty else 0.0) <= 1e-6)
    checks["wages_payable_max_abs_diff"] = float(wages_rf["diff"].max()) if not wages_rf.empty else 0.0

    # Payroll taxes payable rollforward
    payroll_tax_payable_end = tb_signed_normal_balance(tb, ACCTS["payroll_taxes_payable"])
    payroll_tax_payable_delta = payroll.groupby("month", observed=True)["payroll_taxes_payable_delta"].sum().sort_index()
    prtax_rf = _rollforward_from_deltas(payroll_tax_payable_end, payroll_tax_payable_delta)
    checks["payroll_taxes_payable_rollforward_ties"] = bool(float(prtax_rf["diff"].max() if not prtax_rf.empty else 0.0) <= 1e-6)
    checks["payroll_taxes_payable_max_abs_diff"] = float(prtax_rf["diff"].max()) if not prtax_rf.empty else 0.0

    # ---- Sales tax tie-outs ----
    sales_tax["month"] = sales_tax["month"].astype(str)
    for c in ["taxable_sales", "tax_amount", "cash_paid", "sales_tax_payable_delta"]:
        sales_tax[c] = sales_tax[c].astype(float)

    sales_tax_payable_end = tb_signed_normal_balance(tb, ACCTS["sales_tax_payable"])
    sales_tax_delta = sales_tax.groupby("month", observed=True)["sales_tax_payable_delta"].sum().sort_index()
    st_rf = _rollforward_from_deltas(sales_tax_payable_end, sales_tax_delta)
    checks["sales_tax_payable_rollforward_ties"] = bool(float(st_rf["diff"].max() if not st_rf.empty else 0.0) <= 1e-6)
    checks["sales_tax_payable_max_abs_diff"] = float(st_rf["diff"].max()) if not st_rf.empty else 0.0

    # ---- Debt tie-outs ----
    # debt_schedule schema: month, loan_id, txn_id, beginning_balance, payment, interest, principal, ending_balance
    debt["month"] = debt["month"].astype(str)
    for c in ["beginning_balance", "payment", "interest", "principal", "ending_balance"]:
        debt[c] = debt[c].astype(float)

    # Interest ties: sum schedule interest per month == GL interest expense
    debt_interest = debt.groupby("month", observed=True)["interest"].sum().sort_index()
    interest_diff = (debt_interest.reindex(interest_exp_gl.index).fillna(0.0) - interest_exp_gl.fillna(0.0)).abs()
    checks["interest_expense_ties_to_gl"] = bool(float(interest_diff.max() if not interest_diff.empty else 0.0) <= 1e-6)
    checks["interest_expense_max_abs_diff"] = float(interest_diff.max()) if not interest_diff.empty else 0.0

    # Notes payable rollforward: ending balances vs deltas (delta = +new borrowing - principal)
    notes_payable_end = tb_signed_normal_balance(tb, ACCTS["notes_payable"])
    # Use schedule principal as reduction; borrowing may appear as a one-time +delta via a special "originations" row (principal negative)
    # We store deltas explicitly in the simulator; here we infer:
    # month_delta = (begin->end) from schedule (end - begin)
    debt_delta = (debt.groupby("month", observed=True)["ending_balance"].sum() - debt.groupby("month", observed=True)["beginning_balance"].sum()).sort_index()
    np_rf = _rollforward_from_deltas(notes_payable_end, debt_delta)
    checks["notes_payable_rollforward_ties"] = bool(float(np_rf["diff"].max() if not np_rf.empty else 0.0) <= 1e-6)
    checks["notes_payable_max_abs_diff"] = float(np_rf["diff"].max()) if not np_rf.empty else 0.0

    # ---- Accounts payable rollforward (optional tie-out from ap_events) ----
    ap["month"] = ap["month"].astype(str)
    ap["ap_delta"] = ap["ap_delta"].astype(float)
    ap_end = tb_signed_normal_balance(tb, ACCTS["accounts_payable"])
    ap_delta = ap.groupby("month", observed=True)["ap_delta"].sum().sort_index()
    ap_rf = _rollforward_from_deltas(ap_end, ap_delta)
    checks["accounts_payable_rollforward_ties"] = bool(float(ap_rf["diff"].max() if not ap_rf.empty else 0.0) <= 1e-6)
    checks["accounts_payable_max_abs_diff"] = float(ap_rf["diff"].max()) if not ap_rf.empty else 0.0

    # ---- Equity event ties (simple) ----
    equity["month"] = equity["month"].astype(str)
    equity["amount"] = equity["amount"].astype(float)

    # Contributions should match GL credit to owner_capital (in debit-credit space, credit is negative),
    # but we compare absolute “economic” amounts:
    contrib_sub = equity.loc[equity["event_type"] == "contribution"].groupby("month", observed=True)["amount"].sum().sort_index()
    draw_sub = equity.loc[equity["event_type"] == "draw"].groupby("month", observed=True)["amount"].sum().sort_index()

    owner_cap_gl = gl_monthly_amount(gl, ACCTS["owner_capital"])  # debit-credit
    owner_draw_gl = gl_monthly_amount(gl, ACCTS["owner_draw"])

    # owner_capital postings are credits, so owner_cap_gl is usually negative; compare -owner_cap_gl to contrib amounts
    contrib_diff = (contrib_sub.reindex(owner_cap_gl.index).fillna(0.0) - (-owner_cap_gl).fillna(0.0)).abs()
    draw_diff = (draw_sub.reindex(owner_draw_gl.index).fillna(0.0) - owner_draw_gl.fillna(0.0)).abs()

    checks["owner_contributions_tie_to_gl"] = bool(float(contrib_diff.max() if not contrib_diff.empty else 0.0) <= 1e-6)
    checks["owner_contributions_max_abs_diff"] = float(contrib_diff.max()) if not contrib_diff.empty else 0.0
    checks["owner_draws_tie_to_gl"] = bool(float(draw_diff.max() if not draw_diff.empty else 0.0) <= 1e-6)
    checks["owner_draws_max_abs_diff"] = float(draw_diff.max()) if not draw_diff.empty else 0.0

    # ---- Outputs ----
    metrics = {
        "n_months": int(tb["month"].nunique()) if "month" in tb.columns else None,
        "n_gl_rows": int(gl.shape[0]),
        "n_payroll_events": int(payroll.shape[0]),
        "n_sales_tax_events": int(sales_tax.shape[0]),
        "n_debt_rows": int(debt.shape[0]),
        "n_equity_events": int(equity.shape[0]),
    }

    # Write summary + rollforwards
    (outdir / "business_ch05_summary.json").write_text(
        json.dumps({"checks": checks, "metrics": metrics}, indent=2),
        encoding="utf-8",
    )

    wages_rf.to_csv(outdir / "business_ch05_wages_payable_rollforward.csv", index=False)
    prtax_rf.to_csv(outdir / "business_ch05_payroll_taxes_payable_rollforward.csv", index=False)
    st_rf.to_csv(outdir / "business_ch05_sales_tax_payable_rollforward.csv", index=False)
    np_rf.to_csv(outdir / "business_ch05_notes_payable_rollforward.csv", index=False)
    ap_rf.to_csv(outdir / "business_ch05_accounts_payable_rollforward.csv", index=False)

    # Optional plot (lightweight and useful)
    plot_liabilities_over_time(
        outpath=outdir / "business_ch05_liabilities_over_time.png",
        wages_payable_end=wages_payable_end,
        payroll_tax_payable_end=payroll_tax_payable_end,
        sales_tax_payable_end=sales_tax_payable_end,
        notes_payable_end=notes_payable_end,
    )

    # Console output (match style)
    print("\nChecks:")
    for k, v in checks.items():
        print(f"- {k}: {v}")

    print("\nMetrics:")
    for k, v in metrics.items():
        print(f"- {k}: {v}")

    print(f"\nWrote outputs -> {outdir}")

    return Ch05Summary(checks=checks, metrics=metrics)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Track D Chapter 5: liabilities, payroll, taxes, equity (tie-outs).")
    p.add_argument("--datadir", type=pathlib.Path, required=True)
    p.add_argument("--outdir", type=pathlib.Path, required=True)
    p.add_argument("--seed", type=int, default=None)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    analyze_ch05(args.datadir, args.outdir, seed=args.seed)


if __name__ == "__main__":
    main()
