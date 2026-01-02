"""Track D — Chapter 17: Revenue forecasting via segmentation + drivers (NSO v1).

We forecast AR invoice revenue by combining two drivers:

- Invoice count
- Average invoice value

Revenue = invoice_count × avg_invoice_value.

Customers are segmented into the top-K customers by invoice revenue plus an
"All other customers" bucket.

The forecasting methods are intentionally simple baselines (last value, moving
averages, seasonal naive, month-of-year mean) selected by 12-month backtest.

Run:
    python -m scripts.business_ch17_revenue_forecasting_segmentation_drivers \
        --datadir data/synthetic/nso_v1 --outdir outputs/track_d --seed 123
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scripts._reporting_style import style_context


def _save_fig(fig, path: Path) -> None:
    """Save and close a matplotlib figure (create parent dirs)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
# ----------------------------
# Constants
# ----------------------------

DEFAULT_TOP_K = 3
BACKTEST_WINDOW_MONTHS = 12
SEASONAL_PERIOD = 12


# ----------------------------
# Data structures
# ----------------------------


@dataclass(frozen=True)
class Outputs:
    outdir: Path
    figures_dir: Path

    seg_monthly_csv: Path
    series_monthly_csv: Path
    customer_segments_csv: Path

    backtest_metrics_csv: Path
    backtest_total_csv: Path

    forecast_csv: Path
    memo_md: Path

    design_json: Path
    known_events_template_json: Path

    fig_segment_history: Path
    fig_backtest_total: Path
    fig_forecast_total: Path

    figures_manifest_csv: Path
    manifest_json: Path

    # Backwards-compat / convenience aliases
    forecast_csv_alias: Path
    memo_md_alias: Path


# ----------------------------
# IO helpers
# ----------------------------


def _read_csv(path: Path, schema: dict[str, str] | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    if schema is None:
        return pd.read_csv(path)
    return pd.read_csv(path, dtype=schema)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _safe_div(numer: float, denom: float) -> float:
    if denom == 0:
        return float("nan")
    return numer / denom


def _as_month_period(s: pd.Series) -> pd.PeriodIndex:
    # Expect formats like YYYY-MM-DD or YYYY-MM
    return pd.to_datetime(s, errors="raise").dt.to_period("M")


# ----------------------------
# Loading + shaping
# ----------------------------


def load_ar_invoices(datadir: Path) -> pd.DataFrame:
    """Load AR events and keep only invoice rows."""
    path = datadir / "ar_events.csv"
    df = _read_csv(path)

    # Normalize expected fields
    # - date: YYYY-MM-DD
    # - month: YYYY-MM (optional)
    if "date" not in df.columns:
        raise ValueError("ar_events.csv must include a 'date' column")

    if "month" in df.columns:
        month = df["month"].astype(str)
        # Coerce to Period via YYYY-MM parsing
        month_period = pd.PeriodIndex(month, freq="M")
    else:
        month_period = _as_month_period(df["date"].astype(str))

    df = df.copy()
    df["month"] = month_period.astype(str)

    if "event_type" not in df.columns:
        raise ValueError("ar_events.csv must include an 'event_type' column")

    inv = df[df["event_type"].astype(str).str.lower().eq("invoice")].copy()

    # Minimal required columns
    required = {"month", "customer", "amount"}
    missing = required.difference(inv.columns)
    if missing:
        raise ValueError(f"ar_events.csv invoice rows missing columns: {sorted(missing)}")

    inv["customer"] = inv["customer"].astype(str)
    inv["amount"] = pd.to_numeric(inv["amount"], errors="coerce").fillna(0.0)

    return inv[["month", "customer", "amount"]]


def build_customer_segments(inv: pd.DataFrame, top_k: int) -> tuple[list[str], pd.DataFrame]:
    """Return (top_customers, customer_segments_df)."""
    totals = (
        inv.groupby("customer", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total_invoice_amount"})
        .sort_values("total_invoice_amount", ascending=False)
        .reset_index(drop=True)
    )

    top_customers = totals.head(top_k)["customer"].tolist()

    seg = totals.copy()
    seg["segment"] = np.where(seg["customer"].isin(top_customers), seg["customer"], "All other customers")

    return top_customers, seg


def build_segment_monthly(inv: pd.DataFrame, top_customers: list[str]) -> pd.DataFrame:
    """Monthly drivers table by segment."""
    df = inv.copy()
    df["segment"] = np.where(df["customer"].isin(top_customers), df["customer"], "All other customers")

    monthly = (
        df.groupby(["month", "segment"], as_index=False)
        .agg(invoice_count=("amount", "size"), invoice_amount=("amount", "sum"))
        .sort_values(["month", "segment"], ascending=True)
    )

    monthly["avg_invoice_value"] = monthly.apply(
        lambda r: _safe_div(float(r["invoice_amount"]), float(r["invoice_count"])), axis=1
    )

    # Ensure a complete month x segment grid with zeros for missing months
    months = sorted(monthly["month"].unique().tolist())
    segments = sorted(monthly["segment"].unique().tolist())

    grid = pd.MultiIndex.from_product([months, segments], names=["month", "segment"]).to_frame(index=False)
    merged = grid.merge(monthly, on=["month", "segment"], how="left")
    merged["invoice_count"] = merged["invoice_count"].fillna(0).astype(float)
    merged["invoice_amount"] = merged["invoice_amount"].fillna(0.0).astype(float)
    merged["avg_invoice_value"] = merged.apply(
        lambda r: _safe_div(float(r["invoice_amount"]), float(r["invoice_count"])), axis=1
    )

    # Month-of-year helper (1..12)
    merged["moy"] = pd.PeriodIndex(merged["month"], freq="M").month

    return merged[["month", "moy", "segment", "invoice_count", "invoice_amount", "avg_invoice_value"]]


def build_series_monthly(seg_monthly: pd.DataFrame) -> pd.DataFrame:
    g = seg_monthly.groupby("month", as_index=False).agg(
        invoice_count=("invoice_count", "sum"),
        invoice_amount=("invoice_amount", "sum"),
    )
    g["avg_invoice_value"] = g.apply(
        lambda r: _safe_div(float(r["invoice_amount"]), float(r["invoice_count"])), axis=1
    )
    g["moy"] = pd.PeriodIndex(g["month"], freq="M").month
    return g[["month", "moy", "invoice_count", "invoice_amount", "avg_invoice_value"]]


# ----------------------------
# Forecast methods
# ----------------------------


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = y_true != 0
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])))


