"""Matplotlib compatibility helpers for workbook scripts.

Matplotlib 3.9 renamed the Axes.boxplot keyword argument "labels" to
"tick_labels". The old name is deprecated and scheduled for removal.

These helpers keep our educational scripts working on Matplotlib 3.8+
while avoiding deprecation warnings on newer versions.
"""

from __future__ import annotations

from typing import Any, Sequence


def ax_boxplot(
    ax: Any,
    *args: Any,
    tick_labels: Sequence[str] | None = None,
    **kwargs: Any,
):
    """Call ``ax.boxplot`` with a 3.8/3.9+ compatible keyword.

    Prefer ``tick_labels`` (Matplotlib >= 3.9). If that keyword is not
    supported (Matplotlib <= 3.8), fall back to the legacy ``labels``.
    """

    if tick_labels is None:
        return ax.boxplot(*args, **kwargs)

    try:
        return ax.boxplot(*args, tick_labels=tick_labels, **kwargs)
    except TypeError:
        # Older Matplotlib: the new keyword doesn't exist.
        return ax.boxplot(*args, labels=tick_labels, **kwargs)
