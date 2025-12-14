from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path


def get_local_docs_path() -> Path:
    """Return the path to the bundled PDF documentation.

    Raises FileNotFoundError if the PDF is missing.
    """
    # Most robust for wheels: resources are installed on disk under the package directory.
    pkg_dir = Path(__file__).resolve().parent
    pdf_path = pkg_dir / "docs" / "pystatsv1.pdf"

    if not pdf_path.exists():
        raise FileNotFoundError(f"Documentation PDF not found: {pdf_path}")

    return pdf_path


def _open_file_native(path: Path) -> bool:
    """Try to open a local file in the default viewer. Returns True if attempted."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
            return True
        if sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
            return True
        # Linux + other Unix
        subprocess.run(["xdg-open", str(path)], check=False)
        return True
    except Exception:
        return False


def open_local_docs() -> None:
    """Open the bundled PDF documentation in the default PDF viewer."""
    pdf_path = get_local_docs_path()

    # Prefer native open (best chance of launching the user's PDF viewer).
    if _open_file_native(pdf_path):
        return

    # Fallback: open as file URL (may open in browser).
    webbrowser.open_new(pdf_path.as_uri())
