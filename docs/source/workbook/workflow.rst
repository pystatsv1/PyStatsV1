Workflow
========

The PyStatsV1 Workbook follows a simple loop:

1. **Run** a chapter script (or a ``make`` target).
2. **Inspect** the printed output + any saved plots/tables.
3. **Check your work** by running the corresponding unit tests.

Run a chapter
-------------

Most Track C chapters have a "problem set" script under ``scripts/``.
You can run a chapter in two equivalent ways.

Option A: Use the Makefile target (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each problem set has a ``make`` target that runs the script for you.
Example (Chapter 18, ANCOVA)::

   make psych-ch18-problems

Option B: Run the script directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Makefile target is just a convenience wrapper. You can always run the script::

   python scripts/psych_ch18_problem_set.py

Where outputs go
----------------

Most Track C scripts write two kinds of artifacts:

- **Synthetic datasets** used in the exercises:

  - ``data/synthetic/`` (CSV files)

- **Student-facing outputs** (plots and/or summary tables):

  - ``outputs/track_c/``

The exact filenames vary by chapter, but you will usually see a pattern like:

- ``psych_ch18_exercise_1_*.csv`` in ``data/synthetic/``
- ``psych_ch18_exercise_1_*.png`` and/or ``.json`` in ``outputs/track_c/``

Check your work
---------------

Every Workbook chapter has unit tests that assert the *intended statistical pattern*.
For example, to check Chapter 18::

   pytest -q tests/test_psych_ch18_problem_set.py

If a test fails, the most common causes are:

- You changed a parameter (sample size, standard deviations, effect sizes) and the
  simulated data no longer reliably shows the intended pattern.
- You changed factor labels or column names (the analysis functions expect stable
  names like ``group``, ``time``, ``score``, etc.).

Tip: keep the default ``random_state`` values in each exercise while you learn.
That makes your results stable and makes it easier to compare your output
with classmates and with the docs.
