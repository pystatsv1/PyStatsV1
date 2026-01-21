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
- ``revenue_proxy`` (net credits to Revenue accounts)
- ``expenses_proxy`` (net debits to Expense accounts)
- ``net_proxy`` (revenue_proxy − expenses_proxy)

Download (prebuilt)
-------------------

If you want to jump straight to analysis without running the normalization step first:

- :download:`gnucash_demo_daily_totals.csv <_downloads/gnucash_demo/gnucash_demo_daily_totals.csv>`

Option A — Build daily totals from your normalized tables
---------------------------------------------------------

Assume your BYOD project is at ``<BYOD_DIR>`` and you have:

- ``<BYOD_DIR>/normalized/gl_journal.csv``
- ``<BYOD_DIR>/normalized/chart_of_accounts.csv``

Run the built-in helper:

.. code-block:: console

   pystatsv1 trackd byod daily-totals --project <BYOD_DIR>

   # (optional) choose an explicit output path
   pystatsv1 trackd byod daily-totals --project <BYOD_DIR> --out <BYOD_DIR>/normalized/daily_totals.csv

Need a reminder of options? Run: ``pystatsv1 trackd byod daily-totals --help``

This writes:

- ``<BYOD_DIR>/normalized/daily_totals.csv``

Option B — Quick first analysis (no repo clone required)
--------------------------------------------------------

Once you have ``normalized/daily_totals.csv``, you can do a quick first pass with pandas.
This snippet prints a few summary stats and writes a simple plot:

.. code-block:: console

   python - <<'PY'
   import pandas as pd
   import matplotlib.pyplot as plt
   from pathlib import Path

   project = Path("byod/gnucash_demo")  # <-- set to your BYOD project folder (e.g., "<BYOD_DIR>")

   csv_path = project / "normalized" / "daily_totals.csv"
   outdir = Path("outputs/gnucash_demo")
   outdir.mkdir(parents=True, exist_ok=True)

   df = pd.read_csv(csv_path, parse_dates=["date"])
   df = df.sort_values("date")

   print(df.describe(include="all"))

   ax = df.plot(x="date", y=["revenue_proxy", "expenses_proxy", "net_proxy"])
   ax.figure.tight_layout()
   ax.figure.savefig(outdir / "daily_totals.png")
   print(f"Wrote: {outdir / 'daily_totals.png'}")
   PY

(If you *are* working from the repo source, you can also adapt ``scripts/my_data_01_explore.py`` to your needs.)
