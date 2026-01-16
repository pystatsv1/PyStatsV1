Case Study Pack: Intro Stats
============================

This “starter case study pack” is a tiny mini-course inside the Workbook:

* one dataset,
* one story,
* and a short sequence of scripts you can run and check.

It’s designed for **absolute beginners** who want a concrete, repeatable workflow:

**Run → Inspect → Check.**

The story
---------

A teacher pilots a new study strategy and wants to know if it improves exam scores.

Two groups of students take the same final exam:

* **control** — normal study habits
* **treatment** — new strategy

We’ll use the same dataset in five short scripts, each building intuition:

1) descriptives
2) simulation (bootstrap)
3) distributions + outliers
4) confidence intervals
5) hypothesis testing by simulation + effect size

What you get
------------

Inside your workbook folder (created by ``pystatsv1 workbook init``):

Dataset
  * ``data/intro_stats_scores.csv``

Scripts
  * ``scripts/intro_stats_01_descriptives.py``
  * ``scripts/intro_stats_02_simulation.py``
  * ``scripts/intro_stats_03_distributions_outliers.py``
  * ``scripts/intro_stats_04_confidence_intervals.py``
  * ``scripts/intro_stats_05_hypothesis_testing.py``

Write-up template
  * ``writeups/intro_stats_interpretation_template.md``

Tests
  * ``tests/test_intro_stats_case_study.py``

Outputs go to
  * ``outputs/case_studies/intro_stats/``

Run → Inspect → Check
---------------------

From inside your workbook folder:

.. code-block:: bash

   # Part 1: descriptives (means/SDs + a quick histogram)
   pystatsv1 workbook run intro_stats_01_descriptives

   # Part 2: bootstrap simulation for the mean difference
   pystatsv1 workbook run intro_stats_02_simulation

   # Part 3: distributions + outliers (IQR rule) + plots
   pystatsv1 workbook run intro_stats_03_distributions_outliers

   # Part 4: 95% confidence intervals (t-based) + plot
   pystatsv1 workbook run intro_stats_04_confidence_intervals

   # Part 5: permutation test (p-value by simulation) + effect size
   pystatsv1 workbook run intro_stats_05_hypothesis_testing

   # Check: confirms the dataset shape + the expected effect direction
   pystatsv1 workbook check intro_stats

Inspect your outputs
--------------------

Open the output folder in File Explorer:

.. code-block:: bash

   explorer outputs/case_studies/intro_stats

Start with these files:

* ``group_summary.csv`` (group means and SDs)
* ``bootstrap_mean_diff.csv`` + ``bootstrap_mean_diff.png``
* ``distributions_summary.csv`` + ``outliers_iqr.csv`` + ``score_distributions.png``
* ``ci_mean_diff_welch_95.csv`` + ``ci_group_means_95.png``
* ``permutation_test_summary.csv`` + ``permutation_null_distribution.png``
* ``effect_size.csv``

Then (optional) write up your interpretation
--------------------------------------------

The pack includes a tiny write-up template. Copy it and fill in the blanks:

.. code-block:: bash

   cp writeups/intro_stats_interpretation_template.md writeups/intro_stats_writeup.md

Then open ``writeups/intro_stats_writeup.md`` in Notepad (or your editor) and answer the questions.

What you should see
-------------------

* The **treatment** group should have a higher mean score than the **control** group.
* The bootstrap distribution of the mean difference should be mostly **above 0**.
* The permutation test should usually report a **small p-value** (because the simulated data was
  generated with a real group difference).
* The effect size (Cohen’s d) should be in the **small-to-medium** range.

Notes
-----

* If you’re short on time, Parts **1–2** are the minimum “vibe check”.
* The scripts are intentionally simple and readable — open them and explore!
