from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_my_data_scaffold_script_runs_and_writes_outputs(tmp_path):
    """Smoke test for the beginner template + scaffold script.

    This is intentionally lightweight:
      - proves the template CSV can be read
      - proves the scaffold script runs without errors
      - proves it writes a couple of expected artifacts
    """

    repo_root = Path(__file__).resolve().parents[1]
    csv_path = repo_root / "data" / "my_data.csv"
    script_path = repo_root / "scripts" / "my_data_01_explore.py"

    assert csv_path.exists()
    assert script_path.exists()

    outdir = tmp_path / "out"

    cmd = [
        sys.executable,
        str(script_path),
        "--csv",
        str(csv_path),
        "--outdir",
        str(outdir),
    ]
    subprocess.run(cmd, check=True)

    assert (outdir / "tables" / "missingness.csv").exists()
    assert (outdir / "tables" / "numeric_summary.csv").exists()
