Track D — Chapter 14
====================

Regression Driver Analysis (NSO running case)
---------------------------------------------

This chapter shows how to turn operational activity into a simple, explainable
regression model that supports accounting planning + control.

What you will build
-------------------

- A monthly **driver table**:
  - Units sold (from ``inventory_movements.csv``; ``sale_issue`` rows)
  - Invoice count (from ``ar_events.csv``; ``invoice`` rows)
  - Revenue and COGS (from ``statements_is_monthly.csv``)

- Three regression models:
  - ``COGS ~ units_sold`` (fixed + variable)
  - ``Revenue ~ units_sold`` (average selling price lens)
  - ``Revenue ~ units_sold + invoice_count`` (simple multi-driver check)

Run the chapter
---------------

From repo root::

  make business-ch14

Outputs
-------

Written to::

  outputs/track_d/

Key files:

- ``ch14_driver_table.csv``
- ``ch14_regression_design.json``
- ``ch14_regression_summary.json``
- ``ch14_regression_memo.md``
- ``ch14_figures_manifest.csv``
- ``figures/`` (PNG charts)

Guardrails
----------

Regression is a **driver lens**. It does not prove causation.
Interpret slopes as *rates* and intercepts as *baselines*.
