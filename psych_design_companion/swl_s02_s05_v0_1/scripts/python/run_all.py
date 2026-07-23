#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from studies import write_runtime_python_results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output_root = (
        args.output_root.resolve()
        if args.output_root
        else root / "outputs" / "python"
    )
    paths = write_runtime_python_results(root, output_root)
    for path in paths:
        print(f"wrote {path}")
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S02_S05_PYTHON_OK")


if __name__ == "__main__":
    main()
