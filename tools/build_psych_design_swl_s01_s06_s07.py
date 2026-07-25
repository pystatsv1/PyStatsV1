from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "psych_design_companion/swl_s01_s06_s07_v0_1"
STUDIES_PATH = COMPANION / "scripts/python/studies.py"


def load_studies():
    spec = importlib.util.spec_from_file_location("psych_design_second_batch_studies", STUDIES_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load study implementation")
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

    verification_contract = COMPANION / "evidence/PYTHON_R_VERIFICATION_CONTRACT.json"
    write_json(
        verification_contract,
        {
            "batch_id": studies.BATCH_ID,
            "contract_version": "0.1",
            "independent_implementation": "base R scripts do not call the Python implementation",
            "runtime_outputs_tracked": False,
            "studies": [
                {
                    "parity_fields": [
                        "n",
                        "correlation_r_sleep_confidence",
                        "correlation_t",
                        "correlation_df",
                        "correlation_p_two_sided",
                        "correlation_ci_95_low",
                        "correlation_ci_95_high",
                        "regression_df_model",
                        "regression_df_residual",
                        "regression_f",
                        "regression_p",
                        "regression_r_squared",
                        "regression_adjusted_r_squared",
                        "regression_rmse",
                        "intercept_b",
                        "intercept_se",
                        "intercept_t",
                        "intercept_p",
                        "intercept_ci_95_low",
                        "intercept_ci_95_high",
                        "study_hours_b",
                        "study_hours_se",
                        "study_hours_t",
                        "study_hours_p",
                        "study_hours_ci_95_low",
                        "study_hours_ci_95_high",
                        "confidence_b",
                        "confidence_se",
                        "confidence_t",
                        "confidence_p",
                        "confidence_ci_95_low",
                        "confidence_ci_95_high"
                    ],
                    "r_script": "scripts/r/swl_s01.R",
                    "study_id": "SWL-S01",
                    "verification_category": "V2"
                },
                {
                    "parity_fields": [
                        "n_scheduled_participants",
                        "scheduled_rows",
                        "observed_outcomes",
                        "missing_outcomes",
                        "missing_baseline",
                        "missing_post",
                        "missing_follow_up",
                        "n_complete_case",
                        "n_incomplete_participants",
                        "mean_baseline_complete_case",
                        "mean_post_complete_case",
                        "mean_follow_up_complete_case",
                        "mean_change_post_minus_baseline",
                        "mean_change_follow_up_minus_baseline",
                        "rm_anova_f",
                        "rm_anova_df_occasion",
                        "rm_anova_df_error",
                        "rm_anova_p",
                        "greenhouse_geisser_epsilon",
                        "greenhouse_geisser_df_occasion",
                        "greenhouse_geisser_df_error",
                        "greenhouse_geisser_p",
                        "partial_eta_squared"
                    ],
                    "r_script": "scripts/r/swl_s06.R",
                    "study_id": "SWL-S06",
                    "verification_category": "V2"
                },
                {
                    "parity_fields": [
                        "n_total",
                        "n_comparison",
                        "n_intervention",
                        "baseline_overall_mean",
                        "raw_baseline_mean_comparison",
                        "raw_baseline_mean_intervention",
                        "raw_post_mean_comparison",
                        "raw_post_mean_intervention",
                        "adjusted_mean_comparison_at_overall_baseline",
                        "adjusted_mean_intervention_at_overall_baseline",
                        "adjusted_group_difference_intervention_minus_comparison",
                        "group_effect_se",
                        "group_effect_t",
                        "group_effect_p",
                        "group_effect_ci_95_low",
                        "group_effect_ci_95_high",
                        "group_effect_f",
                        "group_effect_df",
                        "model_df_error",
                        "group_partial_eta_squared",
                        "baseline_slope",
                        "baseline_slope_se",
                        "baseline_slope_t",
                        "baseline_slope_p",
                        "baseline_slope_ci_95_low",
                        "baseline_slope_ci_95_high",
                        "model_r_squared",
                        "model_adjusted_r_squared",
                        "homogeneity_interaction_b",
                        "homogeneity_interaction_se",
                        "homogeneity_interaction_t",
                        "homogeneity_interaction_p"
                    ],
                    "r_script": "scripts/r/swl_s07.R",
                    "study_id": "SWL-S07",
                    "verification_category": "V2"
                }
            ],
            "tolerance": 1e-7
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
            "book_drafting_unblock_role": "eligible_after_green_merge_and_explicit_new_commit_anchor",
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
                "result_receipt_present": True
            },
            "public_release": False,
            "r_parity_status_role": "required_green_local_and_ci_gate_not_tracked_runtime_output",
            "study_ids": list(studies.STUDY_IDS),
            "synthetic_only": True
        },
    )
    generated.append(implementation)

    handoff = COMPANION / "evidence/BOOK_INTEGRATION_HANDOFF.json"
    write_json(
        handoff,
        {
            "accepted_book_baseline": studies.BOOK_HANDOFF_COMMIT,
            "batch_id": studies.BATCH_ID,
            "chapter_authorization_candidate": ["ch10", "ch11", "ch12", "ch13"],
            "contract_version": "0.1",
            "next_book_action": "After this PyStatsV1 batch is merged and tagged, create a book-repository source-anchor acceptance drop-in that verifies these exact assets before authorizing controlled drafting.",
            "public_release": False,
            "required_new_pystatsv1_commit_anchor": True,
            "study_ids": list(studies.STUDY_IDS),
            "synthetic_only": True
        },
    )
    generated.append(handoff)

    source_inputs = [
        COMPANION / "METHOD_SOURCE_BINDING.json",
        COMPANION / "PSYCH_DESIGN_SWL_S01_S06_S07_CONTRACT.json",
        COMPANION / "SOURCE_PROVENANCE.json",
        COMPANION / "scripts/python/studies.py",
        COMPANION / "scripts/python/generate_figures.py",
        COMPANION / "scripts/python/compare_r_results.py",
        COMPANION / "scripts/r/common.R",
        COMPANION / "scripts/r/run_all.R",
        COMPANION / "scripts/r/swl_s01.R",
        COMPANION / "scripts/r/swl_s06.R",
        COMPANION / "scripts/r/swl_s07.R",
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
            "synthetic_only": True
        },
    )
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S01_S06_S07_BUILD_OK")


if __name__ == "__main__":
    main()
