# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch02_double_entry_and_gl.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* business_ch02_gl_tidy.csv
* business_ch02_trial_balance.csv
* business_ch02_account_rollup.csv
* business_ch02_tb_by_account.png
* business_ch02_summary.json


Use either:
  pystatsv1 workbook run d02
or:
  pystatsv1 workbook run business_ch02_double_entry_and_gl
"""

from __future__ import annotations

from scripts.business_ch02_double_entry_and_gl import main


if __name__ == "__main__":
    main()
