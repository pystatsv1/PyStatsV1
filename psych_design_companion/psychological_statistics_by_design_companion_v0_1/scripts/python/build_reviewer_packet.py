#!/usr/bin/env python3
"""Build a bounded, hash-manifested reviewer packet for one or all studies."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from companion_runtime import (
    ROOT,
    normalize_study_id,
    sha256,
    study_index,
    write_json,
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_manifest_record(study_id: str, row: dict[str, Any]) -> dict[str, Any]:
    lineage = _load_json(ROOT / "SOURCE_LINEAGE.json")
    study_lineage = next(
        item for item in lineage["studies"] if item["study_id"] == study_id
    )
    return {
        "schema_version": "psych-design-reviewer-source-manifest-record-v0.1",
        "study_id": study_id,
        "source_anchor": lineage["source_anchor"],
        "source_batch": study_lineage["source_batch"],
        "dataset_path": row["dataset_path"],
        "dataset_sha256": sha256(ROOT / row["dataset_path"]),
        "design_contract_path": row["design_contract_path"],
        "design_contract_sha256": sha256(ROOT / row["design_contract_path"]),
        "reference_python_result": row["reference_python_result"],
        "reference_python_result_sha256": sha256(
            ROOT / row["reference_python_result"]
        ),
        "lineage_origins": study_lineage["origins"],
        "synthetic_only": True,
        "real_data_authorized": False,
    }


def _figure_spec_record(study_id: str, row: dict[str, Any]) -> dict[str, Any]:
    records = []
    for relative in row["figure_specs"]:
        path = ROOT / relative
        records.append(
            {
                "path": relative,
                "sha256": sha256(path),
                "payload": _load_json(path),
            }
        )
    return {
        "schema_version": "psych-design-reviewer-figure-spec-record-v0.1",
        "study_id": study_id,
        "specifications": records,
        "synthetic_only": True,
    }


def build(study_id: str) -> Path:
    study_id = normalize_study_id(study_id)
    row = study_index()[study_id]
    slug = study_id.lower().replace("-", "_")
    output = ROOT / "outputs" / slug
    packet = output / "reviewer_packet"

    source_files = {
        "DESIGN_CONTRACT.json": ROOT / row["design_contract_path"],
        "MEASUREMENT_MAP.json": ROOT / row["measurement_map_path"],
        "DATA_LAYOUT_AUDIT.json": output / "data_layout_audit.json",
        "PYTHON_RESULT.json": output / "python_result.json",
        "R_RESULT.csv": output / "r_result.csv",
        "VERIFICATION_RECEIPT.json": output / "verification_receipt.json",
        "FIGURE_MANIFEST.json": output / "figures" / "FIGURE_MANIFEST.json",
        "APA_SOURCE_MAP.json": output / "apa_source_map.json",
        "MATCHED_LIMITATION.md": output / "matched_limitation.md",
    }
    missing = [str(path) for path in source_files.values() if not path.is_file()]
    if missing:
        raise SystemExit(
            "reviewer packet prerequisites missing:\n" + "\n".join(missing)
        )

    if packet.exists():
        shutil.rmtree(packet)
    packet.mkdir(parents=True)

    write_json(packet / "STUDY_INDEX_RECORD.json", row)
    write_json(
        packet / "SOURCE_MANIFEST_RECORD.json",
        _source_manifest_record(study_id, row),
    )
    write_json(packet / "FIGURE_SPECS.json", _figure_spec_record(study_id, row))

    for name, source in source_files.items():
        shutil.copyfile(source, packet / name)

    records = []
    for path in sorted(item for item in packet.iterdir() if item.is_file()):
        records.append(
            {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    manifest = {
        "schema_version": "psych-design-reviewer-packet-manifest-v0.1",
        "study_id": study_id,
        "files": records,
        "file_count": len(records),
        "synthetic_only": True,
        "real_data_authorized": False,
    }
    write_json(packet / "MANIFEST.json", manifest)
    print(
        "PYSTATSV1_PSYCH_DESIGN_REVIEWER_PACKET_OK "
        f"study={study_id} files={len(records)}"
    )
    return packet / "MANIFEST.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study")
    args = parser.parse_args()
    study_ids = [args.study] if args.study else list(study_index())
    for study_id in study_ids:
        build(study_id)


if __name__ == "__main__":
    main()
