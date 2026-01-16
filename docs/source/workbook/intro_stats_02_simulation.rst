Intro Stats 2 - Simulation and uncertainty (bootstrap)
======================================================

This is Part 2 of the **Intro Stats case study pack**.

You still have the same dataset and the same research question:

* **Dataset:** ``data/intro_stats_scores.csv``
* **Question:** Do students in the **treatment** group score higher than students in the **control** group?

In Part 1 you computed a **point estimate** (a single number): the difference
between the treatment and control means.

In Part 2 you will answer the natural follow-up question:

*If we repeated this study with "different students", how much could the
mean difference change?*

Learning goals
--------------

By the end of this chapter, you should be able to:

* explain (in plain language) why a single mean difference is often not enough,
* generate a simulation-based uncertainty summary using a bootstrap, and
* interpret a bootstrap confidence interval as a "plausible range" for the
  mean difference.

Concepts (plain language)
-------------------------

**Sampling variability**
  If you sample a different set of students, you will not get the exact same
  mean difference every time. Small changes in the sample can cause small (and
  sometimes not-so-small) changes in the result.

**Bootstrap simulation**
  The bootstrap is a simple simulation trick:

  * treat your dataset as your best snapshot of reality,
  * repeatedly resample rows *with replacement* (so some students may appear
    twice and some not at all), and
  * recompute the statistic each time (here: mean(treatment) - mean(control)).

  The collection of simulated statistics is an *approximate sampling
  distribution*.

**Deterministic outputs (important for the Workbook)**
  This script sets a fixed random seed so your outputs are reproducible.
  That is why your CSV and PNG artifacts should match the reference results
  when your input dataset matches the workbook dataset.

Run
---

From inside your workbook folder:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_02_simulation

If you want to run the script directly:

.. code-block:: bash

   python scripts/intro_stats_02_simulation.py

What gets created
-----------------

The script writes outputs to:

* ``outputs/case_studies/intro_stats/``

You should see:

* ``bootstrap_mean_diffs.csv`` - one row per bootstrap draw
* ``bootstrap_summary.csv`` - a tiny one-row summary table
* ``bootstrap_mean_diff_hist.png`` - a histogram of the bootstrap distribution

Inspect
-------

1) Open ``bootstrap_summary.csv`` and answer:

* What is the **observed** mean difference?
* What is the **95% bootstrap interval** (low and high)?

2) Open ``bootstrap_mean_diff_hist.png`` and check:

* Is the distribution centered near the observed difference?
* Is most of the distribution above 0 (meaning treatment > control)?

Reference outputs (what you should see)
---------------------------------------

If your ``data/intro_stats_scores.csv`` matches the workbook dataset, you should
see results close to:

* Observed mean difference: about **11.20** points
* 95% bootstrap interval: about **[9.50, 12.85]**

The exact values are saved in ``bootstrap_summary.csv``.

Worked problems (with solutions)
--------------------------------

Problem 1: Compute the mean difference by hand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From Part 1, you should have a table like this (values may vary slightly if you
rounded when you copied them):

* control mean: about 69.0
* treatment mean: about 80.2

Question:
  What is the mean difference (treatment - control)?

Solution:
  Subtract:

  ``80.2 - 69.0 = 11.2`` points.

  That is your **point estimate**.

Problem 2: Interpret the bootstrap interval
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open ``bootstrap_summary.csv``.

Question:
  Suppose the interval is ``[9.50, 12.85]``. What does that mean in plain
  language?

Solution:
  A good plain-language interpretation is:

  "Given this dataset, a reasonable (simulation-based) range for the true
  mean advantage of the treatment group is about **9.5 to 12.9 points**."

  It does *not* mean "95% chance the treatment works". It is about the
  uncertainty in the **estimated mean difference**.

Problem 3: How often is the mean difference <= 0?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a quick sanity check.

From inside your workbook folder:

.. code-block:: bash

   python -c "import pandas as pd; d=pd.read_csv('outputs/case_studies/intro_stats/bootstrap_mean_diffs.csv'); print('P(diff<=0)=', (d.boot_mean_diff<=0).mean())"

Interpretation:

* If ``P(diff<=0)`` is near 0, your bootstrap draws almost always show
  treatment > control.
* If it is large (for example 0.30), your data are consistent with treatment
  sometimes being worse or equal.

Using your own data (or your own mini-example)
----------------------------------------------

The Intro Stats case study expects a very simple CSV format:

* one row per student
* columns: ``id``, ``group``, ``score``
* ``group`` should be ``control`` or ``treatment``

.. warning::

   Editing ``data/intro_stats_scores.csv`` changes the inputs for *all* Intro
   Stats chapters. Always make a backup first.

Step A: Make a backup
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cp data/intro_stats_scores.csv data/intro_stats_scores_backup.csv

Step B: Edit the CSV in a text editor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open the file with Notepad:

.. code-block:: bash

   notepad data/intro_stats_scores.csv

Replace the contents with this small worked example:

.. code-block:: text

   id,group,score
   1,control,73
   2,control,69
   3,control,75
   4,control,71
   5,treatment,82
   6,treatment,79
   7,treatment,85
   8,treatment,81

Save the file and close Notepad.

Step C: Run the script and compare to the expected pattern
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pystatsv1 workbook run intro_stats_02_simulation

For this mini-example, you should see:

* Observed mean difference: **9.75** points
* 95% bootstrap interval: roughly **[4.88, 15.12]**

(Your exact values will be written to ``bootstrap_summary.csv``.)

Step D: Restore the workbook dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   mv data/intro_stats_scores_backup.csv data/intro_stats_scores.csv

Reproducibility checkpoint
--------------------------

Run the chapter twice:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_02_simulation
   pystatsv1 workbook run intro_stats_02_simulation

Because the script uses a fixed seed, you should get the same outputs each time.

Check
-----

This case study pack includes a small "check your work" test.

From inside your workbook folder:

.. code-block:: bash

   pystatsv1 workbook check intro_stats

If you edited the dataset for the mini-example, restore the original dataset
first (see the restore step above) so the check matches the workbook reference.

Next
----

Go to :doc:`intro_stats_03_distributions_outliers` to look at distributions,
outliers, and why plots matter before you run formal tests.