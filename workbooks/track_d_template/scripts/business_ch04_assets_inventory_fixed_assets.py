# SPDX-License-Identifier: MIT
"""Track D - Chapter 4
Assets: inventory, fixed assets, depreciation (and leases, conceptual).

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* business_ch04_inventory_rollforward.csv
* business_ch04_margin_bridge.csv
* business_ch04_depreciation_rollforward.csv
* business_ch04_summary.json
* business_ch04_gross_margin_over_time.png
* business_ch04_depreciation_over_time.png

Reads NSO v1 tables, builds rollforwards and tie-outs:
- Inventory movements -> Inventory ending balance
- Inventory movements -> COGS (sale issues + count adjustments)
- Depreciation schedule -> Depreciation Expense + Accumulated Depreciation

Outputs:
- business_ch04_summary.json
- business_ch04_inventory_rollforward.csv
- business_ch04_margin_bridge.csv
- business_ch04_depreciation_rollforward.csv
- (optional) plots"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from scripts._cli import apply_seed


@dataclass(frozen=True)
class Ch04Summary:
    checks: dict[str, Any]
    metrics: dict[str, Any]


def _read_csv(path: Path, **kwargs: Any) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required table: {path}")
    return pd.read_csv(path, **kwargs)


def _months_from_table(df: pd.DataFrame) -> list[str]:
    if df.empty or "month" not in df.columns:
        return []
    months = sorted(set(df["month"].astype(str)))
    return months


def _get_stmt_amount(stmt: pd.DataFrame, month: str, line: str) -> float:
    hit = stmt.loc[(stmt["month"].astype(str) == month) & (stmt["line"].astype(str) == line), "amount"]
    if hit.empty:
        return 0.0
    return float(hit.iloc[0])


def plot_series(df: pd.DataFrame, x: str, y: str, title: str, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(df[x], df[y], marker="o")
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.grid(True, linestyle=":", alpha=0.7)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def analyze_ch04(datadir: Path, outdir: Path, seed: int | None = None) -> Ch04Summary:
    apply_seed(seed)
    outdir.mkdir(parents=True, exist_ok=True)

    gl = _read_csv(datadir / "gl_journal.csv", dtype={"txn_id": str, "account_id": str, "doc_id": str})
    inv = _read_csv(datadir / "inventory_movements.csv", dtype={"txn_id": str})
    fa = _read_csv(datadir / "fixed_assets.csv")
    dep = _read_csv(datadir / "depreciation_schedule.csv")
    is_stmt = _read_csv(datadir / "statements_is_monthly.csv")
    bs_stmt = _read_csv(datadir / "statements_bs_monthly.csv")

    months = _months_from_table(is_stmt)
    if not months:
        raise ValueError("No months found in statements_is_monthly.csv")

    # --- Inventory rollforward + tie to BS/GL ---
    inv["amount"] = inv["amount"].astype(float)
    inv["qty"] = inv["qty"].astype(float)

    roll_rows: list[dict[str, Any]] = []
    beg_inv = 0.0

    for m in months:
        mdf = inv.loc[inv["month"].astype(str) == m]
        purchases = float(mdf.loc[mdf["movement_type"] == "purchase", "amount"].sum())
        issues = float(mdf.loc[mdf["movement_type"] == "sale_issue", "amount"].sum())  # negative
        adjusts = float(mdf.loc[mdf["movement_type"] == "count_adjustment", "amount"].sum())

        end_sub = float(beg_inv + purchases + issues + adjusts)

        # inventory from BS statement
        end_bs = float(_get_stmt_amount(bs_stmt, m, "Inventory"))

        roll_rows.append(
            {
                "month": m,
                "begin_inventory": beg_inv,
                "purchases": purchases,
                "sale_issues": issues,
                "count_adjustments": adjusts,
                "end_inventory_subledger": end_sub,
                "end_inventory_balance_sheet": end_bs,
                "abs_diff": abs(end_sub - end_bs),
            }
        )
        beg_inv = end_sub

    inv_roll = pd.DataFrame(roll_rows)

    # --- COGS tie: COGS expense should equal - (inventory deltas from issues + adjustments) ---
    cogs_rows: list[dict[str, Any]] = []
    for m in months:
        mdf = inv.loc[inv["month"].astype(str) == m]
        inv_delta_for_cogs = float(
            mdf.loc[mdf["movement_type"].isin(["sale_issue", "count_adjustment"]), "amount"].sum()
        )
        cogs_from_subledger = float(-inv_delta_for_cogs)

        cogs_stmt = float(_get_stmt_amount(is_stmt, m, "Cost of Goods Sold"))

        cogs_rows.append(
            {
                "month": m,
                "cogs_from_subledger": cogs_from_subledger,
                "cogs_from_income_statement": cogs_stmt,
                "abs_diff": abs(cogs_from_subledger - cogs_stmt),
            }
        )
    cogs_tie = pd.DataFrame(cogs_rows)

    # --- Depreciation tie: schedule -> GL/statement ---
    dep["dep_expense"] = dep["dep_expense"].astype(float)
    dep_by_month = dep.groupby("month", observed=True)["dep_expense"].sum().reset_index()

    dep_rows: list[dict[str, Any]] = []
    for m in months:
        dep_exp = float(dep_by_month.loc[dep_by_month["month"].astype(str) == m, "dep_expense"].sum())

        # GL depreciation expense (6400) in the month (debits minus credits)
        gl_m = gl.loc[pd.to_datetime(gl["date"]).dt.to_period("M").astype(str) == m]
        dep_gl = float(
            gl_m.loc[gl_m["account_id"].astype(str) == "6400", "debit"].astype(float).sum()
            - gl_m.loc[gl_m["account_id"].astype(str) == "6400", "credit"].astype(float).sum()
        )

        # Accum dep in GL is credit-normal 1350; ending balance per BS is negative line,
        # so use absolute value from BS line to compare.
        accum_bs_line = float(_get_stmt_amount(bs_stmt, m, "Accumulated Depreciation"))  # negative
        accum_bs_abs = float(abs(accum_bs_line))

        accum_sched = float(
            dep.loc[(dep["month"].astype(str) == m), "accum_dep"].sum()
        )  # note: sum across assets

        dep_rows.append(
            {
                "month": m,
                "dep_expense_schedule": dep_exp,
                "dep_expense_gl": dep_gl,
                "dep_expense_abs_diff": abs(dep_exp - dep_gl),
                "accum_dep_schedule": accum_sched,
                "accum_dep_balance_sheet_abs": accum_bs_abs,
                "accum_dep_abs_diff": abs(accum_sched - accum_bs_abs),
            }
        )
    dep_roll = pd.DataFrame(dep_rows)

    # --- Margin bridge (Sales, COGS, GM%) ---
    margin_rows: list[dict[str, Any]] = []
    for m in months:
        sales = float(_get_stmt_amount(is_stmt, m, "Sales Revenue"))
        cogs = float(_get_stmt_amount(is_stmt, m, "Cost of Goods Sold"))
        gp = float(sales - cogs)
        gm_pct = float(gp / sales) if sales != 0 else 0.0
        margin_rows.append({"month": m, "sales": sales, "cogs": cogs, "gross_profit": gp, "gross_margin_pct": gm_pct})
    margin = pd.DataFrame(margin_rows)

    # --- Checks ---
    checks: dict[str, Any] = {}

    inv_max_diff = float(inv_roll["abs_diff"].max()) if not inv_roll.empty else 0.0
    checks["inventory_subledger_ties_to_gl_inventory"] = bool(inv_max_diff <= 1e-6)
    checks["inventory_max_abs_diff"] = inv_max_diff

    cogs_max_diff = float(cogs_tie["abs_diff"].max()) if not cogs_tie.empty else 0.0
    checks["cogs_subledger_ties_to_gl_cogs"] = bool(cogs_max_diff <= 1e-6)
    checks["cogs_max_abs_diff"] = cogs_max_diff

    dep_exp_max = float(dep_roll["dep_expense_abs_diff"].max()) if not dep_roll.empty else 0.0
    checks["depreciation_schedule_ties_to_gl_dep_expense"] = bool(dep_exp_max <= 1e-6)
    checks["depreciation_expense_max_abs_diff"] = dep_exp_max

    accum_max = float(dep_roll["accum_dep_abs_diff"].max()) if not dep_roll.empty else 0.0
    checks["accum_dep_ties_to_gl_accum_dep"] = bool(accum_max <= 1e-6)
    checks["accum_dep_max_abs_diff"] = accum_max

    # --- Metrics ---
    metrics: dict[str, Any] = {
        "n_months": int(len(months)),
        "n_gl_rows": int(gl.shape[0]),
        "n_inventory_movements": int(inv.shape[0]),
        "n_fixed_assets": int(fa.shape[0]),
    }

    # --- Write outputs ---
    (outdir / "business_ch04_inventory_rollforward.csv").write_text(inv_roll.to_csv(index=False), encoding="utf-8")
    (outdir / "business_ch04_margin_bridge.csv").write_text(margin.to_csv(index=False), encoding="utf-8")
    (outdir / "business_ch04_depreciation_rollforward.csv").write_text(dep_roll.to_csv(index=False), encoding="utf-8")

    (outdir / "business_ch04_summary.json").write_text(
        json.dumps({"checks": checks, "metrics": metrics}, indent=2),
        encoding="utf-8",
    )

    # Optional plots (keep simple)
    plot_series(
        margin,
        x="month",
        y="gross_margin_pct",
        title="Gross Margin % over time",
        outpath=outdir / "business_ch04_gross_margin_over_time.png",
    )

    plot_series(
        dep_roll,
        x="month",
        y="dep_expense_gl",
        title="Depreciation Expense (GL) over time",
        outpath=outdir / "business_ch04_depreciation_over_time.png",
    )

    # Console output
    print("\nChecks:")
    for k, v in checks.items():
        print(f"- {k}: {v}")

    print("\nMetrics:")
    for k, v in metrics.items():
        print(f"- {k}: {v}")

    print(f"\nWrote outputs -> {outdir}")

    return Ch04Summary(checks=checks, metrics=metrics)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Track D Chapter 4: Assets (inventory + fixed assets + depreciation).")
    p.add_argument("--datadir", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--seed", type=int, default=None)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    analyze_ch04(args.datadir, args.outdir, seed=args.seed)


if __name__ == "__main__":
    main()
