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

CHAPTER = "Track D Chapter 15 — Forecasting Foundations and Forecast Hygiene (NSO)"


@dataclass(frozen=True)
class Outputs:
    series_csv: Path
    backtest_predictions_csv: Path
    backtest_metrics_csv: Path
    forecast_csv: Path
    assumptions_template_csv: Path
    design_json: Path
    memo_md: Path
    figures_manifest_csv: Path


def _read_csv(datadir: Path, name: str) -> pd.DataFrame:
    p = datadir / name
    if not p.exists():
        raise FileNotFoundError(f"Expected {name} in {datadir} but not found.")
    return pd.read_csv(p)


def _month_sort_key(month_series: pd.Series) -> pd.Series:
    # stable month ordering for strings like "YYYY-MM"
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
    """
    Build a clean monthly series table from NSO v1 statements_is_monthly.csv.

    Output columns:
      - month (YYYY-MM)
      - revenue, cogs, gross_profit, operating_expenses, net_income
    """
    is_df = _read_csv(datadir, "statements_is_monthly.csv")

    wide = (
        is_df.pivot_table(index="month", columns="line", values="amount", aggfunc="sum")
        .reset_index()
        .copy()
    )
    wide["month"] = wide["month"].astype(str)
    wide = wide.sort_values("month", key=_month_sort_key).reset_index(drop=True)

    # normalize columns (keep only the lines we care about for Ch15)
    col_map = {c: _snake(str(c)) for c in wide.columns}
    wide = wide.rename(columns=col_map)

    # expected normalized line names from the simulator
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

    keep = ["month"] + list(expected.keys())
    out = wide[keep].rename(columns=expected).copy()
    return out


def _forecast_naive_last(train: np.ndarray, horizon: int) -> np.ndarray:
    return np.repeat(float(train[-1]), horizon)


def _forecast_moving_average(
    train: np.ndarray, horizon: int, window: int = 3
) -> np.ndarray:
    window = int(max(1, min(window, train.size)))
    return np.repeat(float(np.mean(train[-window:])), horizon)


def _forecast_linear_trend(train: np.ndarray, horizon: int) -> np.ndarray:
    # y = a + b*t, fit by least squares (polyfit degree 1)
    t = np.arange(train.size, dtype=float)
    b, a = np.polyfit(t, train.astype(float), deg=1)  # [slope, intercept]
    t_future = np.arange(train.size, train.size + horizon, dtype=float)
    return a + b * t_future


def _mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_pred - y_true)))


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = y_true.astype(float)
    denom = np.where(y_true == 0.0, np.nan, y_true)
    ape = np.abs((y_pred - y_true) / denom) * 100.0
    return float(np.nanmean(ape))


