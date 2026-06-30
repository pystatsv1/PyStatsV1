#!/usr/bin/env python3
"""Generate Book 1 teaching figures from versioned synthetic companion CSVs.

The figures are reproducible build outputs. Do not hand-edit the PNG files:
re-run this script after changing the source CSVs or figure specification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "figures_specs.json"
DEFAULT_OUTPUT_ROOT = ROOT / "outputs" / "figures"
DEFAULT_MANIFEST = ROOT / "outputs" / "figure_manifest.json"
GENERATOR_RELATIVE_PATH = "scripts/python/generate_figures.py"

# The plotting parameters deliberately avoid a named style or fixed colours.
# Matplotlib defaults keep the figures plain and make the scripts easy to inspect.
plt.rcParams.update({
    "figure.dpi": 144,
    "savefig.dpi": 144,
    "font.family": "DejaVu Sans",
    "svg.hashsalt": "book1-visual-evidence-v0.1",
})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def read_csv(relative_path: str) -> pd.DataFrame:
    path = ROOT / relative_path
    if not path.exists():
        raise SystemExit(f"missing declared synthetic CSV: {path}")
    return pd.read_csv(path)


def save_figure(figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(
        path,
        format="png",
        dpi=144,
        bbox_inches="tight",
        pad_inches=0.08,
        metadata={"Software": "Psych Stats with Python Book 1 visual evidence v0.1"},
    )
    plt.close(figure)


def fig_03(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    scores = data["test_score"].astype(float)
    mean = float(scores.mean())
    sample_sd = float(scores.std(ddof=1))
    example = float(scores.max())
    z_score = (example - mean) / sample_sd

    figure, axis = plt.subplots(figsize=(7.0, 4.4))
    axis.hist(scores, bins=8, edgecolor="black", alpha=0.75)
    axis.axvline(mean, linestyle="--", linewidth=1.8, label="Sample mean")
    axis.axvline(mean + sample_sd, linestyle=":", linewidth=1.8, label="Mean + 1 SD")
    axis.plot([example], [0], marker="v", markersize=8, linestyle="None", label=f"Example score (z = {z_score:.2f})")
    axis.set_xlabel("Synthetic test score")
    axis.set_ylabel("Number of students")
    axis.set_title("Distribution and one z-score location")
    axis.legend(frameon=False)
    save_figure(figure, output)


def fig_06(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    figure, axis = plt.subplots(figsize=(6.6, 4.4))
    x_values = np.array([0, 1])
    for _, row in data.sort_values("participant_id").iterrows():
        axis.plot(x_values, [row["anxiety_pre"], row["anxiety_post"]], alpha=0.35, linewidth=1.0)
    mean_values = [float(data["anxiety_pre"].mean()), float(data["anxiety_post"].mean())]
    axis.plot(x_values, mean_values, marker="o", linewidth=3.0, label="Sample mean")
    axis.set_xticks(x_values, ["Before workshop", "After workshop"])
    axis.set_ylabel("Synthetic anxiety score")
    axis.set_title("Paired before-to-after scores")
    axis.legend(frameon=False)
    save_figure(figure, output)


def fig_08(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    means = data.groupby(["strategy", "feedback"], sort=True)["test_score"].mean()
    feedback_order = ["no_feedback", "feedback"]
    labels = ["No feedback", "Feedback"]
    figure, axis = plt.subplots(figsize=(6.8, 4.4))
    for strategy in ["standard", "structured"]:
        values = [float(means[(strategy, feedback)]) for feedback in feedback_order]
        axis.plot([0, 1], values, marker="o", linewidth=2.2, label=strategy.replace("_", " ").title())
    axis.set_xticks([0, 1], labels)
    axis.set_ylabel("Synthetic mean test score")
    axis.set_title("Strategy by feedback cell means")
    axis.legend(title="Study strategy", frameon=False)
    save_figure(figure, output)


def fig_09(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    time_order = ["baseline", "week_2", "week_4"]
    time_labels = ["Baseline", "Week 2", "Week 4"]
    wide = data.pivot(index="participant_id", columns="time", values="confidence_score")[time_order]
    figure, axis = plt.subplots(figsize=(7.0, 4.6))
    x_values = np.arange(len(time_order))
    for _, row in wide.sort_index().iterrows():
        axis.plot(x_values, row.to_numpy(dtype=float), alpha=0.27, linewidth=1.0)
    axis.plot(x_values, wide.mean(axis=0).to_numpy(dtype=float), marker="o", linewidth=3.0, label="Sample mean")
    axis.set_xticks(x_values, time_labels)
    axis.set_ylabel("Synthetic confidence score")
    axis.set_title("Within-person confidence trajectories")
    axis.legend(frameon=False)
    save_figure(figure, output)


def fig_10_11(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    x = data["study_hours"].to_numpy(dtype=float)
    y = data["test_score"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    x_line = np.linspace(float(x.min()), float(x.max()), 100)
    figure, axis = plt.subplots(figsize=(7.0, 4.6))
    axis.scatter(x, y, label="Synthetic students")
    axis.plot(x_line, intercept + slope * x_line, linewidth=2.4, label="Least-squares line")
    axis.set_xlabel("Weekly study hours")
    axis.set_ylabel("Synthetic test score")
    axis.set_title("Association and fitted regression line")
    axis.legend(frameon=False)
    save_figure(figure, output)


FIGURE_BUILDERS: dict[str, Callable[[dict, Path], None]] = {
    "fig_03_1_distribution_zscore": fig_03,
    "fig_06_1_paired_change": fig_06,
    "fig_08_1_interaction": fig_08,
    "fig_09_1_repeated_trajectory": fig_09,
    "fig_10_11_1_scatter_regression": fig_10_11,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--only", choices=sorted(FIGURE_BUILDERS), help="Build one declared figure only.")
    args = parser.parse_args()

    spec_document = load_spec()
    if spec_document.get("generator") != GENERATOR_RELATIVE_PATH:
        raise SystemExit("figure specification generator path is not current")
    if spec_document.get("synthetic_data_only") is not True:
        raise SystemExit("figure specification must require synthetic data only")

    figures = spec_document.get("figures", [])
    selected = [figure for figure in figures if args.only is None or figure["figure_id"] == args.only]
    if not selected:
        raise SystemExit("no declared figures selected")

    args.output_root.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    for figure_spec in selected:
        figure_id = figure_spec["figure_id"]
        builder = FIGURE_BUILDERS.get(figure_id)
        if builder is None:
            raise SystemExit(f"no builder registered for {figure_id}")
        source_csv = figure_spec["source_csv"]
        if not source_csv.startswith("data/") or not (ROOT / source_csv).is_file():
            raise SystemExit(f"{figure_id}: source_csv must be a versioned companion CSV")
        output_path = args.output_root / Path(figure_spec["output_filename"]).name
        builder(figure_spec, output_path)
        manifest_rows.append({
            "figure_id": figure_id,
            "chapter_placement": figure_spec["chapter_placement"],
            "source_csv": source_csv,
            "script": GENERATOR_RELATIVE_PATH,
            "output_filename": str(output_path.relative_to(args.output_root.parent if args.output_root.name == "figures" else args.output_root.parent)).replace("\\", "/"),
            "sha256": sha256(output_path),
            "alt_text": figure_spec["alt_text"],
            "caption": figure_spec["caption"],
            "does_not_prove": figure_spec["does_not_prove"],
            "synthetic_data_only": True,
        })

    manifest = {
        "schema_version": "book1-visual-evidence-manifest-v0.1",
        "companion_version": spec_document["companion_version"],
        "generator": GENERATOR_RELATIVE_PATH,
        "synthetic_data_only": True,
        "matplotlib_version": matplotlib.__version__,
        "figures": manifest_rows,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BOOK1_COMPANION_FIGURES_OK figures={len(manifest_rows)} manifest={args.manifest}")


if __name__ == "__main__":
    main()
