"""Shared types for Track D helpers.

These are intentionally lightweight. Track D functions should accept common "path
like" inputs and return pandas DataFrames.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypeAlias

import pandas as pd

PathLike: TypeAlias = str | Path
DataFrame: TypeAlias = pd.DataFrame
DataFrames: TypeAlias = dict[str, pd.DataFrame]
