# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch11_sampling_estimation_audit_controls.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch11_sampling_plan.json
* ch11_sampling_summary.json
* ch11_audit_memo.md
* ch11_figures_manifest.csv


Use either:
  pystatsv1 workbook run d11
or:
  pystatsv1 workbook run business_ch11_sampling_estimation_audit_controls
"""

from __future__ import annotations

from scripts.business_ch11_sampling_estimation_audit_controls import main


if __name__ == "__main__":
    main()
