The Track D dataset contract (what scripts expect)
==================================================

**Why this exists:** Track D works because every chapter agrees on a shared data contract. This chapter explains the contract at a high level.

Learning objectives
-------------------

- Know the minimum tables required for GL-based analysis (``chart_of_accounts`` + ``gl_journal``).
- Explain what ``normalized/`` outputs are and why we prefer them for analysis.
- Understand where synthetic datasets come from (seeded, reproducible).

Outline
-------

Inputs vs normalized outputs
----------------------------

- BYOD projects store raw exports under ``tables/`` (source-specific).
- Normalization produces ``normalized/chart_of_accounts.csv`` and ``normalized/gl_journal.csv`` (canonical).
- Everything after that is “just analysis.”

Column naming and why it matters
--------------------------------

- Stable column headers allow scripts to be reused across systems.
- If headers drift, you want a failure early (during normalize/validate), not silent bad analysis.

What ``pystatsv1 trackd validate`` does conceptually
----------------------------------------------------

- Uses a profile (for example, ``core_gl``) to decide what tables/columns are required.
- Checks basic schema and required columns.
- Catches common data issues: missing dates, non-numeric amounts, or malformed account identifiers.

Where this connects in the workbook
-----------------------------------

- :doc:`../track_d_dataset_map` (table-by-table map)
- :doc:`../track_d_outputs_guide` (artifacts and how to use them)
- :doc:`../track_d_byod` (normalization and validation commands)

.. note::

   This page is intentionally an outline right now. Expand it incrementally as we refine Track D narrative.
