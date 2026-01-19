# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch05_liabilities_payroll_taxes_equity.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* business_ch05_summary.json
* business_ch05_wages_payable_rollforward.csv
* business_ch05_payroll_taxes_payable_rollforward.csv
* business_ch05_sales_tax_payable_rollforward.csv
* business_ch05_notes_payable_rollforward.csv
* business_ch05_accounts_payable_rollforward.csv
* business_ch05_liabilities_over_time.png


Use either:
  pystatsv1 workbook run d05
or:
  pystatsv1 workbook run business_ch05_liabilities_payroll_taxes_equity
"""

from __future__ import annotations

from scripts.business_ch05_liabilities_payroll_taxes_equity import main


if __name__ == "__main__":
    main()
