# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch16_seasonality_baselines.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):



Use either:
  pystatsv1 workbook run d16
or:
  pystatsv1 workbook run business_ch16_seasonality_baselines
"""

from __future__ import annotations

from scripts.business_ch16_seasonality_baselines import main


if __name__ == "__main__":
    main()
