# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch17_revenue_forecasting_segmentation_drivers.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch17_ar_revenue_segment_monthly.csv
* ch17_series_monthly.csv
* ch17_customer_segments.csv
* ch17_backtest_metrics.csv
* ch17_backtest_total_revenue.csv
* ch17_forecast_next12.csv
* ch17_memo.md
* ch17_design.json
* ch17_known_events_template.json
* ch17_figures_manifest.csv
* ch17_manifest.json
* ch17_forecast_next_12m.csv
* ch17_forecast_memo.md


Use either:
  pystatsv1 workbook run d17
or:
  pystatsv1 workbook run business_ch17_revenue_forecasting_segmentation_drivers
"""

from __future__ import annotations

from scripts.business_ch17_revenue_forecasting_segmentation_drivers import main


if __name__ == "__main__":
    main()
