# SPDX-License-Identifier: MIT
"""Schema contracts for Track D business datasets."""

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


CONTRACT_TABLES: dict[str, TableSchema] = {
    "chart_of_accounts": TableSchema(
        name="chart_of_accounts.csv",
        required_columns=("account_id", "account_name", "account_type", "normal_side"),
    ),
    "gl_journal": TableSchema(
        name="gl_journal.csv",
        required_columns=("txn_id", "date", "doc_id", "description", "account_id", "debit", "credit"),
    ),
    "trial_balance_monthly": TableSchema(
        name="trial_balance_monthly.csv",
        required_columns=(
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
    "statements_is_monthly": TableSchema(
        name="statements_is_monthly.csv",
        required_columns=("month", "line", "amount"),
    ),
    "statements_bs_monthly": TableSchema(
        name="statements_bs_monthly.csv",
        required_columns=("month", "line", "amount"),
    ),
    "statements_cf_monthly": TableSchema(
        name="statements_cf_monthly.csv",
        required_columns=("month", "line", "amount"),
    ),
    "inventory_movements": TableSchema(
        name="inventory_movements.csv",
        required_columns=("month", "txn_id", "date", "sku", "movement_type", "qty", "unit_cost", "amount"),
    ),
    "fixed_assets": TableSchema(
        name="fixed_assets.csv",
        required_columns=(
            "asset_id",
            "asset_name",
            "in_service_month",
            "cost",
            "useful_life_months",
            "salvage_value",
            "method",
        ),
    ),
    "depreciation_schedule": TableSchema(
        name="depreciation_schedule.csv",
        required_columns=("month", "asset_id", "dep_expense", "accum_dep", "net_book_value"),
    ),
    # Chapter 5
    "payroll_events": TableSchema(
        name="payroll_events.csv",
        required_columns=(
            "month",
            "txn_id",
            "date",
            "event_type",
            "gross_wages",
            "employee_withholding",
            "employer_tax",
            "cash_paid",
            "wages_payable_delta",
            "payroll_taxes_payable_delta",
        ),
    ),
    "sales_tax_events": TableSchema(
        name="sales_tax_events.csv",
        required_columns=(
            "month",
            "txn_id",
            "date",
            "event_type",
            "taxable_sales",
            "tax_amount",
            "cash_paid",
            "sales_tax_payable_delta",
        ),
    ),
    "debt_schedule": TableSchema(
        name="debt_schedule.csv",
        required_columns=("month", "loan_id", "txn_id", "beginning_balance", "payment", "interest", "principal", "ending_balance"),
    ),
    "equity_events": TableSchema(
        name="equity_events.csv",
        required_columns=("month", "txn_id", "date", "event_type", "amount"),
    ),
    "ap_events": TableSchema(
        name="ap_events.csv",
        required_columns=("month", "txn_id", "date", "vendor", "invoice_id", "event_type", "amount", "ap_delta", "cash_paid"),
    ),
    # Chapter 6
    "ar_events": TableSchema(
        name="ar_events.csv",
        required_columns=("month", "txn_id", "date", "customer", "invoice_id", "event_type", "amount", "ar_delta", "cash_received"),
    ),
    "bank_statement": TableSchema(
        name="bank_statement.csv",
        required_columns=("month", "bank_txn_id", "posted_date", "description", "amount", "gl_txn_id"),
    ),
}

NSO_V1_TABLE_ORDER: tuple[str, ...] = (
    "chart_of_accounts",
    "gl_journal",
    "trial_balance_monthly",
    "statements_is_monthly",
    "statements_bs_monthly",
    "statements_cf_monthly",
    "inventory_movements",
    "fixed_assets",
    "depreciation_schedule",
    # Chapter 5
    "payroll_events",
    "sales_tax_events",
    "debt_schedule",
    "equity_events",
    "ap_events",
    # Chapter 6
    "ar_events",
    "bank_statement",
)

NSO_V1_TABLES: tuple[TableSchema, ...] = tuple(CONTRACT_TABLES[k] for k in NSO_V1_TABLE_ORDER)


def schemas_for_dataset(dataset: str) -> tuple[TableSchema, ...]:
    if dataset == DATASET_NSO_V1:
        return NSO_V1_TABLES
    raise ValueError(f"Unknown dataset: {dataset}")


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

        df = pd.read_csv(table_path)
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