def analyze_ch15(datadir: Path, outdir: Path, seed: int = 123) -> Outputs:
    """
    Chapter 15: Forecasting foundations (baseline methods + backtesting + hygiene).

    Reads:
      - statements_is_monthly.csv (NSO v1)

    Writes (into outdir):
      - ch15_series_monthly.csv
      - ch15_backtest_predictions.csv
      - ch15_backtest_metrics.csv
      - ch15_forecast_next12.csv
      - ch15_assumptions_log_template.csv
      - ch15_forecast_design.json
      - ch15_forecast_memo.md
      - ch15_figures_manifest.csv
      - figures/*.png referenced by the manifest
    """
    outdir.mkdir(parents=True, exist_ok=True)
    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    series = _build_monthly_series(datadir)

    target_col = "revenue"
    months = series["month"].tolist()
    y = series[target_col].astype(float).to_numpy()

    if y.size < 18:
        raise ValueError(
            f"Need at least 18 months to do the Chapter 15 backtest; got {y.size}."
        )

    # Backtest: first 12 months train, last 12 months test
    n_train = 12
    y_train, y_test = y[:n_train], y[n_train:]
    months_train, months_test = months[:n_train], months[n_train:]

    methods: dict[str, Callable[[np.ndarray, int], np.ndarray]] = {
        "naive_last": lambda tr, h: _forecast_naive_last(tr, h),
        "moving_avg_3": lambda tr, h: _forecast_moving_average(tr, h, window=3),
        "linear_trend": lambda tr, h: _forecast_linear_trend(tr, h),
    }

    pred_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []

    for name, fn in methods.items():
        yhat = fn(y_train, y_test.size).astype(float)
        err = yhat - y_test.astype(float)
        abs_err = np.abs(err)

        ape = np.abs(err / y_test.astype(float)) * 100.0
        for m, a, p, e, ae, pe in zip(
            months_test, y_test, yhat, err, abs_err, ape, strict=True
        ):
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

        metric_rows.append(
            {
                "method": name,
                "mae": _mae(y_test, yhat),
                "mape": _mape(y_test, yhat),
            }
        )

    metrics = (
        pd.DataFrame(metric_rows)
        .sort_values(["mape", "mae"], ascending=[True, True])
        .reset_index(drop=True)
    )

    chosen_method = str(metrics.loc[0, "method"])
    chosen_mae = float(metrics.loc[metrics["method"] == chosen_method, "mae"].iloc[0])

    # Refit on all data and forecast next 12 months
    horizon = 12
    yhat_next = methods[chosen_method](y, horizon).astype(float)

    last_month = pd.Period(months[-1], freq="M")
    next_months = [(last_month + i).strftime("%Y-%m") for i in range(1, horizon + 1)]

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

    # Write artifacts
    series_csv = outdir / "ch15_series_monthly.csv"
    backtest_predictions_csv = outdir / "ch15_backtest_predictions.csv"
    backtest_metrics_csv = outdir / "ch15_backtest_metrics.csv"
    forecast_csv = outdir / "ch15_forecast_next12.csv"
    assumptions_template_csv = outdir / "ch15_assumptions_log_template.csv"
    design_json = outdir / "ch15_forecast_design.json"
    memo_md = outdir / "ch15_forecast_memo.md"
    figures_manifest_csv = outdir / "ch15_figures_manifest.csv"

    series.to_csv(series_csv, index=False)
    pd.DataFrame(pred_rows).to_csv(backtest_predictions_csv, index=False)
    metrics.to_csv(backtest_metrics_csv, index=False)
    forecast.to_csv(forecast_csv, index=False)

    tmpl = pd.DataFrame(
        [
            {
                "as_of_month": months[-1],
                "series": target_col,
                "horizon_months": horizon,
                "assumption": "Example: New customer contract starts in 2027-03",
                "direction": "up|down|mixed",
                "estimated_impact": "e.g., +12000 revenue/month starting 2027-03",
                "owner": "name/role",
                "notes": "Delete this example row and use one row per major assumption.",
            }
        ]
    )
    tmpl.to_csv(assumptions_template_csv, index=False)

    design = {
        "chapter": CHAPTER,
        "seed": seed,
        "target_series": target_col,
        "history_months": months,
        "train_months": months_train,
        "test_months": months_test,
        "methods_compared": list(methods.keys()),
        "selection_rule": "min MAPE on 12-month holdout; tie-break on MAE",
        "chosen_method": chosen_method,
        "chosen_method_backtest_mae": chosen_mae,
        "forecast_horizon_months": horizon,
        "forecast_months": next_months,
        "forecast_interval_note": (
            "+/- backtest MAE (simple heuristic, not a probabilistic interval)"
        ),
    }
    design_json.write_text(json.dumps(design, indent=2), encoding="utf-8")

    memo_lines = [
        "# Chapter 15 Forecast Memo (baseline + hygiene)\n\n",
        f"**Target series:** {target_col}\n",
        f"**History window:** {months[0]} to {months[-1]} ({len(months)} months)\n",
        f"**Backtest:** train={months_train[0]}..{months_train[-1]} (12 months), "
        f"test={months_test[0]}..{months_test[-1]} (12 months)\n\n",
        "## Compared baseline methods\n",
        "- naive_last: use the last observed month as the forecast\n",
        "- moving_avg_3: average of the last 3 months\n",
        "- linear_trend: least-squares line over time\n\n",
        "## Backtest results (lower is better)\n\n",
        metrics.to_markdown(index=False),
        "\n\n",
        f"**Selected method:** `{chosen_method}` (lowest MAPE; tie-break on MAE)\n\n",
        "## Next 12-month forecast (with simple range)\n",
        "The range shown is a simple heuristic: forecast ± backtest MAE.\n\n",
        forecast.to_markdown(index=False),
        "\n\n",
        "## Forecast hygiene notes\n",
        "- Document assumptions in the **assumptions log** (what changed, when, "
        "and expected impact).\n",
        "- Keep a versioned trail: dataset seed/inputs + method choice + metrics.\n",
        "- Treat this as a baseline. Chapter 16+ introduces seasonality, "
        "breaks, and better models.\n",
    ]
    memo_md.write_text("".join(memo_lines), encoding="utf-8")

    # Figures + manifest
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
                    "Forecasts are estimates. Verify assumptions, ranges, "
                    "and error metrics before sharing."
                ),
            )
        )

    with style_context():
        fig = plot_time_series(
            series,
            x="month",
            series={"Revenue (actual)": "revenue"},
            title="Revenue history (monthly)",
            x_label="Month",
            y_label="Revenue",
        )
        spec = FigureSpec(
            chart_type="line",
            title="Revenue history (monthly)",
            x_label="Month",
            y_label="Revenue",
            data_source="statements_is_monthly.csv (Sales Revenue line)",
            notes="Actual history used for baseline forecasting.",
        )
        fig_path = figures_dir / "ch15_fig_revenue_history.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    bt_best = pd.read_csv(backtest_predictions_csv)
    bt_best = bt_best[bt_best["method"] == chosen_method].copy()

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
            series={
                "Revenue (actual)": "revenue",
                f"Backtest ({chosen_method})": "predicted_best",
            },
            title="Backtest overlay (12-month holdout)",
            x_label="Month",
            y_label="Revenue",
        )
        spec = FigureSpec(
            chart_type="line",
            title="Backtest overlay (12-month holdout)",
            x_label="Month",
            y_label="Revenue",
            data_source="statements_is_monthly.csv + ch15_backtest_predictions.csv",
            notes="Predicted values shown only for the test window.",
        )
        fig_path = figures_dir / "ch15_fig_backtest_overlay.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    with style_context():
        fig = plot_bar(
            metrics,
            x="method",
            y="mape",
            title="Backtest MAPE by method (lower is better)",
            x_label="Method",
            y_label="MAPE (%)",
        )
        spec = FigureSpec(
            chart_type="bar",
            title="Backtest MAPE by method (lower is better)",
            x_label="Method",
            y_label="MAPE (%)",
            data_source="ch15_backtest_metrics.csv",
            notes="Use error metrics to avoid 'forecast fantasy'.",
        )
        fig_path = figures_dir / "ch15_fig_mape_by_method.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    pd.DataFrame([r.__dict__ for r in manifest_rows]).to_csv(
        figures_manifest_csv, index=False
    )

    return Outputs(
        series_csv=series_csv,
        backtest_predictions_csv=backtest_predictions_csv,
        backtest_metrics_csv=backtest_metrics_csv,
        forecast_csv=forecast_csv,
        assumptions_template_csv=assumptions_template_csv,
        design_json=design_json,
        memo_md=memo_md,
        figures_manifest_csv=figures_manifest_csv,
    )


def write_outputs(_: Outputs) -> None:
    return


def _build_cli() -> Any:
    p = base_parser(description=CHAPTER)
    p.add_argument("--datadir", type=Path, required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    p = _build_cli()
    args = p.parse_args(argv)

    outdir = args.outdir / "track_d"
    analyze_ch15(datadir=args.datadir, outdir=outdir, seed=args.seed or 123)
    print("Wrote Chapter 15 artifacts ->", outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
