#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from studies import STUDY_IDS


def read_r_metrics(path: Path) -> dict[str, float]:
    metrics: dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        if rows.fieldnames != ["metric", "value"]:
            raise ValueError(
                f"{path}: expected CSV columns ['metric', 'value']; "
                f"found {rows.fieldnames!r}"
            )
        for row_number, row in enumerate(rows, start=2):
            metric = (row.get("metric") or "").strip()
            raw_value = (row.get("value") or "").strip()
            if not metric:
                raise ValueError(f"{path}:{row_number}: empty R metric name")
            if metric in metrics:
                raise ValueError(
                    f"{path}:{row_number}: duplicate R metric {metric!r}"
                )
            try:
                value = float(raw_value)
            except ValueError as exc:
                raise ValueError(
                    f"{path}:{row_number}: R metric {metric!r} has "
                    f"non-numeric value {raw_value!r}"
                ) from exc
            if not math.isfinite(value):
                raise ValueError(
                    f"{path}:{row_number}: R metric {metric!r} has "
                    f"non-finite value {raw_value!r}"
                )
            metrics[metric] = value
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--python-root", type=Path)
    parser.add_argument("--r-root", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    python_root = (
        args.python_root.resolve()
        if args.python_root
        else root / "outputs" / "python"
    )
    r_root = args.r_root.resolve() if args.r_root else root / "outputs" / "r"
    receipt_path = (
        args.receipt.resolve()
        if args.receipt
        else root / "outputs" / "PYTHON_R_PARITY_RECEIPT.json"
    )
    contract = json.loads(
        (root / "evidence" / "PYTHON_R_VERIFICATION_CONTRACT.json").read_text(
            encoding="utf-8"
        )
    )
    tolerance = float(contract["tolerance"])
    contract_rows = {row["study_id"]: row for row in contract["studies"]}

    comparisons: list[dict[str, object]] = []
    failures: list[str] = []
    for study_id in STUDY_IDS:
        python_payload = json.loads(
            (python_root / study_id / "py_results.json").read_text(encoding="utf-8")
        )["reported_fields"]
        r_payload = read_r_metrics(r_root / f"{study_id}_r_results.csv")
        expected_fields = set(contract_rows[study_id]["parity_fields"])
        python_fields = set(python_payload)
        r_fields = set(r_payload)
        if python_fields != expected_fields:
            failures.append(
                f"{study_id}: Python fields differ from the parity contract"
            )
        if r_fields != expected_fields:
            failures.append(f"{study_id}: R fields differ from the parity contract")
        missing = sorted(python_fields ^ r_fields)
        study_rows: list[dict[str, object]] = []
        for metric in sorted(expected_fields & python_fields & r_fields):
            py_value = float(python_payload[metric])
            r_value = float(r_payload[metric])
            passed = math.isclose(
                py_value,
                r_value,
                rel_tol=tolerance,
                abs_tol=tolerance,
            )
            study_rows.append(
                {
                    "metric": metric,
                    "python": py_value,
                    "r": r_value,
                    "absolute_difference": abs(py_value - r_value),
                    "status": "pass" if passed else "fail",
                }
            )
            if not passed:
                failures.append(
                    f"{study_id} {metric}: python={py_value} r={r_value}"
                )
        comparisons.append(
            {
                "study_id": study_id,
                "field_names_match": not missing
                and python_fields == expected_fields
                and r_fields == expected_fields,
                "comparisons": study_rows,
                "all_within_tolerance": not missing
                and python_fields == expected_fields
                and r_fields == expected_fields
                and all(row["status"] == "pass" for row in study_rows),
            }
        )

    payload = {
        "contract_version": "0.1",
        "tolerance": tolerance,
        "studies": comparisons,
        "all_within_tolerance": not failures,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"wrote {receipt_path}")
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S02_S05_R_PARITY_OK")


if __name__ == "__main__":
    main()
