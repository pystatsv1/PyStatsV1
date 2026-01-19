Track D — Chapter 14
====================

.. |trackd_run| replace:: d14
.. include:: _includes/track_d_run_strip.rst


Regression Driver Analysis (NSO running case)
---------------------------------------------

This chapter turns “operational activity” into an **explainable planning model**.

In accounting work you often start from outcomes:

- Revenue was up (or down).
- COGS moved.
- Gross margin shifted.

That outcome view is essential, but it’s not always sufficient for planning and control.
When leadership asks:

- “What happens to COGS if we sell 15% more units next month?”
- “Is margin pressure mostly price, volume, or some fixed baseline cost?”
- “Are we seeing higher revenue because we sold more… or because invoices changed (mix/activity)?”

…you need a **driver lens**.

**Regression driver analysis** is a practical way to estimate simple relationships like:

- a **baseline** level (intercept): “what tends to happen even if activity is low”
- a **rate** (slope): “how much outcome changes per unit of activity”

You’ll build this lens for the North Shore Outfitters (NSO) running case using monthly data.


Where this fits in Track D
--------------------------

This chapter is intentionally downstream of earlier Track D ideas:

- Chapter 12 (Hypothesis Testing): disciplined interpretation; avoid overconfidence from noisy data.
- Chapter 13 (Correlation, Causation, Controlled Comparisons): *correlation is not causation* and
  “third factors” often drive two lines together.

Regression is powerful, but it can also create false confidence if used carelessly.
So we carry forward the Chapter 13 discipline here:

- Use regression as a **driver lens**
- Prefer **simple, explainable models**
- Check residuals and sanity-check assumptions
- Treat results as **planning inputs**, not proof


What you will build
-------------------

You will produce two things:

1) A monthly **driver table** that lines up activity measures with financial outcomes.

2) Three small regression models:

- **m1:** ``COGS ~ units_sold`` (fixed + variable cost per unit lens)
- **m2:** ``Revenue ~ units_sold`` (baseline + average price-per-unit lens)
- **m3:** ``Revenue ~ units_sold + invoice_count`` (two-driver “mix/activity check”)

The goal is not “best possible prediction.”
The goal is **simple, auditable explanations** that help accounting planning + control.


The driver table (what it is and where it comes from)
-----------------------------------------------------

The Chapter 14 script builds a monthly table with these columns:

.. list-table:: Chapter 14 driver table fields
   :header-rows: 1
   :widths: 18 22 60

   * - Column
     - Meaning
     - Source in NSO outputs
   * - ``month``
     - Month key (YYYY-MM)
     - Derived from date fields in each input file
   * - ``month_dt``
     - Month as a real date (YYYY-MM-01) for sorting/plotting
     - Derived
   * - ``units_sold``
     - Units sold in that month (positive count)
     - ``inventory_movements.csv`` where ``movement_type == sale_issue``.
       (In the simulator, sale issues are negative inventory movements, so the script flips the sign.)
   * - ``invoice_count``
     - Count of invoices issued in that month
     - ``ar_events.csv`` where ``event_type == invoice`` (grouped and counted by month)
   * - ``sales_revenue``
     - Monthly sales revenue
     - ``statements_is_monthly.csv`` where ``line == Sales Revenue``
   * - ``cogs``
     - Monthly cost of goods sold
     - ``statements_is_monthly.csv`` where ``line == Cost of Goods Sold``

Why these drivers?
^^^^^^^^^^^^^^^^^^

Accounting planning usually needs a bridge between **operations** and **financial outcomes**.

- Units sold is a natural driver for both revenue and COGS in many product businesses.
- Invoice count is not “better than units,” but it can be a useful **activity proxy**
  (and a warning sign for mix changes, bundling, partial shipments, pricing patterns, etc.).

This chapter keeps the driver set intentionally small. In real work you might add:

- labor hours, headcount, shipments, store traffic, returns
- discount rate, product mix %, channel mix %, seasonality indicators
- capacity constraints (overtime, stockouts)


Regression models (m1, m2, m3)
------------------------------

All three models use ordinary least squares (OLS). Conceptually:

- ``y = intercept + slope * x + residual``

- **Intercept** is the baseline component.
- **Slope** is the rate per unit of driver.
- **Residuals** are what the driver did not explain.

The script uses ``statsmodels`` and includes an intercept term (a constant).

