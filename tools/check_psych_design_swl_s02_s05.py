#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from psych_design_companion.swl_s02_s05_v0_1.scripts.python.studies import (  # noqa: E402
    BASELINE_SOURCE_COMMIT,
    BATCH_ID,
    STUDY_CONFIG,
    STUDY_IDS,
    data_filename,
    generate_tracked_assets,
    load_tracked_dataset,
    sha256,
    validate_dataset,
)

REQUIRED_STATIC = (
    "PSYCH_DESIGN_SWL_S02_S05_CONTRACT.json",
    "SOURCE_PROVENANCE.json",
    "METHOD_SOURCE_BINDING.json",
    "README.md",
    "Makefile",
    "requirements-psych-design-companion.txt",
    "scripts/python/studies.py",
    "scripts/python/run_all.py",
    "scripts/python/compare_r_results.py",
    "scripts/python/generate_figures.py",
    "scripts/r/common.R",
    "scripts/r/run_all.R",
    "scripts/r/swl_s02.R",
    "scripts/r/swl_s03.R",
    "scripts/r/swl_s04.R",
    "scripts/r/swl_s05.R",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def generated_relative_paths(root: Path) -> list[Path]:
    receipt = read_json(root / "evidence" / "BATCH_EXACT_REGENERATION_RECEIPT.json")
    paths = [Path(path) for path in receipt["generated_file_sha256"]]
    paths.append(Path("evidence/BATCH_EXACT_REGENERATION_RECEIPT.json"))
    return sorted(paths)


def verify_contract(root: Path) -> None:
    contract = read_json(root / "PSYCH_DESIGN_SWL_S02_S05_CONTRACT.json")
    if contract["batch_id"] != BATCH_ID:
        raise ValueError("batch identity mismatch")
    if contract["baseline_source_commit"] != BASELINE_SOURCE_COMMIT:
        raise ValueError("baseline source commit mismatch")
    if contract["public_release"] is not False:
        raise ValueError("the source candidate must not be a public release")
    if contract["synthetic_only"] is not True:
        raise ValueError("synthetic-only boundary was weakened")
    if contract["real_data_authorized"] is not False:
        raise ValueError("real data must remain unauthorized")
    if [row["study_id"] for row in contract["studies"]] != list(STUDY_IDS):
        raise ValueError("study order or identity mismatch")
    provenance = read_json(root / "SOURCE_PROVENANCE.json")
    if provenance["baseline_pystatsv1_commit"] != BASELINE_SOURCE_COMMIT:
        raise ValueError("source provenance baseline mismatch")
    if provenance["public_release"] is not False:
        raise ValueError("source provenance incorrectly claims public release")



def verify_method_source_binding(root: Path) -> None:
    binding = read_json(root / "METHOD_SOURCE_BINDING.json")
    if binding["baseline_source_commit"] != BASELINE_SOURCE_COMMIT:
        raise ValueError("method-source baseline mismatch")
    if [row["study_id"] for row in binding["studies"]] != list(STUDY_IDS):
        raise ValueError("method-source study identity mismatch")
    for study in binding["studies"]:
        for role in ("method_rst", "method_python", "method_test"):
            record = study[role]
            path = REPO_ROOT / record["path"]
            if not path.is_file():
                raise ValueError(f"missing bound method source: {record['path']}")
            if sha256(path) != record["sha256"]:
                raise ValueError(f"bound method source drift: {record['path']}")

def verify_required_files(root: Path) -> None:
    missing = [path for path in REQUIRED_STATIC if not (root / path).is_file()]
    if missing:
        raise ValueError(f"missing static files: {missing}")
    for study_id in STUDY_IDS:
        required = (
            f"contracts/{study_id}_DESIGN_CONTRACT.json",
            f"data/{data_filename(study_id)}",
            f"evidence/{study_id}/PYTHON_RESULT_RECEIPT.json",
            f"evidence/{study_id}/FIGURE_SPEC.json",
            f"evidence/{study_id}/APA_RESULT_SOURCE_MAP.json",
            f"evidence/{study_id}/MATCHED_LIMITATION.json",
        )
        missing = [path for path in required if not (root / path).is_file()]
        if missing:
            raise ValueError(f"{study_id}: missing deliverables {missing}")


def verify_study_assets(root: Path) -> None:
    studies_source_hash = sha256(root / "scripts" / "python" / "studies.py")
    for study_id in STUDY_IDS:
        config = STUDY_CONFIG[study_id]
        contract_path = root / "contracts" / f"{study_id}_DESIGN_CONTRACT.json"
        contract = read_json(contract_path)
        if contract["study_id"] != study_id:
            raise ValueError(f"{study_id}: design contract identity mismatch")
        if contract["factor_levels"] != config["factor_levels"]:
            raise ValueError(f"{study_id}: factor-level contract drift")
        if contract["synthetic_only"] is not True:
            raise ValueError(f"{study_id}: synthetic-only boundary weakened")

        dataset = load_tracked_dataset(root, study_id)
        validate_dataset(study_id, dataset)
        dataset_path = root / "data" / data_filename(study_id)

        result_path = root / "evidence" / study_id / "PYTHON_RESULT_RECEIPT.json"
        result = read_json(result_path)
        if result["study_id"] != study_id:
            raise ValueError(f"{study_id}: result receipt identity mismatch")
        if result["data_sha256"] != sha256(dataset_path):
            raise ValueError(f"{study_id}: result receipt has stale dataset hash")
        if result["design_contract_sha256"] != sha256(contract_path):
            raise ValueError(f"{study_id}: result receipt has stale contract hash")
        if result["analysis_source_sha256"] != studies_source_hash:
            raise ValueError(f"{study_id}: result receipt has stale analysis hash")
        if not result["reported_fields"]:
            raise ValueError(f"{study_id}: empty result receipt")

        limitation = read_json(
            root / "evidence" / study_id / "MATCHED_LIMITATION.json"
        )
        if limitation["study_id"] != study_id:
            raise ValueError(f"{study_id}: limitation identity mismatch")
        if limitation["must_accompany_apa_result"] is not True:
            raise ValueError(f"{study_id}: limitation binding weakened")

        figure = read_json(root / "evidence" / study_id / "FIGURE_SPEC.json")
        if figure["study_id"] != study_id or figure["grayscale_required"] is not True:
            raise ValueError(f"{study_id}: figure contract invalid")
        if figure["output_role"] != "generated_build_instance_not_tracked":
            raise ValueError(f"{study_id}: figure output boundary invalid")

        apa = read_json(root / "evidence" / study_id / "APA_RESULT_SOURCE_MAP.json")
        if apa["study_id"] != study_id:
            raise ValueError(f"{study_id}: APA map identity mismatch")
        if apa["receipt_sha256"] != sha256(result_path):
            raise ValueError(f"{study_id}: APA map has stale result hash")
        bound_fields = {
            row["json_pointer"].removeprefix("/reported_fields/")
            for row in apa["reported_number_bindings"]
        }
        if bound_fields != set(config["apa_fields"]):
            raise ValueError(f"{study_id}: APA field bindings drifted")
        if not bound_fields.issubset(result["reported_fields"]):
            raise ValueError(f"{study_id}: APA map points to missing result fields")



def verify_batch_evidence(root: Path) -> None:
    implementation = read_json(root / "evidence" / "BATCH_IMPLEMENTATION_RECEIPT.json")
    if implementation["batch_id"] != BATCH_ID:
        raise ValueError("batch implementation identity mismatch")
    if implementation["all_study_specific_asset_sets_complete"] is not True:
        raise ValueError("batch implementation is not complete")
    if implementation["study_ids"] != list(STUDY_IDS):
        raise ValueError("batch implementation study set mismatch")
    dimensions = implementation["dimensions"]
    for key in (
        "dataset_present",
        "design_contract_present",
        "python_analysis_present",
        "r_verification_path_present",
        "result_receipt_present",
        "figure_source_present",
        "apa_source_map_present",
        "limitations_present",
    ):
        if dimensions[key] is not True:
            raise ValueError(f"batch implementation dimension failed: {key}")
    if dimensions["exact_regeneration_status"] != "passed":
        raise ValueError("batch exact-regeneration dimension failed")
    if implementation["public_release"] is not False:
        raise ValueError("batch implementation incorrectly authorizes release")

    r_contract = read_json(root / "evidence" / "PYTHON_R_VERIFICATION_CONTRACT.json")
    if r_contract["batch_id"] != BATCH_ID:
        raise ValueError("R verification contract identity mismatch")
    if r_contract["independent_path_required"] is not True:
        raise ValueError("independent R path was weakened")
    if float(r_contract["tolerance"]) != 1e-7:
        raise ValueError("R parity tolerance drifted")
    r_studies = {row["study_id"]: row for row in r_contract["studies"]}
    if set(r_studies) != set(STUDY_IDS):
        raise ValueError("R verification study set mismatch")
    for study_id in STUDY_IDS:
        result = read_json(
            root / "evidence" / study_id / "PYTHON_RESULT_RECEIPT.json"
        )
        if set(r_studies[study_id]["parity_fields"]) != set(result["reported_fields"]):
            raise ValueError(f"{study_id}: R parity field contract drifted")
        if not (root / r_studies[study_id]["r_script"]).is_file():
            raise ValueError(f"{study_id}: R verification script is missing")

    handoff = read_json(root / "evidence" / "BOOK_INTEGRATION_HANDOFF.json")
    if handoff["status"] != "ready_after_green_merge":
        raise ValueError("book integration handoff status mismatch")
    if handoff["current_book_source_anchor"] != BASELINE_SOURCE_COMMIT:
        raise ValueError("book integration source-anchor baseline mismatch")
    if handoff["unblocked_study_ids"] != list(STUDY_IDS):
        raise ValueError("book integration study set mismatch")
    if handoff["public_release_authorized"] is not False:
        raise ValueError("book integration handoff authorizes public release")
    if handoff["portal_change_authorized"] is not False:
        raise ValueError("book integration handoff authorizes portal work")

def verify_exact_regeneration(root: Path) -> None:
    tracked_receipt = read_json(
        root / "evidence" / "BATCH_EXACT_REGENERATION_RECEIPT.json"
    )
    if tracked_receipt["exact_regeneration_status"] != "passed":
        raise ValueError("tracked exact-regeneration status is not passed")
    if tracked_receipt["public_release"] is not False:
        raise ValueError("exact-regeneration receipt claims public release")
    if tracked_receipt["baseline_source_commit"] != BASELINE_SOURCE_COMMIT:
        raise ValueError("exact-regeneration baseline mismatch")

    with tempfile.TemporaryDirectory(prefix="pystatsv1-swl-regeneration-") as temp:
        generated_root = Path(temp) / "candidate"
        shutil.copytree(root, generated_root, dirs_exist_ok=True)
        for relative in generated_relative_paths(root):
            path = generated_root / relative
            if path.exists():
                path.unlink()
        generate_tracked_assets(generated_root, generated_root)
        expected_paths = generated_relative_paths(root)
        regenerated_paths = generated_relative_paths(generated_root)
        if expected_paths != regenerated_paths:
            raise ValueError("generated path set changed")
        for relative in expected_paths:
            tracked = root / relative
            regenerated = generated_root / relative
            if tracked.read_bytes() != regenerated.read_bytes():
                raise ValueError(f"exact regeneration mismatch: {relative}")

    for relative, expected_hash in tracked_receipt["generated_file_sha256"].items():
        actual_hash = sha256(root / relative)
        if actual_hash != expected_hash:
            raise ValueError(f"stale exact-regeneration hash: {relative}")
    for relative, expected_hash in tracked_receipt["source_input_sha256"].items():
        actual_hash = sha256(root / relative)
        if actual_hash != expected_hash:
            raise ValueError(f"stale source-input hash: {relative}")


def verify_companion(root: Path) -> None:
    root = root.resolve()
    verify_required_files(root)
    verify_contract(root)
    verify_method_source_binding(root)
    verify_study_assets(root)
    verify_batch_evidence(root)
    verify_exact_regeneration(root)


def run_r_verification(root: Path) -> None:
    if shutil.which("Rscript") is None:
        raise RuntimeError("Rscript is required for independent R verification")
    with tempfile.TemporaryDirectory(prefix="pystatsv1-swl-r-") as temp:
        output_root = Path(temp)
        python_root = output_root / "python"
        r_root = output_root / "r"
        receipt = output_root / "PYTHON_R_PARITY_RECEIPT.json"
        subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "python" / "run_all.py"),
                "--root",
                str(root),
                "--output-root",
                str(python_root),
            ],
            check=True,
        )
        subprocess.run(
            [
                "Rscript",
                str(root / "scripts" / "r" / "run_all.R"),
                str(root),
                str(r_root),
            ],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "python" / "compare_r_results.py"),
                "--root",
                str(root),
                "--python-root",
                str(python_root),
                "--r-root",
                str(r_root),
                "--receipt",
                str(receipt),
            ],
            check=True,
        )
        parity = read_json(receipt)
        if parity["all_within_tolerance"] is not True:
            raise ValueError("Python/R parity receipt failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("psych_design_companion/swl_s02_s05_v0_1"),
    )
    parser.add_argument("--run-r", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    verify_companion(root)
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S02_S05_VERIFY_OK")
    if args.run_r:
        run_r_verification(root)
        print("PYSTATSV1_PSYCH_DESIGN_SWL_S02_S05_R_VERIFY_OK")


if __name__ == "__main__":
    main()
