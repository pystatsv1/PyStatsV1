# SPDX-License-Identifier: MIT
"""GnuCash CSV export adapter (GL splits -> core_gl normalized tables).

This adapter consumes the output of:

    File -> Export -> Export Transactions to CSV

with "Simple Layout" unchecked (the multi-line/complex export).

It then produces the Track D "core_gl" normalized tables:

    normalized/chart_of_accounts.csv
    normalized/gl_journal.csv

We infer `account_type` and `normal_side` from the top-level account group
(Assets/Liabilities/Equity/Income/Expenses). This is intentionally pragmatic:
it keeps the adapter free and cross-platform without requiring GnuCash APIs.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from .base import NormalizeContext
from .mapping import clean_cell, normalize_col_name, parse_money
from .._errors import TrackDDataError


@dataclass(frozen=True)
class _AcctMeta:
    account_type: str
    normal_side: str


_ROOT_META = {
    "assets": _AcctMeta("Asset", "Debit"),
    "liabilities": _AcctMeta("Liability", "Credit"),
    "equity": _AcctMeta("Equity", "Credit"),
    "income": _AcctMeta("Revenue", "Credit"),
    "expenses": _AcctMeta("Expense", "Debit"),
}


def _acct_meta_from_full_name(full_name: str) -> _AcctMeta:
    root = (full_name.split(":", 1)[0] if full_name else "").strip().lower()
    meta = _ROOT_META.get(root)
    if not meta:
        raise TrackDDataError(
            "GnuCash export uses unexpected top-level account group: "
            f"{root!r}. Expected one of: Assets, Liabilities, Equity, Income, Expenses."
        )
    return meta


def _to_decimal_money(value: str) -> Decimal:
    """Parse an amount into a Decimal, keeping sign."""

    cleaned = parse_money(value)
    if cleaned == "":
        return Decimal("0")
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:  # pragma: no cover
        raise TrackDDataError(f"Invalid money amount: {value!r}") from exc


def _fmt_2dp(x: Decimal) -> str:
    """Format with 2 decimals, but use blank for zero.

    Track D templates typically leave the non-side empty (rather than "0.00").
    """

    q = x.quantize(Decimal("0.01"))
    if q == Decimal("0.00"):
        return ""
    return f"{q:.2f}"


class GnuCashGLAdapter:
    name = "gnucash_gl"

    def normalize(
        self,
        ctx: NormalizeContext,
    ) -> dict[str, Any]:
        """Normalize a GnuCash transactions export to the core_gl contract.

        Notes
        -----
        Users should export from:
          File -> Export -> Export Transactions to CSV
        with "Simple Layout" unchecked (complex/multi-line).
        """

        # This adapter currently targets the minimal core_gl contract.
        if ctx.profile != "core_gl":
            raise TrackDDataError(
                f"gnucash_gl adapter currently supports profile 'core_gl' only (got {ctx.profile!r})."
            )

        tables_dir = ctx.tables_dir
        normalized_dir = ctx.normalized_dir

        # We expect the GnuCash export to be placed at tables/gl_journal.csv.
        # (BYOD init creates both required files; users overwrite gl_journal.csv.)
        src_path = tables_dir / "gl_journal.csv"
        if not src_path.exists():
            raise TrackDDataError(
                "Missing tables/gl_journal.csv. Put the GnuCash export CSV here and re-run normalize."
            )

        with src_path.open("r", encoding="utf-8", newline="", errors="replace") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []

            norm_to_src: dict[str, str] = {normalize_col_name(h): h for h in fieldnames}

            def _col(*aliases: str) -> str | None:
                for a in aliases:
                    if a in norm_to_src:
                        return norm_to_src[a]
                return None

            col_date = _col("date")
            col_txn_id = _col("transaction_id")
            col_number = _col("number")
            col_desc = _col("description")
            col_full_acct = _col("full_account_name")
            col_acct = _col("account_name")
            col_amt = _col("amount_num")

            missing = [
                k
                for k, v in {
                    "Date": col_date,
                    "Transaction ID": col_txn_id,
                    "Number": col_number,
                    "Description": col_desc,
                    "Full Account Name": col_full_acct,
                    "Amount Num.": col_amt,
                }.items()
                if v is None
            ]
            if missing:
                raise TrackDDataError(
                    "GnuCash export is missing required columns: "
                    + ", ".join(missing)
                    + ". Make sure you exported 'Transactions to CSV' with Simple Layout unchecked."
                )

            normalized_dir.mkdir(parents=True, exist_ok=True)

            # Collect splits and a derived chart of accounts.
            splits: list[dict[str, str]] = []
            coa: dict[str, _AcctMeta] = {}

            for row in reader:
                date = clean_cell(row[col_date])
                txn_id = clean_cell(row[col_txn_id])
                doc_id = clean_cell(row[col_number])
                desc = clean_cell(row[col_desc])

                full_acct = clean_cell(row[col_full_acct])
                if not full_acct and col_acct:
                    full_acct = clean_cell(row[col_acct])
                if not full_acct:
                    # Skip empty rows.
                    continue

                meta = _acct_meta_from_full_name(full_acct)
                coa.setdefault(full_acct, meta)

                amt = _to_decimal_money(clean_cell(row[col_amt]))

                debit = Decimal("0")
                credit = Decimal("0")
                if meta.normal_side == "Debit":
                    if amt >= 0:
                        debit = amt
                    else:
                        credit = -amt
                else:  # Credit-normal
                    if amt >= 0:
                        credit = amt
                    else:
                        debit = -amt

                splits.append(
                    {
                        "txn_id": txn_id,
                        "date": date,
                        "doc_id": doc_id,
                        "description": desc,
                        "account_id": full_acct,
                        "debit": _fmt_2dp(debit) if debit != 0 else "",
                        "credit": _fmt_2dp(credit) if credit != 0 else "",
                    }
                )

        # Write normalized gl_journal.csv
        gl_path = normalized_dir / "gl_journal.csv"
        with gl_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "txn_id",
                    "date",
                    "doc_id",
                    "description",
                    "account_id",
                    "debit",
                    "credit",
                ],
            )
            writer.writeheader()
            for r in splits:
                writer.writerow(r)

        # Write normalized chart_of_accounts.csv
        coa_path = normalized_dir / "chart_of_accounts.csv"
        with coa_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "account_id",
                    "account_name",
                    "account_type",
                    "normal_side",
                ],
            )
            writer.writeheader()
            for account_id in sorted(coa.keys()):
                meta = coa[account_id]
                leaf = account_id.split(":")[-1].strip()
                writer.writerow(
                    {
                        "account_id": account_id,
                        "account_name": leaf,
                        "account_type": meta.account_type,
                        "normal_side": meta.normal_side,
                    }
                )

        return {
            "adapter": self.name,
            "profile": ctx.profile,
            "project": str(ctx.project_root),
            "tables_dir": str(ctx.tables_dir),
            "normalized_dir": str(ctx.normalized_dir),
            "files": [
                {"dst": str(coa_path), "rows": len(coa)},
                {"dst": str(gl_path), "rows": len(splits)},
            ],
        }
