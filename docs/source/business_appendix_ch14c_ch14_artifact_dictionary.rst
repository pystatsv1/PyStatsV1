Appendix 14C: Chapter 14 artifact dictionary (what each output is for)
======================================================================

Chapter 14 is designed to produce a small “analysis pack” of artifacts that are:

- easy to inspect (CSV / Markdown),
- easy to automate (JSON),
- easy to review visually (figures + manifest),
- and reproducible (regenerate from the same dataset + seed).

This appendix lists each artifact, its purpose, and what to look at first.

Where the Chapter 14 artifacts live
-----------------------------------

Chapter 14 is run via:

.. code-block:: bash

   make business-ch14

The Makefile passes an output root like ``--outdir outputs/track_d``.
The Chapter 14 script then writes inside a Track D subfolder, so the final location is:

- ``outputs/track_d/track_d/``

Typical directory layout:

.. code-block:: text

   outputs/track_d/track_d/
     ch14_driver_table.csv
     ch14_regression_design.json
     ch14_regression_summary.json
     ch14_regression_memo.md
     ch14_figures_manifest.csv
     figures/
       ch14_fig01_cogs_vs_units.png
       ch14_fig02_revenue_vs_units.png
       ch14_fig03_actual_vs_predicted_revenue_m3.png


Suggested review order (fastest to insight)
-------------------------------------------

1. ``ch14_driver_table.csv`` (sanity check the monthly driver table)
2. ``ch14_regression_memo.md`` (read the story in plain English)
3. ``figures/*.png`` (does the relationship look stable / linear-ish?)
4. ``ch14_regression_summary.json`` (exact coefficients, R², and structured values)
5. ``ch14_regression_design.json`` + ``ch14_figures_manifest.csv`` (repro + reporting metadata)


Artifact dictionary
-------------------

.. list-table:: Chapter 14 outputs (artifact → purpose → what to look for first)
   :header-rows: 1
   :widths: 26 40 34

   * - Artifact
     - Purpose
     - What to look for first
   * - ``ch14_driver_table.csv``
     - The monthly driver table used for all models (units sold, invoice count, revenue, COGS).
       This is the “data contract” for Chapter 14.
     - Check month alignment and magnitude:
       - Are months continuous?
       - Are ``units_sold`` positive and plausible?
       - Do revenue/COGS values look reasonable and consistent with your NSO story?
   * - ``ch14_regression_memo.md``
     - Human-readable summary (the “starter executive memo”).
       This is what you would paste into a planning email or a short doc.
     - Read it top-to-bottom:
       - Are the slopes/intercepts interpreted correctly (baseline vs rate)?
       - Do the guardrails make sense (driver lens, not causation)?
   * - ``ch14_regression_summary.json``
     - Machine-readable results:
       coefficients, R², key diagnostics, and structured values for downstream automation.
     - Look for:
       - Coefficients (intercept + slopes)
       - R² per model
       - Any “notes”/flags the script includes for interpretation
   * - ``ch14_regression_design.json``
     - Reproducibility “design contract”:
       expected inputs, driver definitions, and model formulas.
       Useful for reviewers and for future chapters that want to rely on the same structure.
     - Confirm:
       - Model formulas match the chapter narrative (m1/m2/m3)
       - Driver definitions match the dataset lineage (inventory movements, AR events, IS lines)
   * - ``ch14_figures_manifest.csv``
     - A reporting manifest listing each figure file plus metadata
       (chart type, title, axis labels, guardrail note, data source).
       This supports consistent documentation and future “report assembly.”
     - Open it and confirm:
       - All figure filenames exist under ``figures/``
       - Titles/labels read well (this matters for end users)
       - Guardrail notes match the chapter’s interpretation discipline
   * - ``figures/ch14_fig01_cogs_vs_units.png``
     - Visual check for Model 1: COGS vs units sold with a fitted line.
     - Look for:
       - Is the relationship roughly linear?
       - Do you see major outliers dominating the fit?
       - Does the intercept look plausible (near-zero vs baseline cost)?
   * - ``figures/ch14_fig02_revenue_vs_units.png``
     - Visual check for Model 2: Revenue vs units sold with a fitted line.
     - Look for:
       - Is slope stable (implied blended price-per-unit)?
       - Any clusters suggesting mix/price shifts?
       - Does a non-zero intercept suggest timing or non-unit revenue?
   * - ``figures/ch14_fig03_actual_vs_predicted_revenue_m3.png``
     - Visual check for Model 3: multi-driver revenue model
       (actual vs predicted / fit quality view).
     - Look for:
       - Are predictions systematically high/low in certain months (patterned residuals)?
       - Does adding invoice_count appear to improve fit meaningfully?
       - Any “regime change” behavior (model works early, breaks later)?


How to regenerate the artifacts (and why they are not committed)
---------------------------------------------------------------

Artifacts under ``outputs/`` are generated and not committed to git.
This keeps the repo small and makes your results reproducible.

Standard regeneration:

.. code-block:: bash

   # Ensure the dataset exists locally (gitignored)
   make business-nso-sim
   make business-validate

   # Rebuild Chapter 14 artifacts
   make business-ch14

If you want to run Chapter 14 on a different dataset folder:

.. code-block:: bash

   python -m scripts.business_ch14_regression_driver_analysis \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123


Common “first checks” when something looks wrong
------------------------------------------------

- If slopes look odd, first verify ``ch14_driver_table.csv``:
  a sign convention mistake (e.g., units sold negative) can flip interpretations.

- If a figure is missing, open ``ch14_figures_manifest.csv`` and confirm the filename
  is listed and matches the file on disk.

- If revenue/COGS appear inconsistent, re-run:

  .. code-block:: bash

     make business-validate

  Track D assumes measurement quality before modeling.

Closing note
------------

Chapter 14 artifacts are intentionally designed to make regression “accounting-grade”:

- a driver table you can audit,
- models you can explain,
- visuals you can sanity-check,
- and structured JSON you can automate.

Appendix 14B (NSO v1 data dictionary) explains the *tables*.
Appendix 14C explains the *artifacts produced from those tables*.
