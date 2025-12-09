"""
Top-level package for the PyStatsV1 project.

Convenience re-exports:

- DATA_DIR, SYNTHETIC_DATA_DIR
- OUTPUTS_DIR, TRACK_C_OUTPUT_DIR
- PROJECT_ROOT
"""

from importlib.metadata import PackageNotFoundError, version

from .paths import (  # noqa: F401
    DATA_DIR,
    SYNTHETIC_DATA_DIR,
    OUTPUTS_DIR,
    TRACK_C_OUTPUT_DIR,
    PROJECT_ROOT,
)

__all__ = [
    "DATA_DIR",
    "SYNTHETIC_DATA_DIR",
    "OUTPUTS_DIR",
    "TRACK_C_OUTPUT_DIR",
    "PROJECT_ROOT",
    "__version__",
]

try:
    __version__ = version("pystatsv1")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
