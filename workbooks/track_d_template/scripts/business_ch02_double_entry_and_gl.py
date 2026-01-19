# SPDX-License-Identifier: MIT
"""Track D – Chapter 2: Double-entry and the general ledger as a database.

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* business_ch02_gl_tidy.csv
* business_ch02_trial_balance.csv
* business_ch02_account_rollup.csv
* business_ch02_tb_by_account.png
* business_ch02_summary.json
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd

from scripts._cli import apply_seed, base_parser


@dataclass(frozen=True)
class Ch02Summary:
    checks: dict[str, Any]
    metrics: dict[str, Any]


ALLOWED_ACCOUNT_TYPES: set[str] = {"Asset", "Liability", "Equity", "Revenue", "Expense"}


def _require_columns(df: pd.DataFrame, cols: Iterable[str], name: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing required columns: {', '.join(missing)}")


def load_ledgerlab_core(datadir: pathlib.Path) -> dict[str, pd.DataFrame]:
    """Load the core LedgerLab tables used in Chapter 2."""
    tables = {
        "chart_of_accounts": datadir / "chart_of_accounts.csv",
        "gl_journal": datadir / "gl_journal.csv",
        "trial_balance_monthly": datadir / "trial_balance_monthly.csv",
    }
    missing = [name for name, path in tables.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing required LedgerLab tables in {datadir}: {', '.join(missing)}"
        )

    read_specs: dict[str, dict[str, Any]] = {
        "chart_of_accounts": {"dtype": {"account_id": str}},
        "gl_journal": {"dtype": {"txn_id": str, "doc_id": str, "account_id": str}},
        "trial_balance_monthly": {"dtype": {"account_id": str}},
    }

    return {name: pd.read_csv(path, **read_specs[name]) for name, path in tables.items()}


def check_schema(coa: pd.DataFrame, gl: pd.DataFrame) -> dict[str, Any]:
    _require_columns(
        coa,
        ["account_id", "account_name", "account_type", "normal_side"],
        "chart_of_accounts",
    )
    _require_columns(
        gl,
        ["txn_id", "date", "doc_id", "description", "account_id", "debit", "credit"],
        "gl_journal",
    )

    checks: dict[str, Any] = {}

    checks["coa_account_ids_unique"] = bool(coa["account_id"].is_unique)

    bad_types = sorted(set(coa["account_type"]) - ALLOWED_ACCOUNT_TYPES)
    checks["coa_account_types_valid"] = len(bad_types) == 0
    checks["coa_bad_account_types"] = bad_types

    bad_sides = sorted(set(coa["normal_side"]) - {"Debit", "Credit"})
    checks["coa_normal_sides_valid"] = len(bad_sides) == 0
    checks["coa_bad_normal_sides"] = bad_sides

    coa_ids = set(coa["account_id"].astype(str))
    gl_ids = set(gl["account_id"].astype(str))
    missing_ids = sorted(gl_ids - coa_ids)
    checks["gl_account_ids_in_coa"] = len(missing_ids) == 0
    checks["gl_missing_account_ids"] = missing_ids[:20]

    checks["gl_debits_nonnegative"] = bool((gl["debit"].astype(float) >= 0).all())
    checks["gl_credits_nonnegative"] = bool((gl["credit"].astype(float) >= 0).all())

    return checks


def check_transactions_balance(gl: pd.DataFrame, tol: float = 1e-6) -> dict[str, Any]:
    by_txn = gl.groupby("txn_id", as_index=False)[["debit", "credit"]].sum()
    by_txn["diff"] = (by_txn["debit"] - by_txn["credit"]).abs()
    bad = by_txn.loc[by_txn["diff"] > tol]
    return {
        "transactions_balanced": bool(bad.empty),
        "n_transactions": int(by_txn.shape[0]),
        "n_unbalanced": int(bad.shape[0]),
        "max_abs_diff": float(by_txn["diff"].max()) if not by_txn.empty else 0.0,
    }


def make_tidy_gl(gl: pd.DataFrame, coa: pd.DataFrame) -> pd.DataFrame:
    """Analysis-ready GL export with explicit signed-amount conventions.

    Handles cases where gl_journal already includes COA-like columns by
    coalescing values instead of creating _x/_y suffix confusion.
    """
    # Bring only COA columns we need (and name them with a suffix to avoid collisions)
    coa_small = coa[["account_id", "account_name", "account_type", "normal_side"]].copy()

    df = gl.merge(coa_small, on="account_id", how="left", suffixes=("", "_coa"))

    # Coalesce: prefer existing GL columns if present, otherwise use COA
    for col in ["account_name", "account_type", "normal_side"]:
        col_coa = f"{col}_coa"
        if col in df.columns and col_coa in df.columns:
            df[col] = df[col].where(df[col].notna(), df[col_coa])
            df = df.drop(columns=[col_coa])
        elif col_coa in df.columns and col not in df.columns:
            df = df.rename(columns={col_coa: col})

    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Convention A: debit-positive, credit-negative
    df["dc_amount"] = df["debit"].astype(float) - df["credit"].astype(float)

    # Convention B: normal-balance-positive
    df["normal_amount"] = np.where(
        df["normal_side"] == "Debit", df["dc_amount"], -df["dc_amount"]
    ).astype(float)

    # Simple statement mapping
    df["statement"] = np.where(df["account_type"].isin(["Revenue", "Expense"]), "IS", "BS")

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
        "statement",
    ]
    return df[cols].sort_values(["date", "txn_id", "account_id"], kind="mergesort").reset_index(drop=True)



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


def plot_tb_by_account(tb: pd.DataFrame, outpath: pathlib.Path, top_n: int = 10) -> None:
    top = tb.sort_values("ending_balance", ascending=False).head(top_n).copy()
    if top.empty:
        return

    labels = top["account_name"].astype(str).to_list()
    values = top["ending_balance"].astype(float).to_list()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(labels, values)
    ax.set_title(f"Trial Balance (Top {len(values)} accounts by balance)")
    ax.set_ylabel("Ending balance (absolute)")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", linestyle=":", alpha=0.7)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def analyze_ch02(datadir: pathlib.Path, outdir: pathlib.Path, seed: int | None = None) -> Ch02Summary:
    apply_seed(seed)
    outdir.mkdir(parents=True, exist_ok=True)

    tables = load_ledgerlab_core(datadir)
    coa = tables["chart_of_accounts"]
    gl = tables["gl_journal"]
    tb_src = tables["trial_balance_monthly"]

    # month: prefer provided TB month column, else infer from first GL date
    if "month" in tb_src.columns and not tb_src.empty:
        month = str(tb_src.iloc[0]["month"])
    else:
        first_date = pd.to_datetime(gl["date"].iloc[0]).to_period("M")
        month = f"{first_date.year:04d}-{first_date.month:02d}"

    checks: dict[str, Any] = {}
    checks.update(check_schema(coa, gl))
    checks.update(check_transactions_balance(gl))

    tidy = make_tidy_gl(gl, coa)
    tb = compute_trial_balance(tidy, month=month)

    # Compare recomputed TB to source TB (lightweight consistency check)
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

    rollup = (
        tidy.groupby(["account_type", "statement"], observed=True)["normal_amount"]
        .sum()
        .reset_index()
        .rename(columns={"normal_amount": "total_normal_amount"})
        .sort_values(["statement", "account_type"])
        .reset_index(drop=True)
    )

    metrics = {
        "month": month,
        "n_gl_rows": int(tidy.shape[0]),
        "n_transactions": int(tidy["txn_id"].nunique()),
        "n_accounts_used": int(tidy["account_id"].nunique()),
    }

    tidy.to_csv(outdir / "business_ch02_gl_tidy.csv", index=False)
    tb.to_csv(outdir / "business_ch02_trial_balance.csv", index=False)
    rollup.to_csv(outdir / "business_ch02_account_rollup.csv", index=False)
    plot_tb_by_account(tb, outdir / "business_ch02_tb_by_account.png")

    payload = {
        "chapter": "business_ch02_double_entry_and_gl",
        "datadir": str(datadir),
        "seed": seed,
        "checks": checks,
        "metrics": metrics,
    }
    (outdir / "business_ch02_summary.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    return Ch02Summary(checks=checks, metrics=metrics)


def main() -> None:
    parser = base_parser("Track D Chapter 2: Double-entry & the GL as a database")
    parser.add_argument(
        "--datadir",
        type=pathlib.Path,
        default=pathlib.Path("data/synthetic/ledgerlab_ch01"),
        help="Directory containing LedgerLab core tables",
    )
    parser.set_defaults(outdir=pathlib.Path("outputs/track_d"))
    args = parser.parse_args()

    try:
        summary = analyze_ch02(args.datadir, args.outdir, seed=args.seed)
    except FileNotFoundError as e:
        print(str(e))
        print("Hint: run `make business-sim` first.")
        return

    print("\nChecks:")
    for k, v in summary.checks.items():
        print(f"- {k}: {v}")

    print("\nMetrics:")
    for k, v in summary.metrics.items():
        print(f"- {k}: {v}")

    print(f"\nWrote outputs -> {args.outdir}")


if __name__ == "__main__":
    main()
