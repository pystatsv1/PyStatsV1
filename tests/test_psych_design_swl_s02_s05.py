from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from tools.check_psych_design_swl_s02_s05 import verify_companion

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "psych_design_companion" / "swl_s02_s05_v0_1"


def copy_companion(tmp_path: Path) -> Path:
    copied = tmp_path / "companion"
    shutil.copytree(COMPANION, copied)
    return copied


def write_json(path: Path, payload: dict[str, object]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_pristine_batch_passes_exact_verification() -> None:
    verify_companion(COMPANION)


def test_registered_results_are_stable_and_chapter_ready() -> None:
    expected = {
        "SWL-S02": ("welch_t", 7.423685817),
        "SWL-S03": ("paired_t", 9.281362778),
        "SWL-S04": ("anova_f", 65.02135348),
        "SWL-S05": ("interaction_f", 20.56078634),
    }
    for study_id, (field, value) in expected.items():
        receipt = json.loads(
            (
                COMPANION
                / "evidence"
                / study_id
                / "PYTHON_RESULT_RECEIPT.json"
            ).read_text(encoding="utf-8")
        )
        assert receipt["study_id"] == study_id
        assert receipt["synthetic_only"] is True
        assert receipt["reported_fields"][field] == value


def test_duplicate_independent_group_identifier_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "data" / "swl_s02_structured_study_routine.csv"
    data = pd.read_csv(path)
    data.loc[1, "participant_id"] = data.loc[0, "participant_id"]
    data.to_csv(path, index=False, lineterminator="\n")
    with pytest.raises(ValueError, match="duplicate participant"):
        verify_companion(copied)


def test_unpaired_pre_post_row_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "data" / "swl_s03_skills_workshop_pre_post.csv"
    data = pd.read_csv(path)
    data = data.drop(data.index[-1])
    data.to_csv(path, index=False, lineterminator="\n")
    with pytest.raises(ValueError, match="every participant"):
        verify_companion(copied)


def test_unregistered_three_group_level_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "data" / "swl_s04_three_condition_support.csv"
    data = pd.read_csv(path)
    data.loc[0, "support_condition"] = "unregistered_support"
    data.to_csv(path, index=False, lineterminator="\n")
    with pytest.raises(ValueError, match="factor levels"):
        verify_companion(copied)


def test_empty_factorial_cell_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "data" / "swl_s05_strategy_feedback.csv"
    data = pd.read_csv(path)
    keep = ~(
        (data["study_strategy"] == "retrieval_practice")
        & (data["feedback_condition"] == "explanatory_feedback")
    )
    data.loc[keep].to_csv(path, index=False, lineterminator="\n")
    with pytest.raises(ValueError, match="factorial cell counts"):
        verify_companion(copied)


def test_stale_result_receipt_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence" / "SWL-S02" / "PYTHON_RESULT_RECEIPT.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["reported_fields"]["welch_t"] = 999.0
    write_json(path, payload)
    with pytest.raises(ValueError, match="stale result hash|exact regeneration mismatch"):
        verify_companion(copied)


def test_stale_apa_binding_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence" / "SWL-S04" / "APA_RESULT_SOURCE_MAP.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["reported_number_bindings"][0]["json_pointer"] = (
        "/reported_fields/not_a_registered_number"
    )
    write_json(path, payload)
    with pytest.raises(ValueError, match="APA field bindings drifted"):
        verify_companion(copied)


def test_missing_r_path_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    (copied / "scripts" / "r" / "swl_s05.R").unlink()
    with pytest.raises(ValueError, match="missing static files"):
        verify_companion(copied)


def test_public_release_claim_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "PSYCH_DESIGN_SWL_S02_S05_CONTRACT.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["public_release"] = True
    write_json(path, payload)
    with pytest.raises(ValueError, match="must not be a public release"):
        verify_companion(copied)


def test_source_anchor_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "SOURCE_PROVENANCE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["baseline_pystatsv1_commit"] = "0" * 40
    write_json(path, payload)
    with pytest.raises(ValueError, match="source provenance baseline mismatch"):
        verify_companion(copied)


def test_figure_sources_generate_four_grayscale_candidates(tmp_path: Path) -> None:
    output = tmp_path / "figures"
    subprocess.run(
        [
            sys.executable,
            str(COMPANION / "scripts" / "python" / "generate_figures.py"),
            "--root",
            str(COMPANION),
            "--output-root",
            str(output),
        ],
        check=True,
    )
    manifest = json.loads(
        (output / "FIGURE_MANIFEST.json").read_text(encoding="utf-8")
    )
    assert len(manifest["figures"]) == 4
    assert all(row["grayscale"] is True for row in manifest["figures"])
    assert all((output / row["output"]).is_file() for row in manifest["figures"])


def test_incomplete_batch_receipt_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence" / "BATCH_IMPLEMENTATION_RECEIPT.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["all_study_specific_asset_sets_complete"] = False
    write_json(path, payload)
    with pytest.raises(ValueError, match="batch implementation is not complete"):
        verify_companion(copied)


def test_r_parity_field_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence" / "PYTHON_R_VERIFICATION_CONTRACT.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["studies"][0]["parity_fields"].append("not_a_real_metric")
    write_json(path, payload)
    with pytest.raises(ValueError, match="R parity field contract drifted"):
        verify_companion(copied)


def test_method_source_hash_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "METHOD_SOURCE_BINDING.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["studies"][0]["method_python"]["sha256"] = "0" * 64
    write_json(path, payload)
    with pytest.raises(ValueError, match="bound method source drift"):
        verify_companion(copied)

def test_r_metric_reader_rejects_na_with_metric_identity(tmp_path: Path) -> None:
    script_root = COMPANION / "scripts" / "python"
    sys.path.insert(0, str(script_root))
    try:
        from compare_r_results import read_r_metrics
    finally:
        sys.path.remove(str(script_root))

    path = tmp_path / "r_results.csv"
    path.write_text(
        '"metric","value"\n"anova_f","NA"\n',
        encoding="utf-8",
    )
    with pytest.raises(
        ValueError,
        match=r"anova_f.*non-numeric value 'NA'",
    ):
        read_r_metrics(path)


def test_anova_r_paths_use_explicit_finite_formulas() -> None:
    common = (COMPANION / "scripts" / "r" / "common.R").read_text(
        encoding="utf-8"
    )
    swl_s04 = (COMPANION / "scripts" / "r" / "swl_s04.R").read_text(
        encoding="utf-8"
    )
    swl_s05 = (COMPANION / "scripts" / "r" / "swl_s05.R").read_text(
        encoding="utf-8"
    )

    assert "!is.finite(values)" in common
    assert "summary(fit)" not in swl_s04
    assert "summary(fit)" not in swl_s05
    assert "pf(anova_f" in swl_s04
    assert "pf(interaction_f" in swl_s05

def test_generated_assets_use_canonical_lf_and_posix_receipt_paths() -> None:
    receipt_path = COMPANION / "evidence" / "BATCH_EXACT_REGENERATION_RECEIPT.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    generated_paths = list(receipt["generated_file_sha256"])

    assert generated_paths
    assert all("\\" not in path for path in generated_paths)
    assert all(not Path(path).is_absolute() for path in generated_paths)

    for relative in [*generated_paths, "evidence/BATCH_EXACT_REGENERATION_RECEIPT.json"]:
        payload = (COMPANION / relative).read_bytes()
        assert b"\r\n" not in payload, relative
        assert payload.endswith(b"\n"), relative


def test_generator_declares_platform_independent_text_serialization() -> None:
    source = (COMPANION / "scripts" / "python" / "studies.py").read_text(
        encoding="utf-8"
    )
    assert 'newline="\\n"' in source
    assert 'write_bytes(csv_text.encode("utf-8"))' in source
    assert '.relative_to(output_root).as_posix()' in source


def test_r_verification_has_dedicated_nonduplicating_workflow() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    workflow = (
        ROOT
        / ".github"
        / "workflows"
        / "psych-design-swl-first-batch-r-verify.yml"
    ).read_text(encoding="utf-8")

    assert "psych-design-swl-first-batch-r-verify:" not in ci
    assert "pull_request:" in workflow
    assert "branches: [ main ]" in workflow
    assert "make psych-design-swl-s02-s05-r-verify" in workflow
    assert "feat/**" not in workflow
