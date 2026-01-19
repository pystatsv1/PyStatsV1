# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch03_statements_as_summaries.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* business_ch03_summary.json
* business_ch03_statement_bridge.csv
* business_ch03_trial_balance.csv
* business_ch03_net_income_vs_cash_change.png


Use either:
  pystatsv1 workbook run d03
or:
  pystatsv1 workbook run business_ch03_statements_as_summaries
"""

from __future__ import annotations

from scripts.business_ch03_statements_as_summaries import main


if __name__ == "__main__":
    main()
