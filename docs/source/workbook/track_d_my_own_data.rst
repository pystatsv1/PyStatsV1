.. _track_d_my_own_data:

============================================
Track D: Apply what you learned to your data
============================================

This page is the *bridge* between the Track D running case (LedgerLab + NSO v1)
and your own accounting / bookkeeping / finance data.

**The promise of Track D:** you leave with analyst habits that transfer:

- think in **tables** (grain + keys + joins)
- write **contracts** before analysis
- run **checks** (duplicates, missingness, reconciliations)
- produce **reproducible outputs** (tables + charts + short memo)

.. tip::

   If your starting point is a **real export** (GnuCash / QuickBooks / bank / invoices),
   begin with :doc:`track_d_byod` to normalize it into Track D’s canonical tables.
   Then come back to this page for the analysis checklist.


If you haven’t yet, skim these pages first:

- :doc:`track_d_student_edition` (entry point)
- :doc:`track_d_dataset_map` (what the Track D tables are)
- :doc:`track_d_outputs_guide` (what the Track D scripts write)

Two paths
=========

Most student projects fall into one of these paths.
Pick the one that matches what you *actually* have today.

.. list-table:: Choose your path
   :header-rows: 1
   :widths: 28 72

   * - Path
     - When it’s a good fit
   * - **Path A: exports only**
     - You have bank transactions, invoices, bills, payroll exports, but **no** clean GL detail export.
       You can still build a monthly "TB-style" table (a consistent monthly rollup) and do real analysis.
   * - **Path B: GL export**
     - You have a **General Ledger detail** (or journal export) with debits/credits by account.
       You can validate fast and get to trial-balance and statement style outputs quickly.

The "first 30 minutes" recipe below is intentionally minimal.
You can make it fancier later.

Setup once (recommended)
========================

Create a small project folder structure and keep raw exports untouched.

.. code-block:: text

   my_trackd_project/
     raw/        # untouched exports
     working/    # renamed columns, cleaned values
     outputs/    # your tables + charts + short memo
     notes/      # assumptions, mapping notes, QA notes

**Privacy note:** remove names / emails / account numbers before sharing.

Path A: exports only (bank + invoices/bills)
============================================

You can do meaningful analysis without a full GL.
Your first goal is a **monthly rollup table** you can trust.
Think of it as "trial-balance style": consistent columns, consistent sign conventions,
reproducible from your exports.

Minimum required columns
------------------------

**Bank transactions (CSV)**

- ``posted_date`` (or ``date``): transaction date (parseable)
- ``description``: text description
- ``amount``: numeric amount (see sign conventions below)
- *(strongly recommended)* ``bank_txn_id``: unique id from the bank export

**Invoices / sales (CSV)** (if you have them)

- ``invoice_id``: unique id
- ``invoice_date`` (or ``date``): invoice date
- ``amount``: invoice total (or subtotal + tax)
- *(optional but very useful)* ``customer_id`` or ``customer``
- *(optional)* ``paid_date`` or ``status``

Sign conventions (decide early)
-------------------------------

Pick one convention and stick to it:

- **cash inflows are positive**
- **cash outflows are negative**

If your bank export uses the opposite (or splits debit/credit into separate columns),
normalize it during the "working" step.

First 30 minutes recipe
-----------------------

1) Copy exports into ``raw/``.
2) Create cleaned versions in ``working/`` with consistent headers.
3) Produce **one table + one chart + one sanity check**.

Example script (save as ``working/path_a_30min.py`` and run with ``python working/path_a_30min.py``):

