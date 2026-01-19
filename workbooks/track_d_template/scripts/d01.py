# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch01_accounting_measurement.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* business_ch01_cash_balance.png
* business_ch01_balance_sheet_bar.png
* business_ch01_summary.json


Use either:
  pystatsv1 workbook run d01
or:
  pystatsv1 workbook run business_ch01_accounting_measurement
"""

from __future__ import annotations

from scripts.business_ch01_accounting_measurement import main


if __name__ == "__main__":
    main()
