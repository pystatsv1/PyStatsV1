from __future__ import annotations

import hashlib
import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"
SCHEMA_VERSION = "book1-companion-results-v0.1"


def rounded(value: float, digits: int = 10) -> float:
    """Keep reportable values stable without rounding tiny p-values to zero."""
    return float(f"{float(value):.{digits}g}")


def bridge_metadata() -> dict[str, str]:
    """Record the PyStatsV1 environment bridge without hiding the analysis engine."""
    try:
        pystatsv1_version = version("pystatsv1")
    except PackageNotFoundError:
        pystatsv1_version = "not-installed"
    return {
        "workflow": "Python-first, R-verified",
        "pystatsv1_version": pystatsv1_version,
        "analysis_engine": "numpy/scipy/statsmodels",
    }


def write_result(chapter: str, analysis_name: str, data_file: str, fields: dict[str, Any]) -> Path:
    out = OUTPUTS / chapter / "py_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "chapter": chapter,
        "analysis_name": analysis_name,
        "engine": bridge_metadata(),
        "data_file": data_file,
        "synthetic_data_only": True,
        "reported_fields": fields,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def format_p(value: float) -> str:
    return "p < .001" if value < 0.001 else f"p = {value:.3f}".replace("0.", ".")
