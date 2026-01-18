Track D Workbook: Business Statistics for Accounting Data
=========================================================

Track D is a **Business Statistics & Forecasting** track built around a realistic
accounting running case (North Shore Outfitters, “NSO”).

The Track D Workbook is a **PyPI-first** student experience. You can install
PyStatsV1, create a Track D workbook folder, and run **Track D only** (no repo
clone required).

If you haven't seen the Track D overview yet, start here:

* :doc:`../business_intro`

What you get
------------

When you run ``pystatsv1 workbook init --track d``, PyStatsV1 creates a local
folder containing:

* convenience runner scripts (``d01`` … ``d23``) that map to Track D chapters
* a reproducible, pre-installed dataset under ``data/synthetic/`` (seed=123)
* an ``outputs/track_d/`` folder where results are written
* a small smoke test so you can quickly confirm everything is working

Quickstart (PyPI-only)
----------------------

1) Create a virtual environment and install the workbook extras.

.. code-block:: bash

   python -m venv .venv
   # Windows (Git Bash):
   source .venv/Scripts/activate

   python -m pip install -U pip
   pip install "pystatsv1[workbook]"

2) Create a Track D workbook folder.

.. code-block:: bash

   pystatsv1 workbook init --track d --dest track_d_workbook
   cd track_d_workbook

3) See what you can run.

.. code-block:: bash

   pystatsv1 workbook list --track d

4) **Peek the data** (recommended first step).

.. code-block:: bash

   pystatsv1 workbook run d00_peek_data

This prints the row counts and column names for the key CSV files and writes a
short markdown summary into ``outputs/track_d/``.

5) Run the first chapter.

.. code-block:: bash

   pystatsv1 workbook run d01

6) Run a quick self-check.

.. code-block:: bash

   pystatsv1 workbook check business_smoke

.. tip::

   You can re-run any chapter as many times as you want. The scripts overwrite
   outputs deterministically as long as you keep the dataset unchanged.

What data you are working with
------------------------------

Track D ships **two canonical datasets**. They are **synthetic but realistic**,
and are the same every time (seed=123).

1) **LedgerLab (Ch01)** — a small “starter ledger”

* purpose: introduce the accounting equation, debits/credits, and how a general
  ledger becomes an analysis-ready table
* location: ``data/synthetic/ledgerlab_ch01/``
* key files:

  * ``chart_of_accounts.csv``
  * ``gl_journal.csv``
  * monthly outputs like ``trial_balance_monthly.csv`` and ``statements_*_monthly.csv``

2) **NSO v1 running case** — a richer business dataset

* purpose: practice the *real* analyst workflow: reconcile, validate, reshape,
  summarize, model, and forecast
* location: ``data/synthetic/nso_v1/``
* key files include event logs (AR/AP/payroll/inventory), a bank statement feed,
  a generated general ledger, and monthly statements and trial balances

If you want to see the full data dictionary for NSO v1:

* :doc:`../business_appendix_ch14b_nso_v1_data_dictionary`

Resetting (or regenerating) the datasets
----------------------------------------

Datasets are installed automatically during workbook init.

If you edit anything under ``data/synthetic/`` and want to return to the
canonical seed=123 version:

.. code-block:: bash

   pystatsv1 workbook run d00_setup_data --force

This restores the canonical dataset files and re-runs a few lightweight checks.

Where your results go
---------------------

By default, Track D scripts write artifacts to:

* ``outputs/track_d/`` — tables, memos, and small machine-readable summaries
* ``outputs/track_d/figures/`` — charts created by chapters that plot results

A typical chapter produces:

* one or more ``.csv`` artifacts (tables you can open in Excel)
* a short ``.md`` memo describing what the script did and what to look for
* a “manifest” CSV listing outputs (useful for grading or reproducible reports)

How Track D helps you become a better accounting-data analyst
-------------------------------------------------------------

Track D is not “statistics in isolation.” The goal is to practice the full loop:

* **Measurement + integrity**: understand what the numbers *mean* and what can go wrong
* **Quality control**: detect issues early (duplicates, broken keys, imbalances)
* **Summarization**: build monthly statements and diagnostic KPIs from transactions
* **Explanation**: connect changes in performance to drivers (mix, price, volume)
* **Forecasting**: build baselines, add drivers, run scenarios, and communicate uncertainty

Most chapters are designed to leave you with a concrete artifact you can show:

* an analysis table (CSV)
* a chart
* a short memo with the “story” and the assumptions

Suggested workflow by week
--------------------------

A simple way to work through Track D:

* Start each week with ``d00_peek_data`` to remind yourself what tables exist.
* Run the chapter wrapper (``dNN``).
* Open ``outputs/track_d/`` and read the newest memo first.
* Use the artifacts for your write-up.

To connect the workbook runs to the textbook pages, use the Track D chapter docs
as your “book”:

* :ref:`business-track-d`

Troubleshooting
---------------

* If a chapter fails, try running ``pystatsv1 workbook check business_smoke``
  to confirm your environment is healthy.
* If you modified data and things look “weird,” reset with
  ``pystatsv1 workbook run d00_setup_data --force``.
* For general workbook workflow tips, see :doc:`workflow`.
