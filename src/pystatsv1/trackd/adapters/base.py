# SPDX-License-Identifier: MIT
"""Adapter interface for Track D BYOD normalization.

The long-term goal is to support multiple data sources (Sheets-first, then
system exports like QuickBooks) without changing the downstream pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class NormalizeContext:
    """Context passed to a BYOD adapter during normalization."""

    project_root: Path
    profile: str
    tables_dir: Path
    raw_dir: Path
    normalized_dir: Path


class TrackDAdapter(Protocol):
    """Protocol for BYOD adapters."""

    name: str

    def normalize(self, ctx: NormalizeContext) -> dict[str, Any]:
        """Normalize project inputs into canonical ``normalized/`` outputs."""

        ...
