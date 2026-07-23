from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy import stats

BATCH_ID = "psych-design-swl-s02-s05-v0.1"
BASELINE_SOURCE_COMMIT = "621b1eb4a534f4dfedb0647b7e0853a7fd9b8a90"
BOOK_HANDOFF_COMMIT = "0bb3db0c53dd3bb7ad18adc682a3fe1d39de5df0"
ANALYSIS_VERSION = "0.1"
STUDY_IDS = ("SWL-S02", "SWL-S03", "SWL-S04", "SWL-S05")


def stable_number(value: float | int) -> float | int:
    if isinstance(value, int):
        return value
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"non-finite result: {value}")
    return float(f"{value:.10g}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _noise(values: list[int], n: int, shift: int = 0) -> np.ndarray:
    base = np.asarray(values, dtype=float)
    resized = np.resize(base, n)
    return np.roll(resized, shift)


def generate_swl_s02() -> pd.DataFrame:
    n_per_group = 32
    base_noise = [-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 1, -2, 2, -4, 4]
    rows: list[dict[str, Any]] = []
    for index in range(n_per_group):
        rows.append(
            {
                "study_id": "SWL-S02",
                "participant_id": f"S02-{index + 1:03d}",
                "study_routine_group": "standard_routine",
                "post_session_performance": int(68 + _noise(base_noise, n_per_group)[index]),
            }
        )
    for index in range(n_per_group):
        rows.append(
            {
                "study_id": "SWL-S02",
                "participant_id": f"S02-{n_per_group + index + 1:03d}",
                "study_routine_group": "structured_routine",
                "post_session_performance": int(
                    74 + _noise(base_noise, n_per_group, shift=5)[index]
                ),
            }
        )
    return pd.DataFrame(rows)


def analyze_swl_s02(df: pd.DataFrame) -> dict[str, float | int]:
    standard = df.loc[
        df["study_routine_group"] == "standard_routine",
        "post_session_performance",
    ].to_numpy(dtype=float)
    structured = df.loc[
        df["study_routine_group"] == "structured_routine",
        "post_session_performance",
    ].to_numpy(dtype=float)
    test = stats.ttest_ind(structured, standard, equal_var=False)
    mean_difference = float(structured.mean() - standard.mean())
    variance_a = float(structured.var(ddof=1))
    variance_b = float(standard.var(ddof=1))
    se = math.sqrt(variance_a / len(structured) + variance_b / len(standard))
    df_welch = float(test.df)
    critical = float(stats.t.ppf(0.975, df_welch))
    pooled_sd = math.sqrt(
        (
            (len(structured) - 1) * variance_a
            + (len(standard) - 1) * variance_b
        )
        / (len(structured) + len(standard) - 2)
    )
    values: dict[str, float | int] = {
        "n_standard": len(standard),
        "n_structured": len(structured),
        "mean_standard": standard.mean(),
        "mean_structured": structured.mean(),
        "sd_standard": standard.std(ddof=1),
        "sd_structured": structured.std(ddof=1),
        "mean_difference_structured_minus_standard": mean_difference,
        "welch_t": float(test.statistic),
        "welch_df": df_welch,
        "p_value_two_sided": float(test.pvalue),
        "ci_95_low": mean_difference - critical * se,
        "ci_95_high": mean_difference + critical * se,
        "cohen_d_pooled": mean_difference / pooled_sd,
    }
    return {key: stable_number(value) for key, value in values.items()}


def generate_swl_s03() -> pd.DataFrame:
    n = 48
    pre_noise = [-8, -6, -5, -3, -2, -1, 0, 1, 2, 3, 5, 7]
    change_noise = [-5, -3, -2, -1, 0, 1, 2, 3, 4, 5, -4, 2]
    pre = 55 + _noise(pre_noise, n)
    change = 4 + _noise(change_noise, n)
    rows: list[dict[str, Any]] = []
    for index in range(n):
        participant_id = f"S03-{index + 1:03d}"
        rows.append(
            {
                "study_id": "SWL-S03",
                "participant_id": participant_id,
                "occasion": "pre",
                "academic_confidence": int(pre[index]),
            }
        )
        rows.append(
            {
                "study_id": "SWL-S03",
                "participant_id": participant_id,
                "occasion": "post",
                "academic_confidence": int(pre[index] + change[index]),
            }
        )
    return pd.DataFrame(rows)


def analyze_swl_s03(df: pd.DataFrame) -> dict[str, float | int]:
    wide = df.pivot(
        index="participant_id",
        columns="occasion",
        values="academic_confidence",
    ).sort_index()
    pre = wide["pre"].to_numpy(dtype=float)
    post = wide["post"].to_numpy(dtype=float)
    differences = post - pre
    test = stats.ttest_rel(post, pre)
    n = len(differences)
    mean_change = float(differences.mean())
    sd_change = float(differences.std(ddof=1))
    se = sd_change / math.sqrt(n)
    critical = float(stats.t.ppf(0.975, n - 1))
    values: dict[str, float | int] = {
        "n_paired": n,
        "mean_pre": pre.mean(),
        "mean_post": post.mean(),
        "mean_change_post_minus_pre": mean_change,
        "sd_change": sd_change,
        "paired_t": float(test.statistic),
        "df": n - 1,
        "p_value_two_sided": float(test.pvalue),
        "ci_95_low": mean_change - critical * se,
        "ci_95_high": mean_change + critical * se,
        "cohen_dz": mean_change / sd_change,
    }
    return {key: stable_number(value) for key, value in values.items()}


def generate_swl_s04() -> pd.DataFrame:
    n_per_condition = 30
    base_noise = [-7, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, -2, 2]
    conditions = (
        ("standard_support", 67, 0),
        ("guided_practice", 72, 4),
        ("guided_practice_plus_feedback", 78, 8),
    )
    rows: list[dict[str, Any]] = []
    next_id = 1
    for condition, mean, shift in conditions:
        condition_noise = _noise(base_noise, n_per_condition, shift=shift)
        for index in range(n_per_condition):
            rows.append(
                {
                    "study_id": "SWL-S04",
                    "participant_id": f"S04-{next_id:03d}",
                    "support_condition": condition,
                    "assessment_performance": int(mean + condition_noise[index]),
                }
            )
            next_id += 1
    return pd.DataFrame(rows)


def _holm_adjust_two(p_first: float, p_second: float) -> tuple[float, float]:
    indexed = sorted(enumerate((p_first, p_second)), key=lambda pair: pair[1])
    adjusted = [0.0, 0.0]
    first_index, first_value = indexed[0]
    second_index, second_value = indexed[1]
    adjusted[first_index] = min(1.0, 2.0 * first_value)
    adjusted[second_index] = max(adjusted[first_index], min(1.0, second_value))
    return adjusted[0], adjusted[1]


def analyze_swl_s04(df: pd.DataFrame) -> dict[str, float | int]:
    levels = (
        "standard_support",
        "guided_practice",
        "guided_practice_plus_feedback",
    )
    arrays = {
        level: df.loc[
            df["support_condition"] == level,
            "assessment_performance",
        ].to_numpy(dtype=float)
        for level in levels
    }
    all_values = np.concatenate([arrays[level] for level in levels])
    grand_mean = float(all_values.mean())
    group_means = {level: float(arrays[level].mean()) for level in levels}
    ss_between = sum(
        len(arrays[level]) * (group_means[level] - grand_mean) ** 2
        for level in levels
    )
    ss_within = sum(
        float(np.square(arrays[level] - group_means[level]).sum())
        for level in levels
    )
    df_between = len(levels) - 1
    df_within = len(all_values) - len(levels)
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    f_value = ms_between / ms_within
    p_value = float(stats.f.sf(f_value, df_between, df_within))

    contrasts = (
        (
            "guided_average_minus_standard",
            {
                "standard_support": -1.0,
                "guided_practice": 0.5,
                "guided_practice_plus_feedback": 0.5,
            },
        ),
        (
            "feedback_increment_within_guided",
            {
                "standard_support": 0.0,
                "guided_practice": -1.0,
                "guided_practice_plus_feedback": 1.0,
            },
        ),
    )
    contrast_results: list[tuple[str, float, float, float]] = []
    for name, coefficients in contrasts:
        estimate = sum(
            coefficients[level] * group_means[level] for level in levels
        )
        se = math.sqrt(
            ms_within
            * sum(
                coefficients[level] ** 2 / len(arrays[level])
                for level in levels
            )
        )
        t_value = estimate / se
        p_contrast = float(2.0 * stats.t.sf(abs(t_value), df_within))
        contrast_results.append((name, estimate, t_value, p_contrast))
    adjusted = _holm_adjust_two(
        contrast_results[0][3],
        contrast_results[1][3],
    )

    values: dict[str, float | int] = {
        "n_total": len(all_values),
        "n_standard_support": len(arrays["standard_support"]),
        "n_guided_practice": len(arrays["guided_practice"]),
        "n_guided_practice_plus_feedback": len(
            arrays["guided_practice_plus_feedback"]
        ),
        "mean_standard_support": group_means["standard_support"],
        "mean_guided_practice": group_means["guided_practice"],
        "mean_guided_practice_plus_feedback": group_means[
            "guided_practice_plus_feedback"
        ],
        "anova_f": f_value,
        "df_between": df_between,
        "df_within": df_within,
        "p_value": p_value,
        "eta_squared": ss_between / (ss_between + ss_within),
        "contrast_guided_average_minus_standard_estimate": contrast_results[0][1],
        "contrast_guided_average_minus_standard_t": contrast_results[0][2],
        "contrast_guided_average_minus_standard_p": contrast_results[0][3],
        "contrast_guided_average_minus_standard_p_holm": adjusted[0],
        "contrast_feedback_increment_estimate": contrast_results[1][1],
        "contrast_feedback_increment_t": contrast_results[1][2],
        "contrast_feedback_increment_p": contrast_results[1][3],
        "contrast_feedback_increment_p_holm": adjusted[1],
    }
    return {key: stable_number(value) for key, value in values.items()}


def generate_swl_s05() -> pd.DataFrame:
    n_per_cell = 24
    base_noise = [-6, -5, -3, -2, -1, 0, 1, 2, 3, 4, 5, 2, -2, 1, -4, 4]
    cells = (
        ("rereading", "no_feedback", 68, 0),
        ("retrieval_practice", "no_feedback", 72, 3),
        ("rereading", "explanatory_feedback", 70, 6),
        ("retrieval_practice", "explanatory_feedback", 80, 9),
    )
    rows: list[dict[str, Any]] = []
    next_id = 1
    for strategy, feedback, mean, shift in cells:
        cell_noise = _noise(base_noise, n_per_cell, shift=shift)
        for index in range(n_per_cell):
            rows.append(
                {
                    "study_id": "SWL-S05",
                    "participant_id": f"S05-{next_id:03d}",
                    "study_strategy": strategy,
                    "feedback_condition": feedback,
                    "assessment_performance": int(mean + cell_noise[index]),
                }
            )
            next_id += 1
    return pd.DataFrame(rows)


def analyze_swl_s05(df: pd.DataFrame) -> dict[str, float | int]:
    strategies = ("rereading", "retrieval_practice")
    feedback_levels = ("no_feedback", "explanatory_feedback")
    cells = {
        (strategy, feedback): df.loc[
            (df["study_strategy"] == strategy)
            & (df["feedback_condition"] == feedback),
            "assessment_performance",
        ].to_numpy(dtype=float)
        for strategy in strategies
        for feedback in feedback_levels
    }
    cell_sizes = {len(values) for values in cells.values()}
    if len(cell_sizes) != 1:
        raise ValueError("SWL-S05 requires balanced cell sizes")
    n_per_cell = cell_sizes.pop()
    all_values = np.concatenate(list(cells.values()))
    grand_mean = float(all_values.mean())
    cell_means = {key: float(values.mean()) for key, values in cells.items()}
    strategy_means = {
        strategy: np.concatenate(
            [cells[(strategy, feedback)] for feedback in feedback_levels]
        ).mean()
        for strategy in strategies
    }
    feedback_means = {
        feedback: np.concatenate(
            [cells[(strategy, feedback)] for strategy in strategies]
        ).mean()
        for feedback in feedback_levels
    }
    ss_strategy = len(feedback_levels) * n_per_cell * sum(
        (float(strategy_means[strategy]) - grand_mean) ** 2
        for strategy in strategies
    )
    ss_feedback = len(strategies) * n_per_cell * sum(
        (float(feedback_means[feedback]) - grand_mean) ** 2
        for feedback in feedback_levels
    )
    ss_interaction = n_per_cell * sum(
        (
            cell_means[(strategy, feedback)]
            - float(strategy_means[strategy])
            - float(feedback_means[feedback])
            + grand_mean
        )
        ** 2
        for strategy in strategies
        for feedback in feedback_levels
    )
    ss_within = sum(
        float(np.square(values - cell_means[key]).sum())
        for key, values in cells.items()
    )
    df_within = len(all_values) - len(cells)
    ms_within = ss_within / df_within
    f_strategy = ss_strategy / ms_within
    f_feedback = ss_feedback / ms_within
    f_interaction = ss_interaction / ms_within

    simple_results: dict[str, tuple[float, float, float]] = {}
    for feedback in feedback_levels:
        estimate = (
            cell_means[("retrieval_practice", feedback)]
            - cell_means[("rereading", feedback)]
        )
        se = math.sqrt(ms_within * (2.0 / n_per_cell))
        t_value = estimate / se
        p_value = float(2.0 * stats.t.sf(abs(t_value), df_within))
        simple_results[feedback] = (estimate, t_value, p_value)

    interaction_estimate = (
        simple_results["explanatory_feedback"][0]
        - simple_results["no_feedback"][0]
    )
    values: dict[str, float | int] = {
        "n_total": len(all_values),
        "n_per_cell": n_per_cell,
        "mean_rereading_no_feedback": cell_means[("rereading", "no_feedback")],
        "mean_retrieval_no_feedback": cell_means[
            ("retrieval_practice", "no_feedback")
        ],
        "mean_rereading_explanatory_feedback": cell_means[
            ("rereading", "explanatory_feedback")
        ],
        "mean_retrieval_explanatory_feedback": cell_means[
            ("retrieval_practice", "explanatory_feedback")
        ],
        "strategy_f": f_strategy,
        "strategy_p": float(stats.f.sf(f_strategy, 1, df_within)),
        "strategy_partial_eta_squared": ss_strategy / (ss_strategy + ss_within),
        "feedback_f": f_feedback,
        "feedback_p": float(stats.f.sf(f_feedback, 1, df_within)),
        "feedback_partial_eta_squared": ss_feedback / (ss_feedback + ss_within),
        "interaction_f": f_interaction,
        "interaction_p": float(stats.f.sf(f_interaction, 1, df_within)),
        "interaction_partial_eta_squared": ss_interaction
        / (ss_interaction + ss_within),
        "df_effect": 1,
        "df_within": df_within,
        "interaction_difference_in_differences": interaction_estimate,
        "simple_strategy_no_feedback_estimate": simple_results["no_feedback"][0],
        "simple_strategy_no_feedback_t": simple_results["no_feedback"][1],
        "simple_strategy_no_feedback_p": simple_results["no_feedback"][2],
        "simple_strategy_explanatory_feedback_estimate": simple_results[
            "explanatory_feedback"
        ][0],
        "simple_strategy_explanatory_feedback_t": simple_results[
            "explanatory_feedback"
        ][1],
        "simple_strategy_explanatory_feedback_p": simple_results[
            "explanatory_feedback"
        ][2],
    }
    return {key: stable_number(value) for key, value in values.items()}


GENERATORS: dict[str, Callable[[], pd.DataFrame]] = {
    "SWL-S02": generate_swl_s02,
    "SWL-S03": generate_swl_s03,
    "SWL-S04": generate_swl_s04,
    "SWL-S05": generate_swl_s05,
}
ANALYZERS: dict[str, Callable[[pd.DataFrame], dict[str, float | int]]] = {
    "SWL-S02": analyze_swl_s02,
    "SWL-S03": analyze_swl_s03,
    "SWL-S04": analyze_swl_s04,
    "SWL-S05": analyze_swl_s05,
}

STUDY_CONFIG: dict[str, dict[str, Any]] = {
    "SWL-S02": {
        "slug": "swl_s02_structured_study_routine",
        "chapter_id": "ch06",
        "short_name": "Structured Study-Routine Pilot",
        "research_question": (
            "Do students assigned to a structured study routine differ in "
            "post-session performance from students using a standard routine?"
        ),
        "design": "Two-group pilot with declared stratified random assignment.",
        "unit_of_analysis": "student",
        "row_structure": "One row per student.",
        "identifier_fields": ["participant_id"],
        "factor_levels": {
            "study_routine_group": ["standard_routine", "structured_routine"]
        },
        "outcome": "post_session_performance",
        "assignment_procedure": (
            "Synthetic students are assigned in equal numbers by a declared "
            "computer-generated blocked procedure."
        ),
        "missingness_rule": "No missing outcomes in the registered synthetic dataset.",
        "causal_scope": (
            "Causal interpretation is limited to the declared assignment, "
            "implementation, and synthetic pilot conditions."
        ),
        "limitation": (
            "The small synthetic pilot represents one implementation of the "
            "routine; it does not establish transportability to other students, "
            "settings, or delivery conditions."
        ),
        "figure_type": "two_group_mean_ci",
        "apa_fields": [
            "mean_standard",
            "sd_standard",
            "mean_structured",
            "sd_structured",
            "welch_t",
            "welch_df",
            "p_value_two_sided",
            "ci_95_low",
            "ci_95_high",
            "cohen_d_pooled",
        ],
    },
    "SWL-S03": {
        "slug": "swl_s03_skills_workshop_pre_post",
        "chapter_id": "ch07",
        "short_name": "Skills Workshop Pre/Post Study",
        "research_question": (
            "How does academic confidence change from before to after a skills "
            "workshop for students with linked observations?"
        ),
        "design": "Within-person pre/post study.",
        "unit_of_analysis": "student",
        "row_structure": "Two occasion rows per participant in long form.",
        "identifier_fields": ["participant_id", "occasion"],
        "factor_levels": {"occasion": ["pre", "post"]},
        "outcome": "academic_confidence",
        "assignment_procedure": "No control condition is present.",
        "missingness_rule": (
            "The registered dataset contains exactly one pre and one post row "
            "per participant; incomplete pairs are not silently retained."
        ),
        "causal_scope": (
            "The analysis estimates within-person change, not the workshop's "
            "causal effect in the absence of a control condition."
        ),
        "limitation": (
            "Pre/post change may reflect history, testing, maturation, or other "
            "time-varying influences because the design has no control condition."
        ),
        "figure_type": "paired_change",
        "apa_fields": [
            "n_paired",
            "mean_pre",
            "mean_post",
            "mean_change_post_minus_pre",
            "sd_change",
            "paired_t",
            "df",
            "p_value_two_sided",
            "ci_95_low",
            "ci_95_high",
            "cohen_dz",
        ],
    },
    "SWL-S04": {
        "slug": "swl_s04_three_condition_support",
        "chapter_id": "ch08",
        "short_name": "Three-Condition Learning-Support Study",
        "research_question": (
            "Do assessment outcomes differ across standard support, guided "
            "practice, and guided practice plus feedback, and which planned "
            "contrasts answer the substantive questions?"
        ),
        "design": "Three-condition between-student randomized study.",
        "unit_of_analysis": "student",
        "row_structure": "One row per student.",
        "identifier_fields": ["participant_id"],
        "factor_levels": {
            "support_condition": [
                "standard_support",
                "guided_practice",
                "guided_practice_plus_feedback",
            ]
        },
        "outcome": "assessment_performance",
        "assignment_procedure": (
            "Synthetic students are assigned in equal numbers to three declared "
            "conditions."
        ),
        "missingness_rule": "No missing outcomes in the registered synthetic dataset.",
        "causal_scope": (
            "Causal interpretation is conditional on the declared random "
            "assignment and implementation fidelity."
        ),
        "limitation": (
            "The two planned contrasts answer only the registered support "
            "questions; they do not justify unregistered pairwise fishing or "
            "generalization beyond the synthetic implementation."
        ),
        "figure_type": "three_group_mean_ci",
        "apa_fields": [
            "anova_f",
            "df_between",
            "df_within",
            "p_value",
            "eta_squared",
            "contrast_guided_average_minus_standard_estimate",
            "contrast_guided_average_minus_standard_t",
            "contrast_guided_average_minus_standard_p_holm",
            "contrast_feedback_increment_estimate",
            "contrast_feedback_increment_t",
            "contrast_feedback_increment_p_holm",
        ],
    },
    "SWL-S05": {
        "slug": "swl_s05_strategy_feedback",
        "chapter_id": "ch09",
        "short_name": "Strategy-by-Feedback Experiment",
        "research_question": (
            "Does the effect of study strategy on assessment performance depend "
            "on the feedback condition?"
        ),
        "design": "Balanced two-factor between-student factorial experiment.",
        "unit_of_analysis": "student",
        "row_structure": (
            "One row per student with exactly one valid strategy-by-feedback cell."
        ),
        "identifier_fields": ["participant_id"],
        "factor_levels": {
            "study_strategy": ["rereading", "retrieval_practice"],
            "feedback_condition": ["no_feedback", "explanatory_feedback"],
        },
        "outcome": "assessment_performance",
        "assignment_procedure": (
            "Synthetic students are assigned in equal numbers to all four cells."
        ),
        "missingness_rule": (
            "The registered dataset contains all four cells with equal counts and "
            "no missing outcomes."
        ),
        "causal_scope": (
            "Causal interpretation is conditional on random assignment, "
            "implementation fidelity, and the defined factor levels."
        ),
        "limitation": (
            "The interaction is specific to the registered strategy and feedback "
            "levels; main effects alone would obscure that conditional pattern."
        ),
        "figure_type": "factorial_interaction",
        "apa_fields": [
            "interaction_f",
            "df_effect",
            "df_within",
            "interaction_p",
            "interaction_partial_eta_squared",
            "interaction_difference_in_differences",
            "simple_strategy_no_feedback_estimate",
            "simple_strategy_no_feedback_t",
            "simple_strategy_no_feedback_p",
            "simple_strategy_explanatory_feedback_estimate",
            "simple_strategy_explanatory_feedback_t",
            "simple_strategy_explanatory_feedback_p",
        ],
    },
}


def data_filename(study_id: str) -> str:
    return f"{STUDY_CONFIG[study_id]['slug']}.csv"


def build_design_contract(study_id: str) -> dict[str, Any]:
    config = STUDY_CONFIG[study_id]
    return {
        "contract_version": "0.1",
        "batch_id": BATCH_ID,
        "study_id": study_id,
        "short_name": config["short_name"],
        "chapter_id": config["chapter_id"],
        "synthetic_only": True,
        "research_question": config["research_question"],
        "design": config["design"],
        "unit_of_analysis": config["unit_of_analysis"],
        "row_structure": config["row_structure"],
        "identifier_fields": config["identifier_fields"],
        "factor_levels": config["factor_levels"],
        "outcome": config["outcome"],
        "assignment_procedure": config["assignment_procedure"],
        "missingness_rule": config["missingness_rule"],
        "causal_scope": config["causal_scope"],
        "data_file": f"data/{data_filename(study_id)}",
        "python_analysis": "scripts/python/studies.py",
        "r_verification": f"scripts/r/{study_id.lower().replace('-', '_')}.R",
        "result_receipt": f"evidence/{study_id}/PYTHON_RESULT_RECEIPT.json",
        "figure_spec": f"evidence/{study_id}/FIGURE_SPEC.json",
        "apa_source_map": f"evidence/{study_id}/APA_RESULT_SOURCE_MAP.json",
        "matched_limitation": f"evidence/{study_id}/MATCHED_LIMITATION.json",
    }


def build_figure_spec(study_id: str) -> dict[str, Any]:
    config = STUDY_CONFIG[study_id]
    return {
        "contract_version": "0.1",
        "batch_id": BATCH_ID,
        "study_id": study_id,
        "figure_id": f"{study_id}-FIG-01",
        "figure_type": config["figure_type"],
        "data_file": f"data/{data_filename(study_id)}",
        "source_script": "scripts/python/generate_figures.py",
        "grayscale_required": True,
        "minimum_dpi": 300,
        "output_role": "generated_build_instance_not_tracked",
        "caption_scope": (
            f"Synthetic {config['short_name']} display; interpretation remains "
            "bounded by the matched limitation."
        ),
    }


def build_limitation(study_id: str) -> dict[str, Any]:
    config = STUDY_CONFIG[study_id]
    return {
        "contract_version": "0.1",
        "batch_id": BATCH_ID,
        "study_id": study_id,
        "design": config["design"],
        "causal_scope": config["causal_scope"],
        "matched_limitation": config["limitation"],
        "must_accompany_apa_result": True,
        "synthetic_only": True,
    }


def build_apa_map(
    study_id: str,
    receipt_sha256: str,
) -> dict[str, Any]:
    config = STUDY_CONFIG[study_id]
    return {
        "contract_version": "0.1",
        "batch_id": BATCH_ID,
        "study_id": study_id,
        "receipt_path": f"evidence/{study_id}/PYTHON_RESULT_RECEIPT.json",
        "receipt_sha256": receipt_sha256,
        "reported_number_bindings": [
            {
                "reporting_role": field,
                "json_pointer": f"/reported_fields/{field}",
            }
            for field in config["apa_fields"]
        ],
        "limitation_path": f"evidence/{study_id}/MATCHED_LIMITATION.json",
        "source_mapping_complete": True,
        "prose_is_generated_from_stable_fields": False,
        "policy": (
            "Book prose must be written from these stable fields and rechecked "
            "after any dataset or analysis change."
        ),
    }


def _validate_common(df: pd.DataFrame, study_id: str) -> None:
    if df.empty:
        raise ValueError(f"{study_id}: dataset is empty")
    if set(df["study_id"]) != {study_id}:
        raise ValueError(f"{study_id}: incorrect study_id binding")
    if df["participant_id"].isna().any():
        raise ValueError(f"{study_id}: missing participant identifier")


def validate_dataset(study_id: str, df: pd.DataFrame) -> None:
    _validate_common(df, study_id)
    config = STUDY_CONFIG[study_id]
    outcome = config["outcome"]
    if outcome not in df:
        raise ValueError(f"{study_id}: missing outcome {outcome}")
    if df[outcome].isna().any():
        raise ValueError(f"{study_id}: missing outcomes are not allowed")
    if study_id != "SWL-S03" and df["participant_id"].duplicated().any():
        raise ValueError(f"{study_id}: duplicate participant identifiers")
    for factor, expected_levels in config["factor_levels"].items():
        actual_levels = sorted(df[factor].astype(str).unique().tolist())
        if actual_levels != sorted(expected_levels):
            raise ValueError(
                f"{study_id}: factor levels for {factor} are {actual_levels}, "
                f"expected {sorted(expected_levels)}"
            )
    if study_id == "SWL-S02":
        counts = df.groupby("study_routine_group").size().to_dict()
        if counts != {"standard_routine": 32, "structured_routine": 32}:
            raise ValueError(f"SWL-S02: invalid group counts {counts}")
    elif study_id == "SWL-S03":
        if df.duplicated(["participant_id", "occasion"]).any():
            raise ValueError("SWL-S03: duplicate participant-occasion rows")
        counts = df.groupby("participant_id")["occasion"].nunique()
        if len(counts) != 48 or not (counts == 2).all():
            raise ValueError("SWL-S03: every participant must have pre and post")
        occasions = df.groupby("participant_id")["occasion"].apply(set)
        if not occasions.apply(lambda value: value == {"pre", "post"}).all():
            raise ValueError("SWL-S03: invalid occasion pairing")
    elif study_id == "SWL-S04":
        counts = df.groupby("support_condition").size().to_dict()
        expected = {
            "guided_practice": 30,
            "guided_practice_plus_feedback": 30,
            "standard_support": 30,
        }
        if counts != expected:
            raise ValueError(f"SWL-S04: invalid condition counts {counts}")
    elif study_id == "SWL-S05":
        counts = (
            df.groupby(["study_strategy", "feedback_condition"])
            .size()
            .to_dict()
        )
        expected = {
            ("rereading", "explanatory_feedback"): 24,
            ("rereading", "no_feedback"): 24,
            ("retrieval_practice", "explanatory_feedback"): 24,
            ("retrieval_practice", "no_feedback"): 24,
        }
        if counts != expected:
            raise ValueError(f"SWL-S05: invalid factorial cell counts {counts}")


def _write_dataset(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")


def generate_tracked_assets(output_root: Path, source_root: Path) -> list[Path]:
    output_root = output_root.resolve()
    source_root = source_root.resolve()
    generated: list[Path] = []
    studies_source = source_root / "scripts" / "python" / "studies.py"
    for study_id in STUDY_IDS:
        contract_path = output_root / "contracts" / f"{study_id}_DESIGN_CONTRACT.json"
        write_json(contract_path, build_design_contract(study_id))
        generated.append(contract_path)

        dataset_path = output_root / "data" / data_filename(study_id)
        dataset = GENERATORS[study_id]()
        validate_dataset(study_id, dataset)
        _write_dataset(dataset_path, dataset)
        generated.append(dataset_path)

        reported_fields = ANALYZERS[study_id](dataset)
        receipt_path = output_root / "evidence" / study_id / "PYTHON_RESULT_RECEIPT.json"
        receipt = {
            "contract_version": "0.1",
            "batch_id": BATCH_ID,
            "analysis_version": ANALYSIS_VERSION,
            "study_id": study_id,
            "synthetic_only": True,
            "data_file": f"data/{data_filename(study_id)}",
            "data_sha256": sha256(dataset_path),
            "design_contract": f"contracts/{study_id}_DESIGN_CONTRACT.json",
            "design_contract_sha256": sha256(contract_path),
            "analysis_source": "scripts/python/studies.py",
            "analysis_source_sha256": sha256(studies_source),
            "engine": "numpy/scipy transparent analysis",
            "reported_fields": reported_fields,
        }
        write_json(receipt_path, receipt)
        generated.append(receipt_path)

        limitation_path = output_root / "evidence" / study_id / "MATCHED_LIMITATION.json"
        write_json(limitation_path, build_limitation(study_id))
        generated.append(limitation_path)

        figure_path = output_root / "evidence" / study_id / "FIGURE_SPEC.json"
        write_json(figure_path, build_figure_spec(study_id))
        generated.append(figure_path)

        apa_path = output_root / "evidence" / study_id / "APA_RESULT_SOURCE_MAP.json"
        write_json(apa_path, build_apa_map(study_id, sha256(receipt_path)))
        generated.append(apa_path)

    r_contract_path = output_root / "evidence" / "PYTHON_R_VERIFICATION_CONTRACT.json"
    r_contract = {
        "contract_version": "0.1",
        "batch_id": BATCH_ID,
        "python_engine": "numpy/scipy transparent analysis",
        "r_engine": "base R stats",
        "tolerance": 1e-7,
        "independent_path_required": True,
        "runtime_outputs_tracked": False,
        "runtime_output_policy": "R results and parity receipts are ignored build-instance evidence.",
        "studies": [
            {
                "study_id": study_id,
                "r_script": f"scripts/r/{study_id.lower().replace('-', '_')}.R",
                "parity_fields": sorted(ANALYZERS[study_id](GENERATORS[study_id]()).keys()),
            }
            for study_id in STUDY_IDS
        ],
    }
    write_json(r_contract_path, r_contract)
    generated.append(r_contract_path)

    implementation_path = output_root / "evidence" / "BATCH_IMPLEMENTATION_RECEIPT.json"
    implementation = {
        "contract_version": "0.1",
        "batch_id": BATCH_ID,
        "baseline_source_commit": BASELINE_SOURCE_COMMIT,
        "book_handoff_commit": BOOK_HANDOFF_COMMIT,
        "synthetic_only": True,
        "public_release": False,
        "study_ids": list(STUDY_IDS),
        "all_study_specific_asset_sets_complete": True,
        "dimensions": {
            "dataset_present": True,
            "design_contract_present": True,
            "python_analysis_present": True,
            "r_verification_path_present": True,
            "result_receipt_present": True,
            "figure_source_present": True,
            "apa_source_map_present": True,
            "limitations_present": True,
            "exact_regeneration_status": "passed",
        },
        "r_parity_status_role": "required_green_local_and_ci_gate_not_tracked_runtime_output",
        "book_drafting_unblock_role": "eligible_after_green_merge_and_explicit_new_commit_anchor",
    }
    write_json(implementation_path, implementation)
    generated.append(implementation_path)

    handoff_path = output_root / "evidence" / "BOOK_INTEGRATION_HANDOFF.json"
    handoff = {
        "contract_version": "0.1",
        "batch_id": BATCH_ID,
        "status": "ready_after_green_merge",
        "candidate_tag": "psych-design-swl-s02-s05-v0-1",
        "book_baseline_commit": BOOK_HANDOFF_COMMIT,
        "current_book_source_anchor": BASELINE_SOURCE_COMMIT,
        "new_source_commit": "resolve_from_the_merged_candidate_tag",
        "unblocked_study_ids": list(STUDY_IDS),
        "unblocked_chapter_ids": [
            STUDY_CONFIG[study_id]["chapter_id"] for study_id in STUDY_IDS
        ],
        "required_book_actions": [
            "record the exact merged PyStatsV1 commit",
            "update the book source anchor explicitly",
            "regenerate the exact source inventory",
            "rerun the ten-study readiness matrix",
            "authorize the Chapters 6-9 drafting batch only after those gates pass",
        ],
        "public_release_authorized": False,
        "portal_change_authorized": False,
    }
    write_json(handoff_path, handoff)
    generated.append(handoff_path)

    relative_hashes = {
        str(path.relative_to(output_root)): sha256(path)
        for path in sorted(generated)
    }
    receipt_path = output_root / "evidence" / "BATCH_EXACT_REGENERATION_RECEIPT.json"
    source_input_paths = (
        "PSYCH_DESIGN_SWL_S02_S05_CONTRACT.json",
        "SOURCE_PROVENANCE.json",
        "METHOD_SOURCE_BINDING.json",
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
    source_input_hashes = {
        path: sha256(source_root / path) for path in source_input_paths
    }
    receipt = {
        "contract_version": "0.1",
        "batch_id": BATCH_ID,
        "baseline_source_commit": BASELINE_SOURCE_COMMIT,
        "book_handoff_commit": BOOK_HANDOFF_COMMIT,
        "synthetic_only": True,
        "generated_file_count": len(relative_hashes),
        "generated_file_sha256": relative_hashes,
        "source_input_sha256": source_input_hashes,
        "exact_regeneration_status": "passed",
        "public_release": False,
    }
    write_json(receipt_path, receipt)
    generated.append(receipt_path)
    return generated


def load_tracked_dataset(root: Path, study_id: str) -> pd.DataFrame:
    return pd.read_csv(root / "data" / data_filename(study_id))


def write_runtime_python_results(root: Path, output_root: Path) -> list[Path]:
    written: list[Path] = []
    for study_id in STUDY_IDS:
        dataset = load_tracked_dataset(root, study_id)
        validate_dataset(study_id, dataset)
        payload = {
            "contract_version": "0.1",
            "batch_id": BATCH_ID,
            "study_id": study_id,
            "synthetic_only": True,
            "reported_fields": ANALYZERS[study_id](dataset),
        }
        path = output_root / study_id / "py_results.json"
        write_json(path, payload)
        written.append(path)
    return written
