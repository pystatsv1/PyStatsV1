Psych Stats with Python — Book 1 Launcher
=========================================

PyStatsV1 v0.24.1 packages a synthetic-only, inspectable local companion for
*Psych Stats with Python*. The launcher creates a new directory from a
versioned package asset. It does not overwrite existing work, upload data, run
an analysis automatically, or make a real-data claim.

Quick start
-----------

.. code-block:: bash

   python -m pip install "pystatsv1[book1]==0.24.1"
   pystatsv1 book1 init
   cd psych_stats_with_python_companion_v0_1
   python -m pip install -r requirements-book1-companion.txt
   make figures
   make all
   pystatsv1 book1 verify --dest .

``make all`` requires ``Rscript`` because the full Book 1 workflow compares
named Python and base-R reportable fields. ``make figures`` builds five
synthetic-data teaching plots with Matplotlib and writes an evidence manifest.

Commands
--------

``pystatsv1 book1 info``
  Displays the packaged companion version and source-file count.

``pystatsv1 book1 init --dest PATH``
  Creates a new local companion folder. The command refuses to overwrite an
  existing path.

``pystatsv1 book1 verify --dest PATH``
  Checks the extracted source data, scripts, figure specification, and reader
  files against the package manifest. It intentionally ignores generated
  ``outputs/`` because students create those by running the companion.

Scope boundary
--------------

The companion uses synthetic teaching data only. Its Python scripts use
pandas, NumPy, SciPy, and statsmodels for the named calculations; local scripts
write evidence files; optional base-R scripts independently check named values;
and PyStatsV1 provides the versioned package environment and launcher. None of
these tools substitute for study design, authorization, privacy protection, or
research judgment.
