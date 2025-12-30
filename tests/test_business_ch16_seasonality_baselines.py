from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

from scripts.business_ch16_seasonality_baselines import analyze_ch16
from scripts.sim_business_nso_v1 import simulate_nso_v1, write_nso_v1


def test_business_ch16_outputs_exist_and_contract(tmp_path: Path) -> None:
    out = simulate_nso_v1(seed=123)
    write_nso_v1(out, tmp_path)

    outdir = tmp_path / "outputs"
    res = analyze_ch16(datadir=tmp_path, outdir=outdir, seed=123)

    assert res.series_csv.exists()
    assert res.seasonal_profile_csv.exists()
    assert res.backtest_predictions_csv.exists()
    assert res.backtest_metrics_csv.exists()
    assert res.forecast_csv.exists()
    assert res.design_json.exists()
    assert res.memo_md.exists()
    assert res.figures_manifest_csv.exists()

    series = pd.read_csv(res.series_csv)
    assert "month" in series.columns
    assert "revenue" in series.columns
    assert len(series) == 24
    assert series["month"].nunique() == len(series)

    seasonal = pd.read_csv(res.seasonal_profile_csv)
    assert set(seasonal.columns) >= {"month_of_year", "mean_revenue", "seasonal_index"}
    assert len(seasonal) == 12
    assert seasonal["month_of_year"].nunique() == 12

    metrics = pd.read_csv(res.backtest_metrics_csv)
    expected = {"naive_last", "moving_avg_3", "linear_trend", "seasonal_naive_12", "seasonal_mean"}
    assert set(metrics["method"].tolist()) == expected
    assert (metrics["mae"] >= 0).all()
    assert (metrics["mape"] >= 0).all()

    fc = pd.read_csv(res.forecast_csv)
    assert len(fc) == 12
    assert set(fc.columns) >= {"month", "method", "forecast", "lower", "upper"}

    last_actual = pd.Period(series["month"].iloc[-1], freq="M")
    first_forecast = pd.Period(fc["month"].iloc[0], freq="M")
    assert first_forecast == last_actual + 1

    design = json.loads(res.design_json.read_text(encoding="utf-8"))
    assert design["chosen_method"] in expected
    assert design["chosen_method"] == str(fc["method"].iloc[0])

    mf = pd.read_csv(res.figures_manifest_csv)
    assert len(mf) >= 2
    figs_dir = outdir / "figures"
    for fname in mf["filename"].tolist():
        assert (figs_dir / fname).exists()