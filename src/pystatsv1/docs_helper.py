from __future__ import annotations

import os
import sys
from pathlib import Path


def get_local_docs_path() -> Path:
    """Return the absolute path to the packaged PDF (pystatsv1/docs/pystatsv1.pdf)."""
    # Resolve relative to this module, which is stable in editable installs and wheels.
    pkg_dir = Path(__file__).resolve().parent
    pdf = pkg_dir / "docs" / "pystatsv1.pdf"
    return pdf


def open_local_docs() -> Path:
    """Open the packaged PDF in the system default viewer and return the path."""
    pdf = get_local_docs_path()
    if not pdf.exists():
        raise FileNotFoundError(f"Local docs PDF not found: {pdf}")

    if sys.platform.startswith("win"):
        os.startfile(str(pdf))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        os.system(f'open "{pdf}"')
    else:
        os.system(f'xdg-open "{pdf}"')

    return pdf
