"""
Chapter 16b – Regression diagnostics with Pingouin, including Anscombe's Quartet.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg


DATA_DIR = Path("data") / "synthetic"
OUTPUT_DIR = Path("outputs") / "track_b"


def simulate_regression_dataset(
    n: int = 200,
    random_state: int = 123,
) -> pd.DataFrame:
    """Simulate a psychology-style regression dataset.

    Reuses the basic structure from Chapter 16: stress, sleep_hours,
    study_hours, motivation, exam_score.
    """
    rng = np.random.default_rng(random_state)

    # Latent traits
    baseline_ability = rng.normal(loc=0.0, scale=1.0, size=n)
    motivation = rng.normal(loc=0.0, scale=1.0, size=n)

    # Observed predictors
    stress = 50 + 10 * (-motivation) + rng.normal(0, 8, size=n)
    sleep_hours = 7.0 + 0.4 * motivation + rng.normal(0, 0.8, size=n)
    study_hours = 8.0 + 2.5 * motivation + 1.5 * baseline_ability + rng.normal(
        0,
        1.5,
        size=n,
    )

    # Outcome: exam_score
    exam_score = (
        80
        + 5.5 * study_hours
        + 2.0 * sleep_hours
        - 0.5 * stress
        + 4.0 * baseline_ability
        + rng.normal(0, 8, size=n)
    )

    df = pd.DataFrame(
        {
            "stress": stress,
            "sleep_hours": sleep_hours,
            "study_hours": study_hours,
            "motivation": motivation,
            "exam_score": exam_score,
        }
    )

    return df


def compute_regression_diagnostics(
    df: pd.DataFrame,
    predictors: Iterable[str],
    outcome: str,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Fit multiple regression and compute diagnostics.

    Returns
    -------
    diagnostics : pd.DataFrame
        Columns include fitted, residual, std_residual, leverage, cooks_distance.
    summary : pd.DataFrame
        Pingouin regression summary table.
    """
    predictors = list(predictors)
    X = df[predictors].to_numpy()
    y = df[outcome].to_numpy()

    # Add intercept for design matrix
    X_design = np.column_stack([np.ones(len(df)), X])
    n, p = X_design.shape

    # OLS solution
    xtx_inv = np.linalg.inv(X_design.T @ X_design)
    beta_hat = xtx_inv @ (X_design.T @ y)

    fitted = X_design @ beta_hat
    residual = y - fitted

    # Residual variance and standardized residuals
    dof = n - p
    residual_var = (residual**2).sum() / dof
    residual_std = math.sqrt(residual_var)
    std_residual = residual / residual_std

    # Hat matrix diagonal (leverage)
    # H = X (X'X)^(-1) X', but we only need the diagonal.
    hat_matrix = X_design @ xtx_inv @ X_design.T
    leverage = np.diag(hat_matrix)

    # Cook's distance
    cooks_distance = (std_residual**2 * leverage) / (p * (1 - leverage) ** 2)

    diagnostics = pd.DataFrame(
        {
            "fitted": fitted,
            "residual": residual,
            "std_residual": std_residual,
            "leverage": leverage,
            "cooks_distance": cooks_distance,
        }
    )

    # Cross-check with pingouin
    summary = pg.linear_regression(
        X=df[predictors],
        y=df[outcome],
        add_intercept=True,
    )

    return diagnostics, summary


def plot_residuals_vs_fitted(
    diagnostics: pd.DataFrame,
    output_path: Path,
) -> None:
    """Simple residuals vs fitted plot."""
    fig, ax = plt.subplots()
    ax.scatter(diagnostics["fitted"], diagnostics["residual"], alpha=0.7)
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("Residuals")
    ax.set_title("Residuals vs Fitted")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)


def plot_leverage_vs_cooks(
    diagnostics: pd.DataFrame,
    output_path: Path,
) -> None:
    """Plot leverage vs Cook's distance."""
    fig, ax = plt.subplots()
    ax.scatter(diagnostics["leverage"], diagnostics["cooks_distance"], alpha=0.7)
    ax.set_xlabel("Leverage")
    ax.set_ylabel("Cook's distance")
    ax.set_title("Leverage vs Cook's Distance")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)


# --- Anscombe's Quartet helpers -------------------------------------------------


def make_anscombe_quartet() -> pd.DataFrame:
    """Construct Anscombe's Quartet in tidy form.

    Returns
    -------
    df : pd.DataFrame
        Columns: x, y, dataset (I, II, III, IV)
    """
    # Classic Anscombe values
    x1 = np.array([10.0, 8.0, 13.0, 9.0, 11.0, 14.0, 6.0, 4.0, 12.0, 7.0, 5.0])
    y1 = np.array([8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68])

    x2 = x1.copy()
    y2 = np.array([9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74])

    x3 = x1.copy()
    y3 = np.array([7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73])

    x4 = np.array([8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 19.0, 8.0, 8.0, 8.0])
    y4 = np.array([6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89])

    df_list = []
    for x, y, label in [
        (x1, y1, "I"),
        (x2, y2, "II"),
        (x3, y3, "III"),
        (x4, y4, "IV"),
    ]:
        df_list.append(
            pd.DataFrame(
                {
                    "x": x,
                    "y": y,
                    "dataset": label,
                }
            )
        )

    return pd.concat(df_list, ignore_index=True)


