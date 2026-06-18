"""Package-identity helpers for proof-first psychology workflows."""

from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError, distribution, version
from pathlib import Path
from typing import Any
import sys


def _safe_distribution_location(package_name: str) -> str | None:
    """Return the installed distribution location when metadata is available."""

    try:
        dist = distribution(package_name)
    except PackageNotFoundError:
        return None
    location = dist.locate_file("")
    return str(Path(location).resolve())


def _source_kind(module_file: str | None, distribution_location: str | None) -> str:
    """Classify a package source in a deliberately conservative way."""

    if not module_file:
        return "unknown"
    module_path = Path(module_file).resolve()
    text = str(module_path)
    if "site-packages" in text or "dist-packages" in text:
        # Editable installs may still point back into a source tree, so keep this
        # classification conservative and receipt-friendly rather than absolute.
        return "installed-package"
    if distribution_location and str(module_path).startswith(str(Path(distribution_location).resolve())):
        return "installed-distribution"
    return "local-source-or-editable"


def package_identity(package_name: str = "pystatsv1", module_name: str = "pystatsv1") -> dict[str, Any]:
    """Return a JSON-serializable identity receipt for a Python package.

    The receipt is designed for companion labs that need to prove exactly which
    public package was imported. It records version, import path, module file,
    distribution location, and a conservative source-kind label.
    """

    module = import_module(module_name)
    module_file = getattr(module, "__file__", None)
    try:
        package_version = version(package_name)
        status = "available"
    except PackageNotFoundError:
        package_version = getattr(module, "__version__", None)
        status = "importable-without-distribution-metadata"

    distribution_location = _safe_distribution_location(package_name)
    exports = sorted(name for name in dir(module) if not name.startswith("_"))
    return {
        "package_name": package_name,
        "module_name": module_name,
        "status": status,
        "version": package_version,
        "module_file": str(Path(module_file).resolve()) if module_file else None,
        "module_dir": str(Path(module_file).resolve().parent) if module_file else None,
        "distribution_location": distribution_location,
        "source_kind": _source_kind(module_file, distribution_location),
        "python_executable": sys.executable,
        "top_level_exports": exports,
    }
