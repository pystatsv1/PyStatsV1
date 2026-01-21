"""Console helpers.

PyStatsV1 aims to be beginner-friendly across Windows/macOS/Linux.
Some Windows terminals still default to non-UTF-8 encodings (e.g., cp1252),
so **runtime console output should stay ASCII-only by default**.

These helpers provide consistent, ASCII-safe status prefixes for scripts.
"""

from __future__ import annotations

from typing import Final

OK_TAG: Final[str] = "[OK]"
WARN_TAG: Final[str] = "[WARN]"
FAIL_TAG: Final[str] = "NOT OK"


def status_ok(message: str = "") -> str:
    """Return an ASCII-safe OK status line.

    Prefer using this in scripts instead of emoji markers, e.g.:

        print(status_ok("Wrote outputs/..."))
    """

    if not message:
        return OK_TAG
    return f"{OK_TAG} {message}"


def status_warn(message: str = "") -> str:
    """Return an ASCII-safe WARN status line."""

    if not message:
        return WARN_TAG
    return f"{WARN_TAG} {message}"


def status_fail(message: str = "") -> str:
    """Return an ASCII-safe FAIL status line."""

    if not message:
        return FAIL_TAG
    return f"{FAIL_TAG} {message}"
