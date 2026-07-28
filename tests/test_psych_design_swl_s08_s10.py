from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "psych_design_companion/swl_s08_s10_v0_1"
CHECKER = ROOT / "tools/check_psych_design_swl_s08_s10.py"

spec = importlib.util.spec_from_file_location("final_batch_checker", CHECKER)
assert spec is not None and spec.loader is not None
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)

STUDIES_PATH = COMPANION / "scripts/python/studies.py"
studies_spec = importlib.util.spec_from_file_location("final_batch_studies", STUDIES_PATH)
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
    assert "PYSTATSV1_PSYCH_DESIGN_SWL_S08_S10_VERIFY_OK" in done.stdout


def test_exact_regeneration_receipt_covers_generated_assets() -> None:
    receipt = read(COMPANION / "evidence/BATCH_EXACT_REGENERATION_RECEIPT.json")
    assert receipt["exact_regeneration_status"] == "passed"
    assert receipt["generated_file_count"] == len(receipt["generated_file_sha256"])
    assert receipt["generated_file_count"] >= 27
    for relative in receipt["generated_file_sha256"]:
        assert (COMPANION / relative).is_file()


def test_swl_s08_preserves_unequal_visit_mixed_model_target() -> None:
    values = read(COMPANION / "evidence/SWL-S08/PYTHON_RESULT_RECEIPT.json")[
        "reported_fields"
    ]
    assert values["n_participants"] == 60
    assert values["observed_rows"] == 168
    assert values["missing_visits"] == 12
    assert values["complete_participants"] == 48
    assert values["treatment_post_b"] == pytest.approx(5.86493, abs=1e-5)
    assert values["treatment_followup_b"] == pytest.approx(7.784909, abs=1e-5)
    assert values["converged"] == 1


def test_swl_s09_keeps_registered_outcomes_distinct() -> None:
    values = read(COMPANION / "evidence/SWL-S09/PYTHON_RESULT_RECEIPT.json")[
        "reported_fields"
    ]
    assert values["comparison_improved"] == 36
    assert values["intervention_improved"] == 56
    assert values["chi_square_p"] < 0.01
    assert values["minimum_expected_cell_count"] >= 5
    assert values["comparison_burden_skewness"] > 1
    assert values["intervention_burden_skewness"] > 1
    assert values["intervention_burden_median"] < values["comparison_burden_median"]
    assert values["mann_whitney_p_two_sided"] < 0.001


def test_swl_s10_separates_planning_from_observed_synthesis() -> None:
    values = read(COMPANION / "evidence/SWL-S10/PYTHON_RESULT_RECEIPT.json")[
        "reported_fields"
    ]
    assert values["study_count"] == 6
    assert values["planning_n_per_group_ceiling_80"] == 99
    assert values["planning_n_per_group_ceiling_90"] == 132
    assert 0.35 < values["fixed_effect_pooled_d"] < 0.45
    assert values["fixed_effect_p"] < 0.001
    assert values["i_squared_percent"] == 0


def test_swl_s08_duplicate_visit_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "data/swl_s08_longitudinal_treatment.csv"
    frame = pd.read_csv(path)
    frame.loc[1, ["participant_id", "occasion"]] = frame.loc[
        0, ["participant_id", "occasion"]
    ]
    frame.to_csv(path, index=False, lineterminator="\n")
    with pytest.raises(ValueError, match="duplicate participant/occasion"):
        MOD.verify_companion(copied)


def test_swl_s09_group_balance_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "data/swl_s09_outcome_distribution_extension.csv"
    frame = pd.read_csv(path)
    frame.loc[0, "support_condition"] = "intervention"
    frame.to_csv(path, index=False, lineterminator="\n")
    with pytest.raises(ValueError, match="group balance"):
        MOD.verify_companion(copied)


def test_swl_s10_variance_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "data/swl_s10_replication_program.csv"
    frame = pd.read_csv(path)
    frame.loc[0, "sampling_variance_d"] = 0
    frame.to_csv(path, index=False, lineterminator="\n")
    with pytest.raises(ValueError, match="variances must be positive"):
        MOD.verify_companion(copied)


def test_stale_result_receipt_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence/SWL-S10/PYTHON_RESULT_RECEIPT.json"
    payload = read(path)
    payload["reported_fields"]["fixed_effect_pooled_d"] = 9.99
    write(path, payload)
    with pytest.raises(ValueError, match="stale result fields"):
        MOD.verify_companion(copied)


def test_stale_apa_binding_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence/SWL-S09/APA_RESULT_SOURCE_MAP_RANK.json"
    payload = read(path)
    payload["reported_number_bindings"][0]["json_pointer"] = (
        "/reported_fields/not_registered"
    )
    write(path, payload)
    with pytest.raises(ValueError, match="APA field binding drifted"):
        MOD.verify_companion(copied)


def test_missing_r_path_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    (copied / "scripts/r/swl_s08.R").unlink()
    with pytest.raises(ValueError, match="missing static files"):
        MOD.verify_companion(copied)


def test_public_release_claim_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "PSYCH_DESIGN_SWL_S08_S10_CONTRACT.json"
    payload = read(path)
    payload["public_release"] = True
    write(path, payload)
    with pytest.raises(ValueError, match="private source candidate"):
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


def test_r_verification_field_drift_is_rejected(tmp_path: Path) -> None:
    copied = copy_companion(tmp_path)
    path = copied / "evidence/PYTHON_R_VERIFICATION_CONTRACT.json"
    payload = read(path)
    payload["studies"][1]["parity_fields"].append("not_a_metric")
    write(path, payload)
    with pytest.raises(ValueError, match="R verification field drifted"):
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


def test_r_verification_is_governed_local_only() -> None:
    workflow = ROOT / ".github/workflows/psych-design-swl-final-batch-r-verify.yml"
    assert not workflow.exists()

    runner = (ROOT / "tools/run_local_r_verification.py").read_text(encoding="utf-8")
    policy = (ROOT / "docs/LOCAL_R_VERIFICATION_POLICY.md").read_text(encoding="utf-8")
    assert "psych-design-swl-s08-s10-r-verify" in runner
    assert "nlme" in runner
    assert "r-cran-nlme" in policy
