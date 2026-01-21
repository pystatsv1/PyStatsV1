Accounting data as a dataset pipeline
=====================================

**Why this exists:** Students often know debits/credits but not how that becomes an analyzable dataset. This bridges that gap.

Learning objectives
-------------------

- Describe the path from business events to statements and analytics.
- Recognize the difference between a chart of accounts, journal, ledger, and trial balance.
- Explain what a “normalization step” does and why it matters.

Outline
-------

From events to reports
----------------------

- Business event → journal entry (date, accounts, amounts, memo).
- Journal entries are the “source record”; the ledger is the “by-account view” of those entries.
- Trial balance is a snapshot of balances by account.
- Statements are *views* built from the trial balance and classifications.

From reports to analysis
------------------------

- Analytics usually starts from the journal/ledger (not the formatted financial statements).
- We create time series (daily/monthly totals), ratios, and variance explanations.
- We then ask: what changed, why, and what should we do next?

Where BYOD fits
---------------

- Different systems export different CSV shapes.
- Adapters convert exports into the Track D canonical tables.
- After normalization, you typically work from ``normalized/gl_journal.csv`` (plus ``normalized/chart_of_accounts.csv``).
- After normalization, analysis scripts don’t care where the data came from.

Where this connects in the workbook
-----------------------------------

- :doc:`../track_d_dataset_map` (what tables exist and what they mean)
- :doc:`../track_d_byod` (the adapter/normalize/validate workflow)

.. note::

   This page is intentionally an outline right now. Expand it incrementally as we refine Track D narrative.
