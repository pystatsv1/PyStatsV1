"""Track D reconciliation helpers.

This module mirrors the public API of ``scripts/_business_recon.py``.

Rationale
---------
We want chapter/workbook code to be able to import a stable implementation from
the installed package (``pystatsv1.trackd``) while keeping the repo-local
``scripts/_business_recon.py`` as a thin, backwards-compatible shim.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def write_json(obj: Any, path: str | Path) -> Path:
    """Write a JSON file (pretty-printed) and return the written path."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")
    return p


def build_cash_txns_from_gl(gl: pd.DataFrame) -> pd.DataFrame:
    """Group cash lines in GL into one row per txn_id with net cash impact."""
    cash_lines = gl.loc[
        gl["account_id"].astype(str) == "1000",
        ["txn_id", "date", "description", "debit", "credit"],
    ].copy()
    if cash_lines.empty:
        return pd.DataFrame(columns=["txn_id", "date", "description", "amount"])

    cash_lines["cash_net"] = cash_lines["debit"].astype(float) - cash_lines["credit"].astype(float)

    cash_txn = (
        cash_lines.groupby("txn_id", observed=True)
        .agg(date=("date", "min"), description=("description", "first"), amount=("cash_net", "sum"))
        .reset_index()
    )
    cash_txn = cash_txn.loc[cash_txn["amount"].abs() > 1e-9].copy()
    cash_txn = cash_txn.sort_values(["date", "txn_id"], kind="mergesort").reset_index(drop=True)
    return cash_txn


def build_cash_txn_from_gl(gl: pd.DataFrame) -> pd.DataFrame:
    """Alias for build_cash_txns_from_gl (keeps chapter script imports stable)."""
    return build_cash_txns_from_gl(gl)


@dataclass(frozen=True)
class BankReconOutputs:
    cash_txns: pd.DataFrame
    matches: pd.DataFrame
    exceptions: pd.DataFrame


def bank_reconcile(*, bank_statement: pd.DataFrame, cash_txns: pd.DataFrame, amount_tol: float = 0.01) -> BankReconOutputs:
    """Reconcile bank statement lines against book cash transactions."""
    bank = bank_statement.copy()
    if bank.empty:
        empty = pd.DataFrame()
        return BankReconOutputs(cash_txns=cash_txns.copy(), matches=empty, exceptions=empty)

    bank["gl_txn_id"] = pd.to_numeric(bank["gl_txn_id"], errors="coerce").astype("Int64")
    bank["amount"] = bank["amount"].astype(float)

    cash = cash_txns.copy()
    cash["txn_id"] = cash["txn_id"].astype(int)
    cash["amount"] = cash["amount"].astype(float)

    matches = bank.merge(
        cash.rename(columns={"txn_id": "gl_txn_id", "amount": "gl_amount", "date": "gl_date"}),
        on="gl_txn_id",
        how="left",
        validate="m:1",
    )

    # convenience flag for summaries
    matches["is_matched"] = matches["gl_amount"].notna()

    exceptions: list[dict[str, Any]] = []

    # 1) duplicate bank_txn_id
    dup_mask = matches["bank_txn_id"].astype(str).duplicated(keep=False)
    if dup_mask.any():
        for _, r in matches.loc[dup_mask].iterrows():
            exceptions.append(
                {
                    "exception_type": "bank_duplicate_txn_id",
                    "month": str(r.get("month", "")),
                    "bank_txn_id": str(r.get("bank_txn_id")),
                    "posted_date": str(r.get("posted_date")),
                    "gl_txn_id": (int(r["gl_txn_id"]) if pd.notna(r["gl_txn_id"]) else np.nan),
                    "bank_amount": float(r.get("amount", 0.0)),
                    "gl_amount": float(r.get("gl_amount", np.nan)) if pd.notna(r.get("gl_amount", np.nan)) else np.nan,
                    "details": "Duplicate bank_txn_id appears multiple times in bank feed.",
                }
            )

    # 2) unmatched bank item
    unmatched_bank = matches["gl_txn_id"].isna() | matches["gl_amount"].isna()
    if unmatched_bank.any():
        for _, r in matches.loc[unmatched_bank].iterrows():
            exceptions.append(
                {
                    "exception_type": "bank_unmatched_item",
                    "month": str(r.get("month", "")),
                    "bank_txn_id": str(r.get("bank_txn_id")),
                    "posted_date": str(r.get("posted_date")),
                    "gl_txn_id": (int(r["gl_txn_id"]) if pd.notna(r["gl_txn_id"]) else np.nan),
                    "bank_amount": float(r.get("amount", 0.0)),
                    "gl_amount": np.nan,
                    "details": "Bank statement line has no matching GL cash transaction.",
                }
            )

    # 3) amount mismatch
    matched = matches.loc[matches["gl_amount"].notna()].copy()
    mism = matched.loc[(matched["amount"] - matched["gl_amount"]).abs() > float(amount_tol)]
    if not mism.empty:
        for _, r in mism.iterrows():
            exceptions.append(
                {
                    "exception_type": "amount_mismatch",
                    "month": str(r.get("month", "")),
                    "bank_txn_id": str(r.get("bank_txn_id")),
                    "posted_date": str(r.get("posted_date")),
                    "gl_txn_id": int(r["gl_txn_id"]),
                    "bank_amount": float(r.get("amount", np.nan)),
                    "gl_amount": float(r.get("gl_amount", np.nan)),
                    "details": f"Bank amount differs from book by > {amount_tol}.",
                }
            )

    # 4) book-only transactions (cash txn not seen on bank)
    bank_gl_ids = set(matches.loc[matches["gl_txn_id"].notna(), "gl_txn_id"].astype(int).tolist())
    book_only = cash.loc[~cash["txn_id"].isin(bank_gl_ids)].copy()
    if not book_only.empty:
        for _, r in book_only.iterrows():
            exceptions.append(
                {
                    "exception_type": "book_unmatched_cash_txn",
                    "month": str(r["date"])[:7],
                    "bank_txn_id": np.nan,
                    "posted_date": np.nan,
                    "gl_txn_id": int(r["txn_id"]),
                    "bank_amount": np.nan,
                    "gl_amount": float(r["amount"]),
                    "details": "Cash transaction in GL does not appear in bank feed.",
                }
            )

    exc_df = pd.DataFrame(exceptions)
    if not exc_df.empty:
        exc_df = exc_df.sort_values(["exception_type", "month", "bank_txn_id"], kind="mergesort").reset_index(drop=True)

    return BankReconOutputs(cash_txns=cash, matches=matches, exceptions=exc_df)


