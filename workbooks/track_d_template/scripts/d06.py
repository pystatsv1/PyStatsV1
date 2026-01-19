# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch06_reconciliations_quality_control.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* ar_rollforward.csv
* bank_recon_matches.csv
* bank_recon_exceptions.csv
* ch06_summary.json


Use either:
  pystatsv1 workbook run d06
or:
  pystatsv1 workbook run business_ch06_reconciliations_quality_control
"""

from __future__ import annotations

from scripts.business_ch06_reconciliations_quality_control import main


if __name__ == "__main__":
    main()
