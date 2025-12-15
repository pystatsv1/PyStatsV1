Track C — Chapter 15 Problem Set (Correlation)
==============================================

This problem set gives practice with **correlation**, including:

- Pearson correlation (r) and interpretation
- Correlation matrices
- The **third-variable** problem
- **Partial correlation** (controlling for a third variable)

Prerequisite
------------

Complete the Chapter 15 lab first:

- :doc:`psych_ch15_correlation`

How to run
----------

From the repository root:

.. code-block:: bash

   python -m scripts.psych_ch15_problem_set

Run a single exercise:

.. code-block:: bash

   python -m scripts.psych_ch15_problem_set --exercise 1
   python -m scripts.psych_ch15_problem_set --exercise 2
   python -m scripts.psych_ch15_problem_set --exercise 3

What you should submit
----------------------

For each exercise:

1. Report **Pearson r**, degrees of freedom, and p-value.
2. Report and interpret the **95% CI** for r.
3. Write a short interpretation (2–4 sentences):
   - direction and strength,
   - what the scatterplot *would* look like,
   - whether the relationship is practically meaningful.

For Exercise 3:
- Explain why **correlation does not imply causation** (third-variable problem).
- Report the **partial correlation** controlling for Z and interpret the difference.

Exercises
---------

Exercise 1 — Strong positive correlation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dataset with a clear positive linear relationship.

Goal:
- large positive r and a highly significant p-value.

Exercise 2 — Near-zero correlation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dataset where x and y are unrelated.

Goal:
- r close to 0 and typically non-significant.

Exercise 3 — Third-variable problem (partial correlation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

x and y share a common cause z, producing a strong raw correlation.

Goal:
- strong raw correlation for x–y,
- **partial correlation** controlling z near zero.
