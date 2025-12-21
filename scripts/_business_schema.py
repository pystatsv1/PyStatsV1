# SPDX-License-Identifier: MIT
"""Shared schemas/contracts for Track D (Business).

This module defines:
- Required table names for each synthetic dataset family
- Required columns ("contracts") for each table
- Lightweight schema validation helpers

Goal: make later chapters (controls, reconciliations, forecasting) stable by
treating datasets like governed interfaces, not ad-hoc CSV dumps.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_NSO_V1 = "nso_v1"


@dataclass(frozen=True)
class TableSchema:
    name: str
    required_columns: tuple[str, ...]


NSO_V1_TABLES: tuple[TableSchema, ...] = (
    TableSchema(
        "chart_of_accounts.csv",
        ("account_id", "account_name", "account_type", "normal_side"),
    ),
    TableSchema(
        "gl_journal.csv",
        (
            "txn_id",
            "date",
            "doc_id",
            "description",
            "account_id",
            "debit",
            "credit",
            "account_name",
            "account_type",
            "normal_side",
        ),
    ),
    TableSchema(
        "trial_balance_monthly.csv",
        (
            "month",
            "account_id",
            "account_name",
            "account_type",
            "normal_side",
            "debit",
            "credit",
            "ending_side",
            "ending_balance",
        ),
    ),
    TableSchema("statements_is_monthly.csv", ("month", "line", "amount")),
    TableSchema("statements_bs_monthly.csv", ("month", "line", "amount")),
    TableSchema("statements_cf_monthly.csv", ("month", "line", "amount")),
    # Ch04 subledgers
    TableSchema(
        "inventory_movements.csv",
        (
            "month",
            "txn_id",
            "date",
            "sku",
            "movement_type",
            "qty",
            "unit_cost",
            "amount",
        ),
    ),
    TableSchema(
        "fixed_assets.csv",
        (
            "asset_id",
            "asset_name",
            "in_service_month",
            "cost",
            "useful_life_months",
            "salvage_value",
            "method",
        ),
    ),
    TableSchema(
        "depreciation_schedule.csv",
        ("month", "asset_id", "dep_expense", "accum_dep", "net_book_value"),
    ),

     # --- Chapter 5 additions ---
     TableSchema(
         name="payroll_events.csv",
         required_columns={
             "month","txn_id","date","event_type",
             "gross_wages","employee_withholding","employer_tax",
             "cash_paid","wages_payable_delta","payroll_taxes_payable_delta",
         },
     ),
     TableSchema(
         name="sales_tax_events.csv",
         required_columns={
             "month","txn_id","date","event_type",
             "taxable_sales","tax_amount","cash_paid","sales_tax_payable_delta",
         },
     ),
     TableSchema(
         name="debt_schedule.csv",
         required_columns={
             "month","loan_id","txn_id",
             "beginning_balance","payment","interest","principal","ending_balance",
         },
     ),
     TableSchema(
         name="equity_events.csv",
         required_columns={"month","txn_id","date","event_type","amount"},
     ),
     TableSchema(
         name="ap_events.csv",
         required_columns={"month","txn_id","date","vendor","invoice_id","event_type","amount","ap_delta","cash_paid"},
     ),

)


def schemas_for_dataset(dataset: str) -> tuple[TableSchema, ...]:
    if dataset == DATASET_NSO_V1:
        return NSO_V1_TABLES
    raise ValueError(f"Unknown dataset: {dataset}")


def _read_csv(path: Path, **kwargs: Any) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, **kwargs)


def validate_schema(datadir: Path, dataset: str) -> dict[str, Any]:
    """Validate presence + required columns. Returns a report dict."""
    report: dict[str, Any] = {
        "dataset": dataset,
        "datadir": str(datadir),
        "missing_tables": [],
        "tables": {},
        "ok": True,
    }

    for schema in schemas_for_dataset(dataset):
        table_path = datadir / schema.name
        if not table_path.exists():
            report["missing_tables"].append(schema.name)
            report["tables"][schema.name] = {
                "exists": False,
                "missing_columns": list(schema.required_columns),
            }
            report["ok"] = False
            continue

        df = _read_csv(table_path)
        cols = set(map(str, df.columns))
        missing = [c for c in schema.required_columns if c not in cols]
        report["tables"][schema.name] = {
            "exists": True,
            "n_rows": int(df.shape[0]),
            "missing_columns": missing,
        }
        if missing:
            report["ok"] = False

    return report