def forecast_naive_last(train: np.ndarray, h: int) -> np.ndarray:
    if len(train) == 0:
        return np.zeros(h)
    return np.full(h, train[-1])


def forecast_ma(train: np.ndarray, h: int, window: int) -> np.ndarray:
    if len(train) == 0:
        return np.zeros(h)
    w = min(window, len(train))
    return np.full(h, float(np.mean(train[-w:])))


def forecast_seasonal_naive(train: np.ndarray, h: int, period: int = SEASONAL_PERIOD) -> np.ndarray:
    if len(train) == 0:
        return np.zeros(h)
    if len(train) < period:
        return forecast_naive_last(train, h)
    last_season = train[-period:]
    reps = int(np.ceil(h / period))
    return np.tile(last_season, reps)[:h]


def forecast_moy_mean(train_df: pd.DataFrame, value_col: str, h_months: list[str]) -> np.ndarray:
    # train_df must have columns: month, moy, value_col
    moy_means = train_df.groupby("moy")[value_col].mean()
    h_moy = pd.PeriodIndex(h_months, freq="M").month
    vals = []
    for m in h_moy:
        if m in moy_means.index:
            vals.append(float(moy_means.loc[m]))
        else:
            vals.append(float(train_df[value_col].mean()))
    return np.asarray(vals, dtype=float)


# ----------------------------
# Backtest + selection
# ----------------------------


def _split_train_test_months(months: list[str], test_window: int) -> tuple[list[str], list[str]]:
    if len(months) <= test_window:
        raise ValueError("Not enough months to backtest")
    train_months = months[:-test_window]
    test_months = months[-test_window:]
    return train_months, test_months


