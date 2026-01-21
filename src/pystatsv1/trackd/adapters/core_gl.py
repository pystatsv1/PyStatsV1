# SPDX-License-Identifier: MIT
"""Generic 'core_gl' adapter for Track D BYOD normalization.

This adapter is the bridge from "perfect" template exports (already matching the
contract) to "slightly messy" Sheets/Excel exports.

Features (v1):
- Header matching that tolerates case/spacing/punctuation (e.g., "Account ID")
- Whitespace trimming across all cells
- Money cleanup for debit/credit (commas, $, parentheses-as-negative)
- Canonical output column order (required first, then passthrough extras)

Inputs
------
Reads contract-named files from ``tables/``:
- chart_of_accounts.csv
- gl_journal.csv

Outputs
-------
Writes contract-named files to ``normalized/`` with contract column names.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .._errors import TrackDDataError, TrackDSchemaError
from ..contracts import schemas_for_profile
from .base import NormalizeContext
from .mapping import (
    build_rename_map,
    clean_cell,
    detect_duplicate_destinations,
    parse_money,
)


_COA_ALIASES: dict[str, tuple[str, ...]] = {
    "account_id": ("acct_id", "acct", "account", "account number", "account_no"),
    "account_name": ("acct_name", "name"),
    "account_type": ("type",),
    "normal_side": ("normal", "side"),
}

_GL_ALIASES: dict[str, tuple[str, ...]] = {
    "txn_id": ("txnid", "transaction_id", "transaction id", "id"),
    "doc_id": ("doc", "document", "document_id", "document id"),
    "description": ("desc", "memo", "narrative"),
    "account_id": ("acct_id", "acct", "account", "account number", "account_no"),
    "debit": ("dr", "debits"),
    "credit": ("cr", "credits"),
}


def _write_normalized_csv(
    src: Path,
    dst: Path,
    *,
    required_columns: tuple[str, ...],
    aliases: dict[str, tuple[str, ...]] | None = None,
    money_columns: tuple[str, ...] = (),
) -> dict[str, Any]:
    with src.open("r", newline="", encoding="utf-8-sig") as f_in:
        reader = csv.DictReader(f_in)
        if not reader.fieldnames:
            raise TrackDDataError(f"CSV appears to have no header row: {src.name}")

        fieldnames = [str(c) for c in reader.fieldnames if c is not None]
        rename_map = build_rename_map(fieldnames, required_columns=required_columns, aliases=aliases)

        dups = detect_duplicate_destinations(rename_map)
        if dups:
            pieces = [f"{dst}: {', '.join(srcs)}" for dst, srcs in sorted(dups.items())]
            raise TrackDSchemaError(
                "Ambiguous column mapping (multiple source columns map to the same required column).\n"
                + "\n".join(pieces)
            )

        # Determine output fields: required columns first, then passthrough extras.
        required_set = set(required_columns)
        extras: list[str] = []
        for c in fieldnames:
            dest = rename_map.get(c, c)
            if dest in required_set:
                continue
            # Preserve original extra column names (trimmed).
            extras.append(c.strip())

        out_fields = list(required_columns) + extras

        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=out_fields)
            writer.writeheader()
            n_rows = 0
            for row in reader:
                out_row: dict[str, str] = {k: "" for k in out_fields}

                # Map + clean required columns
                for src_col in fieldnames:
                    raw_val = row.get(src_col)
                    val = clean_cell(raw_val)
                    dest = rename_map.get(src_col, src_col).strip()

                    # Extra columns: keep under original header (trimmed).
                    if dest not in required_set:
                        dest = src_col.strip()

                    if dest not in out_row:
                        # If an extra column name collides with required, prefer required slot.
                        continue

                    if dest in money_columns:
                        val = parse_money(val)

                    out_row[dest] = val

                writer.writerow(out_row)
                n_rows += 1

    return {
        "src": str(src),
        "dst": str(dst),
        "written_rows": n_rows,
        "written_columns": out_fields,
    }


class CoreGLAdapter:
    name = "core_gl"

    def normalize(self, ctx: NormalizeContext) -> dict[str, Any]:
        schemas = schemas_for_profile(ctx.profile)

        ctx.normalized_dir.mkdir(parents=True, exist_ok=True)

        files: list[dict[str, Any]] = []
        for schema in schemas:
            src = ctx.tables_dir / schema.name
            dst = ctx.normalized_dir / schema.name
            if not src.exists():
                raise TrackDDataError(f"Missing required input file for adapter '{self.name}': {src}")

            if schema.name == "chart_of_accounts.csv":
                aliases = _COA_ALIASES
                money_cols: tuple[str, ...] = ()
            elif schema.name == "gl_journal.csv":
                aliases = _GL_ALIASES
                money_cols = ("debit", "credit")
            else:
                aliases = None
                money_cols = ()

            files.append(
                _write_normalized_csv(
                    src,
                    dst,
                    required_columns=schema.required_columns,
                    aliases=aliases,
                    money_columns=money_cols,
                )
            )

        return {
            "ok": True,
            "adapter": self.name,
            "profile": ctx.profile,
            "project": str(ctx.project_root),
            "tables_dir": str(ctx.tables_dir),
            "normalized_dir": str(ctx.normalized_dir),
            "files": files,
        }