Model 1: COGS as a function of units sold
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**m1:** ``COGS ~ units_sold``

Interpretation in planning terms:

- **Intercept (baseline COGS):**
  costs that tend to appear even at low activity (minimum staffing, spoilage, fixed handling, etc.).
  In some businesses baseline COGS should be near zero; in others it may not be.

- **Slope (variable cost per unit):**
  the estimated cost-per-unit implied by the data (a “rate”).

How you use it:

- Build a cost forecast from a unit forecast.
- Explain COGS variance as “rate vs baseline vs unexplained residual.”

Model 2: Revenue as a function of units sold
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**m2:** ``Revenue ~ units_sold``

Interpretation:

- **Intercept (baseline revenue):**
  in many settings this should be near zero. If it is not, that’s a signal to investigate:
  timing, returns, non-unit revenue streams, seasonality, or a model mismatch.

- **Slope (average price per unit lens):**
  an implied average revenue per unit. This is *not* a SKU-level price;
  it’s a blended rate across product mix for the period.

How you use it:

- Translate a unit plan into a revenue plan.
- Detect periods where price/mix changes break the “stable rate” assumption.

Model 3: Revenue as a function of units sold + invoice count
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**m3:** ``Revenue ~ units_sold + invoice_count``

This is a simple two-driver extension:

- If invoice count adds meaningful explanatory power beyond units sold,
  you may be seeing changes in ordering patterns or mix (e.g., more small invoices,
  more split shipments, different channel behavior).

- If invoice count does *not* add anything (small coefficient, noisy, low incremental fit),
  that’s also useful: units alone may be sufficient for the current planning lens.

This is not “the final truth.” It’s a lightweight check that encourages better questions.


Interpreting outputs like an accountant
---------------------------------------

Intercepts and slopes: baseline vs rate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A helpful mental model is:

- **Intercept** = baseline component (what happens at “zero-ish” activity)
- **Slope** = marginal rate (how much outcome changes per unit of activity)

This matches common accounting narratives:

- “There is a fixed component plus a variable component.”
- “Most of the change is volume-driven; rate is stable.”
- “The rate is drifting — pricing/mix or cost structure is changing.”

R²: “how much of the story is volume”
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

R² is the fraction of variance explained by the model *in-sample*.

- High R² can mean the driver captures the main movement (often volume/seasonality).
- Low R² can mean the driver is incomplete or the process changed.

Accounting interpretation:

- R² is not “goodness” by itself; it’s a signpost.
- Even a moderate R² can be useful if the slope is stable and interpretable.

Residuals: what the drivers didn’t explain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Residuals are where accounting insight often lives:

- promotions and discounting
- unusual returns
- supply shocks and stockouts
- one-time events or timing effects

A healthy workflow is:

1) Fit the simple model.
2) Inspect residual patterns.
3) Decide whether you need more drivers or segmentation.

.. important::

   If pricing or product mix changes materially, re-fit the model and re-check residuals.
   Stable slopes are an assumption, not a guarantee.


How to run the chapter
----------------------

Prerequisite: NSO dataset
^^^^^^^^^^^^^^^^^^^^^^^^^

Chapter 14 expects the NSO v1 synthetic dataset to exist (it is generated by the Track D simulator).
If you already ran earlier Track D chapters locally, you likely have it.

To (re)generate NSO v1:

.. code-block:: bash

   make business-nso-sim

This writes the NSO v1 dataset under:

- ``data/synthetic/nso_v1/``

Run Chapter 14
^^^^^^^^^^^^^^

Run the Chapter 14 target:

.. code-block:: bash

   make business-ch14

Note on output location:

- The Makefile passes ``--outdir outputs/track_d``.
- The Chapter 14 script writes inside a nested folder and prints the final path.

So you should expect artifacts under something like:

- ``outputs/track_d/track_d/``


Outputs and how to inspect them
-------------------------------

The chapter writes a small “analysis pack” you can use for inspection, debugging, or reporting.

Core artifacts
^^^^^^^^^^^^^^

- ``ch14_driver_table.csv``
  The monthly driver table (month, units_sold, invoice_count, revenue, cogs).
  Start here—open it and sanity-check the numbers.

- ``ch14_regression_design.json``
  A lightweight “design contract” describing expected inputs, driver definitions, and model formulas.
  Use this for reproducibility and review.

