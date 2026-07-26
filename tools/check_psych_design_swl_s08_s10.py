from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "psych_design_companion/swl_s08_s10_v0_1"
EXPECTED_BASELINE = "bb618a4c8c8186df43823b33bf2fab3e5d42330a"
EXPECTED_BOOK = "2d8532a62e7b4f1ded957325426ac6ed16a69e06"
EXPECTED_STUDIES = ("SWL-S08", "SWL-S09", "SWL-S10")


def fail(message: str) -> None:
    raise ValueError(message)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_studies(root: Path):
    path = root / "scripts/python/studies.py"
    spec = importlib.util.spec_from_file_location("final_batch_studies_check", path)
    if spec is None or spec.loader is None:
        fail("cannot load study implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_static_files(companion: Path) -> None:
    required = [
        "METHOD_SOURCE_BINDING.json",
        "PSYCH_DESIGN_SWL_S08_S10_CONTRACT.json",
        "README.md",
        "SOURCE_PROVENANCE.json",
        "requirements-psych-design-companion.txt",
        "scripts/python/studies.py",
        "scripts/python/run_all.py",
        "scripts/python/generate_figures.py",
        "scripts/python/compare_r_results.py",
        "scripts/r/common.R",
        "scripts/r/run_all.R",
        "scripts/r/swl_s08.R",
        "scripts/r/swl_s09.R",
        "scripts/r/swl_s10.R",
        "evidence/BATCH_EXACT_REGENERATION_RECEIPT.json",
        "evidence/BATCH_IMPLEMENTATION_RECEIPT.json",
        "evidence/BOOK_INTEGRATION_HANDOFF.json",
        "evidence/PYTHON_R_VERIFICATION_CONTRACT.json",
        "evidence/SWL-S08/PYTHON_R_COMPARISON_POLICY.json",
    ]
    missing = [path for path in required if not (companion / path).is_file()]
    if missing:
        fail("missing static files: " + ", ".join(missing))


def verify_contracts(companion: Path) -> None:
    contract = read_json(companion / "PSYCH_DESIGN_SWL_S08_S10_CONTRACT.json")
    if contract.get("baseline_source_commit") != EXPECTED_BASELINE:
        fail("batch baseline mismatch")
    if contract.get("book_handoff_commit") != EXPECTED_BOOK:
        fail("book handoff mismatch")
    if contract.get("public_release") is not False or contract.get("source_candidate_only") is not True:
        fail("batch must remain a private source candidate")
    if [row["study_id"] for row in contract.get("studies", [])] != list(EXPECTED_STUDIES):
        fail("study batch changed")
    if contract.get("synthesis_chapters_unblocked_after_book_acceptance") != ["ch17", "ch18", "ch19"]:
        fail("synthesis chapter handoff changed")

    provenance = read_json(companion / "SOURCE_PROVENANCE.json")
    if provenance.get("baseline_pystatsv1_commit") != EXPECTED_BASELINE:
        fail("source provenance baseline mismatch")
    if provenance.get("book_dropin_016_merged_main") != EXPECTED_BOOK:
        fail("source provenance book handoff mismatch")
    if provenance.get("public_release") is not False:
        fail("source provenance public release changed")

    implementation = read_json(companion / "evidence/BATCH_IMPLEMENTATION_RECEIPT.json")
    if implementation.get("all_study_specific_asset_sets_complete") is not True:
        fail("batch implementation is not complete")
    if implementation.get("final_study_specific_batch") is not True:
        fail("final-batch role changed")
    if implementation.get("study_ids") != list(EXPECTED_STUDIES):
        fail("batch implementation study set changed")


def verify_method_bindings(companion: Path) -> None:
    binding = read_json(companion / "METHOD_SOURCE_BINDING.json")
    if binding.get("baseline_source_commit") != EXPECTED_BASELINE:
        fail("method binding baseline mismatch")
    for study in binding.get("studies", []):
        for category in ("method_python", "method_rst", "method_test"):
            rows = study.get(category, [])
            if not rows:
                fail(f"missing bound method source: {study.get('study_id')}:{category}")
            for row in rows:
                path = ROOT / row["path"]
                if not path.is_file() or sha256(path) != row["sha256"]:
                    fail("bound method source drift: " + row["path"])


def verify_studies(companion: Path) -> None:
    studies = load_studies(companion)
    verification = read_json(companion / "evidence/PYTHON_R_VERIFICATION_CONTRACT.json")
    parity_by_study = {row["study_id"]: row["parity_fields"] for row in verification["studies"]}
    for study_id in EXPECTED_STUDIES:
        dataset = studies.dataset_path(companion, study_id)
        contract = companion / "contracts" / f"{study_id}_DESIGN_CONTRACT.json"
        evidence = companion / "evidence" / study_id
        if not dataset.is_file() or not contract.is_file():
            fail("missing study dataset or contract: " + study_id)
        frame = pd.read_csv(dataset)
        studies.validate_dataset(study_id, frame)
        receipt = read_json(evidence / "PYTHON_RESULT_RECEIPT.json")
        if receipt.get("dataset_sha256") != sha256(dataset):
            fail("stale dataset hash: " + study_id)
        if receipt.get("design_contract_sha256") != sha256(contract):
            fail("stale design hash: " + study_id)
        recomputed = studies.ANALYZERS[study_id](frame)
        if receipt.get("reported_fields") != recomputed:
            fail("stale result fields: " + study_id)
        for field in parity_by_study[study_id]:
            if field not in recomputed:
                fail("R verification field drifted: " + study_id + ":" + field)
        apa_files = sorted(evidence.glob("APA_RESULT_SOURCE_MAP*.json"))
        figure_files = sorted(evidence.glob("FIGURE_SPEC*.json"))
        limitation_files = sorted(evidence.glob("MATCHED_LIMITATION*.json"))
        if not apa_files or not figure_files or not limitation_files:
            fail("incomplete evidence asset set: " + study_id)
        for apa_path in apa_files:
            apa = read_json(apa_path)
            for row in apa.get("reported_number_bindings", []):
                field = row.get("field")
                if row.get("json_pointer") != f"/reported_fields/{field}" or field not in recomputed:
                    fail("APA field binding drifted: " + study_id)
        if any(read_json(path).get("grayscale") is not True for path in figure_files):
            fail("figure grayscale boundary changed: " + study_id)
        if any(not read_json(path).get("limitation") for path in limitation_files):
            fail("matched limitation missing: " + study_id)


def verify_scientific_boundaries(companion: Path) -> None:
    studies = load_studies(companion)
    s08 = read_json(companion / "evidence/SWL-S08/PYTHON_RESULT_RECEIPT.json")["reported_fields"]
    if s08["observed_rows"] != 168 or s08["missing_visits"] != 12:
        fail("SWL-S08 observed-visit boundary changed")
    if s08["treatment_post_b"] <= 0 or s08["treatment_followup_b"] <= 0:
        fail("SWL-S08 interaction direction changed")

    s09 = read_json(companion / "evidence/SWL-S09/PYTHON_RESULT_RECEIPT.json")["reported_fields"]
    if s09["minimum_expected_cell_count"] < 5:
        fail("SWL-S09 chi-square expected-count boundary failed")
    if s09["comparison_burden_skewness"] <= 1 or s09["intervention_burden_skewness"] <= 1:
        fail("SWL-S09 positive-skew fixture changed")
    if s09["intervention_burden_median"] >= s09["comparison_burden_median"]:
        fail("SWL-S09 rank-analysis direction changed")

    frame = pd.read_csv(studies.dataset_path(companion, "SWL-S10"))
    if not (frame["sampling_variance_d"] > 0).all():
        fail("SWL-S10 sampling variance changed")
    s10 = read_json(companion / "evidence/SWL-S10/PYTHON_RESULT_RECEIPT.json")["reported_fields"]
    if s10["planning_n_per_group_ceiling_80"] != 99:
        fail("SWL-S10 power-planning result changed")
    if not (0 < s10["fixed_effect_pooled_d"] < 1):
        fail("SWL-S10 pooled-effect boundary changed")


def verify_exact_regeneration() -> None:
    exact = read_json(COMPANION / "evidence/BATCH_EXACT_REGENERATION_RECEIPT.json")
    if exact.get("exact_regeneration_status") != "passed":
        fail("exact regeneration status changed")
    if exact.get("baseline_source_commit") != EXPECTED_BASELINE:
        fail("exact regeneration baseline mismatch")
    for relative, expected in exact.get("generated_file_sha256", {}).items():
        path = COMPANION / relative
        if not path.is_file() or sha256(path) != expected:
            fail("exact regeneration mismatch: " + relative)
    for relative, expected in exact.get("source_input_sha256", {}).items():
        path = COMPANION / relative
        if not path.is_file() or sha256(path) != expected:
            fail("source input drift: " + relative)

    with tempfile.TemporaryDirectory() as directory:
        copied_root = Path(directory) / "repo"
        shutil.copytree(ROOT, copied_root)
        copied_companion = copied_root / COMPANION.relative_to(ROOT)
        subprocess.run(
            [sys.executable, str(copied_root / "tools/build_psych_design_swl_s08_s10.py")],
            cwd=copied_root,
            check=True,
            capture_output=True,
            text=True,
        )
        regenerated = read_json(copied_companion / "evidence/BATCH_EXACT_REGENERATION_RECEIPT.json")
        if regenerated != exact:
            fail("exact regeneration receipt drifted")
        for relative in exact["generated_file_sha256"]:
            if (copied_companion / relative).read_bytes() != (COMPANION / relative).read_bytes():
                fail("exact regeneration byte mismatch: " + relative)


def run_r_verification(companion: Path) -> None:
    executable = shutil.which("Rscript")
    if executable is None:
        fail("Rscript is required for --run-r")
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "r"
        subprocess.run(
            [executable, str(companion / "scripts/r/run_all.R"), str(companion), str(output)],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(companion / "scripts/python/compare_r_results.py"),
                "--root",
                str(companion),
                "--r-root",
                str(output),
            ],
            check=True,
        )


def verify_companion(companion: Path = COMPANION, run_r: bool = False) -> None:
    verify_static_files(companion)
    verify_contracts(companion)
    verify_method_bindings(companion)
    verify_studies(companion)
    verify_scientific_boundaries(companion)
    if companion.resolve() == COMPANION.resolve():
        verify_exact_regeneration()
    if run_r:
        run_r_verification(companion)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-r", action="store_true")
    args = parser.parse_args()
    verify_companion(run_r=args.run_r)
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S08_S10_VERIFY_OK")


if __name__ == "__main__":
    main()
