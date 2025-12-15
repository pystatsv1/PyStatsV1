Track C — Chapter 14 Problem Set (Repeated-Measures ANOVA)
=========================================================

This problem set gives you practice with **repeated-measures (within-subjects) ANOVA**.
You will analyze designs where the **same participants** are measured at **3+ time points**.

Prerequisite
------------

Complete the Chapter 14 lab first:

- :doc:`psych_ch14_repeated_measures_anova`

How to run
----------

From the repository root:

.. code-block:: bash

   python -m scripts.psych_ch14_problem_set

Run a single exercise:

.. code-block:: bash

   python -m scripts.psych_ch14_problem_set --exercise 1
   python -m scripts.psych_ch14_problem_set --exercise 2
   python -m scripts.psych_ch14_problem_set --exercise 3

What you should submit
----------------------

For each exercise:

1. Report the repeated-measures ANOVA result (F, df, p).
2. Report **partial eta-squared** (np2) as the effect size.
3. Write a 2–4 sentence interpretation in APA-style language, including:
   - whether there is evidence of change over time,
   - the direction/pattern of means (e.g., increasing, flat, etc.),
   - practical interpretation of the effect size.

Exercises
---------

Exercise 1 — Clear time effect
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dataset with three time points and a strong change over time.

Goal:
- You should see a **significant** time effect and a **large** effect size.

Exercise 2 — No true time effect
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dataset with four time points where the population means are equal.

Goal:
- You should see a **non-significant** time effect and a **tiny** effect size.

Exercise 3 — Correlated measurements (sphericity risk)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dataset with four time points and **correlated** within-subject errors (realistic longitudinal structure).

Goal:
- You should still detect a time effect.
- Discuss **sphericity** conceptually (and if the output includes sphericity/GG info, comment on it).
