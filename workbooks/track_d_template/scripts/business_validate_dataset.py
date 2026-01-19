# SPDX-License-Identifier: MIT
"""Track D utility: validate a dataset as a governed interface.

This is intentionally light-weight:
- validate required tables + required columns (schema contract)
- check transactions balance (GL)
- check balance sheet equation balances (if BS statements exist)

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
        return {
            "transactions_balanced": None,
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


def _get_stmt_amount(bs: pd.DataFrame, month: str, line: str) -> float:
    if bs.empty:
        return 0.0
    hit = bs.loc[
        (bs["month"].astype(str) == str(month)) & (bs["line"].astype(str) == str(line)),
        "amount",
    ]
    if hit.empty:
        return 0.0
    return float(hit.iloc[0])


def check_bs_equation(bs: pd.DataFrame) -> dict[str, Any]:
    if bs.empty or not {"month", "line", "amount"}.issubset(bs.columns):
        return {
            "balance_sheet_equation_balances": None,
            "balance_sheet_max_abs_diff": None,
            "n_months_checked": None,
        }

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

    checks: dict[str, Any] = {
        "schema_ok": bool(schema_report.get("ok", False)),
        "schema_missing_tables": list(schema_report.get("missing_tables", [])),
    }

    # Metrics: basic identity + row counts (if available from schema report)
    metrics: dict[str, Any] = {
        "dataset": dataset,
        "datadir": str(datadir),
    }

    tables_report: dict[str, Any] = dict(schema_report.get("tables", {}))
    if tables_report:
        metrics["table_row_counts"] = {
            name: int(info.get("n_rows", 0)) for name, info in tables_report.items() if info.get("exists")
        }

    # Deeper checks (only if the relevant tables exist)
    gl_path = datadir / "gl_journal.csv"
    if gl_path.exists():
        gl = _read_csv(gl_path, dtype={"txn_id": str, "account_id": str, "doc_id": str})
        checks.update(check_transactions_balance(gl))
        metrics["n_gl_rows"] = int(gl.shape[0])
        metrics["n_gl_transactions"] = int(gl["txn_id"].nunique())
    else:
        checks.update(
            {
                "transactions_balanced": None,
                "n_transactions": None,
                "n_unbalanced": None,
                "max_abs_diff": None,
            }
        )

    bs_path = datadir / "statements_bs_monthly.csv"
    if bs_path.exists():
        bs = _read_csv(bs_path)
        checks.update(check_bs_equation(bs))
        if not bs.empty and "month" in bs.columns:
            metrics["n_statement_months"] = int(bs["month"].astype(str).nunique())
    else:
        checks.update(
            {
                "balance_sheet_equation_balances": None,
                "balance_sheet_max_abs_diff": None,
                "n_months_checked": None,
            }
        )

    payload = {"schema": schema_report, "checks": checks, "metrics": metrics}
    outpath = outdir / "business_validate_summary.json"
    outpath.write_text(json.dumps(payload, indent=2), encoding="utf-8")

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
    missing = summary.checks.get("schema_missing_tables", [])
    if missing:
        print("Missing tables:", ", ".join(map(str, missing)))

    print("Transactions balanced:", summary.checks.get("transactions_balanced"))
    print("BS equation balances:", summary.checks.get("balance_sheet_equation_balances"))
    print(f"\nWrote -> {args.outdir / 'business_validate_summary.json'}")


if __name__ == "__main__":
    main()
