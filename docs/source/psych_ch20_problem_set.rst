Track C – Chapter 20 Problem Set (Responsible Researcher)
=========================================================

This problem set practices the capstone ideas of a responsible researcher:

- **Power analysis** (planning sample size before running a study)
- **Meta-analysis** (combining evidence across studies)
- **Research integrity** (how questionable practices inflate false positives)

Run the worked solutions
------------------------

::

   make psych-ch20-problems

Run only the tests
------------------

::

   make test-psych-ch20-problems

Files and outputs
-----------------

The solution script writes:

- Synthetic datasets: ``data/synthetic/``
- Summaries + plots: ``outputs/track_c/``

Exercises
---------

Exercise 1 — Power analysis (a priori)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plan a study to detect a **moderate effect** (Cohen's *d* = 0.50) with:

- alpha = 0.05 (two-sided)
- target power = 0.80

You will interpret:

1. The **required n per group**
2. The **power curve** (power as a function of sample size)

Exercise 2 — Meta-analysis (fixed vs random)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You are given a set of simulated studies with heterogeneity.

You will interpret:

1. The **fixed-effect** pooled estimate
2. The **random-effects** pooled estimate
3. Heterogeneity statistics (**Q**, **I²**, **tau²**)

Exercise 3 — Optional stopping inflates Type I error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A researcher "peeks" at the p-value multiple times and stops early if p < 0.05.
Even if the null hypothesis is true, this practice inflates false positives.

You will interpret:

1. The observed **false-positive rate**
2. Why "peeking" violates the planned alpha level