def _eval_methods_for_segment(
    seg_df: pd.DataFrame,
    value_col: str,
    methods: list[str],
    test_window: int,
) -> pd.DataFrame:
    months = seg_df["month"].tolist()
    train_months, test_months = _split_train_test_months(months, test_window)

    train = seg_df.loc[seg_df["month"].isin(train_months), value_col].to_numpy(dtype=float)
    test = seg_df.loc[seg_df["month"].isin(test_months), value_col].to_numpy(dtype=float)

    rows: list[dict[str, object]] = []

    for method in methods:
        if method == "naive_last":
            pred = forecast_naive_last(train, len(test))
        elif method == "ma3":
            pred = forecast_ma(train, len(test), window=3)
        elif method == "seasonal_naive":
            pred = forecast_seasonal_naive(train, len(test), period=SEASONAL_PERIOD)
        elif method == "last":
            pred = forecast_naive_last(train, len(test))
        elif method == "ma6":
            pred = forecast_ma(train, len(test), window=6)
        elif method == "moy_mean":
            train_df = seg_df.loc[seg_df["month"].isin(train_months), ["month", "moy", value_col]].copy()
            pred = forecast_moy_mean(train_df, value_col, test_months)
        else:
            raise ValueError(f"Unknown method: {method}")

        rows.append(
            {
                "series": value_col,
                "method": method,
                "mae": mae(test, pred),
                "mape": mape(test, pred),
            }
        )

    return pd.DataFrame(rows)


def select_best_method(metrics: pd.DataFrame) -> str:
    # Prefer lowest MAE; tie-breaker lowest MAPE.
    # If MAPE is NaN for some methods, treat as worse than numeric.
    df = metrics.copy()
    df["mape_rank"] = df["mape"].fillna(np.inf)
    df = df.sort_values(["mae", "mape_rank"], ascending=[True, True])
    return str(df.iloc[0]["method"])


# ----------------------------
# Figures
# ----------------------------


def plot_segment_revenue_history(seg_monthly: pd.DataFrame, fig_path: Path) -> None:
    """Stacked bar chart of AR invoice revenue by customer segment over time."""
    piv = (
        seg_monthly.pivot_table(index="month", columns="segment", values="invoice_amount", aggfunc="sum")
        .fillna(0.0)
    )

    with style_context():
        fig, ax = plt.subplots(figsize=(10, 5))
        piv.plot(kind="bar", stacked=True, ax=ax)
        ax.set_title("AR (invoice) revenue by customer segment (history)")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue (invoice amount)")
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(45)
            lbl.set_ha("right")
        _save_fig(fig, fig_path)


def plot_backtest_total(backtest_total: pd.DataFrame, fig_path: Path) -> None:
    """Line chart comparing actual vs predicted total revenue in backtest window."""
    with style_context():
        fig, ax = plt.subplots(figsize=(10, 4))
        x = pd.to_datetime(backtest_total["month"])
        ax.plot(x, backtest_total["actual"], marker="o", label="Actual")
        ax.plot(x, backtest_total["pred"], marker="o", label="Pred")
        ax.set_title("Backtest: Total revenue (1-step ahead)")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue")
        fig.autofmt_xdate(rotation=45)
        ax.legend()
        _save_fig(fig, fig_path)



def plot_forecast_total(
    history_total: pd.DataFrame,
    forecast_total: pd.DataFrame,
    fig_path: Path,
) -> None:
    """Line chart of historical total revenue and the next-12-month forecast (with optional band)."""
    with style_context():
        fig, ax = plt.subplots(figsize=(10, 4))
        x_hist = pd.to_datetime(history_total["month"])
        x_fc = pd.to_datetime(forecast_total["month"])
        ax.plot(x_hist, history_total["invoice_amount"], marker="o", label="History")
        ax.plot(x_fc, forecast_total["forecast_revenue"], marker="o", label="Forecast")

        if "forecast_lo" in forecast_total.columns and "forecast_hi" in forecast_total.columns:
            lo = forecast_total["forecast_lo"]
            hi = forecast_total["forecast_hi"]
            if lo.notna().any() and hi.notna().any():
                ax.fill_between(x_fc, lo, hi, alpha=0.2, label="p10–p90 band")

        ax.set_title("Forecast: Total revenue (next 12 months)")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue")
        fig.autofmt_xdate(rotation=45)
        ax.legend()
        _save_fig(fig, fig_path)



