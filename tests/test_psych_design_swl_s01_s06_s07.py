from __future__ import annotations

import importlib.util
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "psych_design_companion/swl_s01_s06_s07_v0_1"
CHECKER = ROOT / "tools/check_psych_design_swl_s01_s06_s07.py"

spec = importlib.util.spec_from_file_location("second_batch_checker", CHECKER)
assert spec is not None and spec.loader is not None
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)

STUDIES_PATH = COMPANION / "scripts/python/studies.py"
studies_spec = importlib.util.spec_from_file_location("second_batch_studies", STUDIES_PATH)
assert studies_spec is not None and studies_spec.loader is not None
STUDIES = importlib.util.module_from_spec(studies_spec)
studies_spec.loader.exec_module(STUDIES)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def copy_companion(tmp_path: Path) -> Path:
    copied = tmp_path / "companion"
    shutil.copytree(COMPANION, copied)
    return copied


def test_checker_passes() -> None:
    done = subprocess.run(
        [sys.executable, str(CHECKER)],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    assert "PYSTATSV1_PSYCH_DESIGN_SWL_S01_S06_S07_VERIFY_OK" in done.stdout


def test_exact_regeneration_receipt_covers_generated_assets() -> None:
    receipt = read(COMPANION / "evidence/BATCH_EXACT_REGENERATION_RECEIPT.json")
    assert receipt["exact_regeneration_status"] == "passed"
    assert receipt["generated_file_count"] == len(receipt["generated_file_sha256"])
    assert receipt["generated_file_count"] >= 24
    for relative in receipt["generated_file_sha256"]:
        assert (COMPANION / relative).is_file()


def test_swl_s01_supports_distinct_association_and_prediction_targets() -> None:
    values = read(COMPANION / "evidence/SWL-S01/PYTHON_RESULT_RECEIPT.json")["reported_fields"]
    assert values["n"] == 120
    assert 0.70 < values["correlation_r_sleep_confidence"] < 0.80
    assert values["correlation_p_two_sided"] < 0.001
    assert values["regression_r_squared"] > 0.60
    assert values["study_hours_b"] > 0
    assert values["confidence_b"] > 0
    assert values["cooks_distance_above_4_over_n"] == 0


def test_swl_s01_fisher_interval_uses_exact_normal_quantile() -> None:
    frame = pd.read_csv(COMPANION / "data/swl_s01_student_well_being_survey.csv")
    values = STUDIES.analyze_swl_s01(frame)
    r = float(values["correlation_r_sleep_confidence"])
    fisher_z = math.atanh(r)
    fisher_se = 1.0 / math.sqrt(len(frame) - 3)
    critical = float(stats.norm.ppf(0.975))
    expected_low = math.tanh(fisher_z - critical * fisher_se)
    expected_high = math.tanh(fisher_z + critical * fisher_se)

    assert values["correlation_ci_95_low"] == pytest.approx(expected_low, abs=1e-9)
    assert values["correlation_ci_95_high"] == pytest.approx(expected_high, abs=1e-9)

    approximate_low = math.tanh(fisher_z - 1.96 * fisher_se)
    assert abs(float(values["correlation_ci_95_low"]) - approximate_low) > 1e-6


def test_swl_s06_records_missing_visits_and_complete_case_target() -> None:
    values = read(COMPANION / "evidence/SWL-S06/PYTHON_RESULT_RECEIPT.json")["reported_fields"]
    assert values["n_scheduled_participants"] == 60
    assert values["scheduled_rows"] == 180
    assert values["missing_outcomes"] == 6
    assert values["n_complete_case"] == 54
    assert 0.5 <= values["greenhouse_geisser_epsilon"] <= 1.0
    assert values["greenhouse_geisser_p"] < 0.001


def test_swl_s07_binds_adjusted_effect_and_slope_diagnostic() -> None:
    values = read(COMPANION / "evidence/SWL-S07/PYTHON_RESULT_RECEIPT.json")["reported_fields"]
    assert values["n_total"] == 90
    assert values["adjusted_group_difference_intervention_minus_comparison"] > 3.0
    assert values["group_effect_p"] < 0.001
    assert values["homogeneity_interaction_p"] > 0.05
    assert values["model_r_squared"] > 0.80


def test_duplicate_swl_s01_identifier_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "data/swl_s01_student_well_being_survey.csv"
    frame = pd.read_csv(path)
    frame.loc[1, "participant_id"] = frame.loc[0, "participant_id"]
    frame.to_csv(path, index=False, lineterminator="\n")
    with pytest.raises(ValueError, match="SWL-S01 row or participant count"):
        MOD.verify_companion(copied)


def test_swl_s06_missing_visit_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "data/swl_s06_confidence_trajectory.csv"
    frame = pd.read_csv(path)
    frame.loc[frame.index[0], "academic_confidence"] = None
    frame.to_csv(path, index=False, lineterminator="\n", na_rep="")
    with pytest.raises(ValueError, match="SWL-S06 missing-visit count"):
        MOD.verify_companion(copied)


def test_swl_s07_group_count_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "data/swl_s07_baseline_adjusted_intervention.csv"
    frame = pd.read_csv(path)
    frame.loc[0, "intervention_group"] = "intervention"
    frame.to_csv(path, index=False, lineterminator="\n")
    with pytest.raises(ValueError, match="SWL-S07 group counts"):
        MOD.verify_companion(copied)


def test_stale_result_receipt_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence/SWL-S07/PYTHON_RESULT_RECEIPT.json"
    payload = read(path)
    payload["reported_fields"]["group_effect_f"] = 999.0
    write(path, payload)
    with pytest.raises(ValueError, match="stale result hash or reported fields"):
        MOD.verify_companion(copied)


def test_stale_apa_binding_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence/SWL-S01/APA_RESULT_SOURCE_MAP_REGRESSION.json"
    payload = read(path)
    payload["reported_number_bindings"][0]["json_pointer"] = "/reported_fields/not_registered"
    write(path, payload)
    with pytest.raises(ValueError, match="APA field bindings drifted"):
        MOD.verify_companion(copied)


def test_missing_r_path_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    (copied / "scripts/r/swl_s06.R").unlink()
    with pytest.raises(ValueError, match="missing static files"):
        MOD.verify_companion(copied)


def test_public_release_claim_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "PSYCH_DESIGN_SWL_S01_S06_S07_CONTRACT.json"
    payload = read(path)
    payload["public_release"] = True
    write(path, payload)
    with pytest.raises(ValueError, match="must not be a public release"):
        MOD.verify_companion(copied)


def test_source_anchor_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "SOURCE_PROVENANCE.json"
    payload = read(path)
    payload["baseline_pystatsv1_commit"] = "0" * 40
    write(path, payload)
    with pytest.raises(ValueError, match="source provenance baseline mismatch"):
        MOD.verify_companion(copied)


def test_figure_sources_generate_four_grayscale_candidates(tmp_path: Path) -> None:
    output = tmp_path / "figures"
    done = subprocess.run(
        [
            sys.executable,
            str(COMPANION / "scripts/python/generate_figures.py"),
            "--root",
            str(COMPANION),
            "--output-root",
            str(output),
        ],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = read(output / "FIGURE_MANIFEST.json")
    assert len(manifest["figures"]) == 4
    assert all(row["grayscale"] is True for row in manifest["figures"])
    assert all((output / row["output"]).is_file() for row in manifest["figures"])


def test_incomplete_batch_receipt_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence/BATCH_IMPLEMENTATION_RECEIPT.json"
    payload = read(path)
    payload["all_study_specific_asset_sets_complete"] = False
    write(path, payload)
    with pytest.raises(ValueError, match="batch implementation is not complete"):
        MOD.verify_companion(copied)


def test_r_parity_field_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence/PYTHON_R_VERIFICATION_CONTRACT.json"
    payload = read(path)
    payload["studies"][0]["parity_fields"].append("not_a_metric")
    write(path, payload)
    with pytest.raises(ValueError, match="R parity field contract drifted"):
        MOD.verify_companion(copied)


def test_method_source_hash_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "METHOD_SOURCE_BINDING.json"
    payload = read(path)
    payload["studies"][0]["method_python"][0]["sha256"] = "0" * 64
    write(path, payload)
    with pytest.raises(ValueError, match="bound method source drift"):
        MOD.verify_companion(copied)


def test_generated_assets_use_lf_and_posix_receipt_paths() -> None:
    receipt = read(COMPANION / "evidence/BATCH_EXACT_REGENERATION_RECEIPT.json")
    generated = list(receipt["generated_file_sha256"])
    assert generated
    assert all("\\" not in path for path in generated)
    assert all(not Path(path).is_absolute() for path in generated)
    for relative in [*generated, "evidence/BATCH_EXACT_REGENERATION_RECEIPT.json"]:
        payload = (COMPANION / relative).read_bytes()
        assert b"\r\n" not in payload, relative
        assert payload.endswith(b"\n"), relative


def test_r_verification_has_dedicated_workflow() -> None:
    workflow = ROOT / ".github/workflows/psych-design-swl-second-batch-r-verify.yml"
    text = workflow.read_text(encoding="utf-8")
    assert "pull_request:" in text
    assert "branches: [ main ]" in text
    assert "make psych-design-swl-s01-s06-s07-r-verify" in text
    assert "feat/**" not in text