.. code-block:: python

   from pathlib import Path
   import pandas as pd
   import matplotlib.pyplot as plt

   ROOT = Path(__file__).resolve().parents[1]
   raw_bank = ROOT / "raw" / "bank.csv"
   out_dir = ROOT / "outputs"
   out_dir.mkdir(exist_ok=True)

   bank = pd.read_csv(raw_bank)

   # --- Required columns (rename if needed)
   required = {"posted_date", "description", "amount"}
   missing = required - set(bank.columns)
   if missing:
       raise ValueError(f"Bank export missing columns: {sorted(missing)}")

   # --- Dates
   bank["posted_date"] = pd.to_datetime(bank["posted_date"], errors="coerce")
   if bank["posted_date"].isna().any():
       bad = bank.loc[bank["posted_date"].isna(), :].head(5)
       raise ValueError(f"Some bank dates failed to parse. Examples:\n{bad}")

   # --- Amounts
   bank["amount"] = pd.to_numeric(bank["amount"], errors="coerce")
   if bank["amount"].isna().any():
       bad = bank.loc[bank["amount"].isna(), :].head(5)
       raise ValueError(f"Some bank amounts failed to parse. Examples:\n{bad}")

   # --- Optional QA: duplicate IDs
   if "bank_txn_id" in bank.columns:
       dup_ids = bank.loc[bank["bank_txn_id"].duplicated(), "bank_txn_id"].unique()
       if len(dup_ids) > 0:
           print(f"WARNING: duplicate bank_txn_id (showing up to 10): {dup_ids[:10]}")

   # --- Month rollup
   bank["month"] = bank["posted_date"].dt.to_period("M").astype(str)

   g = bank.groupby("month")["amount"]
   monthly = pd.DataFrame(
       {
           "cash_in": g.apply(lambda s: s[s > 0].sum()),
           "cash_out": g.apply(lambda s: -s[s < 0].sum()),
           "net_cash": g.sum(),
           "n_txns": g.size(),
       }
   ).reset_index()

   # Sanity check: net_cash = cash_in - cash_out
   max_err = (monthly["cash_in"] - monthly["cash_out"] - monthly["net_cash"]).abs().max()
   if max_err > 1e-6:
       raise ValueError(f"Sanity check failed (cash_in - cash_out != net_cash). max_err={max_err}")

   # Save the table
   monthly.to_csv(out_dir / "monthly_cash_summary.csv", index=False)

   # One chart: net cash by month
   plt.figure()
   plt.plot(monthly["month"], monthly["net_cash"], marker="o")
   plt.xticks(rotation=45, ha="right")
   plt.title("Net cash flow by month")
   plt.tight_layout()
   plt.savefig(out_dir / "net_cash_by_month.png", dpi=150)

   print("Wrote:")
   print(" -", out_dir / "monthly_cash_summary.csv")
   print(" -", out_dir / "net_cash_by_month.png")

What you just did is the Track D pattern:

- define a contract (required columns)
- normalize types (dates, numeric)
- run one QA check (duplicates)
- produce a reproducible table + chart

From there, you can grow into richer questions (cash forecasting, seasonality, outliers,
customer payment behavior if you have invoices).

Path B: GL export (journal / general ledger detail)
===================================================

If you have GL detail, you can validate and build trial-balance style tables fast.

Minimum required columns
------------------------

At minimum:

- ``date``: transaction date
- ``account_id`` (or ``account``): account identifier
- ``debit``: numeric debit amount (0 if none)
- ``credit``: numeric credit amount (0 if none)

Strongly recommended:

- ``txn_id`` (or ``journal_entry_id``): lets you check balance per transaction
- ``description``

Even better (optional):

- a Chart of Accounts export you can join on ``account_id`` with ``account_name`` and ``account_type``

First 30 minutes recipe
-----------------------

Example script (save as ``working/path_b_30min.py`` and run with ``python working/path_b_30min.py``):

