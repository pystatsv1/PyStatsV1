Track C – Chapter 18 Problem Set (ANCOVA)
========================================

This problem set practices the core ideas of **Analysis of Covariance (ANCOVA)**:

- Between-subjects factor: ``group`` (Control vs Treatment)
- Covariate: ``pretest``
- DV: ``posttest``

You will interpret:

1. The covariate effect (does ``pretest`` predict ``posttest``?)
2. The adjusted group effect (does Treatment differ after controlling for ``pretest``?)
3. The **homogeneity of regression slopes** assumption (``pretest × group``)

Run the worked solutions
------------------------

.. code-block:: bash

   make psych-ch18-problems

Run only the tests
------------------

.. code-block:: bash

   make test-psych-ch18-problems

Files and outputs
-----------------

The solution script writes:

- Synthetic datasets: ``data/synthetic/``
- Summaries + plots: ``outputs/track_c/``

Exercises
---------

Exercise 1 — True adjusted group effect
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A real Treatment advantage exists **after controlling for pretest**.
You should see:

- significant covariate effect
- significant adjusted group effect

Exercise 2 — Spurious raw difference (pretest imbalance)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Treatment starts higher on the pretest, but there is **no true Treatment effect**.
You should see:

- raw posttest means differ
- ANCOVA group effect becomes non-significant after controlling for pretest

Exercise 3 — Slopes assumption violation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The relationship between pretest and posttest differs by group.
You should see:

- significant ``pretest × group`` interaction in the slopes test
- this is a red flag for standard ANCOVA interpretation
