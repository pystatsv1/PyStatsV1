"""Track D workbook helper: peek at the (canonical) datasets.

This script is meant to be run inside a Track D workbook folder created by:

  pystatsv1 workbook init --track d

It looks for the two Track D synthetic datasets under:

  data/synthetic/ledgerlab_ch01/
  data/synthetic/nso_v1/

For the Track D student experience, these datasets are intended to be stable and
repeatable (seed=123).

What it does:
- lists the available CSV tables
- prints shapes + column names
- prints a small preview of each table
- writes a summary report under outputs/track_d/
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _preview_csv(path: Path, n: int = 5) -> str:
    df = pd.read_csv(path)
    head = df.head(n)
    return (
        f"{path.name}: rows={len(df)} cols={len(df.columns)}\n"
        f"columns: {', '.join(map(str, df.columns))}\n"
        f"preview:\n{head.to_string(index=False)}\n"
    )


def _peek_dataset(name: str, folder: Path, preview_rows: int) -> tuple[str, list[str]]:
    if not folder.exists():
        msg = (
            f"⚠️  Missing dataset folder: {folder}\n"
            "If you just created this workbook, you may be on an older PyStatsV1 version.\n"
            "Update, then re-run workbook init:\n\n"
            "  python -m pip install -U pystatsv1\n"
            "  pystatsv1 workbook init --track d --dest pystatsv1_track_d --force\n"
        )
        return msg, [msg]

    csvs = sorted(folder.glob("*.csv"))
    if not csvs:
        msg = (
            f"⚠️  No CSV files found in: {folder}\n"
            "This workbook expects canonical datasets to exist under data/synthetic/.\n"
        )
        return msg, [msg]

    lines: list[str] = []
    print(f"\n== {name} ==")
    lines.append(f"## {name}\n")
    lines.append(f"Folder: {folder}\n")

    for csv in csvs:
        block = _preview_csv(csv, n=preview_rows)
        print(block)
        lines.append(f"### {csv.name}\n")
        lines.append("```\n")
        lines.append(block.rstrip())
        lines.append("\n```\n")

    return "OK", lines


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Peek at Track D datasets (seed=123).")
    p.add_argument(
        "--root",
        default="data/synthetic",
        help="Dataset root (default: data/synthetic).",
    )
    p.add_argument(
        "--outdir",
        default="outputs/track_d",
        help="Where to write the summary report (default: outputs/track_d).",
    )
    p.add_argument(
        "--preview-rows",
        type=int,
        default=5,
        help="Number of rows to preview per table (default: 5).",
    )

    args = p.parse_args(argv)

    root = Path(args.root)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    sections: list[str] = []
    sections.append("# Track D dataset peek (seed=123)\n")

    _status, lines = _peek_dataset(
        "LedgerLab (Ch01)", root / "ledgerlab_ch01", preview_rows=args.preview_rows
    )
    sections.extend(lines)

    _status, lines = _peek_dataset(
        "NSO v1 running case", root / "nso_v1", preview_rows=args.preview_rows
    )
    sections.extend(lines)

    report = outdir / "d00_peek_data_summary.md"
    report.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")

    print(f"\n✅ Wrote summary: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