.. code-block:: python

   from pathlib import Path
   import pandas as pd
   import matplotlib.pyplot as plt

   ROOT = Path(__file__).resolve().parents[1]
   raw_gl = ROOT / "raw" / "gl_detail.csv"
   out_dir = ROOT / "outputs"
   out_dir.mkdir(exist_ok=True)

   gl = pd.read_csv(raw_gl)

   required = {"date", "account_id", "debit", "credit"}
   missing = required - set(gl.columns)
   if missing:
       raise ValueError(f"GL export missing columns: {sorted(missing)}")

   gl["date"] = pd.to_datetime(gl["date"], errors="coerce")
   if gl["date"].isna().any():
       bad = gl.loc[gl["date"].isna(), :].head(5)
       raise ValueError(f"Some GL dates failed to parse. Examples:\n{bad}")

   for col in ["debit", "credit"]:
       gl[col] = pd.to_numeric(gl[col], errors="coerce").fillna(0.0)

   gl["month"] = gl["date"].dt.to_period("M").astype(str)

   # Check 1: debits = credits per month (basic reconciliation)
   monthly_dc = gl.groupby("month")[["debit", "credit"]].sum().reset_index()
   monthly_dc["diff"] = monthly_dc["debit"] - monthly_dc["credit"]

   max_diff = monthly_dc["diff"].abs().max()
   if max_diff > 1e-6:
       print(monthly_dc)
       raise ValueError(
           "Debits != credits by month. This often means the export was filtered, "
           "or some lines are missing. Fix this before you trust any analysis."
       )

   # Optional Check 2: debits = credits per txn_id (stronger)
   if "txn_id" in gl.columns:
       per_txn = gl.groupby("txn_id")[["debit", "credit"]].sum()
       per_txn["diff"] = per_txn["debit"] - per_txn["credit"]
       bad = per_txn[per_txn["diff"].abs() > 1e-6]
       if len(bad) > 0:
           raise ValueError(
               f"Found {len(bad)} unbalanced txn_id rows. "
               "Your export may be incomplete or mis-keyed."
           )

   # Build a monthly TB-style table: debit, credit, net (debit-positive convention)
   tb = gl.groupby(["month", "account_id"], as_index=False)[["debit", "credit"]].sum()
   tb["net"] = tb["debit"] - tb["credit"]

   tb.to_csv(out_dir / "tb_monthly.csv", index=False)

   # One chart: total debits and credits by month (a quick integrity picture)
   plt.figure()
   plt.plot(monthly_dc["month"], monthly_dc["debit"], marker="o", label="debit")
   plt.plot(monthly_dc["month"], monthly_dc["credit"], marker="o", label="credit")
   plt.xticks(rotation=45, ha="right")
   plt.title("GL totals by month (should match)")
   plt.legend()
   plt.tight_layout()
   plt.savefig(out_dir / "gl_debits_credits_by_month.png", dpi=150)

   print("Wrote:")
   print(" -", out_dir / "tb_monthly.csv")
   print(" -", out_dir / "gl_debits_credits_by_month.png")

You now have:

- a **reconciliation check** (debits == credits)
- a **monthly TB-style table** you can analyze
- a **chart** you can put in a memo

From here, you can add one join (Chart of Accounts) and start doing Track D-style
statement rollups or account-level diagnostics.

Common pitfalls (and what to do)
================================

Date parsing
------------

- Mixed formats (``MM/DD/YYYY`` vs ``YYYY-MM-DD``) cause silent errors.
- Always use ``pd.to_datetime(..., errors="coerce")`` and *fail fast* if you get nulls.

Signs and "negative" exports
----------------------------

- Some systems export credits as negative numbers instead of a separate credit column.
- Decide your convention, normalize once, and document it in ``notes/assumptions.txt``.

Duplicate IDs
-------------

- Bank feeds can duplicate rows (Track D includes this on purpose).
- If you have IDs, check duplicates and decide: remove exact duplicates, or keep and flag.

Missing months / incomplete exports
-----------------------------------

- If debits != credits by month, the export is likely filtered or incomplete.
- Fix the export first. Don’t "patch" it with analysis code.

Month boundaries
----------------

- Accruals, backdated entries, and late postings create confusing month swings.
- Track D teaches the right response: *describe it, measure it, and document the limitation.*

Template header pack (copy/paste)
=================================

If you want a starting point without hunting for column names, these tiny CSV templates
are safe to download and copy into your own project.

- :download:`gl_detail_minimal.csv <_downloads/track_d_headers/gl_detail_minimal.csv>`
- :download:`chart_of_accounts_minimal.csv <_downloads/track_d_headers/chart_of_accounts_minimal.csv>`
- :download:`bank_transactions_minimal.csv <_downloads/track_d_headers/bank_transactions_minimal.csv>`
- :download:`invoices_minimal.csv <_downloads/track_d_headers/invoices_minimal.csv>`

Next steps
==========

Once you can produce one table + one chart + one check, you are ready for:

- a short "executive summary" memo (what you found + what limits confidence)
- deeper Track D-style joins (drivers, segmentation)
- classroom labs and rubrics (the next Track D docs pages)
