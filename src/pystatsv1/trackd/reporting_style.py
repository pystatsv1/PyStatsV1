# SPDX-License-Identifier: MIT
"""Shared plotting/reporting helpers.

Track D Chapter 9 introduces a *style contract* for figures and small reports.
This module centralizes the rules so later chapters can reuse them.

Design goals
------------
- Matplotlib-only (no seaborn)
- Deterministic output filenames and metadata
- Guardrails against misleading axes (especially for bar charts)
- Simple defaults suitable for ReadTheDocs screenshots and printing

The "style contract" is intentionally conservative; it favors clarity over
flash. Downstream chapters can extend it, but should keep the core rules.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
from contextlib import contextmanager
import matplotlib as mpl
import numpy as np

# Matplotlib is an optional dependency for some repo users.
# Track D chapters require it, so we import lazily in functions where possible.

STYLE_CONTRACT: dict[str, Any] = {
    "version": "1.0",
    "allowed_chart_types": [
        "line",
        "bar",
        "histogram",
        "ecdf",
        "box",
        "scatter",
        "waterfall_bridge",
    ],
    "labeling_rules": {
        "title_required": True,
        "axis_labels_required": True,
        "units_in_labels": True,
        "use_month_tick_labels": "YYYY-MM",
        "legend_only_if_multiple_series": True,
        "caption_required_in_manifest": True,
    },
    "anti_misleading_axes": {
        "bar_charts_start_at_zero": True,
        "explicit_note_if_y_truncated": True,
        "show_zero_line_for_ratios": True,
        "avoid_dual_axes": True,
    },
    "distribution_guidance": {
        "for_skewed_distributions": [
            "histogram + vertical lines for mean and median",
            "ECDF (or quantile plot) to reveal tails",
            "report key quantiles (p50, p75, p90, p95 if available)",
        ]
    },
    "file_format": {"type": "png", "dpi": 150},
    "figure_sizes": {
        "time_series": [10.0, 4.0],
        "distribution": [7.5, 4.5],
    },
}


# Minimal matplotlib rcParams for a consistent, non-misleading reporting look.
# NOTE: We intentionally avoid specifying colors so matplotlib defaults apply.
_REPORTING_RC: dict[str, object] = {
    "figure.dpi": 120,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "axes.grid": True,
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
}


@contextmanager
def style_context():
    """Context manager to apply the reporting style contract to matplotlib figures."""
    with mpl.rc_context(rc=_REPORTING_RC):
        yield



@dataclass(frozen=True)
class FigureSpec:
    """Minimal spec used when saving figures (validation + metadata)."""

    chart_type: str
    title: str
    caption: str = ""
    x_label: str = ""
    y_label: str = ""
    data_source: str = ""
    notes: str = ""


@dataclass(frozen=True)
class FigureManifestRow:
    """One row in the Chapter 9 figure manifest CSV."""

    filename: str
    chart_type: str
    title: str
    x_label: str
    y_label: str
    guardrail_note: str
    data_source: str



def write_style_contract_json(outpath: Path) -> None:
    """Write the global style contract to a JSON file."""

    outpath.write_text(json.dumps(STYLE_CONTRACT, indent=2), encoding="utf-8")


def write_contract_json(outpath: Path) -> None:
    """Write the global style contract to a JSON file."""
    outpath.write_text(json.dumps(STYLE_CONTRACT, indent=2), encoding="utf-8")



def _mpl():
    """Import matplotlib with a non-interactive backend."""

    import matplotlib

    # Ensure headless operation for CI / tests.
    matplotlib.use("Agg", force=True)

    import matplotlib.pyplot as plt

    return matplotlib, plt


def mpl_context():
    """Context manager that applies a lightweight, consistent style."""

    matplotlib, plt = _mpl()

    # A minimal rcParams set: keep things readable without over-styling.
    rc = {
        "figure.dpi": int(STYLE_CONTRACT["file_format"]["dpi"]),
        "savefig.dpi": int(STYLE_CONTRACT["file_format"]["dpi"]),
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }

    return matplotlib.rc_context(rc)


def save_figure(fig, outpath: Path, spec: FigureSpec | None = None) -> None:
    """Save and close a Matplotlib figure deterministically.

    If spec is provided, enforce allowed chart types.
    """
    if spec is not None:
        ensure_allowed_chart_type(spec.chart_type)

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")

    # Avoid memory leaks in test runs.
    _, plt = _mpl()
    plt.close(fig)



def _format_month_ticks(ax, months: list[str]) -> None:
    """Format x-axis ticks for YYYY-MM month labels."""

    # Show at most ~8 ticks; for longer series, reduce tick density.
    n = len(months)
    if n <= 8:
        step = 1
    elif n <= 18:
        step = 2
    else:
        step = 3

    ticks = list(range(0, n, step))
    ax.set_xticks(ticks)
    ax.set_xticklabels([months[i] for i in ticks], rotation=45, ha="right")


def _enforce_bar_zero_baseline(ax) -> None:
    """Enforce y-axis baseline at zero for bar charts."""

    y0, y1 = ax.get_ylim()
    if y0 > 0:
        ax.set_ylim(0.0, y1)
    elif y1 < 0:
        ax.set_ylim(y0, 0.0)


def plot_time_series(
    df,
    x: str,
    series: dict[str, str],
    title: str,
    x_label: str,
    y_label: str,
    figsize: tuple[float, float] | None = None,
    show_zero_line: bool = False,
):
    """Create a standard time-series line chart.

    Parameters
    ----------
    df:
        Dataframe with columns including x and all series columns.
    x:
        Column name for x-axis (typically month).
    series:
        Mapping of legend label -> column name.
    show_zero_line:
        If True, draw a horizontal line at y=0 (useful for ratios/growth).
    """

    _, plt = _mpl()

    if figsize is None:
        w, h = STYLE_CONTRACT["figure_sizes"]["time_series"]
        figsize = (float(w), float(h))

    fig, ax = plt.subplots(figsize=figsize)

    months = [str(m) for m in df[x].tolist()]
    x_idx = np.arange(len(months))

    for label, col in series.items():
        ax.plot(x_idx, df[col].astype(float).to_numpy(), marker="o", linewidth=1.5, label=label)

    if show_zero_line:
        ax.axhline(0.0, linewidth=1.0)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    _format_month_ticks(ax, months)

    if len(series) > 1:
        ax.legend(loc="best")

    return fig


def plot_bar(
    df,
    x: str,
    y: str,
    title: str,
    x_label: str,
    y_label: str,
    figsize: tuple[float, float] | None = None,
):
    """Create a standard bar chart with a zero baseline."""

    _, plt = _mpl()

    if figsize is None:
        w, h = STYLE_CONTRACT["figure_sizes"]["time_series"]
        figsize = (float(w), float(h))

    fig, ax = plt.subplots(figsize=figsize)

    months = [str(m) for m in df[x].tolist()]
    x_idx = np.arange(len(months))

    ax.bar(x_idx, df[y].astype(float).to_numpy())

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    _format_month_ticks(ax, months)
    _enforce_bar_zero_baseline(ax)

    return fig


def _ecdf(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if v.size == 0:
        return np.array([]), np.array([])
    v = np.sort(v)
    y = np.arange(1, v.size + 1, dtype=float) / float(v.size)
    return v, y


def plot_histogram_with_markers(
    values: Iterable[float],
    title: str,
    x_label: str,
    y_label: str,
    markers: dict[str, float] | None = None,
    figsize: tuple[float, float] | None = None,
):
    """Histogram with optional vertical markers (e.g., mean/median)."""

    _, plt = _mpl()

    if figsize is None:
        w, h = STYLE_CONTRACT["figure_sizes"]["distribution"]
        figsize = (float(w), float(h))

    v = np.asarray(list(values), dtype=float)
    v = v[~np.isnan(v)]

    fig, ax = plt.subplots(figsize=figsize)

    if v.size > 0:
        ax.hist(v, bins="auto")

    if markers:
        for label, x0 in markers.items():
            if np.isfinite(x0):
                ax.axvline(float(x0), linestyle="--", linewidth=1.2, label=label)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if markers and len(markers) > 0:
        ax.legend(loc="best")

    return fig


def plot_ecdf(
    values: Iterable[float],
    title: str,
    x_label: str,
    y_label: str,
    markers: dict[str, float] | None = None,
    figsize: tuple[float, float] | None = None,
):
    """ECDF plot with optional vertical markers."""

    _, plt = _mpl()

    if figsize is None:
        w, h = STYLE_CONTRACT["figure_sizes"]["distribution"]
        figsize = (float(w), float(h))

    v = np.asarray(list(values), dtype=float)
    x, y = _ecdf(v)

    fig, ax = plt.subplots(figsize=figsize)

    if x.size > 0:
        ax.plot(x, y, marker=".", linestyle="none")

    if markers:
        for label, x0 in markers.items():
            if np.isfinite(x0):
                ax.axvline(float(x0), linestyle="--", linewidth=1.2, label=label)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_ylim(0.0, 1.0)

    if markers and len(markers) > 0:
        ax.legend(loc="best")

    return fig


def plot_waterfall_bridge(
    start_label: str,
    end_label: str,
    start_value: float,
    end_value: float,
    components: list[tuple[str, float]],
    title: str,
    y_label: str,
    x_label: str = "Component",
    figsize: tuple[float, float] | None = None,
):
    """Create a variance waterfall / bridge chart (start -> end via additive components).

    Guardrails
    ---------
    - Deterministic structure: explicit start and end totals plus additive components.
    - Printer-safe encoding: hatch patterns distinguish positive vs negative deltas.
    - Zero line included; y-limits padded to reduce truncation temptation.

    Notes
    -----
    The caller is responsible for choosing defensible components. Any residual
    can be included as an "Other / rounding" component to reconcile exactly.
    """

    _, plt = _mpl()

    if figsize is None:
        w, h = STYLE_CONTRACT["figure_sizes"]["time_series"]
        figsize = (float(w), float(h))

    labels = [start_label] + [name for name, _ in components] + [end_label]

    # Running totals after each component (for connectors and y-range).
    running = float(start_value)
    totals = [running]
    for _, delta in components:
        running += float(delta)
        totals.append(running)
    totals.append(float(end_value))

    fig, ax = plt.subplots(figsize=figsize)

    # Start total
    ax.bar(0, float(start_value), edgecolor="black", linewidth=0.8)

    # Component deltas
    running = float(start_value)
    for i, (_, delta) in enumerate(components, start=1):
        d = float(delta)
        new_total = running + d

        if d >= 0:
            bottom = running
            height = d
            hatch = "//"
        else:
            bottom = new_total
            height = -d
            hatch = "\\"

        ax.bar(i, height, bottom=bottom, hatch=hatch, edgecolor="black", linewidth=0.8)
        running = new_total

    # End total
    ax.bar(len(labels) - 1, float(end_value), edgecolor="black", linewidth=0.8)

    # Connectors between bars (running totals)
    running = float(start_value)
    for i, (_, delta) in enumerate(components, start=1):
        ax.plot([i - 0.4, i + 0.4], [running, running], linewidth=1.0)
        running += float(delta)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xticks(list(range(len(labels))))
    ax.set_xticklabels(labels, rotation=0)
    ax.axhline(0.0, linewidth=1.0)

    def _fmt(v: float) -> str:
        return f"{v:,.0f}"

    # Annotate start/end totals
    ax.text(0, float(start_value), _fmt(float(start_value)), ha="center", va="bottom")
    ax.text(len(labels) - 1, float(end_value), _fmt(float(end_value)), ha="center", va="bottom")

    # Annotate component deltas
    running = float(start_value)
    for i, (_, delta) in enumerate(components, start=1):
        d = float(delta)
        y = (running + d) if d >= 0 else running
        ax.text(i, y, f"{d:+,.0f}", ha="center", va="bottom")
        running += d

    # Pad y-limits (anti-truncation guardrail)
    lo = min([0.0] + totals)
    hi = max([0.0] + totals)
    span = hi - lo
    pad = 0.10 * span if span > 0 else 1.0
    ax.set_ylim(lo - pad, hi + pad)

    return fig


def figure_manifest_to_frame(specs: list[FigureSpec]):
    import pandas as pd

    return pd.DataFrame([asdict(s) for s in specs])


def ensure_allowed_chart_type(chart_type: str) -> None:
    allowed = set(STYLE_CONTRACT["allowed_chart_types"])
    if chart_type not in allowed:
        raise ValueError(f"chart_type must be one of {sorted(allowed)}; got {chart_type!r}")
