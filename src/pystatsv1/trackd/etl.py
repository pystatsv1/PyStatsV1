"""Track D ETL helpers.

This module mirrors the public API of ``scripts/_business_etl.py``.

Rationale
---------
We want chapter/workbook code to be able to import a stable implementation from
the installed package (``pystatsv1.trackd``) while keeping the repo-local
``scripts/_business_etl.py`` as a thin, backwards-compatible shim.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class GLPrepOutputs:
    """Outputs for Chapter 7 ETL."""

    gl_tidy: pd.DataFrame
    gl_monthly_summary: pd.DataFrame
    summary: dict[str, Any]


def _to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0.0).astype(float)



def _infer_normal_side(account_type: pd.Series) -> pd.Series:
    """Infer a normal side (debit/credit) from an account type label.

    This is intentionally forgiving: simplified student datasets often only include
    ``account_type`` (e.g., Asset, Liability, Revenue, Expense, Equity).

    If a label contains ``contra``, we flip the inferred side (e.g., contra-asset
    is normally credit). Unknown/blank types yield an empty string.
    """

    s = account_type.astype(str).str.strip().str.lower()
    is_contra = s.str.contains("contra")
    base = s.str.replace("contra", "", regex=False).str.strip()

    # Broad, case-insensitive buckets
    side = pd.Series("", index=account_type.index, dtype="object")
    side = side.mask(base.str.contains("asset"), "debit")
    side = side.mask(base.str.contains("expense"), "debit")
    side = side.mask(base.str.contains("liabil"), "credit")
    side = side.mask(base.str.contains("equity"), "credit")
    side = side.mask(base.str.contains("revenue") | base.str.contains("income"), "credit")

    # Flip contra accounts when we have a known base side
    side = side.mask(is_contra & side.eq("debit"), "credit")
    side = side.mask(is_contra & side.eq("credit"), "debit")
    return side


def prepare_gl_tidy(gl_journal: pd.DataFrame, chart_of_accounts: pd.DataFrame) -> pd.DataFrame:
    """Return a line-level tidy GL dataset.

    Parameters
    ----------
    gl_journal:
        Raw journal export with debit/credit columns.
    chart_of_accounts:
        COA mapping account_id -> account_name/account_type/normal_side.

    Returns
    -------
    pd.DataFrame
        A normalized table with one row per GL line, plus:
        - joined account labels
        - parsed dates + a month key
        - `raw_amount = debit - credit` (debit-positive convention)
        - `amount` where sign is aligned to the account's normal side
    """

    gl = gl_journal.copy()
    coa = chart_of_accounts.copy()

    gl["account_id"] = gl["account_id"].astype(str)
    coa["account_id"] = coa["account_id"].astype(str)

    # `normal_side` is optional in simplified COA exports; infer it from account_type when absent.
    if "normal_side" not in coa.columns:
        coa["normal_side"] = _infer_normal_side(
            coa.get("account_type", pd.Series("", index=coa.index))
        )
    else:
        mask = coa["normal_side"].isna() | (coa["normal_side"].astype(str).str.strip() == "")
        if mask.any():
            inferred = _infer_normal_side(coa.get("account_type", pd.Series("", index=coa.index)))
            coa.loc[mask, "normal_side"] = inferred.loc[mask]

    # Be forgiving: some templates may omit label columns; fill with empty strings.
    for col in ("account_name", "account_type"):
        if col not in coa.columns:
            coa[col] = ""

    coa_cols = ["account_id", "account_name", "account_type", "normal_side"]
    out = gl.merge(
        coa[coa_cols],
        on="account_id",
        how="left",
        validate="many_to_one",
        suffixes=("", "_coa"),
    )

    # If the GL already carried labels, keep them; otherwise fill from the COA.
    for col in ("account_name", "account_type", "normal_side"):
        rhs = f"{col}_coa"
        if rhs in out.columns:
            if col in out.columns:
                out[col] = out[col].where(out[col].notna() & (out[col].astype(str) != ""), out[rhs])
            else:
                out[col] = out[rhs]
            out = out.drop(columns=[rhs])


    # If still missing, infer from account_type (useful for BYOD or minimal COA inputs).
    mask = out["normal_side"].isna() | (out["normal_side"].astype(str).str.strip() == "")
    if mask.any():
        out.loc[mask, "normal_side"] = _infer_normal_side(
            out.get("account_type", pd.Series("", index=out.index))
        ).loc[mask]


    # Be forgiving for simplified inputs: allow missing txn_id/doc_id/description.
    if "txn_id" not in out.columns:
        if "doc_id" in out.columns:
            out["txn_id"] = out["doc_id"].astype(str)
        else:
            out["txn_id"] = pd.Series(range(1, len(out) + 1), index=out.index).astype(str)
    else:
        out["txn_id"] = out["txn_id"].astype(str)

    if "doc_id" not in out.columns:
        out["doc_id"] = out["txn_id"].astype(str)
    out["doc_id"] = out["doc_id"].astype(str)

    if "description" not in out.columns:
        out["description"] = ""
    out["description"] = out["description"].astype(str)

    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["month"] = out["date"].dt.strftime("%Y-%m")

    had_debit = "debit" in out.columns
    had_credit = "credit" in out.columns
    had_dc = "dc" in out.columns
    had_amount = "amount" in out.columns

    dc_input = out["dc"].astype(str).str.upper() if had_dc else pd.Series("", index=out.index)
    amount_input = _to_float(out["amount"]) if had_amount else pd.Series(0.0, index=out.index)

    if "debit" not in out.columns:
        out["debit"] = 0.0
    if "credit" not in out.columns:
        out["credit"] = 0.0

    out["debit"] = _to_float(out["debit"])
    out["credit"] = _to_float(out["credit"])

    # Support the minimal (dc, amount) input format by materializing debit/credit.
    if (not had_debit and not had_credit) and had_dc and had_amount:
        mask_d = dc_input.eq("D")
        mask_c = dc_input.eq("C")
        out.loc[mask_d, "debit"] = amount_input.loc[mask_d]
        out.loc[mask_c, "credit"] = amount_input.loc[mask_c]

    # Prefer provided dc, else infer from debit/credit.
    out["dc"] = dc_input.where(dc_input.isin(["D", "C"]), "")
    out.loc[out["dc"].eq(""), "dc"] = np.where(
        out["debit"] > 0,
        "D",
        np.where(out["credit"] > 0, "C", ""),
    )

    # Debit-positive convention
    out["raw_amount"] = out["debit"] - out["credit"]

    # Signed-by-normal-side: positive means "account increased"
    normal = out["normal_side"].astype(str).str.lower()
    out["amount"] = np.where(normal.eq("credit"), -out["raw_amount"], out["raw_amount"])

    # Stable row ids (helpful for downstream joins)
    out = out.sort_values(["date", "txn_id", "account_id"], kind="mergesort").reset_index(drop=True)
    out["line_no"] = out.groupby("txn_id").cumcount() + 1
    out["gl_line_id"] = out["txn_id"].astype(str) + "-" + out["line_no"].astype(str)

    cols = [
        "gl_line_id",
        "txn_id",
        "line_no",
        "date",
        "month",
        "doc_id",
        "description",
        "account_id",
        "account_name",
        "account_type",
        "normal_side",
        "dc",
        "debit",
        "credit",
        "raw_amount",
        "amount",
    ]

    # Keep any extra columns at the end (future-proof)
    extra = [c for c in out.columns if c not in cols]
    return out[cols + extra]


def build_gl_tidy_dataset(gl: pd.DataFrame, coa: pd.DataFrame) -> pd.DataFrame:
    """Backward-compatible alias for :func:`prepare_gl_tidy`.

    Chapter 8 imports ``build_gl_tidy_dataset``.
    Chapter 7 uses the canonical name ``prepare_gl_tidy``.
    """

    return prepare_gl_tidy(gl, coa)


def prepare_gl_monthly_summary(gl_tidy: pd.DataFrame) -> pd.DataFrame:
    """Monthly rollup of tidy GL.

    Produces one row per (month, account) with debit/credit totals and a
    signed net change (`net_change`) aligned to the account's normal side.
    """

    g = gl_tidy.copy()

    group_cols = ["month", "account_id", "account_name", "account_type", "normal_side"]
    out = (
        g.groupby(group_cols, dropna=False)
        .agg(
            n_lines=("gl_line_id", "count"),
            debit=("debit", "sum"),
            credit=("credit", "sum"),
            net_change=("amount", "sum"),
        )
        .reset_index()
    )

    out["debit"] = out["debit"].astype(float)
    out["credit"] = out["credit"].astype(float)
    out["net_change"] = out["net_change"].astype(float)

    return out.sort_values(["month", "account_id"], kind="mergesort").reset_index(drop=True)




def build_data_dictionary() -> dict[str, str]:
    """A lightweight data dictionary for the Chapter 7 output tables.

    This is intentionally small and human-readable (useful for docs + downstream
    notebooks). It is *not* intended to be a formal metadata standard.
    """

    return {
        # Keys used in gl_tidy.csv
        "gl_line_id": "Stable line identifier (txn_id-line_no).",
        "txn_id": "Journal transaction id (groups debit/credit lines for one event).",
        "line_no": "Line number within txn_id (1..k).",
        "date": "Journal posting date (YYYY-MM-DD).",
        "month": "Month key derived from date (YYYY-MM).",
        "doc_id": "Source document id (invoice, payroll run, bank transfer, etc.).",
        "description": "Text description from the journal.",
        "account_id": "Chart-of-accounts id.",
        "account_name": "Chart-of-accounts account name.",
        "account_type": "High-level account class (Asset, Liability, Equity, Revenue, Expense).",
        "normal_side": "Normal balance side for the account (debit or credit).",
        "debit": "Debit amount for the line (0 if none).",
        "credit": "Credit amount for the line (0 if none).",
        "dc": "D if debit>0, C if credit>0, blank if both are 0.",
        "raw_amount": "Single-column amount in debit-positive convention: debit - credit.",
        "amount": "Signed amount aligned to the account's normal side (positive means the account increased).",
        # Keys used in gl_monthly_summary.csv
        "n_lines": "Number of GL lines aggregated into the month/account group.",
        "net_change": "Sum of `amount` in the month/account group.",
    }


def analyze_gl_preparation(gl_journal: pd.DataFrame, chart_of_accounts: pd.DataFrame) -> GLPrepOutputs:
    """Compute Chapter 7 outputs + a small QC summary."""

    gl_tidy = prepare_gl_tidy(gl_journal, chart_of_accounts)
    monthly = prepare_gl_monthly_summary(gl_tidy)

    n_lines = int(len(gl_tidy))
    n_txns = int(gl_tidy["txn_id"].nunique()) if n_lines else 0
    n_missing_accounts = int(gl_tidy["account_name"].isna().sum())
    n_bad_dates = int(gl_tidy["date"].isna().sum())

    # Basic accounting invariant: sum of raw debit-positive amounts should be ~0
    raw_total = float(gl_tidy["raw_amount"].sum()) if n_lines else 0.0
    gl_balances = bool(abs(raw_total) < 1e-6)

    summary: dict[str, Any] = {
        "checks": {
            "gl_balances_raw_amount_sum_zero": gl_balances,
            "coa_join_coverage_ok": n_missing_accounts == 0,
            "no_missing_coa_mappings": n_missing_accounts == 0,
            "all_gl_dates_parse": n_bad_dates == 0,
            "no_unparseable_dates": n_bad_dates == 0,
        },
        "metrics": {
            "n_gl_lines": n_lines,
            "n_txns": n_txns,
            "n_accounts": int(gl_tidy["account_id"].nunique()) if n_lines else 0,
            "n_months": int(gl_tidy["month"].nunique()) if n_lines else 0,
            "n_missing_coa_mappings": n_missing_accounts,
            "n_bad_dates": n_bad_dates,
            "raw_amount_sum": raw_total,
        },
        "data_dictionary": build_data_dictionary(),
        "notes": {
            "amount_definition": (
                "amount is signed so positive means the account increased on its normal side; "
                "raw_amount uses debit-positive convention (debit - credit)."
            )
        },
    }

    return GLPrepOutputs(gl_tidy=gl_tidy, gl_monthly_summary=monthly, summary=summary)

__all__ = [
    "GLPrepOutputs",
    "prepare_gl_tidy",
    "build_gl_tidy_dataset",
    "prepare_gl_monthly_summary",
    "build_data_dictionary",
    "analyze_gl_preparation",
]
