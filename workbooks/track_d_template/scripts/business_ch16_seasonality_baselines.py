# SPDX-License-Identifier: MIT
"""Track D — Chapter 16: Seasonality and baseline forecasts (NSO).

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch16_series_monthly.csv
* ch16_seasonal_profile.csv
* ch16_backtest_predictions.csv
* ch16_backtest_metrics.csv
* ch16_forecast_next12.csv
* ch16_design.json
* ch16_memo.md
* ch16_figures_manifest.csv

"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

from scripts._cli import base_parser
from scripts._reporting_style import (
    FigureManifestRow,
    FigureSpec,
    plot_bar,
    plot_time_series,
    save_figure,
    style_context,
)

CHAPTER = "Track D Chapter 16 — Seasonality and Seasonal Baselines (NSO)"


@dataclass(frozen=True)
class Outputs:
    series_csv: Path
    seasonal_profile_csv: Path
    backtest_predictions_csv: Path
    backtest_metrics_csv: Path
    forecast_csv: Path
    design_json: Path
    memo_md: Path
    figures_manifest_csv: Path


def _read_csv(datadir: Path, name: str) -> pd.DataFrame:
    p = datadir / name
    if not p.exists():
        raise FileNotFoundError(f"Expected {name} in {datadir} but not found.")
    return pd.read_csv(p)


def _month_sort_key(month_series: pd.Series) -> pd.Series:
    return pd.to_datetime(month_series.astype(str) + "-01")


def _snake(s: str) -> str:
    return (
        s.strip()
        .lower()
        .replace("&", "and")
        .replace("/", " ")
        .replace("-", " ")
        .replace("(", "")
        .replace(")", "")
        .replace("  ", " ")
        .replace(" ", "_")
    )


def _build_monthly_series(datadir: Path) -> pd.DataFrame:
    """Build a clean monthly series from NSO v1 statements_is_monthly.csv.

    Output columns (wide, normalized):
      - month (YYYY-MM)
      - revenue, cogs, gross_profit, operating_expenses, net_income
      - month_num (1..N)
      - month_of_year (1..12)
    """
    is_df = _read_csv(datadir, "statements_is_monthly.csv")

    wide = (
        is_df.pivot_table(index="month", columns="line", values="amount", aggfunc="sum")
        .reset_index()
        .copy()
    )
    wide["month"] = wide["month"].astype(str)
    wide = wide.sort_values("month", key=_month_sort_key).reset_index(drop=True)

    col_map = {c: _snake(str(c)) for c in wide.columns}
    wide = wide.rename(columns=col_map)

    expected = {
        "sales_revenue": "revenue",
        "cost_of_goods_sold": "cogs",
        "gross_profit": "gross_profit",
        "operating_expenses": "operating_expenses",
        "net_income": "net_income",
    }
    missing = [src for src in expected if src not in wide.columns]
    if missing:
        raise ValueError(
            "statements_is_monthly.csv is missing required income statement lines "
            f"after pivot: {missing}. Available: {sorted(wide.columns)}"
        )

    out = wide[["month"] + list(expected.keys())].rename(columns=expected).copy()

    # Add deterministic helper keys used for seasonality calculations.
    out["month_num"] = np.arange(1, len(out) + 1, dtype=int)
    out["month_of_year"] = pd.PeriodIndex(out["month"], freq="M").month.astype(int)
    return out


def _mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_pred - y_true)))


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = y_true.astype(float)
    denom = np.where(y_true == 0.0, np.nan, y_true)
    ape = np.abs((y_pred - y_true) / denom) * 100.0
    return float(np.nanmean(ape))


def _forecast_naive_last(train: np.ndarray, horizon: int) -> np.ndarray:
    return np.repeat(float(train[-1]), horizon)


def _forecast_moving_average(train: np.ndarray, horizon: int, window: int = 3) -> np.ndarray:
    window = int(max(1, min(window, train.size)))
    return np.repeat(float(np.mean(train[-window:])), horizon)


def _forecast_linear_trend(train: np.ndarray, horizon: int) -> np.ndarray:
    t = np.arange(train.size, dtype=float)
    slope, intercept = np.polyfit(t, train.astype(float), deg=1)
    t_future = np.arange(train.size, train.size + horizon, dtype=float)
    return intercept + slope * t_future


def _forecast_seasonal_naive_12(train: np.ndarray, horizon: int) -> np.ndarray:
    """Seasonal naive with period=12 months.

    For each month in the next year, reuse the value from the same month last year.
    Requires train length >= 12 and horizon == 12 for this chapter.
    """
    if train.size < 12:
        raise ValueError("seasonal_naive_12 requires at least 12 months of training data.")
    if horizon != 12:
        # Keep the method explicit and simple for Track D.
        raise ValueError("seasonal_naive_12 is defined for a 12-month horizon in this chapter.")
    return train[-12:].astype(float).copy()


def _forecast_seasonal_mean(train: np.ndarray, train_months: list[str], horizon_months: list[str]) -> np.ndarray:
    """Seasonal mean baseline: forecast each month as the mean of that calendar month in training."""
    train_moy = pd.PeriodIndex(pd.Series(train_months), freq="M").month.astype(int)
    df = pd.DataFrame({"moy": train_moy, "y": train.astype(float)})
    means = df.groupby("moy")["y"].mean().to_dict()

    future_moy = pd.PeriodIndex(pd.Series(horizon_months), freq="M").month.astype(int)
    # Fall back to overall mean if a month_of_year is missing (should not happen with 12-month train).
    overall = float(np.mean(train.astype(float)))
    return np.array([float(means.get(int(m), overall)) for m in future_moy], dtype=float)


def analyze_ch16(datadir: Path, outdir: Path, seed: int = 123) -> Outputs:
    """Chapter 16: seasonality + seasonal baselines (NSO running case).

    Reads:
      - statements_is_monthly.csv

    Writes (into outdir):
      - ch16_series_monthly.csv
      - ch16_seasonal_profile.csv
      - ch16_backtest_predictions.csv
      - ch16_backtest_metrics.csv
      - ch16_forecast_next12.csv
      - ch16_design.json
      - ch16_memo.md
      - ch16_figures_manifest.csv
      - figures/*.png referenced by the manifest
    """
    outdir.mkdir(parents=True, exist_ok=True)
    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    series = _build_monthly_series(datadir)
    months = series["month"].tolist()

    if len(months) < 24:
        raise ValueError(f"Chapter 16 requires 24 months for a 12/12 backtest; got {len(months)}.")

    target_col = "revenue"
    y = series[target_col].astype(float).to_numpy()

    # --- Seasonality profile (month-of-year mean + index) ---
    seasonal = (
        series.groupby("month_of_year", as_index=False)[target_col]
        .mean()
        .rename(columns={target_col: "mean_revenue"})
        .sort_values("month_of_year")
        .reset_index(drop=True)
    )
    overall_mean = float(series[target_col].mean())
    seasonal["seasonal_index"] = seasonal["mean_revenue"] / overall_mean

    # --- Backtest: first 12 months train, last 12 months test ---
    horizon = 12
    n_train = 12
    y_train, y_test = y[:n_train], y[n_train:]
    months_train, months_test = months[:n_train], months[n_train:]

    methods_simple: dict[str, Callable[[np.ndarray, int], np.ndarray]] = {
        "naive_last": _forecast_naive_last,
        "moving_avg_3": lambda tr, h: _forecast_moving_average(tr, h, window=3),
        "linear_trend": _forecast_linear_trend,
        "seasonal_naive_12": _forecast_seasonal_naive_12,
    }

    pred_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []

    # methods that depend on month labels
    def _run_method(name: str) -> np.ndarray:
        if name == "seasonal_mean":
            return _forecast_seasonal_mean(y_train, months_train, months_test)
        return methods_simple[name](y_train, horizon).astype(float)

    method_names = ["naive_last", "moving_avg_3", "linear_trend", "seasonal_naive_12", "seasonal_mean"]
    for name in method_names:
        yhat = _run_method(name).astype(float)
        err = yhat - y_test.astype(float)
        abs_err = np.abs(err)
        ape = np.abs(err / y_test.astype(float)) * 100.0

        for m, a, p, e, ae, pe in zip(months_test, y_test, yhat, err, abs_err, ape, strict=True):
            pred_rows.append(
                {
                    "method": name,
                    "month": m,
                    "actual": float(a),
                    "predicted": float(p),
                    "error": float(e),
                    "abs_error": float(ae),
                    "abs_pct_error": float(pe),
                }
            )

        metric_rows.append({"method": name, "mae": _mae(y_test, yhat), "mape": _mape(y_test, yhat)})

    metrics = (
        pd.DataFrame(metric_rows)
        .sort_values(["mape", "mae"], ascending=[True, True])
        .reset_index(drop=True)
    )
    chosen_method = str(metrics.loc[0, "method"])
    chosen_mae = float(metrics.loc[metrics["method"] == chosen_method, "mae"].iloc[0])

    # --- Refit on all data and forecast next 12 months ---
    last_month = pd.Period(months[-1], freq="M")
    next_months = [(last_month + i).strftime("%Y-%m") for i in range(1, horizon + 1)]

    def _forecast_full(name: str) -> np.ndarray:
        if name == "seasonal_mean":
            # Use all history for means; forecast next months by month-of-year means.
            return _forecast_seasonal_mean(y, months, next_months)
        if name == "seasonal_naive_12":
            return _forecast_seasonal_naive_12(y, horizon)
        return methods_simple[name](y, horizon).astype(float)

    yhat_next = _forecast_full(chosen_method).astype(float)
    lower = np.maximum(0.0, yhat_next - chosen_mae)
    upper = yhat_next + chosen_mae

    forecast = pd.DataFrame(
        {
            "month": next_months,
            "method": chosen_method,
            "forecast": yhat_next,
            "lower": lower,
            "upper": upper,
        }
    )

    # --- Write artifacts ---
    series_csv = outdir / "ch16_series_monthly.csv"
    seasonal_profile_csv = outdir / "ch16_seasonal_profile.csv"
    backtest_predictions_csv = outdir / "ch16_backtest_predictions.csv"
    backtest_metrics_csv = outdir / "ch16_backtest_metrics.csv"
    forecast_csv = outdir / "ch16_forecast_next12.csv"
    design_json = outdir / "ch16_design.json"
    memo_md = outdir / "ch16_memo.md"
    figures_manifest_csv = outdir / "ch16_figures_manifest.csv"

    series.to_csv(series_csv, index=False)
    seasonal.to_csv(seasonal_profile_csv, index=False)
    pd.DataFrame(pred_rows).to_csv(backtest_predictions_csv, index=False)
    metrics.to_csv(backtest_metrics_csv, index=False)
    forecast.to_csv(forecast_csv, index=False)

    design = {
        "chapter": CHAPTER,
        "seed": seed,
        "target_series": target_col,
        "history_months": months,
        "train_months": months_train,
        "test_months": months_test,
        "methods_compared": method_names,
        "selection_rule": "min MAPE on 12-month holdout; tie-break on MAE",
        "chosen_method": chosen_method,
        "chosen_method_backtest_mae": chosen_mae,
        "seasonality_profile_note": "month-of-year mean and seasonal index (mean / overall mean)",
        "forecast_horizon_months": horizon,
        "forecast_months": next_months,
        "forecast_interval_note": "+/- backtest MAE (simple heuristic, not a probabilistic interval)",
    }
    design_json.write_text(json.dumps(design, indent=2), encoding="utf-8")

    top = seasonal.sort_values("seasonal_index", ascending=False).head(3)
    bottom = seasonal.sort_values("seasonal_index", ascending=True).head(3)

    memo_lines = [
        "# Chapter 16 Memo — Seasonality and Seasonal Baselines\n\n",
        f"**Target series:** {target_col}\n",
        f"**History window:** {months[0]} to {months[-1]} ({len(months)} months)\n",
        f"**Backtest:** train={months_train[0]}..{months_train[-1]} (12), "
        f"test={months_test[0]}..{months_test[-1]} (12)\n\n",
        "## What seasonality means (in business terms)\n",
        "Seasonality is a repeating calendar pattern (month-of-year effects) that shows up even when\n",
        "nothing is “wrong.” If revenue is typically higher in some months and lower in others, a\n",
        "non-seasonal baseline (like naive_last) will systematically miss those cycles.\n\n",
        "## Seasonality profile (month-of-year)\n\n",
        seasonal.to_markdown(index=False),
        "\n\n",
        "Top seasonal months (highest index):\n\n",
        top.to_markdown(index=False),
        "\n\n",
        "Bottom seasonal months (lowest index):\n\n",
        bottom.to_markdown(index=False),
        "\n\n",
        "## Backtest results (lower is better)\n\n",
        metrics.to_markdown(index=False),
        "\n\n",
        f"**Selected method:** `{chosen_method}` (lowest MAPE; tie-break on MAE)\n\n",
        "## Next 12-month forecast (with simple range)\n",
        "Range shown is forecast ± backtest MAE.\n\n",
        forecast.to_markdown(index=False),
        "\n\n",
        "## Hygiene reminders\n",
        "- Seasonal baselines are not magic; they are a disciplined way to respect calendar patterns.\n",
        "- If a major business change occurred (pricing, channel shift, store closure), document it and\n",
        "  consider resetting the training window or splitting pre/post periods.\n",
        "- Always sanity-check outliers: one unusual month can distort both seasonal means and trend.\n",
    ]
    memo_md.write_text("".join(memo_lines), encoding="utf-8")

    # --- Figures + manifest ---
    manifest_rows: list[FigureManifestRow] = []

    def _add_row(fig_path: Path, spec: FigureSpec) -> None:
        manifest_rows.append(
            FigureManifestRow(
                filename=fig_path.name,
                chart_type=spec.chart_type,
                title=spec.title,
                x_label=spec.x_label,
                y_label=spec.y_label,
                data_source="NSO v1 synthetic outputs",
                guardrail_note=(
                    "Seasonality baselines assume repeating calendar patterns. "
                    "Confirm that the business context supports this assumption."
                ),
            )
        )

    # Figure 1: seasonal index profile
    seasonal_plot = seasonal.copy()
    seasonal_plot["month_of_year"] = seasonal_plot["month_of_year"].astype(int)

    with style_context():
        fig = plot_bar(
            seasonal_plot,
            x="month_of_year",
            y="seasonal_index",
            title="Seasonal index by month-of-year (Revenue)",
            x_label="Month of year (1=Jan ... 12=Dec)",
            y_label="Seasonal index (mean / overall mean)",
        )
        spec = FigureSpec(
            chart_type="bar",
            title="Seasonal index by month-of-year (Revenue)",
            x_label="Month of year (1=Jan ... 12=Dec)",
            y_label="Seasonal index",
            data_source="statements_is_monthly.csv (Sales Revenue)",
            notes="Index > 1 means above-average month; < 1 means below-average.",
        )
        fig_path = figures_dir / "ch16_fig_seasonal_profile.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    # Figure 2: backtest overlay for chosen method
    bt = pd.DataFrame(pred_rows)
    bt_best = bt[bt["method"] == chosen_method].copy()

    overlay = series[["month", "revenue"]].copy()
    overlay = overlay.merge(
        bt_best[["month", "predicted"]].rename(columns={"predicted": "predicted_best"}),
        on="month",
        how="left",
    )

    with style_context():
        fig = plot_time_series(
            overlay,
            x="month",
            series={"Revenue (actual)": "revenue", f"Backtest ({chosen_method})": "predicted_best"},
            title="Backtest overlay (seasonality-aware method selection)",
            x_label="Month",
            y_label="Revenue",
        )
        spec = FigureSpec(
            chart_type="line",
            title="Backtest overlay (seasonality-aware method selection)",
            x_label="Month",
            y_label="Revenue",
            data_source="statements_is_monthly.csv + ch16_backtest_predictions.csv",
            notes="Predicted values shown only for the 12-month test window.",
        )
        fig_path = figures_dir / "ch16_fig_backtest_overlay.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    # Figure 3: forecast next 12 months (actual history + future forecast)
    hist = pd.DataFrame({"month": months, "actual": y.astype(float), "forecast": np.nan})
    fut = pd.DataFrame({"month": next_months, "actual": np.nan, "forecast": yhat_next.astype(float)})
    combined = pd.concat([hist, fut], ignore_index=True)
    with style_context():
        fig = plot_time_series(
            combined,
            x="month",
            series={"Revenue (actual)": "actual", f"Forecast ({chosen_method})": "forecast"},
            title="Revenue forecast (next 12 months)",
            x_label="Month",
            y_label="Revenue",
        )
        spec = FigureSpec(
            chart_type="line",
            title="Revenue forecast (next 12 months)",
            x_label="Month",
            y_label="Revenue",
            data_source="statements_is_monthly.csv + ch16_forecast_next12.csv",
            notes="Forecast shown for future months only (history remains actuals).",
        )
        fig_path = figures_dir / "ch16_fig_forecast_next12.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    pd.DataFrame([r.__dict__ for r in manifest_rows]).to_csv(figures_manifest_csv, index=False)

    return Outputs(
        series_csv=series_csv,
        seasonal_profile_csv=seasonal_profile_csv,
        backtest_predictions_csv=backtest_predictions_csv,
        backtest_metrics_csv=backtest_metrics_csv,
        forecast_csv=forecast_csv,
        design_json=design_json,
        memo_md=memo_md,
        figures_manifest_csv=figures_manifest_csv,
    )


def _build_cli() -> Any:
    p = base_parser(description=CHAPTER)
    p.add_argument("--datadir", type=Path, required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    p = _build_cli()
    args = p.parse_args(argv)

    outdir = args.outdir
    analyze_ch16(datadir=args.datadir, outdir=outdir, seed=args.seed or 123)
    print("Wrote Chapter 16 artifacts ->", outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())