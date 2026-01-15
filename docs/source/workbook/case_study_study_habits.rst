Study Habits Case Study Pack
============================

This “starter case study pack” is meant to feel like a tiny mini-course inside the Workbook:

* one dataset,
* one story,
* and a short sequence of scripts you can run and check.

The goal is to stop the Workbook from feeling like “random scripts with random numbers”.


The story
---------

A school is piloting three different study strategies over 4 weeks:

* **control** — study like you normally do
* **flashcards** — daily flashcard practice
* **spaced** — spaced repetition schedule

Each student takes:

* a **pretest**
* a **posttest**
* and a **retention** test one week later


What you get
------------

Inside your workbook folder (created by ``pystatsv1 workbook init``):

* Dataset: ``data/study_habits.csv``
* Explore script: ``scripts/study_habits_01_explore.py``
* ANOVA script: ``scripts/study_habits_02_anova.py``
* Tests: ``tests/test_study_habits_case_study.py``

Outputs go to: ``outputs/case_studies/study_habits/``


Run → Inspect → Check
---------------------

From inside your workbook folder:

.. code-block:: bash

   # Part 1: explore the dataset and generate starter outputs
   pystatsv1 workbook run study_habits_01_explore

   # Part 2: run a one-way ANOVA on posttest_score by group
   pystatsv1 workbook run study_habits_02_anova

   # Check: confirms the dataset and effect pattern match the lesson
   pystatsv1 workbook check study_habits


How this becomes a mini-course
------------------------------

A simple path through multiple chapters:

* **Ch10 (ANOVA):** Use the case study pack to practice one-way ANOVA.
* **Ch18 (ANCOVA):** Treat ``pretest_score`` as a covariate.
* **Ch19 (Regression):** Predict ``posttest_score`` from ``study_hours_per_week``, ``sleep_hours``, etc.
* **Ch20 (Non-parametric):** Compare groups using rank-based alternatives.

You can reuse the same story and dataset, but apply a different method each chapter.
