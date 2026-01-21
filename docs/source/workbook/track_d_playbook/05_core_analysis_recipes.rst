Core analysis recipes (what students actually do)
=================================================

**Why this exists:** This is the practical chapter: recurring tasks and the patterns behind them.

Learning objectives
-------------------

- Compute daily/monthly totals and compare periods.
- Build a simple sales proxy from ledger data.
- Create a small set of plots/tables that answer one clear question.

Outline
-------

Recipe: daily totals
--------------------

- Start from ``normalized/gl_journal.csv`` (canonical) and choose a revenue (or cash) account group.
- Group by date, sum signed amounts.
- If you’re using BYOD, you can generate daily totals with ``pystatsv1 trackd byod daily-totals --project <BYOD_DIR>``.
- Plot a time series; note spikes and missing days.
- Write one sentence about the pattern you see.

Recipe: monthly P&L by category
-------------------------------

- Start from ``normalized/gl_journal.csv`` and map accounts to categories (revenue/COGS/opex).
- Aggregate by month and category; compute shares and changes.
- Identify the top 3 drivers of change month-over-month.
- Sales proxy = sum of signed amounts for revenue accounts by day/month.

Recipe: concentration and outliers
----------------------------------

- Start from ``normalized/gl_journal.csv`` and find the largest transactions and their accounts.
- Compute the share of total explained by the top N rows.
- Flag unusual values for follow-up documentation.

Where this connects in the workbook
-----------------------------------

- :doc:\../track_d_byod` (Bring Your Own Data hub)`
- :doc:`../track_d_outputs_guide` (how to read artifacts)
- :doc:`../track_d_byod_gnucash_demo_analysis` (daily totals helper + example plots)

.. note::

   This page is intentionally an outline right now. Expand it incrementally as we refine Track D narrative.