def reconcile_bank_statement(bank_statement: pd.DataFrame, gl_journal: pd.DataFrame, *, amount_tol: float = 0.01) -> BankReconOutputs:
    """Wrapper used by chapter script: bank feed vs GL."""
    cash_txns = build_cash_txns_from_gl(gl_journal)
    return bank_reconcile(bank_statement=bank_statement, cash_txns=cash_txns, amount_tol=amount_tol)


def _ending_balance_from_tb(tb_month: pd.DataFrame, account_id: str) -> float:
    """Return balance in its normal direction (positive if normal-side)."""
    hit = tb_month.loc[tb_month["account_id"].astype(str) == str(account_id)]
    if hit.empty:
        return 0.0
    normal = str(hit.iloc[0]["normal_side"])
    ending_side = str(hit.iloc[0]["ending_side"])
    bal = float(hit.iloc[0]["ending_balance"])
    return bal if ending_side == normal else -bal


def ar_rollforward_vs_tb(trial_balance_monthly: pd.DataFrame, ar_events: pd.DataFrame) -> pd.DataFrame:
    """Compute AR rollforward (begin + activity = end) and compare to TB."""
    tb = trial_balance_monthly.copy()
    tb["month"] = tb["month"].astype(str)

    months = sorted(tb["month"].unique().tolist())

    ar_monthly = (
        ar_events.assign(month=lambda d: d["month"].astype(str))
        .groupby("month", observed=True)["ar_delta"]
        .sum()
        .reindex(months, fill_value=0.0)
    )

    rows: list[dict[str, Any]] = []
    ar_begin = 0.0
    for m in months:
        ar_delta = float(ar_monthly.loc[m])
        ar_end_events = float(ar_begin + ar_delta)

        tb_m = tb.loc[tb["month"] == m]
        ar_end_tb = float(_ending_balance_from_tb(tb_m, "1100"))
        diff = float(ar_end_events - ar_end_tb)

        rows.append(
            {
                "month": m,
                "ar_begin": float(ar_begin),
                "ar_delta": float(ar_delta),
                "ar_end_from_events": float(ar_end_events),
                "ar_end_from_tb": float(ar_end_tb),
                "diff": float(diff),
            }
        )
        ar_begin = ar_end_events

    return pd.DataFrame(rows)


def build_ar_rollforward(trial_balance_monthly: pd.DataFrame, ar_events: pd.DataFrame) -> pd.DataFrame:
    """Alias for ar_rollforward_vs_tb."""
    return ar_rollforward_vs_tb(trial_balance_monthly, ar_events)