- ``ch14_regression_summary.json``
  Machine-readable regression results (parameters, R², and a small forecast example).
  Useful for downstream automation (dashboards, reports, tests).

- ``ch14_regression_memo.md``
  A short human-readable memo summarizing the key results.
  This is intentionally brief: it’s a starter “executive narrative.”

Figures
^^^^^^^

- ``ch14_figures_manifest.csv``
  A manifest listing each figure saved by the script (path + chart metadata).

- ``figures/``
  PNG charts (scatter + fit line, plus a residual-style view for the multi-driver check).

A quick inspection workflow:

1) Open ``ch14_driver_table.csv`` and verify the month alignment.
2) Read ``ch14_regression_memo.md`` to see the story.
3) Open the figures to check whether relationships look linear and whether outliers dominate.
4) Use ``ch14_regression_summary.json`` if you want to extract slopes/intercepts programmatically.


Guardrails (read this before you sell the story)
------------------------------------------------

Regression is a **driver lens**, not a causality machine.

Common failure modes in accounting settings:

- **Seasonality / timing** drives both the driver and the outcome (spurious fit).
- **Mix shifts** break slope stability (price per unit or cost per unit changes).
- **Capacity constraints** create nonlinearity (overtime, stockouts, shipping changes).
- **Definition drift** (what counts as an invoice, what counts as a unit) changes over time.

Use regression to support planning conversations like:

- “Given our recent pattern, the implied cost-per-unit is X.”
- “If we hit Y units next month, the model implies COGS around Z, plus/minus residual noise.”
- “This month looks unusual relative to the driver story; let’s investigate why.”


Troubleshooting
---------------

Missing input files (FileNotFoundError)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you see an error like “Expected inventory_movements.csv … but not found”:

- Confirm you generated NSO v1:

  .. code-block:: bash

     make business-nso-sim

- Confirm the files exist under ``data/synthetic/nso_v1/``:
  ``inventory_movements.csv``, ``ar_events.csv``, ``statements_is_monthly.csv``.

Wrong output directory / permission issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If artifacts don’t appear under ``outputs/track_d/track_d/``:

- Ensure your working tree is the repo root and you’re running targets from there.
- Confirm you have permission to create the ``outputs/`` directory on your machine.
- If needed, clear old outputs and re-run:

  .. code-block:: bash

     make clean
     make business-ch14

Plots not rendering / backend issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This chapter saves plots to PNG files; it does not require an interactive GUI.
If you hit a matplotlib backend error on Windows, ensure you’re using the project’s
recommended environment (venv) and that your matplotlib install is healthy.



What’s next (Chapter 15+)
-------------------------

Chapter 14 gives you the core regression driver workflow:

- build a driver table
- fit simple explainable models
- produce artifacts that are reviewable (CSV/JSON/MD/figures)

The natural next steps for Chapter 15+ are to expand from “single driver lens” to
“planning-grade forecasting,” for example:

- add seasonality (month indicators) and compare fit/residuals
- segment by product line or channel (separate slopes for different mixes)
- introduce richer drivers (labor hours, shipments, discounts)
- build a repeatable rolling forecast workflow and variance decomposition narrative

If Chapter 14 is your first regression chapter, you’re already in the right place:
the goal is not sophistication—it’s **usable, auditable models that improve decisions**.


Appendix 14B: NSO v1 data dictionary cheat sheet
------------------------------------------------

For a compact “what table is what” reference (grain, keys, joins, checks), see:

- :doc:`business_appendix_ch14b_nso_v1_data_dictionary`


Appendix 14C: Chapter 14 artifact dictionary
--------------------------------------------

For a compact reference that explains every Chapter 14 output artifact (what it is, what it’s for,
and what to look at first), see:

- :doc:`business_appendix_ch14c_ch14_artifact_dictionary`


Appendix 14D: Artifact QA checklist (what to verify before sharing results)
---------------------------------------------------------------------------

Before you share the Chapter 14 memo or coefficients, use the “big picture” QA checklist:

- :doc:`business_appendix_ch14d_artifact_qa_checklist_big_picture`


Appendix 14E: applying this chapter to your own data
----------------------------------------------------

To adapt the Chapter 14 workflow (driver table + explainable regression + artifacts) to your own
real-world business data, see:

- :doc:`business_appendix_ch14e_apply_to_real_world`