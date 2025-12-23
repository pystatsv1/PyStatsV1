# SPDX-License-Identifier: MIT
# business_ch07_preparing_accounting_data_for_analysis.py
"""Track D Chapter 7: Preparing accounting data for analysis.

This chapter turns the *raw* general ledger (GL) export into two analysis-ready
datasets:

1) ``gl_tidy.csv``
   One row per GL line with COA labels and a single signed amount column.

2) ``gl_monthly_summary.csv``
   A monthly rollup per account with debit/credit totals and a signed net change.

Inputs (from the dataset folder, e.g., ``data/synthetic/nso_v1``):
- ``gl_journal.csv``
- ``chart_of_accounts.csv``

Outputs (in ``--outdir``):
- ``gl_tidy.csv``
- ``gl_monthly_summary.csv``
- ``ch07_summary.json``
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from scripts._business_etl import GLPrepOutputs, analyze_gl_preparation
from scripts._cli import base_parser
from scripts._business_recon import write_json


@dataclass(frozen=True)
class Ch07Outputs:
    gl_tidy: pd.DataFrame
    gl_monthly_summary: pd.DataFrame
    summary: dict[str, Any]


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def analyze_ch07(datadir: Path) -> Ch07Outputs:
    gl = _read_csv(datadir / "gl_journal.csv")
    coa = _read_csv(datadir / "chart_of_accounts.csv")

    out: GLPrepOutputs = analyze_gl_preparation(gl, coa)
    return Ch07Outputs(gl_tidy=out.gl_tidy, gl_monthly_summary=out.gl_monthly_summary, summary=out.summary)


def write_ch07_outputs(result: Ch07Outputs, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    result.gl_tidy.to_csv(outdir / "gl_tidy.csv", index=False)
    result.gl_monthly_summary.to_csv(outdir / "gl_monthly_summary.csv", index=False)
    write_json(result.summary, outdir / "ch07_summary.json")


def main() -> None:
    p = base_parser("Track D Chapter 7: Preparing accounting data for analysis")
    p.add_argument("--datadir", type=Path, default=Path("data/synthetic/nso_v1"))
    args = p.parse_args()

    result = analyze_ch07(args.datadir)
    write_ch07_outputs(result, args.outdir)
    print(f"Wrote Chapter 7 artifacts -> {args.outdir}")


if __name__ == "__main__":
    main()
