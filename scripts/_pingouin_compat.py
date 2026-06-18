"""Compatibility helpers for Pingouin result-table column names.

Pingouin has used both hyphenated and underscore-style column names across
versions.  The teaching scripts in PyStatsV1 historically used the hyphenated
names shown in older Pingouin tables, such as ``p-val`` and ``p-unc``.  Newer
Pingouin releases may instead return names such as ``p_val`` and ``p_unc``.

The helpers here add missing legacy aliases without removing the newer columns.
That keeps existing lessons, tests, and workbook templates stable while still
letting readers inspect the native Pingouin output style for their installed
version.
"""

from __future__ import annotations

import pandas as pd


_PINGOUIN_LEGACY_ALIASES: dict[str, str] = {
    "p_val": "p-val",
    "p_unc": "p-unc",
    "p_corr": "p-corr",
    "p_GG_corr": "p-GG-corr",
    "p_spher": "p-spher",
    "U_val": "U-val",
    "W_val": "W-val",
    "cohen_d": "cohen-d",
}


def add_pingouin_legacy_aliases(table: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of a Pingouin table with legacy hyphen aliases.

    The function is intentionally conservative: it only adds an alias when the
    underscore-style source column exists and the corresponding hyphenated
    legacy column is absent. Existing columns are never overwritten or removed.
    """
    result = table.copy()
    for source, alias in _PINGOUIN_LEGACY_ALIASES.items():
        if source in result.columns and alias not in result.columns:
            result[alias] = result[source]
    return result
