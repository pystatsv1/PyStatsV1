# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch08_descriptive_statistics_financial_performance.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* gl_kpi_monthly.csv
* ar_monthly_metrics.csv
* ar_payment_slices.csv
* ar_days_stats.csv
* ch08_summary.json


Use either:
  pystatsv1 workbook run d08
or:
  pystatsv1 workbook run business_ch08_descriptive_statistics_financial_performance
"""

from __future__ import annotations

from scripts.business_ch08_descriptive_statistics_financial_performance import main


if __name__ == "__main__":
    main()
