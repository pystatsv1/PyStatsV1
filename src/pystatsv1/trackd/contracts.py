# SPDX-License-Identifier: MIT
"""Dataset profile contracts for Track D.

Phase 2 (BYOD foundations) introduces *profiles* that let users validate smaller
subsets of the full Track D dataset contract.

Profiles are defined as ordered subsets of the existing Track D contract tables
in :mod:`pystatsv1.trackd.schema`.
"""

from __future__ import annotations

from typing import Final

from .schema import CONTRACT_TABLES, NSO_V1_TABLE_ORDER, TableSchema


# Ordered subsets of the existing Track D contract.
#
# - core_gl: the smallest General Ledger "starter" export (Chart of Accounts + GL)
# - ar: adds accounts receivable events
# - full: all Track D tables in canonical workbook order
PROFILE_TABLE_KEYS: Final[dict[str, tuple[str, ...]]] = {
    "core_gl": (
        "chart_of_accounts",
        "gl_journal",
    ),
    "ar": (
        "chart_of_accounts",
        "gl_journal",
        "ar_events",
    ),
    "full": NSO_V1_TABLE_ORDER,
}


ALLOWED_PROFILES: Final[tuple[str, ...]] = tuple(PROFILE_TABLE_KEYS.keys())


def schemas_for_profile(profile: str) -> tuple[TableSchema, ...]:
    """Return the ordered :class:`~pystatsv1.trackd.schema.TableSchema` tuple for a profile."""

    p = (profile or "").strip().lower()
    keys = PROFILE_TABLE_KEYS.get(p)
    if keys is None:
        raise ValueError(f"Unknown profile: {profile}. Use one of: {', '.join(ALLOWED_PROFILES)}")

    # Defensive: ensure profile only references known contract tables.
    missing = [k for k in keys if k not in CONTRACT_TABLES]
    if missing:
        raise ValueError(f"Profile '{p}' references unknown contract tables: {', '.join(missing)}")

    return tuple(CONTRACT_TABLES[k] for k in keys)
