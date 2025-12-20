# SPDX-License-Identifier: MIT
"""Track D utility: validate a dataset as a governed interface.

This is intentionally light-weight:
- checks required tables + required columns
- checks transactions balance (GL)
- checks BS equation balances (if statements exist)

Later chapters can treat reconciliations as "dataset validation", not clerical work.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from scripts._business_schema import DATASET_NSO_V1, validate_schema
from scripts._cli import apply_seed


@dataclass(frozen=True)
class ValidateSummary:
    checks: dict[str, Any]
    metrics: dict[str, Any]
    schema: dict[str, Any]


def _read_csv(path: Path, **kwargs: Any) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required table: {path}")
    return pd.read_csv(path, **kwargs)


def check_transactions_balance(gl: pd.DataFrame) -> dict[str, Any]:
    required = {"txn_id", "debit", "credit"}
    if not required.issubset(gl.columns):
        return {"transactions_balanced": False, "n_transactions": None, "max_abs_diff": None}

    g = gl.groupby("txn_id", observed=True)[["debit", "credit"]].sum()
    diff = (g["debit"].astype(float) - g["credit"].astype(float)).abs()
    n_txn = int(g.shape[0])
    max_abs_diff = float(diff.max()) if n_txn else 0.0
    return {
        "transactions_balanced": bool(max_abs_diff <= 1e-9),
        "n_transactions": n_txn,
        "max_abs_diff": max_abs_diff,
    }


def _get_stmt_amount(stmt: pd.DataFrame, month: str, line: str) -> float:
    hit = stmt.loc[(stmt["month"].astype(str) == month) & (stmt["line"].astype(str) == line), "amount"]
    if hit.empty:
        return 0.0
    return float(hit.iloc[0])


def check_bs_equation(bs: pd.DataFrame) -> dict[str, Any]:
    if bs.empty or not {"month", "line", "amount"}.issubset(bs.columns):
        return {"balance_sheet_equation_balances": None, "balance_sheet_max_abs_diff": None}

    months = sorted(set(bs["month"].astype(str)))
    diffs: list[float] = []
    for m in months:
        assets = _get_stmt_amount(bs, m, "Total Assets")
        lpe = _get_stmt_amount(bs, m, "Total Liabilities + Equity")
        diffs.append(abs(float(assets) - float(lpe)))
    max_diff = float(np.max(diffs)) if diffs else 0.0
    return {
        "balance_sheet_equation_balances": bool(max_diff <= 1e-6),
        "balance_sheet_max_abs_diff": max_diff,
        "n_months_checked": int(len(diffs)),
    }


def validate_dataset(datadir: Path, outdir: Path, dataset: str, seed: int | None = None) -> ValidateSummary:
    apply_seed(seed)
    outdir.mkdir(parents=True, exist_ok=True)

    schema_report = validate_schema(datadir, dataset=dataset)

    checks: dict[str, Any] = {"schema_ok": bool(schema_report["ok"])}

    metrics: dict[str, Any] = {"dataset": dataset, "datadir": str(datadir)}

    # Only attempt deeper checks if core tables exist
    gl_path = datadir / "gl_journal.csv"
    if gl_path.exists():
        gl = _read_csv(gl_path, dtype={"txn_id": str, "account_id": str, "doc_id": str})
        checks.update(check_transactions_balance(gl))
        metrics["n_gl_rows"] = int(gl.shape[0])
    else:
        checks["transactions_balanced"] = None

    bs_path = datadir / "statements_bs_monthly.csv"
    if bs_path.exists():
        bs = _read_csv(bs_path)
        checks.update(check_bs_equation(bs))
    else:
        checks["balance_sheet_equation_balances"] = None

    payload = {"schema": schema_report, "checks": checks, "metrics": metrics}
    (outdir / "business_validate_summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return ValidateSummary(checks=checks, metrics=metrics, schema=schema_report)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Track D: validate dataset schema + basic accounting checks.")
    p.add_argument("--datadir", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--dataset", type=str, default=DATASET_NSO_V1)
    p.add_argument("--seed", type=int, default=None)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    summary = validate_dataset(args.datadir, args.outdir, dataset=args.dataset, seed=args.seed)

    print("\nSchema OK:", summary.checks.get("schema_ok"))
    print("Transactions balanced:", summary.checks.get("transactions_balanced"))
    print("BS equation balances:", summary.checks.get("balance_sheet_equation_balances"))
    print(f"\nWrote -> {args.outdir / 'business_validate_summary.json'}")


if __name__ == "__main__":
    main()
