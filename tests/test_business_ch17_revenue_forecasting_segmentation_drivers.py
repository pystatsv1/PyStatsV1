from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.business_ch17_revenue_forecasting_segmentation_drivers import analyze_ch17


def test_business_ch17_generates_expected_outputs(tmp_path: Path) -> None:
    datadir = Path("data") / "synthetic" / "nso_v1"
    outdir = tmp_path / "outputs"

    res = analyze_ch17(datadir=datadir, outdir=outdir, seed=123, top_k=3)

    # Core artifacts exist
    assert res.customer_segments_csv.exists()
    assert res.seg_monthly_csv.exists()
    assert res.series_monthly_csv.exists()
    assert res.backtest_metrics_csv.exists()
    assert res.backtest_total_csv.exists()
    assert res.forecast_csv.exists()
    assert res.memo_md.exists()
    assert res.design_json.exists()
    assert res.known_events_template_json.exists()
    assert res.figures_manifest_csv.exists()
    assert res.manifest_json.exists()

    # Compatibility aliases exist
    assert (outdir / "ch17_forecast_next_12m.csv").exists()
    assert (outdir / "ch17_forecast_memo.md").exists()

    # Basic schema checks
    seg = pd.read_csv(res.seg_monthly_csv)
    assert {
        "month",
        "moy",
        "segment",
        "invoice_count",
        "invoice_amount",
        "avg_invoice_value",
    }.issubset(set(seg.columns))

    series = pd.read_csv(res.series_monthly_csv)
    assert {
        "month",
        "moy",
        "invoice_count",
        "invoice_amount",
        "avg_invoice_value",
    }.issubset(set(series.columns))

    fc = pd.read_csv(res.forecast_csv)
    assert {
        "month",
        "segment",
        "forecast_invoice_count",
        "forecast_avg_invoice_value",
        "forecast_revenue",
        "forecast_lo",
        "forecast_hi",
    }.issubset(set(fc.columns))
    assert "TOTAL" in set(fc["segment"].astype(str))

    # Memo sanity
    memo = res.memo_md.read_text(encoding="utf-8")
    assert "Chapter 17" in memo
    assert "Top customers" in memo

    # Figures exist and are referenced by the figures manifest
    figures_dir = outdir / "figures"
    assert figures_dir.exists()
    assert res.fig_segment_history.exists()
    assert res.fig_backtest_total.exists()
    assert res.fig_forecast_total.exists()

    mf = pd.read_csv(res.figures_manifest_csv)
    assert "filename" in mf.columns
    for fn in mf["filename"].astype(str).tolist():
        assert (figures_dir / fn).exists()
