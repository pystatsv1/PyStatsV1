#!/usr/bin/env python3
"""Generate source-faithful, grayscale Book 1 v0.2 public-release figures.

The PNGs are reproducible outputs. Do not hand-edit them. This public
Companion v0.2 bundle preserves the historical v0.1 companion while providing
source-faithful evidence figures for the released launcher workflow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
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
PRINT_PROFILE = "high-contrast-grayscale"
PUBLIC_RELEASE_STATUS = "public_release"
PLOT_DPI = 360

BLACK = "0.0"
DARK_GRAY = "0.28"
MID_GRAY = "0.50"
LIGHT_GRAY = "0.76"

plt.rcParams.update({
    "figure.dpi": PLOT_DPI,
    "savefig.dpi": PLOT_DPI,
    "font.family": "DejaVu Sans",
    "svg.hashsalt": "book1-visual-evidence-v0.2",
})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def load_spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def read_csv(relative_path: str) -> pd.DataFrame:
    path = ROOT / relative_path
    if not path.is_file():
        raise SystemExit(f"missing declared synthetic CSV: {path}")
    return pd.read_csv(path)


def save_figure(figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(
        path,
        format="png",
        dpi=PLOT_DPI,
        bbox_inches="tight",
        pad_inches=0.08,
        facecolor="white",
        metadata={"Software": "Psych Stats with Python Book 1 visual evidence v0.2 public release"},
    )
    plt.close(figure)


def fig_03(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    scores = data["test_score"].astype(float)
    mean = float(scores.mean())
    sample_sd = float(scores.std(ddof=1))
    example = float(scores.max())
    z_score = (example - mean) / sample_sd
    figure, axis = plt.subplots(figsize=(7.5, 5.2))
    axis.hist(scores, bins=8, edgecolor=BLACK, color=LIGHT_GRAY)
    axis.axvline(mean, color=BLACK, linestyle="--", linewidth=1.8, label="Sample mean")
    axis.axvline(mean + sample_sd, color=DARK_GRAY, linestyle=":", linewidth=2.0, label="Mean + 1 SD")
    axis.plot([example], [0], color=BLACK, marker="v", markersize=8, linestyle="None", label=f"Example score (z = {z_score:.2f})")
    axis.set_xlabel("Synthetic test score")
    axis.set_ylabel("Number of students")
    axis.set_title("Distribution and one z-score location")
    axis.legend(frameon=False)
    save_figure(figure, output)


def fig_06(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    figure, axis = plt.subplots(figsize=(7.2, 5.2))
    x_values = np.array([0, 1])
    for _, row in data.sort_values("participant_id").iterrows():
        axis.plot(x_values, [row["anxiety_pre"], row["anxiety_post"]], color=LIGHT_GRAY, linewidth=1.0)
    mean_values = [float(data["anxiety_pre"].mean()), float(data["anxiety_post"].mean())]
    axis.plot(x_values, mean_values, color=BLACK, marker="o", linewidth=3.0, label="Sample mean")
    axis.set_xticks(x_values, ["Before workshop", "After workshop"])
    axis.set_ylabel("Synthetic anxiety score")
    axis.set_title("Paired before-to-after scores")
    axis.legend(frameon=False)
    save_figure(figure, output)


def fig_08(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    means = data.groupby(["strategy", "feedback"], sort=True)["test_score"].mean()
    feedback_order = ["no_feedback", "feedback"]
    figure, axis = plt.subplots(figsize=(7.2, 5.2))
    style = {
        "standard": {"color": BLACK, "marker": "o", "linestyle": "-", "label": "Standard"},
        "structured": {"color": DARK_GRAY, "marker": "s", "linestyle": "--", "label": "Structured"},
    }
    for strategy in ["standard", "structured"]:
        values = [float(means[(strategy, feedback)]) for feedback in feedback_order]
        axis.plot([0, 1], values, linewidth=2.5, **style[strategy])
    axis.set_xticks([0, 1], ["No feedback", "Feedback"])
    axis.set_ylabel("Synthetic mean test score")
    axis.set_title("Strategy by feedback cell means")
    axis.legend(title="Study strategy", frameon=False)
    save_figure(figure, output)


def fig_09(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    time_order = ["baseline", "week_2", "week_4"]
    time_labels = ["Baseline", "Week 2", "Week 4"]
    wide = data.pivot(index="participant_id", columns="time", values="confidence_score")[time_order]
    figure, axis = plt.subplots(figsize=(7.5, 5.3))
    x_values = np.arange(len(time_order))
    for _, row in wide.sort_index().iterrows():
        axis.plot(x_values, row.to_numpy(dtype=float), color=LIGHT_GRAY, linewidth=1.0)
    axis.plot(x_values, wide.mean(axis=0).to_numpy(dtype=float), color=BLACK, marker="o", linewidth=3.0, label="Sample mean")
    axis.set_xticks(x_values, time_labels)
    axis.set_ylabel("Synthetic confidence score")
    axis.set_title("Within-person confidence trajectories")
    axis.legend(frameon=False)
    save_figure(figure, output)


def fig_10(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    figure, axis = plt.subplots(figsize=(7.5, 5.2))
    axis.scatter(data["study_hours"], data["test_score"], color=MID_GRAY, edgecolors=BLACK, linewidths=0.45, marker="o", label="Synthetic students")
    axis.set_xlabel("Weekly study hours")
    axis.set_ylabel("Synthetic test score")
    axis.set_title("Association before a correlation summary")
    axis.legend(frameon=False)
    save_figure(figure, output)


def fig_11(spec: dict, output: Path) -> None:
    data = read_csv(spec["source_csv"])
    x = data["study_hours"].to_numpy(dtype=float)
    y = data["test_score"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    x_line = np.linspace(float(x.min()), float(x.max()), 100)
    figure, axis = plt.subplots(figsize=(7.5, 5.2))
    axis.scatter(x, y, color=MID_GRAY, edgecolors=BLACK, linewidths=0.45, marker="o", label="Synthetic students")
    axis.plot(x_line, intercept + slope * x_line, color=BLACK, linewidth=2.7, linestyle="-", label="Least-squares line")
    axis.set_xlabel("Weekly study hours")
    axis.set_ylabel("Synthetic test score")
    axis.set_title("Regression teaching data and fitted line")
    axis.legend(frameon=False)
    save_figure(figure, output)


FIGURE_BUILDERS: dict[str, Callable[[dict, Path], None]] = {
    "fig_03_1_distribution_zscore": fig_03,
    "fig_06_1_paired_change": fig_06,
    "fig_08_1_interaction": fig_08,
    "fig_09_1_repeated_trajectory": fig_09,
    "fig_10_1_correlation_scatter": fig_10,
    "fig_11_1_regression_scatter": fig_11,
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
    if spec_document.get("companion_version") != "v0.2":
        raise SystemExit("public v0.2 figure specification must declare Companion v0.2")
    release_status = spec_document.get("release_status")
    if release_status != PUBLIC_RELEASE_STATUS:
        raise SystemExit("public release status must remain explicit")
    if spec_document.get("synthetic_data_only") is not True:
        raise SystemExit("figure specification must require synthetic data only")
    if spec_document.get("print_profile") != PRINT_PROFILE:
        raise SystemExit("public figure specification must require grayscale print profile")

    figures = spec_document.get("figures", [])
    selected = [row for row in figures if args.only is None or row["figure_id"] == args.only]
    if not selected:
        raise SystemExit("no declared figures selected")

    args.output_root.mkdir(parents=True, exist_ok=True)
    rows = []
    for figure_spec in selected:
        figure_id = figure_spec["figure_id"]
        builder = FIGURE_BUILDERS.get(figure_id)
        if builder is None:
            raise SystemExit(f"no builder registered for {figure_id}")
        source_csv = figure_spec["source_csv"]
        if not source_csv.startswith("data/") or not (ROOT / source_csv).is_file():
            raise SystemExit(f"{figure_id}: source_csv must be a versioned companion CSV")
        contract = figure_spec.get("analysis_contract", {})
        if not contract.get("analysis_script") or not contract.get("python_result"):
            raise SystemExit(f"{figure_id}: analysis contract must name script and Python result")
        output = args.output_root / Path(figure_spec["output_filename"]).name
        builder(figure_spec, output)
        width, height = png_dimensions(output)
        print_width = float(spec_document["planned_print_width_inches"])
        print_height = float(spec_document["planned_print_height_inches"])
        effective_width_ppi = width / print_width
        effective_height_ppi = height / print_height
        rows.append({
            "figure_id": figure_id,
            "chapter_placement": figure_spec["chapter_placement"],
            "source_csv": source_csv,
            "script": GENERATOR_RELATIVE_PATH,
            "output_filename": str(output.relative_to(args.output_root.parent)).replace("\\", "/"),
            "sha256": sha256(output),
            "pixel_width": width,
            "pixel_height": height,
            "planned_print_width_inches": print_width,
            "planned_print_height_inches": print_height,
            "minimum_effective_ppi": int(spec_document["minimum_effective_ppi"]),
            "effective_ppi_width": round(effective_width_ppi, 2),
            "effective_ppi_height": round(effective_height_ppi, 2),
            "print_profile": PRINT_PROFILE,
            "alt_text": figure_spec["alt_text"],
            "caption": figure_spec["caption"],
            "does_not_prove": figure_spec["does_not_prove"],
            "analysis_contract": contract,
            "synthetic_data_only": True,
        })

    manifest = {
        "schema_version": "book1-visual-evidence-manifest-v0.2",
        "companion_version": "v0.2",
        "release_status": release_status,
        "generator": GENERATOR_RELATIVE_PATH,
        "synthetic_data_only": True,
        "print_profile": PRINT_PROFILE,
        "matplotlib_version": matplotlib.__version__,
        "figures": rows,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PYSTATSV1_BOOK1_V02_PUBLIC_FIGURES_OK figures={len(rows)} manifest={args.manifest}")


if __name__ == "__main__":
    main()
