BYOD in the real world (adapters, exports, privacy)
===================================================

**Why this exists:** Students need a 'real export' experience. This chapter frames BYOD as a repeatable, safe workflow.

Learning objectives
-------------------

- Explain what adapters do and why we prefer them to manual spreadsheet cleaning.
- Know the BYOD commands: ``pystatsv1 trackd byod init``, ``pystatsv1 trackd byod normalize``, ``pystatsv1 trackd validate``, ``pystatsv1 trackd byod daily-totals``.
- Handle privacy safely (what to redact and how to share).

Outline
-------

The BYOD workflow
-----------------

- Initialize a project folder with templates.
- Drop in an export under ``tables/`` (source-specific).
- Normalize to canonical outputs under ``normalized/``.
- Run analysis helpers and Track D scripts on normalized outputs.
- Adapters keep the cleanup step repeatable and testable — no one-off spreadsheet edits.

Adapters and tradeoffs
----------------------

- ``passthrough``: already canonical data.
- ``core_gl``: generic GL export cleaning.
- ``gnucash_gl``: specific to GnuCash multi-line export.

Privacy + classroom sharing
---------------------------

- Never publish raw exports that include names, addresses, invoice details.
- Prefer aggregated outputs (daily totals) for sharing examples.
- If you must share, redact names, shorten the date range, and consider rounding amounts.

Where this connects in the workbook
-----------------------------------

- :doc:`../track_d_byod` (BYOD hub)
- :doc:`../track_d_byod_gnucash` (GnuCash tutorial pack)

.. note::

   This page is intentionally an outline right now. Expand it incrementally as we refine Track D narrative.
