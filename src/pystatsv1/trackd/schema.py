# SPDX-License-Identifier: MIT
"""Schema contracts for Track D business datasets.

This module centralizes the Track D CSV contracts so both:
- the workbook template scripts, and
- future BYOD adapters
can validate datasets with consistent, friendly errors.

Design notes
- Keep the existing workbook behavior: validate_schema(...) returns a report dict.
- Provide assert_schema(...) for fail-fast workflows.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from ._errors import TrackDSchemaError

DATASET_NSO_V1 = "nso_v1"


@dataclass(frozen=True)
class TableSchema:
    """A simple contract for one required CSV table."""

    # Filename on disk, including .csv
    name: str
    # Required column headers that must appear in the CSV
    required_columns: tuple[str, ...]


# Canonical contract table definitions.
# Keys are "logical" table identifiers used for ordering / grouping.
CONTRACT_TABLES: dict[str, TableSchema] = {
    "chart_of_accounts": TableSchema(
        name="chart_of_accounts.csv",
        required_columns=("account_id", "account_name", "account_type", "normal_side"),
    ),
    "gl_journal": TableSchema(
        name="gl_journal.csv",
        required_columns=(
            "txn_id",
            "date",
            "doc_id",
            "description",
            "account_id",
            "debit",
            "credit",
        ),
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
        required_columns=(
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
        required_columns=(
            "month",
            "loan_id",
            "txn_id",
            "beginning_balance",
            "payment",
            "interest",
            "principal",
            "ending_balance",
        ),
    ),
    "equity_events": TableSchema(
        name="equity_events.csv",
        required_columns=("month", "txn_id", "date", "event_type", "amount"),
    ),
    "ap_events": TableSchema(
        name="ap_events.csv",
        required_columns=(
            "month",
            "txn_id",
            "date",
            "vendor",
            "invoice_id",
            "event_type",
            "amount",
            "ap_delta",
            "cash_paid",
        ),
    ),
    # Chapter 6
    "ar_events": TableSchema(
        name="ar_events.csv",
        required_columns=(
            "month",
            "txn_id",
            "date",
            "customer",
            "invoice_id",
            "event_type",
            "amount",
            "ar_delta",
            "cash_received",
        ),
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

# Convenience alias used by some internal helpers/tests.
NSO_V1: dict[str, TableSchema] = {k: CONTRACT_TABLES[k] for k in NSO_V1_TABLE_ORDER}


def schemas_for_dataset(dataset: str) -> tuple[TableSchema, ...]:
    if dataset == DATASET_NSO_V1:
        return NSO_V1_TABLES
    raise ValueError(f"Unknown dataset: {dataset}")


def _read_header(path: Path) -> list[str]:
    # Small helper to keep schema checks cheap.
    # We only need headers for required-column validation.
    df = pd.read_csv(path, nrows=0)
    return [str(c) for c in df.columns]


def validate_schema(datadir: Path, dataset: str) -> dict[str, Any]:
    """Validate presence + required columns.

    Returns a report dict (workbook-friendly), e.g.:
    {
      "ok": bool,
      "dataset": "nso_v1",
      "datadir": "...",
      "missing_tables": [...],
      "tables": {
          "chart_of_accounts.csv": {"exists": bool, "missing_columns": [...], "n_rows": int?},
          ...
      }
    }
    """

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

        cols = set(_read_header(table_path))
        missing = [c for c in schema.required_columns if c not in cols]

        # Optional: if the file is big, avoid reading it all just for row count.
        # For now, keep it simple: an approximate count is not worth it.
        df = pd.read_csv(table_path)

        report["tables"][schema.name] = {
            "exists": True,
            "n_rows": int(df.shape[0]),
            "missing_columns": missing,
        }

        if missing:
            report["ok"] = False

    return report


def validate_table_map(table_map: Mapping[str, Path], schemas: Mapping[str, TableSchema]) -> dict[str, Any]:
    """Validate a provided mapping of logical table keys -> CSV paths.

    This is useful for future BYOD adapters where files may not live in a single directory.
    The report format matches validate_schema(...), but keys are schema.name (filename).
    """

    report: dict[str, Any] = {
        "missing_tables": [],
        "tables": {},
        "ok": True,
    }

    for key, schema in schemas.items():
        path = table_map.get(key)
        if path is None or not Path(path).exists():
            report["missing_tables"].append(schema.name)
            report["tables"][schema.name] = {
                "exists": False,
                "missing_columns": list(schema.required_columns),
            }
            report["ok"] = False
            continue

        cols = set(_read_header(Path(path)))
        missing = [c for c in schema.required_columns if c not in cols]
        report["tables"][schema.name] = {
            "exists": True,
            "missing_columns": missing,
        }
        if missing:
            report["ok"] = False

    return report


def assert_schema(datadir: Path, dataset: str) -> None:
    """Fail-fast wrapper around validate_schema(...).

    Raises TrackDSchemaError with one friendly summary message if invalid.
    """

    report = validate_schema(datadir=datadir, dataset=dataset)
    if report.get("ok"):
        return

    missing_tables: list[str] = list(report.get("missing_tables", []))
    tables: dict[str, Any] = dict(report.get("tables", {}))
    missing_cols = {
        name: info.get("missing_columns", [])
        for name, info in tables.items()
        if info.get("exists") and info.get("missing_columns")
    }

    lines: list[str] = [
        "Track D dataset schema check failed.",
        f"Dataset: {dataset}",
        f"Data directory: {datadir}",
        "",
    ]

    if missing_tables:
        lines += ["Missing CSV files:", *[f"  - {n}" for n in missing_tables], ""]

    if missing_cols:
        lines += ["CSV files with missing required columns:"]
        for name, cols in sorted(missing_cols.items()):
            lines.append(f"  - {name}: missing {', '.join(map(str, cols))}")
        lines.append("")

    lines += [
        "Fix: ensure the required CSVs exist and match the Track D headers.",
        "Tip: compare your exported CSV headers against the downloads in the workbook docs.",
    ]

    raise TrackDSchemaError("\n".join(lines))
