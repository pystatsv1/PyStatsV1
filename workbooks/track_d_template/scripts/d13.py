# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch13_correlation_causation_controlled_comparisons.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch13_controlled_comparisons_design.json
* ch13_correlation_summary.json
* ch13_correlation_memo.md
* ch13_figures_manifest.csv


Use either:
  pystatsv1 workbook run d13
or:
  pystatsv1 workbook run business_ch13_correlation_causation_controlled_comparisons
"""

from __future__ import annotations

from scripts.business_ch13_correlation_causation_controlled_comparisons import main


if __name__ == "__main__":
    main()
