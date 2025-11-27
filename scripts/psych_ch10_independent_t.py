"""
Track B – Chapter 10: Independent-samples t-test (pooled vs Welch)

This script simulates a simple between-subjects experiment with two
independent groups ("control" and "treatment") on a stress_score variable.

It computes:
- the classical pooled-variance independent-samples t-test
- Cohen's d using the pooled SD
- a 95% CI for the mean difference
- a Welch "safety check" t-test that does not assume equal variances
- a bar plot of group means with 95% CIs
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = Path("data") / "synthetic"
OUTPUT_DIR = Path("outputs") / "track_b"


# ---------------------------------------------------------------------------
# Helpers for generating and summarizing groups
# ---------------------------------------------------------------------------


def generate_independent_groups(
    rng: np.random.Generator,
    n_per_group: int = 25,
    mean_control: float = 20.0,
    sd_control: float = 10.0,
    mean_treatment: float = 18.0,
    sd_treatment: float = 10.0,
) -> pd.DataFrame:
    """
    Generate a synthetic dataset with two independent groups:
    'control' and 'treatment', each with n_per_group observations.

    Returns a DataFrame with columns:
    - id: integer ID
    - condition: 'control' or 'treatment'
    - stress_score: simulated outcome
    """
    control_scores = rng.normal(loc=mean_control, scale=sd_control, size=n_per_group)
    treatment_scores = rng.normal(
        loc=mean_treatment, scale=sd_treatment, size=n_per_group
    )

    df_control = pd.DataFrame(
        {
            "id": np.arange(1, n_per_group + 1),
            "condition": "control",
            "stress_score": control_scores,
        }
    )

    df_treatment = pd.DataFrame(
        {
            "id": np.arange(1, n_per_group + 1),
            "condition": "treatment",
            "stress_score": treatment_scores,
        }
    )

    return pd.concat([df_control, df_treatment], ignore_index=True)


def summarize_group(df: pd.DataFrame, condition: str) -> Tuple[float, float, int]:
    """
    Return (mean, sd, n) for the specified condition.
    """
    subset = df.loc[df["condition"] == condition, "stress_score"]
    mean = float(subset.mean())
    sd = float(subset.std(ddof=1))
    n = int(subset.shape[0])
    return mean, sd, n


# ---------------------------------------------------------------------------
# Pooled-variance t-test helpers
# ---------------------------------------------------------------------------


def compute_pooled_variance(sd1: float, sd2: float, n1: int, n2: int) -> float:
    """
    Compute the pooled variance under the equal-variances assumption.

    s_p^2 = [ (n1 - 1)*s1^2 + (n2 - 1)*s2^2 ] / (n1 + n2 - 2)
    """
    numerator = (n1 - 1) * (sd1**2) + (n2 - 1) * (sd2**2)
    denominator = n1 + n2 - 2
    return numerator / denominator


def compute_pooled_sd(sd1: float, sd2: float, n1: int, n2: int) -> float:
    """
    Pooled standard deviation (square root of pooled variance).
    """
    sp2 = compute_pooled_variance(sd1, sd2, n1, n2)
    return float(np.sqrt(sp2))


def compute_se_difference_from_pooled(sp: float, n1: int, n2: int) -> float:
    """
    Standard error of the difference in means using pooled SD.

    SE = s_p * sqrt(1/n1 + 1/n2)
    """
    return float(sp * np.sqrt(1.0 / n1 + 1.0 / n2))


def compute_pooled_t(mean1: float, mean2: float, se_diff: float) -> float:
    """
    t statistic for the pooled-variance independent-samples t-test.

    t = (mean1 - mean2) / SE
    """
    if se_diff <= 0:
        raise ValueError("Standard error must be positive.")
    return float((mean1 - mean2) / se_diff)


# ---------------------------------------------------------------------------
# Welch t-test helpers (no equal-variances assumption)
# ---------------------------------------------------------------------------


def compute_welch_standard_error(sd1: float, sd2: float, n1: int, n2: int) -> float:
    """
    Standard error of the difference in means for Welch's t-test.

    SE_welch = sqrt( s1^2 / n1 + s2^2 / n2 )
    """
    return float(np.sqrt((sd1**2) / n1 + (sd2**2) / n2))


def compute_welch_df(sd1: float, sd2: float, n1: int, n2: int) -> float:
    """
    Welch–Satterthwaite approximation to the degrees of freedom.

    df = (s1^2/n1 + s2^2/n2)^2
         / [ (s1^2/n1)^2/(n1-1) + (s2^2/n2)^2/(n2-1) ]
    """
    term1 = (sd1**2) / n1
    term2 = (sd2**2) / n2
    numerator = (term1 + term2) ** 2
    denominator = (term1**2) / (n1 - 1) + (term2**2) / (n2 - 1)
    return float(numerator / denominator)


def compute_welch_t(mean1: float, mean2: float, se_welch: float) -> float:
    """
    t statistic for Welch's independent-samples t-test.

    t = (mean1 - mean2) / SE_welch
    """
    if se_welch <= 0:
        raise ValueError("Standard error must be positive.")
    return float((mean1 - mean2) / se_welch)


# ---------------------------------------------------------------------------
# Plotting (95% CI, not just SE)
# ---------------------------------------------------------------------------


def save_group_means_plot(
    mean1: float,
    sd1: float,
    n1: int,
    mean2: float,
    sd2: float,
    n2: int,
    output_path: Path,
) -> None:
    """
    Save a simple bar plot with 95% confidence intervals for
    control vs treatment.

    We compute a separate t-critical value for each group and use:
    CI = mean ± t_crit * SE.
    """
    # Standard errors for each group mean
    se1 = sd1 / np.sqrt(n1)
    se2 = sd2 / np.sqrt(n2)

    alpha = 0.05
    tcrit1 = stats.t.ppf(1.0 - alpha / 2.0, df=n1 - 1)
    tcrit2 = stats.t.ppf(1.0 - alpha / 2.0, df=n2 - 1)

    ci1 = tcrit1 * se1
    ci2 = tcrit2 * se2

    labels = ["control", "treatment"]
    means = [mean1, mean2]
    yerrs = [ci1, ci2]

    fig, ax = plt.subplots()
    ax.bar(labels, means, yerr=yerrs, capsize=5)
    ax.set_ylabel("Stress score")
    ax.set_title("Group means with 95% CI")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def main() -> None:
    rng = np.random.default_rng(12345)

    # 1. Generate synthetic data
    df = generate_independent_groups(rng=rng, n_per_group=25)

    mean_control, sd_control, n_control = summarize_group(df, "control")
    mean_treatment, sd_treatment, n_treatment = summarize_group(df, "treatment")

    print(f"Generated independent groups with n = {n_control} per condition")
    print(
        f"Group: control    mean = {mean_control:5.2f}  "
        f"SD = {sd_control:5.2f}  n = {n_control}"
    )
    print(
        f"Group: treatment  mean = {mean_treatment:5.2f}  "
        f"SD = {sd_treatment:5.2f}  n = {n_treatment}"
    )
    print()

    # 2. Pooled-variance independent-samples t-test
    diff = mean_control - mean_treatment
    sp = compute_pooled_sd(sd_control, sd_treatment, n_control, n_treatment)
    se_diff = compute_se_difference_from_pooled(sp, n_control, n_treatment)
    t_pooled = compute_pooled_t(mean_control, mean_treatment, se_diff)
    df_pooled = n_control + n_treatment - 2
    p_pooled = 2.0 * stats.t.sf(abs(t_pooled), df=df_pooled)

    # 95% CI for the mean difference using pooled SE
    alpha = 0.05
    tcrit = stats.t.ppf(1.0 - alpha / 2.0, df=df_pooled)
    ci_lower = diff - tcrit * se_diff
    ci_upper = diff + tcrit * se_diff

    # Cohen's d (pooled)
    d_pooled = diff / sp if sp > 0 else float("nan")

    print(f"Mean difference (control - treatment) = {diff:5.2f}")
    print(f"Pooled SD = {sp:5.2f}")
    print(f"SE of difference (pooled) = {se_diff:5.2f}")
    print(f"df (pooled) = {df_pooled}")
    print(f"t statistic (pooled) = {t_pooled:5.2f}")
    print(f"Two-sided p-value (pooled) = {p_pooled:5.3f}")
    print()
    print(
        f"95% CI for (mu_control - mu_treatment) "
        f"(pooled): [{ci_lower:5.2f}, {ci_upper:5.2f}]"
    )
    print(f"Cohen's d (pooled) = {d_pooled:5.2f}")
    print()

    # 3. Welch "safety check" (no equal-variances assumption)
    se_welch = compute_welch_standard_error(
        sd_control, sd_treatment, n_control, n_treatment
    )
    t_welch = compute_welch_t(mean_control, mean_treatment, se_welch)
    df_welch = compute_welch_df(
        sd_control, sd_treatment, n_control, n_treatment
    )
    p_welch = 2.0 * stats.t.sf(abs(t_welch), df=df_welch)

    print("Welch t-test (safety check, unequal variances allowed):")
    print(f"SE of difference (Welch) = {se_welch:5.2f}")
    print(f"df (Welch) ≈ {df_welch:5.2f}")
    print(f"t statistic (Welch) = {t_welch:5.2f}")
    print(f"Two-sided p-value (Welch) = {p_welch:5.3f}")
    print()

    # 4. Save CSV and plot
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = DATA_DIR / "psych_ch10_independent_groups.csv"
    plot_path = OUTPUT_DIR / "ch10_group_means_with_ci.png"

    df.to_csv(csv_path, index=False)
    save_group_means_plot(
        mean_control,
        sd_control,
        n_control,
        mean_treatment,
        sd_treatment,
        n_treatment,
        plot_path,
    )

    print(f"Wrote data to: {csv_path}")
    print(f"Wrote plot (means with 95% CI) to: {plot_path}")


if __name__ == "__main__":
    main()
