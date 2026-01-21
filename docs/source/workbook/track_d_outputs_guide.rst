Track D Outputs Guide
=====================

This page explains what Track D writes to disk when you run workbook scripts, where those files go, and
how to use them in a lab, assignment, or your own analysis.

Why outputs matter
------------------

Track D is designed so you practice two real-world skills at once:

1. **Accounting-data discipline**: checks that the data behave like a coherent accounting system
   (balanced postings, accounting equation consistency, etc.).
2. **Analytics discipline**: metrics, tables, and plots that turn accounting data into decisions.

The **files written to** ``outputs/`` are the evidence trail for both.

Where outputs go
----------------

By default, Track D scripts write into a folder under your workbook directory:

.. code-block:: text

   <your_workbook_folder>/
     outputs/
       track_d/

Example (Windows):

.. code-block:: text

   C:\Users\nicho\Videos\Python\Test6PyStatsV1\track_d_workbook\outputs\track_d

All Track D scripts use the same convention so you always know where to look.

Tip: if you run a script and nothing appears to change in ``outputs/track_d``, you may not be in the
workbook folder. Run ``pwd`` (Git Bash) to confirm you are inside your ``track_d_workbook`` directory.

What kinds of files you get
---------------------------

Track D outputs are intentionally simple and "Excel-friendly":

**1) Summary JSON (machine-readable)**

Many chapters write a compact ``*.json`` summary you can:

* read in a text editor
* load in Python for grading or reporting
* compare across runs (did your results change?)

**2) Tables as CSV (spreadsheet-friendly)**

Common derived tables are written as ``*.csv`` so you can open them in:

* Excel / Google Sheets
* pandas

These are often the best starting point for "what is the data doing?"

**3) Plots as PNG (report-friendly)**

Chapters that produce visuals write ``*.png`` files so you can paste them into:

* a lab write-up
* a slide deck
* a memo

**4) Human-readable Markdown summaries (quick scan)**

Some utilities (like ``d00_peek_data``) write a ``*.md`` file that you can read immediately.

The Track D output folder layout
--------------------------------

After you run a few scripts, ``outputs/track_d`` will look something like this:

.. code-block:: text

   outputs/track_d/
     d00_peek_data_summary.md
     business_ch01_summary.json
     business_ch01_cash_balance.png
     business_ch01_balance_sheet_bar.png
     ...

The exact filenames vary by chapter.

**The most important rule:** Track D chapter scripts (and the ``dXX`` wrapper scripts) list their expected artifacts near the top of the file.
Open the script (in your workbook folder under ``scripts/``) and look at the docstring.

If you don't see an artifacts list for some reason, search within the script for ``--outdir`` or for path joins like ``outdir / ...``.

Example from Chapter 1:

.. code-block:: text

   scripts/business_ch01_accounting_measurement.py
     Artifacts written to --outdir (default: outputs/track_d)
       * business_ch01_summary.json
       * business_ch01_balance_sheet_bar.png
       * business_ch01_cash_balance.png

Interpreting the console output
-------------------------------

Most Track D scripts print two blocks to your terminal:

**Checks**
  These are pass/fail guards. They answer: *"Is the dataset coherent?"* and *"Did we violate an
  accounting invariant?"*

**Key metrics**
  These are the results. They answer: *"What happened in the business?"* and *"What should we do next?"*

Example (abridged):

.. code-block:: console

   $ pystatsv1 workbook run d01

   Checks:
   - transactions_balanced: True
   - accounting_equation_balances: True

   Key metrics:
   - sales_total: 4079.3879
   - gross_margin_pct: 0.4500
   - net_income: -2155.5873
   - ending_cash: 2974.2179

How to explain that to students:

* **Checks** tell you whether it's safe to trust the results.
* **Metrics** are the business story.

For example, a negative net income does *not* mean the analysis "failed". It might mean:

* the business spent heavily in a startup month (rent, equipment, payroll),
* revenue hasn't ramped up yet,
* or costs were higher than expected.

The job of the analyst is to connect those numbers back to the underlying transaction patterns.

Fast workflow: from outputs to a write-up
-----------------------------------------

This is a reliable "lab rhythm" that works for almost any Track D chapter:

1. Run the script.

   .. code-block:: console

      pystatsv1 workbook run d01

2. Read the console output (Checks + Key metrics).

3. Open the files in ``outputs/track_d``.

   * open ``*.png`` plots first to get intuition
   * open ``*.csv`` tables next to find the rows driving the story
   * use the ``*.json`` summary as your "official" numbers

4. Write 4-6 sentences:

   * What checks matter here and did we pass them?
   * What are the two most important metrics?
   * What is your hypothesis for why those numbers look that way?
   * What would you check next (a drill-down or follow-up plot)?

Optional: changing the output location
--------------------------------------

Most Track D scripts support an ``--outdir`` argument **when you run the script directly**.

The ``pystatsv1 workbook run ...`` command is the simplest way to run Track D, but it does not forward
extra arguments to the underlying script. So if you want a custom outputs folder, run the script with Python:

.. code-block:: console

   # from inside your Track D workbook folder
   python scripts/d01.py --outdir outputs/track_d_groupA

If you are new to command-line tools, ignore this at first and use the default ``outputs/track_d`` folder.

Common gotchas
--------------

**"My outputs aren't showing up"**
  Make sure you are in the workbook folder (the one that contains ``data/``, ``scripts/``, and
  ``outputs/``). In Git Bash: ``pwd``.

**"I edited the data and now results look weird"**
  Track D ships canonical seed=123 datasets so everyone starts from the same baseline.
  If you want to reset, run:

  .. code-block:: console

     pystatsv1 workbook run d00_setup_data --force

**"Why are there so many files?"**
  This is intentional. In real analytics work, outputs are what let you:

  * reproduce results
  * audit calculations
  * review someone else's analysis
  * grade consistently

Appendix: reading a JSON summary in Python
------------------------------------------

If you want to pull "official" metrics into a notebook, start with the JSON summary.

.. code-block:: python

   import json
   from pathlib import Path

   summary_path = Path("outputs/track_d/business_ch01_summary.json")
   summary = json.loads(summary_path.read_text(encoding="utf-8"))

   summary["key_metrics"]["net_income"], summary["key_metrics"]["gross_margin_pct"]

You can then build your own tables/plots on top of those saved artifacts.
