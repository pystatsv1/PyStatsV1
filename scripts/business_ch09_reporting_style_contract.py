# SPDX-License-Identifier: MIT
# business_ch09_reporting_style_contract.py
"""Track D Business Chapter 9: Plotting/reporting style contract + example outputs.

Chapter 9 defines a small, reusable plotting/reporting *style contract* for
Track D and produces example figures that comply with it.

Outputs (written to outdir)
---------------------------
- ch09_style_contract.json
- ch09_figures_manifest.csv
- ch09_summary.json
- figures/
    - kpi_revenue_net_income_line.png
    - kpi_margins_line.png
    - ar_dso_line.png
    - ar_days_hist.png
    - ar_days_ecdf.png

Design notes
------------
- Matplotlib only (no seaborn)
- Deterministic file names
- “Axis guardrails”: bar charts start at 0; truncated axes must be explicit
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ._cli import base_parser
from ._reporting_style import (
    FigureManifestRow,
    FigureSpec,
    plot_ecdf,
    plot_histogram_with_markers,
    save_figure,
    style_context,
    write_contract_json,
)
from .business_ch08_descriptive_statistics_financial_performance import analyze_ch08


@dataclass(frozen=True)
class Ch09Outputs:
    contract_path: Path
    manifest_path: Path
    memo_path: Path
    summary_path: Path
    figures_dir: Path
    figure_paths: list[Path]


def _ensure_outdir(outdir: Path) -> tuple[Path, Path, Path, Path, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    contract_path = outdir / "ch09_style_contract.json"
    manifest_path = outdir / "ch09_figures_manifest.csv"
    memo_path = outdir / "ch09_executive_memo.md"
    summary_path = outdir / "ch09_summary.json"
    return contract_path, manifest_path, memo_path, summary_path, figures_dir


def _make_executive_memo(kpi: pd.DataFrame, ar_monthly: pd.DataFrame, ar_days_stats: pd.DataFrame) -> str:
    """Create a compact, deterministic markdown memo (10 bullets max).

    Chapter 9 embeds *ethics guardrails* directly in the memo generator so the
    output is harder to misuse in executive settings.
    """
    lines: list[str] = []
    lines.append("# Chapter 9 — Executive memo (example)\n")
    lines.append(
        "This memo is generated from the synthetic NSO v1 data and exists to demonstrate "
        "consistent reporting style (not to make real-world claims).\n"
    )

    # --- Ethics guardrails (deterministic) ---
    # Percent metrics (margins, growth) can be misleading when the denominator is tiny.
    # We flag percent metrics when the revenue base is "small" relative to the series.
    PCT_DENOM_ABS_MIN: float = 1_000.0
    PCT_DENOM_REL_MIN: float = 0.05  # 5% of typical (median) revenue

    # DSO is a risk metric; extreme values are flagged neutrally as "needs investigation".
    DSO_NEEDS_INVESTIGATION_DAYS: float = 75.0

    typical_revenue = 0.0
    if not kpi.empty and "revenue" in kpi.columns:
        s = (
            pd.to_numeric(kpi["revenue"], errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
            .astype(float)
        )
        if len(s) > 0:
            typical_revenue = float(s.median())

    def _is_small_denominator(denom: float | int | None, typical: float) -> bool:
        if denom is None:
            return True
        d = float(denom)
        if not np.isfinite(d):
            return True
        floor = max(PCT_DENOM_ABS_MIN, PCT_DENOM_REL_MIN * float(typical))
        return d < floor

    def _pct_note_if_unstable(denom: float | int | None, typical: float) -> str:
        if _is_small_denominator(denom=denom, typical=typical):
            return " (flag: denominator small; interpret with caution)"
        return ""

    if not kpi.empty:
        latest = kpi.iloc[-1]
        prev = kpi.iloc[-2] if len(kpi) > 1 else latest
        lines.append(f"- Latest month: **{latest['month']}**")
        lines.append(f"- Revenue: **{latest['revenue']:.0f}** (prev {prev['revenue']:.0f})")
        lines.append(f"- Net income: **{latest['net_income']:.0f}** (prev {prev['net_income']:.0f})")
        if pd.notna(latest.get("gross_margin_pct", pd.NA)):
            note = _pct_note_if_unstable(denom=latest.get("revenue"), typical=typical_revenue)
            lines.append(f"- Gross margin: **{latest['gross_margin_pct']:.1%}**{note}")
        if pd.notna(latest.get("net_margin_pct", pd.NA)):
            note = _pct_note_if_unstable(denom=latest.get("revenue"), typical=typical_revenue)
            lines.append(f"- Net margin: **{latest['net_margin_pct']:.1%}**{note}")
        if pd.notna(latest.get("revenue_growth_pct", pd.NA)):
            note = _pct_note_if_unstable(denom=prev.get("revenue"), typical=typical_revenue)
            lines.append(f"- MoM revenue growth: **{latest['revenue_growth_pct']:.1%}**{note}")

    if not ar_monthly.empty and "dso" in ar_monthly.columns:
        latest_ar = ar_monthly.iloc[-1]
        dso = latest_ar.get("dso")
        cr = latest_ar.get("collections_rate")
        if pd.notna(dso):
            note = ""
            if float(dso) >= DSO_NEEDS_INVESTIGATION_DAYS:
                note = " (flag: unusually high; needs investigation)"
            elif float(dso) < 0:
                note = " (flag: negative; check data/definitions)"
            lines.append(f"- DSO (approx): **{float(dso):.1f} days**{note}")
        if pd.notna(cr):
            lines.append(f"- Collections rate: **{float(cr):.1%}**")

    # Tail risk from payment lag distribution
    if not ar_days_stats.empty:
        all_row = ar_days_stats.loc[ar_days_stats["customer"] == "ALL"]
        if not all_row.empty:
            r = all_row.iloc[0]
            if pd.notna(r.get("median_days", pd.NA)):
                lines.append(f"- Payment lag median: **{float(r['median_days']):.0f} days**")
            if pd.notna(r.get("p90_days", pd.NA)):
                lines.append(f"- Payment lag p90 (tail): **{float(r['p90_days']):.0f} days**")

    # Keep it to ~10 bullets for a one-page feel
    bullet_lines = [ln for ln in lines if ln.startswith("-")]
    if len(bullet_lines) > 10:
        trimmed: list[str] = []
        kept = 0
        for ln in lines:
            if ln.startswith("-"):
                kept += 1
                if kept > 10:
                    continue
            trimmed.append(ln)
        lines = trimmed

    return "\n".join(lines).strip() + "\n"


def _month_ticks(ax: Any, months: list[str], step: int = 2) -> None:
    """Readable month ticks for short monthly series."""
    if not months:
        return
    idx = np.arange(len(months))
    ticks = idx[::step]
    labels = [months[i] for i in ticks]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=0, ha="center")


def _plot_time_series(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str],
    title: str,
    x_label: str,
    y_label: str,
    show_zero_line: bool = False,
) -> plt.Figure:
    months = df[x_col].astype(str).tolist()
    x = np.arange(len(months))

    fig, ax = plt.subplots(figsize=(10, 4))
    for col in y_cols:
        ax.plot(x, df[col].astype(float).to_numpy(), marker="o", linewidth=2, label=col)

    if show_zero_line:
        ax.axhline(0.0, linewidth=1, linestyle="--")

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    _month_ticks(ax, months, step=2)
    ax.grid(True, axis="y")
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def analyze_ch09(datadir: Path, outdir: Path, seed: int = 123) -> Ch09Outputs:
    """Run Chapter 9 and write contract + example figures."""
    contract_path, manifest_path, memo_path, summary_path, figures_dir = _ensure_outdir(Path(outdir))

    # 1) Produce the style contract JSON (the “rules” later chapters will follow)
    write_contract_json(contract_path)

    # 2) Use Chapter 8 to get consistent inputs (KPIs + A/R metrics + A/R day slices)
    ch08 = analyze_ch08(datadir=Path(datadir), outdir=None, seed=seed)
    kpi = ch08.gl_kpi_monthly.copy()
    ar_month = ch08.ar_monthly_metrics.copy()
    slices = ch08.ar_payment_slices.copy()

    ar_days_stats = ch08.ar_days_stats.copy()

    # 3) Build figures (each must comply with the contract)
    manifest: list[FigureManifestRow] = []
    figure_paths: list[Path] = []

    # KPI: Revenue + Net income
    with style_context():
        fig = _plot_time_series(
            kpi,
            x_col="month",
            y_cols=["revenue", "net_income"],
            title="Monthly revenue and net income",
            x_label="Month",
            y_label="Amount (currency units)",
            show_zero_line=True,
        )
        path = figures_dir / "kpi_revenue_net_income_line.png"
        save_figure(fig, path, FigureSpec(chart_type="line", title="Monthly revenue and net income"))
        plt.close(fig)
    manifest.append(
        FigureManifestRow(
            filename=path.name,
            chart_type="line",
            title="Monthly revenue and net income",
            x_label="Month",
            y_label="Amount (currency units)",
            guardrail_note="Line charts may use non-zero y-limits; include a 0 reference line when helpful.",
            data_source="gl_kpi_monthly.csv",
        )
    )
    figure_paths.append(path)

    # KPI: margins
    with style_context():
        fig = _plot_time_series(
            kpi,
            x_col="month",
            y_cols=["gross_margin_pct", "net_margin_pct"],
            title="Gross and net margin (%)",
            x_label="Month",
            y_label="Margin (fraction)",
            show_zero_line=True,
        )
        path = figures_dir / "kpi_margins_line.png"
        save_figure(fig, path, FigureSpec(chart_type="line", title="Gross and net margin (%)"))
        plt.close(fig)
    manifest.append(
        FigureManifestRow(
            filename=path.name,
            chart_type="line",
            title="Gross and net margin (%)",
            x_label="Month",
            y_label="Margin (fraction)",
            guardrail_note="Include a 0 reference line for ratio charts.",
            data_source="gl_kpi_monthly.csv",
        )
    )
    figure_paths.append(path)

    # A/R: DSO
    if not ar_month.empty and "dso_approx" in ar_month.columns:
        with style_context():
            fig = _plot_time_series(
                ar_month,
                x_col="month",
                y_cols=["dso_approx"],
                title="A/R days sales outstanding (approx.)",
                x_label="Month",
                y_label="Days",
                show_zero_line=False,
            )
            path = figures_dir / "ar_dso_line.png"
            save_figure(fig, path, FigureSpec(chart_type="line", title="A/R DSO (approx.)"))
            plt.close(fig)
        manifest.append(
            FigureManifestRow(
                filename=path.name,
                chart_type="line",
                title="A/R days sales outstanding (approx.)",
                x_label="Month",
                y_label="Days",
                guardrail_note="Do not truncate y-axis to exaggerate small changes.",
                data_source="ar_monthly_metrics.csv",
            )
        )
        figure_paths.append(path)

    # A/R distribution: days outstanding (hist + ECDF)
    if not slices.empty and "days_outstanding" in slices.columns:
        days = slices["days_outstanding"].astype(float).to_numpy()
        weights = slices.get("amount_applied", pd.Series(np.ones(len(slices)))).astype(float).to_numpy()

        mean_days = float(np.average(days, weights=np.clip(weights, 0, None))) if days.size else float("nan")
        med_days = float(np.nanmedian(days)) if days.size else float("nan")
        p90 = float(np.nanpercentile(days, 90)) if days.size else float("nan")

        with style_context():
            fig = plot_histogram_with_markers(
                values=days,
                title="A/R payment lag (days) — histogram",
                x_label="Days outstanding",
                y_label="Count",
                markers={"mean": mean_days, "median": med_days, "p90": p90},
            )
            path = figures_dir / "ar_days_hist.png"
            save_figure(fig, path, FigureSpec(chart_type="histogram", title="A/R payment lag histogram"))
            plt.close(fig)
        manifest.append(
            FigureManifestRow(
                filename=path.name,
                chart_type="histogram",
                title="A/R payment lag (days) — histogram",
                x_label="Days outstanding",
                y_label="Count",
                guardrail_note="Histogram x-axis uses real units; avoid binning that hides tails.",
                data_source="ar_payment_slices.csv",
            )
        )
        figure_paths.append(path)

        with style_context():
            fig = plot_ecdf(
                values=days,
                title="A/R payment lag (days) — ECDF",
                x_label="Days outstanding",
                y_label="Cumulative proportion",
                markers={"median": med_days, "p90": p90},
            )
            path = figures_dir / "ar_days_ecdf.png"
            save_figure(fig, path, FigureSpec(chart_type="ecdf", title="A/R payment lag ECDF"))
            plt.close(fig)
        manifest.append(
            FigureManifestRow(
                filename=path.name,
                chart_type="ecdf",
                title="A/R payment lag (days) — ECDF",
                x_label="Days outstanding",
                y_label="Cumulative proportion",
                guardrail_note="ECDF is recommended for skewed distributions; show tail percentiles.",
                data_source="ar_payment_slices.csv",
            )
        )
        figure_paths.append(path)

    # 4) Write manifest + summary
    pd.DataFrame([m.__dict__ for m in manifest]).to_csv(manifest_path, index=False)

    summary: dict[str, Any] = {
        "chapter": "business_ch09_reporting_style_contract",
        "seed": int(seed),
        "paths": {
            "contract": str(contract_path),
            "manifest": str(manifest_path),
            "memo": str(memo_path),
            "summary": str(summary_path),
            "figures_dir": str(figures_dir),
        },
        "n_figures": int(len(figure_paths)),
        "figures": [p.name for p in figure_paths],
    }
    # Small “one-page” executive memo (markdown)
    # memo_path.write_text(_make_executive_memo(kpi=kpi, ar_monthly=ar_m, ar_days_stats=ar_days_stats), encoding="utf-8")
    memo_path.write_text(
        _make_executive_memo(kpi=kpi, ar_monthly=ar_month, ar_days_stats=ar_days_stats),
        encoding="utf-8",
    )

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return Ch09Outputs(
        contract_path=contract_path,
        manifest_path=manifest_path,
        memo_path=memo_path,
        summary_path=summary_path,
        figures_dir=figures_dir,
        figure_paths=figure_paths,
    )


def main(argv: list[str] | None = None) -> int:
    p = base_parser("Business Ch09: plotting/reporting style contract")
    p.add_argument("--datadir", type=str, required=True, help="Path to NSO v1 dataset folder")
    args = p.parse_args(argv)

    seed = int(args.seed) if args.seed is not None else 123
    analyze_ch09(datadir=Path(args.datadir), outdir=Path(args.outdir), seed=seed)
    print(f"Wrote Chapter 9 artifacts -> {Path(args.outdir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
