.. _track_d_byod_gnucash_demo_analysis:

===========================================
GnuCash demo: daily totals + first analysis
===========================================

Once you have a normalized BYOD project (see :doc:`track_d_byod_gnucash`), you can turn accounting tables into
a simple “business time series” for basic statistics and forecasting.

What we’ll build
----------------

A small daily table:

- ``date``
- ``revenue_proxy`` (credits to Income accounts)
- ``expenses_proxy`` (debits to Expense accounts)

Download (prebuilt)
-------------------

If you want to jump straight to analysis without running the normalization step first:

- :download:`gnucash_demo_daily_totals.csv <_downloads/gnucash_demo/gnucash_demo_daily_totals.csv>`

Option A — Build daily totals from your normalized tables
---------------------------------------------------------

Assume your BYOD project is at ``byod/gnucash_demo`` and you have:

- ``byod/gnucash_demo/normalized/gl_journal.csv``
- ``byod/gnucash_demo/normalized/chart_of_accounts.csv``

Create a tiny script (for example ``scripts/gnucash_daily_totals.py``) with:

.. code-block:: python

   from pathlib import Path
   import pandas as pd

   root = Path("byod/gnucash_demo")

   gl = pd.read_csv(root / "normalized" / "gl_journal.csv")
   coa = pd.read_csv(root / "normalized" / "chart_of_accounts.csv")

   gl["date"] = pd.to_datetime(gl["date"], errors="coerce")

   gl["debit"] = pd.to_numeric(gl["debit"], errors="coerce").fillna(0.0)
   gl["credit"] = pd.to_numeric(gl["credit"], errors="coerce").fillna(0.0)

   gl = gl.merge(coa[["account_id", "account_type"]], on="account_id", how="left")

   revenue = (
       gl.query("account_type == 'Income'")
         .groupby(gl["date"].dt.date)["credit"]
         .sum()
         .rename("revenue_proxy")
   )

   expenses = (
       gl.query("account_type == 'Expenses'")
         .groupby(gl["date"].dt.date)["debit"]
         .sum()
         .rename("expenses_proxy")
   )

   daily = (
       pd.concat([revenue, expenses], axis=1)
         .fillna(0.0)
         .reset_index()
         .rename(columns={"index": "date"})
   )

   out = root / "normalized" / "daily_totals.csv"
   daily.to_csv(out, index=False)
   print("Wrote:", out)
   print(daily)

Option B — Run the existing “My Own Data” explore scaffold
----------------------------------------------------------

PyStatsV1 includes a beginner-friendly scaffold script:

``scripts/my_data_01_explore.py``

Run it against the daily totals CSV (either the prebuilt download, or the file you generated above):

.. code-block:: console

   python scripts/my_data_01_explore.py --csv byod/gnucash_demo/normalized/daily_totals.csv --outdir outputs/gnucash_demo

This will write a few simple outputs under ``outputs/gnucash_demo/`` (tables + quick plots).
