from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


def read_r_metrics(path: Path) -> dict[str, float]:
    result: dict[str, float] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            metric = row["metric"]
            raw = row["value"]
            try:
                value = float(raw)
            except ValueError as error:
                raise ValueError(f"{metric}: non-numeric value {raw!r}") from error
            if not math.isfinite(value):
                raise ValueError(f"{metric}: non-finite value {raw!r}")
            result[metric] = value
    return result


def compare(root: Path, r_root: Path) -> dict[str, Any]:
    contract = json.loads(
        (root / "evidence/PYTHON_R_VERIFICATION_CONTRACT.json").read_text(
            encoding="utf-8"
        )
    )
    rows: list[dict[str, Any]] = []
    for study in contract["studies"]:
        study_id = study["study_id"]
        python_payload = json.loads(
            (root / "evidence" / study_id / "PYTHON_RESULT_RECEIPT.json").read_text(
                encoding="utf-8"
            )
        )["reported_fields"]
        r_payload = read_r_metrics(r_root / f"{study_id}.csv")
        default_tolerance = float(study.get("default_absolute_tolerance", 1e-7))
        field_tolerances = {
            key: float(value)
            for key, value in study.get("absolute_tolerance_by_field", {}).items()
        }
        for field in study["parity_fields"]:
            if field not in python_payload or field not in r_payload:
                raise ValueError(f"missing parity field {study_id}:{field}")
            python_value = float(python_payload[field])
            r_value = float(r_payload[field])
            difference = abs(python_value - r_value)
            tolerance = field_tolerances.get(field, default_tolerance)
            if difference > tolerance:
                raise ValueError(
                    f"R verification mismatch {study_id}:{field}: "
                    f"python={python_value} r={r_value} difference={difference} "
                    f"allowed={tolerance}"
                )
            rows.append(
                {
                    "absolute_difference": difference,
                    "allowed_absolute_difference": tolerance,
                    "field": field,
                    "study_id": study_id,
                    "verification_category": study["verification_category"],
                }
            )
    return {
        "contract_version": "0.1",
        "parity_status": "passed",
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--r-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = compare(args.root.resolve(), args.r_root.resolve())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S08_S10_R_VERIFICATION_OK")


if __name__ == "__main__":
    main()
