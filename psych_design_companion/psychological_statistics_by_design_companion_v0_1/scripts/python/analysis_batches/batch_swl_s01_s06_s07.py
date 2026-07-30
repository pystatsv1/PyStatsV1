from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy import stats

BATCH_ID = "psych-design-swl-s01-s06-s07-v0.1"
BASELINE_SOURCE_COMMIT = "da9abc9d5c71779cf794804cce6cfe245980b988"
BOOK_HANDOFF_COMMIT = "954835653734a33f234308fec78282b5dc8feb3d"
ANALYSIS_VERSION = "0.1"
STUDY_IDS = ("SWL-S01", "SWL-S06", "SWL-S07")


def stable_number(value: float | int) -> float | int:
    if isinstance(value, (int, np.integer)):
        return int(value)
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"non-finite result: {value}")
    return float(f"{value:.10g}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _noise(values: list[float], n: int, shift: int = 0) -> np.ndarray:
    base = np.asarray(values, dtype=float)
    return np.roll(np.resize(base, n), shift)


def _ols(y: np.ndarray, x: np.ndarray) -> dict[str, Any]:
    beta = np.linalg.solve(x.T @ x, x.T @ y)
    fitted = x @ beta
    residual = y - fitted
    n, p = x.shape
    df_residual = n - p
    sse = float(residual @ residual)
    sigma2 = sse / df_residual
    xtx_inv = np.linalg.inv(x.T @ x)
    covariance = sigma2 * xtx_inv
    se = np.sqrt(np.diag(covariance))
    t_values = beta / se
    p_values = 2.0 * stats.t.sf(np.abs(t_values), df_residual)
    critical = float(stats.t.ppf(0.975, df_residual))
    ci_low = beta - critical * se
    ci_high = beta + critical * se
    y_centered = y - y.mean()
    sst = float(y_centered @ y_centered)
    r_squared = 1.0 - sse / sst
    df_model = p - 1
    ss_model = sst - sse
    f_value = (ss_model / df_model) / (sse / df_residual)
    f_p = float(stats.f.sf(f_value, df_model, df_residual))
    leverage = np.einsum("ij,jk,ik->i", x, xtx_inv, x)
    standardized = residual / np.sqrt(sigma2 * np.maximum(1e-12, 1.0 - leverage))
    cooks = (standardized**2 * leverage) / (
        p * np.maximum(1e-12, 1.0 - leverage)
    )
    return {
        "beta": beta,
        "se": se,
        "t": t_values,
        "p": p_values,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "fitted": fitted,
        "residual": residual,
        "df_model": df_model,
        "df_residual": df_residual,
        "r_squared": r_squared,
        "adjusted_r_squared": 1.0 - (1.0 - r_squared) * (n - 1) / df_residual,
        "model_f": f_value,
        "model_p": f_p,
        "rmse": math.sqrt(sse / df_residual),
        "leverage": leverage,
        "standardized_residual": standardized,
        "cooks_distance": cooks,
    }


def generate_swl_s01() -> pd.DataFrame:
    n = 120
    index = np.arange(n, dtype=float)
    sleep = (
        50
        + _noise([-12, -9, -7, -5, -3, -1, 0, 2, 4, 6, 8, 10], n)
        + 0.28 * np.sin(index * 0.73)
        + 0.12 * np.cos(index * 0.31)
    )
    study_hours = (
        7
        + 0.5 * _noise([-6, -4, -2, 0, 2, 4, 6, 3, -3, 1, -1, 5], n, shift=3)
        + 0.09 * np.sin(index * 0.47)
    )
    anxiety = (
        58
        - 0.28 * sleep
        + _noise([-5, -3, -2, -1, 0, 1, 2, 3, 4, -4, 1, -1], n, shift=5)
        + 0.18 * np.cos(index * 0.41)
    )
    confidence = (
        42
        + 0.48 * sleep
        - 0.16 * anxiety
        + _noise([-4, -3, -2, -1, 0, 1, 2, 3, 4, -2, 1, -1], n, shift=7)
        + 0.22 * np.sin(index * 0.29)
    )
    performance = (
        28
        + 2.1 * study_hours
        + 0.58 * confidence
        - 0.20 * anxiety
        + _noise([-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 1, -2, 2, -4, 4], n, shift=2)
        + 0.25 * np.cos(index * 0.37)
    )
    return pd.DataFrame(
        {
            "study_id": "SWL-S01",
            "participant_id": [f"S01-{index + 1:03d}" for index in range(n)],
            "sleep_quality": np.round(sleep, 2),
            "study_hours_per_week": np.round(study_hours, 2),
            "anxiety_score": np.round(anxiety, 2),
            "academic_confidence": np.round(confidence, 2),
            "assessment_performance": np.round(performance, 2),
        }
    )


def analyze_swl_s01(df: pd.DataFrame) -> dict[str, float | int]:
    sleep = df["sleep_quality"].to_numpy(dtype=float)
    confidence = df["academic_confidence"].to_numpy(dtype=float)
    correlation = stats.pearsonr(sleep, confidence)
    n = len(df)
    r = float(correlation.statistic)
    correlation_t = r * math.sqrt((n - 2) / (1.0 - r**2))
    fisher_se = 1.0 / math.sqrt(n - 3)
    fisher_z = math.atanh(r)
    fisher_critical = float(stats.norm.ppf(0.975))
    correlation_ci_low = math.tanh(fisher_z - fisher_critical * fisher_se)
    correlation_ci_high = math.tanh(fisher_z + fisher_critical * fisher_se)

    y = df["assessment_performance"].to_numpy(dtype=float)
    x = np.column_stack(
        [
            np.ones(n),
            df["study_hours_per_week"].to_numpy(dtype=float),
            confidence,
        ]
    )
    model = _ols(y, x)
    beta = model["beta"]
    se = model["se"]
    t_values = model["t"]
    p_values = model["p"]
    ci_low = model["ci_low"]
    ci_high = model["ci_high"]
    cooks = model["cooks_distance"]
    standardized = model["standardized_residual"]
    values: dict[str, float | int] = {
        "n": n,
        "correlation_r_sleep_confidence": r,
        "correlation_t": correlation_t,
        "correlation_df": n - 2,
        "correlation_p_two_sided": float(correlation.pvalue),
        "correlation_ci_95_low": correlation_ci_low,
        "correlation_ci_95_high": correlation_ci_high,
        "regression_df_model": model["df_model"],
        "regression_df_residual": model["df_residual"],
        "regression_f": model["model_f"],
        "regression_p": model["model_p"],
        "regression_r_squared": model["r_squared"],
        "regression_adjusted_r_squared": model["adjusted_r_squared"],
        "regression_rmse": model["rmse"],
        "intercept_b": beta[0],
        "intercept_se": se[0],
        "intercept_t": t_values[0],
        "intercept_p": p_values[0],
        "intercept_ci_95_low": ci_low[0],
        "intercept_ci_95_high": ci_high[0],
        "study_hours_b": beta[1],
        "study_hours_se": se[1],
        "study_hours_t": t_values[1],
        "study_hours_p": p_values[1],
        "study_hours_ci_95_low": ci_low[1],
        "study_hours_ci_95_high": ci_high[1],
        "confidence_b": beta[2],
        "confidence_se": se[2],
        "confidence_t": t_values[2],
        "confidence_p": p_values[2],
        "confidence_ci_95_low": ci_low[2],
        "confidence_ci_95_high": ci_high[2],
        "sleep_quality_min": sleep.min(),
        "sleep_quality_max": sleep.max(),
        "study_hours_min": df["study_hours_per_week"].min(),
        "study_hours_max": df["study_hours_per_week"].max(),
        "academic_confidence_min": confidence.min(),
        "academic_confidence_max": confidence.max(),
        "max_abs_standardized_residual": np.max(np.abs(standardized)),
        "max_cooks_distance": np.max(cooks),
        "cooks_distance_above_4_over_n": int(np.sum(cooks > 4.0 / n)),
    }
    return {key: stable_number(value) for key, value in values.items()}


def generate_swl_s06() -> pd.DataFrame:
    n = 60
    index = np.arange(n, dtype=float)
    baseline = (
        50
        + _noise([-7, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5], n)
        + 0.18 * np.sin(index * 0.43)
    )
    post = baseline + 4 + _noise(
        [-2, -1, 0, 1, 2, 1, -1, 0, 2, -2, 1, -1], n, shift=4
    ) + 0.16 * np.cos(index * 0.39)
    follow_up = baseline + 6 + _noise(
        [-3, -2, -1, 0, 1, 2, 3, 1, -1, 2, -2, 0], n, shift=7
    ) + 0.14 * np.sin(index * 0.33)
    post[[4, 16, 40]] = np.nan
    follow_up[[8, 27, 53]] = np.nan
    rows: list[dict[str, Any]] = []
    for index in range(n):
        participant_id = f"S06-{index + 1:03d}"
        for occasion, value in (
            ("baseline", baseline[index]),
            ("post", post[index]),
            ("follow_up", follow_up[index]),
        ):
            rows.append(
                {
                    "study_id": "SWL-S06",
                    "participant_id": participant_id,
                    "occasion": occasion,
                    "academic_confidence": None
                    if np.isnan(value)
                    else round(float(value), 2),
                }
            )
    return pd.DataFrame(rows)


def analyze_swl_s06(df: pd.DataFrame) -> dict[str, float | int]:
    wide = df.pivot(
        index="participant_id",
        columns="occasion",
        values="academic_confidence",
    ).sort_index()
    wide = wide[["baseline", "post", "follow_up"]]
    complete = wide.dropna()
    y = complete.to_numpy(dtype=float)
    n, k = y.shape
    grand_mean = float(y.mean())
    subject_means = y.mean(axis=1)
    occasion_means = y.mean(axis=0)
    ss_total = float(np.square(y - grand_mean).sum())
    ss_subjects = float(k * np.square(subject_means - grand_mean).sum())
    ss_within = ss_total - ss_subjects
    ss_occasion = float(n * np.square(occasion_means - grand_mean).sum())
    ss_error = ss_within - ss_occasion
    df_occasion = k - 1
    df_error = (n - 1) * (k - 1)
    f_value = (ss_occasion / df_occasion) / (ss_error / df_error)
    p_value = float(stats.f.sf(f_value, df_occasion, df_error))
    covariance = np.cov(y, rowvar=False, ddof=1)
    centering = np.eye(k) - np.ones((k, k)) / k
    transformed = centering @ covariance @ centering
    trace = float(np.trace(transformed))
    epsilon = trace**2 / ((k - 1) * float(np.trace(transformed @ transformed)))
    epsilon = max(1.0 / (k - 1), min(1.0, epsilon))
    gg_df_occasion = epsilon * df_occasion
    gg_df_error = epsilon * df_error
    gg_p = float(stats.f.sf(f_value, gg_df_occasion, gg_df_error))
    missing_by_occasion = wide.isna().sum()
    values: dict[str, float | int] = {
        "n_scheduled_participants": len(wide),
        "scheduled_rows": len(wide) * k,
        "observed_outcomes": int(wide.notna().sum().sum()),
        "missing_outcomes": int(wide.isna().sum().sum()),
        "missing_baseline": int(missing_by_occasion["baseline"]),
        "missing_post": int(missing_by_occasion["post"]),
        "missing_follow_up": int(missing_by_occasion["follow_up"]),
        "n_complete_case": n,
        "n_incomplete_participants": len(wide) - n,
        "mean_baseline_complete_case": occasion_means[0],
        "mean_post_complete_case": occasion_means[1],
        "mean_follow_up_complete_case": occasion_means[2],
        "mean_change_post_minus_baseline": occasion_means[1] - occasion_means[0],
        "mean_change_follow_up_minus_baseline": occasion_means[2] - occasion_means[0],
        "rm_anova_f": f_value,
        "rm_anova_df_occasion": df_occasion,
        "rm_anova_df_error": df_error,
        "rm_anova_p": p_value,
        "greenhouse_geisser_epsilon": epsilon,
        "greenhouse_geisser_df_occasion": gg_df_occasion,
        "greenhouse_geisser_df_error": gg_df_error,
        "greenhouse_geisser_p": gg_p,
        "partial_eta_squared": ss_occasion / (ss_occasion + ss_error),
    }
    return {key: stable_number(value) for key, value in values.items()}


def generate_swl_s07() -> pd.DataFrame:
    n_per_group = 45
    base_pattern = [-8, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7]
    index = np.arange(n_per_group, dtype=float)
    baseline_control = 49 + _noise(base_pattern, n_per_group) + 0.22 * np.sin(index * 0.51)
    baseline_treatment = 52 + _noise(base_pattern, n_per_group, shift=4) + 0.19 * np.cos(index * 0.47)
    error_pattern = [-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 1, -2, 2, -4]
    post_control = 24 + 0.72 * baseline_control + _noise(
        error_pattern, n_per_group, shift=1
    ) + 0.20 * np.cos(index * 0.37)
    post_treatment = 24 + 0.72 * baseline_treatment + 5.5 + _noise(
        error_pattern, n_per_group, shift=6
    ) + 0.18 * np.sin(index * 0.41)
    rows: list[dict[str, Any]] = []
    for index in range(n_per_group):
        rows.append(
            {
                "study_id": "SWL-S07",
                "participant_id": f"S07-{index + 1:03d}",
                "intervention_group": "comparison",
                "baseline_performance": round(float(baseline_control[index]), 2),
                "post_performance": round(float(post_control[index]), 2),
            }
        )
    for index in range(n_per_group):
        rows.append(
            {
                "study_id": "SWL-S07",
                "participant_id": f"S07-{n_per_group + index + 1:03d}",
                "intervention_group": "intervention",
                "baseline_performance": round(float(baseline_treatment[index]), 2),
                "post_performance": round(float(post_treatment[index]), 2),
            }
        )
    return pd.DataFrame(rows)


def analyze_swl_s07(df: pd.DataFrame) -> dict[str, float | int]:
    n = len(df)
    treatment = (df["intervention_group"] == "intervention").astype(float).to_numpy()
    baseline = df["baseline_performance"].to_numpy(dtype=float)
    post = df["post_performance"].to_numpy(dtype=float)
    baseline_mean = float(baseline.mean())
    centered = baseline - baseline_mean
    x = np.column_stack([np.ones(n), treatment, centered])
    model = _ols(post, x)
    beta = model["beta"]
    se = model["se"]
    t_values = model["t"]
    p_values = model["p"]
    ci_low = model["ci_low"]
    ci_high = model["ci_high"]
    interaction_x = np.column_stack(
        [np.ones(n), treatment, centered, treatment * centered]
    )
    interaction_model = _ols(post, interaction_x)
    group_f = float(t_values[1] ** 2)
    df_error = int(model["df_residual"])
    control_mask = treatment == 0
    intervention_mask = treatment == 1
    values: dict[str, float | int] = {
        "n_total": n,
        "n_comparison": int(control_mask.sum()),
        "n_intervention": int(intervention_mask.sum()),
        "baseline_overall_mean": baseline_mean,
        "raw_baseline_mean_comparison": baseline[control_mask].mean(),
        "raw_baseline_mean_intervention": baseline[intervention_mask].mean(),
        "raw_post_mean_comparison": post[control_mask].mean(),
        "raw_post_mean_intervention": post[intervention_mask].mean(),
        "adjusted_mean_comparison_at_overall_baseline": beta[0],
        "adjusted_mean_intervention_at_overall_baseline": beta[0] + beta[1],
        "adjusted_group_difference_intervention_minus_comparison": beta[1],
        "group_effect_se": se[1],
        "group_effect_t": t_values[1],
        "group_effect_p": p_values[1],
        "group_effect_ci_95_low": ci_low[1],
        "group_effect_ci_95_high": ci_high[1],
        "group_effect_f": group_f,
        "group_effect_df": 1,
        "model_df_error": df_error,
        "group_partial_eta_squared": group_f / (group_f + df_error),
        "baseline_slope": beta[2],
        "baseline_slope_se": se[2],
        "baseline_slope_t": t_values[2],
        "baseline_slope_p": p_values[2],
        "baseline_slope_ci_95_low": ci_low[2],
        "baseline_slope_ci_95_high": ci_high[2],
        "model_r_squared": model["r_squared"],
        "model_adjusted_r_squared": model["adjusted_r_squared"],
        "homogeneity_interaction_b": interaction_model["beta"][3],
        "homogeneity_interaction_se": interaction_model["se"][3],
        "homogeneity_interaction_t": interaction_model["t"][3],
        "homogeneity_interaction_p": interaction_model["p"][3],
    }
    return {key: stable_number(value) for key, value in values.items()}


GENERATORS: dict[str, Callable[[], pd.DataFrame]] = {
    "SWL-S01": generate_swl_s01,
    "SWL-S06": generate_swl_s06,
    "SWL-S07": generate_swl_s07,
}
ANALYZERS: dict[str, Callable[[pd.DataFrame], dict[str, float | int]]] = {
    "SWL-S01": analyze_swl_s01,
    "SWL-S06": analyze_swl_s06,
    "SWL-S07": analyze_swl_s07,
}

STUDY_CONFIG: dict[str, dict[str, Any]] = {
    "SWL-S01": {
        "slug": "swl_s01_student_well_being_survey",
        "chapter_ids": ["ch11", "ch12"],
        "short_name": "Student Well-Being Survey",
        "research_questions": [
            "How are sleep quality and academic confidence associated in the synthetic survey records?",
            "How well do weekly study hours and academic confidence predict synthetic assessment performance within the registered predictor domain?",
        ],
        "design": "Cross-sectional synthetic survey with one row per participant.",
        "unit_of_analysis": "student",
        "row_structure": "One row per synthetic participant.",
        "identifier_fields": ["participant_id"],
        "outcomes": ["academic_confidence", "assessment_performance"],
        "predictors": ["sleep_quality", "study_hours_per_week", "academic_confidence"],
        "missingness_rule": "No missing values in the registered synthetic dataset.",
        "causal_scope": "Association and within-domain prediction only; no intervention or causal claim is authorized.",
        "limitations": {
            "correlation": "The cross-sectional synthetic association does not establish temporal order, rule out common causes, or support the claim that changing sleep would change confidence.",
            "regression": "Predictive performance is registered only for the generated records and observed predictor ranges; the model does not authorize extrapolation, causal interpretation, or performance claims for real students.",
        },
        "figure_types": ["correlation_scatter", "regression_residual_diagnostic"],
        "apa_field_sets": {
            "correlation": [
                "n",
                "correlation_r_sleep_confidence",
                "correlation_df",
                "correlation_p_two_sided",
                "correlation_ci_95_low",
                "correlation_ci_95_high",
            ],
            "regression": [
                "n",
                "regression_f",
                "regression_df_model",
                "regression_df_residual",
                "regression_p",
                "regression_r_squared",
                "study_hours_b",
                "study_hours_se",
                "study_hours_t",
                "study_hours_p",
                "confidence_b",
                "confidence_se",
                "confidence_t",
                "confidence_p",
            ],
        },
    },
    "SWL-S06": {
        "slug": "swl_s06_confidence_trajectory",
        "chapter_ids": ["ch10"],
        "short_name": "Confidence Trajectory Study",
        "research_questions": [
            "Does mean academic confidence differ across baseline, post, and follow-up among complete synthetic trajectories?"
        ],
        "design": "Three-occasion repeated-measures study with six scheduled outcomes missing.",
        "unit_of_analysis": "student",
        "row_structure": "Three scheduled participant-occasion rows per student.",
        "identifier_fields": ["participant_id", "occasion"],
        "factor_levels": {"occasion": ["baseline", "post", "follow_up"]},
        "outcomes": ["academic_confidence"],
        "missingness_rule": "The registered repeated-measures ANOVA uses complete trajectories and separately reports all missing visits.",
        "causal_scope": "Occasion differences are descriptive/inferential within the registered synthetic schedule and do not identify a unique cause.",
        "limitations": {
            "primary": "The complete-case repeated-measures analysis excludes six participants with a missing scheduled outcome and can be biased when missingness is informative; a mixed model is required for the later incomplete-longitudinal workflow."
        },
        "figure_types": ["complete_case_trajectory"],
        "apa_field_sets": {
            "primary": [
                "n_complete_case",
                "mean_baseline_complete_case",
                "mean_post_complete_case",
                "mean_follow_up_complete_case",
                "rm_anova_f",
                "rm_anova_df_occasion",
                "rm_anova_df_error",
                "greenhouse_geisser_epsilon",
                "greenhouse_geisser_df_occasion",
                "greenhouse_geisser_df_error",
                "greenhouse_geisser_p",
                "partial_eta_squared",
            ]
        },
    },
    "SWL-S07": {
        "slug": "swl_s07_baseline_adjusted_intervention",
        "chapter_ids": ["ch13"],
        "short_name": "Baseline-Adjusted Intervention",
        "research_questions": [
            "Do the intervention and comparison groups differ in post performance after adjustment to the overall baseline mean?"
        ],
        "design": "Two-group synthetic intervention study with one pre-treatment baseline covariate.",
        "unit_of_analysis": "student",
        "row_structure": "One row per synthetic participant.",
        "identifier_fields": ["participant_id"],
        "factor_levels": {"intervention_group": ["comparison", "intervention"]},
        "outcomes": ["post_performance"],
        "predictors": ["intervention_group", "baseline_performance"],
        "missingness_rule": "No missing values in the registered synthetic dataset.",
        "causal_scope": "Causal language remains conditional on the declared assignment and intervention implementation; adjustment alone does not create randomization.",
        "limitations": {
            "primary": "The adjusted comparison depends on linearity, reliable pre-treatment measurement, and sufficiently homogeneous covariate slopes; baseline adjustment does not repair unmeasured confounding or support generalization beyond the synthetic implementation."
        },
        "figure_types": ["ancova_parallel_lines"],
        "apa_field_sets": {
            "primary": [
                "n_total",
                "adjusted_mean_comparison_at_overall_baseline",
                "adjusted_mean_intervention_at_overall_baseline",
                "adjusted_group_difference_intervention_minus_comparison",
                "group_effect_f",
                "group_effect_df",
                "model_df_error",
                "group_effect_p",
                "group_partial_eta_squared",
                "homogeneity_interaction_p",
            ]
        },
    },
}


def dataset_path(root: Path, study_id: str) -> Path:
    return root / "data" / f"{STUDY_CONFIG[study_id]['slug']}.csv"


def validate_dataset(study_id: str, frame: pd.DataFrame) -> None:
    if set(frame["study_id"].unique()) != {study_id}:
        raise ValueError(f"study ID drift: {study_id}")
    if study_id == "SWL-S01":
        if len(frame) != 120 or frame["participant_id"].nunique() != 120:
            raise ValueError("SWL-S01 row or participant count")
        if frame.isna().any().any():
            raise ValueError("SWL-S01 missing values")
    elif study_id == "SWL-S06":
        if len(frame) != 180 or frame["participant_id"].nunique() != 60:
            raise ValueError("SWL-S06 row or participant count")
        if frame.duplicated(["participant_id", "occasion"]).any():
            raise ValueError("SWL-S06 duplicate participant-occasion key")
        if set(frame["occasion"].unique()) != {"baseline", "post", "follow_up"}:
            raise ValueError("SWL-S06 occasion levels")
        if int(frame["academic_confidence"].isna().sum()) != 6:
            raise ValueError("SWL-S06 missing-visit count")
    elif study_id == "SWL-S07":
        if len(frame) != 90 or frame["participant_id"].nunique() != 90:
            raise ValueError("SWL-S07 row or participant count")
        counts = frame["intervention_group"].value_counts().to_dict()
        if counts != {"comparison": 45, "intervention": 45}:
            raise ValueError("SWL-S07 group counts")
        if frame.isna().any().any():
            raise ValueError("SWL-S07 missing values")
    else:
        raise ValueError(f"unknown study: {study_id}")


def result_receipt(root: Path, study_id: str, frame: pd.DataFrame) -> dict[str, Any]:
    dataset = dataset_path(root, study_id)
    contract = root / "contracts" / f"{study_id}_DESIGN_CONTRACT.json"
    return {
        "analysis_version": ANALYSIS_VERSION,
        "batch_id": BATCH_ID,
        "contract_version": "0.1",
        "dataset_sha256": sha256(dataset),
        "design_contract_sha256": sha256(contract),
        "python_analysis_sha256": sha256(Path(__file__)),
        "reported_fields": ANALYZERS[study_id](frame),
        "study_id": study_id,
        "synthetic_only": True,
    }


def design_contract(study_id: str) -> dict[str, Any]:
    config = STUDY_CONFIG[study_id]
    return {
        "analysis_version": ANALYSIS_VERSION,
        "batch_id": BATCH_ID,
        "causal_scope": config["causal_scope"],
        "chapter_ids": config["chapter_ids"],
        "contract_version": "0.1",
        "design": config["design"],
        "identifier_fields": config["identifier_fields"],
        "missingness_rule": config["missingness_rule"],
        "real_data_authorized": False,
        "research_questions": config["research_questions"],
        "row_structure": config["row_structure"],
        "short_name": config["short_name"],
        "study_id": study_id,
        "synthetic_only": True,
        "unit_of_analysis": config["unit_of_analysis"],
        **({"factor_levels": config["factor_levels"]} if "factor_levels" in config else {}),
        **({"outcomes": config["outcomes"]} if "outcomes" in config else {}),
        **({"predictors": config["predictors"]} if "predictors" in config else {}),
    }


def figure_specs(study_id: str) -> list[tuple[str, dict[str, Any]]]:
    config = STUDY_CONFIG[study_id]
    result: list[tuple[str, dict[str, Any]]] = []
    for figure_type in config["figure_types"]:
        role = {
            "correlation_scatter": "correlation",
            "regression_residual_diagnostic": "regression",
            "complete_case_trajectory": "primary",
            "ancova_parallel_lines": "primary",
        }[figure_type]
        suffix = role.upper()
        result.append(
            (
                f"FIGURE_SPEC_{suffix}.json" if study_id == "SWL-S01" else "FIGURE_SPEC.json",
                {
                    "batch_id": BATCH_ID,
                    "chapter_ids": config["chapter_ids"],
                    "contract_version": "0.1",
                    "figure_role": role,
                    "figure_type": figure_type,
                    "generator": "scripts/python/generate_figures.py",
                    "grayscale": True,
                    "result_source": f"evidence/{study_id}/PYTHON_RESULT_RECEIPT.json",
                    "study_id": study_id,
                    "synthetic_only": True,
                },
            )
        )
    return result


def apa_maps(study_id: str) -> list[tuple[str, dict[str, Any]]]:
    config = STUDY_CONFIG[study_id]
    result: list[tuple[str, dict[str, Any]]] = []
    for role, fields in config["apa_field_sets"].items():
        filename = (
            f"APA_RESULT_SOURCE_MAP_{role.upper()}.json"
            if study_id == "SWL-S01"
            else "APA_RESULT_SOURCE_MAP.json"
        )
        result.append(
            (
                filename,
                {
                    "batch_id": BATCH_ID,
                    "chapter_ids": config["chapter_ids"],
                    "contract_version": "0.1",
                    "reporting_role": role,
                    "reported_number_bindings": [
                        {
                            "field": field,
                            "json_pointer": f"/reported_fields/{field}",
                        }
                        for field in fields
                    ],
                    "result_receipt": f"evidence/{study_id}/PYTHON_RESULT_RECEIPT.json",
                    "study_id": study_id,
                    "synthetic_only": True,
                },
            )
        )
    return result


def limitation_records(study_id: str) -> list[tuple[str, dict[str, Any]]]:
    config = STUDY_CONFIG[study_id]
    result: list[tuple[str, dict[str, Any]]] = []
    for role, text in config["limitations"].items():
        filename = (
            f"MATCHED_LIMITATION_{role.upper()}.json"
            if study_id == "SWL-S01"
            else "MATCHED_LIMITATION.json"
        )
        result.append(
            (
                filename,
                {
                    "batch_id": BATCH_ID,
                    "chapter_ids": config["chapter_ids"],
                    "contract_version": "0.1",
                    "limitation": text,
                    "limitation_role": role,
                    "study_id": study_id,
                    "synthetic_only": True,
                },
            )
        )
    return result


def generate_all(output_root: Path) -> list[Path]:
    generated: list[Path] = []
    output_root.mkdir(parents=True, exist_ok=True)
    for study_id in STUDY_IDS:
        frame = GENERATORS[study_id]()
        validate_dataset(study_id, frame)
        dataset = dataset_path(output_root, study_id)
        dataset.parent.mkdir(parents=True, exist_ok=True)
        csv_text = frame.to_csv(index=False, lineterminator="\n", na_rep="")
        dataset.write_bytes(csv_text.encode("utf-8"))
        generated.append(dataset)
        contract = output_root / "contracts" / f"{study_id}_DESIGN_CONTRACT.json"
        write_json(contract, design_contract(study_id))
        generated.append(contract)
        receipt = output_root / "evidence" / study_id / "PYTHON_RESULT_RECEIPT.json"
        write_json(receipt, result_receipt(output_root, study_id, frame))
        generated.append(receipt)
        for filename, payload in figure_specs(study_id):
            path = output_root / "evidence" / study_id / filename
            write_json(path, payload)
            generated.append(path)
        for filename, payload in apa_maps(study_id):
            path = output_root / "evidence" / study_id / filename
            write_json(path, payload)
            generated.append(path)
        for filename, payload in limitation_records(study_id):
            path = output_root / "evidence" / study_id / filename
            write_json(path, payload)
            generated.append(path)
    return generated
