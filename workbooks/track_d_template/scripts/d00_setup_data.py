# SPDX-License-Identifier: MIT
"""Track D workbook helper: (re)generate the synthetic datasets.

Artifacts written to ``--outdir``:

* data/synthetic/ledgerlab_ch01/  (LedgerLab seed=123 tables)
* data/synthetic/nso_v1/          (NSO v1 seed=123 tables)
* outputs/track_d/d00_setup_data_validate/  (optional validation artifacts)

Normally you do **not** need this because Track D canonical datasets (seed=123)
are shipped and extracted during:

  pystatsv1 workbook init --track d

Use this script if you deleted/modified files under data/synthetic and want to
reset them, or if you want to confirm determinism."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def _rm_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def _run(script_path: Path, args: list[str]) -> None:
    subprocess.run([sys.executable, str(script_path), *args], check=True)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="(Re)generate Track D datasets (deterministic).")
    p.add_argument(
        "--seed",
        type=int,
        default=123,
        help="Random seed (default: 123). Keep 123 to match the canonical datasets.",
    )
    p.add_argument(
        "--root",
        default="data/synthetic",
        help="Dataset root folder (default: data/synthetic).",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Delete existing dataset folders before regenerating.",
    )
    p.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip the NSO dataset validation step.",
    )

    args = p.parse_args(argv)

    root = Path(args.root)
    ledger_dir = root / "ledgerlab_ch01"
    nso_dir = root / "nso_v1"

    if args.force:
        _rm_tree(ledger_dir)
        _rm_tree(nso_dir)

    ledger_dir.mkdir(parents=True, exist_ok=True)
    nso_dir.mkdir(parents=True, exist_ok=True)

    scripts_dir = Path(__file__).resolve().parent
    _run(
        scripts_dir / "sim_business_ledgerlab.py",
        ["--outdir", str(ledger_dir), "--seed", str(args.seed)],
    )
    _run(
        scripts_dir / "sim_business_nso_v1.py",
        ["--outdir", str(nso_dir), "--seed", str(args.seed)],
    )

    if not args.no_validate:
        outdir = Path("outputs/track_d") / "d00_setup_data_validate"
        outdir.mkdir(parents=True, exist_ok=True)
        _run(
            scripts_dir / "business_validate_dataset.py",
            [
                "--datadir",
                str(nso_dir),
                "--outdir",
                str(outdir),
                "--dataset",
                "nso_v1",
                "--seed",
                str(args.seed),
            ],
        )

    # ASCII-only status marker for Windows consoles that default to cp1252.
    print("\n[OK] Datasets ready under:", root)
    print("   -", ledger_dir)
    print("   -", nso_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
