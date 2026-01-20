# SPDX-License-Identifier: MIT
"""Bring-your-own-data (BYOD) helpers for Track D.

Phase 2 foundation:
- create a local BYOD project folder
- generate header-only CSV templates from the canonical Track D contracts

Design: avoid shipping a second "header pack" contract.
We generate templates directly from :mod:`pystatsv1.trackd.schema` so the
single source of truth stays in one place.
"""

from __future__ import annotations

import csv
import textwrap
from pathlib import Path

from ._errors import TrackDDataError
from ._types import PathLike
from .contracts import ALLOWED_PROFILES, schemas_for_profile


def init_byod_project(dest: PathLike, *, profile: str = "core_gl", force: bool = False) -> Path:
    """Create a Track D BYOD project folder.

    The project layout is intentionally simple:

    - tables/      student-edited CSVs (header templates created here)
    - raw/         optional dumps from source systems
    - normalized/  adapter outputs (generated)
    - notes/       assumptions, mapping notes, and QA

    Parameters
    ----------
    dest:
        Destination folder to create.
    profile:
        One of: core_gl, ar, full.
    force:
        Allow writing into an existing non-empty directory.

    Returns
    -------
    Path
        The created project root.

    Raises
    ------
    TrackDDataError
        If *dest* is non-empty and *force* is False, or if *profile* is invalid.
    """

    root = Path(dest).expanduser().resolve()

    if root.exists() and any(root.iterdir()) and not force:
        raise TrackDDataError(
            f"Refusing to write into non-empty directory: {root}\n"
            "Use --force to overwrite into an existing directory."
        )

    p = (profile or "").strip().lower()
    try:
        schemas = schemas_for_profile(p)
    except ValueError as e:
        raise TrackDDataError(
            f"Unknown profile: {profile}.\n" f"Use one of: {', '.join(ALLOWED_PROFILES)}"
        ) from e

    # Create core folders
    root.mkdir(parents=True, exist_ok=True)
    (root / "tables").mkdir(parents=True, exist_ok=True)
    (root / "raw").mkdir(parents=True, exist_ok=True)
    (root / "normalized").mkdir(parents=True, exist_ok=True)
    (root / "notes").mkdir(parents=True, exist_ok=True)

    # Write header-only CSV templates into tables/
    for schema in schemas:
        out = root / "tables" / schema.name
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(list(schema.required_columns))

    # Tiny config (write-only for now)
    config = textwrap.dedent(
        f"""\
        # Track D BYOD project config
        [trackd]
        profile = "{p}"
        tables_dir = "tables"
        """
    ).lstrip()
    (root / "config.toml").write_text(config, encoding="utf-8")

    readme = textwrap.dedent(
        f"""\
        # Track D — Bring Your Own Data (BYOD)

        This folder is a starter project for using your own accounting data with Track D.

        ## What to edit

        - `tables/` contains **student-edited** CSVs.
          Header-only templates are generated from the Track D contract.

        ## What not to edit

        - `normalized/` is for **generated** outputs from future adapters.

        ## Quickstart

        1) Fill in the required CSVs under `tables/`.
        2) Validate your dataset:

           ```bash
           pystatsv1 trackd validate --datadir tables --profile {p}
           ```

        If validation fails, fix the missing files/columns and re-run.
        """
    ).lstrip()

    (root / "README.md").write_text(readme, encoding="utf-8")
    return root
