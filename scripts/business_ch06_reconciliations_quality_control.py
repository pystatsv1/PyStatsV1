# SPDX-License-Identifier: MIT
# business_ch06_reconciliations_quality_control.py
"""Chapter 6 (Track D): Reconciliations as quality control.

Inputs (dataset folder):
- gl_journal.csv
- trial_balance_monthly.csv
- ar_events.csv
- bank_statement.csv

Outputs (outdir):
- ar_rollforward.csv
- bank_recon_matches.csv
- bank_recon_exceptions.csv
- ch06_summary.json
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from scripts._cli import base_parser
from scripts._business_recon import (
    build_ar_rollforward,
    reconcile_bank_statement,
    write_json,
)

@dataclass(frozen=True)
class Ch06Outputs:
    ar_rollforward: pd.DataFrame
    bank_matches: pd.DataFrame
    bank_exceptions: pd.DataFrame
    summary: dict[str, Any]

def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path}")
    return pd.read_csv(path)

def analyze_ch06(datadir: Path) -> Ch06Outputs:
    gl = _read_csv(datadir / "gl_journal.csv")
    tb = _read_csv(datadir / "trial_balance_monthly.csv")
    ar_events = _read_csv(datadir / "ar_events.csv")
    bank = _read_csv(datadir / "bank_statement.csv")

    # AR rollforward tie-out

    ar_roll = build_ar_rollforward(tb, ar_events)
    ar_ok = bool(ar_roll["diff"].abs().max() < 1e-6)

    # Bank reconciliation + exception report
    bank_out = reconcile_bank_statement(bank, gl)
    bank_matches = bank_out.matches
    bank_ex = bank_out.exceptions

    exc_counts = {}
    if not bank_ex.empty:
        exc_counts = bank_ex["exception_type"].astype(str).value_counts().to_dict()

    summary = {
        "checks": {
            "ar_rollforward_ties_to_tb": ar_ok,
        },
        "metrics": {
            "n_bank_lines": int(len(bank)),
            "n_cash_txns_in_gl": int(len(bank_out.cash_txns)),
            "n_bank_matches": int(bank_matches.get("is_matched", pd.Series(dtype=bool)).fillna(False).sum()),
            "n_bank_exceptions": int(len(bank_ex)),
        },
        "exception_counts": exc_counts,
    }

    return Ch06Outputs(
        ar_rollforward=ar_roll,
        bank_matches=bank_matches,
        bank_exceptions=bank_ex,
        summary=summary,
    )


def write_ch06_outputs(result: Ch06Outputs, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    result.ar_rollforward.to_csv(outdir / "ar_rollforward.csv", index=False)
    result.bank_matches.to_csv(outdir / "bank_recon_matches.csv", index=False)
    result.bank_exceptions.to_csv(outdir / "bank_recon_exceptions.csv", index=False)

    write_json(result.summary, outdir / "ch06_summary.json")


def main() -> None:
    p = base_parser("Track D Chapter 6: Reconciliations as quality control")
    p.add_argument("--datadir", type=Path, default=Path("data/synthetic/nso_v1"))
    args = p.parse_args()

    result = analyze_ch06(args.datadir)
    write_ch06_outputs(result, args.outdir)
    print(f"Wrote Chapter 6 artifacts -> {args.outdir}")


if __name__ == "__main__":
    main()
