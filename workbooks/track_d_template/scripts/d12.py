# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch12_hypothesis_testing_decisions.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch12_experiment_design.json
* ch12_hypothesis_testing_summary.json
* ch12_experiment_memo.md
* ch12_figures_manifest.csv


Use either:
  pystatsv1 workbook run d12
or:
  pystatsv1 workbook run business_ch12_hypothesis_testing_decisions
"""

from __future__ import annotations

from scripts.business_ch12_hypothesis_testing_decisions import main


if __name__ == "__main__":
    main()