def summarize_anscombe(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-dataset summary stats for Anscombe's Quartet."""
    results = []
    for dataset, group in df.groupby("dataset"):
        x = group["x"].to_numpy()
        y = group["y"].to_numpy()
        n = len(group)

        mean_x = x.mean()
        mean_y = y.mean()
        var_x = x.var(ddof=1)
        var_y = y.var(ddof=1)
        r = np.corrcoef(x, y)[0, 1]

        # Simple linear regression y ~ x
        x_design = np.column_stack([np.ones(n), x])
        beta = np.linalg.inv(x_design.T @ x_design) @ (x_design.T @ y)
        intercept, slope = beta[0], beta[1]

        results.append(
            {
                "dataset": dataset,
                "n": n,
                "mean_x": mean_x,
                "mean_y": mean_y,
                "var_x": var_x,
                "var_y": var_y,
                "r": r,
                "slope": slope,
                "intercept": intercept,
            }
        )

    return pd.DataFrame(results).sort_values("dataset").reset_index(drop=True)


def plot_anscombe_quartet(df: pd.DataFrame, output_path: Path) -> None:
    """Create a 2x2 grid of Anscombe scatterplots with regression lines."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(8, 8), sharex=True, sharey=True)
    axes = axes.ravel()

    x_min, x_max = df["x"].min() - 1, df["x"].max() + 1
    y_min, y_max = df["y"].min() - 1, df["y"].max() + 1

    for ax, (dataset, group) in zip(axes, df.groupby("dataset")):
        x = group["x"].to_numpy()
        y = group["y"].to_numpy()

        # Fit simple regression
        x_design = np.column_stack([np.ones(len(x)), x])
        beta = np.linalg.inv(x_design.T @ x_design) @ (x_design.T @ y)
        intercept, slope = beta[0], beta[1]

        ax.scatter(x, y, alpha=0.8)
        xx = np.linspace(x_min, x_max, 100)
        yy = intercept + slope * xx
        ax.plot(xx, yy)

        ax.set_title(f"Dataset {dataset}")
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

    fig.suptitle("Anscombe's Quartet – Same Stats, Different Stories")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(output_path)
    plt.close(fig)


def run_ch16b_demo(
    n: int = 200,
    random_state: int = 123,
) -> None:
    """Run the full Chapter 16b diagnostics demonstration, including Anscombe."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Simulating regression dataset for diagnostics...")
    df = simulate_regression_dataset(n=n, random_state=random_state)
    print("\nFirst 5 rows of the dataset:")
    print(df.head())

    predictors = ["study_hours", "sleep_hours", "stress", "motivation"]
    outcome = "exam_score"

    diagnostics, summary = compute_regression_diagnostics(
        df=df,
        predictors=predictors,
        outcome=outcome,
    )

    print("\nPingouin multiple regression summary:")
    print(summary)

    # Basic sanity check on R^2
    model_r2 = float(summary.loc[1:, "r2"].iloc[0])
    print(f"\nModel R^2 (first predictor row): {model_r2:0.3f}")

    # Save diagnostics and influential points
    diagnostics_path = OUTPUT_DIR / "ch16b_regression_diagnostics.csv"
    influential_path = OUTPUT_DIR / "ch16b_influential_points.csv"
    diagnostics.to_csv(diagnostics_path, index=False)

    top_influential = diagnostics.sort_values("cooks_distance", ascending=False).head(10)
    top_influential.to_csv(influential_path, index=False)

    # Plots
    residuals_plot = OUTPUT_DIR / "ch16b_residuals_vs_fitted.png"
    leverage_plot = OUTPUT_DIR / "ch16b_leverage_vs_cooks.png"
    plot_residuals_vs_fitted(diagnostics, residuals_plot)
    plot_leverage_vs_cooks(diagnostics, leverage_plot)

    print(f"\nDiagnostics saved to: {diagnostics_path}")
    print(f"Top influential points saved to: {influential_path}")
    print(f"Residuals vs fitted plot: {residuals_plot}")
    print(f"Leverage vs Cook's distance plot: {leverage_plot}")

    # --- Anscombe's Quartet section -----------------------------------------
    print("\nConstructing Anscombe's Quartet...")
    anscombe_df = make_anscombe_quartet()
    anscombe_summary = summarize_anscombe(anscombe_df)

    print("\nAnscombe summary (per dataset):")
    print(anscombe_summary)

    anscombe_summary_path = OUTPUT_DIR / "ch16b_anscombe_summary.csv"
    anscombe_plot_path = OUTPUT_DIR / "ch16b_anscombe_quartet.png"

    anscombe_summary.to_csv(anscombe_summary_path, index=False)
    plot_anscombe_quartet(anscombe_df, anscombe_plot_path)

    print(f"\nAnscombe summary saved to: {anscombe_summary_path}")
    print(f"Anscombe quartet plot saved to: {anscombe_plot_path}")
    print("\nChapter 16b diagnostics + Anscombe demo complete.")


if __name__ == "__main__":
    run_ch16b_demo()
