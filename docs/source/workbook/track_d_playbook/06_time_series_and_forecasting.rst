Time series + forecasting for accounting data
=============================================

**Why this exists:** Forecasting becomes less scary once you’ve built clean daily/monthly series. This chapter outlines the progression.

Learning objectives
-------------------

- Explain trend, seasonality, and noise using accounting time series.
- Build a baseline forecast and evaluate it.
- Understand when forecasting is inappropriate (garbage in / structural breaks).

Outline
-------

Start with baselines
--------------------

- Start from ``normalized/gl_journal.csv`` and build a clean daily/monthly series (revenue proxy, expense totals, or cash).
- Last value, moving average, seasonal naive.
- Always do a simple backtest (train on earlier months, test on later months).
- Compare forecasts with simple error metrics.

Add explanatory variables
-------------------------

- Promotions, holidays, payroll cycles, or other known drivers.
- Use regression as a driver model (not magic).

Keep it business-grounded
-------------------------

- Always interpret: what would make the forecast wrong?
- Document assumptions and data limitations.
- Structural breaks examples: pricing changes, a new location, system migrations, one-time events, policy changes.

Where this connects in the workbook
-----------------------------------

- :doc:`../track_d_chapter_index` (chapters that introduce forecasting ideas)
- :doc:`../track_d_my_own_data` (how to apply the same methods to your exports)

.. note::

   This page is intentionally an outline right now. Expand it incrementally as we refine Track D narrative.
