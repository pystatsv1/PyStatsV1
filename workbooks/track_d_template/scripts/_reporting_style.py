"""Backward-compatible shim for Track D reporting style.

The Track D workbook template historically shipped an implementation of this
module in the workbook itself. The canonical implementation now lives in the
installed PyStatsV1 package at :mod:`pystatsv1.trackd.reporting_style`.

Keeping this shim avoids breaking imports inside the workbook's chapter scripts.
"""

from __future__ import annotations

from pystatsv1.trackd.reporting_style import (
    FigureManifestRow,
    FigureSpec,
    STYLE_CONTRACT,
    ensure_allowed_chart_type,
    figure_manifest_to_frame,
    mpl_context,
    plot_bar,
    plot_ecdf,
    plot_histogram_with_markers,
    plot_time_series,
    plot_waterfall_bridge,
    save_figure,
    style_context,
    write_contract_json,
    write_style_contract_json,
)

__all__ = [
    "STYLE_CONTRACT",
    "FigureSpec",
    "FigureManifestRow",
    "write_style_contract_json",
    "write_contract_json",
    "mpl_context",
    "style_context",
    "save_figure",
    "plot_time_series",
    "plot_bar",
    "plot_histogram_with_markers",
    "plot_ecdf",
    "plot_waterfall_bridge",
    "figure_manifest_to_frame",
    "ensure_allowed_chart_type",
]
