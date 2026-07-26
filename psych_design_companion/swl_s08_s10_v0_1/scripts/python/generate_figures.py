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

from studies import analyze_swl_s10  # noqa: E402


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


def swl_s08_group_time(root: Path, output: Path) -> None:
    frame = pd.read_csv(root / "data/swl_s08_longitudinal_treatment.csv")
    means = (
        frame.groupby(["treatment_group", "occasion"], as_index=False)[
            "well_being_score"
        ]
        .mean()
    )
    order = ["baseline", "post", "followup"]
    x = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for group, marker, linestyle in (
        ("control", "o", "-"),
        ("treatment", "s", "--"),
    ):
        subset = means[means["treatment_group"] == group].set_index("occasion")
        y = [float(subset.loc[level, "well_being_score"]) for level in order]
        ax.plot(
            x,
            y,
            color="black",
            marker=marker,
            linestyle=linestyle,
            linewidth=1.7,
            markersize=6,
            label=group.title(),
        )
    ax.set_xticks(x, ["Baseline", "Post", "Follow-up"])
    ax.set_xlabel("Occasion")
    ax.set_ylabel("Well-being score")
    ax.set_title("SWL-S08: Observed group-by-occasion means")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def swl_s09_improvement(root: Path, output: Path) -> None:
    frame = pd.read_csv(root / "data/swl_s09_outcome_distribution_extension.csv")
    table = pd.crosstab(
        frame["support_condition"], frame["clinically_improved"], normalize="index"
    ).reindex(index=["comparison", "intervention"], columns=["yes", "no"])
    x = np.arange(2)
    yes = table["yes"].to_numpy(float)
    no = table["no"].to_numpy(float)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.bar(x, yes, edgecolor="black", facecolor="white", label="Improved")
    ax.bar(
        x,
        no,
        bottom=yes,
        edgecolor="black",
        facecolor="0.70",
        hatch="///",
        label="Not improved",
    )
    ax.set_xticks(x, ["Comparison", "Intervention"])
    ax.set_ylim(0, 1)
    ax.set_xlabel("Support condition")
    ax.set_ylabel("Proportion")
    ax.set_title("SWL-S09: Registered binary outcome")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def swl_s09_burden(root: Path, output: Path) -> None:
    frame = pd.read_csv(root / "data/swl_s09_outcome_distribution_extension.csv")
    groups = [
        frame.loc[
            frame["support_condition"] == group, "recovery_burden_days"
        ].to_numpy(float)
        for group in ["comparison", "intervention"]
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    box = ax.boxplot(
        groups,
        tick_labels=["Comparison", "Intervention"],
        patch_artist=True,
        showfliers=False,
    )
    for patch, hatch in zip(box["boxes"], ["", "///"]):
        patch.set_facecolor("white")
        patch.set_edgecolor("black")
        patch.set_hatch(hatch)
    for key in ["whiskers", "caps", "medians"]:
        for artist in box[key]:
            artist.set_color("black")
    for position, values in enumerate(groups, start=1):
        offsets = np.linspace(-0.11, 0.11, len(values))
        ax.scatter(
            position + offsets,
            values,
            facecolors="none",
            edgecolors="0.35",
            s=12,
            linewidths=0.5,
        )
    ax.set_xlabel("Support condition")
    ax.set_ylabel("Recovery burden (days)")
    ax.set_title("SWL-S09: Positive-skew recovery burden")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def swl_s10_forest(root: Path, output: Path) -> None:
    frame = pd.read_csv(root / "data/swl_s10_replication_program.csv")
    values = analyze_swl_s10(frame)
    effects = frame["observed_cohens_d"].to_numpy(float)
    se = np.sqrt(frame["sampling_variance_d"].to_numpy(float))
    low = effects - 1.96 * se
    high = effects + 1.96 * se
    labels = frame["study_id"].tolist()
    y = np.arange(len(frame), 0, -1)
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.errorbar(
        effects,
        y,
        xerr=np.vstack([effects - low, high - effects]),
        fmt="o",
        color="black",
        ecolor="black",
        capsize=3,
        markersize=5,
    )
    pooled = float(values["fixed_effect_pooled_d"])
    pooled_low = float(values["fixed_effect_ci_95_low"])
    pooled_high = float(values["fixed_effect_ci_95_high"])
    ax.errorbar(
        [pooled],
        [0],
        xerr=[[pooled - pooled_low], [pooled_high - pooled]],
        fmt="D",
        color="black",
        ecolor="black",
        capsize=4,
        markersize=6,
    )
    ax.axvline(0, color="0.35", linestyle="--", linewidth=1)
    ax.set_yticks(list(y) + [0], labels + ["Fixed-effect pooled"])
    ax.set_xlabel("Standardized mean difference")
    ax.set_ylabel("Replication")
    ax.set_title("SWL-S10: Cumulative synthetic evidence")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("outputs/psych_design_swl_s08_s10"),
    )
    args = parser.parse_args()
    root = args.root.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    figures = [
        ("swl_s08_group_time_means.png", "SWL-S08", "primary", swl_s08_group_time),
        (
            "swl_s09_improvement_proportions.png",
            "SWL-S09",
            "categorical",
            swl_s09_improvement,
        ),
        ("swl_s09_recovery_burden.png", "SWL-S09", "rank", swl_s09_burden),
        ("swl_s10_fixed_effect_forest.png", "SWL-S10", "primary", swl_s10_forest),
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
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S08_S10_FIGURES_OK")


if __name__ == "__main__":
    main()
