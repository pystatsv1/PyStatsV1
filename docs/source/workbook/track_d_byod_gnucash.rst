.. _track_d_byod_gnucash:

===========================================
Track D BYOD with GnuCash (core_gl profile)
===========================================

GnuCash is a **free, open-source** double-entry accounting system.
In Track D, we use it as a “real but accessible” source system:

- it produces realistic **multi-line split** exports (not toy spreadsheets)
- it teaches a *cleaning + normalization* lesson that matches real analytics work
- it requires **no trials** and works offline

What you’ll do
--------------

1. Create a tiny mock business in GnuCash (guided transaction list).
2. Export your transactions using **Export Transactions to CSV** with **Simple Layout OFF**.
3. Run the Track D BYOD normalization pipeline to produce:

   - ``normalized/chart_of_accounts.csv``
   - ``normalized/gl_journal.csv``

Downloads (demo pack)
---------------------

If you want to follow along quickly, download:

- :download:`Transaction list to enter in GnuCash <_downloads/gnucash_demo/gnucash_demo_transactions_to_enter.csv>`
- :download:`Demo export (complex/multi-line) <_downloads/gnucash_demo/gnucash_demo_export_complex.csv>`

The export file above is **adapter-ready** (it matches what the ``gnucash_gl`` adapter expects).

Step 1 — Create a tiny GnuCash book
-----------------------------------

In GnuCash, create a new file (a “book”).

You can either:

- use a default “Small Business” chart of accounts, *or*
- create only the accounts you need (minimum below)

Minimum accounts used in the demo:

- ``Assets:Current Assets:Checking``
- ``Assets:Equipment``
- ``Liabilities:Credit Card``
- ``Liabilities:Sales Tax Payable``
- ``Equity:Owner Capital``
- ``Income:Sales``
- ``Expenses:Supplies``
- ``Expenses:Rent``
- ``Expenses:Shipping``
- ``Expenses:Advertising``

Step 2 — Enter the demo transactions
------------------------------------

Use the downloaded transaction list as your guide:

:download:`gnucash_demo_transactions_to_enter.csv <_downloads/gnucash_demo/gnucash_demo_transactions_to_enter.csv>`

Tips:

- Most entries can be done in the **Checking** register.
- For the “sales tax” example, use a **split** transaction.
- For the credit-card equipment purchase, enter it in the **Credit Card** register.

Step 3 — Export from GnuCash (complex layout)
---------------------------------------------

Use:

``File → Export → Export Transactions to CSV``

Critical setting:

- **Uncheck** “Simple Layout” (this creates the multi-line export)

Export a CSV that includes your accounts and the date range that covers your demo transactions.

Step 4 — Initialize a Track D BYOD project
------------------------------------------

From any folder you like (your BYOD projects can live anywhere):

.. code-block:: console

   pystatsv1 trackd byod init --dest byod/gnucash_demo --profile core_gl

This creates:

- ``tables/`` (where you place exports)
- ``normalized/`` (generated outputs)
- ``config.toml`` (tiny config: profile, tables_dir, adapter)

Step 5 — Point the project at the GnuCash adapter
-------------------------------------------------

Open:

``byod/gnucash_demo/config.toml``

Change:

.. code-block:: toml

   [trackd]
   adapter = "gnucash_gl"

(Leave ``profile = "core_gl"`` as-is.)

Step 6 — Place your export in the expected location
---------------------------------------------------

Copy your GnuCash export CSV to:

``byod/gnucash_demo/tables/gl_journal.csv``

Yes, the file is called ``gl_journal.csv`` even though it is still “raw export.”
The adapter reads this file and writes the canonical tables to ``normalized/``.

If you want to test without GnuCash, copy the demo export instead:

If you installed PyStatsV1 from PyPI (no repo clone), download **"Demo export (complex/multi-line)"** above
and copy that file to ``byod/gnucash_demo/tables/gl_journal.csv``.

If you have the repo source code, you can copy the demo export from this docs folder:


.. code-block:: console

   # (Windows PowerShell)
   copy docs\source\workbook\_downloads\gnucash_demo\gnucash_demo_export_complex.csv byod\gnucash_demo\tables\gl_journal.csv

   # (macOS/Linux)
   cp docs/source/workbook/_downloads/gnucash_demo/gnucash_demo_export_complex.csv byod/gnucash_demo/tables/gl_journal.csv

Step 7 — Normalize
------------------

Run:

.. code-block:: console

   pystatsv1 trackd byod normalize --project byod/gnucash_demo

You should now have:

- ``byod/gnucash_demo/normalized/chart_of_accounts.csv``
- ``byod/gnucash_demo/normalized/gl_journal.csv``

Step 8 — Validate the normalized tables
---------------------------------------

.. code-block:: console

   pystatsv1 trackd validate --datadir byod/gnucash_demo/normalized --profile core_gl

Step 9 — Do a first analysis
----------------------------

Go to:

- :doc:`track_d_byod_gnucash_demo_analysis` (daily totals + basic plots), or
- :doc:`track_d_my_own_data` (the general “apply Track D to your data” bridge)

Troubleshooting
---------------

- If normalization complains about missing columns, re-export and confirm **Simple Layout is OFF**.
- If numbers import incorrectly (decimal commas, etc.), adjust your export settings so amounts use a ``.`` decimal.
