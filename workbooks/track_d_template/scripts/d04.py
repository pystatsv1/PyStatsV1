# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch04_assets_inventory_fixed_assets.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* business_ch04_inventory_rollforward.csv
* business_ch04_margin_bridge.csv
* business_ch04_depreciation_rollforward.csv
* business_ch04_summary.json
* business_ch04_gross_margin_over_time.png
* business_ch04_depreciation_over_time.png


Use either:
  pystatsv1 workbook run d04
or:
  pystatsv1 workbook run business_ch04_assets_inventory_fixed_assets
"""

from __future__ import annotations

from scripts.business_ch04_assets_inventory_fixed_assets import main


if __name__ == "__main__":
    main()