def write_markdown_memo(
    out_path: Path,
    design: dict,
    selected_models: dict,
    next12_total: pd.DataFrame,
) -> None:
    lines: list[str] = []
    lines.append("# Chapter 17 — Revenue forecasting (segmentation + drivers)\n")
    lines.append("## What we forecast\n")
    lines.append("## Top customers\n")
    lines.append(
        "Top customers are treated as separate segments (top_k by total invoice amount in AR).\n\n"
    )
    lines.append("We forecast AR (invoice) revenue as:\n")
    lines.append("- **Revenue = invoice_count × avg_invoice_value**\n")
    lines.append("\n")

    segs = design["segments"]
    lines.append("## Customer segmentation\n")
    lines.append(f"Segments (top-{design['top_k']} customers + bucket): {', '.join(segs)}\n")
    lines.append("\n")

    lines.append("## Model selection (12-month backtest)\n")
    lines.append("Per segment, we select:\n")
    lines.append("- one method for **invoice_count** (naive_last / ma3 / seasonal_naive)\n")
    lines.append("- one method for **avg_invoice_value** (last / ma6 / moy_mean)\n")
    lines.append("Chosen by lowest MAE (tie-breaker MAPE).\n")
    lines.append("\n")

    lines.append("### Selected models\n")
    for seg, cfg in selected_models.items():
        lines.append(f"- **{seg}**: count={cfg['count_method']}, value={cfg['value_method']}\n")
    lines.append("\n")

    lines.append("## Next 12 months (TOTAL)\n")
    if len(next12_total) > 0:
        lo = next12_total["forecast_lo"].dropna().min()
        hi = next12_total["forecast_hi"].dropna().max()
        lines.append(
            "Forecast includes a simple uncertainty band for TOTAL derived from backtest errors (p10–p90).\n"
        )
        if pd.notna(lo) and pd.notna(hi):
            lines.append(f"Band range over horizon: lo={lo:,.2f}, hi={hi:,.2f}\n")
    lines.append("\n")

    lines.append("## Files written\n")
    lines.append("Outputs are written under the Track D output folder:\n")
    lines.append("- CSV/JSON/MD in the chapter output directory\n")
    lines.append("- Figures under `figures/`\n")

    out_path.write_text("".join(lines), encoding="utf-8")


def write_figures_manifest(paths: Outputs) -> None:
    rows = [
        {
            "filename": paths.fig_segment_history.name,
            "chart_type": "bar",
            "title": "AR (invoice) revenue by customer segment (history)",
            "x_label": "Month",
            "y_label": "Revenue (invoice amount)",
            "guardrail_note": "Stacked bar of segmented AR invoice revenue; verify totals align with ch17_ar_revenue_segment_monthly.csv.",
            "data_source": "ar_events.csv (invoice rows), grouped by month and customer segment",
        },
        {
            "filename": paths.fig_backtest_total.name,
            "chart_type": "line",
            "title": "Backtest: total revenue (12-month holdout)",
            "x_label": "Month",
            "y_label": "Revenue",
            "guardrail_note": "Backtest compares predicted vs actual total revenue on a 12-month holdout window.",
            "data_source": "ch17_ar_revenue_segment_monthly.csv (summed across segments)",
        },
        {
            "filename": paths.fig_forecast_total.name,
            "chart_type": "line",
            "title": "Forecast: total revenue (next 12 months)",
            "x_label": "Month",
            "y_label": "Revenue",
            "guardrail_note": "Forecast total revenue using selected driver methods and a simple p10–p90 band (TOTAL only).",
            "data_source": "ch17_forecast_next12.csv",
        },
    ]
    pd.DataFrame(rows).to_csv(paths.figures_manifest_csv, index=False)


def write_manifest(paths: Outputs) -> None:
    payload = {
        "chapter": 17,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "outdir": str(paths.outdir.as_posix()),
        "figures_dir": str(paths.figures_dir.as_posix()),
        "artifacts": [
            paths.seg_monthly_csv.name,
            paths.series_monthly_csv.name,
            paths.customer_segments_csv.name,
            paths.backtest_metrics_csv.name,
            paths.backtest_total_csv.name,
            paths.forecast_csv.name,
            paths.memo_md.name,
            paths.design_json.name,
            paths.known_events_template_json.name,
            paths.figures_manifest_csv.name,
            # figures (names only; stored under figures_dir)
            paths.fig_segment_history.name,
            paths.fig_backtest_total.name,
            paths.fig_forecast_total.name,
        ],
        "aliases": [paths.forecast_csv_alias.name, paths.memo_md_alias.name],
    }
    paths.manifest_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# ----------------------------
