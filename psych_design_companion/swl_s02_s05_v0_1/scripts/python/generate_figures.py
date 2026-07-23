#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from studies import STUDY_IDS, STUDY_CONFIG, load_tracked_dataset, sha256


def mean_ci(values: np.ndarray) -> tuple[float, float]:
    mean = float(values.mean())
    se = float(values.std(ddof=1) / np.sqrt(len(values)))
    return mean, 1.96 * se


def plot_s02(root: Path, output: Path) -> None:
    df = load_tracked_dataset(root, "SWL-S02")
    levels = ["standard_routine", "structured_routine"]
    stats = [
        mean_ci(
            df.loc[
                df["study_routine_group"] == level,
                "post_session_performance",
            ].to_numpy(dtype=float)
        )
        for level in levels
    ]
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.errorbar(
        [0, 1],
        [value[0] for value in stats],
        yerr=[value[1] for value in stats],
        fmt="o",
        color="black",
        capsize=5,
    )
    ax.set_xticks([0, 1], ["Standard routine", "Structured routine"])
    ax.set_ylabel("Post-session performance")
    ax.set_title("SWL-S02: Group means and 95% CIs")
    fig.tight_layout()
    fig.savefig(output, dpi=300)
    plt.close(fig)


def plot_s03(root: Path, output: Path) -> None:
    df = load_tracked_dataset(root, "SWL-S03")
    wide = df.pivot(
        index="participant_id",
        columns="occasion",
        values="academic_confidence",
    )
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    for _, row in wide.iterrows():
        ax.plot([0, 1], [row["pre"], row["post"]], color="0.75", linewidth=0.7)
    means = [wide["pre"].mean(), wide["post"].mean()]
    ax.plot([0, 1], means, color="black", marker="o", linewidth=2.0)
    ax.set_xticks([0, 1], ["Pre", "Post"])
    ax.set_ylabel("Academic confidence")
    ax.set_title("SWL-S03: Linked pre/post change")
    fig.tight_layout()
    fig.savefig(output, dpi=300)
    plt.close(fig)


def plot_s04(root: Path, output: Path) -> None:
    df = load_tracked_dataset(root, "SWL-S04")
    levels = [
        "standard_support",
        "guided_practice",
        "guided_practice_plus_feedback",
    ]
    display = ["Standard", "Guided", "Guided + feedback"]
    stats = [
        mean_ci(
            df.loc[
                df["support_condition"] == level,
                "assessment_performance",
            ].to_numpy(dtype=float)
        )
        for level in levels
    ]
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.errorbar(
        range(3),
        [value[0] for value in stats],
        yerr=[value[1] for value in stats],
        fmt="o",
        color="black",
        capsize=5,
    )
    ax.set_xticks(range(3), display)
    ax.set_ylabel("Assessment performance")
    ax.set_title("SWL-S04: Condition means and 95% CIs")
    fig.tight_layout()
    fig.savefig(output, dpi=300)
    plt.close(fig)


def plot_s05(root: Path, output: Path) -> None:
    df = load_tracked_dataset(root, "SWL-S05")
    feedback_levels = ["no_feedback", "explanatory_feedback"]
    strategies = ["rereading", "retrieval_practice"]
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    for index, strategy in enumerate(strategies):
        means = [
            df.loc[
                (df["study_strategy"] == strategy)
                & (df["feedback_condition"] == feedback),
                "assessment_performance",
            ].mean()
            for feedback in feedback_levels
        ]
        ax.plot(
            [0, 1],
            means,
            color="black",
            linestyle="-" if index == 0 else "--",
            marker="o" if index == 0 else "s",
            label=strategy.replace("_", " ").title(),
        )
    ax.set_xticks([0, 1], ["No feedback", "Explanatory feedback"])
    ax.set_ylabel("Assessment performance")
    ax.set_title("SWL-S05: Strategy × Feedback interaction")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=300)
    plt.close(fig)


PLOTTERS = {
    "SWL-S02": plot_s02,
    "SWL-S03": plot_s03,
    "SWL-S04": plot_s04,
    "SWL-S05": plot_s05,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output_root = (
        args.output_root.resolve()
        if args.output_root
        else root / "outputs" / "figures"
    )
    output_root.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    for study_id in STUDY_IDS:
        output = output_root / f"{study_id.lower().replace('-', '_')}.png"
        PLOTTERS[study_id](root, output)
        manifest.append(
            {
                "study_id": study_id,
                "figure_type": STUDY_CONFIG[study_id]["figure_type"],
                "output": output.name,
                "sha256": sha256(output),
                "dpi": 300,
                "grayscale": True,
            }
        )
    manifest_path = output_root / "FIGURE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(
            {"contract_version": "0.1", "figures": manifest},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {manifest_path}")
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S02_S05_FIGURES_OK")


if __name__ == "__main__":
    main()
