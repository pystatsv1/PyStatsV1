Track D — Chapter 10: Probability and risk in business terms
============================================================

.. |trackd_run| replace:: d10
.. include:: _includes/track_d_run_strip.rst

Chapter 10 translates abstract probability into operational business risk.
Instead of saying **"there is a 5% chance"**, the goal is to say:

- **"We will hit $0 cash about 1 out of every 20 months"**
- **"Expected bad debt is about $X, but the p90 worst case is about $Y"**

This chapter focuses on communicating uncertainty honestly **without false precision**
(e.g., avoid predicting ``$1,000,043.22`` when ``~$1.0M`` is the honest level of accuracy).

Learning objectives
-------------------

By the end of Chapter 10, you should be able to:

- **Translate probability into operational risk** (cash shortfalls, payroll risk, stockouts).
- **Build scenario distributions** using simple historical resampling and interpret percentiles.
- **Communicate uncertainty** in a memo with explicit assumptions and "unknown unknowns".

What we implement in code
-------------------------

This chapter implements a small, deterministic risk report:

- ``scripts/business_ch10_probability_risk.py``

It uses the Track D NSO v1 dataset and reuses Chapter 8's A/R slicing logic
as a simple input to risk estimation.

Risk models (simple, defensible)
--------------------------------

Cash buffer sizing (95% confidence)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We use historical monthly net cash changes (from ``bank_statement.csv``) and a
bootstrap simulation:

- Sample the past monthly net cash changes with replacement.
- Generate many 12-month futures.
- Track the worst (minimum) cash balance in each simulated future.
- The **buffer needed** is the amount required to keep cash from going negative.

We report a **p95** buffer: a buffer that prevents a cash shortfall in ~95% of
simulated futures.

Bad debt risk (expected loss and p90)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For a small-business case study, we use a conservative proxy:

- Treat "severely late" collections (>= 90 days outstanding) as a signal of elevated default risk.
- Estimate a monthly "severe late rate" from payment slices.
- Apply that rate to the latest A/R balance to produce:

  - **Expected loss** (mean rate × A/R)
  - **p90 worst case** (p90 rate × A/R)

This is not a substitute for a full credit model; it is an audit-friendly
starting point with explicit assumptions.

Chapter outputs
---------------

Running Chapter 10 writes these outputs to ``outdir``:

- ``ch10_figures_manifest.csv``
  - Audit log of figures (filenames, chart types, labels, guardrail notes).
- ``ch10_risk_memo.md``
  - Short memo translating risk into operational terms (with assumptions).
- ``ch10_risk_summary.json``
  - Structured summary including key percentiles and configuration.
- ``figures/*.png``
  - Example charts:

    - ``ch10_cash_flow_hist.png``
    - ``ch10_cash_buffer_ecdf.png``
    - ``ch10_bad_debt_loss_ecdf.png``

How to run
----------

From the repo root:

.. code-block:: bash

   make business-nso-sim
   make business-ch10

Or run the script directly:

.. code-block:: bash

   python -m scripts.business_ch10_probability_risk \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

Ethics and guardrails
---------------------

- Prefer ranges and percentiles over single-point numbers.
- Avoid false precision by rounding currency to sensible units.
- Always state the assumptions behind the simulation, and name at least a few
  "unknown unknowns" (shocks not present in historical data).
