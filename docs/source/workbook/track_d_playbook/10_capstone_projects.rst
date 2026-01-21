Capstones: applying Track D to your own accounting data
=======================================================

**Why this exists:** This is where Track D becomes a portfolio piece: a reproducible analysis on realistic accounting exports.

Learning objectives
-------------------

- Define a narrow, answerable question for a business dataset.
- Build a reproducible pipeline from export → normalized → analysis → report.
- Deliver a short write-up with artifacts that support the claims.

Outline
-------

Capstone scope options
----------------------

- Performance review: compare two quarters and explain drivers.
- Cash-flow proxy: build a daily inflow/outflow series and summarize volatility.
- Expense audit: identify top sources of expense growth and anomalies.

Deliverables checklist
----------------------

- BYOD project folder (``tables/`` exports + ``normalized/`` outputs + ``config.toml``).
- A small ``outputs/`` folder with plots/tables.
- A short report (1–2 pages) with interpretation and caveats.
- Optional: ``normalized/daily_totals.csv`` generated via ``pystatsv1 trackd byod daily-totals``.

Rubric outline (draft)
----------------------

- Reproducibility (can someone rerun it?).
- Correctness (schema and basic checks pass).
- Insight (the narrative matches the evidence).
- Communication (clear figures and concise writing).

Where this connects in the workbook
-----------------------------------

- :doc:`../track_d_my_own_data` (bridge from case study to BYOD)
- :doc:`../track_d_byod` (normalization workflow)

.. note::

   This page is intentionally an outline right now. Expand it incrementally as we refine Track D narrative.
