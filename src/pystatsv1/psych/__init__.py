"""Psychology-study support helpers for PyStatsV1.

These helpers provide a small, stable bridge layer for proof-first
psychology examples. They intentionally do not replace SciPy, statsmodels,
or R for inferential procedures. Instead, they help projects record package
identity, produce simple descriptive summaries, and write auditable receipts.
"""

from .identity import package_identity
from .receipts import compare_numeric_results, write_json_receipt
from .summaries import describe_by_group

__all__ = [
    "compare_numeric_results",
    "describe_by_group",
    "package_identity",
    "write_json_receipt",
]