# Main analysis
# ----------------------------


def make_outpaths(outdir: Path) -> Outputs:
    figures_dir = outdir / "figures"

    return Outputs(
        outdir=outdir,
        figures_dir=figures_dir,
        seg_monthly_csv=outdir / "ch17_ar_revenue_segment_monthly.csv",
        series_monthly_csv=outdir / "ch17_series_monthly.csv",
        customer_segments_csv=outdir / "ch17_customer_segments.csv",
        backtest_metrics_csv=outdir / "ch17_backtest_metrics.csv",
        backtest_total_csv=outdir / "ch17_backtest_total_revenue.csv",
        forecast_csv=outdir / "ch17_forecast_next12.csv",
        memo_md=outdir / "ch17_memo.md",
        design_json=outdir / "ch17_design.json",
        known_events_template_json=outdir / "ch17_known_events_template.json",
        fig_segment_history=figures_dir / "ch17_fig_segment_revenue_history.png",
        fig_backtest_total=figures_dir / "ch17_fig_backtest_total_revenue.png",
        fig_forecast_total=figures_dir / "ch17_fig_forecast_total_revenue.png",
        figures_manifest_csv=outdir / "ch17_figures_manifest.csv",
        manifest_json=outdir / "ch17_manifest.json",
        forecast_csv_alias=outdir / "ch17_forecast_next_12m.csv",
        memo_md_alias=outdir / "ch17_forecast_memo.md",
    )


