Appendix 14E: Applying Track D through Chapter 14 to your own real-world data
============================================================================

Chapters 1–14 in Track D are not “just a demo.”
They are a reusable workflow:

- clean measurement (accounting structure + quality control),
- build a driver table (operations + financial outcomes at a consistent grain),
- fit simple explainable models (driver lens),
- generate auditable artifacts (CSV/JSON/MD/figures),
- communicate responsibly (guardrails, residuals, sensitivity).

This appendix explains how to take the code and concepts you’ve seen through Chapter 14
and apply them to your own real-world business problems and datasets.


What you can (and can’t) use Chapter 14 for
-------------------------------------------

Chapter 14 is designed for **planning and control** questions like:

- “How does COGS typically move when units sold change?”
- “What’s the implied revenue-per-unit rate over the last 12–24 months?”
- “Are invoices adding extra explanatory power beyond units (mix/activity signal)?”
- “Which months look unusual relative to our driver story?”

It is not designed (yet) for:

- causal claims (“X caused Y”),
- regulatory or audit assurance conclusions,
- highly non-linear processes without additional modeling discipline,
- fine-grained pricing/mix models across hundreds of SKUs.

Treat Chapter 14 as a **professional starting point**:
a small set of explainable tools that are safe to use when data quality is real and communication is careful.


The transfer principle: make your “driver table” the center of the world
------------------------------------------------------------------------

In Chapter 14, everything flows from one small table:

- one row per month,
- operational drivers (units, invoices),
- financial outcomes (revenue, COGS).

That structure transfers extremely well to real organizations because it matches how
accountants and FP&A teams operate:

- The month is the reporting unit.
- Operational activity is measured in one or two clear drivers.
- Outcomes are measured in statement lines.

If you want Chapter 14 to work on your data, focus on building a credible driver table first.


Step 1: Define the decision and the audience (before touching data)
-------------------------------------------------------------------

Before you write code, answer these in plain English:

- Who will read the memo (owner, controller, ops manager, finance lead)?
- What decision is it supporting (budget, staffing, inventory, pricing, capacity)?
- What outcome are we trying to explain (COGS, revenue, labor cost, gross margin)?
- What operational drivers plausibly move that outcome (units, hours, shipments, invoices)?

A good driver analysis is not “cool modeling.”
It is an answer to a specific planning/control question.


Step 2: Choose the grain (usually monthly) and be consistent
------------------------------------------------------------

Most accounting analytics errors are “grain errors”:

- mixing daily operational data with monthly financial outcomes,
- joining tables at the wrong level (duplicates),
- aggregating in one table but not another.

For Chapter 14 style analysis, the default grain is:

- **one row per month** (YYYY-MM)

If your organization plans weekly, you can use weekly grain — but be consistent across all fields.


Step 3: Map your data sources to the Track D roles
--------------------------------------------------

Chapter 14 uses a deliberate split:

- Drivers come from operational/subledger activity.
- Outcomes come from statement lines (or GL-derived summaries).

In your organization, the source systems may differ (QuickBooks, Xero, NetSuite, Sage, ERP,
shop system, POS, CRM), but the roles are the same.

.. list-table:: Real-world source mapping (role → examples → why it matters)
   :header-rows: 1
   :widths: 18 42 40

   * - Role
     - Real-world examples
     - Why it matters
   * - Outcomes
     - Monthly revenue, COGS, payroll expense, operating expense, gross margin
     - Outcomes must match what leadership uses to judge performance.
   * - Operational drivers
     - Units sold, shipments, orders, invoices, labor hours, headcount, store traffic
     - Drivers are the levers you can plan and control.
   * - Calendar logic
     - Month start/end, fiscal vs calendar months, posting period rules
     - Misaligned periods silently break analysis.
   * - Definitions
     - What counts as “unit”, “invoice”, “sale”, “return”, “COGS”
     - A driver analysis is only as good as definitions.


Step 4: Build your own “driver table” (the minimum viable dataset)
------------------------------------------------------------------

Your goal is a single table that looks like this:

- ``month`` (YYYY-MM)
- one or more drivers (units, invoices, hours…)
- one or more outcomes (revenue, COGS…)
- optional: flags for known structural events (price change month, system change month)

A practical template:

.. list-table:: Driver table template (recommended minimum fields)
   :header-rows: 1
   :widths: 22 78

   * - Column
     - Notes
   * - ``month``
     - Month key (YYYY-MM). Use consistent time zone and fiscal rules.
   * - ``driver_1``
     - Primary operational driver (e.g., units sold, labor hours).
   * - ``driver_2``
     - Optional second driver (e.g., invoice count, headcount).
   * - ``outcome_1``
     - Primary financial outcome (e.g., COGS or revenue).
   * - ``outcome_2`` (optional)
     - Secondary outcome (e.g., gross margin, payroll expense).

