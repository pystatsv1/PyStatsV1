# SPDX-License-Identifier: MIT
"""Small mapping/cleaning utilities for Track D BYOD adapters.

Design goals (Phase 3.1):
- Keep utilities tiny and dependency-light (csv-first).
- Support *boring* transformations that come up in Sheets/Excel exports:
  - column-name normalization / rename matching
  - whitespace trimming
  - simple money parsing (commas, $, parentheses-as-negative)

These helpers are intentionally not a full ETL framework. They exist to keep
individual adapters readable and consistent.
"""

from __future__ import annotations

import re
from typing import Iterable


_RE_NON_ALNUM = re.compile(r"[^a-z0-9_]+")
_RE_UNDERSCORES = re.compile(r"_+")
_RE_MONEY = re.compile(r"^\(?\s*(?P<body>.*)\s*\)?$")


def normalize_col_name(name: str) -> str:
    """Normalize a column header for matching purposes.

    Examples
    --------
    "Account ID" -> "account_id"
    " normal-side " -> "normal_side"
    "DOC-ID" -> "doc_id"
    """

    s = (name or "").strip().lower()
    s = s.replace("-", "_").replace(" ", "_")
    s = _RE_NON_ALNUM.sub("_", s)
    s = _RE_UNDERSCORES.sub("_", s).strip("_")
    return s


def build_rename_map(
    fieldnames: Iterable[str],
    *,
    required_columns: tuple[str, ...],
    aliases: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, str]:
    """Build a mapping from source fieldnames to required/normalized names.

    Strategy:
    1) direct normalized match (case/spacing/punct insensitivity)
    2) optional aliases (also normalized), used only as a *fallback*

    Why fallback-only?
    - Many exports include both a canonical column (e.g., "Description") and a
      near-synonym (e.g., "Memo"). We don't want aliases to create ambiguous
      mappings when a direct match already exists.

    Returns a dict that maps *source column name* -> *destination column name*.
    """

    src = list(fieldnames)
    required_norm = {normalize_col_name(c): c for c in required_columns}

    alias_norm: dict[str, str] = {}
    if aliases:
        for dest, alts in aliases.items():
            for a in alts:
                alias_norm[normalize_col_name(a)] = dest

    out: dict[str, str] = {}
    claimed: set[str] = set()

    # Pass 1: exact required matches
    for col in src:
        n = normalize_col_name(col)
        if n in required_norm:
            dest = required_norm[n]
            out[col] = dest
            claimed.add(dest)

    # Pass 2: alias fallback (only if dest not already claimed)
    for col in src:
        if col in out:
            continue
        n = normalize_col_name(col)
        dest = alias_norm.get(n)
        if dest and dest not in claimed:
            out[col] = dest
            claimed.add(dest)

    return out


def detect_duplicate_destinations(rename_map: dict[str, str]) -> dict[str, list[str]]:
    """Return destinations that are mapped from multiple sources."""

    rev: dict[str, list[str]] = {}
    for src, dst in rename_map.items():
        rev.setdefault(dst, []).append(src)
    return {dst: srcs for dst, srcs in rev.items() if len(srcs) > 1}


def clean_cell(value: object) -> str:
    """Trim whitespace and coerce missing values to empty string."""
    if value is None:
        return ""
    s = str(value)
    return s.strip()


def parse_money(value: str) -> str:
    """Parse common spreadsheet money formats into a simple numeric string.

    Supported patterns:
    - "$1,234.00" -> "1234.00"
    - "(1,234.00)" or "($1,234.00)" -> "-1234.00"
    - "-1,234" -> "-1234"

    If the string is blank, returns blank.
    """

    s = (value or "").strip()
    if not s:
        return ""

    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1].strip()

    # Strip currency and grouping separators.
    s = s.replace("$", "").replace(",", "").strip()
    if not s:
        return ""

    # If it already has a leading minus, keep it.
    if s.startswith("-"):
        return s

    return f"-{s}" if neg else s
