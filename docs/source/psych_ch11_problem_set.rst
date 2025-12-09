Chapter 11 Problem Set – Paired-Samples t Test
==============================================

Where this problem set fits in the story
----------------------------------------

This problem set extends the :ref:`psych_ch11_paired_t` chapter on
**within-subjects designs** and the paired-samples t test.

Chapter 11 introduces designs where each participant serves as their
own control (for example, pre–post designs). Track C adds a set of
worked, fully reproducible examples that show how to:

- Simulate pre–post data for different research scenarios.
- Run paired-samples t tests using the PyStatsV1 helpers.
- Interpret the resulting means, t values, p values, and effect sizes.

Learning goals
--------------

By the end of this problem set, you should be able to:

- Recognize when a **paired-samples t test** is appropriate.
- Explain how the test is based on **difference scores** (post – pre).
- Describe how **sample size** and **effect size** jointly determine power.
- Use the PyStatsV1 solution code as a **template** for your own pre–post data.

How to run the worked solutions
-------------------------------

From the project root, run:

.. code-block:: bash

   make psych-ch11-problems

This wraps:

.. code-block:: bash

   python -m scripts.psych_ch11_problem_set

and regenerates all synthetic datasets, the summary CSV, and the group
means plot.

Conceptual warm-up
------------------

- In a paired design, each participant is measured **twice** (or more),
  so we compare them to themselves.
- This reduces error by controlling for stable individual differences.
- The paired-samples t test is equivalent to running a one-sample t
  test on the **difference scores** (post – pre).
- Effect sizes (Cohen's d) are typically calculated using the
  variability of the difference scores.

Applied exercises
-----------------

Each exercise in this problem set corresponds to a realistic research
scenario:

- **Exercise 1 – Moderate improvement (n = 40)**

  A typical lab-based intervention with a medium-sized effect. The
  paired t test should be clearly significant.

- **Exercise 2 – Small / ambiguous effect (n = 30)**

  A small effect with modest sample size. The t test will often be
  non-significant, highlighting how hard it is to detect small effects
  without sufficient power.

- **Exercise 3 – Strong improvement (n = 25)**

  A large effect with a smaller sample. Despite the lower n, the effect
  is strong enough to be detected with high confidence.

PyStatsV1 Lab: Paired-samples t problem set in action
-----------------------------------------------------

The solution script :mod:`scripts.psych_ch11_problem_set` shows how to:

- Generate pre–post data for each scenario (exercise label, group means,
  effect size, etc.).
- Run the paired t tests using
  :func:`scripts.psych_ch11_paired_t.run_paired_t`.
- Save one CSV per exercise plus a **summary CSV** with the key
  statistics side-by-side.
- Produce a simple bar plot comparing pre and post means for each
  exercise.

Running the Chapter 11 problem set lab
--------------------------------------

After running:

.. code-block:: bash

   make psych-ch11-problems

you should see the following outputs:

- ``data/synthetic/psych_ch11_exercise1.csv`` –
  Moderate-effect pre–post study (n = 40).
- ``data/synthetic/psych_ch11_exercise2.csv`` –
  Small-effect pre–post study (n = 30).
- ``data/synthetic/psych_ch11_exercise3.csv`` –
  Strong-effect pre–post study (n = 25).
- ``outputs/track_c/ch11_problem_set_results.csv`` –
  Summary table of the three paired t tests.
- ``outputs/track_c/ch11_problem_set_means.png`` –
  Group means plot (pre vs post for each exercise).

Conceptual summary
------------------

- Paired-samples t tests compare **mean differences within participants**
  rather than between independent groups.
- They are often **more powerful** than independent-samples designs,
  because each person serves as their own control.
- Power depends on the magnitude of the true effect, the variability of
  the difference scores, and the sample size.
- PyStatsV1 solution scripts give you a **reusable pre–post template**:
  drop in your own dataset, rerun the analysis, and verify the results
  using transparent, version-controlled code.
