#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import sys
from importlib import metadata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "psych_design_companion/swl_s01_s06_s07_v0_1/ENVIRONMENT_CONTRACT.json"
MARKER = "PYSTATSV1_PSYCH_DESIGN_SWL_S01_S06_S07_ENVIRONMENT_OK"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def runtime_receipt() -> dict[str, Any]:
    contract = read_json(CONTRACT)
    expected_python = contract["python"]
    expected_packages = contract["packages"]
    actual_packages = {name: metadata.version(name) for name in expected_packages}
    return {
        "contract_version": contract["contract_version"],
        "batch_id": contract["batch_id"],
        "status": "passed",
        "python": {
            "expected": f"{expected_python['major']}.{expected_python['minor']}",
            "actual": f"{sys.version_info.major}.{sys.version_info.minor}",
            "full": platform.python_version(),
        },
        "packages": {
            name: {"expected": expected, "actual": actual_packages[name]}
            for name, expected in expected_packages.items()
        },
        "exact_result_identity_required": contract["exact_result_identity_required"],
    }


def verify(receipt: dict[str, Any]) -> None:
    if receipt["python"]["actual"] != receipt["python"]["expected"]:
        raise SystemExit(
            "governed Python version mismatch: "
            + receipt["python"]["actual"]
            + " != "
            + receipt["python"]["expected"]
        )
    mismatches = [
        f"{name}={row['actual']} (expected {row['expected']})"
        for name, row in receipt["packages"].items()
        if row["actual"] != row["expected"]
    ]
    if mismatches:
        raise SystemExit("governed package version mismatch: " + ", ".join(mismatches))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = runtime_receipt()
    verify(receipt)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(MARKER)


if __name__ == "__main__":
    main()
