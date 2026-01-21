Risk, controls, and data quality checks
=======================================

**Why this exists:** Accounting data is only useful if you trust it. Track D teaches a light version of audit/control thinking for analysts.

Learning objectives
-------------------

- Describe why controls and reconciliation matter for analytics.
- Run simple anomaly checks and interpret them carefully.
- Explain the difference between an error and a legitimate outlier.

Outline
-------

Practical checks that scale
---------------------------

- Start from ``normalized/gl_journal.csv`` (and optionally ``normalized/chart_of_accounts.csv``).
- Missing dates, negative amounts where unexpected, duplicated rows or duplicated transaction references (when present).
- Unusual spikes relative to typical ranges.

Sampling mindset
----------------

- You can’t check everything; choose samples based on risk and materiality.
- Document what you checked and what you didn’t.

When to stop and ask for accounting context
-------------------------------------------

- A statistical red flag is not automatically fraud or error.
- Your next step is often: ask for invoices, contracts, or policy notes (e.g., revenue timing, refunds, capitalization).

Where this connects in the workbook
-----------------------------------

- :doc:`../track_d_outputs_guide` (where checks appear in script outputs)
- :doc:`../track_d_byod` (validate step and why it exists)

.. note::

   This page is intentionally an outline right now. Expand it incrementally as we refine Track D narrative.
