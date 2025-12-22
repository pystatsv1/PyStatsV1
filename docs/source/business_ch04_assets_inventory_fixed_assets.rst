Business Chapter 4: Assets — Inventory and Fixed Assets
=======================================================

In this chapter we zoom in on **assets**—resources the business controls that are expected to provide future economic benefit.
In the NSO v1 running case, assets show up in two very different “data shapes”:

- **Inventory**: many small movements (buy/sell/adjust) that accumulate over time.
- **Fixed assets**: relatively few purchases, but each asset produces a long stream of depreciation.

Chapter 4 introduces two foundational bookkeeping skills that also behave like **data quality controls**:

1. Building an **inventory roll-forward** from event-level movements and tying it back to the trial balance.
2. Building a **depreciation roll-forward** and tying it back to the trial balance and financial statements.

What you should be able to do after this chapter
-----------------------------------------------

Accounting concepts
^^^^^^^^^^^^^^^^^^
- Explain the difference between **current assets** (inventory) and **long‑term assets** (property, plant & equipment).
- Describe how inventory flows into the income statement via **Cost of Goods Sold (COGS)**.
- Explain why we record **Accumulated Depreciation** (a contra‑asset) and how depreciation affects net income and cash flow.

Python / software concepts
^^^^^^^^^^^^^^^^^^^^^^^^^^
- Treat CSV datasets as **interfaces** with explicit schema contracts (required tables + required columns).
- Recompute “expected” balances from event-level data and compare to reported balances (a basic **reconciliation** pattern).
- Produce chapter outputs as reproducible artifacts: tidy CSVs + a small JSON summary for dashboards/CI.

Inputs and outputs
------------------

Inputs (NSO v1 dataset folder)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This chapter is designed to run against a generated dataset (see :mod:`scripts.sim_business_nso_v1`).
The key input tables for Chapter 4 are:

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Table
     - Purpose
   * - ``trial_balance_monthly.csv``
     - The monthly trial balance (account-level balances). We use it as the *control total* to tie our subledgers back to.
   * - ``inventory_movements.csv``
     - Event-level inventory activity (purchases, sales consumption, adjustments) with quantities and unit costs.
   * - ``fixed_assets.csv``
     - Master data for each asset (cost, in-service month, useful life, method).
   * - ``depreciation_schedule.csv``
     - Precomputed depreciation schedule produced by the simulator (used for validation + illustration).

Outputs (``outdir``)
^^^^^^^^^^^^^^^^^^^^
The Chapter 4 script writes:

- ``business_ch04_summary.json`` — key checks and metrics (for CI/automation).
- ``business_ch04_inventory_rollforward.csv`` — monthly inventory roll-forward and valuation summary.
- ``business_ch04_depreciation_rollforward.csv`` — monthly depreciation / accumulated depreciation / net book value.
- ``business_ch04_margin_bridge.csv`` — a small “bridge” table connecting sales → COGS → gross margin.
- ``business_ch04_inventory_over_time.png`` — quick visualization of inventory levels over time.
- ``business_ch04_depreciation_and_nbv.png`` — visualization of depreciation and net book value.

Where these tables come from in code
------------------------------------

- Simulator: :mod:`scripts.sim_business_nso_v1` (writes the NSO v1 dataset)
- Contracts: :mod:`scripts._business_schema` (declares required tables/columns)
- Chapter 4 analysis: :mod:`scripts.business_ch04_assets_inventory_fixed_assets`

Running the chapter
-------------------

From the repository root, generate the dataset and run the chapter analysis:

.. code-block:: bash

   # Generate the multi-month NSO v1 running case (deterministic)
   make business-nso-sim

   # Run Chapter 4 analysis and write artifacts to outputs/track_d
   make business-ch04

Or run the script directly:

.. code-block:: bash

   python -m scripts.business_ch04_assets_inventory_fixed_assets      --datadir data/synthetic/nso_v1      --outdir outputs/track_d      --seed 123

If something fails, start with schema validation:

.. code-block:: bash

   make business-validate

Inventory: what we are checking
-------------------------------

Inventory accounting in one paragraph
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When the business purchases inventory, it records an **asset** (Inventory). When it sells goods,
the cost of the goods sold is moved from Inventory to **COGS** on the income statement.
This means the balance of Inventory depends on the history of purchases and sales—exactly the kind
of thing that benefits from a subledger.

How the inventory roll-forward works in this project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The NSO v1 dataset includes an event stream in ``inventory_movements.csv``. Each row describes:

- the month and date of the movement,
- the SKU,
- movement type (purchase / sale / adjustment),
- quantity and unit cost,
- and the dollar amount (qty × unit cost).

The Chapter 4 script aggregates these movements by month to produce an inventory roll-forward and compares it to
inventory-related trial balance accounts. Any persistent mismatch usually means one of:

- missing event rows,
- incorrect sign conventions,
- or inconsistent account mapping between the subledger and the GL.

Fixed assets and depreciation: what we are checking
---------------------------------------------------

Why depreciation exists
^^^^^^^^^^^^^^^^^^^^^^^
Fixed assets (equipment, computers, vehicles) typically provide benefit over multiple months or years.
Instead of expensing the full purchase immediately, we **capitalize** the cost as an asset and then recognize the expense gradually as
**depreciation**. Depreciation reduces net income but does not directly consume cash; in a cash flow statement, it is typically added back
under operating cash flow (indirect method).

Straight-line depreciation (the default here)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For an asset with cost :math:`C`, salvage value :math:`S`, and useful life of :math:`L` months,
straight-line monthly depreciation is:

.. math::

   \text{Depreciation per month} = \frac{C - S}{L}

The depreciation roll-forward also tracks:

- **Accumulated Depreciation** (contra-asset): cumulative depreciation to date
- **Net Book Value**: :math:`C - \text{Accumulated Depreciation}`

The Chapter 4 script recomputes and summarizes these quantities, then ties totals back to the trial balance.

Reading the outputs
-------------------

A quick way to inspect the outputs in Python:

.. code-block:: python

   import pandas as pd

   inv = pd.read_csv("outputs/track_d/business_ch04_inventory_rollforward.csv")
   dep = pd.read_csv("outputs/track_d/business_ch04_depreciation_rollforward.csv")

   print(inv.head())
   print(dep.head())

Exercises and extensions
------------------------

1. **Change the seed** and regenerate the NSO dataset. Do the checks still pass?
2. Add a new fixed asset row (in the simulator) and verify the depreciation roll-forward and trial balance impacts.
3. Extend depreciation logic to support another method (e.g., declining balance) and compare the time profile of expense.

Notes for maintainers
---------------------

- The schema requirements for the NSO v1 dataset are centralized in :mod:`scripts._business_schema`.
  If you add a new subledger table, update the contracts and add a test that verifies the table is written.
- The “contracts → simulator → chapter analysis → tests” pipeline is deliberate: it turns bookkeeping rules into
  repeatable, testable software.
