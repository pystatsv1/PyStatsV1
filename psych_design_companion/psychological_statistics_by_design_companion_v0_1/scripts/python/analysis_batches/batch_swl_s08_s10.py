from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.regression.mixed_linear_model import MixedLM

BATCH_ID = "psych-design-swl-s08-s10-v0.1"
BASELINE_SOURCE_COMMIT = "bb618a4c8c8186df43823b33bf2fab3e5d42330a"
BOOK_HANDOFF_COMMIT = "2d8532a62e7b4f1ded957325426ac6ed16a69e06"
STUDY_IDS = ("SWL-S08", "SWL-S09", "SWL-S10")

DATA_FILES = {
    "SWL-S08": "swl_s08_longitudinal_treatment.csv",
    "SWL-S09": "swl_s09_outcome_distribution_extension.csv",
    "SWL-S10": "swl_s10_replication_program.csv",
}


def stable_number(value: Any) -> float | int:
    if isinstance(value, (int, np.integer)):
        return int(value)
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"non-finite result: {value!r}")
    if abs(numeric - round(numeric)) < 1e-12:
        return int(round(numeric))
    return float(f"{numeric:.10g}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def dataset_path(root: Path, study_id: str) -> Path:
    return root / "data" / DATA_FILES[study_id]


# ---------------------------------------------------------------------------
# SWL-S08: longitudinal treatment study with unequal observed visits
# ---------------------------------------------------------------------------

S08_OCCASIONS = ("baseline", "post", "followup")
S08_GROUPS = ("control", "treatment")
S08_TARGET_MEANS = {
    ("control", "baseline"): 50.0,
    ("control", "post"): 51.0,
    ("control", "followup"): 51.5,
    ("treatment", "baseline"): 50.4,
    ("treatment", "post"): 57.4,
    ("treatment", "followup"): 59.9,
}
S08_MISSING_VISITS = {
    "control": {"post": {4, 9}, "followup": {3, 8, 13, 18, 23}},
    "treatment": {"post": {7, 18}, "followup": {5, 11, 17}},
}


def _s08_participant_offsets(treatment: int) -> list[float]:
    values = [
        5.0 * math.sin(i * 1.713 + treatment * 0.41)
        + 1.4 * math.cos(i * 0.931 - treatment * 0.22)
        for i in range(1, 31)
    ]
    mean_value = sum(values) / len(values)
    return [value - mean_value for value in values]


def generate_swl_s08() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for treatment, group in ((0, "control"), (1, "treatment")):
        offsets = _s08_participant_offsets(treatment)
        for number in range(1, 31):
            participant_id = f"S08-{group[0].upper()}{number:03d}"
            for occasion_order, occasion in enumerate(S08_OCCASIONS):
                if number in S08_MISSING_VISITS[group].get(occasion, set()):
                    continue
                post = int(occasion == "post")
                followup = int(occasion == "followup")
                base = (
                    50.0
                    + 0.4 * treatment
                    + 1.0 * post
                    + 1.5 * followup
                    + 6.0 * treatment * post
                    + 8.0 * treatment * followup
                )
                residual = (
                    3.2
                    * math.sin(
                        number * 2.137
                        + occasion_order * 1.117
                        + treatment * 0.577
                    )
                    + 0.9
                    * math.cos(
                        number * 0.733
                        + occasion_order * 2.419
                        - treatment * 0.31
                    )
                )
                rows.append(
                    {
                        "study_id": "SWL-S08",
                        "participant_id": participant_id,
                        "treatment_group": group,
                        "occasion": occasion,
                        "occasion_order": occasion_order,
                        "treatment": treatment,
                        "post": post,
                        "followup": followup,
                        "treatment_post": treatment * post,
                        "treatment_followup": treatment * followup,
                        "well_being_score": base + offsets[number - 1] + residual,
                    }
                )
    frame = pd.DataFrame(rows)
    for key, target in S08_TARGET_MEANS.items():
        mask = (
            (frame["treatment_group"] == key[0])
            & (frame["occasion"] == key[1])
        )
        frame.loc[mask, "well_being_score"] += (
            target - frame.loc[mask, "well_being_score"].mean()
        )
    frame["well_being_score"] = frame["well_being_score"].round(6)
    return frame.sort_values(
        ["treatment_group", "participant_id", "occasion_order"],
        kind="stable",
    ).reset_index(drop=True)


def _fit_s08(frame: pd.DataFrame):
    exog = sm.add_constant(
        frame[
            [
                "treatment",
                "post",
                "followup",
                "treatment_post",
                "treatment_followup",
            ]
        ],
        has_constant="add",
    )
    exog_re = pd.DataFrame(
        {"random_intercept": np.ones(len(frame), dtype=float)},
        index=frame.index,
    )
    model = MixedLM(
        endog=frame["well_being_score"],
        exog=exog,
        groups=frame["participant_id"],
        exog_re=exog_re,
    )
    return model.fit(reml=False, method="lbfgs", maxiter=500, disp=False)


def analyze_swl_s08(frame: pd.DataFrame) -> dict[str, float | int]:
    result = _fit_s08(frame)
    confidence = result.conf_int()
    visits = frame.groupby("participant_id").size()
    values: dict[str, float | int] = {
        "n_participants": frame["participant_id"].nunique(),
        "n_control": frame.loc[
            frame["treatment_group"] == "control", "participant_id"
        ].nunique(),
        "n_treatment": frame.loc[
            frame["treatment_group"] == "treatment", "participant_id"
        ].nunique(),
        "scheduled_rows": 180,
        "observed_rows": len(frame),
        "missing_visits": 180 - len(frame),
        "complete_participants": int((visits == 3).sum()),
        "incomplete_participants": int((visits == 2).sum()),
        "control_baseline_mean": frame.loc[
            (frame["treatment_group"] == "control")
            & (frame["occasion"] == "baseline"),
            "well_being_score",
        ].mean(),
        "control_post_mean": frame.loc[
            (frame["treatment_group"] == "control")
            & (frame["occasion"] == "post"),
            "well_being_score",
        ].mean(),
        "control_followup_mean": frame.loc[
            (frame["treatment_group"] == "control")
            & (frame["occasion"] == "followup"),
            "well_being_score",
        ].mean(),
        "treatment_baseline_mean": frame.loc[
            (frame["treatment_group"] == "treatment")
            & (frame["occasion"] == "baseline"),
            "well_being_score",
        ].mean(),
        "treatment_post_mean": frame.loc[
            (frame["treatment_group"] == "treatment")
            & (frame["occasion"] == "post"),
            "well_being_score",
        ].mean(),
        "treatment_followup_mean": frame.loc[
            (frame["treatment_group"] == "treatment")
            & (frame["occasion"] == "followup"),
            "well_being_score",
        ].mean(),
    }
    terms = {
        "const": "intercept",
        "treatment": "treatment",
        "post": "post",
        "followup": "followup",
        "treatment_post": "treatment_post",
        "treatment_followup": "treatment_followup",
    }
    for raw, name in terms.items():
        b = float(result.fe_params[raw])
        se = float(result.bse_fe[raw])
        values[f"{name}_b"] = b
        values[f"{name}_se"] = se
        values[f"{name}_z"] = b / se
        values[f"{name}_p"] = float(result.pvalues[raw])
        values[f"{name}_ci_95_low"] = float(confidence.loc[raw, 0])
        values[f"{name}_ci_95_high"] = float(confidence.loc[raw, 1])
    values.update(
        {
            "random_intercept_variance": float(result.cov_re.iloc[0, 0]),
            "residual_variance": float(result.scale),
            "log_likelihood": float(result.llf),
            "aic": float(result.aic),
            "bic": float(result.bic),
            "converged": int(bool(result.converged)),
        }
    )
    return {key: stable_number(value) for key, value in values.items()}


# ---------------------------------------------------------------------------
# SWL-S09: categorical and positive-skew outcome extension
# ---------------------------------------------------------------------------


def _s09_burden(index: int, intervention: bool) -> float:
    # Modular ordering yields a reproducible, positive-skewed distribution
    # without random-number-generator or library-version dependence.
    order = ((index * 37 + (11 if intervention else 0)) % 80) + 1
    base = math.exp(order / 22.0)
    ripple = ((index * 7) % 13) * 0.017 + index * 0.0003
    if intervention:
        value = 2.3 + 0.68 * base + ripple
    else:
        value = 4.1 + base + ripple
    return round(value, 3)


def generate_swl_s09() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    improved_counts = {"comparison": 36, "intervention": 56}
    for group in ("comparison", "intervention"):
        intervention = group == "intervention"
        for index in range(80):
            # A co-prime permutation keeps outcome labels distributed across
            # the ordered participant identifiers rather than clustered.
            improved = ((index * 29) % 80) < improved_counts[group]
            rows.append(
                {
                    "study_id": "SWL-S09",
                    "participant_id": f"S09-{len(rows) + 1:03d}",
                    "support_condition": group,
                    "clinically_improved": "yes" if improved else "no",
                    "recovery_burden_days": _s09_burden(index, intervention),
                }
            )
    return pd.DataFrame(rows)


def _mann_whitney_no_continuity(
    intervention_values: np.ndarray,
    comparison_values: np.ndarray,
) -> tuple[float, float, float, float]:
    n1 = len(intervention_values)
    n2 = len(comparison_values)
    combined = np.concatenate([intervention_values, comparison_values])
    ranks = stats.rankdata(combined, method="average")
    u1 = float(ranks[:n1].sum() - n1 * (n1 + 1) / 2)
    _, tie_counts = np.unique(combined, return_counts=True)
    tie_sum = float(np.sum(tie_counts**3 - tie_counts))
    n = n1 + n2
    variance = n1 * n2 / 12.0 * (
        (n + 1.0) - tie_sum / (n * (n - 1.0))
    )
    expected = n1 * n2 / 2.0
    z = (u1 - expected) / math.sqrt(variance)
    p = float(2.0 * stats.norm.sf(abs(z)))
    rank_biserial_lower = 1.0 - 2.0 * u1 / (n1 * n2)
    return u1, z, p, rank_biserial_lower


def analyze_swl_s09(frame: pd.DataFrame) -> dict[str, float | int]:
    table = pd.crosstab(
        frame["support_condition"], frame["clinically_improved"]
    ).reindex(index=["comparison", "intervention"], columns=["no", "yes"])
    observed = table.to_numpy(dtype=float)
    chi_square, chi_p, chi_df, expected = stats.chi2_contingency(
        observed, correction=False
    )
    n = int(observed.sum())
    comparison = frame.loc[
        frame["support_condition"] == "comparison", "recovery_burden_days"
    ].to_numpy(float)
    intervention = frame.loc[
        frame["support_condition"] == "intervention", "recovery_burden_days"
    ].to_numpy(float)
    u, z, rank_p, rank_biserial = _mann_whitney_no_continuity(
        intervention, comparison
    )
    values: dict[str, float | int] = {
        "n_total": n,
        "n_comparison": len(comparison),
        "n_intervention": len(intervention),
        "comparison_improved": int(table.loc["comparison", "yes"]),
        "comparison_not_improved": int(table.loc["comparison", "no"]),
        "intervention_improved": int(table.loc["intervention", "yes"]),
        "intervention_not_improved": int(table.loc["intervention", "no"]),
        "comparison_improved_proportion": table.loc["comparison", "yes"]
        / len(comparison),
        "intervention_improved_proportion": table.loc[
            "intervention", "yes"
        ]
        / len(intervention),
        "improved_risk_difference_intervention_minus_comparison": (
            table.loc["intervention", "yes"] / len(intervention)
            - table.loc["comparison", "yes"] / len(comparison)
        ),
        "chi_square": chi_square,
        "chi_square_df": chi_df,
        "chi_square_p": chi_p,
        "cramers_v": math.sqrt(chi_square / n),
        "minimum_expected_cell_count": expected.min(),
        "comparison_burden_median": np.median(comparison),
        "intervention_burden_median": np.median(intervention),
        "burden_median_difference_intervention_minus_comparison": (
            np.median(intervention) - np.median(comparison)
        ),
        "mann_whitney_u_intervention": u,
        "mann_whitney_z_no_continuity": z,
        "mann_whitney_p_two_sided": rank_p,
        "rank_biserial_intervention_lower": rank_biserial,
        "comparison_burden_skewness": stats.skew(comparison, bias=False),
        "intervention_burden_skewness": stats.skew(intervention, bias=False),
        "comparison_burden_min": comparison.min(),
        "comparison_burden_max": comparison.max(),
        "intervention_burden_min": intervention.min(),
        "intervention_burden_max": intervention.max(),
    }
    return {key: stable_number(value) for key, value in values.items()}


# ---------------------------------------------------------------------------
# SWL-S10: prospective power planning and cumulative evidence
# ---------------------------------------------------------------------------


def generate_swl_s10() -> pd.DataFrame:
    rows = [
        ("S10-R01", 70, 0.28, "direct"),
        ("S10-R02", 85, 0.42, "direct"),
        ("S10-R03", 60, 0.35, "direct"),
        ("S10-R04", 100, 0.51, "conceptual"),
        ("S10-R05", 75, 0.31, "direct"),
        ("S10-R06", 90, 0.46, "conceptual"),
    ]
    payload: list[dict[str, Any]] = []
    for study_id, n_per_group, observed_d, replication_type in rows:
        variance = (2.0 / n_per_group) + (
            observed_d**2 / (2.0 * (n_per_group - 2))
        )
        payload.append(
            {
                "study_id": study_id,
                "program_id": "SWL-S10",
                "replication_type": replication_type,
                "registered_before_analysis": "yes",
                "n_per_group": n_per_group,
                "total_n": n_per_group * 2,
                "observed_cohens_d": observed_d,
                "sampling_variance_d": round(variance, 10),
            }
        )
    return pd.DataFrame(payload)


def _power_n_per_group(
    effect_size: float,
    power: float,
    alpha: float = 0.05,
) -> float:
    z_alpha = float(stats.norm.ppf(1.0 - alpha / 2.0))
    z_power = float(stats.norm.ppf(power))
    return 2.0 * ((z_alpha + z_power) / effect_size) ** 2


def analyze_swl_s10(frame: pd.DataFrame) -> dict[str, float | int]:
    d = frame["observed_cohens_d"].to_numpy(float)
    var_d = frame["sampling_variance_d"].to_numpy(float)
    weights = 1.0 / var_d
    pooled = float(np.sum(weights * d) / np.sum(weights))
    se = float(np.sqrt(1.0 / np.sum(weights)))
    z = pooled / se
    p = float(2.0 * stats.norm.sf(abs(z)))
    ci_low = pooled - 1.96 * se
    ci_high = pooled + 1.96 * se
    q = float(np.sum(weights * np.square(d - pooled)))
    df_q = len(d) - 1
    p_q = float(stats.chi2.sf(q, df_q))
    i2 = max(0.0, (q - df_q) / q * 100.0) if q > 0 else 0.0
    n80 = _power_n_per_group(0.40, 0.80)
    n90 = _power_n_per_group(0.40, 0.90)
    values: dict[str, float | int] = {
        "study_count": len(frame),
        "total_participants": frame["total_n"].sum(),
        "target_effect_size_d": 0.40,
        "planning_alpha_two_sided": 0.05,
        "planning_power_primary": 0.80,
        "planning_n_per_group_unrounded_80": n80,
        "planning_n_per_group_ceiling_80": math.ceil(n80),
        "planning_power_sensitivity": 0.90,
        "planning_n_per_group_unrounded_90": n90,
        "planning_n_per_group_ceiling_90": math.ceil(n90),
        "minimum_observed_d": d.min(),
        "maximum_observed_d": d.max(),
        "fixed_effect_pooled_d": pooled,
        "fixed_effect_se": se,
        "fixed_effect_z": z,
        "fixed_effect_p": p,
        "fixed_effect_ci_95_low": ci_low,
        "fixed_effect_ci_95_high": ci_high,
        "cochran_q": q,
        "cochran_q_df": df_q,
        "cochran_q_p": p_q,
        "i_squared_percent": i2,
    }
    return {key: stable_number(value) for key, value in values.items()}


GENERATORS: dict[str, Callable[[], pd.DataFrame]] = {
    "SWL-S08": generate_swl_s08,
    "SWL-S09": generate_swl_s09,
    "SWL-S10": generate_swl_s10,
}
ANALYZERS: dict[str, Callable[[pd.DataFrame], dict[str, float | int]]] = {
    "SWL-S08": analyze_swl_s08,
    "SWL-S09": analyze_swl_s09,
    "SWL-S10": analyze_swl_s10,
}


def validate_dataset(study_id: str, frame: pd.DataFrame) -> None:
    if study_id == "SWL-S08":
        required = {
            "study_id",
            "participant_id",
            "treatment_group",
            "occasion",
            "occasion_order",
            "treatment",
            "post",
            "followup",
            "treatment_post",
            "treatment_followup",
            "well_being_score",
        }
        if set(frame.columns) != required:
            raise ValueError("SWL-S08 columns changed")
        if len(frame) != 168 or frame["participant_id"].nunique() != 60:
            raise ValueError("SWL-S08 dimensions changed")
        if frame.duplicated(["participant_id", "occasion"]).any():
            raise ValueError("SWL-S08 duplicate participant/occasion key")
        if (frame.groupby("participant_id")["treatment_group"].nunique() != 1).any():
            raise ValueError("SWL-S08 group drift")
        if set(frame["occasion"]) != set(S08_OCCASIONS):
            raise ValueError("SWL-S08 occasion levels changed")
        visits = frame.groupby("participant_id").size()
        if int((visits == 3).sum()) != 48 or int((visits == 2).sum()) != 12:
            raise ValueError("SWL-S08 visit pattern changed")
    elif study_id == "SWL-S09":
        required = {
            "study_id",
            "participant_id",
            "support_condition",
            "clinically_improved",
            "recovery_burden_days",
        }
        if set(frame.columns) != required:
            raise ValueError("SWL-S09 columns changed")
        if len(frame) != 160 or frame["participant_id"].nunique() != 160:
            raise ValueError("SWL-S09 dimensions changed")
        if set(frame["support_condition"]) != {"comparison", "intervention"}:
            raise ValueError("SWL-S09 group levels changed")
        if set(frame["clinically_improved"]) != {"yes", "no"}:
            raise ValueError("SWL-S09 categorical outcome levels changed")
        if frame.groupby("support_condition").size().to_dict() != {
            "comparison": 80,
            "intervention": 80,
        }:
            raise ValueError("SWL-S09 group balance changed")
        if (frame["recovery_burden_days"] <= 0).any():
            raise ValueError("SWL-S09 burden outcome must be positive")
    elif study_id == "SWL-S10":
        required = {
            "study_id",
            "program_id",
            "replication_type",
            "registered_before_analysis",
            "n_per_group",
            "total_n",
            "observed_cohens_d",
            "sampling_variance_d",
        }
        if set(frame.columns) != required:
            raise ValueError("SWL-S10 columns changed")
        if len(frame) != 6 or frame["study_id"].nunique() != 6:
            raise ValueError("SWL-S10 study count changed")
        if set(frame["program_id"]) != {"SWL-S10"}:
            raise ValueError("SWL-S10 program identity changed")
        if set(frame["registered_before_analysis"]) != {"yes"}:
            raise ValueError("SWL-S10 registration boundary changed")
        if not np.all(frame["total_n"] == 2 * frame["n_per_group"]):
            raise ValueError("SWL-S10 sample-size arithmetic changed")
        if (frame["sampling_variance_d"] <= 0).any():
            raise ValueError("SWL-S10 variances must be positive")
    else:
        raise ValueError("unknown study: " + study_id)


def _study_contract(study_id: str) -> dict[str, Any]:
    if study_id == "SWL-S08":
        return {
            "chapter_ids": ["ch14"],
            "claim_boundary": (
                "The synthetic model demonstrates differential change under the "
                "declared random-intercept specification; it is not evidence about "
                "a real treatment."
            ),
            "contract_version": "0.1",
            "data_layout": {
                "format": "long",
                "primary_key": ["participant_id", "occasion"],
                "observed_rows": 168,
                "participants": 60,
                "scheduled_rows": 180,
                "unequal_visit_counts_permitted": True,
            },
            "dataset": f"data/{DATA_FILES[study_id]}",
            "design": "two-group longitudinal study with three scheduled occasions",
            "estimands": [
                "additional treatment-group change from baseline to post",
                "additional treatment-group change from baseline to follow-up",
            ],
            "missingness_fixture": (
                "Twelve visit omissions are fixed by participant identifier before "
                "outcome generation and do not depend on realized outcomes."
            ),
            "model": {
                "engine": "statsmodels MixedLM",
                "fixed_effects": (
                    "well_being_score ~ treatment + post + followup + "
                    "treatment_post + treatment_followup"
                ),
                "random_effects": "random intercept for participant_id",
                "estimation": "maximum likelihood",
            },
            "outcome": "well_being_score",
            "study_id": study_id,
            "synthetic_only": True,
            "verification_category": "V3 fixed-effect estimand alignment plus V4 inference documentation",
        }
    if study_id == "SWL-S09":
        return {
            "chapter_ids": ["ch15"],
            "claim_boundary": (
                "The categorical and rank-based analyses answer different questions "
                "about two registered outcomes; neither is a generic repair for a "
                "failed normality test."
            ),
            "contract_version": "0.1",
            "data_layout": {
                "format": "one row per participant",
                "primary_key": ["participant_id"],
                "participants": 160,
                "participants_per_condition": 80,
            },
            "dataset": f"data/{DATA_FILES[study_id]}",
            "design": "two independent support conditions with two registered outcomes",
            "estimands": [
                "association between condition and binary clinical-improvement status",
                "distributional shift in positive-skew recovery burden between conditions",
            ],
            "outcomes": {
                "categorical": "clinically_improved",
                "positive_skew_continuous": "recovery_burden_days",
            },
            "study_id": study_id,
            "synthetic_only": True,
            "verification_category": "V2 numeric parity",
        }
    return {
        "chapter_ids": ["ch16"],
        "claim_boundary": (
            "Prospective power depends on a justified target effect and model; the "
            "fixed-effect synthesis assumes one common true effect and does not "
            "address publication bias or selective reporting."
        ),
        "contract_version": "0.1",
        "data_layout": {
            "format": "one row per completed synthetic replication",
            "primary_key": ["study_id"],
            "replication_count": 6,
        },
        "dataset": f"data/{DATA_FILES[study_id]}",
        "design": "registered replication program summarized at study level",
        "estimands": [
            "prospective per-group sample size for d=0.40 at 80 percent power",
            "fixed-effect pooled standardized mean difference across six replications",
        ],
        "study_id": study_id,
        "synthetic_only": True,
        "verification_category": "V2 numeric parity",
    }


def _apa_maps(study_id: str, fields: dict[str, float | int]) -> list[tuple[str, dict[str, Any]]]:
    common = {
        "contract_version": "0.1",
        "result_source": f"evidence/{study_id}/PYTHON_RESULT_RECEIPT.json",
        "study_id": study_id,
        "synthetic_only": True,
    }
    if study_id == "SWL-S08":
        sentence = (
            "A maximum-likelihood random-intercept model indicated larger "
            "treatment-group change from baseline to post, b = 5.86, SE = 0.87, "
            "z = 6.74, p < .001, 95% CI [4.16, 7.57], and from baseline to "
            "follow-up, b = 7.78, SE = 0.89, z = 8.70, p < .001, 95% CI "
            "[6.03, 9.54]."
        )
        names = [
            "treatment_post_b",
            "treatment_post_se",
            "treatment_post_z",
            "treatment_post_p",
            "treatment_post_ci_95_low",
            "treatment_post_ci_95_high",
            "treatment_followup_b",
            "treatment_followup_se",
            "treatment_followup_z",
            "treatment_followup_p",
            "treatment_followup_ci_95_low",
            "treatment_followup_ci_95_high",
        ]
        payload = dict(common)
        payload.update(
            {
                "analysis_role": "longitudinal_random_intercept_model",
                "rendered_text": sentence,
                "reported_number_bindings": [
                    {
                        "field": name,
                        "json_pointer": f"/reported_fields/{name}",
                    }
                    for name in names
                ],
            }
        )
        return [("APA_RESULT_SOURCE_MAP.json", payload)]
    if study_id == "SWL-S09":
        categorical_names = [
            "chi_square",
            "chi_square_df",
            "chi_square_p",
            "cramers_v",
            "comparison_improved_proportion",
            "intervention_improved_proportion",
        ]
        rank_names = [
            "comparison_burden_median",
            "intervention_burden_median",
            "mann_whitney_u_intervention",
            "mann_whitney_z_no_continuity",
            "mann_whitney_p_two_sided",
            "rank_biserial_intervention_lower",
        ]
        categorical = dict(common)
        categorical.update(
            {
                "analysis_role": "categorical_improvement_status",
                "rendered_text": (
                    "Clinical-improvement status differed by support condition, "
                    "chi-square(1) = 10.23, p = .001, Cramer's V = .253; the "
                    "improved proportions were .45 in comparison and .70 in intervention."
                ),
                "reported_number_bindings": [
                    {"field": name, "json_pointer": f"/reported_fields/{name}"}
                    for name in categorical_names
                ],
            }
        )
        rank_map = dict(common)
        rank_map.update(
            {
                "analysis_role": "positive_skew_recovery_burden",
                "rendered_text": (
                    "Recovery burden was lower in intervention (Mdn = 6.75) than "
                    "comparison (Mdn = 10.53), U = 1966.00, z = -4.21, p < .001, "
                    "rank-biserial effect = .386."
                ),
                "reported_number_bindings": [
                    {"field": name, "json_pointer": f"/reported_fields/{name}"}
                    for name in rank_names
                ],
            }
        )
        return [
            ("APA_RESULT_SOURCE_MAP_CATEGORICAL.json", categorical),
            ("APA_RESULT_SOURCE_MAP_RANK.json", rank_map),
        ]
    power_names = [
        "target_effect_size_d",
        "planning_power_primary",
        "planning_alpha_two_sided",
        "planning_n_per_group_ceiling_80",
    ]
    meta_names = [
        "study_count",
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
    ]
    power = dict(common)
    power.update(
        {
            "analysis_role": "prospective_power_planning",
            "rendered_text": (
                "Under the declared normal-approximation assumptions, detecting "
                "d = 0.40 with 80% power and two-sided alpha = .05 required 99 "
                "participants per group after rounding up."
            ),
            "reported_number_bindings": [
                {"field": name, "json_pointer": f"/reported_fields/{name}"}
                for name in power_names
            ],
        }
    )
    meta = dict(common)
    meta.update(
        {
            "analysis_role": "fixed_effect_cumulative_evidence",
            "rendered_text": (
                "Across six synthetic replications, the fixed-effect pooled estimate "
                "was d = 0.40, SE = 0.07, z = 6.05, p < .001, 95% CI [0.27, 0.53], "
                "with Q(5) = 1.60, p = .901, I-squared = 0%."
            ),
            "reported_number_bindings": [
                {"field": name, "json_pointer": f"/reported_fields/{name}"}
                for name in meta_names
            ],
        }
    )
    return [
        ("APA_RESULT_SOURCE_MAP_POWER.json", power),
        ("APA_RESULT_SOURCE_MAP_META.json", meta),
    ]


def _figure_specs(study_id: str) -> list[tuple[str, dict[str, Any]]]:
    common = {
        "contract_version": "0.1",
        "grayscale": True,
        "study_id": study_id,
        "synthetic_only": True,
    }
    if study_id == "SWL-S08":
        payload = dict(common)
        payload.update(
            {
                "caption": "Observed well-being means by group and occasion.",
                "generator": "scripts/python/generate_figures.py",
                "output": "swl_s08_group_time_means.png",
                "role": "descriptive_pattern_not_model_result",
                "required_axis_labels": ["Occasion", "Well-being score"],
            }
        )
        return [("FIGURE_SPEC.json", payload)]
    if study_id == "SWL-S09":
        cat = dict(common)
        cat.update(
            {
                "caption": "Improvement-status proportions by support condition.",
                "generator": "scripts/python/generate_figures.py",
                "output": "swl_s09_improvement_proportions.png",
                "role": "categorical_outcome_descriptive",
                "required_axis_labels": ["Support condition", "Proportion"],
            }
        )
        rank = dict(common)
        rank.update(
            {
                "caption": "Positive-skew recovery burden by support condition.",
                "generator": "scripts/python/generate_figures.py",
                "output": "swl_s09_recovery_burden.png",
                "role": "rank_analysis_distribution_display",
                "required_axis_labels": ["Support condition", "Recovery burden (days)"],
            }
        )
        return [("FIGURE_SPEC_CATEGORICAL.json", cat), ("FIGURE_SPEC_RANK.json", rank)]
    payload = dict(common)
    payload.update(
        {
            "caption": "Study-level standardized effects and fixed-effect pooled estimate.",
            "generator": "scripts/python/generate_figures.py",
            "output": "swl_s10_fixed_effect_forest.png",
            "role": "cumulative_evidence_forest_plot",
            "required_axis_labels": ["Standardized mean difference", "Replication"],
        }
    )
    return [("FIGURE_SPEC.json", payload)]


def _limitations(study_id: str) -> list[tuple[str, dict[str, Any]]]:
    common = {
        "contract_version": "0.1",
        "study_id": study_id,
        "synthetic_only": True,
    }
    if study_id == "SWL-S08":
        payload = dict(common)
        payload.update(
            {
                "analysis_role": "longitudinal_random_intercept_model",
                "limitation": (
                    "The synthetic result validates the workflow rather than a "
                    "real-world treatment claim. Interpretation depends on the "
                    "declared coding, random-intercept specification, assignment, "
                    "measurement stability, and an ignorable-missingness assumption."
                ),
            }
        )
        return [("MATCHED_LIMITATION.json", payload)]
    if study_id == "SWL-S09":
        categorical = dict(common)
        categorical.update(
            {
                "analysis_role": "categorical_improvement_status",
                "limitation": (
                    "The chi-square result concerns the registered binary outcome and "
                    "does not recover information discarded when a continuous or "
                    "ordinal construct is dichotomized."
                ),
            }
        )
        rank = dict(common)
        rank.update(
            {
                "analysis_role": "positive_skew_recovery_burden",
                "limitation": (
                    "The rank-based test detects a distributional shift under the "
                    "independent-groups design; it is not automatically a test of means "
                    "or medians unless stronger shape assumptions are defended."
                ),
            }
        )
        return [
            ("MATCHED_LIMITATION_CATEGORICAL.json", categorical),
            ("MATCHED_LIMITATION_RANK.json", rank),
        ]
    power = dict(common)
    power.update(
        {
            "analysis_role": "prospective_power_planning",
            "limitation": (
                "The sample-size calculation is conditional on the chosen target effect, "
                "two-sided alpha, equal allocation, independent observations, and the "
                "normal approximation; power cannot repair invalid design or measurement."
            ),
        }
    )
    meta = dict(common)
    meta.update(
        {
            "analysis_role": "fixed_effect_cumulative_evidence",
            "limitation": (
                "The fixed-effect synthesis assumes one common true effect and the six "
                "synthetic replications are complete by construction; publication bias, "
                "selective reporting, and meaningful heterogeneity are not ruled out."
            ),
        }
    )
    return [("MATCHED_LIMITATION_POWER.json", power), ("MATCHED_LIMITATION_META.json", meta)]


def generate_all(root: Path) -> list[Path]:
    generated: list[Path] = []
    for study_id in STUDY_IDS:
        frame = GENERATORS[study_id]()
        validate_dataset(study_id, frame)
        data = dataset_path(root, study_id)
        data.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(data, index=False, lineterminator="\n")
        generated.append(data)

        contract = root / "contracts" / f"{study_id}_DESIGN_CONTRACT.json"
        write_json(contract, _study_contract(study_id))
        generated.append(contract)

        fields = ANALYZERS[study_id](frame)
        receipt = root / "evidence" / study_id / "PYTHON_RESULT_RECEIPT.json"
        write_json(
            receipt,
            {
                "analysis_version": "0.1",
                "batch_id": BATCH_ID,
                "contract_version": "0.1",
                "dataset_sha256": sha256(data),
                "design_contract_sha256": sha256(contract),
                "python_analysis_sha256": sha256(Path(__file__)),
                "reported_fields": fields,
                "study_id": study_id,
                "synthetic_only": True,
            },
        )
        generated.append(receipt)

        for filename, payload in _apa_maps(study_id, fields):
            path = root / "evidence" / study_id / filename
            write_json(path, payload)
            generated.append(path)
        for filename, payload in _figure_specs(study_id):
            path = root / "evidence" / study_id / filename
            write_json(path, payload)
            generated.append(path)
        for filename, payload in _limitations(study_id):
            path = root / "evidence" / study_id / filename
            write_json(path, payload)
            generated.append(path)
    return generated
