"""
Centralized filesystem paths for the PyStatsV1 project.

Repo layout:

    PyStatsV1/
      data/
        synthetic/
      outputs/
        track_c/
      docs/
      scripts/
      src/pystatsv1/...

This module exposes a small set of reusable Path objects so scripts and
tests don't have to duplicate logic for finding the project root.
"""

from __future__ import annotations

from pathlib import Path

# src/pystatsv1/paths.py -> .../src/pystatsv1 -> .../src -> .../PyStatsV1
PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parents[1]

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"

# Outputs (top-level and Track C specific)
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
TRACK_C_OUTPUT_DIR = OUTPUTS_DIR / "track_c"


def ensure_dir(path: Path) -> Path:
    """Ensure that ``path`` exists (mkdir -p) and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_output_subdir(name: str) -> Path:
    """Ensure that a subdirectory of OUTPUTS_DIR exists and return it."""
    return ensure_dir(OUTPUTS_DIR / name)