If you can build this table cleanly for 12–36 months, you can apply Chapter 14.


Step 5: Apply the Chapter 14 code pattern to your data
------------------------------------------------------

The easiest path is to **copy** the Chapter 14 script pattern and adapt it.

Recommended approach:

1) Copy the script file:

- from: ``scripts/business_ch14_regression_driver_analysis.py``
- to:   ``scripts/business_my_driver_analysis.py``

2) Update only the parts that read your inputs and assemble your driver table.

3) Keep the output “analysis pack” structure:

- a driver table CSV
- a design JSON (definitions and formulas)
- a summary JSON (coefficients and structured results)
- a short memo MD (human-readable story)
- figures + a figures manifest CSV

Why keep the same artifact structure?

- It trains users to review results consistently.
- It makes regression auditable and shareable.
- It allows later chapters (forecasting) to build on stable outputs.

A practical real-world folder pattern:

.. code-block:: text

   data/
     raw/                # your original exports (never edit)
     processed/          # cleaned monthly tables (safe to regenerate)
     synthetic/          # Track D synthetic datasets (gitignored)
   outputs/
     my_company/         # your artifacts (gitignored)
     track_d/            # book artifacts (gitignored)

Tip: commit code and docs, not raw real-world data.
Put real-world data under ``data/raw`` and keep it out of git.


Step 6: Quality control “trust gates” before regression
-------------------------------------------------------

Do not start regression until these are true:

- The driver table has one row per month.
- Months are complete and in order.
- No duplicate months exist.
- Driver sign conventions are correct (units should not be negative unless you intend that).
- Revenue/COGS match the exact definition leadership uses.
- If returns or refunds are important, you either:
  - include them explicitly, or
  - explain how they are treated in outcomes.

If you can’t explain where a number came from, you are not ready to model it.


Step 7: Modeling tips (keep it explainable)
-------------------------------------------

Start with the Chapter 14 progression:

- Model 1: outcome ~ primary_driver
- Model 2: another outcome ~ primary_driver
- Model 3: outcome ~ primary_driver + secondary_driver

Keep the goal in mind:

- not “max accuracy,”
- but “usable planning rates and baseline components.”

Interpretation tips:

- A slope is a planning **rate** (“per unit”, “per hour”, “per invoice”).
- An intercept is a **baseline component**, but only if “near-zero driver levels”
  are meaningful for the business. If not meaningful, treat intercepts cautiously.

Diagnostics to prioritize:

- Do scatterplots look roughly linear?
- Does one month dominate the fit?
- Do residuals show patterns (seasonality, regime changes, systematic under/over prediction)?

When in doubt, simplify, segment, or add a clear control variable (later chapters).


Caveats and common real-world failure modes
-------------------------------------------

The Chapter 14 method works best when measurement is stable and definitions are consistent.
Be careful with:

- **Pricing changes and mix shifts**
  - slope (revenue-per-unit) can drift if prices or mix change.
- **Seasonality**
  - high R² can be “seasonality fit,” not causal driver fit.
- **Capacity constraints**
  - overtime, stockouts, new equipment can create non-linear behavior.
- **Policy/accounting changes**
  - revenue recognition changes or system migrations create structural breaks.
- **Short history**
  - with only 6–10 months, regression is fragile. Prefer descriptive trend analysis first.

If your process changed, that’s not a regression failure — it’s a business reality signal.
Handle it explicitly: segment the timeline or add an indicator for the change month.


How to communicate results responsibly (the memo discipline)
-----------------------------------------------------------

Before you share a memo:

- Use “driver lens” language, not causality language.
- State the period covered (“based on the last 24 months of data”).
- Call out known break points (price change month, system change month, acquisitions).
- Mention residual uncertainty (“plus/minus unexplained movement”).

Safe phrasing patterns:

- “Given the recent history, the implied rate is…”
- “If driver increases by X, the model implies outcome changes by about Y, with variation.”
- “This month is unusual relative to the driver story; investigate…”

Avoid:

- “X causes Y”
- “This proves…”
- “We can guarantee…”

The goal is to support planning decisions, not win an argument.


A practical “bring your own data” recipe (summary)
--------------------------------------------------

1) Define decision + outcome + driver(s).
2) Choose a grain (monthly is default).
3) Build a driver table (one row per month).
4) Run QC trust gates (completeness, signs, lineage).
5) Fit simple explainable models (start with one driver).
6) Inspect figures and residual patterns.
7) Write a short memo with guardrails.
8) Save artifacts, not raw data.
9) Iterate: add seasonality/segmentation only when needed.

This is exactly what Track D is building toward: analysis that is credible to accountants,
useful to operators, and reproducible for teams.

What’s next
-----------

Appendix 14E is the “transfer guide.”
Chapters 15+ are where this turns into a forecasting system:
backtesting, forecast error measurement, scenario planning, and roll-forward workflows.
