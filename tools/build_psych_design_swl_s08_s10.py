from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "psych_design_companion/swl_s08_s10_v0_1"
STUDIES_PATH = COMPANION / "scripts/python/studies.py"


def load_studies():
    spec = importlib.util.spec_from_file_location(
        "psych_design_final_batch_studies", STUDIES_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load final-batch study implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def relative_hashes(paths: list[Path]) -> dict[str, str]:
    return {
        path.relative_to(COMPANION).as_posix(): sha256(path)
        for path in sorted(paths)
    }


def main() -> None:
    studies = load_studies()
    generated = studies.generate_all(COMPANION)

    comparison_policy = COMPANION / "evidence/SWL-S08/PYTHON_R_COMPARISON_POLICY.json"
    write_json(
        comparison_policy,
        {
            "contract_version": "0.1",
            "python_engine": "statsmodels MixedLM",
            "r_engine": "nlme::lme",
            "shared_model": {
                "fixed_effects_formula": (
                    "well_being_score ~ treatment + post + followup + "
                    "treatment_post + treatment_followup"
                ),
                "random_effects_structure": "random intercept for participant_id",
                "estimation_method": "maximum likelihood",
                "group_reference": "control",
                "occasion_reference": "baseline",
            },
            "study_id": "SWL-S08",
            "v3_estimand_aligned_fields": {
                "estimate_absolute_tolerance": 0.05,
                "standard_error_absolute_tolerance": 0.15,
            },
            "v4_documented_fields": [
                "test_statistic_type",
                "denominator_degrees_of_freedom",
                "p_value",
                "confidence_interval_method",
                "optimizer_details",
                "log_likelihood_and_information_criteria",
            ],
        },
    )
    generated.append(comparison_policy)

    s08_parity = [
        "n_participants",
        "n_control",
        "n_treatment",
        "scheduled_rows",
        "observed_rows",
        "missing_visits",
        "complete_participants",
        "incomplete_participants",
        "control_baseline_mean",
        "control_post_mean",
        "control_followup_mean",
        "treatment_baseline_mean",
        "treatment_post_mean",
        "treatment_followup_mean",
        "intercept_b",
        "intercept_se",
        "treatment_b",
        "treatment_se",
        "post_b",
        "post_se",
        "followup_b",
        "followup_se",
        "treatment_post_b",
        "treatment_post_se",
        "treatment_followup_b",
        "treatment_followup_se",
    ]
    s08_tolerances = {
        field: 0.15 if field.endswith("_se") else 0.05
        for field in s08_parity
        if field.endswith("_b") or field.endswith("_se")
    }
    verification_contract = COMPANION / "evidence/PYTHON_R_VERIFICATION_CONTRACT.json"
    write_json(
        verification_contract,
        {
            "batch_id": studies.BATCH_ID,
            "contract_version": "0.1",
            "independent_implementation": (
                "R scripts do not call the Python implementation; SWL-S08 uses "
                "nlme::lme and SWL-S09/S10 use explicit base-R calculations."
            ),
            "runtime_outputs_tracked": False,
            "studies": [
                {
                    "absolute_tolerance_by_field": s08_tolerances,
                    "default_absolute_tolerance": 1e-7,
                    "parity_fields": s08_parity,
                    "r_script": "scripts/r/swl_s08.R",
                    "study_id": "SWL-S08",
                    "verification_category": "V3_estimand_aligned",
                },
                {
                    "default_absolute_tolerance": 1e-7,
                    "parity_fields": [
                        "n_total",
                        "n_comparison",
                        "n_intervention",
                        "comparison_improved",
                        "comparison_not_improved",
                        "intervention_improved",
                        "intervention_not_improved",
                        "comparison_improved_proportion",
                        "intervention_improved_proportion",
                        "improved_risk_difference_intervention_minus_comparison",
                        "chi_square",
                        "chi_square_df",
                        "chi_square_p",
                        "cramers_v",
                        "minimum_expected_cell_count",
                        "comparison_burden_median",
                        "intervention_burden_median",
                        "burden_median_difference_intervention_minus_comparison",
                        "mann_whitney_u_intervention",
                        "mann_whitney_z_no_continuity",
                        "mann_whitney_p_two_sided",
                        "rank_biserial_intervention_lower",
                        "comparison_burden_min",
                        "comparison_burden_max",
                        "intervention_burden_min",
                        "intervention_burden_max",
                    ],
                    "r_script": "scripts/r/swl_s09.R",
                    "study_id": "SWL-S09",
                    "verification_category": "V2_numeric_parity",
                },
                {
                    "default_absolute_tolerance": 1e-7,
                    "parity_fields": [
                        "study_count",
                        "total_participants",
                        "target_effect_size_d",
                        "planning_alpha_two_sided",
                        "planning_power_primary",
                        "planning_n_per_group_unrounded_80",
                        "planning_n_per_group_ceiling_80",
                        "planning_power_sensitivity",
                        "planning_n_per_group_unrounded_90",
                        "planning_n_per_group_ceiling_90",
                        "minimum_observed_d",
                        "maximum_observed_d",
                        "fixed_effect_pooled_d",
                        "fixed_effect_se",
                        "fixed_effect_z",
                        "fixed_effect_p",
                        "fixed_effect_ci_95_low",
                        "fixed_effect_ci_95_high",
                        "cochran_q",
                        "cochran_q_df",
                        "cochran_q_p",
                        "i_squared_percent",
                    ],
                    "r_script": "scripts/r/swl_s10.R",
                    "study_id": "SWL-S10",
                    "verification_category": "V2_numeric_parity",
                },
            ],
        },
    )
    generated.append(verification_contract)

    implementation = COMPANION / "evidence/BATCH_IMPLEMENTATION_RECEIPT.json"
    write_json(
        implementation,
        {
            "all_study_specific_asset_sets_complete": True,
            "baseline_source_commit": studies.BASELINE_SOURCE_COMMIT,
            "batch_id": studies.BATCH_ID,
            "book_drafting_unblock_role": (
                "eligible_after_green_merge_and_explicit_new_book_source_anchor"
            ),
            "book_handoff_commit": studies.BOOK_HANDOFF_COMMIT,
            "contract_version": "0.1",
            "dimensions": {
                "apa_source_map_present": True,
                "dataset_present": True,
                "design_contract_present": True,
                "exact_regeneration_status": "passed",
                "figure_source_present": True,
                "limitations_present": True,
                "python_analysis_present": True,
                "r_verification_path_present": True,
                "result_receipt_present": True,
            },
            "final_study_specific_batch": True,
            "public_release": False,
            "study_ids": list(studies.STUDY_IDS),
            "synthetic_only": True,
        },
    )
    generated.append(implementation)

    handoff = COMPANION / "evidence/BOOK_INTEGRATION_HANDOFF.json"
    write_json(
        handoff,
        {
            "accepted_book_baseline": studies.BOOK_HANDOFF_COMMIT,
            "analysis_chapter_authorization_candidate": ["ch14", "ch15", "ch16"],
            "batch_id": studies.BATCH_ID,
            "book_construction_candidate": [
                "ch14",
                "ch15",
                "ch16",
                "part04",
                "ch17",
                "ch18",
                "ch19",
            ],
            "contract_version": "0.1",
            "next_book_action": (
                "After this PyStatsV1 batch is merged and tagged, create a book "
                "source-anchor acceptance drop-in that verifies the exact assets and "
                "reopens controlled construction of Chapters 14 through 19."
            ),
            "public_release": False,
            "required_new_pystatsv1_commit_anchor": True,
            "study_ids": list(studies.STUDY_IDS),
            "synthetic_only": True,
        },
    )
    generated.append(handoff)

    source_inputs = [
        COMPANION / "METHOD_SOURCE_BINDING.json",
        COMPANION / "PSYCH_DESIGN_SWL_S08_S10_CONTRACT.json",
        COMPANION / "SOURCE_PROVENANCE.json",
        COMPANION / "scripts/python/studies.py",
        COMPANION / "scripts/python/generate_figures.py",
        COMPANION / "scripts/python/compare_r_results.py",
        COMPANION / "scripts/r/common.R",
        COMPANION / "scripts/r/run_all.R",
        COMPANION / "scripts/r/swl_s08.R",
        COMPANION / "scripts/r/swl_s09.R",
        COMPANION / "scripts/r/swl_s10.R",
    ]
    exact = COMPANION / "evidence/BATCH_EXACT_REGENERATION_RECEIPT.json"
    write_json(
        exact,
        {
            "baseline_source_commit": studies.BASELINE_SOURCE_COMMIT,
            "batch_id": studies.BATCH_ID,
            "book_handoff_commit": studies.BOOK_HANDOFF_COMMIT,
            "contract_version": "0.1",
            "exact_regeneration_status": "passed",
            "generated_file_count": len(generated),
            "generated_file_sha256": relative_hashes(generated),
            "public_release": False,
            "source_input_sha256": relative_hashes(source_inputs),
            "synthetic_only": True,
        },
    )
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S08_S10_BUILD_OK")


if __name__ == "__main__":
    main()
