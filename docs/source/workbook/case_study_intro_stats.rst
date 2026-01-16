Case Study Pack: Intro Stats
============================

This “starter case study pack” is a tiny mini-course for absolute beginners:

* one dataset,
* one story,
* and a short sequence of scripts you can run and check.

The goal is to practice the Workbook pattern:

**Run → Inspect → Check**

The story
---------

A teacher is piloting a new “practice quiz” strategy.
Two groups of students take the same short quiz:

* **control** — the usual study approach
* **treatment** — a structured practice-quiz approach

You’re given the quiz scores. Your job is to:

1) describe what you see (tables + plots)
2) use simulation to understand variability (bootstrap)

What you get
------------

Inside your workbook folder (created by ``pystatsv1 workbook init``):

* Dataset: ``data/intro_stats_scores.csv``
* Descriptives script: ``scripts/intro_stats_01_descriptives.py``
* Simulation script: ``scripts/intro_stats_02_simulation.py``
* Tests: ``tests/test_intro_stats_case_study.py``

Outputs go to:

* ``outputs/case_studies/intro_stats/``

Run → Inspect → Check
---------------------

From inside your workbook folder:

.. code-block:: bash

   # Part 1: descriptives + plot
   pystatsv1 workbook run intro_stats_01_descriptives

   # Part 2: simulation (bootstrap)
   pystatsv1 workbook run intro_stats_02_simulation

   # Check: confirms the dataset contract + the “treatment > control” pattern
   pystatsv1 workbook check intro_stats

What you should see
-------------------

After Part 1, open:

* ``outputs/case_studies/intro_stats/group_summary.csv``
* ``outputs/case_studies/intro_stats/score_by_group.png``

The group means should show a clear difference:

* control mean ≈ **70.65**
* treatment mean ≈ **81.85**

After Part 2, open:

* ``outputs/case_studies/intro_stats/bootstrap_summary.csv``
* ``outputs/case_studies/intro_stats/bootstrap_mean_diff_hist.png``

You should see something like:

* observed mean difference (treatment − control) ≈ **11.20**
* bootstrap 95% CI ≈ **[9.50, 12.85]**

Note: The first time you make a plot, Matplotlib may print a one-time message
about building a font cache. That’s normal.
