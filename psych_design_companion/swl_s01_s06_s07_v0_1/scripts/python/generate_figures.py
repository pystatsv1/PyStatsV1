from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from studies import analyze_swl_s01, analyze_swl_s07  # noqa: E402


def write_manifest(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        json.dumps(
            {
                "contract_version": "0.1",
                "figures": rows,
                "grayscale_only": True,
                "synthetic_only": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def swl_s01_correlation(root: Path, output: Path) -> None:
    frame = pd.read_csv(root / "data/swl_s01_student_well_being_survey.csv")
    x = frame["sleep_quality"].to_numpy(float)
    y = frame["academic_confidence"].to_numpy(float)
    slope, intercept = np.polyfit(x, y, 1)
    grid = np.linspace(x.min(), x.max(), 100)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.scatter(x, y, facecolors="none", edgecolors="black", marker="o", s=28)
    ax.plot(grid, intercept + slope * grid, color="black", linewidth=1.5)
    ax.set_xlabel("Sleep quality")
    ax.set_ylabel("Academic confidence")
    ax.set_title("SWL-S01: Sleep quality and academic confidence")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def swl_s01_regression(root: Path, output: Path) -> None:
    frame = pd.read_csv(root / "data/swl_s01_student_well_being_survey.csv")
    values = analyze_swl_s01(frame)
    x = np.column_stack(
        [
            np.ones(len(frame)),
            frame["study_hours_per_week"].to_numpy(float),
            frame["academic_confidence"].to_numpy(float),
        ]
    )
    beta = np.array(
        [values["intercept_b"], values["study_hours_b"], values["confidence_b"]],
        dtype=float,
    )
    fitted = x @ beta
    residual = frame["assessment_performance"].to_numpy(float) - fitted
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.axhline(0.0, color="black", linewidth=1.0, linestyle="--")
    ax.scatter(fitted, residual, facecolors="none", edgecolors="black", marker="s", s=28)
    ax.set_xlabel("Fitted assessment performance")
    ax.set_ylabel("Residual")
    ax.set_title("SWL-S01: Registered prediction-model residuals")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def swl_s06_trajectory(root: Path, output: Path) -> None:
    frame = pd.read_csv(root / "data/swl_s06_confidence_trajectory.csv")
    wide = frame.pivot(index="participant_id", columns="occasion", values="academic_confidence")
    wide = wide[["baseline", "post", "follow_up"]]
    complete = wide.dropna()
    positions = np.arange(3)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for _, row in complete.iterrows():
        ax.plot(positions, row.to_numpy(float), color="0.78", linewidth=0.65)
    means = complete.mean(axis=0).to_numpy(float)
    ax.plot(positions, means, color="black", linewidth=2.0, marker="o", markersize=6)
    ax.set_xticks(positions, ["Baseline", "Post", "Follow-up"])
    ax.set_ylabel("Academic confidence")
    ax.set_title("SWL-S06: Complete-case confidence trajectories")
    ax.text(
        0.01,
        0.02,
        f"Complete trajectories: {len(complete)}; incomplete: {len(wide) - len(complete)}",
        transform=ax.transAxes,
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def swl_s07_ancova(root: Path, output: Path) -> None:
    frame = pd.read_csv(root / "data/swl_s07_baseline_adjusted_intervention.csv")
    values = analyze_swl_s07(frame)
    baseline_mean = float(values["baseline_overall_mean"])
    centered = frame["baseline_performance"].to_numpy(float) - baseline_mean
    grid = np.linspace(centered.min(), centered.max(), 100)
    intercept = float(values["adjusted_mean_comparison_at_overall_baseline"])
    difference = float(values["adjusted_group_difference_intervention_minus_comparison"])
    slope = float(values["baseline_slope"])
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for group, marker, line, offset in (
        ("comparison", "o", "-", 0.0),
        ("intervention", "s", "--", difference),
    ):
        subset = frame[frame["intervention_group"] == group]
        ax.scatter(
            subset["baseline_performance"],
            subset["post_performance"],
            facecolors="none",
            edgecolors="black",
            marker=marker,
            s=30,
            label=group.replace("_", " ").title(),
        )
        ax.plot(
            grid + baseline_mean,
            intercept + offset + slope * grid,
            color="black",
            linestyle=line,
            linewidth=1.5,
        )
    ax.set_xlabel("Baseline performance")
    ax.set_ylabel("Post performance")
    ax.set_title("SWL-S07: Baseline-adjusted parallel regression lines")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-root", type=Path, default=Path("outputs/psych_design_swl_s01_s06_s07"))
    args = parser.parse_args()
    root = args.root.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    figures = [
        ("swl_s01_correlation.png", "SWL-S01", "correlation", swl_s01_correlation),
        ("swl_s01_regression_residuals.png", "SWL-S01", "regression", swl_s01_regression),
        ("swl_s06_complete_case_trajectory.png", "SWL-S06", "primary", swl_s06_trajectory),
        ("swl_s07_ancova_parallel_lines.png", "SWL-S07", "primary", swl_s07_ancova),
    ]
    rows: list[dict[str, object]] = []
    for filename, study_id, role, builder in figures:
        builder(root, output_root / filename)
        rows.append(
            {
                "grayscale": True,
                "output": filename,
                "role": role,
                "study_id": study_id,
            }
        )
    write_manifest(output_root / "FIGURE_MANIFEST.json", rows)
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S01_S06_S07_FIGURES_OK")


if __name__ == "__main__":
    main()
