Psych Stats with Python — Book 1 Launcher
=========================================

The current Book 1 route is PyStatsV1 v0.25.2 with Companion v0.2.1, a
synthetic-only, inspectable local companion for *Psych Stats with Python*.
Companion v0.2.1 corrects the Chapter 8 synthetic participant identifiers so
all 48 rows have globally unique IDs. The analytical columns, row order,
reported statistics, APA sentence, Python/R parity, and Chapter 8 figure remain
unchanged.

The launcher creates a new directory from a versioned package asset. It does
not overwrite existing work, upload data, run an analysis automatically, or
make a real-data claim.

Quick start
-----------

.. code-block:: bash

   python -m pip install "pystatsv1[book1]==0.25.2"
   pystatsv1 book1 init
   cd psych_stats_with_python_companion_v0_2_1
   python -m pip install -r requirements-book1-companion.txt
   make figures
   make all
   pystatsv1 book1 verify --dest .

``make all`` requires ``Rscript`` because the full Book 1 workflow compares
named Python and base-R reportable fields. ``make figures`` builds six
source-faithful high-contrast grayscale synthetic-data teaching plots with
Matplotlib and writes an evidence manifest.

Historical proof boundary
-------------------------

The prior proof route remains preserved as PyStatsV1 v0.25.0 with Companion
v0.2:

.. code-block:: bash

   python -m pip install "pystatsv1[book1]==0.25.0"
   pystatsv1 book1 init
   cd psych_stats_with_python_companion_v0_2

The historical v0.2 source snapshot, package asset, portal-handoff receipt, and
``0.25.0`` requirement are retained as immutable lineage evidence. New installs
should use the corrected v0.25.2/v0.2.1 route.

Commands
--------

``pystatsv1 book1 info``
  Displays the packaged companion version and source-file count.

``pystatsv1 book1 init --dest PATH``
  Creates a new local companion folder. The command refuses to overwrite an
  existing path.

``pystatsv1 book1 verify --dest PATH``
  Checks the extracted source data, scripts, figure specification, maintenance
  receipt, and reader files against the package manifest. It intentionally
  ignores generated ``outputs/`` because students create those by running the
  companion.

Maintenance evidence
--------------------

Companion v0.2.1 includes ``BOOK1_MAINTENANCE_RECEIPT.json``. The receipt
records the old and new Chapter 8 CSV hashes, the deterministic
``ch08_001`` through ``ch08_048`` identifier sequence, the ID-only change
contract, unchanged Python/R reported fields, passing parity, the unchanged APA
sentence, and the byte-identical Chapter 8 figure.

Figure evidence
---------------

Chapter 10 correlation and Chapter 11 regression have separate source-faithful
figures. Their manifest records source CSV, analysis script, result path,
caption, accessibility text, SHA-256, and a minimum effective print resolution
of 300 PPI at the documented Book 1 image slot.

Scope boundary
--------------

The companion uses synthetic teaching data only. Its Python scripts use
pandas, NumPy, SciPy, and statsmodels for the named calculations; local scripts
write evidence files; optional base-R scripts independently check named values;
and PyStatsV1 provides the versioned package environment and launcher. None of
these tools substitute for study design, authorization, privacy protection, or
research judgment.