def analyze_ch17(datadir: Path, outdir: Path, seed: int = 123, top_k: int = DEFAULT_TOP_K) -> Outputs:
    np.random.seed(seed)
    paths = make_outpaths(outdir)
    _ensure_dir(paths.outdir)
    _ensure_dir(paths.figures_dir)

    inv = load_ar_invoices(datadir)
    top_customers, customer_segments = build_customer_segments(inv, top_k=top_k)

    seg_monthly = build_segment_monthly(inv, top_customers=top_customers)
    series_monthly = build_series_monthly(seg_monthly)

    # Backtest + model selection per segment
    segments = sorted(seg_monthly["segment"].unique().tolist())
    months = sorted(seg_monthly["month"].unique().tolist())

    count_methods = ["naive_last", "ma3", "seasonal_naive"]
    value_methods = ["last", "ma6", "moy_mean"]

    metrics_rows: list[pd.DataFrame] = []
    selected: dict[str, dict[str, str]] = {}

    for seg in segments:
        seg_df = seg_monthly[seg_monthly["segment"].eq(seg)].sort_values("month")

        m_count = _eval_methods_for_segment(seg_df, "invoice_count", count_methods, BACKTEST_WINDOW_MONTHS)
        m_count["segment"] = seg
        metrics_rows.append(m_count)

        m_val = _eval_methods_for_segment(seg_df, "avg_invoice_value", value_methods, BACKTEST_WINDOW_MONTHS)
        m_val["segment"] = seg
        metrics_rows.append(m_val)

        best_count = select_best_method(m_count)
        best_value = select_best_method(m_val)
        selected[seg] = {"count_method": best_count, "value_method": best_value}

    metrics = pd.concat(metrics_rows, ignore_index=True)
    metrics = metrics[["segment", "series", "method", "mae", "mape"]].sort_values(
        ["segment", "series", "mae"], ascending=[True, True, True]
    )

    # Backtest total revenue: build a 12-month holdout using selected methods
    train_months, test_months = _split_train_test_months(months, BACKTEST_WINDOW_MONTHS)

    # Predict per segment in the test window
    preds_by_seg: dict[str, np.ndarray] = {}

    for seg in segments:
        seg_df = seg_monthly[seg_monthly["segment"].eq(seg)].sort_values("month")
        train_df = seg_df[seg_df["month"].isin(train_months)].copy()

        # count
        train_count = train_df["invoice_count"].to_numpy(dtype=float)
        cm = selected[seg]["count_method"]
        if cm == "naive_last":
            pred_count = forecast_naive_last(train_count, len(test_months))
        elif cm == "ma3":
            pred_count = forecast_ma(train_count, len(test_months), window=3)
        elif cm == "seasonal_naive":
            pred_count = forecast_seasonal_naive(train_count, len(test_months), period=SEASONAL_PERIOD)
        else:
            raise ValueError(f"Unknown count method: {cm}")

        # value
        train_value = train_df["avg_invoice_value"].to_numpy(dtype=float)
        vm = selected[seg]["value_method"]
        if vm == "last":
            pred_value = forecast_naive_last(train_value, len(test_months))
        elif vm == "ma6":
            pred_value = forecast_ma(train_value, len(test_months), window=6)
        elif vm == "moy_mean":
            pred_value = forecast_moy_mean(train_df[["month", "moy", "avg_invoice_value"]], "avg_invoice_value", test_months)
        else:
            raise ValueError(f"Unknown value method: {vm}")

        preds_by_seg[seg] = pred_count * pred_value

    # Actual total revenue in the test window
    actual_total = (
        seg_monthly[seg_monthly["month"].isin(test_months)]
        .groupby("month", as_index=False)["invoice_amount"]
        .sum()
        .rename(columns={"invoice_amount": "actual"})
        .sort_values("month")
    )

    pred_total = pd.DataFrame({"month": test_months, "pred": np.zeros(len(test_months), dtype=float)})
    for seg in segments:
        pred_total["pred"] += preds_by_seg[seg]

    backtest_total = actual_total.merge(pred_total, on="month", how="left")
    backtest_total["error"] = backtest_total["actual"] - backtest_total["pred"]

    # Build simple TOTAL band using backtest percent error quantiles
    pct_err = backtest_total.apply(
        lambda r: _safe_div(float(r["error"]), float(r["actual"])) if float(r["actual"]) != 0 else float("nan"), axis=1
    )
    pct_err = pct_err.replace([np.inf, -np.inf], np.nan).dropna()
    lo_pct = float(np.quantile(pct_err, 0.10)) if len(pct_err) else float("nan")
    hi_pct = float(np.quantile(pct_err, 0.90)) if len(pct_err) else float("nan")

    # Forecast next 12 months (per segment)
    last_period = pd.Period(months[-1], freq="M")
    future_months = [(last_period + i).strftime("%Y-%m") for i in range(1, 13)]

    fc_rows: list[dict[str, object]] = []

    for seg in segments:
        seg_df = seg_monthly[seg_monthly["segment"].eq(seg)].sort_values("month")

        # counts
        train_count_full = seg_df["invoice_count"].to_numpy(dtype=float)
        cm = selected[seg]["count_method"]
        if cm == "naive_last":
            fc_count = forecast_naive_last(train_count_full, 12)
        elif cm == "ma3":
            fc_count = forecast_ma(train_count_full, 12, window=3)
        elif cm == "seasonal_naive":
            fc_count = forecast_seasonal_naive(train_count_full, 12, period=SEASONAL_PERIOD)
        else:
            raise ValueError(f"Unknown count method: {cm}")

        # values
        train_value_full = seg_df["avg_invoice_value"].to_numpy(dtype=float)
        vm = selected[seg]["value_method"]
        if vm == "last":
            fc_value = forecast_naive_last(train_value_full, 12)
        elif vm == "ma6":
            fc_value = forecast_ma(train_value_full, 12, window=6)
        elif vm == "moy_mean":
            fc_value = forecast_moy_mean(seg_df[["month", "moy", "avg_invoice_value"]], "avg_invoice_value", future_months)
        else:
            raise ValueError(f"Unknown value method: {vm}")

        for m, c, v in zip(future_months, fc_count, fc_value, strict=True):
            fc_rows.append(
                {
                    "month": m,
                    "segment": seg,
                    "forecast_invoice_count": float(c),
                    "forecast_avg_invoice_value": float(v),
                    "forecast_revenue": float(c) * float(v),
                    "forecast_lo": np.nan,
                    "forecast_hi": np.nan,
                }
            )

    forecast = pd.DataFrame(fc_rows)

    # Add TOTAL segment row
    total = (
        forecast.groupby("month", as_index=False)
        .agg(
            forecast_invoice_count=("forecast_invoice_count", "sum"),
            forecast_avg_invoice_value=("forecast_avg_invoice_value", "mean"),
            forecast_revenue=("forecast_revenue", "sum"),
        )
    )
    total["segment"] = "TOTAL"

    if pd.notna(lo_pct) and pd.notna(hi_pct):
        total["forecast_lo"] = total["forecast_revenue"] * (1.0 + lo_pct)
        total["forecast_hi"] = total["forecast_revenue"] * (1.0 + hi_pct)

    forecast = pd.concat([forecast, total], ignore_index=True)
    forecast = forecast[[
        "month",
        "segment",
        "forecast_invoice_count",
        "forecast_avg_invoice_value",
        "forecast_revenue",
        "forecast_lo",
        "forecast_hi",
    ]].sort_values(["month", "segment"], ascending=[True, True])

    # Known events template
    known_template = {
        "notes": "Optional: add known events / one-off adjustments that affect invoices or values.",
        "schema": {
            "month": "YYYY-MM",
            "segment": "One of design.segments (including 'All other customers')",
            "delta_invoice_count": "integer (additive)",
            "mult_avg_invoice_value": "float multiplier, e.g. 1.10",
            "comment": "string",
        },
        "events": [],
    }

    # Design json
    design = {
        "chapter": 17,
        "seed": seed,
        "datadir": str(datadir),
        "top_k": top_k,
        "segments": ["All other customers"] + top_customers,
        "segment_meta": {
            "top_k": top_k,
            "top_customers": top_customers,
            "segment_definition": "Top customers by total invoice amount (AR) vs All other customers",
            "n_invoices": int(len(inv)),
            "months": months,
        },
        "count_methods": count_methods,
        "value_methods": value_methods,
        "selected_models": selected,
        "backtest_window_months": BACKTEST_WINDOW_MONTHS,
        "total_band_pct_quantiles": {
            "lo": 0.10,
            "hi": 0.90,
            "lo_pct": lo_pct,
            "hi_pct": hi_pct,
        },
    }

    # Write outputs
    seg_monthly.to_csv(paths.seg_monthly_csv, index=False)
    series_monthly.to_csv(paths.series_monthly_csv, index=False)
    customer_segments.to_csv(paths.customer_segments_csv, index=False)

    metrics.to_csv(paths.backtest_metrics_csv, index=False)
    backtest_total.to_csv(paths.backtest_total_csv, index=False)

    forecast.to_csv(paths.forecast_csv, index=False)
    # aliases
    forecast.to_csv(paths.forecast_csv_alias, index=False)

    paths.design_json.write_text(json.dumps(design, indent=2), encoding="utf-8")
    paths.known_events_template_json.write_text(json.dumps(known_template, indent=2), encoding="utf-8")

    # Figures
    plot_segment_revenue_history(seg_monthly, paths.fig_segment_history)
    plot_backtest_total(backtest_total, paths.fig_backtest_total)

    hist_total = series_monthly[["month", "invoice_amount"]].copy()
    fc_total = forecast[forecast["segment"].eq("TOTAL")].copy().sort_values("month")
    plot_forecast_total(hist_total, fc_total, paths.fig_forecast_total)

    # Memo
    write_markdown_memo(paths.memo_md, design, selected, fc_total)
    # memo alias
    paths.memo_md_alias.write_text(paths.memo_md.read_text(encoding="utf-8"), encoding="utf-8")

    # Manifests
    write_figures_manifest(paths)
    write_manifest(paths)

    return paths


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Track D Chapter 17: revenue forecasting via segmentation + drivers")
    p.add_argument("--datadir", type=Path, required=True, help="Directory containing NSO v1 synthetic data")
    p.add_argument("--outdir", type=Path, required=True, help="Output root (e.g. outputs/track_d)")
    p.add_argument("--seed", type=int, default=123, help="Random seed")
    p.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help="Number of top customers to segment")
    return p


def main() -> None:
    args = build_parser().parse_args()
    outdir = args.outdir / "track_d"
    res = analyze_ch17(args.datadir, outdir, seed=int(args.seed), top_k=int(args.top_k))
    print(f"Wrote Chapter 17 artifacts -> {res.outdir}")


if __name__ == "__main__":
    main()