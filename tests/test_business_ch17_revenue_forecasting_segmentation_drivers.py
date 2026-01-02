from pathlib import Path

import pandas as pd

from scripts.business_ch17_revenue_forecasting_segmentation_drivers import analyze_ch17


def _write_ar_events_fixture(datadir: Path) -> None:
    """Create a minimal AR events dataset for Ch17 tests (CI-safe)."""
    rows: list[dict[str, object]] = []

    start = pd.Period("2025-01", freq="M")  # 24 months supports 12m backtest + 12m forecast
    for i in range(24):
        p = start + i
        # a stable day inside the month
        date = (p.to_timestamp(how="start") + pd.Timedelta(days=1)).date().isoformat()

        # 3 top customers + 1 small customer that becomes "All other customers"
        specs = [
            ("Summit", 220.0, 2),
            ("AquaSports", 160.0, 2),
            ("Mariner", 130.0, 2),
            ("SmallCo", 25.0, 1 if i % 2 == 0 else 0),
        ]
        for cust, base, n in specs:
            for j in range(n):
                rows.append(
                    {
                        "date": date,
                        "event_type": "invoice",
                        "customer": cust,
                        "amount": base + (i * 3.0) + j,
                    }
                )

    df = pd.DataFrame(rows)
    datadir.mkdir(parents=True, exist_ok=True)
    df.to_csv(datadir / "ar_events.csv", index=False)


def test_business_ch17_generates_expected_outputs(tmp_path: Path) -> None:
    datadir = tmp_path / "nso_v1"
    outdir = tmp_path / "outputs"

    _write_ar_events_fixture(datadir)

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
