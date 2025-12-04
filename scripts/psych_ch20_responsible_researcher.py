"""
Chapter 20 lab: Responsible Researcher tools

This script provides three small utilities that match the structure of
the Chapter 20 narrative:

1. Power planning helper for an independent-samples t-test
2. Toy fixed-effect meta-analysis over simulated studies
3. A final-project APA-style report template (Markdown)

All outputs are written under:

    data/synthetic/
    outputs/track_b/

and are deterministic given the random_state arguments.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.stats import chi2


DATA_DIR = Path("data") / "synthetic"
OUTPUT_DIR = Path("outputs") / "track_b"


@dataclass
class MetaAnalysisResult:
    """Container for toy fixed-effect meta-analysis results."""

    pooled_d: float
    se: float
    z: float
    p: float
    ci_low: float
    ci_high: float
    Q: float
    df_Q: int
    p_Q: float
    I2: float


def ensure_directories() -> Tuple[Path, Path]:
    """Ensure data and output directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR, OUTPUT_DIR


# ---------------------------------------------------------------------------
# 20.1 Power analysis helper
# ---------------------------------------------------------------------------


def compute_sample_size_for_ttest(
    effect_size: float,
    power: float = 0.80,
    alpha: float = 0.05,
    alternative: str = "two-sided",
) -> float:
    """Return per-group sample size for an independent t-test.

    Uses a normal-approximation formula rather than pingouin.power_ttest
    to avoid version-dependent behavior. This is accurate enough for
    planning and keeps the logic fully transparent for students.
    """
    if effect_size <= 0:
        raise ValueError("effect_size must be positive.")
    if not (0 < power < 1):
        raise ValueError("power must be between 0 and 1.")
    if alternative not in {"two-sided", "greater", "less"}:
        raise ValueError(
            "alternative must be 'two-sided', 'greater', or 'less'."
        )

    # Critical values
    if alternative == "two-sided":
        z_alpha = norm.ppf(1 - alpha / 2)
    else:
        z_alpha = norm.ppf(1 - alpha)

    z_power = norm.ppf(power)

    # Approximate per-group n for two independent groups with equal n
    n_per_group = 2.0 * ((z_alpha + z_power) / effect_size) ** 2
    return float(n_per_group)




def build_power_grid() -> pd.DataFrame:
    """Build a small grid of power calculations for teaching.

    Effect sizes: 0.2, 0.5, 0.8
    Power levels: 0.8, 0.9
    Alpha: 0.05
    """
    rows = []
    for d in (0.2, 0.5, 0.8):
        for power in (0.8, 0.9):
            n = compute_sample_size_for_ttest(effect_size=d, power=power)
            rows.append(
                {
                    "test": "independent_t",
                    "effect_size_d": d,
                    "power": power,
                    "alpha": 0.05,
                    "n_per_group": ceil(n),
                }
            )

    df = pd.DataFrame(rows)
    return df


# ---------------------------------------------------------------------------
# 20.2 Meta-analysis helper
# ---------------------------------------------------------------------------


def simulate_meta_studies(
    num_studies: int = 5,
    base_effect: float = 0.4,
    random_state: int | None = 123,
) -> pd.DataFrame:
    """Simulate a set of 'published' effect sizes for meta-analysis.

    Each study has:
        - n_per_group (between 40 and 120)
        - observed_d (Cohen's d with sampling noise)
        - var_d (approximate sampling variance of d)
    """
    rng = np.random.default_rng(random_state)

    n_per_group = rng.integers(40, 121, size=num_studies)
    # Allow modest variation around the base effect
    true_effects = rng.normal(loc=base_effect, scale=0.10, size=num_studies)
    observed_d = rng.normal(loc=true_effects, scale=0.15)

    # Approximate variance of Cohen's d for balanced two-group design
    # (Hedges & Olkin style approximation).
    var_d = (2 / n_per_group) + (observed_d**2 / (2 * (n_per_group - 2)))

    studies = pd.DataFrame(
        {
            "study_id": np.arange(1, num_studies + 1),
            "n_per_group": n_per_group,
            "true_d": true_effects,
            "observed_d": observed_d,
            "var_d": var_d,
        }
    )

    return studies


