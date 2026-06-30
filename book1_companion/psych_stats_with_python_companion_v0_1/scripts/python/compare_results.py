#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

from common import OUTPUTS

CHAPTERS = ["ch05", "ch06", "ch07", "ch08", "ch09", "ch10", "ch11", "ch12"]
TOLERANCE = 1e-5


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-r", action="store_true")
    args = parser.parse_args()
    failures: list[str] = []
    receipt_lines = ["# Book 1 Python/R parity summary", "", f"Tolerance: {TOLERANCE}", ""]
    for chapter in CHAPTERS:
        py_path = OUTPUTS / chapter / "py_results.json"
        r_path = OUTPUTS / chapter / "r_results.json"
        out_path = OUTPUTS / chapter / "parity_receipt.md"
        if not r_path.exists():
            message = f"R result is missing: {r_path.relative_to(OUTPUTS.parent)}"
            if args.require_r:
                failures.append(message)
            out_path.write_text(f"# Python/R parity receipt\n\nStatus: PENDING\n\n{message}\n", encoding="utf-8")
            receipt_lines.append(f"- {chapter}: PENDING")
            continue
        py = json.loads(py_path.read_text(encoding="utf-8"))["reported_fields"]
        r = json.loads(r_path.read_text(encoding="utf-8"))["reported_fields"]
        mismatches = []
        if set(py) != set(r):
            mismatches.append(f"field names differ: python={sorted(py)} r={sorted(r)}")
        else:
            for key in sorted(py):
                if not math.isclose(float(py[key]), float(r[key]), rel_tol=TOLERANCE, abs_tol=TOLERANCE):
                    mismatches.append(f"{key}: python={py[key]} r={r[key]}")
        if mismatches:
            failures.extend(f"{chapter}: {item}" for item in mismatches)
            status = "FAIL"
        else:
            status = "PASS"
        out_path.write_text(
            "# Python/R parity receipt\n\n"
            f"Chapter: {chapter}\n\nTolerance: {TOLERANCE}\n\nStatus: {status}\n"
            + ("\n".join(f"- {item}" for item in mismatches) + "\n" if mismatches else "\nAll reported fields agree within tolerance.\n"),
            encoding="utf-8",
        )
        receipt_lines.append(f"- {chapter}: {status}")
    summary = OUTPUTS / "PARITY_SUMMARY.md"
    summary.write_text("\n".join(receipt_lines) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit("\n".join(failures))
    subprocess.run([sys.executable, str(Path(__file__).with_name("finalize_apa_reporting_audit.py"))], check=True)
    print(f"wrote {summary}")


if __name__ == "__main__":
    main()
