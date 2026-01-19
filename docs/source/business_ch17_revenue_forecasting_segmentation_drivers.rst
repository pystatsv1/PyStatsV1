.. |trackd_run| replace:: d17
.. include:: _includes/track_d_run_strip.rst

Track D — Chapter 17
====================

Revenue forecasting via segmentation + drivers (NSO running case)
-----------------------------------------------------------------

This chapter extends the Track D planning toolkit by building a simple, explainable
forecast of **AR invoice revenue**.

Key idea
~~~~~~~~
Revenue is modeled from two drivers:

- **Invoice count** (how many invoices we expect)
- **Average invoice value** (the typical size of an invoice)

.. math::

   \text{Revenue} = \text{InvoiceCount} \times \text{AvgInvoiceValue}

To make the output actionable for planning, we segment customers into:

- the **top K customers by invoice revenue** (each is its own segment)
- an **All other customers** segment

What you will build
~~~~~~~~~~~~~~~~~~~

1. A customer segmentation table based on AR invoices.
2. A monthly segmented revenue table.
3. A baseline model selection (backtest) for each segment and each driver.
4. A 12-month revenue forecast per segment and in total.

Command
~~~~~~~

From the project root:

.. code-block:: bash

   make business-ch17

Or run the script directly:

.. code-block:: bash

   python -m scripts.business_ch17_revenue_forecasting_segmentation_drivers \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

Outputs
~~~~~~~

Artifacts are written under::

   outputs/track_d/track_d/

CSV / JSON / MD files (chapter folder)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``ch17_customer_segments.csv``
  Customer-level totals and segment assignment.

- ``ch17_ar_revenue_segment_monthly.csv``
  Monthly segmented table with invoice count, invoice amount, and average invoice value.

- ``ch17_series_monthly.csv``
  Monthly TOTAL series (sum across segments).

- ``ch17_backtest_metrics.csv``
  MAE / MAPE metrics for candidate driver methods.

- ``ch17_backtest_total_revenue.csv``
  12-month holdout backtest comparing TOTAL actual vs predicted revenue.

- ``ch17_forecast_next12.csv``
  Next 12 months forecast per segment and TOTAL. (Includes ``forecast_lo`` / ``forecast_hi``
  for TOTAL only.)

- ``ch17_memo.md``
  A short memo with the chosen models and headline results.

- ``ch17_design.json``
  Run metadata, segmentation details, and selected driver methods.

- ``ch17_known_events_template.json``
  Template to record known upcoming events (optional adjustments).

- ``ch17_figures_manifest.csv`` and ``ch17_manifest.json``
  Figure metadata and artifact manifest.

Compatibility aliases
^^^^^^^^^^^^^^^^^^^^^

Two alias files are also written for convenience:

- ``ch17_forecast_next_12m.csv`` (same as ``ch17_forecast_next12.csv``)
- ``ch17_forecast_memo.md`` (same as ``ch17_memo.md``)

Figures
^^^^^^^

Figures are saved under::

   outputs/track_d/track_d/figures/

- ``ch17_fig_segment_revenue_history.png``
- ``ch17_fig_backtest_total_revenue.png``
- ``ch17_fig_forecast_total_revenue.png``

Interpretation guide
~~~~~~~~~~~~~~~~~~~~

- **Segmentation**: Treat the top customers as high-signal leading indicators. Large
  changes in these segments often drive the TOTAL.

- **Invoice count**: A proxy for activity/volume. If count is rising while average value
  is flat, you likely have growth via more orders.

- **Average invoice value**: A proxy for pricing/contract size. If value is rising while
  count is flat, you may have price increases or bigger deals.

- **Backtest**: Use the holdout window to sanity-check whether the methods are stable
  enough for planning. If backtest errors are large, consider shortening the horizon or
  adding a "known events" overlay.