def run_fixed_effect_meta(studies: pd.DataFrame) -> MetaAnalysisResult:
    """Compute a toy fixed-effect meta-analysis over observed d-values."""
    d = studies["observed_d"].to_numpy()
    var_d = studies["var_d"].to_numpy()
    w = 1.0 / var_d

    pooled_d = float(np.sum(w * d) / np.sum(w))
    se = float(np.sqrt(1.0 / np.sum(w)))
    z = pooled_d / se
    p = 2 * (1 - norm.cdf(abs(z)))

    # 95% CI
    ci_low = pooled_d - 1.96 * se
    ci_high = pooled_d + 1.96 * se

    # Heterogeneity (Q, df, p, I^2)
    Q = float(np.sum(w * (d - pooled_d) ** 2))
    df_Q = len(d) - 1
    p_Q = 1 - chi2.cdf(Q, df_Q)
    I2 = max(0.0, (Q - df_Q) / Q * 100) if Q > 0 else 0.0

    return MetaAnalysisResult(
        pooled_d=pooled_d,
        se=se,
        z=float(z),
        p=float(p),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        Q=Q,
        df_Q=df_Q,
        p_Q=float(p_Q),
        I2=float(I2),
    )


# ---------------------------------------------------------------------------
# 20.4 Final project template
# ---------------------------------------------------------------------------


def generate_project_template(path: Path) -> None:
    """Create a simple Markdown template for the final PyStatsV1 project."""
    template = """# PyStatsV1 Final Project Report

## 1. Title and Research Question

- Descriptive title:
- Primary research question(s):

## 2. Background and Rationale

- Brief summary of prior findings (1–2 paragraphs).
- Why is this question interesting or important?

## 3. Methods

### 3.1 Design

- Design type (e.g., between-subjects, within-subjects, mixed).
- Independent variables and their levels.
- Dependent variable(s).

### 3.2 Participants

- Sample size and recruitment.
- Inclusion / exclusion criteria.

### 3.3 Measures and Materials

- Scales, tasks, or instruments used.
- Reliability or validity notes if available.

### 3.4 Procedure

- Step-by-step description of what participants did.
- Any randomization or counterbalancing.

### 3.5 Power Planning (Chapter 20)

- Brief summary of your power analysis:
  - Test type:
  - Effect size assumed:
  - Alpha and desired power:
  - Planned sample size per group:

## 4. Results

- Descriptive statistics (means, standard deviations, counts).
- Main inferential tests with:
  - Test statistic and df
  - p-value
  - Effect size and 95% CI
- Reference specific PyStatsV1 scripts or commands used
  (e.g., `python -m scripts.psych_ch16_regression`).

## 5. Discussion

### 5.1 Summary of Findings

- Answer the research question in plain language.
- Emphasize effect sizes and direction of effects.

### 5.2 Relation to Prior Work / Meta-analytic View

- Do your results align with or differ from prior studies?
- How might they fit into a broader body of evidence?

### 5.3 Limitations

- Sample characteristics.
- Measurement concerns.
- Design and analytic constraints.

### 5.4 Future Directions

- Follow-up studies or analyses that would strengthen the conclusions.

## 6. Reproducibility Notes

- Git commit hash of the PyStatsV1 repository.
- Random seeds used (if applicable).
- Exact commands or notebooks used to generate tables and figures.
- Notes on any external data sources, with links or DOIs.

"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(template, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the Chapter 20 lab workflow."""
    ensure_directories()

    print("Running Chapter 20: Responsible Researcher lab...\n")

    # 1. Power grid
    print("Computing power grid for independent-samples t-test...")
    power_df = build_power_grid()
    power_path = OUTPUT_DIR / "ch20_power_grid.csv"
    power_df.to_csv(power_path, index=False)
    print(power_df)
    print(f"\nPower grid saved to: {power_path}\n")

    # 2. Meta-analysis simulation
    print("Simulating toy meta-analysis over multiple studies...")
    studies = simulate_meta_studies(num_studies=5, base_effect=0.4, random_state=2025)
    meta_result = run_fixed_effect_meta(studies)

    studies_path = OUTPUT_DIR / "ch20_meta_studies.csv"
    studies.to_csv(studies_path, index=False)

    summary_path = OUTPUT_DIR / "ch20_meta_summary.csv"
    summary_df = pd.DataFrame(
        [
            {
                "pooled_d": meta_result.pooled_d,
                "se": meta_result.se,
                "z": meta_result.z,
                "p": meta_result.p,
                "ci_low": meta_result.ci_low,
                "ci_high": meta_result.ci_high,
                "Q": meta_result.Q,
                "df_Q": meta_result.df_Q,
                "p_Q": meta_result.p_Q,
                "I2": meta_result.I2,
            }
        ]
    )
    summary_df.to_csv(summary_path, index=False)

    print("Meta-analysis studies:")
    print(studies)
    print("\nMeta-analysis summary:")
    print(summary_df)
    print(f"\nMeta-analysis tables saved to:\n  {studies_path}\n  {summary_path}\n")

    # 3. Final project template
    template_path = OUTPUT_DIR / "ch20_final_project_template.md"
    generate_project_template(template_path)
    print(f"Final project template written to: {template_path}\n")

    print("Chapter 20 Responsible Researcher lab complete.")


if __name__ == "__main__":
    main()
