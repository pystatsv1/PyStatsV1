.. _track_d_byod:

=================================
Track D BYOD: Bring Your Own Data
=================================

Track D is built around a realistic accounting case study (NSO), but the *skills* are meant to transfer.

This BYOD (Bring Your Own Data) pipeline lets you take **real exports** (from a bookkeeping/accounting system)
and convert them into the same **Track D dataset contract** used in the workbook.

What “BYOD” means in Track D
----------------------------

Think of BYOD as a boring, reliable 3-step pipeline:

1. **Export** data from a real system (or a CSV you already have).
2. **Normalize** it into Track D’s canonical tables (``normalized/``).
3. **Validate + analyze** the normalized tables using the Track D workflow.

The core idea is: *separate the messy export from the clean analysis tables*.

Quick start (template)
----------------------

Create a BYOD project folder (this writes header-only templates under ``tables/``):

.. code-block:: console

   pystatsv1 trackd byod init --dest byod/my_project --profile core_gl

Edit ``byod/my_project/config.toml`` to choose an adapter (examples):

- ``adapter = "passthrough"`` — your ``tables/`` files are already in Track D’s canonical format
- ``adapter = "core_gl"`` — generic GL export adapter (varies by source)
- ``adapter = "gnucash_gl"`` — **GnuCash** “Export Transactions to CSV” (complex layout)

Then normalize:

.. code-block:: console

   pystatsv1 trackd byod normalize --project byod/my_project

You should now have:

- ``byod/my_project/normalized/chart_of_accounts.csv``
- ``byod/my_project/normalized/gl_journal.csv``

Validate the normalized tables:

.. code-block:: console

   pystatsv1 trackd validate --datadir byod/my_project/normalized --profile core_gl

PyPI-only setup (no Git required)
----------------------------------------------

If you just want to *use* Track D tools (you don’t need to clone the repo):

1. Create a virtual environment.
2. Install PyStatsV1 from PyPI.
3. Use the CLI + the workbook downloads in this section.

.. code-block:: console

   python -m venv .venv

   # Windows (Git Bash)
   source .venv/Scripts/activate

   # macOS/Linux
   # source .venv/bin/activate

   python -m pip install -U pip
   pip install "pystatsv1[workbook]"

(Optional) sanity check:

.. code-block:: console

   pystatsv1 doctor

Next: choose a tutorial
-----------------------

.. toctree::
   :maxdepth: 1

   track_d_byod_gnucash
   track_d_byod_gnucash_demo_analysis

Where this fits in the workbook
-------------------------------

- If you’re new to Track D, start with :doc:`track_d_student_edition`.
- If you’re ready to apply the workflow to your own data, see :doc:`track_d_my_own_data`.
- This BYOD hub is the “how do I get from *my export* to *Track D tables*?” bridge.
